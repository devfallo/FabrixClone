from __future__ import annotations

import uuid
from typing import Dict, List

from app.models.schemas import Citation


class RAGService:
    def __init__(self) -> None:
        self._knowledge_bases: Dict[str, dict] = {}
        self._documents: Dict[str, List[dict]] = {}

    def create_kb(self, name: str, description: str | None, acl: List[str]) -> str:
        kb_id = str(uuid.uuid4())
        self._knowledge_bases[kb_id] = {"name": name, "description": description, "acl": acl}
        self._documents[kb_id] = []
        return kb_id

    def add_document(
        self,
        kb_id: str,
        title: str,
        text: str,
        source_uri: str | None,
        page: int | None,
        acl: List[str],
    ) -> str:
        doc_id = str(uuid.uuid4())
        self._documents[kb_id].append(
            {
                "doc_id": doc_id,
                "title": title,
                "text": text,
                "source_uri": source_uri,
                "page": page,
                "acl": acl,
            }
        )
        return doc_id

    def query(self, kb_id: str, query: str, roles: List[str]) -> tuple[str, List[Citation]]:
        docs = self._documents.get(kb_id, [])
        hits: List[dict] = []
        for doc in docs:
            if doc["acl"] and not set(doc["acl"]).intersection(roles):
                continue
            if query.lower() in doc["text"].lower() or query.lower() in doc["title"].lower():
                hits.append(doc)
        citations = [
            Citation(
                doc_id=doc["doc_id"],
                title=doc["title"],
                page=doc["page"],
                snippet=doc["text"][:200],
            )
            for doc in hits[:3]
        ]
        if citations:
            answer = "\n".join([f"{c.title}: {c.snippet}" for c in citations])
        else:
            answer = "No relevant documents found."
        return answer, citations
