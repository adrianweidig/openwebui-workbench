# Offline OpenWebUI Deployment

Dieses Verzeichnis enthält lokale Vorlagen für einen offline nutzbaren OpenWebUI-Betrieb mit eigenem Jupyter-Server, persistenten Modellen, Tools, Skills und Artefakten.

## Zielbild

- OpenWebUI läuft ohne Internetzugriff.
- Ein lokaler oder intern erreichbarer Jupyter-Server übernimmt kontrollierte Python-Ausführung.
- Modelle, Tools und Skills werden aus diesem Repository importiert.
- Erzeugte HTML-, PDF-, ZIP- und Datenartefakte landen in einem persistenten Volume.
- Nutzer können im Chat Ergebnisse anfordern und erhalten klare Datei-Hinweise oder Downloads, soweit die OpenWebUI-Instanz den Datei-Event bzw. den gemounteten Pfad bereitstellt.

## Wichtige Volumes

- `E:\OpenWebUI\Modelle\dist` nach `/app/backend/data/openwebui-import`
- `E:\OpenWebUI\Tools` nach `/app/backend/data/openwebui-tools`
- `E:\OpenWebUI\Artefakte\output` nach `/app/backend/data/offline_artifacts`

## Wichtige Variablen

```text
OPENWEBUI_JUPYTER_URL
OPENWEBUI_JUPYTER_TOKEN
OPENWEBUI_JUPYTER_TIMEOUT_SECONDS
OPENWEBUI_JUPYTER_ALLOWED_WORKDIR
OPENWEBUI_ARTIFACT_ROOT
```

## PDF-Konvertierung

Für direkte PDF-Erzeugung muss im OpenWebUI-Container oder in der Tool-Laufzeit lokal ein Konverter vorhanden sein:

- bevorzugt Python-Paket `weasyprint`
- alternativ lokal installiertes `wkhtmltopdf`, nur wenn die Tool-Valve `allow_wkhtmltopdf` aktiviert wird

Ohne Konverter erzeugt das Tool weiterhin druckfertige HTML-Dateien, die manuell oder durch eine lokal bereitgestellte Pipeline in PDF umgewandelt werden können.
