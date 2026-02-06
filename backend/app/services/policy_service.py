from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import List

from app.models.schemas import PolicyEvent


class PolicyService:
    def __init__(self) -> None:
        self._events: List[PolicyEvent] = []
        self._pii_patterns = [
            re.compile(r"\b\d{6}-\d{7}\b"),
            re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            re.compile(r"\b\d{2,3}-\d{3,4}-\d{4}\b"),
        ]
        self._injection_patterns = [
            re.compile(r"ignore (all|previous) instructions", re.IGNORECASE),
            re.compile(r"system prompt", re.IGNORECASE),
        ]

    def check_input(self, message: str) -> tuple[bool, str]:
        for pattern in self._pii_patterns:
            if pattern.search(message):
                self._record("input", "block", "PII detected")
                return False, "Input blocked due to PII policy."
        for pattern in self._injection_patterns:
            if pattern.search(message):
                self._record("input", "redact", "Prompt injection detected")
                return True, "Potential injection detected; proceeding with caution."
        return True, ""

    def check_output(self, answer: str, citations: int) -> tuple[bool, str]:
        if citations == 0:
            self._record("output", "redact", "No citations present")
            return True, "Answer generated without citations; confidence reduced."
        return True, ""

    def _record(self, policy: str, action: str, message: str) -> None:
        self._events.append(
            PolicyEvent(
                event_id=str(uuid.uuid4()),
                policy=policy,
                action=action,
                message=message,
                created_at=datetime.utcnow(),
            )
        )

    def list_events(self) -> List[PolicyEvent]:
        return list(self._events)
