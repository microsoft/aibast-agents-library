window.AibastDesktop = {
  root: new URL('../../../', document.currentScript.src),
  mount(host, options = {}) {
    host.practiceDesktop?.dispose();
    if (options.stage) host.classList.add('desktop-stage');
    host.innerHTML = `  <div id="pc" aria-label="Pretend Windows 11 desktop">
    <div id="desk">
      <div class="dicon" style="left:12px;top:12px" data-app="bin"><div class="ico" style="background:#9ca3af"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.6"><path d="M6 7h12l-1 13H7zM4 7h16M9 7V4h6v3"/></svg></div>Recycle Bin</div>
      <div class="dicon" style="left:12px;top:100px" data-app="edge"><div class="ico" style="background:linear-gradient(135deg,#34d399,#0ea5e9,#2563eb)">e</div>Microsoft Edge</div>
    </div>
    <div class="hint" id="hint"></div>
    <div class="toast" id="toast"></div>

    <div id="start" role="dialog" aria-label="Start">
      <div class="srch"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#555" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input id="ssearch" type="text" placeholder="Search for apps, settings, and documents" autocomplete="off"></div>
      <div class="sec">Pinned <span>All apps &gt;</span></div>
      <div id="pins"></div>
      <div class="sec rec-sec">Recommended <span>More &gt;</span></div>
      <div id="recs">
        <div class="rec"><div class="ico" style="width:28px;height:28px;border-radius:6px;background:#2b579a;color:#fff;display:grid;place-items:center;font-weight:700">W</div><div>Getting started<small>Recently added</small></div></div>
        <div class="rec"><div class="ico" style="width:28px;height:28px;border-radius:6px;background:#217346;color:#fff;display:grid;place-items:center;font-weight:700">X</div><div>Budget 2026<small>2h ago</small></div></div>
      </div>
      <div id="results"></div>
      <div class="foot"><div class="me"><div class="av"></div>You</div><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="1.8"><path d="M12 3v9M6.3 7.3a8 8 0 1 0 11.4 0"/></svg></div>
    </div>

    <div id="taskbar">
      <div id="tb-center">
        <div class="tb-btn" id="tb-start" title="Start"><svg width="22" height="22" viewBox="0 0 24 24"><path fill="#0067c0" d="M3 3h8.5v8.5H3zM12.5 3H21v8.5h-8.5zM3 12.5h8.5V21H3zM12.5 12.5H21V21h-8.5z"/></svg></div>
        <div id="tb-search"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#555" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>Search</div>
        <div class="tb-btn" title="Task view"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="1.6"><rect x="3" y="5" width="10" height="8" rx="1"/><rect x="11" y="11" width="10" height="8" rx="1"/></svg></div>
        <div id="tb-apps" style="display:flex;gap:4px"></div>
      </div>
      <div id="tray"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#222" stroke-width="1.8"><path d="M5 12.5a10 10 0 0 1 14 0M8 15.5a6 6 0 0 1 8 0M12 19h.01"/></svg><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#222" stroke-width="1.8"><path d="M4 9v6M8 7v10M12 5v14M16 8v8M20 10v4"/></svg><svg width="18" height="16" viewBox="0 0 26 16" fill="none" stroke="#222" stroke-width="1.8"><rect x="1" y="2" width="20" height="12" rx="2"/><path d="M23 6v4"/><rect x="3" y="4" width="14" height="8" fill="#222" stroke="none"/></svg><div class="clock"><div id="clk">10:42 AM</div><div id="dte">11/8/2026</div></div></div>
    </div>
  </div>

  <div class="coach" id="coach">
    <div class="n"><span id="c-n">Step 1 of 8</span>${options.stage ? ' · Nothing here touches your real computer.' : ''}</div>
    <div class="say" id="c-say"></div>
    ${options.stage ? '<div id="c-context" hidden></div>' : ''}
    <div class="acts" id="c-acts"></div>
    ${options.stage ? '<details class="all-steps" open><summary>All steps</summary>' : ''}
    <div class="prog" id="c-prog"></div>
    ${options.stage ? '</details>' : ''}
    ${options.stage && options.journey !== 'express' ? '<details id="step-help"><summary>Stuck?</summary><ul id="step-fixes"></ul><a id="step-help-link">Get help</a></details>' : ''}
  </div>`;

  const installBase = location.protocol === 'https:' && location.hostname.endsWith('.github.io')
    ? new URL('../../', location.href).href : 'https://microsoft.github.io/aibast-agents-library/';
  const PS_LINE = `irm ${installBase}install.ps1 | iex`;
  const VS_LINE = 'Go and read https://microsoft.github.io/aibast-agents-library/docs/start/skill.md and set up my Brainstem for me.';
  const LIB = 'https://microsoft.github.io/aibast-agents-library/';
  const HELP = 'https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=v4j5cvGGr0GRqy180BHbR7RNABRLLw9Eq-9okV_7Z-hURVhJVVozNURGOE85SkI4VkFaOVhLTTNLUC4u';
  const $ = (s, r = document) => r.querySelector(s);
  const pc = $('#pc');
  const stage = !!options.stage;
  const express = options.journey === 'express';
  const sessionPractice = stage && !express;
  host.dataset.journey = express ? 'express' : 'local';
  if (express) {
    host.querySelectorAll('[data-app="edge"]').forEach(el => el.remove());
    $('#pc').setAttribute('aria-label', 'Pretend computer: Copilot Studio setup with sample data');
  }
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const phone = matchMedia('(max-width: 600px)');
  const adaptSteps = () => { if (stage) $('.all-steps').open = !phone.matches; };
  if (stage) { adaptSteps(); phone.addEventListener('change', adaptSteps); }
  const manualStart = still || new URLSearchParams(location.search).get('watch') === '0';
  let disposed = false, mode = options.mode || (manualStart ? 'try' : 'watch');
  let playing = stage && mode === 'watch', playbackVersion = 0;
  let pointer = null;
  if (stage) {
    const controls = document.createElement('div');
    controls.id = 'stage-controls';
    controls.setAttribute('aria-label', 'Practice computer controls');
    controls.innerHTML = '<span class="mode-switch" role="group" aria-label="Practice mode"><button id="watch-mode" aria-pressed="true">Watch</button><button id="try-mode" aria-pressed="false">Step by step</button></span><button id="stage-pause">Pause</button><button id="stage-again">Play again</button><button id="practice-mute" aria-pressed="false">Unmute</button><audio id="practice-voice" preload="none"></audio>';
    $('#c-acts').before(controls);
    const caption = document.createElement('div');
    caption.id = 'practice-caption';
    caption.setAttribute('aria-live', 'polite');
    controls.after(caption);
    pointer = document.createElement('div');
    pointer.id = 'watch-pointer';
    pointer.setAttribute('aria-hidden', 'true');
    pointer.innerHTML = '<svg width="26" height="32" viewBox="0 0 26 32"><path d="M2 2v24l6-6 5 10 5-3-5-9h9z" fill="#fff" stroke="#18181b" stroke-width="2"/></svg>';
    pc.appendChild(pointer);
    $('#watch-mode').onclick = () => setMode('watch');
    $('#try-mode').onclick = () => setMode('try');
    $('#stage-pause').onclick = () => {
      playing = !playing; playbackVersion++;
      if (!playing) stopNarration();
      else speakScreen(true);
      renderControls();
    };
    $('#stage-again').onclick = () => restart(0, 'watch');
    let takingOver = false;
    pc.addEventListener('pointerdown', e => {
      if (!e.isTrusted || mode !== 'watch') return;
      takingOver = true;
      setMode('try');
      e.preventDefault();
      e.stopImmediatePropagation();
    }, true);
    pc.addEventListener('click', e => {
      if (!takingOver) return;
      takingOver = false;
      e.preventDefault();
      e.stopImmediatePropagation();
    }, true);
    pc.addEventListener('keydown', e => {
      if (!e.isTrusted || mode !== 'watch') return;
      setMode('try');
      e.preventDefault();
      e.stopImmediatePropagation();
    }, true);
  }
  const state = { brainstemInstalled: false, brainstemRunning: false, signedIn: false, clip: '', code: 'A1B2-C3D4',
    memory: '', completed: [] };
  const copy = value => JSON.parse(JSON.stringify(value));
  const sceneControls = 'button, input, textarea, [contenteditable], [tabindex], .tbar .ctl i, .vsc .send';
  let restoring = false, layoutObserver = null;
  const fileSystem = {id:'computer', name:'This PC', children:[
    {id:'desktop', name:'Desktop', children:[]},
    {id:'downloads', name:'Downloads', children:[]},
    {id:'documents', name:'Documents', children:[
      {id:'agents', name:'agents', children:[
        {id:'context-memory', name:'context_memory_agent.py', loaded:true},
        {id:'manage-memory', name:'manage_memory_agent.py', loaded:true},
        {id:'learn-new', name:'rar_rapp_learn_new_skill_agent.py', loaded:true},
        {id:'hacker-news', name:'hacker_news_agent.py', loaded:true}
      ]}
    ]}
  ]};
  function findFile(id, tree = fileSystem) {
    if (tree.id === id) return tree;
    return tree.children?.map(child => findFile(id, child)).find(Boolean);
  }
  function exportFile(tree = fileSystem) {
    const file = findFile('hacker-news', tree), downloads = findFile('downloads', tree);
    if (!downloads.children.includes(file)) {
      const agents = findFile('agents', tree);
      agents.children.splice(agents.children.indexOf(file), 1);
      downloads.children.push(file);
    }
  }
  function addAgent(id, name, tree = fileSystem) {
    if (!findFile(id, tree)) findFile('agents', tree).children.push({id, name, loaded:true});
  }
  Object.defineProperties(state, {
    news:{enumerable:true, get:() => findFile('hacker-news').loaded,
      set:value => { findFile('hacker-news').loaded = value; }},
    exported:{enumerable:true, get:() => findFile('downloads').children.some(f => f.id === 'hacker-news')},
    meeting:{enumerable:true, get:() => !!findFile('meeting-prep')?.loaded,
      set:value => { if (value) addAgent('meeting-prep', 'meeting_prep_agent.py'); }},
    created:{enumerable:true, get:() => !!findFile('quote-of-the-day')?.loaded,
      set:value => { if (value) addAgent('quote-of-the-day', 'quote_of_the_day_agent.py'); }}
  });
  function restoreFiles(tree) {
    const existing = new Map();
    const collect = node => { existing.set(node.id, node); node.children?.forEach(collect); };
    collect(fileSystem);
    function reconcile(source) {
      const node = existing.get(source.id) || {};
      Object.assign(node, source);
      if (source.children) node.children = source.children.map(reconcile);
      return node;
    }
    reconcile(tree);
  }
  function openFiles(key = 'files', folder = key === 'downloads' ? 'downloads' : 'desktop') {
    const el = makeWin(key, key === 'downloads' ? 'Pretend Downloads' : 'File Explorer',
      'plain file-explorer' + (key === 'downloads' ? ' downloads' : ''), key === 'downloads' ? 330 : 640,
      key === 'downloads' ? 190 : 420, '<div class="file-folders"></div><div class="file-list"></div>');
    el.dataset.folder = folder;
    renderFiles();
  }
  function renderFiles() {
    for (const key of ['files', 'downloads']) {
      const el = wins[key]; if (!el) continue;
      const folder = findFile(el.dataset.folder);
      const nav = $('.file-folders', el);
      nav.replaceChildren();
      const folders = key === 'downloads' ? [folder] : [...fileSystem.children, findFile('agents')];
      folders.forEach(node => {
        const button = document.createElement('button');
        button.textContent = node.name; button.setAttribute('aria-pressed', String(node === folder));
        button.onclick = () => { el.dataset.folder = node.id; renderFiles(); };
        nav.appendChild(button);
      });
      const list = $('.file-list', el);
      list.replaceChildren();
      if (!folder.children.length) {
        const empty = document.createElement('p'); empty.textContent = 'This folder is empty.'; list.appendChild(empty);
      }
      folder.children.forEach(node => {
        const item = document.createElement(node.children ? 'button' : 'div');
        item.dataset.fileId = node.id; item.textContent = node.name;
        if (node.children) item.onclick = () => { el.dataset.folder = node.id; renderFiles(); };
        else {
          item.draggable = true; item.tabIndex = 0;
          if (key === 'downloads' && node.id === 'hacker-news') item.id = 'download-agent';
          item.ondragstart = e => e.dataTransfer.setData('text/plain', 'pretend:' + node.id);
        }
        list.appendChild(item);
      });
    }
  }

  // ── apps ──
  const tile = (bg, txt) => `<div class="ico" style="background:${bg}">${txt}</div>`;
  const APPS = {
    ps:   { name: 'Windows PowerShell', kw: 'powershell power shell terminal command', ico: tile('#012456', '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="m5 7 6 5-6 5M13 17h6"/></svg>'), kind: 'App' },
    code: { name: 'Visual Studio Code', kw: 'visual studio code vscode vs code editor', ico: tile('#0078d4', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#fff"><path d="M17 3 8.5 10.6 4.6 7.6 3 8.4v7.2l1.6.8 3.9-3L17 21l4-2V5z"/></svg>'), kind: 'App' },
    edge: { name: 'Microsoft Edge', kw: 'edge browser internet web', ico: tile('linear-gradient(135deg,#34d399,#0ea5e9,#2563eb)', 'e'), kind: 'App' },
    settings: { name: 'Settings', kw: 'settings control panel', ico: tile('#6b7280', '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg>'), kind: 'App' },
    files: { name: 'File Explorer', kw: 'file explorer files folders', ico: tile('#f5b400', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#fff"><path d="M3 6h7l2 2h9v10H3z"/></svg>'), kind: 'App' },
    word: { name: 'Word', kw: 'word document', ico: tile('#2b579a', 'W'), kind: 'App' },
    excel: { name: 'Excel', kw: 'excel spreadsheet', ico: tile('#217346', 'X'), kind: 'App' },
    outlook: { name: 'Outlook', kw: 'outlook mail email', ico: tile('#0f6cbd', 'O'), kind: 'App' },
    teams: { name: 'Microsoft Teams', kw: 'teams chat meeting', ico: tile('#5059c9', 'T'), kind: 'App' },
    calc: { name: 'Calculator', kw: 'calculator', ico: tile('#374151', '='), kind: 'App' },
    photos: { name: 'Photos', kw: 'photos pictures', ico: tile('#0ea5e9', '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 17 5-5 4 4 3-3 6 6"/></svg>'), kind: 'App' },
    terminal: { name: 'Terminal', kw: 'terminal windows terminal cmd', ico: tile('#1f2937', '>_'), kind: 'App' },
  };
  const PINS = ['edge', 'word', 'excel', 'outlook', 'teams', 'settings', 'files', 'calc', 'photos', 'ps', 'code', 'terminal'];
  $('#pins').innerHTML = PINS.map((k) => `<div class="pin" data-app="${k}">${APPS[k].ico}<span>${APPS[k].name}</span></div>`).join('');

  // ── start menu + search ──
  const start = $('#start'), ssearch = $('#ssearch'), results = $('#results');
  function openStart(on) {
    start.classList.toggle('open', on);
    $('#tb-start').classList.toggle('active', on);
    if (on) {
      ssearch.value = ''; search('');
      if (!restoring) setTimeout(() => ssearch.focus({preventScroll:stage}), 0);
      emit('start-open');
    }
  }
  $('#tb-start').addEventListener('click', (e) => { e.stopPropagation(); openStart(!start.classList.contains('open')); });
  $('#tb-search').addEventListener('click', (e) => { e.stopPropagation(); openStart(true); });
  start.addEventListener('click', (e) => {
    e.stopPropagation();
    const app = stage && e.target.closest('[data-app]');
    if (app) launch(app.dataset.app);
  });
  pc.addEventListener('click', () => openStart(false));
  function search(q) {
    q = q.trim().toLowerCase();
    start.classList.toggle('searching', !!q);
    if (!q) { results.innerHTML = ''; return; }
    const hits = Object.entries(APPS).filter(([, a]) => (a.name + ' ' + a.kw).toLowerCase().includes(q));
    if (!hits.length) { results.innerHTML = `<div class="res-head">Best match</div><div class="res"><div class="lbl"><b>Search the web</b><small>${esc(q)} - See web results</small></div></div>`; return; }
    results.innerHTML = `<div class="res-head">Best match</div>` + hits.map(([k, a], i) => `<div class="res ${i ? '' : 'best'}" data-app="${k}">${a.ico}<div class="lbl"><b>${a.name}</b><small>${a.kind}</small></div></div>` + (i === 0 && hits.length > 1 ? '<div class="res-head">Apps</div>' : '')).join('');
    emit('search', q);
  }
  ssearch.addEventListener('input', () => search(ssearch.value));
  ssearch.addEventListener('keydown', (e) => { if (e.key === 'Enter') { const best = $('.res.best', results) || $('.res[data-app]', results); if (best) launch(best.dataset.app); } if (e.key === 'Escape') openStart(false); });
  pc.addEventListener('click', (e) => { const t = e.target.closest('[data-app]'); if (t && !t.classList.contains('tb-app')) { launch(t.dataset.app); } });
  pc.addEventListener('dblclick', (e) => { const t = e.target.closest('.dicon'); if (t) launch(t.dataset.app); });

  // ── clock ──
  function tick() { const d = new Date(); $('#clk').textContent = d.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }); $('#dte').textContent = d.toLocaleDateString(); }
  tick(); const clock = setInterval(tick, 15000);

  // ── window manager ──
  const wins = {}; let z = 10, cascade = 0;
  function makeWin(key, title, cls, w, h, bodyHtml, iconHtml) {
    const el = document.createElement('div');
    el.className = 'win ' + cls; el.dataset.key = key;
    const W = Math.min(w, pc.clientWidth - 40), H = Math.min(h, pc.clientHeight - 88);
    el.style.width = W + 'px'; el.style.height = H + 'px';
    el.style.left = Math.max(10, (pc.clientWidth - W) / 2 + (cascade % 5) * 24 - 48) + 'px';
    el.style.top = Math.max(8, (pc.clientHeight - 48 - H) / 2 + (cascade % 5) * 20 - 40) + 'px'; cascade++;
    el.innerHTML = `<div class="tbar">${iconHtml || ''}<span class="t">${title}</span><span class="ctl"><i class="mn" title="Minimize">&#8211;</i><i class="mx" title="Maximize"><svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1"><rect x=".5" y=".5" width="9" height="9"/></svg></i><i class="x" title="Close"><svg width="10" height="10" viewBox="0 0 10 10" stroke="currentColor" stroke-width="1.2"><path d="M0 0l10 10M10 0 0 10"/></svg></i></span></div><div class="body">${bodyHtml}</div>`;
    pc.appendChild(el); wins[key] = el; focus(el);
    const tb = document.createElement('div'); tb.className = 'tb-btn tb-app open'; tb.dataset.win = key; tb.innerHTML = APPS[key] ? APPS[key].ico.replace('class="ico"', 'class="ico" style="width:24px;height:24px;font-size:11px;border-radius:5px;') : ''; tb.title = title;
    tb.addEventListener('click', (e) => { e.stopPropagation(); if (el.classList.contains('min')) { el.classList.remove('min'); focus(el); } else if (el === top()) { el.classList.add('min'); } else focus(el); });
    $('#tb-apps').appendChild(tb); el._tb = tb;
    // drag
    const bar = $('.tbar', el); let drag = null;
    bar.addEventListener('pointerdown', (e) => { if (e.target.closest('.ctl')) return; drag = { x: e.clientX - el.offsetLeft, y: e.clientY - el.offsetTop }; bar.setPointerCapture(e.pointerId); focus(el); });
    bar.addEventListener('pointermove', (e) => { if (!drag) return; el.style.left = Math.max(-W + 120, Math.min(pc.clientWidth - 120, e.clientX - drag.x)) + 'px'; el.style.top = Math.max(0, Math.min(pc.clientHeight - 80, e.clientY - drag.y)) + 'px'; });
    bar.addEventListener('pointerup', () => { drag = null; });
    bar.addEventListener('dblclick', (e) => { if (!e.target.closest('.ctl')) maximize(el); });
    el.addEventListener('pointerdown', () => focus(el));
    $('.mn', el).addEventListener('click', (e) => { e.stopPropagation(); el.classList.add('min'); });
    $('.mx', el).addEventListener('click', (e) => { e.stopPropagation(); maximize(el); });
    $('.x', el).addEventListener('click', (e) => { e.stopPropagation(); closeWin(key); });
    el.addEventListener('click', (e) => e.stopPropagation());
    return el;
  }
  function maximize(el) { if (el.dataset.max) { Object.assign(el.style, JSON.parse(el.dataset.max)); delete el.dataset.max; } else { el.dataset.max = JSON.stringify({ left: el.style.left, top: el.style.top, width: el.style.width, height: el.style.height }); Object.assign(el.style, { left: '0px', top: '0px', width: pc.clientWidth + 'px', height: (pc.clientHeight - 48) + 'px' }); } }
  function focus(el) { el.style.zIndex = ++z; document.querySelectorAll('.tb-app').forEach((b) => b.classList.toggle('active', b.dataset.win === el.dataset.key)); }
  function top() { let best = null; Object.values(wins).forEach((w) => { if (!w.classList.contains('min') && (!best || +w.style.zIndex > +best.style.zIndex)) best = w; }); return best; }
  function closeWin(key) {
    const el = wins[key]; if (!el) return;
    el._tb.remove(); el.remove(); delete wins[key];
    if (key === 'edge') edge = null;
    if (key === 'ps') ps = null;
    if (key === 'code') vs = null;
    emit('close', key);
  }
  function launch(key) {
    openStart(false);
    if (wins[key]) { wins[key].classList.remove('min'); focus(wins[key]); return; }
    if (key === 'ps') openPowerShell();
    else if (key === 'code') openVSCode();
    else if (key === 'edge') openEdge(LIB);
    else if (key === 'files' || key === 'downloads') openFiles(key);
    else if (key === 'bin') makeWin('bin', 'Recycle Bin', 'plain', 560, 360, '<p>Recycle Bin is empty.</p>');
    else makeWin(key, APPS[key].name, 'plain', 640, 420, `<p><strong>${APPS[key].name}</strong> is not part of the setup, so this practice computer leaves it empty.</p><p>Close this window and carry on with the step in the coach box below the screen.</p>`);
    emit('launch', key);
  }

  // ── PowerShell ──
  const esc = (s) => s.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  const sleep = (ms) => new Promise((resolve) => {
    if (!stage) { setTimeout(resolve, still ? Math.min(ms, 120) : ms); return; }
    let remaining = still ? Math.min(ms, 120) : (!express && ps?.busy ? Math.min(ms, 100) : ms), last = performance.now();
    function tickDelay() {
      if (disposed) return;
      const now = performance.now();
      if (mode === 'try' || playing) remaining -= now - last;
      last = now;
      if (remaining <= 0) resolve();
      else setTimeout(tickDelay, 40);
    }
    tickDelay();
  });
  let ps = null;
  function openPowerShell() {
    const el = makeWin('ps', 'Windows PowerShell', 'ps dark', 820, 460, '<div class="out"></div>', APPS.ps.ico.replace('class="ico"', 'class="ico" style="width:16px;height:16px;border-radius:3px;font-size:9px;"'));
    ps = { el, out: $('.out', el), busy: false };
    psPrint('Windows PowerShell\nCopyright (C) Microsoft Corporation. All rights reserved.\n\nInstall the latest PowerShell for new features and improvements! https://aka.ms/PSWindows\n\n');
    psPrompt();
    $('.body', el).addEventListener('click', () => { if (ps.in) ps.in.focus({preventScroll:stage}); });
    $('.body', el).addEventListener('contextmenu', (e) => { e.preventDefault(); psPaste(); });
  }
  function psPrint(text, cls) { const s = document.createElement('span'); if (cls) s.className = cls; s.textContent = text; ps.out.appendChild(s); ps.out.parentElement.scrollTop = 1e9; }
  function psPrompt() {
    const p = document.createElement('span'); p.className = 'pl'; p.innerHTML = '<span class="y">PS C:\\Users\\You&gt; </span><span class="in" contenteditable="plaintext-only" spellcheck="false"></span>';
    ps.out.appendChild(p); ps.in = $('.in', p);
    if (!restoring) ps.in.focus({preventScroll:stage});
    wirePrompt();
    ps.out.parentElement.scrollTop = 1e9;
  }
  function wirePrompt() {
    ps.in.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); psRun(ps.in.textContent); } });
    ps.in.addEventListener('paste', (e) => { e.preventDefault(); const t = (e.clipboardData || window.clipboardData).getData('text'); ps.in.textContent += t.replace(/\r?\n/g, ' ').trim(); emit('ps-paste'); });
  }
  async function psPaste() {
    if (!ps || !ps.in) return;
    let t = state.clip;
    try { if (navigator.clipboard && navigator.clipboard.readText) t = (await navigator.clipboard.readText()) || t; } catch (_e) { /* no permission: fall back to the coach's copy */ }
    if (!t) { toast('Nothing to paste yet', 'Press "Copy the line" in the coach box first.'); return; }
    ps.in.textContent += t.replace(/\r?\n/g, ' ').trim(); ps.in.focus({preventScroll:stage}); emit('ps-paste');
  }
  async function psRun(cmd) {
    cmd = cmd.trim(); ps.in.contentEditable = 'false'; ps.in = null; psPrint('\n');
    if (!cmd) { psPrompt(); return; }
    const norm = cmd.replace(/\s+/g, ' ').toLowerCase();
    if (norm === PS_LINE.toLowerCase() || /^irm .*install\.ps1 \| iex$/.test(norm)) {
      await psInstall();
      if (sessionPractice) return;
    }
    else if (norm === 'cls' || norm === 'clear') { ps.out.innerHTML = ''; }
    else if (norm === 'brainstem') { if (state.brainstemInstalled) { await psLaunchBlock(); } else { psNotRecognized(cmd); } }
    else { psNotRecognized(cmd); }
    psPrompt();
  }
  function psNotRecognized(cmd) {
    const w = cmd.split(' ')[0];
    psPrint(`${w} : The term '${w}' is not recognized as the name of a cmdlet, function, script file, or operable program. Check the spelling of the name, or if a path was included, verify that the path is correct and try again.\nAt line:1 char:1\n+ ${cmd}\n+ ${'~'.repeat(Math.max(1, w.length))}\n    + CategoryInfo          : ObjectNotFound: (${w}:String) [], CommandNotFoundException\n    + FullyQualifiedErrorId : CommandNotFoundException\n\n`, 'r');
    emit('ps-error');
  }
  async function line(text, cls, ms = 350) { psPrint(text + '\n', cls); await sleep(ms); }
  async function psInstall() {
    if (sessionPractice) { emit('ps-run'); return; }
    ps.busy = true; emit('ps-run');
    await line('\n  RAPP Brainstem', 'c', 200);
    await line('  Local-first AI agent server', 'gr', 120);
    await line('  Powered by GitHub Copilot - no API keys needed\n', 'gr', 500);
    if (!state.brainstemInstalled) {
      await line('Checking prerequisites...', '', 400);
      await line('  [OK] git version 2.47.1.windows.1', 'g', 300);
      await line('  [OK] Python 3.12.6', 'g', 300);
      await line('  [OK] GitHub CLI installed\n', 'g', 400);
      await line('Installing RAPP Brainstem...', '', 300);
      await line('  Downloading only the Brainstem runtime; solution ZIPs stay in the web library.', '', 900);
      await line('  [OK] Source code ready', 'g', 300);
      await line('  Creating Python virtual environment (this can take a minute)...', '', 1400);
      await line('  [OK] Virtual environment ready\n', 'g', 300);
      await line('Installing dependencies...', '', 300);
      await line('  [..] Installing Python packages; pip progress will appear below.', 'y', 600);
      for (const p of ['flask-3.1.0', 'requests-2.32.3', 'python-dotenv-1.0.1', 'markdown-3.7']) await line(`  Successfully installed ${p}`, 'gr', 220);
      await line('  [OK] Dependencies installed\n', 'g', 300);
      await line('Installing CLI...', '', 300);
      await line('  Added to PATH', '', 200);
      await line('  [OK] CLI installed\n', 'g', 400);
      state.brainstemInstalled = true;
    } else {
      await line('  Local version:  0.6.17', 'c', 200);
      await line('  Remote version: 0.6.17', 'c', 200);
      await line('\n  [OK] Already up to date (v0.6.17)\n', 'g', 500);
    }
    if (!state.signedIn) {
      await line('  Authenticating with GitHub Copilot...', '', 600);
      await line('  +-----------------------------------------+', '', 60);
      psPrint('  |  Your code: '); psPrint(state.code + '\n', 'w'); await sleep(60);
      await line('  +-----------------------------------------+', '', 300);
      await line('  Opening browser to authorize...', '', 600);
      await line('  Waiting for authorization...', '', 300);
      openEdge('https://github.com/login/device'); emit('device-open');
      await new Promise((r) => { state.onAuth = r; });
      await line('  [OK] Authenticated - Copilot access confirmed\n', 'g', 500);
      state.signedIn = true;
    } else {
      await line('  [OK] Already authenticated with GitHub Copilot\n', 'g', 400);
    }
    await psLaunchBlock();
    ps.busy = false;
  }
  async function psLaunchBlock() {
    if (state.brainstemRunning) {
      await line('  Starting RAPP Brainstem...', '', 500);
      await line('  [OK] Your Brainstem is already running (v0.6.17)\n', 'g', 400);
      await line('  Open http://localhost:7071 to chat.', '', 150);
      await line('  Next time, just type: brainstem\n', '', 300);
      emit('ps-already-running');
      openEdge('http://localhost:7071'); return;
    }
    await line('  Starting RAPP Brainstem...', '', 600);
    await line('  [OK] Brainstem is running at http://localhost:7071', 'g', 300);
    await line('  Opening http://localhost:7071 in your browser...\n', '', 300);
    await line('  Next time, just type: brainstem\n', '', 300);
    state.brainstemRunning = true; emit('brainstem-up');
    openEdge('http://localhost:7071');
  }

  // ── Edge ──
  let edge = null;
  function openEdge(url, scene = null) {
    if (!edge) {
      const el = makeWin('edge', 'Microsoft Edge', 'edge', 980, 600, `<div class="bar"><div class="nav"><span>&#8592;</span><span>&#8594;</span><span>&#8635;</span></div><div class="url"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#666" stroke-width="2"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg><input id="eurl" spellcheck="false"></div></div><div class="view" id="eview"></div>`);
      $('.tbar .t', el).outerHTML = '<div class="tabs t"><div class="tab"><div class="fav" id="efav"></div><span id="etitle">New tab</span></div><div class="tab plus">+</div></div>';
      edge = { el, url: $('#eurl', el), view: $('#eview', el), title: $('#etitle', el) };
      edge.url.addEventListener('keydown', (e) => { if (e.key === 'Enter') edgeGo(edge.url.value); });
      edge.url.addEventListener('focus', () => edge.url.select());
    } else { edge.el.classList.remove('min'); focus(edge.el); }
    edgeGo(url, scene);
  }
  function browserAddress(address) {
    let text = address.trim();
    if (/^(?:localhost|127\.0\.0\.1):\d+(?:\/|$)/i.test(text)) text = 'http://' + text;
    else if (/^(?:[\w-]+\.)+[a-z]{2,}(?::\d+)?(?:\/|$)/i.test(text) && !/\.html?(?:\/|$)/i.test(text)) text = 'https://' + text;
    let url;
    try { url = new URL(text, location.href); }
    catch (_e) { return {kind:'invalid', text:address}; }
    if (!['http:', 'https:'].includes(url.protocol)) return {kind:'invalid', text:address};
    if (url.origin === location.origin) return {kind:'site', url};
    if (['localhost', '127.0.0.1'].includes(url.hostname) && url.port === '7071' && url.pathname === '/') return {kind:'brainstem', url};
    if (url.origin === 'https://github.com' && url.pathname === '/login/device') return {kind:'auth', url};
    return {kind:'outside', url};
  }
  function browserPanel(url) {
    edge.title.textContent = 'Practice browser';
    const panel = document.createElement('div'); panel.className = 'mock center browser-panel';
    const content = document.createElement('div');
    const text = document.createElement('p');
    text.textContent = 'This site cannot be shown in the practice browser.';
    const open = document.createElement('button');
    open.type = 'button'; open.textContent = 'Open it in a new tab';
    if (url) {
      open.onclick = () => window.open(url.href, '_blank', 'noopener,noreferrer');
    } else {
      open.disabled = true;
      const help = document.createElement('p'); help.textContent = 'Enter an http or https address.';
      content.appendChild(help);
    }
    content.prepend(text); content.appendChild(open); panel.appendChild(content);
    edge.view.replaceChildren(panel);
  }
  async function frameSite(url, browser, navigation, scene = null) {
    if (!navigator.onLine) { browserPanel(url); return; }
    const loading = document.createElement('p'); loading.className = 'browser-loading';
    loading.textContent = 'Opening page...'; browser.view.replaceChildren(loading);
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);
    const current = () => !disposed && edge === browser && browser.navigation === navigation;
    try {
      const response = await fetch(url.href, {method:'HEAD', redirect:'error', signal:controller.signal});
      if (!current()) return;
      if (!response.ok || new URL(response.url).origin !== location.origin ||
          !response.headers.get('content-type')?.includes('text/html')) {
        browserPanel(url); return;
      }
      const frame = document.createElement('iframe');
      frame.id = 'practice-page'; frame.title = 'Site page in the practice browser';
      frame.hidden = true;
      const frameTimeout = setTimeout(() => { if (current()) browserPanel(url); }, 5000);
      frame.onerror = () => { clearTimeout(frameTimeout); if (current()) browserPanel(url); };
      frame.onload = () => {
        clearTimeout(frameTimeout);
        if (!current()) return;
        const doc = frame.contentDocument;
        if (!doc?.body?.textContent.trim()) { browserPanel(url); return; }
        loading.remove(); frame.hidden = false;
        doc.addEventListener('click', event => {
          const link = event.target.closest('a[href]');
          if (!link) return;
          event.preventDefault(); edgeGo(link.href);
        });
        if (scene?.frame) {
          doc.querySelectorAll('input, textarea, select').forEach((input, i) => {
            const value = scene.frame.inputs[i];
            if (value) { input.value = value.value; input.checked = value.checked; }
          });
          frame.contentWindow.scrollTo(scene.frame.x, scene.frame.y);
        }
      };
      frame.src = url.href;
      browser.view.appendChild(frame);
    } catch (error) {
      if (!current()) return;
      if (error.name !== 'AbortError' && !(error instanceof TypeError)) throw error;
      browserPanel(url);
    } finally { clearTimeout(timeout); }
  }
  function edgeGo(address, scene = null) {
    const route = browserAddress(address);
    edge.address = route.url?.href || address;
    edge.navigation = (edge.navigation || 0) + 1;
    edge.url.value = edge.address;
    emit('edge', edge.address);
    if (route.kind === 'site') {
      edge.title.textContent = route.url.pathname.split('/').pop() || route.url.hostname;
      frameSite(route.url, edge, edge.navigation, scene);
    } else if (route.kind === 'brainstem') {
      edge.title.textContent = 'RAPP Brainstem';
      if (!state.brainstemRunning) { edge.view.innerHTML = `<div class="mock center"><div><h2>Hmmm… can't reach this page</h2><p>localhost refused to connect.</p><p style="font-size:12px;color:#777">Your Brainstem is not running yet. Run the one line in PowerShell first.</p></div></div>`; return; }
      edge.view.innerHTML = brainstemPage(); wireBrainstem(edge.view);
    } else if (route.kind === 'auth') {
      edge.title.textContent = 'Device Activation'; edge.view.innerHTML = `<div class="mock"><div class="gh"><div class="card" id="ghcard"><h2>Device Activation</h2><p style="text-align:center;color:#57606a;margin:0 0 6px">Enter the code displayed in PowerShell</p><label for="ghcode">Device code</label><input id="ghcode" maxlength="9" placeholder="XXXX-XXXX" autocomplete="off"><div class="warn" id="ghwarn">That code does not match. Look at the PowerShell window: the code is on the line that says Your code.</div><button id="ghgo">Continue</button></div></div></div>`;
      $('#ghgo', edge.view).addEventListener('click', () => {
        const v = $('#ghcode', edge.view).value.trim().toUpperCase();
        if (v !== state.code) { $('#ghwarn', edge.view).style.display = 'block'; emit('device-wrong'); return; }
        $('#ghcard', edge.view).innerHTML = `<h2>Authorize RAPP Brainstem</h2><p style="text-align:center;color:#57606a">RAPP Brainstem by <b>You</b> wants to use GitHub Copilot on your behalf.</p><p style="font-size:12px;color:#57606a;border:1px solid #d0d7de;border-radius:6px;padding:8px">This is the practice computer. No real GitHub account is involved.</p><button id="ghauth">Authorize</button>`;
        $('#ghauth', edge.view).addEventListener('click', () => { $('#ghcard', edge.view).innerHTML = '<h2>Congratulations, you\'re all set!</h2><p style="text-align:center;color:#57606a">Your device is now connected. You can close this tab and go back to PowerShell.</p>'; emit('device-ok'); if (state.onAuth) { state.onAuth(); state.onAuth = null; } });
      });
      if (!restoring) setTimeout(() => { const i = edge && $('#ghcode', edge.view); if (i) i.focus({preventScroll:stage}); }, 50);
    } else browserPanel(route.url);
  }
  function brainstemPage() {
    return `<div class="bs" id="bs-drop" aria-label="Pretend Brainstem chat: sample replies">
      <div class="hd"><strong>RAPP Brainstem</strong><select aria-label="Pretend model"><option>Auto</option></select>
        <button id="bs-book" title="Agent library" aria-label="Agent library"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor"><path d="M3 4h7l2 2 2-2h7v16h-7l-2 2-2-2H3zM12 6v16"/></svg></button>
        <button id="bs-agents" title="Installed agents" aria-label="Installed agents">&#8853;</button>
        <button class="bs-preview" title="Voice" aria-label="Voice"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor"><rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10v2a7 7 0 0 0 14 0v-2M12 19v3M8 22h8"/></svg></button>
        <button class="bs-preview" title="VS Code" aria-label="VS Code">&lt;/&gt;</button></div>
      <div class="sample-label">Pretend chat · Sample replies only</div>
      <div class="bs-panel" id="bs-agent-panel" hidden></div>
      <div class="bs-panel" id="bs-library" hidden><strong>Agent library (pretend)</strong><input id="bs-library-search" placeholder="Search agents" aria-label="Search agents"><div id="bs-meeting" hidden>Meeting Prep <button id="bs-add-meeting">Add</button></div></div>
      <div class="log" role="log"><div class="m"><h3>Welcome to your local RAPP Brainstem!</h3>
        I am your local assistant powered by Copilot. Here is a quick tour to get you started:
        <ul><li><b>Chat</b>: Just ask me questions below to start building and researching!</li>
        <li><b>Agents Panel</b>: Click the &#8853; icon (top right) to view or remove installed tools.</li>
        <li><b>Add Agents</b>: Drag and drop any <code>agent.py</code> file directly onto this window to instantly teach me new things.</li></ul></div></div>
      <div class="bs-starters"><button class="starter-btn">What can you do?</button><button class="starter-btn">What do you remember?</button><button class="starter-btn">What should I do next?</button></div>
      <div class="bs-toolbar"><button class="bs-preview">Export</button><button class="bs-preview">Import</button><button id="bs-clear">Clear</button><button class="bs-preview">Tutorial</button><button class="bs-preview">Get Help</button></div>
      <form><input placeholder="Message brainstem..." aria-label="Message brainstem" autocomplete="off"><button type="submit">Send</button></form></div>`;
  }
  function wireBrainstem(root) {
    const f = $('form', root), log = $('.log', root), inp = $('form input', root);
    const reply = (text, thought = '') => {
      log.insertAdjacentHTML('beforeend', `${thought ? `<div class="bs-thought">agent called ${esc(thought)} (sample)</div>` : ''}<div class="m"><strong>Sample reply</strong><br>${esc(text)}</div>`);
      log.scrollTop = log.scrollHeight;
    };
    const send = q => {
      if (!q.trim()) return;
      log.insertAdjacentHTML('beforeend', `<div class="m me">${esc(q)}</div>`);
      let event = '', answer = 'This pretend chat only demonstrates the interview. Follow the hint below.', thought = '';
      if (q === 'What can you do?') {
        answer = 'I can remember what you teach me, read Hacker News, and learn new agents from a file or a description.';
        event = 'capabilities';
      } else if (q === 'What do you remember?') {
        answer = state.memory || 'You have not taught me anything in this practice session yet.';
        thought = 'ContextMemory'; event = 'remembered';
      } else if (q === 'What should I do next?') {
        answer = 'Interview it. Teach it. Correct it. Trade agents. Try asking Meeting Prep to prepare a customer meeting, or describe another agent to create.';
        event = 'next';
      } else if (/remember/i.test(q)) {
        state.memory = q; answer = 'Saved. I will remember that across conversations in this pretend session.';
        thought = 'ManageMemory'; event = 'introduced';
      } else if (/hacker news/i.test(q)) {
        answer = state.news ? 'Hacker News is available again. Sample headline: A team shares a new open-source tool. This is not live news.' : 'I cannot get Hacker News: hacker_news_agent.py is not loaded. Restore the file to give me that capability again.';
        thought = state.news ? 'HackerNews' : '';
        event = state.news ? 'verified' : 'honest';
      } else if (/learn.*agent|create.*agent/i.test(q)) {
        state.created = true; answer = 'Created QuoteOfTheDay and hot-loaded its file. Ask for motivation whenever you need it.';
        thought = 'LearnNew'; event = 'created';
      }
      reply(answer, thought); emit(event);
    };
    f.onsubmit = e => { e.preventDefault(); const q = inp.value.trim(); inp.value = ''; send(q); };
    root.querySelectorAll('.starter-btn').forEach(button => { button.onclick = () => send(button.textContent); });
    $('#bs-clear', root).onclick = () => { log.replaceChildren(); emit('cleared'); };
    $('#bs-agents', root).onclick = () => {
      $('#bs-library', root).hidden = true;
      const panel = $('#bs-agent-panel', root); panel.hidden = !panel.hidden; renderAgents(); emit('panel');
    };
    function renderAgents() {
      const panel = $('#bs-agent-panel', root);
      const installed = [];
      const collect = node => {
        if (node.loaded && node.id !== 'hacker-news') installed.push(esc(node.name));
        node.children?.forEach(collect);
      };
      collect(fileSystem);
      panel.innerHTML = `<strong>Installed agents (pretend)</strong><p>${installed.join('<br>')}</p>${state.news ? '<div>hacker_news_agent.py <button id="bs-export-agent">Export</button><button id="bs-delete-agent">Delete</button></div>' : '<p>hacker_news_agent.py is not loaded.</p>'}`;
      if (!state.news) return;
      $('#bs-export-agent', root).onclick = () => {
        exportFile(); renderFiles();
        reply('Exported hacker_news_agent.py to the pretend Downloads window. No real file was downloaded.'); emit('exported');
      };
      $('#bs-delete-agent', root).onclick = () => {
        if ($('#bs-delete-question', root)) return;
        panel.insertAdjacentHTML('beforeend', '<div id="bs-delete-question">Remove hacker_news_agent.py? <button id="bs-confirm-delete">Confirm delete</button><button id="bs-cancel-delete">Cancel</button></div>');
        $('#bs-cancel-delete', root).onclick = () => renderAgents();
        $('#bs-confirm-delete', root).onclick = () => {
          if (!state.exported) { toast('Back up first', 'Export the pretend agent before deleting it.'); return; }
          state.news = false; renderAgents(); reply('Removed hacker_news_agent.py. The chat is still running.'); emit('deleted');
        };
        showHint();
      };
    }
    $('.bs', root).renderAgents = renderAgents;
    $('#bs-book', root).onclick = () => {
      $('#bs-agent-panel', root).hidden = true;
      $('#bs-library', root).hidden = !$('#bs-library', root).hidden; showHint();
    };
    $('#bs-library-search', root).oninput = e => {
      $('#bs-meeting', root).hidden = !/meeting\s*prep/i.test(e.target.value); showHint();
    };
    $('#bs-add-meeting', root).onclick = () => {
      state.meeting = true; $('#bs-library', root).hidden = true;
      reply('Installed Meeting Prep. Ask me to prep you for your next customer meeting.'); emit('installed');
    };
    root.ondragover = e => e.preventDefault();
    root.ondrop = e => {
      e.preventDefault();
      if (e.dataTransfer.getData('text/plain') === 'pretend:hacker-news') restoreAgent();
      else toast('Use the pretend file', 'Drag hacker_news_agent.py from the pretend Downloads window. No real files are imported here.');
    };
    root.querySelectorAll('.bs-preview').forEach(button => {
      button.onclick = () => toast('Pretend control', 'This control is shown to match the real chat. Follow the interview hint below.');
    });
  }
  function restoreAgent() {
    if (!state.exported) { toast('No backup yet', 'Export the pretend agent first, or skip this step.'); return; }
    findFile('hacker-news').loaded = true;
    closeWin('downloads');
    $('.bs .log').insertAdjacentHTML('beforeend', '<div class="m"><strong>Sample reply</strong><br>Hot-loaded hacker_news_agent.py. Instantly.</div>');
    $('.bs').renderAgents();
    emit('restored');
  }

  // ── VS Code ──
  const ICONS = {
    run: '<svg viewBox="0 0 24 24"><path d="M4 5h16v14H4z" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="m7 9 3 2.5L7 14M12 15h5" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>',
    check: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="m8 12 3 3 5-6" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>',
    read: '<svg viewBox="0 0 24 24"><path d="M3 5h7a3 3 0 0 1 3 3v12a2 2 0 0 0-2-2H3zM21 5h-7a3 3 0 0 0-3 3v12a2 2 0 0 1 2-2h8z" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>',
    open: '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M3 9h18" stroke="currentColor" stroke-width="1.6"/></svg>'
  };
  let vs = null;
  function openVSCode() {
    const tree = `<div class="tree"><div class="d">rapp_brainstem</div><div class="d l2 c">.brainstem_data</div><div class="d l2 c">.vscode</div><div class="d l2">agents</div><div class="d l2 c" style="padding-left:42px">experimental</div><div class="f l2" data-k="py">basic_agent.py</div><div class="f l2" data-k="py">context_memory_agent.py</div><div class="f l2" data-k="py">hacker_news_agent.py</div><div class="f l2" data-k="py">manage_memory_agent.py</div><div class="f l2" data-k="py">rar_rapp_learn_new_skill_agent.py</div><div class="d l2 c">tests</div><div class="f" data-k="{}">.brainstem_book.json</div><div class="f" data-k="≡">.copilot_token</div><div class="f" data-k="≡">.env.example</div><div class="f" data-k="py">brainstem.py</div><div class="f" data-k="md">CLAUDE.md</div><div class="f" data-k="≡">requirements.txt</div><div class="f" data-k="md">soul.md</div><div class="f" data-k="≡">start.sh</div></div>`;
    const body = `<div class="act"><i class="on"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M13 3H6v18h12V8z"/><path d="M13 3v5h5"/></svg></i><i><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="6"/><path d="m20 20-4.5-4.5"/></svg></i><i><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="6" cy="6" r="2.5"/><circle cx="6" cy="18" r="2.5"/><circle cx="18" cy="8" r="2.5"/><path d="M6 8.5v7M18 10.5c0 4-12 2-12 5"/></svg></i><i><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="m7 5 11 7-11 7z"/></svg></i><i><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="4" y="4" width="7" height="7"/><rect x="13" y="4" width="7" height="7"/><rect x="4" y="13" width="7" height="7"/><rect x="13" y="13" width="7" height="7"/></svg></i></div>
      <div class="exp"><h4>EXPLORER</h4><div class="empty">NO FOLDER OPENED<br><br>You have not yet opened a folder.</div>${tree}</div>
      <div class="ed"><div class="etabs"><span class="on wel">Welcome</span><span class="sbtab" style="display:none">RAPP Brainstem</span></div><div class="welcome"><div><h2>Visual Studio Code</h2>Editing evolved</div></div><div class="sb"><div class="ab">&#8592; &#8594; &#8635; <span>http://localhost:7071/</span></div><div class="bs-host"></div></div></div>
      <div class="chat"><div class="ch">CHAT <small>GitHub Copilot</small></div><div class="thread"></div><div class="cin"><textarea placeholder="Ask Copilot or type / for commands" spellcheck="false"></textarea><div class="row"><span>+</span><b>Agent</b><span>Auto</span><span class="send" title="Send">&#8593;</span></div></div></div>
      <div class="sbar"><span>&#9099; main</span><span><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="m12 3 10 18H2zM12 9v5M12 17v1"/></svg> 0</span><span style="margin-left:auto">Ln 1, Col 1</span><span>UTF-8</span><span>Copilot</span></div>`;
    const el = makeWin('code', 'Visual Studio Code', 'vsc dark', 1040, 620, body, APPS.code.ico.replace('class="ico"', 'class="ico" style="width:16px;height:16px;border-radius:3px;font-size:9px;"'));
    $('.body', el).style.gridTemplateRows = '1fr 22px';
    $('.tbar .t', el).insertAdjacentHTML('afterend', '<span class="cmd"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg> Search</span>');
    vs = { el, thread: $('.thread', el), ta: $('textarea', el) };
    const send = () => { const t = vs.ta.value.trim(); if (!t) return; vs.ta.value = ''; vsRun(t); };
    vs.ta.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } });
    vs.ta.addEventListener('paste', () => setTimeout(() => emit('vs-paste'), 0));
    $('.send', el).addEventListener('click', send);
    if (!restoring) setTimeout(() => vs?.ta.focus({preventScroll:stage}), 50);
  }
  async function vsSay(cls, html) { const d = document.createElement('div'); d.className = 'msg ' + cls; d.innerHTML = html; vs.thread.appendChild(d); await sleep(30); d.classList.add('show'); vs.thread.scrollTop = 1e9; }
  async function vsStep(icon, html, ms) { await vsSay('step', ICONS[icon] + '<span>' + html + '</span>'); await sleep(ms); }
  async function vsRun(prompt) {
    if (express) { await sendAgentLine(prompt); return; }
    if (stage && vs.busy) return;
    vs.busy = true;
    await vsSay('you', esc(prompt));
    if (!/skill\.md/i.test(prompt) || !/brainstem/i.test(prompt)) { await sleep(600); await vsSay('ai', 'On your real computer, Copilot would answer this. On the practice computer, paste the line from the coach box: it starts with "Go and read".'); vs.busy = false; return; }
    emit('vs-run'); await sleep(600);
    await vsStep('read', 'Read <code>skill.md</code>', 900);
    await vsStep('check', 'Checked <code>localhost:7071/health</code> ' + (state.brainstemRunning ? '<b>ok</b>: already running' : 'not running yet'), 900);
    if (!state.brainstemRunning) { await vsStep('run', 'Ran <code>install.ps1</code> in the terminal', 1600); state.brainstemInstalled = true; state.signedIn = true; state.brainstemRunning = true; await vsStep('check', 'Checked <code>localhost:7071/health</code> <b>ok</b>', 700); }
    await vsStep('read', 'Downloaded 4 starter helpers into <code>agents/</code>', 900);
    await vsStep('open', 'Added <code>rapp_brainstem</code> to the Explorer', 400); vs.el.classList.add('folder'); await sleep(700);
    await vsStep('open', 'Opened <code>localhost:7071</code> in Simple Browser', 300);
    $('.bs-host', vs.el).innerHTML = brainstemPage(); wireBrainstem($('.bs-host', vs.el)); $('.wel', vs.el).classList.remove('on'); const st = $('.sbtab', vs.el); st.style.display = 'flex'; st.classList.add('on'); vs.el.classList.add('browser'); await sleep(500);
    await vsSay('ai', 'Your Brainstem is running beside this chat. Say hello to it whenever you like, and I will show you your first trick.');
    vs.busy = false;
    emit('vs-done');
  }

  // ── coach ──
  const INSTALL_STEPS = [
    { id: 'start', say: 'Press <b>Start</b>: the four blue squares in the middle of the bar at the bottom of the screen.', hint: '#tb-start', done: (e) => e === 'start-open' },
    { id: 'find', say: 'In <b>Search</b>, type <b>PowerShell</b>. When <b>Windows PowerShell</b> shows up as the best match, press Enter.', hint: '#ssearch', done: (e, d) => e === 'launch' && d === 'ps' },
    { id: 'paste', say: 'Copy the one line, then press <b>Ctrl+V</b> or <b>right-click</b> inside the blue Windows PowerShell window to paste it. Press <b>Enter</b>.', copy: PS_LINE, hint: '.ps .body', done: (e) => e === 'ps-run' },
    { id: 'signin', say: 'It is installing. When the sign-in page opens, type the code shown in PowerShell (the line that says <b>Your code</b>), press Continue, then Authorize.', hint: '#ghcode', done: (e) => e === 'device-ok' },
  ];
  const interview = (id, heading, tourHint, event, skippable = false) => ({
    id, heading, tourHint, skippable, say:`<strong>${heading}</strong> ${tourHint}`, done:e => e === event
  });
  const INTERVIEW_STEPS = [
    interview('ask-capabilities', 'Ask what it can do.', 'Click <strong>What can you do?</strong>', 'capabilities'),
    interview('introduce', 'Introduce yourself.', 'Type <em>"Remember, my name is … and I …"</em> and press <strong>Enter</strong>.', 'introduced'),
    interview('clear-slate', 'Now, wipe the slate.', 'Click <strong>Clear</strong> in the toolbar below.', 'cleared'),
    interview('what-remember', 'Make it prove itself.', 'Click <strong>What do you remember?</strong>', 'remembered'),
    interview('agents-panel', 'Look inside its head.', 'Click the <strong>⊕ button</strong>, top right.', 'panel'),
    interview('export-agent', 'Back up an agent.', 'Click <strong>Export</strong> on <strong>hacker_news_agent.py</strong>.', 'exported', true),
    interview('delete-agent', 'Now remove it.', 'Click <strong>Delete</strong> on <strong>hacker_news_agent.py</strong> and confirm.', 'deleted', true),
    interview('prove-removed', 'See for yourself.', 'Type <em>"get my latest hacker news"</em> and press <strong>Enter</strong>.', 'honest', true),
    interview('restore-agent', 'Now put it back.', 'Drag the <strong>agent.py</strong> file you exported from Downloads and drop it <strong>anywhere on this window</strong>. Or skip — your brainstem, your call.', 'restored', true),
    interview('verify-restored', 'Trust — then verify.', 'Ask for the news again.', 'verified', true),
    interview('registry', "There's a whole library.", 'Click the <strong>book button</strong> (top right), search <em>meeting prep</em>, and click <strong>Add</strong> on <strong>Meeting Prep</strong>.', 'installed', true),
    interview('create', 'Create your first agent.', 'Try: <em>"Learn a new agent called QuoteOfTheDay that gives me an inspiring quote when I ask for motivation."</em> Then press <strong>Enter</strong>.', 'created', true),
    interview('finale', 'One last button.', 'Click <strong>What should I do next?</strong>', 'next'),
  ];
  const STEPS = express ? [
    {id:'agent-chat', say:'Open <b>GitHub Copilot chat</b> in Visual Studio Code. This is where you ask it to set up your agent.', hint:'#agent-chat', done:e => e === 'agent-chat'},
    {id:'agent-line', say:'Paste the <b>setup line</b> for your chosen agent, then press <b>Send</b>. The same line is always available below this computer.', copy:options.story.line, hint:'.vsc textarea', done:e => e === 'agent-sent'},
    {id:'agent-setup', say:'Sign in with your Microsoft account when Copilot asks. Review the sample-data setup, then answer <b>Yes</b>. This computer only pretends to sign in.', hint:'#ms-signin', done:e => e === 'agent-ready'},
    {id:'agent-test', say:'Open <b>Copilot Studio</b> in Edge and send the first sample question in your agent\'s test chat. The recorded answer uses <b>sample data</b>.', hint:'#agent-open', done:e => e === 'studio-done'}
  ] : [...INSTALL_STEPS, ...INTERVIEW_STEPS];
  const soundKey = 'aibast-practice-sound';
  let muted = true;
  try { muted = localStorage.getItem(soundKey) !== 'unmuted'; } catch (_e) { /* Muted without storage. */ }
  let activeNarration = null, screenKey = null, narrationPending = Promise.resolve();
  let narrationStarted = false, welcomePending = false, narrationVersion = 0;
  const clips = new Map();
  const siteRoot = window.AibastDesktop.root;
  const narrationData = stage ? fetch(new URL('api/v1/practice/narration.json', siteRoot))
    .then(r => r.ok ? r.json() : null).catch(() => null) : Promise.resolve(null);
  let rawBase;
  const registry = () => rawBase || (rawBase = fetch(new URL('api/registry.json', siteRoot))
    .then(r => r.ok ? r.json() : null).then(d => d?.raw || null).catch(() => null));
  window.__narration = [];
  async function clip(media) {
    if (!clips.has(media.contentHash)) clips.set(media.contentHash, (async () => {
      const local = ['localhost', '127.0.0.1'].includes(location.hostname) || location.protocol === 'file:';
      const urls = local ? [new URL(media.url, siteRoot).href] : [];
      const base = await registry();
      if (base) urls.push(new URL(media.url, base).href);
      for (const url of urls) {
        try {
          const response = await fetch(url);
          if (!response.ok) continue;
          const bytes = await response.arrayBuffer();
          if (!crypto.subtle) continue;
          const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))]
            .map(b => b.toString(16).padStart(2, '0')).join('');
          if (hash !== media.contentHash) continue;
          return {url:URL.createObjectURL(new Blob([bytes], {type:media.mimeType})),
            source:local && url === urls[0] ? 'local' : 'raw'};
        } catch (_e) { /* Unreachable media uses the same timed captions. */ }
      }
      return null;
    })());
    return clips.get(media.contentHash);
  }
  function stopNarration() {
    narrationVersion++;
    activeNarration?.cancel();
    activeNarration = null;
  }
  function narrate(seg, fallback) {
    const caption = $('#practice-caption'), voice = $('#practice-voice');
    if (!seg?.media) {
      caption.textContent = fallback;
      window.__narration.push({id:screenKey, captions:[fallback], fallback:'captions', playedMs:0});
      return Promise.resolve();
    }
    const media = seg.media, shown = [];
    const log = {id:seg.id, durationMs:media.durationMs, captions:shown};
    window.__narration.push(log);
    let finished = false, timer, tick, elapsed = 0, silentStart;
    let resolve;
    const promise = new Promise(done => { resolve = done; });
    const show = ms => {
      const cues = seg.captions.segments;
      const cue = cues.find(c => ms >= c.startMs && ms < c.endMs) || cues[cues.length - 1];
      const text = cue?.text || fallback;
      caption.textContent = text;
      if (shown[shown.length - 1] !== text) shown.push(text);
    };
    const done = stopped => {
      if (finished) return;
      finished = true;
      clearTimeout(timer); clearInterval(tick);
      voice.pause();
      voice.onended = voice.onerror = voice.ontimeupdate = voice.onplaying = null;
      log.end = performance.now();
      log.playedMs = Math.round(log.end - (log.start || log.end));
      if (stopped) log.stopped = true;
      resolve();
    };
    const silent = () => {
      if (finished) return;
      voice.pause();
      elapsed = voice.currentTime ? voice.currentTime * 1000 : elapsed;
      voice.onended = voice.onerror = voice.ontimeupdate = voice.onplaying = null;
      log.start ??= performance.now();
      silentStart = performance.now();
      clearTimeout(timer); clearInterval(tick);
      tick = setInterval(() => show(elapsed + performance.now() - silentStart), 100);
      timer = setTimeout(() => done(false), Math.max(0, media.durationMs - elapsed));
    };
    const run = {promise, cancel:() => done(true), silence:silent};
    activeNarration = run;
    voice.removeAttribute('src'); voice.load();
    show(0);
    if (muted) silent();
    else clip(media).then(src => {
      if (finished || disposed || activeNarration !== run) return;
      if (muted) { if (silentStart == null) silent(); return; }
      if (!src) { log.fallback = 'captions'; silent(); return; }
      voice.src = src.url;
      voice.onplaying = () => { log.start ??= performance.now(); log.source = src.source; };
      voice.ontimeupdate = () => show(voice.currentTime * 1000);
      voice.onended = () => done(false);
      voice.onerror = () => { log.fallback = 'captions'; silent(); };
      voice.play().catch(() => {
        if (!finished) { log.fallback = 'captions'; silent(); }
      });
    });
    return promise;
  }
  function speakScreen(replay = false) {
    if (!stage || restoring || !narrationStarted) return;
    const key = welcomePending ? 'welcome' : finish ? 'finish' : STEPS[step]?.id;
    if (key === screenKey && !replay) return;
    screenKey = key;
    stopNarration();
    if (!key) { $('#practice-caption').textContent = ''; return; }
    const version = ++narrationVersion;
    narrationPending = narrationData.then(data => {
      if (disposed || version !== narrationVersion) return;
      const segment = data?.[express ? 'express' : 'brainstem']?.segments.find(s => s.screenId === key);
      return narrate(segment, $('#c-say').textContent);
    });
    if (key === 'welcome') narrationPending.then(() => {
      if (version === narrationVersion && welcomePending && !disposed) {
        welcomePending = false; speakScreen();
      }
    });
    return narrationPending;
  }
  if (stage) {
    const button = $('#practice-mute');
    const soundLabel = () => {
      button.textContent = muted ? 'Unmute' : 'Mute';
      button.setAttribute('aria-pressed', String(!muted));
    };
    soundLabel();
    button.onclick = () => {
      muted = !muted;
      try { localStorage.setItem(soundKey, muted ? 'muted' : 'unmuted'); } catch (_e) { /* Session-only choice. */ }
      soundLabel();
      if (muted) activeNarration?.silence();
      else speakScreen(true);
    };
  }
  const storageKey = 'aibast-practice-session';
  let saved = null;
  if (sessionPractice) {
    try { saved = JSON.parse(localStorage.getItem(storageKey)); } catch (_e) { /* Practice also works without storage. */ }
  }
  if (options.initialStep != null) saved = null;
  const requested = Number(new URLSearchParams(location.search).get('step'));
  const direct = Number.isInteger(requested) && requested >= 1 && requested <= STEPS.length;
  if (sessionPractice && direct) {
    const url = new URL(location.href);
    url.searchParams.delete('step');
    history.replaceState(null, '', url);
  }
  let step = options.initialStep ?? (sessionPractice && direct ? requested - 1 :
    sessionPractice && Number.isInteger(saved?.step) && saved.step >= 0 && saved.step <= STEPS.length ? saved.step : 0);
  let finish = sessionPractice && !direct && options.initialStep == null && saved?.finish === true && step === 7;
  if (sessionPractice && (direct || saved || options.initialStep > 0)) {
    mode = options.mode || 'try'; playing = mode === 'watch';
  }
  function rememberStep() {
    if (!sessionPractice || restoring) return;
    try {
      localStorage.setItem(storageKey, JSON.stringify(capture()));
    } catch (_e) { /* Storage is optional on shared practice computers. */ }
  }
  function emit(e, d = '') {
    if (restoring || finish) return;
    const s = STEPS[step]; if (s && s.done(e, d)) { advance(); return; }
    if (e === 'ps-error' && step === 2) toast('Not quite', 'PowerShell did not recognise that. Copy the whole line from the coach box and paste it exactly.');
    if (e === 'device-wrong') toast('Not quite', 'Type the code exactly as PowerShell shows it, dashes included.');
    if (e === 'launch' && d !== 'ps' && d !== 'code' && d !== 'edge' && step < 2) toast('Different app', 'That one is not part of the setup. Press Start again and type PowerShell.');
  }
  function advance() {
    welcomePending = false;
    if (sessionPractice && step === 7 && !finish) {
      finish = true; rememberStep(); render(); return;
    }
    if (sessionPractice) {
      const current = capture(), next = copy(canonicalSnapshots[step + 1]);
      for (const key of ['memory', 'clip']) next.state[key] = state[key];
      next.fileSystem = current.fileSystem;
      const chat = current.windows.find(w => w.scene.kind === 'brainstem');
      if (chat) next.windows.find(w => w.scene.kind === 'brainstem').scene.log = chat.scene.log;
      restore(next);
      return;
    }
    state.completed.push(step + 1); step++; finish = false;
    rememberStep(); enterStep(); render(); if (step < STEPS.length) setTimeout(showHint, 600);
  }
  function helpUrl() {
    return HELP + '&step=' + (step + 1) + '&stepName=' + encodeURIComponent(STEPS[step]?.id || 'done');
  }
  function render() {
    const labels = express ? ['Open Copilot chat', 'Send the setup line', 'Review and agree', 'Test your agent'] :
      ['Start', 'Find PowerShell', 'Paste the line', 'Sign in', ...INTERVIEW_STEPS.map(s => s.heading)];
    const entries = (from, to) => STEPS.slice(from, to).map((s, offset) => {
      const i = from + offset;
      return `<div class="${i < step ? 'done' : i === step ? 'now' : ''}"${i === step ? ' aria-current="step"' : ''}>${stage ? (i + 1) + '. ' : ''}${labels[i]}</div>`;
    }).join('');
    const prog = $('#c-prog');
    prog.innerHTML = express ? `<section><h3>Get your agent</h3>${entries(0, 4)}</section>` :
      `<section><h3>Install</h3>${entries(0, 4)}</section><section><h3>Interview it</h3>${entries(4, 17)}</section>`;
    const list = $('.all-steps'), current = $('.now', prog);
    if (list?.open && current) {
      const bottom = current.getBoundingClientRect().bottom - list.getBoundingClientRect().bottom;
      if (bottom > 0) list.scrollTop += bottom + 4;
    }
    const acts = $('#c-acts'); acts.innerHTML = '';
    if (sessionPractice) {
      const fixes = step < 2 ? [
        'Different app? Press Start again and type PowerShell in Search.',
        'No best match yet? Type the whole name, then press Enter.'
      ] : step < 4 ? [
        'PowerShell did not recognise the line? Copy the whole line and paste it exactly, then press Enter.',
        'Sign-in page not open yet? Wait for the install to reach sign-in.',
        'Code rejected? Type the code exactly as PowerShell shows it, dashes included.'
      ] : step === 12 ? [
        'No backup yet? Export the pretend agent first, or use Skip this step.',
        'Cannot drag the file? Use Do it for me to restore the pretend backup.'
      ] : [9, 10].includes(step) ? [
        'Agent list closed? Open the button at the top right of the chat.',
        'Removing an agent? Choose Delete on hacker_news_agent.py, then confirm.'
      ] : [5, 11, 13, 15].includes(step) ? [
        'Message not sent? Type in the chat input, then press Enter.',
        'Practice app still opening? Wait for it to finish, then try again.'
      ] : step === 14 ? [
        'Library closed? Open the book button at the top right.',
        'No matching result? Search meeting prep, then choose Add on Meeting Prep.'
      ] : [
        'Cannot find the control? Use Show me where to highlight it.',
        'Practice app still opening? Wait for it to finish, then try again.'
      ];
      $('#step-fixes').replaceChildren(...fixes.map(text => {
        const li = document.createElement('li'); li.textContent = text; return li;
      }));
      $('#step-help').open = false;
      $('#step-help-link').href = helpUrl();
    }
    if (stage) {
      const context = $('#c-context');
      context.replaceChildren();
      context.hidden = !express || (step !== 1 && step !== 3);
      if (express && (step === 1 || step === 3)) {
        const content = document.createElement(step === 1 ? 'code' : 'span');
        content.id = step === 1 ? 'stage-setup-line' : 'stage-question';
        content.textContent = step === 1 ? options.story.line : options.story.question;
        context.appendChild(content);
      }
    }
    if (step >= STEPS.length) {
      $('#c-n').textContent = 'Done';
      $('#c-say').innerHTML = express ? 'All 4 steps are complete. This was practice with sample data. Use the Copy line in your own GitHub Copilot chat when you are ready.' : 'You now know AI. Interview it. Teach it. Correct it. Trade agents. <span class="journey-link">Only need an agent in Copilot Studio? <a href="../../start.html">Use the short guide.</a></span>';
      acts.innerHTML = `${express ? '' : '<a class="btn" href="../installer.html">Do it for real</a>'}<button id="again">Practice again</button><a class="btn" href="${HELP}">Get help</a>`;
      $('#again').addEventListener('click', () => stage ? restart(0) : location.reload());
      if (stage) { playing = false; renderControls(); $('#hint').style.display = 'none'; }
      speakScreen();
      return;
    }
    const s = STEPS[step];
    $('#c-n').textContent = `Step ${step + 1} of ${STEPS.length}`;
    $('#c-say').innerHTML = s.say;
    if (finish) {
      $('#c-say').textContent = 'You have met it. It still knows you.';
      $('#c-context').hidden = false;
      $('#c-context').textContent = 'Your real one should be ready: open http://localhost:7071 and do the same four steps.';
      const keep = document.createElement('button');
      keep.className = 'pri'; keep.textContent = 'Keep going'; keep.onclick = advance;
      acts.appendChild(keep);
    }
    if (s.copy) {
      const b = document.createElement('button');
      const label = express ? 'Copy' : sessionPractice ? 'Copy the real line' : 'Copy the line';
      b.className = 'pri';
      b.textContent = label;
      b.dataset.line = s.copy;
      b.addEventListener('click', async () => {
        state.clip = s.copy;
        if (express) {
          const copied = await window.AibastJourney.copyText(s.copy);
          b.textContent = copied ? 'Copied' : 'Copy failed';
          if (!copied) toast('Copy failed', 'Select and copy the setup line below the computer.');
        } else {
          try { await navigator.clipboard.writeText(s.copy); b.textContent = 'Copied'; }
          catch (_e) {
            b.textContent = 'Select the line below';
            if (!$('#session-line')) {
              const line = document.createElement('code'); line.id = 'session-line'; line.textContent = s.copy;
              acts.appendChild(line);
            }
            const range = document.createRange();
            range.selectNodeContents($('#session-line'));
            getSelection().removeAllRanges(); getSelection().addRange(range);
            toast('Clipboard unavailable', 'Press Ctrl+C to copy the selected line, then Ctrl+V in Windows PowerShell.');
          }
        }
        setTimeout(() => { b.textContent = label; }, 2500);
      });
      acts.appendChild(b);
      if (sessionPractice) {
        $('#c-context').hidden = false;
        const line = document.createElement('code'); line.id = 'session-line'; line.textContent = PS_LINE;
        const note = document.createElement('span');
        note.textContent = 'Paste this in your real PowerShell now, then come back. It installs while you practise.';
        $('#c-context').append(line, note);
      }
    }
    const h = document.createElement('button'); h.textContent = 'Show me where'; h.addEventListener('click', showHint); acts.appendChild(h);
    if (stage) {
      if ((express && step === 1) || (!express && [1, 2, 3, 5, 11, 12, 13, 15].includes(step))) {
        const type = document.createElement('button');
        type.className = 'type-helper';
        type.textContent = !express && step === 12 ? 'Do it for me' : 'Type it for me';
        if (!express && step === 12) type.classList.add('restore-helper');
        type.onclick = () => {
          setMode('try');
          if (!express && step === 12) { restoreAgent(); return; }
          if (!express && step === 1) {
            if (!start.classList.contains('open')) openStart(true);
            ssearch.value = 'PowerShell';
            ssearch.dispatchEvent(new Event('input', {bubbles:true}));
          } else {
            const selector = express ? '.vsc textarea' : {2:'.ps .in', 3:'#ghcode',
              5:'.bs form input', 11:'.bs form input', 13:'.bs form input', 15:'.bs form input'}[step];
            const input = $(selector);
            if (!input) { toast('One moment', 'Wait for the practice app to finish opening, then try again.'); return; }
            const text = express ? options.story.line : {2:PS_LINE, 3:state.code,
              5:'Remember, my name is Alex and I prepare customer meetings.',
              11:'get my latest hacker news', 13:'get my latest hacker news',
              15:'Learn a new agent called QuoteOfTheDay that gives me an inspiring quote when I ask for motivation.'}[step];
            if (input.isContentEditable) input.textContent = text;
            else input.value = text;
            input.dispatchEvent(new Event('input', {bubbles:true}));
          }
          showHint();
        };
        acts.appendChild(type);
        if (!express && step === 2) {
          const enter = document.createElement('button');
          enter.className = 'type-helper';
          enter.textContent = 'Press Enter';
          enter.onclick = () => {
            setMode('try');
            const input = $('.ps .in');
            if (input) input.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', bubbles:true}));
          };
          acts.appendChild(enter);
        }
      }
      const reset = document.createElement('button');
      reset.textContent = 'Start over';
      reset.onclick = () => restart(0);
      const help = document.createElement('a');
      help.className = 'btn';
      help.textContent = 'Get help';
      help.href = sessionPractice ? helpUrl() : HELP;
      if (sessionPractice && step > 0) {
        const back = document.createElement('button');
        back.textContent = 'Back';
        back.onclick = () => { setMode('try'); restore(canonicalSnapshots[step - 1]); };
        acts.appendChild(back);
      }
      acts.append(reset, help);
    }
    if (s.skippable) { const k = document.createElement('button'); k.textContent = 'Skip this step'; k.addEventListener('click', advance); acts.appendChild(k); }
    if (stage) { renderControls(); showHint(); }
    speakScreen();
  }
  function enterStep() {
    if (!express) return;
    if (step !== 0) return;
    if (!vs) launch('code');
    vs.el.classList.remove('min');
    focus(vs.el);
    vs.el.classList.add('agent-setup');
    vs.thread.replaceChildren();
    agentMessage('Sample reply: Paste the setup line for your chosen agent. I will read the steps and ask you to review before continuing.');
    vs.ta.value = '';
    $('.ch', vs.el).innerHTML = '<button id="agent-chat" type="button">GitHub Copilot chat</button>';
    $('#agent-chat').onclick = () => emit('agent-chat');
  }
  function agentMessage(text, cls = 'ai') {
    const message = document.createElement('div');
    message.className = 'msg show ' + cls;
    message.textContent = text;
    vs.thread.appendChild(message);
    vs.thread.scrollTop = vs.thread.scrollHeight;
    return message;
  }
  function agentButton(id, label, action) {
    const button = document.createElement('button');
    button.id = id;
    button.textContent = label;
    button.onclick = action;
    vs.thread.appendChild(button);
    vs.thread.scrollTop = vs.thread.scrollHeight;
  }
  async function sendAgentLine(prompt) {
    if (step !== 1) return;
    if (prompt !== options.story.line) {
      toast('Use the setup line', 'Copy the whole line for your chosen agent and paste it exactly.');
      return;
    }
    agentMessage(prompt, 'you').id = 'agent-pasted-line';
    emit('agent-sent');
    agentMessage('Reading the setup steps.');
    await sleep(900);
    agentMessage('Sign in with your Microsoft account in the browser window.');
    agentButton('ms-signin', 'Sign in with Microsoft (practice)', async () => {
      $('#ms-signin').remove();
      agentMessage(`I will add ${options.story.name} to your Copilot Studio, with sample data. Go ahead?`);
      agentButton('agent-yes', 'Yes', () => {
        $('#agent-yes').remove();
        agentMessage('Yes', 'you');
        agentMessage(`Done. Open Copilot Studio, open ${options.story.name}, and ask your first question.`);
        agentButton('agent-open', 'Open Copilot Studio', openStudio);
        emit('agent-ready');
      });
      showHint();
    });
    showHint();
  }
  function openStudio() {
    openEdge('https://copilotstudio.microsoft.com');
    if (stage && !edge.el.dataset.max) maximize(edge.el);
    edge.title.textContent = 'Copilot Studio';
    const studio = document.createElement('div');
    studio.className = 'sample-studio';
    const icon = path => `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="${path}"/></svg>`;
    studio.innerHTML = `<div class="studio-topbar"><strong>Copilot Studio</strong><span class="studio-environment">Sample environment</span><span class="studio-account">AL</span></div>
      <div class="studio-workspace">
        <nav class="studio-nav" aria-label="Copilot Studio">
          <span>${icon('M3 10 12 3l9 7v11h-6v-7H9v7H3z')}</span>
          <span class="selected">${icon('m8 5-6 7 6 7M16 5l6 7-6 7M14 3l-4 18')}</span>
          <span>${icon('M3 6c5-6 13 6 18 0v12c-5 6-13-6-18 0zM3 10c5-6 13 6 18 0M3 14c5-6 13 6 18 0')}</span>
        </nav>
        <div class="studio-agent-page">
          <div class="studio-agent-header"><strong id="studio-agent"></strong><span class="studio-draft">Draft</span>
            <div class="studio-tabs"><button type="button" aria-pressed="true" data-studio-tab="build">Build</button><button type="button" aria-pressed="false" data-studio-tab="preview">Preview</button><span>Evaluate</span><span class="studio-muted">Monitor</span></div>
            <span class="studio-publish">Publish</span>
          </div>
          <div class="studio-panels">
            <section class="studio-overview"><div class="studio-agent-title"><span class="studio-agent-icon">${icon('m8 5-6 7 6 7M16 5l6 7-6 7M14 3l-4 18')}</span><h2></h2></div>
              <h3>Instructions</h3><p class="studio-instructions"></p>
              <div class="studio-inventory"><section><h3>Skills</h3><p>Define behaviors through structured instructions</p></section><section><h3>Tools</h3><p>Connect the agent to external systems and actions</p></section><section><h3>Knowledge</h3><p>Provide trusted context to guide decisions</p></section><section><h3>Connected agents</h3><p>Collaborate across agents to complete work</p></section></div>
            </section>
            <aside class="studio-test"><div class="studio-test-header"><strong>Preview</strong><span>New chat</span></div>
              <div class="studio-thread" role="log"></div>
              <form><textarea id="studio-input" aria-label="Ask a question or describe what you need" placeholder="Ask a question or describe what you need" rows="2"></textarea><button id="studio-send" type="submit" aria-label="Send">${icon('m5 12 7-7 7 7M12 5v15')}</button></form>
            </aside>
          </div>
        </div>
      </div><div class="studio-footer">Practice view of Copilot Studio. Your screen may differ.</div>`;
    edge.view.replaceChildren(studio);
    $('#studio-agent').textContent = options.story.name;
    $('.studio-agent-title h2', studio).textContent = options.story.name;
    $('.studio-instructions', studio).textContent = options.story.instructions;
    studio.querySelectorAll('[data-studio-tab]').forEach(button => {
      button.onclick = () => {
        studio.querySelectorAll('[data-studio-tab]').forEach(tab => tab.setAttribute('aria-pressed', String(tab === button)));
        if (button.dataset.studioTab === 'preview') $('#studio-input').focus({preventScroll:true});
      };
    });
    $('#studio-input').value = options.story.question;
    $('#studio-input').onkeydown = event => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        $('form', studio).requestSubmit();
      }
    };
    $('form', studio).onsubmit = e => {
      e.preventDefault();
      if ($('#studio-input').value.trim() !== options.story.question) {
        toast('Try the first sample question', 'Use the question shown below this practice computer.');
        return;
      }
      const question = document.createElement('p');
      question.id = 'studio-question';
      question.className = 'sample-question';
      question.textContent = options.story.question;
      const answer = document.createElement('p');
      answer.id = 'studio-answer';
      if (options.story.answer) {
        answer.textContent = options.story.answer.replace(/[\p{Extended_Pictographic}\p{Emoji_Presentation}]\ufe0f?/gu, '') + '\n\nSample data.';
      } else {
        const demo = document.createElement('a');
        demo.textContent = "Open the demo to see this agent's sample answer";
        demo.href = options.story.demo;
        answer.append(demo, document.createTextNode('\n\nSample data.'));
      }
      $('.studio-thread', studio).replaceChildren(question, answer);
      $('#studio-input').value = '';
      $('#studio-input').rows = 1;
      $('.studio-thread', studio).scrollTop = 0;
      studio.querySelector('[data-studio-tab="preview"]').setAttribute('aria-pressed', 'true');
      studio.querySelector('[data-studio-tab="build"]').setAttribute('aria-pressed', 'false');
      emit('studio-done');
    };
    showHint();
  }
  function showHint() {
    if (disposed) return;
    const s = STEPS[step]; if (!s) return;
    if (stage) {
      const selector = target();
      const hint = $('#hint');
      hint.dataset.target = selector || '';
      const t = selector && $(selector);
      if (!t) { hint.style.display = 'none'; return; }
      const r = t.getBoundingClientRect(), p = pc.getBoundingClientRect();
      Object.assign(hint.style, {display:'block', left:(r.left-p.left-3)+'px', top:(r.top-p.top-3)+'px', width:(r.width+6)+'px', height:(r.height+6)+'px'});
      return;
    }
    if (s.hint === '#ssearch' && !start.classList.contains('open')) openStart(true);
    const t = $(s.hint); const hint = $('#hint');
    if (!t) { if (s.hint === '#ghcode') toast('Not yet', 'The sign-in page opens by itself once the install reaches that point.'); return; }
    const r = t.getBoundingClientRect(), p = pc.getBoundingClientRect();
    Object.assign(hint.style, { display: 'block', left: (r.left - p.left - 6) + 'px', top: (r.top - p.top - 6) + 'px', width: (r.width + 12) + 'px', height: (r.height + 12) + 'px' });
    hint.style.animation = 'none'; void hint.offsetWidth; hint.style.animation = '';
    setTimeout(() => { hint.style.display = 'none'; }, 3800);
  }
  function target() {
    if (express) {
      if (step === 0) return '#agent-chat';
      if (step === 1) return vs?.ta.value ? '.vsc .send' : '.vsc textarea';
      if (step === 2) return $('#agent-yes') ? '#agent-yes' : $('#ms-signin') ? '#ms-signin' : '.vsc .thread';
      if (step === 3) return $('#studio-send') ? '#studio-send' : '#agent-open';
      return null;
    }
    if (step === 0) return '#tb-start';
    if (step === 1) {
      if (!start.classList.contains('open')) return '#tb-start';
      return ssearch.value ? '.res.best' : '#ssearch';
    }
    if (step === 2) return ps?.in ? '.ps .in' : null;
    if (step === 3) {
      if ($('#ghauth')) return '#ghauth';
      if ($('#ghcode')) return $('#ghcode').value === state.code ? '#ghgo' : '#ghcode';
      return '.ps .body';
    }
    if (step === 4) return $('.bs') ? '.bs .starter-btn:nth-child(1)' : '.ps .body';
    if ([5, 11, 13, 15].includes(step)) return $('.bs form input')?.value ? '.bs form button' : '.bs form input';
    if (step === 6) return '#bs-clear';
    if (step === 7) return '.bs .starter-btn:nth-child(2)';
    if (step === 8) return '#bs-agents';
    if (step === 9 || step === 10) {
      if ($('#bs-agent-panel')?.hidden) return '#bs-agents';
      return step === 9 ? '#bs-export-agent' : $('#bs-confirm-delete') ? '#bs-confirm-delete' : '#bs-delete-agent';
    }
    if (step === 12) return $('#download-agent') ? '#download-agent' : '#bs-drop';
    if (step === 14) {
      if ($('#bs-library')?.hidden) return '#bs-book';
      return $('#bs-meeting').hidden ? '#bs-library-search' : '#bs-add-meeting';
    }
    if (step === 16) return '.bs .starter-btn:nth-child(3)';
    return null;
  }
  function setMode(next) {
    if (sessionPractice && next === 'watch' && mode !== 'watch') restore(canonicalSnapshots[step]);
    playbackVersion++;
    mode = next;
    playing = next === 'watch' && step < STEPS.length;
    renderControls();
    showHint();
    if (activeNarration?.promise && screenKey) return;
    speakScreen(true);
  }
  function renderControls() {
    if (!stage) return;
    host.dataset.mode = mode;
    $('#watch-mode').setAttribute('aria-pressed', String(mode === 'watch'));
    $('#try-mode').setAttribute('aria-pressed', String(mode === 'try'));
    $('#stage-pause').textContent = playing ? 'Pause' : 'Play';
    $('#stage-pause').hidden = mode === 'try' || step >= STEPS.length;
    $('#stage-again').hidden = mode === 'try';
    pointer.hidden = still || mode !== 'watch';
    if (!playing && !still) {
      const position = getComputedStyle(pointer);
      Object.assign(pointer.style, {left:position.left, top:position.top});
    }
  }
  async function act(animate) {
    if (finish) { $('#c-acts .pri').click(); return; }
    const current = step;
    const version = playbackVersion;
    const selector = target(), t = selector && $(selector);
    if (!t || !t.getClientRects().length) return;
    if (animate && !still) {
      const r = t.getBoundingClientRect(), p = pc.getBoundingClientRect();
      pointer.style.left = (r.left - p.left + r.width / 2) + 'px';
      pointer.style.top = (r.top - p.top + Math.min(r.height / 2, 20)) + 'px';
      await sleep(600);
      pointer.classList.add('click');
      await sleep(220);
      pointer.classList.remove('click');
    }
    if (disposed || step !== current || version !== playbackVersion || !playing || mode !== 'watch') return;
    if (selector === '#ssearch') {
      t.value = 'PowerShell';
      t.dispatchEvent(new Event('input', {bubbles:true}));
    } else if (selector === '.ps .in') {
      if (!t.textContent) { state.clip = PS_LINE; t.textContent = PS_LINE; }
      else t.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', bubbles:true}));
    } else if (selector === '#ghcode') t.value = state.code;
    else if (selector === '.bs form input') t.value = {
      5:'Remember, my name is Alex and I prepare customer meetings.',
      11:'get my latest hacker news', 13:'get my latest hacker news',
      15:'Learn a new agent called QuoteOfTheDay that gives me an inspiring quote when I ask for motivation.'
    }[step];
    else if (selector === '#bs-library-search') {
      t.value = 'meeting prep';
      t.dispatchEvent(new Event('input', {bubbles:true}));
    } else if (selector === '#download-agent') {
      const transfer = new DataTransfer();
      transfer.setData('text/plain', 'pretend:hacker-news');
      $('#bs-drop').dispatchEvent(new DragEvent('drop', {bubbles:true, dataTransfer:transfer}));
    }
    else if (selector === '#eurl') {
      t.value = LIB;
      t.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', bubbles:true}));
    } else if (selector === '.vsc textarea') t.value = STEPS[step].copy;
    else t.click();
    showHint();
  }
  async function watch() {
    while (!disposed) {
      const version = playbackVersion;
      await sleep(1000);
      if (mode === 'watch' && playing && version === playbackVersion) {
        const pending = narrationPending;
        await pending;
        if (pending !== narrationPending) continue;
        if (version === playbackVersion && playing && mode === 'watch') await act(true);
      }
    }
  }
  function dispose() {
    disposed = true;
    narrationVersion++;
    stopNarration();
    clips.forEach(pending => pending.then(src => { if (src) URL.revokeObjectURL(src.url); }));
    clearInterval(clock);
    layoutObserver?.disconnect();
    if (stage) phone.removeEventListener('change', adaptSteps);
    window.removeEventListener('beforeunload', rememberStep);
    window.removeEventListener('pagehide', rememberStep);
  }
  function restart(initialStep, nextMode = mode) {
    if (sessionPractice) {
      welcomePending = false; screenKey = null; stopNarration();
      mode = nextMode; playing = nextMode === 'watch';
      playbackVersion++;
      restore(canonicalSnapshots[initialStep]);
      if (initialStep === 0) { welcomePending = true; speakScreen(); }
      return window.practicePC;
    }
    dispose();
    return window.AibastDesktop.mount(host, {...options, initialStep, mode:nextMode});
  }
  let toastT; function toast(title, body) { const t = $('#toast'); t.innerHTML = `<b>${title}</b>${body}`; t.style.display = 'block'; clearTimeout(toastT); toastT = setTimeout(() => { t.style.display = 'none'; }, 5000); }
  if (stage) {
    const keyboardControls = '#tb-start, #tb-search, [data-app], .tbar .ctl i, .vsc .send';
    const makeAccessible = () => pc.querySelectorAll(keyboardControls).forEach(el => {
      el.tabIndex = 0; el.setAttribute('role', 'button');
      if (el.title) el.setAttribute('aria-label', el.title);
    });
    const observer = new MutationObserver(() => { makeAccessible(); showHint(); });
    observer.observe(pc, {childList:true, subtree:true});
    makeAccessible();
    pc.addEventListener('keydown', e => {
      if ((e.key === 'Enter' || e.key === ' ') && e.target.matches(keyboardControls)) {
        e.preventDefault(); e.target.click();
      }
    });
    const originalDispose = dispose;
    dispose = () => { observer.disconnect(); originalDispose(); };
  }
  function capture() {
    const values = copy(state);
    for (const key of ['news', 'exported', 'meeting', 'created']) delete values[key];
    const active = document.activeElement, activeWindow = active.closest('.win');
    return copy({
      version:2, step, finish, state:values, fileSystem,
      menu:{open:start.classList.contains('open'), query:ssearch.value},
      focus:active === ssearch ? {key:'start'} : activeWindow ? {
        key:activeWindow.dataset.key,
        index:[...activeWindow.querySelectorAll(sceneControls)].indexOf(active)
      } : null,
      windows:Object.entries(wins).map(([key, el]) => {
        let scene = {kind:'plain', html:$('.body', el).innerHTML};
        if (key === 'ps') scene = {kind:'powershell', output:ps.out.innerHTML, busy:ps.busy};
        if (key === 'edge') {
          const frame = $('#practice-page', el);
          scene = {kind:'address', url:edge.url.value, address:edge.address,
            frame:frame?.contentDocument ? {x:frame.contentWindow.scrollX, y:frame.contentWindow.scrollY,
              inputs:[...frame.contentDocument.querySelectorAll('input, textarea, select')].map(e => ({
                value:e.value, checked:e.checked
              }))} : null};
          if ($('.bs', el)) scene = {
            kind:'brainstem', url:edge.url.value, log:$('.bs .log', el).innerHTML,
            panel:!$('#bs-agent-panel', el).hidden, library:!$('#bs-library', el).hidden,
            query:$('#bs-library-search', el).value, input:$('.bs form input', el).value,
            confirm:!!$('#bs-delete-question', el)
          };
          if ($('#ghcard', el)) scene = {
            kind:'auth', url:edge.url.value, input:$('#ghcode', el)?.value || '',
            phase:$('#ghauth', el) ? 'authorize' : $('#ghcode', el) ? 'code' : 'complete',
            warning:$('#ghwarn', el)?.style.display === 'block'
          };
          scene.address = edge.address;
        }
        if (key === 'code') scene = {kind:'code', thread:vs.thread.innerHTML, input:vs.ta.value,
          folder:el.classList.contains('folder'), browser:el.classList.contains('browser'),
          log:$('.bs .log', el)?.innerHTML || ''};
        if (key === 'files' || key === 'downloads') scene = {kind:'files', folder:el.dataset.folder};
        return {key, title:el._tb.title, cls:el.className.replace(/\bmin\b/g, '').trim(),
          geometry:{left:el.style.left, top:el.style.top, width:el.style.width,
            height:el.style.height, zIndex:el.style.zIndex},
          minimized:el.classList.contains('min'), maximized:el.dataset.max || null,
          scroll:[...el.querySelectorAll('.body, .out, .log, .thread')].map(e => e.scrollTop), scene};
      })
    });
  }
  function restore(snapshot) {
    stopNarration();
    screenKey = null;
    welcomePending = false;
    const data = copy(snapshot);
    restoring = true; playbackVersion++;
    Object.keys(wins).forEach(closeWin);
    ps = edge = vs = null; z = 10; cascade = 0;
    restoreFiles(data.fileSystem);
    Object.assign(state, data.state);
    delete state.onAuth;
    step = data.step; finish = data.finish;
    $('#toast').style.display = 'none'; clearTimeout(toastT);
    for (const window of data.windows) {
      const scene = window.scene;
      if (scene.kind === 'powershell') {
        openPowerShell(); ps.out.innerHTML = scene.output; ps.busy = scene.busy;
        ps.in = $('.in[contenteditable="plaintext-only"]', ps.out);
        if (ps.in) wirePrompt();
      } else if (['address', 'auth', 'brainstem'].includes(scene.kind)) {
        openEdge(scene.kind === 'brainstem' ? 'http://localhost:7071' : scene.address || scene.url, scene);
        if (scene.kind === 'auth') {
          if (scene.phase !== 'code') {
            $('#ghcode').value = state.code; $('#ghgo').click();
            if (scene.phase === 'complete') $('#ghauth').click();
          } else {
            $('#ghcode').value = scene.input;
            $('#ghwarn').style.display = scene.warning ? 'block' : 'none';
          }
        }
        if (scene.kind === 'brainstem') {
          $('.bs .log').innerHTML = scene.log;
          $('.bs form input').value = scene.input;
          $('#bs-agent-panel').hidden = !scene.panel;
          $('#bs-library').hidden = !scene.library;
          $('#bs-library-search').value = scene.query;
          $('#bs-meeting').hidden = !/meeting\s*prep/i.test(scene.query);
          $('.bs').renderAgents();
          if (scene.confirm) $('#bs-delete-agent')?.click();
        }
        edge.url.value = scene.url;
      } else if (scene.kind === 'code') {
        openVSCode(); vs.thread.innerHTML = scene.thread; vs.ta.value = scene.input;
        vs.el.classList.toggle('folder', scene.folder); vs.el.classList.toggle('browser', scene.browser);
        if (scene.browser) {
          $('.bs-host', vs.el).innerHTML = brainstemPage();
          wireBrainstem($('.bs-host', vs.el)); $('.bs .log', vs.el).innerHTML = scene.log;
        }
      } else if (scene.kind === 'files') {
        openFiles(window.key, scene.folder);
      } else {
        makeWin(window.key, window.title, window.cls.replace(/^win\s*/, ''), 640, 420, scene.html);
      }
      const el = wins[window.key];
      Object.assign(el.style, window.geometry);
      el.classList.toggle('min', window.minimized);
      if (window.maximized) el.dataset.max = window.maximized;
      el.querySelectorAll('.body, .out, .log, .thread').forEach((e, i) => { e.scrollTop = window.scroll[i] || 0; });
      z = Math.max(z, Number(window.geometry.zIndex));
    }
    openStart(data.menu.open);
    ssearch.value = data.menu.query; search(data.menu.query);
    const foreground = top();
    Object.values(wins).forEach(el => el._tb.classList.toggle('active', el === foreground));
    if (data.focus?.key === 'start') ssearch.focus({preventScroll:true});
    else if (data.focus && wins[data.focus.key]) {
      wins[data.focus.key].querySelectorAll(sceneControls)[data.focus.index]?.focus({preventScroll:true});
    }
    restoring = false;
    render(); rememberStep();
  }
  function buildCanonicalSnapshots(widthAvailable, heightAvailable) {
    const values = copy(state);
    for (const key of ['news', 'exported', 'meeting', 'created']) delete values[key];
    const desktop = {version:2, step:0, finish:false, state:values, fileSystem:copy(fileSystem),
      menu:{open:false, query:''}, focus:null, windows:[]};
    const snapshots = [copy(desktop)];
    const prompt = '<span class="pl"><span class="y">PS C:\\Users\\You&gt; </span><span class="in" contenteditable="plaintext-only" spellcheck="false"></span></span>';
    const welcome = document.createElement('div'); welcome.innerHTML = brainstemPage();
    const brainstem = {kind:'brainstem', url:'http://localhost:7071',
      log:$('.log', welcome).innerHTML, panel:false, library:false, query:'', input:'', confirm:false};
    function window(key, title, cls, w, h, scene) {
      const i = desktop.windows.length;
      const width = Math.min(w, widthAvailable - 40), height = Math.min(h, heightAvailable - 88);
      return {key, title, cls:'win ' + cls, minimized:false, maximized:null, scroll:[],
        geometry:{width:width + 'px', height:height + 'px',
          left:Math.max(10, (widthAvailable - width) / 2 + i * 24 - 48) + 'px',
          top:Math.max(8, (heightAvailable - 48 - height) / 2 + i * 20 - 40) + 'px',
          zIndex:String(11 + i)}, scene};
    }
    const chat = () => desktop.windows.find(w => w.scene.kind === 'brainstem').scene;
    const reply = (text, thought = '') => `${thought ? `<div class="bs-thought">agent called ${esc(thought)} (sample)</div>` : ''}<div class="m"><strong>Sample reply</strong><br>${esc(text)}</div>`;
    const exchange = (q, text, thought) => { chat().log += `<div class="m me">${esc(q)}</div>` + reply(text, thought); };
    const boundaries = [
      () => { desktop.menu.open = true; },
      () => {
        desktop.menu.open = false;
        desktop.windows.push(window('ps', 'Windows PowerShell', 'ps dark', 820, 460,
          {kind:'powershell', busy:false, output:'<span>Windows PowerShell\nCopyright (C) Microsoft Corporation. All rights reserved.\n\nInstall the latest PowerShell for new features and improvements! https://aka.ms/PSWindows\n\n</span>' + prompt}));
      },
      () => {
        desktop.state.brainstemInstalled = true;
        const ps = desktop.windows[0].scene;
        ps.output = ps.output.replace(prompt, `<span class="pl"><span class="y">PS C:\\Users\\You&gt; </span><span class="in" contenteditable="false" spellcheck="false">${esc(PS_LINE)}</span></span>`);
        ps.output += '<span>\nChecking prerequisites...\n  [OK] Git, Python and GitHub CLI ready\nInstalling RAPP Brainstem...\n  [OK] Source code ready\n  [OK] Virtual environment ready\n  [OK] Dependencies installed\n  [OK] CLI installed\nAuthenticating with GitHub Copilot...\nYour code: A1B2-C3D4\nWaiting for authorization...\n</span>';
        desktop.windows.push(window('edge', 'Microsoft Edge', 'edge', 980, 600,
          {kind:'auth', url:'https://github.com/login/device', input:'', phase:'code', warning:false}));
      },
      () => {
        desktop.state.brainstemRunning = desktop.state.signedIn = true;
        desktop.windows[0].scene.output += '<span>  [OK] Authenticated - Copilot access confirmed\n  [OK] Brainstem is running at http://localhost:7071\n  Next time, just type: brainstem\n</span>';
        desktop.windows[1].scene = brainstem;
      },
      () => exchange('What can you do?', 'I can remember what you teach me, read Hacker News, and learn new agents from a file or a description.'),
      () => {
        desktop.state.memory = 'Remember, my name is Alex and I prepare customer meetings.';
        exchange(desktop.state.memory, 'Saved. I will remember that across conversations in this pretend session.', 'ManageMemory');
      },
      () => { chat().log = ''; },
      () => exchange('What do you remember?', desktop.state.memory, 'ContextMemory'),
      () => { chat().panel = true; },
      () => {
        exportFile(desktop.fileSystem);
        chat().log += reply('Exported hacker_news_agent.py to the pretend Downloads window. No real file was downloaded.');
      },
      () => {
        findFile('hacker-news', desktop.fileSystem).loaded = false; chat().panel = false;
        chat().log += reply('Removed hacker_news_agent.py. The chat is still running.');
      },
      () => {
        exchange('get my latest hacker news', 'I cannot get Hacker News: hacker_news_agent.py is not loaded. Restore the file to give me that capability again.');
        const downloads = window('downloads', 'Pretend Downloads', 'plain file-explorer downloads', 330, 190,
          {kind:'files', folder:'downloads'});
        Object.assign(downloads.geometry, {left:'8px', top:'8px'});
        desktop.windows.push(downloads);
      },
      () => {
        findFile('hacker-news', desktop.fileSystem).loaded = true; desktop.windows.pop();
        chat().log += reply('Hot-loaded hacker_news_agent.py. Instantly.');
      },
      () => exchange('get my latest hacker news', 'Hacker News is available again. Sample headline: A team shares a new open-source tool. This is not live news.', 'HackerNews'),
      () => {
        addAgent('meeting-prep', 'meeting_prep_agent.py', desktop.fileSystem);
        chat().log += reply('Installed Meeting Prep. Ask me to prep you for your next customer meeting.');
      },
      () => {
        addAgent('quote-of-the-day', 'quote_of_the_day_agent.py', desktop.fileSystem);
        exchange('Learn a new agent called QuoteOfTheDay that gives me an inspiring quote when I ask for motivation.',
          'Created QuoteOfTheDay and hot-loaded its file. Ask for motivation whenever you need it.', 'LearnNew');
      },
      () => exchange('What should I do next?', 'Interview it. Teach it. Correct it. Trade agents. Try asking Meeting Prep to prepare a customer meeting, or describe another agent to create.')
    ];
    boundaries.forEach((begin, i) => {
      begin(); desktop.step = i + 1;
      desktop.state.completed.push(i + 1); snapshots.push(copy(desktop));
    });
    return snapshots;
  }
  const initialStep = step, initialFinish = finish;
  if (sessionPractice) { step = 0; finish = false; render(); step = initialStep; finish = initialFinish; }
  let canonicalSnapshots = [];
  window.practicePC = { launch, state, fileSystem, step: () => step, STEPS, dispose, capture, restore };
  host.practiceDesktop = window.practicePC;
  if (sessionPractice) {
    layoutObserver = new ResizeObserver(entries => {
      if (disposed) { layoutObserver.disconnect(); return; }
      const {width, height} = entries[0].contentRect;
      if (!width || !height) return;
      layoutObserver.disconnect();
      canonicalSnapshots = buildCanonicalSnapshots(width, height);
      const resume = !direct && options.initialStep == null && saved?.version === 2 &&
        Array.isArray(saved.windows) && saved.menu && saved.state;
      restore(resume ? saved : canonicalSnapshots[step]);
      narrationStarted = true;
      welcomePending = step === 0;
      speakScreen();
    });
    layoutObserver.observe(pc);
    window.addEventListener('beforeunload', rememberStep);
    window.addEventListener('pagehide', rememberStep);
    pc.addEventListener('input', rememberStep);
    pc.addEventListener('click', () => queueMicrotask(rememberStep));
    $('#coach').addEventListener('click', event => {
      const link = event.target.closest('a[href]');
      if (!link || !['../installer.html', '../../start.html'].includes(link.getAttribute('href'))) return;
      event.preventDefault(); setMode('try'); openEdge(link.getAttribute('href')); rememberStep();
    });
  } else { narrationStarted = true; enterStep(); render(); }
  setTimeout(showHint, 900);
  if (stage) {
    pc.addEventListener('input', showHint);
    pc.addEventListener('click', () => setTimeout(showHint, 0));
    watch();
  }

    return window.practicePC;
  }
};
