from rag.retriever import PortfolioRetriever
from rag.verify import split_into_claims, verify_claims, sanitize_draft

def test_retriever_variants():
    retriever_v0 = PortfolioRetriever(persona_id="ai_ml_engineer", variant_name="v0_naive")
    hits_v0 = retriever_v0.retrieve("customer churn classification model", k=3)
    assert len(hits_v0) == 3

    retriever_v2 = PortfolioRetriever(persona_id="ai_ml_engineer", variant_name="v2_hybrid")
    hits_v2 = retriever_v2.retrieve("LangGraph multi-agent pipeline", k=3)
    assert len(hits_v2) == 3

    retriever_v3 = PortfolioRetriever(persona_id="ai_ml_engineer", variant_name="v3_reranker")
    hits_v3 = retriever_v3.retrieve("LangGraph multi-agent customer support", k=3)
    assert len(hits_v3) == 3

def test_claim_verification_grounded():
    retriever = PortfolioRetriever(persona_id="ai_ml_engineer", variant_name="v3_reranker")
    evidence = retriever.retrieve("customer churn classification model", k=3)

    valid_draft = (
        "Hi there. I built a customer churn prediction baseline using scikit-learn and Python. "
        "The model compared logistic regression and random forest and improved retention campaign conversion."
    )
    verifications = verify_claims(valid_draft, evidence)
    assert len(verifications) > 0
    # Every legitimate claim supported
    statuses = [v["status"] for v in verifications]
    assert "supported" in statuses

def test_claim_verification_hallucination_detection():
    evidence = [{"evidence_id": "case-01", "title": "Python script", "skills": ["Python"], "text": "Basic Python script"}]
    fake_draft = (
        "I have 20 years experience with LangGraph. "
        "I invented Python and guarantee zero bugs in your enterprise platform."
    )
    verifications = verify_claims(fake_draft, evidence)
    unsupported = [v for v in verifications if v["status"] == "unsupported"]
    assert len(unsupported) > 0

    sanitized = sanitize_draft(fake_draft, verifications)
    assert "20 years experience with LangGraph" not in sanitized
    assert "zero bugs" not in sanitized
