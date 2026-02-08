from __future__ import annotations

from app.orchestrator.contracts import Node, NodeResult, RunContext
from app.services.admin_service import AdminService
from app.services.policy_service import PolicyService


class InputPolicyCheck(Node):
    def __init__(self, policy_service: PolicyService, admin_service: AdminService) -> None:
        self._policy_service = policy_service
        self._admin_service = admin_service

    async def run(self, ctx: RunContext) -> NodeResult:
        allowed, message, violated = self._policy_service.check_input(ctx.message)
        if violated:
            self._admin_service.record_policy_violation()
        if not allowed:
            return NodeResult(answer=message, events=["halt"])
        if message:
            return NodeResult(events=[message])
        return NodeResult()
