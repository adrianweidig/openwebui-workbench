from __future__ import annotations

import locale
import os
from collections.abc import Iterable


DEFAULT_LOCALE = "de"
SUPPORTED_LOCALES = ("de", "en")

MESSAGES: dict[str, dict[str, str]] = {
    "de": {
        "action_failed": "Aktion fehlgeschlagen (Exit-Code {returncode}). Details stehen in der Ausgabe.",
        "auth_required": "Authentifizierung erforderlich.",
        "content_too_large": "Dateiinhalt ist größer als {max_bytes} Bytes.",
        "dashboard_listening": "OpenWebUI Workbench Dashboard läuft auf http://{host}:{port}",
        "file_not_found": "Datei nicht gefunden.",
        "invalid_example_filename": "Ungültiger Beispiel-Dateiname.",
        "invalid_model_filename": "Ungültiger Dateiname.",
        "invalid_model_id": "Ungültige Modell-ID.",
        "invalid_resource_id": "Ungültige Ressourcen-ID.",
        "invalid_static_path": "Ungültiger Static-Pfad.",
        "json_body_object": "JSON-Body muss ein Objekt sein.",
        "model_not_found": "Modell nicht gefunden: {model_id}",
        "only_model_markdown": "Nur freigegebene Markdown-Dateien eines Modellpakets dürfen bearbeitet werden.",
        "request_too_large": "Request ist größer als {max_bytes} Bytes.",
        "resource_not_found": "Ressource nicht gefunden: {kind}/{resource_id}",
        "resource_type": "Ressourcentyp muss `tool` oder `skill` sein.",
        "route_not_found": "Route nicht gefunden.",
        "token_missing": "OPENWEBUI_ADMIN_TOKEN oder OPENWEBUI_ADMIN_TOKEN_FILE ist nicht gesetzt.",
        "unknown_action": "Unbekannte Aktion: {action}",
        "write_disabled": "Schreibzugriff ist deaktiviert.",
    },
    "en": {
        "action_failed": "Action failed (exit code {returncode}). See the output for details.",
        "auth_required": "Authentication required.",
        "content_too_large": "File content is larger than {max_bytes} bytes.",
        "dashboard_listening": "OpenWebUI Workbench dashboard listening on http://{host}:{port}",
        "file_not_found": "File not found.",
        "invalid_example_filename": "Invalid example file name.",
        "invalid_model_filename": "Invalid file name.",
        "invalid_model_id": "Invalid model ID.",
        "invalid_resource_id": "Invalid resource ID.",
        "invalid_static_path": "Invalid static path.",
        "json_body_object": "JSON body must be an object.",
        "model_not_found": "Model not found: {model_id}",
        "only_model_markdown": "Only approved Markdown files inside a model package can be edited.",
        "request_too_large": "Request is larger than {max_bytes} bytes.",
        "resource_not_found": "Resource not found: {kind}/{resource_id}",
        "resource_type": "Resource type must be `tool` or `skill`.",
        "route_not_found": "Route not found.",
        "token_missing": "OPENWEBUI_ADMIN_TOKEN or OPENWEBUI_ADMIN_TOKEN_FILE is not set.",
        "unknown_action": "Unknown action: {action}",
        "write_disabled": "Write access is disabled.",
    },
}


def normalize_locale(value: str | None) -> str:
    raw = (value or "").strip().replace("_", "-").lower()
    if not raw:
        return DEFAULT_LOCALE
    language = raw.split("-", 1)[0]
    if language in SUPPORTED_LOCALES:
        return language
    return DEFAULT_LOCALE


def _split_accept_language(value: str) -> Iterable[str]:
    for item in value.split(","):
        language = item.split(";", 1)[0].strip()
        if language:
            yield language


def detect_locale(*candidates: str | None) -> str:
    for candidate in candidates:
        if not candidate:
            continue
        for value in _split_accept_language(candidate):
            normalized = normalize_locale(value)
            if normalized != DEFAULT_LOCALE or value.lower().startswith(DEFAULT_LOCALE):
                return normalized
    for name in ("LC_ALL", "LC_MESSAGES", "LANG"):
        normalized = normalize_locale(os.environ.get(name))
        if normalized != DEFAULT_LOCALE:
            return normalized
    try:
        normalized = normalize_locale(locale.getlocale()[0])
        if normalized != DEFAULT_LOCALE:
            return normalized
    except (TypeError, ValueError):
        pass
    return DEFAULT_LOCALE


def t(key: str, locale_name: str | None = None, **params: object) -> str:
    language = normalize_locale(locale_name)
    template = MESSAGES.get(language, {}).get(key) or MESSAGES[DEFAULT_LOCALE].get(key) or key
    return template.format(**params)
