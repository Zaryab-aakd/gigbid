import os
import yaml
from typing import List, Dict, Any, Optional
from rag.ingest.loaders import PortfolioIngestion
from rag.index.vector_bm25_index import HybridIndex
from rag.variants import (
    v0_naive,
    v1_decomposition,
    v2_hybrid,
    v3_reranker,
    v4_outcome_aware,
    v8_self_rag
)

# In-memory index cache per persona
INDEX_CACHE: Dict[str, HybridIndex] = {}

def get_or_build_index(persona_id: str = "ai_ml_engineer") -> HybridIndex:
    if persona_id not in INDEX_CACHE:
        chunks = PortfolioIngestion.load_all_persona_chunks(persona_id)
        INDEX_CACHE[persona_id] = HybridIndex(chunks)
    return INDEX_CACHE[persona_id]

def get_retriever_variant(variant_name: Optional[str] = None):
    if variant_name is None:
        cfg_path = "agent/config.yaml"
        if os.path.exists(cfg_path):
            with open(cfg_path) as f:
                cfg = yaml.safe_load(f)
                variant_name = cfg.get("rag", {}).get("variant", "v3_reranker")
        else:
            variant_name = "v3_reranker"

    variants = {
        "v0_naive": v0_naive.retrieve,
        "v1_decomposition": v1_decomposition.retrieve,
        "v2_hybrid": v2_hybrid.retrieve,
        "v3_reranker": v3_reranker.retrieve,
        "v4_outcome_aware": v4_outcome_aware.retrieve,
        "v8_self_rag": v8_self_rag.retrieve
    }
    return variants.get(variant_name, v3_reranker.retrieve)

class PortfolioRetriever:
    def __init__(self, persona_id: str = "ai_ml_engineer", variant_name: str = "v3_reranker"):
        self.persona_id = persona_id
        self.variant_name = variant_name
        self.index = get_or_build_index(persona_id)
        self.retrieve_fn = get_retriever_variant(variant_name)

    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        return self.retrieve_fn(query, self.index, k=k)
