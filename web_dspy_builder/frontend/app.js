const { LiteGraph } = window;

registerNodes();

const graph = new LiteGraph.LGraph();
const canvas = new LiteGraph.LGraphCanvas("#graph-canvas", graph);
canvas.ds.scale = 1.1;
canvas.background_image = "";

const state = {
  socket: null,
  pendingMessages: [],
  selectedNode: null,
  selectedRunId: null,
  currentRunId: null,
  runs: [],
  edgeData: {},
  loopEditorGraph: new LiteGraph.LGraph(),
  loopCanvas: null,
  loopEditingNode: null,
};

const paletteEl = document.getElementById("node-palette");
const inspectorEl = document.getElementById("inspector-content");
const edgeDataEl = document.getElementById("edge-data");
const logEl = document.getElementById("log-output");
const runHistoryEl = document.getElementById("run-history");
const runButton = document.getElementById("run-button");
const replayButton = document.getElementById("replay-button");
const clearHistoryButton = document.getElementById("clear-history");
const statusIndicator = document.getElementById("status-indicator");
const loopOverlay = document.getElementById("loop-editor");
const loopSaveButton = document.getElementById("loop-save");
const loopCancelButton = document.getElementById("loop-cancel");
const programSelector = document.getElementById("program-selector");
const loadProgramButton = document.getElementById("load-program");

const DEFAULT_PROGRAM_KEY = "typed-cognition";
const PROGRAM_SAMPLES = {
  "typed-cognition": {
    label: "Typed Cognition Agent",
    build: buildCognitionProgram,
  },
  "llm-echo": {
    label: "LLM Echo Starter",
    build: buildLinearProgram,
  },
};

state.loopCanvas = new LiteGraph.LGraphCanvas("#loop-canvas", state.loopEditorGraph);
state.loopCanvas.ds.scale = 1;
state.loopCanvas.background_image = "";

createPalette();
attachCanvasEvents();
connectSocket();
populateProgramSelector();
attachProgramHandlers();
restoreGraphFromStorage();
createSampleGraphIfEmpty();
attachToolbarHandlers();
resizeCanvases();
window.addEventListener("resize", resizeCanvases);

drawEdgeLabels(canvas);

graph.onNodeAdded = persistGraph;
graph.onNodeRemoved = persistGraph;
graph.onNodeConnectionChange = persistGraph;

