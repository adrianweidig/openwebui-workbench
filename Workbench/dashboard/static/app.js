const state = {
  status: null,
  models: [],
  resources: [],
  locale: "de",
  messages: {},
  fallbackMessages: {},
  selectedModel: null,
  selectedFile: "systemprompt.md",
  selectedResource: null,
  modelDirty: false,
  resourceDirty: false,
  modelView: "split",
  resourceView: "split",
};

const el = (id) => document.getElementById(id);
const DEFAULT_LOCALE = "de";
const SUPPORTED_LOCALES = ["de", "en"];
const SUPPORTED_PANELS = new Set(["models", "resources", "actions", "assets"]);
const queryParams = new URLSearchParams(window.location.search);

function normalizeLocale(value) {
  const language = String(value || "").trim().replace("_", "-").toLowerCase().split("-")[0];
  return SUPPORTED_LOCALES.includes(language) ? language : DEFAULT_LOCALE;
}

function detectInitialLocale() {
  const queryLocale = queryParams.get("locale");
  if (queryLocale) return normalizeLocale(queryLocale);
  const explicit = localStorage.getItem("workbench-locale");
  if (explicit) return normalizeLocale(explicit);
  const browserLocale = (navigator.languages && navigator.languages[0]) || navigator.language || "";
  return normalizeLocale(browserLocale);
}

async function fetchMessages(locale) {
  const response = await fetch(`/static/locales/${locale}.json`, { cache: "no-store" });
  if (!response.ok) throw new Error(`Locale ${locale} could not be loaded`);
  return response.json();
}

function t(key, params = {}) {
  const template = state.messages[key] ?? state.fallbackMessages[key] ?? key;
  return String(template).replace(/\{([A-Za-z0-9_]+)\}/g, (_match, name) => {
    return Object.prototype.hasOwnProperty.call(params, name) ? String(params[name]) : `{${name}}`;
  });
}

function translateDocument() {
  document.documentElement.lang = state.locale;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.setAttribute("placeholder", t(node.dataset.i18nPlaceholder));
  });
  document.querySelectorAll("[data-i18n-aria-label]").forEach((node) => {
    node.setAttribute("aria-label", t(node.dataset.i18nAriaLabel));
  });
  const select = el("locale-select");
  if (select) select.value = state.locale;
}

async function setLocale(locale, persist = true) {
  state.locale = normalizeLocale(locale);
  if (!Object.keys(state.fallbackMessages).length) {
    state.fallbackMessages = await fetchMessages(DEFAULT_LOCALE);
  }
  state.messages = state.locale === DEFAULT_LOCALE
    ? state.fallbackMessages
    : { ...state.fallbackMessages, ...(await fetchMessages(state.locale)) };
  if (persist) localStorage.setItem("workbench-locale", state.locale);
  translateDocument();
  if (state.status) renderStatus();
  renderModels();
  renderResources();
}

async function api(path, options = {}) {
  const method = String(options.method || "GET").toUpperCase();
  const { headers: optionHeaders = {}, ...requestOptions } = options;
  const mutationHeaders = ["POST", "PUT", "DELETE", "PATCH"].includes(method)
    ? { "X-Workbench-Request": "same-origin" }
    : {};
  const response = await fetch(path, {
    ...requestOptions,
    headers: { "Content-Type": "application/json", "X-Workbench-Locale": state.locale, ...mutationHeaders, ...optionHeaders },
  });
  let payload = {};
  try {
    payload = await response.json();
  } catch {
    payload = { error: `HTTP ${response.status}` };
  }
  if (!response.ok) {
    const error = new Error(payload.error || `HTTP ${response.status}`);
    error.status = response.status;
    error.payload = payload;
    throw error;
  }
  return payload;
}

function setText(id, value) {
  el(id).textContent = value;
}

function hasUnsavedChanges(scope = "any") {
  if (scope === "model") return state.modelDirty;
  if (scope === "resource") return state.resourceDirty;
  return state.modelDirty || state.resourceDirty;
}

function unsavedPromptKey(scope) {
  if (scope === "model") return "prompt.discardUnsavedModel";
  if (scope === "resource") return "prompt.discardUnsavedResource";
  return "prompt.discardUnsavedAll";
}

function confirmDiscardUnsaved(scope = "any") {
  if (!hasUnsavedChanges(scope)) return true;
  return window.confirm(t(unsavedPromptKey(scope)));
}

