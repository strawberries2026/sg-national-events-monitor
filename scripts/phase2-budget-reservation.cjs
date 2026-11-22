'use strict';
// Offline planning helpers only. A lock on one runner is not a cross-run lock.
const {canFetch,budgetForDay,recordAttempt}=require('./phase2-fetch-budget.cjs');
function reserveInMemory(ledger,{sourceId,enabled=false,dailyCap=24,now,minimumIntervalMs=3600000}){
 const state=budgetForDay(ledger,sourceId,now);
 const decision=canFetch({enabled,dailyCap,used:state.used,lastAttemptAt:state.lastAttemptAt,now,minimumIntervalMs});
 if(!decision.allowed)return {...decision,state};
 const reserved=recordAttempt(ledger,sourceId,now);
 return {allowed:true,reason:'reserved',state:reserved};
}
// A compare-and-swap adapter must atomically validate revision AND write new state.
// Never use this helper with a non-atomic backend in production.
async function reserveWithCas({load,compareAndSwap,sourceId,enabled=false,dailyCap=24,now,minimumIntervalMs=3600000,maxConflicts=3}){
 if(typeof load!=='function'||typeof compareAndSwap!=='function')throw Error('Atomic backend required');
 if(!Number.isSafeInteger(maxConflicts)||maxConflicts<0)throw Error('Invalid conflict limit');
 for(let attempt=0;attempt<=maxConflicts;attempt++){
  const snapshot=await load();
  if(!snapshot||!(snapshot.ledger instanceof Map)||typeof snapshot.revision!=='string')throw Error('Invalid ledger snapshot');
  const updated=new Map(snapshot.ledger);
  const decision=reserveInMemory(updated,{sourceId,enabled,dailyCap,now,minimumIntervalMs});
  if(!decision.allowed)return decision;
  if(await compareAndSwap(snapshot.revision,updated))return decision;
 }
 return {allowed:false,reason:'concurrent_conflict'};
}
module.exports={reserveInMemory,reserveWithCas};
