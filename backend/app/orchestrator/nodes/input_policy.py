from __future__ import annotations

from app.orchestrator.contracts import Node, NodeResult, RunContext
from app.services.policy_service import PolicyService


class InputPolicyCheck(Node):
    def __init__(self, policy_service: PolicyService) -> None:
        self._policy_service = policy_service

    async def run(self, ctx: RunContext) -> NodeResult:
        allowed, message = self._policy_service.check_input(ctx.message)
        if not allowed:
            return NodeResult(answer=message, events=["halt"])
        if message:
            return NodeResult(events=[message])
        return NodeResult()
