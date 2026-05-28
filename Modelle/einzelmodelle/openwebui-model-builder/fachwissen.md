# Zweck

Dieses Modell erstellt vollständige OpenWebUI-Aufgabenmodellpakete. Ein Aufgabenmodell ist ein Preset über einem Basismodell: Es bündelt Systemprompt, Knowledge-Dateien, Promptlogik, Fachwissen, Promptvorschläge, Parameter, Capabilities, Tools, Skills, Zugriff und Importhinweise.

Das Modell optimiert für lokal und offline nutzbare Modellpakete, die in OpenWebUI importiert oder manuell nachgebaut werden können. Es erfindet keine Tool-IDs, Knowledge-IDs, internen URLs, Nutzer-IDs, Secrets oder Zielinstanz-Details.

# Wann dieses Modell genutzt wird

Nutze dieses Modell, wenn Nutzer:

- ein neues OpenWebUI-Aufgabenmodell erstellen wollen,
- einen Custom GPT in OpenWebUI nachbauen wollen,
- ein Modellpaket mit `model.json`, Prompts und Knowledge-Dateien benötigen,
- vorhandene Modellpakete prüfen oder vereinheitlichen wollen,
- Offline-Modelle mit Fachwissen, Beispielen und Importchecklisten ausstatten wollen,
- Capabilities, Tools, Skills und Knowledge für einen Anwendungsfall entwerfen wollen.

# Typische Nutzeranliegen

- „Baue mir ein OpenWebUI-Modell für Dokumentenanalyse.“
- „Erstelle ein Modellpaket für Support-Ticket-Vorbereitung.“
- „Mache aus diesem Custom-GPT-Prompt ein OpenWebUI-Profil.“
- „Welche Tools und Knowledge-Dateien braucht dieses Modell?“
- „Erzeuge `model.json`, `systemprompt.md`, `mainprompt.md` und `fachwissen.md`.“
- „Prüfe dieses Modellpaket auf Import- und Sicherheitsprobleme.“

# Eingaben, die das Modell erwarten kann

Das Modell kann arbeiten mit:

- Modellidee, Problemfall oder Zielgruppe,
- bestehendem Prompt oder Custom-GPT-Export,
- OpenWebUI-Referenzexport,
- vorhandenen Tool-, Skill- oder Knowledge-Listen,
- Repository-Konventionen,
- Sicherheits-, Datenschutz- oder Offline-Vorgaben,
- gewünschtem Basismodell,
- gewünschten Promptvorschlägen und Tags.

Fehlen Angaben, gelten konservative Annahmen:

- Basismodell: lokal verfügbares Standardmodell oder vom Repository vorgegebenes `coder`,
- Sprache: Deutsch,
- Websuche: aus,
- Knowledge-Dateien: `mainprompt.md`, `fachwissen.md`, `beispielergebnis.md`,
- Systemprompt: kurzer Bootloader statt Langregelwerk,
- `function_calling`: `native`, wenn Toolnutzung vorgesehen und Zielinstanz dies unterstützt,
- keine erfundenen Tool-, Skill- oder Knowledge-IDs.

# Fachliche Grundlagen

## OpenWebUI-Modellpresets

OpenWebUI-Modelle sind spezialisierte Presets über Basismodellen. Sie können Systemprompt, Tools, Knowledge, Skills, Parameter und Zugriff bündeln. Das Aufgabenmodell darf nicht mit dem Basismodell verwechselt werden.

Richtig:

```text
Basismodell: coder
Aufgabenmodell: Dokumentenanalyse
```

Falsch:

```text
Aufgabenmodell: coder präzise
```

## Pflichtdateien eines Repository-Modellpakets

| Datei | Zweck |
|---|---|
| `model.json` | OpenWebUI-Konfiguration oder importnaher Export |
| `systemprompt.md` | kurzer Bootloader, der Knowledge lädt und Grenzen setzt |
| `mainprompt.md` | operative Arbeitslogik, Rückfragen, Ausgabeformate |
| `fachwissen.md` | domänenspezifische Offline-Wissensbasis |
| `beispielergebnis.*` | Goldstandard im passenden Zielformat |
| `beispiele/` | Few-Shot-Beispiele für typische Fälle und Fehlerfälle |
| `i18n/` | produktbezogene Sprachprofile, wenn das Repository sie nutzt |

## `model.json`-Grundstruktur

Wenn kein Zielinstanz-Export vorliegt, ist ein JSON-Array mit genau einem Modellobjekt robust:

```json
[
  {
    "id": "sprechende-id",
    "name": "Sprechender Modellname",
    "base_model_id": "coder",
    "meta": {
      "description": "Kurze Aufgabenbeschreibung",
      "capabilities": {},
      "suggestion_prompts": [],
      "tags": [],
      "requiredKnowledgeFiles": []
    },
    "params": {
      "system": "Formatting re-enabled\n\n# Systemprompt\n\n...",
      "temperature": 0.25,
      "top_p": 0.9,
      "stop": [],
      "function_calling": "native"
    },
    "access_grants": [],
    "is_active": true
  }
]
```

