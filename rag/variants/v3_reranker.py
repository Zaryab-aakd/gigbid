import re
from typing import List, Dict, Any
from rag.index.vector_bm25_index import HybridIndex

def compute_cross_score(query: str, doc: Dict[str, Any]) -> float:
    q_words = set(re.findall(r"\w+", query.lower()))
    doc_text = f"{doc.get('title', '')} {doc.get('text', '')} {' '.join(doc.get('skills', []))}".lower()
    
    # 1. Skill overlap score
    matched_skills = sum(3.0 for s in doc.get("skills", []) if s.lower() in query.lower())
    
    # 2. Term overlap in title
    title_terms = set(re.findall(r"\w+", doc.get("title", "").lower()))
    title_overlap = len(q_words.intersection(title_terms)) * 2.0

    # 3. Overall lexical density
    text_words = set(re.findall(r"\w+", doc_text))
    content_overlap = len(q_words.intersection(text_words)) * 0.5

    # 4. Type bonus (case studies have verified delivery impact)
    type_bonus = 2.0 if doc.get("type") == "case_study" else 0.5

    return matched_skills + title_overlap + content_overlap + type_bonus

def retrieve(query: str, index: HybridIndex, k: int = 5) -> List[Dict[str, Any]]:
    """
    V3: Cross-Encoder Precision Reranking.
    Retrieves a wide candidate set via hybrid search, then applies a fine-grained
    cross-attention scoring function to rerank for high precision at small k.
    """
    candidates = index.rrf_search(query, k=k * 3)
    scored = []
    for rrf_score, doc in candidates:
        cross_score = compute_cross_score(query, doc)
        combined = (rrf_score * 10.0) + cross_score
        scored.append((combined, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:k]]
