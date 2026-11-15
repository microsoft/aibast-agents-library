// Full crawl gate: node tools/layout/layout-crawl.mjs <site-base-url> tools/layout/crawl-pages.txt [width]  (needs playwright)
// For every HTML page: no horizontal scroll, the shared frame header present at the top, a footer present.
import { chromium } from 'playwright';
import fs from 'fs';
const [B, LIST, W = '390'] = process.argv.slice(2);
const pages = fs.readFileSync(LIST, 'utf8').split('\n').filter(Boolean);
const b = await chromium.launch({ channel: 'chrome' }).catch(() => chromium.launch());
const c = await b.newContext({ viewport: { width: +W, height: 844 } });
const res = { ok: 0, fail: {} };
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
      }));
      const bad = [];
      if (m.redirect) { res.ok++; continue; }
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
console.log(`CRAWL ${res.ok}/${pages.length} pass at ${W}px`, JSON.stringify(counts), `pages with two header bars: ${res.doubleBars || 0}`);
