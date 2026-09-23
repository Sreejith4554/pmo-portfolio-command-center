/* Actual Chromium integration checks. Run against disposable local demo state. */
const {chromium}=require('playwright');const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.PMO_BROWSER_EXECUTABLE||undefined,args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--no-zygote','--single-process']});
 const page=await browser.newPage({viewport:{width:1512,height:1100}});const errors=[];const checks=[];page.on('pageerror',e=>errors.push(e.message));
 const check=(name,fn)=>{fn();checks.push({test:name,actual:'PASS'});};
 await page.goto(process.env.PMO_TEST_URL||'http://127.0.0.1:8765');await page.locator('.kpi').first().waitFor();
 assert.equal(await page.locator('#title').innerText(),'Executive portfolio');checks.push({test:'Executive page rendered',actual:'PASS'});
 await page.screenshot({path:path.resolve(__dirname,'../screenshots/executive-portfolio.png'),fullPage:true});
 for(let i=0;i<7;i++){await page.locator(`[data-page="${i}"]`).click();assert.equal(await page.locator('#title').innerText(),['Executive portfolio','Project health','Schedule & milestones','RAID & actions','Financial performance','Dependencies','Project detail'][i]);assert.ok((await page.locator('#content').innerText()).length>100);checks.push({test:`View ${i+1} visible`,actual:'PASS'});}
 await page.locator('#project-select').selectOption('P03');await page.locator('#edit-table').selectOption('milestones');await page.locator('#edit-record').selectOption('P03-M3');await page.locator('#edit-value').fill('2026-10-12');await page.getByRole('button',{name:'Save scenario',exact:true}).click();await page.getByText('Scenario saved.',{exact:false}).waitFor();
 assert.equal(await page.locator('#mode').innerText(),'SAVED SCENARIO');checks.push({test:'Scenario form saves and updates state',actual:'PASS'});
 await page.locator('[data-page="5"]').click();assert.match(await page.locator('#content').innerText(),/21 days exposure/);checks.push({test:'Upstream edit updates downstream exposure in rendered map',actual:'PASS'});
 await page.screenshot({path:path.resolve(__dirname,'../screenshots/dependency-scenario.png'),fullPage:true});
 await page.locator('[data-page="6"]').click();await page.getByRole('button',{name:'Reset all scenario edits'}).click();await page.getByText('Baseline restored.',{exact:false}).waitFor();assert.equal(await page.locator('#mode').innerText(),'BASELINE');checks.push({test:'Reset returns baseline',actual:'PASS'});
 await page.locator('#project-select').selectOption('P07');await page.screenshot({path:path.resolve(__dirname,'../screenshots/project-detail.png'),fullPage:true});
 await page.locator('[data-page="0"]').click();await page.locator('#department').selectOption('D1');await page.waitForFunction(()=>document.querySelector('.kpi strong')?.textContent==='3');checks.push({test:'Department filter changes rendered totals',actual:'PASS'});
 await page.locator('#department').selectOption('');await page.waitForFunction(()=>document.querySelector('.kpi strong')?.textContent==='15');
 await page.locator('#period').selectOption('2026-07-06');await page.waitForFunction(()=>document.querySelector('#asof').textContent==='2026-07-06');checks.push({test:'Reporting-period selection refreshes view',actual:'PASS'});
 await page.locator('#period').selectOption('2026-09-21');await page.waitForFunction(()=>document.querySelector('#asof').textContent==='2026-09-21');
 await page.setViewportSize({width:390,height:844});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true);checks.push({test:'Mobile viewport has no page-level horizontal overflow',actual:'PASS'});
 await page.screenshot({path:path.resolve(__dirname,'../screenshots/mobile-portfolio.png'),fullPage:true});
 assert.deepEqual(errors,[]);checks.push({test:'No browser JavaScript errors',actual:'PASS'});
 const result={scope:'Actual local Chromium rendering and interaction against the Python server',browser:browser.version(),checks:checks.length,results:checks};
 fs.writeFileSync(path.resolve(__dirname,'../docs/browser-test-results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
