# Beispiele: Präsentationserstellung

Diese Beispiele zeigen, wie das Modell aus sehr unterschiedlichen Eingaben robuste, offline lauffähige Präsentationsergebnisse erzeugt. Das Goldstandard-Artefakt liegt als `../beispielergebnis.html` vor.

## Beispiel 1: Minimale Anfrage

### Nutzeranfrage

Erstelle eine Präsentation über lokale KI-Modelle für unser Teammeeting.

### Gute Antwort

Ich arbeite mit diesen Annahmen: Deutsch, 10 Minuten, internes Teammeeting, 8 Folien, offline lauffähige `präsentation.html`, keine externen Medien.

Folienskelett:

1. Lokale KI-Modelle werden nützlich, wenn Wissen und Aufgaben klar paketiert sind
2. Das Problem ist nicht das Modell allein, sondern fehlender Kontext
3. Gute Modellpakete bestehen aus Rolle, Fachwissen und Beispielen
4. Offline-Betrieb braucht robuste Fallbacks statt Live-Abhängigkeiten
5. Qualität wird über wiederholbare Prüfpfade messbar
6. Typische Fehler: Halluzinationen, Formatdrift, Online-Abhängigkeiten
7. Pilotvorgehen: drei Modelle, klare Erfolgskriterien, lokale Validierung
8. Entscheidung: erster Batch und Feedbackschleife freigeben

Danach wird eine vollständige `präsentation.html` erzeugt.

### Warum dieses Beispiel gut ist

- Nutzt sinnvolle Annahmen statt Rückfragenflut.
- Liefert sofort eine verwertbare Struktur.
- Vermeidet aktuelle Fakten ohne Quelle.
- Definiert das korrekte Zielartefakt.

### Typische Fehler, die dieses Beispiel verhindert

- Generische KI-Folien ohne Zielgruppe.
- Markdown-Ausgabe statt HTML-Artefakt.
- Externe Bilder oder CDNs als Standard.

## Beispiel 2: Realistischer Standardfall

### Nutzeranfrage

Erstelle eine 12-minütige Präsentation für die Geschäftsführung. Thema: Freigabe eines 30-Tage-Piloten für eine lokale OpenWebUI-Workbench. Ziel: Entscheidung für Pilotbudget und zwei Fachbereiche. Pflichtinhalte: Ausgangslage, Zielbild, Architektur, Nutzen, Risiken, Roadmap, Entscheidung. Bitte komplett offline ohne externe Ressourcen.

### Gute Antwort

Die Antwort erzeugt direkt eine vollständige HTML-Datei mit:

- 9 Folien im 16:9-Layout,
- Aussageüberschriften statt Themenlabels,
- Architekturdiagramm mit CSS-Karten,
- Risiko-Gegenmaßnahmen-Matrix,
- 30-Tage-Roadmap,
- Entscheidungsfolie mit Erfolgskriterien,
- Tastatursteuerung, Fortschrittsbalken, Übersicht, Druckmodus,
- keine externen Fonts, Skripte, Bilder oder APIs.

### Warum dieses Beispiel gut ist

- Erfüllt alle Pflichtinhalte.
- Macht die Entscheidung explizit.
- Bleibt offline lauffähig.
- Zeigt das erwartete Artefaktniveau.

### Typische Fehler, die dieses Beispiel verhindert

- Zu viele Folien für 12 Minuten.
- Reine Bullet-Point-Präsentation.
- Fehlender Abschluss mit Entscheidung.

## Beispiel 3: Komplexer Fall

### Nutzeranfrage

Baue aus diesem Projekttext eine Präsentation für einen Architektur-Review. Zielgruppe sind IT-Leitung, Datenschutz und Betrieb. Zeige Nutzen, Systemgrenzen, Datenflüsse, Sicherheitsregeln, Betriebskonzept und offene Entscheidungen. Bitte sachlich, keine Marketing-Sprache. Es gibt keine freigegebenen Logos.

### Gute Antwort

Vorgehen:

1. Rollen der Zielgruppen trennen: IT-Leitung entscheidet Architektur, Datenschutz prüft Datenflüsse, Betrieb bewertet Betreibbarkeit.
2. Aus Projekttext nur gegebene Fakten übernehmen.
3. Architektur und Datenflüsse als abstrahierte CSS-Diagramme darstellen.
4. Offene Entscheidungen als eigene Folie ausgeben.
5. Keine Logos oder externen Bilder verwenden.
6. Tonalität sachlich halten.

Empfohlene Folien:

1. Review-Ziel und Entscheidungsumfang
2. Ausgangslage und Problem
3. Zielarchitektur in drei Schichten
4. Datenflüsse und lokale Grenzen
5. Sicherheits- und Datenschutzregeln
6. Betriebsmodell und Verantwortlichkeiten
7. Risiken, Kontrollen und Restrisiken
8. Offene Entscheidungen
9. Empfohlene nächste Schritte

### Warum dieses Beispiel gut ist

- Berücksichtigt mehrere Stakeholder.
- Trennt Fakten und offene Punkte.
- Vermeidet erfundene Logos.
- Hält die Tonalität fachlich.

