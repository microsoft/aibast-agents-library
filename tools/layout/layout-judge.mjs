// Layout judge: node tools/layout/layout-judge.mjs <site-base-url> <outdir>
// Sample pages at 1440 and 390: own consistency checks plus a side-by-side against the live Copilot Studio Gallery layout.
// A blank band over 16px under the home demo costs a point.
import { chromium } from 'playwright';
import fs from 'fs';
const B = process.argv[2];
if (!B) { console.error('usage: node tools/layout/layout-judge.mjs <site-base-url> <outdir>'); process.exit(2); }
const OUT = process.argv[3] || 'shots';
fs.mkdirSync(OUT, { recursive: true });
const G = 'https://microsoft.github.io/copilot-studio-gallery/';
const PAGES = {
  home: 'index.html', sol1: 'solution.html?id=account-intelligence', sol2: 'solution.html?id=ask-hr',
  sol3: 'solution.html?id=ai-customer-assistant', prepare: 'prepare.html', installer: 'docs/installer.html',
  why: 'why.html', blog: 'blog.html', metrics: 'metrics.html', guide: 'docs/rapp-guide.html',
};
const GPAGES = { home: '', detail: 'solutions/contract-compliance-reviewer' };
const WIDTHS = [1440, 390];

const measure = () => {
  const vw = innerWidth, vh = innerHeight;
  const vis = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const header = [...document.querySelectorAll('header, [role=banner], nav, .topbar')].filter(vis)[0];
  const hr = header ? header.getBoundingClientRect() : null;
  const footer = [...document.querySelectorAll('footer, [role=contentinfo]')].filter(vis)[0];
  const main = document.querySelector('main, [role=main]') || document.body;
  // content width: widest block of text paragraphs' container
  // Centered text (a hero, like the gallery's) has no left edge to compare, so it is left out.
  const ps = [...main.querySelectorAll('p, h1, h2')].filter(vis).filter(e => getComputedStyle(e).textAlign !== 'center').slice(0, 40);
  const lefts = ps.map(p => Math.round(p.getBoundingClientRect().left));
  // The content edge is the leftmost text block (cards in a grid sit to the right of it).
  const contentLeft = lefts.length ? Math.min(...lefts) : 0;
  const h1 = [...document.querySelectorAll('h1')].filter(vis)[0];
  const actions = [...document.querySelectorAll('a, button')].filter(vis).filter(e => {
    const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
    const bg = s.backgroundColor; return r.top < vh && r.bottom > 0 && bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent' && r.width >= 60;
  });
  const taps = [...document.querySelectorAll('a, button, input, select, textarea')].filter(vis).filter(e => {
    const r = e.getBoundingClientRect(); return r.top < vh * 3 && !(e.closest('p, li') && e.tagName === 'A');
  });
  const small = taps.filter(e => { const r = e.getBoundingClientRect(); return r.height < 44 && r.width < 44 || r.height < 24; }).length;
  // cards: repeated siblings with same width in a row
  let cols = 0, gap = 0;
  const grids = [...document.querySelectorAll('*')].filter(e => { const s = getComputedStyle(e); return (s.display === 'grid' || s.display === 'flex' && s.flexWrap === 'wrap') && e.children.length >= 3 && vis(e); });
  for (const g of grids) {
    const kids = [...g.children].filter(vis).slice(0, 12); if (kids.length < 3) continue;
    const top = Math.round(kids[0].getBoundingClientRect().top);
    const row = kids.filter(k => Math.abs(k.getBoundingClientRect().top - top) < 4);
    if (row.length >= 2 && row[0].getBoundingClientRect().height > 120 && row.length > cols) {
      cols = row.length; gap = Math.round(row[1].getBoundingClientRect().left - row[0].getBoundingClientRect().right);
    }
  }
  // Bars: full-width header rows with their own background or bottom border (the gallery has one).
  const bars = [...document.querySelectorAll('header, .topbar')].filter(vis).filter(e => {
    const r = e.getBoundingClientRect(), st = getComputedStyle(e);
    const opaque = st.backgroundColor !== 'rgba(0, 0, 0, 0)' && st.backgroundColor !== 'transparent';
    return r.top < 200 && r.width > vw * 0.9 && (opaque || parseFloat(st.borderBottomWidth) > 0);
  }).length;
  const shortFooterLinks = [...document.querySelectorAll('.site-footer a')].filter(vis).filter(e => e.getBoundingClientRect().height < 44).length;
  const hasSearch = !![...document.querySelectorAll('input[type=search], input[placeholder*=earch i]')].filter(vis).length;
  return {
    hscroll: document.documentElement.scrollWidth > vw + 1,
    headerH: hr ? Math.round(hr.height) : 0, headerTop: hr ? Math.round(hr.top) : -1,
    headerSticky: header ? ['sticky', 'fixed'].includes(getComputedStyle(header).position) : false,
    footer: !!footer, contentLeft, h1Top: h1 ? Math.round(h1.getBoundingClientRect().top) : -1,
    shortFooterLinks, bars, primaryAbove: actions.length, smallTaps: small, tapCount: taps.length, cols, gap, hasSearch,
  };
};

