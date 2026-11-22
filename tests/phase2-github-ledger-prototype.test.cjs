'use strict';
const assert=require('node:assert/strict');
const {encodeLedgerDocument,decodeLedgerDocument,makeRevisionStore}=require('../scripts/phase2-github-ledger-prototype.cjs');
const {reserveWithCas}=require('../scripts/phase2-budget-reservation.cjs');
(async()=>{
 let revision=0,content=encodeLedgerDocument(new Map());
 const store=makeRevisionStore({
  getSnapshot:async()=>({revision:String(revision),content}),
  putIfRevision:async(expected,next)=>{await Promise.resolve();if(expected!==String(revision))return false;content=next;revision++;return true}
 });
 const args={...store,sourceId:'pmo',enabled:true,dailyCap:1,now:'2026-11-22T01:00:00Z',minimumIntervalMs:0};
 const [a,b]=await Promise.all([reserveWithCas(args),reserveWithCas(args)]);
 assert.equal([a,b].filter(x=>x.allowed).length,1);
 assert.equal(decodeLedgerDocument(content).get('pmo').used,1);
 assert.equal((await reserveWithCas(args)).reason,'daily_cap');
 assert.throws(()=>decodeLedgerDocument('broken'));
 assert.throws(()=>decodeLedgerDocument('{"version":1,"sources":{"pmo":{"day":"2026-11-22","used":-1,"lastAttemptAt":null}}}'));
 const missing=makeRevisionStore({getSnapshot:async()=>null,putIfRevision:async()=>true});
 await assert.rejects(()=>missing.load(),/Missing authoritative ledger/);
 console.log('Phase 2 versioned storage prototype tests passed');
})().catch(e=>{console.error(e);process.exitCode=1});
