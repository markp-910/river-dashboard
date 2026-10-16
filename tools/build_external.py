#!/usr/bin/env python3
"""Regenerate ../external-catches.json (served by the dashboard) from research/ files.
Usage: python3 tools/build_external.py   (run from repo root or anywhere)
Inputs: research/external-catches.json (required), research/seasonal-timing.json (optional),
research/fishbrain-raw.csv (optional; columns water,date,species,size,gear,cr,pv_id,note; 'MINE ' water prefix = Mark's own catches)."""
import json, os, re, collections, datetime, csv, hashlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda *p: os.path.join(ROOT, *p)
recs = json.load(open(R("research", "external-catches.json")))

# --- Fishbrain import (research/fishbrain-raw.csv). Fishbrain gives only the water name (exact spots hidden), so every record is placed
# on that water's line from rivers.geojson with deterministic jitter (hash of pv_id) and precision "area". No angler usernames are stored.
FB_STATUS = {"updated": "2026-10-16",
  "text": "Fishbrain sweep (updated Oct 16, 2026): Paint Creek covered Oct 2025\u2013Oct 2026 (a few cards skipped); Clinton River covered back to about mid-Aug 2026 only (newest ~100 of ~200 cards, partly skimmed); East Pond Creek covered for the last year. North Branch Clinton, Belle, Kearsley, Huron, Johnson, Mill Creek and St. Clair River not yet read."}
FB_WATERS = {  # water -> (rivers.geojson name, bbox lat0,lat1,lng0,lng1, Fishbrain Explore page, fixed point)
  "Paint Creek": ("Paint Creek", (42.66, 42.78, -83.30, -83.10), "https://fishbrain.com/fishing-waters/L1Y7Xvbt", None),
  "Clinton River": ("Clinton River", (42.55, 42.72, -83.26, -82.85), "https://fishbrain.com/fishing-waters/FWP_xjdL", None),
  "East Pond Creek": ("East Pond Creek", (42.75, 42.90, -83.05, -82.95), "https://fishbrain.com/fishing-waters/xojKgtBJ", None),
  "Lake Saint Clair": (None, None, "https://fishbrain.com/anglers/Markp910", (42.60, -82.785)),
}
def _line_pts(name, box):
    g = json.load(open(R("rivers.geojson"))); pts = []
    for f in g["features"]:
        if f["properties"].get("n") != name: continue
        for line in f["geometry"]["coordinates"]:
            for lng, lat in line:
                if box[0] <= lat <= box[1] and box[2] <= lng <= box[3]: pts.append((lat, lng))
    return sorted(set(pts))
def fishbrain_records():
    path = R("research", "fishbrain-raw.csv")
    if not os.path.exists(path): return []
    out, cache = [], {}
    for row in csv.DictReader(open(path, encoding="utf-8")):
        mine = row["water"].startswith("MINE "); w = row["water"][5:] if mine else row["water"]
        if w not in FB_WATERS: print("skip unknown water", w); continue
        gname, box, page, fixed = FB_WATERS[w]
        h = int(hashlib.md5(row["pv_id"].encode()).hexdigest(), 16)
        if fixed: lat, lng = fixed[0] + ((h % 1000) / 1000 - .5) * 0.02, fixed[1] + (((h >> 10) % 1000) / 1000 - .5) * 0.03
        else:
            if w not in cache: cache[w] = _line_pts(gname, box)
            pts = cache[w]; lat, lng = pts[h % len(pts)]
            lat += (((h >> 12) % 1000) / 1000 - .5) * 0.002; lng += (((h >> 22) % 1000) / 1000 - .5) * 0.002
        label = {"Lake Saint Clair": "Lake St. Clair"}.get(w, w)
        bits = ["Your Fishbrain catch" if mine else "Public Fishbrain catch"]
        if row["gear"]: bits.append("Gear/bait: " + row["gear"])
        if row["cr"].lower() == "yes": bits.append("Catch & release")
        bits.append("Approximate \u2014 Fishbrain only gives the water name")
        out.append({"date": row["date"], "species": row["species"], "size": row["size"] or None,
            "location": label + (" (Mark\u2019s spot, hidden on Fishbrain)" if mine and "secret" in row["note"] else ""),
            "lat": round(lat, 5), "lng": round(lng, 5), "precision": "area", "source": "Fishbrain \u2014 " + label + " Explore page",
            "url": page, "note": " \u00b7 ".join(bits), "type": "catch/observation", "source_group": "Fishbrain"})
    return out
