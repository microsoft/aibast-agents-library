/* Microsoft 365 Copilot chat look for the library's recorded demos.
 *
 *   const chat = window.RappM365.mount(host, {name, starters: [{title, text}], ask: async (question, history) => answer,
 *                                             initials, createdBy})
 *   chat.send(text) -> asks it as Enter in the composer does
 *
 * `ask` returns the finished answer (Markdown); it is streamed client-side a line at a time, as Microsoft 365 Copilot
 * shows an answer.
 */
(() => {
  'use strict';
  const STREAM_CPS = 1200;
  const TICK_MS = 90;
  const GLYPH_MS = 354;
  const HEAD_ONLY_MS = 550;
  const TITLE_MAX = 20;
  const SUGGEST_MS = 700;
  const SUGGEST_MAX = 5;
  const SUGGEST_CUT = 101;
  const THUMB_HOLD_MS = 900;
  const THUMB_FOOT = 32;
  const THINKING = 'Lining things up...';
  const DISCLAIMER = 'AI-generated content may be incorrect';

  const NS = 'http://www.w3.org/2000/svg';
  function svg(w, h, body, cls, box) {
    const node = document.createElementNS(NS, 'svg');
    const [bw, bh] = Array.isArray(box) ? box : box ? [box, box] : [w, h];
    node.setAttribute('width', w); node.setAttribute('height', h); node.setAttribute('viewBox', `0 0 ${bw} ${bh}`);
    node.setAttribute('fill', 'none'); node.setAttribute('aria-hidden', 'true');
    if (cls) node.setAttribute('class', cls);
    node.innerHTML = body;
    return node;
  }
  const stroke = 'stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"';
  const fluent = (d, size = 16, cls) => svg(size, size, `<path fill="currentColor" d="${d}"/>`, cls, 20);
  const FLUENT = {
    compose: 'M17.85 2.85a.5.5 0 0 0-.7-.7l-8 8L9 11l.85-.15 8-8ZM5.5 3A2.5 2.5 0 0 0 3 5.5v9A2.5 2.5 0 0 0 5.5 17h9a2.5 2.5 0 0 0 2.5-2.5v-6a.5.5 0 0 0-1 0v6c0 .83-.67 1.5-1.5 1.5h-9A1.5 1.5 0 0 1 4 14.5v-9C4 4.67 4.67 4 5.5 4h6a.5.5 0 0 0 0-1h-6Z',
    search: 'M12.73 13.44a6.5 6.5 0 1 1 .7-.7l3.42 3.4a.5.5 0 0 1-.63.77l-.07-.06-3.42-3.41Zm-.71-.71A5.54 5.54 0 0 0 14 8.5a5.5 5.5 0 1 0-1.98 4.23Z',
    library: 'M2 3.5C2 2.67 2.67 2 3.5 2h1C5.33 2 6 2.67 6 3.5v12.98c0 .83-.67 1.5-1.5 1.5h-1a1.5 1.5 0 0 1-1.5-1.5V3.5ZM3.5 3a.5.5 0 0 0-.5.5v12.98c0 .28.22.5.5.5h1a.5.5 0 0 0 .5-.5V3.5a.5.5 0 0 0-.5-.5h-1Zm3.5.5C7 2.67 7.67 2 8.5 2h1c.83 0 1.5.67 1.5 1.5v12.98c0 .83-.67 1.5-1.5 1.5h-1a1.5 1.5 0 0 1-1.5-1.5V3.5ZM8.5 3a.5.5 0 0 0-.5.5v12.98c0 .28.22.5.5.5h1a.5.5 0 0 0 .5-.5V3.5a.5.5 0 0 0-.5-.5h-1Zm7.22 3.16a1.5 1.5 0 0 0-1.87-1.1l-.75.2A1.5 1.5 0 0 0 12.04 7l2 9.8c.18.84 1.02 1.36 1.84 1.15l.99-.25c.79-.2 1.27-1 1.1-1.78l-2.25-9.76ZM14.12 6a.5.5 0 0 1 .62.37L17 16.14a.5.5 0 0 1-.37.6l-.98.25a.5.5 0 0 1-.61-.39l-2-9.8a.5.5 0 0 1 .35-.58l.74-.2Z',
    more: 'M6.25 10a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0Zm5 0a1.25 1.25 0 1 1-2.5 0 1.25 1.25 0 0 1 2.5 0ZM15 11.25a1.25 1.25 0 1 0 0-2.5 1.25 1.25 0 0 0 0 2.5Z',
    like: 'M10.05 2.3c.34-.98 1.63-1.43 2.43-.6.17.17.33.36.44.52.32.48.45 1.12.5 1.73.05.63.02 1.3-.05 1.91-.06.62-.16 1.18-.24 1.59v.05H14a3 3 0 0 1 2.95 3.54l-.69 3.76a4.5 4.5 0 0 1-5.6 3.53l-5.6-1.52a2.5 2.5 0 0 1-1.8-1.92l-.35-1.77c-.28-1.39.78-2.56 1.9-3 .33-.13.62-.3.85-.5 1.7-1.5 2.32-2.72 3.38-4.84.36-.71.72-1.68 1-2.49Zm1.97 5.58v-.04a13.7 13.7 0 0 0 .13-.58c.08-.4.17-.93.23-1.5.06-.58.09-1.18.04-1.73a2.73 2.73 0 0 0-.33-1.25 3.26 3.26 0 0 0-.33-.39c-.2-.2-.63-.16-.76.23-.29.82-.67 1.83-1.05 2.6-1.07 2.14-1.76 3.5-3.62 5.15-.34.3-.74.52-1.13.68-.88.34-1.45 1.14-1.3 1.87l.35 1.77c.11.56.53 1 1.08 1.15l5.6 1.53c1.98.54 4-.73 4.36-2.75l.68-3.76a2 2 0 0 0-1.96-2.36h-1.5a.5.5 0 0 1-.5-.62Z',
    dislike: 'M10.05 17.7c.34.98 1.63 1.43 2.43.6.17-.17.33-.36.44-.52.32-.48.45-1.12.5-1.73.05-.63.02-1.3-.05-1.92-.06-.6-.16-1.17-.24-1.58v-.05H14a3 3 0 0 0 2.95-3.54l-.69-3.76a4.5 4.5 0 0 0-5.6-3.54L5.06 3.2c-.92.25-1.62 1-1.8 1.92l-.35 1.77c-.28 1.39.78 2.56 1.9 3 .33.13.62.3.85.5 1.7 1.5 2.32 2.72 3.38 4.84.36.71.72 1.68 1 2.49Zm1.97-5.58v.04a14.2 14.2 0 0 1 .36 2.08c.06.58.09 1.18.04 1.73-.04.55-.15.98-.33 1.25-.06.1-.18.22-.33.39-.2.2-.63.16-.76-.23-.29-.82-.67-1.83-1.05-2.6-1.07-2.14-1.76-3.5-3.62-5.15-.34-.3-.74-.52-1.13-.68-.88-.34-1.45-1.14-1.3-1.87l.35-1.77c.11-.56.53-1 1.08-1.15l5.6-1.53a3.5 3.5 0 0 1 4.36 2.75l.68 3.76a2 2 0 0 1-1.96 2.36h-1.5a.5.5 0 0 0-.5.62Z',
    chat: 'M10 2a8 8 0 1 1-3.61 15.14l-.12-.07-3.65.92a.5.5 0 0 1-.62-.45v-.08l.01-.08.92-3.64-.07-.12a7.95 7.95 0 0 1-.83-2.9l-.02-.37L2 10a8 8 0 0 1 8-8Zm0 1a7 7 0 0 0-6.1 10.42.5.5 0 0 1 .06.28l-.02.1-.75 3.01 3.02-.75a.5.5 0 0 1 .19-.01l.09.02.09.04A7 7 0 1 0 10 3Zm.5 8a.5.5 0 0 1 .09 1H7.5a.5.5 0 0 1-.09-1h3.09Zm2-3a.5.5 0 0 1 .09 1H7.5a.5.5 0 0 1-.09-1h5.09Z',
  };
  const ICONS = {
    logo: () => svg(18.4, 16.8, '<g stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
      + '<path d="M25.5 6H14.4Q11.6 6 10.6 8.8L7.2 20.4Q5.8 26.2 11.4 26.2H21.4"/><path d="M25.6 6.4L19.8 25.8"/>'
      + '<path d="M25 6H28.6Q31 6 31.9 8.8L33.2 14.2"/><path d="M23.4 14.4H37Q41.2 14.6 40.2 18.8L36.8 31.2Q35.8 35.5 31.8 35.5H19.2"/>'
      + '<path d="M27.4 14.8L21.2 35"/><path d="M13.2 26.4Q14.4 29.6 16 32.6Q17.4 35.5 19.6 35.5"/></g>', 'm365-logo-mark', [46, 42]),
    compose: () => fluent(FLUENT.compose),
    search: () => fluent(FLUENT.search),
    library: () => fluent(FLUENT.library),
    shield: () => svg(16, 16, '<path d="M10 2.4Q13 4.4 16.4 4.8V10Q16.4 15 10 17.6Q3.6 15 3.6 10V4.8Q7 4.4 10 2.4Z" stroke="currentColor" stroke-width=".95" stroke-linejoin="round"/>'
      + '<path d="M7.2 9.4L9.5 11.6L13.6 7.4" stroke="currentColor" stroke-width=".95" stroke-linecap="round" stroke-linejoin="round"/>', 'm365-shield', 20),
    more: () => fluent(FLUENT.more),
    plus: () => svg(16, 16, `<path d="M8 2.5v11M2.5 8h11" ${stroke}/>`, 'm365-plus'),
    mic: () => svg(14, 14, `<rect x="4.9" y="1.4" width="4.2" height="7" rx="2.1" ${stroke}/><path d="M3 6.6c0 2.2 1.8 4 4 4s4-1.8 4-4M7 10.6v2.2" ${stroke}/>`),
    arrow: () => svg(12, 12, '<path d="M6 10V2.2M2.6 5.4L6 2l3.4 3.4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>', 'm365-arrow'),
    down: () => svg(12, 12, '<path d="M6 2v7.6M2.8 6.6L6 9.8l3.2-3.2" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/>'),
    copy: () => svg(16, 16, '<g stroke="currentColor" stroke-width="1.05" stroke-linejoin="round"><rect x="9.2" y="3.4" width="7.8" height="10.6" rx="2.3"/>'
      + '<path d="M9.2 6.4H6.6Q4 6.4 4 9V14.4Q4 17 6.6 17H9.6Q12.2 17 12.6 14"/></g>', null, 20),
    like: () => fluent(FLUENT.like),
    dislike: () => fluent(FLUENT.dislike),
    chat: () => fluent(FLUENT.chat, 16),
    chevron: () => svg(8, 8, '<path d="M1.3 2.7l2.7 2.7 2.7-2.7" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/>'),
    robot: s => svg(s, s, '<g stroke="#fff" stroke-width="2.4" stroke-linejoin="round">'
      + '<path d="M20.4 37.2V45L27.6 37.2H37.4Q39.6 37.2 39.6 35V15.4Q39.6 13.2 37.4 13.2H10.6Q8.4 13.2 8.4 15.4V35Q8.4 37.2 10.6 37.2Z"/>'
      + '<path d="M24 13.2V5.6"/><path d="M17 29Q24 34.6 31 29" stroke-linecap="round"/></g><g fill="#fff"><circle cx="24" cy="4" r="2.4"/>'
      + '<rect x="15.6" y="20.6" width="3.8" height="3.8" rx=".8"/><rect x="28.6" y="20.6" width="3.8" height="3.8" rx=".8"/>'
      + '<rect x="4.4" y="20.4" width="3.2" height="6.8" rx=".6"/><rect x="40.4" y="20.4" width="3.2" height="6.8" rx=".6"/></g>', null, 48),
    bars: () => svg(9.6, 9.6, [...Array(9).keys()].map(i => `<rect x="${(i % 3) * 10}" y="${Math.floor(i / 3) * 10}" width="10" height="10"/>`).join(''), 'm365-bars', 30),
  };

  function el(tag, attrs = {}, ...children) {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(attrs || {})) {
      if (value == null || value === false) continue;
      if (key === 'text') node.textContent = value;
      else if (key === 'class') node.className = value;
      else node.setAttribute(key, value === true ? '' : value);
    }
    for (const child of children.flat()) if (child != null && child !== false) node.append(child);
    return node;
  }
  const button = (label, icon, cls = 'm365-ic', extra = {}) => el('button', {type: 'button', class: cls, 'aria-label': label, title: label, ...extra}, icon);
  const GLYPH_FRAMES = [[0, 1, 4, 6, 8], [1, 3, 4, 6, 8], [2, 3, 4, 6, 8], [1, 2, 3, 6, 8], [1, 2, 3, 7, 8],
    [1, 2, 3, 5, 7], [1, 2, 5, 6, 7], [0, 2, 5, 6, 7], [0, 1, 5, 6, 7], [0, 1, 4, 5, 6]];
  function animateGlyph(node, running) {
    const cells = [...node.querySelectorAll('rect')];
    let frame = 0;
    const draw = () => { const on = GLYPH_FRAMES[frame % GLYPH_FRAMES.length]; cells.forEach((c, i) => c.style.opacity = on.includes(i) ? 1 : 0); frame += 1; };
    draw();
    const timer = setInterval(() => (running() ? draw() : clearInterval(timer)), GLYPH_MS);
  }
  const tile = size => el('span', {class: 'm365-tile', 'aria-hidden': 'true'}, ICONS.robot(size));

  const escape = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  function inline(text) {
    let s = escape(text);
    const codes = [];
    s = s.replace(/`([^`]+)`/g, (_, c) => { codes.push(c); return `\u0000${codes.length - 1}\u0000`; });
    s = s.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, t, u) => `<a href="${/^(https?:|mailto:|#)/i.test(u) ? u : '#'}" tabindex="-1">${t}</a>`);
    s = s.replace(/\*\*(?=\S)(.+?)(?<=\S)\*\*/g, '<strong>$1</strong>').replace(/__(?=\S)(.+?)(?<=\S)__/g, '<strong>$1</strong>');
    s = s.replace(/(^|[^\w*])\*(?=\S)(.+?)(?<=\S)\*(?![\w*])/g, '$1<em>$2</em>');
    s = s.replace(/\*\*(?=\S)([^*]*)$/, '<strong>$1</strong>');
    s = s.replace(/\u0000(\d+)\u0000/g, (_, i) => `<code>${codes[+i]}</code>`);
    return s;
  }
  const isTableRow = line => /^\s*\|.*\|\s*$/.test(line);
  const isDivider = line => /^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$/.test(line);
  const isList = line => /^\s*([-*+]|\d{1,3}[.)])\s+/.test(line);
  function blocks(md) {
    const lines = String(md || '').replace(/\r\n?/g, '\n').split('\n');
    const out = [];
    let i = 0;
    while (i < lines.length) {
      const line = lines[i];
      if (!line.trim()) { i += 1; continue; }
      if (/^\s{0,3}#{1,6}\s/.test(line) || /^\s{0,3}([-*_]\s*){3,}$/.test(line)) { out.push(line); i += 1; continue; }
      const take = test => { const start = i; while (i < lines.length && lines[i].trim() && test(lines[i])) i += 1; out.push(lines.slice(start, i).join('\n')); };
      if (isTableRow(line)) { take(isTableRow); continue; }
      if (isList(line)) { take(l => isList(l) || /^\s{2,}\S/.test(l)); continue; }
      take(l => !(/^\s{0,3}#{1,6}\s/.test(l) || isTableRow(l) || isList(l) || /^\s{0,3}([-*_]\s*){3,}$/.test(l)));
    }
    return out;
  }
  function renderBlock(text, complete) {
    const head = /^\s{0,3}(#{1,6})\s+(.*)$/.exec(text);
    if (head) { const level = Math.min(head[1].length, 4); return `<h${level}>${inline(head[2])}</h${level}>`; }
    if (/^\s{0,3}([-*_]\s*){3,}$/.test(text)) return '<hr>';
    const lines = text.split('\n');
    if (isTableRow(lines[0])) {
      let rows = lines.filter(l => !isDivider(l));
      if (!complete && !/\|\s*$/.test(lines[lines.length - 1])) rows = rows.slice(0, -1);
      if (!complete && rows.length && !isTableRow(lines[lines.length - 1])) rows = rows.slice(0, -1);
      const cells = l => l.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(c => inline(c.trim()));
      if (!rows.length) return '';
      const [first, ...rest] = rows;
      return `<table><thead><tr>${cells(first).map(c => `<th>${c}</th>`).join('')}</tr></thead><tbody>${
        rest.map(r => `<tr>${cells(r).map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
    }
    if (isList(lines[0])) {
      const ordered = /^\s*\d/.test(lines[0]);
      const items = [];
      for (const line of lines) {
        const m = /^(\s*)([-*+]|\d{1,3}[.)])\s+(.*)$/.exec(line);
        if (m) items.push({depth: m[1].length >= 2 ? 1 : 0, text: m[3]});
        else if (items.length) items[items.length - 1].text += ' ' + line.trim();
      }
      let html = `<${ordered ? 'ol' : 'ul'}>`, depth = 0;
      for (const item of items) {
        if (item.depth > depth) { html = html.replace(/<\/li>$/, '') + '<ul>'; depth = 1; }
        else if (item.depth < depth) { html += '</ul></li>'; depth = 0; }
        html += `<li>${inline(item.text)}</li>`;
      }
      if (depth) html += '</ul></li>';
      return html + `</${ordered ? 'ol' : 'ul'}>`;
    }
    return `<p>${lines.map(line => inline(line.trim())).join('<br>')}</p>`;
  }
  function markdown(md) { return blocks(md).map(b => renderBlock(b, true)).join(''); }

  async function fontCheck() {
    try {
      await Promise.all(['400 13px "Segoe UI"', '600 13px "Segoe UI"'].map(f => document.fonts.load(f, 'Message')));
      await document.fonts.ready;
    } catch (_) { /* a face that failed to load stays 'error' below */ }
    const faces = [...document.fonts].filter(f => f.family.replace(/["']/g, '') === 'Segoe UI');
    const loaded = w => faces.some(f => String(f.weight) === w && f.status === 'loaded');
    return {font: loaded('400') && loaded('600') ? 'segoe' : 'missing'};
  }

  function mount(host, options = {}) {
    const name = String(options.name || 'Copilot');
    const zoom = Number(options.zoom) || 1;
    const talk = {asked: 0, answered: 0, failed: 0, thinking: false, streaming: false, history: [], abort: null};

    const root = el('div', {class: 'm365', 'data-look': 'm365', style: `--m-zoom:${zoom}`});
    if (zoom !== 1) document.body.style.zoom = String(zoom);
    const initials = options.initials === '' ? '' : String(options.initials || 'KW').trim().slice(0, 2).toUpperCase() || 'KW';
    const rail = el('nav', {class: 'm365-rail', 'aria-label': 'Navigation'},
      button('Copilot', ICONS.logo(), 'm365-ic m365-logo'), button('New chat', ICONS.compose()), button('Search', ICONS.search()),
      button('Library', ICONS.library()), el('span', {class: 'm365-me', 'aria-hidden': 'true', text: initials}));
    const top = el('div', {class: 'm365-top'}, button('Protected', ICONS.shield(), 'm365-ic m365-shield'),
      button('New chat', ICONS.compose(), 'm365-ic', {'data-when': 'chat'}), button('More options', ICONS.more()));

    const input = el('input', {class: 'm365-input', type: 'text', 'aria-label': 'Message ' + name, placeholder: 'Message ' + name,
      autocomplete: 'off', spellcheck: 'false', 'data-control': 'm365-composer'});
    const go = el('button', {type: 'button', class: 'm365-go', 'aria-label': 'Send', 'data-control': 'm365-send'},
      ICONS.arrow(), el('span', {class: 'm365-stop'}));
    const composer = el('div', {class: 'm365-composer', 'data-mode': 'idle'}, ICONS.plus(),
      el('span', {class: 'm365-field'}, input, el('span', {class: 'm365-caret', 'aria-hidden': 'true'})),
      el('span', {class: 'm365-mic'}, ICONS.mic()), go);

    const starters = (Array.isArray(options.starters) ? options.starters : []).slice(0, 3);
    const cards = starters.length ? el('div', {class: 'm365-cards'}, starters.map(s => el('button', {type: 'button', class: 'm365-card'},
      el('div', {class: 'm365-card-title'}, ICONS.chat(), el('span', {text: shortTitle(s.title || s.text || '')})),
      el('div', {class: 'm365-card-text', text: s.text || s.title || ''})))) : null;
    const earlier = [];
    for (const text of [...(Array.isArray(options.suggestions) ? options.suggestions : []), ...starters.map(s => s.text || s.title || '')]) {
      const line = String(text || '').replace(/\s+/g, ' ').trim();
      if (line && !earlier.includes(line)) earlier.push(line);
    }
    const typeahead = el('ul', {class: 'm365-typeahead', role: 'listbox', 'aria-label': 'Suggestions'});
    const hero = el('section', {class: 'm365-hero'},
      el('div', {class: 'm365-hero-id'}, tile(28), el('div', {class: 'm365-hero-name', text: name}),
        el('div', {class: 'm365-hero-by'}, 'Created by ', el('b', {text: options.createdBy || 'Your developer name'}))),
      composer, typeahead, cards,
      cards && el('div', {class: 'm365-more-starters'}, 'Show more', ICONS.chevron()));
    const col = el('div', {class: 'm365-col'});
    const main = el('main', {class: 'm365-main'}, hero, col);
    const down = button('Scroll to the bottom', ICONS.down(), 'm365-down');
    const dock = el('div', {class: 'm365-dock'}, el('div', {class: 'm365-note', text: DISCLAIMER}));
    const thumb = el('div', {class: 'm365-thumb', 'aria-hidden': 'true'});
    const page = el('div', {class: 'm365-page'}, top, main, down, dock, thumb);
    root.append(rail, page);
    host.replaceChildren(root);

    const atBottom = () => main.scrollHeight - main.scrollTop - main.clientHeight < 6;
    const showDown = () => down.classList.toggle('m365-show', !atBottom() && root.classList.contains('m365-chatting'));
    main.addEventListener('scroll', showDown);
    let thumbTimer = null;
    main.addEventListener('scroll', () => {
      const total = main.scrollHeight, view = main.clientHeight;
      if (total - view < 2) return;
      const track = view - THUMB_FOOT;
      const length = Math.max(24, track * view / total);
      thumb.style.height = length + 'px';
      thumb.style.top = (main.offsetTop + (track - length) * main.scrollTop / (total - view)) + 'px';
      thumb.classList.add('m365-show');
      clearTimeout(thumbTimer);
      thumbTimer = setTimeout(() => thumb.classList.remove('m365-show'), THUMB_HOLD_MS);
    });
    const growth = new ResizeObserver(showDown);
    growth.observe(col);
    down.addEventListener('click', () => main.scrollTo({top: main.scrollHeight, behavior: 'smooth'}));

    const mode = () => (talk.thinking || talk.streaming ? 'stop' : input.value.trim() ? 'send' : 'idle');
    const sync = () => {
      composer.dataset.mode = mode();
      go.setAttribute('aria-label', composer.dataset.mode === 'stop' ? 'Stop' : 'Send');
    };
    input.addEventListener('input', sync);
    let suggestTimer = null, suggestFrom = 0;
    const suggest = () => {
      const typed = input.value.trim();
      const matches = typed ? earlier.filter(line => line[0].toLowerCase() === typed[0].toLowerCase()).slice(0, SUGGEST_MAX) : [];
      typeahead.replaceChildren(...matches.map(line => el('li', {role: 'option'}, el('b', {text: line[0]}),
        line.length > SUGGEST_CUT ? line.slice(1, SUGGEST_CUT) + '...' : line.slice(1))));
      hero.classList.toggle('m365-suggesting', matches.length > 0);
    };
    input.addEventListener('input', () => {
      if (root.classList.contains('m365-chatting')) return;
      if (!input.value.trim()) { clearTimeout(suggestTimer); suggestTimer = null; suggestFrom = 0; suggest(); return; }
      if (!suggestFrom) suggestFrom = Date.now();
      if (hero.classList.contains('m365-suggesting') || Date.now() - suggestFrom >= SUGGEST_MS) { suggest(); return; }
      clearTimeout(suggestTimer);
      suggestTimer = setTimeout(suggest, SUGGEST_MS - (Date.now() - suggestFrom));
    });
    const caret = composer.querySelector('.m365-caret');
    const measure = document.createElement('canvas').getContext('2d');
    const placeCaret = () => {
      measure.font = getComputedStyle(input).font;
      const end = input.value ? measure.measureText(input.value).width - input.scrollLeft - .8 : 0;
      caret.style.left = (11 + Math.max(0, Math.min(end, input.clientWidth))) + 'px';
      caret.style.animation = 'none'; void caret.offsetWidth; caret.style.animation = '';
    };
    input.addEventListener('input', placeCaret);
    input.addEventListener('focus', () => { composer.dataset.focus = '1'; placeCaret(); });
    input.addEventListener('blur', () => { delete composer.dataset.focus; });
    input.addEventListener('keydown', event => {
      if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); send(input.value); }
    });
    go.addEventListener('click', () => (talk.thinking || talk.streaming ? stop() : send(input.value)));
    if (cards) [...cards.children].forEach((card, i) => card.addEventListener('click', () => send(starters[i].text || starters[i].title)));

    function stop() { if (talk.abort) talk.abort(); }
    function shortTitle(title) { title = String(title).trim(); return title.length > TITLE_MAX ? title.slice(0, 18) + '...' : title; }
    const wait = ms => new Promise(resolve => setTimeout(resolve, ms));

    async function stream(target, md, abandoned, onFirst) {
      const parts = blocks(md);
      const chunk = Math.round(STREAM_CPS * TICK_MS / 1000);
      let first = true;
      for (const part of parts) {
        const holder = el('div', {class: 'm365-block'});
        target.append(holder);
        let shown = 0;
        while (shown < part.length) {
          if (abandoned()) return false;
          let next = Math.min(part.length, shown + chunk);
          const line = part.indexOf('\n', next);
          if (line !== -1 && line - next < chunk / 2) next = line;
          while (next < part.length && !/\s/.test(part[next])) next += 1;
          shown = next;
          holder.innerHTML = renderBlock(part.slice(0, shown), shown >= part.length);
          if (first) { first = false; onFirst(); }
          await wait(TICK_MS);
        }
      }
      return true;
    }

    async function send(text) {
      const question = String(text || '').trim();
      if (!question || talk.thinking || talk.streaming) return null;
      input.value = '';
      if (!root.classList.contains('m365-chatting')) {
        clearTimeout(suggestTimer);
        root.classList.add('m365-chatting');
        dock.prepend(composer);
      }
      input.focus({preventScroll: true});
      composer.dataset.focus = '1'; placeCaret();
      talk.asked += 1;
      const turn = el('section', {class: 'm365-turn', 'data-turn': String(talk.asked)});
      const glyph = ICONS.bars();
      const status = el('div', {class: 'm365-status', role: 'status'}, el('span', {class: 'm365-glyph'}, glyph), el('span', {text: THINKING}));
      const body = el('div', {class: 'm365-md'});
      const agent = el('article', {class: 'm365-agent m365-thinking'},
        el('div', {class: 'm365-head'}, tile(20), el('span', {class: 'm365-name', text: name})), status, body);
      turn.append(el('div', {class: 'm365-user'}, el('p', {text: question})), agent);
      for (const earlier of col.querySelectorAll('.m365-turn')) earlier.style.minHeight = '';
      col.append(turn);
      const colStyle = getComputedStyle(col);
      const padTop = parseFloat(colStyle.paddingTop) || 0;
      const natural = main.scrollHeight - main.clientHeight;
      turn.style.minHeight = Math.max(0, main.clientHeight - padTop - (parseFloat(colStyle.paddingBottom) || 0)) + 'px';
      main.scrollTop = Math.max(0, natural);
      const pin = () => { main.scrollTop = turn.offsetTop - padTop; showDown(); };
      talk.thinking = true; sync(); showDown();
      animateGlyph(glyph, () => talk.thinking);
      let cancelled = false;
      talk.abort = () => { cancelled = true; };
      let answer = null, failed = false;
      try {
        answer = await options.ask(question, talk.history.slice());
        if (typeof answer !== 'string' || !answer.trim()) failed = true;
      } catch (_) { failed = true; }
      talk.thinking = false;
      agent.classList.remove('m365-thinking');
      if (cancelled) { talk.abort = null; sync(); return null; }
      if (failed) {
        body.innerHTML = '<p>Sorry, something went wrong. Please try again.</p>';
        talk.failed += 1; talk.abort = null; sync();
        return null;
      }
      talk.streaming = true; sync();
      await wait(HEAD_ONLY_MS);
      const done = await stream(body, answer, () => cancelled, pin);
      talk.streaming = false; talk.abort = null;
      showDown();
      if (done) {
        agent.append(el('div', {class: 'm365-actions m365-fresh'}, button('Copy', ICONS.copy()), button('Like', ICONS.like()),
          button('Dislike', ICONS.dislike()), button('More', ICONS.more())));
        talk.history.push({role: 'user', text: question}, {role: 'agent', text: answer});
        talk.answered += 1;
      }
      sync();
      input.focus({preventScroll: true});
      composer.dataset.focus = '1';
      return answer;
    }

    const ready = fontCheck().then(found => { root.dataset.font = found.font; return found; });
    const chat = {
      root, main, input, ready, send,
      state: () => ({asked: talk.asked, answered: talk.answered, failed: talk.failed, thinking: talk.thinking,
        streaming: talk.streaming, atBottom: atBottom(), text: main.innerText}),
    };
    return chat;
  }

  window.RappM365 = {mount, markdown, blocks};
})();
