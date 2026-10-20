"""Streams added in the 4-hour US expansion (hand-entered from FO-200.25 / FO-210.26 PDFs, Michigan Fly Fishing Hub river pages,
Michigan DNR stocking DB, iNaturalist, Ohio DNR). research/drive_times_new.json holds OSRM minutes; research/inat_new.json iNaturalist obs."""
from explore_common import *
DT = json.load(open(R("drive_times_new.json")))
INATJ = json.load(open(R("inat_new.json")))
def inat_catches(key, n=3):
    out = []
    for o in INATJ.get(key, []):
        if not o.get("date") or o.get("obsc"): continue
        out.append({"date": o["date"], "text": f"{o['sp']} photo observation — {(o.get('place') or '').strip(', ')} (iNaturalist, {o['q'].replace('_', ' ')}; a photo within ~5 mi, not a verified catch report)", "url": o["url"]})
        if len(out) >= n: break
    return out
def mk(id, name, county, key, species, wild, repro, st, season, regs, dnr, seasons_text, best, runs, stock, stock_extra, gages, gage_note, conf, flags, sources, access, catches_key=None, tr_cls="unknown", tr_note=None):
    d = DT[key]
    evs = stock_for(**stock) if stock else []
    return {"id": id, "name": name, "county": county, "lat": d["lat"], "lng": d["lng"], "drive_min": d["min"], "drive_miles": d["miles"], "drive_min_alt": d["alt_min"],
        "species": species, "species_groups": groups(species), "wild": wild, "reproduction": repro,
        "tr": dict(cls=tr_cls, type="", gr=("GR" in st["types"]), note=tr_note or "TroutRoutes class not checked yet — send me the class and I'll fill it in."),
        "dnr": dnr, "state": st, "season": season, "regs": regs, "seasons_text": seasons_text, "best_months": best, "runs": runs,
        "stocking_summary": stock_summary(evs, stock_extra), "stocking_events": evs[:40], "catches": inat_catches(catches_key or key), "access": access,
        "gages": [{"id": i, "label": l, "proxy": p} for i, l, p in gages], "gage_note": gage_note, "confidence": conf, "flags": flags, "sources": sources}
RUN_STEEL = {"label": "Steelhead run (typical Sep 25 – Apr 15, peak Oct 25 – Dec 20 per hub tracker)", "months": [10, 11, 12, 3, 4]}
RUN_CHIN = {"label": "Chinook run (typical Aug 27 – Oct 27)", "months": [9, 10]}
RUN_COHO = {"label": "Coho run (typical Sep 12 – Nov 14)", "months": [10, 11]}
RUN_BROWN = {"label": "Lake-run brown (typical Sep 15 – Nov 15)", "months": [10, 11]}
HN = " Run windows are the Michigan Fly Fishing Hub's typical timing, not a forecast."
GENDEF = "Statewide default rules (open all year, 5 trout, 8 in min, brook 7 in)."
NEW = []
NEW.append(mk("au-sable-holy-water", "Au Sable River — Holy Water (Grayling to Wakeley Bridge)", "Crawford", "au-sable-holy-water",
  ["brown trout", "brook trout", "rainbow trout"], "wild", "Wild, self-sustaining brown trout; spring-fed Blue Ribbon water (Michigan Fly Fishing Hub). Not stocked on this reach per the DNR database.",
  state(["2", "GR"], True, "Type 2 + GR flies-only (state-designated)", ["Burton's Landing → South Wakeley Bridge Rd (9.0 mi, the Holy Water): artificial flies only, fishing open all year, possession CLOSED all year (kids <12 may keep 1 trout 8–12 in); bait, scent banned.", "Wakeley Bridge → McMasters Bridge (8.0 mi): fishing open all year, artificial lures only, 2 trout (max 1 ≥18 in); brook & rainbow 10 in, brown 18 in; brook/brown possession last Sat Apr – Sep 30, rainbow all year.", "James St (Business Loop 75) → Burton's Landing: Type 2 (last Sat Apr – Sep 30; brook 10 in, brown 12 in)."], "FO-210.26 p.36 · FO-200.25 p.3 (Type 2), p.12 (Au Sable GR) · FO-213 (GR criteria)", True),
  dict(rule="gr", gr=dict(tackle="flies", cr=True), label="Holy Water (Burton's Landing → Wakeley Bridge): fishing open all year, artificial flies only, possession closed all year (kids <12 may keep 1 trout 8–12 in). Wakeley → McMasters: open all year, lures only, brook/brown kept last Sat Apr – Sep 30. Type 2 above Burton's Landing: last Sat Apr – Sep 30.", also="Type 2 water above Burton's Landing is closed Oct 1 – last Sat in April", src="2026 Michigan Fishing Regulations p.44 · FO-200.25 · DNR Trout & Salmon Regulations layer (GR1/GR2)"),
  "Flies-only no-kill Holy Water; lures-only Wakeley–McMasters (2 trout, brown 18 in); Type 2 above Burton's Landing. Chumming/bait banned on GR reaches.",
  "Designated trout stream (FO-210.26: Au Sable mainstream and tributaries above the Oscoda/Crawford power-line crossing). FO-200.25 lists the Holy Water as a Gear Restricted reach and the stretch above as Type 2.",
  "Hendrickson (May), Sulphur and Brown Drake (June), Hex (late June–July nights); fall BWO and streamers.", [5, 6, 7, 9], [], None, "DNR stocking DB: none for this reach (the DB shows plants at Mio–Alcona and on the East Branch — different water).",
  [("04136500", "Au Sable R at Mio (downstream of the Holy Water)", False)], "04136500 Au Sable River at Mio (live; ~20 mi downstream of the Holy Water, the gage the Hub uses)", "High (regs from FO text; Hub for gear/access)",
  ["The Holy Water boundary is Burton's Landing to Wakeley Bridge — rules differ at each bridge; read the posted signs."],
  [FO210, FO200, FO213, HUB("au-sable-river-holy-water"), HUBBEST], "Public landings below Burton's Landing: Louie's, Keystone, Whirlpool Rd, Thendara Rd, Stephan Bridge, Wakeley Bridge (Michigan Fly Fishing Hub). Marker = Burton's Landing."))
