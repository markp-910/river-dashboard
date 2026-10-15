#!/usr/bin/env python3
"""Build explore-streams.json from research/regional-streams.json (+ drive_times.json, stock_region/stock_named.json).
Usage: python3 tools/build_explore.py   (research/ is NOT committed; only the generated JSON is)"""
import json, os, re, datetime, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda *p: os.path.join(ROOT, "research", *p)
reg = json.load(open(R("regional-streams.json")))
drive = json.load(open(R("drive_times.json"))) if os.path.exists(R("drive_times.json")) else {}

# ---- stocking events from the DNR DB dumps (last 5 years) ----
ev = {}
for f in ("stock_region.json", "stock_named.json"):
    if os.path.exists(R(f)):
        for x in json.load(open(R(f)))["features"]:
            a = x["attributes"]
            if not a.get("stocking_date"): continue
            d = datetime.datetime.utcfromtimestamp(a["stocking_date"] / 1000).strftime("%Y-%m-%d")
            k = (a["Water_Body_Name"].strip(), a["sitename"].strip(), a["SPEC_COMM_Alt"].strip(), d, a["Number_Fish_Stocked"])
            ev[k] = {"water": k[0], "site": k[1].title() if k[1].isupper() else k[1], "species": k[2], "date": d, "count": k[4], "len_cm": a.get("Average_Length")}
EV = sorted(ev.values(), key=lambda e: e["date"], reverse=True)
def stock_for(waters, sites=None, exclude_sites=None):
    out = [e for e in EV if e["water"] in waters and e["date"] >= "2021-10-01"
           and (not sites or any(s.lower() in e["site"].lower() for s in sites))
           and not (exclude_sites and any(s.lower() in e["site"].lower() for s in exclude_sites))]
    return out

