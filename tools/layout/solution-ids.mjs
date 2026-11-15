// Every library slug opens its own solution page: node tools/layout/solution-ids.mjs <site-base-url> api/v1/search.json
import { chromium } from 'playwright'; import fs from 'fs';
const [B, SEARCH] = process.argv.slice(2);
const list = JSON.parse(fs.readFileSync(SEARCH,'utf8')).solutions;
const b=await chromium.launch({channel:'chrome'}).catch(()=>chromium.launch());
const p=await (await b.newContext()).newPage(); const bad=[];
for (const s of list){ await p.goto(`${B}solution.html?id=${s.slug}`,{waitUntil:'load'}); await p.waitForFunction(()=>document.querySelector('h1')||document.querySelector('.empty'),null,{timeout:20000}).catch(()=>{});
  await p.waitForSelector('dd.mono',{timeout:30000}).catch(()=>{});
  const want=JSON.parse(fs.readFileSync(SEARCH.replace('search.json','')+'solutions/'+s.slug+'.json','utf8')).id;
  const h=await p.evaluate(()=>(document.querySelector('dd.mono')||{}).textContent||'none');
  if(h.trim()!==want) bad.push([s.slug,want,h.trim()]); }
await p.goto(`${B}solution.html?id=no-such-thing`,{waitUntil:'load'}); await p.waitForTimeout(1500);
const nf=await p.evaluate(()=>document.body.innerText.includes('No solution called'));
console.log(`IDS ${list.length-bad.length}/${list.length} show their own record; unknown id message: ${nf}`); console.log(JSON.stringify(bad.slice(0,10)));
await b.close();
