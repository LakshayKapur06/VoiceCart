import {VoiceCartMerchantClient} from './voicecart.mjs';
const client=new VoiceCartMerchantClient({baseUrl:'https://merchant.example',adminToken:'server-injected-credential'});
void client.search('appliance',{currency:'USD',limit:20});
void client.addToCart('session',{operation_id:'uuid',variant_id:'variant',quantity:1,currency:'USD',revision:'revision',unit_price_minor:'9223372036854775807'});
// @ts-expect-error operation identity is mandatory
void client.addToCart('session',{variant_id:'variant',quantity:1,currency:'USD',revision:'revision',unit_price_minor:100});
// @ts-expect-error quantity is an integer-valued number, not a string
void client.setQuantity('session',{operation_id:'uuid',variant_id:'variant',quantity:'2',currency:'USD'});
