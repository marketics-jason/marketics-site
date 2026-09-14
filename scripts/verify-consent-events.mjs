/* Requires Playwright, which this repo deliberately does NOT depend on -- there
   is no package.json and no build step (see netlify.toml [functions]). Run it
   against an install elsewhere:

     NODE_PATH=/path/to/node_modules node --input-type=module \
       -e "$(cat scripts/verify-consent-events.mjs)"
   or simply copy it next to a node_modules that has playwright and run it there.

   It fails with this message rather than a stack trace, because "cannot find
   module" reads like a broken test when it actually means "not installed".
   Today's ledger has four instrument defects in it; this is one fewer. */
let chromium;
try {
  ({ chromium } = await import('playwright'));
} catch {
  console.error('playwright is not installed here — see the header of this file.\n'
    + 'This is a MISSING DEPENDENCY, not a failing verification.');
  process.exit(2);
}

const BASE='http://127.0.0.1:8834';
let fails=0; const ok=(c,m)=>{console.log(`  ${c?'PASS':'FAIL'}  ${m}`); if(!c)fails++;};
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});

async function open(tz){
  const ctx=await b.newContext({timezoneId:tz});
  const page=await ctx.newPage();
  const hits=[];
  /* CAPTURE ON page.on('request'), NOT on route(). A sendBeacon issued during
     unload does not reach a route() handler -- the 'ignore' event fired
     correctly and was invisible to the instrument, which read as a missing
     feature. The network-level event sees it. route() is kept only to FULFILL,
     so nothing leaves the machine. */
  page.on('request', r=>{
    const u=r.url();
    if(!u.includes('/api/lead')) return;
    hits.push({url:u, method:r.method(),
               hdr:r.headers()['x-marketics-form']||'',
               /* postData() is null for a Blob body -- which is exactly what
                  sendBeacon sends. postDataBuffer() has the bytes. */
               type:r.resourceType(),
               /* A sendBeacon request arrives as resourceType 'ping' and
                  Playwright exposes NO body for it -- postData and
                  postDataBuffer are both null. That is a tool limit, not a
                  missing payload: the Function tests cover what the ignore body
                  must contain, and this layer asserts only what it can actually
                  see (that the beacon fires, and where to). Asserting a body
                  here would be asserting null. */
               body:r.postData() || (r.postDataBuffer()?r.postDataBuffer().toString('utf8'):'')});
  });
  await page.route('**/*', async r=>{
    const u=r.request().url();
    if(u.includes('/api/lead')) return r.fulfill({status:204, body:''});
    if(!u.startsWith(BASE)) return r.fulfill({status:204,body:''});
    return r.continue();
  });
  await page.goto(BASE+'/get-started/',{waitUntil:'load'});
  await page.waitForTimeout(900);
  return {ctx,page,hits};
}
const act = h => { try { return JSON.parse(h.body).a; } catch { return '(unparsable)'; } };

console.log('\nConsent denominator — the four counts, in a browser\n');

// impression
let {ctx,page,hits}=await open('Europe/Berlin');
ok(await page.evaluate(()=>!!document.getElementById('mkx-consent')), 'gated visitor: banner is shown');
ok(hits.length===1 && act(hits[0])==='impression', 'impression posted once, at mount');
ok(hits[0]?.hdr==='consent', 'impression routes by X-Marketics-Form: consent');
ok(/"g":1/.test(hits[0]?.body||''), 'impression records gated:1');
ok(!/email|id"|visitor/i.test(hits[0]?.body||''), 'impression payload carries no identifier');
await ctx.close();

// accept
({ctx,page,hits}=await open('Europe/Berlin'));
await page.click('#mkx-accept'); await page.waitForTimeout(400);
ok(hits.map(act).join(',')==='impression,accept', 'Accept posts exactly impression,accept');
await ctx.close();

// deny
({ctx,page,hits}=await open('Europe/Berlin'));
await page.click('#mkx-decline'); await page.waitForTimeout(400);
ok(hits.map(act).join(',')==='impression,deny', 'Decline posts exactly impression,deny');
await ctx.close();

// ignore — navigate away undecided
({ctx,page,hits}=await open('Europe/Berlin'));
await page.goto(BASE+'/method/',{waitUntil:'load'});
await page.waitForTimeout(700);
const ig = hits.find(h => h.type === 'ping' && h.url.includes('f=consent'));
ok(!!ig, `leaving undecided fires the ignore beacon (saw: ${hits.map(h=>h.type+' '+(act(h))).join(' | ')})`);
ok(!!ig && ig.url.includes('/api/lead?f=consent'),
   'ignore goes same-origin to /api/lead with ?f=consent — the route sendBeacon can set');
ok(hits.filter(h=>h.type==='ping').length === 1, 'exactly one ignore beacon, not one per page');
await ctx.close();

// decided → no ignore
({ctx,page,hits}=await open('Europe/Berlin'));
await page.click('#mkx-accept'); await page.waitForTimeout(300);
await page.goto(BASE+'/method/',{waitUntil:'load'}); await page.waitForTimeout(700);
ok(!hits.some(h=>h.type==='ping'), 'a visitor who DECIDED never fires an ignore beacon');
await ctx.close();

// ungated → nothing at all
({ctx,page,hits}=await open('America/New_York'));
ok(!(await page.evaluate(()=>!!document.getElementById('mkx-consent'))), 'ungated visitor: no banner');
ok(hits.length===0, 'ungated visitor produces NO consent events (the counter is not vacuous)');
await ctx.close();

await b.close();
console.log(fails===0?'\nCONSENT EVENTS VERIFIED':`\n${fails} FAILED`);
process.exit(fails?1:0);
