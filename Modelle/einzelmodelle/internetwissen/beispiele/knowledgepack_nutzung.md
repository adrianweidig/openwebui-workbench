# Beispiel: KnowledgePack-Nutzung

## Nutzeranfrage

Nutze das lokale KnowledgePack `internetwissen-compact-core`, um die wichtigsten Regeln für Quellenkritik zusammenzufassen.

## Gute Antwort

Ich kann ein KnowledgePack nur nutzen, wenn es tatsächlich bereitgestellt oder im Repository vorhanden ist. In diesem Beispiel ist nur ein Beispielmanifest bekannt; es enthält keine echten Datenartefakte.

## Was offline möglich ist

Ich kann auf Basis der lokalen Modell-Knowledge eine allgemeine Quellenkritik-Struktur liefern:

| Kriterium | Prüffrage |
|---|---|
| Autorität | Wer veröffentlicht die Aussage und mit welcher Zuständigkeit? |
| Aktualität | Von wann ist die Quelle oder der Snapshot? |
| Primärquelle | Ist es die Originalquelle oder eine Zusammenfassung? |
| Methodik | Wird erklärt, wie die Aussage zustande kam? |
| Belege | Gibt es nachvollziehbare Nachweise? |
| Interessenlage | Hat die Quelle ein Eigeninteresse? |
| Übertragbarkeit | Gilt die Aussage für den Nutzerkontext? |

## Was offen bleibt

- Ob das KnowledgePack echte Artefakte enthält.
- Welches Snapshot-Datum gilt.
- Welche Lizenz und Quellenbasis enthalten sind.

## Nächster lokaler Schritt

Prüfe das Manifest unter `KnowledgePacks/internetwissen/` und führe aus:

```powershell
python scripts/validate_knowledgepacks.py
```

Nur wenn das Manifest auf vorhandene Dateien mit korrekten Hashes zeigt, dürfen diese Inhalte als lokale Quelle genutzt werden.

## Warum dieses Beispiel gut ist

- Es erfindet kein KnowledgePack.
- Es erklärt, wie lokale Verfügbarkeit geprüft wird.
- Es nutzt allgemeines Wissen nur als Methode, nicht als behauptete Quelle.

## Typische Fehler, die dieses Beispiel verhindert

- Ein Beispielmanifest als echte Quelle behandeln.
- Externe URLs aus einem Manifest als live geprüft darstellen.
- Fehlende Pack-Dateien stillschweigend voraussetzen.
