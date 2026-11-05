// RAPP/1 reference vault — static viewer for the production guide's reference notes.
// Ported from the RAPP vault viewer (MIT, see NOTICE.md). Loads hash-pinned
// Markdown from the checked-in content bundle, renders with marked.js, resolves
// [[wikilinks]], builds backlinks and a graph. The same notes download as a real
// Obsidian vault (rapp1-vault.zip), built by tools/build_rapp1_vault.py.

const VAULT = {
  manifest: null,
  bundle: null,
  notes: new Map(),         // path -> { meta, body, html, title, section, status }
  byTitle: new Map(),       // lowercased title -> path
  backlinks: new Map(),     // path -> [{from, anchor}]
  mode: 'bundle',
  current: null,
};

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// ── Boot ──────────────────────────────────────────────────────────────────────

window.addEventListener('DOMContentLoaded', async () => {
  marked.setOptions({ gfm: true, breaks: false, headerIds: true, mangle: false });
  wireUI();
  try {
    await loadManifest();
    await prefetchAll();
    buildBacklinks();
    renderTree();
    document.body.dataset.mode = 'ready';
    handleHashChange();
  } catch (err) {
    document.body.dataset.mode = 'error';
    $('#note').innerHTML = `<h1>Vault failed to load</h1><pre>${escapeHtml(String(err))}</pre>`;
    console.error(err);
  }
});

window.addEventListener('hashchange', handleHashChange);

// ── Manifest + fetch ─────────────────────────────────────────────────────────

async function loadManifest() {
  // The manifest sits next to the viewer in pages/vault/. Same-origin relative
  // fetch works on GitHub Pages and on any local static server.
  const res = await fetch('./manifest.json', { cache: 'no-cache' });
  if (!res.ok) throw new Error(`manifest fetch failed: ${res.status}`);
  VAULT.manifest = await res.json();
  VAULT.mode = 'bundle';
  await loadContentBundle();
  $('#subtitle').textContent = VAULT.manifest.subtitle || 'Production guide reference';
}

async function loadContentBundle() {
  const runtime = VAULT.manifest.runtime_content || {};
  if (
    runtime.network_fallback !== false
    || runtime.hash_required !== true
    || runtime.bundle !== 'content-bundle.json'
  ) {
    throw new Error('manifest does not require the checked-in vault bundle');
  }
  const res = await fetch('./content-bundle.json', { cache: 'no-cache' });
  if (!res.ok) throw new Error(`content bundle fetch failed: ${res.status}`);
  const bundle = await res.json();
  if (
    bundle.schema !== 'rapp-vault-content-bundle/1.0'
    || bundle.network_fallback !== false
    || !bundle.notes
    || bundle.note_count !== VAULT.manifest.notes.length
  ) {
    throw new Error('content bundle has an invalid shape');
  }
  VAULT.bundle = bundle;
}

async function sha256Hex(text) {
  if (!globalThis.crypto || !crypto.subtle) {
    throw new Error('Web Crypto is required to verify vault note bytes');
  }
  const bytes = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(digest)]
    .map((value) => value.toString(16).padStart(2, '0'))
    .join('');
}

async function fetchNote(path) {
  const record = VAULT.bundle && VAULT.bundle.notes[path];
  const manifestEntry = VAULT.manifest.notes.find((note) => note.path === path);
  if (!record || !manifestEntry) throw new Error(`bundled note missing: ${path}`);
  const bytes = new TextEncoder().encode(record.content);
  const digest = await sha256Hex(record.content);
  if (
    record.bytes !== bytes.length
    || record.sha256 !== digest
    || manifestEntry.bytes !== record.bytes
    || manifestEntry.sha256 !== record.sha256
  ) {
    throw new Error(`bundled note hash mismatch: ${path}`);
  }
  return record.content;
}