function registerNodes() {
  function ensureUniquePortNames(node) {
    if (node.inputs) {
      node.inputs.forEach((slot, index) => {
        if (!slot.name) slot.name = `in${index}`;
      });
    }
    if (node.outputs) {
      node.outputs.forEach((slot, index) => {
        if (!slot.name) slot.name = `out${index}`;
      });
    }
  }

  function InputNode() {
    this.title = "Input";
    this.properties = { value: "", values: {} };
    this.addOutput("value", "string");
  }
  InputNode.title = "Input";
  InputNode.desc = "Static input value";
  InputNode.prototype.onConfigure = function () {
    ensureUniquePortNames(this);
  };
  LiteGraph.registerNodeType("dspy/input", InputNode);

  function LLMNode() {
    this.title = "LLM";
    this.properties = {
      prompt: "Respond to: {{text}}",
      stop: "",
    };
    this.addInput("text", "string");
    this.addOutput("response", "string");
  }
  LLMNode.title = "LLM";
  LLMNode.prototype.onConfigure = function () {
    ensureUniquePortNames(this);
  };
  LiteGraph.registerNodeType("dspy/llm", LLMNode);
  LiteGraph.registerNodeType("dspy/prompt", LLMNode);

  function PythonNode() {
    this.title = "Python";
    this.properties = {
      code: "# inputs is a dict with incoming data\noutputs.result = inputs.get('value')",
    };
    this.addInput("value", "");
    this.addOutput("result", "");
  }
  PythonNode.title = "Python";
  PythonNode.prototype.onConfigure = function () {
    ensureUniquePortNames(this);
  };
  LiteGraph.registerNodeType("dspy/python", PythonNode);

  function OutputNode() {
    this.title = "Output";
    this.properties = { label: "result" };
    this.addInput("value", "");
  }
  OutputNode.title = "Output";
  OutputNode.prototype.onConfigure = function () {
    ensureUniquePortNames(this);
  };
  LiteGraph.registerNodeType("dspy/output", OutputNode);

  function LoopNode() {
    this.title = "Loop";
    this.properties = {
      loopOutputs: [
        { node: "loopOutput", port: "value", target: "results" },
      ],
      bodyGraph: null,
    };
    this.addInput("items", "array");
    this.addOutput("results", "array");
  }
  LoopNode.title = "Loop";
  LoopNode.prototype.onConfigure = function () {
    ensureUniquePortNames(this);
  };
  LiteGraph.registerNodeType("dspy/loop", LoopNode);

  function LoopInputNode() {
    this.title = "Loop Input";
    this.properties = { binding: "items" };
    this.addOutput("item", "");
  }
  LoopInputNode.title = "Loop Input";
  LoopInputNode.desc = "Expose an external value inside a loop body";
  LoopInputNode.prototype.onConfigure = function () {
    ensureUniquePortNames(this);
  };
  LiteGraph.registerNodeType("dspy/loopInput", LoopInputNode);

  function LoopOutputNode() {
    this.title = "Loop Output";
    this.properties = { target: "results", port: "value" };
    this.addInput("value", "");
  }
  LoopOutputNode.title = "Loop Output";
  LoopOutputNode.prototype.onConfigure = function () {
    ensureUniquePortNames(this);
  };
  LiteGraph.registerNodeType("dspy/loopOutput", LoopOutputNode);

  function CognitionNode() {
    this.title = "Cognition Agent";
    this.properties = {
      observation: "",
      episodic_memory: "",
      goals: "",
      constraints: "",
      utility_def: "",
      prior_belief: "",
      attention_results: "",
      system_events: "",
    };
    this.addInput("observation", "");
    this.addInput("episodic_memory", "");
    this.addInput("goals", "");
    this.addInput("constraints", "");
    this.addInput("utility_def", "");
    this.addInput("prior_belief", "");
    this.addInput("attention_results", "");
    this.addInput("system_events", "");
    this.addOutput("percept", "");
    this.addOutput("belief", "");
    this.addOutput("affect", "");
    this.addOutput("plans", "");
    this.addOutput("scored", "");
    this.addOutput("decision", "");
    this.addOutput("verification", "");
    this.addOutput("outcome", "");
    this.addOutput("update", "");
  }
  CognitionNode.title = "Cognition Agent";
  CognitionNode.desc = "Run the typed cognition DSPy pipeline";
  CognitionNode.prototype.onConfigure = function () {
    ensureUniquePortNames(this);
  };
  LiteGraph.registerNodeType("dspy/cognition", CognitionNode);
}

function createPalette() {
  const nodes = [
    { type: "dspy/input", label: "Input" },
    { type: "dspy/llm", label: "LLM" },
    { type: "dspy/python", label: "Python" },
    { type: "dspy/output", label: "Output" },
    { type: "dspy/loop", label: "Loop" },
    { type: "dspy/cognition", label: "Cognition Agent" },
  ];
  nodes.forEach((entry) => {
    const button = document.createElement("button");
    button.textContent = entry.label;
    button.dataset.nodeType = entry.type;
    button.addEventListener("click", () => addNodeToGraph(entry.type));
    paletteEl.appendChild(button);
  });
}

function addNodeToGraph(type) {
  const node = LiteGraph.createNode(type);
  if (!node) return;
  node.pos = canvas.convertEventToCanvas([window.innerWidth * 0.3, window.innerHeight * 0.3]);
  graph.add(node);
  graph.setDirtyCanvas(true, true);
  persistGraph();
}

function attachCanvasEvents() {
  canvas.onNodeSelected = (node) => {
    state.selectedNode = node;
    updateInspector(node);
    replayButton.disabled = !(node && state.selectedRunId);
  };
  canvas.onNodeDeselected = () => {
    state.selectedNode = null;
    updateInspector(null);
    replayButton.disabled = !state.selectedRunId;
  };

  graph.onAfterExecute = () => {
    persistGraph();
  };
}

function attachToolbarHandlers() {
  runButton.addEventListener("click", () => {
    const request = buildRunRequest("run");
    state.currentRunId = request.run_id;
    sendMessage(request);
  });

  replayButton.addEventListener("click", () => {
    if (!state.selectedRunId || !state.selectedNode) return;
    const request = buildRunRequest("replay");
    request.base_run_id = state.selectedRunId;
    request.start_node = String(state.selectedNode.id);
    state.currentRunId = request.run_id;
    sendMessage(request);
  });

  clearHistoryButton.addEventListener("click", () => {
    state.runs = [];
    state.selectedRunId = null;
    renderRunHistory();
    replayButton.disabled = true;
  });

  loopSaveButton.addEventListener("click", saveLoopBody);
  loopCancelButton.addEventListener("click", closeLoopOverlay);
}

