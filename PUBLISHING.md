# Publishing and reviewing this public GitHub demo

This repository is deliberately independent from the private Nā Pali Studio platform. Its commit history captures only the construction and publication of this *new* illustrative project, not historical private commits. Do not merge proprietary repositories into this sample.

## Owner review checklist

1. Review all tracked source files, the MIT license, and `SECURITY.md`.
2. Run `python -m pip install -e '.[dev]'`, `pytest`, and `python scripts/check_public.py` locally.
3. Confirm no private client records, credentials, production logs, or unpublished Nā Pali methodology appears in any commit.
4. Review [GitHub Actions](.github/workflows/ci.yml) results after changes; the scan is a heuristic, not proof of security.
5. Never deploy the running web service to a public interface. It is designed for localhost and has no authentication.

## How to fork or clone

```bash
git clone https://github.com/jmourrai/napali-studio-public-demo.git
cd napali-studio-public-demo
python -m pip install -e '.[dev]'
pytest
```

Use the actual repo link in applications only after checking the README, source files, and a successful CI run. The repository is a portfolio example of AI-assisted development; it is **not** a deployment of the private Nā Pali Studio product or a substitute for its development history.
