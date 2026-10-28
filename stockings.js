/* Fresh stockings — Michigan DNR plants (stockings.json, refreshed every 6 h by GitHub Actions). */
(()=>{
const esc=x=>String(x??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const DIR=(la,ln)=>`https://www.google.com/maps/dir/?api=1&destination=${la},${ln}`;
const MON=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const pd=s=>{const[y,m,d]=s.split("-").map(Number);return new Date(y,m-1,d)};
const today=()=>{const t=new Date();return new Date(t.getFullYear(),t.getMonth(),t.getDate())};
const ago=s=>Math.round((today()-pd(s))/864e5);
const agoTxt=n=>n<=0?"today":n===1?"yesterday":n<60?`${n} days ago`:n<365?`${Math.round(n/30.4)} mo ago`:"1 yr+ ago";
const fdate=s=>{const d=pd(s);return `${MON[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`};
const sizeTxt=r=>r.len_in==null?"size n/a":`${r.len_in.toFixed(1)} in avg`;
const SK="stkFilter";let S={days:30,sp:"trout",sort:"new",all:false,n:20};try{S={...S,...JSON.parse(localStorage.getItem(SK)||"{}"),n:20}}catch(e){}
let D=null,BYX={};const STK=window.STK={ready:false};
const keep=r=>(S.all||r.catchable)&&(S.sp==="all"||r.is_salmonid);
const tier=n=>n<=14?"hot":n<=60?"warm":"old";
const STY={hot:{radius:10,color:"#fff",weight:3,fillColor:"#b03fd0",fillOpacity:1},warm:{radius:7,color:"#fff",weight:1.5,fillColor:"#7d5a8a",fillOpacity:.75},old:{radius:5,color:"#7d5a8a",weight:1,fillColor:"#7d5a8a",fillOpacity:.28,opacity:.45}};
const css=`#stksec{padding:0 var(--s2,16px)}
#stksec .stkhd{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;margin:4px 0 2px}
.stkf{display:flex;flex-wrap:wrap;gap:8px 10px;align-items:center;margin:10px 0 6px}
.seg{display:inline-flex;padding:2px;border-radius:10px;background:rgba(31,58,43,.08);gap:2px}
.seg button{white-space:nowrap;min-height:36px;padding:4px 14px;border:0;border-radius:8px;background:transparent;color:var(--g800);font-size:13px;font-weight:600;cursor:pointer;-webkit-tap-highlight-color:transparent}
.seg button.on{background:var(--paper,#fffdf7);color:var(--g800);box-shadow:0 1px 2px rgba(20,42,29,.18),0 1px 6px rgba(20,42,29,.08)}
.stkinc{display:inline-flex;align-items:center;gap:6px;font-size:13px;color:var(--mute);min-height:36px}
.stkbox{background:var(--paper);border:.5px solid var(--line);border-radius:var(--r,14px);box-shadow:var(--shadow-sm);padding:2px 12px}
.stkit{display:grid;grid-template-columns:46px 1fr auto;gap:2px 12px;align-items:center;padding:12px 2px;border-top:.5px solid var(--line);cursor:pointer;min-height:44px}
.stkit:first-child{border-top:0}.stkit:hover{background:rgba(31,58,43,.035)}
.stkago{width:44px;height:44px;border-radius:12px;display:flex;flex-direction:column;align-items:center;justify-content:center;font-weight:700;font-size:15px;line-height:1;background:rgba(125,90,138,.12);color:#5d3f69}
.stkago small{font-size:10px;font-weight:600;margin-top:3px;letter-spacing:.02em;opacity:.8}
.stkago.hot{background:#b03fd0;color:#fff}.stkago.old{background:rgba(31,58,43,.06);color:var(--mute)}
.stkit .nm{font-weight:600;letter-spacing:-.01em;line-height:1.3}.stkit .nm span{font-weight:500;color:var(--mute)}
.stkit .s2{font-size:13px;line-height:1.5;color:var(--ink2,#3a4a3f)}
.stkit .dr{text-align:right;font-size:13px;color:var(--mute);white-space:nowrap}.stkit .dr b{display:block;font-size:15px;color:var(--ink)}
.stkit .dr button{margin-top:4px;min-height:32px;padding:4px 10px;border-radius:999px;border:.5px solid var(--line2);background:var(--paper);color:var(--g800);font-size:12px;font-weight:600;cursor:pointer}
.stkflag{display:inline-flex;border-radius:999px;padding:1px 8px;font-size:11px;font-weight:600;background:rgba(184,134,11,.14);color:#7a5a06;margin-left:4px;vertical-align:1px}
.stkchip{display:inline-flex;align-items:center;border-radius:999px;padding:2px 9px;font-size:12px;font-weight:600;line-height:1.5;background:#b03fd0;color:#fff;white-space:nowrap;vertical-align:middle}
.stkchip.warm{background:rgba(125,90,138,.16);color:#5d3f69}
.stkmore{display:block;margin:8px auto 10px;min-height:40px;padding:6px 18px;border-radius:999px;border:.5px solid var(--line2);background:var(--paper);color:var(--g800);font-weight:600;cursor:pointer}
.stkpop{max-height:230px;overflow:auto;font-size:.86em}.stkpop>div{border-top:1px solid #e4dccb;padding:4px 0}
.stkleg{display:flex;gap:10px;flex-wrap:wrap;font-size:12px;color:var(--mute);margin:2px 0 8px}.stkleg i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:4px;vertical-align:-1px}
@media (max-width:700px){.seg{flex:1 1 40%}.seg.sdays{flex:1 1 100%}.seg button{flex:1;padding:4px 6px}.stkit{grid-template-columns:44px 1fr auto;gap:2px 10px}.stkit .dr b{font-size:14px}}`;
function popHtml(g){const rs=g.recs;const r0=rs[0];
 return `<b>🟣 ${esc(r0.water)}</b><br><span style="font-size:.82em">${esc(r0.county)} Co. · ${r0.precision==="county"?"county-level location (DNR gave no section)":"approximate: PLSS section "+esc(r0.trs||"(past plants)")}${r0.drive_min!=null?` · ${r0.drive_est?"~":""}${r0.drive_min} min from home`:""}</span>
 <div class="stkpop">${rs.slice(0,12).map(r=>{const n=ago(r.date);return `<div><b>${esc(fdate(r.date))}</b> · ${agoTxt(n)}<br>${esc(r.species)}${r.strain?` <span style="opacity:.7">(${esc(r.strain)})</span>`:""} · ${(r.count||0).toLocaleString()} fish · ${sizeTxt(r)}${r.site?`<br><span style="opacity:.75">Site: ${esc(r.site)}</span>`:""}${flagH(r)}</div>`}).join("")}${rs.length>12?`<div>+${rs.length-12} more</div>`:""}</div>
 <a href="${esc(D.meta.source_url)}" target="_blank">DNR stocking database ↗</a> · <a href="${DIR(r0.lat,r0.lng)}" target="_blank">Directions</a>`}
function flagH(r){const f=r.flags||[];return (f.includes("small")?'<span class="stkflag">under 6 in</span>':"")+(f.includes("private_plant")?'<span class="stkflag">private plant</span>':"")+(f.includes("great_lakes")?'<span class="stkflag">Great Lakes</span>':"")}
function groups(){const G={};for(const r of D.stockings){if(r.lat==null||!keep(r)||ago(r.date)<0)continue;const k=r.lat.toFixed(4)+","+r.lng.toFixed(4);(G[k]??={k,lat:r.lat,lng:r.lng,recs:[]}).recs.push(r)}
 return Object.values(G).map(g=>(g.recs.sort((a,b)=>b.date.localeCompare(a.date)),g.n=ago(g.recs[0].date),g)).sort((a,b)=>b.n-a.n)}
function paint(lg,mapRef,store){lg.clearLayers();if(store)for(const k in store)delete store[k];
 for(const g of groups()){const t=tier(g.n),m=L.circleMarker([g.lat,g.lng],{...STY[t]}).bindPopup(()=>popHtml(g),{maxWidth:innerWidth<700?250:290,autoPanPaddingTopLeft:L.point(60,16),autoPanPaddingBottomRight:L.point(16,16)});
  m.bindTooltip(`${esc(g.recs[0].water)} · ${agoTxt(g.n)}`,{direction:"top",offset:[0,-6]});m.addTo(lg);if(store)store[g.k]=m}}
const HOMEM={};let homeLG=null,xLG=null;
function attachHome(){const LY=window._LY,map=window._map;if(!LY||!map||homeLG)return!!homeLG;homeLG=L.layerGroup();LY.stock.addLayer(homeLG);paint(homeLG,map,HOMEM);return true}
STK.attachX=(xmap)=>{if(!xmap)return;STK._xmap=xmap;if(!D)return;if(!xLG){xLG=L.layerGroup();const on=localStorage.getItem("xStkOff")!=="1";if(on)xLG.addTo(xmap);
  const c=L.control({position:"topright"});c.onAdd=()=>{const d=L.DomUtil.create("div","xleg");d.style.cssText="padding:6px 10px;font-size:12px";d.innerHTML=`<label style="display:flex;align-items:center;gap:6px;min-height:28px"><input type="checkbox" id="xStkT"${on?" checked":""}> <i style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#b03fd0"></i> DNR stockings (12 mo, ≤14 d bright)</label>`;L.DomEvent.disableClickPropagation(d);
   setTimeout(()=>{const b=document.getElementById("xStkT");if(b)b.onchange=()=>{localStorage.setItem("xStkOff",b.checked?"0":"1");b.checked?xLG.addTo(xmap):xmap.removeLayer(xLG)}},0);return d};c.addTo(xmap)}
 paint(xLG,xmap,null)};
STK.latest=id=>(BYX[id]||[]).find(r=>ago(r.date)>=0);
STK.chip=(id,days=30)=>{const r=STK.latest(id);if(!r)return"";const n=ago(r.date);if(n>days||n<0)return"";return `<span class="stkchip${n>14?" warm":""}" title="${esc(`${r.species} · ${(r.count||0).toLocaleString()} · ${sizeTxt(r)} · ${r.water}, ${fdate(r.date)} (DNR)`)}">Stocked ${n===0?"today":n===1?"1 day ago":n+" days ago"}${(r.flags||[]).includes("small")?" · fingerlings":""}</span>`};
function focus(k){const map=window._map,m=HOMEM[k];if(!map||!m)return;
 const body=document.getElementById("mapBody"),hd=document.getElementById("mapHead");if(body&&body.style.display==="none"&&hd)hd.click();
 if(window._hid&&window._hid.has("stock")){window._hid.delete("stock");window._saveHid&&window._saveHid();const b=document.querySelector('.maplegend button[data-l="stock"]');b&&b._ap&&b._ap();window._lgSync&&window._lgSync()}
 document.getElementById("map").scrollIntoView({behavior:"smooth",block:"center"});setTimeout(()=>{map.invalidateSize();map.setView(m.getLatLng(),11,{animate:false});m.openPopup()},350)}
function render(){const el=document.getElementById("stkList");if(!el||!D)return;localStorage.setItem(SK,JSON.stringify({days:S.days,sp:S.sp,sort:S.sort,all:S.all}));
 document.querySelectorAll("#stkFilt [data-k]").forEach(b=>b.classList.toggle("on",String(S[b.dataset.k])===b.dataset.v));document.getElementById("stkAll").checked=S.all;
 let L0=D.stockings.filter(r=>{if(!r.date||!keep(r))return false;const n=ago(r.date);return n>=0&&n<=S.days});
 L0.sort(S.sort==="near"?(a,b)=>(a.drive_min??1e4)-(b.drive_min??1e4)||b.date.localeCompare(a.date):(a,b)=>b.date.localeCompare(a.date)||(a.drive_min??1e4)-(b.drive_min??1e4));
 const near=L0.filter(r=>r.is_trout&&(r.drive_min??1e4)<=90).length;
 document.getElementById("stkSum").innerHTML=`<b>${L0.length}</b> plant${L0.length===1?"":"s"} in the last ${S.days===365?"12 months":S.days+" days"} · <b>${near}</b> trout within 90 min of home`;
 el.innerHTML=L0.length?L0.slice(0,S.n).map(r=>{const n=ago(r.date),k=r.lat!=null?r.lat.toFixed(4)+","+r.lng.toFixed(4):"";
  return `<div class="stkit" data-k="${k}" role="button" tabindex="0"><div class="stkago ${tier(n)}">${n<1?"new":n<60?n:Math.round(n/30.4)}<small>${n<1?"today":n===1?"day":n<60?"days":"mo"}</small></div>
  <div><div class="nm">${esc(r.species)} <span>· ${esc(r.water)}</span></div><div class="s2">${(r.count||0).toLocaleString()} fish · ${sizeTxt(r)} · ${esc(fdate(r.date))} · ${esc(r.county)} Co.${flagH(r)}</div></div>
  <div class="dr">${r.drive_min!=null?`<b>${r.drive_est?"~":""}${r.drive_min} min</b>${r.drive_miles} mi`:"—"}${k?`<br><button type="button" data-focus="${k}" aria-label="Show on map">Map</button>`:""}</div></div>`}).join("")+(L0.length>S.n?`<button class="stkmore" id="stkMore">Show ${Math.min(30,L0.length-S.n)} more of ${L0.length-S.n}</button>`:"")
  :`<div class="sub" style="padding:14px 4px">No ${S.sp==="trout"?"trout or salmon ":""}plants posted in the last ${S.days} days${S.all?"":" (catchable size, public)"}. The DNR stocks mostly Mar–Jun with a few fall plants, and records can take a couple of weeks to post. <a href="#" id="stkWiden">Show the last ${S.days<90?90:365} days</a></div>`;
 const mo=document.getElementById("stkMore");if(mo)mo.onclick=e=>{e.stopPropagation();S.n+=30;render()};
 const w=document.getElementById("stkWiden");if(w)w.onclick=e=>{e.preventDefault();S.days=S.days<90?90:365;render()}}
function build(){const anchor=document.getElementById("regsec")||document.getElementById("runsec");if(!anchor||document.getElementById("stksec"))return;
 const st=document.createElement("style");st.textContent=css;document.head.appendChild(st);
 const sec=document.createElement("section");sec.id="stksec";
 sec.innerHTML=`<details id="stkDet" open><summary class="sec2">Fresh stockings</summary>
 <div class="sub stkhd"><span id="stkSum">Loading DNR stocking reports…</span></div>
 <div class="stkf" id="stkFilt" role="toolbar" aria-label="Stocking filters">
  <div class="seg sdays">${[[14,"14 d"],[30,"30 d"],[90,"90 d"],[365,"12 mo"]].map(([v,t])=>`<button type="button" data-k="days" data-v="${v}">${t}</button>`).join("")}</div>
  <div class="seg"><button type="button" data-k="sp" data-v="trout">Trout &amp; salmon</button><button type="button" data-k="sp" data-v="all">All</button></div>
  <div class="seg"><button type="button" data-k="sort" data-v="new">Newest</button><button type="button" data-k="sort" data-v="near">Closest</button></div>
  <label class="stkinc"><input type="checkbox" id="stkAll"> Include fry, fingerlings &amp; private plants</label></div>
 <div class="stkleg"><span><i style="background:#b03fd0"></i>≤14 days</span><span><i style="background:#7d5a8a;opacity:.75"></i>15–60 days</span><span><i style="background:#7d5a8a;opacity:.3"></i>older · 🟣 map layer</span></div>
 <div class="stkbox" id="stkList"></div><div class="sub" id="stkSrc" style="margin:8px 0 0"></div></details>`;
 anchor.before(sec);
 {const c=document.getElementById("calDet");if(c)sec.querySelector("#stkDet").appendChild(c)}
 sec.querySelector("#stkFilt").onclick=e=>{const b=e.target.closest("[data-k]");if(!b)return;const k=b.dataset.k;S[k]=k==="days"?+b.dataset.v:b.dataset.v;S.n=20;render()};
 sec.querySelector("#stkAll").onchange=e=>{S.all=e.target.checked;S.n=20;render();refreshMaps()};
 sec.querySelector("#stkFilt").addEventListener("click",e=>{if(e.target.closest('[data-k="sp"]'))refreshMaps()});
 const list=sec.querySelector("#stkList");list.onclick=e=>{const it=e.target.closest("[data-k]");if(it&&it.dataset.k)focus(it.dataset.k)};
 list.onkeydown=e=>{if(e.key==="Enter"){const it=e.target.closest("[data-k]");if(it&&it.dataset.k)focus(it.dataset.k)}}}
function refreshMaps(){if(homeLG)paint(homeLG,window._map,HOMEM);if(xLG&&STK._xmap)paint(xLG,STK._xmap,null)}
async function load(){build();try{D=await (await fetch("stockings.json?v="+Math.floor(Date.now()/36e5))).json()}catch(e){const s=document.getElementById("stkSum");if(s)s.textContent="Couldn't load stocking data.";console.warn("stockings",e);return}
 BYX={};for(const r of D.stockings)for(const id of r.explore||[])(BYX[id]??=[]).push(r);for(const id in BYX)BYX[id].sort((a,b)=>b.date.localeCompare(a.date));
 const m=D.meta;document.getElementById("stkSrc").innerHTML=`Source: <a href="${esc(m.source_url)}" target="_blank">Michigan DNR Fish Stocking Database</a> (public record), checked every 6 hours${m.generated?` · data changed ${esc(new Date(m.generated).toLocaleString("en-US",{month:"short",day:"numeric",hour:"numeric",minute:"2-digit"}))} ET`:""} · newest record ${esc(fdate(m.latest_stocking))}. DNR posts plants after a clean-up step, so they can lag a week or two. Locations are approximate (survey-section centers, ~1 mi). Drive times are free-flow from home. By default this hides fish under 6 in and private plants, like StockedMI.`;
 render();STK.ready=true;rehome();
 const tryHome=()=>{if(!attachHome())setTimeout(tryHome,400)};tryHome();
 if(!STK._xmap&&window._xmap)STK._xmap=window._xmap;if(STK._xmap)STK.attachX(STK._xmap);
 dispatchEvent(new Event("stk-ready"))}
// Signed-in accounts (accounts.js) can set their own home base: re-estimate drive times from it (straight-line ×1.25 at ~50 mph), no extra network calls.
function rehome(n=0){const F=window.FRA,p=F&&F.on&&F.profile&&F.profile();if(!p||p.home_lat==null||p.home_lon==null){if(window.FRA&&FRA.configured&&n<20)setTimeout(()=>rehome(n+1),1000);return}
 const H=D.meta.home||{},hv=(a,b,c,d)=>{const r=Math.PI/180;return 7917.6*Math.asin(Math.sqrt(Math.sin((c-a)*r/2)**2+Math.cos(a*r)*Math.cos(c*r)*Math.sin((d-b)*r/2)**2))};
 if(H.lat!=null&&hv(H.lat,H.lng,+p.home_lat,+p.home_lon)<=0.6)return;
 for(const r of D.stockings){if(r.lat==null){r.drive_min=r.drive_miles=null;continue}const mi=hv(+p.home_lat,+p.home_lon,r.lat,r.lng)*1.25;r.drive_miles=Math.round(mi);r.drive_min=Math.round(mi/50*60+5);r.drive_est=true}
 const s=document.getElementById("stkSrc");if(s)s.innerHTML=s.innerHTML.replace("Drive times are free-flow from home.","Drive times are rough estimates from "+esc(p.home_label||"your home base")+" (straight-line × 1.25 at ~50 mph).");
 render();refreshMaps()}
document.readyState==="loading"?addEventListener("DOMContentLoaded",load):load();
})();
