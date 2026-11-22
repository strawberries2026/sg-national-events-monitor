'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const registry=JSON.parse(fs.readFileSync('data/news-source-registry.json','utf8'));
assert.equal(registry.schema_version,1);
assert.ok(Array.isArray(registry.sources)&&registry.sources.length>0);
const ids=new Set();
for(const source of registry.sources){
 assert.ok(typeof source.id==='string'&&source.id);
 assert.ok(!ids.has(source.id),'duplicate source id: '+source.id);ids.add(source.id);
 assert.ok(['official','news'].includes(source.kind),'unsupported source kind');
 assert.equal(new URL(source.homepage).protocol,'https:');
 if(source.enabled){
   assert.equal(source.verification,'verified','enabled source must be verified');
   assert.equal(new URL(source.feed_url).protocol,'https:','enabled feed must use HTTPS');
 }else if(source.feed_url!=null){
   assert.equal(new URL(source.feed_url).protocol,'https:');
 }
}
console.log('Source registry safety checks passed: '+ids.size+' sources');
