'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {readLedger,writeLedger}=require('../scripts/phase2-budget-ledger.cjs');
const {recordAttempt,budgetForDay}=require('../scripts/phase2-fetch-budget.cjs');
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'phase2-budget-'));
try{
 const filename=path.join(dir,'ledger.json');
 assert.throws(()=>readLedger(filename),/ENOENT/);
 const ledger=readLedger(filename,{missingOk:true});
 recordAttempt(ledger,'pmo','2026-11-21T15:59:00Z');
 writeLedger(filename,ledger);
 const restored=readLedger(filename);
 assert.equal(budgetForDay(restored,'pmo','2026-11-21T15:59:30Z').used,1);
 assert.equal(budgetForDay(restored,'pmo','2026-11-21T16:00:00Z').used,0);
 fs.writeFileSync(filename,'{broken');
 assert.throws(()=>readLedger(filename),SyntaxError,'corrupt ledger must fail closed, not reset usage');
 fs.writeFileSync(filename,JSON.stringify({version:1,sources:{pmo:{day:'2026-11-22',used:-1,lastAttemptAt:null}}}));
 assert.throws(()=>readLedger(filename),/Invalid ledger record/);
 console.log('Phase 2 durable ledger round-trip and corruption checks passed');
}finally{fs.rmSync(dir,{recursive:true,force:true})}
