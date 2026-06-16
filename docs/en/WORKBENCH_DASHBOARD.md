# Workbench Dashboard

🌐 Languages: [Deutsch](../WORKBENCH_DASHBOARD.md) | [English](WORKBENCH_DASHBOARD.md)

The Workbench dashboard turns this repository into an active management UI for an OpenWebUI instance. OpenWebUI remains the chat and runtime container; the Workbench runs next to it and manages the sources used to generate and synchronize tools, functions/filters, skills, prompt templates, knowledge, and model profiles.

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
- `Tools/openwebui_ext/filters/*.py`
- `Tools/openwebui_ext/skills/*.md`
- `Tools/openwebui_ext/prompts/*.md`
- `Tools/dist/`
- `Modelle/dist/`

## Compose Start

```powershell
python scripts/init_workbench_env.py
python scripts/init_workbench_env.py --check
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml up -d --build
```

The init command creates an ignored local `.env` from `Deployment/workbench.env.example`, sets random values for `WEBUI_SECRET_KEY` and `WORKBENCH_AUTH_PASSWORD`, and does not print those values to the console. Existing `.env` files are not overwritten without `--force`.

For Compose or Portainer, the local `.env` must set `WORKBENCH_REQUIRE_AUTH=true` and either `WORKBENCH_AUTH_PASSWORD` or a mounted `WORKBENCH_AUTH_PASSWORD_FILE`. Without effective authentication the dashboard container exits with a clear startup error; with a password set, all dashboard routes are protected with HTTP Basic Auth. `WORKBENCH_AUTH_USERNAME` is optional and defaults to `workbench`.

Then open:

- OpenWebUI: `http://localhost:3000`
- Workbench: `http://localhost:8088`

If the local `top.secret` edge proxy is used, the Workbench can also be exposed as `https://workbench.top.secret`. When the edge is published on a non-default host port, include that port in the URL, for example `https://workbench.top.secret:25443`.

## Workflow

1. Select a model in the dashboard.
2. Edit `systemprompt.md`, `mainprompt.md`, `fachwissen.md`, examples, tools, functions/filters, skills, or prompt templates.
3. Save the file.
4. Run `Regenerate artifacts`.
5. Run `Check import`.
6. In the sync panel, optionally load base models, select the target OpenWebUI base model, and with `OPENWEBUI_ADMIN_TOKEN` or `OPENWEBUI_ADMIN_TOKEN_FILE` set, run `Sync to OpenWebUI`. This sync imports all Workbench models plus tools, functions/filters, skills, prompt templates, required files, and knowledge.
7. Run `Compare model status` to compare Workbench-managed model fields with OpenWebUI.
8. Run `Refresh OpenWebUI snapshot` when OpenWebUI-only models should be visible in the Workbench.

The real OpenWebUI sync runs as a background job. The dashboard remains usable while it runs; triggering the same sync again shows the active job instead of starting a parallel import.

## Bidirectional Model Check

The Workbench remains the write source for the versioned model packages under `Modelle/einzelmodelle/`. The existing API import mirrors these packages to OpenWebUI. The reverse direction deliberately has no automatic destructive pull: `scripts/sync_openwebui_models.py` reads OpenWebUI through the API, compares the managed fields `id`, `name`, `base_model_id`, `params`, and known Workbench `meta` keys with the local model state, and can write an auditable snapshot under `Artefakte/openwebui_sync/`.

Status values are:

- `identical`: local Workbench source and active OpenWebUI model match in the managed fields.
- `local_only`: the model exists locally but not in OpenWebUI.
- `remote_only`: the model exists in OpenWebUI but has no local Workbench source.
- `conflict`: both sides exist, but at least one managed field differs.
- `remote_inactive`: OpenWebUI still knows the model ID, but it is inactive or deleted.
- `read_error`: OpenWebUI could not be queried or the response could not be parsed.

CLI check without local writes:

```powershell
python scripts/sync_openwebui_models.py --base-url https://openwebui.top.secret --token-file /run/secrets/openwebui-admin-token --ca-file /certs/top-secret-edge-root-ca.pem
```

CLI snapshot for the Workbench view:

```powershell
python scripts/sync_openwebui_models.py --base-url https://openwebui.top.secret --token-file /run/secrets/openwebui-admin-token --ca-file /certs/top-secret-edge-root-ca.pem --write-snapshot
```

After `--write-snapshot`, the dashboard reads `Artefakte/openwebui_sync/status.json`. Remote-only models appear in the model list with the `OpenWebUI only` status; the editor remains read-only for these entries so no local model source is invented or overwritten.

## Automation

