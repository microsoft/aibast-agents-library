// Full crawl gate: node tools/layout/layout-crawl.mjs <site-base-url> tools/layout/crawl-pages.txt [width]  (needs playwright)
// For every HTML page: no horizontal scroll, the shared frame header present at the top, a footer present.
// LOOK line: every page against the gallery's look (plain background, hero size, flat cards, one pill row, text size).
import { chromium } from 'playwright';
import fs from 'fs';
const [B, LIST, W = '390'] = process.argv.slice(2);
const pages = fs.readFileSync(LIST, 'utf8').split('\n').filter(Boolean);
const b = await chromium.launch({ channel: 'chrome' }).catch(() => chromium.launch());
const c = await b.newContext({ viewport: { width: +W, height: 844 } });
const res = { ok: 0, fail: {}, lookOk: 0, lookFail: {} };
const N = 8; let i = 0;
async function worker() {
  const p = await c.newPage();
  while (i < pages.length) {
    const path = pages[i++];
    try {
      await p.goto(B + path, { waitUntil: 'load', timeout: 30000 });
      await p.waitForTimeout(600);
      const m = await p.evaluate(() => ({
        hscroll: document.documentElement.scrollWidth > innerWidth + 1,
        shell: !!document.querySelector('header.site-shell'),
        footer: !!document.querySelector('footer'),
        redirect: !!document.querySelector('meta[http-equiv=refresh i]'),
        // Header rows that read as a second bar: near full width, near the top, with their own fill or rule.
        bars: [...document.querySelectorAll('header, .topbar')].filter(e => {
          const r = e.getBoundingClientRect(), st = getComputedStyle(e);
          const fill = st.backgroundColor !== 'rgba(0, 0, 0, 0)' && st.backgroundColor !== 'transparent';
          return r.height > 0 && r.top < 220 && r.width > innerWidth * 0.8 && (fill || parseFloat(st.borderBottomWidth) > 0 || st.boxShadow !== 'none');
        }).length,
        // LOOK, against the gallery: plain background, hero within the gallery's size and weight,
        // flat cards (gallery: 16px radius, 1px border, no shadow), at most one pill row, readable body text.
        look: (() => {
          const vis = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
          const bad = [];
          const bgs = [document.documentElement, document.body, ...document.querySelectorAll('body > *:not(script):not(style)')].slice(0, 12)
            .map(e => getComputedStyle(e).backgroundImage).filter(x => x && x !== 'none');
          if (bgs.some(x => (x.includes('gradient') && /\b1px\b/.test(x)) || /url\(/.test(x) || /repeating-/.test(x))) bad.push('pattern');
          const h1 = [...document.querySelectorAll('h1')].find(vis);
          if (h1) { const st = getComputedStyle(h1); if (parseFloat(st.fontSize) > 52 * innerWidth / 1440 + 8 || +st.fontWeight > 700) bad.push('hero'); }
          const cards = [...document.querySelectorAll('main *, body > div *, body > section *')].filter(e => {
            const st = getComputedStyle(e), r = e.getBoundingClientRect();
            return vis(e) && !e.closest('.site-shell') && parseFloat(st.borderTopLeftRadius) > 4 && parseFloat(st.borderTopWidth) > 0 && r.width > 180 && r.height > 80;
          }).slice(0, 30);
          if (cards.some(e => { const st = getComputedStyle(e); return st.boxShadow !== 'none' || parseFloat(st.borderTopLeftRadius) > 20; })) bad.push('card');
          if (!document.querySelector('#sidebar')) {
            const rows = [...document.querySelectorAll('header:not(.site-shell), .topbar, body > nav, main > nav')].filter(e => vis(e) && !e.closest('.site-shell') && e.querySelectorAll('a, button').length >= 3);
            if (rows.length > 1) bad.push('pills');
          }
          const ps = [...document.querySelectorAll('p')].filter(vis).slice(0, 20).map(e => parseFloat(getComputedStyle(e).fontSize)).sort((x, y) => x - y);
          if (ps.length && ps[Math.floor(ps.length / 2)] < 12) bad.push('small-text');
          return bad;
        })(),
      }));
      const bad = [];
      if (m.redirect) { res.ok++; res.lookOk++; continue; }
      if (m.look.length) { res.lookFail[path] = m.look; } else res.lookOk++;
      if (m.bars > 1) res.doubleBars = (res.doubleBars || 0) + 1;
      if (m.hscroll) bad.push('hscroll'); if (!m.shell) bad.push('no-frame'); if (!m.footer) bad.push('no-footer');
      if (bad.length) res.fail[path] = bad; else res.ok++;
    } catch (e) { res.fail[path] = ['error']; }
  }
}
await Promise.all(Array.from({ length: N }, worker));
await b.close();
const counts = {};
for (const v of Object.values(res.fail)) for (const k of v) counts[k] = (counts[k] || 0) + 1;
if (process.env.CRAWL_OUT) fs.writeFileSync(process.env.CRAWL_OUT, JSON.stringify(res, null, 1));
const lc = {};
for (const v of Object.values(res.lookFail)) for (const k of v) lc[k] = (lc[k] || 0) + 1;
console.log(`LOOK ${res.lookOk}/${pages.length} pass at ${W}px`, JSON.stringify(lc));
console.log(`CRAWL ${res.ok}/${pages.length} pass at ${W}px`, JSON.stringify(counts), `pages with two header bars: ${res.doubleBars || 0}`);