recs = recs + fishbrain_records()

def group(sp):
    s = (sp or "").lower()
    if "steelhead" in s: return "Steelhead"
    if "salmon" in s or "chinook" in s or "coho" in s: return "Salmon"
    if "brown" in s and "rainbow" in s: return "Trout (mixed)"
    if "brown" in s: return "Brown trout"
    if "rainbow" in s: return "Rainbow trout"
    if "trout" in s: return "Trout (mixed)"
    if "smallmouth" in s: return "Smallmouth bass"
    if "largemouth" in s: return "Largemouth bass"
    if "creek chub" in s or s.strip()=="chub": return "Creek chub"
    if "pike" in s: return "Northern pike"
    if "rock bass" in s: return "Rock bass"
    if "walleye" in s: return "Walleye"
    return "Other"

# --- Source grouping: record "source" free text -> clean "source_group" shown as a per-source map layer.
# A record may carry its own "source_group" in research/external-catches.json (e.g. "Fishbrain"); otherwise it is derived here.
# New groups appear on the map automatically; give them a color in SOURCE_COLORS (else the page assigns one from a fallback palette).
SOURCE_COLORS = {  # chosen to read on cream UI, OSM and satellite (all markers get a white outline)
    "iNaturalist": "#8fb800", "Michigan DNR": "#00838f", "Michigan Sportsman": "#d9480f", "Reddit": "#d6336c",
    "X / Social": "#343a40", "News & press": "#d4a017", "Fishbrain": "#1c7ed6"}
RESERVED = ["Fishbrain"]  # always listed on the map (count 0 until data arrives)

def source_group(x):
    if x.get("source_group"): return x["source_group"]
    s = (x.get("source") or "").lower()
    if "inaturalist" in s: return "iNaturalist"
    if "fishbrain" in s: return "Fishbrain"
    if "dnr" in s or "department of natural resources" in s: return "Michigan DNR"
    if "michigan sportsman" in s or "michigan-sportsman" in s or "forum" in s: return "Michigan Sportsman" if "sportsman" in s else "Forums"
    if "reddit" in s: return "Reddit"
    if re.search(r"\bon x\b|\bx post\b|twitter|facebook|instagram", s): return "X / Social"
    if any(k in s for k in ("press release", "times", "media", "news", "gazette", "herald", "tribune", "free press")): return "News & press"
    return (x.get("source") or "Other").strip() or "Other"

def clean(x):
    return {k: x.get(k) for k in ("date","species","size","location","lat","lng","precision","source","url","note","type")} | {"group": group(x.get("species")), "source_group": source_group(x)}

keep = [clean(x) for x in recs if "captive" not in (x.get("flag") or "") and x.get("lat") is not None]
dropped = len(recs) - len(keep)
stock = [x for x in keep if x["type"] == "stocking"]
catches = sorted([x for x in keep if x["type"] != "stocking"], key=lambda x: x["date"], reverse=True)

sites = collections.OrderedDict()
for x in sorted(stock, key=lambda x: x["date"], reverse=True):
    k = (round(x["lat"], 3), round(x["lng"], 3))
    s = sites.setdefault(k, {"lat": x["lat"], "lng": x["lng"], "names": collections.Counter(), "events": []})
    s["names"][x["location"]] += 1
    m = re.match(r"\s*([\d,]+)\s*fish", x.get("size") or "")
    s["events"].append({"date": x["date"], "species": x["species"], "group": x["group"], "count": int(m.group(1).replace(",", "")) if m else None,
                        "size": x["size"], "note": (x["note"] or "").split("; API ")[0], "source": x["source"], "url": x["url"]})
site_list = []
for s in sites.values():
    site_list.append({"name": s["names"].most_common(1)[0][0], "lat": s["lat"], "lng": s["lng"], "last": s["events"][0]["date"], "events": s["events"]})
site_list.sort(key=lambda s: s["name"])

