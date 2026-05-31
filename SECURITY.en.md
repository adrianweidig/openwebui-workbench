# Security Policy

🌐 Languages: [Deutsch](SECURITY.md) | [English](SECURITY.en.md)

## Scope

This repository contains OpenWebUI model artifacts, Python tools, filters, skills, import scripts, a local dashboard, and deployment templates. Security-relevant areas include:

- server-side OpenWebUI tools
- Jupyter and artifact valves
- optional network tools
- import scripts with admin API access
- local configuration files and tokens
- dashboard write access and HTTP Basic Auth

## Reporting Security Issues

Do not post sensitive vulnerability details, tokens, private URLs, or exploit steps in public issues.

If GitHub Private Vulnerability Reporting is enabled for this repository, use that private channel. If it is not enabled, the maintainer should first configure a private security contact or GitHub Security Advisories; concrete steps are listed in `docs/MAINTAINER_CHECKLIST.md`.

## Handling Secrets

- Real values do not belong in Git.
- Local configurations such as `scripts/openwebui_workspace_config.yaml` stay ignored.
- Example values must remain obvious placeholders.
- Review logs and screenshots for tokens, hostnames, and internal paths before sharing.
- The local Workbench dashboard sets browser security headers and is still intended only for local or additionally protected environments.

## Local Security Checks

The central verification runner includes a non-leaking secret hygiene check:

```powershell
python scripts/check_security_hygiene.py
```

The check reports only path, line, and finding type. Suspect values are never printed. An optional Bandit run can be added locally without introducing a required dependency:

```powershell
python scripts/check_security_hygiene.py --include-bandit
```

## Expected Process

After a private report, the maintainer should:

1. Check receipt and reproducibility.
2. Scope the affected tools, filters, import paths, dashboard routes, or documents.
3. Prepare a minimal fix or clear mitigation.
4. Validate with `python scripts/verify_openwebui_workspace.py`.
5. Choose publication and advisory details in a way that protects users.

## Limits

This repository does not provide a security guarantee for any specific OpenWebUI instance. Every target environment must validate its own authentication, network boundaries, tool valves, Jupyter sandboxing, filesystem mounts, and admin permissions.
