"""Runtime handler for compiled conditional MuseLang verbs."""

from __future__ import annotations

from evennia import CmdSet

from commands.command import Command

from .action_eval import execute_program
from .metadata_access import args_match_object, get_interactions
from .runtime_context import RuntimeContext


BEHAVIOUR_PATH = "behaviours.common.conditional_verbs.ConditionalVerbCmdSet"


def _command_class_name(interaction: dict[str, object]) -> str:
    raw_name = str(interaction.get("id") or interaction.get("verb") or "conditional")
    return "Cmd" + "".join(part[:1].upper() + part[1:] for part in raw_name.replace("-", "_").split("_") if part)


def _make_command(interaction: dict[str, object]) -> type[Command]:
    verb = str(interaction.get("verb") or interaction.get("id") or "action")
    aliases = list(interaction.get("aliases", []) or [])
    config = interaction.get("config", {}) or {}

    class CmdConditionalVerb(Command):
        """Execute one compiled MuseLang conditional verb."""

        def func(self) -> None:
            matched, remaining = args_match_object(self.args, self.obj)
            if not matched:
                self.caller.msg(f"You cannot {verb} that.")
                return
            context = RuntimeContext(caller=self.caller, obj=self.obj, verb=verb, raw_args=remaining)
            execute_program(config.get("program", []), context)

    CmdConditionalVerb.__name__ = _command_class_name(interaction)
    CmdConditionalVerb.key = verb
    CmdConditionalVerb.aliases = aliases
    CmdConditionalVerb.help_category = "Interactions"
    return CmdConditionalVerb


class ConditionalVerbCmdSet(CmdSet):
    """CmdSet exposing compiled conditional MuseLang interactions."""

    key = "ConditionalVerbCmdSet"
    priority = 1

    def at_cmdset_creation(self) -> None:
        obj = self.cmdsetobj
        if obj is None:
            return
        for interaction in get_interactions(obj):
            if interaction.get("behaviour") == BEHAVIOUR_PATH:
                self.add(_make_command(interaction)())
