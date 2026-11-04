from typing import List, Dict, Any
from rag.index.vector_bm25_index import HybridIndex
from rag.variants.v3_reranker import compute_cross_score

def retrieve(query: str, index: HybridIndex, k: int = 5) -> List[Dict[str, Any]]:
    """
    V4: Outcome-Aware Retrieval.
    Boosts items that have historical evidence of winning contracts ('won')
    or generating client engagement ('replied').
    """
    candidates = index.rrf_search(query, k=k * 3)
    scored = []
    for rrf_score, doc in candidates:
        score = (rrf_score * 10.0) + compute_cross_score(query, doc)
        
        outcome = doc.get("outcome", "").lower()
        if "won" in outcome or "coursework demonstration" in outcome or "production" in outcome:
            score *= 1.40  # 40% boost for verified win
        elif "replied" in outcome or "adopted" in outcome:
            score *= 1.20  # 20% boost for client engagement
        elif "ignored" in outcome:
            score *= 0.60  # 40% penalty for proposals that clients ignored

        scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:k]]
