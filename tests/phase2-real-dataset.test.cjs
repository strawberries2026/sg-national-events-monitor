'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const data=JSON.parse(fs.readFileSync('data/events.json','utf8'));
assert.ok(Array.isArray(data.events),'events array required');
const allowed=new Set(['PMO','ISTANA','MFA','MHA','MOF','MINDEF','PARLIAMENT']);
const records=data.events.filter(x=>x&&x.type==='Published announcement'&&allowed.has(String(x.agency||'').toUpperCase()));
assert.ok(records.length>0,'expected eligible official announcements');
for(const item of records){assert.ok(typeof item.title==='string'&&item.title.trim(),'title required');const url=new URL(item.source_url);assert.equal(url.protocol,'https:','official links must use HTTPS');assert.match(item.published_date,/^\d{4}-\d{2}-\d{2}$/,'publication date format')}
console.log('Real dataset compatibility passed: '+records.length+' eligible official announcements');
