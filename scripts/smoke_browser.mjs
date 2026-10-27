#!/usr/bin/env node
// Real browser smoke tests of the *sanitized, private visitor export*.
// No public deployment, uploads outside private Actions, or background tasks.
import {chromium} from "playwright";
import {readFileSync, mkdirSync} from "node:fs";
import {spawn} from "node:child_process";
import path from "node:path";

const BASE="http://127.0.0.1:8765/";
const root=process.cwd();
const screenshots=path.join(root,"test-results","screenshots");
mkdirSync(screenshots,{recursive:true});
const browser=await chromium.launch({headless:true});
const server=spawn("python",["-m","http.server","8765","--bind","127.0.0.1","--directory","dist"],{
  cwd:root,stdio:"ignore"
});
const problems=[];
function assert(value,message){if(!value)throw Error(message);}
async function waitForSite(page){
  for(let attempt=0;attempt<25;attempt++){
    try{const response=await page.goto(BASE,{waitUntil:"domcontentloaded",timeout:3500});if(response?.ok())return;}
    catch(_){}
    await new Promise(resolve=>setTimeout(resolve,200));
  }
  throw Error("Local static visitor preview server did not respond.");
}
async function configure(context){
  const leafletDir=path.join(root,"node_modules","leaflet","dist");
  await context.route(/^https:\/\/unpkg\.com\/leaflet@1\.9\.4\/dist\/leaflet\.(js|css)$/,async route=>{
    const js=route.request().url().endsWith(".js");
    await route.fulfill({status:200,body:readFileSync(path.join(leafletDir,"leaflet."+(js?"js":"css"))),
      contentType:js?"application/javascript":"text/css"});
  });
  await context.route(/https:\/\/[^/]*basemaps\.cartocdn\.com\//,route=>route.abort());
  await context.route(/https:\/\/fonts\.(googleapis|gstatic)\.com\//,route=>route.abort());
}
async function pageCheck(page,url,ready,viewportName){
  const failures=[];
  const err=e=>failures.push(e.message);
  page.on("pageerror",err);
  const response=await page.goto(BASE+url,{waitUntil:"domcontentloaded",timeout:12000});
  assert(response?.ok(),viewportName+": failed to load "+url);
  await page.locator(ready).first().waitFor({timeout:12000});
  await page.evaluate(()=>document.fonts.ready);
  const metrics=await page.evaluate(()=>{
    const width=document.documentElement.clientWidth;
    return {
      width,documentWidth:document.documentElement.scrollWidth,
      bodyWidth:document.body.scrollWidth,
      offenders:[...document.querySelectorAll("body *")].map(el=>({el,left:el.getBoundingClientRect().left,right:el.getBoundingClientRect().right})).filter(x=>x.right>width+4||x.left< -4).sort((a,b)=>b.right-a.right).slice(0,12).map(x=>({tag:x.el.tagName,cls:String(x.el.className||"").slice(0,75),id:x.el.id,left:Math.round(x.left),right:Math.round(x.right)})),
      headingCount:document.querySelectorAll("main h1").length,
      mainLabel:document.querySelector("main h1")?.textContent?.trim()||"",
      navCount:document.querySelectorAll(".nav a").length
    };
  });
  assert(metrics.headingCount===1,viewportName+" "+url+": missing unique main h1");
  assert(metrics.navCount===4,viewportName+" "+url+": clean visitor preview must have four navigation links (private Interview excluded)");
  assert(metrics.documentWidth<=metrics.width+3&&metrics.bodyWidth<=metrics.width+3,
    viewportName+" "+url+": horizontal overflow "+JSON.stringify(metrics));
  const safe=url.split("?")[0].replace(".html","");
  await page.screenshot({path:path.join(screenshots,viewportName+"-"+safe+".png"),fullPage:true,animations:"disabled"});
  assert(!failures.length,viewportName+" "+url+" script errors: "+failures.join("; "));
  page.off("pageerror",err);
  return metrics;
}
try{
  const shell=await browser.newPage();
  await waitForSite(shell);
  await shell.close();
  for(const [name,width,height] of [["iphone",390,844],["desktop",1440,900]]){
    const context=await browser.newContext({viewport:{width,height},deviceScaleFactor:1,isMobile:name==="iphone",hasTouch:name==="iphone"});
    await configure(context);
    const page=await context.newPage();
    const routes=[
      ["index.html","#featured-records a.feature-row"],
      ["explore.html","#explore-results a.record-card"],
      ["timeline.html","#timeline-results .timeline-entry"],
      ["map.html","#city-list details.city-section"],
      ["record.html?id=dining-the-majestic-restaurant", "#record-detail h1"]
    ];
    // Resolve a canonical confirmed record ID from the filtered visitor dataset.
    const data=JSON.parse(readFileSync(path.join(root,"dist","data","records.json"),"utf8"));
    const target=data.records.find(r=>r.title==="The Majestic Restaurant")||data.records.find(r=>r.story?.paragraphs?.length);
    assert(target,"No suitable published story for smoke testing");
    routes[4][0]="record.html?id="+encodeURIComponent(target.id);
    for(const [url,selector] of routes){
      const metrics=await pageCheck(page,url,selector,name);
      console.log("PASS",name,url,metrics.width,metrics.documentWidth);
    }
    await page.goto(BASE+"index.html",{waitUntil:"domcontentloaded"});
    await page.locator("#shared-memory-records a.feature-row").first().waitFor();
    assert((await page.locator("#shared-memory-records a.feature-row").count())===2,
      "Exactly two unconfirmed friend memories should appear in their own home section");
    const summary=await page.locator(".metrics").innerText();
    const verifiedCount=data.records.filter(r=>r.status==="confirmed"&&
      ["dining","bar"].includes(r.type)&&r.editorial?.awardQualified).length;
    assert((await page.locator("#total-records").innerText())===String(verifiedCount),
      "Home awards counter must exclude unconfirmed shared memories");
    // City edition links must remain usable and show only that city's stories.
    const cityCards=page.locator("#city-editions a.city-edition");
    await cityCards.first().waitFor();
    assert(await cityCards.count()===6,"Home city editions should show six city destinations");
    const cityHref=await cityCards.first().getAttribute("href");
    assert(cityHref?.startsWith("./explore.html?city="),"City edition link is missing its destination");
    const selectedCity=new URL(cityHref,BASE).searchParams.get("city");
    await cityCards.first().click();
    await page.waitForFunction(expected=>document.querySelector("#city-filter")?.value===expected,selectedCity);
    assert(await page.locator("#explore-results a.record-card").count()>0,
      "City-edition deep link did not select its city");
    await page.locator("#city-filter").selectOption("");
    assert(!new URL(page.url()).searchParams.has("city"),
      "Clearing city filter did not remove its shareable query parameter");
    await page.goto(BASE+"explore.html",{waitUntil:"domcontentloaded"});
    await page.locator("#explore-results a.record-card").first().waitFor();
    await page.locator("#search").fill("Sauvage");
    await page.waitForFunction(()=>document.querySelectorAll("#explore-results a.record-card").length===1);
    assert((await page.locator("#explore-results").innerText()).includes("Sauvage"),"Search failed");
    // The film festival is a separately filterable cultural chapter.
    await page.goto(BASE+"explore.html",{waitUntil:"domcontentloaded"});
    await page.locator("#explore-results a.record-card").first().waitFor();
    await page.locator('[data-type="film"]').click();
    await page.waitForFunction(()=>document.querySelector("#explore-results")?.textContent?.includes("American Fiction"));
    assert((await page.locator("#explore-results a.record-card").count())===1,"Film filter should show the confirmed festival experience");
    await page.goto(BASE+"record.html?id=film-american-fiction-denver-film-festival-2023",{waitUntil:"domcontentloaded"});
    await page.locator("#record-detail h1").waitFor();
    assert((await page.locator("#record-detail").innerText()).includes("Nov 3, 2023")||(await page.locator("#record-detail").innerText()).includes("November 3, 2023"),"Film festival date was not rendered");
    await page.goto(BASE+"map.html",{waitUntil:"domcontentloaded"});
    await page.locator("#city-list details.city-section").first().waitFor();
    // Carto tiles are intentionally blocked by the QA harness. The fallback
    // must be visible without obscuring the usable city directory.
    await page.locator(".map-tile-fallback:visible").waitFor({timeout:12000});
    assert(await page.locator(".map-tile-fallback a[href='#city-list']").isVisible(),
      "Map outage fallback must link to the city directory");
    await page.locator("#map-category").selectOption("bar");
    await page.waitForFunction(()=>document.querySelector("#map-summary")?.textContent?.includes("cities"));
    assert((await page.locator("#city-list details.city-section").count())>0,"Map category filter erased bars");
    await page.goto(BASE+"record.html?id="+encodeURIComponent(target.id),{waitUntil:"domcontentloaded"});
    await page.locator("#record-detail h1").waitFor();
    assert((await page.locator(".experience-navigation a").allTextContents()).some(x=>x.includes("Look up this venue")),
      "Venue lookup missing");
    if(target.story?.paragraphs?.length){
      await page.locator(".feature-story .feature-story-paragraph").first().waitFor();
      assert((await page.locator(".feature-story .feature-story-paragraph").count())>=2,"History did not render");
    }
    await page.locator(".skip-link").focus();
    assert(await page.locator(".skip-link").evaluate(el=>document.activeElement===el),"Keyboard skip link cannot receive focus");
    // A memory page must be reachable while explicitly disclaiming firsthand proof.
    for(const title of ["Cindy's Rooftop","The Library at Gilt Bar"]){
      const memory=data.records.find(r=>r.title===title);
      assert(memory?.status==="recollected"&&memory.editorial.userRequestedMemory===true,
        title+" absent from visitor collection");
      await page.goto(BASE+"record.html?id="+encodeURIComponent(memory.id),{waitUntil:"domcontentloaded"});
      await page.locator("#record-detail h1").waitFor();
      assert((await page.locator(".recalled-notice").innerText()).includes("not been independently confirmed"),
        "Unverified visit not disclosed for "+title);
      await page.locator(".feature-story .feature-story-paragraph").first().waitFor();
      assert(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+3),
        title+" has horizontal overflow on "+name);
    }
    await context.close();
  }
  console.log("PASS: 10 rendered screenshots; search, map filters, history, venue lookup, keyboard focus, and mobile/desktop overflow.");
}finally{
  server.kill("SIGTERM");
  await browser.close();
}
if(problems.length)throw Error(problems.join("\n"));