NEW.append(mk("au-sable-south-branch", "Au Sable — South Branch / Mason Tract", "Crawford / Roscommon", "au-sable-south-branch",
  ["brown trout", "brook trout", "rainbow trout"], "wild", "Wild brown trout; spring-fed, thermally stable (Michigan Fly Fishing Hub)",
  state(["GR"], True, "Gear-restricted flies-only, no-kill (state-designated)", ["Chase Bridge Rd → Lower High Banks (4.3 mi, Mason Tract): artificial flies only, fishing open all year, possession CLOSED (kids <12 may keep 1 trout 8–12 in).", "Lower High Banks → confluence with the mainstream (11.5 mi): fishing open all year, artificial flies only (not lures), 2 trout (max 1 ≥18 in); brook & rainbow 10 in, brown 18 in; brook/brown possession last Sat Apr – Sep 30, rainbow all year."], "FO-210.26 p.36 (South Branch to Co. Rd 602) · FO-200.25 p.13 (South Branch GR) · 2026 Fishing Regulations p.44", True),
  dict(rule="gr", gr=dict(tackle="flies", cr=True), label="Chase Bridge → Lower High Banks (Mason Tract): flies only, open all year, possession closed all year. Lower High Banks → mainstream: flies only, open all year, brook/brown kept last Sat Apr – Sep 30 (2 trout, brown 18 in).", also="below Lower High Banks: also flies only; brook/brown may be kept last Sat Apr – Sep 30", src="2026 Michigan Fishing Regulations p.44 · FO-200.25 · DNR Trout & Salmon Regulations layer (GR5/GR6)"),
  "Flies only on the whole South Branch GR water: no-kill Chase Bridge → Lower High Banks (4.3 mi); below Lower High Banks to the mainstream (11.5 mi) still flies only, 2 trout (max 1 ≥18 in), brown 18 in, kept only last Sat Apr – Sep 30. No bait, scent or beads on flies-only water.",
  "Designated trout stream (FO-210.26: South Branch Au Sable upstream to Co. Rd 602 and tributaries). FO-200.25 gear-restricted reaches as listed.",
  "Afternoon BWO, evening Sulphur / Brown Drake; Hex late June. Walk-in wilderness water.", [5, 6, 7, 9], [], None, "No DNR stocking records for the South Branch; wild fishery per the Hub.",
  [("04135700", "South Branch Au Sable R near Luzerne", False)], "04135700 South Branch Au Sable River near Luzerne (live, has water temp)", "High (regs from FO text; Hub for gear/access)",
  ["Remote walk-in/canoe water — the marker is the Chase Bridge Rd access, not the middle of the Mason Tract."],
  [FO210, FO200, FO213, HUB("au-sable-river-south-branch"), HUBBEST], "Chase Bridge (mile 0), Durant's Castle, Canoe Harbor, Smith Bridge (Michigan Fly Fishing Hub). Several miles have no road crossing."))
NEW.append(mk("au-sable-north-branch", "Au Sable — North Branch (Lovells, flies-only)", "Crawford / Otsego", "au-sable-north-branch",
  ["brown trout", "brook trout", "rainbow trout"], "wild", "Wild brown and brook trout (Michigan Fly Fishing Hub)",
  state(["GR"], True, "Gear-restricted flies-only (state-designated)", ["Sheep Ranch → confluence with the mainstream (20.7 mi): artificial flies only; fishing open all year; brook/brown possession last Sat Apr – Sep 30 (rainbow year-round); 2 trout, only 1 ≥18 in; brook 10 in, brown 18 in, rainbow 10 in; bait/scent banned.", "Above Sheep Ranch (designated, not listed in FO-200 Type 2–4): Type 1 by FO-200 note 1 — not independently verified."], "FO-210.26 p.36 (North Branch upstream) · FO-200.25 p.13 (North Branch GR)", True),
  dict(rule="gr", gr=dict(tackle="flies", cr=False), label="Sheep Ranch → mainstream: fishing open all year, artificial flies only; brook/brown possession last Sat Apr – Sep 30, rainbow all year; 2 trout (max 1 ≥18 in).", src="2026 Michigan Fishing Regulations p.44 · FO-200.25 · DNR Trout & Salmon Regulations layer (GR4)"),
  "Flies-only 20.7 mi: 2 trout (one ≥18 in), browns 18 in minimum, brook 10 in; no bait or scent.",
  "Designated trout stream (FO-210.26: North Branch Au Sable and tributaries). FO-200.25 gear-restricted flies-only from Sheep Ranch to the confluence.",
  "Evening Sulphur and Brown Drake; wild brookies take small attractors; Hex in late June.", [5, 6, 7, 9], [], None, "No DNR stocking records for the North Branch.",
  [("04135800", "North Branch Au Sable R at Kelloggs Bridge near Lovells", False)], "04135800 NB Au Sable River at Kelloggs Bridge near Lovells (live, has water temp)", "High (regs from FO text; Hub for access)",
  ["Fishing is legal all year here but you may only keep brook/brown in season."],
  [FO210, FO200, FO213, HUB("au-sable-river-north-branch"), HUBBEST], "Lovells Bridge (mile 0), Kellogg's Bridge, Morley Rd, McMasters Bridge (Michigan Fly Fishing Hub). Marker = Lovells."))
