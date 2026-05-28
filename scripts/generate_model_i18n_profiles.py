#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SINGLE_MODELS = ROOT / "Modelle" / "einzelmodelle"
PRODUCT_I18N_ROOT = ROOT / "Modelle" / "i18n"

SUPPORTED_PRODUCT_LOCALES = [
    {"code": "de", "name": "Deutsch", "direction": "ltr"},
    {"code": "en", "name": "English", "direction": "ltr"},
    {"code": "es", "name": "Español", "direction": "ltr"},
    {"code": "fr", "name": "Français", "direction": "ltr"},
    {"code": "pt-BR", "name": "Português (Brasil)", "direction": "ltr"},
    {"code": "it", "name": "Italiano", "direction": "ltr"},
    {"code": "nl", "name": "Nederlands", "direction": "ltr"},
    {"code": "pl", "name": "Polski", "direction": "ltr"},
    {"code": "tr", "name": "Türkçe", "direction": "ltr"},
    {"code": "ja", "name": "日本語", "direction": "ltr"},
    {"code": "zh-Hans", "name": "简体中文", "direction": "ltr"},
]

LANGUAGE_TEXT = {
    "de": {
        "heading": "Produktprofil",
        "purpose": "Zweck",
        "when": "Einsatz",
        "outputs": "Typische Ergebnisse",
        "language": "Sprachverhalten",
        "quality": "Qualitätsregeln",
        "usage": "Nutzung in OpenWebUI",
        "purpose_text": "Dieses Produktprofil beschreibt das Modell {name} für die deutschsprachige Standardnutzung und für mehrsprachige OpenWebUI-Workflows.",
        "when_text": "Nutze dieses Modell, wenn die Anfrage zum Fachgebiet {name} passt und lokale Knowledge-Dateien, Beispiele oder Tools ausgewertet werden sollen.",
        "outputs_text": "Antworten, Tabellen, Checklisten, Artefaktentwürfe, Prüfnotizen und Rückfragen werden in der gewählten Nutzersprache formuliert.",
        "language_text": "Deutsch ist der Standard. Wenn die Nutzeranfrage klar eine andere unterstützte Sprache nutzt oder explizit auswählt, antworte in dieser Sprache. Bei unsicherer Locale fällt die Ausgabe auf Deutsch zurück.",
        "quality_text": "Bewahre technische IDs, Dateinamen, Befehle, API-Felder und maschinenlesbare Statuswerte. Übersetze sichtbare Prosa, aber keine kompatibilitätsrelevanten Tokens.",
        "usage_text": "Dieses Profil wird zusammen mit mainprompt.md, fachwissen.md, {example_result} und beispiele/ als Knowledge hochgeladen.",
        "suggestion": "Nutze {name} auf Deutsch und beachte vorhandene Fachbegriffe.",
    },
    "en": {
        "heading": "Product Profile",
        "purpose": "Purpose",
        "when": "When to Use",
        "outputs": "Typical Outputs",
        "language": "Language Behavior",
        "quality": "Quality Rules",
        "usage": "OpenWebUI Usage",
        "purpose_text": "This product profile describes the {name} model for English usage and multilingual OpenWebUI workflows.",
        "when_text": "Use this model when the request fits the {name} domain and local knowledge files, examples, or tools should be applied.",
        "outputs_text": "Responses, tables, checklists, artifact drafts, review notes, and clarification questions are written in the selected user language.",
        "language_text": "German is the project default. If the user clearly uses or selects another supported language, answer in that language. If the locale is uncertain, fall back to German.",
        "quality_text": "Preserve technical IDs, file names, commands, API fields, and machine-readable status values. Translate visible prose, not compatibility-critical tokens.",
        "usage_text": "This profile is uploaded as Knowledge together with mainprompt.md, fachwissen.md, {example_result}, and beispiele/.",
        "suggestion": "Use {name} in English and preserve existing technical terms.",
    },
    "es": {
        "heading": "Perfil del producto",
        "purpose": "Propósito",
        "when": "Uso recomendado",
        "outputs": "Resultados típicos",
        "language": "Comportamiento lingüístico",
        "quality": "Reglas de calidad",
        "usage": "Uso en OpenWebUI",
        "purpose_text": "Este perfil describe el modelo {name} para uso en español y flujos multilingües de OpenWebUI.",
        "when_text": "Usa este modelo cuando la solicitud corresponda al ámbito {name} y deban aplicarse archivos de conocimiento, ejemplos o herramientas locales.",
        "outputs_text": "Respuestas, tablas, listas de verificación, borradores de artefactos, notas de revisión y preguntas se redactan en el idioma elegido por el usuario.",
        "language_text": "El idioma predeterminado del proyecto es alemán. Si el usuario usa o elige claramente otro idioma admitido, responde en ese idioma. Si la configuración regional no es segura, vuelve al alemán.",
        "quality_text": "Conserva identificadores técnicos, nombres de archivo, comandos, campos de API y valores legibles por máquina. Traduce la prosa visible, no los tokens críticos de compatibilidad.",
        "usage_text": "Este perfil se carga como Knowledge junto con mainprompt.md, fachwissen.md, {example_result} y beispiele/.",
        "suggestion": "Usa {name} en español y conserva la terminología técnica existente.",
    },
    "fr": {
        "heading": "Profil produit",
        "purpose": "Objectif",
        "when": "Utilisation",
        "outputs": "Sorties typiques",
        "language": "Comportement linguistique",
        "quality": "Règles de qualité",
        "usage": "Utilisation dans OpenWebUI",
        "purpose_text": "Ce profil décrit le modèle {name} pour l'usage en français et les workflows OpenWebUI multilingues.",
        "when_text": "Utilise ce modèle lorsque la demande relève du domaine {name} et que les fichiers de connaissance, exemples ou outils locaux doivent être appliqués.",
        "outputs_text": "Les réponses, tableaux, listes de contrôle, brouillons d'artefacts, notes de revue et questions sont rédigés dans la langue choisie par l'utilisateur.",
        "language_text": "L'allemand est la langue par défaut du projet. Si l'utilisateur utilise ou choisit clairement une autre langue prise en charge, réponds dans cette langue. Si la locale est incertaine, reviens à l'allemand.",
        "quality_text": "Préserve les identifiants techniques, noms de fichiers, commandes, champs d'API et valeurs lisibles par machine. Traduis la prose visible, pas les tokens critiques pour la compatibilité.",
        "usage_text": "Ce profil est téléversé comme Knowledge avec mainprompt.md, fachwissen.md, {example_result} et beispiele/.",
        "suggestion": "Utilise {name} en français et conserve les termes techniques existants.",
    },
    "pt-BR": {
        "heading": "Perfil do produto",
        "purpose": "Objetivo",
        "when": "Quando usar",
        "outputs": "Resultados típicos",
        "language": "Comportamento de idioma",
        "quality": "Regras de qualidade",
        "usage": "Uso no OpenWebUI",
        "purpose_text": "Este perfil descreve o modelo {name} para uso em português do Brasil e fluxos multilíngues no OpenWebUI.",
        "when_text": "Use este modelo quando a solicitação corresponder ao domínio {name} e arquivos de conhecimento, exemplos ou ferramentas locais precisarem ser aplicados.",
        "outputs_text": "Respostas, tabelas, listas de verificação, rascunhos de artefatos, notas de revisão e perguntas são escritos no idioma escolhido pelo usuário.",
        "language_text": "Alemão é o padrão do projeto. Se o usuário usar ou selecionar claramente outro idioma compatível, responda nesse idioma. Se a localidade for incerta, volte para alemão.",
        "quality_text": "Preserve IDs técnicos, nomes de arquivos, comandos, campos de API e valores legíveis por máquina. Traduza a prosa visível, não tokens críticos de compatibilidade.",
        "usage_text": "Este perfil é enviado como Knowledge junto com mainprompt.md, fachwissen.md, {example_result} e beispiele/.",
        "suggestion": "Use {name} em português do Brasil e preserve os termos técnicos existentes.",
    },
    "it": {
        "heading": "Profilo prodotto",
        "purpose": "Scopo",
        "when": "Quando usarlo",
        "outputs": "Output tipici",
        "language": "Comportamento linguistico",
        "quality": "Regole di qualità",
        "usage": "Uso in OpenWebUI",
        "purpose_text": "Questo profilo descrive il modello {name} per l'uso in italiano e per workflow OpenWebUI multilingue.",
        "when_text": "Usa questo modello quando la richiesta rientra nell'ambito {name} e devono essere applicati file di conoscenza, esempi o strumenti locali.",
        "outputs_text": "Risposte, tabelle, checklist, bozze di artefatti, note di revisione e domande sono scritte nella lingua scelta dall'utente.",
        "language_text": "Il tedesco è la lingua predefinita del progetto. Se l'utente usa o seleziona chiaramente un'altra lingua supportata, rispondi in quella lingua. Se la locale è incerta, usa il tedesco.",
        "quality_text": "Mantieni ID tecnici, nomi di file, comandi, campi API e valori leggibili dalla macchina. Traduci la prosa visibile, non i token critici per la compatibilità.",
        "usage_text": "Questo profilo viene caricato come Knowledge insieme a mainprompt.md, fachwissen.md, {example_result} e beispiele/.",
        "suggestion": "Usa {name} in italiano e conserva la terminologia tecnica esistente.",
    },
    "nl": {
        "heading": "Productprofiel",
        "purpose": "Doel",
        "when": "Wanneer gebruiken",
        "outputs": "Typische uitvoer",
        "language": "Taalgedrag",
        "quality": "Kwaliteitsregels",
        "usage": "Gebruik in OpenWebUI",
        "purpose_text": "Dit profiel beschrijft het model {name} voor Nederlands gebruik en meertalige OpenWebUI-workflows.",
        "when_text": "Gebruik dit model wanneer het verzoek past bij het domein {name} en lokale kennisbestanden, voorbeelden of tools moeten worden toegepast.",
        "outputs_text": "Antwoorden, tabellen, checklists, artefactconcepten, reviewnotities en vragen worden geschreven in de gekozen gebruikerstaal.",
        "language_text": "Duits is de standaardtaal van het project. Als de gebruiker duidelijk een andere ondersteunde taal gebruikt of kiest, antwoord dan in die taal. Bij onzekere locale val je terug op Duits.",
        "quality_text": "Behoud technische ID's, bestandsnamen, commando's, API-velden en machineleesbare waarden. Vertaal zichtbare tekst, niet compatibiliteitskritische tokens.",
        "usage_text": "Dit profiel wordt als Knowledge geüpload samen met mainprompt.md, fachwissen.md, {example_result} en beispiele/.",
        "suggestion": "Gebruik {name} in het Nederlands en behoud bestaande technische termen.",
    },
    "pl": {
        "heading": "Profil produktu",
        "purpose": "Cel",
        "when": "Kiedy używać",
        "outputs": "Typowe wyniki",
        "language": "Zachowanie językowe",
        "quality": "Reguły jakości",
        "usage": "Użycie w OpenWebUI",
        "purpose_text": "Ten profil opisuje model {name} do użycia po polsku i w wielojęzycznych przepływach OpenWebUI.",
        "when_text": "Użyj tego modelu, gdy żądanie pasuje do obszaru {name} i należy zastosować lokalne pliki wiedzy, przykłady lub narzędzia.",
        "outputs_text": "Odpowiedzi, tabele, listy kontrolne, szkice artefaktów, notatki z przeglądu i pytania są tworzone w języku wybranym przez użytkownika.",
        "language_text": "Niemiecki jest językiem domyślnym projektu. Jeśli użytkownik wyraźnie używa lub wybiera inny obsługiwany język, odpowiadaj w tym języku. Przy niepewnej locale wróć do niemieckiego.",
        "quality_text": "Zachowuj identyfikatory techniczne, nazwy plików, polecenia, pola API i wartości czytelne maszynowo. Tłumacz widoczną prozę, nie tokeny krytyczne dla zgodności.",
        "usage_text": "Ten profil jest przesyłany jako Knowledge razem z mainprompt.md, fachwissen.md, {example_result} i beispiele/.",
        "suggestion": "Użyj {name} po polsku i zachowaj istniejące terminy techniczne.",
    },
    "tr": {
        "heading": "Ürün profili",
        "purpose": "Amaç",
        "when": "Ne zaman kullanılır",
        "outputs": "Tipik çıktılar",
        "language": "Dil davranışı",
        "quality": "Kalite kuralları",
        "usage": "OpenWebUI kullanımı",
        "purpose_text": "Bu profil, {name} modelini Türkçe kullanım ve çok dilli OpenWebUI iş akışları için açıklar.",
        "when_text": "İstek {name} alanına uyduğunda ve yerel bilgi dosyaları, örnekler veya araçlar uygulanması gerektiğinde bu modeli kullan.",
        "outputs_text": "Yanıtlar, tablolar, kontrol listeleri, artefakt taslakları, inceleme notları ve sorular kullanıcının seçtiği dilde yazılır.",
        "language_text": "Projenin varsayılan dili Almancadır. Kullanıcı açıkça desteklenen başka bir dili kullanır veya seçerse o dilde yanıt ver. Locale belirsizse Almancaya dön.",
        "quality_text": "Teknik ID'leri, dosya adlarını, komutları, API alanlarını ve makine tarafından okunabilir değerleri koru. Görünür metni çevir, uyumluluk açısından kritik tokenları çevirme.",
        "usage_text": "Bu profil mainprompt.md, fachwissen.md, {example_result} ve beispiele/ ile birlikte Knowledge olarak yüklenir.",
        "suggestion": "{name} modelini Türkçe kullan ve mevcut teknik terimleri koru.",
    },
    "ja": {
        "heading": "製品プロファイル",
        "purpose": "目的",
        "when": "利用場面",
        "outputs": "主な出力",
        "language": "言語動作",
        "quality": "品質ルール",
        "usage": "OpenWebUI での利用",
        "purpose_text": "このプロファイルは、日本語利用と多言語 OpenWebUI ワークフロー向けの {name} モデルを説明します。",
        "when_text": "依頼が {name} の領域に合い、ローカルの Knowledge ファイル、例、ツールを適用する必要がある場合に使います。",
        "outputs_text": "回答、表、チェックリスト、成果物ドラフト、レビュー notes、確認質問は、ユーザーが選んだ言語で作成します。",
        "language_text": "プロジェクトの既定言語はドイツ語です。ユーザーが対応言語を明確に使う、または選択した場合はその言語で回答します。Locale が不確かな場合はドイツ語に戻します。",
        "quality_text": "技術 ID、ファイル名、コマンド、API フィールド、機械可読値は保持します。表示される文章は翻訳し、互換性に関わる token は翻訳しません。",
        "usage_text": "このプロファイルは mainprompt.md、fachwissen.md、{example_result}、beispiele/ と一緒に Knowledge としてアップロードされます。",
        "suggestion": "{name} を日本語で使い、既存の技術用語を保持してください。",
    },
    "zh-Hans": {
        "heading": "产品配置文件",
        "purpose": "用途",
        "when": "适用场景",
        "outputs": "典型输出",
        "language": "语言行为",
        "quality": "质量规则",
        "usage": "OpenWebUI 用法",
        "purpose_text": "此配置文件说明 {name} 模型在简体中文和多语言 OpenWebUI 工作流中的用法。",
        "when_text": "当请求符合 {name} 领域，并且需要使用本地 Knowledge 文件、示例或工具时，使用此模型。",
        "outputs_text": "回答、表格、检查清单、产物草稿、审查说明和澄清问题都会使用用户选择的语言。",
        "language_text": "项目默认语言是德语。如果用户明确使用或选择其他受支持语言，则使用该语言回答。如果 locale 不明确，则回退到德语。",
        "quality_text": "保留技术 ID、文件名、命令、API 字段和机器可读状态值。翻译可见文本，不翻译影响兼容性的 token。",
        "usage_text": "此配置文件会与 mainprompt.md、fachwissen.md、{example_result} 和 beispiele/ 一起作为 Knowledge 上传。",
        "suggestion": "用简体中文使用 {name}，并保留现有技术术语。",
    },
}

