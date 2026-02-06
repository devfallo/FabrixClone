# FABRIX-like AI Platform Implementation Design

## 1. 목표
### 1.1 제품 목표
기업용 AI 플랫폼(=FabriX 유사)으로 확장 가능한 기반 구축을 목표로 한다.

핵심 기능:

- Chat + Orchestrator(Agent Runtime)
- UI Action 실행(RealGrid/DevExtreme)
- RAG(출처 포함, ACL 기반 문서 접근제어)
- Policy(Security Filter: 입력/출력/프롬프트 인젝션)
- AI Store(Agent/Tool/Prompt/KB 자산화/버전관리)
- AI Lab(문서 적재/인덱싱/테스트)
- Admin(RBAC/감사로그/사용량/정책)
- OpenAPI(외부 시스템 연동)

### 1.2 설계 원칙

- Orchestrator 엔진을 교체 가능하게(LC ↔ LG)
- 모든 Tool(Action)을 Manifest(스키마) 기반 표준화
- 모든 실행 흐름은 Trace/Audit로 재현 가능해야 함
- 테넌트/권한/정책을 서버에서 강제(클라이언트 신뢰 X)

## 2. 전체 아키텍처
### 2.1 구성요소

Frontend

- Chat UI
- UIBridge(상태 전송/액션 디스패치)
- AdapterRegistry
- Grid Adapter(RealGrid/DevExtreme)

Backend (Python)

- API Gateway(FastAPI)
- Orchestrator Runtime(LangChain-based, graph-ready)
- Tool Service(UI Action orchestration)
- RAG Service(Index + Retrieve + Cite + ACL)
- Policy Service(Security Filter)
- Asset Service(AI Store)
- Admin Service(RBAC/Usage/Audit)
- Observability(Trace/Metric/Log)

Data

- PostgreSQL: 사용자/권한/자산/대화/감사/정책
- Redis: session state, checkpoints, locks, rate limit
- Vector DB: Qdrant(권장) 또는 pgvector
- Object Storage: 원문 파일/추출 텍스트/청크

## 3. 기술 스택 (Python 3.12.4)
### 3.1 런타임/프레임워크

- Python 3.12.4
- FastAPI + Uvicorn
- Pydantic v2
- SQLAlchemy 2.x + asyncpg
- Redis (redis-py)

### 3.2 LLM/Orchestration

- LangChain (core)
- LangGraph (optional/ready)
- OpenAI/Azure OpenAI connector는 “LLM Adapter” 레이어로 격리

> Python 3.12에서 일부 라이브러리 호환성 이슈가 있을 수 있으니, pyproject.toml로 버전 핀 고정 권장.

## 4. 모듈/폴더 구조

```
backend/
  app/
    main.py
    config.py

    api/
      chat.py
      ui_state.py
      tool_runs.py
      rag.py
      assets.py
      admin.py

    orchestrator/
      engine.py              # 인터페이스 + 실행 엔진 선택(LangChain/LangGraph)
      contracts.py           # RunContext, NodeResult 등 공통 DTO
      nodes/
        input_policy.py
        intent_classify.py
        plan_action.py
        request_tool.py
        apply_result_patch.py
        rag_retrieve.py
        answer_synthesize.py
        output_policy.py

    services/
      state_service.py       # session state store (redis+postgres event log)
      tool_service.py        # tool manifest, validation, permission
      rag_service.py         # index/retrieve/rerank/cite
      policy_service.py      # input/output filter, injection defense
      asset_service.py       # agents/tools/prompts/kb
      admin_service.py       # rbac, usage, audit

    models/
      db.py                  # SQLAlchemy models
      schemas.py             # Pydantic request/response

    infra/
      db_session.py
      redis.py
      vector_store.py
      object_store.py

    observability/
      tracing.py
      metrics.py
      audit.py
      logger.py
```

## 5. 핵심 도메인 모델
### 5.1 개념 모델

- Session: UI와 연결된 실행 컨텍스트(최신 ui_state 포함)
- Conversation: 사용자 대화 단위
- Run: 오케스트레이터 실행 1회(request_id/run_id)
- Tool(Action): UI 또는 외부 시스템에 수행시키는 명령
- Asset: Agent/Tool/Prompt/KB 등 자산(버전/권한/배포 상태 포함)
- Policy: 입력/출력/문서권한/툴권한 등 거버넌스 규칙

