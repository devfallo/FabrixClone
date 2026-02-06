from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.models.schemas import Citation, ToolRunRequest


@dataclass
class RunContext:
    session_id: str
    conversation_id: str
    agent_id: str
    user_id: str
    tenant_id: str
    message: str
    ui_state: Dict[str, Any]
    policies: Dict[str, Any]
    tool_catalog: List[str]
    kb_id: Optional[str] = None
    trace_id: Optional[str] = None


@dataclass
class NodeResult:
    state_patch: Dict[str, Any] = field(default_factory=dict)
    actions_requested: List[ToolRunRequest] = field(default_factory=list)
    rag_context: List[Citation] = field(default_factory=list)
    answer: str | None = None
    events: List[str] = field(default_factory=list)


class Node:
    async def run(self, ctx: RunContext) -> NodeResult:
        raise NotImplementedError
