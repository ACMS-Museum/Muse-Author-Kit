"""Action execution for MuseLang runtime handlers."""

from __future__ import annotations

from typing import Any

from .metadata_access import resolve_accessible_object, write_muse_state


CALL_HANDLERS: dict[str, Any] = {}
ALLOWED_CALL_PREFIXES = ("behaviours.", "world.")


def register_call_handler(name: str, handler: Any) -> None:
    """Register a trusted explicit Python escape hatch."""

    CALL_HANDLERS[name] = handler


def execute_program(program: list[Any], context: Any) -> dict[str, Any]:
    """Execute a compiled MuseLang action program."""

    result: dict[str, Any] = {"ended": False, "goto": None}
    loop_budget = max(0, int(getattr(context, "loop_budget", 1000)))
    for step in program:
        if isinstance(step, dict) and step.get("op") == "if":
            branch_result = _execute_if(step, context)
            if branch_result.get("goto") is not None:
                result["goto"] = branch_result["goto"]
            if branch_result.get("ended"):
                result["ended"] = True
                return result
            continue
        if isinstance(step, dict) and step.get("op") in {"while", "until"}:
            loop_result = _execute_loop(step, context, loop_budget)
            if loop_result.get("goto") is not None:
                result["goto"] = loop_result["goto"]
            if loop_result.get("ended"):
                result["ended"] = True
                return result
            continue
        if not isinstance(step, list) or not step:
            continue
        opcode = step[0]
        if opcode == "say":
            context.caller.msg(str(step[1]))
        elif opcode == "hint":
            context.caller.msg(str(step[1]))
        elif opcode == "set":
            _set_value(context, str(step[1]), step[2] if len(step) > 2 else None)
        elif opcode == "move":
            _move_object(context, str(step[1]), str(step[2]))
        elif opcode == "give":
            _give_object(context, str(step[1]), str(step[2]))
        elif opcode == "show":
            _set_value(context, f"{step[1]}.hidden", False)
        elif opcode == "hide":
            _set_value(context, f"{step[1]}.hidden", True)
        elif opcode == "goto":
            result["goto"] = str(step[1])
            return result
        elif opcode == "call":
            _call_target(str(step[1]), context)
        elif opcode == "end":
            result["ended"] = True
            return result
    return result


def _execute_if(step: dict[str, Any], context: Any) -> dict[str, Any]:
    from .condition_eval import evaluate_condition

    for branch in step.get("branches", []):
        if evaluate_condition(branch.get("condition"), context):
            return execute_program(branch.get("then", []), context)
    return execute_program(step.get("else", []), context)


def _execute_loop(step: dict[str, Any], context: Any, loop_budget: int) -> dict[str, Any]:
    from .condition_eval import evaluate_condition

    remaining = loop_budget
    is_until = step.get("op") == "until"
    while remaining > 0:
        if not is_until and not evaluate_condition(step.get("condition"), context):
            break
        result = execute_program(step.get("body", []), context)
        if result.get("goto") is not None or result.get("ended"):
            return result
        remaining -= 1
        if is_until and evaluate_condition(step.get("condition"), context):
            break
    return {"ended": False, "goto": None}


def _set_value(context: Any, target: str, value: Any) -> None:
    obj_ref, _, attr_name = target.partition(".")
    obj = _resolve_named_object(context, obj_ref)
    if obj is None or not attr_name:
        return
    write_muse_state(obj, attr_name, value)


def _move_object(context: Any, object_id: str, location_id: str) -> None:
    obj = _resolve_named_object(context, object_id)
    location = _resolve_named_object(context, location_id)
    move_to = getattr(obj, "move_to", None) if obj is not None else None
    if callable(move_to) and location is not None:
        move_to(location, quiet=True)


def _give_object(context: Any, object_id: str, character_id: str) -> None:
    obj = _resolve_named_object(context, object_id)
    character = _resolve_named_object(context, character_id)
    move_to = getattr(obj, "move_to", None) if obj is not None else None
    if callable(move_to) and character is not None:
        move_to(character, quiet=True)


def _call_target(target: str, context: Any) -> None:
    handler = CALL_HANDLERS.get(target)
    if callable(handler):
        handler(context)
        return
    if not target.startswith(ALLOWED_CALL_PREFIXES):
        raise RuntimeError(f"MuseLang call target {target!r} is not approved")
    import importlib

    module_name, _, function_name = target.rpartition(".")
    if not module_name or not function_name:
        raise RuntimeError(f"Invalid MuseLang call target {target!r}")
    module = importlib.import_module(module_name)
    func = getattr(module, function_name, None)
    if not callable(func):
        raise RuntimeError(f"MuseLang call target {target!r} is not callable")
    func(context)


def _resolve_named_object(context: Any, name: str) -> Any | None:
    return resolve_accessible_object(context, name)