function resizeCanvases() {
  canvas.resize();
  state.loopCanvas.resize();
}

function connectSocket() {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const url = `${protocol}://${window.location.host}/ws`;
  const socket = new WebSocket(url);
  state.socket = socket;
  setStatus("Connecting to server...");

  socket.onopen = () => {
    setStatus("Connected");
    while (state.pendingMessages.length) {
      socket.send(state.pendingMessages.shift());
    }
  };

  socket.onmessage = (event) => {
    const payload = JSON.parse(event.data);
    handleEvent(payload);
  };

  socket.onclose = () => {
    setStatus("Disconnected. Reconnecting...");
    state.socket = null;
    setTimeout(connectSocket, 1500);
  };

  socket.onerror = () => {
    setStatus("WebSocket error");
  };
}

function buildRunRequest(action) {
  const graphSpec = normalizeGraph(graph.serialize());
  const runId = crypto.randomUUID();
  return {
    action,
    graph: graphSpec,
    run_id: runId,
    settings: gatherSettings(),
    overrides: {},
  };
}

function gatherSettings() {
  const engineEl = document.getElementById("llm-engine");
  const modelEl = document.getElementById("llm-model");
  const tempEl = document.getElementById("llm-temperature");
  const maxEl = document.getElementById("llm-max-tokens");
  return {
    llm: {
      engine: engineEl.value,
      model: modelEl.value || null,
      temperature: parseFloat(tempEl.value || "0"),
      max_tokens: parseInt(maxEl.value || "2048", 10),
      params: {},
    },
    allow_cache_reuse: true,
  };
}

function sendMessage(data) {
  const payload = JSON.stringify(data);
  if (state.socket && state.socket.readyState === WebSocket.OPEN) {
    state.socket.send(payload);
  } else {
    state.pendingMessages.push(payload);
  }
}

function handleEvent(event) {
  switch (event.type) {
    case "run_started":
      state.currentRunId = event.runId;
      resetRunVisuals();
      setStatus(`Run ${event.runId} started`);
      break;
    case "node_start":
      highlightNode(event.nodeId, "start");
      break;
    case "node_end":
      highlightNode(event.nodeId, "end");
      if (event.outputs) {
        const node = graph.getNodeById(Number(event.nodeId));
        if (node) {
          node.properties.__lastOutputs = event.outputs;
        }
      }
      break;
    case "node_cached":
      highlightNode(event.nodeId, "cached");
      break;
    case "node_log":
      appendLog(`[${event.nodeId}] ${event.log}`);
      break;
    case "edge_data":
      registerEdgeData(event);
      break;
    case "run_complete":
      setStatus(`Run ${event.runId} complete`);
      appendRunHistory(event);
      break;
    case "subgraph_started":
    case "subgraph_complete":
      // handled implicitly via edge_data events
      break;
    case "subgraph_error":
      appendLog(`Subgraph error: ${event.message}`);
      break;
    case "run_error":
      setStatus(`Error: ${event.message}`);
      appendLog(`ERROR: ${event.message}`);
      break;
    default:
      break;
  }
  canvas.draw(true, true);
}

function highlightNode(nodeId, mode) {
  const node = graph.getNodeById(Number(nodeId));
  if (!node) return;
  if (mode === "start") {
    node.boxcolor = "#4fa3ff";
  } else if (mode === "end") {
    node.boxcolor = null;
  } else if (mode === "cached") {
    node.boxcolor = "#3cb371";
  }
}

function registerEdgeData(event) {
  const id = event.edgeId;
  const existing = state.edgeData[id] || { history: [] };
  existing.history.push({
    value: event.value,
    iteration: event.iteration,
    cached: event.cached,
    timestamp: event.timestamp,
  });
  if (existing.history.length > 10) {
    existing.history.shift();
  }
  existing.latest = existing.history[existing.history.length - 1];
  state.edgeData[id] = existing;
  updateEdgePanel();
}

