# AI Usage Disclosure

## Tools Used
- **AI Coding Assistant**: Google Antigravity / Gemini 3.8 Flash (Medium).
- **Assisted Areas**:
  * Scaffolding Pydantic v2 data models and handoffs (`agent/handoffs.py`).
  * Generating synthetic persona case studies and historical Upwork job distributions (`scripts/generate_dataset_and_personas.py`).
  * Crafting React component layout and CSS styling (`apps/web/src/components/`).
  * Building RAG benchmarking harnesses and statistical test scripts (`evals/runners/`).

## Incorrect Suggestions Caught & Corrected
1. **Pydantic v1 Deprecation Warning**:
   * *AI Suggestion*: Initially used `.dict()` method on Pydantic instances.
   * *Correction*: Updated all models across `gigsim/store.py` and `agent/handoffs.py` to use Pydantic v2 `.model_dump()` and modern timezone-aware `datetime.now(timezone.utc)`.
2. **LangGraph Interrupt Resume Protocol**:
   * *AI Suggestion*: Attempted to resume interrupted graph threads by passing raw dictionary payloads to `graph.stream(approval_input)`.
   * *Correction*: Fixed according to modern LangGraph specification by using `from langgraph.types import Command; graph.stream(Command(resume=approval_input))`, ensuring correct resumption from `interrupt()`.
3. **Case ID Metadata Extraction in Ingestion**:
   * *AI Suggestion*: Defaulted to using stripped filenames as case IDs.
   * *Correction*: Enhanced frontmatter parser in `rag/ingest/loaders.py` to parse explicit YAML `id: case-ai-001` metadata, ensuring 100% precision in evidence recall benchmarks.
