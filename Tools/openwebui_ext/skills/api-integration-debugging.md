---
name: api-integration-debugging
description: Diagnose von API-, Auth-, HTTP- und OpenAPI-Problemen mit sicherem Umgang mit Tokens und Payloads.
---

# API Integration Debugging

## Arbeitsweise
- Sammle Endpoint, Methode, Statuscode, Request-ID, relevante Header und gekürzte Payloads.
- Trenne Netzwerkfehler, Authentifizierungsfehler, Rate Limits, Validierungsfehler und Serverfehler.
- Prüfe OpenAPI-Schema gegen tatsächliche Requests, ohne Secrets auszugeben.

## Statuscodes
- 400: Payload, Parameter, Schema oder Encoding prüfen.
- 401/403: Auth-Flow, Scope, Token-Ablauf und Berechtigungen prüfen.
- 404: Pfad, Tenant, Version und Basis-URL prüfen.
- 409/422: Zustandskonflikt oder fachliche Validierung prüfen.
- 429: Rate-Limit-Header, Backoff und Quoten prüfen.
- 5xx: Retry-Strategie, Provider-Status und Idempotenz prüfen.

## Sicherheit
- Tokens, Cookies, API-Keys und Signaturen redigieren.
- Keine produktiven Schreiboperationen ohne ausdrückliche Freigabe empfehlen.
- Bei unsicherer Herkunft von URLs SSRF-Risiko benennen.
