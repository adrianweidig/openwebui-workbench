# Deployment

Use this folder when you want to run the Workbench dashboard as a container.

The normal path is intentionally small:

- one Compose file: `Deployment/docker-compose.workbench.yml`
- one container: `workbench`
- one target OpenWebUI URL in `.env`
- no Compose profiles
- no stacked override files for the default setup

## Start

Create the local `.env` file:

```powershell
if (-not (Test-Path .env)) { Copy-Item Deployment/workbench.env.example .env }
```

Fill `WORKBENCH_AUTH_PASSWORD` locally, then check the OpenWebUI URLs:

```env
OPENWEBUI_BASE_URL=http://host.docker.internal:3000
OPENWEBUI_PUBLIC_URL=http://localhost:3000
```

Start the Workbench:

```powershell
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml pull workbench
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml up -d
```

Open the dashboard:

```text
http://localhost:8088
```

The dashboard asks for HTTP Basic Auth. Keep `WORKBENCH_AUTH_PASSWORD` local and do not commit `.env`.

For local image development, build from the checkout instead:

```powershell
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml up -d --build
```

## What The Container Does

The Workbench container mounts the repository as `/workspace`.

From there it can:

- edit model Markdown files under `Modelle/einzelmodelle/`
- edit each model's `model.json`
- edit tools, filters, skills, and prompt templates
- regenerate import artifacts under `Modelle/dist/` and `Tools/dist/`
- run import dry-runs
- sync to OpenWebUI when `OPENWEBUI_ADMIN_TOKEN` or `OPENWEBUI_ADMIN_TOKEN_FILE` is configured

The Workbench does not start or replace OpenWebUI. OpenWebUI remains your separate runtime.

## Minimal `.env`

The local `.env` already contains the needed keys after copying the example. The values most users touch are:

```env
WORKBENCH_IMAGE=ghcr.io/adrianweidig/openwebui-workbench/workbench-dashboard:latest
OPENWEBUI_BASE_URL=http://host.docker.internal:3000
OPENWEBUI_PUBLIC_URL=http://localhost:3000
WORKBENCH_PORT=8088
WORKBENCH_LOCALE=en
```

For real API sync, set one of these in the local `.env`:

```env
OPENWEBUI_ADMIN_TOKEN=
OPENWEBUI_ADMIN_TOKEN_FILE=/run/secrets/openwebui-admin-token
```

Do not commit `.env`, tokens, or secret files.

## Smoke Check

```powershell
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml ps
docker compose --env-file .env -f Deployment/docker-compose.workbench.yml logs --tail=100 workbench
python scripts/verify_openwebui_workspace.py
```

If Docker is available only through WSL, run the non-mutating checks with an explicit Docker command:

```powershell
python scripts/check_workbench_setup.py --docker-command "wsl.exe -d Debian -- docker" --require-docker --run-compose-config
python scripts/verify_openwebui_workspace.py --include-docker-compose --docker-command "wsl.exe -d Debian -- docker"
```

## Private HTTPS

For an OpenWebUI endpoint behind a private CA, mount or provide a CA file and set:

```env
OPENWEBUI_TLS_VERIFY=true
OPENWEBUI_CA_FILE=/path/in/container/root-ca.pem
```

Use `OPENWEBUI_TLS_VERIFY=false` only for a short local diagnostic run.

## Full OpenWebUI Example

`docker-compose.openwebui-offline.example.yml` is kept as a separate example for people who want to study a fuller offline OpenWebUI setup. It is not the default Workbench deployment path.

## Portainer

Use the same single Compose file in Portainer. Paste `Deployment/docker-compose.workbench.yml` as the stack file and set the values from your local `.env` as stack environment variables. Review values before deployment and keep tokens outside Git.
