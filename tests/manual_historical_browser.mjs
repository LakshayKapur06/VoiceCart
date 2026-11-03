import {chromium,expect} from '@playwright/test';
import fs from 'node:fs';
const [origin='http://127.0.0.1:8082',output]=process.argv.slice(2);
const parsed=new URL(origin);if(!output||parsed.protocol!=='http:'||!['127.0.0.1','localhost'].includes(parsed.hostname)||parsed.username||parsed.password||parsed.pathname!=='/'||parsed.search||parsed.hash)throw new Error('Use a loopback preview origin and a new output directory.');
const browser=await chromium.launch({headless:true});
try {
 const page=await browser.newPage();await page.goto(origin+'/');
 await expect(page.locator('#result-summary')).toContainText('298');
 const initial=await page.locator('#result-summary').innerText();
 await page.getByLabel('Product, category or purpose').fill('microwave');await page.getByRole('button',{name:'Find products'}).click();
 await expect(page.locator('#result-summary')).toContainText('11');
 await expect(page.getByRole('button',{name:'Add to local cart',exact:true})).toHaveCount(0);
 await page.locator('.card').first().getByRole('button',{name:'Product details'}).click();await expect(page.getByRole('dialog')).toBeVisible();
 const login=await page.request.post(origin+'/api/local/admin/login',{data:{token:fs.readFileSync('.local/preview-secrets/admin_token','utf8').trim()}});expect(login.ok()).toBeTruthy();
 const metrics=await page.request.get(origin+'/api/local/admin/analytics');expect(metrics.ok()).toBeTruthy();const data=await metrics.json();expect(data.coverage.variants).toBe(298);expect(data.coverage.stock_known).toBe(0);
 fs.mkdirSync(output,{recursive:true});
 fs.writeFileSync(output+'/REAL_BROWSER.json',JSON.stringify({method:'Actual current-code private historical preview, no test fixtures. Real Chromium/details/admin auth and SQL counts; no physical audio/human accessibility claim.',initial_summary:initial,search_summary:await page.locator('#result-summary').innerText(),actionable_historical_add_buttons:0,admin_actual_variants:data.coverage.variants,known_stock:data.coverage.stock_known},null,2)+'\n',{flag:'wx'});
 console.log('Actual historical preview passed:298 records,11 microwave matches,0known stock,0enabled add buttons; actual admin counts verified.');
} finally {await browser.close();}
