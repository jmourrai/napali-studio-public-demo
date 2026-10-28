# QA record

The validation checks below were run during construction of this independent public demo on October 28, 2026. Results are scoped to the version that was packaged; they do not certify a publicly hosted service.

- `python -m pytest -q`: **14 tests passed** after the frontend assertion was corrected.
- `GET /api/metrics` against a locally running seeded service: `total=5`, with one item in each state.
- `python scripts/check_public.py`: passed; this is a **heuristic** only.
- Browser review: the browser environment blocked direct localhost access. A Chromium check rendered the actual HTML/CSS/JavaScript using **mocked synthetic API responses**, validated five initial cards and a sixth created card without JavaScript errors, and saved `docs/demo-board.png`. The backend was separately exercised through pytest and localhost HTTP. This is **not** a full browser-to-server integration test.
- Syntax compilation: `python -m compileall -q app`.
- `ruff check app tests`: configured in GitHub Actions but **not run locally** (dependency installation unavailable in this environment).
- Public review limitations: dependencies and source should be rechecked before publication; continuous integration runs after a GitHub push.
