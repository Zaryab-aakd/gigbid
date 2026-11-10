from worker.worker import GigBidWorker

def test_worker_idempotent_processing():
    worker = GigBidWorker()
    sample_job = {
        "job_id": "worker-test-job-01",
        "title": "Machine Learning Engineer for Tabular Data",
        "description": "Looking for Python specialist to build customer churn model using scikit-learn.",
        "required_skills": ["Python", "scikit-learn"],
        "budget": {"min": 500, "max": 1200, "currency": "USD"}
    }

    # 1. First run processes job
    res1 = worker.process_job_idempotent(sample_job, persona_id="ai_ml_engineer")
    assert res1["job_id"] == "worker-test-job-01"
    assert "paused_for_approval" in res1

    # 2. Immediate rerun is skipped idempotently without duplicate computation!
    res2 = worker.process_job_idempotent(sample_job, persona_id="ai_ml_engineer")
    assert res2["status"] == "skipped_duplicate"
