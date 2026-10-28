# Skill: safely extend the public workflow demo

**Trigger:** A request to add or adjust a feature, test, workflow state, or documentation in this *public demonstration*.

## Inputs

- A narrow feature request and expected behavior.
- Existing source and tests in this repository.
- Safety requirements from `AGENTS.md` and `SECURITY.md`.

## Procedure

1. Confirm the change does not touch or refer to proprietary Nā Pali Studio data or logic.
2. Define success, failure, and stale-data cases before coding.
3. Implement small, readable changes in `app/` and `web/`.
4. Keep backend workflow rules authoritative; clients may not bypass them.
5. Update tests and run `pytest`.
6. Run `python scripts/check_public.py` and inspect `git diff --cached` for sensitive material.
7. Explain the change, tests executed, limitations, and whether human review remains necessary.

## Output

A small change with evidence from tests, updated docs where needed, and an accurate commit message. Never claim production deployment or publish without human authorization.
