/* Requires Playwright, which this repo deliberately does NOT depend on -- there
   is no package.json and no build step (see netlify.toml [functions]). Run it
   against an install elsewhere:

     NODE_PATH=/path/to/node_modules node --input-type=module \
       -e "$(cat scripts/verify-bot-gate.mjs)"
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
/* Match the LEAD POST, not the host. /get-started also loads the GHL chat
   widget's loader.js from leadconnectorhq.com about 5s after load (B4), and a
   host-only matcher counted that GET as a lead submission -- which read as a
   real defect on that one surface while the identical code passed on
   /lp/keep-control. Second instrument defect today; the control is what
   exposed it both times. */
/* Post-proxy (v3.56): leads go SAME-ORIGIN to /api/lead. The consent counter
   uses the same endpoint, so the route label is what separates a lead POST from
   a consent event -- matching the path alone would count banner impressions as
   leads, which is the host-matching mistake of §3a in a new outfit. */
const isLead = r => r.url().includes('/api/lead')
               && r.method() === 'POST'
               && (r.headers()['x-marketics-form'] || '') !== 'consent'
               && !r.url().includes('f=consent');
let fails=0;
const ok=(c,m)=>{console.log(`  ${c?'PASS':'FAIL'}  ${m}`); if(!c)fails++;};

const browser = await chromium.launch({
  executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args:['--no-sandbox']});

async function open(url){
  const ctx=await browser.newContext(); const page=await ctx.newPage();
  const posts=[]; const t0=Date.now();
  await page.route('**/*', async r=>{
    const u=r.request().url();
    if(isLead(r.request())){posts.push({at:Date.now()-t0,body:r.request().postData()||''});
                        return r.fulfill({status:200,body:'{}'});}
    if(!u.startsWith(BASE)) return r.fulfill({status:204,body:''});
    return r.continue();
  });
  await page.goto(url,{waitUntil:'domcontentloaded'});
  return {ctx,page,posts,mark:()=>Date.now()-t0};
}

async function surface(path, fill, submit, isIntel){
  console.log(`\n${path}`);

  // 1. SUB-FLOOR: must NOT drop. Must post, after the remainder.
  let {ctx,page,posts}=await open(BASE+path);
  await fill(page); const tSubmit=Date.now();
  await submit(page);
  await page.waitForTimeout(500);
  ok(posts.length===0, 'sub-floor submit does not post immediately (deferred)');
  await page.waitForTimeout(3200);
  ok(posts.length===1, 'sub-floor submit IS eventually posted — the human is NOT dropped');
  if(posts.length===1){
    const waited=Date.now()-tSubmit;
    ok(waited>=500, `it waited out the floor before posting (~${Math.round(waited/100)*100}ms)`);
    const w=JSON.parse(posts[0].body);
    ok(!!w.email && !('hp_field' in w), 'the deferred payload is the real lead, no honeypot key');
  }
  if(isIntel){
    ok(/thank-you/.test(page.url()), 'the redirect waited with the POST, then landed on thank-you');
  }
  await ctx.close();

  // 2. PAST FLOOR: unchanged behaviour, posts at once.
  ({ctx,page,posts}=await open(BASE+path));
  await fill(page); await page.waitForTimeout(3200);
  const t2=Date.now(); await submit(page); await page.waitForTimeout(700);
  ok(posts.length===1 && Date.now()-t2 < 2000, 'past the floor: posts immediately, no added delay');
  await ctx.close();

  // 3. HONEYPOT: still a silent drop, at any speed.
  ({ctx,page,posts}=await open(BASE+path));
  await fill(page); await page.fill('#mkxHpField','https://spam.example');
  await page.waitForTimeout(3200); await submit(page); await page.waitForTimeout(1200);
  ok(posts.length===0, 'honeypot filled → still posts NOTHING (drop, not defer)');
  await ctx.close();

  // 4. HONEYPOT + sub-floor: the drop must win, and must not post after the wait.
  ({ctx,page,posts}=await open(BASE+path));
  await fill(page); await page.fill('#mkxHpField','x');
  await submit(page); await page.waitForTimeout(4000);
  ok(posts.length===0, 'honeypot + sub-floor → drop wins; nothing posts after the wait either');
  await ctx.close();
}

const fillIntel=async p=>{await p.fill('#fname','Jane');await p.fill('#lname','Host');
                          await p.fill('#email','codelane+defer@example.com');};
const clickIntel=async p=>{await p.evaluate(()=>submitForm());};

for(const c of ['muskoka','miami','montreal','nashville'])
  await surface(`/intel/${c}/`, fillIntel, clickIntel, true);

await surface('/get-started/',
  async p=>{await p.fill('#listingUrl','airbnb.com/rooms/123');
            await p.fill('#email','codelane+defer@example.com');},
  async p=>{await p.click('#submitBtn');}, false);

await surface('/lp/keep-control/',
  async p=>{await p.fill('#lpListingUrl','airbnb.com/rooms/123');
            await p.fill('#lpEmail','codelane+defer@example.com');},
  async p=>{await p.click('#lpSend');}, false);

// (timezone coverage lives in verify_tz.mjs -- the detector here was wrong)

await browser.close();
console.log(fails===0?'\nALL BEHAVIOURAL CHECKS PASS':`\n${fails} FAILED`);
process.exit(fails?1:0);
