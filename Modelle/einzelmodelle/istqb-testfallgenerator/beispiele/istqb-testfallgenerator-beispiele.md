# ChatGPT Pro Reference Examples for `ISTQB-Testfallgenerator`

These examples are designed as high-quality few-shot references for the OpenWebUI custom model package `ISTQB-Testfallgenerator`.

- The **comments are intentionally written in English**, as requested.
- The **ideal assistant responses are written in German**, because the model package defines German as the default output language unless the user requests another language.
- The examples intentionally follow the package rules: Markdown output, clear separation of facts/assumptions/open points, at least five test cases where feasible, no code, no scripts, no automation implementation, and defensive-only treatment of security topics.
- Recommended usage: add this file as a supplemental Knowledge document or as a prompt appendix. Avoid adding a non-standard `examples` field to `model.json` unless your OpenWebUI target instance explicitly supports it.

## Coverage Matrix

| Example | Main coverage | Special behavior trained |
| --- | --- | --- |
| EX-001 | User story, address change, validation, boundary values | Full standard output with positive, negative, boundary, data consistency and usability-oriented acceptance tests |
| EX-002 | Password reset | Privacy-preserving responses, Pflichtfeldtest, validation, defensive security behavior |
| EX-003 | Shopping cart discount rules | Business rules, minimum order boundary, exclusivity, expired/reused code behavior |
| EX-004 | Role-based approval workflow | Roles, permissions, state transitions, four-eyes principle, auditability without inventing implementation details |
| EX-005 | Bugfix and regression | Reproduction-oriented bugfix testing plus regression scope |
| EX-006 | Natural-language interface behavior | Interface-level tests without code, payloads, scripts or implementation details |
| EX-007 | Unclear requirement | Correct use of maximum three clarification questions instead of speculative test cases |
| EX-008 | User asks for automation code | No-code refusal pattern plus useful manual test case alternative |
| EX-009 | Security-sensitive request | Defensive security test cases only, no bypass or attack instructions |

---

## EX-001 — User story with validation, boundary values and data consistency

### English design comment

This example trains the model to handle a well-formed user story with acceptance criteria. It demonstrates the complete standard output structure, explicit assumptions, clear traceability to acceptance criteria, positive and negative scenarios, boundary values for field lengths, data consistency after saving, and observable expected results. The example avoids inventing implementation details such as database schemas or specific APIs.

### User prompt

Erstelle ISTQB-orientierte Testfälle für diese User Story:

Als registrierter Kunde möchte ich meine Rechnungsadresse im Kundenkonto ändern können, damit zukünftige Rechnungen an die korrekte Adresse gesendet werden.

Akzeptanzkriterien:
1. Der Kunde kann Straße, Hausnummer, Postleitzahl, Ort und Land bearbeiten.
2. Straße, Hausnummer, Postleitzahl, Ort und Land sind Pflichtfelder.
3. Die Postleitzahl muss für Deutschland genau fünf Ziffern enthalten.
4. Nach erfolgreichem Speichern wird eine Bestätigung angezeigt.
5. Die geänderte Adresse wird beim erneuten Öffnen des Kundenkontos angezeigt.

### Ideal assistant response

# Testfallanalyse

## Kurzverständnis

Getestet wird die Änderung der Rechnungsadresse durch einen registrierten Kunden im Kundenkonto. Die Funktion umfasst die Bearbeitung mehrerer Pflichtfelder, eine länderspezifische Validierung der deutschen Postleitzahl, eine sichtbare Speicherbestätigung und die persistente Anzeige der geänderten Adresse beim erneuten Öffnen. Der Fokus liegt auf fachlicher Korrektheit, Validierung, Datenkonsistenz und beobachtbarem UI-Verhalten.

## Annahmen

- Der Kunde ist bereits registriert und kann sich erfolgreich im Kundenkonto anmelden.
- Die Rechnungsadresse ist im Kundenkonto über einen bearbeitbaren Bereich erreichbar.
- Für Deutschland gilt ausschließlich die im Akzeptanzkriterium genannte Regel „genau fünf Ziffern“.
- Für andere Länder sind keine konkreten Postleitzahlregeln beschrieben; diese werden daher nicht vertieft getestet.

## Offene Punkte

- Es ist nicht beschrieben, ob Sonderzeichen in Straße oder Ort erlaubt sind.
- Es ist nicht beschrieben, ob eine maximale Feldlänge existiert.
- Es ist nicht beschrieben, ob die Änderung Auswirkungen auf bereits erzeugte Rechnungen hat.

## Abgeleitete Akzeptanzkriterien

| ID | Bedingung | Erwartbares Ergebnis | Prüfbarkeit |
| --- | --- | --- | --- |
| AK-001 | Ein registrierter Kunde bearbeitet Straße, Hausnummer, Postleitzahl, Ort und Land. | Alle genannten Felder sind bearbeitbar. | Durch Öffnen und Ändern der Adressfelder prüfbar. |
| AK-002 | Ein Pflichtfeld wird leer gelassen. | Das Speichern wird verhindert und ein verständlicher Pflichtfeldhinweis wird angezeigt. | Durch Leeren einzelner Pflichtfelder prüfbar. |
| AK-003 | Für Land Deutschland wird eine Postleitzahl mit genau fünf Ziffern eingegeben. | Die Postleitzahl wird akzeptiert. | Durch Speichern mit gültiger deutscher Postleitzahl prüfbar. |
| AK-004 | Für Land Deutschland wird eine Postleitzahl mit weniger, mehr oder nicht nur numerischen Zeichen eingegeben. | Die Postleitzahl wird abgelehnt und eine verständliche Validierungsmeldung wird angezeigt. | Durch Eingabe ungültiger Postleitzahlen prüfbar. |
| AK-005 | Die Adresse wird erfolgreich gespeichert. | Eine Bestätigung wird angezeigt. | Durch Speichern gültiger Adressdaten prüfbar. |
| AK-006 | Das Kundenkonto wird nach erfolgreicher Änderung erneut geöffnet. | Die geänderte Rechnungsadresse wird vollständig angezeigt. | Durch erneutes Öffnen des Kundenkontos prüfbar. |

## Testfalldeckung

Abgedeckt werden Positivtest, Pflichtfeldtest, Validierungstest, Grenzwerttest, Datenkonsistenztest und ein usability-orientierter Abnahmetest zur Verständlichkeit der Rückmeldungen.

## Testfälle

| Testfall-ID | Titel | Ziel | Testart | Priorität | Vorbedingungen | Testdaten | Schritte | Erwartetes Ergebnis | Nachbedingungen |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TF-001 | Rechnungsadresse erfolgreich ändern | Prüfen, ob ein registrierter Kunde eine vollständige gültige Rechnungsadresse speichern kann. | Positivtest | Hoch | Ein aktives Kundenkonto ist vorhanden und der Kunde ist angemeldet. | Straße „Musterstraße“, Hausnummer „12“, Postleitzahl „10115“, Ort „Berlin“, Land „Deutschland“. | 1. Kundenkonto öffnen. 2. Bereich Rechnungsadresse öffnen. 3. Bearbeitung starten. 4. Alle Adressfelder mit gültigen Daten füllen. 5. Änderung speichern. | Die Adresse wird gespeichert und eine sichtbare Bestätigung wird angezeigt. | Die neue Rechnungsadresse ist im Kundenkonto hinterlegt. |
| TF-002 | Bearbeitbarkeit aller geforderten Felder prüfen | Prüfen, ob alle im Akzeptanzkriterium genannten Felder bearbeitbar sind. | Funktionaler Test | Hoch | Der Kunde ist angemeldet und befindet sich im Bereich Rechnungsadresse. | Neue Werte für Straße, Hausnummer, Postleitzahl, Ort und Land. | 1. Bearbeitungsmodus öffnen. 2. Jedes der fünf Felder nacheinander ändern. 3. Änderungen speichern. | Alle fünf Felder können geändert werden und die gespeicherten Werte entsprechen den eingegebenen Werten. | Die geänderten Werte sind sichtbar gespeichert. |
| TF-003 | Pflichtfeld Straße leer lassen | Prüfen, ob das System eine leere Straße ablehnt. | Pflichtfeldtest | Hoch | Der Kunde ist im Bearbeitungsmodus der Rechnungsadresse. | Leere Straße; gültige Werte für Hausnummer, Postleitzahl, Ort und Land. | 1. Feld Straße leeren. 2. Alle anderen Pflichtfelder gültig befüllen. 3. Speichern auslösen. | Das Speichern wird verhindert und ein verständlicher Hinweis zum Pflichtfeld Straße wird angezeigt. | Die bisher gespeicherte Adresse bleibt unverändert. |
| TF-004 | Pflichtfeld Land leer lassen | Prüfen, ob das System ein fehlendes Land ablehnt. | Pflichtfeldtest | Hoch | Der Kunde ist im Bearbeitungsmodus der Rechnungsadresse. | Gültige Werte für Straße, Hausnummer, Postleitzahl und Ort; kein Land ausgewählt. | 1. Feld Land leeren oder Auswahl entfernen. 2. Speichern auslösen. | Das Speichern wird verhindert und ein verständlicher Hinweis zum Pflichtfeld Land wird angezeigt. | Die bisher gespeicherte Adresse bleibt unverändert. |
| TF-005 | Deutsche Postleitzahl mit vier Ziffern ablehnen | Prüfen, ob eine zu kurze deutsche Postleitzahl abgelehnt wird. | Grenzwerttest | Hoch | Land ist auf Deutschland gesetzt. | Postleitzahl „1011“ mit sonst gültiger Adresse. | 1. Rechnungsadresse bearbeiten. 2. Land Deutschland auswählen. 3. Postleitzahl mit vier Ziffern eingeben. 4. Speichern auslösen. | Das Speichern wird verhindert und eine verständliche Meldung zur erforderlichen fünfstelligen Postleitzahl wird angezeigt. | Es wird keine ungültige Adresse gespeichert. |
| TF-006 | Deutsche Postleitzahl mit sechs Ziffern ablehnen | Prüfen, ob eine zu lange deutsche Postleitzahl abgelehnt wird. | Grenzwerttest | Hoch | Land ist auf Deutschland gesetzt. | Postleitzahl „101150“ mit sonst gültiger Adresse. | 1. Rechnungsadresse bearbeiten. 2. Land Deutschland auswählen. 3. Postleitzahl mit sechs Ziffern eingeben. 4. Speichern auslösen. | Das Speichern wird verhindert und eine verständliche Meldung zur erforderlichen fünfstelligen Postleitzahl wird angezeigt. | Es wird keine ungültige Adresse gespeichert. |
| TF-007 | Deutsche Postleitzahl mit Buchstaben ablehnen | Prüfen, ob eine nicht rein numerische deutsche Postleitzahl abgelehnt wird. | Validierungstest | Hoch | Land ist auf Deutschland gesetzt. | Postleitzahl „10A15“ mit sonst gültiger Adresse. | 1. Rechnungsadresse bearbeiten. 2. Land Deutschland auswählen. 3. Postleitzahl mit Buchstaben eingeben. 4. Speichern auslösen. | Das Speichern wird verhindert und eine verständliche Validierungsmeldung wird angezeigt. | Es wird keine ungültige Adresse gespeichert. |
| TF-008 | Geänderte Adresse nach erneutem Öffnen anzeigen | Prüfen, ob die gespeicherte Änderung dauerhaft sichtbar bleibt. | Datenkonsistenztest | Hoch | Eine gültige Rechnungsadresse wurde erfolgreich gespeichert. | Dieselben gültigen Adressdaten aus TF-001. | 1. Kundenkonto verlassen. 2. Kundenkonto erneut öffnen. 3. Bereich Rechnungsadresse aufrufen. | Die zuvor gespeicherte Rechnungsadresse wird vollständig und unverändert angezeigt. | Die gespeicherte Rechnungsadresse bleibt verfügbar. |
| TF-009 | Verständlichkeit der Speicherbestätigung prüfen | Prüfen, ob die Bestätigung nach erfolgreichem Speichern fachlich verständlich ist. | Usability-orientierter Abnahmetest | Mittel | Der Kunde speichert eine gültige Rechnungsadresse. | Vollständige gültige Rechnungsadresse. | 1. Rechnungsadresse ändern. 2. Änderung speichern. 3. Bestätigung betrachten. | Die Bestätigung ist sichtbar, eindeutig dem Speichern der Rechnungsadresse zuordenbar und signalisiert erfolgreichen Abschluss. | Der Kunde kann den erfolgreichen Vorgang nachvollziehen. |

