from __future__ import annotations

from fastapi import FastAPI

from app.api import admin, assets, chat, rag, tool_runs, ui_state
from app.config import settings
from app.orchestrator.engine import OrchestratorEngine
from app.services.admin_service import AdminService
from app.services.asset_service import AssetService
from app.services.policy_service import PolicyService
from app.services.rag_service import RAGService
from app.services.state_service import StateService
from app.services.tool_service import ToolService


app = FastAPI(title=settings.app_name)

state_service = StateService()
policy_service = PolicyService()
rag_service = RAGService()
asset_service = AssetService()
admin_service = AdminService()
tool_service = ToolService()
engine = OrchestratorEngine(policy_service, tool_service, rag_service)

app.include_router(chat.router)
app.include_router(ui_state.router)
app.include_router(tool_runs.router)
app.include_router(rag.router)
app.include_router(assets.router)
app.include_router(admin.router)
