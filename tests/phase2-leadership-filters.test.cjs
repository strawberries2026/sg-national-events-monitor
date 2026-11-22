'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync('preview/phase2-official-feed.html','utf8');
const match=html.match(/function topicMatches\(item\)\{[\s\S]*?\}\};/);
assert.ok(match,'Topic classifier function must exist');
const leader={value:'all'};
const topicMatches=vm.runInNewContext(match[0]+'\ntopicMatches',{leader});
const cases=[
['president','President attends National Day reception',true],
['president','Prime Minister attends reception',false],
['pm','Prime Minister speaks at conference',true],
['pm','Deputy Prime Minister speaks at conference',false],
['dpm','Deputy Prime Minister attends forum',true],
['events','Singapore Airshow 2028',true],
['events','Budget policy update',false]
];
for(const [filter,title,expected] of cases){leader.value=filter;assert.equal(topicMatches({title}),expected,filter+': '+title)}
console.log('Phase 2 leadership keyword filter fixture checks passed');
