# Beispielreview: FlakyCoordinateClickTest.cs

## Gesamtbewertung

Der Test ist nicht zielkonform. Er verletzt die FlaUI-Migrationsregeln, weil er Standardcontrols per x/y-Koordinate bedient und mit statischen Wartezeiten arbeitet.

## Findings

| Schwere | Stelle | Problem | Empfehlung |
|---|---|---|---|
| Hoch | `Mouse.Click(742, 513)` | Koordinatenklick für Standardcontrol | AutomationId verwenden, z. B. `Customer.SaveButton` |
| Mittel | `Thread.Sleep(5000)` | starre Wartezeit, flaky bei Last | `Retry.While...` oder `Waiter.UntilElement` verwenden |
| Mittel | Keine Artefakte | Fehler sind nicht diagnosefähig | `FailureArtifactCollector` in `catch`/`TearDown` nutzen |
| Niedrig | `Assert.Pass` | keine fachliche Assertion | konkrete UIA- oder VisualTrack-Assertion formulieren |

## Zielskizze

- UIA3Automation starten.
- Hauptfenster über `ProductMainWindow` finden.
- Button über `AutomationId` suchen und invoke.
- Ergebniszustand über fachliches Control prüfen.
- Bei Fehler Screenshot, UIA-Dump, metadata.json erzeugen.