function updateEdgePanel() {
  edgeDataEl.innerHTML = "";
  const entries = Object.entries(state.edgeData);
  if (!entries.length) {
    edgeDataEl.textContent = "No edge transmissions yet.";
    return;
  }
  entries.forEach(([edgeId, info]) => {
    const wrapper = document.createElement("div");
    wrapper.className = "edge-entry";
    const title = document.createElement("div");
    title.textContent = `Edge ${edgeId}`;
    wrapper.appendChild(title);
    info.history.slice().reverse().forEach((item) => {
      const row = document.createElement("div");
      row.textContent = formatEdgeValue(item);
      wrapper.appendChild(row);
    });
    edgeDataEl.appendChild(wrapper);
  });
}

function formatEdgeValue(item) {
  const value = formatValue(item.value);
  const iter = item.iteration !== null && item.iteration !== undefined ? `iter ${item.iteration} · ` : "";
  const cached = item.cached ? "cached · " : "";
  return `${iter}${cached}${value}`;
}

function formatValue(value) {
  if (value === null || value === undefined) return "<empty>";
  if (typeof value === "object") {
    try {
      const text = JSON.stringify(value);
      return text.length > 140 ? `${text.slice(0, 140)}…` : text;
    } catch (err) {
      return String(value);
    }
  }
  const text = String(value);
  return text.length > 140 ? `${text.slice(0, 140)}…` : text;
}

function appendLog(message) {
  const timestamp = new Date().toLocaleTimeString();
  logEl.textContent += `[${timestamp}] ${message}\n`;
  logEl.scrollTop = logEl.scrollHeight;
}

function appendRunHistory(event) {
  state.runs.unshift({
    runId: event.runId,
    outputs: event.outputs,
    startedAt: new Date().toISOString(),
  });
  renderRunHistory();
}

function renderRunHistory() {
  runHistoryEl.innerHTML = "";
  if (!state.runs.length) {
    const li = document.createElement("li");
    li.textContent = "No runs yet";
    li.style.opacity = "0.7";
    runHistoryEl.appendChild(li);
    return;
  }
  state.runs.forEach((run) => {
    const li = document.createElement("li");
    li.dataset.runId = run.runId;
    li.textContent = `${run.runId.slice(0, 8)} · ${new Date(run.startedAt).toLocaleTimeString()}`;
    if (run.runId === state.selectedRunId) {
      li.classList.add("active");
    }
    li.addEventListener("click", () => {
      state.selectedRunId = run.runId;
      replayButton.disabled = !state.selectedNode;
      renderRunHistory();
    });
    runHistoryEl.appendChild(li);
  });
}

function resetRunVisuals() {
  state.edgeData = {};
  updateEdgePanel();
  logEl.textContent = "";
  graph._nodes.forEach((node) => {
    node.boxcolor = null;
  });
}

