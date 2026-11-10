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
  const q = (m) => document.querySelector(`[data-aibast~="${m}"]`);
  const qa = (m) => [...document.querySelectorAll(`[data-aibast~="${m}"]`)];
  const tpl = {};
  let suggestionTpl = null, placeholderText = '', placeholderColor = '', agentName = '';

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
    },
    landing(suggestions = []) {
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
    ask(question) {
      this.clearComposer();
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
        #compact-conversation p { margin:0 0 8px; }
        #compact-conversation button { border:1px solid #e0e0e0; background:#fff; color:#242424; border-radius:6px; padding:8px; font:inherit; }
      `;
      document.head.appendChild(style);
      const conversation = document.createElement('div');
      conversation.id = 'compact-conversation';
      conversation.innerHTML = `
        <header><span data-aibast="title agent-name">Agent preview</span></header>
        <section data-aibast="scroll">
          <div data-aibast="turn turn-q"><div data-aibast="question"></div></div>
          <div data-aibast="turn turn-a">
            <div data-aibast="answer"><p></p></div>
            <div data-aibast="suggestions"><button type="button"></button></div>
          </div>
        </section>
        <div data-aibast="composer"><span data-aibast="placeholder">Ask a question</span></div>
      `;
      document.body.replaceChildren(conversation);
    }
    learnTemplates();
    document.querySelectorAll('a[href="#"]').forEach((a) => a.addEventListener('click', (e) => e.preventDefault()));
    document.addEventListener('click', (e) => { if (!e.target.closest('[data-aibast~="suggestion"]')) window.parent.postMessage({aibast: 'click'}, '*'); });
    api.ready = true;
    window.parent.postMessage({aibast: 'ready'}, '*');
  }
  window.AibastSurface = api;
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
