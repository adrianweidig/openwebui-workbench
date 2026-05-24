const state = {
  status: null,
  models: [],
  resources: [],
  selectedModel: null,
  selectedFile: "systemprompt.md",
  selectedResource: null,
  dirty: false,
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
  setText("config-token", status.openwebui.admin_token_configured ? "gesetzt" : "nicht gesetzt");
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
    setText("editor-state", "Ungespeicherte Änderung");
  });
  el("resource-editor").addEventListener("input", () => {
    setText("resource-state", "Ungespeicherte Änderung");
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
