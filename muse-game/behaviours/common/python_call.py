"""Runtime wrapper for compiled MuseLang explicit Python calls."""

from __future__ import annotations

from evennia import CmdSet

from commands.command import Command

from .action_eval import execute_program
from .metadata_access import args_match_object, get_interactions
from .runtime_context import RuntimeContext


BEHAVIOUR_PATH = "behaviours.common.python_call.PythonCallCmdSet"


def _make_command(interaction: dict[str, object]) -> type[Command]:
    verb = str(interaction.get("verb") or interaction.get("id") or "call")
    aliases = list(interaction.get("aliases", []) or [])
    config = interaction.get("config", {}) or {}

    class CmdPythonCall(Command):
        """Execute one compiled explicit Python call interaction."""

        def func(self) -> None:
            matched, remaining = args_match_object(self.args, self.obj)
            if not matched:
                self.caller.msg(f"You cannot {verb} that.")
                return
            context = RuntimeContext(caller=self.caller, obj=self.obj, verb=verb, raw_args=remaining)
            execute_program([["call", config.get("call_target")]], context)

    CmdPythonCall.__name__ = "Cmd" + "".join(part[:1].upper() + part[1:] for part in verb.split("_"))
    CmdPythonCall.key = verb
    CmdPythonCall.aliases = aliases
    CmdPythonCall.help_category = "Interactions"
    return CmdPythonCall


class PythonCallCmdSet(CmdSet):
    """CmdSet exposing compiled explicit Python-call interactions."""

    key = "PythonCallCmdSet"
    priority = 1

    def at_cmdset_creation(self) -> None:
        obj = self.cmdsetobj
        if obj is None:
            return
        for interaction in get_interactions(obj):
            if interaction.get("behaviour") == BEHAVIOUR_PATH:
                self.add(_make_command(interaction)())
