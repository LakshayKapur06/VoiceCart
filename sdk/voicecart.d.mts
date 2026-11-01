export interface AddIntent {operation_id:string;variant_id:string;quantity:number;currency:string;revision:string;unit_price_minor:number|string;}
export interface QuantityIntent {operation_id:string;variant_id:string;quantity:number;currency:string;}
export interface SearchFilters {currency?:string;brand?:string;category?:string;offset?:number;limit?:number;}
export interface SDKOptions {baseUrl:string;merchant?:string;adminToken:string;fetch?:typeof globalThis.fetch;timeoutMs?:number;}
export class VoiceCartMerchantClient {
 constructor(options:SDKOptions);
 synchronize(snapshot:Record<string,unknown>):Promise<Record<string,unknown>>;
 createSession():Promise<{session_id:string;merchant:string}>;
 search(query:string,filters?:SearchFilters):Promise<{items:Array<Record<string,unknown>>;total:number;revision:string}>;
 lookup(productId:string):Promise<Record<string,unknown>>;
 refreshOffers(variantIds:string[]):Promise<{offers:Array<Record<string,unknown>>}>;
 cart(sessionId:string):Promise<Record<string,unknown>>;
 addToCart(sessionId:string,intent:AddIntent):Promise<Record<string,unknown>>;
 setQuantity(sessionId:string,intent:QuantityIntent):Promise<Record<string,unknown>>;
 operation(sessionId:string,operationId:string):Promise<Record<string,unknown>>;
}
