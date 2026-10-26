#!/usr/bin/env python3
"""Build explore-streams.json: US-only, 4 one-way-drive-time tiers, state trout-stream designations (FO-210.26 / FO-200.25).
Inputs: research/regional-streams.json (original 14 streams), research/drive_times_new.json (OSRM), research/stock_*.json (DNR stocking DB),
research/inat_new.json (iNaturalist), research/drive_alt.json (Valhalla cross-check cache). Hand-entered metadata: tools/explore_meta.py (original streams),
tools/explore_new.py (streams added for the 4-hour range). Usage: cd tools && python3 build_explore.py   (research/ is NOT committed)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from explore_common import *
from explore_meta import META
from explore_new import NEW, DT
import explore_grayling as GR
reg = json.load(open(R("regional-streams.json")))
home = reg["home"]
FLAGW = re.compile(r"not verified|inference|inferred|unverified|verify|unreconciled|conflict|no dated|none found|not confirmed|absence", re.I)
streams = []
for c in reg["candidates"]:
    key = next((k for k in META if c["name"].startswith(k)), None)
    if not key:
        print("no meta for", c["name"]); continue
    m = META[key]
    evs = stock_for(**m["stock"]) if m["stock"].get("waters") else []
    flags = ([] if m.get("own_flags") else [f"{f}: {c[f]}" for f in ("reproduction", "access", "stocking", "gage") if c.get(f) and FLAGW.search(c[f])]) + m.get("flag_extra", [])
    if str(c["confidence"]).lower().startswith("low"): flags.append("overall confidence is low")
    sp = list(c["species"]) + [x for x in m.get("extra_species", []) if x not in c["species"]]
    src = [u for u in c["sources"] if not any(d in u for d in m.get("drop_sources", []))]
    if m.get("pin"): src = [u for u in src if "FO_2" not in u]  # re-add the canonical labelled FO links below
    for u in (FO210, FO200):
        if u not in src: src.append(u)
    if m.get("pin"):  # re-pinned entry: drive times from research/drive_times_new.json
        dv = DT[m["pin"]]; lat, lng, dmin, dmi, dalt = dv["lat"], dv["lng"], dv["min"], dv["miles"], dv["alt_min"]
    else:
        lat, lng, dmin, dmi = c["drive"]["lat"], c["drive"]["lng"], c["drive"]["min"], c["drive"]["miles"]; dalt = alt_min(m["id"], lat, lng, home)
    if "species" in m: sp = m["species"]
    src += [u for u in m.get("sources_extra", []) if u not in src]
    streams.append({"id": m["id"], "name": m.get("rename", c["name"]), "county": m.get("county", c["county"]), "lat": lat, "lng": lng,
        "drive_min": dmin, "drive_miles": dmi, "drive_min_alt": dalt,
        "species": sp, "species_groups": groups(sp), "wild": m["wild"], "reproduction": m.get("reproduction", c["reproduction"]),
        "tr": m["tr"], "dnr": m["dnr"] if "dnr" in m else c["dnr"], "state": m["state"], "season": m["season"], "regs": m.get("regs", c["regs"]), "seasons_text": m.get("seasons_text", c["seasons"]),
        "best_months": m["best"], "runs": m["run"], "stocking_summary": m.get("stocking_summary", c["stocking"]) if not evs else stock_summary(evs), "stocking_events": evs[:40],
        "catches": [{"date": a, "text": b, "url": u} for a, b, u in c["catches"]], "access": m.get("access", c["access"]),
        "gages": [{"id": i, "label": l, "proxy": p} for i, l, p in m["gages"]], "gage_note": m.get("gage_note", c["gage"]),
        "confidence": m.get("confidence", c["confidence"]), "flags": flags, "sources": src, **({"history": m["history"]} if m.get("history") else {})})
streams.extend(NEW)
streams.extend(GR.NEW_G)
GR.apply(streams)
streams.sort(key=lambda s: s["drive_min"])
for i, s in enumerate(streams, 1):
    s["rank"] = i
    s["tier"] = tier_of(s["drive_min"]); s["tier_name"] = TIERS[s["tier"] - 1][1]
    assert s["tier"], s["id"]
OUT4H = [
 dict(name="Pine River (Lake/Wexford Co.) — Type 2 Elm Flats → Tippy Dam (Hoxeyville)", min=245, note="Type 2 per FO-200; just past the 4 h cap by OSRM"),
 dict(name="St. Joseph River (Berrien Springs Dam), steelhead/salmon", min=243, note="3 min over the cap by OSRM"),
 dict(name="Chagrin River, OH (Chagrin Falls)", min=248, note="Primary Ohio steelhead stream; slightly over by OSRM"),
 dict(name="Thunder Bay River (Alpena)", min=278), dict(name="Boardman River (Traverse City)", min=270), dict(name="Betsie River (Benzie Co.)", min=283),
 dict(name="Manistee River below Tippy Dam", min=284), dict(name="Little Manistee River (weir)", min=286), dict(name="Pigeon River (Otsego Co.) — Type 2", min=284),
 dict(name="Grand River, OH (Painesville)", min=265), dict(name="Conneaut Creek, OH", min=317), dict(name="Trail Creek (Michigan City, IN)", min=275)]
EXCL = [
 "Canada (Ontario) is excluded entirely: the Sarnia/Point Edward side of the St. Clair River and the Ausable River at Grand Bend, ON were removed.",
 "Cold Creek / Castalia, OH (164 min) — lottery-only access per Ohio DNR; not listed.",
 "Maumee River, OH (134 min) — not a stocked trout stream. Huron River (OH) gets only stray steelhead per Ohio DNR; not listed.",
 "Spring Mill Pond (Island Lake RA, ~61 min) is a pond, not a stream; left out of the stream list."]
out = {"generated": datetime.date.today().isoformat(), "home": home,
  "drive_method": "One-way free-flow minutes from home by OSRM public demo server (car). A Valhalla cross-check (drive_min_alt) is typically 10–20% shorter on long highway legs, and real traffic can add 10–25%. Tiers use the OSRM minutes.",
  "tiers": [dict(n=n, name=nm, max=mx, min=(0 if n == 1 else TIERS[n - 2][2])) for n, nm, mx in TIERS],
  "troutroutes_note": TR_NOTE,
  "regs_note": "Designations/Types come from FO-210.26 (designated trout streams, effective Apr 1, 2026) and FO-200.25 (trout & salmon regulations, effective Apr 1, 2025); FO-213.15 explains the gear-restriction criteria (not a stream list). A stream listed in FO-210 but absent from FO-200's Type 2–4 and gear-restricted lists is Type 1 (FO-200 note 1). Page numbers are PDF page indexes. The ArcGIS 'designated trout streams' experience is a JavaScript app that could not be read programmatically, so the order text was used. Always check the current Michigan Fishing Guide.",
  "trips": [GR.TRIP], "streams": streams, "outside_4h": OUT4H, "excluded": EXCL, "no_evidence": reg["no_evidence"], "notes": [n for n in reg["notes"] if "Spring Mill" not in n and "Ontario" not in n]}
json.dump(out, open(os.path.join(ROOT, "explore-streams.json"), "w"), indent=1)
cnt = {}
for s in streams: cnt[s["tier"]] = cnt.get(s["tier"], 0) + 1
print(len(streams), "streams", cnt, os.path.getsize(os.path.join(ROOT, "explore-streams.json")) // 1024, "KB")
for s in streams: print(s["tier"], s["id"], s["drive_min"], s["drive_min_alt"], "stock", len(s["stocking_events"]), "|", s["state"]["badge"][:45], "| flags", len(s["flags"]))
