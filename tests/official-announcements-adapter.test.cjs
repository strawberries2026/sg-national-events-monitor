'use strict';
const assert = require('node:assert/strict');
const {fromOfficialAnnouncements}=require('../scripts/official-announcements-adapter.cjs');
const input={events:[
{type:'Published announcement',agency:'PMO',title:'Prime Minister speech',source_url:'https://www.pmo.gov.sg/example',published_date:'2026-11-20',category:'Leaders',date:'2026-12-01'},
{type:'Published announcement',agency:'PMO',title:'Prime Minister speech',source_url:'https://www.pmo.gov.sg/example',published_date:'2026-11-20'},
{type:'Published announcement',agency:'PMO',title:'Unsafe',source_url:'javascript:alert(1)'},
{type:'Published announcement',agency:'Unknown',title:'Not official',source_url:'https://example.com'}
]};
const cards=fromOfficialAnnouncements(input);
assert.equal(cards.length,1);
assert.equal(cards[0].publisher,'PMO');
assert.equal(cards[0].verification_status,'official_source_reported');
assert.equal(cards[0].event_start,null);
assert.equal(cards[0].published_at,'2026-11-19T16:00:00.000Z');
assert.deepEqual(fromOfficialAnnouncements({events:null}),[]);
console.log('Official announcements adapter fixture checks passed');
