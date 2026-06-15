# Changelog

🌐 Languages: [Deutsch](CHANGELOG.md) | [English](CHANGELOG.en.md)

All notable changes to this repository are collected here. Published handover states are also documented through GitHub Releases and their related artifacts.

## Unreleased

- Switched Workbench model imports to real required file context for `mainprompt.md`, `fachwissen.md`, and `Golden_Example.<ext>`.
- Extended the Workbench dashboard with selectable base model, bulk actions, and detailed live logs for long-running actions.
- Hardened the context compressor and added the required-file filter to protect the mandatory full-context system block from compression.
- Added public infrastructure marker checks and removed local domain-specific handover templates.
- Removed historical root snapshot notes; current status is documented through the verify runner, release notes, and maintainer checklist.
- Validated the offline image `openwebui-workbench-dashboard:seu` as a local Portainer import tar.
- Documented and hardened `internetwissen` as an integrated offline research and explanation model.
- Added the offline data policy with KnowledgePack structure and a combined 10 GiB limit.
- Added KnowledgePack manifest validation and offline data budget checks to the verify runner.
- Updated README, roadmap, model inventory, and release process to match the actual integration state.
- Regenerated model, tool, and offline handover dist artifacts.
- Added multilingual repository structure, English README/community variants, and dashboard i18n with German fallback.
- Added public repository documentation, community files, CI workflows, and maintainer checklist.
- Made OpenWebUI workbench structure, import paths, validation, and offline boundaries easier to navigate from the README.
