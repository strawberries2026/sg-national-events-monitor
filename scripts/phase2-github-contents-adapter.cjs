'use strict';
// GitHub Contents API response interpreter. Offline only: caller supplies mockable request.
const {makeRevisionStore}=require('./phase2-github-ledger-prototype.cjs');
function makeGithubContentsStore({request,owner,repo,branch,path}){
 if(typeof request!=='function'||![owner,repo,branch,path].every(x=>typeof x==='string'&&x.length))throw Error('Invalid GitHub store config');
 const endpoint='/repos/'+encodeURIComponent(owner)+'/'+encodeURIComponent(repo)+'/contents/'+path.split('/').map(encodeURIComponent).join('/');
 const query='?ref='+encodeURIComponent(branch);
 async function getSnapshot(){
  const res=await request({method:'GET',path:endpoint+query});
  if(!res||res.status!==200)throw Error('GitHub ledger unavailable: '+(res&&res.status));
  const body=res.body;
  if(!body||typeof body.sha!=='string'||typeof body.content!=='string'||body.encoding!=='base64')throw Error('Invalid GitHub Contents response');
  const encoded=body.content.replace(/\s/g,'');
  if(!encoded||encoded.length%4!==0||!/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(encoded))throw Error('Invalid GitHub ledger base64');
  const decoded=Buffer.from(encoded,'base64');
  if(decoded.toString('base64')!==encoded)throw Error('Invalid GitHub ledger encoding');
  return {revision:body.sha,content:decoded.toString('utf8')};
 }
 async function putIfRevision(revision,content){
  const res=await request({method:'PUT',path:endpoint,body:{message:'chore(phase2): reserve request budget',branch,sha:revision,content:Buffer.from(content,'utf8').toString('base64')}});
  if(!res)throw Error('GitHub ledger write unavailable');
  if(res.status===409)return false;
  // 422 can mean validation failure, abuse protection, or another non-conflict error.
  if(res.status===422)throw Error('GitHub ledger update rejected: 422');
  if(res.status!==200)throw Error('GitHub ledger write failed: '+res.status);
  return true;
 }
 return makeRevisionStore({getSnapshot,putIfRevision});
}
module.exports={makeGithubContentsStore};
