# GigBid Data Card

## 1. Dataset Overview & Selection

GigBid utilizes a hybrid data strategy combining real-world marketplace distributions from public Upwork datasets with synthetic persona corpora and evaluation benchmarks:

1. **Marketplace Distribution Benchmark**:
   - Source: Kaggle Upwork job postings & contracts datasets (Asaniczka, 2024).
   - Usage: Parameterized 1,500 historical jobs (`data/jobs/historical_1500_jobs.json`) modeling real-world budget distributions, duration tiers, connects costs, and client hire histories.
   - License: CC0 / Public Domain.

2. **Freelancer Persona Corpora**:
   - 3 distinct personas (`ai_ml_engineer`, `full_stack_developer`, `data_analyst`).
   - Contents per persona:
     * Structured CV in Markdown (`cv.md`)
     * 20 Production Case Studies with problems, architecture, skills, and outcomes
     * 150 historical proposals labeled `won`, `replied`, or `ignored`
     * 15 client reviews with ratings and budgets
     * Codebase READMEs and architectural modules.
   - Status: High-fidelity synthetic grounded data.

3. **Development Evaluation Set (`evals/datasets/dev_set_600_jobs.json`)**:
   - 600 total jobs (200 per persona).
   - Gold annotations:
     * `decision`: `bid` vs `skip`
     * `is_scam`: boolean (flagging free trials, Telegram/WhatsApp requests, crypto deposits)
     * `has_prompt_injection`: boolean (planted adversarial prompt injection strings)
     * `relevant_evidence_ids`: ground truth matching case study IDs
     * `fair_price_band`: `{"min": ..., "max": ..., "recommended": ...}`.

---

## 2. Privacy, PII & Compliance Handling

- **PII Scrubbing**: Regex filters strip residential addresses, telephone numbers, and email patterns prior to storage and LLM inference.
- **No Scraping**: No automated web scraping, browser automation, or unauthorized Upwork session cookie extraction.
- **Tenant Scope**: Freelancer profile data and proposals are isolated by tenant identifier.
