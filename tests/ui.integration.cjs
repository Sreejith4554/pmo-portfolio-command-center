/* DOM integration tests execute the actual UI scripts against the running Python API.
   These are not a rendered-browser/visual test. Run: npm run test:ui */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {JSDOM,VirtualConsole}=require('jsdom');
const base=process.env.PMO_TEST_URL||'http://127.0.0.1:8765';
const checks=[];let errors=[];
const wait=async(fn)=>{for(let i=0;i<150;i++){if(fn())return;await new Promise(r=>setTimeout(r,100));}throw Error('UI condition timed out; errors='+JSON.stringify(errors));};
(async()=>{
 const vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e.message));
 const dom=await JSDOM.fromURL(base,{resources:'usable',runScripts:'dangerously',virtualConsole:vc,beforeParse(w){w.fetch=(url,opts)=>fetch(new URL(url,base),opts);}});
 const doc=dom.window.document;const $=s=>doc.querySelector(s);const change=(s,v)=>{$(s).value=v;$(s).dispatchEvent(new dom.window.Event('change',{bubbles:true}));};
 const check=(name,fn)=>{fn();checks.push({test:name,actual:'PASS'});};
 await wait(()=>$('.kpi'));
 check('Executive view loads live API data',()=>assert.match($('#content').textContent,/15/));
 for(let i=0;i<7;i++){$(`[data-page="${i}"]`).click();check(`Management view ${i+1} renders`,()=>assert.ok($('#content').textContent.length>100));}
 change('#project-select','P03');change('#edit-table','milestones');change('#edit-record','P03-M3');$('#edit-value').value='2026-10-12';$('#edit-form').dispatchEvent(new dom.window.Event('submit',{cancelable:true,bubbles:true}));
 await wait(()=>$('#message').textContent.includes('Scenario saved'));
 check('Scenario edit changes mode',()=>assert.equal($('#mode').textContent,'SAVED SCENARIO'));
 let data=await(await fetch(base+'/api/portfolio')).json();check('Upstream UI edit propagates to dependency',()=>assert.equal(data.dependencies.find(d=>d.dependency_id==='DEP01').exposure_days,21));
 $('#reset').click();await wait(()=>$('#message').textContent.includes('Baseline restored'));
 check('Reset returns to baseline',()=>assert.equal($('#mode').textContent,'BASELINE'));
 change('#project-select','P05');$('#edit-value').value='-1';$('#edit-form').dispatchEvent(new dom.window.Event('submit',{cancelable:true,bubbles:true}));await wait(()=>$('#message').className==='error');
 check('Invalid update displayed as error',()=>assert.match($('#message').textContent,/Invalid numeric/));
 $('[data-page="0"]').click();change('#department','D1');await wait(()=>$('.kpi strong')?.textContent==='3');
 check('Department filter changes active count',()=>assert.equal($('.kpi strong').textContent,'3'));
 change('#department','');await wait(()=>$('.kpi strong')?.textContent==='15');change('#period','2026-07-06');await wait(()=>$('#asof').textContent==='2026-07-06');
 data=await(await fetch(base+'/api/portfolio?period=2026-07-06')).json();check('Historic view excludes future periods',()=>assert.equal(data.history.length,1));
 change('#period','2026-09-21');await wait(()=>$('#asof').textContent==='2026-09-21');
 const report=await(await fetch(new URL($('#report').getAttribute('href'),base))).text();check('Report follows live current-period filter',()=>assert.match(report,/4 Green \/ 3 Amber \/ 8 Red/));
 $('#export').click();await wait(()=>$('#message').textContent.includes('Exported 14 tables'));
 check('Analytics export button completes',()=>assert.match($('#message').textContent,/output folder/));
 check('No JavaScript runtime errors',()=>assert.deepEqual(errors,[]));
 const result={scope:'jsdom DOM integration with actual local Python API; not browser rendering',checks:checks.length,results:checks};
 fs.writeFileSync(path.resolve(__dirname,'../docs/ui-test-results.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify(result,null,2));dom.window.close();
})().catch(e=>{console.error(e);process.exit(1)});
