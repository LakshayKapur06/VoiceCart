import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

async function scriptedCapture(page){
 await page.addInitScript(()=>{
  navigator.mediaDevices.getUserMedia=async()=>({getTracks:()=>[{stop(){}}]});
  window.AudioContext=class {
   constructor(){this.sampleRate=16000;this.destination={};}
   createMediaStreamSource(){return {connect(){},disconnect(){}};}
   createScriptProcessor(){const p={connect(){p.timer=setInterval(()=>p.onaudioprocess?.({inputBuffer:{getChannelData:()=>new Float32Array(4096)}}),20);},disconnect(){clearInterval(p.timer);}};return p;}
   async close(){}
  };
 });
}

test('permission denial retains text recovery and focus returns from details',async({page})=>{
 await page.addInitScript(()=>{navigator.mediaDevices.getUserMedia=async()=>{throw new DOMException('Scripted denied','NotAllowedError');};});
 await page.goto('/');await expect(page.getByRole('status')).toContainText('Found');
 await page.getByRole('button',{name:'Start voice input',exact:true}).click();
 await expect(page.getByRole('alert')).toContainText('Use text input');
 await page.getByLabel('Product, category or purpose').fill('backpack');await page.getByRole('button',{name:'Find products'}).click();
 const opener=page.locator('.card').first().getByRole('button',{name:'Product details'});
 await opener.click();await page.keyboard.press('Escape');await expect(opener).toBeFocused();
 await page.setViewportSize({width:320,height:720});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 expect((await new AxeBuilder({page}).analyze()).violations).toEqual([]);
});

test('corrected transcript is the submitted text and speech failure preserves results',async({page})=>{
 await scriptedCapture(page);
 await page.route('**/transcribe',route=>route.fulfill({json:{text:'WRONG TEST WORDS',requires_review:true,cart_mutated:false}}));
 await page.goto('/');await expect(page.getByRole('status')).toContainText('Found');
 await page.getByRole('button',{name:'Start voice input',exact:true}).click();await expect(page.getByRole('button',{name:'End voice input'})).toBeVisible();await page.waitForTimeout(150);await page.getByRole('button',{name:'End voice input'}).click();
 await page.getByLabel('Correct the words before submitting').fill('blue shirt');
 const request=page.waitForRequest(r=>r.url().endsWith('/search')&&r.method()==='POST');
 await page.getByRole('button',{name:'Use this search'}).click();
 expect((await request).postDataJSON().query).toBe('blue shirt');await expect(page.locator('#review')).toBeHidden();
 await expect(page.locator('#cart-count')).toHaveText('0');
 await page.route('**/speak',route=>route.fulfill({status:503,json:{error:'TEST speaker synthesis unavailable; use text.'}}));
 await page.getByLabel('Speak responses').check();await page.getByRole('button',{name:'Find products'}).click();
 await expect(page.getByRole('alert')).toContainText('use text');await expect(page.getByRole('status')).toContainText('Found');
});

test('expired capability and unavailable interpreter show recovery without cart success',async({page})=>{
 await page.goto('/');await expect(page.getByRole('status')).toContainText('Found');
 await page.route('**/turns',route=>route.fulfill({status:403,json:{error:'TEST session expired; start a new session.'}}));
 await page.getByRole('button',{name:'Find products'}).click();await expect(page.getByRole('alert')).toContainText('session expired');
 await page.unroute('**/turns');
 await page.route('**/query',route=>route.fulfill({status:503,json:{error:'TEST inference timeout; use structured controls.'}}));
 await page.getByLabel(/Shopping assistant/).check();await page.getByLabel('Product, category or purpose').fill('add backpack');await page.getByRole('button',{name:'Find products'}).click();
 await expect(page.getByRole('alert')).toContainText('inference timeout');await expect(page.locator('#cart-count')).toHaveText('0');
});