NEW.append(mk("manistee-upper", "Upper Manistee River (flies-only M-72 → CCC Bridge)", "Crawford / Kalkaska", "manistee-upper",
  ["brown trout", "brook trout", "rainbow trout"], "both", "Wild brown and brook trout (Michigan Fly Fishing Hub); DNR also stocks brown trout in Kalkaska/Wexford Cos.",
  state(["2", "GR"], True, "Type 2 + GR (flies-only M-72 → CCC Bridge; state-designated)", ["Type 2 (CR 612 upstream to the headwaters): last Sat Apr – Sep 30; brook 10 in, brown 12 in.", "CR 612 → M-72 (9.2 mi): fishing open all year, artificial lures only, 2 trout (1 ≥18 in), browns 18 in; brook/brown kept last Sat Apr – Sep 30.", "M-72 → Sunset Trail Rd/CCC Bridge (16.7 mi): fishing open all year, artificial flies only, 2 trout (1 ≥18 in); brook & rainbow 10 in, brown 18 in; brook/brown kept last Sat Apr – Sep 30, rainbow all year.", "CCC Bridge → M-115: Type 4 (fishing all year; brook/brown kept last Sat Apr – Sep 30)."], "FO-210.26 p.20/22 · FO-200.25 p.3 (Type 2), p.17 (Manistee GR), p.11 (Type 4)", True),
  dict(rule="gr", gr=dict(tackle="flies", cr=False), label="M-72 → CCC Bridge: fishing open all year, artificial flies only. CR 612 → M-72: open all year, artificial lures only. Both: brook/brown possession last Sat Apr – Sep 30, rainbow all year; 2 trout (max 1 ≥18 in). Type 2 above CR 612: last Sat Apr – Sep 30. CCC Bridge → M-115: Type 4 (open all year).", also="lures only CR 612 → M-72; Type 2 water above CR 612 closed Oct 1 – last Sat in April", src="2026 Michigan Fishing Regulations p.45 · FO-200.25 · DNR Trout & Salmon Regulations layer (GR14/GR15)"),
  "Flies-only M-72 → CCC Bridge (16.7 mi); lures-only CR 612 → M-72; Type 2 upstream of CR 612. Browns 18 in minimum on the GR reaches, 2 trout (one ≥18 in).",
  "Designated trout stream (FO-210.26). FO-200.25: Type 2 above CR 612, lures-only CR 612–M-72, flies-only M-72–CCC Bridge, Type 4 CCC Bridge–M-115.",
  "Evening Sulphur and Brown Drake; wild browns on dries and nymphs; cool water through summer (Hub).", [5, 6, 7, 9], [], dict(waters=["Manistee River"], counties=["Kalkaska", "Wexford", "Missaukee"]), "",
  [("04123500", "Manistee R near Grayling (at M-72, top of the flies-only reach)", False), ("04124000", "Manistee R near Sherman (far downstream)", True)], "04123500 Manistee River near Grayling sits at the M-72 crossing (live flow, gage height and water temp); 04124000 near Sherman is far downstream (proxy only)", "Medium-High (regs from FO; marker approximate)",
  ["The marker is the river near Sharon (Kalkaska Co.), between the CCC Bridge and M-115 (Type 4). The flies-only water is upstream (M-72 → CCC Bridge) — pick your reach from the order, not the pin."],
  [FO210, FO200, FO213, HUB("upper-manistee-river"), HUBBEST, "https://www2.dnr.state.mi.us/publications/pdfs/DNRFishLibrary/StatusoftheFisheryResourceReports/0345_2020_UpperManisteeRiver.pdf (DNR SFR 2020-283, access sites)", "https://waterdata.usgs.gov/monitoring-location/04123500/ (USGS gage at M-72)"], "Flies-only reach, upstream first: M-72 State Forest Campground (RM 166.6), Hole in the Wall, Hole in the Fence, Tree Farm, Yellowtrees Landing, Burnt Cabin, CCC Bridge State Forest Campground (drift-boat launches per DNR SFR 2020-283; river miles per BirdTrout/MDNR). Below CCC: 3 Mile Bend, 4 Mile Bend, Thayer Rd. Most road crossings allow wade access. Hub lists M-72 Bridge, CCC Bridge, M-66 Bridge, US-131. Marker approximate (Sharon area).",
  tr_note="TroutRoutes class is app-gated (PRO Guide Mode); no public stream page found (checked Oct 2026)."))
NEW.append(mk("pere-marquette", "Pere Marquette River (Baldwin) — flies-only M-37 → Gleason's Landing", "Lake / Mason", "pere-marquette",
  ["steelhead", "brown trout", "chinook", "coho"], "both", "Stocked brown trout plus wild-reproducing steelhead/brown (Michigan Fly Fishing Hub); DNR stocks browns in Lake and Mason Cos.",
  state(["GR"], True, "Gear-restricted flies-only M-37 → Gleason's (state-designated)", ["M-37 → Gleason's Landing (8.5 mi): artificial flies only, fishing open all year, possession CLOSED all year (kids <12: 1 trout/salmon 8–12 in).", "Gleason's Landing → Rainbow Rapids (10.5 mi): last Sat Apr – Aug 31 gear-restricted, artificial lures only, 2 trout/salmon (max 1 brown ≥18 in, max 1 rainbow; no brook/brown 14–18 in kept); Sep 1 – Fri before last Sat Apr Type 4 rules (bait allowed) with 0 brook, 0 brown, 1 rainbow (10 in).", "Rainbow Rapids → Reek Rd: Type 4, max 1 rainbow; Reek Rd → Old US-31: Type 3, max 1 rainbow."], "FO-210.26 p.23 · FO-200.25 p.18 (PM GR), p.4/p.6 (Type 3/4 reaches)", True, "FO-200/FO-210 text read; Gleason's → Rainbow Rapids confirmed in the 2026 guide p.46 and DNR regulations layer"),
  dict(rule="gr", gr=dict(tackle="flies", cr=True), label="M-37 → Gleason's Landing: fishing open all year, artificial flies only, possession closed all year (kids <12: 1 trout/salmon 8–12 in). Gleason's → Rainbow Rapids: Sep 1 – Fri before last Sat Apr Type 4 with 0 brook/0 brown/1 rainbow; last Sat Apr – Aug 31 lures only.", also="below Gleason's the rules switch on Sep 1 (Type 4, bait OK, 1 rainbow, no brook/brown) and the last Sat in April (lures only)", src="2026 Michigan Fishing Regulations p.46 · FO-200.25 · DNR Trout & Salmon Regulations layer (GR18/GR19)"),
  "Flies-only no-kill M-37 → Gleason's Landing; lower reaches Type 4/3 with a 1-rainbow limit. Rules change on Sep 1 and the last Sat in April — check the reach/date.",
  "Designated trout stream (FO-210.26). FO-200.25 gear-restricted and Type 3/4 reaches as above. Wild & Scenic River.",
  "Fall run Sep–Nov (kings, coho, lake-run browns), steelhead Oct–Apr; Hendrickson (May), Sulphur / Brown Drake (June)." + HN, [4, 5, 6, 10, 11], [RUN_CHIN, RUN_COHO, RUN_BROWN, RUN_STEEL],
  dict(waters=["Pere Marquette River", "Big S Br Pere Marquette River"]), "",
  [("04122500", "Pere Marquette R at Scottville", False)], "04122500 Pere Marquette River at Scottville (live, flow only; downstream of the main fishing water)", "High (regs from FO text; Hub for gear/access)",
  ["Marker is Baldwin town; the flies-only water starts at the M-37 bridge just south."],
  [FO210, FO200, FO213, HUB("pere-marquette-river"), HUBBEST, DBURL], "Gleason's Landing, Green Cottage, Rainbow Rapids, Bowman Bridge, Sulak Landing, Upper Branch Bridge, Custer (Michigan Fly Fishing Hub). Wade the flies-only stretch; float below Bowman."))