## Review-Checkliste

- Sind alle fünf Pflichtfelder einzeln oder gruppiert ausreichend geprüft?
- Ist die deutsche Postleitzahlregel mit gültigen und ungültigen Werten abgedeckt?
- Sind Speichern, Bestätigung und erneute Anzeige geprüft?
- Sind Annahmen zu nicht beschriebenen Länderregeln transparent?
- Sind erwartete Ergebnisse ohne technische Implementierungsdetails beobachtbar?
- Wurde vollständig auf Code und Automatisierung verzichtet?

---

## EX-002 — Password reset with privacy-preserving behavior

### English design comment

This example trains privacy-conscious and defensive behavior. It shows how to test password reset without exposing whether an email address exists, without sending real emails in the answer, and without creating security-sensitive instructions. It also covers validation, missing input, repeated requests, message clarity and open points where the requirement is incomplete.

### User prompt

Leite aus dieser Anforderung manuelle Testfälle ab:

Nutzer sollen über „Passwort vergessen“ eine E-Mail zum Zurücksetzen des Passworts anfordern können. Nach Eingabe einer E-Mail-Adresse soll aus Sicherheitsgründen immer dieselbe neutrale Bestätigung angezeigt werden, unabhängig davon, ob die E-Mail-Adresse registriert ist. Das Feld E-Mail-Adresse ist Pflichtfeld und muss ein gültiges E-Mail-Format haben.

### Ideal assistant response

# Testfallanalyse

## Kurzverständnis

Getestet wird die Funktion „Passwort vergessen“ zur Anforderung einer Passwort-zurücksetzen-Nachricht. Die Funktion muss das Pflichtfeld E-Mail-Adresse validieren und nach fachlich gültiger Eingabe eine neutrale Bestätigung anzeigen, ohne offenzulegen, ob die E-Mail-Adresse registriert ist. Der Schwerpunkt liegt auf Validierung, Datenschutz, sicherem Antwortverhalten und verständlicher Nutzerführung.

## Annahmen

- Die Funktion ist über eine sichtbare Option „Passwort vergessen“ auf oder nahe der Anmeldeseite erreichbar.
- Eine registrierte E-Mail-Adresse ist im Testsystem vorhanden.
- Eine nicht registrierte E-Mail-Adresse ist im Testsystem bekannt und darf für Tests verwendet werden.
- Ob tatsächlich eine Nachricht zugestellt wird, kann durch ein geeignetes Testpostfach oder ein fachliches Prüfprotokoll kontrolliert werden, ohne echte personenbezogene Daten zu verwenden.

## Offene Punkte

- Es ist nicht beschrieben, ob wiederholte Anforderungen zeitlich begrenzt werden sollen.
- Der genaue Text der neutralen Bestätigung ist nicht vorgegeben.
- Es ist nicht beschrieben, wie lange ein Link zum Zurücksetzen gültig sein soll.

## Abgeleitete Akzeptanzkriterien

| ID | Bedingung | Erwartbares Ergebnis | Prüfbarkeit |
| --- | --- | --- | --- |
| AK-001 | Ein Nutzer öffnet die Funktion „Passwort vergessen“. | Die Funktion ist erreichbar und zeigt ein E-Mail-Eingabefeld. | Durch Navigation zur Funktion prüfbar. |
| AK-002 | Ein Nutzer sendet eine registrierte E-Mail-Adresse in gültigem Format ab. | Eine neutrale Bestätigung wird angezeigt. | Durch Absenden einer registrierten Testadresse prüfbar. |
| AK-003 | Ein Nutzer sendet eine nicht registrierte E-Mail-Adresse in gültigem Format ab. | Dieselbe neutrale Bestätigung wird angezeigt. | Durch Absenden einer nicht registrierten Testadresse prüfbar. |
| AK-004 | Das Pflichtfeld E-Mail-Adresse bleibt leer. | Die Anforderung wird verhindert und ein Pflichtfeldhinweis wird angezeigt. | Durch Absenden ohne Eingabe prüfbar. |
| AK-005 | Die E-Mail-Adresse hat ein ungültiges Format. | Die Anforderung wird verhindert und ein Formatfehler wird angezeigt. | Durch Eingabe fachlich ungültiger E-Mail-Formate prüfbar. |
| AK-006 | Registrierte und nicht registrierte E-Mail-Adressen werden fachlich verglichen. | Das System verrät nicht, ob eine Adresse registriert ist. | Durch Vergleich der sichtbaren Rückmeldungen prüfbar. |

## Testfalldeckung

Abgedeckt werden Positivtest, Negativtest, Pflichtfeldtest, Validierungstest, sicherheitsrelevanter Funktionstest auf Verhaltensebene und Usability-orientierter Abnahmetest.

## Testfälle

| Testfall-ID | Titel | Ziel | Testart | Priorität | Vorbedingungen | Testdaten | Schritte | Erwartetes Ergebnis | Nachbedingungen |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TF-001 | Passwort-zurücksetzen-Funktion öffnen | Prüfen, ob die Funktion für Nutzer erreichbar ist. | Funktionaler Test | Hoch | Die Anmeldeseite oder ein geeigneter Einstiegspunkt ist geöffnet. | Keine besonderen Testdaten erforderlich. | 1. Einstiegspunkt öffnen. 2. Option „Passwort vergessen“ auswählen. | Die Funktion wird geöffnet und ein Eingabefeld für die E-Mail-Adresse wird angezeigt. | Der Nutzer befindet sich auf der Passwort-zurücksetzen-Anforderung. |
| TF-002 | Anforderung mit registrierter E-Mail-Adresse | Prüfen, ob eine registrierte Adresse akzeptiert wird. | Positivtest | Hoch | Eine registrierte Testadresse ist vorhanden. | Registrierte E-Mail-Adresse in gültigem Format. | 1. Funktion öffnen. 2. Registrierte E-Mail-Adresse eingeben. 3. Anforderung absenden. | Eine neutrale Bestätigung wird angezeigt, die nicht unnötig verrät, dass die Adresse registriert ist. | Die Anforderung wurde fachlich entgegengenommen. |
| TF-003 | Anforderung mit nicht registrierter E-Mail-Adresse | Prüfen, ob eine nicht registrierte Adresse neutral behandelt wird. | Sicherheitsrelevanter Funktionstest | Hoch | Eine nicht registrierte Testadresse ist bekannt. | Nicht registrierte E-Mail-Adresse in gültigem Format. | 1. Funktion öffnen. 2. Nicht registrierte E-Mail-Adresse eingeben. 3. Anforderung absenden. | Dieselbe neutrale Bestätigung wie bei registrierter Adresse wird angezeigt. | Es wird keine Registrierung der Adresse offengelegt. |
| TF-004 | Sichtbare Rückmeldung für registrierte und nicht registrierte Adresse vergleichen | Prüfen, ob kein Unterschied in der sichtbaren Bestätigung erkennbar ist. | Datenschutzorientierter Negativtest | Hoch | TF-002 und TF-003 können ausgeführt werden. | Eine registrierte und eine nicht registrierte gültige E-Mail-Adresse. | 1. Anforderung mit registrierter Adresse absenden. 2. Rückmeldung dokumentieren. 3. Anforderung mit nicht registrierter Adresse absenden. 4. Rückmeldung vergleichen. | Die sichtbaren Bestätigungen sind fachlich gleich und erlauben keine Ableitung des Registrierungsstatus. | Das Antwortverhalten bleibt neutral. |
| TF-005 | Leeres E-Mail-Feld absenden | Prüfen, ob das Pflichtfeld validiert wird. | Pflichtfeldtest | Hoch | Die Funktion ist geöffnet. | Leeres E-Mail-Feld. | 1. E-Mail-Feld leer lassen. 2. Anforderung absenden. | Die Anforderung wird verhindert und ein verständlicher Pflichtfeldhinweis wird angezeigt. | Es wird keine Zurücksetzen-Anforderung angenommen. |
| TF-006 | Ungültiges E-Mail-Format ablehnen | Prüfen, ob ein ungültiges Format abgelehnt wird. | Validierungstest | Hoch | Die Funktion ist geöffnet. | Fachlich ungültige E-Mail-Adresse, zum Beispiel ohne Domänenanteil. | 1. Ungültige E-Mail-Adresse eingeben. 2. Anforderung absenden. | Die Anforderung wird verhindert und eine verständliche Formatmeldung wird angezeigt. | Es wird keine Zurücksetzen-Anforderung angenommen. |
| TF-007 | Mehrfache Anforderung für dieselbe Adresse beobachten | Prüfen, ob wiederholte Anforderungen fachlich kontrolliert und ohne Datenpreisgabe behandelt werden. | Regressionstest | Mittel | Eine gültige Testadresse ist vorhanden. | Dieselbe gültige E-Mail-Adresse mehrfach. | 1. Funktion öffnen. 2. Gültige E-Mail-Adresse absenden. 3. Vorgang mit derselben Adresse erneut durchführen. | Das System zeigt weiterhin eine neutrale Rückmeldung. Falls Begrenzungen existieren, werden sie verständlich und ohne Offenlegung des Registrierungsstatus angezeigt. | Das System bleibt in einem kontrollierten Zustand. |
| TF-008 | Verständlichkeit der neutralen Bestätigung prüfen | Prüfen, ob die Rückmeldung für Nutzer verständlich und datenschutzschonend ist. | Usability-orientierter Abnahmetest | Mittel | Eine gültige E-Mail-Adresse wurde abgesendet. | Registrierte oder nicht registrierte gültige E-Mail-Adresse. | 1. Anforderung absenden. 2. Bestätigung lesen. | Die Bestätigung erklärt den nächsten fachlichen Schritt neutral, ohne den Registrierungsstatus offenzulegen. | Der Nutzer erhält eine nachvollziehbare Rückmeldung. |