async function prefetchAll() {
  // Fetch every note in the manifest in parallel. The vault is small; this
  // keeps search and backlinks instant after first load.
  const entries = VAULT.manifest.notes;
  const results = await Promise.all(entries.map(async (entry) => {
    try {
      const raw = await fetchNote(entry.path);
      const { meta, body } = parseFrontmatter(raw);
      return { ...entry, raw, meta, body, title: entry.title || meta.title || basename(entry.path) };
    } catch (err) {
      console.warn(`prefetch failed for ${entry.path}:`, err);
      return { ...entry, raw: '', meta: {}, body: `*(failed to load: ${escapeHtml(err.message)})*`, title: entry.title || basename(entry.path) };
    }
  }));
  for (const note of results) {
    VAULT.notes.set(note.path, note);
    VAULT.byTitle.set(note.title.toLowerCase(), note.path);
    // Also map by basename without .md so [[Foo]] resolves to "Foo.md".
    const stem = basename(note.path).replace(/\.md$/i, '');
    VAULT.byTitle.set(stem.toLowerCase(), note.path);
  }
}

// ── Frontmatter ──────────────────────────────────────────────────────────────

function parseFrontmatter(md) {
  if (!md.startsWith('---')) return { meta: {}, body: md };
  const end = md.indexOf('\n---', 3);
  if (end === -1) return { meta: {}, body: md };
  const rawYaml = md.slice(3, end).trim();
  const body = md.slice(end + 4).replace(/^\n/, '');
  const meta = {};
  for (const line of rawYaml.split(/\r?\n/)) {
    const m = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (m) meta[m[1]] = stripQuotes(m[2].trim());
  }
  return { meta, body };
}

function stripQuotes(s) {
  if (s.length >= 2 && (s[0] === '"' && s[s.length-1] === '"') ||
      s.length >= 2 && (s[0] === "'" && s[s.length-1] === "'")) {
    return s.slice(1, -1);
  }
  return s;
}

// ── Wikilinks ────────────────────────────────────────────────────────────────

function rewriteWikilinks(md) {
  // Replace [[Note Title]] and [[Note Title|alias]] with markdown links.
  return md.replace(/\[\[([^\]|]+)(\|([^\]]+))?\]\]/g, (_, title, _alias, alias) => {
    // Inside Markdown tables Obsidian writes [[Note\|alias]]; drop the escape.
    title = title.replace(/\\$/, '');
    // [[Note#Heading]] opens the note; the heading part is display only.
    const target = resolveTitle(title.split('#')[0].trim());
    const display = (alias || title).trim();
    if (target) {
      return `[${display}](#${encodeURIComponent(target)} "wikilink")`;
    }
    return `[${display}](#__broken__ "broken wikilink")`;
  });
}

function resolveTitle(title) {
  return VAULT.byTitle.get(title.toLowerCase()) || null;
}

// ── Backlinks ────────────────────────────────────────────────────────────────

function buildBacklinks() {
  for (const [path, note] of VAULT.notes) {
    const re = /\[\[([^\]|]+)(\|[^\]]+)?\]\]/g;
    let m;
    while ((m = re.exec(note.body))) {
      const target = resolveTitle(m[1].replace(/\\$/, '').split('#')[0].trim());
      if (target && target !== path) {
        if (!VAULT.backlinks.has(target)) VAULT.backlinks.set(target, []);
        VAULT.backlinks.get(target).push({ from: path, fromTitle: note.title });
      }
    }
  }
}

// ── Render ───────────────────────────────────────────────────────────────────