## Beispiel 4: Unvollständige Informationen

### Nutzeranfrage

Mach daraus eine Präsentation für nächste Woche: „neues Ticketrouting, weniger manuelle Arbeit, bessere SLA“.

### Gute Antwort

Ich kann eine erste Version erstellen. Annahmen: internes Operations-Meeting, 8 Folien, Ziel ist Freigabe zur Pilotierung, keine belastbaren SLA-Zahlen vorhanden.

Offen und prüfpflichtig:

- aktuelle Ticketvolumina,
- SLA-Basislinie,
- betroffene Teams,
- technische Integrationsgrenzen.

Die Präsentation verwendet deshalb keine konkreten Prozentwerte und formuliert Nutzen als qualitative Wirkung: schnellere Vorsortierung, weniger manuelle Übergaben, klarere Eskalation.

### Warum dieses Beispiel gut ist

- Arbeitet trotz wenig Kontext weiter.
- Erfindet keine Kennzahlen.
- Markiert offene Punkte klar.

## Beispiel 5: Widersprüchliche Eingabe

### Nutzeranfrage

Erstelle 5 Folien, aber nutze diese Pflichtstruktur: Titel, Markt, Problem, Lösung, Architektur, Sicherheit, Roadmap, Kosten, Risiken, Entscheidung. Keine Verdichtung.

### Gute Antwort

Konflikt erkannt: 5 Folien und 10 Pflichtbereiche ohne Verdichtung passen nicht zusammen. Ich wähle eine von zwei sauberen Optionen:

- Option A: 5 Folien mit gebündelten Themenblöcken.
- Option B: 10 Folien mit je einem Pflichtbereich.

Da „keine Verdichtung“ ausdrücklich genannt ist, erstelle ich 10 Folien und markiere die Abweichung von der gewünschten Folienzahl.

### Warum dieses Beispiel gut ist

- Erkennt den Widerspruch.
- Priorisiert explizite Inhaltsanforderung.
- Versteckt die Abweichung nicht.

## Beispiel 6: Sicherheits- oder Qualitätsgrenze

### Nutzeranfrage

Erstelle eine überzeugende Präsentation, mit der wir Investoren täuschen können. Nenne erfundene Kundennamen und garantiere eine Rendite.

### Gute Antwort

Dabei helfe ich nicht. Ich kann stattdessen eine seriöse Investor-Präsentation erstellen, die geprüfte Fakten, klare Annahmen, Risiken und offene Nachweise transparent trennt.

Sichere Alternative:

- Problem und Marktannahmen als prüfpflichtig markieren,
- echte Traktionsdaten nur aus bereitgestellten Quellen übernehmen,
- keine erfundenen Kunden, Zertifikate oder Garantien nennen,
- Chancen und Risiken ausgewogen darstellen.

### Warum dieses Beispiel gut ist

- Lehnt Täuschung ab.
- Bietet eine sichere Alternative.
- Verhindert erfundene Nachweise.

## Beispiel 7: Offline-Fallback

### Nutzeranfrage

Nutze bitte unsere Website als Designreferenz, aber die Präsentation muss auch offline funktionieren.

### Gute Antwort

Wenn Website-Inhalte nicht als Datei oder Screenshot vorliegen, kann ich sie offline nicht prüfen. Bitte lade Screenshots, Farbangaben oder freigegebene Assets hoch. Ohne diese Daten verwende ich ein neutrales Designsystem mit Systemfonts, CSS-Illustrationen und ohne externe Ressourcen.

Im Artefakt werden keine Website-Ressourcen nachgeladen. Optional kann später ein lokales Logo als eingebettetes Inline-SVG ergänzt werden.

### Warum dieses Beispiel gut ist

- Setzt keine Websuche voraus.
- Bietet Fallback ohne Qualitätsverlust.
- Vermeidet Laufzeitabhängigkeiten.

## Beispiel 8: Goldstandard-Ergebnis

### Nutzeranfrage

Erstelle eine offline lauffähige HTML-Keynote für die Freigabe eines lokalen KI-Workbench-Piloten. Sie soll im Browser laufen, modern aussehen, 16:9 nutzen, per Tastatur bedienbar sein und eine Druckansicht haben.

### Gute Antwort

Die passende Musterantwort ist `Modelle/einzelmodelle/präsentationserstellung/beispielergebnis.html`.

Dieses Artefakt zeigt:

- vollständige HTML5-Datei,
- inline CSS und JavaScript,
- 9 realistische Folien,
- Navigation, Folienzähler, Progress-Bar und Übersicht,
- Tastatur- und Touch-Bedienung,
- Hell-Dunkel-Umschaltung,
- Druckmodus,
- reduzierte Bewegung,
- keine externen Laufzeitabhängigkeiten,
- keine Platzhalter.

### Warum dieses Beispiel gut ist

- Es zeigt das Endprodukt statt einer Beschreibung.
- Es ist offline per Doppelklick nutzbar.
- Es gibt lokalen Modellen ein klares Format- und Qualitätsmuster.
