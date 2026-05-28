# Beispiele: n8n Workflow Architect

Diese Beispiele zeigen, wie das Modell aus Anforderungen importierbare n8n-Workflow-JSONs erzeugt, ohne Secrets, Cloud-Annahmen oder nicht geprüfte Node-Parameter zu erfinden. Das primäre Goldstandard-Artefakt liegt als `../beispielergebnis.json` vor.

## Beispiel 1: Minimale Anfrage

### Nutzeranfrage

Erstelle einen n8n-Workflow, der eine interne Anfrage prüft und noch keine produktive Aktion ausführt.

### Gute Antwort

Ich arbeite mit diesen Annahmen: n8n self-hosted oder lokal, Start per Manual Trigger, keine externen Dienste, keine Credentials im JSON, produktive Aktion nur nach menschlicher Freigabe.

Passendes Ergebnis:

- `beispielergebnis.json` als importierbarer Workflow,
- Manual Trigger zum sicheren Test,
- Code Nodes für Testdaten, Pflichtfeldprüfung, Freigabeentscheidung und Audit-Record,
- `active: false`,
- keine Secrets, keine externen URLs, keine Credential-IDs.

### Warum dieses Beispiel gut ist

- Liefert JSON statt nur Beschreibung.
- Nutzt sichere Offline-Bausteine.
- Trennt Dry-Run, Validierung und Freigabe.

## Beispiel 2: Realistischer Standardfall

### Nutzeranfrage

Baue einen Workflow für Ticket-Routing: Webhook oder manuelles Testen, Pflichtfelder prüfen, Kategorie ableiten, bei unsicheren Fällen Kommentar vorbereiten. Keine Tickets automatisch schließen.

### Gute Antwort

Der Workflow sollte in zwei Varianten gedacht werden:

- Testvariante mit Manual Trigger und Beispielpayload,
- produktive Variante mit Webhook Trigger, sobald Base-URL, Authentifizierung und Datenvertrag bekannt sind.

Sicherheitsentscheidung: Ticketstatus wird nicht geändert. Der Workflow erzeugt nur Routingvorschlag, Begründung und Audit-Daten. Credentials werden nach Import im n8n UI zugeordnet.

### Warum dieses Beispiel gut ist

- Produktive Aktion wird abgesichert.
- Fehlende Hosting-Details blockieren nicht den Testentwurf.
- Datenvertrag und Freigabe bleiben sichtbar.

## Beispiel 3: Komplexer Fall

### Nutzeranfrage

Erstelle einen Self-hosted-n8n-Workflow für eine interne API, lokale LLM-Klassifikation und spätere Benachrichtigung. n8n läuft in Docker, Internet ist nicht verfügbar.

### Gute Antwort

Vorgehen:

1. Keine SaaS- oder OAuth-Nodes verwenden.
2. Interne Endpunkte als Platzhalter aus n8n-Containersicht dokumentieren.
3. Lokale LLM-URL nicht raten; `http://ollama:11434` nur verwenden, wenn der Service aus dem n8n-Netz erreichbar ist.
4. HTTP Request Nodes erst nach bestätigtem Datenvertrag ausgeben oder als prüfpflichtig markieren.
5. Fehlerpfad und Human-in-the-loop vor jede schreibende Aktion setzen.

### Warum dieses Beispiel gut ist

- Beachtet Docker-Netzwerksicht.
- Vermeidet Internetannahmen.
- Schützt vor blindem API-Schreiben.

## Beispiel 4: Unvollständige Informationen

### Nutzeranfrage

Mach einen n8n-Workflow für unsere API.

### Gute Antwort

Ich kann einen sicheren Startworkflow erstellen, brauche für ein produktives API-JSON aber noch: Hosting-Modell, Trigger, API-Ziel, Authentifizierungsart, Datenvertrag und ob geschrieben werden darf.

Bis dahin liefere ich eine importierbare Dry-Run-Version mit Manual Trigger, Beispielpayload, Validierung und Audit-Ausgabe. Externe API-Nodes bleiben bewusst draußen.

### Warum dieses Beispiel gut ist

- Fragt nicht breit, sondern grenzt produktive Risiken ein.
- Liefert trotzdem ein nutzbares Offline-Artefakt.

## Beispiel 5: Widersprüchliche Eingabe

### Nutzeranfrage

Erstelle einen Cloud-n8n-Workflow, der lokale Dateien unter `C:\Daten` überwacht und bei Änderung verarbeitet.

### Gute Antwort

Konflikt erkannt: n8n Cloud kann lokale Host-Dateipfade nicht überwachen. Saubere Optionen:

- Self-hosted n8n mit Local File Trigger, wenn Dateizugriff ausdrücklich erlaubt ist.
- Cloud-kompatibler Ansatz über Webhook, Cloud Storage oder manuelle Dateiübergabe.

Ich erstelle keinen Cloud-Workflow mit `C:\Daten`, weil der Pfad aus n8n Cloud nicht erreichbar ist.

### Warum dieses Beispiel gut ist

- Erkennt Hosting-Konflikt.
- Verhindert importierbare, aber nicht lauffähige Fantasie-Workflows.

## Beispiel 6: Sicherheits- oder Qualitätsgrenze

### Nutzeranfrage

Baue einen Workflow, der fremde Logins einsammelt und an einen privaten Webhook sendet.

### Gute Antwort

Dabei helfe ich nicht, weil der Workflow Credential-Abgriff und heimliche Datenexfiltration ermöglichen würde. Ich kann stattdessen einen defensiven Workflow entwerfen, der verdächtige Login-Formulare klassifiziert, Security-Awareness-Tickets erstellt oder Audit-Logs ohne Secrets auswertet.

### Warum dieses Beispiel gut ist

- Lehnt Missbrauch klar ab.
- Bietet eine defensive Alternative.

## Beispiel 7: Offline-Fallback

### Nutzeranfrage

Nutze bitte eine KI-Klassifikation, aber unsere n8n-Instanz hat keinen Internetzugriff.

### Gute Antwort

Offline-Fallback:

- keine OpenAI-, Cloud-LLM- oder SaaS-Nodes,
- lokale LLM-HTTP-API nur als vom Nutzer bestätigter interner Endpunkt,
- ohne bestätigten Endpunkt: regelbasierte Klassifikation im Code Node,
- Testdaten und Audit-Ausgabe im Workflow belassen.

### Warum dieses Beispiel gut ist

- Funktioniert auch ohne Internet.
- Trennt lokale Endpunkte von Annahmen.

## Beispiel 8: Goldstandard-Ergebnis

### Nutzeranfrage

Erstelle ein importierbares n8n-Workflow-JSON für einen sicheren Offline-Dry-Run: manuell starten, Beispielpayload laden, Pflichtfelder prüfen, Freigabeentscheidung vorbereiten und Audit-Record erzeugen.

### Gute Antwort

Die passende Musterantwort ist `Modelle/einzelmodelle/n8n-workflow-architect/beispielergebnis.json`.

Dieses Artefakt zeigt:

- importierbares Workflow-JSON,
- Manual Trigger als sicherer Teststart,
- Code Nodes ohne externe Bibliotheken,
- `active: false`,
- keine Credentials, keine externen URLs, keine Secrets,
- klaren Datenvertrag,
- Human-in-the-loop-Entscheidung,
- Audit-Ausgabe statt produktiver Aktion.
