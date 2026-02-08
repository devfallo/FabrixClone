from __future__ import annotations

from typing import Any, Dict, List

from app.models.schemas import AuditLogEntry
from app.observability.audit import AuditLogger


class AuditService:
    def __init__(self) -> None:
        self._logger = AuditLogger()

    def log(self, actor: str, action: str, target: str, meta: Dict[str, Any]) -> None:
        self._logger.log(actor=actor, action=action, target=target, meta=meta)

    def list_entries(self) -> List[AuditLogEntry]:
        return [AuditLogEntry(**entry) for entry in self._logger.list_events()]
