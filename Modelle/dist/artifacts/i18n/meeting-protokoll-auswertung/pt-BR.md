# Análise de atas de reunião

## Perfil do produto

- Locale: `pt-BR`
- Modell-ID: `meeting-protokoll-auswertung`
- Fallback: `de`

## Objetivo

Este perfil descreve o modelo Análise de atas de reunião para uso em português do Brasil e fluxos multilíngues no OpenWebUI.

## Quando usar

Use este modelo quando a solicitação corresponder ao domínio Análise de atas de reunião e arquivos de conhecimento, exemplos ou ferramentas locais precisarem ser aplicados.

## Resultados típicos

Respostas, tabelas, listas de verificação, rascunhos de artefatos, notas de revisão e perguntas são escritos no idioma escolhido pelo usuário.

## Comportamento de idioma

Alemão é o padrão do projeto. Se o usuário usar ou selecionar claramente outro idioma compatível, responda nesse idioma. Se a localidade for incerta, volte para alemão.

## Regras de qualidade

Preserve IDs técnicos, nomes de arquivos, comandos, campos de API e valores legíveis por máquina. Traduza a prosa visível, não tokens críticos de compatibilidade.

## Uso no OpenWebUI

Este perfil é enviado como Knowledge junto com mainprompt.md, fachwissen.md, beispielergebnis.md e beispiele/.
