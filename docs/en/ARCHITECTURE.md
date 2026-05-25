# Architecture

🌐 Languages: [Deutsch](../ARCHITECTURE.md) | [English](ARCHITECTURE.md)

This repository is a portable OpenWebUI workbench workspace. It does not contain a full running application; it contains curated sources, generator logic, importable artifacts, a local dashboard, and validation.

## Components

```mermaid
flowchart LR
  Briefings["Problemfälle<br/>domain briefings"] --> Builder["OpenWebUI Model Builder<br/>rules and generator workspace"]
  Builder --> Models["Modelle/einzelmodelle<br/>human-readable model packages"]
  Models --> Dist["Modelle/dist<br/>imports, ZIPs, handover"]
  Tools["Tools/openwebui_ext<br/>tools, filters, skills"] --> ToolDist["Tools/dist<br/>OpenWebUI bundles"]
  Jupyter["Tools/jupyter<br/>Jupyter tool"] --> ToolDist
  Dashboard["Workbench/dashboard<br/>local repository UI"] --> Models
  Dashboard --> Tools
  ToolDist --> Importer["Tools/import_openwebui_workspace.py<br/>API import"]
  Dist --> Importer
  Config["scripts/openwebui_workspace_config.yaml<br/>local ignored target config"] --> Importer
  Importer --> OpenWebUI["OpenWebUI target instance"]
  Artifacts["Artefakte/output<br/>local runtime outputs"] <--> OpenWebUI
```

## Main Areas

| Area | Purpose |
|---|---|
| `Problemfälle/` | Domain starting points for model packages |
| `OpenWebUI Model Builder/` | Builder rules and generator workspace |
| `Modelle/einzelmodelle/` | Primary human-readable model store |
| `Modelle/dist/` | Canonical handover and import artifacts |
| `Tools/jupyter/` | Controlled Python execution through Jupyter |
| `Tools/openwebui_ext/` | OpenWebUI tools, filters, skills, docs, and tests |
| `Tools/dist/` | Importable tool, skill, and function bundles |
| `Workbench/dashboard/` | Local dashboard with German/English UI resources |
| `scripts/` | Generator, validation, and example configuration scripts |
| `Deployment/` | Offline Compose and volume templates |
| `Artefakte/` | Local runtime and handover files, usually not versioned |

## Generation and Import Flow

1. Domain requirements are described in `Problemfälle/`.
2. Model packages are maintained in `Modelle/einzelmodelle/`.
3. Tools, filters, and skills are maintained under `Tools/openwebui_ext/`.
4. `scripts/configure_openwebui_tool_models.py` checks and normalizes tool, filter, and model assignments.
5. The generator writes registries, import files, summaries, and ZIPs to `Modelle/dist/` and `Tools/dist/`.
6. `Tools/import_openwebui_workspace.py` can import these artifacts into a target OpenWebUI instance with a local YAML configuration.

## Validation

The central verification runner is `scripts/verify_openwebui_workspace.py`. It runs Python syntax compilation, extension validation, generator checks, an import dry-run, JSON validation, and unit tests.

## Security Boundaries

Real OpenWebUI admin tokens, Jupyter tokens, and local target configurations are not versioned. Network-capable tools are not part of the offline default import. Target instances must secure their own authentication, network boundaries, tool valves, Jupyter sandboxing, filesystem mounts, and admin permissions.