NEW.append(mk("muskegon-croton", "Muskegon River tailwater (below Croton Dam)", "Newaygo", "muskegon-croton",
  ["steelhead", "brown trout", "coho", "smallmouth bass"], "stocked", "Stocked steelhead, brown trout and coho (DNR DB); smallmouth bass are a summer bonus (Michigan Fly Fishing Hub best-rivers page)",
  state(["3"], False, "Type 3 (Croton Dam → M-120) · not Type 1/2", ["Type 3 (FO-200): fishing and possession open all year; brook/brown 15 in minimum, steelhead/salmon 10 in; 5 trout/salmon (max 3 ≥15 in); up to 5 rainbows, max 1 ≥20 in.", "Aug 1 – Nov 15 (mouth → Croton Dam): single-point hooks / small trebles only on body baits, plugs, spoons (Hub)."], "FO-200.25 p.5 (Type 3: Muskegon River, Croton Dam → M-120) · Hub", False),
  dict(rule="year_round", label="Type 3: open all year (15 in brook/brown minimum)"),
  "Type 3: open all year; 15 in minimum on brook/brown; steelhead/salmon 10 in; up to 5 rainbows (1 ≥20 in); terminal-tackle rule Aug 1 – Nov 15.",
  "FO-200.25 lists the Muskegon River from Croton Dam to M-120 as Type 3 (tailwater steelhead fishery). Upstream reaches in FO-210 are designated but far from Croton.",
  "Steelhead fall–spring; summer smallmouth; browns year-round." + HN, [3, 4, 10, 11], [RUN_STEEL, RUN_CHIN],
  dict(waters=["Muskegon River"], counties=["Newaygo"]), "",
  [("04121970", "Muskegon R near Croton", False)], "04121970 Muskegon River near Croton (live, has water temp)", "High (regs from FO text; stocking from DB)",
  ["Terminal-tackle rule (single-point hooks / limited trebles on body baits) applies Aug 1 – Nov 15 from the mouth to Croton Dam, for the whole salmon/steelhead run (Hub)."],
  [FO200, HUB("muskegon-river"), HUBBEST, DBURL], "Croton Dam, Pine Street launch, Thornapple launch, Henning Park, Bridgeton Park, Newaygo (Michigan Fly Fishing Hub). Marker = Croton Dam."))
NEW.append(mk("rifle-river", "Rifle River (Rifle River Recreation Area, Ogemaw Co.)", "Ogemaw / Arenac", "rifle-river",
  ["brown trout", "rainbow trout", "steelhead", "chinook"], "both", "Wild brown trout on the upper river (Hub) plus stocked brown/rainbow (DNR DB); the lower river gets steelhead/chinook from Saginaw Bay (Hub)",
  state(["3"], "partial", "Designated upper river · FO-200 Type 3 below Sage Lake Rd", ["Designated trout stream above T19N R4E S5 (mainstream and tributaries, FO-210). FO-200 lists the Rifle River as Type 3 from Sage Lake Rd (T23N R3E S22) to Saginaw Bay.", "Reaches above Sage Lake Rd are not in FO-200 Type 2–4, so Type 1 by FO-200 note 1 (not independently verified).", "Type 3: open all year; brook/brown 15 in minimum."], "FO-210.26 p.38 · FO-200.25 p.4 (Type 3: Rifle River)", False, "FO text read; reach boundary vs. Rec Area not verified"),
  dict(rule="year_round", label="Type 3 below Sage Lake Rd (open all year, 15 in brook/brown); above it Type 1 (last Sat Apr – Sep 30) — verify your reach"),
  "Type 3 below Sage Lake Rd (open all year; brook/brown 15 in); above it likely Type 1 (last Sat Apr – Sep 30).",
  "Mainstream and tributaries above T19N R4E S5 are designated trout waters (FO-210.26); FO-200.25 lists Type 3 Sage Lake Rd → Saginaw Bay.",
  "Hex hatch late June; Hendrickson, Sulphur/Light Cahill and caddis in summer evenings; fall streamers for pre-spawn browns." + HN, [5, 6, 7, 9, 10], [],
  dict(waters=["Rifle River"], counties=["Ogemaw"]), "",
  [("04142000", "Rifle R near Sterling (downstream — proxy)", True)], "04142000 Rifle River near Sterling (live, flow only; well downstream of the Rec Area)", "Medium (marker approximate; regs boundary unverified)",
  ["The marker is the Rifle River Trail / Rec Area vicinity (geocoded, approximate). Confirm whether you're above or below Sage Lake Rd before assuming Type 1 vs Type 3."],
  [FO210, FO200, HUB("rifle-river"), HUBBEST, DBURL], "Rifle River Recreation Area (large public tract on the upper river), Omer, Sterling, Maple Ridge (Michigan Fly Fishing Hub). Mostly wading."))
