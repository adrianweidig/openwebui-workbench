# Offene Punkte

## OpenWebUI-Importformat

Lokal lag kein Referenzexport aus `openwebui:latest` vor. Die erzeugten `model.json`-Dateien und Import-Bundles sind daher eine dokumentierte Fallback-Struktur. Feldnamen, Tool-Aktivierung und Importmechanik muessen gegen die konkrete Zielinstanz geprueft werden.

## Fehlender Problemfall 26

`00_INDEX.md` nennt `26_bewerbungsunterlagen-optimierung.md`, die Datei ist im Verzeichnis `Problemfälle` nicht vorhanden. Es wurde kein vollstaendiges Modell aus dieser fehlenden Detailquelle erzeugt.

## Jupyter-Laufzeit

Das Jupyter-Tool kann statisch validiert werden. Eine echte Ausfuehrung erfordert eine lokal konfigurierte Jupyter-Adresse, ein lokales Token und ein erlaubtes Arbeitsverzeichnis. Falls `websocket-client` in der OpenWebUI-Tool-Laufzeit fehlt, muss es intern/offline bereitgestellt werden.

## Sandbox-Grenze

Die statische Sicherheitspruefung des Tools reduziert Risiken, ersetzt aber keine harte serverseitige Sandbox. Jupyter muss lokal isoliert, ressourcenbegrenzt und ohne unerwuenschte Netzwerkpfade betrieben werden.

## Sichere Umwandlungen

Es wurden keine Problemfaelle gefunden, deren Hauptzweck Phishing, Malware, Betrug, Exfiltration oder andere verbotene Inhalte sind. Sicherheitsnahe Code- und Compliance-Modelle wurden defensiv formuliert.
