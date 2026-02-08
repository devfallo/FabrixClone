from __future__ import annotations

from app.orchestrator.contracts import Node, NodeResult, RunContext


class IntentClassify(Node):
    async def run(self, ctx: RunContext) -> NodeResult:
        message = ctx.message.lower()
        intent = "chat"
        if any(keyword in message for keyword in ["filter", "sort", "group"]):
            intent = "tool"
        elif any(keyword in message for keyword in ["rag", "document", "kb", "cite"]):
            intent = "rag"
        return NodeResult(state_patch={"intent": intent})
