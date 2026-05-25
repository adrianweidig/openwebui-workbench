# Streszczanie dokumentów

## Profil produktu

- Locale: `pl`
- Modell-ID: `dokumentenzusammenfassung`
- Fallback: `de`

## Cel

Ten profil opisuje model Streszczanie dokumentów do użycia po polsku i w wielojęzycznych przepływach OpenWebUI.

## Kiedy używać

Użyj tego modelu, gdy żądanie pasuje do obszaru Streszczanie dokumentów i należy zastosować lokalne pliki wiedzy, przykłady lub narzędzia.

## Typowe wyniki

Odpowiedzi, tabele, listy kontrolne, szkice artefaktów, notatki z przeglądu i pytania są tworzone w języku wybranym przez użytkownika.

## Zachowanie językowe

Niemiecki jest językiem domyślnym projektu. Jeśli użytkownik wyraźnie używa lub wybiera inny obsługiwany język, odpowiadaj w tym języku. Przy niepewnej locale wróć do niemieckiego.

## Reguły jakości

Zachowuj identyfikatory techniczne, nazwy plików, polecenia, pola API i wartości czytelne maszynowo. Tłumacz widoczną prozę, nie tokeny krytyczne dla zgodności.

## Użycie w OpenWebUI

Ten profil jest przesyłany jako Knowledge razem z mainprompt.md, fachwissen.md, beispielergebnis.md i beispiele/.