## 6. 오케스트레이션 설계 (LangChain-first, LangGraph-ready)
### 6.1 왜 LangChain으로 시작해도 되나?

초기 MVP에서 필요한 건 “노드 순차 실행 + 상태 patch + tool 결과 반영”인데,
이는 LangChain 구조(코드 기반 파이프라인)로 충분히 구현 가능.

대신 노드 인터페이스를 표준화해서, 이후 LangGraph로 옮길 때 노드를 그대로 재사용하도록 설계.

### 6.2 공통 실행 컨트랙트(필수)

- RunContext: session_id, conversation_id, agent_id, user_id, tenant_id, ui_state, policies, tool_catalog, kb_refs, trace_id 등
- Node: `async def run(ctx: RunContext) -> NodeResult`
- NodeResult: state_patch, actions_requested, rag_context, answer, events

LangGraph로 갈 때는 Node들을 graph node로 포장만 하면 됨.

### 6.3 표준 노드 체인 (FabriX 유사)

1. InputPolicyCheck
2. IntentClassify
3. PlanAction (필요하면 여러 action 생성)
4. RequestToolExecution (UI로 action 전송)
5. ApplyActionResultPatch (ui_state/도메인 state patch)
6. RAGRetrieve (ACL 필터 + cite)
7. AnswerSynthesize (출처 포함)
8. OutputPolicyCheck

## 7. Tool(Action) 시스템 설계 (UI Action 포함)
### 7.1 Tool Manifest 표준

모든 tool은 아래 정보를 필수로 가짐:

- name, description
- input_schema (JSON Schema)
- output_schema (JSON Schema)
- permissions (RBAC 코드)
- timeout_ms, rate_limit, audit_tags

### 7.2 Action 프로토콜

Request

```json
{
  "run_id": "r-001",
  "action_id": "a-123",
  "tool": "grid.setFilter",
  "args": { "gridId": "main", "filters": [ ... ] }
}
```

Result

```json
{
  "run_id": "r-001",
  "action_id": "a-123",
  "status": "ok",
  "output": { "applied": true, "rowsAffected": 120 },
  "ui_state_patch": { "grid.main.filter": { ... } }
}
```

### 7.3 실행 방식(권장)

- Chat UI ↔ Backend: WebSocket(SSE도 가능)
- action 전송/결과 수신은 **correlation(run_id/action_id)**로 묶음
- 서버는 action 스키마 검증 + 권한 검증 + 감사 로그를 강제

## 8. RAG 설계 (FabriX 유사)
### 8.1 인덱싱 파이프라인(AI Lab에서 수행)

Upload/Collect → Extract Text → Chunk → Embed → Vector Store 저장

저장 시 필수 메타:

- doc_id, title, source_uri, page/section, created_at, acl(권한)

### 8.2 질의 파이프라인(Chat에서 수행)

1. Query Rewrite(optional)
2. Retrieve(top-k, metadata filter)
3. ACL Filter(서버에서 강제)
4. Rerank(optional)
5. Cite 생성(문서명/페이지/스니펫)

### 8.3 출력 포맷(출처 포함)

```json
{
  "answer": "....",
  "citations": [
    {"doc_id":"D1","title":"HR Policy","page":3,"snippet":"..."}
  ]
}
```

## 9. Policy(Security Filter) 설계
### 9.1 입력 정책(Input Filter)

- PII 패턴(전화/주민/계좌 등) 탐지
- 기밀 키워드/사전 기반 차단 또는 마스킹
- prompt injection 방어 룰(“시스템 무시/정책 무시” 등)

### 9.2 출력 정책(Output Filter)

- 민감정보 마스킹
- 근거 없는 단정 제한(“출처 없으면 답변 강도 제한”)

정책 위반 시:

- block / redact / safe completion 중 정책 설정대로

## 10. AI Store(자산화) 설계
### 10.1 자산 타입

- Agent: system prompt + toolset + KB + model + policy profile
- Tool: manifest + version + permissions
- Prompt: template + variables + version
- KnowledgeBase: index config + ACL + version

### 10.2 라이프사이클

- Draft → Review → Published → Deprecated
- 버전관리: name@version
- 권한: 소유/공유/승인 워크플로우(옵션)

## 11. Admin 설계 (RBAC/Usage/Audit)
### 11.1 RBAC 최소 모델

- tenant → groups → roles → permissions
- Tool 실행 권한은 permissions로 통제

### 11.2 감사 로그(Audit)