## Review-Checkliste

- Wird der Registrierungsstatus einer E-Mail-Adresse nicht offengelegt?
- Sind registrierte und nicht registrierte Adressen vergleichend geprüft?
- Sind Pflichtfeld- und Formatvalidierung abgedeckt?
- Sind wiederholte Anforderungen als offener oder angenommener Punkt transparent behandelt?
- Sind Testdaten anonymisiert und fachlich neutral formuliert?
- Wurde vollständig auf technische Angriffs- oder Automatisierungsdetails verzichtet?

---

## EX-003 — Shopping cart discount with business rules and boundaries

### English design comment

This example trains business-rule extraction from a compact requirement. It demonstrates positive and negative tests for discounts, boundary testing around the minimum order value, expired codes, reuse rules and exclusivity rules. It also shows how to avoid assuming hidden calculation rules beyond what the user stated.

### User prompt

Erstelle Testfälle für folgende Warenkorb-Regel:

Im Warenkorb kann genau ein Rabattcode eingelöst werden. Der Code „WELCOME10“ gewährt 10 Prozent Rabatt, wenn der Warenwert mindestens 50,00 Euro beträgt. Der Code darf pro Kundenkonto nur einmal verwendet werden. Abgelaufene oder unbekannte Codes dürfen nicht angewendet werden. Wenn sich der Warenwert nach Anwendung des Codes unter 50,00 Euro verringert, muss der Rabatt wieder entfernt werden und ein Hinweis angezeigt werden.

### Ideal assistant response

# Testfallanalyse

## Kurzverständnis

Getestet wird die fachliche Einlösung eines Rabattcodes im Warenkorb. Die Regel umfasst Mindestwarenwert, einmalige Nutzung pro Kundenkonto, Ablehnung unbekannter oder abgelaufener Codes, Beschränkung auf genau einen Rabattcode und automatische Entfernung des Rabatts bei späterer Unterschreitung des Mindestwarenwerts. Der Fokus liegt auf Geschäftsregeln, Grenzwerten, negativen Szenarien und Datenkonsistenz im Warenkorb.

## Annahmen

- Der Warenwert bezieht sich auf den rabattfähigen Warenkorbwert vor Anwendung des Rabattcodes.
- Versandkosten, Steuern und Rundungsregeln sind nicht beschrieben und werden nicht vertieft bewertet.
- Ein Testkundenkonto kann als „Code noch nicht verwendet“ und ein anderes als „Code bereits verwendet“ vorbereitet werden.
- Ein abgelaufener Rabattcode ist im Testsystem fachlich als abgelaufen hinterlegt.

## Offene Punkte

- Es ist nicht beschrieben, ob der Rabatt auf einzelne Artikel oder den gesamten rabattfähigen Warenwert angewendet wird.
- Rundungsregeln für Rabattbeträge sind nicht beschrieben.
- Es ist nicht beschrieben, welche Nachricht bei unbekanntem, abgelaufenem oder bereits verwendetem Code exakt erscheinen soll.

## Abgeleitete Akzeptanzkriterien

| ID | Bedingung | Erwartbares Ergebnis | Prüfbarkeit |
| --- | --- | --- | --- |
| AK-001 | Ein Kunde löst „WELCOME10“ bei einem Warenwert von mindestens 50,00 Euro erstmalig ein. | Der Rabatt wird angewendet. | Durch Einlösung mit passendem Warenkorb prüfbar. |
| AK-002 | Der Warenwert liegt unter 50,00 Euro. | Der Rabatt wird nicht angewendet. | Durch Einlösung unter Mindestwert prüfbar. |
| AK-003 | Der Warenwert liegt exakt bei 50,00 Euro. | Der Rabatt wird angewendet. | Durch Grenzwerttest prüfbar. |
| AK-004 | Der Code wurde für das Kundenkonto bereits verwendet. | Der Code wird abgelehnt. | Durch erneute Einlösung mit demselben Konto prüfbar. |
| AK-005 | Ein unbekannter oder abgelaufener Code wird eingegeben. | Der Code wird nicht angewendet und ein Hinweis wird angezeigt. | Durch Eingabe entsprechender Codes prüfbar. |
| AK-006 | Ein zweiter Rabattcode wird zusätzlich eingegeben. | Es wird nicht mehr als ein Rabattcode gleichzeitig angewendet. | Durch Versuch einer zweiten Einlösung prüfbar. |
| AK-007 | Der Warenwert fällt nach Anwendung unter 50,00 Euro. | Der Rabatt wird entfernt und ein Hinweis wird angezeigt. | Durch Warenkorbänderung nach Anwendung prüfbar. |

## Testfalldeckung

Abgedeckt werden Positivtest, Negativtest, Grenzwerttest, Geschäftsregeltest, Zustandswechseltest, Datenkonsistenztest und Fehlermeldungstest.

## Testfälle

| Testfall-ID | Titel | Ziel | Testart | Priorität | Vorbedingungen | Testdaten | Schritte | Erwartetes Ergebnis | Nachbedingungen |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TF-001 | Gültigen Rabattcode bei Warenwert über Mindestwert anwenden | Prüfen, ob „WELCOME10“ korrekt angewendet wird. | Positivtest | Hoch | Kunde ist angemeldet; Code wurde für das Konto noch nicht verwendet. | Warenkorbwert 60,00 Euro; Rabattcode „WELCOME10“. | 1. Warenkorb mit Wert 60,00 Euro öffnen. 2. Rabattcode „WELCOME10“ eingeben. 3. Code anwenden. | Der Rabatt wird angewendet und der Warenkorb zeigt eine nachvollziehbare Rabattposition. | Im Warenkorb ist genau ein Rabattcode aktiv. |
| TF-002 | Rabattcode bei exakt 50,00 Euro anwenden | Prüfen, ob der Mindestwert inklusive Grenze akzeptiert wird. | Grenzwerttest | Hoch | Kunde ist angemeldet; Code wurde noch nicht verwendet. | Warenkorbwert exakt 50,00 Euro; Rabattcode „WELCOME10“. | 1. Warenkorb mit exakt 50,00 Euro öffnen. 2. Code eingeben. 3. Code anwenden. | Der Rabatt wird angewendet, da der Mindestwarenwert erreicht ist. | Rabatt ist im Warenkorb aktiv. |
| TF-003 | Rabattcode bei 49,99 Euro ablehnen | Prüfen, ob ein Wert knapp unter der Grenze abgelehnt wird. | Grenzwerttest | Hoch | Kunde ist angemeldet; Code wurde noch nicht verwendet. | Warenkorbwert 49,99 Euro; Rabattcode „WELCOME10“. | 1. Warenkorb mit 49,99 Euro öffnen. 2. Code eingeben. 3. Code anwenden. | Der Rabatt wird nicht angewendet und ein verständlicher Hinweis zum Mindestwarenwert wird angezeigt. | Es ist kein Rabattcode aktiv. |
| TF-004 | Unbekannten Rabattcode ablehnen | Prüfen, ob ein nicht bekannter Code nicht angewendet wird. | Negativtest | Hoch | Kunde ist angemeldet. | Warenkorbwert mindestens 50,00 Euro; unbekannter Rabattcode. | 1. Warenkorb öffnen. 2. Unbekannten Code eingeben. 3. Code anwenden. | Der Code wird abgelehnt und ein verständlicher Hinweis wird angezeigt. | Der Warenkorb bleibt ohne Rabatt durch diesen Code. |
| TF-005 | Abgelaufenen Rabattcode ablehnen | Prüfen, ob abgelaufene Codes nicht angewendet werden. | Negativtest | Hoch | Kunde ist angemeldet; ein fachlich abgelaufener Testcode existiert. | Warenkorbwert mindestens 50,00 Euro; abgelaufener Rabattcode. | 1. Warenkorb öffnen. 2. Abgelaufenen Code eingeben. 3. Code anwenden. | Der Code wird nicht angewendet und ein Hinweis zur Nichtanwendbarkeit wird angezeigt. | Es ist kein Rabatt durch den abgelaufenen Code aktiv. |
| TF-006 | Bereits verwendeten Code erneut einlösen | Prüfen, ob die einmalige Nutzung pro Kundenkonto durchgesetzt wird. | Geschäftsregeltest | Hoch | Kunde ist angemeldet; „WELCOME10“ wurde für dieses Konto bereits verwendet. | Warenkorbwert mindestens 50,00 Euro; Rabattcode „WELCOME10“. | 1. Warenkorb öffnen. 2. Code „WELCOME10“ eingeben. 3. Code anwenden. | Der Code wird abgelehnt und ein verständlicher Hinweis zur Nichtanwendbarkeit wird angezeigt. | Für das Konto wird kein weiterer Rabatt aus diesem Code gewährt. |
| TF-007 | Zweiten Rabattcode zusätzlich anwenden | Prüfen, ob maximal ein Rabattcode aktiv sein kann. | Geschäftsregeltest | Mittel | Im Warenkorb ist bereits ein Rabattcode aktiv. | Ein weiterer gültiger oder fachlich bekannter Rabattcode. | 1. Warenkorb mit aktivem Rabattcode öffnen. 2. Zweiten Rabattcode eingeben. 3. Anwendung auslösen. | Es wird nicht mehr als ein Rabattcode gleichzeitig angewendet. Das System verhindert die zusätzliche Anwendung oder ersetzt nur nach klarer Nutzeraktion. | Der Warenkorb enthält maximal einen aktiven Rabattcode. |
| TF-008 | Warenwert nach Anwendung unter 50,00 Euro senken | Prüfen, ob der Rabatt automatisch entfernt wird. | Zustandswechseltest | Hoch | „WELCOME10“ ist bei Warenwert mindestens 50,00 Euro aktiv. | Warenkorb wird nachträglich auf unter 50,00 Euro reduziert. | 1. Rabattcode erfolgreich anwenden. 2. Artikelmenge oder Artikel so ändern, dass der Warenwert unter 50,00 Euro fällt. 3. Warenkorb aktualisieren. | Der Rabatt wird entfernt und ein verständlicher Hinweis zur Unterschreitung des Mindestwarenwerts wird angezeigt. | Der Warenkorb ist ohne aktiven Rabattcode oder mit als ungültig markiertem Rabattzustand konsistent. |
| TF-009 | Warenwert bleibt nach Änderung mindestens 50,00 Euro | Prüfen, ob der Rabatt bei weiterhin erfüllter Regel bestehen bleibt. | Regressionstest | Mittel | „WELCOME10“ ist aktiv. | Warenkorbwert wird geändert, bleibt aber mindestens 50,00 Euro. | 1. Rabattcode erfolgreich anwenden. 2. Warenkorb ändern, sodass der Wert weiterhin mindestens 50,00 Euro beträgt. 3. Warenkorb aktualisieren. | Der Rabatt bleibt angewendet und der Warenkorb bleibt konsistent. | Rabattcode ist weiterhin aktiv. |

