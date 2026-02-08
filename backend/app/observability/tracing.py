from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class TraceEvent:
    name: str
    timestamp: datetime
    details: dict


def create_event(name: str, details: dict) -> TraceEvent:
    return TraceEvent(name=name, timestamp=datetime.utcnow(), details=details)
