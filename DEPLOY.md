# Deploying loci.garden

## Infrastructure

- **Host**: a VPS behind Caddy (automatic HTTPS)
- **Domains**: loci.garden, docs.loci.garden
- **Repo**: https://github.com/rainbow-zoku/loci.garden
- **Build**: none needed to deploy; the site is static files. Sync shared partials locally with `python3 build.py` before committing.

Keep drafts, audits, backups and one-off scripts out of the repo (`.gitignore` refuses the common shapes).

## Deploy after PR merge

Deploys are manual by design: CI validates (HTML, links) on every PR and push
but never touches the server. After merging a PR, update the server checkout
to the new `main`:

```bash
git fetch origin
git reset --hard origin/main
```

`reset --hard` rather than `pull`, so the checkout always matches `main` exactly. No restart is needed for a content change. Operator specifics (host, paths, credentials) live in private ops notes, not in this public repo.

## Branch strategy

- `main`: production
- feature branches, PR into `main`
- Never push directly to `main` (branch protection enforces this)

## Rollback

Before deploying, copy the served directory to a timestamped backup. To roll back, restore that copy in place.

## Contact

Questions: themapisnory@tuta.io
