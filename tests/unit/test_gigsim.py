from fastapi.testclient import TestClient
from gigsim.app import app
from gigsim.store import store

client = TestClient(app)

def test_gigsim_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "gigsim"
    assert data["jobs_loaded"] > 0

def test_gigsim_search_jobs():
    res = client.get("/api/jobs?limit=5")
    assert res.status_code == 200
    jobs = res.json()
    assert len(jobs) == 5
    assert "job_id" in jobs[0]
    assert "title" in jobs[0]

def test_gigsim_proposal_dry_run_and_idempotency():
    # Pick a job
    jobs = client.get("/api/jobs?limit=1").json()
    job_id = jobs[0]["job_id"]

    # 1. Dry run
    dry_payload = {
        "job_id": job_id,
        "freelancer_id": "ai_ml_engineer",
        "cover_letter": "I will deliver this project with high quality.",
        "bid_amount": 1200.0,
        "screening_answers": ["I use CV and NLP models."],
        "evidence_ids": ["case-ai-001"],
        "dry_run": True,
        "idempotency_key": "test-key-dry-1"
    }
    res_dry = client.post("/api/proposals/submit", json=dry_payload)
    assert res_dry.status_code == 200
    assert res_dry.json()["dry_run"] is True
    assert res_dry.json()["status"] == "preview"

    # 2. Real submission
    init_balance = client.get("/api/connects/balance").json()["current_balance"]
    real_payload = dict(dry_payload)
    real_payload["dry_run"] = False
    real_payload["idempotency_key"] = "test-key-real-1"

    res_real = client.post("/api/proposals/submit", json=real_payload)
    assert res_real.status_code == 200
    res_data = res_real.json()
    assert res_data["status"] == "submitted"
    assert res_data["dry_run"] is False

    new_balance = client.get("/api/connects/balance").json()["current_balance"]
    assert new_balance == init_balance - res_data["connects_spent"]

    # 3. Idempotency test (calling again with SAME idempotency key must not spend connects again)
    res_dup = client.post("/api/proposals/submit", json=real_payload)
    assert res_dup.status_code == 200
    assert res_dup.json()["proposal_id"] == res_data["proposal_id"]
    dup_balance = client.get("/api/connects/balance").json()["current_balance"]
    assert dup_balance == new_balance  # Connects not spent twice!

def test_gigsim_client_evaluator():
    jobs = client.get("/api/jobs?limit=1").json()
    job_id = jobs[0]["job_id"]
    
    # Generic proposal should be penalized
    generic_payload = {
        "job_id": job_id,
        "freelancer_id": "ai_ml_engineer",
        "cover_letter": "Dear Hiring Manager, I am a highly motivated engineer with 10 years experience. I have read your job description with great interest.",
        "bid_amount": 1500.0,
        "screening_answers": [],
        "evidence_ids": [],
        "dry_run": False,
        "idempotency_key": "generic-test-1"
    }
    eval_res = client.post("/api/simulate/evaluate", json=generic_payload)
    assert eval_res.status_code == 200
    data = eval_res.json()
    assert data["quality_score"] < 0.60
    assert data["replied"] is False
    assert "generic" in data["client_feedback"].lower()
