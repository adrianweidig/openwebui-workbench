# Analyse-Checkliste für FlaUI-Testdateien

## Zielstack

- [ ] NUnit statt xUnit/MSTest
- [ ] `Assert.That`
- [ ] UIA3 für WPF
- [ ] UIA2 für WinForms
- [ ] OpenCvSharp für VisualTrack
- [ ] keine ImageSharp-Abhängigkeit

## Stabilität

- [ ] keine Koordinatenklicks für Standardcontrols
- [ ] keine statischen Sleeps als Hauptwartebedingung
- [ ] robuste Waiter mit Fehlermeldung
- [ ] Testdaten deterministisch
- [ ] Desktop-DPI/Auflösung geprüft

## Diagnose

- [ ] Screenshot bei Fehler
- [ ] UIA-Dump bei Fehler
- [ ] metadata.json
- [ ] Logs
- [ ] VisualTrack: Masken, Overlay, `track-analysis.json`
