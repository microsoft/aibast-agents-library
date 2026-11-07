// Play a solution's demo narration in a real browser and check every clip.
// Usage: node narration-playback.mjs <site base URL> <surface> <solution slug>
// Prints one JSON line: {slug, surface, steps, passed, errors, rows}. A clip passes when it plays
// in order, from the raw base, for its full duration (within 400 ms), with its own captions.
import { chromium } from 'playwright';

const [base, surface = 'm365', slug] = process.argv.slice(2);
if (!base || !slug) { console.error('usage: node narration-playback.mjs <base> <surface> <slug>'); process.exit(2); }
const site = base.replace(/\/?$/, '/');
// Network reads from Node are retried: one dropped request must not end the whole run.
async function getJSON(url) {
  let last;
  for (let i = 0; i < 3; i += 1) {
    try { const r = await fetch(url); if (r.ok) return await r.json(); last = new Error(`${url} returned ${r.status}`); }
    catch (e) { last = e; }
    await new Promise((done) => setTimeout(done, 1500 * (i + 1)));
  }
  throw last;
}
// Any failure still prints one JSON line, with the reason, so a crash is never silent or unexplained.
process.on('unhandledRejection', (e) => { console.log(JSON.stringify({ slug, surface, crash: String(e && e.stack || e).split('\n')[0] })); process.exit(1); });
const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
let result;
try {
  const page = await browser.newPage({ viewport: { width: 1512, height: 980 } });
  const errors = []; page.on('pageerror', (e) => errors.push(String(e)));
  const solution = await getJSON(`${site}api/v1/solutions/${slug}.json`);
  const recorded = solution.try.scenarios.filter((s) => s.doc).map((s) => s.id);
  await page.goto(`${site}solutions/_shared/m365-copilot-demo.html?scenario=${recorded[0]}&surface=${surface}`);
  await page.locator('#aibast-clarity-consent button', { hasText: 'Decline' }).click({ timeout: 3000 }).catch(() => {});
  await page.waitForFunction(() => /of/.test(document.getElementById('step').textContent));
  await page.click('#play');
  await page.waitForFunction(() => document.body.dataset.phase === 'end', null, { timeout: 360000 });
  await page.waitForTimeout(4500);
  const log = await page.evaluate(() => window.__narration);
  const want = [];
  for (const id of recorded) {
    const doc = await getJSON(`${site}api/v1/scenarios/${id}.json`);
    for (const seg of (doc.narration && doc.narration.segments) || []) {
      want.push([seg.id, seg.media.durationMs, seg.captions.segments.map((c) => c.text)]);
    }
  }
  let passed = 0; const rows = [];
  want.forEach(([id, dur, caps], i) => {
    const got = log.find((l) => l.id === id);
    const ok = got && Math.abs(got.playedMs - dur) <= 400 && JSON.stringify(got.captions) === JSON.stringify(caps)
      && log.indexOf(got) === i && got.source === 'raw';
    if (ok) passed += 1;
    rows.push({ id, dur, played: got && got.playedMs, source: got && got.source, ok: !!ok });
  });
  result = { slug, surface, steps: want.length, passed, errors: errors.length, rows };
} catch (e) {
  result = { slug, surface, crash: String(e && e.message || e).split('\n')[0] };
} finally {
  await browser.close();
}
console.log(JSON.stringify(result));
process.exit(result.crash ? 1 : 0);