NEW.append(mk("au-gres-east-branch", "Au Gres River & East Branch (Whitney Drain) steelhead", "Arenac / Iosco", "au-gres-east-branch",
  ["steelhead", "rainbow trout", "brown trout", "coho"], "stocked", "Stocked: recent DNR plants go to the East Branch (Whitney Drain) (DNR DB)",
  state(["3"], False, "East Branch Type 3 · main river unclassified", ["East Branch Au Gres (Whitney Drain) M-55 → Saginaw Bay: Type 3 — open all year, brook/brown 15 in minimum.", "Mainstem is not a designated trout stream: statewide rules; dip netting prohibited from Saginaw Bay up to M-65 (Hub)."], "FO-200.25 p.4 (Type 3: East Branch Au Gres River) · Hub", False),
  dict(rule="year_round", label="Open all year (East Branch Type 3: 15 in brook/brown; steelhead 10 in)"),
  "East Branch (Whitney Drain) is Type 3: open all year, brook/brown 15 in, steelhead 10 in. Mainstem: statewide default; no dip netting Saginaw Bay to M-65.",
  "East Branch Au Gres (Whitney Drain) is FO-200 Type 3; the mainstem is not in FO-210.",
  "Steelhead run typical Sep 25 – Apr 15 (Hub)." + HN, [3, 4, 10, 11], [RUN_STEEL],
  dict(waters=["East Br Au Gres River"]), "",
  [("04138536", "Au Gres R at S Mackinaw Rd near Au Gres", False)], "04138536 Au Gres River at S Mackinaw Rd (live, flow only, lower river)", "Medium",
  ["Smaller steelhead water; the Hub points to paddle/launch lower-river fishing rather than wading."],
  [FO200, HUB("au-gres-river"), DBURL], "Au Gres city boat launch/riverfront park, city park/campground; East Branch: Singing Bridge on US-23 and the lower Whitney Drain (Michigan Fly Fishing Hub)."))
NEW.append(mk("au-sable-foote-dam", "Au Sable River below Foote Dam (Oscoda) — steelhead & salmon", "Iosco", "au-sable-foote-dam",
  ["steelhead", "brown trout", "chinook", "coho"], "stocked", "Lake Huron run fish (kings, coho, lake-run browns, steelhead)",
  state(["3"], False, "Type 3 (Foote Dam → Lake Huron) · not Type 1/2", ["Type 3: open all year, bait legal; brook/brown 15 in minimum, steelhead/salmon/lake trout 10 in; 5 trout/salmon (max 3 ≥15 in)."], "FO-200.25 p.4 (Type 3: Au Sable River, Foote Dam → Lake Huron)", False),
  dict(rule="year_round", label="Type 3: open all year (15 in brook/brown)"),
  "Type 3: open all year, bait legal, 15 in brook/brown, 10 in steelhead/salmon. NOT the flies-only 'Au Sable' — that is the Holy Water near Grayling.",
  "FO-200.25 lists the Au Sable below Foote Dam as Type 3. The designated, gear-restricted waters are ~60 river miles upstream.",
  "Salmon Aug–Nov, steelhead Sep–Apr, lake-run browns Sep–Nov." + HN, [3, 4, 9, 10, 11], [RUN_CHIN, RUN_COHO, RUN_BROWN, RUN_STEEL],
  None, "DNR stocking DB: only walleye recorded on this reach since Oct 2021 — trout/salmon here are Lake Huron fish.",
  [("04137500", "Au Sable R near Au Sable (below Foote Dam)", False)], "04137500 Au Sable River near Au Sable (live, has water temp, below Foote Dam)", "Medium (regs from FO; fishery details from Hub)",
  ["No DNR trout stocking in the database for this reach; fish are strays/Lake Huron runs."],
  [FO200, HUB("au-sable-river-foote-dam"), HUBBEST], "Foote Dam, Whirlpool, Rea Road, Five Channels, the mouth at Oscoda (Michigan Fly Fishing Hub). Marker = Foote Dam."))
NEW.append(mk("kalamazoo-allegan", "Kalamazoo River (Allegan Dam to Saugatuck)", "Allegan", "kalamazoo-allegan",
  ["steelhead", "chinook", "coho"], "stocked", "Stocked steelhead (rainbow), chinook and coho (DNR DB, Allegan Co.)",
  state(["3"], False, "Type 3 (Calkins Dam → US-31)", ["Type 3: open all year; brook/brown 15 in minimum; steelhead/salmon 10 in."], "FO-200.25 p.4 (Type 3: Kalamazoo River, Allegan) · Hub", False),
  dict(rule="year_round", label="Type 3: open all year"),
  "Type 3 reach from Calkins Dam to US-31: open all year, 15 in brook/brown, 10 in steelhead/salmon.",
  "FO-200.25 lists the Kalamazoo River from Calkins Dam to US-31 as Type 3. Not a designated inland trout stream.",
  "Salmon and steelhead runs (Allegan Dam to Saugatuck); mostly a float fishery per the Hub." + HN, [3, 4, 10, 11], [RUN_STEEL, RUN_CHIN, RUN_COHO],
  dict(waters=["Kalamazoo River", "Kalamazoo River (Saugatuck)"], counties=["Allegan"]), "",
  [("04108660", "Kalamazoo R at New Richmond", False)], "04108660 Kalamazoo River at New Richmond (live, has water temp)", "Medium",
  ["Very little wadeable water (Hub): this is a boat fishery."], [FO200, HUB("kalamazoo-river"), DBURL], "Allegan Dam, New Richmond, Saugatuck, Douglas (Michigan Fly Fishing Hub). Float."))
NEW.append(mk("grand-river-gr", "Grand River — Sixth Street Dam, Grand Rapids (salmon & steelhead)", "Kent", "grand-river-gr",
  ["chinook", "steelhead", "brown trout"], "stocked", "Great Lakes run fish; the DNR database has only a few trout plants on the Grand (Ottawa Co.)",
  NONE("Grand River mainstem at Grand Rapids is not typed in FO-210/FO-200 as a trout stream — " + GENDEF),
  dict(rule="year_round", label="Open all year below the Sixth Street Dam (statewide default rules)"),
  "No river-specific trout limit on the mainstem (Hub); statewide default: 5 trout, 8 in minimum (brook 7 in), open all year.",
  "Not designated (FO-210) and not a typed stream in FO-200.",
  "Fall salmon at the Sixth Street Dam / fish ladder, steelhead Oct–Apr." + HN, [4, 9, 10, 11], [RUN_CHIN, RUN_STEEL],
  dict(waters=["Grand River (Ottawa County)"], counties=["Ottawa"]), "DNR DB records for the Grand are mostly walleye/muskie; the few trout records are from the Ottawa Co. reach near Grand Haven.",
  [("04119000", "Grand R at Grand Rapids", False)], "04119000 Grand River at Grand Rapids (live, flow only)", "Medium",
  ["Urban river; Hub: wade at the dam, the rest is a boat river."], [HUB("grand-river"), HUBBEST, FO200], "Sixth Street Dam and Fish Ladder Park, Ann St, Fulton St, Jenison, Grand Haven (Michigan Fly Fishing Hub)."))
