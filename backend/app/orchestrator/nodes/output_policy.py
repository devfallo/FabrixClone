from __future__ import annotations

from app.orchestrator.contracts import Node, NodeResult, RunContext
from app.services.admin_service import AdminService
from app.services.policy_service import PolicyService


class OutputPolicyCheck(Node):
    def __init__(self, policy_service: PolicyService, admin_service: AdminService) -> None:
        self._policy_service = policy_service
        self._admin_service = admin_service

    async def run(self, ctx: RunContext) -> NodeResult:
        answer = ctx.policies.get("answer", "")
        citations = ctx.policies.get("citations", 0)
        _, message, violated = self._policy_service.check_output(answer, citations)
        if violated:
            self._admin_service.record_policy_violation()
        if message:
            return NodeResult(events=[message])
        return NodeResult()
