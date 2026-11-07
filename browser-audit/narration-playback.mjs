// Play a solution's demo narration in a real browser and check every clip.
// Usage: node narration-playback.mjs <site base URL> <surface> <solution slug>
// Prints one JSON line: {slug, surface, steps, passed, errors, rows}. A clip passes when it plays
// in order, from the raw base, for its full duration (within 400 ms), with its own captions.
import { chromium } from 'playwright';

const [base, surface = 'm365', slug] = process.argv.slice(2);
if (!base || !slug) { console.error('usage: node narration-playback.mjs <base> <surface> <slug>'); process.exit(2); }
const site = base.replace(/\/?$/, '/');
const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
try {
  const page = await browser.newPage({ viewport: { width: 1512, height: 980 } });
  const errors = []; page.on('pageerror', (e) => errors.push(String(e)));
  const solution = await (await fetch(`${site}api/v1/solutions/${slug}.json`)).json();
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
    const doc = await (await fetch(`${site}api/v1/scenarios/${id}.json`)).json();
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
  console.log(JSON.stringify({ slug, surface, steps: want.length, passed, errors: errors.length, rows }));
} finally {
  await browser.close();
}
