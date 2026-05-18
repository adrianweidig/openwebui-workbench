# Air-Gapped Betrieb

## Grundregeln

- Keine Websuche.
- Keine externen APIs.
- Keine externen RAGFlow-/RAG-Dienste.
- Keine Paketdownloads zur Laufzeit.
- Keine harten Zugangsdaten in Artefakten.
- Nutzerdateien, Chat-Kontext und lokale Paketdateien sind die primaeren Quellen.

## Fehlende Abhaengigkeiten

Wenn eine lokale Python-Bibliothek oder Jupyter-Komponente fehlt, muss sie vorab intern bereitgestellt werden. Die erzeugten Tools geben in diesem Fall robuste Fehlermeldungen aus und laden nichts nach.

## Jupyter

Jupyter darf nur ueber die konfigurierte interne Adresse genutzt werden. Die tatsaechliche Isolation muss serverseitig umgesetzt werden, z. B. durch Container, eigene Benutzerrechte, begrenztes Arbeitsverzeichnis, kein Internet-Routing und Ressourcenlimits.
