#!/usr/bin/env python3
"""Build rivers.geojson from USGS NHD (National Map ArcGIS REST, layer 6 flowlines). Run: python3 tools/build_rivers.py
(Cached raw download: /workspace/nhd_named.json if present.)"""
import json,os,urllib.request,urllib.parse
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW="/workspace/nhd_named.json"
U="https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer/6/query"
if os.path.exists(RAW): feats=json.load(open(RAW))
else:
  feats=[];off=0
  while True:
    p={"where":"gnis_name IS NOT NULL","geometry":"-83.4,42.4,-82.7,42.85","geometryType":"esriGeometryEnvelope","inSR":4326,"outSR":4326,"spatialRel":"esriSpatialRelIntersects","outFields":"gnis_name,ftype,lengthkm","returnGeometry":"true","maxAllowableOffset":0.0002,"geometryPrecision":5,"f":"geojson","resultOffset":off,"resultRecordCount":1000}
    f=json.load(urllib.request.urlopen(U+"?"+urllib.parse.urlencode(p),timeout=120)).get("features",[]);feats+=f
    if len(f)<1000:break
    off+=1000
# class: 1 = highlight most, 2 = gaged tributaries/branches, 3 = other named
CL={"Paint Creek":1,"Clinton River":1,"North Branch Clinton River":2,"Middle Branch Clinton River":2,"East Pond Creek":2,"East Branch Coon Creek":2,"Coon Creek":2,"Plum Brook":2,"Red Run":2,"River Rouge":2,"Upper River Rouge":2,"Galloway Creek":3,"Stony Creek":3,"Paint Creek Drain":3,"Franklin Branch":3,"Big Beaver Creek":3,"Pebble Creek":3,"Trout Creek":3,"Bell Branch":3,"Sashabaw Creek":3,"Sargent Creek":3,"West Branch Stony Creek":3}
def simp(c,eps=0.00004):
  if len(c)<3:return c
  def d(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    if dx==dy==0:return ((p[0]-a[0])**2+(p[1]-a[1])**2)**.5
    return abs(dy*p[0]-dx*p[1]+b[0]*a[1]-b[1]*a[0])/(dx*dx+dy*dy)**.5
  m,i=max(((d(c[k],c[0],c[-1]),k) for k in range(1,len(c)-1)),default=(0,0))
  return simp(c[:i+1],eps)[:-1]+simp(c[i:],eps) if m>eps else [c[0],c[-1]]
out=[]
for f in feats:
  n=f["properties"]["gnis_name"]
  if n not in CL or not f.get("geometry"):continue
  g=f["geometry"];lines=g["coordinates"] if g["type"]=="MultiLineString" else [g["coordinates"]]
  lines=[[[round(x,5),round(y,5)] for x,y in simp([(p[0],p[1]) for p in l])] for l in lines]
  out.append({"type":"Feature","properties":{"n":n,"c":CL[n]},"geometry":{"type":"MultiLineString","coordinates":lines}})
json.dump({"type":"FeatureCollection","source":"USGS National Hydrography Dataset (The National Map)","features":out},open(os.path.join(ROOT,"rivers.geojson"),"w"),separators=(",",":"))
print(len(out),"features",os.path.getsize(os.path.join(ROOT,"rivers.geojson"))//1024,"KB")
