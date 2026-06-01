# Workbench Dashboard

🌐 Languages: [Deutsch](../WORKBENCH_DASHBOARD.md) | [English](WORKBENCH_DASHBOARD.md)

The Workbench dashboard turns this repository into an active management UI for an OpenWebUI instance. OpenWebUI remains the chat and runtime container; the Workbench runs next to it and manages the sources used to generate and synchronize tools, filters, skills, knowledge, and model profiles.

## Target Setup

```text
Browser
  |-- http://localhost:3000  -> OpenWebUI
  `-- http://localhost:8088  -> Workbench Dashboard

Docker Compose
  |-- openwebui  -> /app/backend/data
  `-- workbench  -> /workspace  (this repository as a volume)
```

The editable source remains the repository:

- `Modelle/einzelmodelle/<modell>/systemprompt.md`
- `Modelle/einzelmodelle/<modell>/mainprompt.md`
- `Modelle/einzelmodelle/<modell>/fachwissen.md`
- model-defined example result files such as `beispielergebnis.md`, `beispielergebnis.html`, or `beispielergebnis.json`
- approved examples under `Modelle/einzelmodelle/<modell>/beispiele/`
- `Tools/openwebui_ext/tools/*.py`
- `Tools/openwebui_ext/skills/*.md`
- `Tools/dist/`
- `Modelle/dist/`

## Compose Start

```powershell
python scripts/init_workbench_env.py
python scripts/init_workbench_env.py --check
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml up -d --build
```

The init command creates an ignored local `.env` from `Deployment/workbench.env.example`, sets random values for `WEBUI_SECRET_KEY` and `WORKBENCH_AUTH_PASSWORD`, and does not print those values to the console. Existing `.env` files are not overwritten without `--force`.

The local `.env` must set `WORKBENCH_AUTH_PASSWORD`. Without this password Docker Compose fails before starting the dashboard; with a password set, all dashboard routes are protected with HTTP Basic Auth. `WORKBENCH_AUTH_USERNAME` is optional and defaults to `workbench`.

Then open:

- OpenWebUI: `http://localhost:3000`
- Workbench: `http://localhost:8088`

If the local `top.secret` edge proxy is used, the Workbench can also be exposed as `https://workbench.top.secret`. When the edge is published on a non-default host port, include that port in the URL, for example `https://workbench.top.secret:25443`.

## Workflow

1. Select a model in the dashboard.
2. Edit `systemprompt.md`, `mainprompt.md`, `fachwissen.md`, examples, tools, or skills.
3. Save the file.
4. Run `Regenerate artifacts`.
5. Run `Check import`.
6. With `OPENWEBUI_ADMIN_TOKEN` set, run `Sync to OpenWebUI`.

The real OpenWebUI sync runs as a background job. The dashboard remains usable while it runs; triggering the same sync again shows the active job instead of starting a parallel import.

## Automation

On normal dashboard startup the Workbench configures an internal automation. The safe default is a non-mutating workspace check every 30 minutes (`WORKBENCH_AUTOMATION_ACTIONS=check`). This keeps status, generator, JSON, and unit-test drift visible without changing model sources or OpenWebUI automatically.

Mutating automation actions are opt-in: add `generate`, `import-dry-run`, or `import-openwebui` to `WORKBENCH_AUTOMATION_ACTIONS` only after the administrator accepts the write/API effect and has configured the required tokens. The scheduler uses the same job locks as the manual UI; an already running job for the same action is not started in parallel.

A manual automation run remains independent from the interval:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8088/api/automation/run -Headers @{ "X-Workbench-Request" = "same-origin" }
```

When Basic Auth is enabled, include the dashboard credentials as well. In the browser, the `Sync` action cards remain the preferred manual path.

The sync actions use the existing scripts:

```powershell
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
python scripts/configure_openwebui_tool_models.py --write --check --import-dry-run --config scripts/openwebui_workspace_config.example.yaml
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips --import-openwebui --base-url <OPENWEBUI_BASE_URL> --token <OPENWEBUI_ADMIN_TOKEN>
```

## Internationalization

The dashboard defaults to German. It can switch to English through the language selector or by setting `WORKBENCH_LOCALE=en`. Unknown or unsupported browser/system languages fall back to German. UI messages live under `Workbench/dashboard/static/locales/`; API and server messages live in `Workbench/dashboard/i18n.py`.

## Configuration

| Variable | Purpose |
|---|---|
| `OPENWEBUI_BASE_URL` | URL used by the Workbench container to reach the OpenWebUI API. |
| `OPENWEBUI_PUBLIC_URL` | Browser link in the dashboard, usually `http://localhost:3000`. |
| `OPENWEBUI_TLS_VERIFY` | `true` verifies HTTPS certificates. |
| `OPENWEBUI_CA_FILE` | Optional CA bundle path for private local certificates. |
| `OPENWEBUI_CA_PATH` | Optional CA directory for private local certificates. |
| `OPENWEBUI_ADMIN_TOKEN` | Admin API key for real synchronization. |
| `OPENWEBUI_ADMIN_TOKEN_FILE` | Alternative path to a token file in the container. |
| `WORKBENCH_AUTH_USERNAME` | Username for dashboard HTTP Basic Auth. Compose default: `workbench`. |
| `WORKBENCH_AUTH_PASSWORD` | Password for dashboard HTTP Basic Auth. Required by Compose. Do not commit it. |
| `WORKBENCH_AUTH_PASSWORD_FILE` | Alternative path to a password file in the container. |
| `WORKBENCH_ALLOW_WRITE` | `true` allows Markdown write access. |
| `WORKBENCH_COMMAND_TIMEOUT_SECONDS` | Timeout for generator, dry-run, and verification actions. |
| `WORKBENCH_IMPORT_TIMEOUT_SECONDS` | Process timeout for the background OpenWebUI sync. Default: 1800 seconds. |
| `WORKBENCH_IMPORT_HTTP_TIMEOUT_SECONDS` | HTTP timeout per OpenWebUI API request during import. Default: 600 seconds. |
| `WORKBENCH_AUTOMATION_ENABLED` | Enables dashboard automation. Default: `true`. |
| `WORKBENCH_AUTOMATION_INTERVAL_MINUTES` | Dashboard automation interval. Default: `30`, allowed range: `5` to `1440`. |
| `WORKBENCH_AUTOMATION_ACTIONS` | Comma-separated actions for automatic runs. Default: `check`; allowed values: `check`, `generate`, `import-dry-run`, `import-openwebui`. |
| `WORKBENCH_AUTOMATION_RUN_ON_START` | `true` starts the first automation run immediately on dashboard startup. Default: `false`, keeping startup quiet. |
| `WORKBENCH_LOCALE` | Dashboard default locale, currently `de` or `en`. |

## Security

The dashboard is intended for local use. In Compose it is bound to `127.0.0.1`. When `WORKBENCH_AUTH_USERNAME` and a password are set, all routes are protected with HTTP Basic Auth. Direct non-loopback binds such as `0.0.0.0` are blocked unless that auth configuration is present. API tokens are read only from environment variables or token files and are redacted in action output.

Mutating API routes (`POST`, `PUT`, `DELETE`) also require the `X-Workbench-Request: same-origin` header. The dashboard UI sends it automatically; direct API clients must set it explicitly.

Dashboard responses set restrictive browser security headers such as `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, and `Referrer-Policy`.

## Validation

```powershell
python scripts/verify_openwebui_workspace.py
python -m unittest discover Workbench.dashboard.tests
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml config
```

The Docker check is optional and requires a local Docker installation.
