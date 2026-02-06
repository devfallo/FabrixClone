from __future__ import annotations

from typing import Dict, List

from app.models.schemas import RoleCreateRequest, UsageStats, UserCreateRequest


class AdminService:
    def __init__(self) -> None:
        self._roles: Dict[str, List[str]] = {}
        self._users: Dict[str, List[str]] = {}
        self._usage = {"tool_runs": 0, "rag_queries": 0, "policy_violations": 0}

    def create_role(self, request: RoleCreateRequest) -> None:
        self._roles[request.role_name] = request.permissions

    def create_user(self, request: UserCreateRequest) -> None:
        self._users[request.user_id] = request.roles

    def user_permissions(self, user_id: str) -> List[str]:
        perms: List[str] = []
        roles = self._users.get(user_id, [])
        for role in roles:
            perms.extend(self._roles.get(role, []))
        return perms

    def increment_usage(self, key: str) -> None:
        if key in self._usage:
            self._usage[key] += 1

    def record_policy_violation(self) -> None:
        self._usage["policy_violations"] += 1

    def usage_stats(self) -> UsageStats:
        return UsageStats(**self._usage)
