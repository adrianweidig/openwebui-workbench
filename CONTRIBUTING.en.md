# Contributing

🌐 Languages: [Deutsch](CONTRIBUTING.md) | [English](CONTRIBUTING.en.md)

Thank you for your interest in OpenWebUI Workbench. Contributions are welcome when they improve direct OpenWebUI usability, offline capability, documentation, validation, or maintainability.

## Suitable Contributions

- new or more precise domain briefings under `Problemfälle/`
- improvements to model packages under `Modelle/einzelmodelle/`
- safe OpenWebUI tools, filters, or skills under `Tools/openwebui_ext/`
- tests for tools, filters, import logic, dashboard i18n, and generator behavior
- documentation fixes for import, deployment, valves, failure modes, localization, or offline operation
- small repository-hygiene improvements without broad formatting churn

## Local Setup

No package installation is required for the base check. Python 3.10 or newer is required.

```powershell
git clone https://github.com/adrianweidig/openwebui-workbench.git
cd openwebui-workbench
python scripts/verify_openwebui_workspace.py
```

Optional packages such as `pydantic`, `fastapi`, `aiohttp`, `requests`, and `starlette` can expand OpenWebUI-adjacent schema tests. Docker is only relevant for the optional Compose validation.

## Development Rules

- Do not destructively overwrite existing content.
- Treat `Problemfälle/` as the domain source and avoid casual rewriting.
- Maintain operational model artifacts under `Modelle/` and tool artifacts under `Tools/`.
- `Modelle/dist/` and `Tools/dist/` are canonical handover artifacts and should only be regenerated deliberately.
- Do not commit secrets, tokens, API keys, or production credentials.
- Do not add public network defaults to offline tools.
- Document new external sources or imported tool exports in `THIRD_PARTY_NOTICES.md`.
- Keep German as the default language and update English variants when user-facing documentation changes.

## Tests and Validation

Before every pull request, run at least:

```powershell
python scripts/verify_openwebui_workspace.py
```

For targeted diagnosis:

```powershell
python -m compileall -q scripts Tools Workbench
python scripts/validate_openwebui_extensions.py
python scripts/configure_openwebui_tool_models.py --check
python Tools/import_openwebui_workspace.py --dry-run --config scripts/openwebui_workspace_config.example.yaml
python -m unittest discover Tools.openwebui_ext.tests
python -m unittest discover Workbench.dashboard.tests
```

When tool, filter, skill, or model artifacts are changed:

```powershell
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
python scripts/verify_openwebui_workspace.py
```

If Docker is available:

```powershell
python scripts/verify_openwebui_workspace.py --include-docker-compose
```

## Pull Requests

A good pull request includes:

- a short description of the problem or goal
- affected areas such as models, tools, filters, docs, i18n, or deployment
- checks that were run and their results
- notes about intentionally untested optional paths
- no irrelevant formatting changes

## Commit Style

Short, meaningful commit messages are sufficient. Useful prefixes include:

- `docs:`
- `test:`
- `tools:`
- `models:`
- `i18n:`
- `ci:`
- `chore:`

## Issues

Please open issues with clear reproduction steps, environment details, and expected impact. Security-sensitive details do not belong in public issues; see `SECURITY.en.md`.
