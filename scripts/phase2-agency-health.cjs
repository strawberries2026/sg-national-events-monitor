'use strict';
// Pure validator for optional future per-agency refresh metadata.
// Never infer a successful source refresh from event publication dates.
const ALLOWED=new Set(['PMO','ISTANA','MFA','MHA','MOF','MINDEF','PARLIAMENT']);
function validateAgencyHealth(value,{now}){
 if(!value||typeof value!=='object'||Array.isArray(value))throw Error('Invalid agency health payload');
 const current=Date.parse(now);if(!Number.isFinite(current))throw Error('Invalid evaluation time');
 const result={};
 for(const [agency,record] of Object.entries(value)){
  if(!ALLOWED.has(agency)||!record||typeof record!=='object'||Array.isArray(record))throw Error('Invalid agency record');
  if(typeof record.last_success_at!=='string'||!Number.isFinite(Date.parse(record.last_success_at))||Date.parse(record.last_success_at)>current)throw Error('Invalid agency success timestamp');
  if(!['verified_refresh','verified_failure'].includes(record.status))throw Error('Invalid agency refresh status');
  result[agency]={status:record.status,last_success_at:record.last_success_at};
 }
 return result;
}
module.exports={validateAgencyHealth};
