from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    session_id: str
    conversation_id: str
    agent_id: str
    user_id: str
    tenant_id: str
    message: str


class Citation(BaseModel):
    doc_id: str
    title: str
    page: Optional[int] = None
    snippet: Optional[str] = None


class ToolRunRequest(BaseModel):
    run_id: str
    action_id: str
    tool: str
    args: Dict[str, Any]


class ToolRunResult(BaseModel):
    run_id: str
    action_id: str
    status: str
    output: Dict[str, Any] = Field(default_factory=dict)
    ui_state_patch: Dict[str, Any] = Field(default_factory=dict)


class ChatMessageResponse(BaseModel):
    run_id: str
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    tool_runs: List[ToolRunRequest] = Field(default_factory=list)


class UIStatePatchRequest(BaseModel):
    session_id: str
    ui_state_patch: Dict[str, Any]
    version: int


class UIStatePatchResponse(BaseModel):
    session_id: str
    version: int
    updated_at: datetime


class ToolManifest(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    permissions: List[str] = Field(default_factory=list)
    timeout_ms: int = 30000
    rate_limit: int = 100
    audit_tags: List[str] = Field(default_factory=list)


class KnowledgeBaseCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    acl: List[str] = Field(default_factory=list)


class KnowledgeBaseDocumentRequest(BaseModel):
    title: str
    text: str
    source_uri: Optional[str] = None
    page: Optional[int] = None
    acl: List[str] = Field(default_factory=list)


class RAGQueryRequest(BaseModel):
    kb_id: str
    query: str
    roles: List[str] = Field(default_factory=list)


class RAGQueryResponse(BaseModel):
    answer: str
    citations: List[Citation] = Field(default_factory=list)


class AssetCreateRequest(BaseModel):
    asset_type: str
    name: str
    version: str
    payload: Dict[str, Any]
    status: str = "draft"


class AssetResponse(BaseModel):
    id: str
    asset_type: str
    name: str
    version: str
    payload: Dict[str, Any]
    status: str


class UserCreateRequest(BaseModel):
    user_id: str
    tenant_id: str
    roles: List[str] = Field(default_factory=list)


class RoleCreateRequest(BaseModel):
    role_name: str
    permissions: List[str] = Field(default_factory=list)


class PolicyEvent(BaseModel):
    event_id: str
    policy: str
    action: str
    message: str
    created_at: datetime


class UsageStats(BaseModel):
    tool_runs: int
    rag_queries: int
    policy_violations: int
