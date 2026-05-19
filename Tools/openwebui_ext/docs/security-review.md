# Security Review

## Checkliste für Tools

- Quelle, Lizenz und Wartungsstand dokumentiert.
- Einzelne Python-Datei mit `Tools`-Klasse und typisierten öffentlichen Methoden.
- Keine Shell-Ausführung, keine dynamische Codeausführung, keine versteckten Netzwerkaufrufe.
- Keine unbeschränkten Dateizugriffe.
- Keine Secrets im Code, in Defaults, Tests oder Dokumentation.
- Eingabegrößen, Ausgabegrößen, Timeouts und Redirects begrenzt.
- Fehlerausgaben redigieren Tokens, Cookies, Passwörter und API-Keys.
- Externe Quellen werden bei Bedarf als Citation-Event angegeben.

## Ausschlusskriterien

- Phishing, Credential Harvesting, Malware, Exploit-Ausführung oder Sicherheitsumgehung.
- Unbeschränkte Shell-, Datei- oder Netzwerkfunktionen.
- Obfuskierter Code oder fehlende Lizenz.
- Schwere, undokumentierte Abhängigkeiten.
- Tools, die Secrets aus Umgebung, Dateien oder Browserdaten auslesen.

## Drittanbieter-Code

Vor Übernahme Drittanbieter-Code vollständig lesen, Lizenz kopieren oder verlinken, konkrete Version oder Commit festhalten und Änderungen dokumentieren. Ohne klare Lizenz oder bei riskanten Mustern nicht integrieren.

## SSRF und Netzwerk

HTTP-Tools müssen Schema, Host, DNS-Auflösung, private IP-Bereiche, Redirects und Antwortgrößen kontrollieren. Interne Ziele nur bei expliziter lokaler Freigabe zulassen.

## Logging und Secrets

Keine Tokens, Cookies, Authorization-Header oder `.env`-Werte in Modellantworten, Logs, Fehlermeldungen oder Tests ausgeben. Platzhalter wie `your-token-here` sind erlaubt, echte Werte nicht.
