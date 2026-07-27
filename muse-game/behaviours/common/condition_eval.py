"""Condition evaluation for MuseLang runtime handlers."""

from __future__ import annotations

from typing import Any

from .metadata_access import object_tokens, read_muse_state, resolve_accessible_object


def evaluate_condition(expr: Any, context: Any) -> bool:
    """Evaluate a compiled MuseLang condition expression."""

    if expr is None:
        return True
    if not isinstance(expr, list) or not expr:
        return bool(expr)

    op = expr[0]
    if op == "and":
        return evaluate_condition(expr[1], context) and evaluate_condition(expr[2], context)
    if op == "or":
        return evaluate_condition(expr[1], context) or evaluate_condition(expr[2], context)
    if op == "not":
        return not evaluate_condition(expr[1], context)
    if op == "have":
        return _caller_has(context, expr[1] if len(expr) > 1 else "")
    if op == "flag":
        return bool(_read_flag(context, expr[1] if len(expr) > 1 else ""))
    if op == "topic":
        return _has_topic(context, expr[1] if len(expr) > 1 else "")
    if op == "selected":
        return (getattr(context, "selected_option", None) or "").lower() == str(expr[1]).lower()
    if op == "truthy":
        return bool(_resolve_reference(context, expr[1] if len(expr) > 1 else ""))
    if op == "compare":
        return _compare(_resolve_reference(context, expr[1]), expr[2], _coerce_value(expr[3]))
    return False


def _caller_has(context: Any, identifier: str) -> bool:
    caller = getattr(context, "caller", None)
    for item in getattr(caller, "contents", []) or []:
        if identifier.lower() in object_tokens(item):
            return True
    return False


def _read_flag(context: Any, name: str) -> Any:
    caller = getattr(context, "caller", None)
    return read_muse_state(caller, name)


def _has_topic(context: Any, topic: str) -> bool:
    caller = getattr(context, "caller", None)
    topics = getattr(getattr(caller, "ndb", None), "muselang_topics", None)
    if isinstance(topics, set):
        return topic in topics
    return False


def _resolve_reference(context: Any, reference: str) -> Any:
    if "." not in reference:
        return _read_simple_reference(context, reference)
    noun_ref, attr_name = reference.split(".", 1)
    obj = _resolve_noun(context, noun_ref)
    if obj is None:
        return None
    return read_muse_state(obj, attr_name)


def _read_simple_reference(context: Any, reference: str) -> Any:
    if reference == "caller":
        return getattr(context, "caller", None)
    return _resolve_reference(context, f"{getattr(getattr(context, 'obj', None), 'key', 'obj')}.{reference}")


def _resolve_noun(context: Any, noun_ref: str) -> Any | None:
    return resolve_accessible_object(context, noun_ref)


def _coerce_value(value: Any) -> Any:
    if isinstance(value, str):
        lowered = value.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value
    return value


def _compare(left: Any, operator: str, right: Any) -> bool:
    if operator == "==":
        return left == right
    if operator == "!=":
        return left != right
    try:
        if operator == ">=":
            return left >= right
        if operator == "<=":
            return left <= right
        if operator == ">":
            return left > right
        if operator == "<":
            return left < right
    except TypeError:
        return False
    return False

