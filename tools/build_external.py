#!/usr/bin/env python3
"""Regenerate ../external-catches.json (served by the dashboard) from research/ files.
Usage: python3 tools/build_external.py   (run from repo root or anywhere)
Inputs: research/external-catches.json (required), research/seasonal-timing.json (optional)."""
import json, os, re, collections, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda *p: os.path.join(ROOT, *p)
recs = json.load(open(R("research", "external-catches.json")))

def group(sp):
    s = (sp or "").lower()
    if "steelhead" in s: return "Steelhead"
    if "salmon" in s or "chinook" in s or "coho" in s: return "Salmon"
    if "brown" in s and "rainbow" in s: return "Trout (mixed)"
    if "brown" in s: return "Brown trout"
    if "rainbow" in s: return "Rainbow trout"
    if "trout" in s: return "Trout (mixed)"
    if "smallmouth" in s: return "Smallmouth bass"
    if "pike" in s: return "Northern pike"
    if "walleye" in s: return "Walleye"
    return "Other"

def clean(x):
    return {k: x.get(k) for k in ("date","species","size","location","lat","lng","precision","source","url","note","type")} | {"group": group(x.get("species"))}

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
out = {"generated": datetime.date.today().isoformat(), "dropped_captive": dropped, "timing_source": timing_src,
       "species": sorted({x["group"] for x in keep}), "sites": site_list, "catches": catches, "timing": timing, "seasonal": seasonal}
json.dump(out, open(R("external-catches.json"), "w"), indent=1)
print(f"wrote external-catches.json: {len(site_list)} stocking sites / {len(stock)} events, {len(catches)} catches/reports, dropped {dropped} captive, timing from {timing_src}")