# ---- per-stream curated metadata (keyed by name prefix) ----
TR_NOTE = "TroutRoutes class read by Mark from his Pro account (county labels in the app are unreliable). Class: 1 best … 3; 'unknown' = not checked."
META = {
 "Paint Creek": dict(id="paint-creek", tr=dict(cls="3", type="Type 1 (DNR)", gr=True, note="Gear-restricted Gunn–Tienken per DNR"),
    season=dict(rule="last_sat_apr_sep30", label="Type 1: last Sat in April – Sep 30"), gages=[("04161540", "Paint Creek at Rochester (offline)", False), ("04161000", "Clinton R at Auburn Hills (nearest live proxy)", True)],
    wild="both", best=[4,5,6,9], run=[], stock=dict(waters=["Paint Creek"])),
 "Clinton River": dict(id="clinton-river", tr=dict(cls="2", type="Type 4", gr=False, note="Open year-round"),
    season=dict(rule="year_round", label="Open year-round (Type 4)"), gages=[("04161000", "Clinton R at Auburn Hills", False), ("04161820", "Clinton R at Sterling Heights (has water temp)", False)],
    wild="stocked", best=[3,4,10,11], run=[{"label": "Steelhead fall run", "months": [10,11]}, {"label": "Steelhead spring run", "months": [2,3,4]}, {"label": "Salmon spawn", "months": [10,11]}], stock=dict(waters=["Clinton River"])),
 "Huron River below Proud Lake": dict(id="huron-proud-lake", tr=dict(cls="1", type="Type 1", gr=True, note="TroutRoutes: Huron River upper (Proud Lake/Commerce/Milford) Class 1, GR, Type 1"),
    season=dict(rule="closed_oct1_mar31", label="Closed Oct 1 – Mar 31; Apr 1–25 flies-only catch & release, then open to Sep 30"), gages=[("04172000", "Huron R near Hamburg (context only, different reach)", True)],
    wild="stocked", best=[4,5], run=[], stock=dict(waters=["Huron River"], exclude_sites=["Rockwood"])),
 "Huron River - Flat Rock": dict(id="huron-lower", tr=dict(cls="2", type="Type 4", gr=False, note="TroutRoutes: Huron lower (Belleville to Flat Rock/Rockwood) Class 2, Type 4"),
    season=dict(rule="year_round", label="Open year-round (Type 4)"), gages=[("04174500", "Huron R at Ann Arbor (far upstream — context only)", True)],
    wild="stocked", best=[3,4,11], run=[{"label": "Steelhead spring run", "months": [3,4]}, {"label": "Steelhead fall run", "months": [9,10,11]}], stock=dict(waters=["Huron River"], sites=["Rockwood"])),
 "Mill Creek, Dexter": dict(id="mill-creek-dexter", tr=dict(cls="unknown", type="", gr=False, note="TroutRoutes class not checked (the TroutRoutes 'Mill Creek' Class 2 is St. Clair Co.)"),
    season=dict(rule="year_round", label="Open year-round (Not Classified)"), gages=[("04173500", "Mill Creek near Dexter", False)],
    wild="stocked", best=[4,5,6,9,10], run=[], stock=dict(waters=["Mill Creek"], sites=["Mill Creek Park", "Shield"])),
 "Belle River": dict(id="belle-river", tr=dict(cls="2", type="Type 1 (TroutRoutes tag)", gr=False, note="TroutRoutes tags it Type 1, but DNR sources say not a designated trout stream — conflict"),
    season=dict(rule="unknown", label="Season unverified (TroutRoutes says Type 1; DNR sources say not designated)"), gages=[("04160600", "Belle River at Memphis", False)],
    wild="stocked", best=[3,4,10,11], run=[{"label": "Steelhead fall entry", "months": [10,11]}, {"label": "Steelhead spring peak", "months": [3,4,5]}], stock=dict(waters=["Belle River"])),
 "Mill Creek / Black River at Yale": dict(id="mill-creek-yale", tr=dict(cls="2", type="", gr=False, note="TroutRoutes 'Mill Creek (St. Clair Co.)' Class 2 — may be this Yale stream, unconfirmed"),
    season=dict(rule="unknown", label="Season unverified"), gages=[("04159900", "Mill Creek near Avoca (~6 mi)", False)],
    wild="stocked", best=[3,4,5], run=[{"label": "Steelhead spring run", "months": [3,4,5]}], stock=dict(waters=["Mill Creek"], sites=["Yale"])),
 "North Branch Clinton River headwaters": dict(id="north-branch-headwaters", tr=dict(cls="unknown", type="", gr=False, note=""),
    season=dict(rule="last_sat_apr_sep30", inferred=True, label="Type 1 above 32 Mile (inferred): last Sat in April – Sep 30"), gages=[("04164151", "N Branch Clinton R at 26 Mile", False), ("04164100", "East Pond Creek at Romeo", False)],
    wild="wild", best=[4,5,6,9,10], run=[], stock=dict(waters=[])),
 "Kearsley Creek": dict(id="kearsley-creek", tr=dict(cls="3", type="", gr=False, note="TroutRoutes 'Kearsley Creek (Oakland Co.)' Class 3 — may differ from the Flint-area Kearsley"),
    season=dict(rule="last_sat_apr_sep30", inferred=True, label="Type 1 (inferred): last Sat in April – Sep 30"), gages=[],
    wild="stocked", best=[4,5,6], run=[], stock=dict(waters=["Kearsley Creek"])),
 "St. Clair River": dict(id="st-clair-river", tr=dict(cls="unknown", type="", gr=False, note="Great Lakes connecting water"),
    season=dict(rule="year_round", label="Great Lakes connecting water — open (check Great Lakes regs; Ontario side separate)"), gages=[("04159130", "St Clair River at Port Huron", False)],
    wild="stocked", best=[3,4,5,10,11], run=[{"label": "Steelhead/brown spring", "months": [3,4,5]}, {"label": "Fall run", "months": [9,10,11]}], stock=dict(waters=[])),
 "Johnson Creek": dict(id="johnson-creek", tr=dict(cls="unknown", type="", gr=False, note=""),
    season=dict(rule="last_sat_apr_sep30", inferred=True, label="Type 1 (inferred): last Sat in April – Sep 30"), gages=[("04166700", "Johnson Creek at 7 Mile Rd", False)],
    wild="wild", best=[4,5,9,10], run=[], stock=dict(waters=[])),
 "Pine Creek & Bottom Creek": dict(id="pine-bottom-creek", tr=dict(cls="3", type="Type 1 (TroutRoutes tag, Bottom Creek)", gr=False, note="TroutRoutes: Bottom Creek (Lapeer) Class 3, Type 1 (a secondary site says Type 2 — conflict)"),
    season=dict(rule="last_sat_apr_sep30", inferred=True, label="Type 1 (inferred): last Sat in April – Sep 30"), gages=[("04146000", "Farmers Creek near Lapeer (regional context only)", True)],
    wild="wild", best=[], run=[], stock=dict(waters=[])),
 "East Pond Creek": dict(id="east-pond-creek", tr=dict(cls="3", type="", gr=False, note=""),
    season=dict(rule="last_sat_apr_sep30", inferred=True, label="Designated upstream of East Mile Pond; Type 1 assumed: last Sat in April – Sep 30"), gages=[("04164100", "East Pond Creek at Romeo", False)],
    wild="wild", best=[], run=[], stock=dict(waters=[])),
 "Red Cedar River": dict(id="red-cedar-grand", tr=dict(cls="unknown", type="", gr=False, note=""),
    season=dict(rule="unknown", label="Season unverified"), gages=[("04112500", "Red Cedar R at East Lansing", False), ("04113000", "Grand R at Lansing", False)],
    wild="stocked", best=[4,5], run=[], stock=dict(waters=["Red Cedar River", "Grand River"])),
}
SPG = [("steelhead", "Steelhead"), ("brown", "Brown trout"), ("rainbow", "Rainbow trout"), ("brook", "Brook trout"), ("chinook", "Salmon"), ("salmon", "Salmon"), ("coho", "Salmon"), ("smallmouth", "Smallmouth bass"), ("largemouth", "Largemouth bass"), ("pike", "Northern pike"), ("creek chub", "Creek chub")]
def groups(sp):
    g = []
    for s in sp:
        for k, v in SPG:
            if k in s.lower() and v not in g: g.append(v)
    return g