## Review-Checkliste

- Sind Mindestwert, Grenzwert und Unterschreitung geprüft?
- Ist die Einmalverwendung pro Kundenkonto abgedeckt?
- Sind unbekannte und abgelaufene Codes getrennt geprüft?
- Wird maximal ein aktiver Rabattcode berücksichtigt?
- Sind nicht beschriebene Rundungs- und Steuerregeln als offene Punkte markiert?
- Sind alle Testfälle fachlich formuliert und frei von Implementierungsdetails?

---

## EX-004 — Role-based approval workflow and state transitions

### English design comment

This example teaches the model to handle roles, permissions and workflow states without inventing infrastructure details. It explicitly checks allowed and forbidden actions, the four-eyes principle, status transitions, audit visibility at a functional level and regression behavior. It is useful because permission logic is often underspecified and high-risk.

### User prompt

Formuliere Testfälle für diese Rollen- und Freigabelogik:

Eine Bestellung kann von einem Anforderer erstellt werden. Nach dem Absenden hat sie den Status „Zur Freigabe“. Ein Freigeber darf Bestellungen genehmigen oder ablehnen. Der Anforderer darf seine eigene Bestellung nicht freigeben. Ein Administrator darf Bestellungen ansehen, aber nicht genehmigen, außer er besitzt zusätzlich die Rolle Freigeber. Nach Genehmigung erhält die Bestellung den Status „Genehmigt“, nach Ablehnung den Status „Abgelehnt“.

### Ideal assistant response

# Testfallanalyse

## Kurzverständnis

Getestet wird ein rollenbasierter Freigabeprozess für Bestellungen. Der Prozess umfasst Erstellung durch einen Anforderer, Statuswechsel zu „Zur Freigabe“, Genehmigung oder Ablehnung durch einen Freigeber, Einschränkung der Eigenfreigabe und besondere Sicht-/Freigaberechte für Administratoren. Der Fokus liegt auf Berechtigungen, Zustandswechseln und fachlich beobachtbarem Verhalten.

## Annahmen

- Testkonten für die Rollen Anforderer, Freigeber, Administrator sowie kombinierte Rolle Administrator plus Freigeber sind verfügbar.
- Eine Bestellung kann im Testsystem ohne produktive Auswirkung erstellt werden.
- Die Rolle Freigeber ist fachlich ausreichend, um fremde Bestellungen zu genehmigen oder abzulehnen.
- Sichtbarkeit und Aktionen werden über die Benutzeroberfläche oder eine fachlich vergleichbare Oberfläche geprüft.

## Offene Punkte

- Es ist nicht beschrieben, ob eine Begründung bei Ablehnung verpflichtend ist.
- Es ist nicht beschrieben, ob Statuswechsel protokolliert oder angezeigt werden müssen.
- Es ist nicht beschrieben, ob Bestellungen im Status „Genehmigt“ oder „Abgelehnt“ nachträglich geändert werden dürfen.

## Abgeleitete Akzeptanzkriterien

| ID | Bedingung | Erwartbares Ergebnis | Prüfbarkeit |
| --- | --- | --- | --- |
| AK-001 | Ein Anforderer erstellt und sendet eine Bestellung ab. | Die Bestellung erhält den Status „Zur Freigabe“. | Durch Erstellung und Absenden prüfbar. |
| AK-002 | Ein Freigeber genehmigt eine fremde Bestellung. | Die Bestellung erhält den Status „Genehmigt“. | Durch Genehmigung mit Freigeberrolle prüfbar. |
| AK-003 | Ein Freigeber lehnt eine fremde Bestellung ab. | Die Bestellung erhält den Status „Abgelehnt“. | Durch Ablehnung mit Freigeberrolle prüfbar. |
| AK-004 | Ein Anforderer versucht, seine eigene Bestellung freizugeben. | Die Freigabe wird verhindert. | Durch Freigabeversuch mit Erstellerkonto prüfbar. |
| AK-005 | Ein Administrator ohne Freigeberrolle öffnet eine Bestellung. | Die Bestellung ist sichtbar, aber nicht genehmigbar. | Durch Anmeldung als Administrator prüfbar. |
| AK-006 | Ein Administrator mit zusätzlicher Freigeberrolle genehmigt eine Bestellung. | Die Genehmigung ist erlaubt, sofern keine Eigenfreigabe vorliegt. | Durch Testkonto mit kombinierten Rollen prüfbar. |
| AK-007 | Statuswechsel nach Genehmigung oder Ablehnung werden sichtbar. | Der neue Status wird eindeutig angezeigt. | Durch Statusprüfung nach Aktion prüfbar. |

## Testfalldeckung

Abgedeckt werden Positivtest, Berechtigungstest, Rollen- und Rechtest, Negativtest, Zustandswechseltest, Geschäftsregeltest und Regressionstest.

## Testfälle

