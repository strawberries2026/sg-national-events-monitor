'use strict';
// Prototype: pure optimistic-concurrency adapter. Does not call GitHub or write files.
// The caller must supply a provider operation that atomically rejects stale revisions.
const {reserveWithCas}=require('./phase2-budget-reservation.cjs');
const {readLedger}=require('./phase2-budget-ledger.cjs');
function decodeLedgerDocument(text){
 const parsed=JSON.parse(text);
 if(!parsed||parsed.version!==1||!parsed.sources||typeof parsed.sources!=='object'||Array.isArray(parsed.sources))throw Error('Invalid ledger document');
 const ledger=new Map();
 for(const [id,r] of Object.entries(parsed.sources)){
  if(!id||!r||typeof r.day!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(r.day)||!Number.isSafeInteger(r.used)||r.used<0||(r.lastAttemptAt!==null&&(typeof r.lastAttemptAt!=='string'||!Number.isFinite(Date.parse(r.lastAttemptAt)))))throw Error('Invalid ledger record');
  ledger.set(id,{day:r.day,used:r.used,lastAttemptAt:r.lastAttemptAt});
 }
 return ledger;
}
function encodeLedgerDocument(ledger){
 const sources=Object.create(null);
 for(const [id,r] of ledger){
  if(!id||!r||typeof r.day!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(r.day)||!Number.isSafeInteger(r.used)||r.used<0||(r.lastAttemptAt!==null&&(typeof r.lastAttemptAt!=='string'||!Number.isFinite(Date.parse(r.lastAttemptAt)))))throw Error('Invalid ledger record');
  sources[id]={day:r.day,used:r.used,lastAttemptAt:r.lastAttemptAt};
 }
 return JSON.stringify({version:1,sources},null,2)+'\n';
}
function makeRevisionStore({getSnapshot,putIfRevision}){
 if(typeof getSnapshot!=='function'||typeof putIfRevision!=='function')throw Error('Versioned backend required');
 return {
  async load(){const snap=await getSnapshot();if(!snap||typeof snap.revision!=='string'||typeof snap.content!=='string')throw Error('Missing authoritative ledger');return {revision:snap.revision,ledger:decodeLedgerDocument(snap.content)}},
  async compareAndSwap(revision,ledger){return putIfRevision(revision,encodeLedgerDocument(ledger))}
 };
}
module.exports={decodeLedgerDocument,encodeLedgerDocument,makeRevisionStore};
