from mcp_servers.portfolio.tools import search_evidence, get_case_study, list_skills
from mcp_servers.portfolio.resources import get_case_resource, get_proposal_resource

def test_search_evidence():
    results = search_evidence("LangGraph multi-agent", k=3, persona_id="ai_ml_engineer")
    assert len(results) > 0
    assert any("LangGraph" in item.get("skills", []) or "agent" in item.get("title", "").lower() for item in results)

def test_get_case_study():
    content = get_case_study("case-ai-001", persona_id="ai_ml_engineer")
    assert content is not None
    assert "Enterprise Multi-Agent" in content or "case-ai-001" in content

def test_list_skills():
    skills = list_skills("ai_ml_engineer")
    assert len(skills) > 5
    assert "Python" in skills or "LangGraph" in skills or "FastAPI" in skills

def test_resources():
    case_txt = get_case_resource("case-ai-001")
    assert len(case_txt) > 20
    prop_txt = get_proposal_resource("prop-ai-001")
    assert len(prop_txt) > 20
