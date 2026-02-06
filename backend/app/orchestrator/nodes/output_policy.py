from __future__ import annotations

from app.orchestrator.contracts import Node, NodeResult, RunContext
from app.services.policy_service import PolicyService


class OutputPolicyCheck(Node):
    def __init__(self, policy_service: PolicyService) -> None:
        self._policy_service = policy_service

    async def run(self, ctx: RunContext) -> NodeResult:
        answer = ctx.policies.get("answer", "")
        citations = ctx.policies.get("citations", 0)
        _, message = self._policy_service.check_output(answer, citations)
        if message:
            return NodeResult(events=[message])
        return NodeResult()
