# FAQ

🌐 Languages: [Deutsch](../FAQ.md) | [English](FAQ.md)

## Is this repository a web app?

No. It is a portable OpenWebUI workbench workspace with model packages, tools, filters, skills, import artifacts, deployment templates, a local dashboard, and validation scripts.

## Which command validates the current state?

```powershell
python scripts/verify_openwebui_workspace.py
```

This command is non-mutating and is the main smoke check for pull requests and local maintenance.

## Why is there no package-manager lockfile?

The repository currently has no project manifest and no conventional app build pipeline. The base validation uses the Python standard library, local scripts, and unit tests. Optional packages can expand OpenWebUI-adjacent schema tests but are not required for the fast base check.

## Why are files in `Modelle/einzelmodelle/` and `Modelle/dist/artifacts/` similar?

That is intentional. `Modelle/einzelmodelle/` is the human-readable maintenance source. `Modelle/dist/` is the canonical handover area for import, copy/paste, ZIP, and air-gap transfer.

## When do dist artifacts need to be regenerated?

When tool, filter, skill, or model artifacts are intentionally changed:

```powershell
python scripts/configure_openwebui_tool_models.py --write --check --rebuild-zips
python scripts/verify_openwebui_workspace.py
```

## What does `Änderungen erkannt: True` mean in the generator check?

The current dist or model state is not synchronized with the generator rules. Run the generator with `--write --check --rebuild-zips`, inspect the diff, and verify again.

## Why is a test skipped?

Minimal environments may miss optional packages such as `pydantic`. In that case OpenWebUI-adjacent GUI schema tests are skipped while structural import tests continue.

## Where do real tokens belong?

In no versioned file. For API imports, create a local `scripts/openwebui_workspace_config.yaml` from `scripts/openwebui_workspace_config.example.yaml`. The real file is ignored.

## How does language selection work?

German is the default. The dashboard can switch to English manually, reads `WORKBENCH_LOCALE`, and can use browser/system language. Unknown or unsupported locales fall back to German. GitHub repository pages use visible language links because GitHub does not automatically translate repository files.

## Are public network tools active in the offline default?

No. The offline default uses air-gap-compatible defaults. Network or rich-UI tools are optional and must be imported, configured, and checked deliberately.

## Where are third-party notices?

In `THIRD_PARTY_NOTICES.md`. It documents reviewed sources, decisions, and imported tool exports.
