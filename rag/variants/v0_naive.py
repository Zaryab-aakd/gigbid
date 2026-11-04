from typing import List, Dict, Any
from rag.index.vector_bm25_index import HybridIndex

def retrieve(query: str, index: HybridIndex, k: int = 5) -> List[Dict[str, Any]]:
    """
    V0: Mandatory Naive Dense Baseline.
    Performs single-query top-k cosine similarity on the raw job text.
    """
    hits = index.dense_search(query, k=k)
    return [item for _, item in hits]
