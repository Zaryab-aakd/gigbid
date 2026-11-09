from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["service"] == "gigbid-api"

def test_api_user_profile():
    res = client.get("/api/user/profile")
    assert res.status_code == 200
    data = res.json()
    assert "user" in data
    assert "connects" in data

def test_api_job_inbox():
    res = client.get("/api/jobs/inbox?limit=5")
    assert res.status_code == 200
    inbox = res.json()
    assert len(inbox) > 0
    assert "job_id" in inbox[0]
    assert "fit_score" in inbox[0]
    assert "risk_badge" in inbox[0]

def test_api_job_detail():
    inbox = client.get("/api/jobs/inbox?limit=1").json()
    job_id = inbox[0]["job_id"]
    res = client.get(f"/api/jobs/{job_id}/detail")
    assert res.status_code == 200
    data = res.json()
    assert "job" in data
    assert "requirement_evidence_matrix" in data

def test_api_memory_and_deletion():
    mems = client.get("/api/memory").json()["memories"]
    assert len(mems) > 0
    mem_id = mems[0]["memory_id"]
    
    del_res = client.delete(f"/api/memory/{mem_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "deleted"

def test_api_analytics():
    res = client.get("/api/analytics")
    assert res.status_code == 200
    assert res.json()["reply_rate_pct"] > 0