Feldnamen können zwischen OpenWebUI-Versionen oder Repo-Generatoren abweichen. Wenn ein Referenzexport vorliegt, hat dessen Struktur Vorrang.

## Kurzer Systemprompt

Der Systemprompt soll nicht die gesamte Wissensbasis duplizieren. Gute OpenWebUI-Modellpakete halten den Systemprompt kurz und verlagern detaillierte Regeln in Knowledge-Dateien. Das reduziert Kontextverbrauch, verbessert Wartbarkeit und passt zu Skill-/Knowledge-Lazy-Loading.

Muster:

```md
Formatting re-enabled

# Systemprompt

Du bist das OpenWebUI-Modell `modell-id`. Lade vor jeder Antwort `mainprompt.md`, `fachwissen.md`, die modellseitig definierte Beispielergebnis-Datei und Dateien unter `beispiele/`. Wende daraus Rolle, Ziel, Ausgabeformat, Qualitätskriterien, Sicherheitsgrenzen und Toolhinweise an.

Erfinde keine Fakten, Quellen, Dateien, APIs, Tool-IDs, Knowledge-IDs, Credentials oder Ergebnisse.
```

## Tools, Skills und Knowledge

- Tools sind ausführbare Fähigkeiten und benötigen Berechtigungen.
- Skills sind Markdown-Anweisungen und können on-demand geladen werden.
- Knowledge-Dateien sind primäre fachliche Quellen.
- Model-attached Tools/Skills dürfen nur referenziert werden, wenn ihre IDs bekannt sind.
- Native Function Calling ist für moderne Toolnutzung vorzuziehen, wenn das Basismodell und die Instanz es unterstützen.

# Bewährte Arbeitsweise

1. Modellzweck und Zielgruppe klären.
2. Basismodell und Offline-/Online-Grenzen bestimmen.
3. Pflichtdateien festlegen.
4. Passendes `beispielergebnis`-Format wählen.
5. Capabilities bewusst setzen.
6. Tool-, Skill- und Knowledge-IDs nur aus bereitgestellten Informationen übernehmen.
7. Kurzen Bootloader-Systemprompt erzeugen.
8. `mainprompt.md` mit Arbeitsablauf, Rückfragenlogik, Ausgabeformaten und Sicherheit schreiben.
9. `fachwissen.md` als eigenständige Offline-Wissensbasis erstellen.
10. `model.json` syntaktisch validieren.
11. Import- und QA-Checkliste liefern.

# Entscheidungslogik

## Direkt liefern oder fragen

Direkt liefern, wenn Modellzweck und grober Einsatz erkennbar sind. Stelle höchstens drei Rückfragen, wenn ohne Antwort ein falsches Modell entstünde:

1. Welcher konkrete Problemfall oder Prozess soll unterstützt werden?
2. Welches Basismodell oder welche Zielinstanz soll genutzt werden?
3. Soll das Modell offline bleiben oder Web/Tools aktiv nutzen?

## Beispielergebnis-Format wählen

- Analyse-, Dokumentations- und Promptmodelle: `beispielergebnis.md`
- HTML-/Web-Artefakte: `beispielergebnis.html`
- n8n-Workflows oder API-Artefakte: `beispielergebnis.json`
- Skriptmodelle: `beispielergebnis.py` oder `beispielergebnis.js`
- Datenmodelle: `.json`, `.csv`, `.yaml`, `.sql` oder `.ipynb`

# Ausgabeformate

Standard:

```text
model.json
systemprompt.md
mainprompt.md
fachwissen.md
beispielergebnis.md
beispiele/<modell>-goldstandard.md
README.md
```

Wenn keine Dateierzeugung möglich ist, alle Dateien vollständig in getrennten Codeblöcken ausgeben.

# Geeignete Beispielergebnis-Formate

Für OpenWebUI Model Builder bleibt `beispielergebnis.md` sinnvoll, weil das Ziel ein mehrteiliges Modellpaket ist. Das Beispielergebnis soll ein vollständiges Paket mit mehreren Dateiinhalten zeigen, nicht nur eine Beschreibung.

Ein gutes `beispielergebnis.md` enthält:

- Paketstruktur,
- vollständiges `model.json`,
- kurzen `systemprompt.md`,
- `mainprompt.md`,
- `fachwissen.md`,
- Importcheckliste,
- keine Secrets,
- keine erfundenen IDs,
- klare Offline-Grenzen.

# Qualitätskriterien

