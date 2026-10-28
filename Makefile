.PHONY: dev test eval seed build lint clean

PYTHON := .venv/bin/python3
PYTEST := .venv/bin/pytest

dev:
	PYTHONPATH=. $(PYTHON) -m uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload

test:
	PYTHONPATH=. $(PYTEST) -v tests/unit/

eval:
	PYTHONPATH=. $(PYTHON) evals/runners/tool_granularity_eval.py
	PYTHONPATH=. $(PYTHON) evals/runners/rag_eval.py
	PYTHONPATH=. $(PYTHON) evals/runners/multi_agent_comparison_eval.py

seed:
	PYTHONPATH=. $(PYTHON) scripts/generate_dataset_and_personas.py

build:
	cd apps/web && npm run build

lint:
	PYTHONPATH=. $(PYTHON) -m py_compile apps/api/main.py gigsim/app.py agent/graphs/bid_graph.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
