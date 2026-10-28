// Section-jump nav: left rail on wide screens, sticky swipeable pill row on phones. Scroll-spy via IntersectionObserver.
(()=>{
const HOME=[["wxsec","Weather & bite"],["mapsec","Map & log"],["stksec","Fresh stockings"],["regsec","Seasons & regs"],["runsec","Run"],["hatchsec","Hatches"],["gagesec","River gages"]];
const EXPL=[["xFiltSec","Filters"],["xmap","Map"],["xTripSec",null],["xPlanSec","Trip planner"],["xWishSec","Want to fish"],["xNotesSec","Notes"]];
const css=`#secnav{position:sticky;top:var(--sntop,0px);z-index:3900;background:rgba(244,240,230,.88);-webkit-backdrop-filter:saturate(180%) blur(20px);backdrop-filter:saturate(180%) blur(20px);border-bottom:.5px solid var(--line2)}
#secnav[hidden]{display:none}
#secnav .snh{display:none}
#secnav ol{list-style:none;margin:0;padding:8px var(--s2);display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch;scroll-padding:0 var(--s2)}
#secnav ol::-webkit-scrollbar{display:none}
#secnav li{flex:none}
#secnav a{display:inline-flex;align-items:center;min-height:36px;padding:0 14px;border-radius:var(--pill);background:rgba(31,58,43,.07);color:var(--g800);font-size:13px;font-weight:600;letter-spacing:-.005em;text-decoration:none;white-space:nowrap;transition:background-color .2s var(--ease),color .2s var(--ease)}
#secnav a:hover{background:rgba(31,58,43,.12)}
#secnav a.on{background:var(--g800);color:var(--cream);box-shadow:0 1px 2px rgba(20,42,29,.22)}
@media (min-width:960px){
 #secnav{position:fixed;top:calc(var(--sntop,64px) + var(--s3));left:max(16px,calc((100vw - 1200px)/2 - 184px));width:168px;max-height:calc(100vh - var(--sntop,64px) - 48px);overflow-y:auto;background:transparent;-webkit-backdrop-filter:none;backdrop-filter:none;border:0}
 #secnav .snh{display:block;padding:0 12px 8px;font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--mute)}
 #secnav ol{flex-direction:column;gap:2px;padding:0;overflow:visible}
 #secnav a{display:flex;position:relative;width:100%;box-sizing:border-box;min-height:36px;padding:0 12px 0 14px;border-radius:10px;background:transparent;color:var(--ink2);font-size:14px;font-weight:500}
 #secnav a:before{content:"";position:absolute;left:3px;top:10px;bottom:10px;width:3px;border-radius:2px;background:transparent;transition:background-color .2s var(--ease)}
 #secnav a:hover{background:rgba(31,58,43,.06);color:var(--g800)}
 #secnav a.on{background:rgba(31,58,43,.08);color:var(--g800);font-weight:600;box-shadow:none}
 #secnav a.on:before{background:var(--g800)}
 body.snrail .statusline{padding-left:calc(var(--s2) + max(0px,calc(200px - max(0px,(100vw - 1200px)/2))))}
 body.snrail #homeView{padding-left:max(0px,calc(200px - max(0px,(100vw - 1200px)/2)))}
 body.snrail #exploreView{padding-left:max(var(--s2),calc(216px - max(0px,(100vw - 1200px)/2)))}
}
body.xlock #secnav{visibility:hidden}`;
const st=document.createElement("style");st.textContent=css;document.head.appendChild(st);
const RM=matchMedia("(prefers-reduced-motion: reduce)"),WIDE=matchMedia("(min-width:960px)");
const $=id=>document.getElementById(id),bar=document.querySelector("header.appbar");
const nav=document.createElement("nav");nav.id="secnav";nav.setAttribute("aria-label","Jump to section");nav.hidden=true;
nav.innerHTML=`<div class="snh">On this page</div><ol></ol>`;(bar?bar.after(nav):document.body.prepend(nav));
const ol=nav.querySelector("ol");let pin=null,items=[],io=null,vis=new Map(),active=null,lock=0,sig="";
const view=()=>$("exploreView")&&!$("exploreView").hidden?"explore":"home";
function list(){const v=view(),root=$(v==="home"?"homeView":"exploreView"),out=[];
 for(const [id,lab] of v==="home"?HOME:EXPL){const el=$(id);if(!el||!root.contains(el))continue;
  let l=lab;if(!l){const s=el.querySelector("summary");l=s?s.textContent.split(" · ")[0].replace(/\s*\(.*$/,"").trim():id}
  out.push({id,lab:l,el})}
 return out.sort((a,b)=>a.el.compareDocumentPosition(b.el)&Node.DOCUMENT_POSITION_FOLLOWING?-1:1)}
let lastTop=-1,lastOff=-1;
function metrics(){const h=bar?bar.offsetHeight+(parseFloat(getComputedStyle(bar).top)||0):0,top=Math.max(0,Math.round(h));
 if(top!==lastTop){lastTop=top;document.documentElement.style.setProperty("--sntop",top+"px")}
 const off=top+(WIDE.matches||nav.hidden?0:nav.offsetHeight)+12;if(off!==lastOff){lastOff=off;for(const it of items)it.el.style.scrollMarginTop=off+"px"}return off}
function build(){const L=list(),s=view()+":"+L.map(i=>i.id+"="+i.lab).join("|");
 const show=L.length>=2;nav.hidden=!show;document.body.classList.toggle("snrail",show&&WIDE.matches);
 if(s===sig){metrics();return}sig=s;items=L;lastOff=-1;
 ol.innerHTML=L.map(i=>`<li><a href="#${i.id}" data-id="${i.id}">${i.lab.replace(/&/g,"&amp;").replace(/</g,"&lt;")}</a></li>`).join("");
 active=null;spy();metrics();setTimeout(()=>{map();pick()},0)}
function openIn(el){if(el.id==="mapsec"){const b=$("mapBody"),h=$("mapHead");if(b&&b.style.display==="none"&&h)h.click();return}
 const d=el.tagName==="DETAILS"?el:el.querySelector(":scope>details");if(d&&!d.open)d.open=true}
function setActive(id,fromClick){if(id===active)return;active=id;
 ol.querySelectorAll("a").forEach(a=>{const on=a.dataset.id===id;a.classList.toggle("on",on);on?a.setAttribute("aria-current","true"):a.removeAttribute("aria-current")});
 if(!WIDE.matches){const a=ol.querySelector(`a[data-id="${id}"]`);if(a){const x=a.parentElement.offsetLeft-(ol.clientWidth-a.parentElement.offsetWidth)/2;ol.scrollTo({left:Math.max(0,x),behavior:RM.matches?"auto":"smooth"})}}}
function jump(id){const it=items.find(i=>i.id===id);if(!it)return;openIn(it.el);metrics();setActive(id,true);pin={id,y:null};lockFor(400);
 requestAnimationFrame(()=>it.el.scrollIntoView({behavior:RM.matches?"auto":"smooth",block:"start"}))}
ol.addEventListener("click",e=>{const a=e.target.closest("a[data-id]");if(!a)return;e.preventDefault();jump(a.dataset.id)});
function pick(){if(lock||!items.length)return;if(pin){if(pin.y===null)pin.y=scrollY;if(Math.abs(scrollY-pin.y)<6)return setActive(pin.id)}pin=null;
 // active = the last section whose top has reached the band under the sticky header; at the very bottom, the last one in view
 const off=metrics(),th=off+Math.min(200,innerHeight*.3);let best=items[0];for(const i of items){const r=i.el.getBoundingClientRect();if((i.el.offsetWidth||i.el.offsetHeight)&&r.top<=th)best=i}
 if(innerHeight+scrollY>=document.documentElement.scrollHeight-2){for(const i of items){const r=i.el.getBoundingClientRect();if(r.top<innerHeight*.6&&r.top>th)best=i}}
 setActive(best.id)}
function map(){vis.clear();for(const i of items){const r=i.el.getBoundingClientRect(),off=metrics(),band=innerHeight*.4;vis.set(i.id,r.bottom>off&&r.top<off+band&&!!(i.el.offsetWidth||i.el.offsetHeight))}}
function spy(){if(io)io.disconnect();vis.clear();if(!("IntersectionObserver"in window)||!items.length)return;
 const off=metrics();io=new IntersectionObserver(es=>{for(const e of es)vis.set(e.target.id,e.isIntersecting);pick()},{rootMargin:`-${off}px 0px -60% 0px`,threshold:0});
 items.forEach(i=>io.observe(i.el))}
let lt=0;function lockFor(ms){lock=1;clearTimeout(lt);lt=setTimeout(unlock,ms)}function unlock(){clearTimeout(lt);if(!lock)return;lock=0;if(pin)pin.y=scrollY;pick()}
let sf=0;addEventListener("scroll",()=>{if(lock)return lockFor(180);if(sf)return;sf=requestAnimationFrame(()=>{sf=0;pick()})},{passive:true});
if("onscrollend"in window)addEventListener("scrollend",()=>{lock?unlock():pick()});
let rt=0;const relayout=()=>{clearTimeout(rt);rt=setTimeout(()=>{document.body.classList.toggle("snrail",!nav.hidden&&WIDE.matches);spy();map();pick()},120)};
addEventListener("resize",relayout);WIDE.addEventListener&&WIDE.addEventListener("change",relayout);
let bt=0;const rebuild=()=>{clearTimeout(bt);bt=setTimeout(build,60)};
const mo=new MutationObserver(rebuild);
const watch=()=>{const h=$("homeView"),x=$("exploreView");if(h)mo.observe(h,{attributes:true,attributeFilter:["hidden"],childList:true});if(x)mo.observe(x,{attributes:true,attributeFilter:["hidden"],childList:true});build()};
document.readyState==="loading"?addEventListener("DOMContentLoaded",watch):watch();
addEventListener("load",()=>{metrics();spy()});
window.SECNAV={jump,build,active:()=>active};
})();
