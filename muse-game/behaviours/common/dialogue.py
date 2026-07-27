"""Runtime handler for compiled MuseLang dialogue."""

from __future__ import annotations

from evennia import CmdSet

from commands.command import Command

from .action_eval import execute_program
from .condition_eval import evaluate_condition
from .metadata_access import args_match_object, get_dialogue, get_interactions
from .runtime_context import RuntimeContext


BEHAVIOUR_PATH = "behaviours.common.dialogue.DialogueCmdSet"
SESSION_KEY = "muselang_dialogue_state"


def _command_class_name(interaction: dict[str, object]) -> str:
    raw_name = str(interaction.get("id") or interaction.get("verb") or "dialogue")
    return "Cmd" + "".join(part[:1].upper() + part[1:] for part in raw_name.replace("-", "_").split("_") if part)


def _make_command(interaction: dict[str, object]) -> type[Command]:
    verb = str(interaction.get("verb") or interaction.get("id") or "talk")
    aliases = list(interaction.get("aliases", []) or [])

    class CmdDialogue(Command):
        """Start or advance one MuseLang dialogue."""

        def func(self) -> None:
            matched, remaining = args_match_object(self.args, self.obj)
            if not matched:
                self.caller.msg(f"You cannot {verb} that.")
                return
            run_dialogue(self.caller, self.obj, verb, remaining)

    CmdDialogue.__name__ = _command_class_name(interaction)
    CmdDialogue.key = verb
    CmdDialogue.aliases = aliases
    CmdDialogue.help_category = "Interactions"
    return CmdDialogue


class DialogueCmdSet(CmdSet):
    """CmdSet exposing MuseLang dialogue entry verbs."""

    key = "DialogueCmdSet"
    priority = 1

    def at_cmdset_creation(self) -> None:
        obj = self.cmdsetobj
        if obj is None:
            return
        for interaction in get_interactions(obj):
            if interaction.get("behaviour") == BEHAVIOUR_PATH:
                self.add(_make_command(interaction)())


def run_dialogue(caller, obj, verb: str, raw_args: str) -> None:
    """Start or advance a dialogue session for one caller and target."""

    dialogue = get_dialogue(obj)
    if not dialogue:
        caller.msg(f"{getattr(obj, 'key', 'That')} has nothing to say.")
        return

    session_state = getattr(getattr(caller, "ndb", None), SESSION_KEY, None) or {}
    target_id = getattr(obj, "id", None)
    active = session_state.get("active") and session_state.get("target") == target_id
    selection = raw_args.strip()
    if not active:
        session_state = {"active": True, "target": target_id, "current_node": dialogue.get("entry"), "last_choice": None}
    elif selection:
        current_node = dialogue.get("nodes", {}).get(session_state.get("current_node"), {})
        selection_context = RuntimeContext(
            caller=caller,
            obj=obj,
            verb=verb,
            raw_args=selection,
            dialogue_state=session_state,
        )
        _says, available_options, _actions = _node_content(current_node, selection_context)
        chosen = _select_option(selection, available_options, caller, obj, session_state)
        if chosen is None:
            caller.msg("Choose one of the displayed dialogue options.")
            _render_node(caller, obj, dialogue, session_state)
            return
        session_state["last_choice"] = chosen["id"]
        session_state["current_node"] = chosen["target"]
    _store_session(caller, session_state)
    _advance_until_prompt(caller, obj, dialogue, session_state, verb)


def _advance_until_prompt(caller, obj, dialogue, session_state: dict[str, object], verb: str) -> None:
    safety = 0
    while safety < 20:
        safety += 1
        node_id = session_state.get("current_node")
        node = dialogue.get("nodes", {}).get(node_id, {})
        context = RuntimeContext(
            caller=caller,
            obj=obj,
            verb=verb,
            raw_args="",
            selected_option=session_state.get("last_choice"),
            dialogue_state=session_state,
        )
        says, options, actions = _node_content(node, context)
        for line in says:
            caller.msg(str(line))
        session_state["visible_options"] = [
            {"id": option["id"], "hotkey": option.get("hotkey"), "index": index + 1}
            for index, option in enumerate(options)
        ]
        if options:
            for index, option in enumerate(options, start=1):
                selector = option.get("hotkey") or str(index)
                caller.msg(f"[{selector}] {option['label']}")
            _store_session(caller, session_state)
            return
        result = execute_program(actions, context)
        if result.get("goto") is not None:
            session_state["current_node"] = result["goto"]
            _store_session(caller, session_state)
            continue
        _clear_session(caller)
        return


def _visible_options(options, context: RuntimeContext) -> list[dict[str, object]]:
    return [option for option in options if evaluate_condition(option.get("condition"), context)]


def _select_option(selection: str, options, caller, obj, session_state) -> dict[str, object] | None:
    context = RuntimeContext(
        caller=caller,
        obj=obj,
        verb="talk",
        raw_args=selection,
        dialogue_state=session_state,
    )
    visible = _visible_options(options, context)
    lowered = selection.strip().lower()
    if lowered.isdigit():
        index = int(lowered) - 1
        if 0 <= index < len(visible):
            return visible[index]
    for option in visible:
        if lowered == str(option.get("id", "")).lower():
            return option
        hotkey = str(option.get("hotkey") or "").lower()
        if hotkey and lowered == hotkey:
            return option
    return None


def _render_node(caller, obj, dialogue, session_state: dict[str, object]) -> None:
    node = dialogue.get("nodes", {}).get(session_state.get("current_node"), {})
    context = RuntimeContext(caller=caller, obj=obj, verb="talk", dialogue_state=session_state)
    says, options, _actions = _node_content(node, context)
    for line in says:
        caller.msg(str(line))
    for index, option in enumerate(options, start=1):
        selector = option.get("hotkey") or str(index)
        caller.msg(f"[{selector}] {option['label']}")


def _node_content(node: dict[str, object], context: RuntimeContext):
    """Materialize visible dialogue content from a compiled node program."""

    if "program" not in node:
        return (
            list(node.get("say", [])),
            _visible_options(node.get("options", []), context),
            list(node.get("actions", [])),
        )
    says: list[str] = []
    options: list[dict[str, object]] = []
    actions: list[object] = []

    def collect(program) -> None:
        for step in program or []:
            if isinstance(step, dict) and step.get("op") == "if":
                selected = step.get("else", [])
                for branch in step.get("branches", []):
                    if evaluate_condition(branch.get("condition"), context):
                        selected = branch.get("then", [])
                        break
                collect(selected)
                continue
            if isinstance(step, list) and step:
                if step[0] == "say":
                    says.append(str(step[1]))
                    continue
                if step[0] == "option":
                    condition = step[4] if len(step) > 4 else None
                    if evaluate_condition(condition, context):
                        options.append(
                            {
                                "id": step[1],
                                "label": step[2],
                                "hotkey": step[3],
                                "condition": condition,
                                "target": step[5],
                            }
                        )
                    continue
            actions.append(step)

    collect(node.get("program", []))
    return says, options, actions


def _store_session(caller, state: dict[str, object]) -> None:
    setattr(caller.ndb, SESSION_KEY, state)


def _clear_session(caller) -> None:
    setattr(caller.ndb, SESSION_KEY, {})
