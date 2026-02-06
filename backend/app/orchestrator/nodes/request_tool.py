from __future__ import annotations

from app.orchestrator.contracts import Node, NodeResult, RunContext
from app.services.tool_service import ToolService


class RequestToolExecution(Node):
    def __init__(self, tool_service: ToolService) -> None:
        self._tool_service = tool_service

    async def run(self, ctx: RunContext) -> NodeResult:
        message = ctx.message.lower()
        tool_name = ""
        args = {"gridId": "main"}
        if "filter" in message:
            tool_name = "grid.setFilter"
            args["filters"] = [{"field": "status", "op": "eq", "value": "active"}]
        elif "sort" in message:
            tool_name = "grid.setSort"
            args["sorts"] = [{"field": "created_at", "dir": "desc"}]
        elif "group" in message:
            tool_name = "grid.setGroup"
            args["groups"] = ["category"]
        if not tool_name:
            return NodeResult()
        action = self._tool_service.create_action(tool_name, args, run_id=ctx.trace_id or "")
        return NodeResult(actions_requested=[action])
