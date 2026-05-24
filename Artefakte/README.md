# Artefakte

Dieser Ordner ist der lokale Arbeits- und Übergabebereich für offline erzeugte Ergebnisse aus OpenWebUI.

## Zweck

OpenWebUI soll wie eine lokale ChatGPT-Arbeitsumgebung nutzbar sein: Nutzer fragen im Chat nach Dokumenten, Präsentationen, Tabellen, HTML-Seiten oder PDFs; die Modelle nutzen bei Bedarf Jupyter und die OpenWebUI-Tools; die fertigen Dateien landen kontrolliert im Artefaktbereich.

## Empfohlene Unterstruktur

- `output/`: erzeugte HTML-, PDF-, ZIP-, CSV-, PNG- und JSON-Artefakte.
- `temp/`: temporäre Zwischenstände, die nicht versioniert werden.
- `examples/`: optionale lokale Beispielartefakte ohne vertrauliche Daten.

## OpenWebUI-Konfiguration

Setze für das Artefakt-Tool bevorzugt:

```text
OPENWEBUI_ARTIFACT_ROOT=/app/backend/data/offline_artifacts
```

Für lokale Windows-Arbeit kann dieser Containerpfad auf `<OPENWEBUI_WORKSPACE>\Artefakte\output` gemountet werden. Die genaue Mount-Strategie steht in `Deployment/README.md`.

## Git-Regel

Erzeugte Arbeitsdateien gehören normalerweise nicht ins Git-Repository. Versioniert werden nur Dokumentation, Beispiele ohne sensible Daten und Konfigurationstemplates.
