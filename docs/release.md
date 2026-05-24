# Release Process

---

## Pre-release checklist

Run before tagging a release:

```bash
bash release-check.sh
```

Manual checks:

- [ ] `VERSION` updated
- [ ] `CHANGELOG.md` has entry for this version
- [ ] `ROADMAP.md` items checked accurately
- [ ] All tests pass: `pytest`
- [ ] CLI works: `mq-image --help`, `mq-image --version`, `mq-image doctor`
- [ ] No model files staged: `git status`
- [ ] No `.env` or secrets staged

---

## Tagging

```bash
git tag v0.1.1
git push origin v0.1.1
```

---

## GitHub release

```bash
gh release create v0.1.1 --title "v0.1.1 — Hardening" --notes-file CHANGELOG.md
```

---

## Version format

`MAJOR.MINOR.PATCH`

- `PATCH` — bug fixes, docs, test additions
- `MINOR` — new commands, new analysis features, new skills
- `MAJOR` — breaking CLI or JSON schema changes

---

## Branch policy

- `main` is always release-ready
- Feature work in branches, merged via PR
- No direct commits to main for feature work
