# OpenWebUI-Modellpaket: Testprogrammierung

## Inhalt

Dieses Paket enthält ein vorkonfiguriertes OpenWebUI-Aufgabenmodell für professionelle Testprogrammierung, Testautomatisierung und CI/CD-fähige Testcode-Erstellung.

Enthaltene Dateien:

| Datei | Zweck |
|---|---|
| `model.json` | Logische OpenWebUI-Modellkonfiguration |
| `systemprompt.md` | Kompakter Systemprompt für das Aufgabenmodell |
| `mainprompt.md` | Vollständige operative Arbeitslogik |
| `fachwissen.md` | Domänenspezifische Wissensbasis |
| `README.md` | Import- und Betriebshinweise |
| `icon_prompt.md` | Optionaler Prompt für eine spätere Icon-Erzeugung |

## Annahmen

- Basismodell: `coder`.
- OpenWebUI-Version: nicht angegeben.
- Referenzexport: nicht angegeben.
- Knowledge Bases: keine konkreten OpenWebUI-Knowledge-IDs genannt.
- Tools/Skills: keine konkreten Tool-, Skill- oder internen Ressourcen-IDs genannt.
- Importfähigkeit: Die JSON-Struktur ist eine bestmögliche, klar strukturierte Best-Effort-Konfiguration und muss gegen einen realen Export der Zielinstanz geprüft werden.

## Modellzweck

Das Modell „Testprogrammierung“ unterstützt bei:

- automatisierter Testprogrammierung
- C#-Tests mit Playwright, Selenium, NUnit, xUnit und MSTest
- Ada-Tests mit AUnit, GNATtest, gprbuild und GNAT-Toolchain
- Überführung von Akzeptanzkriterien in ausführbare Testautomatisierung
- CI/CD-Ausführung, insbesondere Azure DevOps
- Testreports, Artefakten, Logs und Exit-Code-Verhalten
- Refactoring und Stabilisierung bestehender Tests

## Importhinweise

1. Prüfe zunächst einen echten Modell-Export deiner OpenWebUI-Zielinstanz.
2. Vergleiche die Feldnamen aus `model.json` mit dem Exportformat deiner Instanz.
3. Passe ggf. `base_model_id`, Parameterfelder, Capability-Felder, Builtin-Tool-Felder und Access-Control-Felder an.
4. Importiere oder hinterlege `systemprompt.md` als System Prompt des Modells.
5. Stelle `mainprompt.md` und `fachwissen.md` als Knowledge-/Kontextdateien bereit oder binde sie entsprechend deiner OpenWebUI-Struktur ein.
6. Füge reale Knowledge-Base-, Tool- oder Skill-IDs nur dann ein, wenn sie in deiner Instanz existieren.
7. Hinterlege keine API Keys, Passwörter, Tokens oder Secrets in den Dateien.

## Empfohlene Feature-Konfiguration

| Funktion | Empfehlung |
|---|---|
| File Upload | aktiv |
| File Context | aktiv |
| Code Interpreter | erlaubt und standardmäßig sinnvoll |
| Web Search | erlaubt, aber standardmäßig aus |
| Vision | erlaubt, aber standardmäßig aus |
| Image Generation | aus |
| Citations | aktiv |
| Status Updates | aktiv |

## Betriebshinweise

- Das Modell soll bei Testcode immer lokale Ausführung und CI/CD-Ausführung angeben.
- Ada- und C#-Lösungen sind getrennt zu behandeln.
- Ada ist nicht als primäre Sprache für direkte Playwright- oder Selenium-Browserautomation zu empfehlen.
- C# ist der Standardpfad, wenn Playwright, Selenium, Web-UI oder E2E ohne Sprache genannt wird.
- Azure DevOps ist der Standard für CI/CD, wenn keine andere Umgebung genannt ist.
- Aktuelle Frameworkdetails sollten bei Bedarf gegen offizielle Dokumentation geprüft werden.

## Sicherheitsgrenzen

Das Modell darf keine Anleitungen für Captcha-Umgehung, Bot-Erkennungsumgehung, Credential Harvesting, heimliches Scraping, Tests ohne Berechtigung, Malware, Phishing, Social Engineering, Manipulation realer Nutzerkonten oder destruktive Lasttests ohne Sicherheitsrahmen erzeugen.

Sichere Alternativen sind defensive QA-Validierung, Security-Awareness, autorisierte Testplanung, Compliance-Analyse und nicht-destruktive Tests in freigegebenen Umgebungen.

## Nacharbeiten in OpenWebUI

- Feldnamen der `model.json` gegen Zielinstanz prüfen.
- Reale Knowledge Bases, Tools und Skills nur mit existierenden IDs ergänzen.
- Access-Control an Organisationsrollen anpassen.
- Optional organisationsinterne CI/CD-Templates in eine OpenWebUI Knowledge Base auslagern.
