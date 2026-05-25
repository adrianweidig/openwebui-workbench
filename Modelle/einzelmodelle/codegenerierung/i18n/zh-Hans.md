# 代码生成

## 产品配置文件

- Locale: `zh-Hans`
- Modell-ID: `codegenerierung`
- Fallback: `de`

## 用途

此配置文件说明 代码生成 模型在简体中文和多语言 OpenWebUI 工作流中的用法。

## 适用场景

当请求符合 代码生成 领域，并且需要使用本地 Knowledge 文件、示例或工具时，使用此模型。

## 典型输出

回答、表格、检查清单、产物草稿、审查说明和澄清问题都会使用用户选择的语言。

## 语言行为

项目默认语言是德语。如果用户明确使用或选择其他受支持语言，则使用该语言回答。如果 locale 不明确，则回退到德语。

## 质量规则

保留技术 ID、文件名、命令、API 字段和机器可读状态值。翻译可见文本，不翻译影响兼容性的 token。

## OpenWebUI 用法

此配置文件会与 mainprompt.md、fachwissen.md、beispielergebnis.md 和 beispiele/ 一起作为 Knowledge 上传。
