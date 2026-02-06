from __future__ import annotations

from app.orchestrator.contracts import Node, NodeResult, RunContext
from app.services.rag_service import RAGService


class RAGRetrieve(Node):
    def __init__(self, rag_service: RAGService) -> None:
        self._rag_service = rag_service

    async def run(self, ctx: RunContext) -> NodeResult:
        if not ctx.kb_id:
            return NodeResult()
        answer, citations = self._rag_service.query(ctx.kb_id, ctx.message, ctx.policies.get("roles", []))
        return NodeResult(answer=answer, rag_context=citations)
