# Release Process

---

## Pre-release checklist

Run before tagging a release:

```bash
bash release-check.sh
```

Manual checks:

- [ ] `VERSION` and `pyproject.toml` match
- [ ] `CHANGELOG.md` has an entry for this version
- [ ] `ROADMAP.md` items are checked accurately
- [ ] All tests pass: `python -m pytest`
- [ ] CLI works: `mq-image --help`, `mq-image --version`, `mq-image doctor`
- [ ] No model files staged: `git status`
- [ ] No `.env` or secrets staged

---

## Tagging

```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## GitHub release

```bash
gh release create v1.0.0 --title "v1.0.0 — Stable Visual Reasoning Toolkit" --notes-file CHANGELOG.md
```

Pushing a `v*` tag also triggers the GitHub Actions release workflow.

---

## Version format

`MAJOR.MINOR.PATCH`

- `PATCH` — bug fixes, docs, test additions
- `MINOR` — new commands, new analysis features, new skills
- `MAJOR` — breaking CLI or JSON schema changes

---

## Branch policy

- `main` should stay release-ready
- Feature work should happen in branches and merge via PR where practical
- Releases are cut from signed-off clean working trees