MODEL_TITLES = {
    "allgemein": {
        "de": "Allgemein",
        "en": "General",
        "es": "General",
        "fr": "Général",
        "pt-BR": "Geral",
        "it": "Generale",
        "nl": "Algemeen",
        "pl": "Ogólne",
        "tr": "Genel",
        "ja": "汎用",
        "zh-Hans": "通用",
    },
    "anforderungsanalyse-lastenheft": {
        "de": "Anforderungsanalyse und Lastenheft",
        "en": "Requirements Analysis and Specification",
        "es": "Análisis de requisitos y especificación",
        "fr": "Analyse des exigences et cahier des charges",
        "pt-BR": "Análise de requisitos e especificação",
        "it": "Analisi dei requisiti e specifica",
        "nl": "Requirementsanalyse en specificatie",
        "pl": "Analiza wymagań i specyfikacja",
        "tr": "Gereksinim analizi ve şartname",
        "ja": "要件分析と仕様書",
        "zh-Hans": "需求分析与规格说明",
    },
    "api-schnittstellenentwurf": {
        "de": "API- und Schnittstellenentwurf",
        "en": "API and Interface Design",
        "es": "Diseño de API e interfaces",
        "fr": "Conception d'API et d'interfaces",
        "pt-BR": "Design de APIs e interfaces",
        "it": "Progettazione di API e interfacce",
        "nl": "API- en interfaceontwerp",
        "pl": "Projektowanie API i interfejsów",
        "tr": "API ve arayüz tasarımı",
        "ja": "API とインターフェース設計",
        "zh-Hans": "API 与接口设计",
    },
    "code-dokumentation": {
        "de": "Code-Dokumentation",
        "en": "Code Documentation",
        "es": "Documentación de código",
        "fr": "Documentation du code",
        "pt-BR": "Documentação de código",
        "it": "Documentazione del codice",
        "nl": "Codedocumentatie",
        "pl": "Dokumentacja kodu",
        "tr": "Kod dokümantasyonu",
        "ja": "コードドキュメント",
        "zh-Hans": "代码文档",
    },
    "code-review": {
        "de": "Code-Review",
        "en": "Code Review",
        "es": "Revisión de código",
        "fr": "Revue de code",
        "pt-BR": "Revisão de código",
        "it": "Revisione del codice",
        "nl": "Codebeoordeling",
        "pl": "Przegląd kodu",
        "tr": "Kod incelemesi",
        "ja": "コードレビュー",
        "zh-Hans": "代码审查",
    },
    "codeanalyse": {
        "de": "Codeanalyse",
        "en": "Code Analysis",
        "es": "Análisis de código",
        "fr": "Analyse de code",
        "pt-BR": "Análise de código",
        "it": "Analisi del codice",
        "nl": "Codeanalyse",
        "pl": "Analiza kodu",
        "tr": "Kod analizi",
        "ja": "コード分析",
        "zh-Hans": "代码分析",
    },
    "codegenerierung": {
        "de": "Codegenerierung",
        "en": "Code Generation",
        "es": "Generación de código",
        "fr": "Génération de code",
        "pt-BR": "Geração de código",
        "it": "Generazione di codice",
        "nl": "Codegeneratie",
        "pl": "Generowanie kodu",
        "tr": "Kod üretimi",
        "ja": "コード生成",
        "zh-Hans": "代码生成",
    },
    "compliance-richtlinienprüfung": {
        "de": "Compliance- und Richtlinienprüfung",
        "en": "Compliance and Policy Review",
        "es": "Revisión de cumplimiento y políticas",
        "fr": "Contrôle de conformité et de politiques",
        "pt-BR": "Revisão de conformidade e políticas",
        "it": "Verifica di conformità e policy",
        "nl": "Compliance- en beleidscontrole",
        "pl": "Przegląd zgodności i polityk",
        "tr": "Uyumluluk ve politika incelemesi",
        "ja": "コンプライアンスとポリシー確認",
        "zh-Hans": "合规与政策审查",
    },
    "debugging-fehleranalyse": {
        "de": "Debugging und Fehleranalyse",
        "en": "Debugging and Error Analysis",
        "es": "Depuración y análisis de errores",
        "fr": "Débogage et analyse des erreurs",
        "pt-BR": "Depuração e análise de erros",
        "it": "Debugging e analisi degli errori",
        "nl": "Debugging en foutanalyse",
        "pl": "Debugowanie i analiza błędów",
        "tr": "Hata ayıklama ve hata analizi",
        "ja": "デバッグとエラー分析",
        "zh-Hans": "调试与错误分析",
    },
    "dokumentenanalyse": {
        "de": "Dokumentenanalyse",
        "en": "Document Analysis",
        "es": "Análisis de documentos",
        "fr": "Analyse de documents",
        "pt-BR": "Análise de documentos",
        "it": "Analisi dei documenti",
        "nl": "Documentanalyse",
        "pl": "Analiza dokumentów",
        "tr": "Belge analizi",
        "ja": "文書分析",
        "zh-Hans": "文档分析",
    },
    "dokumentengenerierung": {
        "de": "Dokumentengenerierung",
        "en": "Document Generation",
        "es": "Generación de documentos",
        "fr": "Génération de documents",
        "pt-BR": "Geração de documentos",
        "it": "Generazione di documenti",
        "nl": "Documentgeneratie",
        "pl": "Generowanie dokumentów",
        "tr": "Belge oluşturma",
        "ja": "文書生成",
        "zh-Hans": "文档生成",
    },
    "dokumentenvergleich": {
        "de": "Dokumentenvergleich",
        "en": "Document Comparison",
        "es": "Comparación de documentos",
        "fr": "Comparaison de documents",
        "pt-BR": "Comparação de documentos",
        "it": "Confronto di documenti",
        "nl": "Documentvergelijking",
        "pl": "Porównanie dokumentów",
        "tr": "Belge karşılaştırma",
        "ja": "文書比較",
        "zh-Hans": "文档比较",
    },
    "dokumentenzusammenfassung": {
        "de": "Dokumentenzusammenfassung",
        "en": "Document Summarization",
        "es": "Resumen de documentos",
        "fr": "Synthèse de documents",
        "pt-BR": "Resumo de documentos",
        "it": "Sintesi di documenti",
        "nl": "Documentsamenvatting",
        "pl": "Streszczanie dokumentów",
        "tr": "Belge özetleme",
        "ja": "文書要約",
        "zh-Hans": "文档摘要",
    },
    "email-kommunikationsassistenz": {
        "de": "E-Mail- und Kommunikationsassistenz",
        "en": "Email and Communication Assistant",
        "es": "Asistente de correo y comunicación",
        "fr": "Assistant e-mail et communication",
        "pt-BR": "Assistente de e-mail e comunicação",
        "it": "Assistente email e comunicazione",
        "nl": "E-mail- en communicatieassistent",
        "pl": "Asystent poczty i komunikacji",
        "tr": "E-posta ve iletişim asistanı",
        "ja": "メールとコミュニケーション支援",
        "zh-Hans": "电子邮件与沟通助手",
    },
    "informationsextraktion": {
        "de": "Informationsextraktion",
        "en": "Information Extraction",
        "es": "Extracción de información",
        "fr": "Extraction d'informations",
        "pt-BR": "Extração de informações",
        "it": "Estrazione di informazioni",
        "nl": "Informatie-extractie",
        "pl": "Ekstrakcja informacji",
        "tr": "Bilgi çıkarımı",
        "ja": "情報抽出",
        "zh-Hans": "信息提取",
    },
    "internetwissen": {
        "de": "Internetwissen",
        "en": "Internet Knowledge",
        "es": "Conocimiento de Internet",
        "fr": "Connaissances Internet",
        "pt-BR": "Conhecimento da internet",
        "it": "Conoscenza internet",
        "nl": "Internetkennis",
        "pl": "Wiedza internetowa",
        "tr": "İnternet bilgisi",
        "ja": "インターネット知識",
        "zh-Hans": "互联网知识",
    },
    "it-helpdesk-diagnose": {
        "de": "IT-Helpdesk-Diagnose",
        "en": "IT Helpdesk Diagnosis",
        "es": "Diagnóstico de mesa de ayuda de TI",
        "fr": "Diagnostic support informatique",
        "pt-BR": "Diagnóstico de helpdesk de TI",
        "it": "Diagnosi helpdesk IT",
        "nl": "IT-helpdeskdiagnose",
        "pl": "Diagnoza helpdesku IT",
        "tr": "BT yardım masası tanısı",
        "ja": "IT ヘルプデスク診断",
        "zh-Hans": "IT 服务台诊断",
    },
    "json-csv-log-analyse": {
        "de": "JSON-, CSV- und Log-Analyse",
        "en": "JSON, CSV and Log Analysis",
        "es": "Análisis de JSON, CSV y logs",
        "fr": "Analyse JSON, CSV et logs",
        "pt-BR": "Análise de JSON, CSV e logs",
        "it": "Analisi di JSON, CSV e log",
        "nl": "JSON-, CSV- en loganalyse",
        "pl": "Analiza JSON, CSV i logów",
        "tr": "JSON, CSV ve log analizi",
        "ja": "JSON・CSV・ログ分析",
        "zh-Hans": "JSON、CSV 与日志分析",
    },
    "meeting-protokoll-auswertung": {
        "de": "Meeting-Protokoll-Auswertung",
        "en": "Meeting Minutes Analysis",
        "es": "Análisis de actas de reunión",
        "fr": "Analyse de comptes rendus de réunion",
        "pt-BR": "Análise de atas de reunião",
        "it": "Analisi dei verbali di riunione",
        "nl": "Analyse van vergaderverslagen",
        "pl": "Analiza protokołów spotkań",
        "tr": "Toplantı tutanağı analizi",
        "ja": "会議議事録分析",
        "zh-Hans": "会议纪要分析",
    },
    "mistral-vision-workbench": {
        "de": "Mistral Vision Workbench",
        "en": "Mistral Vision Workbench",
        "es": "Mistral Vision Workbench",
        "fr": "Mistral Vision Workbench",
        "pt-BR": "Mistral Vision Workbench",
        "it": "Mistral Vision Workbench",
        "nl": "Mistral Vision Workbench",
        "pl": "Mistral Vision Workbench",
        "tr": "Mistral Vision Workbench",
        "ja": "Mistral Vision Workbench",
        "zh-Hans": "Mistral Vision Workbench",
    },
    "n8n-workflow-architect": {
        "de": "n8n Workflow Architect",
        "en": "n8n Workflow Architect",
        "es": "Arquitecto de workflows n8n",
        "fr": "Architecte de workflows n8n",
        "pt-BR": "Arquiteto de workflows n8n",
        "it": "Architetto di workflow n8n",
        "nl": "n8n-workflowarchitect",
        "pl": "Architekt workflow n8n",
        "tr": "n8n iş akışı mimarı",
        "ja": "n8n ワークフローアーキテクト",
        "zh-Hans": "n8n 工作流架构师",
    },
    "offline-workbench-agent": {
        "de": "Offline Workbench Agent",
        "en": "Offline Workbench Agent",
        "es": "Agente de Workbench sin conexión",
        "fr": "Agent Workbench hors ligne",
        "pt-BR": "Agente Workbench offline",
        "it": "Agente Workbench offline",
        "nl": "Offline Workbench Agent",
        "pl": "Agent Offline Workbench",
        "tr": "Çevrimdışı Workbench ajanı",
        "ja": "オフライン Workbench エージェント",
        "zh-Hans": "离线 Workbench 代理",
    },
    "openwebui-model-builder": {
        "de": "OpenWebUI Model Builder",
        "en": "OpenWebUI Model Builder",
        "es": "Constructor de modelos OpenWebUI",
        "fr": "Générateur de modèles OpenWebUI",
        "pt-BR": "Construtor de modelos OpenWebUI",
        "it": "Generatore di modelli OpenWebUI",
        "nl": "OpenWebUI-modelbouwer",
        "pl": "Kreator modeli OpenWebUI",
        "tr": "OpenWebUI model oluşturucu",
        "ja": "OpenWebUI モデルビルダー",
        "zh-Hans": "OpenWebUI 模型构建器",
    },
    "promptforge": {
        "de": "PromptForge",
        "en": "PromptForge",
        "es": "PromptForge",
        "fr": "PromptForge",
        "pt-BR": "PromptForge",
        "it": "PromptForge",
        "nl": "PromptForge",
        "pl": "PromptForge",
        "tr": "PromptForge",
        "ja": "PromptForge",
        "zh-Hans": "PromptForge",
    },
    "prozess-workflow-dokumentation": {
        "de": "Prozess- und Workflow-Dokumentation",
        "en": "Process and Workflow Documentation",
        "es": "Documentación de procesos y workflows",
        "fr": "Documentation de processus et workflows",
        "pt-BR": "Documentação de processos e workflows",
        "it": "Documentazione di processi e workflow",
        "nl": "Proces- en workflowdocumentatie",
        "pl": "Dokumentacja procesów i workflow",
        "tr": "Süreç ve iş akışı dokümantasyonu",
        "ja": "プロセスとワークフロードキュメント",
        "zh-Hans": "流程与工作流文档",
    },
    "präsentationserstellung": {
        "de": "Präsentationserstellung",
        "en": "Presentation Creation",
        "es": "Creación de presentaciones",
        "fr": "Création de présentations",
        "pt-BR": "Criação de apresentações",
        "it": "Creazione di presentazioni",
        "nl": "Presentatiecreatie",
        "pl": "Tworzenie prezentacji",
        "tr": "Sunum oluşturma",
        "ja": "プレゼンテーション作成",
        "zh-Hans": "演示文稿创建",
    },
    "refactoring-unterstützung": {
        "de": "Refactoring-Unterstützung",
        "en": "Refactoring Support",
        "es": "Soporte de refactorización",
        "fr": "Assistance au refactoring",
        "pt-BR": "Suporte a refatoração",
        "it": "Supporto al refactoring",
        "nl": "Refactoringondersteuning",
        "pl": "Wsparcie refaktoryzacji",
        "tr": "Refactoring desteği",
        "ja": "リファクタリング支援",
        "zh-Hans": "重构支持",
    },
    "report-dashboard-vorbereitung": {
        "de": "Report- und Dashboard-Vorbereitung",
        "en": "Report and Dashboard Preparation",
        "es": "Preparación de informes y dashboards",
        "fr": "Préparation de rapports et tableaux de bord",
        "pt-BR": "Preparação de relatórios e dashboards",
        "it": "Preparazione di report e dashboard",
        "nl": "Rapport- en dashboardvoorbereiding",
        "pl": "Przygotowanie raportów i dashboardów",
        "tr": "Rapor ve dashboard hazırlığı",
        "ja": "レポートとダッシュボード準備",
        "zh-Hans": "报告与仪表板准备",
    },
    "support-ticket-vorbereitung": {
        "de": "Support-Ticket-Vorbereitung",
        "en": "Support Ticket Preparation",
        "es": "Preparación de tickets de soporte",
        "fr": "Préparation de tickets support",
        "pt-BR": "Preparação de tickets de suporte",
        "it": "Preparazione di ticket di supporto",
        "nl": "Supportticketvoorbereiding",
        "pl": "Przygotowanie zgłoszeń supportu",
        "tr": "Destek talebi hazırlığı",
        "ja": "サポートチケット準備",
        "zh-Hans": "支持工单准备",
    },
    "tabellen-csv-datenanalyse": {
        "de": "Tabellen- und CSV-Datenanalyse",
        "en": "Table and CSV Data Analysis",
        "es": "Análisis de tablas y CSV",
        "fr": "Analyse de tableaux et CSV",
        "pt-BR": "Análise de tabelas e CSV",
        "it": "Analisi di tabelle e CSV",
        "nl": "Tabel- en CSV-dataanalyse",
        "pl": "Analiza tabel i CSV",
        "tr": "Tablo ve CSV veri analizi",
        "ja": "表と CSV データ分析",
        "zh-Hans": "表格与 CSV 数据分析",
    },
    "testfall-generierung": {
        "de": "Testfall-Generierung",
        "en": "Test Case Generation",
        "es": "Generación de casos de prueba",
        "fr": "Génération de cas de test",
        "pt-BR": "Geração de casos de teste",
        "it": "Generazione di casi di test",
        "nl": "Testcasegeneratie",
        "pl": "Generowanie przypadków testowych",
        "tr": "Test senaryosu üretimi",
        "ja": "テストケース生成",
        "zh-Hans": "测试用例生成",
    },
    "übersetzung-lokalisierung": {
        "de": "Übersetzung und Lokalisierung",
        "en": "Translation and Localization",
        "es": "Traducción y localización",
        "fr": "Traduction et localisation",
        "pt-BR": "Tradução e localização",
        "it": "Traduzione e localizzazione",
        "nl": "Vertaling en lokalisatie",
        "pl": "Tłumaczenie i lokalizacja",
        "tr": "Çeviri ve yerelleştirme",
        "ja": "翻訳とローカライズ",
        "zh-Hans": "翻译与本地化",
    },
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def product_title(model_id: str, locale: str, fallback_name: str) -> str:
    return MODEL_TITLES.get(model_id, {}).get(locale) or MODEL_TITLES.get(model_id, {}).get("de") or fallback_name


def example_result_file_for_model(model_id: str) -> str:
    return "beispielergebnis.html" if model_id == "präsentationserstellung" else "beispielergebnis.md"


def localized_profile(model_id: str, locale: str, fallback_name: str) -> dict[str, str]:
    texts = LANGUAGE_TEXT[locale]
    title = product_title(model_id, locale, fallback_name)
    return {
        "name": title,
        "description": texts["purpose_text"].format(name=title),
        "suggestion": texts["suggestion"].format(name=title),
    }


def profile_markdown(model_id: str, locale: str, fallback_name: str) -> str:
    texts = LANGUAGE_TEXT[locale]
    title = product_title(model_id, locale, fallback_name)
    example_result = example_result_file_for_model(model_id)
    return f"""# {title}

## {texts["heading"]}

- Locale: `{locale}`
- Modell-ID: `{model_id}`
- Fallback: `de`

## {texts["purpose"]}

{texts["purpose_text"].format(name=title)}

## {texts["when"]}

{texts["when_text"].format(name=title)}

## {texts["outputs"]}

{texts["outputs_text"]}

## {texts["language"]}

{texts["language_text"]}

## {texts["quality"]}

{texts["quality_text"]}

## {texts["usage"]}

{texts["usage_text"].format(example_result=example_result)}
"""


def load_model_name(path: Path) -> str:
    data = read_json(path)
    if isinstance(data, list) and data and isinstance(data[0], dict):
        return str(data[0].get("name") or path.parent.name)
    return path.parent.name


def update_model_meta(model_path: Path, profiles: dict[str, dict[str, str]]) -> None:
    data = read_json(model_path)
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        raise ValueError(f"{model_path} is not an OpenWebUI model array")
    model = data[0]
    meta = model.setdefault("meta", {})
    if not isinstance(meta, dict):
        raise ValueError(f"{model_path} meta is not an object")
    locales = [item["code"] for item in SUPPORTED_PRODUCT_LOCALES]
    meta["defaultLocale"] = "de"
    meta["fallbackLocale"] = "en"
    meta["supportedLocales"] = locales
    meta["productLocaleFiles"] = [f"i18n/{locale}.md" for locale in locales]
    meta["productI18n"] = {
        locale: {
            "name": profile["name"],
            "description": profile["description"],
            "suggestion": profile["suggestion"],
            "profile": f"i18n/{locale}.md",
        }
        for locale, profile in profiles.items()
    }
    write_json(model_path, data)


def main() -> int:
    model_entries: list[dict[str, Any]] = []
    locale_codes = [item["code"] for item in SUPPORTED_PRODUCT_LOCALES]
    for model_path in sorted(SINGLE_MODELS.glob("*/model.json")):
        model_id = model_path.parent.name
        fallback_name = load_model_name(model_path)
        profiles = {locale: localized_profile(model_id, locale, fallback_name) for locale in locale_codes}
        i18n_dir = model_path.parent / "i18n"
        for locale in locale_codes:
            write_text(i18n_dir / f"{locale}.md", profile_markdown(model_id, locale, fallback_name))
        write_json(
            i18n_dir / "manifest.json",
            {
                "schema": "openwebui-workbench-model-i18n/v1",
                "model_id": model_id,
                "default_locale": "de",
                "fallback_locale": "en",
                "supported_locales": locale_codes,
                "files": {locale: f"{locale}.md" for locale in locale_codes},
                "names": {locale: profiles[locale]["name"] for locale in locale_codes},
            },
        )
        update_model_meta(model_path, profiles)
        model_entries.append(
            {
                "id": model_id,
                "default_locale": "de",
                "fallback_locale": "en",
                "supported_locales": locale_codes,
                "names": {locale: profiles[locale]["name"] for locale in locale_codes},
                "files": {locale: f"Modelle/einzelmodelle/{model_id}/i18n/{locale}.md" for locale in locale_codes},
            }
        )

    write_json(
        PRODUCT_I18N_ROOT / "product-locales.json",
        {
            "schema": "openwebui-workbench-product-i18n/v1",
            "default_locale": "de",
            "fallback_locale": "en",
            "locales": SUPPORTED_PRODUCT_LOCALES,
            "supported_locales": SUPPORTED_PRODUCT_LOCALES,
            "models": model_entries,
        },
    )
    print(f"Generated product i18n profiles for {len(model_entries)} models and {len(locale_codes)} locales.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
