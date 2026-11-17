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
    <div class="hint-say" id="hint-say" role="status" aria-live="polite" hidden></div>
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
    ${options.stage ? '<details class="all-steps" open><summary>Steps</summary>' : ''}
    <div class="prog" id="c-prog"></div>
    ${options.stage ? '</details>' : ''}
    ${options.stage && !['express', 'cowork'].includes(options.journey) ? '<details id="step-help"><summary>Stuck?</summary><ul id="step-fixes"></ul><a id="step-help-link">Get help</a></details>' : ''}
  </div>`;

  // Same rule as the installer page: production copies the line that fetches from
  // the counted "installers" release; a staging ring keeps its own rendered copies.
  const stagingRing = location.protocol === 'https:' && location.hostname.endsWith('.github.io')
    && location.hostname.toLowerCase() !== 'microsoft.github.io';
  const installBase = stagingRing
    ? new URL('../../', location.href).href : 'https://github.com/microsoft/aibast-agents-library/releases/download/installers/';
  const PS_LINE = `irm ${installBase}install.ps1 | iex`;
  const VS_LINE = 'Go and read https://microsoft.github.io/aibast-agents-library/docs/start/skill.md and set up my Brainstem for me.';
  const LIB = 'https://microsoft.github.io/aibast-agents-library/';
  const HELP = 'https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=v4j5cvGGr0GRqy180BHbR7RNABRLLw9Eq-9okV_7Z-hURVhJVVozNURGOE85SkI4VkFaOVhLTTNLUC4u';
  const $ = (s, r = document) => r.querySelector(s);
  const pc = $('#pc');
  const stage = !!options.stage;
  // The Cowork path is the express stage with a different scene: a browser only, no code editor.
  const cowork = options.journey === 'cowork';
  const express = cowork || options.journey === 'express';
  const sessionPractice = stage && !express;
  host.dataset.journey = cowork ? 'cowork' : express ? 'express' : 'local';
  if (express) {
    host.querySelectorAll('[data-app="edge"]').forEach(el => el.remove());
    $('#pc').setAttribute('aria-label', cowork ? 'Pretend computer: Cowork plugin setup with sample data' :
      'Pretend computer: Copilot Studio setup with sample data');
  }
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const compactSteps = matchMedia('(max-width: 600px), (min-width: 901px) and (max-height: 920px)');
  const adaptSteps = () => { if (stage) $('.all-steps').open = !compactSteps.matches; };
  if (stage) { adaptSteps(); compactSteps.addEventListener('change', adaptSteps); }
  let disposed = false, mode = options.mode || 'try';
  let studioObserver = null;
  let consentResizeObserver = null, consentMutationObserver = null, consentBanner = null;
  function reserveConsentSpace() {
    const banner = $('#aibast-clarity-consent');
    if (banner !== consentBanner) {
      if (consentBanner) consentResizeObserver.unobserve(consentBanner);
      consentBanner = banner;
      if (banner) consentResizeObserver.observe(banner);
    }
    if (!banner) { host.removeAttribute('data-consent-space'); showHint(); return; }
    const coach = $('#coach').getBoundingClientRect();
    const desktop = pc.getBoundingClientRect();
    const clearance = parseFloat(getComputedStyle($('#coach')).marginTop);
    let bottom = innerHeight - banner.getBoundingClientRect().height;
    // Measure as if the desktop's top edge were on screen. A desktop scrolled above the screen must not
    // grow: growing it moves the page, which would grow it again without end.
    const lift = Math.max(0, -desktop.top);
    if (matchMedia('(min-width:901px)').matches) bottom = Math.min(bottom, host.getBoundingClientRect().bottom + lift);
    const height = Math.max(0, bottom - (desktop.top + lift) - coach.height - clearance * 2);
    host.style.setProperty('--practice-desktop-height', height + 'px');
    host.setAttribute('data-consent-space', '');
    showHint();
  }
  let playing = stage && mode === 'watch', playbackVersion = 0;
  let inputPauseTimer = null, inputPaused = false;
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
    const notice = document.createElement('div');
    notice.id = 'watch-pause-notice';
    notice.hidden = true;
    notice.innerHTML = '<p role="status">Paused because you clicked. Press Resume to keep watching, or carry on yourself.</p><button id="watch-resume" type="button">Resume</button><a id="watch-take-over" href="#try-mode">I\'ll do it myself</a>';
    $('#coach').appendChild(notice);
    $('#watch-resume').onclick = resumeWatch;
    $('#watch-take-over').onclick = e => {
      e.preventDefault();
      setMode('try');
      $('#try-mode').focus({preventScroll:true});
    };
    $('#watch-mode').onclick = () => setMode('watch');
    $('#try-mode').onclick = () => setMode('try');
    $('#stage-pause').onclick = () => {
      if (playing) pauseWatch(false);
      else resumeWatch();
    };
    $('#stage-again').onclick = () => restart(0, 'watch');
    const ownInput = e => {
      if (!e.isTrusted || mode !== 'watch' || (!playing && !inputPaused) ||
          e.target.closest('#watch-pause-notice')) return;
      const current = step, wasFinish = finish;
      playbackVersion++;
      const selector = target(), highlighted = selector && $(selector);
      if (e.type !== 'keydown' && !highlighted?.contains(e.target)) {
        e.preventDefault();
        e.stopImmediatePropagation();
        pauseWatch(true);
        return;
      }
      if (e.type === 'pointerdown') return;
      const checkInput = () => setTimeout(() => {
        if (disposed || mode !== 'watch') return;
        if (step !== current || finish !== wasFinish) {
          if (inputPaused) resumeWatch();
        } else pauseWatch(true);
      }, 0);
      if (e.type === 'keydown' && e.key === ' ' && highlighted?.contains(e.target) &&
          e.target.matches('button, [role="button"]')) {
        e.target.addEventListener('keyup', checkInput, {once:true});
      } else checkInput();
    };
    pc.addEventListener('pointerdown', ownInput, true);
    pc.addEventListener('click', ownInput, true);
    pc.addEventListener('keydown', ownInput, true);
    document.addEventListener('visibilitychange', visibilityChanged);
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
          if (key === 'downloads' && node.id === 'hacker-news') {
            item.id = 'download-agent';
            item.draggable = false;
            wireFilePointerDrag(item);
          }
          item.ondragstart = e => e.dataTransfer.setData('text/plain', 'pretend:' + node.id);
        }
        list.appendChild(item);
      });
    }
  }
  function wireFilePointerDrag(item) {
    let drag = null;
    const clear = () => { drag?.preview?.remove(); drag = null; };
    item.addEventListener('pointerdown', e => {
      if (!e.isPrimary || e.button !== 0) return;
      drag = {id:e.pointerId, x:e.clientX, y:e.clientY, preview:null};
      item.setPointerCapture(e.pointerId);
      e.preventDefault();
    });
    item.addEventListener('pointermove', e => {
      if (!drag || drag.id !== e.pointerId) return;
      if (!drag.preview && Math.hypot(e.clientX - drag.x, e.clientY - drag.y) >= 6) {
        drag.preview = document.createElement('div');
        drag.preview.className = 'file-drag-preview';
        drag.preview.setAttribute('aria-hidden', 'true');
        drag.preview.textContent = item.textContent;
        pc.appendChild(drag.preview);
      }
      if (drag.preview) Object.assign(drag.preview.style, {
        left:e.clientX + 'px', top:e.clientY + 'px'
      });
    });
    item.addEventListener('pointerup', e => {
      if (!drag || drag.id !== e.pointerId) return;
      const dropped = drag.preview &&
        document.elementFromPoint(e.clientX, e.clientY)?.closest('#bs-drop');
      clear();
      if (dropped) restoreAgent();
    });
    item.addEventListener('pointercancel', clear);
    item.addEventListener('lostpointercapture', clear);
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
  if (cowork) delete APPS.code;
  const PINS = ['edge', 'word', 'excel', 'outlook', 'teams', 'settings', 'files', 'calc', 'photos', 'ps', 'code', 'terminal'].filter(k => APPS[k]);
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
  ssearch.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); const best = $('.res.best', results) || $('.res[data-app]', results); if (best) launch(best.dataset.app); } if (e.key === 'Escape') openStart(false); });
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
      if (!document.hidden && (mode === 'try' || playing)) remaining -= Math.min(now - last, 80);
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
    ps.in.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') { e.preventDefault(); psRun(ps.in.textContent); }
      // The practice computer uses Windows keys even when hosted by a Mac.
      if (e.ctrlKey && e.key.toLowerCase() === 'v' && navigator.platform.startsWith('Mac')) {
        e.preventDefault(); psPaste();
      }
    });
    ps.in.addEventListener('paste', (e) => {
      e.preventDefault();
      pastePrompt(e.clipboardData.getData('text/plain'));
    });
  }
  function pastePrompt(text) {
    if (!ps?.in?.isContentEditable) return;
    const selection = getSelection(), range = selection.rangeCount ? selection.getRangeAt(0) : document.createRange();
    if (!ps.in.contains(range.commonAncestorContainer)) {
      range.selectNodeContents(ps.in); range.collapse(false);
    }
    range.deleteContents();
    const node = document.createTextNode(text.replace(/\r?\n/g, ' ').trim());
    range.insertNode(node); range.setStartAfter(node); range.collapse(true);
    selection.removeAllRanges(); selection.addRange(range);
    ps.in.focus({preventScroll:stage});
    ps.out.parentElement.scrollTop = ps.out.parentElement.scrollHeight;
    emit('ps-paste');
  }
  function psPaste() {
    pastePrompt(state.clip || PS_LINE);
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
      edge.title.textContent = 'Device Activation'; edge.view.innerHTML = `<div class="mock"><div class="gh"><div class="card" id="ghcard"><h2>Device Activation</h2><p style="text-align:center;color:#57606a;margin:0 0 6px">Enter the code displayed in PowerShell</p><p class="device-code">Your code: <strong>${esc(state.code)}</strong></p><label for="ghcode">Device code</label><input id="ghcode" maxlength="9" placeholder="XXXX-XXXX" autocomplete="off"><div class="warn" id="ghwarn">That code does not match. Look at the PowerShell window: the code is on the line that says Your code.</div><button id="ghgo">Continue</button></div></div></div>`;
      $('#ghgo', edge.view).addEventListener('click', () => {
        const v = $('#ghcode', edge.view).value.trim().toUpperCase();
        if (v !== state.code) { $('#ghwarn', edge.view).style.display = 'block'; emit('device-wrong'); return; }
        $('#ghcard', edge.view).innerHTML = `<h2>Authorize RAPP Brainstem</h2><p style="text-align:center;color:#57606a">RAPP Brainstem by <b>You</b> wants to use GitHub Copilot on your behalf.</p><p style="font-size:12px;color:#57606a;border:1px solid #d0d7de;border-radius:6px;padding:8px">This is the practice computer. No real GitHub account is involved.</p><button id="ghauth">Authorize</button>`;
        $('#ghauth', edge.view).addEventListener('click', () => { $('#ghcard', edge.view).innerHTML = '<h2>Congratulations, you\'re all set!</h2><p style="text-align:center;color:#57606a">Your device is now connected. You can close this tab and go back to PowerShell.</p>'; emit('device-ok'); if (state.onAuth) { state.onAuth(); state.onAuth = null; } });
      });
      if (!restoring) setTimeout(() => { const i = edge && $('#ghcode', edge.view); if (i) i.focus({preventScroll:stage}); }, 50);
    } else browserPanel(route.url);
  }
  function recalledMemory(memory) {
    return memory === 'Remember, my name is Alex and I prepare customer meetings.'
      ? 'You told me your name is Alex and that you prepare customer meetings.'
      : memory || 'You have not taught me anything in this practice session yet.';
  }
  function sampleExchange(question, text, thought = '') {
    return `<div class="m me">${esc(question)}</div><div class="m">${thought ? `<div class="bs-thought">agent called ${esc(thought)} (sample)</div>` : ''}<strong>Sample reply</strong><br>${esc(text)}</div>`;
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
    const reply = (question, text, thought = '') => {
      log.insertAdjacentHTML('beforeend', sampleExchange(question, text, thought));
      log.scrollTop = log.scrollHeight;
    };
    const send = q => {
      if (!q.trim()) return;
      if (finish && q === 'What do you remember?') {
        const keep = $('#stage-keep-going');
        keep?.focus({preventScroll:true});
        keep?.animate([{boxShadow:'0 0 0 6px #ffb900'}, {boxShadow:'0 0 0 0 transparent'}],
          {duration:600, iterations:2});
        showHint();
        return;
      }
      let event = '', answer = 'This pretend chat only demonstrates the interview. Follow the hint below.', thought = '';
      if (q === 'What can you do?') {
        answer = 'I can remember what you teach me, read Hacker News, and learn new agents from a file or a description.';
        event = 'capabilities';
      } else if (q === 'What do you remember?') {
        answer = recalledMemory(state.memory);
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
      reply(q, answer, thought); emit(event);
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
        reply('Export hacker_news_agent.py', 'Exported hacker_news_agent.py to the pretend Downloads window. No real file was downloaded.'); emit('exported');
      };
      $('#bs-delete-agent', root).onclick = () => {
        if ($('#bs-delete-question', root)) return;
        panel.insertAdjacentHTML('beforeend', '<div id="bs-delete-question">Remove hacker_news_agent.py? <button id="bs-confirm-delete">Confirm delete</button><button id="bs-cancel-delete">Cancel</button></div>');
        $('#bs-cancel-delete', root).onclick = () => renderAgents();
        $('#bs-confirm-delete', root).onclick = () => {
          if (!state.exported) { toast('Back up first', 'Export the pretend agent before deleting it.'); return; }
          state.news = false; renderAgents(); reply('Confirm delete hacker_news_agent.py', 'Removed hacker_news_agent.py. The chat is still running.'); emit('deleted');
        };
        showHint();
      };
    }
    $('.bs', root).renderAgents = renderAgents;
    $('#bs-book', root).onclick = () => {
      $('#bs-agent-panel', root).hidden = true;
      const library = $('#bs-library', root);
      library.hidden = !library.hidden;
      if (!library.hidden) $('#bs-library-search', root).focus({preventScroll:true});
      showHint();
    };
    $('#bs-library-search', root).oninput = e => {
      $('#bs-meeting', root).hidden = !/meeting\s*prep/i.test(e.target.value); showHint();
    };
    $('#bs-add-meeting', root).onclick = () => {
      state.meeting = true; $('#bs-library', root).hidden = true;
      reply('Add Meeting Prep', 'Installed Meeting Prep. Ask me to prep you for your next customer meeting.'); emit('installed');
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
    $('.bs .log').insertAdjacentHTML('beforeend', sampleExchange('Restore hacker_news_agent.py', 'Hot-loaded hacker_news_agent.py. Instantly.'));
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
    vs.ta.addEventListener('keydown', (e) => {
      if (express && step === 1 && e.ctrlKey && e.key.toLowerCase() === 'v') {
        e.preventDefault(); pasteAgentLine();
      } else if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
    });
    vs.ta.addEventListener('contextmenu', e => {
      if (!express || step !== 1) return;
      e.preventDefault(); pasteAgentLine();
    });
    vs.ta.addEventListener('paste', () => setTimeout(() => emit('vs-paste'), 0));
    $('.send', el).addEventListener('click', send);
    if (!restoring) setTimeout(() => {
      if (vs && top() === vs.el) vs.ta.focus({preventScroll:stage});
    }, 50);
  }
  function pasteAgentLine() {
    vs.ta.setRangeText(state.clip || options.story.line, vs.ta.selectionStart, vs.ta.selectionEnd, 'end');
    vs.ta.dispatchEvent(new Event('input', {bubbles:true}));
    vs.ta.focus({preventScroll:true});
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
    { id: 'signin', say: 'It is installing. When the sign-in page opens, type the code shown on the sign-in page (the line that says <b>Your code</b>), press Continue, then Authorize.', hint: '#ghcode', done: (e) => e === 'device-ok' },
  ];
  const interview = (id, heading, tourHint, event, skippable = false) => ({
    id, heading, tourHint, skippable, say:`<strong>${heading}</strong> ${tourHint}`, done:e => e === event
  });
  const INTERVIEW_STEPS = [
    interview('ask-capabilities', 'Ask what it can do.', 'Click <strong>What can you do?</strong>', 'capabilities'),
    interview('introduce', 'Introduce yourself.', 'Type <em>"Remember, my name is … and I …"</em> and press <strong>Enter</strong>.', 'introduced'),
    interview('clear-slate', 'Now, wipe the slate.', 'Click <strong>Clear</strong> in the toolbar above the message box.', 'cleared'),
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
  const STEPS = cowork ? [
    {id:'cowork-download', say:'Choose <b>Download Cowork plugin</b>. One file is saved to your Downloads folder. The real download link is below this computer.', done:e => e === 'cowork-downloaded'},
    {id:'cowork-upload', say:'In Cowork, open <b>Customize</b>, then <b>Manage all</b>, then <b>Add</b>, then <b>Upload</b>, and pick the file you downloaded.', done:e => e === 'cowork-uploaded'},
    {id:'cowork-publish', say:'Keep <b>Only you</b> selected, then choose <b>Publish</b>. The plugin appears in your list.', done:e => e === 'cowork-published'},
    {id:'cowork-ask', say:'Your plugin opens a <b>new task</b> with the first sample question ready. Press <b>Send</b>. The recorded answer uses <b>sample data</b>.', done:e => e === 'cowork-done'}
  ] : express ? [
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
  function setCaption(text) {
    const caption = $('#practice-caption');
    const normalize = value => value.replace(/\s+/g, ' ').trim();
    const instructions = normalize($('#c-say').textContent + ' ' +
      ($('#c-context').hidden ? '' : $('#c-context').textContent) + ' ' +
      ($('.bs-finish p')?.textContent || ''));
    const repeated = !text || normalize(text).split(/(?<=[.!?])\s+/)
      .every(sentence => instructions.includes(sentence));
    caption.classList.toggle('caption-repeated', repeated);
    caption.setAttribute('aria-live', repeated ? 'off' : 'polite');
    caption.textContent = repeated ? '' : text;
  }
  function narrate(seg, fallback) {
    const caption = $('#practice-caption'), voice = $('#practice-voice');
    if (!seg?.media) {
      setCaption(fallback);
      window.__narration.push({id:screenKey, captions:[fallback], fallback:'captions', playedMs:0});
      return Promise.resolve();
    }
    const media = seg.media, shown = [];
    const log = {id:seg.id, durationMs:media.durationMs, captions:shown};
    window.__narration.push(log);
    let finished = false, tick, elapsed = 0, silentStart, paused = false;
    let resolve;
    const promise = new Promise(done => { resolve = done; });
    const show = ms => {
      const cues = seg.captions.segments;
      const cue = cues.find(c => ms >= c.startMs && ms < c.endMs) || cues[cues.length - 1];
      const text = cue?.text || fallback;
      if (caption.textContent !== text) {
        setCaption(text);
        requestAnimationFrame(showHint);
      }
      if (shown[shown.length - 1] !== text) shown.push(text);
    };
    const done = stopped => {
      if (finished) return;
      finished = true;
      clearInterval(tick);
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
      clearInterval(tick);
      tick = setInterval(() => {
        const now = performance.now();
        if (!paused && !document.hidden) elapsed += Math.min(now - silentStart, 200);
        silentStart = now;
        show(elapsed);
        if (elapsed >= media.durationMs) done(false);
      }, 100);
    };
    const play = () => voice.play().catch(() => {
      if (!finished) { log.fallback = 'captions'; silent(); }
    });
    const run = {promise, cancel:() => done(true), silence:silent,
      pause:() => { paused = true; voice.pause(); },
      resume:() => {
        if (finished) return;
        paused = false; silentStart = performance.now();
        if (voice.getAttribute('src') && !tick) play();
      }};
    activeNarration = run;
    paused = stage && (document.hidden || (mode === 'watch' && !playing));
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
      if (!paused) play();
    });
    return promise;
  }
  function speakScreen(replay = false) {
    if (!stage || restoring || !narrationStarted) return;
    const key = welcomePending ? 'welcome' : finish ? 'finish' : STEPS[step]?.id;
    if (key === screenKey && !replay) return;
    screenKey = key;
    stopNarration();
    if (!key) { setCaption(''); return; }
    const version = ++narrationVersion;
    narrationPending = narrationData.then(data => {
      if (disposed || version !== narrationVersion) return;
      const segment = data?.[cowork ? 'cowork' : express ? 'express' : 'brainstem']?.segments.find(s => s.screenId === key);
      const spoken = narrate(segment, $('#c-say').textContent);
      // Without a recorded voice the caption is instant, so Watch leaves time to read each Cowork step.
      return cowork && !segment ? spoken.then(() => sleep(3200)) : spoken;
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
  const reload = performance.getEntriesByType('navigation')[0]?.type === 'reload';
  let step = options.initialStep ?? (stage && direct ? requested - 1 :
    sessionPractice && Number.isInteger(saved?.step) && saved.step >= 0 && saved.step <= STEPS.length ? saved.step : 0);
  let finish = sessionPractice && !direct && options.initialStep == null && saved?.finish === true && step === 7;
  // A different linked step is a shared starting point, not this device's saved place.
  let resumedStep = sessionPractice && (!direct || reload || saved?.step === step) &&
    options.initialStep == null && step > 0 &&
    step < STEPS.length ? step + 1 : null;
  if (resumedStep) {
    const notice = document.createElement('div');
    notice.id = 'resume-notice';
    const startOver = document.createElement('button');
    startOver.id = 'start-from-one';
    startOver.type = 'button';
    startOver.textContent = 'Start from step 1';
    startOver.onclick = () => restart(0);
    notice.append(`Picking up at step ${resumedStep}. `, startOver);
    $('#stage-controls').after(notice);
  }
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
    if (inputPaused) resumeWatch();
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
    if (narrationStarted && resumedStep && (resumedStep !== step + 1 || finish)) {
      resumedStep = null;
      $('#resume-notice')?.remove();
    }
    if (stage) {
      const url = new URL(location.href);
      url.searchParams.set('step', Math.min(step + 1, STEPS.length));
      history.replaceState(history.state, '', url);
    }
    $('.bs-finish')?.remove();
    const labels = cowork ? ['Download the plugin', 'Upload it to Cowork', 'Publish for yourself', 'Ask your first question'] :
      express ? ['Open Copilot chat', 'Send the setup line', 'Review and agree', 'Test your agent'] :
      ['Start', 'Find PowerShell', 'Paste the line', 'Sign in', ...INTERVIEW_STEPS.map(s => s.heading)];
    const entries = (from, to) => STEPS.slice(from, to).map((s, offset) => {
      const i = from + offset;
      return `<div class="${i < step ? 'done' : i === step ? 'now' : ''}"${i === step ? ' aria-current="step"' : ''}>${stage ? (i + 1) + '. ' : ''}${labels[i]}</div>`;
    }).join('');
    const prog = $('#c-prog');
    prog.innerHTML = express ? `<section><h3>${cowork ? 'Add it to your Cowork' : 'Get your agent'}</h3>${entries(0, 4)}</section>` :
      `<section><h3>Install</h3>${entries(0, 4)}</section><section><h3>Interview it</h3>${entries(4, 17)}</section>`;
    const list = $('.all-steps'), current = $('.now', prog);
    if (list?.open && current) revealCurrentStep();
    const acts = $('#c-acts'); acts.innerHTML = '';
    if (sessionPractice) {
      const fixes = step < 2 ? [
        'Different app? Press Start again and type PowerShell in Search.',
        'No best match yet? Type the whole name, then press Enter.'
      ] : step < 4 ? [
        'PowerShell did not recognise the line? Copy the whole line and paste it exactly, then press Enter.',
        'Sign-in page not open yet? Wait for the install to reach sign-in.',
        'PowerShell behind the browser? Your code is also shown on the sign-in card, just above Device code.',
        'Code rejected? Type the code exactly as PowerShell shows it, dashes included.'
      ] : step === 12 ? [
        'No backup yet? Export the pretend agent first, or use Skip this step.',
        'Cannot drag the file? Use Do it for me to restore the pretend backup.'
      ] : [9, 10].includes(step) ? [
        'Agent list closed? Open the button at the top right of the chat.',
        'Removing an agent? Choose Delete on hacker_news_agent.py, then confirm.'
      ] : step === 13 ? [
        'Type "get my latest hacker news" in the chat, then press Enter.',
        'Use Type it for me to fill the words, then send them yourself.'
      ] : [5, 11, 15].includes(step) ? [
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
      const stageText = express && (step === 3 || (step === 1 && !cowork));
      context.hidden = !stageText && !(sessionPractice && step === 13);
      if (stageText) {
        const content = document.createElement(step === 1 ? 'code' : 'span');
        content.id = step === 1 ? 'stage-setup-line' : 'stage-question';
        content.textContent = step === 1 ? options.story.line : options.story.question;
        context.appendChild(content);
      }
      if (sessionPractice && step === 13) {
        const prompt = document.createElement('code');
        prompt.textContent = 'get my latest hacker news';
        context.append('Type this in the chat: ', prompt);
      }
    }
    if (step >= STEPS.length) {
      $('#c-n').textContent = 'Done';
      $('#c-say').innerHTML = cowork ? 'All 4 steps are complete. This was practice with sample data. Use the download link below this computer to add the plugin to your own Cowork when you are ready.' : express ? 'All 4 steps are complete. This was practice with sample data. Use the Copy line in your own GitHub Copilot chat when you are ready.' : 'You now know AI. Interview it. Teach it. Correct it. Trade agents.';
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
      $('#c-say').textContent = 'Continue the interview with the button in the chat.';
      $('#c-context').hidden = false;
      $('#c-context').textContent = 'Your real one should be ready: open http://localhost:7071 and do the same four steps.';
      const notice = document.createElement('section');
      notice.className = 'bs-finish';
      const message = document.createElement('p');
      message.setAttribute('role', 'status');
      message.textContent = 'You have met it. It still knows you.';
      const stageKeep = document.createElement('button');
      stageKeep.id = 'stage-keep-going';
      stageKeep.className = 'pri';
      stageKeep.textContent = 'Keep going';
      stageKeep.onclick = advance;
      notice.append(message, stageKeep);
      $('.bs .log').after(notice);
      stageKeep.focus({preventScroll:true});
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
      if ((express && !cowork && step === 1) || (!express && [1, 2, 3, 5, 11, 12, 13, 15].includes(step))) {
        const type = document.createElement('button');
        type.className = 'type-helper';
        if (s.copy) type.classList.add('paste-helper');
        if (sessionPractice && step === 13) type.classList.add('news-helper');
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
          focusStepInput();
          showHint();
        };
        acts.appendChild(type);
        if (sessionPractice && step === 13) {
          const item = document.createElement('li'), fill = type.cloneNode(true);
          fill.onclick = type.onclick;
          item.appendChild(fill);
          $('#step-fixes').appendChild(item);
        }
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
    if (s.skippable) {
      const k = document.createElement('button');
      k.textContent = 'Skip this step';
      k.addEventListener('click', () => sessionPractice ? restore(canonicalSnapshots[step + 1]) : advance());
      acts.appendChild(k);
    }
    if (stage) {
      setCaption($('#practice-caption').textContent);
      renderControls(); showHint();
    }
    speakScreen();
  }
  function revealCurrentStep() {
    const list = $('.all-steps'), current = $('[aria-current="step"]', list);
    if (!list?.open || !current) return;
    const prog = $('#c-prog');
    const scroller = getComputedStyle(prog).position === 'absolute' ? prog : list;
    const bounds = scroller.getBoundingClientRect(), rect = current.getBoundingClientRect();
    if (rect.bottom > bounds.bottom) scroller.scrollTop += rect.bottom - bounds.bottom + 4;
    if (rect.top < bounds.top + 24) scroller.scrollTop -= bounds.top + 24 - rect.top;
  }
  if (stage) $('.all-steps').addEventListener('toggle', revealCurrentStep);
  function enterStep() {
    if (!express) return;
    if (cowork) { if (step < STEPS.length) coworkScene(); return; }
    if (step === 1) { focusStepInput(); return; }
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
  function focusStepInput() {
    const selector = express ? (step === 1 ? '.vsc textarea' : null) :
      {1:'#ssearch', 2:'.ps .in', 3:'#ghcode', 5:'.bs form input',
        11:'.bs form input', 13:'.bs form input', 15:'.bs form input'}[step];
    if (selector) $(selector)?.focus({preventScroll:true});
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
    requestAgentSignin();
  }
  function agentSetupReady() {
    agentMessage(`Done. Open Copilot Studio, open ${options.story.name}, and ask your first question.`);
    agentButton('agent-open', 'Open Copilot Studio', openStudio);
  }
  function requestAgentSignin() {
    agentMessage('Sign in with your Microsoft account in the browser window.');
    agentButton('ms-signin', 'Sign in with Microsoft (practice)', () => {
      $('#ms-signin').remove();
      agentMessage(`I will add ${options.story.name} to your Copilot Studio, with sample data. Go ahead?`);
      agentButton('agent-yes', 'Yes', () => {
        $('#agent-yes').remove();
        agentMessage('Yes', 'you');
        agentSetupReady();
        emit('agent-ready');
      });
      showHint();
    });
    showHint();
  }
  function renderStudioAnswer(text) {
    const fragment = document.createDocumentFragment();
    const inline = (node, value) => {
      let end = 0;
      for (const match of value.matchAll(/\*\*([^*\n]+)\*\*/g)) {
        node.append(document.createTextNode(value.slice(end, match.index)));
        const bold = document.createElement('strong');
        bold.textContent = match[1];
        node.append(bold);
        end = match.index + match[0].length;
      }
      node.append(document.createTextNode(value.slice(end)));
    };
    const lines = text.split('\n');
    const separator = /^\s*\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)+\|?\s*$/;
    const cells = line => line.trim().replace(/^\||\|$/g, '').split('|').map(cell => cell.trim());
    const tableAt = index => lines[index]?.includes('|') && separator.test(lines[index + 1] || '');
    let index = 0;
    while (index < lines.length) {
      const line = lines[index];
      if (!line.trim()) { index++; continue; }
      if (tableAt(index)) {
        const table = document.createElement('table');
        const head = document.createElement('thead');
        const body = document.createElement('tbody');
        const row = (parent, values, tag) => {
          const tr = document.createElement('tr');
          for (const value of values) {
            const cell = document.createElement(tag);
            if (tag === 'th') cell.scope = 'col';
            inline(cell, value);
            tr.append(cell);
          }
          parent.append(tr);
        };
        const headers = cells(line);
        row(head, headers, 'th');
        index += 2;
        while (index < lines.length && lines[index].includes('|') && cells(lines[index]).length === headers.length) {
          row(body, cells(lines[index++]), 'td');
        }
        table.append(head, body);
        fragment.append(table);
      } else if (/^#{1,2} /.test(line)) {
        const heading = document.createElement(line.startsWith('## ') ? 'h4' : 'h3');
        inline(heading, line.replace(/^#{1,2} /, ''));
        fragment.append(heading);
        index++;
      } else if (/^[-*] /.test(line)) {
        const list = document.createElement('ul');
        while (index < lines.length && /^[-*] /.test(lines[index])) {
          const item = document.createElement('li');
          inline(item, lines[index++].slice(2));
          list.append(item);
        }
        fragment.append(list);
      } else {
        const paragraph = document.createElement('p');
        const content = [lines[index++]];
        while (index < lines.length && lines[index].trim()
            && !/^#{1,2} |^[-*] /.test(lines[index]) && !tableAt(index)) {
          content.push(lines[index++]);
        }
        inline(paragraph, content.join('\n'));
        fragment.append(paragraph);
      }
    }
    return fragment;
  }
  // ── Cowork (sample) ──
  // One scene for the four Cowork steps. Each step starts from a known screen, so a linked step,
  // Start over and Watch all draw the same thing.
  function coworkScene() {
    studioObserver?.disconnect();
    const name = options.story.name, file = options.story.file;
    openEdge('https://m365.cloud.microsoft/');
    if (stage && !edge.el.dataset.max) maximize(edge.el);
    edge.title.textContent = step === 0 ? 'Agent Library' : 'Cowork';
    edge.url.value = step === 0 ? LIB : 'https://m365.cloud.microsoft/';
    const icon = (path, size = 18) => `<svg viewBox="0 0 20 20" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="${path}"/></svg>`;
    const root = document.createElement('div');
    root.className = 'sample-cowork';
    const put = (el, text) => { el.textContent = text; return el; };
    const make = (tag, cls, text) => { const el = document.createElement(tag); if (cls) el.className = cls; if (text) el.textContent = text; return el; };
    const button = (id, label, cls) => { const b = make('button', cls, label); b.type = 'button'; b.id = id; return b; };
    if (step === 0) {
      root.classList.add('cowork-library');
      const card = make('div', 'cowork-card');
      card.append(make('p', 'cowork-kicker', 'AI BAST Agent Library'), make('h2', '', name),
        make('p', '', 'Cowork plugin. One file, sample data only.'));
      const download = button('cowork-download', 'Download Cowork plugin', 'cowork-primary');
      const saved = make('p', 'cowork-saved');
      saved.setAttribute('role', 'status');
      download.onclick = async () => {
        if (download.disabled) return;
        download.disabled = true;
        saved.append(make('strong', '', file), ' saved to Downloads.');
        await sleep(900);
        emit('cowork-downloaded');
      };
      card.append(download, saved);
      root.append(card);
      edge.view.replaceChildren(root);
      showHint();
      return;
    }
    root.innerHTML = `
      <nav class="cowork-rail" aria-label="Cowork">
        <button type="button" id="cowork-new-task">${icon('M10 3.5a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13M10 6.5v7M6.5 10h7')}<span>New task</span></button>
        <span class="cowork-rail-icon">${icon('M4 6h3M4 10h3M4 14h3M9 6h7M9 10h7M9 14h7')}</span>
        <button type="button" id="cowork-customize">${icon('M4 6h7m3 0h2M4 14h2m3 0h7M12.5 4v4M7.5 12v4')}<span>Customize</span></button>
        <span class="cowork-me" aria-hidden="true">AB</span>
      </nav>
      <div class="cowork-main">
        <div class="cowork-bar"><strong>Cowork</strong><span>Sample</span></div>
        <div class="cowork-page"></div>
        <div class="cowork-footer">Practice view of Cowork. Your screen may differ.</div>
      </div>
      <div class="cowork-layer" hidden></div>`;
    edge.view.replaceChildren(root);
    const page = $('.cowork-page', root), layer = $('.cowork-layer', root);
    const overlay = (label, ...children) => {
      const box = make('div', 'cowork-dialog');
      box.setAttribute('role', 'dialog'); box.setAttribute('aria-label', label);
      box.append(make('h3', '', label), ...children);
      layer.replaceChildren(box); layer.hidden = false;
    };
    const closeOverlay = () => { layer.replaceChildren(); layer.hidden = true; };
    const home = ask => {
      const col = make('div', 'cowork-col');
      col.append(make('h2', 'cowork-greeting', 'What can I do for you?'));
      const form = make('form', 'cowork-box');
      if (ask) {
        const input = make('textarea'); input.id = 'cowork-input'; input.rows = 3;
        input.setAttribute('aria-label', 'Start a task'); input.value = options.story.question;
        const send = button('cowork-send', '', 'cowork-send'); send.type = 'submit';
        send.setAttribute('aria-label', 'Send'); send.innerHTML = icon('M10 16V4M5 9l5-5 5 5', 16);
        input.onkeydown = e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); } };
        form.append(input, send);
        form.onsubmit = e => { e.preventDefault(); answer(input.value.trim()); };
      } else form.append(make('span', 'cowork-placeholder', 'Start a task...'));
      col.append(form);
      page.replaceChildren(col);
    };
    const plugins = (published, menu) => {
      const col = make('div', 'cowork-col');
      const head = make('div', 'cowork-head');
      head.append(make('h2', '', 'Plugins'));
      if (!published) head.append(button('cowork-add', 'Add', 'cowork-primary'));
      col.append(head);
      if (menu) {
        const list = make('div', 'cowork-menu');
        const upload = button('cowork-upload', 'Upload');
        upload.onclick = () => {
          const pick = button('cowork-file', file, 'cowork-file');
          pick.onclick = () => emit('cowork-uploaded');
          overlay('Downloads', make('p', '', 'Pick the file you downloaded.'), pick);
        };
        list.append(upload);
        col.append(list);
      }
      if (published) {
        const row = make('div', 'cowork-plugin');
        row.id = 'cowork-plugin';
        row.append(make('strong', '', name), make('span', '', 'Published · Only you'));
        col.append(row);
      } else col.append(make('p', 'cowork-empty', 'No plugins added yet.'));
      page.replaceChildren(col);
      const add = $('#cowork-add', col);
      if (add) add.onclick = () => plugins(false, true);
    };
    const answer = text => {
      const samples = [{prompt:options.story.question, assistant_response:options.story.answer},
        ...(options.story.samples || [])];
      const sample = samples.find(item => item.prompt === text);
      if (!sample) {
        toast('Try the first sample question', 'Use the question shown below this practice computer.');
        return;
      }
      const col = make('div', 'cowork-col cowork-chat');
      const question = make('p', 'cowork-ask', sample.prompt); question.id = 'cowork-question';
      const trail = make('p', 'cowork-trail', `Reviewed custom skill ${name}`); trail.id = 'cowork-skill';
      const reply = make('div', 'cowork-answer'); reply.id = 'cowork-answer';
      if (sample.assistant_response) {
        reply.append(renderStudioAnswer(sample.assistant_response.replace(/[\p{Extended_Pictographic}\p{Emoji_Presentation}]️?/gu, '') + '\n\nSample data.'));
      } else {
        const demo = make('a', '', "Open the demo to see this agent's sample answer");
        demo.href = options.story.demo;
        reply.append(demo, make('p', '', 'Sample data.'));
      }
      col.append(make('p', 'cowork-when', 'Just now'), question, trail, reply);
      page.replaceChildren(col);
      page.scrollTop = 0;
      emit('cowork-done');
    };
    $('#cowork-customize').onclick = () => {
      if (step !== 1) return;
      const manage = button('cowork-manage', 'Manage all', 'cowork-primary');
      manage.onclick = () => { closeOverlay(); plugins(false, false); };
      overlay('Customize', make('p', '', 'Plugins add skills to Cowork. You have none yet.'), manage);
    };
    $('#cowork-new-task').onclick = () => { if (step === 3) { home(true); showHint(); } };
    if (step === 1) home(false);
    else if (step === 2) {
      plugins(false, false);
      const who = make('div', 'cowork-who');
      who.setAttribute('role', 'radiogroup'); who.setAttribute('aria-label', 'Who can use this plugin');
      for (const [label, on] of [['Only you', true], ['People in your organization', false]]) {
        const option = make('span', on ? 'on' : '', label);
        option.setAttribute('role', 'radio'); option.setAttribute('aria-checked', String(on));
        who.append(option);
      }
      const publish = button('cowork-publish', 'Publish', 'cowork-primary');
      publish.onclick = async () => {
        if (publish.disabled) return;
        publish.disabled = true;
        closeOverlay(); plugins(true, false);
        await sleep(900);
        emit('cowork-published');
        if (!disposed) { home(true); showHint(); }
      };
      overlay('Publish plugin', put(make('p', 'cowork-name'), name), make('p', '', 'Who can use this plugin'), who, publish);
    } else home(true);
    showHint();
  }
  function openStudio() {
    studioObserver?.disconnect();
    openEdge('https://copilotstudio.microsoft.com');
    if (stage && !edge.el.dataset.max) maximize(edge.el);
    edge.title.textContent = 'Copilot Studio';
    const studio = document.createElement('div');
    studio.className = 'sample-studio';
    const icon = path => `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="${path}"/></svg>`;
    const person = icon('M8 7a4 4 0 1 0 8 0 4 4 0 1 0-8 0M4 21v-3a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v3');
    const chat = icon('M4 4h16v12H9l-5 4z');
    const more = icon('M5 12h2m4 0h2m4 0h2');
    const plus = icon('M12 5v14M5 12h14');
    studio.innerHTML = `
        <nav class="studio-nav" aria-label="Copilot Studio">
          <span class="studio-logo" aria-label="Copilot Studio"><img width="24" height="24" alt="" src="data:image/svg+xml,%3csvg%20width='24'%20height='24'%20viewBox='0%200%2024%2024'%20fill='none'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M16.7725%201.10115C13.8009%200.110601%2012.3149%20-0.384405%2011.2875%200.356016C10.2601%201.0965%2010.2603%202.66277%2010.2603%205.79522V8.53129L7.14408%207.49292C4.17243%206.50233%202.68638%206.00728%201.65903%206.74778C0.63183%207.48829%200.631836%209.05468%200.631836%2012.1869V16.599C0.631836%2018.3201%200.632053%2019.1808%201.09901%2019.8287C1.56597%2020.4765%202.38215%2020.7488%204.0149%2021.2931L8.66842%2022.8444C10.3702%2023.4117%2011.2213%2023.6952%2012.0773%2023.5784C12.9334%2023.4614%2013.6773%2022.9596%2015.1648%2021.9565L20.2278%2018.5417C21.8299%2017.4613%2022.6311%2016.9211%2023.0655%2016.1042C23.4999%2015.2873%2023.4998%2014.3212%2023.4998%2012.3891V8.66644H23.4981V6.90935C23.4981%205.18831%2023.4978%204.32757%2023.0309%203.67974C22.5639%203.03197%2021.7477%202.75952%2020.115%202.21531L16.7725%201.10115Z'%20fill='url(%23paint0_linear_3480_350)'/%3e%3cpath%20d='M16.7725%201.10115C13.8009%200.110601%2012.3149%20-0.384405%2011.2875%200.356016C10.2601%201.0965%2010.2603%202.66277%2010.2603%205.79522V8.53129L7.14408%207.49292C4.17243%206.50233%202.68638%206.00728%201.65903%206.74778C0.63183%207.48829%200.631836%209.05468%200.631836%2012.1869V16.599C0.631836%2018.3201%200.632053%2019.1808%201.09901%2019.8287C1.56597%2020.4765%202.38215%2020.7488%204.0149%2021.2931L8.66842%2022.8444C10.3702%2023.4117%2011.2213%2023.6952%2012.0773%2023.5784C12.9334%2023.4614%2013.6773%2022.9596%2015.1648%2021.9565L20.2278%2018.5417C21.8299%2017.4613%2022.6311%2016.9211%2023.0655%2016.1042C23.4999%2015.2873%2023.4998%2014.3212%2023.4998%2012.3891V8.66644H23.4981V6.90935C23.4981%205.18831%2023.4978%204.32757%2023.0309%203.67974C22.5639%203.03197%2021.7477%202.75952%2020.115%202.21531L16.7725%201.10115Z'%20fill='url(%23paint1_radial_3480_350)'/%3e%3cpath%20d='M16.7725%201.10115C13.8009%200.110601%2012.3149%20-0.384405%2011.2875%200.356016C10.2601%201.0965%2010.2603%202.66277%2010.2603%205.79522V8.53129L7.14408%207.49292C4.17243%206.50233%202.68638%206.00728%201.65903%206.74778C0.63183%207.48829%200.631836%209.05468%200.631836%2012.1869V16.599C0.631836%2018.3201%200.632053%2019.1808%201.09901%2019.8287C1.56597%2020.4765%202.38215%2020.7488%204.0149%2021.2931L8.66842%2022.8444C10.3702%2023.4117%2011.2213%2023.6952%2012.0773%2023.5784C12.9334%2023.4614%2013.6773%2022.9596%2015.1648%2021.9565L20.2278%2018.5417C21.8299%2017.4613%2022.6311%2016.9211%2023.0655%2016.1042C23.4999%2015.2873%2023.4998%2014.3212%2023.4998%2012.3891V8.66644H23.4981V6.90935C23.4981%205.18831%2023.4978%204.32757%2023.0309%203.67974C22.5639%203.03197%2021.7477%202.75952%2020.115%202.21531L16.7725%201.10115Z'%20fill='url(%23paint2_radial_3480_350)'/%3e%3cpath%20d='M13.8693%2013.301C13.8693%2011.58%2013.8693%2010.7194%2013.4024%2010.0715C12.9354%209.42367%2012.119%209.15151%2010.4863%208.60729L7.14408%207.49322C4.17237%206.50263%202.68655%206.00734%201.65919%206.74784C0.631836%207.48829%200.631836%209.05451%200.631836%2012.1869V16.5993C0.631836%2018.3204%200.631836%2019.181%201.09879%2019.8289C1.56575%2020.4767%202.38214%2020.7489%204.0149%2021.2931L7.3571%2022.4072C10.3288%2023.3978%2011.8146%2023.8931%2012.842%2023.1526C13.8693%2022.4121%2013.8693%2020.8459%2013.8693%2017.7134V13.301Z'%20fill='url(%23paint3_radial_3480_350)'/%3e%3cpath%20d='M13.8693%2013.301C13.8693%2011.58%2013.8693%2010.7194%2013.4024%2010.0715C12.9354%209.42367%2012.119%209.15151%2010.4863%208.60729L7.14408%207.49322C4.17237%206.50263%202.68655%206.00734%201.65919%206.74784C0.631836%207.48829%200.631836%209.05451%200.631836%2012.1869V16.5993C0.631836%2018.3204%200.631836%2019.181%201.09879%2019.8289C1.56575%2020.4767%202.38214%2020.7489%204.0149%2021.2931L7.3571%2022.4072C10.3288%2023.3978%2011.8146%2023.8931%2012.842%2023.1526C13.8693%2022.4121%2013.8693%2020.8459%2013.8693%2017.7134V13.301Z'%20fill='url(%23paint4_linear_3480_350)'/%3e%3cpath%20d='M23.4954%2016.3042V8.63525L13.9905%2015.0942L0.631836%2011.2597V20.1655L12.1352%2024L23.4954%2016.3042Z'%20fill='url(%23paint5_radial_3480_350)'/%3e%3cpath%20d='M10.2771%203.72664C8.38458%203.1334%207.28592%202.94642%206.4738%203.53156C5.6978%204.09088%205.50837%205.12154%205.46191%206.94224C5.96383%207.09953%206.52182%207.28517%207.14493%207.49283L10.2606%208.5312V5.79513C10.2606%205.01148%2010.2609%204.32586%2010.2771%203.72664Z'%20fill='url(%23paint6_linear_3480_350)'/%3e%3cpath%20d='M10.2771%203.72664C8.38458%203.1334%207.28592%202.94642%206.4738%203.53156C5.6978%204.09088%205.50837%205.12154%205.46191%206.94224C5.96383%207.09953%206.52182%207.28517%207.14493%207.49283L10.2606%208.5312V5.79513C10.2606%205.01148%2010.2609%204.32586%2010.2771%203.72664Z'%20fill='url(%23paint7_linear_3480_350)'%20fill-opacity='0.7'/%3e%3cpath%20d='M10.2762%203.72681C10.2601%204.32602%2010.2598%205.01171%2010.2598%205.7953V10.2079C10.2598%2011.9288%2010.26%2012.7892%2010.7269%2013.437C11.1939%2014.0848%2012.0101%2014.3571%2013.6428%2014.9014C13.7765%2014.9459%2014.0616%2015.041%2014.4318%2015.1642C16.3322%2015.7969%2017.2824%2016.1131%2017.9817%2015.6094C18.681%2015.1055%2018.6818%2014.105%2018.6834%2012.104C18.6841%2011.1556%2018.6842%2010.3582%2018.6842%2010.0851C18.6842%208.36426%2018.6838%207.50383%2018.217%206.85599C17.75%206.20815%2016.9337%205.93581%2015.3011%205.39159L11.958%204.27686C11.3354%204.06932%2010.7778%203.88404%2010.2762%203.72681Z'%20fill='url(%23paint8_linear_3480_350)'/%3e%3cpath%20d='M10.2762%203.72681C10.2601%204.32602%2010.2598%205.01171%2010.2598%205.7953V10.2079C10.2598%2011.9288%2010.26%2012.7892%2010.7269%2013.437C11.1939%2014.0848%2012.0101%2014.3571%2013.6428%2014.9014C13.7765%2014.9459%2014.0616%2015.041%2014.4318%2015.1642C16.3322%2015.7969%2017.2824%2016.1131%2017.9817%2015.6094C18.681%2015.1055%2018.6818%2014.105%2018.6834%2012.104C18.6841%2011.1556%2018.6842%2010.3582%2018.6842%2010.0851C18.6842%208.36426%2018.6838%207.50383%2018.217%206.85599C17.75%206.20815%2016.9337%205.93581%2015.3011%205.39159L11.958%204.27686C11.3354%204.06932%2010.7778%203.88404%2010.2762%203.72681Z'%20fill='url(%23paint9_radial_3480_350)'/%3e%3cpath%20d='M5.4612%206.94214C5.44616%207.53185%205.44531%208.20442%205.44531%208.97067V13.3833C5.44531%2015.1044%205.44555%2015.9651%205.91251%2016.6129C6.37946%2017.2606%207.19584%2017.5326%208.82837%2018.0767C8.96148%2018.1211%209.24436%2018.2154%209.61178%2018.3377C11.5158%2018.9715%2012.4677%2019.2883%2013.167%2018.7844C13.8663%2018.2806%2013.867%2017.2782%2013.8685%2015.2735C13.8691%2014.3433%2013.8691%2013.5652%2013.8691%2013.301C13.8691%2011.5799%2013.8689%2010.7192%2013.402%2010.0713C12.935%209.42355%2012.1188%209.15114%2010.4861%208.60692L7.14361%207.49279C6.52069%207.28513%205.96299%207.09943%205.4612%206.94214Z'%20fill='url(%23paint10_linear_3480_350)'/%3e%3cpath%20d='M10.2598%2010.208C10.2598%2011.9288%2010.2596%2012.7893%2010.7264%2013.4371C11.1933%2014.085%2012.0101%2014.3573%2013.6428%2014.9015L13.869%2014.9767V13.3014C13.869%2011.5803%2013.8688%2010.7196%2013.4019%2010.0717C12.9349%209.42388%2012.1187%209.15153%2010.486%208.60731L10.2598%208.53149V10.208Z'%20fill='url(%23paint11_linear_3480_350)'/%3e%3cdefs%3e%3clinearGradient%20id='paint0_linear_3480_350'%20x1='13.7174'%20y1='18.9577'%20x2='20.3845'%20y2='2.26449'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='%232764E7'/%3e%3cstop%20offset='0.307475'%20stop-color='%238B52F4'/%3e%3cstop%20offset='0.544627'%20stop-color='%23BB45EA'/%3e%3cstop%20offset='0.803866'%20stop-color='%23DB56C6'/%3e%3cstop%20offset='1'%20stop-color='%23F462AB'/%3e%3c/linearGradient%3e%3cradialGradient%20id='paint1_radial_3480_350'%20cx='0'%20cy='0'%20r='1'%20gradientTransform='matrix(6.22515%205.8102%203.77546%20-3.83006%2013.4633%2011.0459)'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20offset='0.549399'%20stop-color='%235B2AB5'/%3e%3cstop%20offset='1'%20stop-color='%23A931D8'%20stop-opacity='0'/%3e%3c/radialGradient%3e%3cradialGradient%20id='paint2_radial_3480_350'%20cx='0'%20cy='0'%20r='1'%20gradientTransform='matrix(11.9422%203.70864%201.90015%20-5.79338%2011.3036%208.32628)'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20offset='0.527929'%20stop-color='%239529C2'/%3e%3cstop%20offset='1'%20stop-color='%23DD3CE2'%20stop-opacity='0'/%3e%3c/radialGradient%3e%3cradialGradient%20id='paint3_radial_3480_350'%20cx='0'%20cy='0'%20r='1'%20gradientTransform='matrix(-11.5112%20-16.6189%20-16.507%2011.5892%2015.1912%2021.9439)'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='%232764E7'/%3e%3cstop%20offset='0.225228'%20stop-color='%230094F0'/%3e%3cstop%20offset='0.443437'%20stop-color='%2319B2CE'/%3e%3cstop%20offset='0.6999'%20stop-color='%2352D17C'/%3e%3cstop%20offset='1'%20stop-color='%23FFD638'/%3e%3c/radialGradient%3e%3clinearGradient%20id='paint4_linear_3480_350'%20x1='4.93267'%20y1='20.3082'%20x2='13.3411'%20y2='20.3082'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='%2316BBDA'%20stop-opacity='0'/%3e%3cstop%20offset='0.535279'%20stop-color='%230094F0'/%3e%3cstop%20offset='1'%20stop-color='%232764E7'/%3e%3c/linearGradient%3e%3cradialGradient%20id='paint5_radial_3480_350'%20cx='0'%20cy='0'%20r='1'%20gradientTransform='matrix(5.32952%202.73735%201.90044%20-3.03783%2011.1348%2017.1807)'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='%231B44B1'/%3e%3cstop%20offset='1'%20stop-color='%23367AF2'%20stop-opacity='0'/%3e%3c/radialGradient%3e%3clinearGradient%20id='paint6_linear_3480_350'%20x1='9.05348'%20y1='8.14265'%20x2='9.17888'%20y2='3.09185'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='%23FF9C70'/%3e%3cstop%20offset='1'%20stop-color='%23FFD394'/%3e%3c/linearGradient%3e%3clinearGradient%20id='paint7_linear_3480_350'%20x1='7.71598'%20y1='6.07061'%20x2='7.21281'%20y2='8.27943'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='%23FFB357'%20stop-opacity='0'/%3e%3cstop%20offset='1'%20stop-color='%23F24A9D'/%3e%3c/linearGradient%3e%3clinearGradient%20id='paint8_linear_3480_350'%20x1='14.9399'%20y1='4.98656'%20x2='15.0814'%20y2='16.435'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='%23FFB357'/%3e%3cstop%20offset='0.380259'%20stop-color='%23FB6F7B'/%3e%3cstop%20offset='0.659779'%20stop-color='%23F24A9D'/%3e%3cstop%20offset='1'%20stop-color='%23DD3CE2'/%3e%3c/linearGradient%3e%3cradialGradient%20id='paint9_radial_3480_350'%20cx='0'%20cy='0'%20r='1'%20gradientTransform='matrix(5.49926%201.36273%20-1.23951%206.04595%2010.7277%2013.7339)'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20offset='0.567938'%20stop-color='%23D7257D'/%3e%3cstop%20offset='1'%20stop-color='%23F462AB'%20stop-opacity='0'/%3e%3c/radialGradient%3e%3clinearGradient%20id='paint10_linear_3480_350'%20x1='12.4722'%20y1='19.5783'%20x2='4.4383'%20y2='6.96368'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='%230FAFFF'/%3e%3cstop%20offset='0.54828'%20stop-color='%232BDABE'/%3e%3cstop%20offset='0.765945'%20stop-color='%2388E06C'/%3e%3cstop%20offset='1'%20stop-color='%23FFD638'/%3e%3c/linearGradient%3e%3clinearGradient%20id='paint11_linear_3480_350'%20x1='9.8587'%20y1='10.9485'%20x2='13.3611'%20y2='12.0252'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='%2376EB95'/%3e%3cstop%20offset='1'%20stop-color='%233BD5FF'%20stop-opacity='0'/%3e%3c/linearGradient%3e%3c/defs%3e%3c/svg%3e"></span>
          <span class="studio-item" aria-label="Home"><svg width="24" height="24" aria-hidden="true" fill="currentColor" aria-hidden="true" data-fui-icon="" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M10.55 2.53c.84-.7 2.06-.7 2.9 0l6.75 5.7c.5.42.8 1.05.8 1.71v9.31c0 .97-.78 1.75-1.75 1.75h-3.5c-.97 0-1.75-.78-1.75-1.75v-5a.25.25 0 0 0-.25-.25h-3.5a.25.25 0 0 0-.25.25v5c0 .97-.78 1.75-1.75 1.75h-3.5C3.78 21 3 20.22 3 19.25v-9.3c0-.67.3-1.3.8-1.73zm1.93 1.15a.75.75 0 0 0-.96 0l-6.75 5.7a.8.8 0 0 0-.27.56v9.31c0 .14.11.25.25.25h3.5q.23-.01.25-.25v-5c0-.97.78-1.75 1.75-1.75h3.5c.97 0 1.75.78 1.75 1.75v5q.02.23.25.25h3.5q.23-.01.25-.25v-9.3q0-.36-.27-.58z" fill="currentColor"></path></svg></span>
          <span class="studio-item" aria-label="Chat"><svg width="24" height="24" aria-hidden="true" fill="currentColor" aria-hidden="true" data-fui-icon="" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M9.56 3a7.5 7.5 0 0 0-6.8 10.67l-.72 2.84c-.23.92.59 1.75 1.5 1.53l2.93-.7q1.44.64 3.1.66a7.5 7.5 0 0 0 0-15m-6 7.5a6 6 0 1 1 3.33 5.37l-.24-.12-.27.07-2.78.66.69-2.7.07-.28-.13-.25a6 6 0 0 1-.67-2.75m11 10.5a7.5 7.5 0 0 1-5.1-2 8 8 0 0 0 2.18-.26 6 6 0 0 0 5.6.13l.24-.12.26.07c.92.22 1.96.44 2.74.6-.18-.74-.41-1.75-.64-2.64l-.07-.28.13-.25a5.97 5.97 0 0 0-2.09-7.8 8 8 0 0 0-.8-2.04 7.5 7.5 0 0 1 4.35 10.26l.67 2.8c.2.9-.57 1.7-1.47 1.5-.72-.15-1.87-.39-2.91-.63q-1.43.64-3.09.66" fill="currentColor"></path></svg></span><hr>
          <span class="studio-item selected" aria-label="Agents"><svg width="24" height="24" aria-hidden="true" aria-hidden="true" fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="forced-color-adjust: auto;"><path d="M11.9757 4.26513C12.125 3.79599 12.3558 3.36973 12.6497 3H8.10571C7.45796 3 6.84987 3.27846 6.42782 3.75085H6.4401C6.33781 3.86536 6.24644 3.99125 6.16809 4.12733L2.27031 10.8972C1.87941 11.5761 1.86981 12.4095 2.24495 13.0972L5.85959 19.7241C5.87299 19.7487 5.88679 19.7729 5.90095 19.7969C6.11349 20.1568 6.41068 20.4501 6.75917 20.657L6.78329 20.6711C7.14944 20.8829 7.57063 21 8.00894 21C9.07512 21 10.0187 20.31 10.342 19.294L14.8345 5.17477C14.9623 4.77291 15.2588 4.37673 15.7573 4.5C16.2564 4.62343 16.3905 5.12911 16.2356 5.61941L11.7714 19.7488C11.6239 20.2124 11.3963 20.6339 11.1068 21H15.8956C16.6996 21 17.4425 20.571 17.8443 19.8746L18.5109 18.7196L18.4825 18.7536L18.4907 18.7311L21.7198 13.1227C22.1199 12.4277 22.1199 11.5723 21.7198 10.8773L17.8965 4.23675C17.6762 3.85417 17.3621 3.54498 16.9928 3.33144L16.9676 3.31707C16.6041 3.11261 16.1887 3 15.7573 3C14.6824 3 13.731 3.69564 13.4051 4.71996L8.9126 18.8392C8.83847 19.0722 8.68012 19.2609 8.47756 19.3761C8.33799 19.4555 8.17029 19.5105 7.97765 19.4646C7.49268 19.3491 7.35876 18.8585 7.50961 18.3834L11.6364 5.38498H11.6194L11.9757 4.26513Z" fill="currentColor"></path></svg></span>
          <span class="studio-item" aria-label="Workflows"><svg width="24" height="24" aria-hidden="true" aria-hidden="true" fill="none" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg" style="forced-color-adjust: auto;"><path d="M13.7432 2.62695C16.0884 2.62734 17.999 4.52841 17.999 6.87598C17.999 7.42674 17.8907 7.95184 17.6992 8.43457C17.892 8.919 17.999 9.447 17.999 10C17.999 10.5512 17.89 11.0765 17.6982 11.5596C17.8908 12.0438 17.998 12.5712 17.998 13.124C17.998 15.4719 16.0878 17.373 13.7422 17.373C12.6159 17.3729 11.5324 16.9258 10.7354 16.1289L10 15.3936L9.26465 16.1289C8.46763 16.9258 7.38412 17.3729 6.25781 17.373C3.91223 17.373 2.002 15.4718 2.00195 13.124C2.002 12.5722 2.10809 12.0452 2.2998 11.5615C2.10803 11.0781 2.00201 10.5516 2.00195 10C2.00201 9.44794 2.10827 8.92047 2.2998 8.43652C2.10824 7.95337 2.00201 7.42721 2.00195 6.87598C2.00202 4.52817 3.91224 2.62695 6.25781 2.62695C7.38406 2.62707 8.46764 3.07427 9.26465 3.87109L10 4.60645L10.7363 3.87109C11.5334 3.0743 12.6169 2.62701 13.7432 2.62695ZM13.7422 9.875C12.8802 9.87512 12.0513 10.2182 11.4424 10.8271L9.26465 13.0049C8.46764 13.8017 7.38408 14.2489 6.25781 14.249C4.96517 14.249 3.80577 13.6701 3.02441 12.7588C3.01087 12.8787 3.00197 13.0005 3.00195 13.124C3.002 14.9173 4.46226 16.373 6.25781 16.373C7.11966 16.3729 7.94867 16.0307 8.55762 15.4219L12.0703 11.9092C12.9977 10.9821 14.5015 10.9819 15.4287 11.9092L15.5088 11.9902C15.7037 12.1855 15.7039 12.5021 15.5088 12.6973C15.3136 12.8922 14.997 12.8921 14.8018 12.6973L14.7207 12.6162C14.184 12.0799 13.314 12.0798 12.7773 12.6162L10.707 14.6865L11.4424 15.4219C12.0513 16.0307 12.8803 16.3729 13.7422 16.373C15.5378 16.373 16.998 14.9174 16.998 13.124C16.9979 11.3308 15.5377 9.875 13.7422 9.875ZM13.7432 6.75098C12.8815 6.75098 12.0523 7.09364 11.4434 7.70215L9.26465 9.88086C8.46764 10.6777 7.38408 11.1249 6.25781 11.125C4.96517 11.125 3.80577 10.5461 3.02441 9.63477C3.0109 9.75459 3.00197 9.87657 3.00195 10C3.00219 11.7931 4.46237 13.249 6.25781 13.249C7.11962 13.2489 7.94868 12.9066 8.55762 12.2979L9.02148 11.833L9.95898 10.8965L10.7354 10.1191C11.5324 9.32232 12.6159 8.87512 13.7422 8.875C15.0344 8.875 16.1933 9.45341 16.9746 10.3643C16.9885 10.2446 16.999 10.1233 16.999 10C16.999 8.20707 15.5384 6.75143 13.7432 6.75098ZM13.7432 3.62695C12.8812 3.62701 12.0524 3.97018 11.4434 4.5791L8.79102 7.22852L7.92969 8.09082C7.00233 9.01788 5.49853 9.01806 4.57129 8.09082L4.49121 8.00977C4.29628 7.81448 4.29606 7.49789 4.49121 7.30273C4.68637 7.10772 5.003 7.10785 5.19824 7.30273L5.2793 7.38379C5.81605 7.92011 6.68596 7.92019 7.22266 7.38379L9.29199 5.31348L8.55762 4.5791C7.94865 3.97014 7.11976 3.62707 6.25781 3.62695C4.46227 3.62695 3.00202 5.08271 3.00195 6.87598C3.00219 8.66911 4.46237 10.125 6.25781 10.125C7.11962 10.1249 7.94868 9.7826 8.55762 9.17383L10.7363 6.99512C11.5334 6.19855 12.6171 5.75098 13.7432 5.75098C15.0348 5.75123 16.1933 6.32892 16.9746 7.23926C16.9884 7.11991 16.999 6.99896 16.999 6.87598C16.999 5.08295 15.5384 3.62734 13.7432 3.62695Z" fill="currentColor"></path></svg></span>
          <span class="studio-item" aria-label="Apps (Preview)"><svg width="24" height="24" aria-hidden="true" aria-hidden="true" fill="none" viewBox="6 6 24 24" xmlns="http://www.w3.org/2000/svg" style="forced-color-adjust: auto;"><path d="M20.5745 13.1282C21.7333 13.3214 22.642 14.2292 22.8353 15.3879L23.1614 17.3469L21.596 17.0862L21.3548 15.635C21.2669 15.1082 20.8542 14.6955 20.3275 14.6077L18.8773 14.3655L18.6165 12.801L20.5745 13.1282Z" fill="currentColor"></path><path d="M17.2132 8.04028H17.2689C17.3275 8.04272 17.3868 8.04891 17.4466 8.05884L24.9417 9.30786C25.8195 9.45426 26.5071 10.143 26.6536 11.0208L26.7279 11.469C26.7291 11.4761 26.7315 11.4833 26.7327 11.4905L27.9027 18.5149C27.9149 18.5882 27.9192 18.6612 27.9202 18.7327C27.9598 19.5048 27.6729 20.2641 27.1195 20.8176L20.7796 27.1575C20.1517 27.7853 19.259 28.071 18.3831 27.9251L11.4525 26.7708C10.2937 26.5775 9.386 25.6687 9.1927 24.51L8.03742 17.5793C7.89156 16.7035 8.17721 15.8108 8.805 15.1829L15.1448 8.84302C15.6943 8.29359 16.4469 8.00574 17.2132 8.04028ZM9.86555 16.2434C9.58026 16.5288 9.45062 16.9352 9.51691 17.3333L10.6722 24.2629C10.76 24.7897 11.1728 25.2024 11.6995 25.2903L18.6292 26.4456C19.0273 26.5119 19.4336 26.3822 19.7191 26.0969L21.8577 23.9573L15.3499 22.8733C14.1913 22.6799 13.2835 21.7712 13.0902 20.6126L12.0052 14.1038L9.86555 16.2434ZM14.0657 12.0422L15.4866 12.2795L15.7474 13.844L13.4173 13.4553L14.5696 20.3655C14.6575 20.8921 15.0704 21.3049 15.597 21.3928L22.5071 22.5452L22.1185 20.2141L23.6829 20.4749L23.9193 21.8958L25.7562 20.0579L18.7786 18.8958C17.9009 18.7493 17.2121 18.0616 17.0657 17.1838L15.9027 10.2053L14.0657 12.0422ZM18.5452 16.9368C18.5862 17.1824 18.7792 17.3751 19.0247 17.4163L26.4036 18.6458L25.2523 11.7376C25.1645 11.2107 24.7518 10.798 24.2249 10.7102L17.3157 9.55786L18.5452 16.9368Z" fill="currentColor"></path></svg></span>
          <span class="studio-nav-bottom" aria-label="Switch environment"><svg width="24" height="24" aria-hidden="true" fill="currentColor" aria-hidden="true" data-fui-icon="" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M20.5 10.5a8.5 8.5 0 1 0-17 0 8.5 8.5 0 0 0 17 0m-7.03 5.37c-.66 1.42-1.29 1.63-1.47 1.63s-.8-.21-1.47-1.63q-.46-.98-.75-2.37h4.44q-.28 1.39-.75 2.37M9.5 10.5q0-.78.07-1.5h4.86a16 16 0 0 1 0 3H9.57q-.07-.72-.07-1.5m5.07 6.51c.52-.93.93-2.13 1.17-3.51h2.59a7 7 0 0 1-3.76 3.51M15.94 12a18 18 0 0 0 0-3h2.9a7 7 0 0 1 0 3zM5.16 12a7 7 0 0 1 0-3h2.9a18 18 0 0 0 0 3zm3.1 1.5c.24 1.38.65 2.58 1.17 3.51a7 7 0 0 1-3.76-3.51zm5.96-6H9.78q.28-1.39.75-2.37C11.19 3.7 11.82 3.5 12 3.5s.8.21 1.47 1.63q.46.98.75 2.37m4.1 0h-2.58a11 11 0 0 0-1.17-3.51c1.65.65 3 1.91 3.76 3.51m-10.06 0H5.67a7 7 0 0 1 3.76-3.51c-.52.93-.93 2.13-1.17 3.51M4 16h.25q.6.83 1.33 1.5H4.57l-.83 3h16.52l-.83-3h-1q.73-.67 1.32-1.5H20c.34 0 .63.22.72.55l1.25 4.5a.75.75 0 0 1-.72.95H2.75a.75.75 0 0 1-.72-.95l1.25-4.5A.75.75 0 0 1 4 16" fill="currentColor"></path></svg></span>
          <span class="studio-account" aria-label="Practice account">AB</span>
          <span aria-label="More options"><svg width="24" height="24" aria-hidden="true" fill="currentColor" aria-hidden="true" data-fui-icon="" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M7.75 12a1.75 1.75 0 1 1-3.5 0 1.75 1.75 0 0 1 3.5 0m6 0a1.75 1.75 0 1 1-3.5 0 1.75 1.75 0 0 1 3.5 0M18 13.75a1.75 1.75 0 1 0 0-3.5 1.75 1.75 0 0 0 0 3.5" fill="currentColor"></path></svg></span>
        </nav>
        <div class="studio-agent-page">
          <div class="studio-topbar studio-agent-header">
            <div class="studio-identity"><strong id="studio-agent"></strong><span class="studio-draft">${icon('M7 3h7l4 4v14H7zM14 3v5h5M10 12h5m-5 4h5')}Draft</span></div>
            <div class="studio-tabs" role="group" aria-label="Agent workspace"><span data-studio-tab="build" aria-pressed="false">Build</span><span data-studio-tab="preview" aria-pressed="true">Preview</span><span data-studio-tab="evaluate" aria-pressed="false">Evaluate</span><span data-studio-tab="monitor" aria-pressed="false">Monitor</span></div>
            <div class="studio-actions" aria-label="Sample workspace actions">
              <span aria-label="More">${more}</span><span aria-label="Share">${person}</span>
              <span aria-label="Export">${icon('M4 14v7h16v-7M12 17V3m-5 5 5-5 5 5')}</span>
              <span aria-label="Save">${icon('M4 3h13l4 4v14H3V3zM7 3v6h10V3M7 21v-8h10v8')}</span>
              <span class="studio-review"><span class="studio-shield">${icon('M12 2 3 6v6c0 5 9 10 9 10s9-5 9-10V6z')}<small>2</small></span>Review</span>
              <span class="studio-publish">Publish</span>
            </div>
          </div>
          <div class="studio-preview">
            <section class="studio-test" aria-label="Preview">
              <div class="studio-test-header"><strong class="studio-header-name"></strong>
                <div class="studio-chat-actions"><span>0 credits ${icon('M12 3a9 9 0 1 0 0 18 9 9 0 1 0 0-18M12 7v1m0 3v6')}</span>
                  <button type="button" id="studio-new-chat">${icon('M4 4h16v16H4zM12 8v8M8 12h8')}New chat</button>
                  <span>${icon('M3 12a9 9 0 1 0 9-9M3 3v9h9M12 7v5l4 2')}History</span>
                  <span>${icon('m7 4 14 8-14 8z')}</span><span>Debug mode</span><span role="switch" aria-label="Debug mode" aria-checked="true" class="studio-toggle"></span>
                </div>
              </div>
              <div class="studio-thread" role="log" tabindex="0" aria-label="Sample conversation">
                <div class="studio-greeting"><div class="studio-speaker">${person}<h2></h2></div>
                  <p class="studio-description"></p>
                  <div class="studio-feedback" aria-hidden="true">${icon('M8 8h13v13H8zM16 8V3H3v13h5')}${icon('M8 10h-5v11h5zM8 20h11l3-10h-8l1-7h-3l-4 7z')}${icon('M8 14H3V3h5zM8 4h11l3 10h-8l1 7h-3l-4-7z')}</div>
                </div>
              </div>
              <div class="studio-scroll-status"><p class="studio-scroll-hint" hidden>Scroll for the rest of the sample answer.</p></div>
              <div class="studio-prompts" aria-label="Suggested prompts"></div>
              <form><span class="studio-plus" aria-hidden="true">${plus}</span><textarea id="studio-input" aria-label="Message" rows="2"></textarea><button id="studio-send" type="submit" aria-label="Send">${icon('m5 12 7-7 7 7M12 5v15')}</button></form>
              <p class="studio-ai-disclaimer">AI-generated content may be incorrect. <span>Learn more</span></p>
            </section>
          </div>
          <div class="studio-footer">Practice view of Copilot Studio. Your screen may differ.</div>
        </div>
      `;
    edge.view.replaceChildren(studio);
    const thread = $('.studio-thread', studio);
    const scrollHint = $('.studio-scroll-hint', studio);
    const updateScrollHint = () => {
      const more = !!$('#studio-answer', studio) && thread.scrollHeight - thread.clientHeight - thread.scrollTop > 1;
      scrollHint.hidden = !more;
      thread.dataset.more = String(more);
    };
    thread.addEventListener('scroll', updateScrollHint);
    thread.addEventListener('keydown', event => {
      if (event.key !== 'Home' && event.key !== 'End') return;
      event.preventDefault();
      thread.scrollTop = event.key === 'Home' ? 0 : thread.scrollHeight;
      updateScrollHint();
    });
    studioObserver = new ResizeObserver(updateScrollHint);
    studioObserver.observe(thread);
    $('#studio-agent').textContent = options.story.name;
    $('.studio-header-name', studio).textContent = options.story.name;
    $('.studio-greeting h2', studio).textContent = options.story.name;
    $('.studio-description', studio).textContent = options.story.description;
    const greeting = $('.studio-greeting', studio);
    const prompts = $('.studio-prompts', studio);
    const samples = [{prompt:options.story.question, assistant_response:options.story.answer},
      ...(options.story.samples || []).filter(sample => sample.prompt !== options.story.question)].slice(0, 6);
    for (const sample of samples) {
      const button = document.createElement('button');
      button.type = 'button';
      button.innerHTML = chat + '<span></span>';
      $('span', button).textContent = sample.prompt;
      button.title = sample.prompt;
      button.onclick = () => {
        $('#studio-input').value = sample.prompt;
        $('form', studio).requestSubmit();
      };
      prompts.append(button);
    }
    $('#studio-input').placeholder = `Message ${options.story.name}`;
    $('#studio-input').setAttribute('aria-label', `Message ${options.story.name}`);
    $('#studio-new-chat').onclick = () => {
      thread.replaceChildren(greeting);
      prompts.hidden = false;
      $('#studio-input').value = options.story.question;
      $('#studio-input').focus({preventScroll:true});
      updateScrollHint();
    };
    $('#studio-input').value = options.story.question;
    $('#studio-input').onkeydown = event => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        $('form', studio).requestSubmit();
      }
    };
    $('form', studio).onsubmit = e => {
      e.preventDefault();
      const sample = samples.find(sample => sample.prompt === $('#studio-input').value.trim());
      if (!sample) {
        toast('Try the first sample question', 'Use the question shown below this practice computer.');
        return;
      }
      const question = document.createElement('p');
      question.id = 'studio-question';
      question.className = 'sample-question';
      question.textContent = sample.prompt;
      const answer = document.createElement('div');
      answer.id = 'studio-answer';
      if (sample.assistant_response) {
        answer.append(renderStudioAnswer(sample.assistant_response.replace(/[\p{Extended_Pictographic}\p{Emoji_Presentation}]\ufe0f?/gu, '') + '\n\nSample data.'));
      } else {
        const demo = document.createElement('a');
        demo.textContent = "Open the demo to see this agent's sample answer";
        demo.href = options.story.demo;
        answer.append(demo, document.createTextNode('\n\nSample data.'));
      }
      const speaker = document.createElement('div');
      speaker.className = 'studio-speaker';
      speaker.innerHTML = person + '<strong></strong>';
      $('strong', speaker).textContent = options.story.name;
      thread.replaceChildren(question, speaker, answer);
      prompts.hidden = true;
      $('#studio-input').value = '';
      $('#studio-input').rows = 1;
      thread.scrollTop = 0;
      updateScrollHint();
      emit('studio-done');
    };
    $('#studio-input').focus({preventScroll:true});
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
      const say = $('#hint-say');
      if (!t) { hint.style.display = 'none'; if (say && !say.hidden) say.hidden = true; return; }
      const thread = t.closest('.thread');
      if (thread) {
        const bounds = thread.getBoundingClientRect(), control = t.getBoundingClientRect();
        if (control.bottom > bounds.bottom) thread.scrollTop += control.bottom - bounds.bottom + 10;
        if (control.top < bounds.top) thread.scrollTop -= bounds.top - control.top;
      }
      const r = t.getBoundingClientRect(), p = pc.getBoundingClientRect();
      Object.assign(hint.style, {display:'block', left:(r.left-p.left-3)+'px', top:(r.top-p.top-3)+'px', width:(r.width+6)+'px', height:(r.height+6)+'px'});
      if (say) {
        const text = HINT_SAY[selector] || (s.say || '').replace(/<[^>]+>/g, '').split('. ')[0].replace(/\.$/, '');
        if (say.textContent !== text) say.textContent = text;
        if (say.hidden !== !text) say.hidden = !text;
        if (text) {
          const w = say.offsetWidth, h = say.offsetHeight;
          const left = Math.round(Math.max(8, Math.min(r.left - p.left + r.width / 2 - w / 2, p.width - w - 8)));
          const above = Math.round(r.top - p.top - h - 14);
          const below = above < 8 || selector === '#cowork-send';
          const place = [String(below), left + 'px', (below ? Math.round(r.bottom - p.top + 14) : above) + 'px',
            Math.round(r.left - p.left + r.width / 2 - left) + 'px'].join('|');
          if (say.dataset.place !== place) {
            const [flag, x, y, arrow] = place.split('|');
            say.dataset.place = place; say.dataset.below = flag;
            say.style.left = x; say.style.top = y; say.style.setProperty('--arrow', arrow);
          }
        }
      }
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
  const HINT_SAY = {
    '#agent-chat':'Click here to open Copilot chat',
    '.vsc textarea':'Paste your setup line here. Use Copy below, then paste.',
    '.vsc .send':'Now press Send',
    '#ms-signin':'Sign in here (pretend sign-in)',
    '#agent-yes':'Choose Yes to go ahead',
    '#agent-open':'Open Copilot Studio',
    '#studio-send':'Press Send to ask the sample question',
    '#cowork-download':'Download the plugin file',
    '#cowork-customize':'Open Customize',
    '#cowork-manage':'Choose Manage all',
    '#cowork-add':'Choose Add',
    '#cowork-upload':'Choose Upload',
    '#cowork-file':'Pick the file you downloaded',
    '#cowork-publish':'Publish it, just for you',
    '#cowork-send':'Your plugin is ready. Press Send to try it',
    '#stage-keep-going':'Keep going',
  };
  function target() {
    if (finish) return '#stage-keep-going';
    if (cowork) {
      if (step === 0) return $('#cowork-download:not(:disabled)') ? '#cowork-download' : null;
      if (step === 1) return ['#cowork-file', '#cowork-upload', '#cowork-add', '#cowork-manage', '#cowork-customize'].find(id => $(id)) || null;
      if (step === 2) return $('#cowork-publish') ? '#cowork-publish' : null;
      if (step === 3) return $('#cowork-send') ? '#cowork-send' : null;
      return null;
    }
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
      return ssearch.value && $('.res.best') ? '.res.best' : '#ssearch';
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
      const library = $('#bs-library');
      if (!library) return null;
      if (library.hidden) return '#bs-book';
      return $('#bs-meeting').hidden ? '#bs-library-search' : '#bs-add-meeting';
    }
    if (step === 16) return '.bs .starter-btn:nth-child(3)';
    return null;
  }
  function clearInputPause() {
    clearTimeout(inputPauseTimer);
    inputPauseTimer = null;
    inputPaused = false;
    const notice = $('#watch-pause-notice');
    if (notice) notice.hidden = true;
  }
  function pauseWatch(fromInput) {
    if (disposed || mode !== 'watch') return;
    clearInputPause();
    playing = false; playbackVersion++;
    activeNarration?.pause();
    inputPaused = fromInput;
    if (fromInput) {
      const notice = $('#watch-pause-notice');
      notice.hidden = false;
      inputPauseTimer = setTimeout(resumeWatch, 8000);
    }
    renderControls();
  }
  function resumeWatch() {
    if (disposed || mode !== 'watch') return;
    const focusedNotice = document.activeElement?.closest('#watch-pause-notice');
    clearInputPause();
    playing = step < STEPS.length; playbackVersion++;
    if (!document.hidden) activeNarration?.resume();
    renderControls();
    if (focusedNotice) $('#stage-pause').focus({preventScroll:true});
  }
  function visibilityChanged() {
    if (document.hidden) {
      playbackVersion++;
      activeNarration?.pause();
    } else if (mode === 'try' || playing) activeNarration?.resume();
  }
  function setMode(next) {
    clearInputPause();
    if (sessionPractice && next === 'watch' && mode !== 'watch') restore(canonicalSnapshots[step]);
    playbackVersion++;
    mode = next;
    playing = next === 'watch' && step < STEPS.length;
    renderControls();
    showHint();
    if (!document.hidden) activeNarration?.resume();
    if (activeNarration?.promise && screenKey) return;
    speakScreen(true);
  }
  function renderControls() {
    if (!stage) return;
    host.dataset.mode = mode;
    $('#watch-mode').setAttribute('aria-pressed', String(mode === 'watch'));
    $('#try-mode').setAttribute('aria-pressed', String(mode === 'try'));
    $('#stage-pause').textContent = playing ? 'Pause' : 'Resume';
    $('#stage-pause').hidden = mode === 'try' || step >= STEPS.length;
    $('#stage-again').hidden = mode === 'try';
    pointer.hidden = still || mode !== 'watch';
    if (!playing && !still) {
      const position = getComputedStyle(pointer);
      Object.assign(pointer.style, {left:position.left, top:position.top});
    }
  }
  async function act(animate) {
    if (finish) { $('#stage-keep-going').click(); return; }
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
    if (disposed || document.hidden || step !== current || version !== playbackVersion || !playing || mode !== 'watch') return;
    if (selector === '#ssearch') {
      t.value = 'PowerShell';
      t.dispatchEvent(new Event('input', {bubbles:true}));
    } else if (selector === '.ps .in') {
      if (t.textContent.trim() !== PS_LINE) { state.clip = PS_LINE; t.textContent = PS_LINE; }
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
    else {
      if (selector === '.vsc .send') vs.ta.value = STEPS[step].copy;
      t.click();
    }
    showHint();
  }
  async function watch() {
    while (!disposed) {
      const version = playbackVersion;
      await sleep(1000);
      if (!document.hidden && mode === 'watch' && playing && version === playbackVersion) {
        const pending = narrationPending;
        await pending;
        if (pending !== narrationPending) continue;
        if (version === playbackVersion && playing && mode === 'watch') await act(true);
      }
    }
  }
  function dispose() {
    disposed = true;
    clearInputPause();
    narrationVersion++;
    stopNarration();
    clips.forEach(pending => pending.then(src => { if (src) URL.revokeObjectURL(src.url); }));
    clearInterval(clock);
    layoutObserver?.disconnect();
    studioObserver?.disconnect();
    consentResizeObserver?.disconnect();
    consentMutationObserver?.disconnect();
    window.removeEventListener('resize', reserveConsentSpace);
    if (stage) compactSteps.removeEventListener('change', adaptSteps);
    document.removeEventListener('visibilitychange', visibilityChanged);
    window.removeEventListener('beforeunload', rememberStep);
    window.removeEventListener('pagehide', rememberStep);
  }
  function restart(initialStep, nextMode = mode) {
    clearInputPause();
    resumedStep = null;
    $('#resume-notice')?.remove();
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
    render();
    for (const window of data.windows) {
      if (window.scroll.length) continue;
      wins[window.key].querySelectorAll('.log, .thread').forEach(el => { el.scrollTop = el.scrollHeight; });
    }
    if (!data.focus) focusStepInput();
    rememberStep();
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
    const exchange = (q, text, thought) => { chat().log += sampleExchange(q, text, thought); };
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
      () => exchange('What do you remember?', recalledMemory(desktop.state.memory), 'ContextMemory'),
      () => { chat().panel = true; },
      () => {
        exportFile(desktop.fileSystem);
        exchange('Export hacker_news_agent.py', 'Exported hacker_news_agent.py to the pretend Downloads window. No real file was downloaded.');
      },
      () => {
        findFile('hacker-news', desktop.fileSystem).loaded = false; chat().panel = false;
        exchange('Confirm delete hacker_news_agent.py', 'Removed hacker_news_agent.py. The chat is still running.');
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
        exchange('Restore hacker_news_agent.py', 'Hot-loaded hacker_news_agent.py. Instantly.');
      },
      () => exchange('get my latest hacker news', 'Hacker News is available again. Sample headline: A team shares a new open-source tool. This is not live news.', 'HackerNews'),
      () => {
        addAgent('meeting-prep', 'meeting_prep_agent.py', desktop.fileSystem);
        exchange('Add Meeting Prep', 'Installed Meeting Prep. Ask me to prep you for your next customer meeting.');
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
      const resume = (!direct || reload && saved?.step === step) &&
        options.initialStep == null && saved?.version === 2 &&
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
  } else {
    narrationStarted = true;
    if (express && !cowork && step > 0) {
      const initial = step;
      step = 0; enterStep(); step = initial;
      state.completed = Array.from({length:initial}, (_, i) => i + 1);
      if (initial >= 2) {
        agentMessage(options.story.line, 'you').id = 'agent-pasted-line';
        if (initial === 2) requestAgentSignin();
        else { agentMessage('Yes', 'you'); agentSetupReady(); openStudio(); }
      }
    }
    enterStep(); render();
  }
  setTimeout(showHint, 900);
  if (stage) {
    consentResizeObserver = new ResizeObserver(reserveConsentSpace);
    consentResizeObserver.observe($('#coach'));
    consentResizeObserver.observe(pc);
    consentMutationObserver = new MutationObserver(reserveConsentSpace);
    consentMutationObserver.observe(document.body, {childList:true});
    window.addEventListener('resize', reserveConsentSpace);
    reserveConsentSpace();
    pc.addEventListener('input', showHint);
    pc.addEventListener('click', () => setTimeout(showHint, 0));
    watch();
  }

    return window.practicePC;
  }
};
