# OpenWebUI-Modellpaket: ISTQB-Testfallgenerator

## Zweck

Dieses Paket enthält ein OpenWebUI-Aufgabenmodell zur Erstellung professioneller, textueller Testfälle nach ISTQB-orientierter Struktur. Es basiert auf dem vom Nutzer bereitgestellten Markdown-Anhang „ISTQB-Testfallgenerator ohne Code“.

Das Modell erzeugt ausdrücklich keinen Code, keine Skripte und keine Automatisierungsimplementierungen.

## Enthaltene Dateien

| Datei | Zweck |
| --- | --- |
| `model.json` | Logische OpenWebUI-Modellkonfiguration. |
| `systemprompt.md` | Kompakter Systemprompt des Aufgabenmodells. |
| `mainprompt.md` | Vollständige operative Arbeitslogik. |
| `fachwissen.md` | Domänenspezifische Wissensbasis für ISTQB-orientierte Testfallerstellung. |
| `README.md` | Importhinweise, Annahmen und Nacharbeiten. |

## Annahmen

- Basismodell: `mistral-medium`, da kein anderes Basismodell angegeben wurde.
- OpenWebUI-Version: nicht angegeben.
- Referenzexport: nicht bereitgestellt.
- Die Datei `model.json` ist daher eine bestmögliche, strukturierte Konfiguration und muss gegen einen realen Export der Zielinstanz geprüft werden.
- Es wurden keine Tool-, Knowledge- oder Skill-IDs erfunden.
- Web Search und Image Generation sind deaktiviert.
- File Upload und File Context sind für Anforderungsdokumente und Tickets vorgesehen.
- Vision ist als Capability erlaubt, aber nicht standardmäßig aktiv, damit UI-Screenshots bei Bedarf analysiert werden können.
- Code Interpreter ist aufgrund des No-Code-Modellzwecks deaktiviert.

## Importhinweise

1. Prüfe in deiner OpenWebUI-Zielinstanz zuerst einen realen Modellexport.
2. Vergleiche Feldnamen und Struktur mit `model.json`.
3. Übernimm die Promptinhalte aus `systemprompt.md`, `mainprompt.md` und `fachwissen.md` in die dafür vorgesehenen Bereiche oder Knowledge-Dateien.
4. Falls OpenWebUI Knowledge Bases genutzt werden sollen, trage nur reale Knowledge-IDs ein.
5. Falls Tools genutzt werden sollen, trage nur reale Tool-IDs ein.
6. Hinterlege keine API Keys, Passwörter, Tokens oder internen URLs in diesen Dateien.
7. Teste das Modell mit einfachen Anforderungen, zum Beispiel Login, Passwortzurücksetzung oder Rollenberechtigung.

## Empfohlene erste Prompt Suggestions

- Erstelle ISTQB-orientierte Testfälle für diese User Story: ...
- Leite aus diesen Akzeptanzkriterien positive, negative und Grenzfalltests ab.
- Prüfe diese Anforderung auf Testbarkeit und erstelle konkrete Testfälle.
- Erstelle manuelle Testfälle für diesen Bugfix, inklusive Regressionstests.
- Formuliere Testfälle für Rollen- und Berechtigungsverhalten.
- Erzeuge eine Testfallanalyse mit Annahmen, offenen Punkten und Review-Checkliste.

## Governance

Das Modell darf keine produktiven Änderungen ausführen und keine Testautomatisierung schreiben. Sicherheitsrelevante Tests werden nur defensiv und auf Verhaltensebene formuliert.
