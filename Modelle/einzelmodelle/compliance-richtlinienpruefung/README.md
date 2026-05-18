# Compliance- und Richtlinienprüfung

## Zweck

Nutzer möchten Inhalte gegen bereitgestellte interne Regeln, Checklisten, Datenschutzvorgaben oder Qualitätsrichtlinien prüfen.

**Dieses Modell soll ausgewählt werden,** wenn ein Dokument gegen bekannte, vom Nutzer bereitgestellte Vorgaben geprüft werden soll, nicht gegen aktuelle externe Gesetze.

## Quelle

Erzeugt aus `25_compliance-richtlinienpruefung.md`.

## OpenWebUI-Basis

- Basismodell: `coder`
- Reale technische Grundlage laut Problemfall: `rdtand/Mistral-Medium-3.5-128B-PrismaQuant-4.75-vllm`
- Offline-Betrieb: ja
- Web Search: aus
- Jupyter: optional

## Dateien

- `model.json`: generisches Modellprofil
- `systemprompt.md`: kompakter Systemprompt
- `mainprompt.md`: operative Arbeitslogik
- `fachwissen.md`: domänenspezifische Regeln

## Hinweis

Die JSON-Struktur ist eine Fallback-Struktur, weil lokal kein Referenzexport der Zielinstanz vorhanden war.
