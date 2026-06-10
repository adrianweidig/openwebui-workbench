# Beispielausgabe: Migration `wpf_login_customer_save.script`

## 1. Klassifizierung

| Feld | Entscheidung |
|---|---|
| Oberfläche | WPF |
| Zielprojekt | `Product.UiTests.Uia3` |
| Migrationsklasse | Klasse A: Standard-WPF-Workflow |
| VisualTrack | nein |
| Primäre Selektoren | AutomationId |
| Migration Wave | Welle 2 |

## 2. Business Intent

Der Eggplant-Test prüft nicht „Klicks“, sondern diesen fachlichen Ablauf:

1. Anwendung starten.
2. Benutzer anmelden.
3. Kunden suchen.
4. Kundennamen ändern.
5. Speichern und Erfolgsmeldung prüfen.

## 3. Zielartefakte

| Datei | Zweck |
|---|---|
| `Product.UiTests.Shared/Screens/LoginScreen.cs` | Login-Screen-Object |
| `Product.UiTests.Shared/Screens/CustomerScreen.cs` | Kundensuche und Speichern |
| `Product.UiTests.Uia3/Wpf/CustomerWorkflowTests.cs` | migrierter NUnit-Test |

## 4. Offene Prüfpunkte

- Existieren `Login.UserNameField`, `Login.PasswordField`, `Login.SubmitButton`?
- Ist `Customer.SaveSuccessToast` im UIA-Baum sichtbar?
- Soll das Passwort aus einem sicheren Testsecret kommen oder über dedizierten Testmodus entfallen?

## 5. Akzeptanz

- Keine Koordinatenklicks.
- Keine Fullscreen-Bildassertion.
- Fehlschlag erzeugt Screenshot, UIA-Dump und metadata.json.