누가/언제/무엇을:

- 대화 요청
- tool 실행 요청/결과
- KB 접근(문서/청크)
- 정책 위반 이벤트
- 자산 변경/배포

### 11.3 사용량(Usage)

- 토큰/비용(모델별)
- tool 실행 수/실패율/timeout
- RAG hit rate, cite rate, latency

## 12. API 설계(OpenAPI)
### 12.1 Chat

`POST /v1/chat/message`

req: session_id, conversation_id, agent_id, message

res: answer, citations, tool_runs, run_id

### 12.2 UI State

`POST /v1/ui/state`

req: session_id, ui_state_patch, version

### 12.3 Action Result

`POST /v1/tools/action-result`

req: run_id, action_id, status, output, ui_state_patch

### 12.4 RAG / KB / Assets / Admin

- `POST /v1/kb` / `POST /v1/kb/{id}/documents` / `POST /v1/rag/query`
- `POST /v1/assets/agents|tools|prompts`
- `POST /v1/admin/users|groups|roles|policies`
- `GET /v1/admin/usage`

## 13. DB 스키마(핵심 테이블)

Postgres

- tenants, users, groups, roles, permissions, user_roles, user_groups
- assets(공통), agent_configs, tool_manifests, prompt_templates, knowledge_bases
- conversations, messages
- ui_state_events(session_id, patch_json, version)
- tool_runs(run_id, action_id, tool, args, output, status, latency)
- audit_logs(actor, action, target, meta)
- kb_documents(doc meta + acl), kb_chunks(chunk meta + embedding ref)

Redis

- session latest state
- run checkpoints(선택)
- locks/rate limits

## 14. LangChain ↔ LangGraph 전환 전략
### 14.1 지금(LC)에서 반드시 지킬 것

- 노드 함수 시그니처 통일: `Node.run(ctx) -> NodeResult`
- state는 state_patch 이벤트로만 변경(immutable-like)
- run_id/action_id 기반 correlation 필수
- tool execution을 “노드”로 분리(나중에 그래프에서 반복/병렬화 가능)

### 14.2 나중(LG)로 갈 때 얻는 것

- 체크포인트/재시도/루프/분기/병렬 노드 실행이 쉬워짐
- 상태 기반 디버깅/리플레이가 쉬워짐
- 멀티 에이전트 라우팅(그래프 분기)이 쉬워짐

즉, 처음부터 LangGraph로 갈 필요는 없지만, “전환 가능한 설계”는 지금 반드시 해야 함.

## 15. 구현 순서(추천 MVP 로드맵)

Phase 1: 네 시퀀스 코어를 플랫폼 런타임으로 고정

- FastAPI + session/state store(redis)
- Orchestrator 노드 4개: InputPolicy → Intent → ToolExecute → Answer
- Tool manifest + schema validation + audit
- UI action 3종(필터/정렬/그룹)

Phase 2: RAG + 출처 + ACL

- KB 생성/문서 적재/인덱싱 worker
- retrieve + cite + acl filter
- 답변에 citations 포함

Phase 3: Policy 강화 + Admin

- 입력/출력 필터, 위반 이벤트 로그
- RBAC/권한 기반 tool/kb 접근 통제
- 사용량/성공률 대시보드 API

Phase 4: Store/Lab 확장 + LangGraph 전환(선택)

- 자산 버전/배포/승인
- 그래프 기반 workflow(복잡한 분기/루프 필요 시)

## 16. “네 기존 시퀀스”와의 1:1 매핑

| 네 구성 | 플랫폼 모듈 |
| --- | --- |
| UIBridge + AdapterRegistry | Tool Execution Client + Tool Registry |
| ui_state 주기적 전송 | State Service(서버가 최신상태 보관) |
| Orch intent 분류 | Orchestrator Node: IntentClassify |
| action 수행 및 결과 반영 | Tool Service + ApplyPatch Node |
| QUERY만이면 RAG 답변 | RAG Service + AnswerSynthesize Node |
| Server가 answer 반환 | Chat API Gateway |

## 부록 A. 결정 포인트(권장값)

- Vector DB: Qdrant 권장(ACL metadata filter 용이)
- State: 최신은 Redis, 이벤트로그는 Postgres
- UI action 전달: WebSocket 우선(폴링도 가능)
- Orchestrator: 초기 LangChain, 노드 컨트랙트 고정 → 필요 시 LangGraph로 전환
