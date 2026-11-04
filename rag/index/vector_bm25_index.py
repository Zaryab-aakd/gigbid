import math
import re
from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def tokenize(text: str) -> List[str]:
    clean = re.sub(r"[^\w\s-]", " ", text.lower())
    return [t for t in clean.split() if len(t) > 1]

class HybridIndex:
    def __init__(self, chunks: List[Dict[str, Any]]):
        self.chunks = chunks
        self.corpus_texts = [f"{c.get('title', '')} {c.get('text', '')} {' '.join(c.get('skills', []))}" for c in chunks]
        
        # 1. BM25 Setup
        self.tokenized_corpus = [tokenize(doc) for doc in self.corpus_texts]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

        # 2. Dense Vector Setup (TF-IDF sublinear normalized dense embedding representation)
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            max_features=8000
        )
        if self.corpus_texts:
            self.dense_matrix = self.vectorizer.fit_transform(self.corpus_texts)
        else:
            self.dense_matrix = None

    def dense_search(self, query: str, k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        if self.dense_matrix is None or not self.corpus_texts:
            return []
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.dense_matrix)[0]
        top_indices = np.argsort(sims)[::-1][:k]
        
        results = []
        for idx in top_indices:
            results.append((float(sims[idx]), self.chunks[idx]))
        return results

    def bm25_search(self, query: str, k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        if not self.corpus_texts:
            return []
        tokens = tokenize(query)
        scores = self.bm25.get_scores(tokens)
        top_indices = np.argsort(scores)[::-1][:k]

        results = []
        for idx in top_indices:
            results.append((float(scores[idx]), self.chunks[idx]))
        return results

    def rrf_search(self, query: str, k: int = 5, rrf_k: int = 60) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Reciprocal Rank Fusion (RRF) combining Dense and BM25 rankings:
        RRF_Score(d) = sum_{m in models} 1 / (rrf_k + rank_m(d))
        """
        dense_hits = self.dense_search(query, k=k*3)
        bm25_hits = self.bm25_search(query, k=k*3)

        rrf_scores: Dict[int, float] = {}

        # Dense ranks
        for rank, (_, item) in enumerate(dense_hits, start=1):
            chunk_idx = self.chunks.index(item)
            rrf_scores[chunk_idx] = rrf_scores.get(chunk_idx, 0.0) + (1.0 / (rrf_k + rank))

        # BM25 ranks
        for rank, (_, item) in enumerate(bm25_hits, start=1):
            chunk_idx = self.chunks.index(item)
            rrf_scores[chunk_idx] = rrf_scores.get(chunk_idx, 0.0) + (1.0 / (rrf_k + rank))

        sorted_indices = sorted(rrf_scores.keys(), key=lambda idx: rrf_scores[idx], reverse=True)[:k]
        return [(rrf_scores[idx], self.chunks[idx]) for idx in sorted_indices]
