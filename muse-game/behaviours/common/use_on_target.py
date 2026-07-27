"""Runtime handler for compiled two-object MuseLang rules."""

from __future__ import annotations

from evennia import CmdSet

from commands.command import Command

from .action_eval import execute_program
from .metadata_access import args_match_object, get_macro_rules, object_tokens, resolve_accessible_object
from .runtime_context import RuntimeContext


BEHAVIOUR_PATH = "behaviours.common.use_on_target.UseOnTargetCmdSet"


def _make_command(rules: list[dict[str, object]]) -> type[Command]:
    verb = str(rules[0].get("verb") or "use")

    class CmdUseOnTarget(Command):
        """Execute one compiled MuseLang two-object rule."""

        def func(self) -> None:
            parsed = _parse_arguments(self.args, self.obj, rules)
            if parsed is None:
                prepositions = sorted({str(rule.get("preposition") or "on") for rule in rules})
                prep = prepositions[0] if len(prepositions) == 1 else "on/to"
                self.caller.msg(f"Try '{verb} <item> {prep} {getattr(self.obj, 'key', 'target')}'.")
                return
            direct_name, preposition = parsed
            context = RuntimeContext(caller=self.caller, obj=self.obj, verb=verb, raw_args=self.args)
            direct_obj = resolve_accessible_object(context, direct_name)
            if direct_obj is None:
                self.caller.msg(f"You cannot find {direct_name}.")
                return
            for rule in rules:
                if str(rule.get("preposition") or "on").casefold() != preposition.casefold():
                    continue
                if str(rule.get("direct_object") or "").casefold() not in object_tokens(direct_obj):
                    continue
                context.direct_obj = direct_obj
                context.indirect_obj = self.obj
                execute_program(rule.get("program", []), context)
                return
            self.caller.msg(f"That does not seem useful to {verb} here.")

    CmdUseOnTarget.__name__ = "Cmd" + "".join(part[:1].upper() + part[1:] for part in verb.split("_"))
    CmdUseOnTarget.key = verb
    CmdUseOnTarget.aliases = []
    CmdUseOnTarget.help_category = "Interactions"
    return CmdUseOnTarget


class UseOnTargetCmdSet(CmdSet):
    """CmdSet exposing compiled `verb X on/to Y` rules."""

    key = "UseOnTargetCmdSet"
    priority = 1

    def at_cmdset_creation(self) -> None:
        obj = self.cmdsetobj
        if obj is None:
            return
        by_verb: dict[str, list[dict[str, object]]] = {}
        for rule in get_macro_rules(obj):
            if rule.get("handler") == BEHAVIOUR_PATH:
                by_verb.setdefault(str(rule.get("verb") or "use"), []).append(rule)
        for rules in by_verb.values():
            self.add(_make_command(rules)())


def _parse_arguments(
    args: str,
    target: object,
    rules: list[dict[str, object]],
) -> tuple[str, str] | None:
    text = (args or "").strip()
    lowered = text.casefold()
    for preposition in {str(rule.get("preposition") or "on") for rule in rules}:
        marker = f" {preposition.casefold()} "
        index = lowered.find(marker)
        if index < 0:
            continue
        direct = text[:index].strip()
        target_text = text[index + len(marker) :].strip()
        matched, remaining = args_match_object(target_text, target)
        if direct and matched and not remaining:
            return direct, preposition
    return None