NEW.append(mk("rogue-river", "Rogue River (Rockford Dam to the Grand)", "Kent", "rogue-river",
  ["steelhead", "rainbow trout", "brown trout", "coho"], "stocked", "Stocked (DNR DB: browns, rainbows, coho). The Hub notes the Rogue's rainbow stocking includes non-steelhead strains.",
  state(["4"], False, "Type 4 · 5-rainbow special rule", ["Type 4 (FO-200): fishing open all year; brook/brown possession last Sat Apr – Sep 30; rainbow year-round.", "Rockford Dam → Grand River: up to 5 rainbows/day (≤3 ≥15 in, max 1 ≥20 in)."], "FO-200.25 p.6/p.9 (Type 4: Rogue River, Kent Co.) · Hub", False),
  dict(rule="type4", label="Type 4: fishing open all year; brook/brown kept last Sat Apr – Sep 30; rainbows year-round (up to 5)"),
  "Type 4: open all year; brook/brown possession last Sat Apr – Sep 30; up to 5 rainbows (max 3 ≥15 in, 1 ≥20 in).",
  "FO-200.25 Type 4 (Rockford Dam to the Grand River). Nash, Ball and Buck Creeks are separate Type 4 listings.",
  "Spring and fall steelhead below Rockford Dam." + HN, [3, 4, 10, 11], [RUN_STEEL],
  dict(waters=["Rogue River"]), "",
  [("04118500", "Rogue R near Rockford", False)], "04118500 Rogue River near Rockford (live, flow only)", "Medium-High",
  ["Some reaches have soft bottoms and fish better from a boat (Hub)."], [FO200, HUB("rogue-river"), DBURL], "Peppler Park at Rockford Dam, Pickett Park, Belmont, Jericho, Childsdale and Packer Dr (Michigan Fly Fishing Hub). Mostly wadeable below the dam."))
NEW.append(mk("coldwater-barry", "Coldwater River (Barry/Kent Co., Freeport–Middleville)", "Barry / Kent", "coldwater-barry",
  ["brown trout", "rainbow trout"], "stocked", "Stocked brown and rainbow trout (DNR DB: Barry and Kent Cos.)",
  state(["2", "4"], True, "Type 2 above Freeport Rd (state-designated) · Type 4 below", ["Type 2: M-43 bridge → Freeport Rd bridge: last Sat Apr – Sep 30; brook 10 in, brown 12 in.", "Type 4: Freeport Rd → Thornapple River confluence: fishing all year; brook/brown possession last Sat Apr – Sep 30."], "FO-210.26 p.28 (Coldwater mainstream) · FO-200.25 p.3 (Type 2), p.7 (Type 4)", True),
  dict(rule="last_sat_apr_sep30", label="Type 2 (M-43 → Freeport): last Sat Apr – Sep 30; Type 4 below Freeport: fishing all year", also="Type 4 below Freeport Rd is open all year (brook/brown catch & release until the last Sat in April)"),
  "Type 2 reach: last Sat Apr – Sep 30, 5 trout (max 3 ≥15 in), brook 10 in, brown 12 in. Type 4 below Freeport Rd: fishing all year, brook/brown kept last Sat Apr – Sep 30.",
  "Designated trout stream (FO-210.26: Coldwater River mainstream to the M-43 bridge, plus several Barry Co. tributaries). FO-200.25 Type 2 (M-43 → Freeport Rd) and Type 4 below.",
  "Spring (after stocking) through early fall; check water temperature July–August.", [4, 5, 6, 9], [],
  dict(waters=["Coldwater River"], counties=["Barry", "Kent"]), "",
  [("04117500", "Thornapple R near Hastings (regional proxy only)", True)], "No gage on this reach; 04117500 Thornapple River near Hastings (live flow) is regional context only", "Medium-High",
  ["The marker is Freeport (the Type 2/Type 4 boundary). This is the Barry/Kent Co. Coldwater River (a Thornapple tributary), not the Coldwater in Branch Co."],
  [FO210, FO200, DBURL], "Public road crossings between M-43 and Freeport (iNaturalist photos near Alto/Freeport, N Country Trail). Public access not researched — verify before driving."))
NEW.append(mk("augusta-creek", "Augusta Creek (Barry/Kalamazoo Cos.)", "Barry / Kalamazoo", "augusta-creek",
  ["brown trout"], "stocked", "Stocked brown trout (DNR DB: 13 plants since Oct 2021)",
  state(["4"], True, "State-designated · FO-200 Type 4 reach (to Knappen Mills Dam)", ["FO-200 lists Augusta Creek (Little Gilkey Lake & Fair Lakes outlets → Knappen Mills Dam) as Type 4: fishing all year; brook/brown possession last Sat Apr – Sep 30.", "Designated trout stream in FO-210 (Augusta Creek to the Knappen Mills Dam)."], "FO-210.26 p.29 · FO-200.25 p.8 (Type 4: Augusta Creek)", False, "FO text read; headwater reaches may be Type 1 (not verified)"),
  dict(rule="type4", label="Type 4 reach: fishing open all year; brook/brown kept last Sat Apr – Sep 30"),
  "Type 4 listed reach: fishing all year; brook/brown possession last Sat Apr – Sep 30; 5 trout; brook 7 in, brown 10 in.",
  "Designated trout stream (FO-210.26) and FO-200.25 Type 4 listed reach; headwater/tributary reaches not listed in FO-200 would be Type 1.",
  "Spring after stocking, early summer, fall.", [4, 5, 6, 9], [], dict(waters=["Augusta Creek"]), "",
  [("04105700", "Augusta Creek near Augusta", False)], "04105700 Augusta Creek near Augusta (live, flow only)", "Medium",
  ["Small stocked creek; public access not researched — the marker is the village of Augusta."], [FO210, FO200, DBURL], "Augusta area (Kalamazoo/Barry Cos.). Specific public access sites not researched."))
