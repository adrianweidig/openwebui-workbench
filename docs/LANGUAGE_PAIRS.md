# Sprachpaarpflege

Dieses Repository nutzt Deutsch als Standard und Englisch als wichtigste Alternativsprache. Die folgende Liste ist der bewusst gepflegte Mindestumfang; sie ist keine Aussage, dass jede Nebendatei vollständig übersetzt ist.

## Erwartete Paare

| Deutsch | Englisch |
|---|---|
| `README.md` | `README.en.md` |
| `CONTRIBUTING.md` | `CONTRIBUTING.en.md` |
| `SECURITY.md` | `SECURITY.en.md` |
| `SUPPORT.md` | `SUPPORT.en.md` |
| `CODE_OF_CONDUCT.md` | `CODE_OF_CONDUCT.en.md` |
| `CHANGELOG.md` | `CHANGELOG.en.md` |
| `docs/ARCHITECTURE.md` | `docs/en/ARCHITECTURE.md` |
| `docs/WORKBENCH_DASHBOARD.md` | `docs/en/WORKBENCH_DASHBOARD.md` |
| `docs/de/index.md` | `docs/en/index.md` |
| `docs/de/I18N.md` | `docs/en/I18N.md` |

## Prüfung

Der zentrale Verify-Runner prüft, dass diese Paare existieren und am Dateianfang sichtbare Sprachlinks tragen:

```powershell
python scripts/check_doc_language_pairs.py
python scripts/verify_openwebui_workspace.py
```

Neue zentrale deutsch/englische Dokumente sollten in `scripts/check_doc_language_pairs.py` ergänzt werden. Einseitige Spezialdokumente sind erlaubt, wenn sie nicht als kanonischer Einstieg dienen.