timing_path = R("research", "seasonal-timing.json")
seasonal = None
if os.path.exists(timing_path):
    seasonal = json.load(open(timing_path)); timing_src = "research/seasonal-timing.json (" + seasonal.get("generated", "") + ")"
    P, C = seasonal["rivers"]["Paint Creek"], seasonal["rivers"]["Clinton River"]
    fs = lambda x: (x.get("sources") or [x.get("source", "")])[0].split(" ")[0]
    timing = [
        {"label": "Clinton — steelhead fall run", "river": "Clinton River", "species": "Steelhead", "months": [9,10,11], "peak": [10,11], "note": C["steelhead_runs"]["fall"], "url": fs(C["steelhead_runs"])},
        {"label": "Clinton — steelhead spring run", "river": "Clinton River", "species": "Steelhead", "months": [2,3,4,5], "peak": [3,4], "note": C["steelhead_runs"]["spring"], "url": fs(C["steelhead_runs"])},
        {"label": "Clinton — salmon spawn", "river": "Clinton River", "species": "Salmon", "months": [10,11], "peak": [11], "note": C["salmon"]["window"], "url": fs(C["salmon"])},
        {"label": "Clinton — adult trout stocking (Squirrel Rd)", "river": "Clinton River", "species": "Brown trout", "months": [3], "peak": [3], "note": C["stocking"]["adult_broodstock"], "url": "https://www.dnr.state.mi.us/fishstock/"},
        {"label": "Clinton — steelhead smolt stocking (Ryan Rd)", "river": "Clinton River", "species": "Steelhead", "months": [4], "peak": [4], "note": C["stocking"]["steelhead_smolts"], "url": "https://www.dnr.state.mi.us/fishstock/"},
        {"label": "Paint Creek — trout season open", "river": "Paint Creek", "species": "Brown trout", "months": [4,5,6,7,8,9], "peak": [5,6,9], "note": P["regulations"]["season"] + ". Best: " + "; ".join(w["window"] for w in P["best_windows"]), "url": P["regulations"]["sources"][0]},
        {"label": "Paint Creek — yearling brown stocking", "river": "Paint Creek", "species": "Brown trout", "months": [4,5], "peak": [4], "note": P["stocking"]["window"], "url": "https://www.dnr.state.mi.us/fishstock/"},
    ]
else:
    timing_src = "derived from research/external-catches.json summary"
    timing = [
        {"label": "Steelhead — fall run", "species": "Steelhead", "months": [9,10,11], "peak": [10], "note": "Forum reports of 15–30 in steelhead Sept–Nov 2025 below Yates Dam / Clinton River", "source": "Michigan Sportsman forum, Clinton River 2025/2026 thread", "url": "https://www.michigan-sportsman.com/threads/clinton-river-2025-2026.772769/"},
        {"label": "Steelhead — spring run", "species": "Steelhead", "months": [3,4], "peak": [4], "note": "Spring spawning run (typical Michigan timing; Ryan Rd smolt stocking in April)", "source": "MI DNR stocking data / general MI run timing", "url": "https://www.dnr.state.mi.us/fishstock/"},
        {"label": "Salmon spawn", "species": "Salmon", "months": [10,11], "peak": [11], "note": "Salmon redds peak ~Nov 12 per 2025 forum reports", "source": "Michigan Sportsman forum", "url": "https://www.michigan-sportsman.com/threads/clinton-river-2025-2026.772769/"},
        {"label": "Adult brown trout stocking (Squirrel Rd)", "species": "Brown trout", "months": [3], "peak": [3], "note": "DNR broodstock browns 13–18 in, late March most years", "source": "MI DNR Fish Stocking Database", "url": "https://www.dnr.state.mi.us/fishstock/"},
        {"label": "Yearling brown trout stocking", "species": "Brown trout", "months": [4,5], "peak": [4], "note": "Paint Creek & upper Clinton yearlings every spring (Apr 15 – May 5)", "source": "MI DNR Fish Stocking Database", "url": "https://www.dnr.state.mi.us/fishstock/"},
    ]
_cnt = collections.Counter(c["source_group"] for c in catches)
for r in RESERVED: _cnt.setdefault(r, 0)
source_groups = [{"name": n, "color": SOURCE_COLORS.get(n), "count": c} for n, c in sorted(_cnt.items(), key=lambda kv: (-kv[1], kv[0]))]
out = {"source_groups": source_groups, "fishbrain_status": FB_STATUS, "generated": datetime.date.today().isoformat(), "dropped_captive": dropped, "timing_source": timing_src,
       "species": sorted({x["group"] for x in keep}), "sites": site_list, "catches": catches, "timing": timing, "seasonal": seasonal}
json.dump(out, open(R("external-catches.json"), "w"), indent=1)
print(f"wrote external-catches.json: {len(site_list)} stocking sites / {len(stock)} events, {len(catches)} catches/reports, dropped {dropped} captive, timing from {timing_src}")
