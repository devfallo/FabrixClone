from __future__ import annotations

import uuid
from typing import Any, Dict, List

from app.models.schemas import ChatMessageResponse
from app.orchestrator.contracts import NodeResult, RunContext
from app.orchestrator.nodes.answer_synthesize import AnswerSynthesize
from app.orchestrator.nodes.apply_result_patch import ApplyActionResultPatch
from app.orchestrator.nodes.input_policy import InputPolicyCheck
from app.orchestrator.nodes.intent_classify import IntentClassify
from app.orchestrator.nodes.output_policy import OutputPolicyCheck
from app.orchestrator.nodes.rag_retrieve import RAGRetrieve
from app.orchestrator.nodes.request_tool import RequestToolExecution
from app.services.policy_service import PolicyService
from app.services.rag_service import RAGService
from app.services.tool_service import ToolService


class OrchestratorEngine:
    def __init__(self, policy_service: PolicyService, tool_service: ToolService, rag_service: RAGService) -> None:
        self._policy_service = policy_service
        self._tool_service = tool_service
        self._rag_service = rag_service

    async def run(self, ctx: RunContext) -> ChatMessageResponse:
        run_id = ctx.trace_id or str(uuid.uuid4())
        ctx.trace_id = run_id
        combined_actions: List[Any] = []
        citations = []
        answer = ""
        state_patch: Dict[str, Any] = {}
        events: List[str] = []

        nodes = [
            InputPolicyCheck(self._policy_service),
            IntentClassify(),
            RequestToolExecution(self._tool_service),
            ApplyActionResultPatch(self._tool_service),
            RAGRetrieve(self._rag_service),
            AnswerSynthesize(),
            OutputPolicyCheck(self._policy_service),
        ]

        for node in nodes:
            result = await node.run(ctx)
            self._merge_result(result, state_patch, combined_actions, citations, events)
            if result.answer:
                answer = result.answer
            if "intent" in result.state_patch:
                ctx.policies["intent"] = result.state_patch["intent"]
            if result.rag_context:
                ctx.policies["rag_answer"] = result.answer
                ctx.policies["rag_citations"] = result.rag_context
            if result.answer:
                ctx.policies["answer"] = result.answer
                ctx.policies["citations"] = len(result.rag_context)
            if "halt" in result.events:
                break

        return ChatMessageResponse(run_id=run_id, answer=answer, citations=citations, tool_runs=combined_actions)

    def _merge_result(
        self,
        result: NodeResult,
        state_patch: Dict[str, Any],
        actions: List[Any],
        citations: List[Any],
        events: List[str],
    ) -> None:
        if result.state_patch:
            state_patch.update(result.state_patch)
        if result.actions_requested:
            actions.extend(result.actions_requested)
        if result.rag_context:
            citations.extend(result.rag_context)
        if result.events:
            events.extend(result.events)