function updateInspector(node) {
  inspectorEl.innerHTML = "";
  if (!node) {
    inspectorEl.textContent = "Select a node to edit its properties.";
    return;
  }

  const titleField = document.createElement("div");
  titleField.className = "property-field";
  const titleLabel = document.createElement("label");
  titleLabel.textContent = "Node title";
  const titleInput = document.createElement("input");
  titleInput.value = node.title || "";
  titleInput.addEventListener("input", () => {
    node.title = titleInput.value;
    graph.setDirtyCanvas(true, true);
  });
  titleField.append(titleLabel, titleInput);
  inspectorEl.appendChild(titleField);

  const typeDisplay = document.createElement("div");
  typeDisplay.textContent = `Type: ${node.type}`;
  typeDisplay.style.fontSize = "0.85rem";
  typeDisplay.style.opacity = "0.7";
  inspectorEl.appendChild(typeDisplay);

  Object.entries(node.properties || {}).forEach(([key, value]) => {
    if (key.startsWith("__")) return;
    const field = document.createElement("div");
    field.className = "property-field";
    const label = document.createElement("label");
    label.textContent = key;
    let editor;
    if (typeof value === "string" || typeof value === "number") {
      editor = document.createElement(typeof value === "number" ? "input" : "textarea");
      if (typeof value === "number") {
        editor.type = "number";
        editor.value = value;
      } else {
        editor.value = value;
      }
    } else {
      editor = document.createElement("textarea");
      editor.value = JSON.stringify(value, null, 2);
    }
    editor.addEventListener("change", () => {
      try {
        if (typeof value === "string") {
          node.properties[key] = editor.value;
        } else if (typeof value === "number") {
          node.properties[key] = parseFloat(editor.value || "0");
        } else {
          node.properties[key] = JSON.parse(editor.value || "null");
        }
        persistGraph();
      } catch (err) {
        alert(`Invalid value for ${key}`);
      }
    });
    field.append(label, editor);
    inspectorEl.appendChild(field);
  });

  const portsSection = document.createElement("div");
  portsSection.className = "port-list";
  const inputsHeader = document.createElement("strong");
  inputsHeader.textContent = "Inputs";
  portsSection.appendChild(inputsHeader);
  (node.inputs || []).forEach((slot, index) => {
    const row = document.createElement("div");
    row.className = "port-item";
    const input = document.createElement("input");
    input.value = slot.name || `in${index}`;
    input.addEventListener("change", () => {
      slot.name = input.value || `in${index}`;
      graph.setDirtyCanvas(true, true);
    });
    const remove = document.createElement("button");
    remove.textContent = "Remove";
    remove.className = "small-button";
    remove.addEventListener("click", () => {
      node.removeInput(index);
      updateInspector(node);
      persistGraph();
    });
    row.append(input, remove);
    portsSection.appendChild(row);
  });

  const addInputButton = document.createElement("button");
  addInputButton.textContent = "Add input";
  addInputButton.className = "small-button";
  addInputButton.addEventListener("click", () => {
    const name = prompt("Input name?") || `input${(node.inputs || []).length}`;
    node.addInput(name, "");
    updateInspector(node);
    persistGraph();
  });
  portsSection.appendChild(addInputButton);

  const outputsHeader = document.createElement("strong");
  outputsHeader.textContent = "Outputs";
  portsSection.appendChild(outputsHeader);
  (node.outputs || []).forEach((slot, index) => {
    const row = document.createElement("div");
    row.className = "port-item";
    const input = document.createElement("input");
    input.value = slot.name || `out${index}`;
    input.addEventListener("change", () => {
      slot.name = input.value || `out${index}`;
      graph.setDirtyCanvas(true, true);
    });
    const remove = document.createElement("button");
    remove.textContent = "Remove";
    remove.className = "small-button";
    remove.addEventListener("click", () => {
      node.removeOutput(index);
      updateInspector(node);
      persistGraph();
    });
    row.append(input, remove);
    portsSection.appendChild(row);
  });

  const addOutputButton = document.createElement("button");
  addOutputButton.textContent = "Add output";
  addOutputButton.className = "small-button";
  addOutputButton.addEventListener("click", () => {
    const name = prompt("Output name?") || `output${(node.outputs || []).length}`;
    node.addOutput(name, "");
    updateInspector(node);
    persistGraph();
  });
  portsSection.appendChild(addOutputButton);

  inspectorEl.appendChild(portsSection);

  if (node.type === "dspy/loop") {
    const editLoopButton = document.createElement("button");
    editLoopButton.textContent = "Edit loop body";
    editLoopButton.addEventListener("click", () => openLoopEditor(node));
    inspectorEl.appendChild(editLoopButton);
  }
}

function openLoopEditor(node) {
  state.loopEditingNode = node;
  state.loopEditorGraph.clear();
  const body = node.properties.bodyGraph;
  if (body) {
    state.loopEditorGraph.configure(body);
  } else {
    const input = LiteGraph.createNode("dspy/loopInput");
    input.pos = [60, 120];
    const python = LiteGraph.createNode("dspy/python");
    python.pos = [260, 120];
    const output = LiteGraph.createNode("dspy/loopOutput");
    output.pos = [500, 120];
    state.loopEditorGraph.add(input);
    state.loopEditorGraph.add(python);
    state.loopEditorGraph.add(output);
  }
  loopOverlay.classList.remove("hidden");
  state.loopEditorGraph.start();
  state.loopCanvas.draw(true, true);
}

function saveLoopBody() {
  if (!state.loopEditingNode) return;
  const serialized = state.loopEditorGraph.serialize();
  state.loopEditingNode.properties.bodyGraph = serialized;
  state.loopEditingNode.properties.loopOutputs = extractLoopOutputs(serialized);
  closeLoopOverlay();
  persistGraph();
  updateInspector(state.loopEditingNode);
}

