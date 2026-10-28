# Publishing to your GitHub account

This package is **ready to review**, not yet published. You must approve public release.

## Recommended method: existing local Git history

1. Review `SECURITY.md`, all sources, license, and `git log --oneline`.
2. Run tests and the public-file scan. Confirm `git status --short` is empty.
3. On [GitHub's new repository page](https://github.com/new), create a **PUBLIC** repository named `napali-studio-public-demo`. Do **not** initialize with README, license, or `.gitignore` (they are already included).
4. In the extracted project directory (the ZIP includes its `.git` directory), run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/napali-studio-public-demo.git
git push -u origin main
```

5. Confirm the repository README, files, commits, and CI checks are visible. Then share **your real GitHub URL** with an employer; do not supply a guessed link before publishing.

## Alternative: restore the Git bundle

The companion `.bundle` file retains the demo Git history. Restore with:

```bash
git clone napali-studio-public-demo.bundle napali-studio-public-demo
cd napali-studio-public-demo
git remote remove origin    # The bundle is the original local origin.
git remote add origin https://github.com/YOUR_USERNAME/napali-studio-public-demo.git
git push -u origin main
```

## What this history means

These commits reflect the **actual construction of the new, AI-assisted demonstration** during this session. They are not a copy of, or evidence for, earlier private project commits. The commits use an explicit AI-assisted builder author rather than impersonating the project owner. Review the history and code before representing it as your work.

## After publishing

Use the GitHub repository URL in the employer's public-repo field. Explain that it is a public engineering demonstration **derived from the type of workflow challenges** encountered in your private work, not the proprietary application itself.
