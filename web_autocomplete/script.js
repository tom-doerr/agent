/* -----------------------------------------------------------
 *  Global constants & state
 * --------------------------------------------------------- */
const MODEL_ID = "google/gemini-2.5-flash-lite-preview-06-17";
const ENDPOINT = "https://openrouter.ai/api/v1/chat/completions";

const MAX_TREE_DEPTH   = 5;     // hard cap on expansion depth
const MAX_TOTAL_NODES  = 500;   // guard DOM & cost
const RATE_LIMIT_MS    = 500;   // min gap between any two API calls

let totalNodeCount     = 0;
let lastRequestAt      = 0;
let nodeIdSeq          = 0;     // incremental id for ARIA & AbortControllers

/* -----------------------------------------------------------
 *  DOM handles
 * --------------------------------------------------------- */
const apiKeyInput   = $("#apiKey");
const maxTokInput   = $("#maxTokens");
const nCompInput    = $("#nCompletions");
const reqPerNodeInp = $("#reqPerNode");
const promptBox     = $("#prompt");
const seedBtn       = $("#seedBtn");
const treeContainer = $("#treeContainer");
const liveStatus    = $("#live");
const helpDialog    = $("#helpDialog");

/* Helpers */
function $(sel){ return document.querySelector(sel); }
function announce(msg){ liveStatus.textContent = msg; }

/* -----------------------------------------------------------
 *  Tokeniser — punctuation‑aware, falls back to whitespace
 * --------------------------------------------------------- */
const segmenter = (typeof Intl !== "undefined" && Intl.Segmenter)
  ? new Intl.Segmenter("en", { granularity: "word" })
  : null;

function splitTokens(text){
  if (segmenter){
    return [...segmenter.segment(text)]
      .filter(seg => seg.isWordLike)
      .map(seg => seg.segment);
  }
  // Fallback
  return text.trim().split(/(\s+|[,.!?;:])/g).filter(Boolean);
}

/* -----------------------------------------------------------
 *  Build collapsed‑prefix tree
 * --------------------------------------------------------- */
function buildTree(completions){
  const root = { text:"", children:[], freq:completions.length, depth:0 };

  function recurse(tokensArr, prefixTokens, depth){
    if (!tokensArr.length || depth >= MAX_TREE_DEPTH) return [];

    // Group by first token
    const groups={};
    tokensArr.forEach(toks=>{
      const head = toks[0] || "";
      (groups[head]=groups[head]||[]).push(toks.slice(1));
    });

    const nodes=[];
    for (const [tok, tails] of Object.entries(groups)){
      const nodeTokens = [...prefixTokens, tok];
      const node={ text: nodeTokens.join(" "),
                   children: [],
                   freq: tails.length,
                   depth };
      node.children = recurse(tails.filter(t=>t.length), nodeTokens, depth+1);
      nodes.push(node);
    }
    nodes.sort((a,b)=>b.freq - a.freq);
    return nodes;
  }

  const tokenised = completions.map(splitTokens);
  root.children = recurse(tokenised, [], 1);
  return root;
}

/* -----------------------------------------------------------
 *  Rendering & focus management (roving focus)
 * --------------------------------------------------------- */
function renderTree(root){
  treeContainer.innerHTML="";
  totalNodeCount = 0;
  root.children.forEach(child => renderNode(child, treeContainer, 1));
  // Focus first node
  const first = treeContainer.querySelector(".node");
  setFocus(first);
}