NEW.append(mk("rice-nottawa", "Rice, Nottawa & Dickinson Creeks (Marshall/Battle Creek, Calhoun Co.)", "Calhoun", "rice-nottawa",
  ["brown trout"], "stocked", "Stocked brown trout (DNR DB: Rice 10, Nottawa 15, Dickinson 5 plants since Oct 2021)",
  state(["4", "1"], True, "Designated · Rice/Nottawa Type 4, Dickinson Type 1", ["South Branch Rice Creek and Nottawa Creek are FO-200 Type 4 reaches (fishing all year; brook/brown possession last Sat Apr – Sep 30).", "Dickinson Creek is designated in FO-210 and not in FO-200 Type 2–4 → Type 1 (last Sat Apr – Sep 30)."], "FO-210.26 p.29–30 · FO-200.25 p.7 (Type 4: Nottawa, Rice)", False, "FO text read; Dickinson Type 1 by FO-200 note 1"),
  dict(rule="type4", label="Rice/Nottawa Type 4: fishing all year, brook/brown kept last Sat Apr – Sep 30; Dickinson Type 1: last Sat Apr – Sep 30"),
  "Mixed: Type 4 on the Rice/Nottawa listed reaches; Dickinson Creek Type 1 (last Sat Apr – Sep 30). 5 trout; brook 7 in; brown 8 in (Type 1) / 10 in (Type 4).",
  "Designated trout streams (FO-210.26) with FO-200.25 Type 4 reaches for Rice (S. Branch) and Nottawa.",
  "Spring after stocking through early summer; fall.", [4, 5, 6, 9], [], dict(waters=["Rice Creek", "Nottawa River", "Dickinson Creek"]), "",
  [("04103500", "Kalamazoo R at Marshall (regional proxy only)", True)], "No creek gage; 04103500 Kalamazoo River at Marshall (live flow) is context only", "Medium-Low (three small creeks combined; marker is Marshall)",
  ["Three separate creeks combined into one card; the pin is Marshall, not any single creek."], [FO210, FO200, DBURL], "Marshall / Battle Creek area (Calhoun Co.). Specific access sites not researched — verify before driving."))
NEW.append(mk("st-joseph-maumee", "St. Joseph River of the Maumee (Pittsford, Hillsdale Co.)", "Hillsdale", "st-joseph-maumee",
  ["brown trout"], "stocked", "Stocked brown trout (DNR DB, 12 plants since Oct 2021)",
  state(["1"], True, "Type 1 · state-designated", ["Designated: Pittsford Rd upstream to Trail Rd (except the Pittsford Millpond impoundment). Not in FO-200 Type 2–4 → Type 1: last Sat Apr – Sep 30; 5 trout (max 3 ≥15 in); brook 7 in, brown 8 in."], "FO-210.26 p.40 · FO-200.25 p.2 (Type 1 rule)", True),
  dict(rule="last_sat_apr_sep30", label="Type 1 (designated): last Sat in April – Sep 30"),
  "Type 1: fishing and possession last Sat in April – Sep 30; 5 trout (max 3 ≥15 in); brook 7 in, brown 8 in.",
  "Designated trout stream (FO-210.26: St. Joseph-of-the-Maumee, Pittsford Rd to Trail Rd, Hillsdale Co.).",
  "Spring after stocking through early summer.", [4, 5, 6], [], dict(waters=["St Joseph of the Maumee"]), "",
  [], "No USGS gage found near Pittsford for this creek-scale water.", "Medium",
  ["No gage; the pin is the village of Pittsford — put-in points not researched. This is not the St. Joseph River of Lake Michigan."], [FO210, FO200, DBURL], "Pittsford Rd to Trail Rd reach, Hillsdale Co. Public access sites not researched — verify."))
KIDDER = mk("kidder-creek", "Kidder Creek (wild brookies)", "Macomb (Bruce Twp)", "kidder-creek",
  ["wild brook trout", "brown trout"], "wild", "Wild brook trout: the 2002 DNR survey at Boardman Rd found brook trout (8.6% of the catch) and a few browns (1.4%) and called it 'a good cold water stream' (SR39 p.38, Table 20). Brook trout were collected here in 1927 (UMMZ 82620, 'Burr Creek', same Kidder Rd culvert location). No newer survey found.",
  state(["1"], "partial", "Type 1? · designation unclear — confirm with DNR", ["FO-210.26 designates the North Branch Clinton and its tributaries above 32 Mile Rd, but italicizes an exception for 'Tributaries to North Branch upstream from confluence of East Pond Creek (T5N, R13E, S31)' in Macomb Co. Kidder Creek is a Macomb tributary above that confluence, so it may be excluded.", "If excluded it is non-designated water (FO-200 general rule: trout season open all year; 5 trout, brook 7 in). If designated, Type 1 (last Sat Apr – Sep 30). Confirm with DNR Southfield Fisheries, 248-359-9040, before fishing outside the Type 1 season."], "FO-210.26 p.39 · FO-200.25 p.1–2", False, "FO text read; application to Kidder Creek not confirmed"),
  dict(rule="last_sat_apr_sep30", label="Treated as Type 1 (last Sat in April – Sep 30) until DNR confirms — it may be non-designated (open all year)", inferred=True),
  "If designated: Type 1 — 5 trout (max 3 ≥15 in), brook trout 7 in, brown 8 in, last Sat in April – Sep 30. If excluded from FO-210: statewide default (open all year, 5 trout, brook 7 in). Confirm with DNR Southfield 248-359-9040.",
  "FO-210.26 lists the North Branch Clinton above 32 Mile Rd with an italicized exception for Macomb tributaries upstream of the East Pond Creek confluence; whether that removes Kidder Creek has not been confirmed with DNR.",
  "Tiny spring creek: opener through June and September; summer only in cool spells. Dap or roll-cast small dries and terrestrials.", [4, 5, 6, 9], [], None,
  "History: 500 brown trout in 1972 (SR39 Table 25); no other stocking found. No trout stocked since (DNR stocking DB).",
  [("04164151", "N Branch Clinton R at 26 Mile (flow only, no temp; far downstream)", True)],
  "No gage on Kidder Creek. Nearest live gage is 04164151 North Branch Clinton at 26 Mile Rd (flow and gage height only, no temperature) — context only. USGS 04164022 at Kidder Rd is an inactive sampling site.",
  "Medium-Low (wild brookies last documented 2002; designation and access unconfirmed)",
  ["regulation: may be excluded from the designated trout-stream list (Macomb tributaries above the East Pond Creek confluence) — confirm with DNR Southfield 248-359-9040", "access: no public land found — road crossings only; see the private-water caution", "no fish survey since 2002 found"],
  [FO210, FO200, SR39, CRWC_CW, UMMZ[1], NAS98] + NAVSRC,
  "No public land found. Road crossings: Kidder Rd (the pin; old USGS site 04164022 and the 1927 museum collection spot) and Bordman Rd (the 2002 DNR survey site). " + NAVCAUTION)
