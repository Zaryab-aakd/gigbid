from typing import List, Dict, Any
from rag.index.vector_bm25_index import HybridIndex

def retrieve(query: str, index: HybridIndex, k: int = 5) -> List[Dict[str, Any]]:
    """
    V2: Hybrid BM25 + Dense with Reciprocal Rank Fusion (RRF).
    Combines exact keyword lexical matching with semantic dense cosine similarity.
    """
    hits = index.rrf_search(query, k=k, rrf_k=60)
    return [item for _, item in hits]
