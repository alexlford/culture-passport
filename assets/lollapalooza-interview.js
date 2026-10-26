(() => {
"use strict";
const source="./data/lollapalooza-2007-interview.json";
const storageKey="culture-passport-lolla-2007-private-interview-v1";
const root=document.getElementById("lolla-interview");
let model=null, answers={}, notes="", step=0, day="2007-08-03", search="", onlyOpen=false;
const $=(id)=>document.getElementById(id);
const node=(tag,cls,text)=>{const z=document.createElement(tag);if(cls)z.className=cls;if(text!==undefined)z.textContent=String(text);return z;};
const title=(s)=>s.artist;
const setById=(id)=>model.sets.find(s=>s.id===id);
const fmt=(minutes)=>{
  const hour=Math.floor(minutes/60),minute=minutes%60;
  return (hour%12||12)+":"+String(minute).padStart(2,"0")+(hour>=12?" PM":" AM");
};
function persist(){try{localStorage.setItem(storageKey,JSON.stringify({answers,notes,updated:new Date().toISOString()}));}catch(e){}}
function restore(){answers={...(model.answers||{})};try{const old=JSON.parse(localStorage.getItem(storageKey)||"{}");if(old.answers&&typeof old.answers==="object")answers={...answers,...old.answers};if(typeof old.notes==="string")notes=old.notes;}catch(e){}}
function status(id){return answers[id]||"unanswered";}
function counts(){const n=Object.values(answers);return {watched:n.filter(x=>x==="watched").length,part:n.filter(x=>x==="partial").length,no:n.filter(x=>x==="not_watched").length,unknown:n.filter(x=>x==="unsure").length};}
function progress(){
 const c=counts(),total=model.sets.length,reviewed=c.watched+c.part+c.no+c.unknown;
 $("lolla-progress").textContent=reviewed+" / "+total+" performers reviewed · "+(c.watched+c.part)+" marked watched or partly watched";
 $("lolla-summary").textContent=(c.watched+c.part)+" watched / partially watched · "+c.unknown+" uncertain · "+c.no+" not watched";
}
const choices=[
["watched","Watched"],
["partial","Caught part"],
["not_watched","Didn't watch"],
["unsure","Can't remember"]
];
function choose(id,value){answers[id]=value;persist();progress();renderDecisions();renderLineup();}
function choiceRow(set,context){
 const wrap=node("div","lolla-performer");
 const head=node("div","lolla-performer-header");
 head.append(node("strong","",title(set)),node("span","",set.stage+(set.scheduledStartMinutes!=null?" · "+fmt(set.scheduledStartMinutes)+"–"+fmt(set.scheduledEndMinutes):" · time not firmly established")));
 wrap.append(head);
 const buttons=node("div","lolla-choice-row");
 for(const [value,label] of choices){
  const b=node("button","lolla-choice",label);b.type="button";
  const selected=status(set.id)===value;b.classList.toggle("selected",selected);b.setAttribute("aria-pressed",String(selected));
  b.addEventListener("click",()=>choose(set.id,value));buttons.append(b);
 }
 wrap.append(buttons);
 return wrap;
}
const openStages=new Set(["AT&T","Bud Light"]);
const spotlightIds=["decision-03","decision-06","decision-07","decision-08","decision-09","decision-11","decision-12"];
function allSteps(){
 const special=model.conflicts.filter(c=>spotlightIds.includes(c.id));
 const more=model.conflicts.filter(c=>!spotlightIds.includes(c.id));
 return special.concat(more);
}
function renderDecisions(){
 const steps=allSteps();step=Math.min(step,steps.length-1);
 const cur=steps[step];const parent=$("lolla-current-decision");parent.replaceChildren();
 $("lolla-step").textContent="Checkpoint "+(step+1)+" of "+steps.length;
 const when=node("p","eyebrow",model.days.find(d=>d.date===cur.day).label+" · "+cur.label);
 parent.append(when,node("h2","",cur.setIds.length>1?"Which sets did you catch?":"Did you catch this set?"));
 const intro=node("p","lolla-guidance",cur.note+" You may mark multiple overlapping acts if you moved between stages.");
 parent.append(intro);
 cur.setIds.map(setById).filter(Boolean).forEach(set=>parent.append(choiceRow(set,"spotlight")));
 const recorded=cur.setIds.filter(id=>["watched","partial"].includes(status(id)));
 if(recorded.length>1)parent.append(node("p","lolla-conflict-warning","Multiple overlapping sets are marked watched. That's possible if you split your time; note the approximate portion below if you remember."));
 $("lolla-prev").disabled=step===0;
 $("lolla-next").textContent=step===steps.length-1?"Review all performers →":"Next checkpoint →";
}
function renderDays(){
 const tabs=$("lolla-day-tabs");tabs.replaceChildren();
 for(const d of model.days){
  const b=node("button","lolla-day-btn",d.label);b.type="button";b.setAttribute("aria-pressed",String(d.date===day));
  if(d.date===day)b.classList.add("selected");
  b.addEventListener("click",()=>{day=d.date;renderDays();renderLineup();});
  tabs.append(b);
 }
}
function renderLineup(){
 const target=$("lolla-stage-lineup");for(const previous of target.querySelectorAll("details.lolla-stage")){const which=previous.dataset.stage;if(previous.open)openStages.add(which);else openStages.delete(which);}target.replaceChildren();
 const stages=[...new Set(model.sets.filter(s=>s.day===day).map(s=>s.stage))];
 let visible=0;
 for(const stage of stages){
  const candidates=model.sets.filter(s=>s.day===day&&s.stage===stage&&(!onlyOpen||status(s.id)==="unanswered")&&(!search||s.artist.toLowerCase().includes(search.toLowerCase())));
  if(!candidates.length)continue;
  visible+=candidates.length;
  const details=node("details","lolla-stage");details.dataset.stage=stage;
  if(search||openStages.has(stage))details.open=true;
  const heading=node("summary","",stage+" · "+candidates.length+" performers");
  details.append(heading);details.addEventListener("toggle",()=>{if(details.open)openStages.add(stage);else openStages.delete(stage);});
  const desc=node("p","lolla-guidance","Artists are ordered as they appeared on the historical stage lineup; an exact time is shown only where independently established.");
  details.append(desc);
  candidates.sort((a,b)=>a.stageOrder-b.stageOrder).forEach(s=>details.append(choiceRow(s,"stage")));
  target.append(details);
 }
 if(!visible)target.append(node("p","lolla-guidance","No matching performers. Clear search or show previously reviewed sets."));
 const change=model.historicalChanges.find(x=>x.day===day);
 if(change)target.append(node("p","lolla-guidance","Historical schedule change: "+change.artist+" did not perform as initially billed; "+change.replacement+" was reported as the replacement. This canceled set is not treated as a visit."));
}
function report(){
 const selected=model.sets.filter(s=>["watched","partial"].includes(status(s.id)));
 const unsure=model.sets.filter(s=>status(s.id)==="unsure");
 const watched=selected.map(s=>({day:s.day,artist:s.artist,stage:s.stage,watched:status(s.id)==="watched"?"watched":"partly watched"}));
 const conflicts=model.conflicts.filter(c=>c.setIds.filter(id=>["watched","partial"].includes(status(id))).length>1).map(c=>({label:c.label,artists:c.setIds.filter(id=>["watched","partial"].includes(status(id))).map(id=>setById(id).artist)}));
 return {project:"Culture Passport",interview:"Lollapalooza 2007",festivalAttendance:"confirmed_all_three_days",userConfirmedSets:watched,unsureArtists:unsure.map(s=>({date:s.day,artist:s.artist})),answeredNotWatched:model.sets.filter(s=>status(s.id)==="not_watched").map(s=>({date:s.day,artist:s.artist})),overlapChecks:conflicts,notes,reminder:"Don't infer attendance for unreviewed performers. Multi-stage partial attendance may explain overlaps."};
}
function renderReport(){
 const obj=report();const perDay=model.days.map(d=>({day:d.label,artists:obj.userConfirmedSets.filter(s=>s.day===d.date).map(s=>s.artist+(s.watched==="partly watched"?" (part)":""))}));
 let out="CULTURE PASSPORT — LOLLAPALOOZA 2007 INTERVIEW\nAttendance: all 3 days confirmed\n\n";
 for(const d of perDay)out+=d.day+"\n"+(d.artists.length?d.artists.join("; "):"No individual acts marked watched yet")+"\n\n";
 out+="Overlap checks: "+obj.overlapChecks.length+"\n";
 for(const c of obj.overlapChecks)out+="  "+c.label+": "+c.artists.join(" / ")+"\n";
 if(obj.unsureArtists.length)out+="\nStill unsure: "+obj.unsureArtists.map(a=>a.artist+" ("+a.date+")").join("; ")+"\n";
 if(notes.trim())out+="\nPersonal memories: "+notes.trim()+"\n";
 out+="\nOnly explicitly selected bands are confirmed. Other entries are not automatically excluded.\n";
 $("lolla-export").value=out;
}
async function copy(){
 renderReport();
 const text=$("lolla-export").value;
 try{await navigator.clipboard.writeText(text);$("lolla-copy-status").textContent="Copied. Paste this in our ChatGPT conversation to update the private archive.";}
 catch(e){$("lolla-export").focus();$("lolla-export").select();$("lolla-copy-status").textContent="Select and copy the text above, then paste it into the conversation.";}
}
function start(){
 $("lolla-prev").addEventListener("click",()=>{step=Math.max(0,step-1);renderDecisions();});
 $("lolla-next").addEventListener("click",()=>{if(step<allSteps().length-1){step++;renderDecisions();}else{$("lolla-all-lineup").scrollIntoView({behavior:"smooth",block:"start"});}});
 $("lolla-search").addEventListener("input",e=>{search=e.target.value;renderLineup();});
 $("lolla-unanswered").addEventListener("change",e=>{onlyOpen=e.target.checked;renderLineup();});
 $("lolla-notes").value=notes;$("lolla-notes").addEventListener("input",e=>{notes=e.target.value;persist();});
 $("lolla-copy").addEventListener("click",copy);
 $("lolla-report").addEventListener("click",()=>{renderReport();$("lolla-report-section").scrollIntoView({behavior:"smooth"});});
 const sources=$("lolla-sources");
 model.sources.forEach(s=>{const a=node("a","text-link",s.role+" ↗");a.href=s.url;a.target="_blank";a.rel="noopener noreferrer";sources.append(a);});
 renderDays();renderDecisions();renderLineup();progress();renderReport();
}
fetch(source,{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("HTTP "+r.status);return r.json();}).then(data=>{
 if(data.version!==1||!Array.isArray(data.sets)||data.days.length!==3)throw Error("Incomplete historical lineup");
 model=data;restore();start();
}).catch(e=>{root.replaceChildren(node("p","lolla-guidance","The historical interview data could not load: "+e.message+". This interview needs the Culture Passport local preview or private source deployment."));});
})();
