import re
from typing import List, Dict, Any
from rag.index.vector_bm25_index import HybridIndex

def extract_requirements(job_text: str) -> List[str]:
    # Look for bullet points or comma separated requirements
    lines = job_text.split("\n")
    reqs = []
    for l in lines:
        cleaned = l.strip("*-•123456789. ")
        if len(cleaned) > 10 and not any(kw in cleaned.lower() for kw in ["budget", "hourly", "apply", "urgent"]):
            reqs.append(cleaned)
    if not reqs:
        # Fallback to sentence splitting
        reqs = [s.strip() for s in re.split(r"[.!?]", job_text) if len(s.strip()) > 15]
    return reqs[:4] if reqs else [job_text]

def retrieve(query: str, index: HybridIndex, k: int = 5) -> List[Dict[str, Any]]:
    """
    V1: Requirement Decomposition.
    Decomposes job post into distinct technical requirements, retrieves candidates
    for each requirement, and merges deduplicated results.
    """
    reqs = extract_requirements(query)
    seen_ids = set()
    combined_results = []

    per_req_k = max(2, k // len(reqs) + 1)
    for r in reqs:
        hits = index.dense_search(r, k=per_req_k)
        for _, item in hits:
            cid = item.get("chunk_id")
            if cid not in seen_ids:
                seen_ids.add(cid)
                combined_results.append(item)
            if len(combined_results) >= k:
                break
        if len(combined_results) >= k:
            break

    # If still under k, pad with top general hits
    if len(combined_results) < k:
        fallback_hits = index.dense_search(query, k=k)
        for _, item in fallback_hits:
            cid = item.get("chunk_id")
            if cid not in seen_ids:
                seen_ids.add(cid)
                combined_results.append(item)
            if len(combined_results) >= k:
                break

    return combined_results[:k]
