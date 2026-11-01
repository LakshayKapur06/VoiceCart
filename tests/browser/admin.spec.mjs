import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('admin authentication, actual analytics, edit and provenance',async({page})=>{
 await page.goto('/admin');
 await page.getByLabel('Private merchant administrator token').fill('TEST-ONLY-ADMIN-KEY-DO-NOT-USE-OUTSIDE-TESTS');
 await page.getByRole('button',{name:'Sign in',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Observed activity'})).toBeVisible();
 await page.getByRole('button',{name:'Edit College backpack',exact:true}).click();
 await expect(page.getByLabel('Product title')).toHaveValue('College backpack');
 await page.getByLabel('Product title').fill('College backpack inspected');
 await page.getByRole('button',{name:'Validate and publish changes'}).click();
 await expect(page.getByRole('status')).toContainText('Actual catalogue');
 await expect(page.getByRole('button',{name:'Edit College backpack inspected',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Edit College backpack inspected',exact:true}).click();
 await page.getByLabel('Product title').fill('College backpack');
 await page.getByRole('button',{name:'Validate and publish changes'}).click();
 await expect(page.getByRole('button',{name:'Edit College backpack',exact:true})).toBeVisible();
 const result=await new AxeBuilder({page}).analyze();expect(result.violations).toEqual([]);
 await page.getByRole('button',{name:'Sign out'}).click();await expect(page.getByRole('heading',{name:'Administrator sign in'})).toBeVisible();
});
