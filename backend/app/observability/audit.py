from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


class AuditLogger:
    def __init__(self) -> None:
        self._events: List[Dict[str, Any]] = []

    def log(self, actor: str, action: str, target: str, meta: Dict[str, Any]) -> None:
        self._events.append(
            {
                "actor": actor,
                "action": action,
                "target": target,
                "meta": meta,
                "created_at": datetime.utcnow(),
            }
        )

    def list_events(self) -> List[Dict[str, Any]]:
        return list(self._events)
