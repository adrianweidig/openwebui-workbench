# OpenWebUI Workbench

🌐 Languages: [Deutsch](README.md) | [English](README.en.md)

![OpenWebUI Workbench Hero](docs/assets/openwebui-workbench-hero.png)

[![CI](https://github.com/adrianweidig/openwebui-workbench/actions/workflows/ci.yml/badge.svg)](https://github.com/adrianweidig/openwebui-workbench/actions/workflows/ci.yml)
[![CodeQL](https://github.com/adrianweidig/openwebui-workbench/actions/workflows/codeql.yml/badge.svg)](https://github.com/adrianweidig/openwebui-workbench/actions/workflows/codeql.yml)
[![License](https://img.shields.io/github/license/adrianweidig/openwebui-workbench)](LICENSE)
[![Issues](https://img.shields.io/github/issues/adrianweidig/openwebui-workbench)](https://github.com/adrianweidig/openwebui-workbench/issues)
[![Pull requests](https://img.shields.io/github/issues-pr/adrianweidig/openwebui-workbench)](https://github.com/adrianweidig/openwebui-workbench/pulls)

Portable OpenWebUI workspace for offline-ready task models, importable tools, filters, skills, handover artifacts, and deployment templates.

This repository bundles domain briefings, human-readable model packages, OpenWebUI import files, Jupyter/artifact tools, a local dashboard, and validation scripts. It is not a conventional web application, intentionally has no package-manager lockfile, and can be cloned into any local path.

## Quick Links

| Goal | Entry point |
|---|---|
| Import models manually | [`Modelle/einzelmodelle/`](Modelle/einzelmodelle/) and [`Modelle/dist/openwebui-models-import.json`](Modelle/dist/openwebui-models-import.json) |
| Import tools and filters | [`Tools/dist/`](Tools/dist/) and [`OPENWEBUI_EXTENSIONS.md`](OPENWEBUI_EXTENSIONS.md) |
| Prepare full API import | [`scripts/openwebui_workspace_config.example.yaml`](scripts/openwebui_workspace_config.example.yaml) |
| Start the dashboard container | [`docs/WORKBENCH_DASHBOARD.md`](docs/WORKBENCH_DASHBOARD.md) and [`Deployment/docker-compose.workbench.yml`](Deployment/docker-compose.workbench.yml) |
| Run local validation | [`TESTING.md`](TESTING.md) |
| Understand deployment mounts | [`Deployment/README.md`](Deployment/README.md) |
| Review architecture | [`docs/en/ARCHITECTURE.md`](docs/en/ARCHITECTURE.md) |
| Contribute | [`CONTRIBUTING.en.md`](CONTRIBUTING.en.md) |
| Understand internationalization | [`docs/en/I18N.md`](docs/en/I18N.md) |

## What This Repository Provides

- 31 curated chat model profiles for recurring workflows such as code analysis, document generation, presentations, n8n workflow design, prompting, data analysis, and offline workbench usage.
- Directly importable OpenWebUI JSON artifacts for models, tools, and functions/filters.
- Offline-default tooling for Jupyter, artifact generation, JSON/CSV/text validation, visuals, subagent planning, Markdown normalization, and context compression.
- A reproducible generator for tool/filter registries, model profiles, embedded icons, ZIP handover bundles, and import plans.
- Non-mutating validation scripts that check Python syntax, OpenWebUI extensions, generator state, import payloads, JSON files, and unit tests.
- Deployment templates for offline OpenWebUI operation with an optional Jupyter server and local addon stack.

## Internationalization

German is the default language for the repository, dashboard UI, primary README, default documentation, and human-readable fallback messages. English is maintained as the main alternative language. GitHub does not automatically switch the normal repository view by visitor language, so the project uses explicit language files and visible links:

- [`README.md`](README.md) is the German default landing page.
- [`README.en.md`](README.en.md) is the English landing page.
- [`docs/de/`](docs/de/) contains the German documentation entry and i18n guidance.
- [`docs/en/`](docs/en/) contains the English documentation entry and i18n guidance.
- Community files such as [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md), [`SUPPORT.md`](SUPPORT.md), [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md), and [`CHANGELOG.md`](CHANGELOG.md) have English `.en.md` variants.
- The Workbench dashboard uses `WORKBENCH_LOCALE`, browser/system language, and a manual language selector. Unknown or missing locale information falls back to German.

All text resources stay UTF-8. Umlauts, accents, emojis, and non-Latin characters are preserved instead of being transliterated when they are visible prose.

## Repository Structure

| Path | Purpose |
|---|---|
| [`OpenWebUI Model Builder/`](OpenWebUI%20Model%20Builder/) | Builder rules and workspace |
| [`Problemfälle/`](Problemfälle/) | Domain briefings used to derive model packages |
| [`Modelle/einzelmodelle/`](Modelle/einzelmodelle/) | Human-readable model packages with prompts, knowledge, examples, and `model.json` |
| [`Modelle/dist/`](Modelle/dist/) | Canonical air-gap handover artifacts, import files, and ZIP bundle |
| [`Tools/jupyter/`](Tools/jupyter/) | Production Jupyter tool with example configuration |
| [`Tools/openwebui_ext/`](Tools/openwebui_ext/) | Importable tools, filters, skills, docs, and tests |
| [`Tools/dist/`](Tools/dist/) | Bundled tool, skill, and function artifacts |
| [`Artefakte/`](Artefakte/) | Local output and handover area; runtime files are ignored |
| [`Deployment/`](Deployment/) | Offline container and volume templates |
| [`Workbench/dashboard/`](Workbench/dashboard/) | Local dashboard with German/English UI resources |
| [`docs/`](docs/) | Public project, architecture, release, and maintainer documentation |

## Quick Start

Start a local OpenWebUI instance plus the Workbench dashboard:

```powershell
Copy-Item Deployment/workbench.env.example .env
docker compose -f Deployment/docker-compose.workbench.yml up -d --build
```

Then open:

- OpenWebUI: `http://localhost:3000`
- Workbench: `http://localhost:8088`
- Optional local `top.secret` edge route: `https://workbench.top.secret`

The Workbench mounts this repository as `/workspace`, edits model Markdown under `Modelle/einzelmodelle/`, tool sources under `Tools/openwebui_ext/tools/`, and skill Markdown under `Tools/openwebui_ext/skills/`. It can generate dist artifacts, run import dry-runs, and sync to the OpenWebUI API when `OPENWEBUI_ADMIN_TOKEN` is set.

If OpenWebUI is already running, start only the Workbench container:

```powershell
$env:OPENWEBUI_BASE_URL="http://host.docker.internal:3000"
docker compose -f Deployment/docker-compose.workbench.yml up -d --build workbench
```

## Validation

Run the non-mutating verification suite:

```powershell
python scripts/verify_openwebui_workspace.py
```

Targeted diagnostics:

```powershell
python -m compileall -q scripts Tools Workbench
python scripts/validate_openwebui_extensions.py
python scripts/configure_openwebui_tool_models.py --check
python Tools/import_openwebui_workspace.py --dry-run --config scripts/openwebui_workspace_config.example.yaml
python -m unittest discover Tools.openwebui_ext.tests
python -m unittest discover Workbench.dashboard.tests
```

When tool, filter, skill, or model artifacts are intentionally changed:

```powershell
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
python scripts/verify_openwebui_workspace.py
```

## Configuration

The local API import configuration is `scripts/openwebui_workspace_config.yaml`. Create it from the versioned example and keep it untracked:

```powershell
Copy-Item scripts/openwebui_workspace_config.example.yaml scripts/openwebui_workspace_config.yaml
notepad scripts/openwebui_workspace_config.yaml
```

Important runtime values include:

- OpenWebUI root URL, for example `http://127.0.0.1:3000`
- OpenWebUI admin API key
- Jupyter URL and token
- artifact and addon paths
- tool valves and function/filter valves
- `import.include_optional_network_tools`
- `WORKBENCH_LOCALE` for the dashboard default language

Never commit real tokens or production configuration files.

## Documentation

- [`docs/en/index.md`](docs/en/index.md): English documentation entry
- [`docs/en/I18N.md`](docs/en/I18N.md): internationalization model
- [`docs/en/ARCHITECTURE.md`](docs/en/ARCHITECTURE.md): components and data flow
- [`docs/en/WORKBENCH_DASHBOARD.md`](docs/en/WORKBENCH_DASHBOARD.md): dashboard usage and configuration
- [`docs/en/FAQ.md`](docs/en/FAQ.md): frequently asked questions
- [`OPENWEBUI_EXTENSIONS.md`](OPENWEBUI_EXTENSIONS.md): tools, filters, skills, valves, security, and tests
- [`TESTING.md`](TESTING.md): validation model and expected checks

## Contributing

Contributions are welcome when they improve offline usability, importability, documentation quality, validation, or maintainability. Read [`CONTRIBUTING.en.md`](CONTRIBUTING.en.md) before opening a pull request and run at least:

```powershell
python scripts/verify_openwebui_workspace.py
```

Do not report sensitive vulnerabilities publicly. See [`SECURITY.en.md`](SECURITY.en.md).

## License and Third-Party Notices

This repository uses the Apache License 2.0; see [`LICENSE`](LICENSE). Third-party sources, reviewed OpenWebUI references, and imported tool exports are documented in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
