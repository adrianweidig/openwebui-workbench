const state = {
  status: null,
  models: [],
  resources: [],
  selectedModel: null,
  selectedFile: "systemprompt.md",
  selectedResource: null,
  dirty: false,
  modelView: "split",
  resourceView: "split",
};

const el = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || `HTTP ${response.status}`);
  }
  return payload;
}

function setText(id, value) {
  el(id).textContent = value;
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
  return output.join("\n") || "<p class=\"empty-preview\">Keine Vorschau verfügbar.</p>";
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
  el("theme-toggle").textContent = light ? "Light" : "Dark";
  el("theme-toggle").setAttribute("aria-pressed", String(!light));
  localStorage.setItem("workbench-theme", theme);
}

function renderStatus() {
  const status = state.status;
  if (!status) return;
  setText("repo-root", status.root);
  setText("count-models", status.counts.models);
  setText("count-tools", status.counts.tools);
  setText("count-skills", status.counts.skills);
  setText("openwebui-url", status.openwebui.public_url);
  setText("openwebui-status", status.openwebui.reachable.ok ? "OpenWebUI erreichbar" : "OpenWebUI nicht erreichbar");
  el("open-openwebui").href = status.openwebui.public_url;
  el("openwebui-dot").classList.toggle("online", Boolean(status.openwebui.reachable.ok));
  setText("config-local", status.config.local_config_exists ? status.config.config_path : `${status.config.config_path} fehlt`);
  const tlsMode = status.openwebui.tls_verify ? "TLS verifiziert" : "TLS Prüfung aus";
  const caMode = status.openwebui.ca_file_configured || status.openwebui.ca_path_configured ? "eigene CA" : "System-CA";
  setText("config-token", `${status.openwebui.admin_token_configured ? "gesetzt" : "nicht gesetzt"} · ${tlsMode} · ${caMode}`);
  setText("config-write", status.write_enabled ? "aktiv" : "deaktiviert");

  const artifactList = el("artifact-list");
  artifactList.replaceChildren();
  status.artifacts.forEach((item) => {
    const row = document.createElement("div");
    row.className = "artifact-item";
    const title = document.createElement("strong");
    title.textContent = item.path;
    const meta = document.createElement("span");
    meta.textContent = item.exists ? `${item.bytes} Bytes · ${item.mtime}` : "fehlt";
    row.append(title, meta);
    artifactList.append(row);
  });
}

function visibleModels() {
  const query = el("model-search").value.trim().toLowerCase();
  if (!query) return state.models;
  return state.models.filter((model) => {
    return `${model.id} ${model.name} ${model.description}`.toLowerCase().includes(query);
  });
}

function visibleResources() {
  const query = el("resource-search").value.trim().toLowerCase();
  if (!query) return state.resources;
  return state.resources.filter((resource) => {
    return `${resource.kind} ${resource.id} ${resource.name} ${resource.path}`.toLowerCase().includes(query);
  });
}

function renderResources() {
  const list = el("resource-list");
  list.replaceChildren();
  visibleResources().forEach((resource) => {
    const button = document.createElement("button");
    button.className = `resource-row${state.selectedResource?.kind === resource.kind && state.selectedResource?.id === resource.id ? " active" : ""}`;
    button.type = "button";
    const title = document.createElement("strong");
    title.textContent = resource.name;
    const sub = document.createElement("span");
    sub.textContent = `${resource.kind} · ${resource.path}`;
    button.append(title, sub);
    button.addEventListener("click", () => selectResource(resource.kind, resource.id));
    list.append(button);
  });
}

function renderModels() {
  const list = el("model-list");
  list.replaceChildren();
  visibleModels().forEach((model) => {
    const button = document.createElement("button");
    button.className = `model-row${state.selectedModel?.id === model.id ? " active" : ""}`;
    button.type = "button";
    const title = document.createElement("strong");
    title.textContent = model.name;
    const sub = document.createElement("span");
    sub.textContent = model.id;
    button.append(title, sub);
    button.addEventListener("click", () => selectModel(model.id));
    list.append(button);
  });
}

function renderFileTabs() {
  const tabs = el("file-tabs");
  tabs.replaceChildren();
  if (!state.selectedModel) return;
  state.selectedModel.files.forEach((file) => {
    const button = document.createElement("button");
    button.className = `file-tab${state.selectedFile === file.name ? " active" : ""}`;
    button.type = "button";
    button.textContent = file.name;
    button.addEventListener("click", () => loadFile(file.name));
    tabs.append(button);
  });
}

async function selectResource(kind, resourceId) {
  const resource = state.resources.find((item) => item.kind === kind && item.id === resourceId);
  state.selectedResource = resource;
  setText("resource-title", resource.name);
  setText("resource-description", resource.path);
  renderResources();
  setText("resource-state", "Lade Datei");
  const payload = await api(`/api/resources/${encodeURIComponent(kind)}/${encodeURIComponent(resourceId)}/file`);
  el("resource-editor").disabled = false;
  el("resource-editor").value = payload.content;
  updateResourcePreview();
  el("save-resource").disabled = false;
  setText("resource-state", `${payload.path} geladen`);
}

