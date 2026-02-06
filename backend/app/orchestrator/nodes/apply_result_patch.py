from __future__ import annotations

from app.orchestrator.contracts import Node, NodeResult, RunContext
from app.services.tool_service import ToolService


class ApplyActionResultPatch(Node):
    def __init__(self, tool_service: ToolService) -> None:
        self._tool_service = tool_service

    async def run(self, ctx: RunContext) -> NodeResult:
        if not ctx.trace_id:
            return NodeResult()
        patches = {}
        for result in self._tool_service.list_results(ctx.trace_id):
            patches.update(result.ui_state_patch)
        if patches:
            return NodeResult(state_patch=patches)
        return NodeResult()
