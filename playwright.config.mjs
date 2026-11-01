import {defineConfig} from '@playwright/test';
export default defineConfig({testDir:'./tests/browser',workers:1,use:{baseURL:process.env.VOICECART_BROWSER_URL||'http://127.0.0.1:8089',headless:true},reporter:[['list']],timeout:30000});