On normal dashboard startup the Workbench configures an internal automation. The safe default is a non-mutating workspace check every 30 minutes (`WORKBENCH_AUTOMATION_ACTIONS=check`). This keeps status, generator, JSON, and unit-test drift visible without changing model sources or OpenWebUI automatically.

Mutating automation actions are opt-in: add `generate`, `import-dry-run`, or `import-openwebui` to `WORKBENCH_AUTOMATION_ACTIONS` only after the administrator accepts the write/API effect and has configured the required tokens. `sync-status` is non-mutating and can be automated when desired; `pull-openwebui` writes local snapshots and therefore remains a deliberate manual action. The scheduler uses the same job locks as the manual UI; an already running job for the same action is not started in parallel.

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
python scripts/sync_openwebui_models.py --base-url <OPENWEBUI_BASE_URL> --token-file <OPENWEBUI_ADMIN_TOKEN_FILE> --write-snapshot
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
| `OPENWEBUI_ADMIN_TOKEN_HOST_FILE` | Host path for generated Portainer stacks or the optional Compose override `docker-compose.openwebui-admin-token-file.yml`, bind-mounted read-only to `OPENWEBUI_ADMIN_TOKEN_FILE`. |
| `WORKBENCH_AUTH_USERNAME` | Username for dashboard HTTP Basic Auth. Compose default: `workbench`. |
| `WORKBENCH_REQUIRE_AUTH` | `true` requires effective dashboard authentication at startup. Compose/Portainer set this by default. |
| `WORKBENCH_AUTH_PASSWORD` | Password for dashboard HTTP Basic Auth. Alternative to `WORKBENCH_AUTH_PASSWORD_FILE`; do not commit it. |
| `WORKBENCH_AUTH_PASSWORD_FILE` | Alternative path to a password file in the container. |
| `WORKBENCH_AUTH_PASSWORD_HOST_FILE` | Host path for generated Portainer stacks or the optional Compose override `docker-compose.workbench-password-file.yml`, bind-mounted read-only to `WORKBENCH_AUTH_PASSWORD_FILE`. |
| `WORKBENCH_ALLOW_WRITE` | `true` allows Markdown write access. |
| `WORKBENCH_COMMAND_TIMEOUT_SECONDS` | Timeout for generator, dry-run, and verification actions. |
| `WORKBENCH_IMPORT_TIMEOUT_SECONDS` | Process timeout for the background OpenWebUI sync. Default: 1800 seconds. |
| `WORKBENCH_IMPORT_HTTP_TIMEOUT_SECONDS` | HTTP timeout per OpenWebUI API request during import. Default: 600 seconds. |
| `WORKBENCH_AUTOMATION_ENABLED` | Enables dashboard automation. Default: `true`. |
| `WORKBENCH_AUTOMATION_INTERVAL_MINUTES` | Dashboard automation interval. Default: `30`, allowed range: `5` to `1440`. |
| `WORKBENCH_AUTOMATION_ACTIONS` | Comma-separated actions for automatic runs. Default: `check`; allowed values: `check`, `generate`, `import-dry-run`, `import-openwebui`, `sync-status`. |
| `WORKBENCH_AUTOMATION_RUN_ON_START` | `true` starts the first automation run immediately on dashboard startup. Default: `false`, keeping startup quiet. |
| `WORKBENCH_LOCALE` | Dashboard default locale, currently `de` or `en`. |

## Security

The dashboard is intended for local use. In Compose it is bound to `127.0.0.1`. When `WORKBENCH_AUTH_USERNAME` and a password or password file are set, all routes are protected with HTTP Basic Auth. With `WORKBENCH_REQUIRE_AUTH=true`, the dashboard does not start without that auth configuration. Direct non-loopback binds such as `0.0.0.0` are blocked unless authentication is present. API tokens are read only from environment variables or token files and are redacted in action output.

Mutating API routes (`POST`, `PUT`, `DELETE`) also require the `X-Workbench-Request: same-origin` header. The dashboard UI sends it automatically; direct API clients must set it explicitly.

Dashboard responses set restrictive browser security headers such as `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, and `Referrer-Policy`.

## Validation

```powershell
python scripts/verify_openwebui_workspace.py
python -m unittest discover Workbench.dashboard.tests
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml config
```

The Docker check is optional and requires a local Docker installation. If Docker is available only through WSL, the setup doctor can probe that path without starting containers:

```powershell
python scripts/check_workbench_setup.py --docker-command "wsl.exe -d Debian -- docker" --require-docker
```

This preflight runs `docker compose version` and reports a disabled `WSLService` or unavailable WSL Docker path before any Compose startup is attempted.
