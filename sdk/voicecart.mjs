/** Server-side merchant SDK. Never embed adminToken in a customer bundle. */
export class VoiceCartMerchantClient {
 #token;
 constructor({baseUrl,merchant='local',adminToken,fetch=globalThis.fetch,timeoutMs=15000}){
  const url=new URL(baseUrl);
  if(url.username||url.password||url.search||url.hash||!['','/'].includes(url.pathname)||!(url.protocol==='https:'||(url.protocol==='http:'&&['127.0.0.1','localhost','[::1]'].includes(url.hostname))))throw new Error('Use HTTPS or explicit loopback HTTP origin');
  if(!/^[a-z0-9][a-z0-9-]{0,31}$/.test(merchant)||typeof adminToken!=='string'||adminToken.length<32||!Number.isFinite(timeoutMs)||timeoutMs<1||timeoutMs>120000)throw new Error('Invalid merchant credential/configuration');
  this.base=`${url.origin}/api/${merchant}/`;this.#token=adminToken;this.fetch=fetch;this.timeout=timeoutMs;
 }
 async request(resource,body){const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),this.timeout);try{const response=await this.fetch(this.base+resource,{method:body===undefined?'GET':'POST',headers:{Authorization:`Bearer ${this.#token}`,'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body),signal:controller.signal,redirect:'error'});const result=await response.json();if(!response.ok){const error=new Error(result.error||`VoiceCart HTTP ${response.status}`);error.status=response.status;error.operationId=body?.operation_id;throw error;}return result;}finally{clearTimeout(timer);}}
 synchronize(snapshot){return this.request('admin/import',snapshot);}
 createSession(){return this.request('merchant/sessions',{});}
 search(query,filters={}){return this.request('merchant/search',{...filters,query});}
 lookup(productId){return this.request('merchant/lookup',{product_id:productId});}
 refreshOffers(variantIds){return this.request('merchant/refresh',{variant_ids:variantIds});}
 cart(sessionId){return this.request('merchant/cart',{session_id:sessionId});}
 addToCart(sessionId,intent){if(!intent.operation_id)throw new Error('Caller must retain a stable operation_id');return this.request('merchant/add',{...intent,session_id:sessionId});}
 setQuantity(sessionId,intent){if(!intent.operation_id)throw new Error('Caller must retain a stable operation_id');return this.request('merchant/quantity',{...intent,session_id:sessionId});}
 operation(sessionId,operationId){return this.request('merchant/operation',{session_id:sessionId,operation_id:operationId});}
}