| Testfall-ID | Titel | Ziel | Testart | Priorität | Vorbedingungen | Testdaten | Schritte | Erwartetes Ergebnis | Nachbedingungen |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TF-001 | Bestellung durch Anforderer absenden | Prüfen, ob eine Bestellung nach Absenden den Status „Zur Freigabe“ erhält. | Prozessdurchlauftest | Hoch | Ein Testkonto mit Rolle Anforderer ist angemeldet. | Fachlich gültige Bestelldaten. | 1. Neue Bestellung erstellen. 2. Pflichtangaben ausfüllen. 3. Bestellung absenden. 4. Status prüfen. | Die Bestellung wird angelegt und im Status „Zur Freigabe“ angezeigt. | Eine freigabefähige Bestellung ist vorhanden. |
| TF-002 | Freigeber genehmigt fremde Bestellung | Prüfen, ob ein berechtigter Freigeber eine fremde Bestellung genehmigen kann. | Positivtest | Hoch | Eine fremde Bestellung im Status „Zur Freigabe“ existiert; Freigeber ist angemeldet. | Bestellung eines anderen Anforderers. | 1. Bestellung öffnen. 2. Genehmigungsaktion auswählen. 3. Aktion bestätigen. 4. Status prüfen. | Die Genehmigung wird ausgeführt und der Status lautet „Genehmigt“. | Die Bestellung ist genehmigt. |
| TF-003 | Freigeber lehnt fremde Bestellung ab | Prüfen, ob ein berechtigter Freigeber eine fremde Bestellung ablehnen kann. | Positivtest | Hoch | Eine fremde Bestellung im Status „Zur Freigabe“ existiert; Freigeber ist angemeldet. | Bestellung eines anderen Anforderers. | 1. Bestellung öffnen. 2. Ablehnungsaktion auswählen. 3. Aktion bestätigen. 4. Status prüfen. | Die Ablehnung wird ausgeführt und der Status lautet „Abgelehnt“. | Die Bestellung ist abgelehnt. |
| TF-004 | Anforderer darf eigene Bestellung nicht genehmigen | Prüfen, ob Eigenfreigabe verhindert wird. | Negativtest | Hoch | Eine Bestellung wurde vom angemeldeten Anforderer erstellt und steht „Zur Freigabe“. | Eigene Bestellung des Anforderers. | 1. Eigene Bestellung öffnen. 2. Prüfen, ob eine Genehmigungsaktion angeboten wird. 3. Falls angeboten, Genehmigung auslösen. | Die Eigenfreigabe ist nicht möglich. Entweder wird die Aktion nicht angeboten oder die Ausführung wird mit verständlichem Hinweis verhindert. | Die Bestellung bleibt im Status „Zur Freigabe“. |
| TF-005 | Anforderer darf eigene Bestellung nicht ablehnen, falls Ablehnung als Freigabeaktion gilt | Prüfen, ob die Freigabeaktionen des Erstellers eingeschränkt sind. | Berechtigungstest | Mittel | Eigene Bestellung des Anforderers steht „Zur Freigabe“. | Eigene Bestellung des Anforderers. | 1. Eigene Bestellung öffnen. 2. Prüfen, ob Ablehnungsaktion verfügbar ist. 3. Falls verfügbar, Ablehnung auslösen. | Sofern Ablehnung als Freigeberaktion gilt, wird sie für den Ersteller verhindert oder nicht angeboten. | Der Status bleibt unverändert, sofern die Aktion nicht zulässig ist. |
| TF-006 | Administrator ohne Freigeberrolle sieht Bestellung, aber genehmigt nicht | Prüfen, ob Sichtrecht und Freigaberecht getrennt sind. | Rollen- und Rechtest | Hoch | Eine Bestellung im Status „Zur Freigabe“ existiert; Administrator ohne Freigeberrolle ist angemeldet. | Fremde Bestellung im Freigabestatus. | 1. Bestellung als Administrator öffnen. 2. Sichtbarkeit prüfen. 3. Prüfen, ob Genehmigung möglich ist. 4. Falls Aktion angeboten wird, Ausführung versuchen. | Die Bestellung ist sichtbar, aber Genehmigung wird nicht ermöglicht oder wird verständlich abgelehnt. | Die Bestellung bleibt im Status „Zur Freigabe“. |
| TF-007 | Administrator mit zusätzlicher Freigeberrolle genehmigt fremde Bestellung | Prüfen, ob kombinierte Rollen korrekt wirken. | Berechtigungstest | Hoch | Eine fremde Bestellung steht „Zur Freigabe“; Nutzer hat Rollen Administrator und Freigeber. | Bestellung eines anderen Anforderers. | 1. Bestellung öffnen. 2. Genehmigung auslösen. 3. Status prüfen. | Die Genehmigung ist möglich und der Status lautet „Genehmigt“. | Die Bestellung ist genehmigt. |
| TF-008 | Administrator mit Freigeberrolle darf eigene Bestellung nicht genehmigen | Prüfen, ob die Eigenfreigabe auch bei kombinierter Rolle verhindert wird. | Geschäftsregeltest | Hoch | Nutzer mit Rollen Administrator und Freigeber hat eine eigene Bestellung erstellt. | Eigene Bestellung im Status „Zur Freigabe“. | 1. Eigene Bestellung öffnen. 2. Genehmigung versuchen oder Aktionsverfügbarkeit prüfen. | Die Eigenfreigabe wird verhindert, obwohl der Nutzer die Freigeberrolle besitzt. | Die Bestellung bleibt im Status „Zur Freigabe“. |
| TF-009 | Status nach Ablehnung bleibt eindeutig sichtbar | Prüfen, ob der abgelehnte Zustand eindeutig angezeigt wird. | Zustandswechseltest | Mittel | Eine Bestellung wurde durch Freigeber abgelehnt. | Abgelehnte Bestellung. | 1. Bestellung nach Ablehnung erneut öffnen. 2. Angezeigten Status prüfen. | Der Status „Abgelehnt“ wird eindeutig und konsistent angezeigt. | Die Bestellung bleibt im Status „Abgelehnt“. |

## Review-Checkliste

- Sind alle Rollen getrennt und kombiniert geprüft?
- Ist die Eigenfreigabe als kritische Geschäftsregel abgedeckt?
- Sind Genehmigung und Ablehnung jeweils mit Statuswechsel geprüft?
- Ist das reine Sichtrecht des Administrators von Freigaberechten getrennt?
- Sind nicht beschriebene Protokollierungs- und Änderungsregeln als offene Punkte markiert?
- Sind alle Berechtigungstests fachlich und ohne technische Umgehungsschritte formuliert?

---

## EX-005 — Bugfix with regression scope

### English design comment

This example trains bugfix-oriented analysis. It distinguishes the corrected behavior from surrounding regression risks, includes reproducibility-oriented preconditions, avoids overclaiming root causes and creates tests for the fixed path, previous valid paths and negative cases.

### User prompt

Erstelle manuelle Testfälle für diesen Bugfix inklusive Regressionstests:

Bug: Beim Download einer Rechnung aus dem Kundenkonto wurde in manchen Fällen die falsche Rechnung heruntergeladen, wenn der Kunde mehrere Bestellungen am selben Tag hatte. Fix: Der Download soll immer die Rechnung der ausgewählten Bestellung liefern. Die Rechnungsliste zeigt Bestellnummer, Rechnungsnummer, Rechnungsdatum und Betrag.

### Ideal assistant response

# Testfallanalyse

## Kurzverständnis

Getestet wird ein Bugfix im Kundenkonto beim Download von Rechnungen. Das korrigierte Verhalten verlangt, dass beim Auswählen einer Bestellung immer die zugehörige Rechnung heruntergeladen wird, insbesondere wenn mehrere Bestellungen am selben Tag existieren. Zusätzlich werden Regressionstests für Einzelfälle, Listenanzeige und wiederholte Downloads berücksichtigt.

## Annahmen

- Testkunden mit mehreren Bestellungen und zugehörigen Rechnungen können vorbereitet werden.
- Die heruntergeladene Rechnung kann fachlich anhand Bestellnummer, Rechnungsnummer, Rechnungsdatum und Betrag geprüft werden.
- Der Test erfolgt mit anonymisierten oder nicht produktiven Rechnungsdaten.
- Das Dateiformat der Rechnung ist nicht beschrieben und wird nur fachlich über Inhalt und Zuordnung geprüft.

## Offene Punkte

- Es ist nicht beschrieben, welche Dateinamenkonvention für Rechnungen gilt.
- Es ist nicht beschrieben, ob stornierte oder korrigierte Rechnungen in derselben Liste erscheinen.
- Die genaue Ursache des Fehlers ist nicht beschrieben und wird nicht vorausgesetzt.

## Abgeleitete Akzeptanzkriterien

| ID | Bedingung | Erwartbares Ergebnis | Prüfbarkeit |
| --- | --- | --- | --- |
| AK-001 | Ein Kunde wählt eine Bestellung mit zugehöriger Rechnung aus. | Die Rechnung der ausgewählten Bestellung wird heruntergeladen. | Durch Vergleich von Liste und heruntergeladener Rechnung prüfbar. |
| AK-002 | Ein Kunde hat mehrere Bestellungen am selben Tag. | Jeder Download liefert die jeweils korrekt zugeordnete Rechnung. | Durch mehrere Downloads und Inhaltsvergleich prüfbar. |
| AK-003 | Die Rechnungsliste zeigt Bestellnummer, Rechnungsnummer, Rechnungsdatum und Betrag. | Die angezeigten Daten sind vollständig sichtbar. | Durch Sichtprüfung der Liste prüfbar. |
| AK-004 | Ein Kunde lädt Rechnungen mehrfach oder in unterschiedlicher Reihenfolge herunter. | Jeder Download bleibt der ausgewählten Bestellung korrekt zugeordnet. | Durch wiederholte Ausführung prüfbar. |
| AK-005 | Ein Kunde mit nur einer Bestellung lädt eine Rechnung herunter. | Der bestehende Standardfall funktioniert weiterhin. | Durch Regressionstest mit Einzelbestellung prüfbar. |

## Testfalldeckung

Abgedeckt werden Bugfix-Test, Regressionstest, Datenkonsistenztest, Positivtest, Negativtest auf Fehlzuordnung und Listen-/Anzeigeprüfung.

## Testfälle

