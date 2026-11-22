'use strict';
// Offline policy for interpreting provider responses; does not perform HTTP requests.
function retryAfterMs(header,now){
 if(header===null||header===undefined)return null;
 const value=String(header).trim();
 if(/^\d+$/.test(value))return Math.min(Number(value)*1000,86400000);
 const date=Date.parse(value);
 const current=Date.parse(now);
 if(!Number.isFinite(date)||!Number.isFinite(current))return null;
 return Math.min(Math.max(0,date-current),86400000);
}
function responsePolicy({status,retryAfter=null,now,failures=0}){
 if(!Number.isInteger(status)||status<100||status>599)throw Error('Invalid HTTP status');
 if(!Number.isSafeInteger(failures)||failures<0)throw Error('Invalid failure count');
 if(status>=200&&status<300)return {outcome:'success',retry:false,waitMs:0};
 if(status===429||status===503){
  const providerWait=retryAfterMs(retryAfter,now);
  const exponential=Math.min(3600000,60000*Math.pow(2,Math.min(failures,6)));
  return {outcome:'rate_limited',retry:true,waitMs:Math.max(providerWait??0,exponential)};
 }
 if(status>=500)return {outcome:'transient_error',retry:true,waitMs:Math.min(3600000,60000*Math.pow(2,Math.min(failures,6)))};
 return {outcome:'permanent_error',retry:false,waitMs:0};
}
module.exports={retryAfterMs,responsePolicy};
