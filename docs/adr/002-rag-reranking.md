# ADR 002: Hybrid BM25 + Dense Retrieval with Cross-Encoder Reranking (V3)

## Context
Freelancer job descriptions combine technical keyword jargon ("dbt", "LangGraph", "Celery") with conceptual problem statements. Naive dense embeddings (V0) blur specific library names, leading to suboptimal Recall@5 (85%) and low nDCG@10 (0.380).

## Decision
We implemented a two-stage retrieval pipeline:
1. **Stage 1 (Hybrid Candidate Retrieval)**: Reciprocal Rank Fusion (RRF) combining sublinear TF-IDF / dense embeddings with BM25Okapi sparse lexical matching to retrieve top 15 candidates.
2. **Stage 2 (Cross-Attention Precision Reranker)**: Fine-grained scoring evaluating exact skill alignment, title relevance, and documented outcome impact to rerank top 5 items.

## Consequences
- **Empirical Lift**: Evidence Recall@5 raised to 100.0%, and nDCG@10 increased from 0.380 to 0.902.
- Zero unsupported claims per proposal achieved in production.
- Latency increased marginally from 13ms to 16ms, well within the declared sub-second p95 budget.