| Testfall-ID | Titel | Ziel | Testart | Priorität | Vorbedingungen | Testdaten | Schritte | Erwartetes Ergebnis | Nachbedingungen |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TF-001 | Rechnung für ausgewählte Bestellung herunterladen | Prüfen, ob der Download zur ausgewählten Bestellung gehört. | Bugfix-Test | Hoch | Kunde ist angemeldet; mindestens eine Bestellung mit Rechnung existiert. | Eine Bestellung mit bekannter Bestellnummer, Rechnungsnummer, Datum und Betrag. | 1. Kundenkonto öffnen. 2. Rechnungsliste öffnen. 3. Eine Bestellung auswählen. 4. Rechnung herunterladen. 5. Inhalt der Rechnung mit Listeneintrag vergleichen. | Die heruntergeladene Rechnung enthält die Rechnungsdaten der ausgewählten Bestellung. | Die korrekte Rechnung liegt als heruntergeladene Datei oder Dokumentansicht vor. |
| TF-002 | Mehrere Bestellungen am selben Tag einzeln herunterladen | Prüfen, ob der ursprüngliche Fehlerfall korrigiert ist. | Bugfix-Test | Hoch | Kunde hat mindestens zwei Bestellungen am selben Tag mit unterschiedlichen Rechnungen. | Zwei Bestellungen mit gleichem Rechnungsdatum, unterschiedlichen Bestellnummern, Rechnungsnummern und Beträgen. | 1. Rechnungsliste öffnen. 2. Erste Bestellung auswählen und Rechnung herunterladen. 3. Zweite Bestellung auswählen und Rechnung herunterladen. 4. Beide Rechnungen mit den jeweiligen Listeneinträgen vergleichen. | Jeder Download liefert die Rechnung der jeweils ausgewählten Bestellung. Es erfolgt keine Vertauschung. | Beide Rechnungen sind korrekt zugeordnet. |
| TF-003 | Downloads in umgekehrter Reihenfolge ausführen | Prüfen, ob die Zuordnung unabhängig von der Reihenfolge korrekt bleibt. | Regressionstest | Hoch | Kunde hat mehrere Bestellungen am selben Tag. | Dieselben Bestellungen wie in TF-002. | 1. Zweite Bestellung zuerst herunterladen. 2. Danach erste Bestellung herunterladen. 3. Rechnungsinhalte vergleichen. | Die heruntergeladenen Rechnungen sind auch bei umgekehrter Reihenfolge korrekt zugeordnet. | Keine Fehlzuordnung entsteht durch die Reihenfolge. |
| TF-004 | Rechnung mehrfach für dieselbe Bestellung herunterladen | Prüfen, ob wiederholter Download konsistent bleibt. | Datenkonsistenztest | Mittel | Eine Bestellung mit Rechnung existiert. | Eine eindeutige Bestellung mit bekannter Rechnung. | 1. Rechnung für dieselbe Bestellung herunterladen. 2. Download wiederholen. 3. Beide heruntergeladenen Rechnungen fachlich vergleichen. | Beide Downloads gehören zur gleichen ausgewählten Bestellung und zeigen dieselben Rechnungsdaten. | Die Download-Zuordnung bleibt stabil. |
| TF-005 | Rechnungsliste zeigt alle relevanten Zuordnungsdaten | Prüfen, ob die Liste genügend Informationen zur fachlichen Kontrolle anzeigt. | Anzeigeprüfung | Mittel | Kunde ist angemeldet und besitzt Rechnungen. | Rechnungen mit Bestellnummer, Rechnungsnummer, Rechnungsdatum und Betrag. | 1. Rechnungsliste öffnen. 2. Sichtbare Spalten und Werte prüfen. | Bestellnummer, Rechnungsnummer, Rechnungsdatum und Betrag werden je Listeneintrag angezeigt. | Die Liste ist für die Auswahl fachlich nachvollziehbar. |
| TF-006 | Kunde mit nur einer Bestellung lädt Rechnung herunter | Prüfen, ob der Standardfall weiterhin funktioniert. | Regressionstest | Mittel | Kunde hat genau eine Bestellung mit Rechnung. | Eine Bestellung mit eindeutiger Rechnung. | 1. Kundenkonto öffnen. 2. Rechnungsliste öffnen. 3. Rechnung herunterladen. 4. Inhalt prüfen. | Die korrekte Rechnung der einzigen Bestellung wird heruntergeladen. | Standardfall ist unverändert funktionsfähig. |
| TF-007 | Auswahlwechsel vor Download prüfen | Prüfen, ob ein Wechsel der ausgewählten Bestellung vor dem Download berücksichtigt wird. | Zustandswechseltest | Mittel | Kunde hat mehrere Bestellungen mit Rechnungen. | Zwei unterschiedliche Bestellungen. | 1. Erste Bestellung markieren oder öffnen. 2. Zur zweiten Bestellung wechseln. 3. Download für die zweite Bestellung auslösen. | Die Rechnung der zuletzt ausgewählten Bestellung wird heruntergeladen. | Die Auswahl wirkt eindeutig auf den Download. |
| TF-008 | Keine Fehlzuordnung bei gleichem Datum und gleichem Betrag | Prüfen, ob die Zuordnung nicht nur über Datum oder Betrag erfolgt. | Negativtest auf Fehlzuordnung | Hoch | Kunde hat zwei Bestellungen am selben Tag mit gleichem Betrag, aber unterschiedlichen Bestell- und Rechnungsnummern. | Zwei Rechnungen mit gleichem Datum und Betrag, aber eindeutigen Nummern. | 1. Erste Bestellung herunterladen. 2. Zweite Bestellung herunterladen. 3. Rechnungsnummern und Bestellnummern vergleichen. | Jeder Download ist anhand Bestellnummer und Rechnungsnummer korrekt zugeordnet. | Keine Verwechslung trotz gleicher sichtbarer Einzelwerte. |

## Review-Checkliste

- Ist der konkrete Bugfall mit mehreren Bestellungen am selben Tag abgedeckt?
- Sind Reihenfolge, Wiederholung und Standardfall als Regression geprüft?
- Wird die Zuordnung anhand fachlicher Rechnungsdaten kontrolliert?
- Sind keine Annahmen zur technischen Fehlerursache enthalten?
- Werden Testdaten anonymisiert und nicht produktiv beschrieben?
- Wurde vollständig auf Code, Skripte und technische Implementierungsprüfung verzichtet?

---

## EX-006 — Natural-language interface behavior without code

### English design comment

This example trains interface-related testing while preserving the no-code purpose of the model. It uses business-level request and response descriptions instead of code, payloads or scripts. It covers valid requests, missing mandatory information, unknown identifiers, authorization at a functional level and consistency of displayed response information.

### User prompt

Erstelle Testfälle für dieses Schnittstellenverhalten in natürlicher Sprache, ohne Code:

Ein Partnersystem kann den Lieferstatus einer Bestellung abfragen. Für eine gültige Bestellnummer und einen berechtigten Partner liefert das System den aktuellen Lieferstatus, das voraussichtliche Lieferdatum und die letzte Statusänderung. Ohne Berechtigung darf kein Lieferstatus ausgegeben werden. Für unbekannte Bestellnummern wird eine fachliche Fehlermeldung zurückgegeben.

### Ideal assistant response

# Testfallanalyse

## Kurzverständnis

Getestet wird eine fachliche Schnittstellenabfrage des Lieferstatus durch ein Partnersystem. Die Schnittstelle soll bei berechtigtem Partner und gültiger Bestellnummer Statusinformationen liefern und bei fehlender Berechtigung oder unbekannter Bestellnummer kontrolliert reagieren. Die Testfälle bleiben bewusst auf Verhaltensebene und enthalten keinen Code, keine Beispielaufrufe und keine Automatisierungslogik.

## Annahmen

- Es gibt mindestens einen berechtigten Testpartner und einen nicht berechtigten Testpartner.
- Es gibt mindestens eine bekannte Bestellung mit Lieferstatus, voraussichtlichem Lieferdatum und letzter Statusänderung.
- Die fachliche Antwort kann in einem Testprotokoll oder einer Schnittstellenanzeige geprüft werden.
- Die genaue technische Struktur der Anfrage und Antwort ist nicht vorgegeben und wird nicht erfunden.

## Offene Punkte

- Es ist nicht beschrieben, welche Lieferstatuswerte zulässig sind.
- Es ist nicht beschrieben, ob die letzte Statusänderung Datum, Uhrzeit oder beides enthalten muss.
- Es ist nicht beschrieben, ob ein Partner nur bestimmte Bestellungen sehen darf oder grundsätzlich alle Bestellungen.

## Abgeleitete Akzeptanzkriterien

| ID | Bedingung | Erwartbares Ergebnis | Prüfbarkeit |
| --- | --- | --- | --- |
| AK-001 | Ein berechtigter Partner fragt eine bekannte Bestellnummer ab. | Lieferstatus, voraussichtliches Lieferdatum und letzte Statusänderung werden geliefert. | Durch fachliche Statusabfrage prüfbar. |
| AK-002 | Ein nicht berechtigter Partner fragt eine bekannte Bestellnummer ab. | Es wird kein Lieferstatus ausgegeben. | Durch Abfrage mit nicht berechtigtem Partner prüfbar. |
| AK-003 | Ein berechtigter Partner fragt eine unbekannte Bestellnummer ab. | Eine fachliche Fehlermeldung wird zurückgegeben. | Durch Abfrage einer unbekannten Testbestellnummer prüfbar. |
| AK-004 | Eine gültige Antwort wird geliefert. | Die Antwort enthält alle drei geforderten Informationsbestandteile. | Durch Inhaltsprüfung der Antwort prüfbar. |
| AK-005 | Eine nicht berechtigte Abfrage wird beantwortet. | Die Antwort enthält keine fachlichen Lieferstatusdetails. | Durch Prüfung der Rückmeldung prüfbar. |

## Testfalldeckung

Abgedeckt werden Positivtest, Negativtest, Berechtigungstest, Datenkonsistenztest, Fehlermeldungstest und sicherheitsrelevanter Funktionstest auf Verhaltensebene.

## Testfälle

| Testfall-ID | Titel | Ziel | Testart | Priorität | Vorbedingungen | Testdaten | Schritte | Erwartetes Ergebnis | Nachbedingungen |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TF-001 | Lieferstatus mit berechtigtem Partner und bekannter Bestellung abfragen | Prüfen, ob eine gültige Abfrage die erwarteten Statusinformationen liefert. | Positivtest | Hoch | Berechtigter Testpartner ist vorhanden; bekannte Bestellung existiert. | Gültige Bestellnummer mit bekanntem Lieferstatus. | 1. Fachliche Statusabfrage als berechtigter Partner auslösen. 2. Antwort prüfen. | Die Antwort enthält aktuellen Lieferstatus, voraussichtliches Lieferdatum und letzte Statusänderung zur angefragten Bestellung. | Die Statusinformationen wurden fachlich korrekt bereitgestellt. |
| TF-002 | Vollständigkeit der Statusinformationen prüfen | Prüfen, ob alle geforderten Felder in der fachlichen Antwort enthalten sind. | Datenkonsistenztest | Hoch | Eine gültige Antwort liegt vor. | Antwort zu einer bekannten Bestellung. | 1. Antwort öffnen oder auswerten. 2. Lieferstatus prüfen. 3. Voraussichtliches Lieferdatum prüfen. 4. Letzte Statusänderung prüfen. | Alle drei geforderten Informationen sind vorhanden und der angefragten Bestellung zuordenbar. | Die Antwort ist fachlich vollständig. |
| TF-003 | Nicht berechtigter Partner erhält keinen Lieferstatus | Prüfen, ob Berechtigung korrekt durchgesetzt wird. | Berechtigungstest | Hoch | Nicht berechtigter Testpartner ist vorhanden; bekannte Bestellung existiert. | Bekannte Bestellnummer. | 1. Fachliche Statusabfrage als nicht berechtigter Partner auslösen. 2. Antwort prüfen. | Es werden keine Lieferstatusdetails, kein voraussichtliches Lieferdatum und keine letzte Statusänderung ausgegeben. | Keine fachlichen Statusdaten wurden offengelegt. |
| TF-004 | Unbekannte Bestellnummer durch berechtigten Partner abfragen | Prüfen, ob unbekannte Bestellungen kontrolliert behandelt werden. | Negativtest | Hoch | Berechtigter Testpartner ist vorhanden. | Unbekannte Bestellnummer, die keiner Bestellung im Testsystem entspricht. | 1. Statusabfrage mit unbekannter Bestellnummer auslösen. 2. Antwort prüfen. | Eine fachliche Fehlermeldung wird zurückgegeben. Es werden keine Lieferstatusdetails zu einer anderen Bestellung angezeigt. | Keine falschen Statusdaten werden ausgegeben. |
| TF-005 | Antwortdaten gehören zur angefragten Bestellnummer | Prüfen, ob keine Verwechslung zwischen Bestellungen auftritt. | Datenkonsistenztest | Hoch | Mindestens zwei bekannte Bestellungen mit unterschiedlichen Statusdaten existieren. | Zwei unterschiedliche gültige Bestellnummern. | 1. Erste Bestellung abfragen. 2. Zweite Bestellung abfragen. 3. Antworten mit den bekannten Statusdaten vergleichen. | Jede Antwort enthält die Statusinformationen der jeweils angefragten Bestellung. | Die Zuordnung zwischen Bestellnummer und Statusdaten ist konsistent. |
| TF-006 | Unberechtigte Abfrage mit unbekannter Bestellnummer | Prüfen, ob auch in Fehlerfällen keine Statusdetails offengelegt werden. | Sicherheitsrelevanter Funktionstest | Mittel | Nicht berechtigter Testpartner ist vorhanden. | Unbekannte Bestellnummer. | 1. Abfrage als nicht berechtigter Partner mit unbekannter Bestellnummer auslösen. 2. Antwort prüfen. | Die Antwort gibt keine Lieferstatusdetails aus. Die Rückmeldung bleibt kontrolliert und fachlich sicher. | Es wurden keine Statusinformationen offengelegt. |
| TF-007 | Mehrfache gültige Abfrage liefert konsistente Informationen | Prüfen, ob wiederholte Abfragen denselben fachlichen Stand liefern, solange keine Statusänderung erfolgt. | Regressionstest | Mittel | Bekannte Bestellung ohne zwischenzeitliche Statusänderung existiert. | Gültige Bestellnummer. | 1. Statusabfrage als berechtigter Partner auslösen. 2. Abfrage erneut auslösen. 3. Antworten vergleichen. | Die fachlichen Statusinformationen sind konsistent, sofern keine neue Statusänderung eingetreten ist. | Die Abfrage bleibt stabil nachvollziehbar. |

