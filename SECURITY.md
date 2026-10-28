# Security and privacy policy

## Intended use

**Source-review and localhost educational demonstration only.** The application intentionally has no authentication, authorization, tenant isolation, rate limiting, CSRF controls, server-side actor identity, or enterprise logging. Do not use it with live client data or expose it as a public hosted service.

## Privacy boundary

This is entirely new sample software using fabricated work items. Do not add private Nā Pali Studio code, real names or relationships, business records, proprietary publication/assessment methodologies, production logs, credentials, configuration files, private URLs, data dumps, or customer/client data.

The sample `demo-user` field is not an authentication mechanism, and its event trail is not tamperproof against a database administrator. Event timestamps are UTC. SQLite stores sample data only in a Git-ignored `.data/` directory. Production-grade security claims are out of scope.

## Pre-publication checklist

1. Manually inspect all tracked files and `git log --stat` for confidential content.
2. Run `python scripts/check_public.py` (**heuristic only**; not a replacement for credential or license scanning).
3. Verify `git status --short` is clean and no `.env`, `.data`, or secrets are tracked.
4. Review third-party dependency licenses and the repository's MIT license suitability.
5. Do not publish the historical private Git repository or its remotes/branches.
6. Have the project owner approve any public repository push.

## Reporting vulnerabilities

Because this is a local example, please avoid public disclosure of live credentials or customer information. Contact the repository owner via GitHub security reporting if they choose to enable it; do not put secrets in public issues.