FLAGW = re.compile(r"not verified|inference|inferred|unverified|verify|unreconciled|conflict|unknown|no dated|none found|not confirmed|absence", re.I)

streams = []
for c in reg["candidates"]:
    key = next((k for k in META if c["name"].startswith(k)), None)
    if not key: print("no meta for", c["name"]); continue
    m = META[key]
    st = stock_for(**m["stock"]) if m["stock"].get("waters") else []
    flags = [f"{f}: {c[f]}" for f in ("dnr", "reproduction", "regs", "seasons", "access", "stocking", "gage") if c.get(f) and FLAGW.search(c[f]) and "unknown (TroutRoutes pages" not in c[f]]
    if m["season"].get("inferred"): flags.append("season: inferred from DNR order structure, not confirmed in the regulation guide")
    if c["confidence"].lower().startswith("low"): flags.append("overall confidence is low")
    streams.append({
        "id": m["id"], "rank": c["rank"], "tier": c["tier"], "name": c["name"], "county": c["county"], "lat": c["drive"]["lat"], "lng": c["drive"]["lng"],
        "drive_min": c["drive"]["min"], "drive_miles": c["drive"]["miles"],
        "species": c["species"], "species_groups": groups(c["species"]), "wild": m["wild"], "reproduction": c["reproduction"],
        "tr": m["tr"], "dnr": c["dnr"], "season": m["season"], "regs": c["regs"], "seasons_text": c["seasons"], "best_months": m["best"], "runs": m["run"],
        "stocking_summary": c["stocking"], "stocking_events": st,
        "catches": [{"date": a, "text": b, "url": u} for a, b, u in c["catches"]],
        "access": c["access"], "gages": [{"id": i, "label": l, "proxy": p} for i, l, p in m["gages"]], "gage_note": c["gage"],
        "confidence": c["confidence"], "flags": flags, "sources": c["sources"]})
out = {"generated": reg["generated"], "home": reg["home"], "drive_method": reg["drive_method"], "troutroutes_note": TR_NOTE,
       "no_gold_note": "No TroutRoutes Gold Medal / DNR Blue Ribbon water found within 2 hours of home.",
       "streams": streams, "outside_2h": reg["outside_2h"], "no_evidence": reg["no_evidence"], "notes": reg["notes"]}
json.dump(out, open(os.path.join(ROOT, "explore-streams.json"), "w"), indent=1)
print(len(streams), "streams;", sum(len(s["stocking_events"]) for s in streams), "stocking events; size", os.path.getsize(os.path.join(ROOT, "explore-streams.json")) // 1024, "KB")
for s in streams: print(s["tier"], s["id"], s["drive_min"], len(s["stocking_events"]), s["tr"]["cls"], len(s["flags"]))
