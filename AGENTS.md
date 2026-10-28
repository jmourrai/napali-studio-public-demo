# Agent guidelines — public engineering demo

These instructions apply to both human and AI coding collaborators.

## Purpose

Maintain a **new, sanitized public demonstration** of general workflow software practices. It is **not** the private Nā Pali Studio platform and must not become a gateway for publishing private source.

## Never include

- Customer/client/lead identifiers, correspondence, contact records, payment information, real assessment or publishing content.
- Real Nā Pali operating-system methodologies, proprietary documents, internal database schema, or private repo history.
- Secrets, API credentials, `.env` files, production infrastructure addresses, production databases or backups.
- Fake claims that AI code was manually implemented, that this project was in production, or that the commit history predates this demonstration.

## Working method

1. Read `README.md`, `SECURITY.md`, and `docs/ARCHITECTURE.md` before editing.
2. Propose a small change with a testable acceptance criterion.
3. Favor typed, simple Python and standard FastAPI patterns.
4. Preserve explicit state transitions and version-checked updates; do not bypass the audit trail.
5. Include tests for success, bad input, and conflict conditions.
6. Run `pytest` and `python scripts/check_public.py`; run `ruff check app tests` when installed.
7. Document meaningful decisions in `docs/AI_DEVELOPMENT.md` and keep commit descriptions factual.
8. Request **human review** before any external publication or deployment.

## AI attribution

Describe assistance as generated suggestions/code reviewed and validated through tools. Do not assert independent human authorship or invent months of commit history. Do not publish the service on the internet: there is no auth.
