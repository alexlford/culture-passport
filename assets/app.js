(function(){
  "use strict";
  const page=document.body.dataset.page||"home";
  const $=(selector,root=document)=>root.querySelector(selector);
  const all=(selector,root=document)=>Array.from(root.querySelectorAll(selector));
  const el=(tag,cls,text)=>{const x=document.createElement(tag);if(cls)x.className=cls;if(text!==undefined&&text!==null)x.textContent=String(text);return x;};
  const link=(label,url,cls)=>{const a=el("a",cls,label);a.href=url;return a;};
  const byId=(id)=>document.getElementById(id);
  const href=(r)=>"./record.html?id="+encodeURIComponent(r.id);
  // The archive keeps precision; the public UI favors memories and meaningful periods.
  const readableDate=(d)=>{
    if(!/^\d{4}-\d{2}-\d{2}$/.test(d||""))return d||"";
    const [year,month,day]=d.split("-").map(Number);
    return new Intl.DateTimeFormat("en-US",{month:"short",day:"numeric",year:"numeric",timeZone:"UTC"}).format(new Date(Date.UTC(year,month-1,day)));
  };
  // User-requested memories may appear without claiming a verified visit.
  const inCollection=(r)=>r.status==="confirmed"||
    (r.status==="recollected"&&r.editorial?.userRequestedMemory===true);
  const isRecalled=(r)=>r.status==="recollected";
  // JBF program participation is not a James Beard Award.
  // Recognition only controls an optional highlight filter, never whether a confirmed visit appears.
  const includedDining=(r)=>!!(r.editorial?.awardQualified||r.editorial?.featuredException||r.editorial?.officialFeature||r.editorial?.culturalSpotlight||r.officialFeatures?.length||r.siteRecognitions?.length||r.recognitions?.some(a=>!a.recognitionAtDifferentVenue));
  const reservationDerived=(r)=>r.visit?.evidenceType==="completed_reservation"||r.visit?.evidenceType==="completed_reservation_and_user_confirmed_venue";
  const storyPeriod=(r)=>{
    // Culture Passport is a memory archive: restaurant/cocktail stories show a year or
    // memorable occasion first. Dates in bookings are supporting provenance only.
    const isDining=["dining","bar"].includes(r.type);
    if(isDining&&r.memory?.period)return r.memory.period;
    if(isDining&&r.visit?.label&&/^(January|February|March|April|May|June|July|August|September|October|November|December|Christmas|Valentine|Fall|Autumn|Winter|Spring|Summer)/.test(r.visit.label))return r.visit.label;
    if(isDining&&r.visit?.year)return String(r.visit.year);
    const yrs=r.visit?.possibleYears||[];
    if(isDining&&yrs.length===1)return String(yrs[0]);
    if(isDining&&yrs.length>1)return String(yrs[0])+"–"+String(yrs[yrs.length-1]).slice(-2);
    if(r.visit?.date&&r.visit?.precision==="day")return readableDate(r.visit.date);
    if(r.memory?.period)return r.memory.period;
    if(r.visit?.year)return String(r.visit.year);
    if(yrs.length===1)return String(yrs[0]);
    if(yrs.length>1)return String(yrs[0])+"–"+String(yrs[yrs.length-1]).slice(-2);
    return r.visit?.label||"A time worth remembering";
  };
  const storyTeaser=(r)=>r.memory?.teaser||(r.visit?.evidenceType==="completed_reservation"?"A restaurant that surfaced in the reservation archive. Its personal story is still to be told.":r.summary);
  const timelineChapter=(r)=>{
    if(r.visit?.year)return String(r.visit.year);
    const yrs=r.visit?.possibleYears||[];
    return yrs.length?String(yrs[0]):"Other memories";
  };
  const displayYear=(r)=>{
    if(r.visit?.year)return String(r.visit.year);
    const yrs=r.visit?.possibleYears||[];
    if(yrs.length===1)return String(yrs[0]);
    if(yrs.length>1)return yrs[0]+"–"+yrs[yrs.length-1];
    return "Date unknown";
  };
  const yearForSorting=(r)=>r.visit?.year||r.visit?.possibleYears?.[0]||-1;
  const dateMonth=(r)=>r.visit?.month||Number(r.visit?.date?.slice(5,7))||0;
  const dateDay=(r)=>Number(r.visit?.date?.slice(8,10))||0;
  const byDate=(a,b)=>yearForSorting(b)-yearForSorting(a)||dateMonth(b)-dateMonth(a)||dateDay(b)-dateDay(a)||a.title.localeCompare(b.title);
  const titleFor={dining:"Restaurants",bar:"Bars, Pubs & Breweries",concert:"Concerts",opera:"Opera",theater:"Theater",film:"Film & Festivals"};
  // Each chapter has its own editorial voice; never fabricate details missing from the archive.
  const experienceModes={
    dining:{chapter:"01 / THE TABLE",genre:"Dining",heading:"At the table",program:"THE TABLE NOTES",mark:"✦"},
    bar:{chapter:"02 / AFTER DARK",genre:"Bars & breweries",heading:"After dark",program:"THE ROOM",mark:"◒"},
    concert:{chapter:"03 / LIVE",genre:"Concert",heading:"In the crowd",program:"THE LIVE RECORD",mark:"≋"},
    opera:{chapter:"04 / THE OPERA",genre:"Opera",heading:"From the program",program:"THE OPERA PROGRAM",mark:"◇"},
    theater:{chapter:"05 / THE STAGE",genre:"Theater",heading:"In the playbill",program:"THE PRODUCTION",mark:"✧"},
    film:{chapter:"06 / THE SCREEN",genre:"Film & festival",heading:"The screening",program:"THE FESTIVAL PROGRAM",mark:"▣"}
  };
  const experienceMode=(r)=>experienceModes[r.type]||experienceModes.dining;
  const safeExternalLink=(label,url)=>{
    if(typeof url!=="string"||!url.startsWith("https://"))return null;
    const a=link(label+" →",url);
    a.target="_blank";a.rel="noopener noreferrer";
    return a;
  };
  const programLine=(label,value)=>{
    if(value===null||value===undefined||String(value).trim()==="")return null;
    const row=el("div","program-fact");
    row.append(el("dt","",label),el("dd","",value));
    return row;
  };
  function experienceCover(r,v){
    const mode=experienceMode(r),cover=el("header","experience-cover");
    const bar=el("div","cover-topline");
    bar.append(el("span","",mode.chapter),el("span","cover-symbol",mode.mark));
    bar.lastChild.setAttribute("aria-hidden","true");
    cover.append(bar,el("p","cover-genre",mode.genre+" / Culture Passport"),
      el("h1","",r.title));
    const headline=r.memory?.headline;
    if(headline&&headline.toLocaleLowerCase()!==r.title.toLocaleLowerCase()){
      cover.append(el("p","cover-deck",headline));
    }else if(r.summary){
      cover.append(el("p","cover-deck",r.summary));
    }
    const line=el("div","cover-baseline");
    line.append(el("span","",storyPeriod(r)),
      el("span","",[v.city,v.region].filter(Boolean).join(" / ")||"Location unconfirmed"));
    cover.append(line);
    return cover;
  }
  function experienceProgram(r,v){
    const mode=experienceMode(r),panel=el("section","experience-program experience-program--"+r.type);
    panel.setAttribute("aria-label",mode.heading);
    panel.append(el("p","eyebrow",mode.program),el("h2","",mode.heading));
    const intro=(copy)=>{if(copy)panel.append(el("p","program-intro",copy));};
    const facts=(items)=>{
      const dl=el("dl","program-facts");
      items.filter(Boolean).forEach(x=>dl.append(x));
      if(dl.childElementCount)panel.append(dl);
    };
    const source=(label,url)=>{const a=safeExternalLink(label,url);if(a)panel.append(a);};
    if(r.type==="dining"){
      intro(r.memory?.teaser||r.summary);
      const g=r.guide;
      const starCount=g?.distinction==="starred"&&Number.isInteger(g.stars)&&g.stars>0?g.stars:null;
      const distinction=starCount?starCount+" Michelin "+(starCount===1?"star":"stars"):
        g?.distinction==="bib"?"Michelin Bib Gourmand":
        g?.distinction==="selected"?"Michelin Selected":
        g?.distinction==="plate"?"Michelin Plate (historical)":null;
      facts([programLine("The remembered meal",storyPeriod(r)),
        distinction?programLine("Guide distinction",distinction):null,
        g?.edition&&distinction?programLine("Guide edition",g.edition):null]);
      if(distinction)intro("Guide distinctions are recorded separately from the visit; a listing does not establish the recognition held on the night of the meal.");
    }else if(r.type==="bar"){
      intro(r.memory?.teaser||r.summary);
      facts([programLine("Place",v.name||r.title),
        programLine("Occasion",storyPeriod(r)),
        isRecalled(r)?programLine("Visit status","Recalled by a friend · personal attendance unconfirmed"):null]);
    }else if(r.type==="concert"){
      const acts=Array.isArray(r.attendedPerformers)?r.attendedPerformers.filter(x=>x.artist):[];
      if(acts.length){
        intro("Artists personally recalled from this festival. This is not a complete lineup, a setlist, or a record of stage times.");
        const dates=[...new Set(acts.map(x=>x.date||"Date not recorded"))];
        const lineup=el("div","concert-lineup");
        for(const date of dates){
          const block=el("div","concert-day");
          block.append(el("h3","",date==="Date not recorded"?date:readableDate(date)));
          const ul=el("ul","concert-performers");
          acts.filter(x=>(x.date||"Date not recorded")===date).forEach(x=>ul.append(el("li","",x.artist)));
          block.append(ul);lineup.append(block);
        }
        panel.append(lineup);
      }else{
        intro(r.memory?.teaser||r.summary);
        facts([programLine("Artist / event",r.title),
          programLine("Show",storyPeriod(r)),
          v.name?programLine("Venue",v.name):null]);
      }
      source("Event-history source",r.historicalEventVerification?.sourceUrl);
    }else if(r.type==="opera"){
      const performances=Array.isArray(r.attendedPerformances)?
        r.attendedPerformances.filter(x=>x.attendance==="confirmed"):[];
      intro("The performances attended, with surviving program credits kept separate from the personal memory.");
      if(performances.length){
        const list=el("ol","opera-acts");
        performances.forEach((p,i)=>{
          const item=el("li","opera-act");
          item.append(el("span","opera-act-number",String(i+1).padStart(2,"0")));
          const desc=el("div");
          desc.append(el("h3","",p.title),el("p","opera-date",readableDate(p.date)));
          if(p.michelleFordCredit)desc.append(el("p","opera-credit","Program credit: Michelle Ford · "+p.michelleFordCredit));
          const a=safeExternalLink("Original Lyric program",p.programUrl);
          if(a)desc.append(a);
          item.append(desc);list.append(item);
        });
        panel.append(list);
      }else{
        facts([programLine("Performance",r.title),programLine("Period",storyPeriod(r))]);
      }
      if(performances.length)intro("The original programs identify Michelle as an actor; they do not establish specific characters or singing roles.");
    }else if(r.type==="theater"){
      const p=r.production;
      intro(r.memory?.teaser||r.summary);
      facts([programLine("Production",p?.titleConfirmed===false?
        (p.name||r.title)+" (tentative identification)":p?.name||r.title),
        p?.engagementWindow?programLine("Production run (not attendance date)",p.engagementWindow):null,
        programLine("Remembered outing",storyPeriod(r)),
        v.name?programLine("Stage / venue",v.name):null]);
      source("Production source",p?.sourceUrl);
    }else if(r.type==="film"){
      const p=r.screening;
      intro(r.memory?.teaser||r.summary);
      facts([programLine("Festival",p?.festival),
        programLine("Screening",p?.program),
        programLine("Attended",p?.attendanceDate?readableDate(p.attendanceDate):storyPeriod(r)),
        programLine("Director",p?.filmDirector),
        programLine("Screening venue",p?.location||v.name),
        p?.scheduledTime?programLine("Published screening time (not arrival)",p.scheduledTime):null]);
      source("Original festival program",p?.scheduleSourceUrl);
    }
    return panel;
  }
  function empty(parent,title,description,url,label){
    parent.replaceChildren();
    const block=el("div","empty");
    block.append(el("h3","",title),el("p","",description));
    if(url)block.append(link(label||"Explore →",url));
    parent.append(block);
  }
  function setActiveNav(){
    const target=page==="record"?"explore":page;
    all(".nav a").forEach(a=>{const current=a.dataset.nav===target;a.classList.toggle("active",current);if(current)a.setAttribute("aria-current","page");});
  }
  function card(r,v){
    const mode=experienceMode(r);
    const a=link(" ",href(r),"record-card record-card--"+r.type);
    a.textContent="";
    const categoryLabel=isRecalled(r)?"FRIEND-RECALLED MEMORY":r.editorial?.awardQualified?"MICHELIN / JAMES BEARD RECOGNIZED":r.editorial?.culturalSpotlight?"CULTURAL DESTINATION":r.editorial?.officialFeature?"OFFICIAL FOUNDATION CONNECTION":r.editorial?.featuredException?"PERSONAL FEATURE":r.recognitions?.length?"OTHER RECOGNITION":r.type.toUpperCase();
    const top=el("p","eyebrow",categoryLabel+" / "+(v?.city||"LOCATION UNKNOWN"));
    const h=el("h3","",r.title),description=el("p","",storyTeaser(r));
    const bottom=el("div","record-footer");
    bottom.append(el("span","",storyPeriod(r)+(r.favorite?" · A favorite":"")),el("span","","Open record →"));
    const chapter=el("div","record-chapter");
    chapter.append(el("span","",mode.chapter),el("span","record-mark",mode.mark));
    chapter.lastChild.setAttribute("aria-hidden","true");
    a.append(chapter,top,h,description,bottom);
    return a;
  }
  function siteStats(db){
    // Verified visit totals must NEVER include friend-recalled, unconfirmed memories.
    const confirmed=db.records.filter(r=>r.status==="confirmed");
    const selected=db.records.filter(inCollection);
    const venues=new Map(db.venues.map(v=>[v.id,v]));
    const cities=new Set(confirmed.map(r=>venues.get(r.venueId)?.city).filter(Boolean));
    const starred=confirmed.filter(r=>r.type==="dining"&&r.guide?.distinction==="starred"&&r.guide.stars>0);
    const awards=confirmed.filter(r=>["dining","bar"].includes(r.type)&&r.editorial?.awardQualified);
    const visitVenues=new Set(confirmed.filter(r=>["dining","bar"].includes(r.type)).map(r=>r.venueId));
    const st=[["total-records",awards.length],["total-venues",visitVenues.size],["total-cities",cities.size],["total-starred",starred.length]];
    st.forEach(([key,value])=>{const target=byId(key);if(target)target.textContent=value;});
    for(const key of Object.keys(titleFor)){
      const target=byId(key); // counts use their own id rather than a category placeholder
      const badge=byId(key+"-count");
      if(!badge)continue;
      if(key==="dining")badge.textContent=confirmed.filter(r=>r.type==="dining").length+" confirmed visits";
      else if(key==="bar"){
        const visits=confirmed.filter(r=>r.type==="bar").length,shared=selected.filter(r=>r.type==="bar"&&isRecalled(r)).length;
        badge.textContent=visits+" visits · "+shared+" shared memories";
      }else badge.textContent=confirmed.filter(r=>r.type===key).length+" recorded";
    }
  }
  function home(db){
    siteStats(db);
    const venues=new Map(db.venues.map(v=>[v.id,v]));
    const host=byId("featured-records");
    const records=db.records.filter(inCollection).sort((a,b)=>Number(isRecalled(a))-Number(isRecalled(b))||Number(!!b.editorial?.featuredException)-Number(!!a.editorial?.featuredException)||Number(!!b.favorite)-Number(!!a.favorite)||byDate(a,b)).slice(0,6);
    host.replaceChildren();
    records.forEach(r=>{
      const v=venues.get(r.venueId);
      const a=link("",href(r),"feature-row feature-row--"+r.type);
      a.append(el("span","feature-year",timelineChapter(r)==="Other memories"?"✦":timelineChapter(r)));
      const mid=el("div");mid.append(el("strong","",r.title),el("small","",v.city+" · "+(r.memory?.headline||"A place in the collection")));
      a.append(mid,el("span","feature-arrow","→"));host.append(a);
    });
    // City editions are generated from confirmed *curated* stories only. This
    // works on both the private archive and the separately sanitized preview,
    // never counting tentative interview memories or friend-recalled visits.
    const cityHost=byId("city-editions");
    if(cityHost){
      const grouped=new Map();
      db.records.filter(r=>r.status==="confirmed").forEach(r=>{
        const venue=venues.get(r.venueId);
        if(!venue?.city)return;
        let entry=grouped.get(venue.city);
        if(!entry){entry={city:venue.city,venueIds:new Set(),records:[]};grouped.set(venue.city,entry);}
        entry.venueIds.add(r.venueId);entry.records.push(r);
      });
      const cities=[...grouped.values()]
        .sort((a,b)=>b.venueIds.size-a.venueIds.size||a.city.localeCompare(b.city))
        .slice(0,6);
      cityHost.replaceChildren();
      if(!cities.length)empty(cityHost,"The city editions are being prepared.","Confirmed curated stories will appear here after they have been reviewed.");
      cities.forEach((entry,index)=>{
        const preview=entry.records.slice().sort((a,b)=>
          Number(!!b.favorite)-Number(!!a.favorite)||
          Number(!!b.editorial?.featuredException)-Number(!!a.editorial?.featuredException)||
          byDate(a,b))[0];
        const card=link("","./explore.html?city="+encodeURIComponent(entry.city),"city-edition");
        card.setAttribute("aria-label","Explore "+entry.city+" — "+entry.venueIds.size+" confirmed places");
        card.append(el("span","city-edition-number",String(index+1).padStart(2,"0")+" / CITY EDITION"));
        card.append(el("h3","city-edition-name",entry.city));
        card.append(el("span","city-edition-count",entry.venueIds.size+" confirmed "+(entry.venueIds.size===1?"place":"places")));
        card.append(el("p","city-edition-memory","From the archive: "+preview.title));
        card.append(el("span","city-edition-cta","Explore stories →"));
        cityHost.append(card);
      });
    }
    const shared=byId("shared-memory-records");
    if(shared){
      shared.replaceChildren();
      db.records.filter(r=>inCollection(r)&&isRecalled(r))
        .sort((a,b)=>a.title.localeCompare(b.title)).forEach(r=>{
          const venue=venues.get(r.venueId);
          const row=link("",href(r),"feature-row friend-memory-row");
          const title=el("div");
          title.append(el("strong","",r.title),
            el("small","",(venue?.city||"Chicago")+" · Shared recollection · Visit unconfirmed"));
          row.append(el("span","feature-year","◒"),title,el("span","feature-arrow","→"));
          shared.append(row);
        });
    }
  }
  function explore(db){
    const host=byId("explore-results"),city=byId("city-filter"),search=byId("search"),count=byId("result-count"),highlightsOnly=byId("highlights-only");
    const venues=new Map(db.venues.map(v=>[v.id,v]));
    const availableCities=[...new Set(db.records.map(r=>venues.get(r.venueId)?.city).filter(Boolean))].sort();
    availableCities.forEach(n=>{const option=el("option","",n);option.value=n;city.append(option);});
    const params=new URLSearchParams(window.location.search);
    let filter=Object.prototype.hasOwnProperty.call(titleFor,params.get("type"))?params.get("type"):"all";
    highlightsOnly.checked=params.get("highlights")==="1";
    const buttons=all(".tabstrip button[data-type]");
    function update(){
      buttons.forEach(b=>{const active=b.dataset.type===filter;b.classList.toggle("active",active);b.setAttribute("aria-pressed",String(active));});
      const q=search.value.trim().toLocaleLowerCase();
      const rows=db.records.filter(r=>{
        const v=venues.get(r.venueId);
        const content=[r.title,r.summary,r.memory?.headline,r.memory?.teaser,r.memory?.story,v?.city,v?.region,v?.name].join(" ").toLocaleLowerCase();
        return inCollection(r)&&(!highlightsOnly.checked||!["dining","bar"].includes(r.type)||includedDining(r))&&(filter==="all"||r.type===filter)&&(!city.value||city.value===v?.city)&&(!q||content.includes(q));
      }).sort(byDate);
      count.textContent=rows.length+" places & experiences";
      host.replaceChildren();
      if(rows.length===0){empty(host,filter!=="all"?"This chapter is awaiting its first entry.":"No matching experiences yet.",filter!=="all"?"No "+titleFor[filter].toLowerCase()+" have been confirmed in this archive. Names and dates will be added as you recall them.":"Try changing the category, city, or search terms.",filter==="dining"?"./interview.html":null,"Continue the interview →");return;}
      rows.forEach(r=>host.append(card(r,venues.get(r.venueId))));
    }
    buttons.forEach(b=>b.addEventListener("click",()=>{filter=b.dataset.type;const url=new URL(location.href);if(filter==="all")url.searchParams.delete("type");else url.searchParams.set("type",filter);history.replaceState(null,"",url);update();}));
    const initialCity=params.get("city");
    if(initialCity&&availableCities.includes(initialCity))city.value=initialCity;
    city.addEventListener("change",()=>{const url=new URL(location.href);if(city.value)url.searchParams.set("city",city.value);else url.searchParams.delete("city");history.replaceState(null,"",url);update();});search.addEventListener("input",update);highlightsOnly.addEventListener("change",()=>{const url=new URL(location.href);if(highlightsOnly.checked)url.searchParams.set("highlights","1");else url.searchParams.delete("highlights");url.searchParams.delete("memories");history.replaceState(null,"",url);update();});update();
  }
  function timeline(db){
    const host=byId("timeline-results"),select=byId("timeline-type"),count=byId("timeline-count"),highlightsOnly=byId("timeline-highlights-only");
    const venues=new Map(db.venues.map(v=>[v.id,v]));
    function render(){
      const grouped=new Map();
      const results=db.records.filter(r=>inCollection(r)&&(!highlightsOnly.checked||!["dining","bar"].includes(r.type)||includedDining(r))&&(select.value==="all"||r.type===select.value)).sort(byDate);
      for(const r of results){const label=timelineChapter(r);if(!grouped.has(label))grouped.set(label,[]);grouped.get(label).push(r);}
      count.textContent=results.length+" recorded experience"+(results.length===1?"":"s");
      host.replaceChildren();
      if(!results.length){empty(host,"No memories in this chapter yet.","More places can be added as the stories return.");return;}
      for(const [label,rows] of grouped){
        const section=el("section","timeline-group"),year=el("div","timeline-year",label),stack=el("div","timeline-stack");
        rows.forEach(r=>{const v=venues.get(r.venueId);const a=link("",href(r),"timeline-entry timeline-entry--"+r.type),mid=el("div");
          mid.append(el("small","",r.type.toUpperCase()+" · "+v.city+" · "+storyPeriod(r)),el("h3","",r.title),el("p","timeline-memory",storyTeaser(r)));
          a.append(mid,el("span","","→"));stack.append(a);
        });
        section.append(year,stack);host.append(section);
      }
    }
    select.addEventListener("change",render);highlightsOnly.addEventListener("change",render);render();
  }
  function map(db){
    const host=byId("culture-map"),list=byId("city-list"),category=byId("map-category");
    const venues=new Map(db.venues.map(v=>[v.id,v]));
    const available=db.records.filter(inCollection);
    // These are explicitly CITY-LEVEL reference coordinates, never venue positions.
    // Existing verified city coordinates in the collection take precedence.
    // Sources: Ordnance Survey Open Names (Cambridge UK), LA Almanac (West Hollywood),
    // public NYC center listing, and Cambridge Massachusetts city coordinates.
    const cityCenters=new Map([
      ["Cambridge · Cambridgeshire, England · United Kingdom",[52.20486,0.11968]],
      ["West Hollywood · California · USA",[34.088267,-118.371831]],
      ["New York · New York · USA",[40.7128,-74.0060]],
      ["Cambridge · Massachusetts · USA",[42.37361,-71.11056]]
    ]);
    const validPoint=(v)=>v?.location&&Number.isFinite(v.location.lat)&&
      Number.isFinite(v.location.lng)&&Math.abs(v.location.lat)<=90&&Math.abs(v.location.lng)<=180;
    let leafletMap=null,markers=[];
    if(typeof window.L!=="undefined"){
      host.replaceChildren();
      leafletMap=L.map(host,{scrollWheelZoom:false,zoomControl:true,minZoom:2});
      const tileFallback=el("div","map-tile-fallback");
      tileFallback.hidden=true;
      tileFallback.setAttribute("role","status");
      tileFallback.append(el("strong","","Map background unavailable"),
        el("p","","The city directory still works. Select a city below to explore your experiences."),
        link("Browse cities ↓","#city-list"));
      let successfulTiles=0,failedTiles=0;
      const layer=L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        {attribution:"&copy; OpenStreetMap contributors &copy; CARTO",maxZoom:18});
      layer.on("tileload",()=>{successfulTiles+=1;tileFallback.hidden=true;});
      layer.on("tileerror",()=>{
        failedTiles+=1;
        if(successfulTiles===0&&failedTiles>=2)tileFallback.hidden=false;
      });
      layer.addTo(leafletMap);
      host.append(tileFallback);
    }else{
      host.replaceChildren(el("div","empty",
        "Map background unavailable. Browse the city directory to explore the experiences."),
        link("Browse cities ↓","#city-list"));
    }
    function render(){
      markers.forEach(m=>{if(leafletMap)leafletMap.removeLayer(m);});
      markers=[];
      const groups=new Map(),unlocated=[];
      for(const r of available){
        if(category.value!=="all"&&r.type!==category.value)continue;
        const v=venues.get(r.venueId);
        // A known city still belongs in the directory when its venue has no
        // coordinates. Do not silently hide confirmed visits.
        if(!v?.city){unlocated.push(r);continue;}
        const cityKey=[v.city,v.region,v.country].filter(Boolean).join(" · ");
        if(!groups.has(cityKey)){
          groups.set(cityKey,{key:cityKey,name:v.city,region:v.region||v.country||"",
            lat:null,lng:null,records:[],venues:new Set()});
        }
        const g=groups.get(cityKey);
        if(validPoint(v)&&g.lat===null){g.lat=v.location.lat;g.lng=v.location.lng;}
        g.records.push(r);
        g.venues.add(r.venueId);
      }
      list.replaceChildren();
      const groupsSorted=[...groups.values()].sort((a,b)=>a.name.localeCompare(b.name)||
        String(a.region||"").localeCompare(String(b.region||"")));
      const selectedCity=new URLSearchParams(location.search).get("city");
      const nameMatches=selectedCity?groupsSorted.filter(g=>g.name===selectedCity):[];
      let focus=null,pinnedCities=0;
      const locations=[];
      for(const g of groupsSorted){
        if(g.lat===null&&cityCenters.has(g.key)){
          [g.lat,g.lng]=cityCenters.get(g.key);
        }
        const details=el("details","city-section");
        const summary=el("summary","city-summary");
        const name=el("strong","",g.name);
        const qualifier=el("span","",g.venues.size+" place"+(g.venues.size===1?"":"s")+
          " · "+g.region+(g.lat===null?" · Map position pending":""));
        summary.append(name,qualifier);details.append(summary);
        const ul=el("ul","map-place-list");
        for(const r of [...g.records].sort((a,b)=>a.title.localeCompare(b.title))){
          const li=el("li"),a=link(r.title,href(r));
          a.append(el("span","",storyPeriod(r)));
          li.append(a);ul.append(li);
        }
        details.append(ul);list.append(details);
        if(selectedCity===g.key||(nameMatches.length===1&&selectedCity===g.name)){
          details.open=true;focus=g.lat!==null?g:null;
        }
        if(g.lat!==null)pinnedCities++;
        if(leafletMap&&g.lat!==null){
          const marker=L.marker([g.lat,g.lng],{icon:L.divIcon({
            className:"",html:'<div class="culture-marker" aria-hidden="true">'+g.venues.size+'</div>',
            iconSize:[30,30],iconAnchor:[15,15]})}).addTo(leafletMap);
          const popup=el("div","map-popup");
          popup.append(el("strong","",g.name+" · "+g.region),
            el("p","",g.venues.size+" place"+(g.venues.size===1?"":"s")+
              " · city-level pin, not an exact venue"));
          const openCity=el("button","map-popup-link","View places in this city");
          openCity.type="button";
          openCity.addEventListener("click",()=>{
            details.open=true;
            details.scrollIntoView({behavior:"smooth",block:"nearest"});
          });
          popup.append(openCity);
          marker.bindPopup(popup);
          summary.addEventListener("click",()=>{
            leafletMap.setView([g.lat,g.lng],9,{animate:false});
            marker.openPopup();
          });
          markers.push(marker);locations.push([g.lat,g.lng]);

        }
      }
      if(!groupsSorted.length&&!unlocated.length){
        list.append(el("p","map-legend","No experiences in this category yet."));
      }
      if(unlocated.length){
        const details=el("details","city-section map-unlocated");
        const summary=el("summary","city-summary");
        summary.append(el("strong","","Location not confirmed"),
          el("span","",unlocated.length+" experience"+(unlocated.length===1?"":"s")+
            " · no city pin"));
        details.append(summary);
        const ul=el("ul","map-place-list");
        for(const r of [...unlocated].sort((a,b)=>a.title.localeCompare(b.title))){
          const li=el("li"),a=link(r.title,href(r));
          a.append(el("span","","City or venue location not confirmed"));
          li.append(a);ul.append(li);
        }
        details.append(ul);list.append(details);
      }
      const totalRecords=groupsSorted.reduce((n,g)=>n+g.records.length,0)+unlocated.length;
      const status=byId("map-summary");
      if(status)status.textContent=totalRecords+" experiences · "+pinnedCities+
        " cities on the map"+(unlocated.length?" · "+unlocated.length+
        " with locations to confirm":"")+(groupsSorted.length>pinnedCities?
        " · "+(groupsSorted.length-pinnedCities)+" cities awaiting map positions":"");
      if(leafletMap){
        if(focus)leafletMap.setView([focus.lat,focus.lng],9,{animate:false});
        else if(locations.length===1)leafletMap.setView(locations[0],9,{animate:false});
        else if(locations.length)leafletMap.fitBounds(locations,{padding:[45,45],maxZoom:9});
        else leafletMap.setView([39.5,-98.35],4,{animate:false});
      }
    }
    category.addEventListener("change",render);
    render();
  }
    function detail(db){
    const host=byId("record-detail"),params=new URLSearchParams(window.location.search),id=params.get("id");
    const r=db.records.find(x=>x.id===id&&inCollection(x));
    if(!r){empty(host,"Experience not found.","This record may have moved or is not part of the collection.","./explore.html","Back to the archive →");return;}
    document.title=r.title+" | Culture Passport";
    const v=db.venues.find(x=>x.id===r.venueId)||{},context=r.memory;
    host.replaceChildren();
    host.className="detail detail--"+r.type;
    host.append(experienceCover(r,v));
    const period=el("p","memory-period",storyPeriod(r)+" · "+[v.city,v.region].filter(Boolean).join(", "));
    host.append(period);
    if(isRecalled(r))host.append(el("p","recalled-notice",
      "FRIEND-RECALLED MEMORY · Included for the setting and shared story. A personal visit has not been independently confirmed; the year is unknown."));
    const orientation=el("div","experience-orientation");
    const periodTag=el("div","orientation-item");
    periodTag.append(el("span","","WHEN"),el("strong","",storyPeriod(r)));
    const placeTag=el("div","orientation-item");
    placeTag.append(el("span","","WHERE"),el("strong","",[v.city,v.region].filter(Boolean).join(", ")||"Location to be established"));
    orientation.append(periodTag,placeTag);
    host.append(orientation);
    if(context){
      host.append(el("h2","memory-heading",context.headline),el("p","memory-quote",context.story));
    }else{
      host.append(el("h2","memory-heading","A page in the collection"),
        el("p","memory-quote",storyTeaser(r)));
    }
    if((r.favorite||r.editorial?.featuredException)&&!isRecalled(r)){
      host.append(el("p","eyebrow memory-favorite","✦ KEPT FOR THE MEMORY"));
    }
    if(["dining","bar"].includes(r.type)&&!r.editorial?.awardQualified){
      host.append(el("p","memory-disclosure",r.editorial?.culturalSpotlight?
        "A curated cultural landmark with independently documented preservation, architectural or cocktail-industry recognition. These honors are not Michelin or James Beard distinctions.":r.editorial?.featuredException?
        "A personally selected cultural memory.":r.editorial?.officialFeature?
        (r.editorial.officialFeatureType==="jbf_editorial_mention"?
          "Official James Beard Foundation editorial coverage; no award or nomination claimed.":
          "Official James Beard Foundation program connection, not an award or nomination."):
        "A confirmed personal visit; no venue-specific Michelin or James Beard award is claimed."));
    }
    host.append(experienceProgram(r,v));
    if(r.story?.paragraphs?.length){
      const feature=el("section","feature-story");
      feature.append(el("p","eyebrow","BEHIND THE EXPERIENCE"),
        el("h2","","The place and its history"));
      for(const paragraph of r.story.paragraphs)feature.append(el("p","feature-story-paragraph",paragraph));
      if(r.story.chapters?.length){
        feature.append(el("h3","","A few chapters in the story"));
        const chapters=el("ol","heritage-list");
        for(const ch of r.story.chapters){
          const li=el("li","heritage-chapter");
          li.append(el("time","heritage-year",ch.year||""),el("div","heritage-copy"));
          li.lastChild.append(el("strong","",ch.title),el("p","",ch.detail));
          chapters.append(li);
        }
        feature.append(chapters);
      }
      if(r.story.sourceUrls?.length){
        const sources=el("div","feature-sources");
        sources.append(el("span","","HISTORY & SOURCES"));
        for(const source of r.story.sourceUrls){
          if(typeof source.url==="string"&&source.url.startsWith("https://")){
            const a=link(source.label||"Read source",source.url);
            a.target="_blank";a.rel="noopener noreferrer";
            sources.append(a);
          }
        }
        feature.append(sources);
      }
      host.append(feature);
    }
    // A shared historic site may contain independently confirmed experiences.
    // Render each named venue with its own recognition and prohibit award inheritance.
    if(Array.isArray(r.onSiteExperiences)&&r.onSiteExperiences.length){
      const section=el("section","onsite-experiences");
      section.append(el("p","eyebrow","CONFIRMED EXPERIENCES"),
        el("h2","",r.onSiteExperiences.length+" experiences in one landmark"),
        el("p","onsite-intro","These are separately recalled visits or experiences at the J. Rieger complex. Dates and companions remain unknown; distinctions belong only to their named recipients."));
      const grid=el("div","onsite-grid");
      for(const experience of r.onSiteExperiences){
        const item=el("article","onsite-item");
        item.append(el("p","onsite-period",experience.visitPeriod||"Date not specified"),
          el("h3","",experience.title),el("p","onsite-memory",experience.personalMemory||""),
          el("p","",experience.description||""));
        if(experience.recognitionContext)item.append(el("p","onsite-context",experience.recognitionContext));
        for(const award of experience.recognitions||[]){
          const card=el("div","onsite-award");
          card.append(el("strong","",award.organization+" · "+award.year+" · "+award.category),
            el("p","",award.recipient+" · "+award.result));
          if(award.relationship)card.append(el("p","",award.relationship));
          if(award.sourceUrl?.startsWith("https://")){
            const a=link("Read official recognition →",award.sourceUrl);
            a.target="_blank";a.rel="noopener noreferrer";card.append(a);
          }
          item.append(card);
        }
        if(experience.sources?.length){
          const refs=el("div","onsite-sources");
          for(const source of experience.sources){
            if(!source.url?.startsWith("https://"))continue;
            const a=link(source.label+" →",source.url);
            a.target="_blank";a.rel="noopener noreferrer";refs.append(a);
          }
          item.append(refs);
        }
        grid.append(item);
      }
      section.append(grid);
      host.append(section);
    }
    if(Array.isArray(r.siteRecognitions)&&r.siteRecognitions.length){
      const section=el("section","site-recognitions");
      section.append(el("h2","","Recognition for the restored historic site"),
        el("p","onsite-intro","Building-level preservation recognition applies to the overall distillery, not automatically to any cocktail lounge."));
      const cards=el("div","award-list");
      for(const award of r.siteRecognitions){
        const card=el("div","award-card");
        card.append(el("strong","",award.organization+" · "+award.category+" · "+award.year),
          el("p","",award.recipient+" · "+award.result));
        if(award.relationship)card.append(el("p","",award.relationship));
        if(award.sourceUrl?.startsWith("https://")){
          const a=link("Recognition source →",award.sourceUrl);
          a.target="_blank";a.rel="noopener noreferrer";card.append(a);
        }
        cards.append(card);
      }
      section.append(cards);host.append(section);
    }
    if(Array.isArray(r.relatedExperienceIds)&&r.relatedExperienceIds.length){
      const related=r.relatedExperienceIds.map(id=>db.records.find(x=>x.id===id&&inCollection(x))).filter(Boolean);
      if(related.length){
        const section=el("section","related-experiences");
        section.append(el("h2","","Connected Kansas City stories"),
          el("p","onsite-intro","The historic Rieger Hotel restaurant and Manifesto cocktail bar were separate experiences at a different address, not rooms inside this distillery."));
        for(const other of related)section.append(link(other.title+" →",href(other)));
        host.append(section);
      }
    }
    const around=el("div","experience-navigation");
    around.append(link("Explore experiences in "+(v.city||"this city")+" →","./explore.html?"+new URLSearchParams({city:v.city||""}).toString()));
    if(v.location&&v.city)around.append(link("Find this city on the map →","./map.html?"+new URLSearchParams({city:v.city}).toString()));
    // Link to a *place-name search*, never an unverified door-level GPS marker.
    // Restaurants can move/close; this is a lookup, not proof of present operation.
    if(v.name&&v.city){
      const placeQuery=[v.name,v.city,v.region].filter(Boolean).join(", ");
      const mapsUrl="https://www.google.com/maps/search/?"+new URLSearchParams({api:"1",query:placeQuery}).toString();
      const lookup=link("Look up this venue →",mapsUrl);
      lookup.target="_blank";lookup.rel="noopener noreferrer";
      around.append(lookup);
    }
    host.append(around);
        const badges=el("div","award-list"),g=r.guide;
    if(g?.distinction==="starred"){
      const b=el("div","award-card");b.append(el("strong","","Michelin · "+g.stars+" star"+(g.stars===1?"":"s")),el("p","","Recognition belongs to the restaurant, but may differ from the date of the meal."));if(g.sourceUrl)b.append(link("Guide source →",g.sourceUrl));badges.append(b);
    }else if(g?.distinction==="bib"){const b=el("div","award-card");b.append(el("strong","","Michelin Bib Gourmand"),el("p","",g.note||"Michelin recognition for great food at good value, not a Michelin star."));if(g.sourceUrl)b.append(link("Guide source →",g.sourceUrl));badges.append(b);}
    else if(g?.distinction==="plate"||g?.distinction==="selected"){
      const b=el("div","award-card");b.append(el("strong","",g.distinction==="plate"?"Michelin · The Plate (historical)":"Michelin Selected"),el("p","","Guide recognition, not a Michelin star. The listing year may differ from the dining year."));if(g.sourceUrl)b.append(link("Guide source →",g.sourceUrl));badges.append(b);
    }
    for(const feature of r.officialFeatures||[]){
      // Label editorial and program connections with their exact relationship.
      const isEditorial=feature.recognitionType==="editorial_mention";
      const b=el("div","award-card");
      b.append(el("strong","",feature.organization+" · "+(isEditorial?"Editorial connection":"Program connection")+" · "+feature.year));
      b.append(el("p","",feature.category+" — not an award or nomination."));
      if(feature.relationship)b.append(el("p","",feature.relationship));
      if(feature.venueScope==="named_branch_chef_team_offsite_event")b.append(el("p","","Chefs from this branch took part in an event held elsewhere; the restaurant did not host it."));
      if(feature.sourceUrl)b.append(link(isEditorial?"Official editorial source →":"Official program source →",feature.sourceUrl));
      badges.append(b);
    }
    for(const a of r.recognitions||[]){
      if(a.recognitionAtDifferentVenue)continue;
      const b=el("div","award-card");
      b.append(el("strong","",a.organization+" · "+a.category+(a.year?" · "+a.year:"")),
        el("p","",a.recipient+" · "+a.result));
      if(a.relationship)b.append(el("p","",a.relationship));
      if(a.timingRelativeToVisit==="after_visit")b.append(el("p","","Recognized after the remembered visit."));
      if(a.sourceUrl)b.append(link(a.organization==="CAMRA"?"CAMRA recognition source →":"Award source →",a.sourceUrl));
      badges.append(b);
    }
    if(badges.childElementCount)host.append(el("h2","","Why it stands out"),badges);
    // Retain dates and party size for provenance without making them the story.
    const details=el("details","archive-details"),heading=el("summary","","Historical notes & sources"),body=el("div","archive-details-body");
    details.append(heading);
    const note=(label,value)=>{if(!value)return;const row=el("p");row.append(el("strong","",label+" "));row.append(document.createTextNode(String(value)));body.append(row);};
    note("Place:",[v.name||r.title,v.city,v.region].filter(Boolean).join(" · "));
    note(reservationDerived(r)?"Reservation date on file:":"Visit/event date or period:",r.visit?.date?readableDate(r.visit.date):r.visit?.label||"Not established");
    if(r.visit?.partySize)note("Reservation party:",r.visit.partySize);
    if(r.visit?.timeWindow)note("Possible visit window:",r.visit.timeWindow);
    if(r.production?.engagementWindow)note("Production's engagement dates:",r.production.engagementWindow+" (individual show date not established)");
    if(Array.isArray(r.reservations)){
      for(const booking of r.reservations){
        note("Reservation evidence:",readableDate(booking.date)+(booking.occasion?" · "+booking.occasion:"")+(booking.partySize?" · party of "+booking.partySize:"")+" · booking on file, not independently proven attendance");
      }
    }
    note("Evidence:",r.visit?.source);
    if(r.visit?.evidenceType==="completed_reservation"||r.visit?.attendanceCertainty==="not_independently_verified")note("Booking note:","Reservation dates are archival context; the memory is organized by approximate year and occasion.");
    note("Award context:",r.editorial?.note);
    details.append(body);host.append(details);
  }
  const key="alexford:culture-interview:v1";
  function interview(db){
    const list=byId("interview-list"),progress=byId("interview-progress"),summary=byId("interview-summary"),output=byId("copy-status"),savedStatus=byId("interview-save-status");
    const pageInfo=byId("interview-page-state"),previous=byId("interview-previous"),next=byId("interview-next");
    const batchSize=12,uiKey=key+":navigation";
    let active="Denver Metro",screen="awards",page=0,answers={},storageAvailable=true;
    // Wishlist intent is separate from an actual visit. Keep the old browser-storage
    // namespace and historical "not_visited" answers for backward compatibility.
    const labels={visited:"Visited",maybe:"Possibly visited",not_visited:"Did not visit",
      want_to_visit:"No, but want to go"};
    const statuses=["visited","maybe","not_visited","want_to_visit"];
    const locked=(x)=>["confirmed","not_visited","maybe"].includes(x.visitStatus);
    const answer=(x)=>x.visitStatus==="confirmed"?"visited":
      x.visitStatus==="not_visited"?(x.wantsToVisit===true||answers[x.id]==="want_to_visit"?"want_to_visit":"not_visited"):
      x.visitStatus==="maybe"?"maybe":answers[x.id]|| (x.wantsToVisit===true?"want_to_visit":undefined);
    const included=db.candidates.filter(x=>!x.excludedFromPublication);
    try{
      const saved=JSON.parse(localStorage.getItem(key)||"{}");
      if(saved&&typeof saved==="object"&&!Array.isArray(saved))answers=saved;
      const nav=JSON.parse(localStorage.getItem(uiKey)||"{}");
      if(included.some(x=>x.area===nav.area))active=nav.area;
      if(["awards","leads","all"].includes(nav.screen))screen=nav.screen;
      if(Number.isInteger(nav.page)&&nav.page>=0)page=nav.page;
    }catch(_){storageAvailable=false;}
    const persist=()=>{
      try{
        localStorage.setItem(key,JSON.stringify(answers));
        localStorage.setItem(uiKey,JSON.stringify({area:active,screen,page}));
        storageAvailable=true;
      }catch(_){storageAvailable=false;}
      if(savedStatus)savedStatus.textContent=storageAvailable?"Your responses are saved in this browser.":"Browser storage is unavailable; copy your answers below to preserve them.";
    };
    const candidateFilter=(x)=>x.area===active&&(screen==="all"||screen==="awards"&&x.screening?.status==="award_qualified"||screen==="leads"&&(x.userMemoryLead&&!x.userMemoryLead.identityConfirmed||x.screening?.status!=="award_qualified"));
    const relevant=()=>included.filter(candidateFilter);
    const tabBox=$(".interview-actions .tabstrip");
    const allAreas=[...new Set([...included.map(x=>x.area),...Object.keys(db.periods||{})])];
    allAreas.filter(a=>!all("[data-area]").some(b=>b.dataset.area===a)).forEach(a=>{
      const b=el("button","",a);b.dataset.area=a;b.type="button";b.setAttribute("aria-pressed","false");tabBox.append(b);
    });
    const areaButtons=all("[data-area]"),screeningButtons=all("[data-screen]");
    const syncTabs=()=>{
      areaButtons.forEach(b=>{const on=b.dataset.area===active;b.classList.toggle("active",on);b.setAttribute("aria-pressed",String(on));});
      screeningButtons.forEach(b=>{const on=b.dataset.screen===screen;b.classList.toggle("active",on);b.setAttribute("aria-pressed",String(on));});
    };
    const updateSummary=()=>{
      const grouped={visited:[],maybe:[],not_visited:[],want_to_visit:[]};
      for(const x of included){
        const a=answer(x);
        if(!statuses.includes(a))continue;
        const marker=x.wantsToVisit===true?" (canonical future wishlist)":
          locked(x)?" (confirmed interview answer)":" (saved response)";
        const row=x.area+" — "+x.name+marker;
        if(a==="want_to_visit"){grouped.not_visited.push(row);grouped.want_to_visit.push(row);}
        else grouped[a].push(row);
      }
      const pending=included.filter(x=>x.userMemoryLead&&!x.userMemoryLead.identityConfirmed);
      summary.value="CULTURE PASSPORT — RESTAURANT AND BAR INTERVIEW\n\n"+
        statuses.map(s=>labels[s]+" ("+grouped[s].length+"):\n"+(grouped[s].map(n=>"• "+n).join("\n")||"None yet")).join("\n\n")+
        "\n\nWISHLIST ENTRIES ABOVE ARE NOT VISITS. Transfer them to the canonical private places-to-go list after review."+
        "\n\nVENUE IDENTITY TO CONFIRM:\n"+(pending.map(x=>"• "+x.name+" — "+x.userMemoryLead.recalled).join("\n")||"None")+
        "\n\nYour editable responses are saved locally and do not publish to the public passport automatically.";
      const completed=included.filter(x=>statuses.includes(answer(x))).length;
      const local=Object.keys(answers).filter(id=>included.some(c=>c.id===id)).length;
      progress.textContent=completed+" / "+included.length+" reviewed · "+local+" local answers";
    };
    const updatePagination=(count)=>{
      const pages=Math.max(1,Math.ceil(count/batchSize));
      if(page>=pages)page=pages-1;
      if(previous)previous.disabled=page===0;
      if(next)next.disabled=page>=pages-1;
      if(pageInfo)pageInfo.textContent=count?"Batch "+(page+1)+" of "+pages+" · "+(page*batchSize+1)+"–"+Math.min(count,(page+1)*batchSize)+" of "+count+" places":"No places in this selection";
    };
    function render(){
      const candidates=relevant();
      updatePagination(candidates.length);
      syncTabs();
      list.replaceChildren();
      const period=byId("interview-period");
      if(period)period.textContent=db.periods?.[active]?"HISTORICAL INTERVIEW WINDOW / "+db.periods[active]:"";
      const sc=byId("screening-count");
      if(sc)sc.textContent=candidates.length+" in "+active+" · "+(screen==="awards"?"Michelin / James Beard candidates":screen==="leads"?"memory leads":"all historical candidates");
      if(!candidates.length){
        empty(list,"No candidates in this selection.","Switch between Michelin / James Beard, Memory leads, and All candidates.");
        persist();return;
      }
      const slice=candidates.slice(page*batchSize,(page+1)*batchSize);
      slice.forEach((x,i)=>{
        const card=el("article","interview-item");
        card.append(el("span","tag",(x.venueType==="cocktail_bar"?"COCKTAIL BAR ":"RESTAURANT ")+String(page*batchSize+i+1).padStart(2,"0")+" / "+x.area),
          el("h3","",x.name),el("p","",x.interviewCue),el("p","",x.recognition));
        if(x.screening?.status==="award_qualified")card.append(el("p","qualifies","Award candidate · "+(x.screening.basis==="michelin"?"Michelin Guide":"James Beard")));
        else card.append(el("p","qualifies neutral","Personal memory / recognition not yet verified"));
        if(x.userMemoryLead&&!x.userMemoryLead.identityConfirmed)card.append(el("p","tag","Identification lead: "+x.userMemoryLead.recalled));
        // Source-linked historical photos help recognition without hotlinking images
        // whose redistribution rights are unknown. Preserve original-venue identity.
        if(Array.isArray(x.photographicEvidence)&&x.photographicEvidence.length){
          const photos=el("div","interview-photo-evidence");
          photos.append(el("p","interview-photo-title","HISTORICAL PHOTO CUES"));
          for(const photo of x.photographicEvidence){
            if(photo.renderMode!=="source_link_only"||typeof photo.sourceUrl!=="string"||!photo.sourceUrl.startsWith("https://"))continue;
            const item=el("div","interview-photo-item");
            const a=link(photo.label+" →",photo.sourceUrl,"interview-photo-link");
            a.target="_blank";a.rel="noopener noreferrer";item.append(a);
            if(photo.caption)item.append(el("p","interview-photo-caption",photo.caption));
            photos.append(item);
          }
          photos.append(el("p","interview-photo-caveat","Images open at their original source. No photo is presented as the historic dining room without verification."));
          card.append(photos);
        }

        if(locked(x)){
          const style=x.visitStatus==="maybe"?"locked maybe":x.visitStatus==="not_visited"?"locked no":"locked";
          card.append(el("div",style,x.visitStatus==="confirmed"?"✓ Confirmed visit"+(x.visitPeriod?" · "+x.visitPeriod:""):x.visitStatus==="not_visited"?"✕ Confirmed not visited":"? Possibly visited, pending confirmation"));
          // Already-confirmed non-visits may be added to the future wishlist locally
          // without rewriting the canonical not-visited evidence or suggesting attendance.
          if(x.visitStatus==="not_visited"){
            if(x.wantsToVisit===true)card.append(el("p","locked wishlist","♥ Already on future-visit list"));
            else{
              const choices=el("div","choices");
              const wishlistButton=el("button",answers[x.id]==="want_to_visit"?"active":"",labels.want_to_visit);
              wishlistButton.type="button";
              wishlistButton.setAttribute("aria-pressed",String(answers[x.id]==="want_to_visit"));
              wishlistButton.addEventListener("click",()=>{
                if(answers[x.id]==="want_to_visit")delete answers[x.id];else answers[x.id]="want_to_visit";
                const selected=answers[x.id]==="want_to_visit";
                wishlistButton.classList.toggle("active",selected);
                wishlistButton.setAttribute("aria-pressed",String(selected));
                output.textContent="";updateSummary();persist();
              });
              choices.append(wishlistButton);card.append(choices);
            }
          }
        }else{
          const choices=el("div","choices");
          choices.setAttribute("role","group");choices.setAttribute("aria-label","Have you visited "+x.name+"?");
          const buttons={};
          for(const status of statuses){
            const b=el("button",answer(x)===status?"active":"",labels[status]);
            b.type="button";b.setAttribute("aria-pressed",String(answer(x)===status));
            buttons[status]=b;
            b.addEventListener("click",()=>{
              if(answers[x.id]===status)delete answers[x.id];else answers[x.id]=status;
              for(const s of statuses){const selected=answers[x.id]===s;buttons[s].classList.toggle("active",selected);buttons[s].setAttribute("aria-pressed",String(selected));}
              // Crucially, do not rebuild the card or page after answering: this preserves focus and scroll.
              output.textContent="";
              updateSummary();persist();
            });
            choices.append(b);
          }
          card.append(choices);
        }
        if(x.sourceUrl){const a=link("Source / restaurant →",x.sourceUrl,"source-link");a.target="_blank";a.rel="noopener noreferrer";card.append(a);}
        list.append(card);
      });
      persist();
    }
    for(const b of areaButtons)b.addEventListener("click",()=>{active=b.dataset.area;page=0;render();});
    for(const b of screeningButtons)b.addEventListener("click",()=>{screen=b.dataset.screen;page=0;render();});
    if(previous)previous.addEventListener("click",()=>{if(page>0){page--;render();}});
    if(next)next.addEventListener("click",()=>{if((page+1)*batchSize<relevant().length){page++;render();}});
    byId("reset-interview").addEventListener("click",()=>{
      if(!window.confirm("Clear your locally saved interview answers? Historical confirmed responses will remain."))return;
      answers={};output.textContent="Local edits cleared; historical answers are unchanged.";updateSummary();render();
    });
    byId("copy-interview").addEventListener("click",async()=>{
      try{
        if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(summary.value);output.textContent="Answers copied. Paste them into ChatGPT for review.";}
        else {summary.focus();summary.select();output.textContent="Select and copy the highlighted answers.";}
      }catch(_){summary.focus();summary.select();output.textContent="Select and copy the highlighted answers.";}
    });
    updateSummary();render();
  }
  setActiveNav();
  const isInterview=page==="interview";
  const loadHosts={home:["featured-records","city-editions","shared-memory-records"],
    explore:["explore-results"],timeline:["timeline-results"],map:["culture-map","city-list"],
    record:["record-detail"],interview:["interview-list"]};
  const hosts=(loadHosts[page]||[]).map(byId).filter(Boolean);
  const controls=all("main button, main input, main select");
  const initiallyDisabled=new Map(controls.map(control=>[control,control.disabled]));
  let loadState="idle";
  async function boot(){
    if(loadState==="loading"||loadState==="loaded")return;
    const focusHost=hosts.find(host=>host.contains(document.activeElement));
    loadState="loading";
    controls.forEach(control=>{control.disabled=true;});
    hosts.forEach(host=>{
      host.setAttribute("aria-busy","true");
      const message=el("p","empty",isInterview?"Loading the interview…":"Loading the collection…");
      message.setAttribute("role","status");host.replaceChildren(message);
    });
    const controller=new AbortController();
    const timeout=setTimeout(()=>controller.abort(),15000);
    try{
      const r=await fetch(isInterview?"./data/interview.json":"./data/records.json",
        {cache:"no-cache",signal:controller.signal});
      if(!r.ok)throw Error("Culture data HTTP "+r.status);
      const db=await r.json();
      if(!db||typeof db!=="object"||
        (isInterview?!Array.isArray(db.candidates):!Array.isArray(db.records)||!Array.isArray(db.venues)))throw Error("Invalid culture data");
      controls.forEach(control=>{control.disabled=initiallyDisabled.get(control);});
      if(page==="home")home(db);
      if(page==="explore")explore(db);
      if(page==="timeline")timeline(db);
      if(page==="map")map(db);
      if(page==="record")detail(db);
      if(isInterview)interview(db);
      loadState="loaded";
      hosts.forEach(host=>host.setAttribute("aria-busy","false"));
      if(focusHost){
        focusHost.setAttribute("tabindex","-1");
        focusHost.focus({preventScroll:true});
      }
    }catch(err){
      loadState="error";
      controls.forEach(control=>{control.disabled=true;});
      hosts.forEach(host=>{
        empty(host,isInterview?"Unable to load the interview.":"Unable to load the archive.",
          "Check your connection, then try again.");
        host.setAttribute("aria-busy","false");
        const block=host.firstElementChild;block.setAttribute("role","status");
        const retry=el("button","button-main load-retry","Try again");
        retry.type="button";retry.addEventListener("click",boot);block.append(retry);
      });
      const status=byId(isInterview?"interview-page-state":page==="map"?"map-summary":"result-count");
      if(status)status.textContent=isInterview?"Interview unavailable.":"Collection unavailable.";
      if(window.console&&console.error)console.error("Culture Passport load error:",err);
    }finally{
      clearTimeout(timeout);
    }
  }
  boot();
})();