function renderNode(node, parentEl, ariaLevel){
  if (totalNodeCount >= MAX_TOTAL_NODES) return;
  totalNodeCount++;

  // Create node element
  const el = document.createElement("div");
  el.className = "node";
  el.textContent = node.text;
  el.dataset.fullText = node.text;
  el.dataset.depth = node.depth;
  el.id = `n${++nodeIdSeq}`;

  // ARIA
  el.setAttribute("role","treeitem");
  el.setAttribute("aria-level", ariaLevel);
  el.setAttribute("aria-expanded", "false");
  el.setAttribute("tabindex", "-1");

  // Accept on Enter / Space (handled globally)
  // Generate on focus if leaf
  el.addEventListener("focus", () => {
    if (!el.dataset.expanded){
      if (parseInt(node.depth,10) < MAX_TREE_DEPTH){
        debounceExpand(el);
      }
    }
  });

  parentEl.appendChild(el);

  if (node.children.length){
    const childWrap = document.createElement("div");
    childWrap.className="children";
    childWrap.setAttribute("role","group");
    el.appendChild(childWrap);

    node.children.forEach(child => renderNode(child, childWrap, ariaLevel+1));
  }
}

/* -----------------------------------------------------------
 *  Roving focus utility
 * --------------------------------------------------------- */
function setFocus(el){
  if (!el) return;
  const prev = treeContainer.querySelector('.node[tabindex="0"]');
  if (prev) prev.setAttribute("tabindex","-1");
  el.setAttribute("tabindex","0");
  el.focus({preventScroll:false});
}

/* -----------------------------------------------------------
 *  Keyboard navigation
 * --------------------------------------------------------- */
treeContainer.addEventListener("keydown", e=>{
  const current = treeContainer.querySelector('.node[tabindex="0"]');
  if (!current) return;

  switch(e.key){
    case "ArrowDown": e.preventDefault(); focusSibling(current, 1); break;
    case "ArrowUp":   e.preventDefault(); focusSibling(current,-1); break;
    case "Tab":
      e.preventDefault();
      focusNextVisible(current, !e.shiftKey);
      break;
    case "ArrowRight":
      e.preventDefault();
      if (!current.dataset.expanded){
        expandNode(current);
      } else {
        // Focus first child
        const child = current.querySelector(".node");
        if (child) setFocus(child);
      }
      break;
    case "ArrowLeft":
      e.preventDefault();
      if (current.dataset.expanded === "true"){
        collapseNode(current);
      } else {
        const parent = current.parentElement.closest(".node");
        if (parent) setFocus(parent);
      }
      break;
    case "Enter":
    case " ":
      e.preventDefault();
      acceptNode(current);
      break;
    case "Escape":
      e.preventDefault();
      promptBox.focus();
      break;
  }
});

/* ---- Helpers for navigation ---- */
function focusSibling(el, dir){
  const siblings = Array.from(el.parentElement.querySelectorAll(':scope > .node'));
  const idx = siblings.indexOf(el);
  if (idx === -1) return;
  const next = siblings[(idx + dir + siblings.length) % siblings.length];
  setFocus(next);
}

function focusNextVisible(el, forward=true){
  const nodes = Array.from(treeContainer.querySelectorAll(".node"));
  const idx = nodes.indexOf(el);
  if (idx === -1) return;
  const next = nodes[(idx + (forward?1:-1) + nodes.length) % nodes.length];
  setFocus(next);
}

/* -----------------------------------------------------------
 *  Accepting a node
 * --------------------------------------------------------- */
function acceptNode(el){
  promptBox.value = el.dataset.fullText;
  announce("Accepted suggestion");
  promptBox.focus();
}

/* -----------------------------------------------------------
 *  Expansion mechanics with cancel‑on‑blur
 * --------------------------------------------------------- */
const controllers = new Map();  // nodeId → AbortController

function debounceExpand(el){
  const timerId = setTimeout(()=> expandNode(el), 500);
  // Cancel debounce if focus leaves
  function cancel(){ clearTimeout(timerId); el.removeEventListener("blur", cancel); }
  el.addEventListener("blur", cancel);
}