function extractLoopOutputs(graphData) {
  const outputs = [];
  (graphData.nodes || []).forEach((node) => {
    if (node.type === "dspy/loopOutput") {
      const portName = node.inputs && node.inputs[0] ? node.inputs[0].name || "value" : "value";
      const target = node.properties?.target || portName;
      outputs.push({ node: String(node.id), port: portName, target });
    }
  });
  return outputs;
}

function closeLoopOverlay() {
  loopOverlay.classList.add("hidden");
  state.loopEditorGraph.stop();
  state.loopEditingNode = null;
}

function setStatus(message) {
  statusIndicator.textContent = message;
}

function persistGraph() {
  localStorage.setItem("dspy-graph", JSON.stringify(graph.serialize()));
}

function restoreGraphFromStorage() {
  const stored = localStorage.getItem("dspy-graph");
  if (!stored) return;
  try {
    const data = JSON.parse(stored);
    graph.configure(data);
  } catch (err) {
    console.warn("Failed to restore graph", err);
  }
}

function populateProgramSelector() {
  if (!programSelector) return;
  programSelector.innerHTML = "";
  Object.entries(PROGRAM_SAMPLES).forEach(([key, sample], index) => {
    const option = document.createElement("option");
    option.value = key;
    option.textContent = sample.label;
    if (index === 0 && !DEFAULT_PROGRAM_KEY) {
      option.selected = true;
    }
    programSelector.appendChild(option);
  });
  if (PROGRAM_SAMPLES[DEFAULT_PROGRAM_KEY]) {
    programSelector.value = DEFAULT_PROGRAM_KEY;
  }
}

function attachProgramHandlers() {
  if (!loadProgramButton) return;
  loadProgramButton.addEventListener("click", () => {
    const selected = programSelector ? programSelector.value : null;
    if (!selected) return;
    if (graph._nodes && graph._nodes.length) {
      const confirmed = window.confirm(
        "Replace the current graph with the selected template?"
      );
      if (!confirmed) {
        return;
      }
    }
    loadProgramSample(selected);
  });
}

function loadProgramSample(key, options = {}) {
  const sample = PROGRAM_SAMPLES[key];
  if (!sample || typeof sample.build !== "function") return;
  const { persist = true } = options;

  graph.clear();
  state.selectedNode = null;
  updateInspector(null);
  state.edgeData = {};
  updateEdgePanel();
  logEl.textContent = "";

  sample.build(graph);

  if (programSelector) {
    programSelector.value = key;
  }

  graph.setDirtyCanvas(true, true);
  canvas.draw(true, true);
  if (persist) {
    persistGraph();
  }
}

function buildCognitionProgram(targetGraph) {
  const baseX = 60;
  const baseY = 80;
  const spacingY = 90;
  const inputDefinitions = [
    {
      key: "observation",
      title: "Observation",
      value: "Operator reports debris blocking the main walkway.",
    },
    {
      key: "episodic_memory",
      title: "Episodic Memory",
      value: "Previous shift cleared similar debris using lift equipment.",
    },
    {
      key: "goals",
      title: "Goals",
      value: "Restore safe passage while keeping staff injury risk low.",
    },
    {
      key: "constraints",
      title: "Constraints",
      value: "Respect maintenance window and avoid exceeding overtime budget.",
    },
    {
      key: "utility_def",
      title: "Utility Definition",
      value: "Prioritize safety over throughput while minimizing costs.",
    },
    {
      key: "prior_belief",
      title: "Prior Belief",
      value: "Crew is trained for debris removal tasks.",
    },
    {
      key: "attention_results",
      title: "Attention",
      value: "Sensors highlight moderate obstruction; forklift available.",
    },
    {
      key: "system_events",
      title: "System Events",
      value: "No critical alarms; ventilation nominal.",
    },
  ];

  const inputNodes = inputDefinitions.map((entry, index) => {
    const node = LiteGraph.createNode("dspy/input");
    node.title = entry.title;
    node.pos = [baseX, baseY + index * spacingY];
    node.properties.value = entry.value;
    targetGraph.add(node);
    return { entry, node };
  });

  const cognition = LiteGraph.createNode("dspy/cognition");
  cognition.pos = [360, baseY + 3 * spacingY];
  cognition.properties = cognition.properties || {};
  inputNodes.forEach(({ entry }, index) => {
    cognition.properties[entry.key] = entry.value;
    inputNodes[index].node.connect(0, cognition, index);
  });
  targetGraph.add(cognition);

  const outputs = [
    { title: "Percept", port: 0, label: "percept", pos: [720, baseY] },
    { title: "Plans", port: 3, label: "plans", pos: [720, baseY + spacingY] },
    { title: "Decision", port: 5, label: "decision", pos: [720, baseY + spacingY * 2] },
    { title: "Outcome", port: 7, label: "outcome", pos: [720, baseY + spacingY * 3] },
    { title: "Update", port: 8, label: "update", pos: [720, baseY + spacingY * 4] },
  ];

  outputs.forEach(({ title, port, label, pos }) => {
    const outputNode = LiteGraph.createNode("dspy/output");
    outputNode.title = title;
    outputNode.pos = pos;
    outputNode.properties.label = label;
    if (outputNode.inputs && outputNode.inputs[0]) {
      outputNode.inputs[0].name = label;
    }
    targetGraph.add(outputNode);
    cognition.connect(port, outputNode, 0);
  });
}