function renderTree() {
  const sections = new Map();
  for (const note of VAULT.notes.values()) {
    const sec = note.section || '__top__';
    if (!sections.has(sec)) sections.set(sec, []);
    sections.get(sec).push(note);
  }

  const tree = $('#tree');
  tree.innerHTML = '';

  const top = sections.get('__top__') || [];
  if (top.length) {
    const ul = document.createElement('ul');
    for (const note of top) ul.appendChild(makeTreeLink(note));
    tree.appendChild(ul);
  }

  // Preserve manifest order for sections.
  const sectionOrder = [];
  for (const note of VAULT.manifest.notes) {
    if (note.section && !sectionOrder.includes(note.section)) sectionOrder.push(note.section);
  }
  for (const sec of sectionOrder) {
    const notes = sections.get(sec) || [];
    const det = document.createElement('details');
    det.open = true;
    const sum = document.createElement('summary');
    sum.textContent = sec;
    det.appendChild(sum);
    const ul = document.createElement('ul');
    for (const note of notes) ul.appendChild(makeTreeLink(note));
    det.appendChild(ul);
    tree.appendChild(det);
  }

  $('#noteCount').textContent = `${VAULT.notes.size} notes`;
}

function makeTreeLink(note) {
  const li = document.createElement('li');
  const a = document.createElement('a');
  a.href = '#' + encodeURIComponent(note.path);
  a.dataset.path = note.path;
  const status = (note.meta && note.meta.status) || note.status || 'stub';
  a.innerHTML = `<span class="status ${status}"></span><span>${escapeHtml(note.title)}</span>`;
  li.appendChild(a);
  return li;
}

function renderNote(path) {
  const note = VAULT.notes.get(path);
  if (!note) {
    $('#note').innerHTML = `<h1>Note not found</h1><p>No vault entry for <code>${escapeHtml(path)}</code>.</p>`;
    $('#backlinks').hidden = true;
    return;
  }
  VAULT.current = path;
  document.title = `${note.title} — RAPP/1 Reference Vault`;
  setView('note');

  const status = (note.meta && note.meta.status) || note.status;
  const chip = status ? `<div class="frontmatter-chip"><span class="pill ${status}">${status}</span><span>${escapeHtml(note.section || 'Vault')}</span></div>` : '';

  const linked = rewriteWikilinks(note.body);
  let html = sanitizeHtml(marked.parse(linked));
  // Tag wiki anchors so CSS can style broken vs. resolved.
  html = html.replace(/<a href="#__broken__"([^>]*)>/g, '<a href="#" class="wikilink broken" title="No vault note matches this wikilink"$1>');
  html = html.replace(/<a href="#([^"]+)" title="wikilink">/g, (_, hash) => `<a href="#${hash}" class="wikilink">`);
  // Relative links to another note (e.g. NOTICE.md) open in the viewer.
  html = html.replace(/<a href="(?![a-z]+:|#|\.\.\/)([^"#]+\.md)"/gi, (whole, href) => {
    const base = path.includes('/') ? path.slice(0, path.lastIndexOf('/') + 1) : '';
    const target = decodeURIComponent(base + href).replace(/[^/]+\/\.\.\//g, '');
    return VAULT.notes.has(target) ? `<a href="#${encodeURIComponent(target)}" class="wikilink"` : whole;
  });

  $('#note').innerHTML = chip + html;

  decorateHeadings(path);

  // Active state in tree.
  $$('#tree a').forEach((a) => a.classList.toggle('active', a.dataset.path === path));

  // Mobile breadcrumb.
  const bc = $('#breadcrumb');
  if (bc) bc.textContent = note.section ? `${note.section} · ${note.title}` : note.title;

  // Backlinks panel.
  const bls = VAULT.backlinks.get(path) || [];
  const blEl = $('#backlinks');
  const blList = $('#backlinksList');
  if (bls.length) {
    blList.innerHTML = bls.map((b) =>
      `<li><a href="#${encodeURIComponent(b.from)}">← ${escapeHtml(b.fromTitle)}</a></li>`
    ).join('');
    blEl.hidden = false;
  } else {
    blEl.hidden = true;
  }

  function sanitizeHtml(html) {
    const template = document.createElement('template');
    template.innerHTML = html;
    template.content
      .querySelectorAll('script,iframe,object,embed,link,meta,base,form')
      .forEach((node) => node.remove());
    template.content.querySelectorAll('*').forEach((node) => {
      for (const attr of [...node.attributes]) {
        const name = attr.name.toLowerCase();
        const value = attr.value.trim().toLowerCase();
        if (
          name.startsWith('on')
          || ((name === 'href' || name === 'src')
            && (value.startsWith('javascript:') || value.startsWith('data:text/html')))
        ) {
          node.removeAttribute(attr.name);
        }
      }
    });
    return template.innerHTML;
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Add anchor + copy-link buttons to every H2/H3 in the rendered note.
function decorateHeadings(path) {
  $$('#note h2, #note h3').forEach((h) => {
    if (!h.id) h.id = slugify(h.textContent);
    const url = `${location.origin}${location.pathname}#${encodeURIComponent(path)}#${h.id}`;
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'heading-link';
    btn.title = 'Copy link to this section';
    btn.textContent = '#';
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      navigator.clipboard.writeText(url).then(() => {
        btn.textContent = '✓';
        setTimeout(() => { btn.textContent = '#'; }, 1200);
      }).catch(() => { /* clipboard unavailable */ });
    });
    h.appendChild(btn);
  });
}

