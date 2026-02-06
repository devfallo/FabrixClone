from __future__ import annotations

from app.orchestrator.contracts import Node, NodeResult, RunContext


class AnswerSynthesize(Node):
    async def run(self, ctx: RunContext) -> NodeResult:
        if ctx.policies.get("intent") == "tool":
            return NodeResult(answer="Tool action requested. Awaiting UI execution.")
        if ctx.policies.get("rag_answer"):
            return NodeResult(answer=ctx.policies["rag_answer"], rag_context=ctx.policies.get("rag_citations", []))
        return NodeResult(answer="Acknowledged. Let me know if you need help with data or actions.")
