"""Quick heuristic public-readiness check; not a full secret scanner."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
IGNORE = {".git", ".venv", "__pycache__", ".pytest_cache", ".data", ".ruff_cache"}
SIGNATURES = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "AWS key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "OpenAI API key": re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{24,}"),
    "token assignment": re.compile(r"(?i)(?:access_token|secret_key|api_key)\s*[:=]\s*['\"][A-Za-z0-9]{20,}"),
}
issues = []
for path in ROOT.rglob("*"):
    if not path.is_file() or any(part in IGNORE for part in path.relative_to(ROOT).parts):
        continue
    if path.suffix.lower() not in {".py", ".md", ".yaml", ".yml", ".json", ".js", ".css", ".html", ".toml", ".txt", ".example"}:
        continue
    data = path.read_text(encoding="utf-8", errors="replace")
    for label, pattern in SIGNATURES.items():
        if pattern.search(data):
            issues.append(f"{path.relative_to(ROOT)}: possible {label}")
if issues:
    print("\n".join(issues))
    sys.exit(1)
print("Heuristic scan passed; complete a manual review before publishing.")