function slugify(s) {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60);
}

function handleHashChange() {
  const hash = decodeURIComponent(location.hash.slice(1) || '');
  if (!hash) {
    const entry = VAULT.manifest.entry || 'README.md';
    location.hash = '#' + encodeURIComponent(entry);
    return;
  }
  if (hash === '__broken__') {
    return; // ignore clicks on broken wikilinks
  }
  renderNote(hash);
}

// ── Search ───────────────────────────────────────────────────────────────────

function wireUI() {
  $('#search').addEventListener('input', (e) => {
    const q = e.target.value.trim().toLowerCase();
    if (!q) {
      $$('#tree a').forEach((a) => a.parentElement.style.display = '');
      $$('#tree details').forEach((d) => d.style.display = '');
      return;
    }
    const matches = new Set();
    for (const note of VAULT.notes.values()) {
      const hay = (note.title + ' ' + note.body).toLowerCase();
      if (hay.includes(q)) matches.add(note.path);
    }
    $$('#tree a').forEach((a) => {
      a.parentElement.style.display = matches.has(a.dataset.path) ? '' : 'none';
    });
    $$('#tree details').forEach((d) => {
      const visible = [...d.querySelectorAll('li')].some((li) => li.style.display !== 'none');
      d.style.display = visible ? '' : 'none';
      if (visible) d.open = true;
    });
  });

  $('#randomBtn').addEventListener('click', openRandom);
  $('#readingBtn').addEventListener('click', toggleReadingMode);
  $('#graphBtn').addEventListener('click', toggleGraph);
  $('#navToggle')?.addEventListener('click', () => {
    document.body.classList.toggle('nav-open');
  });

  // Keyboard navigation. Single-key + simple `g i` chord.
  let chord = null;
  let chordTimer = null;
  document.addEventListener('keydown', (e) => {
    // Ignore when typing in an input/textarea.
    const tag = (e.target.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea' || e.target.isContentEditable) {
      if (e.key === 'Escape') e.target.blur();
      return;
    }
    if (e.metaKey || e.ctrlKey || e.altKey) return;

    // Chord pending — second key resolves it.
    if (chord === 'g') {
      clearTimeout(chordTimer);
      chord = null;
      if (e.key === 'i') { location.hash = '#' + encodeURIComponent(VAULT.manifest.index || '_index.md'); e.preventDefault(); return; }
      if (e.key === 'g') { toggleGraph(); e.preventDefault(); return; }
      // Unknown chord — fall through.
    }

    switch (e.key) {
      case '/':
        e.preventDefault();
        $('#search').focus();
        $('#search').select();
        break;
      case 'j':
        e.preventDefault();
        navigateRelative(1);
        break;
      case 'k':
        e.preventDefault();
        navigateRelative(-1);
        break;
      case 'r':
        e.preventDefault();
        openRandom();
        break;
      case 'm':
        e.preventDefault();
        toggleReadingMode();
        break;
      case 'g':
        chord = 'g';
        chordTimer = setTimeout(() => { chord = null; }, 800);
        break;
      case '?':
        e.preventDefault();
        $('#kbHint').hidden = !$('#kbHint').hidden;
        break;
      case 'Escape':
        $('#kbHint').hidden = true;
        document.body.classList.remove('nav-open');
        if (document.body.dataset.view === 'graph') setView('note');
        break;
    }
  });
}

