'use strict';
// Pure source-health model for Phase 2 preview. No external fetching.
function sourceHealth({enabled=false,lastSuccessAt=null,lastAttemptAt=null,lastError=null,now,staleAfterMinutes=180}){
 const current=Date.parse(now);
 if(!Number.isFinite(current)||!Number.isFinite(staleAfterMinutes)||staleAfterMinutes<=0)throw Error('Invalid health evaluation');
 if(!enabled)return {status:'disabled',ageMinutes:null,message:'Source not enabled'};
 if(!lastSuccessAt)return {status:lastError?'failed':'awaiting_first_update',ageMinutes:null,message:lastError?'Latest update failed':'Awaiting first successful update'};
 const success=Date.parse(lastSuccessAt);
 if(!Number.isFinite(success)||success>current)throw Error('Invalid last-success timestamp');
 const ageMinutes=Math.floor((current-success)/60000);
 if(lastError)return {status:'failed',ageMinutes,message:'Latest update failed; showing previously retrieved data'};
 if(ageMinutes>=staleAfterMinutes)return {status:'stale',ageMinutes,message:'Source data may be outdated'};
 return {status:'fresh',ageMinutes,message:'Source data is within freshness threshold'};
}
module.exports={sourceHealth};