function buildLinearProgram(targetGraph) {
  const input = LiteGraph.createNode("dspy/input");
  input.pos = [60, 160];
  input.properties.value = "Hello DSPy";
  const llm = LiteGraph.createNode("dspy/llm");
  llm.pos = [320, 140];
  const output = LiteGraph.createNode("dspy/output");
  output.pos = [600, 150];
  targetGraph.add(input);
  targetGraph.add(llm);
  targetGraph.add(output);
  input.connect(0, llm, 0);
  llm.connect(0, output, 0);
}

function createSampleGraphIfEmpty() {
  if (graph._nodes && graph._nodes.length) return;
  loadProgramSample(DEFAULT_PROGRAM_KEY);
}

function normalizeGraph(data) {
  const nodesArray = Array.isArray(data.nodes) ? data.nodes : Object.values(data.nodes || {});
  const linksArray = Array.isArray(data.links) ? data.links : Object.values(data.links || {});
  const nodeMap = new Map();
  nodesArray.forEach((node) => nodeMap.set(node.id, node));
  const nodes = nodesArray.map((node) => {
    const typeParts = typeof node.type === "string" ? node.type.split("/") : [node.type];
    const type = typeParts[typeParts.length - 1];
    const config = { ...(node.properties || {}) };
    if (config.bodyGraph) {
      config.bodyGraph = normalizeGraph(config.bodyGraph);
    }
    return {
      id: String(node.id),
      type,
      label: node.title || "",
      config,
      ports: {
        inputs: (node.inputs || []).map((slot, idx) => slot.name || `in${idx}`),
        outputs: (node.outputs || []).map((slot, idx) => slot.name || `out${idx}`),
      },
    };
  });

  const edges = linksArray.map((link) => {
    const sourceNode = nodeMap.get(link.origin_id);
    const targetNode = nodeMap.get(link.target_id);
    const sourcePort = sourceNode?.outputs?.[link.origin_slot]?.name || `out${link.origin_slot}`;
    const targetPort = targetNode?.inputs?.[link.target_slot]?.name || `in${link.target_slot}`;
    return {
      id: String(link.id),
      source: { node: String(link.origin_id), port: sourcePort },
      target: { node: String(link.target_id), port: targetPort },
    };
  });

  return {
    id: data.config?.id || null,
    nodes,
    edges,
    metadata: data.config || {},
  };
}

function drawEdgeLabels(canvasInstance) {
  const originalDrawBack = canvasInstance.drawBack;
  canvasInstance.drawBack = function (ctx) {
    if (originalDrawBack) originalDrawBack.call(this, ctx);
    ctx.save();
    ctx.font = "12px 'Fira Code', monospace";
    ctx.fillStyle = "rgba(230, 233, 255, 0.8)";
    Object.entries(state.edgeData).forEach(([edgeId, info]) => {
      const link = this.graph.links[Number(edgeId)];
      if (!link || !info.latest) return;
      const originNode = this.graph.getNodeById(link.origin_id);
      const targetNode = this.graph.getNodeById(link.target_id);
      if (!originNode || !targetNode) return;
      const a = originNode.getConnectionPos(false, link.origin_slot, [0, 0]);
      const b = targetNode.getConnectionPos(true, link.target_slot, [0, 0]);
      const x = (a[0] + b[0]) / 2;
      const y = (a[1] + b[1]) / 2;
      const label = formatEdgeValue(info.latest);
      ctx.fillText(label, x, y);
    });
    ctx.restore();
  };
}