function formatActionResult(result) {
  const command = Array.isArray(result.command) ? `$ ${result.command.join(" ")}` : result.label || result.action || "";
  const returncode = result.returncode === null || typeof result.returncode === "undefined" ? "-" : result.returncode;
  return `${command}\n\n${t("log.exitCode")}: ${returncode}\n${t("log.duration")}: ${formatNumber(result.duration_seconds, 1)}s\n\n${result.output || ""}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function inlineMarkdown(value) {
  let html = escapeHtml(value);
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*([^*]+)\*/g, "<em>$1</em>");
  return html;
}

function renderMarkdown(content) {
  const lines = String(content || "").replace(/\r\n/g, "\n").split("\n");
  const output = [];
  let listType = "";
  let inCode = false;
  let codeLines = [];

  const closeList = () => {
    if (listType) {
      output.push(`</${listType}>`);
      listType = "";
    }
  };
  const flushCode = () => {
    output.push(`<pre><code>${escapeHtml(codeLines.join("\n"))}</code></pre>`);
    codeLines = [];
  };

  for (const line of lines) {
    if (line.trim().startsWith("```")) {
      closeList();
      if (inCode) {
        flushCode();
      }
      inCode = !inCode;
      continue;
    }
    if (inCode) {
      codeLines.push(line);
      continue;
    }

    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      closeList();
      const level = heading[1].length;
      output.push(`<h${level}>${inlineMarkdown(heading[2])}</h${level}>`);
      continue;
    }

    const bullet = line.match(/^\s*[-*]\s+(.+)$/);
    if (bullet) {
      if (listType !== "ul") {
        closeList();
        output.push("<ul>");
        listType = "ul";
      }
      output.push(`<li>${inlineMarkdown(bullet[1])}</li>`);
      continue;
    }

    const numbered = line.match(/^\s*\d+\.\s+(.+)$/);
    if (numbered) {
      if (listType !== "ol") {
        closeList();
        output.push("<ol>");
        listType = "ol";
      }
      output.push(`<li>${inlineMarkdown(numbered[1])}</li>`);
      continue;
    }

    const quote = line.match(/^>\s?(.*)$/);
    if (quote) {
      closeList();
      output.push(`<blockquote>${inlineMarkdown(quote[1])}</blockquote>`);
      continue;
    }

    if (!line.trim()) {
      closeList();
      continue;
    }

    closeList();
    output.push(`<p>${inlineMarkdown(line)}</p>`);
  }

  closeList();
  if (inCode) flushCode();
  return output.join("\n") || `<p class="empty-preview">${t("preview.empty")}</p>`;
}

function highlightPython(content) {
  const keywords = new Set([
    "False", "None", "True", "and", "as", "assert", "async", "await", "break", "class", "continue", "def", "del",
    "elif", "else", "except", "finally", "for", "from", "global", "if", "import", "in", "is", "lambda", "nonlocal",
    "not", "or", "pass", "raise", "return", "try", "while", "with", "yield",
  ]);
  const builtins = new Set(["dict", "int", "len", "list", "max", "min", "print", "range", "set", "str", "sum", "tuple"]);
  const tokenPattern = /(@[A-Za-z_][\w.]*|#[^\n]*|"""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b\d+(?:\.\d+)?\b|\b[A-Za-z_]\w*\b)/g;
  let html = "";
  let index = 0;
  for (const match of String(content || "").matchAll(tokenPattern)) {
    const token = match[0];
    const start = match.index || 0;
    html += escapeHtml(String(content || "").slice(index, start));
    const safe = escapeHtml(token);
    if (token.startsWith("#")) html += `<span class="py-comment">${safe}</span>`;
    else if (token.startsWith("@")) html += `<span class="py-decorator">${safe}</span>`;
    else if (/^['"]/.test(token)) html += `<span class="py-string">${safe}</span>`;
    else if (/^\d/.test(token)) html += `<span class="py-number">${safe}</span>`;
    else if (keywords.has(token)) html += `<span class="py-keyword">${safe}</span>`;
    else if (builtins.has(token)) html += `<span class="py-builtin">${safe}</span>`;
    else html += safe;
    index = start + token.length;
  }
  html += escapeHtml(String(content || "").slice(index));
  return `<pre><code>${html}</code></pre>`;
}

function updateModelPreview() {
  el("markdown-preview").innerHTML = renderMarkdown(el("markdown-editor").value);
}

function updateResourcePreview() {
  const content = el("resource-editor").value;
  if (state.selectedResource?.kind === "tool") {
    el("resource-preview").innerHTML = highlightPython(content);
  } else {
    el("resource-preview").innerHTML = renderMarkdown(content);
  }
}

function applyView(editor, mode) {
  const workspace = el(editor === "model" ? "model-workspace" : "resource-workspace");
  workspace.classList.remove("split-mode", "edit-mode", "preview-mode");
  workspace.classList.add(`${mode}-mode`);
  if (editor === "model") state.modelView = mode;
  if (editor === "resource") state.resourceView = mode;
  document.querySelectorAll(`.view-mode[data-editor="${editor}"]`).forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === mode);
  });
}

function applyTheme(theme) {
  const light = theme === "light";
  document.body.classList.toggle("light-theme", light);
  el("theme-toggle").textContent = light ? t("theme.light") : t("theme.dark");
  el("theme-toggle").setAttribute("aria-pressed", String(!light));
  localStorage.setItem("workbench-theme", theme);
}

