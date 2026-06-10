# OpenWebUI-Paket 1: Eggplant-FlaUI-Skriptmigration

## Zweck

Dieses Paket erzeugt ein Custom OpenWebUI-Aufgabenmodell, das bereitgestellte Eggplant-/SenseTalk-Skripte in den definierten FlaUI/NUnit/OpenCV/Azure-DevOps-Server-Ansatz migriert.

## Aufgabenmodell

- Anzeigename: `Eggplant-FlaUI-Skriptmigration`
- Technische ID: `eggplant-flaui-skriptmigration`
- Basismodell: `coder`
- Einsatzmodus: intern/offline-nah
- Fokus: Migration vorhandener Eggplant-Skripte zu Zielcode, Zielstruktur, Inventar und Akzeptanzkriterien.

## Enthaltene Kernkomponenten

- `model.json`
- `systemprompt.md`
- `mainprompt.md`
- `fachwissen.md`
- `prompt_suggestions.md`
- `beispiele/` mit Eggplant-Skripten, C#-Zielcode, VisualTrack-Testdaten, Pipeline-Snippet und Migrationsoutput
- `knowledge/eggplant-zu-flaui-migrationsleitfaden-visual-track.md`

## Beispiele

Die Beispiele sind so aufgebaut, dass sie offline als Referenz dienen:

- `beispiele/eggplant/*.script`: Ausgangsskripte.
- `beispiele/generated-csharp/`: Zielstruktur und C#-Dateien.
- `beispiele/test-assets/`: VisualTrack-JSON und Displayprofil.
- `beispiele/migration-output/`: Musterantwort für eine Migration.

## Importhinweis

Die `model.json` ist logisch strukturiert, aber ohne konkrete OpenWebUI-Version und ohne Referenzexport erzeugt. Prüfe Feldnamen und Importfähigkeit gegen einen echten Export deiner Zielinstanz.

## Sicherheitsnotiz

Das Paket enthält keine Secrets. Beispielpasswörter sind bewusst nicht produktiv. Generierter Migrationscode ist reviewpflichtig.
