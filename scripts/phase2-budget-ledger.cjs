'use strict';
// Local-file ledger adapter for a future opt-in collector. Does not fetch or enable feeds.
// Persistence between CI runs requires an explicitly configured durable store.
const fs=require('node:fs');
const path=require('node:path');
const {singaporeDay}=require('./phase2-fetch-budget.cjs');
function validateRecord(sourceId,record){
 if(typeof sourceId!=='string'||!sourceId||!record||typeof record!=='object'
 || !/^\d{4}-\d{2}-\d{2}$/.test(record.day)
 || !Number.isSafeInteger(record.used)||record.used<0
 || (record.lastAttemptAt!==null&&(typeof record.lastAttemptAt!=='string'||!Number.isFinite(Date.parse(record.lastAttemptAt)))))
 throw Error('Invalid ledger record');
}
function readLedger(filename,{missingOk=false}={}){
 let raw;
 try{raw=fs.readFileSync(filename,'utf8')}catch(err){if(missingOk&&err.code==='ENOENT')return new Map();throw err}
 const parsed=JSON.parse(raw);
 if(!parsed||parsed.version!==1||!parsed.sources||typeof parsed.sources!=='object'||Array.isArray(parsed.sources))throw Error('Invalid ledger format');
 const ledger=new Map();
 for(const [id,record] of Object.entries(parsed.sources)){validateRecord(id,record);ledger.set(id,{day:record.day,used:record.used,lastAttemptAt:record.lastAttemptAt})}
 return ledger;
}
function writeLedger(filename,ledger){
 if(!(ledger instanceof Map))throw Error('Ledger must be a Map');
 const sources=Object.create(null);
 for(const [id,record] of ledger){validateRecord(id,record);sources[id]={day:record.day,used:record.used,lastAttemptAt:record.lastAttemptAt}}
 const parent=path.dirname(filename);
 fs.mkdirSync(parent,{recursive:true});
 const temp=filename+'.tmp-'+process.pid;
 try{fs.writeFileSync(temp,JSON.stringify({version:1,sources},null,2)+'\n',{flag:'wx',mode:0o600});fs.renameSync(temp,filename)}
 finally{try{fs.unlinkSync(temp)}catch(err){if(err.code!=='ENOENT')throw err}}
}
module.exports={readLedger,writeLedger};