async function expandNode(el){
  // Already expanded / at depth cap / node cap
  if (el.dataset.expanded || totalNodeCount >= MAX_TOTAL_NODES) return;

  // Rate‑limit
  const now = Date.now();
  if (now - lastRequestAt < RATE_LIMIT_MS){ return; }
  lastRequestAt = now;

  // Abort handle
  if (controllers.get(el.id)){ return; }     // one active per node
  const ctrl = new AbortController();
  controllers.set(el.id, ctrl);

  try{
    const completions = await fetchCompletions(
      el.dataset.fullText,
      +maxTokInput.value,
      +nCompInput.value,
      +reqPerNodeInp.value,
      ctrl.signal
    );
    controllers.delete(el.id);

    if (!completions.length) return;
    const subtree = buildTree(completions);

    const wrap = document.createElement("div");
    wrap.className="children";
    wrap.setAttribute("role","group");
    subtree.children.forEach(child=>renderNode(child, wrap, parseInt(el.getAttribute("aria-level"),10)+1));
    el.appendChild(wrap);

    el.setAttribute("aria-expanded","true");
    el.dataset.expanded="true";
    announce("Branch expanded");

  }catch(err){
    if (err.name !== "AbortError"){
      console.error(err);
      alert("Request failed: "+err.message);
    }
    controllers.delete(el.id);
  }
}

function collapseNode(el){
  const wrap = el.querySelector(":scope > .children");
  if (wrap) wrap.remove();
  el.dataset.expanded = "";
  el.setAttribute("aria-expanded","false");
  announce("Branch collapsed");
}

/* -----------------------------------------------------------
 *  OpenRouter call
 * --------------------------------------------------------- */
async function fetchCompletions(baseText, maxTokens, n, reqCount, signal){
  const results=[];
  const headers={
    "Content-Type":"application/json",
    Authorization:`Bearer ${apiKeyInput.value.trim()}`,
    "HTTP-Referer":"https://example.com",
    "X-Title":"AutocompleteTreeDemo"
  };

  for (let i=0;i<reqCount;i++){
    const body={
      model: MODEL_ID,
      n,
      max_tokens: maxTokens,
      temperature:0.7,
      messages:[
        {role:"system",content:"You are an autocomplete engine. Reply ONLY with the continuation."},
        {role:"user",content:baseText}
      ]
    };

    const resp = await fetch(ENDPOINT,{
      method:"POST",
      headers,
      body:JSON.stringify(body),
      signal
    });

    if (!resp.ok){
      const t = await resp.text();
      throw new Error(t);
    }
    const data = await resp.json();
    data.choices.forEach(ch => results.push(ch.message.content.trim()));
  }
  return results;
}

/* -----------------------------------------------------------
 *  Seeding the tree
 * --------------------------------------------------------- */
async function seedTree(){
  const seedText = promptBox.value.trim();
  if (!seedText){ promptBox.focus(); return; }

  // Clear previous AbortControllers
  controllers.forEach(ctrl=>ctrl.abort());
  controllers.clear();

  try{
    const completions = await fetchCompletions(
      seedText,
      +maxTokInput.value,
      +nCompInput.value,
      +reqPerNodeInp.value
    );
    const tree = buildTree(completions);
    renderTree(tree);
    announce("Tree created; use arrow keys to explore");
  }catch(e){
    console.error(e);
    alert("Seed request failed: "+e.message);
  }
}

/* -----------------------------------------------------------
 *  Global key bindings
 * --------------------------------------------------------- */
document.addEventListener("keydown", e=>{
  // Ctrl Enter in composer
  if (e.key === "Enter" && e.ctrlKey && document.activeElement === promptBox){
    e.preventDefault();
    seedTree();
  }

  // Ctrl /  toggles help
  if (e.key === "/" && e.ctrlKey){
    e.preventDefault();
    if (helpDialog.open) helpDialog.close();
    else helpDialog.showModal();
  }
});

/* -----------------------------------------------------------
 *  Button & startup wiring
 * --------------------------------------------------------- */
seedBtn.addEventListener("click", seedTree);

promptBox.addEventListener("keydown", e=>{
  if (e.key==="Tab"){
    // Quick jump from composer to tree
    const firstNode = treeContainer.querySelector(".node");
    if (firstNode){
      e.preventDefault();
      setFocus(firstNode);
    }
  }
});

/* Focus ring visible even when user starts in tree */
treeContainer.setAttribute("tabindex","-1");

/* End of file */
