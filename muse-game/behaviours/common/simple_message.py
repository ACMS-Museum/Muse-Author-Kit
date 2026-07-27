"""Reusable command-set for declarative, text-only interactions."""

from __future__ import annotations

from typing import Any

from evennia import CmdSet

from commands.command import Command

from .metadata_access import args_match_object, get_interactions

BEHAVIOUR_PATH = "behaviours.common.simple_message.SimpleMessage"

def _interaction_value(interaction: Any, key: str, default: Any = None) -> Any:
    if isinstance(interaction, dict):
        return interaction.get(key, default)
    return getattr(interaction, key, default)


def _interaction_records(obj: Any) -> list[dict[str, Any]]:
    """Return interaction metadata stored on an object, if present."""

    return get_interactions(obj)


def _command_class_name(interaction: dict[str, Any]) -> str:
    raw_name = str(_interaction_value(interaction, "id") or _interaction_value(interaction, "verb") or "message")
    parts = [part for part in raw_name.replace("-", "_").split("_") if part]
    camel = "".join(part[:1].upper() + part[1:] for part in parts) or "Message"
    return f"Cmd{camel}"


def _make_command(interaction: dict[str, Any]) -> type[Command]:
    key = str(_interaction_value(interaction, "verb") or _interaction_value(interaction, "id") or "message")
    aliases = list(_interaction_value(interaction, "aliases", []) or [])
    message = _interaction_value(interaction, "message")
    hint = _interaction_value(interaction, "hint")

    class CmdInteractionMessage(Command):
        """Command that sends the configured message for one interaction."""

        def func(self) -> None:
            matched, _remaining = args_match_object(self.args, self.obj)
            if not matched:
                self.caller.msg(f"You cannot {key} that.")
                return
            if message is not None:
                self.caller.msg(str(message))
                return
            if hint is not None:
                self.caller.msg(str(hint))
                return
            self.caller.msg(f"{getattr(self.obj, 'key', 'That')} does nothing.")

    CmdInteractionMessage.__name__ = _command_class_name(interaction)
    CmdInteractionMessage.key = key
    CmdInteractionMessage.aliases = aliases
    CmdInteractionMessage.help_category = "Interactions"
    return CmdInteractionMessage


class SimpleMessage(CmdSet):
    """CmdSet that exposes declarative interaction messages as commands."""

    key = "SimpleMessage"
    priority = 1

    def at_cmdset_creation(self) -> None:
        obj = self.cmdsetobj
        if obj is None:
            return

        for interaction in _interaction_records(obj):
            if interaction.get("behaviour") == BEHAVIOUR_PATH:
                self.add(_make_command(interaction)())