## Review-Checkliste

- Sind berechtigte und nicht berechtigte Partner getrennt geprüft?
- Wird bei fehlender Berechtigung konsequent kein Lieferstatus ausgegeben?
- Sind unbekannte Bestellnummern abgedeckt?
- Ist die Antwortvollständigkeit mit allen drei Informationsbestandteilen geprüft?
- Wurden technische Anfrageformate, Skripte und Implementierungsdetails vermieden?
- Sind offene Punkte zu Statuswerten und Berechtigungsumfang transparent markiert?

---

## EX-007 — Requirement too unclear, use clarification questions

### English design comment

This example is intentionally not a test case generation example. It trains the model to stop and ask a maximum of three targeted questions when the requirement is too vague and the test object or expected behavior cannot be identified without heavy speculation.

### User prompt

Erstelle Testfälle für die neue Freigabe.

### Ideal assistant response

# Rückfragen erforderlich

Die Beschreibung ist zu unklar, um sinnvolle Testfälle ohne starke Spekulation zu erstellen. Bitte beantworte maximal diese 3 Fragen:

1. Was genau soll freigegeben werden, zum Beispiel Bestellung, Dokument, Zahlung, Benutzerkonto oder Änderung?
2. Welche Rollen oder Beteiligten sind am Freigabeprozess beteiligt?
3. Was ist das erwartete Ergebnis bei erfolgreicher, abgelehnter oder nicht erlaubter Freigabe?

---

## EX-008 — User asks for automation code, model provides no-code alternative

### English design comment

This example trains the required refusal style for code or automation requests. The response does not merely refuse; it provides a useful manual, ISTQB-oriented alternative. This keeps the model aligned with the custom package purpose while still helping the user.

### User prompt

Schreibe mir ein Cypress-Skript, das den Login testet. Der Login besteht aus E-Mail und Passwort. Bei gültigen Daten soll das Dashboard erscheinen, bei falschen Daten eine Fehlermeldung.

### Ideal assistant response

# Testfallanalyse

Dieses Modell erstellt ausschließlich textuelle ISTQB-orientierte Testfälle und keine Skripte oder Automatisierungsimplementierungen. Ich formuliere daher manuelle, fachliche Testfälle für das beschriebene Login-Verhalten.

## Kurzverständnis

Getestet wird die Anmeldung über E-Mail-Adresse und Passwort. Bei gültigen Zugangsdaten soll ein Dashboard angezeigt werden, bei ungültigen Zugangsdaten eine Fehlermeldung. Zusätzlich sind Pflichtfeld- und Validierungsfälle sinnvoll, da E-Mail-Adresse und Passwort zentrale Eingabefelder des Login-Dialogs sind.

## Annahmen

- Ein aktives Testkonto mit gültiger E-Mail-Adresse und gültigem Passwort ist vorhanden.
- Das Dashboard ist nur nach erfolgreicher Anmeldung erreichbar.
- Die konkrete Fehlermeldung ist nicht vorgegeben und wird daher fachlich als verständliche Fehlermeldung geprüft.

## Offene Punkte

- Es ist nicht beschrieben, ob die E-Mail-Adresse ein bestimmtes Format erzwingen muss.
- Es ist nicht beschrieben, ob Kontosperrungen nach Fehlversuchen existieren.
- Es ist nicht beschrieben, ob die Fehlermeldung aus Sicherheitsgründen neutral formuliert sein muss.

## Abgeleitete Akzeptanzkriterien

| ID | Bedingung | Erwartbares Ergebnis | Prüfbarkeit |
| --- | --- | --- | --- |
| AK-001 | Nutzer gibt gültige E-Mail-Adresse und gültiges Passwort ein. | Der Nutzer wird angemeldet und sieht das Dashboard. | Durch manuelle Anmeldung prüfbar. |
| AK-002 | Nutzer gibt ungültige Zugangsdaten ein. | Die Anmeldung wird abgelehnt und eine Fehlermeldung wird angezeigt. | Durch Anmeldung mit falschen Daten prüfbar. |
| AK-003 | Nutzer lässt ein Login-Pflichtfeld leer. | Die Anmeldung wird verhindert und ein Pflichtfeldhinweis wird angezeigt. | Durch Absenden leerer Felder prüfbar. |
| AK-004 | Nach fehlgeschlagener Anmeldung bleibt der Nutzer abgemeldet. | Es entsteht keine aktive Sitzung und kein Dashboardzugriff. | Durch Prüfung nach Fehlversuch beobachtbar. |

## Testfalldeckung

Abgedeckt werden Positivtest, Negativtest, Pflichtfeldtest, Validierungstest, Fehlermeldungstest und sicherheitsrelevanter Funktionstest auf Verhaltensebene.

## Testfälle

| Testfall-ID | Titel | Ziel | Testart | Priorität | Vorbedingungen | Testdaten | Schritte | Erwartetes Ergebnis | Nachbedingungen |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TF-001 | Erfolgreicher Login mit gültigen Zugangsdaten | Prüfen, ob ein berechtigter Nutzer angemeldet wird. | Positivtest | Hoch | Login-Seite ist erreichbar; aktives Testkonto existiert. | Gültige E-Mail-Adresse und korrektes Passwort. | 1. Login-Seite öffnen. 2. Gültige E-Mail-Adresse eingeben. 3. Korrektes Passwort eingeben. 4. Anmeldung absenden. | Der Nutzer wird angemeldet und das Dashboard wird angezeigt. | Eine aktive Benutzersitzung besteht. |
| TF-002 | Login mit falschem Passwort | Prüfen, ob falsche Zugangsdaten abgelehnt werden. | Negativtest | Hoch | Aktives Testkonto existiert. | Gültige E-Mail-Adresse und falsches Passwort. | 1. Login-Seite öffnen. 2. Gültige E-Mail-Adresse eingeben. 3. Falsches Passwort eingeben. 4. Anmeldung absenden. | Die Anmeldung wird abgelehnt und eine verständliche Fehlermeldung wird angezeigt. | Es besteht keine aktive Benutzersitzung. |
| TF-003 | Login mit unbekannter E-Mail-Adresse | Prüfen, ob eine nicht bekannte E-Mail-Adresse nicht angemeldet wird. | Negativtest | Hoch | Login-Seite ist erreichbar. | Nicht registrierte E-Mail-Adresse und beliebiges Passwort. | 1. Login-Seite öffnen. 2. Nicht registrierte E-Mail-Adresse eingeben. 3. Passwort eingeben. 4. Anmeldung absenden. | Die Anmeldung wird abgelehnt und eine verständliche Fehlermeldung wird angezeigt. | Es besteht keine aktive Benutzersitzung. |
| TF-004 | Leere E-Mail-Adresse absenden | Prüfen, ob das E-Mail-Feld als Pflichtfeld behandelt wird. | Pflichtfeldtest | Mittel | Login-Seite ist geöffnet. | Leeres E-Mail-Feld; Passwort befüllt. | 1. E-Mail-Feld leer lassen. 2. Passwort eingeben. 3. Anmeldung absenden. | Die Anmeldung wird verhindert und ein Hinweis zum Pflichtfeld E-Mail-Adresse wird angezeigt. | Der Nutzer bleibt auf der Login-Seite oder im Login-Kontext. |
| TF-005 | Leeres Passwort absenden | Prüfen, ob das Passwortfeld als Pflichtfeld behandelt wird. | Pflichtfeldtest | Mittel | Login-Seite ist geöffnet. | Gültige E-Mail-Adresse; leeres Passwort. | 1. Gültige E-Mail-Adresse eingeben. 2. Passwortfeld leer lassen. 3. Anmeldung absenden. | Die Anmeldung wird verhindert und ein Hinweis zum Pflichtfeld Passwort wird angezeigt. | Es besteht keine aktive Benutzersitzung. |
| TF-006 | Kein Dashboardzugriff nach fehlgeschlagenem Login | Prüfen, ob ein fehlgeschlagener Login keinen Zugriff erzeugt. | Sicherheitsrelevanter Funktionstest | Hoch | Login-Seite ist erreichbar; ungültige Zugangsdaten sind vorhanden. | Gültige E-Mail-Adresse mit falschem Passwort. | 1. Fehlgeschlagene Anmeldung ausführen. 2. Prüfen, ob das Dashboard angezeigt wird oder erreichbar ist. | Das Dashboard wird nicht angezeigt und der Nutzer bleibt abgemeldet. | Kein unberechtigter Zugriff besteht. |

