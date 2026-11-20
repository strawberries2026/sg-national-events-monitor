// Run with: node tests/verify-f1-2027.cjs
// Dependency-free regression checks for the verified Singapore F1 event.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(root, 'data/verified-events.json'), 'utf8'));
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const f1 = data.events.filter(e => /Singapore Grand Prix 2027/i.test(e.title));
assert.equal(f1.length, 1, 'Expected exactly one F1 2027 record');
const event = f1[0];
assert.equal(event.start, '2027-10-08');
assert.equal(event.end, '2027-10-10');
assert.equal(event.verification_status, 'verified');
assert.equal(event.type, 'Major public event');
assert.match(event.source, /^https:\/\/www\.formula1\.com\/en\/racing\/2027\/singapore$/);
assert.ok(html.includes('<option value="Major public event">'), 'Event filter must support F1 category');
assert.ok(html.includes('event.pattern.test(e.title||\'\')'), 'National event list must match verified event titles');
assert.ok(html.includes('renderNationalEvents();'), 'National events rendering must be invoked');
assert.ok(html.includes("fetch('data/verified-events.json?ts='"), 'Verified event feed must be fetched');

const airshows = data.events.filter(e => /Singapore Airshow/i.test(e.title));
assert.equal(airshows.length, 1, 'Expected exactly one Singapore Airshow record');
assert.equal(airshows[0].start, '2028-02-15');
assert.equal(airshows[0].end, '2028-02-20');
assert.equal(airshows[0].verification_status, 'verified');
assert.ok(!data.events.some(e => /Singapore Airshow/i.test(e.title) && e.start.startsWith('2027-')), 'There must be no 2027 Airshow edition');

console.log('F1 2027 and Singapore Airshow 2028 regression checks passed (data and static integration).');
// Browser/Android visual checks and live deployment checks are still required.
