# GigBid Operational Runbook

## 1. Quick Start

### Local Development (Python Virtual Environment)
```bash
# 1. Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -e ".[dev]"
pip install rank_bm25 scikit-learn

# 3. Seed datasets and personas
make seed

# 4. Run tests & evaluations
make test
make eval

# 5. Start web UI and API
make dev
```
Navigate to `http://localhost:8000` to interact with the full web interface.

---

## 2. Docker Deployment
```bash
docker-compose -f infra/docker-compose.yml up --build
```
Services started:
- `api` (Port 8000)
- `gigsim` (Port 8001)
- `worker` (Background scouting scheduler)
- `postgres` (Port 5432)
- `redis` (Port 6379)

---

## 3. Degraded Mode & Chaos Recovery

### Testing Marketplace Downtime During Viva:
1. Simulate marketplace failure by injecting chaos:
   ```bash
   curl -X POST http://localhost:8001/api/admin/chaos?simulate_500=true
   ```
2. The UI automatically displays a degraded mode banner: *"Marketplace simulator temporarily unavailable. All background scouting tasks are safely queued in Redis without losing state."*
3. To recover, disable chaos flag:
   ```bash
   curl -X POST http://localhost:8001/api/admin/chaos?simulate_500=false
   ```

---

## 4. Crash & Resume Durability Proof

1. Start bid graph execution on job `dev-job-0001`.
2. Execution pauses at the `human_approval` interrupt.
3. Simulate an unexpected worker / server crash (`kill -9`).
4. Restart the API / worker.
5. Inspect state via thread ID `thread-bid-dev-job-0001`:
   - State snapshot is safely recovered from checkpointer.
   - Resuming with approval dispatches the proposal exactly once due to the enforced `idempotency_key`.
