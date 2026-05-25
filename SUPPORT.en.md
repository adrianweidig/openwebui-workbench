# Support

🌐 Languages: [Deutsch](SUPPORT.md) | [English](SUPPORT.en.md)

## Public Questions

For reproducible bugs, documentation gaps, and concrete improvement proposals, use GitHub Issues:

- Bug Report for broken tools, filters, import artifacts, dashboard behavior, or validation scripts
- Documentation for unclear instructions, paths, localization links, or import order
- Feature Request for new models, tools, skills, translations, or checks

## Before Opening a Request

If possible, run:

```powershell
python scripts/verify_openwebui_workspace.py
```

For Docker/Compose questions, also run this when Docker is available:

```powershell
python scripts/verify_openwebui_workspace.py --include-docker-compose
```

## No Public Secrets

Do not share admin tokens, Jupyter tokens, private hostnames, `.env` files, or production configuration files in issues, pull requests, or screenshots.

## Security Issues

Do not report security-sensitive details publicly. See `SECURITY.en.md`.
