# Workbench Dashboard

Languages: [Deutsch](../WORKBENCH_DASHBOARD.md) | [English](WORKBENCH_DASHBOARD.md)

The dashboard is the easiest way to maintain the OpenWebUI model packages in this repository.

OpenWebUI stays your chat runtime. The Workbench is a separate local dashboard that edits the files used to build and sync custom GPT-style OpenWebUI models.

## Start

```powershell
if (-not (Test-Path .env)) { Copy-Item Deployment/workbench.env.example .env }
# Edit .env: set WORKBENCH_AUTH_PASSWORD and OPENWEBUI_BASE_URL.
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml pull workbench
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml up -d
```

Open:

```text
http://localhost:8088
```

The standard Compose file starts exactly one container: `workbench`.

For local dashboard image development, add `--build` to build from the checkout.

Set `OPENWEBUI_BASE_URL` in `.env` to the OpenWebUI instance the container should call. For Docker Desktop with OpenWebUI running on the host, the default is usually enough:

```env
OPENWEBUI_BASE_URL=http://host.docker.internal:3000
OPENWEBUI_PUBLIC_URL=http://localhost:3000
```

## What To Edit

Use the dashboard to edit:

- `mainprompt.md`
- `fachwissen.md`
- `Golden_Example.*`
- examples under `beispiele/`
- each model's `model.json`
- tools under `Tools/openwebui_ext/tools/`
- filters under `Tools/openwebui_ext/filters/`
- skills under `Tools/openwebui_ext/skills/`
- prompt templates under `Tools/openwebui_ext/prompts/`

The repository remains the source of truth.

## Model Settings

Every model has a **Settings** tab. Use it when the target OpenWebUI environment is different from the maintainer's setup.

Common fields:

- `base_model_id`
- name, description, and tags
- capabilities
- `toolIds`, `filterIds`, and `skillIds`
- `params.temperature`
- `params.top_p`
- `params.stop`
- `params.function_calling`
- `params.reasoning_effort`
- `params.parallel_tool_calls`
- raw JSON for fields that do not have a form control yet

After saving, regenerate the import artifacts and run an import dry-run before syncing.

## Sync Flow

1. Edit model files or settings.
2. Save.
3. Run **Regenerate artifacts**.
4. Run **Check import**.
5. Set `OPENWEBUI_ADMIN_TOKEN` or `OPENWEBUI_ADMIN_TOKEN_FILE` only when you want real API sync.
6. Run **Sync to OpenWebUI**.

Without an admin token, the Workbench still works as an editor and artifact generator.

## Model Status

The Workbench can compare local model definitions with OpenWebUI.

Status values:

- `identical`: local and OpenWebUI fields match
- `local_only`: the model exists only in the repository
- `remote_only`: the model exists only in OpenWebUI
- `conflict`: both sides exist, but managed fields differ
- `remote_inactive`: OpenWebUI reports the model as inactive or deleted
- `read_error`: OpenWebUI could not be read cleanly

The Workbench does not destructively pull remote models into the repository. Remote-only models are shown as read-only snapshots.

## Security

- Compose binds the dashboard to `127.0.0.1`.
- Compose requires dashboard authentication.
- Tokens are read from environment variables or token files only.
- Mutating API routes require the dashboard's same-origin request header.
- Dashboard actions run fixed repository commands, not arbitrary shell input.

## Validate

```powershell
python scripts/verify_openwebui_workspace.py
python -m unittest discover Workbench.dashboard.tests
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml config
```
