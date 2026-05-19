# Offene Punkte

## OpenWebUI-Importformat

Die erzeugten `model.json`-Dateien folgen dem lokal geprüften OpenWebUI-Exportformat. Vor dem produktiven Einsatz sollten dennoch Tool-Zuordnung, Default-Features und GUI-Verhalten einmal gegen die konkrete `openwebui:latest`-Instanz verifiziert werden.

## Fehlender Problemfall 26

`00_INDEX.md` nennt `26_bewerbungsunterlagen-optimierung.md`, die Datei ist im Verzeichnis `Problemfälle` nicht vorhanden. Es wurde kein vollständiges Modell aus dieser fehlenden Detailquelle erzeugt.

## Jupyter-Laufzeit

Das Jupyter-Tool kann statisch validiert werden. Eine echte Ausführung erfordert eine lokal konfigurierte Jupyter-Adresse, ein lokales Token und ein erlaubtes Arbeitsverzeichnis. Falls `websocket-client` in der OpenWebUI-Tool-Laufzeit fehlt, muss es intern/offline bereitgestellt werden.

## Sandbox-Grenze

Die statische Sicherheitsprüfung des Tools reduziert Risiken, ersetzt aber keine harte serverseitige Sandbox. Jupyter muss lokal isoliert, ressourcenbegrenzt und ohne unerwünschte Netzwerkpfade betrieben werden.

## Sichere Umwandlungen

Es wurden keine Problemfälle gefunden, deren Hauptzweck Phishing, Malware, Betrug, Exfiltration oder andere verbotene Inhalte sind. Sicherheitsnahe Code- und Compliance-Modelle wurden defensiv formuliert.