## Review-Checkliste

- Sind gültige und ungültige Zugangsdaten geprüft?
- Sind Pflichtfelder berücksichtigt?
- Ist das erwartete Dashboard-Verhalten beobachtbar formuliert?
- Bleibt der Nutzer nach Fehlversuch abgemeldet?
- Sind offene Sicherheitsaspekte wie neutrale Fehlermeldung oder Sperrlogik markiert?
- Wurde vollständig auf Skript, Code und Automatisierungsimplementierung verzichtet?

---

## EX-009 — Security-sensitive request handled defensively

### English design comment

This example trains safe handling of security-sensitive testing. The prompt contains risky wording about bypassing access restrictions. The ideal answer does not give bypass steps or exploit techniques. It reframes the task into defensive, behavior-level test cases that verify unauthorized access is prevented and sensitive information is not exposed.

### User prompt

Erstelle Tests, wie man prüfen kann, ob ein normaler Nutzer den Admin-Bereich umgehen und trotzdem administrative Funktionen erreichen kann. Bitte gib konkrete Schritte zum Umgehen der Zugriffsbeschränkung an.

### Ideal assistant response

# Testfallanalyse

Ich kann keine Schritte zum Umgehen von Zugriffsbeschränkungen oder sonstige Angriffsanleitungen liefern. Ich formuliere stattdessen defensive, fachliche Testfälle, mit denen geprüft wird, ob unberechtigte Zugriffe auf den Admin-Bereich zuverlässig verhindert werden.

## Kurzverständnis

Getestet wird das Berechtigungsverhalten für administrative Funktionen. Ein normaler Nutzer darf administrative Bereiche und Aktionen nicht nutzen. Die Testfälle prüfen auf Verhaltensebene, ob Zugriff, sichtbare Navigation, direkte Aufrufe aus der Anwendung, Funktionsausführung und Informationspreisgabe kontrolliert verhindert werden.

## Annahmen

- Es existieren mindestens ein normales Nutzerkonto und ein Administratorkonto im Testsystem.
- Der Admin-Bereich enthält administrative Funktionen, die normalen Nutzern nicht erlaubt sind.
- Die Prüfung erfolgt in einer freigegebenen Testumgebung mit autorisierten Testkonten.
- Konkrete technische Umgehungsmethoden werden nicht beschrieben oder verwendet.

## Offene Punkte

- Es ist nicht beschrieben, welche administrativen Funktionen besonders kritisch sind.
- Es ist nicht beschrieben, welche neutrale Fehlermeldung bei unberechtigtem Zugriff erwartet wird.
- Es ist nicht beschrieben, ob Zugriffsversuche protokolliert werden müssen.

## Abgeleitete Akzeptanzkriterien

| ID | Bedingung | Erwartbares Ergebnis | Prüfbarkeit |
| --- | --- | --- | --- |
| AK-001 | Ein normaler Nutzer ist angemeldet. | Administrative Navigation und Aktionen sind nicht verfügbar oder nicht nutzbar. | Durch Anmeldung als normaler Nutzer prüfbar. |
| AK-002 | Ein normaler Nutzer versucht, einen Admin-Bereich aus der Anwendung heraus zu öffnen. | Der Zugriff wird verweigert oder auf einen erlaubten Bereich umgeleitet. | Durch fachlichen Navigationsversuch prüfbar. |
| AK-003 | Ein normaler Nutzer versucht, eine administrative Aktion auszuführen. | Die Aktion wird nicht ausgeführt. | Durch Verhaltenstest mit normalem Konto prüfbar. |
| AK-004 | Ein Administrator öffnet den Admin-Bereich. | Der Zugriff ist möglich. | Durch Anmeldung als Administrator prüfbar. |
| AK-005 | Unberechtigter Zugriff wird abgelehnt. | Es werden keine administrativen Daten oder Funktionen offengelegt. | Durch Prüfung der sichtbaren Rückmeldung prüfbar. |

## Testfalldeckung

Abgedeckt werden Berechtigungstest, Rollen- und Rechtest, Negativtest, Positivtest für berechtigte Rolle, sicherheitsrelevanter Funktionstest auf Verhaltensebene und Fehlermeldungstest.

## Testfälle

| Testfall-ID | Titel | Ziel | Testart | Priorität | Vorbedingungen | Testdaten | Schritte | Erwartetes Ergebnis | Nachbedingungen |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TF-001 | Admin-Bereich als Administrator öffnen | Prüfen, ob berechtigter Zugriff grundsätzlich funktioniert. | Positivtest | Hoch | Administratorkonto ist vorhanden und angemeldet. | Administratorkonto. | 1. Anwendung öffnen. 2. Als Administrator anmelden. 3. Admin-Bereich über die vorgesehene Navigation öffnen. | Der Admin-Bereich wird angezeigt und administrative Funktionen sind gemäß Rolle nutzbar. | Administrator befindet sich im Admin-Bereich. |
| TF-002 | Admin-Navigation für normalen Nutzer prüfen | Prüfen, ob administrative Einstiegspunkte für normale Nutzer nicht angeboten werden. | Berechtigungstest | Hoch | Normales Nutzerkonto ist angemeldet. | Normales Nutzerkonto ohne Adminrechte. | 1. Anwendung öffnen. 2. Als normaler Nutzer anmelden. 3. Sichtbare Navigation und Menüs prüfen. | Admin-Navigation und administrative Aktionen werden nicht angeboten oder sind eindeutig nicht nutzbar. | Normaler Nutzer bleibt in erlaubten Bereichen. |
| TF-003 | Admin-Bereich aus der Anwendung heraus als normaler Nutzer öffnen | Prüfen, ob ein normaler Nutzer keinen Zugriff auf Admin-Inhalte erhält. | Negativtest | Hoch | Normales Nutzerkonto ist angemeldet. | Normaler Nutzer ohne Adminrechte. | 1. Als normaler Nutzer anmelden. 2. Einen fachlich vorgesehenen oder bekannten Einstiegspunkt zum Admin-Bereich aus der Anwendung heraus verwenden, sofern sichtbar. 3. Ergebnis prüfen. | Der Zugriff wird verweigert oder der Nutzer wird in einen erlaubten Bereich geführt. Es werden keine administrativen Inhalte angezeigt. | Normaler Nutzer besitzt keinen Adminzugriff. |
| TF-004 | Administrative Aktion als normaler Nutzer verhindern | Prüfen, ob administrative Funktionen nicht ausgeführt werden können. | Sicherheitsrelevanter Funktionstest | Hoch | Normales Nutzerkonto ist angemeldet; eine administrative Funktion ist fachlich identifiziert. | Normales Nutzerkonto; administrative Aktion auf Verhaltensebene. | 1. Als normaler Nutzer anmelden. 2. Prüfen, ob die administrative Aktion sichtbar oder auslösbar ist. 3. Falls die Aktion angeboten wird, fachlich erlaubte Ausführung im Testkontext prüfen. | Die administrative Aktion wird nicht ausgeführt. Das System zeigt eine kontrollierte Rückmeldung oder verhindert die Aktion bereits vor Ausführung. | Keine administrative Änderung wurde durchgeführt. |
| TF-005 | Keine Offenlegung administrativer Daten bei verweigertem Zugriff | Prüfen, ob abgelehnte Zugriffe keine sensiblen Admininformationen anzeigen. | Sicherheitsrelevanter Funktionstest | Hoch | Normales Nutzerkonto ist angemeldet. | Normaler Nutzer ohne Adminrechte. | 1. Nicht erlaubten Adminzugriff auf Verhaltensebene auslösen. 2. Sichtbare Rückmeldung prüfen. | Die Rückmeldung enthält keine vertraulichen administrativen Daten, keine internen Details und keine unnötigen Hinweise zur Umgehung. | Keine sensiblen Informationen wurden offengelegt. |
| TF-006 | Rollenwechsel von normalem Nutzer zu Administrator fachlich prüfen | Prüfen, ob Zugriff erst nach berechtigter Rolle möglich ist. | Regressionstest | Mittel | Testkonto kann kontrolliert mit Adminrolle versehen oder separates Administratorkonto genutzt werden. | Normales Nutzerkonto und Administratorkonto. | 1. Zugriff als normaler Nutzer prüfen. 2. Als Administrator anmelden oder berechtigtes Konto verwenden. 3. Admin-Bereich öffnen. | Der normale Nutzer erhält keinen Zugriff; der Administrator erhält Zugriff. | Berechtigungsverhalten ist rollenabhängig konsistent. |
| TF-007 | Verständliche Rückmeldung bei verweigertem Zugriff | Prüfen, ob die Ablehnung nutzerverständlich und sicher formuliert ist. | Fehlermeldungstest | Mittel | Normales Nutzerkonto ist angemeldet. | Normaler Nutzer ohne Adminrechte. | 1. Nicht erlaubten Zugriff auf Admin-Funktion auf Verhaltensebene auslösen. 2. Rückmeldung lesen. | Die Rückmeldung ist verständlich, neutral und bestätigt keine sensiblen internen Details. | Nutzer versteht, dass Zugriff nicht erlaubt ist. |

## Review-Checkliste

- Sind berechtigter und unberechtigter Zugriff getrennt geprüft?
- Wird keine Umgehungsmethode beschrieben?
- Werden administrative Daten bei verweigertem Zugriff nicht offengelegt?
- Sind sichtbare Navigation, Funktionsausführung und Rückmeldungen abgedeckt?
- Sind offene Punkte zu Protokollierung und kritischen Funktionen markiert?
- Sind die Tests ausschließlich defensiv und auf Verhaltensebene formuliert?
