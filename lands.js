/* Land ownership / parcel / basemap layers for both Leaflet maps.
   Sources are free, keyless, public REST endpoints (verified CORS). Reference only, not a legal survey. */
(function(){
"use strict";
const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const trim=s=>s==null?"":String(s).trim();
const num=(v,d=1)=>v==null||v===""||isNaN(+v)?"":(+v).toLocaleString(undefined,{maximumFractionDigits:d});
const PADUS="https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Manager_Name_PADUS/FeatureServer/0";
const DNR="https://services3.arcgis.com/Jdnp1TjADvSDxMAX/arcgis/rest/services/";
const MT={FED:["Federal","#9a5b2e"],STAT:["State","#2f7d32"],LOC:["Local / county / Metroparks","#1f8a8a"],NGO:["Conservancy (NGO)","#7b5ea7"],DIST:["Special district","#6b6b6b"],JNT:["Joint","#6b6b6b"],TRIB:["Tribal","#8a6d1f"],UNK:["Unknown","#6b6b6b"]};
const mcol=t=>(MT[t]||MT.UNK)[1];
const PA={OA:"Open access",RA:"Restricted access (permit, fee or seasonal)",XA:"Closed to public",UK:"Unknown"};
const PCLS={"1":"Agricultural","2":"Commercial","3":"Industrial","4":"Residential","5":"Timber-cutover","6":"Developmental"};
const pcls=c=>{c=trim(c);if(!c)return"";const m=c.match(/^(\d)/);return esc(c)+(m&&PCLS[m[1]]&&!/[a-z]/i.test(c)?" ("+PCLS[m[1]]+")":"")};
const DIV={FRD:"DNR Forest Resources",PRD:"DNR Parks & Recreation",WLD:"DNR Wildlife",FD:"DNR Fisheries"};
// County parcel services. bbox = [s,w,n,e] generous county extents, used only to decide which services to ask.
const PARCELS=[
 {c:"Macomb",src:"Macomb County GIS",url:"https://services6.arcgis.com/K0qS4r8AEJxrE8em/arcgis/rest/services/Macomb_County_Parcel_Data/FeatureServer/10",bb:[42.44,-83.13,42.90,-82.68],
  f:p=>({id:p.TAX_ID,own:p.ownername1,addr:[p.propstreetcombined,p.propertyCityStateZip].filter(Boolean).join(", "),cvt:p.CVT_NAME,zon:p.zoning,link:p.TAX_URL})},
 {c:"Oakland",src:"Oakland County Tax Parcel Plus",url:"https://gisservices.oakgov.com/arcgis/rest/services/Enterprise/EnterpriseOpenParcelDataMapService/MapServer/1",bb:[42.42,-83.70,42.90,-83.07],
  f:p=>({id:p.PIN,own:trim(p.NAME1)||null,noown:"not published in Oakland's open parcel data",addr:[p.SITEADDRESS,p.SITECITY].filter(Boolean).join(", "),cvt:p.CVTTAXDESCRIPTION,cls:p.CLASSCODE,ac:p["Shape.area"]?p["Shape.area"]/43560:null,acapprox:1})},
 {c:"Lapeer",src:"Lapeer County Road Commission Parcels_2023 (2023 snapshot)",url:"https://services8.arcgis.com/n1QQsnAVBkeegRxs/arcgis/rest/services/Parcels_2023/FeatureServer/0",bb:[42.86,-83.48,43.33,-82.98],
  f:p=>({id:p.PID,own:p.Owner,addr:[[p.pNumber,trim(p.pDir),p.pStreet].filter(Boolean).join(" "),p.City].filter(Boolean).join(", "),cls:p.Class,ac:p.MapAcres})},
 {c:"St. Clair",src:"St. Clair County TaxParcels_Nightly",url:"https://maps.stclaircounty.org/GeoCortex_wa/rest/services/Public_GISweb/TaxParcels_Nightly/MapServer/0",bb:[42.48,-83.00,43.24,-82.40],
  f:p=>({id:p.PARCEL_NUMBER,own:[trim(p.OWNER),trim(p.OWNER2)].filter(Boolean).join(" / "),addr:p.PROP_ADDRESS_COMBINED,cls:p.PROP_CLASS,ac:p.Keyd_Acres||p.Calc_Acres})},
 {c:"Genesee",src:"Genesee County (GCDCWWS) Parcels2025County",url:"https://services2.arcgis.com/PrYwGqAi1wKjoFb1/arcgis/rest/services/Parcels2025County/FeatureServer/0",bb:[42.76,-83.95,43.23,-83.45],
  f:p=>({id:p.ParcelID,own:p.OwnName,addr:[p.PropComb,p.PropCity].filter(Boolean).join(", "),cls:p.PropClass,ac:p.AcreCalcNM})},
 {c:"Kent",src:"Kent County ParcelsWithCondos",url:"https://gis.kentcountymi.gov/agisprod/rest/services/ParcelsWithCondos/FeatureServer/0",bb:[42.76,-85.80,43.47,-85.29],
  f:p=>({id:p.PNUM,own:[trim(p.OWNERNAME1),trim(p.OWNERNAME2)].filter(Boolean).join(" / "),addr:[trim(p.PROPERTYADDRESS),trim(p.PROPADDRESSCITY)].filter(Boolean).join(", "),cls:p.PROPERTYCLASS,ac:p.ACREAGE})},
 {c:"Barry",src:"Barry County Parcels (Open Data)",url:"https://services.arcgis.com/i0SsdDzLI3mLGmPR/arcgis/rest/services/Parcels_OpenData_View/FeatureServer/14",bb:[42.42,-85.56,42.78,-85.07],
  f:p=>({id:p.Tparcel,own:null,noown:"not published in Barry's open data",ac:p.Acres})}
];
const MISSING="No free public parcel service found for Washtenaw or Livingston (county services need a login), or for Crawford, Kalkaska, Lake, Wexford, Manistee, Oscoda, Otsego, Missaukee, Osceola, Newaygo, Roscommon and the other northern counties (paid or viewer-only systems). Up north, use the public-land, DNR and Commercial Forest layers.";
const rcol=p=>{const g=p.GearRestriction,t=p.StreamType||"";if(g)return"#d0282e";if(/^Type 1/.test(t))return"#2e9e46";if(/^Type 2/.test(t))return"#e3c21b";if(/^Type 3/.test(t))return"#ef8a1c";if(/^Type 4/.test(t))return"#2c6fd6";return"#777"};
const LAY={
 pub:{lab:"🏛️ Public land",def:1,minZ:10,url:PADUS,where:"FeatClass='Fee' AND Own_Type<>'PVT'",out:"FeatClass,Own_Type,Loc_Own,Mang_Type,Loc_Mang,Des_Tp,Unit_Nm,GIS_Acres,Pub_Access",
  st:f=>({color:mcol(f.properties.Mang_Type),weight:1,opacity:.9,fillColor:mcol(f.properties.Mang_Type),fillOpacity:.3})},
 ease:{lab:"🤝 Conservation easements",minZ:11,url:PADUS,where:"FeatClass='Easement'",out:"FeatClass,Own_Type,Loc_Own,Mang_Type,Loc_Mang,Des_Tp,Unit_Nm,GIS_Acres,Pub_Access",
  st:()=>({color:"#b8860b",weight:1.6,dashArray:"5 4",opacity:.95,fillColor:"#b8860b",fillOpacity:.08})},
 lots:{lab:"🌲 DNR state land",def:1,minZ:11,url:DNR+"DNRLOTSParcelsOPENDATA/FeatureServer/2",where:"1=1",out:"County,ProjectName,ProjectUseType,DivisionDepartment,Acreage,LandStatus,TransactionType,ParcelType",
  st:f=>/^Acquired (Easement|Lease)/.test(f.properties.TransactionType||"")?{color:"#1e5e22",weight:1.4,dashArray:"5 4",opacity:.9,fillColor:"#2f7d32",fillOpacity:.05}:{color:"#1e5e22",weight:.8,opacity:.7,fillColor:"#3a9a3e",fillOpacity:.28}},
 cfa:{lab:"🪓 Commercial Forest",minZ:10,url:DNR+"CommercialForestOPENDATA/FeatureServer/0",where:"1=1",out:"parid,GISAcres",
  st:()=>({color:"#c0602a",weight:1.2,opacity:.9,fillColor:"#e08a3c",fillOpacity:.22,dashArray:"2 3"})},
 bal:{lab:"🚤 DNR boat launches",minZ:9,pt:1,url:DNR+"Boat_Launches/FeatureServer/0",where:"1=1",out:"SiteName,WaterBody,Owner,Type,SiteManager,TotalParking,AccessFee,AccessCost,County,RampCode,CarryDown,PublicPhone"},
 regs:{lab:"🎣 Trout regs (DNR)",minZ:10,line:1,url:DNR+"DNRFisheriesTroutRegsOPENDATA/FeatureServer/0",where:"isActive=1 AND (StreamType<>'Unclassified' OR GearRestriction IS NOT NULL)",out:"DNRName,StreamType,GearRestriction,RegulationDesc,FSeasonStart,FSeasonEnd,PSeasonStart,PSeasonEnd,DPL,Tackle,GRFSeasonStart,GRFSeasonEnd,GRPSeasonStart,GRPSeasonEnd,GRDPL,GRTackle,GRSL,GRLocDesc,GRMileage",
  st:f=>({color:rcol(f.properties),weight:f.properties.GearRestriction?4.5:3,opacity:.9})},
 tt:{lab:"⭐ DNR Trout Trails",minZ:7,pt:1,col:"#b8860b",url:DNR+"TroutTrailPointsOpenData/FeatureServer/0",where:"1=1",out:"locationname,locationdesignation,speciesdescription,locationcounty,locationdescription,locationdirections,regionalvisitorurl"},
 par:{lab:"📐 Parcel lines",minZ:14,par:1}
};
const SW=k=>({pub:"",ease:'<i style="border:2px dashed #b8860b;background:rgba(184,134,11,.08)"></i>',lots:'<i style="border:1px solid #1e5e22;background:rgba(58,154,62,.45)"></i>',cfa:'<i style="border:2px dotted #c0602a;background:rgba(224,138,60,.3)"></i>',bal:'<i style="background:#1d5fa8;border-radius:50%"></i>',par:'<i style="border:2px solid #7a2e1d;background:transparent"></i>',tt:'<i style="background:#b8860b;border-radius:50%"></i>'}[k]);
const css=`.lndc{background:rgba(251,247,236,.97);border:1px solid var(--line2);border-radius:10px;box-shadow:var(--shadow-sm);color:var(--ink);font-size:13px;max-width:min(300px,78vw)}
.lndc>.lndt{display:block;min-height:40px;padding:8px 12px;font-weight:700;color:var(--g800);background:none;border:0;cursor:pointer;font-size:13px;width:100%;text-align:left}
.lndc .lndb{padding:0 10px 10px;max-height:min(52vh,430px);overflow:auto}.lndc.shut .lndb{display:none}
.lndc .lnr{display:flex;flex-wrap:wrap;gap:5px;margin:4px 0 6px}.lndc .lnr button{min-height:34px;padding:5px 10px;border-radius:18px;border:1px solid var(--line2);background:var(--paper);color:var(--ink);font-size:12px;font-weight:600;cursor:pointer}
.lndc .lnr button.off{opacity:.55;text-decoration:line-through;background:transparent;font-weight:400}.lndc .lnr button.sel{background:var(--g800);color:var(--cream);border-color:var(--g800)}
.lndc .lnh{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--mute);margin-top:6px}.lndc .lnk{line-height:1.6;font-size:12px}.lndc i{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:5px;vertical-align:-2px}
.lndc .lns{font-size:12px;color:var(--g700);margin:6px 0;min-height:1em}.lndc .lnd{font-size:11px;color:var(--mute);line-height:1.4;border-top:1px solid var(--line);padding-top:6px;margin-top:6px}
.lndc .lnwarn{font-size:12px;color:var(--bad,#8a2a1a);margin:4px 0}.lndc summary{cursor:pointer;font-size:12px;font-weight:700;color:var(--g800);padding:4px 0}
.lnpop h4{margin:8px 0 2px;font-size:13px;color:var(--g800)}.lnpop h4:first-child{margin-top:0}.lnpop .sm{font-size:11px;color:var(--mute)}.lnpop{font-size:12.5px;line-height:1.45}
@media(max-width:700px){.lndc{font-size:12px;max-width:66vw}.lndc>.lndt{min-height:36px;padding:6px 10px;font-size:12px}.lndc .lnb,.lndc .lndb{max-height:46vh}.lndc .lnr{gap:4px}.lndc .lnr button{min-height:34px;padding:4px 9px;font-size:11.5px}.lndc .lnh{margin-top:3px}.lndc .lns{font-size:11px}}`;
document.head.appendChild(Object.assign(document.createElement("style"),{textContent:css}));

function pip(pt,g){ // point-in-polygon for GeoJSON Polygon/MultiPolygon; pt=[lng,lat]
 const ring=(r)=>{let c=false;for(let i=0,j=r.length-1;i<r.length;j=i++){const xi=r[i][0],yi=r[i][1],xj=r[j][0],yj=r[j][1];if(((yi>pt[1])!==(yj>pt[1]))&&(pt[0]<(xj-xi)*(pt[1]-yi)/(yj-yi)+xi))c=!c}return c};
 const poly=p=>{if(!p.length||!ring(p[0]))return false;for(let k=1;k<p.length;k++)if(ring(p[k]))return false;return true};
 if(!g)return false;if(g.type==="Polygon")return poly(g.coordinates);if(g.type==="MultiPolygon")return g.coordinates.some(poly);return false}

const cache=new Map();
async function query(url,where,out,b,map,extra){
 const w=map.getSize().x||800,deg=(b.getEast()-b.getWest())/w;
 const p=new URLSearchParams({where,geometry:[b.getWest(),b.getSouth(),b.getEast(),b.getNorth()].map(v=>v.toFixed(5)).join(","),geometryType:"esriGeometryEnvelope",inSR:"4326",outSR:"4326",spatialRel:"esriSpatialRelIntersects",outFields:out,returnGeometry:"true",f:"geojson",resultRecordCount:"2000",...(extra||{})});
 if(!extra||!extra.pt)p.set("maxAllowableOffset",(deg*0.8).toPrecision(2));p.delete("pt");
 const key=url+"?"+p;if(cache.has(key))return cache.get(key);
 const pr=fetch(url+"/query?"+p).then(r=>{if(!r.ok)throw new Error("HTTP "+r.status);return r.json()}).then(j=>{if(j.error)throw new Error(j.error.message||"error");return j});
 cache.set(key,pr);if(cache.size>60)cache.delete(cache.keys().next().value);pr.catch(()=>cache.delete(key));return pr}

function attach(map,opt){
 if(map._lands)return;map._lands=1;const SK="lands:"+opt.id;
 let S;try{S=JSON.parse(localStorage.getItem(SK)||"null")}catch(e){}
 if(!S){S={on:{},base:"osm",open:0};for(const k in LAY)S.on[k]=!!LAY[k].def}
 const save=()=>localStorage.setItem(SK,JSON.stringify(S));
 const pane=(n,z)=>{if(!map.getPane(n))map.createPane(n);map.getPane(n).style.zIndex=z};pane("lands",330);pane("landsTop",340);pane("parcels",345);
 // basemaps
 let osm=null;map.eachLayer(l=>{if(l._url&&/openstreetmap/.test(l._url))osm=l});
 const topo=L.tileLayer("https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}",{maxZoom:19,maxNativeZoom:16,attribution:"USGS The National Map"});
 const img=L.layerGroup([L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",{maxZoom:19,maxNativeZoom:18,attribution:"Imagery © Esri, Maxar, Earthstar Geographics"}),
  L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}",{maxZoom:19,maxNativeZoom:18}),
  L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",{maxZoom:19,maxNativeZoom:18,attribution:"Labels © Esri"})]);
 const BASE={osm:["Street",osm],topo:["USGS Topo",topo],img:["Imagery + labels",img]};
 const setBase=k=>{if(!BASE[k]||!BASE[k][1])k="osm";for(const b in BASE){const l=BASE[b][1];if(!l)continue;if(b===k){if(!map.hasLayer(l)){l.addTo(map);l.bringToBack&&l.bringToBack()}}else if(map.hasLayer(l))map.removeLayer(l)}S.base=k;save()};
 // data layers
 const G={};for(const k in LAY){const d=LAY[k];G[k]=d.pt?L.layerGroup():d.line?L.geoJSON(null,{pane:"landsTop",interactive:true,bubblingMouseEvents:false,style:d.st,onEachFeature:(f,l)=>l.bindPopup(popRegs(f.properties),{maxWidth:300})}):L.geoJSON(null,{pane:k==="par"?"parcels":(k==="pub"?"lands":"landsTop"),interactive:false,style:d.st||(()=>({color:"#7a2e1d",weight:1.3,opacity:.9,fill:false}))});G[k].addTo(map)}
 const data={};const stat={};
 const ui=L.control({position:"topright"});let box;
 ui.onAdd=()=>{box=L.DomUtil.create("div","lndc"+(S.open?"":" shut"));
  box.innerHTML=`<button class="lndt" type="button" aria-expanded="${!!S.open}">🗺️ Land &amp; parcels ${S.open?"▴":"▾"}</button><div class="lndb">
  <div class="lnh">Basemap</div><div class="lnr" data-g="base">${Object.keys(BASE).filter(k=>BASE[k][1]).map(k=>`<button type="button" data-b="${k}">${BASE[k][0]}</button>`).join("")}</div>
  <div class="lnh">Layers</div><div class="lnr" data-g="lay">${Object.keys(LAY).map(k=>`<button type="button" data-k="${k}">${LAY[k].lab}</button>`).join("")}</div>
  <div class="lns" aria-live="polite"></div>
  <div class="lnwarn">⚠️ <b>Reference only, not a legal survey.</b></div><details class="lnkd"><summary>Legend, sources &amp; disclaimer</summary><div class="lnk"><b>Public land</b> (USGS PAD-US, by manager, zoom 10+):<br>${["FED","STAT","LOC","NGO"].map(t=>`<i style="background:${MT[t][1]};opacity:.6"></i>${MT[t][0]}`).join("<br>")}<br>
  ${SW("ease")}Conservation easement: usually private, no public access<br>${SW("lots")}DNR state land (DNR's own ownership records, zoom 11+)<br>${SW("cfa")}Commercial Forest: private, open to foot traffic for fishing/hunting<br>${SW("bal")}DNR boat launch / access site<br><b>Trout regs</b> (DNR, zoom 10+): <i style="background:#2e9e46"></i>Type 1 <i style="background:#e3c21b"></i>Type 2 <i style="background:#ef8a1c"></i>Type 3 <i style="background:#2c6fd6"></i>Type 4 <i style="background:#d0282e"></i>Gear-restricted · tap a line for the season, tackle and limits<br>${SW("tt")}DNR Trout Trails (biologist-picked spots)<br>${SW("par")}County tax parcel (zoom 14+)</div>
  <div class="lnd">Lines come from county, state and federal GIS and can be offset or out of date. Unshaded land is usually private. Private land needs the owner's permission, and on a non-navigable (private) stream the public can neither wade nor float. Parcels: Macomb, Oakland, Lapeer (2023), St. Clair, Genesee, Kent, Barry. ${esc(MISSING)} Tap the map for details.</div></details></div>`;
  L.DomEvent.disableClickPropagation(box);L.DomEvent.disableScrollPropagation(box);const kd=box.querySelector('.lnkd');if(kd&&map.getSize().x>=560)kd.open=true;
  box.querySelector(".lndt").onclick=()=>{S.open=S.open?0:1;save();box.classList.toggle("shut",!S.open);const t=box.querySelector(".lndt");t.setAttribute("aria-expanded",String(!!S.open));t.innerHTML=`🗺️ Land &amp; parcels ${S.open?"▴":"▾"}`};
  box.querySelectorAll("[data-b]").forEach(b=>b.onclick=()=>{setBase(b.dataset.b);paint()});
  box.querySelectorAll("[data-k]").forEach(b=>b.onclick=()=>{const k=b.dataset.k;S.on[k]=!S.on[k];save();if(!S.on[k]){G[k].clearLayers();data[k]=[]}paint();refresh()});
  return box};
 ui.addTo(map);
 function paint(){if(!box)return;box.querySelectorAll("[data-b]").forEach(b=>b.classList.toggle("sel",b.dataset.b===S.base));
  box.querySelectorAll("[data-k]").forEach(b=>{const on=!!S.on[b.dataset.k];b.classList.toggle("off",!on);b.setAttribute("aria-pressed",String(on))});
  const z=map.getZoom(),msg=[];for(const k in LAY){if(!S.on[k])continue;const d=LAY[k];if(z<d.minZ)msg.push(`${d.lab.replace(/^\S+\s/,"")}: zoom in (${d.minZ}+)`);else if(stat[k])msg.push(stat[k])}
  const s=box.querySelector(".lns");s.textContent=msg.join(" · ")}
 let seq=0,tmr=null;
 async function refresh(){const my=++seq,z=map.getZoom(),b=map.getBounds().pad(0.15);const jobs=[];
  for(const k in LAY){const d=LAY[k];if(!S.on[k]||z<d.minZ){G[k].clearLayers();data[k]=[];stat[k]="";continue}
   if(d.par){const srcs=PARCELS.filter(s=>!(s.bb[0]>b.getNorth()||s.bb[2]<b.getSouth()||s.bb[1]>b.getEast()||s.bb[3]<b.getWest()));
    if(!srcs.length){G[k].clearLayers();data[k]=[];stat[k]="Parcels: no free county parcel service for this area";continue}
    stat[k]="Parcels: loading…";
    jobs.push(Promise.allSettled(srcs.map(s=>query(s.url,"1=1","*",map.getBounds().pad(0.05),map).then(j=>({s,j})))).then(rs=>{if(my!==seq)return;G[k].clearLayers();data[k]=[];let n=0,part=0,bad=[];
     rs.forEach((r,i)=>{if(r.status!=="fulfilled"){bad.push(srcs[i].c);return}const {s,j}=r.value;if(j.exceededTransferLimit||(j.properties&&j.properties.exceededTransferLimit))part=1;
      (j.features||[]).forEach(f=>{f._src=s;data[k].push(f);n++});G[k].addData({type:"FeatureCollection",features:j.features||[]})});
     stat[k]=`Parcels: ${n} (${srcs.map(s=>s.c).join(", ")})${part?" — partial, zoom in":""}${bad.length?" — failed: "+bad.join(", "):""}`}));continue}
   stat[k]=d.lab.replace(/^\S+\s/,"")+": loading…";
   jobs.push(query(d.url,d.where,d.out,b,map,d.pt?{pt:1}:null).then(j=>{if(my!==seq)return;G[k].clearLayers();data[k]=j.features||[];
    if(d.pt){data[k].forEach(f=>{const c=f.geometry&&f.geometry.coordinates;if(!c)return;L.circleMarker([c[1],c[0]],{radius:k==="tt"?7:6,color:"#fff",weight:1.5,fillColor:d.col||"#1d5fa8",fillOpacity:.95}).bindPopup(k==="tt"?popTT(f.properties):popBal(f.properties),{maxWidth:280}).addTo(G[k])})}
    else G[k].addData(j);stat[k]=`${d.lab.replace(/^\S+\s/,"")}: ${data[k].length}${j.exceededTransferLimit||(j.properties&&j.properties.exceededTransferLimit)?" (partial)":""}`})
    .catch(e=>{if(my===seq)stat[k]=`${d.lab.replace(/^\S+\s/,"")}: couldn't load (${e.message})`}));}
  paint();await Promise.allSettled(jobs);if(my===seq){paint();map.getContainer().dataset.landsready=String(my)}}
 map.on("moveend zoomend",()=>{clearTimeout(tmr);tmr=setTimeout(refresh,350)});
 // click → one popup with everything under the point
 const shut=()=>{if(box&&S.open&&map.getSize().x<560){S.open=0;save();box.classList.add('shut');const t=box.querySelector('.lndt');t.setAttribute('aria-expanded','false');t.innerHTML='🗺️ Land &amp; parcels ▾'}};
 map.on("click",e=>{shut();const pt=[e.latlng.lng,e.latlng.lat],h=[];
  const hits=k=>S.on[k]?(data[k]||[]).filter(f=>pip(pt,f.geometry)):[];
  hits("pub").sort((a,b)=>(a.properties.GIS_Acres||0)-(b.properties.GIS_Acres||0)).forEach(f=>h.push(popPad(f.properties,0)));
  hits("ease").forEach(f=>h.push(popPad(f.properties,1)));
  hits("lots").slice(0,3).forEach(f=>h.push(popLots(f.properties)));
  hits("cfa").forEach(f=>h.push(popCfa(f.properties)));
  hits("par").forEach(f=>h.push(popPar(f)));
  if(!h.length){const any=["pub","ease","lots","cfa","par"].some(k=>S.on[k]&&map.getZoom()>=LAY[k].minZ);if(!any)return;
   h.push(`<h4>No mapped public land here</h4><div>${S.on.par&&map.getZoom()>=14?"No parcel loaded at this point.":"Likely private land. Turn on 📐 Parcel lines at zoom 14+ where available."}</div>`)}
  L.popup({maxWidth:290,className:"lnpopw",autoPanPaddingTopLeft:L.point(56,64),autoPanPaddingBottomRight:L.point(16,24)}).setLatLng(e.latlng).setContent(`<div class="lnpop">${h.join("")}<div class="sm" style="margin-top:6px">Reference only, not a legal survey.</div></div>`).openOn(map)});
 setBase(S.base);paint();refresh();
 return map._landsApi={S,G,data,refresh}}

function popPad(p,ease){const mt=MT[p.Mang_Type]||MT.UNK;
 return `<h4>${ease?"🤝 Conservation easement":"🏛️ Public land"}: ${esc(p.Unit_Nm||"(unnamed)")}</h4>
 <div>${ease?"Usually <b>private land</b> with a protective easement; an easement alone doesn't open it to the public.":"<b>Publicly owned</b> ("+esc(mt[0])+")"}</div>
 <div>Manager: ${esc(p.Loc_Mang||"—")}${p.Loc_Own&&p.Loc_Own!==p.Loc_Mang&&!/^(PVT|UNK|DESG)$/.test(p.Loc_Own)?"<br>Owner: "+esc(p.Loc_Own):(ease&&p.Own_Type==="PVT"?"<br>Owner: private":"")}</div>
 <div>Public access (PAD-US): ${esc(PA[p.Pub_Access]||p.Pub_Access||"—")}${p.GIS_Acres!=null?" · "+num(p.GIS_Acres,0)+" ac":""}</div>
 <div class="sm">USGS PAD-US 4.1 (${esc(p.FeatClass)}${p.Des_Tp?", "+esc(p.Des_Tp):""})</div>`}
function popLots(p){const ez=/^Acquired (Easement|Lease)/.test(p.TransactionType||"");
 return `<h4>🌲 ${ez?"DNR easement/lease":"State land"}: ${esc(p.ProjectName||"DNR")}</h4><div>${ez?"DNR holds an easement or lease here; the land itself may be private. Check the terms before using it.":"<b>Owned by the State of Michigan</b>, managed by "+esc(p.DivisionDepartment||"DNR")}</div>
 <div>${esc(p.ProjectUseType||"")}${p.Acreage!=null?" · "+num(p.Acreage)+" ac":""}${p.County?" · "+esc(p.County)+" Co.":""}</div><div class="sm">DNR Land Ownership Tracking System (Managed Lands) · last record: ${esc(trim(p.TransactionType))}</div>`}
function popCfa(p){return `<h4>🪓 Commercial Forest (private)</h4><div>Private land enrolled in the DNR Commercial Forest Program. Open to the public <b>on foot for fishing, hunting and trapping only</b>; no camping, vehicles or other uses without permission. Owner may close it during logging.</div>
 <div>${p.GISAcres!=null?num(p.GISAcres)+" ac · ":""}DNR parcel ${esc(p.parid)}</div><div class="sm">Michigan DNR Commercial Forest open data</div>`}
function popBal(p){const fee=trim(p.AccessFee)||trim(p.AccessCost);return `<div class="lnpop"><h4>🚤 ${esc(p.SiteName||"Access site")}</h4><div>${esc(p.WaterBody||"")}${p.Type?" · "+esc(p.Type):""}</div>
 <div>Managed by: ${esc(p.SiteManager||"—")}${p.Owner?" · owner "+esc(DIV[p.Owner]||p.Owner):""}</div><div>${p.TotalParking!=null?"Parking: "+esc(p.TotalParking):""}${fee?" · Fee: "+esc(fee):""}</div>
 <div class="sm">Michigan DNR boat launch data</div></div>`}
function popRegs(p){const g=p.GearRestriction,t=trim(p.StreamType),cut=v=>trim(v).replace(/Artifical/g,"Artificial").replace(/limt/g,"limit").replace(/Minmum/g,"Minimum");
 const base=p.FSeasonStart?`<div><b>Fishing:</b> ${esc(p.FSeasonStart)} – ${esc(p.FSeasonEnd)}<br><b>Possession:</b> ${esc(p.PSeasonStart)} – ${esc(p.PSeasonEnd)}<br><b>Tackle:</b> ${esc(cut(p.Tackle))}<br><b>Limit:</b> ${esc(cut(p.DPL))}</div>`:"";
 const grh=g?`<div style="margin-top:4px"><b>Gear-restricted (${esc(g)})</b>${p.GRLocDesc?": "+esc(p.GRLocDesc):""}<br><b>Fishing:</b> ${esc(p.GRFSeasonStart)} – ${esc(p.GRFSeasonEnd)}<br><b>Possession:</b> ${esc(cut(p.GRPSeasonStart))}${/^Closed/.test(p.GRPSeasonStart||"")?"":" – "+esc(cut(p.GRPSeasonEnd))}<br><b>Tackle:</b> ${esc(cut(p.GRTackle))}<br><b>Limit:</b> ${esc(cut(p.GRDPL))}${p.GRSL?"<br><b>Size:</b> "+esc(cut(p.GRSL)):""}</div>`:"";
 const typ=!g&&!base&&/^Type/.test(t)?`<div>${/^Type [12]/.test(t)?"Fishing &amp; possession last Sat in April – Sep 30.":/^Type 3/.test(t)?"Open all year.":/^Type 4/.test(t)?"Fishing all year; brook/brown kept last Sat in April – Sep 30.":""} See the Fishing Guide p.43 for limits.</div>`:"";
 return `<div class="lnpop"><h4>🎣 ${esc(p.DNRName||"Stream")}</h4><div>${esc(t||"")}${t&&g?" + ":""}${g?"Gear-restricted":""}</div>${base}${grh}${typ}<div class="sm">Michigan DNR Trout &amp; Salmon Regulations layer (FO-200/FO-210). Check the current Fishing Guide.</div></div>`}
function popTT(p){const d=trim(p.locationdescription).replace(/<[^>]*>/g," ");return `<div class="lnpop"><h4>⭐ ${esc(p.locationname)}</h4><div>${esc([p.locationdesignation,p.locationcounty&&p.locationcounty+" Co."].filter(Boolean).join(" · "))}</div>${p.speciesdescription?`<div>${esc(trim(p.speciesdescription).slice(0,200))}</div>`:""}${d?`<div class="sm">${esc(d.slice(0,260))}${d.length>260?"…":""}</div>`:""}${p.regionalvisitorurl&&/^https?:\/\//.test(p.regionalvisitorurl)?`<div><a href="${esc(p.regionalvisitorurl)}" target="_blank" rel="noopener">Area visitor info</a></div>`:""}<div class="sm">Michigan DNR Trout Trails</div></div>`}
function popPar(f){const s=f._src,v=s.f(f.properties||{});
 return `<h4>📐 Parcel ${esc(v.id||"")}</h4><div>Owner: ${v.own?esc(v.own):"<i>"+esc(v.noown||"not listed")+"</i>"}</div>${v.addr?`<div>Site: ${esc(v.addr)}</div>`:""}
 ${v.cvt?`<div>${esc(v.cvt)}</div>`:""}${v.cls?`<div>Class: ${pcls(v.cls)}</div>`:""}${v.zon?`<div>Zoning: ${esc(v.zon)}</div>`:""}${v.ac?`<div>${v.acapprox?"≈":""}${num(v.ac,2)} ac</div>`:""}
 ${v.link&&/^https:\/\//.test(v.link)?`<div><a href="${esc(v.link)}" target="_blank" rel="noopener">County tax record</a></div>`:""}<div class="sm">${esc(s.c)} County · ${esc(s.src)}</div>`}

window.LANDS={attach,PARCELS,LAY};
const tryAttach=()=>{if(window._map&&!window._map._lands)attach(window._map,{id:"home"});if(window._xmap&&!window._xmap._lands)attach(window._xmap,{id:"explore"})};
setInterval(tryAttach,700);tryAttach();
})();
