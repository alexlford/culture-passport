#!/usr/bin/env node
// Local-only recovery checks. Private interview data never enters dist or screenshots.
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {spawn} from "node:child_process";
import {chromium} from "playwright";

const visitor="http://127.0.0.1:8767/",source="http://127.0.0.1:8768/";
const servers=[[8767,"dist"],[8768,"."]].map(([port,dir])=>spawn("python",
  ["-m","http.server",String(port),"--bind","127.0.0.1","--directory",dir],{stdio:"ignore"}));
const browser=await chromium.launch({headless:true});
async function ready(url){
  for(let attempt=0;attempt<30;attempt++){
    try{if((await fetch(url)).ok)return;}catch{}
    await new Promise(resolve=>setTimeout(resolve,100));
  }
  throw Error("Local loading-test server did not start");
}
async function context(width=390){
  const ctx=await browser.newContext({viewport:{width,height:844}});
  await ctx.route("**/*",route=>route.request().url().startsWith(visitor)||
    route.request().url().startsWith(source)?route.continue():route.abort());
  return ctx;
}
async function recovered(page,host,selector){
  await page.locator(selector).first().waitFor();
  await page.waitForFunction(id=>document.getElementById(id)?.getAttribute("aria-busy")==="false",host);
  assert.equal(await page.locator(".load-retry").count(),0);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+3));
}
try{
  await Promise.all([ready(visitor),ready(source)]);
  for(const width of [390,768,1440]){
    const ctx=await context(width),page=await ctx.newPage();
    let fail=true,requests=0,interviewRequests=0;
    await page.route("**/data/records.json",route=>{
      requests++;
      return fail?route.fulfill({status:503,body:"Unavailable"}):route.continue();
    });
    await page.route("**/data/interview.json",route=>{interviewRequests++;return route.abort();});
    await page.goto(visitor+"explore.html");
    const retry=page.locator("#explore-results .load-retry");
    await retry.waitFor();
    assert.equal(await page.locator("#explore-results").getAttribute("aria-busy"),"false");
    assert.equal(await page.locator("#search").isDisabled(),true);
    assert((await retry.boundingBox()).height>=44);
    await retry.focus();fail=false;await page.keyboard.press("Enter");
    await recovered(page,"explore-results","#explore-results a.record-card");
    assert.equal(await page.locator("#search").isEnabled(),true);
    assert.equal(await page.evaluate(()=>document.activeElement?.id),"explore-results");
    assert.equal(requests,2,"Retry must not reload the page or issue duplicate requests");
    assert.equal(interviewRequests,0,"Visitor pages must never request private interview data");
    await page.locator("#search").fill("Sauvage");
    assert.equal(await page.locator("#explore-results a.record-card").count(),1);
    await ctx.close();console.log("PASS archive HTTP retry and keyboard focus",width);
  }
  // Exercise malformed JSON and a valid JSON document with the wrong root shape.
  for(const body of ["{broken",JSON.stringify({records:[],venues:"invalid"})]){
    const ctx=await context(),page=await ctx.newPage();let fail=true;
    await page.route("**/data/records.json",route=>fail?route.fulfill({status:200,contentType:"application/json",body}):route.continue());
    await page.goto(visitor+"index.html");
    await page.locator("#city-editions .load-retry").waitFor();
    assert.equal(await page.locator('[aria-busy="true"]').count(),0);
    fail=false;await page.locator("#city-editions .load-retry").click();
    await recovered(page,"featured-records","#featured-records a.feature-row");
    assert.equal(await page.locator("#city-editions a.city-edition").count(),6);
    await ctx.close();console.log("PASS malformed archive recovery");
  }
  // A hanging request must become a recoverable error rather than an endless spinner.
  {
    const ctx=await context(),page=await ctx.newPage();let pending,hang=true;
    await page.route("**/data/records.json",route=>{if(hang){pending=route;return;}return route.continue();});
    await page.goto(visitor+"timeline.html",{waitUntil:"domcontentloaded"});
    await page.locator("#timeline-results .load-retry").waitFor({timeout:20000});
    assert.equal(await page.locator("#timeline-results").getAttribute("aria-busy"),"false");
    hang=false;await pending.abort().catch(()=>{});
    await page.locator("#timeline-results .load-retry").click();
    await recovered(page,"timeline-results","#timeline-results .timeline-entry");
    await ctx.close();console.log("PASS stalled archive timeout and retry");
  }
  // Private interview uses only its own source, including during archive outages.
  {
    const ctx=await context(),page=await ctx.newPage();let recordRequests=0,fail=true;
    const db=JSON.parse(readFileSync("data/interview.json","utf8"));
    const area=[...new Set(db.candidates.map(x=>x.area))].find(area=>
      db.candidates.filter(x=>x.area===area&&!x.excludedFromPublication).slice(0,12).some(x=>x.visitStatus==="unreviewed"));
    const candidate=db.candidates.filter(x=>x.area===area&&!x.excludedFromPublication).slice(0,12).find(x=>x.visitStatus==="unreviewed");
    assert(candidate,"Need an editable candidate to check saved responses");
    const key="alexford:culture-interview:v1",saved=JSON.stringify({[candidate.id]:"maybe"});
    await page.addInitScript(({key,saved,area})=>{
      localStorage.setItem(key,saved);
      localStorage.setItem(key+":navigation",JSON.stringify({area,screen:"all",page:0}));
    },{key,saved,area});
    await page.route("**/data/records.json",route=>{recordRequests++;return route.abort();});
    await page.route("**/data/interview.json",route=>fail?route.fulfill({status:503,body:"Unavailable"}):route.continue());
    await page.goto(source+"interview.html");
    await page.locator("#interview-list .load-retry").waitFor();
    assert((await page.locator("#interview-list").innerText()).includes("Unable to load the interview."));
    assert.equal(await page.evaluate(key=>localStorage.getItem(key),key),saved);
    fail=false;await page.locator("#interview-list .load-retry").click();
    await recovered(page,"interview-list","#interview-list .interview-item");
    assert.equal(recordRequests,0,"Interview must not depend on archive data");
    const card=page.locator(".interview-item").filter({has:page.getByRole("heading",{name:candidate.name,exact:true})});
    assert.equal(await card.getByRole("button",{name:"Possibly visited",exact:true}).getAttribute("aria-pressed"),"true");
    assert((await page.locator("#interview-summary").inputValue()).includes(candidate.name+" (saved response)"));
    const wishButton=card.getByRole("button",{name:"Haven't been — add to my list",exact:true});
    assert.equal(await wishButton.count(),1,"Interview must show a fourth wishlist answer");
    await wishButton.click();
    assert.equal(await wishButton.getAttribute("aria-pressed"),"true");
    assert.equal(JSON.parse(await page.evaluate(key=>localStorage.getItem(key),key))[candidate.id],"want_to_visit");
    const summary=(await page.locator("#interview-summary").inputValue());
    assert(summary.includes("Haven't been — add to my list")&&
      summary.includes("WISHLIST ENTRIES ABOVE ARE NOT VISITS.")&&
      summary.includes("Did not visit"),"Wishlist must be distinct from confirmation and included as a non-visit");
    // A new page shares localStorage but not the original page's addInitScript,
    // which intentionally seeds the first page with a legacy "maybe" answer.
    const restoredPage=await ctx.newPage();
    await restoredPage.goto(source+"interview.html");
    await recovered(restoredPage,"interview-list","#interview-list .interview-item");
    const restored=restoredPage.locator(".interview-item").filter({has:restoredPage.getByRole("heading",{name:candidate.name,exact:true})});
    assert.equal(await restored.getByRole("button",{name:"Haven't been — add to my list",exact:true}).getAttribute("aria-pressed"),"true",
      "Wishlist selection must survive reload");
    await ctx.close();console.log("PASS independent interview retry and local wishlist choice");
  }
  console.log("PASS Culture loading recovery; no private screenshots or export changes");
}finally{
  servers.forEach(server=>server.kill("SIGTERM"));
  await browser.close();
}
