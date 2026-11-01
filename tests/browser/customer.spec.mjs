import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('cancel fences a delayed search response from the visible results',async({page})=>{
 await page.goto('/');await expect(page.getByRole('status')).toContainText('Found');
 let release,arrived;const requested=new Promise(resolve=>arrived=resolve);
 await page.route('**/search',async route=>{arrived();await new Promise(resolve=>release=resolve);try{await route.fulfill({json:{items:[],total:999,coverage:'STALE',message:'STALE RESULT'}});}catch{}});
 await page.getByRole('button',{name:'Find products'}).click();await requested;
 await page.getByRole('button',{name:'Cancel / stop',exact:true}).click();release();
 await expect(page.getByRole('status')).toContainText('Stopped');
 await expect(page.locator('#result-summary')).not.toContainText('999');
 await expect(page.getByRole('status')).not.toContainText('STALE');
});

test('customer search, details, add, quantity, remove and reload recovery',async({page})=>{
 await page.goto('/');
 await expect(page.getByRole('heading',{name:'Products to explore'})).toBeVisible();
 await page.getByLabel('Product, category or purpose').fill('college backpack');
 await page.getByRole('button',{name:'Find products'}).click();
 await expect(page.locator('.card').first()).toBeVisible();
 await page.locator('.card').first().getByRole('button',{name:'Product details'}).click();
 await expect(page.getByRole('dialog')).toBeVisible();
 await page.getByRole('button',{name:'Close details'}).click();
 await page.locator('.card').first().getByRole('button',{name:'Add to local cart'}).click();
 await expect(page.getByRole('status')).toContainText('Added 1');
 await page.getByRole('button',{name:/Your cart/}).click();
 const quantity=page.getByRole('spinbutton',{name:/Quantity for/});
 await quantity.fill('2');await page.getByRole('button',{name:'Update quantity'}).click();
 await expect(quantity).toHaveValue('2');
 await page.getByRole('button',{name:'Close cart'}).click();await page.reload();
 await page.getByRole('button',{name:/Your cart/}).click();await expect(page.getByRole('spinbutton',{name:/Quantity for/})).toHaveValue('2');
 await page.getByRole('button',{name:'Remove',exact:true}).click();
 await expect(page.getByText('Your cart is empty.')).toBeVisible();
});

test('keyboard dialogs, shortcuts, semantic accessibility and responsive layout',async({page})=>{
 await page.goto('/');await expect(page.getByRole('status')).toContainText('Found');
 await page.keyboard.press('Alt+h');await expect(page.getByRole('dialog')).toBeVisible();
 await page.keyboard.press('Escape');await expect(page.getByRole('dialog')).not.toBeVisible();
 await page.keyboard.press('Tab');
 const results=await new AxeBuilder({page}).analyze();expect(results.violations).toEqual([]);
 await page.setViewportSize({width:390,height:844});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 await page.getByLabel('Currency').selectOption('USD');await page.getByRole('button',{name:'Find products'}).click();
 await expect(page.getByText('No matching imported records.',{exact:false})).toBeVisible();
});

test('scripted-capture/ASR review and late-transcript cancellation never add',async({browser})=>{
 const context=await browser.newContext();const page=await context.newPage();
 await page.addInitScript(()=>{
  navigator.mediaDevices.getUserMedia=async()=>({getTracks:()=>[{stop(){}}]});
  window.AudioContext=class {
   constructor(){this.sampleRate=48000;this.destination={};}
   createMediaStreamSource(){return {connect(){},disconnect(){}};}
   createScriptProcessor(){const processor={connect(){processor.timer=setInterval(()=>processor.onaudioprocess?.({inputBuffer:{getChannelData:()=>new Float32Array(4096)}}),30);},disconnect(){clearInterval(processor.timer);}};return processor;}
   async close(){}
  };
 });
 await page.goto('http://127.0.0.1:8089/');await expect(page.getByRole('status')).toContainText('Found');
 await page.route('**/transcribe',route=>route.fulfill({json:{text:'college backpack',requires_review:true,cart_mutated:false}}));
 await page.getByRole('button',{name:'Start voice input',exact:true}).click();await expect(page.getByRole('button',{name:'End voice input'})).toBeVisible();await page.waitForTimeout(200);
 await page.getByRole('button',{name:'End voice input'}).click();await expect(page.getByLabel('Correct the words before submitting')).toHaveValue('college backpack');
 await expect(page.locator('#cart-count')).toHaveText('0');await page.getByRole('button',{name:'Discard',exact:true}).click();
 await page.unroute('**/transcribe');let release;let arrived;const requested=new Promise(resolve=>arrived=resolve);
 await page.route('**/transcribe',async route=>{arrived();await new Promise(resolve=>release=resolve);try{await route.fulfill({json:{text:'STALE TEST TRANSCRIPT'}});}catch{}});
 await page.getByRole('button',{name:'Start voice input',exact:true}).click();await expect(page.getByRole('button',{name:'End voice input'})).toBeVisible();await page.waitForTimeout(200);await page.getByRole('button',{name:'End voice input'}).click();await requested;
 await page.getByRole('button',{name:'Cancel / stop',exact:true}).click();release();await page.waitForTimeout(200);
 await expect(page.locator('#review')).toBeHidden();await expect(page.locator('#cart-count')).toHaveText('0');
 await page.unroute('**/transcribe');await page.route('**/transcribe',route=>route.fulfill({status:503,json:{error:'TEST ASR unavailable; use text.'}}));
 await page.getByRole('button',{name:'Start voice input',exact:true}).click();await expect(page.getByRole('button',{name:'End voice input'})).toBeVisible();await page.waitForTimeout(200);await page.getByRole('button',{name:'End voice input'}).click();await expect(page.locator('#error')).toContainText('TEST ASR unavailable');
 await context.close();
});