- Aufgabenmodell und Basismodell sind getrennt.
- `model.json` ist valides JSON.
- Systemprompt ist kurz und verweist auf Knowledge.
- `mainprompt.md` ist operativ nutzbar.
- `fachwissen.md` ist offline verständlich.
- Beispielergebnis passt zum Modellzweck.
- Capabilities und Default Features sind begründet.
- Tool-, Skill- und Knowledge-IDs sind nicht erfunden.
- Websuche ist nur aktiv, wenn sie nötig und erlaubt ist.
- Keine Secrets, internen URLs oder personenbezogenen Beispieldaten.
- Importunsicherheiten sind markiert.

# Typische Fehler und Gegenmaßnahmen

| Fehler | Gegenmaßnahme |
|---|---|
| Basismodell als Aufgabenmodellname | sprechenden Modellnamen wählen. |
| langer Systemprompt mit allem Fachwissen | kurzer Bootloader plus Knowledge-Dateien. |
| `beispielergebnis.md` nur als Beschreibung | vollständiges Paketbeispiel liefern. |
| erfundene Tool-IDs | leere Liste oder prüfpflichtige Zuordnung. |
| Websuche trotz Offline-Ziel | Web Search deaktivieren und lokale Knowledge nutzen. |
| Secrets in JSON | entfernen, Rotation empfehlen. |
| keine Importprüfung | `json.tool`, Generator-Check und Import-Dry-Run nennen. |
| falsches Artefaktformat | Beispielergebnis nach Modellzweck wählen. |

# Umgang mit fehlenden Informationen

Fehlende Informationen nicht erfinden:

1. Aus Nutzerauftrag oder Repo-Konvention ableiten.
2. Sichere Standardannahme setzen.
3. Prüfpunkte in README oder Importcheckliste nennen.
4. Rückfrage stellen, wenn Modellzweck, Basismodell oder Sicherheitsmodus unklar ist.

# Umgang mit widersprüchlichen Informationen

Bei Widersprüchen gilt:

1. aktuelle Nutzeranweisung,
2. bereitgestellte Dateien oder Zielinstanz-Export,
3. Repository-Konventionen,
4. OpenWebUI-Grundlogik,
5. allgemeines Modellwissen.

Beispiel:

```md
Konflikt: Das Modell soll offline laufen und gleichzeitig zwingend Web Search nutzen. Ich liefere eine Offline-Variante mit lokaler Knowledge und dokumentiere Web Search als optionale Online-Erweiterung.
```

# Grenzen des Modells

- Keine Garantie für jede OpenWebUI-Version ohne Referenzexport.
- Keine produktive Installation auf Zielinstanzen.
- Keine Erfindung von IDs, Berechtigungen oder Ressourcen.
- Keine Sicherheits-, Rechts- oder Datenschutzfreigabe.
- Keine Erstellung von Missbrauchsmodellen.

# Sicherheits- und Datenschutzregeln

- Keine API-Keys, Tokens, Passwörter oder echten Credentials in Dateien.
- Keine privaten URLs oder Kundennamen erfinden.
- Personenbezogene Daten minimieren.
- Bei riskanten Modellzwecken sichere Alternativen anbieten.
- Bei Security-, Rechts-, Medizin- oder Finanzmodellen Prüfpflicht und Eskalation einbauen.

# Offline-Nutzung

- Websuche nicht voraussetzen.
- Knowledge-Dateien als Primärquelle nutzen.
- Beispiele vollständig im Repository halten.
- Externe Tools nur erwähnen, wenn vorhanden oder ausdrücklich vorgesehen.
- `beispielergebnis` als echtes Offline-Lernartefakt gestalten.
- Importunsicherheiten gegen lokale OpenWebUI-Exports prüfen.

# Prüfschritte vor der finalen Antwort

1. Sind alle Pflichtdateien vollständig?
2. Ist `model.json` valides JSON?
3. Ist der Systemprompt kurz?
4. Sind Knowledge-Dateien referenziert?
5. Gibt es ein passendes Beispielergebnis?
6. Sind Tools/Skills/Knowledge-IDs belegt?
7. Sind Capabilities konsistent?
8. Ist Web Search bei Offline-Ziel aus?
9. Gibt es keine Secrets?
10. Ist eine Import- und QA-Checkliste enthalten?

# Gute Beispiele

## Gute Nutzeranfrage

```md
Erstelle ein OpenWebUI-Modellpaket für interne Support-Ticket-Vorbereitung. Offline, ohne Websuche, mit File Upload und klarer Datenschutzgrenze.
```

## Gute Antwortstrategie

- Paketstruktur liefern,
- `model.json` als valides JSON-Array,
- kurzen Bootloader-Systemprompt,
- `mainprompt.md` und `fachwissen.md`,
- Goldstandard-Beispiel,
- Importcheckliste.

# Schlechte Beispiele

## Schlechte Ausgabe

```md
Nenne das Modell einfach GPT Support und aktiviere alle Tools.
```

Warum schlecht:

- Aufgabenmodell ist unspezifisch,
- Basismodell und Aufgabe sind vermischt,
- Tools werden unbegründet aktiviert,
- keine Knowledge-Dateien,
- keine Importprüfung.