const b = await chromium.launch({ channel: 'chrome' }).catch(() => chromium.launch());
async function run(base, pages, tag) {
  const res = {};
  for (const w of WIDTHS) {
    const c = await b.newContext({ viewport: { width: w, height: w > 500 ? 900 : 844 } });
    const p = await c.newPage();
    let errors = [];
    p.on('pageerror', e => errors.push(String(e)));
    for (const [k, path] of Object.entries(pages)) {
      try {
        errors = [];
        await p.goto(base + path, { waitUntil: 'load', timeout: 60000 });
        await p.waitForTimeout(2500);
        res[`${k}@${w}`] = await p.evaluate(measure);
        res[`${k}@${w}`].errors = errors.length;
        if (k === 'home') res[`${k}@${w}`].cards = await p.locator('#grid > :not(.loading)').count();
        if (k === 'home') {
          // Blank band under the featured demo: frame height minus the demo stage and caption bottom.
          const f = p.frame({ url: /m365-copilot-demo/ });
          res[`${k}@${w}`].band = f ? await f.evaluate(() => {
            const st = document.getElementById('stage'), cap = document.getElementById('caption');
            const bottom = Math.max(st ? st.getBoundingClientRect().bottom : 0, cap ? cap.getBoundingClientRect().bottom : 0);
            return Math.round(innerHeight - bottom);
          }).catch(() => null) : null;
        }
        await p.screenshot({ path: `${OUT}/${tag}-${k}-${w}.png` });
      } catch (e) { res[`${k}@${w}`] = { error: String(e).slice(0, 120) }; }
    }
    await c.close();
  }
  return res;
}
const ours = await run(B, PAGES, 'ours');
const gal = await run(G, GPAGES, 'gallery');
await b.close();

// Scoring: each page/width out of 10.
const score = {}; let total = 0, max = 0; const fails = [];
const headerHs = {}, lefts = {};
for (const w of WIDTHS) {
  headerHs[w] = Object.keys(PAGES).map(k => ours[`${k}@${w}`]?.headerH).filter(Boolean);
  lefts[w] = Object.keys(PAGES).map(k => ours[`${k}@${w}`]?.contentLeft).filter(x => x != null);
}
const med = a => [...a].sort((x, y) => x - y)[Math.floor(a.length / 2)] || 0;
for (const w of WIDTHS) for (const k of Object.keys(PAGES)) {
  const m = ours[`${k}@${w}`]; const g = gal[`${k === 'home' ? 'home' : k.startsWith('sol') ? 'detail' : 'home'}@${w}`];
  let s = 0; const why = [];
  const chk = (ok, label) => { if (ok) s++; else why.push(label); };
  if (m.error) { score[`${k}@${w}`] = 0; total += 0; max += 10; fails.push(`${k}@${w}: error`); continue; }
  chk(!m.hscroll, 'hscroll');
  chk(m.headerH > 0 && m.headerTop <= 1, 'no top header');
  chk(Math.abs(m.headerH - med(headerHs[w])) <= 8, `header height ${m.headerH} vs site ${med(headerHs[w])}`);
  chk(m.footer, 'no footer');
  if (w < 500 && m.shortFooterLinks) { why.push(`${m.shortFooterLinks} footer links under 44px`); s--; }
  if (m.errors) { why.push(`${m.errors} page errors`); s -= 2; }
  if (k === 'home' && !(m.cards >= 1)) { why.push('home shows no solution cards'); s -= 3; }
  if (m.bars > 1) { why.push(`${m.bars} header bars`); s--; }
  chk(Math.abs(m.contentLeft - med(lefts[w])) <= 24, `content left ${m.contentLeft} vs site ${med(lefts[w])}`);
  chk(m.primaryAbove >= 1, 'no primary action above fold');
  chk(w > 500 || m.smallTaps <= 2, `small taps ${m.smallTaps}`);
  // gallery comparison
  chk(g && Math.abs(m.headerH - g.headerH) <= 16, `header ${m.headerH} vs gallery ${g?.headerH}`);
  chk(g && m.headerSticky === g.headerSticky, `sticky ${m.headerSticky} vs gallery ${g?.headerSticky}`);
  if (k === 'home' && m.band != null && m.band > 16) why.push(`demo blank band ${m.band}px`), s--;
  if (k === 'home') chk(g && m.cols === g.cols && m.hasSearch === g.hasSearch, `cards ${m.cols} cols search ${m.hasSearch} vs gallery ${g?.cols}/${g?.hasSearch}`);
  else {
    // Graded, not pass/fail: full credit within 80px of the gallery, then it falls off over the next 200px,
    // so moving a heading closer always counts even before it is inside the window.
    const d = g ? Math.abs(m.h1Top - g.h1Top) : Infinity;
    const credit = d <= 80 ? 1 : Math.max(0, 1 - (d - 80) / 200);
    s += Math.round(credit * 10) / 10;
    if (credit < 1) why.push(`h1 top ${m.h1Top} vs gallery ${g?.h1Top}`);
  }
  score[`${k}@${w}`] = s; total += s; max += 10; if (why.length) fails.push(`${k}@${w}: ${why.join('; ')}`);
}
const report = { total, max, score, fails, ours, gallery: gal };
fs.writeFileSync(`${OUT}/report.json`, JSON.stringify(report, null, 1));
total = Math.round(total * 10) / 10;
console.log(`SCORE ${total}/${max}`); console.log(fails.join('\n'));