function renderStatus() {
  const status = state.status;
  if (!status) return;
  const artifacts = status.artifacts || [];
  const existingArtifacts = artifacts.filter((item) => item.exists).length;
  const artifactBytes = artifacts.reduce((total, item) => total + (item.bytes || 0), 0);
  setText("repo-root", displayRepoPath(status.root));
  setText("count-models", formatNumber(status.counts.models));
  setText("count-tools", formatNumber(status.counts.tools));
  setText("count-skills", formatNumber(status.counts.skills));
  setText("openwebui-url", status.openwebui.public_url);
  setText("openwebui-status", status.openwebui.reachable.ok ? t("status.openwebuiReachable") : t("status.openwebuiUnreachable"));
  el("open-openwebui").href = status.openwebui.public_url;
  el("openwebui-dot").classList.toggle("online", Boolean(status.openwebui.reachable.ok));
  setText("config-local", status.config.local_config_exists ? status.config.config_path : t("config.missing", { path: status.config.config_path }));
  const tlsMode = status.openwebui.tls_verify ? t("config.tlsVerified") : t("config.tlsOff");
  const caMode = status.openwebui.ca_file_configured || status.openwebui.ca_path_configured ? t("config.customCa") : t("config.systemCa");
  setText("config-token", `${status.openwebui.admin_token_configured ? t("state.set") : t("state.notSet")} · ${tlsMode} · ${caMode}`);
  setText("config-write", status.write_enabled ? t("state.active") : t("state.disabled"));
  setText("signal-api", status.openwebui.reachable.ok ? t("signals.connected") : t("signals.unreachable"));
  setText("signal-api-detail", status.openwebui.base_url);
  setText("signal-auth", status.dashboard?.auth_enabled ? t("signals.authEnabled") : t("signals.localMode"));
  setText("signal-auth-detail", status.dashboard?.auth_enabled ? t("signals.allRoutesProtected") : t("signals.authEnvMissing"));
  setText("signal-write", status.write_enabled ? t("signals.writeEnabled") : t("signals.readOnly"));
  setText("signal-config", status.config.local_config_exists ? t("signals.localConfig") : t("signals.exampleConfig"));
  setText("signal-artifacts", t("artifacts.existing", { existing: existingArtifacts, total: artifacts.length }));
  setText("signal-artifacts-detail", t("artifacts.handover", { bytes: formatBytes(artifactBytes) }));
  setSignalState("signal-api", status.openwebui.reachable.ok ? "ok" : "danger");
  setSignalState("signal-auth", status.dashboard?.auth_enabled ? "ok" : "warn");
  setSignalState("signal-write", status.write_enabled ? "ok" : "warn");
  setSignalState("signal-artifacts", existingArtifacts === artifacts.length ? "ok" : "warn");
  renderSetupChecks(status, existingArtifacts, artifacts.length);

  const artifactList = el("artifact-list");
  artifactList.replaceChildren();
  artifacts.forEach((item) => {
    const row = document.createElement("div");
    row.className = "artifact-item";
    const title = document.createElement("strong");
    title.textContent = item.path;
    const meta = document.createElement("span");
    meta.textContent = item.exists ? `${formatNumber(item.bytes)} ${t("unit.bytes")} · ${formatDateTime(item.mtime)}` : t("state.missing");
    const stateChip = document.createElement("span");
    stateChip.className = `chip artifact-state ${item.exists ? "ok" : "warn"}`;
    stateChip.textContent = item.exists ? formatBytes(item.bytes) : t("state.missing");
    const text = document.createElement("div");
    text.append(title, meta);
    row.append(text, stateChip);
    artifactList.append(row);
  });
}

function setupChecks(status, existingArtifacts, artifactTotal) {
  const syncReady = Boolean(status.openwebui.admin_token_configured || status.config.local_config_exists);
  return [
    {
      level: status.dashboard?.auth_enabled ? "ok" : "warn",
      title: status.dashboard?.auth_enabled ? t("setup.authReady") : t("setup.authMissing"),
      detail: status.dashboard?.auth_enabled ? t("signals.allRoutesProtected") : t("signals.authEnvMissing"),
    },
    {
      level: status.openwebui.reachable.ok ? "ok" : "danger",
      title: status.openwebui.reachable.ok ? t("setup.openwebuiReady") : t("setup.openwebuiMissing"),
      detail: status.openwebui.base_url,
    },
    {
      level: syncReady ? "ok" : "warn",
      title: syncReady ? t("setup.syncReady") : t("setup.syncMissing"),
      detail: syncReady ? t("setup.syncReadyDetail") : t("setup.syncMissingDetail"),
    },
    {
      level: existingArtifacts === artifactTotal ? "ok" : "warn",
      title: existingArtifacts === artifactTotal ? t("setup.artifactsReady") : t("setup.artifactsMissing"),
      detail: t("artifacts.existing", { existing: existingArtifacts, total: artifactTotal }),
    },
    {
      level: status.write_enabled ? "ok" : "warn",
      title: status.write_enabled ? t("setup.writeReady") : t("setup.writeDisabled"),
      detail: status.write_enabled ? t("signals.writeEnabled") : t("signals.readOnly"),
    },
  ];
}

