# Modelle Dist

Dieser Ordner ist der Air-Gap-Handover-Bereich fuer OpenWebUI.

## Inhalt

- `openwebui-offline-artifacts.zip`: gebuendeltes Paket fuer Transport
- `models_fallback_bundle.json`: generisches Modellbundle
- `tools_fallback_bundle.json`: generisches Toolbundle
- `artifacts/models/`: einzelne `model.json`-Dateien
- `artifacts/tools/`: einzelne Tool-Dateien

## Einsatz

- Fuer Copy/Paste in eine getrennte Zielumgebung diesen Ordner oder die ZIP-Datei verwenden.
- Falls OpenWebUI in der Zielumgebung keine direkte Dateierkennung unterstuetzt, die Inhalte manuell per GUI uebernehmen.
- Falls die Zielinstanz dateibasierte Bereitstellung ueber Container-Volumes erlaubt, diesen Ordner in den Container einhaengen.
