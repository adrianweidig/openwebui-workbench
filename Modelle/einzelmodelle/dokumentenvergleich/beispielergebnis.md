# Beispielergebnis: Dokumentenvergleich

Dieses Goldstandard-Beispiel zeigt eine direkt nutzbare Offline-Antwort des Modells `dokumentenvergleich`. Es nutzt nur sichtbare Nutzerinformationen, markiert Annahmen und vermeidet erfundene Quellen, Zahlen oder Dateiinhalte.

## Nutzeranfrage

Zwei Versionen eines Dokuments sollen mit inhaltlichen und strukturellen Unterschieden verglichen werden.

## Gute Antwort

### Kurzfazit

Ich erstelle eine erste belastbare Fassung für diesen Auftrag: Dokumentversionen, Textvarianten, Tabellen und Scans nachvollziehbar vergleichen.

Die Antwort bleibt offline nutzbar. Nicht bereitgestellte Fakten, aktuelle Versionen, Rechtsstände, Kennzahlen, Dateiinhalte oder Toolausgaben werden nicht ergänzt.

### Annahmen

- Die Sprache bleibt Deutsch.
- Der Auftrag basiert auf den vom Nutzer bereitgestellten Stichpunkten, Dateien oder Screenshots.
- Fehlende Pflichtinformationen werden als offen markiert statt erfunden.
- Falls Bilder oder Screenshots fehlen, wird nur mit Text gearbeitet und Vision nicht vorgetäuscht.

### Arbeitsprodukt

| Abschnitt | Inhalt |
|---|---|
| Ziel | Dokumentversionen, Textvarianten, Tabellen und Scans nachvollziehbar vergleichen. |
| Eingangsquellen | Nutzertext, bereitgestellte Dateien und sichtbare Bildinhalte; keine Live-Websuche |
| Zielformat | `beispielergebnis.md`; ergänzendes Few-Shot-Material in `beispiele/dokumentenvergleich-matrix-vorlage.md` |
| Kernstruktur | Kurzfazit, verwendete Quellen, Hauptteil, Risiken, offene Punkte, nächste Schritte |
| Prüflogik | Unterschiede müssen nach Relevanz, Quelle, Risiko und empfohlener Aktion sortiert sein. |
| Offline-Grenze | Aktuelle externe Fakten werden als prüfpflichtig markiert |

### Musterabschnitt für das Ergebnis

#### Verwendete Informationen

- Direkt aus der Anfrage übernommen: Zwei Versionen eines Dokuments sollen mit inhaltlichen und strukturellen Unterschieden verglichen werden.
- Sichtbare Zusatzquellen: nur berücksichtigen, wenn sie im Chat oder als Datei vorliegen.
- Nicht belegt: externe Aktualität, nicht bereitgestellte Dateien, interne Kennzahlen und fremde Systeme.

#### Ergebnisentwurf

1. Den Auftrag in das passende Zielformat überführen.
2. Belegte Inhalte und Annahmen getrennt darstellen.
3. Risiken und offene Punkte so formulieren, dass ein Mensch sie prüfen kann.
4. Mit einem konkreten nächsten Schritt schließen, der lokal ausführbar ist.

### Vision- und Screenshot-Regel

Nutze Vision für gescannte Versionen, markierte PDFs, Layoutabweichungen oder Screenshotvergleiche.

### Qualitätscheck

- Unterschiede müssen nach Relevanz, Quelle, Risiko und empfohlener Aktion sortiert sein.
- Keine erfundenen Quellen, Dateien, Kennzahlen oder Toolergebnisse.
- Keine Secrets, produktiven Tokens oder personenbezogenen Beispieldaten.
- Offline weiterverwendbar.

## Warum dieses Beispiel gut ist

- Es zeigt das gewünschte Arbeitsmuster ohne Platzhalter.
- Es trennt belegte Informationen und Annahmen.
- Es macht Offline-Grenzen explizit.
- Es verweist auf das echte Beispielartefakt.
