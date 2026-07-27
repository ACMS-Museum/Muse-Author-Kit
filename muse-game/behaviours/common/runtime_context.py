"""Runtime context container for MuseLang handlers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class RuntimeContext:
    """Shared runtime state for one MuseLang command execution."""

    caller: Any
    obj: Any
    verb: str
    raw_args: str = ""
    direct_obj: Any | None = None
    indirect_obj: Any | None = None
    selected_option: str | None = None
    dialogue_state: dict[str, Any] | None = None
    loop_budget: int = 1000

    @property
    def room(self) -> Any | None:
        return getattr(self.caller, "location", None)

