# Claude-compatible project context

The canonical collaborator rules are in [AGENTS.md](AGENTS.md). Apply them unchanged.

- Project type: **standalone sanitized demonstration**, not the private Nā Pali Studio codebase.
- Backend: Python 3.11+, FastAPI, SQLite; frontend: plain HTML/CSS/JS.
- Read from: `app/main.py`, `app/storage.py`, `web/`, `tests/`.
- Test: `pytest`; lint: `ruff check app tests`; privacy heuristic: `python scripts/check_public.py`.
- Security: no secrets, external customer data, client workflow details, or private-company code. Local-only service, no auth.
- Keep state changes validated and audited; use expected-version checks.
- Make truthful, human-reviewable commits, and document AI contributions without exaggeration.