async function selectModel(modelId) {
  const model = state.models.find((item) => item.id === modelId);
  state.selectedModel = model;
  state.selectedFile = model.files.find((file) => file.name === "systemprompt.md")?.name || model.files[0]?.name || "systemprompt.md";
  setText("model-title", model.name);
  setText("model-description", model.description || model.id);
  renderModels();
  renderFileTabs();
  await loadFile(state.selectedFile);
}

async function loadFile(name) {
  if (!state.selectedModel) return;
  state.selectedFile = name;
  renderFileTabs();
  setText("editor-state", "Lade Datei");
  const payload = await api(`/api/models/${encodeURIComponent(state.selectedModel.id)}/file?name=${encodeURIComponent(name)}`);
  el("markdown-editor").disabled = false;
  el("markdown-editor").value = payload.content;
  updateModelPreview();
  el("save-file").disabled = false;
  state.dirty = false;
  setText("editor-state", payload.exists ? `${payload.path} geladen` : `${payload.path} neu`);
}

async function saveResource() {
  if (!state.selectedResource) return;
  el("save-resource").disabled = true;
  setText("resource-state", "Speichere");
  try {
    const payload = await api(
      `/api/resources/${encodeURIComponent(state.selectedResource.kind)}/${encodeURIComponent(state.selectedResource.id)}/file`,
      {
        method: "PUT",
        body: JSON.stringify({ content: el("resource-editor").value }),
      },
    );
    setText("resource-state", `${payload.path} gespeichert`);
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
  setText("editor-state", "Speichere");
  try {
    const payload = await api(`/api/models/${encodeURIComponent(state.selectedModel.id)}/file`, {
      method: "PUT",
      body: JSON.stringify({ name: state.selectedFile, content: el("markdown-editor").value }),
    });
    state.dirty = false;
    setText("editor-state", `${payload.path} gespeichert`);
    await refreshModels(false);
  } catch (error) {
    setText("editor-state", error.message);
  } finally {
    el("save-file").disabled = false;
  }
}

async function runAction(action) {
  const log = el("action-log");
  log.textContent = `Starte ${action} ...`;
  try {
    const result = await api(`/api/actions/${encodeURIComponent(action)}`, { method: "POST", body: "{}" });
    log.textContent = `$ ${result.command.join(" ")}\n\nExit-Code: ${result.returncode}\nDauer: ${result.duration_seconds}s\n\n${result.output}`;
    await refreshStatus();
    await refreshModels(false);
    await refreshResources(false);
  } catch (error) {
    log.textContent += `\n\nFehler: ${error.message}`;
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
  renderResources();
}

async function refreshModels(keepSelection = true) {
  const payload = await api("/api/models");
  const previous = state.selectedModel?.id;
  state.models = payload.models;
  if (keepSelection && previous) {
    state.selectedModel = state.models.find((model) => model.id === previous) || null;
  }
  renderModels();
}

function wireEvents() {
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".nav-item").forEach((item) => item.classList.remove("active"));
      document.querySelectorAll(".panel").forEach((panel) => panel.classList.remove("active"));
      button.classList.add("active");
      el(`panel-${button.dataset.panel}`).classList.add("active");
    });
  });
  el("model-search").addEventListener("input", renderModels);
  el("resource-search").addEventListener("input", renderResources);
  el("markdown-editor").addEventListener("input", () => {
    state.dirty = true;
    updateModelPreview();
    setText("editor-state", "Ungespeicherte Änderung");
  });
  el("resource-editor").addEventListener("input", () => {
    updateResourcePreview();
    setText("resource-state", "Ungespeicherte Änderung");
  });
  document.querySelectorAll(".view-mode").forEach((button) => {
    button.addEventListener("click", () => applyView(button.dataset.editor, button.dataset.mode));
  });
  el("theme-toggle").addEventListener("click", () => {
    applyTheme(document.body.classList.contains("light-theme") ? "dark" : "light");
  });
  el("save-file").addEventListener("click", saveFile);
  el("save-resource").addEventListener("click", saveResource);
  document.querySelectorAll("[data-action]").forEach((button) => {
    button.addEventListener("click", () => runAction(button.dataset.action));
  });
  el("clear-log").addEventListener("click", () => {
    el("action-log").textContent = "Noch keine Aktion ausgeführt.";
  });
}

async function init() {
  applyTheme(localStorage.getItem("workbench-theme") || "dark");
  applyView("model", state.modelView);
  applyView("resource", state.resourceView);
  wireEvents();
  await refreshStatus();
  await refreshModels(false);
  await refreshResources(false);
  if (state.models.length > 0) {
    await selectModel(state.models[0].id);
  }
}

init().catch((error) => {
  document.body.innerHTML = `<main class="main"><pre>${error.message}</pre></main>`;
});
