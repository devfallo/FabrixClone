from __future__ import annotations

from typing import Dict


class MetricsRegistry:
    def __init__(self) -> None:
        self._counters: Dict[str, int] = {}

    def incr(self, name: str, amount: int = 1) -> None:
        self._counters[name] = self._counters.get(name, 0) + amount

    def get(self, name: str) -> int:
        return self._counters.get(name, 0)

    def snapshot(self) -> Dict[str, int]:
        return dict(self._counters)
