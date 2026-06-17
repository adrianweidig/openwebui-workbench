# Language Pair Maintenance

Languages: [English](LANGUAGE_PAIRS.md) | [Deutsch](LANGUAGE_PAIRS.md)

`README.md` is now the English GitHub landing page. German remains available as `README.de.md`.

This list is the minimum set of documentation pairs checked by the verify runner. It does not claim that every secondary file is translated.

## Expected Pairs

| Deutsch | Englisch |
|---|---|
| `README.de.md` | `README.md` |
| `CONTRIBUTING.md` | `CONTRIBUTING.en.md` |
| `SECURITY.md` | `SECURITY.en.md` |
| `SUPPORT.md` | `SUPPORT.en.md` |
| `CODE_OF_CONDUCT.md` | `CODE_OF_CONDUCT.en.md` |
| `CHANGELOG.md` | `CHANGELOG.en.md` |
| `docs/ARCHITECTURE.md` | `docs/en/ARCHITECTURE.md` |
| `docs/WORKBENCH_DASHBOARD.md` | `docs/en/WORKBENCH_DASHBOARD.md` |
| `docs/de/index.md` | `docs/en/index.md` |
| `docs/de/I18N.md` | `docs/en/I18N.md` |

## Check

The central verify runner checks that these files exist and include visible language links near the top:

```powershell
python scripts/check_doc_language_pairs.py
python scripts/verify_openwebui_workspace.py
```

Add new canonical German/English documentation pairs to `scripts/check_doc_language_pairs.py`. One-off specialty documents can stay single-language when they are not a main entry point.
