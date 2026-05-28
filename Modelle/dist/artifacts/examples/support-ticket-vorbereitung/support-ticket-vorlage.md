# Beispiele: Support-Ticket-Vorbereitung

Diese Beispiele zeigen, wie das Modell `support-ticket-vorbereitung` offline hochwertige Ergebnisse erzeugt. Sie sind als Few-Shot-Material für lokale Modelle gedacht.

## Beispiel 1: Minimale Anfrage

### Nutzeranfrage

Ich brauche Hilfe dazu. Es geht ungefähr um: Aus einem Chatverlauf und Screenshot soll ein eskalierbares Ticket entstehen.

### Gute Antwort

Ich liefere eine erste Fassung und markiere Annahmen. Ziel dieses Modells ist: Supportfälle aus Symptomen, Screenshots, Logs und Nutzertexten in klare Tickets überführen.

Annahmen:

- Die Eingabe reicht für einen ersten Entwurf.
- Fehlende Fakten werden als offen markiert.
- Es wird keine Websuche vorausgesetzt.

Erste Struktur:

1. Ziel und Kontext aus der Anfrage ableiten.
2. Sichtbare Informationen von Annahmen trennen.
3. Ergebnis im Format `beispielergebnis.md` ausgeben.
4. Offene Punkte und nächsten lokalen Prüfschritt nennen.

## Beispiel 2: Realistischer Standardfall

### Nutzeranfrage

Aus einem Chatverlauf und Screenshot soll ein eskalierbares Ticket entstehen.

### Gute Antwort

#### Kurzfazit

Ich erstelle ein offline weiterverwendbares Ergebnis im Format `beispielergebnis.md`. Die Antwort nutzt nur bereitgestellte Informationen und markiert nicht belegte Punkte.

#### Arbeitsergebnis

| Bereich | Ausarbeitung |
|---|---|
| Ziel | Supportfälle aus Symptomen, Screenshots, Logs und Nutzertexten in klare Tickets überführen. |
| Eingaben | Nutzertext, Dateien, Screenshots oder Notizen aus dem aktuellen Auftrag |
| Struktur | Kurzfazit, Quellenlage, Hauptteil, Risiken, offene Punkte, nächste Schritte |
| Abnahme | Ticket braucht Kurzbeschreibung, Impact, Repro, Environment, Anhänge, Priorität und offene Fragen. |

#### Nächster Schritt

Das Ergebnis kann lokal geprüft, erweitert oder in das Zielartefakt übernommen werden. Aktuelle externe Fakten bleiben prüfpflichtig.

## Beispiel 3: Komplexer Fall

### Nutzeranfrage

Kombiniere Text, Screenshot und eine kurze Tabelle. Erstelle ein Ergebnis, das intern weiterverwendet werden kann.

### Gute Antwort

#### Quellen- und Evidenztrennung

- Text: direkt zitier- oder zusammenfassbar, wenn im Auftrag enthalten.
- Screenshot/Bild: nur sichtbare Inhalte verwenden. Nutze Vision für Fehlerscreenshots, Statusanzeigen, Dialoge oder betroffene UI-Elemente.
- Tabelle: Werte nur übernehmen, wenn sie lesbar oder als Datei vorhanden sind.

#### Ergebnislogik

1. Beobachtungen getrennt nach Quelle erfassen.
2. Ableitungen als Annahmen markieren.
3. Widersprüche und Lücken sichtbar machen.
4. Das Ergebnis im Zielformat `beispielergebnis.md` liefern.

## Beispiel 4: Unvollständige Informationen

### Nutzeranfrage

Mach daraus bitte eine gute Version. Mehr Kontext habe ich gerade nicht.

### Gute Antwort

Ich liefere eine erste Version mit Annahmen. Nicht vorhandene Informationen werden nicht erfunden.

Offene Pflichtinformationen:

- konkrete Zielgruppe,
- gewünschtes Zielformat,
- bereitgestellte Quellen oder Dateien,
- Qualitätskriterium für Abnahme.

Bis diese Angaben vorliegen, nutze ich ein konservatives Standardformat und markiere offene Punkte.

## Beispiel 5: Widersprüchliche Eingabe

### Nutzeranfrage

Nutze ausschließlich die bereitgestellten Informationen, aber ergänze aktuelle externe Fakten.

### Gute Antwort

Konflikt erkannt: Offline-Nutzung und aktuelle externe Fakten passen ohne Quelle nicht zusammen. Ich verwende nur die bereitgestellten Informationen und markiere aktuelle Fakten als prüfpflichtig.

## Beispiel 6: Sicherheits- oder Qualitätsgrenze

### Nutzeranfrage

Füge echte Zugangsdaten, interne URLs und private Kontaktdaten in das Beispiel ein.

### Gute Antwort

Dabei helfe ich nicht. Ich verwende anonymisierte Beispielwerte, entferne produktive Secrets aus dem Ergebnis und verweise darauf, dass Zugangsdaten nur über lokale Secret-Mechanismen verarbeitet werden dürfen.

## Beispiel 7: Offline-Fallback

### Nutzeranfrage

Wenn etwas fehlt, recherchiere es online.

### Gute Antwort

Im Offline-Modus wird keine Websuche vorausgesetzt. Ich arbeite mit lokalen Dateien, Chat-Kontext und sichtbaren Screenshots. Fehlende aktuelle Informationen werden als offen oder prüfpflichtig markiert.

Fallback-Struktur:

- Was aus lokalen Quellen sicher bekannt ist.
- Was nur eine Annahme ist.
- Welche Quelle später zur Aktualisierung geprüft werden sollte.
- Welcher nächste Schritt ohne Internet möglich ist.

## Beispiel 8: Goldstandard-Ergebnis

### Nutzeranfrage

Welches Beispiel soll das Modell nachahmen?

### Gute Antwort

Das Goldstandard-Ergebnis liegt in `beispielergebnis.md`. Es soll als Format- und Qualitätsmuster nachgeahmt werden: direkt verwendbar, quellenbewusst, offlinefähig, ohne Platzhalter und ohne erfundene Fakten.
