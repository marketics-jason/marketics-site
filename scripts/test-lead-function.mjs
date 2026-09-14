/* Behavioural tests for netlify/functions/lead.mjs, run against the real module. */
const MOD = new URL('../netlify/functions/lead.mjs', import.meta.url);
let fails = 0;
const ok = (c, m) => { console.log(`  ${c ? 'PASS' : 'FAIL'}  ${m}`); if (!c) fails++; };

let sent = [];
globalThis.fetch = async (url, init) => { sent.push({ url, body: init.body, headers: init.headers }); return new Response('{}', { status: 200 }); };
const logs = [];
const realLog = console.log;
console.log = (...a) => { const s = a.join(' '); if (s.startsWith('{"evt"')) logs.push(JSON.parse(s)); else realLog(...a); };

process.env.GHL_HOOK_ORGANIC = 'https://ghl.example/hooks/ORGANIC';
process.env.GHL_HOOK_PAID    = 'https://ghl.example/hooks/PAID';
process.env.GHL_HOOK_INTEL   = 'https://ghl.example/hooks/INTEL';

const { default: handler } = await import(MOD);
const post = (route, body, method = 'POST') => new Request('https://marketics.io/api/lead', {
  method,
  headers: route ? { 'x-marketics-form': route, 'content-type': 'application/json' } : { 'content-type': 'application/json' },
  body: method === 'POST' ? body : undefined,
});
const reset = () => { sent = []; logs.length = 0; };
/* The Function's outbound assert THROWS by design. A test that dies on it prints
   no verdict at all, which reads as "the control did not fire" -- so every call
   goes through here and a throw becomes an ordinary failed assertion. */
let threw = null;
const call = async (req) => { threw = null; try { return await handler(req); } catch (e) { threw = e; return null; } };

console.log('\n/api/lead — Function behaviour\n');

reset();
ok((await call(post('get-started', '{}', 'GET')))?.status === 405, 'GET is 405');
ok(sent.length === 0, 'GET forwards nothing');

reset();
let r = await call(post('', '{"email":"a@b.c"}'));
ok(r.status === 400 && sent.length === 0, 'missing route header → 400, forwards nothing');

reset();
r = await call(post('nope', '{"email":"a@b.c"}'));
ok(r.status === 400 && sent.length === 0, 'unknown route → 400, forwards nothing');

reset();
const savedPaid = process.env.GHL_HOOK_PAID; delete process.env.GHL_HOOK_PAID;
r = await call(post('lp-keep-control', '{"email":"a@b.c"}'));
ok(r.status === 502 && sent.length === 0,
   'env var missing → 502 and NO forward (never a silent 200 that loses a real lead)');
process.env.GHL_HOOK_PAID = savedPaid;

reset();
r = await call(post('get-started', 'not json'));
ok(r.status === 400 && sent.length === 0, 'malformed JSON → 400, forwards nothing');

reset();
r = await call(post('get-started', '[1,2,3]'));
ok(r.status === 400 && sent.length === 0, 'JSON array → 400 (payload must be an object)');

reset();
r = await call(post('get-started', JSON.stringify({ x: 'y'.repeat(70000) })));
ok(r.status === 413 && sent.length === 0, 'oversized body → 413, forwards nothing');

// ── routing ──
for (const [route, hook] of [['get-started','ORGANIC'],['lp-keep-control','PAID'],['intel','INTEL']]) {
  reset();
  await call(post(route, '{"email":"a@b.c"}'));
  ok(!threw && sent.length === 1 && sent[0].url.endsWith('/' + hook), `${route} → the ${hook} trigger, and only that one`);
}

// ── the load-bearing one: byte-identical forward ──
reset();
const tricky = '{"email":"a@b.c","utm_term":"a b&c=d","note":"trailing  spaces  ","n":1.50,"z":"\\u00e9"}';
await call(post('get-started', tricky));
ok(!threw && sent.length === 1 && sent[0].body === tricky,
   'outbound body is BYTE-IDENTICAL to inbound (no re-serialize)'       + (threw ? ` [handler threw: ${threw.message}]` : ''));
ok(!threw && sent.length === 1 && sent[0].body.includes('1.50') && sent[0].body.includes('\\u00e9'),
   'number formatting and escapes survive — proof it was not parsed and rebuilt');

// ── empty-key tripwire: observed, never repaired, never introduced ──
reset();
const withEmpty = '{"email":"a@b.c","utm_source":"","gclid_first":""}';
await call(post('get-started', withEmpty));
ok(!threw && sent.length === 1 && sent[0].body === withEmpty,
   'an empty key that arrives is forwarded unchanged, not silently repaired');
ok(logs.some(l => l.evt === 'lead_forwarded' && l.emptyKeys === 2),
   'empty keys are COUNTED as a tripwire (2 seen) so an upstream regression is visible');

reset();
await call(post('get-started', '{"email":"a@b.c"}'));
ok(logs.some(l => l.evt === 'lead_forwarded' && l.emptyKeys === 0),
   'a clean payload reports zero empty keys — the tripwire can distinguish, so it is not vacuous');

// ── deliverable 3: the counter line exists and carries no client data ──
reset();
await call(post('lp-keep-control', '{"email":"secret@person.com","listingUrl":"https://x"}'));
const line = logs.find(l => l.evt === 'lead_forwarded');
ok(!!line && line.route === 'lp-keep-control' && line.keys === 2, 'one counter line per POST, with a key COUNT');
ok(!JSON.stringify(line).includes('secret@person.com'),
   'the counter line carries counts, never client-level values');

// ── upstream failure is reported, not swallowed ──
reset();
globalThis.fetch = async () => { throw new Error('network down'); };
r = await call(post('get-started', '{"email":"a@b.c"}'));
ok(r.status === 502, 'upstream unreachable → 502, not a false success');
ok(logs.some(l => l.evt === 'lead_forwarded' && l.ok === false), 'the failure is recorded in the counter line');

console.log = realLog;
console.log(fails === 0 ? '\nALL FUNCTION TESTS PASS' : `\n${fails} FAILED`);
process.exit(fails ? 1 : 0);
