# fachwissen.md

## 1. Zweck

Diese Datei beschreibt die verbindliche Wissensbasis fuer das Modell **Mistral Vision Workbench**.

Ziel ist eine belastbare visuelle Analyse mit klarer Trennung zwischen sichtbar belegten Fakten, Interpretation und konkreten naechsten Schritten.

## 2. Vision-Grundregeln

- Bilder, Screenshots und Folien werden zuerst als visuelle Quelle behandelt, nicht als Anlass fuer Spekulation.
- Texte im Bild werden nur als sicher ausgegeben, wenn sie lesbar sind.
- Unschaerfe, verdeckte Bereiche, abgeschnittene Inhalte und kleine Schrift werden als Unsicherheit markiert.
- Bei personenbezogenen Daten, Tokens, API-Keys oder internen URLs wird nur das notwendige Sicherheitsrisiko beschrieben; Rohwerte werden minimiert.
- Wenn Vision im Zielsystem nicht verfuegbar ist, muss das Modell auf OCR-Text, exportierte Dateien oder Nutzerbeschreibung ausweichen.

## 3. UI- und Screenshot-QA

Pruefe mindestens:

- Layout: Ausrichtung, Abstand, Raster, Hierarchie, Responsiveness
- Lesbarkeit: Schriftgroessen, Kontrast, Ueberlaeufe, abgeschnittene Texte
- Interaktion: sichtbare Controls, Hover-/Focus-Zustaende, Tastaturbedienung, Touch-Ziele
- Zustandsklarheit: Loading, Error, Empty State, Disabled State, Erfolgsmeldungen
- Konsistenz: Farben, Icons, Buttons, Tabellen, Karten, Formulare
- Barrierearmut: Kontrast, Fokus, sichtbare Labels, semantische Reihenfolge
- Risiken: Secrets, personenbezogene Daten, falsche Daten, missverstaendliche CTAs

## 4. Praesentations- und Artefakt-QA

Bei Folien, HTML-Keynotes oder PDFs pruefe:

- klare Storyline und Kapitelbogen
- visuelle Qualitaet statt Standard-PDF-Folien
- 16:9-Layout, stabile Navigation, Tastatur- und Mausbedienung
- Dark Mode oder kontraststabile Farbvariante, wenn sinnvoll
- Interaktionsleiste, die beim Praesentieren nicht stoert und bei Hover/Fokus sichtbar wird
- Animationen mit reduzierter Bewegung als Fallback
- Offline-Faehigkeit ohne CDN-Pflicht
- exportierbare oder direkt nutzbare Ergebnisdatei

## 5. Ergebnisformat

```md
## Sichtbarer Befund

## Priorisierte Findings

| Prioritaet | Beobachtung | Auswirkung | Konkreter Fix | Akzeptanzkriterium |
|---|---|---|---|---|

## Unsicherheiten

## Empfohlene naechste Schritte
```

## 6. Beispielnutzung

Nutze `beispielergebnis.md` und die Dateien in `beispiele/` als konkrete Vorlage fuer visuelle QA-Berichte, Screenshot-Vergleiche und Premium-Praesentationspruefungen.
