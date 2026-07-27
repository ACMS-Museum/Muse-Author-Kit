"""Shared metadata access helpers for MuseLang runtime handlers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def _plain_value(value: Any) -> Any:
    """Detach Evennia's mutable saver wrappers from persisted metadata."""

    if isinstance(value, Mapping):
        return {key: _plain_value(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_plain_value(item) for item in value]
    return value


def get_muse_attribute(obj: Any, key: str, default: Any = None) -> Any:
    """Read an Evennia attribute in the `muse` category if available."""

    attributes = getattr(obj, "attributes", None)
    if attributes is not None:
        try:
            value = attributes.get(key, category="muse")
        except Exception:
            value = default
        else:
            if value is not None:
                return _plain_value(value)

    db = getattr(obj, "db", None)
    if db is not None:
        value = getattr(db, key, None)
        if value is not None:
            return _plain_value(value)
    return default


def get_interactions(obj: Any) -> list[dict[str, Any]]:
    """Return compiled interaction metadata for an object."""

    records = get_muse_attribute(obj, "interactions", default=[])
    if isinstance(records, dict):
        return [records]
    if isinstance(records, list):
        return [record for record in records if isinstance(record, dict)]
    return []


def get_dialogue(obj: Any) -> dict[str, Any] | None:
    """Return compiled dialogue metadata for an object."""

    dialogue = get_muse_attribute(obj, "dialogue")
    if isinstance(dialogue, dict):
        return dialogue
    return None


def get_macro_rules(obj: Any) -> list[dict[str, Any]]:
    """Return compiled rule metadata for an object."""

    rules = get_muse_attribute(obj, "macro_rules", default=[])
    if isinstance(rules, dict):
        return [rules]
    if isinstance(rules, list):
        return [rule for rule in rules if isinstance(rule, dict)]
    return []


def read_muse_state(obj: Any, key: str, default: Any = None) -> Any:
    """Read mutable Muse state, preferring the namespaced attribute."""

    return get_muse_attribute(obj, key, default)


def write_muse_state(obj: Any, key: str, value: Any) -> None:
    """Write mutable Muse state into the `muse` attribute category."""

    attributes = getattr(obj, "attributes", None)
    if attributes is not None:
        add = getattr(attributes, "add", None)
        if callable(add):
            add(key, value, category="muse")
            return
    db = getattr(obj, "db", None)
    if db is not None:
        setattr(db, key, value)


def interaction_matches(interaction: dict[str, Any], verb: str) -> bool:
    """Return `True` if an interaction matches a verb or alias."""

    verb_lower = verb.lower()
    primary = str(interaction.get("verb", "")).lower()
    if primary == verb_lower:
        return True
    aliases = interaction.get("aliases", []) or []
    return any(str(alias).lower() == verb_lower for alias in aliases)


def find_interaction(obj: Any, verb: str, behaviour_path: str | None = None) -> dict[str, Any] | None:
    """Find one interaction matching a verb and optional behaviour."""

    for interaction in get_interactions(obj):
        if not interaction_matches(interaction, verb):
            continue
        if behaviour_path is not None and interaction.get("behaviour") != behaviour_path:
            continue
        return interaction
    return None


def object_tokens(obj: Any) -> set[str]:
    """Return the likely textual tokens by which an object may be referenced."""

    tokens: set[str] = set()
    key = getattr(obj, "key", None)
    if isinstance(key, str) and key:
        tokens.add(key.lower())
    aliases_handler = getattr(obj, "aliases", None)
    if aliases_handler is not None:
        try:
            for alias in aliases_handler.all():
                if isinstance(alias, str) and alias:
                    tokens.add(alias.lower())
        except Exception:
            pass
    return tokens


def args_match_object(args: str, obj: Any) -> tuple[bool, str]:
    """Strip an optional target-object prefix or suffix from command args."""

    text = (args or "").strip()
    if not text:
        return True, ""
    tokens = object_tokens(obj)
    if not tokens:
        return True, text
    lowered = text.lower()
    if lowered in tokens:
        return True, ""
    for token in sorted(tokens, key=len, reverse=True):
        if lowered.startswith(token + " "):
            return True, text[len(token) :].strip()
        if lowered.endswith(" " + token):
            return True, text[: -len(token)].strip()
    return False, text


def resolve_accessible_object(context: Any, name: str) -> Any | None:
    """Resolve an object visible to the current runtime command."""

    lowered = name.strip().lower()
    if lowered in {"caller", "player"}:
        return getattr(context, "caller", None)
    if lowered == "this":
        return getattr(context, "obj", None)
    for candidate in (
        getattr(context, "direct_obj", None),
        getattr(context, "indirect_obj", None),
        getattr(context, "obj", None),
    ):
        if candidate is not None and lowered in object_tokens(candidate):
            return candidate
    caller = getattr(context, "caller", None)
    room = getattr(caller, "location", None)
    search_space = list(getattr(caller, "contents", []) or [])
    if room is not None:
        search_space.extend(getattr(room, "contents", []) or [])
    for candidate in search_space:
        if lowered in object_tokens(candidate):
            return candidate
    search = getattr(caller, "search", None)
    if callable(search):
        try:
            result = search(name, global_search=True, quiet=True)
        except (TypeError, AttributeError):
            result = None
        if isinstance(result, (list, tuple)):
            return result[0] if len(result) == 1 else None
        if result is not None:
            return result
    return None

