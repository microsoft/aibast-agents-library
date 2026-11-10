window.AibastDesktop = {
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
    controls.innerHTML = '<span class="mode-switch" role="group" aria-label="Practice mode"><button id="watch-mode" aria-pressed="true">Watch</button><button id="try-mode" aria-pressed="false">Step by step</button></span><button id="stage-pause">Pause</button><button id="stage-again">Play again</button>';
    $('#c-acts').before(controls);
    pointer = document.createElement('div');
    pointer.id = 'watch-pointer';
    pointer.setAttribute('aria-hidden', 'true');
    pointer.innerHTML = '<svg width="26" height="32" viewBox="0 0 26 32"><path d="M2 2v24l6-6 5 10 5-3-5-9h9z" fill="#fff" stroke="#18181b" stroke-width="2"/></svg>';
    pc.appendChild(pointer);
    $('#watch-mode').onclick = () => setMode('watch');
    $('#try-mode').onclick = () => setMode('try');
    $('#stage-pause').onclick = () => { playing = !playing; playbackVersion++; renderControls(); };
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
    memory: '', news: true, exported: false, meeting: false, created: false, completed: [] };

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
    if (on) { ssearch.value = ''; search(''); setTimeout(() => ssearch.focus({preventScroll:stage}), 0); emit('start-open'); }
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
  function closeWin(key) { const el = wins[key]; if (!el) return; el._tb.remove(); el.remove(); delete wins[key]; emit('close', key); }
  function launch(key) {
    openStart(false);
    if (wins[key]) { wins[key].classList.remove('min'); focus(wins[key]); return; }
    if (key === 'ps') openPowerShell();
    else if (key === 'code') openVSCode();
    else if (key === 'edge') openEdge(LIB);
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
    ps.out.appendChild(p); ps.in = $('.in', p); ps.in.focus({preventScroll:stage});
    ps.in.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); psRun(ps.in.textContent); } });
    ps.in.addEventListener('paste', (e) => { e.preventDefault(); const t = (e.clipboardData || window.clipboardData).getData('text'); ps.in.textContent += t.replace(/\r?\n/g, ' ').trim(); emit('ps-paste'); });
    ps.out.parentElement.scrollTop = 1e9;
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
    if (norm === PS_LINE.toLowerCase() || /^irm .*install\.ps1 \| iex$/.test(norm)) { await psInstall(); }
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
  function openEdge(url) {
    if (!edge) {
      const el = makeWin('edge', 'Microsoft Edge', 'edge', 980, 600, `<div class="bar"><div class="nav"><span>&#8592;</span><span>&#8594;</span><span>&#8635;</span></div><div class="url"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#666" stroke-width="2"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg><input id="eurl" spellcheck="false"></div></div><div class="view" id="eview"></div>`);
      $('.tbar .t', el).outerHTML = '<div class="tabs t"><div class="tab"><div class="fav" id="efav"></div><span id="etitle">New tab</span></div><div class="tab plus">+</div></div>';
      edge = { el, url: $('#eurl', el), view: $('#eview', el), title: $('#etitle', el) };
      edge.url.addEventListener('keydown', (e) => { if (e.key === 'Enter') edgeGo(edge.url.value); });
      edge.url.addEventListener('focus', () => edge.url.select());
    } else { edge.el.classList.remove('min'); focus(edge.el); }
    edgeGo(url);
  }
  function edgeGo(url) {
    url = url.trim(); if (!/^https?:\/\//.test(url)) url = 'https://' + url;
    const u = url.replace(/^https?:\/\//, '').replace(/\/$/, '');
    edge.url.value = url; emit('edge', u);
    if (u.startsWith('microsoft.github.io/aibast-agents-library')) {
      edge.title.textContent = 'AI BAST Agent Library';
      edge.view.innerHTML = `<div class="mock library-scene">
        <header><strong>AI BAST Agent Library<small>Industry Solutions</small></strong>
          <nav aria-label="Pretend library navigation"><button>Agent Library</button><button>Workshops</button><button>Academy</button><button>Get an agent running</button></nav>
        </header>
        <div class="library-hero"><section>
          <h2>AI agent solutions you can show a customer.</h2>
          <p>Watch one work on a sample question. Then get it running in your own Copilot Studio with sample data.</p>
          <button class="library-watch">Watch a demo</button>
          <div class="library-links"><button>Get an agent running</button><button>Request one-pagers and videos</button><button>Office hours</button><button>AIdeate sessions</button></div>
        </section><figure><div class="library-preview"><strong>Account Intelligence Agent</strong>
          <p class="library-question">Prepare a synthetic Acme Corporation account overview and show the evidence that deserves seller attention.</p>
          <p class="library-answer">Sample data preview. Review account evidence and the next conversation to prepare.</p>
        </div><figcaption>Now showing: Account Intelligence Agent</figcaption></figure></div>
      </div>`;
      $('.library-watch', edge.view).onclick = () => {
        $('.library-answer', edge.view).textContent = 'Sample data: the account overview brings together stakeholder signals, opportunities, and evidence to review before your customer conversation.';
      };
      edge.view.querySelectorAll('.library-scene nav button, .library-links button').forEach(button => {
        button.onclick = () => toast('Practice library', 'This is a preview. Continue with the step bar below the computer; open the real Agent Library from the page navigation.');
      });
    } else if (u.startsWith('localhost:7071') || u.startsWith('127.0.0.1:7071')) {
      edge.title.textContent = 'RAPP Brainstem';
      if (!state.brainstemRunning) { edge.view.innerHTML = `<div class="mock center"><div><h2>Hmmm… can't reach this page</h2><p>localhost refused to connect.</p><p style="font-size:12px;color:#777">Your Brainstem is not running yet. Run the one line in PowerShell first.</p></div></div>`; return; }
      edge.view.innerHTML = brainstemPage(); wireBrainstem(edge.view);
    } else if (u.startsWith('github.com/login/device')) {
      edge.title.textContent = 'Device Activation'; edge.view.innerHTML = `<div class="mock"><div class="gh"><div class="card" id="ghcard"><h2>Device Activation</h2><p style="text-align:center;color:#57606a;margin:0 0 6px">Enter the code displayed in PowerShell</p><label for="ghcode">Device code</label><input id="ghcode" maxlength="9" placeholder="XXXX-XXXX" autocomplete="off"><div class="warn" id="ghwarn">That code does not match. Look at the PowerShell window: the code is on the line that says Your code.</div><button id="ghgo">Continue</button></div></div></div>`;
      $('#ghgo', edge.view).addEventListener('click', () => {
        const v = $('#ghcode', edge.view).value.trim().toUpperCase();
        if (v !== state.code) { $('#ghwarn', edge.view).style.display = 'block'; emit('device-wrong'); return; }
        $('#ghcard', edge.view).innerHTML = `<h2>Authorize RAPP Brainstem</h2><p style="text-align:center;color:#57606a">RAPP Brainstem by <b>You</b> wants to use GitHub Copilot on your behalf.</p><p style="font-size:12px;color:#57606a;border:1px solid #d0d7de;border-radius:6px;padding:8px">This is the practice computer. No real GitHub account is involved.</p><button id="ghauth">Authorize</button>`;
        $('#ghauth', edge.view).addEventListener('click', () => { $('#ghcard', edge.view).innerHTML = '<h2>Congratulations, you\'re all set!</h2><p style="text-align:center;color:#57606a">Your device is now connected. You can close this tab and go back to PowerShell.</p>'; emit('device-ok'); if (state.onAuth) { state.onAuth(); state.onAuth = null; } });
      });
      setTimeout(() => { const i = $('#ghcode', edge.view); if (i) i.focus({preventScroll:stage}); }, 50);
    } else {
      edge.title.textContent = u; edge.view.innerHTML = `<div class="mock center"><div><h2>Hmmm… can't reach this page</h2><p>The practice computer only reaches the AIBAST library, GitHub sign-in and your Brainstem.</p></div></div>`;
    }
  }
  function brainstemPage() {
    return `<div class="bs" id="bs-drop" aria-label="Pretend Brainstem chat: sample replies">
      <div class="hd"><strong>RAPP Brainstem</strong><select aria-label="Pretend model"><option>Auto</option></select>
        <button id="bs-book" title="Agent library" aria-label="Agent library"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor"><path d="M3 4h7l2 2 2-2h7v16h-7l-2 2-2-2H3zM12 6v16"/></svg></button>
        <button id="bs-agents" title="Installed agents" aria-label="Installed agents">&#8853;</button>
        <button class="bs-preview" title="Voice" aria-label="Voice"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor"><rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10v2a7 7 0 0 0 14 0v-2M12 19v3M8 22h8"/></svg></button>
        <button class="bs-preview" title="VS Code" aria-label="VS Code">&lt;/&gt;</button></div>
      <div class="sample-label">Pretend chat · Sample replies only · Nothing is saved on your computer</div>
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
      panel.innerHTML = `<strong>Installed agents (pretend)</strong><p>context_memory_agent.py<br>manage_memory_agent.py<br>rar_rapp_learn_new_skill_agent.py</p>${state.news ? '<div>hacker_news_agent.py <button id="bs-export-agent">Export</button><button id="bs-delete-agent">Delete</button></div>' : '<p>hacker_news_agent.py is not loaded.</p>'}${state.meeting ? '<p>meeting_prep_agent.py</p>' : ''}${state.created ? '<p>quote_of_the_day_agent.py</p>' : ''}`;
      if (!state.news) return;
      $('#bs-export-agent', root).onclick = () => {
        state.exported = true; reply('Exported hacker_news_agent.py to the pretend Downloads window. No real file was downloaded.'); emit('exported');
      };
      $('#bs-delete-agent', root).onclick = () => {
        panel.insertAdjacentHTML('beforeend', '<div id="bs-delete-question">Remove hacker_news_agent.py? <button id="bs-confirm-delete">Confirm delete</button><button id="bs-cancel-delete">Cancel</button></div>');
        $('#bs-cancel-delete', root).onclick = () => renderAgents();
        $('#bs-confirm-delete', root).onclick = () => {
          if (!state.exported) { toast('Back up first', 'Export the pretend agent before deleting it.'); return; }
          state.news = false; renderAgents(); reply('Removed hacker_news_agent.py. The chat is still running.'); emit('deleted');
        };
        showHint();
      };
    }
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
      if (e.dataTransfer.getData('text/plain') === 'pretend:hacker_news_agent.py') restoreAgent();
      else toast('Use the pretend file', 'Drag hacker_news_agent.py from the pretend Downloads window. No real files are imported here.');
    };
    root.querySelectorAll('.bs-preview').forEach(button => {
      button.onclick = () => toast('Pretend control', 'This control is shown to match the real chat. Follow the interview hint below.');
    });
  }
  function restoreAgent() {
    if (!state.exported) { toast('No backup yet', 'Export the pretend agent first, or skip this step.'); return; }
    state.news = true;
    closeWin('downloads');
    $('.bs .log').insertAdjacentHTML('beforeend', '<div class="m"><strong>Sample reply</strong><br>Hot-loaded hacker_news_agent.py. Instantly.</div>');
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
      <div class="sbar"><span>&#9099; main</span><span>&#9888; 0</span><span style="margin-left:auto">Ln 1, Col 1</span><span>UTF-8</span><span>Copilot</span></div>`;
    const el = makeWin('code', 'Visual Studio Code', 'vsc dark', 1040, 620, body, APPS.code.ico.replace('class="ico"', 'class="ico" style="width:16px;height:16px;border-radius:3px;font-size:9px;"'));
    $('.body', el).style.gridTemplateRows = '1fr 22px';
    $('.tbar .t', el).insertAdjacentHTML('afterend', '<span class="cmd"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg> Search</span>');
    vs = { el, thread: $('.thread', el), ta: $('textarea', el) };
    const send = () => { const t = vs.ta.value.trim(); if (!t) return; vs.ta.value = ''; vsRun(t); };
    vs.ta.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } });
    vs.ta.addEventListener('paste', () => setTimeout(() => emit('vs-paste'), 0));
    $('.send', el).addEventListener('click', send);
    setTimeout(() => vs.ta.focus({preventScroll:stage}), 50);
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
    { id: 'find', say: 'Type <b>PowerShell</b>. When <b>Windows PowerShell</b> shows up as the best match, press Enter.', hint: '#ssearch', done: (e, d) => e === 'launch' && d === 'ps' },
    { id: 'paste', say: 'Copy the one line, then <b>right-click</b> inside the blue PowerShell window to paste it. Press Enter.', copy: PS_LINE, hint: '.ps .body', done: (e) => e === 'ps-run' },
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
    {id:'agent-test', say:'Open <b>Copilot Studio</b> in Edge and send the first sample question in your agent\'s test chat. The answer here is a placeholder labelled <b>Sample data</b>.', hint:'#agent-open', done:e => e === 'studio-done'}
  ] : [...INSTALL_STEPS, ...INTERVIEW_STEPS];
  let step = options.initialStep || 0;
  function emit(e, d = '') {
    const s = STEPS[step]; if (s && s.done(e, d)) { advance(); return; }
    if (e === 'ps-error' && step === 2) toast('Not quite', 'PowerShell did not recognise that. Copy the whole line from the coach box and paste it exactly.');
    if (e === 'device-wrong') toast('Not quite', 'Type the code exactly as PowerShell shows it, dashes included.');
    if (e === 'launch' && d !== 'ps' && d !== 'code' && d !== 'edge' && step < 2) toast('Different app', 'That one is not part of the setup. Press Start again and type PowerShell.');
  }
  function advance() { state.completed.push(step + 1); step++; enterStep(); render(); if (step < STEPS.length) setTimeout(showHint, 600); }
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
      return;
    }
    const s = STEPS[step];
    $('#c-n').textContent = `Step ${step + 1} of ${STEPS.length}`;
    $('#c-say').innerHTML = s.say;
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
      help.href = HELP;
      acts.append(reset, help);
    }
    if (s.skippable) { const k = document.createElement('button'); k.textContent = 'Skip this step'; k.addEventListener('click', advance); acts.appendChild(k); }
    if (stage) { renderControls(); showHint(); }
  }
  function enterStep() {
    if (!express) {
      if (step >= 11 && $('#bs-agent-panel')) $('#bs-agent-panel').hidden = true;
      if (step === 12 && state.exported && !wins.downloads) {
        const downloads = makeWin('downloads', 'Pretend Downloads', 'plain downloads', 330, 160,
          '<p>Sample exported file</p><div id="download-agent" draggable="true" tabindex="0">hacker_news_agent.py</div>');
        $('#download-agent', downloads).ondragstart = e => {
          e.dataTransfer.setData('text/plain', 'pretend:hacker_news_agent.py');
        };
        Object.assign(downloads.style, {left:'8px', top:'8px'});
      }
      if (step === 13 && wins.downloads) closeWin('downloads');
      return;
    }
    if (step !== 0) return;
    if (!vs) launch('code');
    vs.el.classList.remove('min');
    focus(vs.el);
    vs.el.classList.add('agent-setup');
    vs.thread.replaceChildren();
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
    edge.title.textContent = 'Copilot Studio';
    const studio = document.createElement('div');
    studio.className = 'sample-studio';
    studio.innerHTML = '<header><span>Copilot Studio</span><strong id="studio-agent"></strong><span>Test your agent</span></header><div class="studio-thread"></div><form><input id="studio-input" aria-label="First sample question"><button id="studio-send" type="submit">Send</button></form>';
    edge.view.replaceChildren(studio);
    $('#studio-agent').textContent = options.story.name;
    $('#studio-input').value = options.story.question;
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
      answer.textContent = 'Sample data: answer placeholder. On your own agent, you will see an answer drawn from the sample records, with supporting evidence to review.';
      $('.studio-thread', studio).replaceChildren(question, answer);
      $('#studio-input').value = '';
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
    playbackVersion++;
    mode = next;
    playing = next === 'watch' && step < STEPS.length;
    renderControls();
    showHint();
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
      transfer.setData('text/plain', 'pretend:hacker_news_agent.py');
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
      await sleep(1000);
      if (mode === 'watch' && playing) await act(true);
    }
  }
  function dispose() {
    disposed = true;
    clearInterval(clock);
    if (stage) phone.removeEventListener('change', adaptSteps);
  }
  function restart(initialStep, nextMode = mode) {
    dispose();
    return window.AibastDesktop.mount(host, {...options, initialStep, mode:nextMode});
  }
  let toastT; function toast(title, body) { const t = $('#toast'); t.innerHTML = `<b>${title}</b>${body}`; t.style.display = 'block'; clearTimeout(toastT); toastT = setTimeout(() => { t.style.display = 'none'; }, 5000); }
  enterStep(); render(); setTimeout(showHint, 900);
  window.practicePC = { launch, state, step: () => step, STEPS, dispose };
  host.practiceDesktop = window.practicePC;
  if (stage) {
    pc.addEventListener('input', showHint);
    pc.addEventListener('click', () => setTimeout(showHint, 0));
    watch();
  }

    return window.practicePC;
  }
};
