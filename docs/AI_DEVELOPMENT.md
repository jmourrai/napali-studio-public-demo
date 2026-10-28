# AI-assisted development record

**Project:** Nā Pali Studio — Public Engineering Demo
**Date:** October 28, 2026
**Status:** Standalone, independently authored demo; not imported from private repositories.

This file documents the **actual development collaboration on this public sample**. It is not reconstructed evidence of prior project commits, and it makes no claim that the model built the private Nā Pali Studio platform.

## Prompt / decision / verification journal

| Iteration | Human objective or instruction | AI-assisted implementation | Verification and outcome |
|---|---|---|---|
| 1: scope | Create a sanitized public demonstration, ideally better than an application blurb, without exposing proprietary Nā Pali materials. | Selected an original, generic review-and-publication workflow with fabricated records. | Reviewed the scope against exclusions: no clients, secrets, publication methodology, or internal code. |
| 2: API | Demonstrate credible engineering with readable source and tests. | Implemented FastAPI endpoints, a SQLite store, bounded input, state validation, conflict checks, and an append-only audit trail. | Ran pytest locally. The first full suite surfaced a case-sensitive frontend-text assertion; corrected the assertion to match the actual UI. |
| 3: usable app | Make the repo show more than documentation by providing a working interface. | Added the responsive browser board, creation form, status action, event-history view, and status counts. | Exercised the service locally and checked API counts. Browser screenshot and UI interaction evidence produced with **mock API responses** because Chromium could not access localhost here; backend checked independently. |
| 4: safety & delivery | Make public publishing and review straightforward. | Added contributor rules, a CI workflow, an explicitly limited secret heuristic, a Dockerfile, Compose loopback binding, and publication instructions. | Re-ran tests, code compilation, manual public-file inspection, and the heuristic scan before packaging. |

## Model assistance versus human accountability

- AI assistance is used for **proposing and generating source code, tests, docs, and configuration**.
- The human project owner is responsible for scope, correctness, repository visibility, licensing decisions, and final publishing.
- Tests and running services offer evidence of functionality, **not proof of production readiness**.
- Demo commit history shows genuine stages of **this newly created sample**, not historic private development.
- No external LLM inference is used by the demo at runtime. It showcases **AI-driven software development**, not an AI-powered feature masquerading as intelligence.

## Reproducible acceptance criteria

```bash
python -m pip install -e '.[dev]'
pytest
ruff check app tests
python scripts/check_public.py
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

From the browser: create an example, advance its status, inspect event history, and verify the counter increments. On another tab, attempt a stale update by reusing an old `expected_version`; the API must return `409`.

## Safe next iterations

- Add a command-line fixture generator and explicit schema migration path.
- Add accessibility and browser integration tests in CI.
- Add versioned API contracts and a minimal example client.
- Keep the proprietary private platform entirely separate; never copy code, data, publication content, or identifiers into this repository.