function renderSetupChecks(status, existingArtifacts, artifactTotal) {
  const checks = setupChecks(status, existingArtifacts, artifactTotal);
  const blockers = checks.filter((item) => item.level === "danger").length;
  const warnings = checks.filter((item) => item.level === "warn").length;
  setText(
    "setup-summary",
    blockers
      ? t("setup.summaryBlockers", { count: blockers })
      : warnings
        ? t("setup.summaryWarnings", { count: warnings })
        : t("setup.summaryReady"),
  );

  const container = el("setup-checks");
  container.replaceChildren();
  checks.forEach((item) => {
    const row = document.createElement("div");
    row.className = `setup-check ${item.level}`;
    const marker = document.createElement("span");
    marker.className = "setup-marker";
    marker.setAttribute("aria-hidden", "true");
    const text = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = item.title;
    const detail = document.createElement("span");
    detail.textContent = item.detail;
    text.append(title, detail);
    row.append(marker, text);
    container.append(row);
  });
}

function setSignalState(id, level) {
  const card = el(id).closest(".signal-card");
  card.classList.remove("ok", "warn", "danger");
  card.classList.add(level);
}

function formatBytes(bytes) {
  if (!bytes) return `0 ${t("unit.byteShort")}`;
  const units = ["B", "KB", "MB", "GB"];
  let value = bytes;
  let index = 0;
  while (value >= 1024 && index < units.length - 1) {
    value /= 1024;
    index += 1;
  }
  return `${formatNumber(value, index === 0 ? 0 : 1)} ${units[index]}`;
}

function formatNumber(value, fractionDigits = 0) {
  return new Intl.NumberFormat(state.locale === "en" ? "en-US" : "de-DE", {
    maximumFractionDigits: fractionDigits,
    minimumFractionDigits: fractionDigits,
  }).format(value);
}

