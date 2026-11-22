'use strict';
// Pure, offline policy helpers. No network requests or credential access.
const DAY_MS=86400000;
function singaporeDay(iso){const d=new Date(iso);if(!Number.isFinite(d.getTime()))throw Error('Invalid timestamp');return new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Singapore',year:'numeric',month:'2-digit',day:'2-digit'}).format(d)}
function canFetch({enabled=false,dailyCap=24,used=0,lastAttemptAt=null,now,minimumIntervalMs=3600000}){
 if(!enabled)return {allowed:false,reason:'disabled'};
 if(!Number.isSafeInteger(dailyCap)||dailyCap<0||!Number.isSafeInteger(used)||used<0)throw Error('Invalid budget');
 if(used>=dailyCap)return {allowed:false,reason:'daily_cap'};
 const timestamp=new Date(now).getTime();
 if(!Number.isFinite(timestamp))throw Error('Invalid current timestamp');
 if(lastAttemptAt!==null){const last=new Date(lastAttemptAt).getTime();if(!Number.isFinite(last))throw Error('Invalid last attempt');if(timestamp-last<minimumIntervalMs)return {allowed:false,reason:'minimum_interval'}}
 return {allowed:true,reason:'within_budget'};
}
function cacheKey({sourceId,url}){if(!sourceId||typeof sourceId!=='string')throw Error('Source required');const u=new URL(url);if(u.protocol!=='https:')throw Error('HTTPS required');u.hash='';u.searchParams.sort();return sourceId+'|'+u.href.replace(/\/$/,'')}
function addOnce(cache,item){const key=cacheKey(item);if(cache.has(key))return false;cache.set(key,{...item});return true}
module.exports={singaporeDay,canFetch,cacheKey,addOnce};
