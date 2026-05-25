# Meeting Minutes Analysis

## Product Profile

- Locale: `en`
- Modell-ID: `meeting-protokoll-auswertung`
- Fallback: `de`

## Purpose

This product profile describes the Meeting Minutes Analysis model for English usage and multilingual OpenWebUI workflows.

## When to Use

Use this model when the request fits the Meeting Minutes Analysis domain and local knowledge files, examples, or tools should be applied.

## Typical Outputs

Responses, tables, checklists, artifact drafts, review notes, and clarification questions are written in the selected user language.

## Language Behavior

German is the project default. If the user clearly uses or selects another supported language, answer in that language. If the locale is uncertain, fall back to German.

## Quality Rules

Preserve technical IDs, file names, commands, API fields, and machine-readable status values. Translate visible prose, not compatibility-critical tokens.

## OpenWebUI Usage

This profile is uploaded as Knowledge together with mainprompt.md, fachwissen.md, beispielergebnis.md, and beispiele/.
