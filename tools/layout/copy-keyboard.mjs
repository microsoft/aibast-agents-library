// Copy lines on solution.html: Tab reaches each one and Enter copies its command. node tools/layout/copy-keyboard.mjs <site-base-url>
import { chromium } from 'playwright';
const B=process.argv[2];
const b=await chromium.launch({channel:'chrome'}).catch(()=>chromium.launch());
const c=await b.newContext({viewport:{width:390,height:844}}); await c.grantPermissions(['clipboard-read','clipboard-write'],{origin:new URL(B).origin});
const p=await c.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(String(e)));
await p.goto(B+'solution.html?id=account-intelligence',{waitUntil:'load'}); await p.waitForSelector('.cmd',{timeout:30000});
const n=await p.locator('.cmd').count(); const sizes=await p.locator('.cmd').evaluateAll(a=>a.map(e=>Math.round(e.getBoundingClientRect().height)));
let reached=0, copied=0;
for(let i=0;i<120;i++){await p.keyboard.press('Tab'); const isCmd=await p.evaluate(()=>document.activeElement?.classList.contains('cmd'));
 if(isCmd){reached++; const want=await p.evaluate(()=>document.activeElement.querySelector('code').textContent); await p.keyboard.press('Enter'); await p.waitForTimeout(300);
  const got=await p.evaluate(()=>navigator.clipboard.readText()); if(got===want) copied++; if(reached>=n) break;}}
console.log(JSON.stringify({lines:n, heights:sizes, reachedByTab:reached, enterCopied:copied, errors:errs.length})); await b.close();