KIDDER["history"] = NBHIST
NEW.append(KIDDER)
OHSRC = ["https://ohiodnr.gov/buy-and-apply/hunting-fishing-boating/fishing-resources/steelhead-fishing-promo", "https://dam.assets.ohio.gov/image/upload/ohiodnr.gov/documents/wildlife/fish-management/Ohio_Steelhead_Stockings_2021-2025.pdf", "https://dam.assets.ohio.gov/image/upload/ohiodnr.gov/documents/wildlife/laws-regs-licenses/OhioFishingRegs_English.pdf"]
OHREG = "Ohio rules (2026-27 regs): Lake Erie tributaries Mar 1 – May 15: 2/day; May 16 – Aug 31: 5/day, 12 in min; Sep 1 – Feb 28: 2/day, 12 in min. Snagging illegal Sep 1 – Apr 30. Ohio fishing license required (not a Michigan license)."
OHRUN = {"label": "Steelhead run (Ohio DNR: fall through spring)", "months": [10, 11, 12, 1, 2, 3, 4]}
NEW.append(mk("vermilion-oh", "Vermilion River, Ohio (Lake Erie steelhead, mouth to Wakeman Dam)", "Erie / Lorain (OH)", "vermilion-oh",
  ["steelhead"], "stocked", "Ohio DNR stocks ~50,000 Little Manistee-strain yearling steelhead each spring (50,021 in 2025; 2026 target 50,000) — one of five primary Ohio steelhead streams",
  state([], False, "Ohio water — no Michigan trout-stream types", [OHREG], "Ohio DNR 2026-27 Fishing Regulations · Michigan FO-200/FO-210 do not apply", False, "Ohio DNR pages read"),
  dict(rule="year_round", label="Open (Ohio Lake Erie tribs: 2/day Sep 1 – Feb 28, 12 in min; steelhead season ~Oct–May)"),
  OHREG + " Public access only — stream beds are private unless on public land.",
  "Ohio waters — Michigan designated-trout-stream types do not apply. Ohio DNR lists the Vermilion among its five primary stocked steelhead streams.",
  "Steelhead fall through spring (Ohio DNR: Oct–May; fish harbor/lower river early and late, whole river mid-season).", [10, 11, 12, 1, 2, 3, 4], [OHRUN],
  None, "Ohio DNR stocking: 50,021 steelhead smolts in 2025 (65,453 in 2021, 58,954 in 2022, 55,000 in 2023, 50,024 in 2024); not in Michigan's database.",
  [("04199500", "Vermilion R near Vermilion, OH", False)], "04199500 Vermilion River near Vermilion OH (live, flow only)", "Medium-High (Ohio DNR sources)",
  ["Ohio, not Michigan: separate license and rules. Marker is Vermilion town."], OHSRC + ["https://dam.assets.ohio.gov/image/upload/ohiodnr.gov/documents/wildlife/river-stream-fishing/vermilionriver.pdf"],
  "Public access (Ohio DNR map): Vermilion municipal boat ramp, Jerusalem Rd access, Mill Hollow, Bacon Woods, Peasley Rd, Gore Orphanage Rd (roadside), Schoepfle Garden, Wakeman Dam."))
NEW.append(mk("rocky-river-oh", "Rocky River, Ohio (Lake Erie steelhead, marina to Lagoon Dam)", "Cuyahoga (OH)", "rocky-river-oh",
  ["steelhead"], "stocked", "Ohio DNR stocks ~80,000 Little Manistee-strain yearling steelhead each spring (80,045 in 2025; 2026 target 80,000)",
  state([], False, "Ohio water — no Michigan trout-stream types", [OHREG], "Ohio DNR 2026-27 Fishing Regulations · Michigan FO-200/FO-210 do not apply", False, "Ohio DNR pages read"),
  dict(rule="year_round", label="Open (Ohio Lake Erie tribs: 2/day Sep 1 – Feb 28, 12 in min; steelhead season ~Oct–May)"),
  OHREG + " Public access (Cleveland Metroparks Rocky River Reservation).",
  "Ohio waters — Michigan designated-trout-stream types do not apply. Ohio DNR lists the Rocky among its five primary stocked steelhead streams.",
  "Steelhead fall through spring (Ohio DNR: Oct–May). Fish from the Metropark marina up to the Lagoon Dam.", [10, 11, 12, 1, 2, 3, 4], [OHRUN],
  None, "Ohio DNR stocking: 80,045 steelhead smolts in 2025 (100,532 in 2021, 94,530 in 2022, 93,801 in 2023, 81,051 in 2024); not in Michigan's database.",
  [("04201500", "Rocky R near Berea, OH", False)], "04201500 Rocky River near Berea OH (live, flow only)", "Medium-High (Ohio DNR sources)",
  ["Ohio, not Michigan: separate license and rules. Marker is Rocky River city, approximate."], OHSRC,
  "Cleveland Metroparks Rocky River Reservation / Metropark marina up to the Lagoon Dam (Ohio DNR). Access points not individually researched."))