function formatDateTime(value) {
  if (!value) return "-";
  const parsed = new Date(String(value).replace(" ", "T"));
  if (Number.isNaN(parsed.getTime())) return value;
  return new Intl.DateTimeFormat(state.locale === "en" ? "en-US" : "de-DE", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(parsed);
}

function localizedProduct(model) {
  const i18n = model?.i18n || {};
  return i18n[state.locale] || i18n[model?.fallback_locale || "en"] || i18n[model?.default_locale || "de"] || i18n.de || {};
}

function modelDisplayName(model) {
  return localizedProduct(model).name || model.name || model.id;
}

function modelDisplayDescription(model) {
  return localizedProduct(model).description || model.description || model.id;
}

function visibleModels() {
  const query = el("model-search").value.trim().toLocaleLowerCase(state.locale);
  if (!query) return state.models;
  return state.models.filter((model) => {
    const product = localizedProduct(model);
    return `${model.id} ${model.name} ${model.description} ${product.name || ""} ${product.description || ""}`.toLocaleLowerCase(state.locale).includes(query);
  });
}

function visibleResources() {
  const query = el("resource-search").value.trim().toLocaleLowerCase(state.locale);
  if (!query) return state.resources;
  return state.resources.filter((resource) => {
    return `${resource.kind} ${resource.id} ${resource.name} ${resource.path}`.toLocaleLowerCase(state.locale).includes(query);
  });
}

function renderResources() {
  const list = el("resource-list");
  list.replaceChildren();
  const resources = visibleResources();
  setText("resource-filter-state", t("resources.count", { visible: formatNumber(resources.length), total: formatNumber(state.resources.length) }));
  if (!resources.length) {
    renderEmpty(list, t("resources.empty"));
    return;
  }
  resources.forEach((resource) => {
    const button = document.createElement("button");
    button.className = `resource-row${state.selectedResource?.kind === resource.kind && state.selectedResource?.id === resource.id ? " active" : ""}`;
    button.type = "button";
    if (state.selectedResource?.kind === resource.kind && state.selectedResource?.id === resource.id) {
      button.setAttribute("aria-current", "true");
    }
    const title = document.createElement("strong");
    title.textContent = resource.name;
    const meta = document.createElement("div");
    meta.className = "row-meta";
    meta.append(makeChip(t(`resource.kind.${resource.kind}`), resource.kind === "tool" ? "accent" : "ok"), makeChip(resource.extension), makeChip(formatBytes(resource.bytes)));
    const sub = document.createElement("span");
    sub.textContent = resource.path;
    button.append(title, meta, sub);
    button.addEventListener("click", () => selectResource(resource.kind, resource.id));
    list.append(button);
  });
}

function renderModels() {
  const list = el("model-list");
  list.replaceChildren();
  const models = visibleModels();
  setText("model-filter-state", t("models.count", { visible: formatNumber(models.length), total: formatNumber(state.models.length) }));
  if (!models.length) {
    renderEmpty(list, t("models.empty"));
    return;
  }
  models.forEach((model) => {
    const button = document.createElement("button");
    button.className = `model-row${state.selectedModel?.id === model.id ? " active" : ""}`;
    button.type = "button";
    if (state.selectedModel?.id === model.id) {
      button.setAttribute("aria-current", "true");
    }
    const title = document.createElement("strong");
    title.textContent = modelDisplayName(model);
    const meta = document.createElement("div");
    meta.className = "row-meta";
    meta.append(
      makeChip(model.base_model_id || t("models.noBase"), "accent"),
      makeChip(t("models.filesCount", { existing: model.files.filter((file) => file.exists).length, total: model.files.length }), "ok"),
    );
    if (model.tags?.[0]) meta.append(makeChip(model.tags[0]));
    const sub = document.createElement("span");
    sub.textContent = modelDisplayDescription(model);
    button.append(title, meta, sub);
    button.addEventListener("click", () => selectModel(model.id));
    list.append(button);
  });
}

function makeChip(text, tone = "") {
  const chip = document.createElement("span");
  chip.className = `chip${tone ? ` ${tone}` : ""}`;
  chip.textContent = text;
  return chip;
}

function renderEmpty(container, message) {
  const empty = document.createElement("div");
  empty.className = "empty-state";
  empty.textContent = message;
  container.append(empty);
}

function displayRepoPath(value) {
  const normalized = String(value || "").replace(/\\/g, "/");
  const parts = normalized.split("/").filter(Boolean);
  if (parts.length >= 2) {
    return `.../${parts.slice(-2).join("/")}`;
  }
  return normalized || "-";
}

function modelFileGroup(name) {
  if (name.startsWith("beispiele/")) return "examples";
  if (name.startsWith("i18n/")) return "i18n";
  if (name.startsWith("beispielergebnis.")) return "artifacts";
  return "core";
}

function modelFileTemplate(name) {
  if (name.endsWith(".html")) return "<!doctype html>\n<html lang=\"de\">\n  <head>\n    <meta charset=\"utf-8\" />\n    <title>Beispiel</title>\n  </head>\n  <body>\n    <main>\n      <h1>Beispiel</h1>\n    </main>\n  </body>\n</html>\n";
  if (name.endsWith(".json")) return "{\n  \"name\": \"Beispiel\"\n}\n";
  if (name.endsWith(".yaml") || name.endsWith(".yml")) return "name: Beispiel\n";
  if (name.endsWith(".py")) return "from __future__ import annotations\n\n\ndef main() -> None:\n    print(\"Beispiel\")\n\n\nif __name__ == \"__main__\":\n    main()\n";
  if (name.endsWith(".js")) return "\"use strict\";\n\nconsole.log(\"Beispiel\");\n";
  if (name.endsWith(".css")) return ":root {\n  color-scheme: light dark;\n}\n";
  if (name.endsWith(".csv")) return "name,value\nBeispiel,1\n";
  if (name.endsWith(".sql")) return "select 1 as beispiel;\n";
  if (name.endsWith(".svg")) return "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 320 180\" role=\"img\" aria-label=\"Beispielgrafik\"><rect width=\"320\" height=\"180\" fill=\"#f8fafc\"/><text x=\"24\" y=\"96\" font-family=\"Arial\" font-size=\"24\" fill=\"#17202e\">Beispiel</text></svg>\n";
  return "# Neue Datei\n\nBeschreibe hier den Zweck dieser Datei.\n";
}

function selectedModelFileExists() {
  return Boolean(state.selectedModel?.files.find((file) => file.name === state.selectedFile && file.exists));
}

function resetModelEditor() {
  state.selectedModel = null;
  state.selectedFile = "systemprompt.md";
  state.modelDirty = false;
  setText("model-title", t("models.none"));
  setText("model-description", t("models.pick"));
  el("markdown-editor").value = "";
  el("markdown-editor").disabled = true;
  el("markdown-preview").innerHTML = renderMarkdown("");
  el("save-file").disabled = true;
  el("delete-model-file").disabled = true;
  setText("editor-state", t("state.ready"));
  renderFileTabs();
}

function resetResourceEditor() {
  state.selectedResource = null;
  state.resourceDirty = false;
  setText("resource-title", t("resources.none"));
  setText("resource-description", t("resources.pick"));
  el("resource-editor").value = "";
  el("resource-editor").disabled = true;
  el("resource-preview").innerHTML = renderMarkdown("");
  el("save-resource").disabled = true;
  el("delete-resource").disabled = true;
  setText("resource-state", t("state.ready"));
}

function renderFileTabs() {
  const tabs = el("file-tabs");
  tabs.replaceChildren();
  if (!state.selectedModel) return;
  const grouped = new Map();
  state.selectedModel.files.forEach((file) => {
    const group = modelFileGroup(file.name);
    if (!grouped.has(group)) grouped.set(group, []);
    grouped.get(group).push(file);
  });
  ["core", "artifacts", "examples", "i18n"].forEach((group) => {
    const files = grouped.get(group) || [];
    if (!files.length) return;
    const section = document.createElement("section");
    section.className = "file-group";
    const heading = document.createElement("h4");
    heading.textContent = t(`files.group.${group}`);
    section.append(heading);
    files.forEach((file) => {
      const button = document.createElement("button");
      button.className = `file-tab${state.selectedFile === file.name ? " active" : ""}${file.exists ? "" : " missing"}`;
      button.type = "button";
      const name = document.createElement("span");
      name.textContent = file.name;
      const meta = document.createElement("small");
      meta.textContent = file.exists ? `${formatBytes(file.bytes)} · ${formatDateTime(file.mtime)}` : t("state.missing");
      button.append(name, meta);
      button.addEventListener("click", () => loadFile(file.name));
      section.append(button);
    });
    tabs.append(section);
  });
  el("delete-model-file").disabled = !selectedModelFileExists();
}

async function selectResource(kind, resourceId) {
  if (state.selectedResource?.kind === kind && state.selectedResource?.id === resourceId) return;
  if (!confirmDiscardUnsaved("resource")) return;
  const resource = state.resources.find((item) => item.kind === kind && item.id === resourceId);
  state.selectedResource = resource;
  setText("resource-title", resource.name);
  setText("resource-description", resource.path);
  renderResources();
  setText("resource-state", t("state.loadingFile"));
  const payload = await api(`/api/resources/${encodeURIComponent(kind)}/${encodeURIComponent(resourceId)}/file`);
  el("resource-editor").disabled = false;
  el("resource-editor").value = payload.content;
  state.resourceDirty = false;
  updateResourcePreview();
  el("save-resource").disabled = false;
  el("delete-resource").disabled = false;
  setText("resource-state", t("state.loaded", { path: payload.path }));
}

async function selectModel(modelId) {
  if (state.selectedModel?.id === modelId) return;
  if (!confirmDiscardUnsaved("model")) return;
  const model = state.models.find((item) => item.id === modelId);
  state.selectedModel = model;
  state.selectedFile = model.files.find((file) => file.name === "systemprompt.md")?.name || model.files[0]?.name || "systemprompt.md";
  setText("model-title", modelDisplayName(model));
  setText("model-description", modelDisplayDescription(model));
  renderModels();
  renderFileTabs();
  await loadFile(state.selectedFile);
}

async function loadFile(name) {
  if (!state.selectedModel) return;
  if (state.selectedFile === name && !state.modelDirty && !el("markdown-editor").disabled) return;
  if (state.selectedFile !== name && !confirmDiscardUnsaved("model")) return;
  state.selectedFile = name;
  renderFileTabs();
  setText("editor-state", t("state.loadingFile"));
  const payload = await api(`/api/models/${encodeURIComponent(state.selectedModel.id)}/file?name=${encodeURIComponent(name)}`);
  el("markdown-editor").disabled = false;
  el("markdown-editor").value = payload.content;
  updateModelPreview();
  el("save-file").disabled = false;
  el("delete-model-file").disabled = !payload.exists;
  state.modelDirty = false;
  setText("editor-state", payload.exists ? t("state.loaded", { path: payload.path }) : t("state.newFile", { path: payload.path }));
}

async function addModelFile() {
  if (!state.selectedModel) return;
  if (!confirmDiscardUnsaved("model")) return;
  const name = window.prompt(t("prompt.modelFileName"), "beispiele/neues-beispiel.md");
  if (!name) return;
  if (state.selectedModel.files.some((file) => file.name === name && file.exists)) {
    window.alert(t("files.exists"));
    return;
  }
  setText("editor-state", t("state.saving"));
  try {
    await api(`/api/models/${encodeURIComponent(state.selectedModel.id)}/file`, {
      method: "PUT",
      body: JSON.stringify({ name, content: modelFileTemplate(name) }),
    });
    await refreshModels(true);
    await loadFile(name);
  } catch (error) {
    setText("editor-state", error.message);
  }
}

async function deleteModelFile() {
  if (!state.selectedModel || !state.selectedFile) return;
  if (!window.confirm(t("prompt.deleteFile", { name: state.selectedFile }))) return;
  setText("editor-state", t("state.deleting"));
  try {
    await api(`/api/models/${encodeURIComponent(state.selectedModel.id)}/file?name=${encodeURIComponent(state.selectedFile)}`, {
      method: "DELETE",
    });
    const deleted = state.selectedFile;
    await refreshModels(true);
    const nextFile = state.selectedModel?.files.find((file) => file.exists && file.name !== deleted)?.name
      || state.selectedModel?.files[0]?.name
      || "systemprompt.md";
    await loadFile(nextFile);
  } catch (error) {
    setText("editor-state", error.message);
  }
}

function resourceTemplate(kind, id) {
  if (kind === "tool") {
    let methodName = String(id || "new_tool").replace(/[^A-Za-z0-9_]/g, "_");
    if (!/^[A-Za-z_]/.test(methodName)) methodName = `tool_${methodName}`;
    return `from __future__ import annotations\n\n\nclass Tools:\n    def __init__(self) -> None:\n        pass\n\n    async def ${methodName}(self, text: str) -> str:\n        \"\"\"Kurze Beschreibung der Tool-Funktion.\"\"\"\n        return text\n`;
  }
  return `# ${id}\n\n## Zweck\n\nBeschreibe, wann dieser Skill genutzt werden soll.\n\n## Arbeitsweise\n\n- Prüfe zuerst die Eingaben.\n- Arbeite offline-fähig und ohne Secrets.\n- Gib konkrete, prüfbare Ergebnisse aus.\n`;
}

async function addResource() {
  if (!confirmDiscardUnsaved("resource")) return;
  const rawKind = window.prompt(t("prompt.resourceKind"), "skill");
  if (!rawKind) return;
  const kind = rawKind.trim().toLowerCase();
  if (!["tool", "skill"].includes(kind)) {
    window.alert(t("resource.kind.invalid"));
    return;
  }
  const id = window.prompt(t("prompt.resourceId"), kind === "tool" ? "neues_tool" : "neuer-skill");
  if (!id) return;
  setText("resource-state", t("state.saving"));
  try {
    const payload = await api("/api/resources", {
      method: "POST",
      body: JSON.stringify({ kind, id, content: resourceTemplate(kind, id) }),
    });
    await refreshResources(true);
    await selectResource(payload.kind, payload.id);
  } catch (error) {
    setText("resource-state", error.message);
  }
}

async function deleteResource() {
  if (!state.selectedResource) return;
  const { kind, id } = state.selectedResource;
  if (!window.confirm(t("prompt.deleteResource", { name: `${kind}/${id}` }))) return;
  setText("resource-state", t("state.deleting"));
  try {
    await api(`/api/resources/${encodeURIComponent(kind)}/${encodeURIComponent(id)}/file`, { method: "DELETE" });
    state.selectedResource = null;
    state.resourceDirty = false;
    el("resource-editor").value = "";
    el("resource-editor").disabled = true;
    el("resource-preview").innerHTML = "";
    el("save-resource").disabled = true;
    el("delete-resource").disabled = true;
    setText("resource-title", t("resources.none"));
    setText("resource-description", t("resources.pick"));
    setText("resource-state", t("state.deleted"));
    await refreshResources(false);
  } catch (error) {
    setText("resource-state", error.message);
  }
}

async function saveResource() {
  if (!state.selectedResource) return;
  el("save-resource").disabled = true;
  setText("resource-state", t("state.saving"));
  try {
    const payload = await api(
      `/api/resources/${encodeURIComponent(state.selectedResource.kind)}/${encodeURIComponent(state.selectedResource.id)}/file`,
      {
        method: "PUT",
        body: JSON.stringify({ content: el("resource-editor").value }),
      },
    );
    state.resourceDirty = false;
    setText("resource-state", t("state.saved", { path: payload.path }));
    await refreshResources(false);
  } catch (error) {
    setText("resource-state", error.message);
  } finally {
    el("save-resource").disabled = false;
  }
}

async function saveFile() {
  if (!state.selectedModel || !state.selectedFile) return;
  el("save-file").disabled = true;
  setText("editor-state", t("state.saving"));
  try {
    const payload = await api(`/api/models/${encodeURIComponent(state.selectedModel.id)}/file`, {
      method: "PUT",
      body: JSON.stringify({ name: state.selectedFile, content: el("markdown-editor").value }),
    });
    state.modelDirty = false;
    setText("editor-state", t("state.saved", { path: payload.path }));
    await refreshModels(false);
  } catch (error) {
    setText("editor-state", error.message);
  } finally {
    el("save-file").disabled = false;
  }
}

async function runAction(action) {
  const log = el("action-log");
  log.textContent = t("log.starting", { action });
  try {
    const result = await api(`/api/actions/${encodeURIComponent(action)}`, { method: "POST", body: "{}" });
    if (result.running && result.job_id) {
      await pollActionJob(result.job_id);
      return;
    }
    log.textContent = formatActionResult(result);
    await refreshStatus();
    await refreshModels(false);
    await refreshResources(false);
  } catch (error) {
    if (error.payload?.command && typeof error.payload.output === "string") {
      log.textContent = `${formatActionResult(error.payload)}\n\n${t("state.error")}: ${error.message}`;
    } else {
      log.textContent += `\n\n${t("state.error")}: ${error.message}`;
    }
  }
}

async function pollActionJob(jobId) {
  const log = el("action-log");
  for (;;) {
    const result = await api(`/api/action-jobs/${encodeURIComponent(jobId)}`);
    if (result.running) {
      log.textContent = `${formatActionResult(result)}\n\n${t("state.running")}`;
      await new Promise((resolve) => setTimeout(resolve, 2000));
      continue;
    }
    log.textContent = formatActionResult(result);
    await refreshStatus();
    await refreshModels(false);
    await refreshResources(false);
    return;
  }
}

async function refreshStatus() {
  state.status = await api("/api/status");
  renderStatus();
}

async function refreshResources(keepSelection = true) {
  const payload = await api("/api/resources");
  const previous = state.selectedResource ? `${state.selectedResource.kind}:${state.selectedResource.id}` : "";
  state.resources = [...payload.tools, ...payload.skills];
  if (keepSelection && previous) {
    state.selectedResource = state.resources.find((resource) => `${resource.kind}:${resource.id}` === previous) || null;
  }
  if (!state.selectedResource || !state.resources.some((resource) => resource.kind === state.selectedResource.kind && resource.id === state.selectedResource.id)) {
    resetResourceEditor();
  }
  renderResources();
}

async function refreshModels(keepSelection = true) {
  const payload = await api("/api/models");
  const previous = state.selectedModel?.id;
  state.models = payload.models;
  if (keepSelection && previous) {
    state.selectedModel = state.models.find((model) => model.id === previous) || null;
  }
  if (!state.selectedModel || !state.models.some((model) => model.id === state.selectedModel.id)) {
    resetModelEditor();
  }
  renderModels();
}

function wireEvents() {
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => activatePanel(button.dataset.panel));
  });
  el("model-search").addEventListener("input", renderModels);
  el("resource-search").addEventListener("input", renderResources);
  el("markdown-editor").addEventListener("input", () => {
    state.modelDirty = true;
    updateModelPreview();
    setText("editor-state", t("state.unsaved"));
  });
  el("resource-editor").addEventListener("input", () => {
    state.resourceDirty = true;
    updateResourcePreview();
    setText("resource-state", t("state.unsaved"));
  });
  document.querySelectorAll(".view-mode").forEach((button) => {
    button.addEventListener("click", () => applyView(button.dataset.editor, button.dataset.mode));
  });
  el("theme-toggle").addEventListener("click", () => {
    applyTheme(document.body.classList.contains("light-theme") ? "dark" : "light");
  });
  el("locale-select").addEventListener("change", async () => {
    await setLocale(el("locale-select").value, true);
    applyTheme(document.body.classList.contains("light-theme") ? "light" : "dark");
  });
  el("refresh-dashboard").addEventListener("click", async () => {
    if (!confirmDiscardUnsaved()) return;
    setText("editor-state", t("state.refreshing"));
    await refreshStatus();
    await refreshModels(true);
    await refreshResources(true);
    setText("editor-state", t("state.refreshed"));
  });
  el("save-file").addEventListener("click", saveFile);
  el("add-model-file").addEventListener("click", addModelFile);
  el("delete-model-file").addEventListener("click", deleteModelFile);
  el("add-resource").addEventListener("click", addResource);
  el("delete-resource").addEventListener("click", deleteResource);
  el("save-resource").addEventListener("click", saveResource);
  document.querySelectorAll("[data-action]").forEach((button) => {
    button.addEventListener("click", () => runAction(button.dataset.action));
  });
  el("clear-log").addEventListener("click", () => {
    el("action-log").textContent = t("log.empty");
  });
  window.addEventListener("beforeunload", (event) => {
    if (!hasUnsavedChanges()) return;
    event.preventDefault();
    event.returnValue = "";
  });
}