// ── View switching (note vs graph) ───────────────────────────────────────────

function setView(view) {
  document.body.dataset.view = view;
  $('#note').hidden = (view === 'graph');
  $('#backlinks').hidden = (view === 'graph') || !$('#backlinks').children.length;
  $('#graph').hidden = (view !== 'graph');
  if (view === 'graph') renderGraph();
}

function toggleGraph() {
  setView(document.body.dataset.view === 'graph' ? 'note' : 'graph');
}

// ── Reading mode ─────────────────────────────────────────────────────────────

function toggleReadingMode() {
  document.body.classList.toggle('reading');
}

// ── Random note ──────────────────────────────────────────────────────────────

function openRandom() {
  const paths = [...VAULT.notes.keys()].filter((p) => p !== VAULT.current);
  if (!paths.length) return;
  const next = paths[Math.floor(Math.random() * paths.length)];
  location.hash = '#' + encodeURIComponent(next);
}

// ── j/k navigation through tree order ────────────────────────────────────────

function navigateRelative(delta) {
  // Order matches the rendered sidebar: top-level + per-section in manifest order.
  const ordered = VAULT.manifest.notes.map((n) => n.path);
  const idx = ordered.indexOf(VAULT.current);
  if (idx === -1) {
    location.hash = '#' + encodeURIComponent(ordered[0]);
    return;
  }
  let next = idx + delta;
  if (next < 0) next = 0;
  if (next >= ordered.length) next = ordered.length - 1;
  if (ordered[next] !== VAULT.current) {
    location.hash = '#' + encodeURIComponent(ordered[next]);
  }
}

// ── Graph view ───────────────────────────────────────────────────────────────

