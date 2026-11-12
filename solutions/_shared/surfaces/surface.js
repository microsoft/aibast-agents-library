/* AIBAST demo surface adapter.
 *
 * Each surface (m365, cowork, studio) is a saved copy of the real product page with its parts
 * marked by data-aibast: question, answer, turn-q, turn-a, thinking, suggestions, composer,
 * placeholder, scroll, agent-name, title, greeting, skill. This file fills those parts. It makes
 * no network calls; the player gives it everything it shows.
 *
 *   AibastSurface.setAgent(name, {skill, greeting, title, chats})
 *   AibastSurface.landing(suggestions)     clear the conversation, show starter questions
 *   AibastSurface.type(text) / clearComposer()
 *   AibastSurface.ask(question)            show the question and the thinking state
 *   AibastSurface.answer(markdown, opts)   stream the answer; resolves when it is all shown
 *   AibastSurface.followups(list)
 *   AibastSurface.target(name, index)      a rectangle for the pointer: composer, suggestion
 */
(() => {
  'use strict';
  // One player bar for every surface (Cowork, Microsoft 365 Copilot, Copilot Studio): same look, same buttons.
  const PLAYER_CSS = '  /* player bar */\n  .aibast-player, .aibast-player *, .aibast-menu, .aibast-pill { box-sizing: border-box; font-family: "Segoe UI", system-ui, sans-serif; line-height: normal; }\n  .aibast-player { position: fixed; left: 50%; bottom: 14px; transform: translateX(-50%); width: min(1180px, calc(100% - 40px)); display: flex; align-items: center; gap: 14px; padding: 8px 14px; background: #3b3b3d; color: #f2f2f2; border-radius: 16px; box-shadow: 0 8px 28px rgba(0,0,0,.28); font-size: 14px; z-index: 5; }\n  .aibast-player button { all: unset; cursor: pointer; display: grid; place-items: center; min-width: 32px; height: 32px; border-radius: 50%; color: #f2f2f2; font-size: 13px; font-weight: 600; }\n  .aibast-player button:hover { background: rgba(255,255,255,.12); }\n  .aibast-player button:focus-visible { outline: 2px solid #fff; }\n  .aibast-player .big { width: 38px; height: 38px; background: rgba(255,255,255,.14); }\n  .aibast-player .n { color: #bdbdbd; white-space: nowrap; }\n  .aibast-player .t { font-weight: 600; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }\n  .aibast-player .cc[aria-pressed="true"] { background: rgba(255,255,255,.22); }\n  .aibast-menu { position: fixed; bottom: 64px; left: 50%; transform: translateX(-50%); width: 420px; background: #2d2d2f; color: #f2f2f2; border-radius: 12px; padding: 8px; list-style: none; margin: 0; display: none; z-index: 6; font-size: 13px; }\n  .aibast-menu.open { display: block; }\n  .aibast-menu li { padding: 8px 10px; border-radius: 8px; cursor: pointer; }\n  .aibast-menu li:hover, .aibast-menu li.on { background: rgba(255,255,255,.12); }\n  .aibast-pill { position: fixed; left: 50%; bottom: 74px; transform: translateX(-50%); max-width: 760px; background: rgba(32,32,32,.86); color: #fff; padding: 8px 16px; border-radius: 18px; font-size: 15px; text-align: center; z-index: 4; }\n';
  const PLAYER_HTML = '<div class="aibast-pill" data-aibast="caption"></div>\n<ul class="aibast-menu" data-aibast="player-menu" role="menu"></ul>\n<div class="aibast-player" data-aibast="player" role="toolbar" aria-label="Demo player">\n  <button type="button" data-act="back" aria-label="Previous screen">&#10094;</button>\n  <button type="button" class="big" data-act="play" data-aibast="player-play" aria-label="Play">&#9654;</button>\n  <button type="button" data-act="next" aria-label="Next screen">&#10095;</button>\n  <span class="n" data-aibast="player-n">Screen 1 of 1</span>\n  <span class="t" data-aibast="player-title">Cowork</span>\n  <button type="button" data-act="list" aria-label="Screens">&#9776;</button>\n  <button type="button" data-act="mute" data-aibast="player-mute" aria-label="Sound"><svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 8h3l4-3.5v11L6 12H3z"/><path d="M13 7.5a3.5 3.5 0 0 1 0 5M15 5a7 7 0 0 1 0 10"/></svg></button>\n  <button type="button" data-act="speed" data-aibast="player-speed" aria-label="Speed">1x</button>\n  <button type="button" class="cc" data-act="cc" data-aibast="player-cc" aria-pressed="true" aria-label="Captions">CC</button>\n  <button type="button" data-act="replay" aria-label="Replay">&#8634;</button>\n</div>\n';
  function mountPlayer() {
    if (q('player')) return;
    const st = document.createElement('style'); st.textContent = PLAYER_CSS; document.head.appendChild(st);
    const box = document.createElement('div'); box.innerHTML = PLAYER_HTML;
    if (q('caption')) box.querySelector('[data-aibast="caption"]').remove();
    document.body.append(...box.children);
    // Cowork leaves room for the bar in its own layout; the other surfaces get the room here.
    if (!document.body.hasAttribute('data-player-room')) { const r = document.createElement('style'); r.textContent = 'html, body { box-sizing: border-box; } body { padding-bottom: 96px !important; height: 100vh; }'; document.head.appendChild(r); }
  }
  const q = (m) => document.querySelector(`[data-aibast~="${m}"]`);
  const qa = (m) => [...document.querySelectorAll(`[data-aibast~="${m}"]`)];
  const tpl = {};
  let suggestionTpl = null, placeholderText = '', placeholderColor = '', agentName = '';
  // Cowork frame only: the task plan (Workspace steps), the data sources (Plugins) and the tool
  // trail. Every part is optional; a surface without the marker simply ignores it.
  const isCowork = () => document.documentElement.dataset.aibastSurface === 'cowork';
  const work = {plan: [], done: new Set(), plugins: [], tools: [], timers: [], step: -1};
  const human = (s) => { const t = String(s).replace(/^@[^/]+\//, '').replace(/[-_]+/g, ' ').trim(); return t.charAt(0).toUpperCase() + t.slice(1); };
  function renderPlan() {
    const box = q('plan'); if (!box) return;
    box.innerHTML = '';
    work.plan.forEach((t, i) => { const li = document.createElement('li'); li.textContent = t;
      if (work.done.has(i)) li.className = 'done'; else if (i === work.step) li.className = 'now'; box.appendChild(li); });
    const c = q('plan-count'); if (c) c.textContent = `${work.done.size} / ${work.plan.length}`;
  }
  function renderPlugins() {
    const box = q('plugins'); if (!box) return;
    box.innerHTML = '';
    work.plugins.forEach((t) => { const s = document.createElement('span'); s.textContent = t; s.title = t; box.appendChild(s); });
  }
  function clearTrail() { work.timers.forEach(clearTimeout); work.timers = []; const t = q('trail'); if (t) t.innerHTML = ''; }
  function playTrail(step) {
    const box = q('trail'); if (!box) return;
    clearTrail();
    const p = work.plugins, t = work.tools, lines = [];
    if (p.length) lines.push(['Read ' + p[step % p.length]]);
    for (let k = 0; k < Math.min(2, t.length); k++) lines.push(['Run ' + t[(step + k) % t.length]]);
    if (p.length > 1) lines.push(['Read ' + p[(step + 1) % p.length]]);
    lines.push(['Running analysis...', 'sub']);
    lines.forEach(([text, cls], i) => work.timers.push(setTimeout(() => {
      box.querySelectorAll('li.now').forEach((n) => n.classList.remove('now'));
      const li = document.createElement('li'); li.textContent = text; li.className = (cls || '') + ' now'; box.appendChild(li);
    }, i * 220)));
  }

  function learnTemplates() {
    const answer = q('answer');
    if (answer) {
      for (const tag of ['p', 'ul', 'ol', 'li', 'strong', 'h1', 'h2', 'h3', 'h4']) {
        const el = answer.querySelector(tag);
        if (el) tpl[tag] = {cls: el.getAttribute('class') || '', style: el.getAttribute('style') || ''};
      }
    }
    const box = q('suggestions');
    if (box && box.firstElementChild) suggestionTpl = box.firstElementChild.cloneNode(true);
    const ph = q('placeholder');
    if (ph) { placeholderText = ph.textContent; placeholderColor = getComputedStyle(ph).color; }
  }

  function el(tag, html) {
    const node = document.createElement(tag);
    const t = tpl[tag];
    if (t) { if (t.cls) node.setAttribute('class', t.cls); if (t.style) node.setAttribute('style', t.style); }
    if (html != null) node.innerHTML = html;
    return node;
  }
  const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  // "***4521" is a masked number, not emphasis: keep it literal
  const inline = (s) => esc(s).replace(/\*{3}(?=\d)/g, '\u0000').replace(/\*\*(.+?)\*\*/g, (m, x) => {
    const t = tpl.strong; return `<strong${t && t.cls ? ` class="${t.cls}"` : ''}>${x}</strong>`;
  }).replace(/\u0000/g, '***');

  /** Markdown (the subset the recorded answers use) into blocks styled like the product's own. */
  function blocks(md) {
    const out = [];
    let list = null;
    let table = null;
    for (const raw of String(md).split('\n')) {
      const line = raw.replace(/\s+$/, '');
      if (/^\s*\|.*\|\s*$/.test(line)) {   // markdown table row
        list = null;
        const cells = line.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim());
        if (cells.every((c) => /^:?-{2,}:?$/.test(c))) continue;
        if (!table) { table = document.createElement('table'); table.setAttribute('style', 'border-collapse:collapse;margin:8px 0 12px;font:inherit;width:100%'); out.push(table); }
        const head = !table.rows.length, tr = table.insertRow();
        for (const c of cells) { const td = document.createElement(head ? 'th' : 'td');
          td.setAttribute('style', `text-align:left;vertical-align:top;padding:6px 10px;border-bottom:1px solid #e0e0e0;${head ? 'font-weight:600;' : ''}`);
          td.innerHTML = inline(c); tr.appendChild(td); }
        continue;
      }
      table = null;
      const bullet = line.match(/^\s*[-*]\s+(.*)/), num = line.match(/^\s*\d+[.)]\s+(.*)/);
      const head = line.match(/^(#{1,4})\s+(.*)/);
      if (bullet || num) {
        const kind = bullet ? 'ul' : 'ol';
        if (!list || list.tagName.toLowerCase() !== kind) { list = el(kind); out.push(list); }
        list.appendChild(el('li', inline((bullet || num)[1])));
        continue;
      }
      list = null;
      if (!line.trim()) continue;
      if (head) { const tag = 'h' + Math.min(4, head[1].length + 1); const ht = /^\*\*.*\*\*$/.test(head[2]) ? head[2] : `**${head[2]}**`;
        out.push(el(tpl[tag] ? tag : 'p', tpl[tag] ? inline(ht) : `<strong>${inline(head[2])}</strong>`)); continue; }
      out.push(el('p', inline(line)));
    }
    return out;
  }

  const show = (m, on) => qa(m).forEach((n) => { n.style.visibility = on ? '' : 'hidden'; n.style.display = on ? '' : 'none'; });
  const scroller = () => q('scroll');
  function scrollTo(node) {
    const sc = scroller(); if (!sc || !node) return;
    const r = node.getBoundingClientRect(), c = sc.getBoundingClientRect();
    sc.scrollTop += r.top - c.top - 24;
  }
  function scrollBottom() { const sc = scroller(); if (sc) sc.scrollTop = sc.scrollHeight; }

  const api = {
    ready: false,
    setAgent(name, opts = {}) {
      agentName = name;
      qa('agent-name').forEach((n) => { n.textContent = name; });
      if (opts.title) qa('title').forEach((n) => { n.textContent = opts.title; if (n.hasAttribute('title')) n.setAttribute('title', opts.title); });
      const g = q('greeting'); if (g && opts.greeting) g.textContent = opts.greeting;
      if (opts.chats) qa('chat-item').forEach((n, i) => { const t = opts.chats[i] || ''; n.textContent = t; const a = n.closest('a'); if (a) a.setAttribute('aria-label', t); });
      const s = q('skill'); if (s && opts.skill) s.textContent = 'Used skill: ' + opts.skill;
      const ph = q('placeholder');
      if (ph && document.documentElement.dataset.aibastSurface !== 'cowork') { placeholderText = 'Message ' + name; ph.textContent = placeholderText; }
      document.title = name;
      if (opts.plan) { work.plan = opts.plan.slice(); renderPlan(); }
      if (opts.plugins) { work.plugins = opts.plugins.slice(); renderPlugins(); }
      if (opts.tools) work.tools = opts.tools.map(human);
      const cards = q('cards');
      if (cards && opts.cards) { cards.innerHTML = ''; opts.cards.forEach((t) => { const c = document.createElement('div'); c.className = 'card'; c.textContent = t; cards.appendChild(c); }); }
    },
    /** Cowork: forget which plan steps are done (a fresh run from the start). */
    resetPlan() { work.done.clear(); work.step = -1; renderPlan(); },
    /** Cowork: the floating player bar mirrors the player's state; its buttons post back. */
    /** True only when this surface draws its own player bar (Cowork). */
    hasPlayer() { return !!q('player'); },
    player(state = {}) {
      const bar = q('player'); if (!bar) return;
      const set = (m, text) => { const n = q(m); if (n) n.textContent = text; };
      set('player-n', `Screen ${state.n || 1} of ${state.total || 1}`);
      set('player-title', state.title || '');
      const play = q('player-play'); if (play) { play.innerHTML = state.playing ? '&#10073;&#10073;' : '&#9654;'; play.setAttribute('aria-label', state.playing ? 'Pause' : 'Play'); }
      const mute = q('player-mute'); if (mute) { mute.style.opacity = state.muted ? '.5' : ''; mute.setAttribute('aria-label', state.muted ? 'Sound off' : 'Sound on'); }
      const cc = q('player-cc'); if (cc) cc.setAttribute('aria-pressed', String(state.cc !== false));
      const sp = q('player-speed'); if (sp) sp.textContent = (state.speed || 1) + 'x';
      const menu = q('player-menu');
      if (menu && state.steps) { menu.innerHTML = ''; state.steps.forEach((t, i) => { const li = document.createElement('li'); li.setAttribute('role', 'menuitem'); li.textContent = `${i + 1}. ${t}`;
        if (i === (state.stepIndex || 0)) li.className = 'on';
        li.addEventListener('click', () => { menu.classList.remove('open'); window.parent.postMessage({aibast: 'control', action: 'goto', index: i}, '*'); }); menu.appendChild(li); }); }
    },
    caption(text) { const c = q('caption'); if (!c) return false; c.textContent = text || ''; return true; },
    landing(suggestions = []) {
      if (isCowork()) { document.documentElement.dataset.mode = 'home'; clearTrail(); }
      show('turn', false);
      this.followups(suggestions);
      this.clearComposer();
      const sc = scroller(); if (sc) sc.scrollTop = 0;
    },
    type(text) {
      const ph = q('placeholder'); if (!ph) return;
      ph.textContent = text; ph.style.color = '#242424';
    },
    clearComposer() {
      const ph = q('placeholder'); if (!ph) return;
      ph.textContent = placeholderText; ph.style.color = '';
    },
    ask(question, opts = {}) {
      this.clearComposer();
      if (isCowork()) {
        document.documentElement.dataset.mode = 'chat';
        qa('task-title').forEach((n) => { n.textContent = opts.task || question; });
        const wl = q('work-label'); if (wl) wl.textContent = 'Working on it';
        if (opts.step != null) { work.step = opts.step; renderPlan(); playTrail(opts.step); }
      }
      const qn = q('question'); if (qn) qn.textContent = question;
      show('turn-q', true); show('turn-a', true);
      const a = q('answer'); if (a) a.innerHTML = '';
      show('thinking', true);
      this.followups([]);
      scrollTo(q('turn-q'));
    },
    async answer(md, opts = {}) {
      const a = q('answer'); if (!a) return;
      const cps = opts.cps || 1200, tick = opts.tick || 90;
      const parts = blocks(md);
      a.innerHTML = '';
      // stream a line or more at a time, top to bottom, the way the product does
      for (const part of parts) {
        if (opts.signal && opts.signal.aborted) return;
        const html = part.innerHTML; const isList = /^(UL|OL)$/.test(part.tagName) || part.tagName === 'TABLE';
        if (isList) {
          const holder = part.tagName === 'TABLE' ? part.tBodies[0] : part; const items = [...holder.children]; holder.innerHTML = ''; a.appendChild(part);
          for (const li of items) { holder.appendChild(li); await wait(Math.max(tick, (li.textContent.length / cps) * 1000), opts.signal); keepInView(); }
        } else {
          a.appendChild(part);
          await wait(Math.max(tick, (html.length / cps) * 1000), opts.signal); keepInView();
        }
      }
      if (isCowork() && !(opts.signal && opts.signal.aborted)) {
        show('thinking', false);
        work.timers.forEach(clearTimeout); work.timers = []; qa('trail').forEach((t) => [...t.children].forEach((li) => { li.classList.remove('now'); li.classList.add('ok'); }));
        const wl = q('work-label'), n = (q('trail') || {children: []}).children.length; if (wl) wl.textContent = `Worked through ${n} steps`;
        if (work.step >= 0) { work.done.add(work.step); renderPlan(); }
      }
      function keepInView() { const sc = scroller(); if (!sc) return; const turn = q('turn-q');
        const r = a.getBoundingClientRect(), c = sc.getBoundingClientRect();
        if (r.bottom > c.bottom - 8) sc.scrollTop += Math.min(r.bottom - c.bottom + 24, turn ? turn.getBoundingClientRect().top - c.top : 1e9); }
    },
    followups(list) {
      const box = q('suggestions'); if (!box) return;
      box.innerHTML = '';
      if (!suggestionTpl) return;
      list.forEach((text, i) => {
        const b = suggestionTpl.cloneNode(true);
        const w = document.createTreeWalker(b, NodeFilter.SHOW_TEXT); let n, set = false;
        while ((n = w.nextNode())) { if (!set && n.textContent.trim()) { n.textContent = text; set = true; } else if (n.textContent.trim()) n.textContent = ''; }
        if (!set) b.textContent = text;
        b.setAttribute('data-aibast', 'suggestion'); b.setAttribute('data-index', String(i));
        if (isCowork() && work.plugins.length) { const chip = document.createElement('span'); chip.className = 'chip'; chip.textContent = work.plugins[i % work.plugins.length]; b.appendChild(chip); }
        b.addEventListener('click', () => window.parent.postMessage({aibast: 'suggestion', index: i}, '*'));
        box.appendChild(b);
      });
      box.style.display = list.length ? (box.getAttribute('data-aibast-display') || '') : 'none';
    },
    target(name, index = 0) {
      let node = null;
      if (name === 'suggestion') node = document.querySelectorAll('[data-aibast~="suggestion"]')[index] || null;
      else node = q(name);
      if (!node) return null;
      const r = node.getBoundingClientRect();
      if (!r.width || !r.height) return null;
      return {x: r.left, y: r.top, width: r.width, height: r.height};
    },
    scrollAnswerIntoView() { scrollTo(q('turn-q')); },
  };

  function wait(ms, signal) {
    return new Promise((resolve) => { const t = setTimeout(resolve, ms); if (signal) signal.addEventListener('abort', () => { clearTimeout(t); resolve(); }, {once: true}); });
  }

  function init() {
    if (new URLSearchParams(location.search).get('compact') === '1') {
      const style = document.createElement('style');
      style.textContent = `
        html, body { margin:0 !important; height:100% !important; min-width:0 !important; overflow:hidden !important; }
        #compact-conversation { display:flex; flex-direction:column; height:100%; background:#fff; color:#242424; font:14px/1.5 "Segoe UI",sans-serif; }
        #compact-conversation * { box-sizing:border-box; max-width:100%; }
        #compact-conversation header { padding:8px 12px; border-bottom:1px solid #e0e0e0; font-size:12px; font-weight:600; }
        #compact-conversation section { flex:1; min-height:0; overflow:auto; padding:12px; }
        #compact-conversation [data-aibast~="turn-q"] { margin-bottom:12px; padding:10px; border-radius:8px; background:#f0f5fa; }
        #compact-conversation [data-aibast~="composer"] { flex-shrink:0; padding:10px 12px; border-top:1px solid #e0e0e0; overflow-wrap:anywhere; }
        #compact-conversation [data-aibast~="suggestions"] { display:grid; gap:8px; }
        #compact-conversation p { margin:0 0 8px; }
        #compact-conversation button { border:1px solid #e0e0e0; background:#fff; color:#242424; border-radius:6px; padding:8px; font:inherit; }
      `;
      document.head.appendChild(style);
      const conversation = document.createElement('div');
      conversation.id = 'compact-conversation';
      conversation.innerHTML = `
        <header><span data-aibast="title agent-name">Agent preview</span></header>
        <section data-aibast="scroll">
          <p data-aibast="greeting">Ask a question using sample data.</p>
          <div data-aibast="turn turn-q"><div data-aibast="question"></div></div>
          <div data-aibast="turn turn-a">
            <div data-aibast="answer"><p></p></div>
          </div>
          <div data-aibast="suggestions"><button type="button"></button></div>
        </section>
        <div data-aibast="composer"><span data-aibast="placeholder">Ask a question</span></div>
      `;
      document.body.replaceChildren(conversation);
    }
    learnTemplates();
    mountPlayer();
    const bar = q('player');
    if (bar) bar.addEventListener('click', (e) => {
      const b = e.target.closest('[data-act]'); if (!b) return;
      e.stopPropagation();
      const menu = q('player-menu');
      if (b.dataset.act === 'list') { if (menu) menu.classList.toggle('open'); return; }
      window.parent.postMessage({aibast: 'control', action: b.dataset.act}, '*');
    });
    document.querySelectorAll('a[href="#"]').forEach((a) => a.addEventListener('click', (e) => e.preventDefault()));
    document.addEventListener('click', (e) => { if (!e.target.closest('[data-aibast~="suggestion"]')) window.parent.postMessage({aibast: 'click'}, '*'); });
    api.ready = true;
    window.parent.postMessage({aibast: 'ready'}, '*');
  }
  window.AibastSurface = api;
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
