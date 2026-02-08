from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


class StateService:
    def __init__(self) -> None:
        self._latest_state: Dict[str, Dict[str, Any]] = {}
        self._versions: Dict[str, int] = {}
        self._events: Dict[str, List[Dict[str, Any]]] = {}

    def apply_patch(self, session_id: str, patch: Dict[str, Any], version: int) -> Dict[str, Any]:
        current = self._latest_state.get(session_id, {})
        merged = {**current, **patch}
        self._latest_state[session_id] = merged
        self._versions[session_id] = version
        event = {
            "patch": patch,
            "version": version,
            "updated_at": datetime.utcnow(),
        }
        self._events.setdefault(session_id, []).append(event)
        return event

    def get_state(self, session_id: str) -> Dict[str, Any]:
        return self._latest_state.get(session_id, {})

    def get_version(self, session_id: str) -> int:
        return self._versions.get(session_id, 0)

    def events(self, session_id: str) -> List[Dict[str, Any]]:
        return list(self._events.get(session_id, []))