function renderGraph() {
  const svg = $('#graphSvg');
  if (!svg) return;
  const W = 1200, H = 960;
  const cx = W / 2, cy = H / 2;

  // Group notes by section (top-level entries land in "_top").
  const sections = new Map();
  for (const note of VAULT.notes.values()) {
    const s = note.section || '_top';
    if (!sections.has(s)) sections.set(s, []);
    sections.get(s).push(note);
  }

  // Place each section's anchor on a circle around the center; place notes on
  // a smaller circle around the section's anchor.
  const sectionList = [...sections.keys()];
  const sectionAnchor = new Map();
  const nodePos = new Map();
  const ringR = 330;
  const sectionRadius = new Map();
  // Each section gets an arc of the ring in proportion to its size.
  const weight = (s) => Math.max(3, sections.get(s).length);
  const totalWeight = sectionList.reduce((sum, s) => sum + weight(s), 0);
  let arcStart = -Math.PI / 2;
  sectionList.forEach((s) => {
    const span = (weight(s) / totalWeight) * Math.PI * 2;
    const angle = arcStart + span / 2;
    arcStart += span;
    const ax = cx + Math.cos(angle) * ringR * 1.25;
    const ay = cy + Math.sin(angle) * ringR;
    sectionAnchor.set(s, { x: ax, y: ay });
    const notes = sections.get(s);
    // Big sections get a bigger circle so their labels do not collide.
    const innerR = Math.min(125, Math.max(40, 9 * notes.length));
    sectionRadius.set(s, innerR);
    notes.forEach((note, j) => {
      const a = (j / notes.length) * Math.PI * 2;
      nodePos.set(note.path, {
        x: ax + Math.cos(a) * innerR,
        y: ay + Math.sin(a) * innerR,
        section: s,
        title: note.title,
        status: (note.meta && note.meta.status) || note.status || 'stub',
      });
    });
  });

  // Edges: every wikilink that resolves.
  const edges = [];
  for (const [path, note] of VAULT.notes) {
    const re = /\[\[([^\]|]+)(\|[^\]]+)?\]\]/g;
    let m;
    const seen = new Set();
    while ((m = re.exec(note.body))) {
      const target = resolveTitle(m[1].replace(/\\$/, '').split('#')[0].trim());
      if (target && target !== path && !seen.has(target)) {
        seen.add(target);
        edges.push([path, target]);
      }
    }
  }

  // Draw.
  const ns = 'http://www.w3.org/2000/svg';
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  svg.innerHTML = '';

  // Section labels.
  for (const [s, anchor] of sectionAnchor) {
    if (s === '_top') continue;
    const t = document.createElementNS(ns, 'text');
    t.setAttribute('x', anchor.x);
    t.setAttribute('y', anchor.y - sectionRadius.get(s) - 22);
    t.setAttribute('text-anchor', 'middle');
    t.setAttribute('class', 'graph-section-label');
    t.textContent = s;
    svg.appendChild(t);
  }

  // Edges.
  const edgeGroup = document.createElementNS(ns, 'g');
  edgeGroup.setAttribute('class', 'graph-edges');
  for (const [a, b] of edges) {
    const pa = nodePos.get(a), pb = nodePos.get(b);
    if (!pa || !pb) continue;
    const line = document.createElementNS(ns, 'line');
    line.setAttribute('x1', pa.x);
    line.setAttribute('y1', pa.y);
    line.setAttribute('x2', pb.x);
    line.setAttribute('y2', pb.y);
    line.dataset.from = a;
    line.dataset.to = b;
    edgeGroup.appendChild(line);
  }
  svg.appendChild(edgeGroup);

  // Nodes.
  const nodeGroup = document.createElementNS(ns, 'g');
  nodeGroup.setAttribute('class', 'graph-nodes');
  for (const [path, p] of nodePos) {
    const g = document.createElementNS(ns, 'g');
    g.setAttribute('class', `graph-node status-${p.status}`);
    g.setAttribute('transform', `translate(${p.x}, ${p.y})`);
    g.dataset.path = path;
    g.style.cursor = 'pointer';

    const circle = document.createElementNS(ns, 'circle');
    circle.setAttribute('r', 6);
    g.appendChild(circle);

    const t = document.createElementNS(ns, 'text');
    t.setAttribute('y', -10);
    t.setAttribute('text-anchor', 'middle');
    t.textContent = p.title.length > 22 ? p.title.slice(0, 20) + '…' : p.title;
    g.appendChild(t);

    g.addEventListener('click', () => {
      location.hash = '#' + encodeURIComponent(path);
      setView('note');
    });
    g.addEventListener('mouseenter', () => highlightNeighbors(path, true));
    g.addEventListener('mouseleave', () => highlightNeighbors(path, false));

    nodeGroup.appendChild(g);
  }
  svg.appendChild(nodeGroup);
}

function highlightNeighbors(path, on) {
  const svg = $('#graphSvg');
  if (!svg) return;
  const neighbors = new Set([path]);
  svg.querySelectorAll('.graph-edges line').forEach((line) => {
    const matches = line.dataset.from === path || line.dataset.to === path;
    line.classList.toggle('hot', on && matches);
    if (on && matches) {
      neighbors.add(line.dataset.from);
      neighbors.add(line.dataset.to);
    }
  });
  svg.querySelectorAll('.graph-node').forEach((node) => {
    const isNeighbor = neighbors.has(node.dataset.path);
    node.classList.toggle('hot', on && isNeighbor);
    node.classList.toggle('dim', on && !isNeighbor);
  });
}

// ── Utils ────────────────────────────────────────────────────────────────────

function basename(path) {
  return path.split('/').pop();
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
