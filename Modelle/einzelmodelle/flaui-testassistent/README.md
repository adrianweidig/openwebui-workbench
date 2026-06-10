# OpenWebUI-Paket 2: FlaUI-Testassistent

## Zweck

Dieses Paket erzeugt ein dauerhaft einsetzbares Custom OpenWebUI-Aufgabenmodell für FlaUI-Testarbeit: Analyse, Generierung, Review, Diagnose, Refactoring und Pipelineprüfung.

## Aufgabenmodell

- Anzeigename: `FlaUI-Testassistent`
- Technische ID: `flaui-testassistent`
- Basismodell: `coder`
- Einsatzmodus: intern/offline-nah
- Fokus: dauerhafte Pflege und Erweiterung von FlaUI/NUnit-Tests, nicht nur Codegenerierung.

## Enthaltene Kernkomponenten

- `model.json`
- `systemprompt.md`
- `mainprompt.md`
- `fachwissen.md`
- `prompt_suggestions.md`
- `beispiele/` mit C#-Infrastruktur, Testbeispielen, Reviewbeispiel, Legacy-Eggplant-Referenzen, UIA-Dump und Track-Analyse.
- `knowledge/eggplant-zu-flaui-migrationsleitfaden-visual-track.md`

## Beispielnutzung

- bestehenden Test hochladen und analysieren lassen.
- neuen UIA3-WPF- oder UIA2-WinForms-Test erzeugen lassen.
- VisualTrack-Analyse erweitern.
- Flaky-Test mit Screenshot/UIA-Dump/TRX diagnostizieren.
- Azure-DevOps-Server-YAML gegen Zielstack prüfen.

## Importhinweis

Die `model.json` ist logisch strukturiert, aber ohne konkrete OpenWebUI-Version und ohne Referenzexport erzeugt. Prüfe Feldnamen und Importfähigkeit gegen einen echten Export deiner Zielinstanz.

## Sicherheitsnotiz

Keine Secrets, keine produktiven Änderungen ohne menschliche Freigabe, keine unreviewten KI-generierten Tests als finaler Release-Gate-Nachweis.
