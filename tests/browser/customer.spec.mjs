import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

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