function activatePanel(panelName) {
  const target = SUPPORTED_PANELS.has(panelName) ? panelName : "models";
  document.querySelectorAll(".nav-item").forEach((item) => {
    const active = item.dataset.panel === target;
    item.classList.toggle("active", active);
    if (active) {
      item.setAttribute("aria-current", "page");
    } else {
      item.removeAttribute("aria-current");
    }
  });
  document.querySelectorAll(".panel").forEach((panel) => panel.classList.remove("active"));
  el(`panel-${target}`).classList.add("active");
}

async function init() {
  const requestedPanel = queryParams.get("panel") || "models";
  await setLocale(detectInitialLocale(), false);
  applyTheme(localStorage.getItem("workbench-theme") || "dark");
  applyView("model", state.modelView);
  applyView("resource", state.resourceView);
  wireEvents();
  activatePanel(requestedPanel);
  await Promise.all([refreshStatus(), refreshModels(false), refreshResources(false)]);
  if (state.models.length > 0) {
    const requestedModel = queryParams.get("model");
    const initialModel = state.models.find((model) => model.id === requestedModel) || state.models[0];
    if (requestedModel && initialModel.id === requestedModel) {
      el("model-search").value = requestedModel;
      renderModels();
    }
    await selectModel(initialModel.id);
    const requestedFile = queryParams.get("file");
    if (requestedFile && initialModel.files.some((file) => file.name === requestedFile)) {
      await loadFile(requestedFile);
    }
  }
  if (requestedPanel === "resources" && state.resources.length > 0) {
    const requestedResource = queryParams.get("resource");
    const initialResource =
      state.resources.find((resource) => `${resource.kind}:${resource.id}` === requestedResource || resource.id === requestedResource) ||
      state.resources[0];
    await selectResource(initialResource.kind, initialResource.id);
  }
}

init().catch((error) => {
  document.body.innerHTML = `<main class="main"><pre>${error.message}</pre></main>`;
});
