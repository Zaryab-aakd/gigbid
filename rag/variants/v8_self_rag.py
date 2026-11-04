import re
from typing import List, Dict, Any, Tuple
from rag.index.vector_bm25_index import HybridIndex
from rag.variants.v3_reranker import retrieve as reranker_retrieve

def grade_evidence_relevance(query: str, doc: Dict[str, Any]) -> float:
    """Grade evidence document relevance from 0.0 to 1.0."""
    q_words = set(re.findall(r"\w+", query.lower()))
    doc_words = set(re.findall(r"\w+", f"{doc.get('title', '')} {doc.get('text', '')}".lower()))
    skills = [s.lower() for s in doc.get("skills", [])]

    skill_match = any(s in query.lower() for s in skills)
    overlap = len(q_words.intersection(doc_words)) / max(len(q_words), 1)
    
    score = (overlap * 0.5) + (0.5 if skill_match else 0.0)
    return min(1.0, score)

def expand_query(query: str) -> str:
    """Expand query terms for corrective re-retrieval."""
    replacements = {
        "rag": "retrieval augmented generation vector embeddings",
        "llm": "large language models transformers fine-tuning",
        "agent": "multi-agent LangGraph orchestration",
        "dashboard": "analytics visualization reporting",
        "churn": "classification machine learning scikit-learn",
        "e-commerce": "storefront payments checkout"
    }
    expanded = query
    for kw, exp in replacements.items():
        if kw in query.lower():
            expanded += f" {exp}"
    return expanded

def retrieve(query: str, index: HybridIndex, k: int = 5) -> List[Dict[str, Any]]:
    """
    V8: Corrective / Self-RAG.
    1. Initial retrieval using cross-encoder reranking.
    2. Grade evidence relevance.
    3. If average grade < 0.35 (weak evidence), trigger query expansion and re-retrieve.
    4. Return filtered high-confidence evidence.
    """
    results = reranker_retrieve(query, index, k=k)
    grades = [grade_evidence_relevance(query, doc) for doc in results]
    avg_grade = sum(grades) / max(len(grades), 1)

    # Corrective loop if retrieval is poor
    if avg_grade < 0.35:
        expanded_q = expand_query(query)
        second_pass = reranker_retrieve(expanded_q, index, k=k)
        # Combine and take best
        combined = {doc.get("chunk_id"): doc for doc in results + second_pass}
        results = list(combined.values())[:k]

    return results
