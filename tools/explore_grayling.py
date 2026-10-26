"""Grayling trip focus (Apr 30 – May 2, 2027): new Grayling-area waters + trip tags on existing Au Sable / Manistee entries.
Regs: DNR Trout & Salmon Regulations ArcGIS layer (queried Oct 2026), FO-200.25, FO-254.26 (inland trout lakes, eff. Sep 10, 2026),
2026 Michigan Fishing Regulations digest. Drive times: OSRM (home → pin in research/drive_times_new.json; trip house → pin below).
The trip house is deliberately stored without its street number."""
from explore_common import *
from explore_new import mk, DT, NEW, GENDEF

REGL = "https://services3.arcgis.com/Jdnp1TjADvSDxMAX/arcgis/rest/services/DNRFisheriesTroutRegsOPENDATA/FeatureServer/0 (DNR Trout & Salmon Regulations layer — StreamType / GearRestriction, queried Oct 2026)"
FO254 = FO + "FO_254.pdf (FO-254.26, inland lakes trout & salmon regulations, effective Sep 10, 2026)"
DIG = "https://www.michigan.gov/dnr/-/media/Project/Websites/dnr/Documents/LED/digests/2026-Michigan-Fishing-Regulations_web_accessible.pdf (2026 Michigan Fishing Regulations: definitions p.8, licences)"
BFW = "https://www.michigan.gov/dnr/things-to-do/fishing/where/better-fishing-waters (DNR Better Fishing Waters)"
HPSP = "https://www.michigan.gov/recsearch/parks/hartwick (Hartwick Pines State Park: fishing piers on Bright & Glory Lakes)"
HPMAP = "https://michigandnr.com/Publications/PDFS/RecreationCamping/hartwick_pines_map.pdf (Hartwick Pines map: Au Sable River Trail)"
KNEFFCG = "https://www.fs.usda.gov/r09/huron-manistee/recreation/kneff-lake-campground (USFS Kneff Lake Campground)"
PADUS = "https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Manager_Name_PADUS/FeatureServer/0 (USGS PAD-US land ownership)"
USGS_STAT = "https://waterservices.usgs.gov/nwis/stat/ (USGS daily statistics, Apr 30 – May 2)"
KW = "https://www.fws.gov/refuge/kirtlands-warbler-wildlife-management-area/visit-us/activities (occupied Kirtland's warbler nesting areas closed to entry May 1 – Aug 15, posted)"
TT71 = "https://www.michigandnr.com/publications/PDFS/ArcGISOnline/StoryMaps/fish_troutTrails/PDFs/TT2017071.pdf (DNR Trout Trails: Au Sable at Burton's Landing)"
HATCH = "https://michiganflyfishinghub.com/hatch-calendar/ (Hub hatch calendar: Hendrickson mid Apr – late May, best early–mid afternoon, ideal water 55°F)"
ACCESS103 = "https://ausableaccess.com/ (Au Sable River Public Access, 103 S James St, Grayling — canoe/kayak put-in)"
HATCHERY = "https://www.graylingfishhatchery.org/hours-and-information/ (Grayling Fish Hatchery: open Memorial Day – Labor Day, so CLOSED on the trip dates)"

TRIP_ID = "grayling-2027"
# house→pin OSRM minutes / miles (computed Oct 26, 2026)
HOUSE = {"au-sable-grayling": (3, 1.2), "au-sable-holy-water": (9, 4.9), "manistee-upper": (11, 7.1), "howes-lake": (12, 5.9), "bright-lake": (12, 6.7),
         "au-sable-east-branch": (19, 9.4), "kneff-lake": (20, 10.0), "manistee-headwaters": (26, 13.2), "au-sable-south-branch": (28, 19.6),
         "grayling-creeks": (28, 12.1), "au-sable-north-branch": (36, 20.5)}
OPEN27 = "Last Saturday in April 2027 is Apr 24, so the trip (Fri Apr 30 – Sun May 2) is the second weekend of the season."

AS_TOWN_LINES = ["Kolke/Bradford Creek confluence → Business Loop 75 (James St) bridge in Grayling: Type 1 — season last Sat Apr – Sep 30; artificial lures and all natural bait allowed; 5 trout (max 3 ≥15 in); brook 7 in, brown 8 in, rainbow 10 in. (DNR regs layer)",
                 "James St bridge → Burton's Landing: Type 2 — season last Sat Apr – Sep 30; bait and lures allowed; brook 10 in, brown 12 in (FO-200.25 p.3).",
                 "Burton's Landing → Wakeley Bridge (Holy Water): artificial flies only — a separate Explore entry."]
NEW_G = []
NEW_G.append(mk("au-sable-grayling", "Au Sable River at Grayling — trip-house & town water (Type 1 / Type 2)", "Crawford", "au-sable-grayling",
  ["brown trout", "brook trout", "rainbow trout"], "wild", "Wild brown and brook trout (DNR Trout Trails, Burton's Landing: wild brook to 12 in, brown 20 in+). Not stocked on this reach per the DNR database.",
  state(["1", "2"], True, "Type 1 (house water) → Type 2 (James St → Burton's Landing)", AS_TOWN_LINES, "DNR Trout & Salmon Regulations layer · FO-200.25 p.3 (Type 2) · FO-210.26 (designated)", True, "regs layer queried Oct 2026"),
  dict(rule="last_sat_apr_sep30", label="Type 1 above James St and Type 2 James St → Burton's Landing: last Saturday in April – Sep 30 (opens Apr 24, 2027). Bait and lures legal on both.", src="DNR Trout & Salmon Regulations layer · FO-200.25"),
  "Type 1 at the house (bait + lures; brook 7 in, brown 8 in) and Type 2 through town to Burton's Landing (bait + lures; brook 10 in, brown 12 in). Flies-only starts at Burton's Landing. No chumming.",
  "Designated trout stream (FO-210.26: Au Sable mainstream and tributaries). Type 1 / Type 2 per the DNR regs layer and FO-200.25.",
  "Early season: nymphs, small spinners and worms drifted through bends; Hendricksons in the afternoon when water nears 50–55°F.", [5, 6, 7, 9], [], None,
  "DNR stocking DB: none on the mainstream at Grayling (Oct 2021–now).",
  [("04135800", "North Branch Au Sable at Kelloggs Bridge (nearest live gage with temp; different branch)", True), ("04136500", "Au Sable R at Mio (far downstream)", True)],
  "No live gage on this reach: USGS 04135500 Au Sable at Grayling was discontinued in 1993 (records 1942–1993; median flow about 90–97 cfs for Apr 30 – May 2, USGS daily stats). The North Branch and Mio gages are shown for context only.",
  "High (regs from DNR layer + FO-200; house pin approximate)",
  ["The house pin is approximate and the street number is hidden on purpose. River access at the house = the rental's own frontage; elsewhere use public sites.",
   "Canoe and kayak traffic launches in Grayling — expect boats on weekends; fish edges and let them pass.",
   "Water is cold in early May (nearby gages median ~48–52°F on Apr 30 – May 2): kids need waders or should fish from the bank."],
  [REGL, FO200, FO210, TT71, ACCESS103, USGS_STAT, DIG],
  "Trip house frontage (river right there, inside a meander bend). Public: Au Sable River Public Access at 103 S James St (canoe put-in, parking/restrooms per ausableaccess.com — third-party site); Burton's Landing (DNR, end of Burton's Landing Rd ~0.5 mi north of M-72, ~3 mi east of Bus. I-75). Marker = James St bridge, the Type 1 / Type 2 boundary.",
  tr_note="TroutRoutes class not checked (app-gated)."))

NEW_G.append(mk("au-sable-east-branch", "East Branch Au Sable — Hartwick Pines (Type 1 small stream)", "Crawford", "au-sable-east-branch",
  ["brook trout", "brown trout"], "both", "Small spring creek; DNR Better Fishing Waters lists the East Branch for brook and brown trout. DNR planted 200 small brown trout (1.5 cm, likely fry) on 2024-05-17.",
  state(["1"], True, "Type 1 (state-designated, per DNR regs layer)", ["East Branch Au Sable from Hartwick Pines down to the mainstream in Grayling: Type 1 — last Sat Apr – Sep 30; bait and lures allowed; brook 7 in, brown 8 in."], "DNR Trout & Salmon Regulations layer (StreamType = Type 1)", False, "regs layer queried Oct 2026", "BirdTrout lists the East Branch as Type 2/3 — conflicts with the DNR layer; trust the DNR layer and the posted signs."),
  dict(rule="last_sat_apr_sep30", label="Type 1: last Saturday in April – Sep 30 (opens Apr 24, 2027). Bait and lures legal.", src="DNR Trout & Salmon Regulations layer"),
  "Type 1: bait and lures allowed; brook 7 in, brown 8 in. Small, brushy water — short rods.",
  "Designated trout stream (FO-210.26: Au Sable tributaries). Type 1 per the DNR regs layer.",
  "Short-line drift a worm or small nymph under cut banks; a #0 spinner where there is room.", [5, 6], [], dict(waters=["East Branch Au Sable River"], counties=["Crawford"]), "",
  [], "No USGS gage on the East Branch.", "Medium (Type 1 from DNR layer; BirdTrout disagrees)",
  ["Type conflict: DNR layer says Type 1, BirdTrout says Type 2/3. Both allow bait and lures in season; read the signs.",
   "Hartwick Pines needs a Michigan Recreation Passport on the vehicle (state park).",
   "Part of the East Branch corridor touches Camp Grayling land (PAD-US) — stay on the state-park side."],
  [REGL, FO210, BFW, HPSP, HPMAP, PADUS, DBURL],
  "Hartwick Pines State Park: the Au Sable River Trail (about 3 mi, west of M-93) has a footbridge over the East Branch; fishing allowed along it (park map). Marker = trail/river point in the park.",
  tr_note="TroutRoutes class not checked (app-gated)."))

NEW_G.append(mk("manistee-headwaters", "Upper Manistee headwaters — lures-only CR 612 → M-72 & Type 2 above", "Crawford / Kalkaska", "manistee-headwaters",
  ["brook trout", "brown trout", "rainbow trout"], "wild", "Wild brook and brown trout headwaters (Michigan Fly Fishing Hub; DNR SFR 2020-283 Upper Manistee).",
  state(["2", "GR"], True, "Type 2 above CR 612 · GR lures-only CR 612 → M-72", ["Above CR 612: Type 2 — last Sat Apr – Sep 30; bait and lures allowed; brook 10 in, brown 12 in.", "CR 612 → M-72 (9.2 mi): artificial lures only (spinners, spoons, plugs, flies — no live/natural bait); fishing open all year; 2 trout (max 1 ≥18 in), brown 18 in; brook/brown kept last Sat Apr – Sep 30.", "M-72 → CCC Bridge: artificial flies only (see the Upper Manistee entry)."], "DNR Trout & Salmon Regulations layer (GR14) · FO-200.25 p.3, p.17", True, "regs layer queried Oct 2026"),
  dict(rule="gr", gr=dict(tackle="lures", cr=False), label="CR 612 → M-72: artificial lures only, open all year. Type 2 above CR 612: last Sat Apr – Sep 30 (open Apr 24, 2027), bait allowed.", also="Type 2 water above CR 612 is closed Oct 1 – last Sat in April", src="DNR regs layer (GR14) · FO-200.25"),
  "Lures-only CR 612 → M-72: kids can throw spinners, no worms. Type 2 above CR 612: worms OK in season.",
  "Designated trout stream (FO-210.26). FO-200.25: Type 2 above CR 612, lures-only CR 612 – M-72.",
  "Small spinners (#0–#1) and small nymph/streamer swings in the lures-only reach; afternoon Hendricksons.", [5, 6, 7, 9], [], None, "No DNR stocking records for the headwaters reach.",
  [("04123500", "Manistee R near Grayling (at M-72, bottom of the lures-only reach)", False)], "04123500 Manistee River near Grayling at M-72 (live flow + temp). Median about 200 cfs and ~48–50°F for Apr 29 – May 2 (USGS daily stats).", "High (regs from DNR layer + FO-200)",
  ["CR 612 bridge sits in state land (DNR Kirtland's Warbler Unit Manistee, open access per PAD-US). Occupied Kirtland's warbler nesting areas are posted closed to entry May 1 – Aug 15 — obey any signs (May 1–2 falls in the closure window)."],
  [REGL, FO200, FO210, HUB("upper-manistee-river"), PADUS, KW, "https://waterdata.usgs.gov/monitoring-location/04123500/ (USGS gage at M-72)"],
  "CR 612 bridge (state land, marker) and M-72 bridge / Manistee River Bridge State Forest Campground (bottom of the lures-only reach, top of flies-only). Banks between are mostly state forest; check signs.",
  tr_note="TroutRoutes class not checked (app-gated)."))

NEW_G.append(mk("howes-lake", "Howes Lake (Camp Grayling) — tip from the Old AuSable Fly Shop", "Crawford", "howes-lake",
  ["rainbow trout", "brown trout", "brook trout", "largemouth bass"], "stocked", "About 14 acres, ~24 ft deep (third-party lake sites). DNR Better Fishing Waters lists Howes Lake for rainbow trout. Trout are stocked, not wild.",
  state([], False, "Inland lake — not a classified trout lake (FO-254.26)", ["Howes Lake is not listed in FO-254.26 (Types A–E), so the default inland-lake trout rule applies: trout season open all year, all natural bait and artificial lures allowed, 8 in minimum, 5 trout (max 3 ≥15 in)."], "FO-254.26 (searched; not listed) · 2026 Michigan Fishing Regulations", False, "FO-254 text read"),
  dict(rule="year_round", label="Unclassified inland lake: trout season open all year; all bait and lures legal (FO-254.26 default).", src="FO-254.26 · 2026 Michigan Fishing Regulations"),
  "Open all year; bait and lures legal (kids can use worms, spinners, bobbers). Catch and release by choice.",
  "Not a designated trout lake. Listed on DNR Better Fishing Waters for rainbow trout.",
  "Shore-cast a worm or PowerBait-style dough under a bobber, or a small spinner; trout cruise near drop-offs in cool spring water.", [4, 5, 6, 9, 10], [],
  dict(waters=["Howes Lake"], counties=["Crawford"]),
  "Full DNR history: rainbows 1980–84 (≈600/yr); 2019-11-06: 701 rainbow (~15 in), 203 brown (~8.5 in), 205 brook (~9 in); 2021-10-27: 935 Eagle Lake rainbow (~12 in). Nothing recorded 2022 – Oct 2026, so 'stocked at times' is right but recent plants are not on record — the shop may know more.",
  [], "No gage (lake).", "Medium (regs/stocking verified; access needs confirming)",
  ["Access unverified: PAD-US maps the lake inside Camp Grayling (National Guard maneuver training area). The Grayling visitors bureau says much of Camp Grayling is open to public hunting and fishing when training is not happening; roads can be gated during exercises. Call ahead or check Camp Grayling's public notices.",
   "No DNR boat launch is listed — plan on shore fishing or a carry-in.",
   "Last DNR stocking on record is Oct 2021; trout may be sparse by 2027 unless it is stocked again."],
  [FO254, BFW, DBURL, PADUS, "https://www.fishroulette.com/lakes/e041891a4b66c6b68c9d-howes-lake (third-party: 14 acres, species list)", "https://www.oldausable.com/ (Old AuSable Fly Shop, 200 Ingham St, Grayling — recommended Howes Lake)"],
  "West of Grayling off M-72 via N Howes Lake Rd / Arrowhead Rd (matches Mark's screenshot, ~1,144 ft). Inside Camp Grayling per PAD-US — public fishing allowed when not closed for training (confirm). Shore / carry-in only.",
  tr_note="Lake — not on TroutRoutes streams."))

KNEFF_EXTRA = "Stocked every April with yearling rainbows (≈1,000/yr, ~7–8 in) — the 2026 plant was 994 on Apr 21, a week before the opener."
NEW_G.append(mk("kneff-lake", "Kneff Lake — Type A trout lake (Huron NF, stocked every April)", "Crawford", "kneff-lake",
  ["rainbow trout"], "stocked", "Put-and-take rainbow trout lake (DNR Type A).",
  state(["A"], True, "Type A designated trout lake (FO-254.26)", ["Type A lake: fishing season last Sat Apr – Oct 31 (opens Apr 24, 2027); natural bait except minnows (dead or alive) and artificial lures may be used; 5 trout (max 3 ≥15 in); rainbow 12 in, brook 10 in, brown 12 in."], "FO-254.26 (Type A list: Crawford — Kneff Lake)", False, "FO-254 text read"),
  dict(rule="last_sat_apr_oct31", label="Type A lake: last Saturday in April – Oct 31 (opens Apr 24, 2027). Worms and lures legal; no minnows.", src="FO-254.26"),
  "Type A: worms/dough/lures legal, no minnows. Stocked rainbows are mostly under the 12 in keep size — catch and release anyway.",
  "Designated trout lake (all Type A lakes are designated, 2026 Fishing Regulations definitions).",
  "Bobber + worm or small spinner from shore; stocked rainbows school up and bite well in spring.", [4, 5, 6, 9, 10], [], dict(waters=["Kneff Lake"], counties=["Crawford"]), KNEFF_EXTRA,
  [], "No gage (lake).", "High (regs + stocking from DNR)",
  ["USFS lists the Kneff Lake Campground season as May 1 – Sep 30 — whether the day-use area/launch is open on Fri Apr 30 is unverified.",
   "Shupac Lake (also Type A, stocked ~5,500 rainbows every April; 43 min from the house near Lovells) is the bigger backup, but it is 244 min from home so it sits outside the 4-hour Explore cap."],
  [FO254, DBURL, KNEFFCG, PADUS],
  "Kneff Lake Campground, Huron National Forest (public land, open access per PAD-US), east of Grayling off M-72.",
  tr_note="Lake — not on TroutRoutes streams."))

NEW_G.append(mk("bright-lake", "Bright Lake — Hartwick Pines SP (Type B, fishing pier, stocked)", "Crawford", "bright-lake",
  ["rainbow trout"], "stocked", "Small state-park lake (Alexander Lakes) stocked with rainbow trout every April.",
  state(["B"], False, "Type B trout lake (FO-254.26)", ["Type B lake: fishing open all year; all natural bait and artificial lures allowed; 5 trout (max 3 ≥15 in); rainbow 12 in, brook 10 in, brown 12 in."], "FO-254.26 (Type B list: Crawford — Bright Lake)", False, "FO-254 text read"),
  dict(rule="year_round", label="Type B lake: open all year; bait and lures legal.", src="FO-254.26"),
  "Type B: open all year, bait and lures legal — easy kid spot.",
  "Type B trout lake (not a designated trout lake — only Types A and D are).",
  "Bobber + worm from the accessible fishing pier; small spinners along the edges.", [4, 5, 6, 9, 10], [], dict(waters=["Bright Lake (Alexander Lakes)"], counties=["Crawford"]),
  "Stocked ≈700–770 rainbows each April (720 on 2026-04-16).",
  [], "No gage (lake).", "High (regs + stocking from DNR)",
  ["Recreation Passport required to enter Hartwick Pines State Park."],
  [FO254, DBURL, HPSP, PADUS],
  "Hartwick Pines State Park — accessible fishing piers on Bright and Glory Lakes, 0.25-mi Bright & Glory Lakes Trail from the modern campground.",
  tr_note="Lake — not on TroutRoutes streams."))

NEW_G.append(mk("grayling-creeks", "Small blue lines near Grayling — Kolke, Bradford, Simpson, Goose & Portage Creeks (Type 1)", "Crawford / Kalkaska", "grayling-creeks",
  ["brook trout", "brown trout"], "wild", "Small Type 1 brook-trout feeders of the upper Au Sable and Manistee (DNR regs layer). Not stocked per the DNR database. Fish populations not surveyed here — unverified.",
  state(["1"], True, "Type 1 small streams (DNR regs layer)", ["Kolke Creek and Bradford Creek (Au Sable headwaters, meet at ~44.806 N, -84.758 W): Type 1.", "Simpson Creek (enters the Au Sable right by the trip house): Type 1.", "Goose Creek (Manistee tributary, joins ~44.716 N, -84.824 W): Type 1.", "Portage Creek (Manistee tributary): Type 1 below ~44.662 N; the stretch just below Portage Lake is unclassified.", "Type 1 = last Sat Apr – Sep 30, bait and lures allowed, brook 7 in, brown 8 in."], "DNR Trout & Salmon Regulations layer (queried Oct 2026)", False, "regs layer"),
  dict(rule="last_sat_apr_sep30", label="Type 1: last Saturday in April – Sep 30 (opens Apr 24, 2027). Bait and lures legal.", src="DNR Trout & Salmon Regulations layer"),
  "Type 1: worms and spinners legal; brook 7 in.",
  "Designated trout streams (Au Sable / Manistee tributaries, FO-210.26). Type 1 per the DNR regs layer.",
  "Dap a worm or a small dry along undercut banks; quiet approach. Good 'adventure' outing for the 13-year-old.", [5, 6, 7], [], None, "No DNR stocking records.",
  [], "No USGS gages on these creeks.", "Low–Medium (regs verified; access and fish numbers not verified)",
  ["Access not verified for any of these creeks. " + NAVCAUTION,
   "Marker is the Kolke/Bradford confluence (approximate). Use the DNR regs map or onX/TroutRoutes to find public crossings."],
  [REGL, FO210, NAVSRC[0]],
  "Not verified. Road crossings only unless the land is posted public (state forest). Simpson Creek near the house: fish only where you have permission.",
  tr_note="TroutRoutes class not checked (app-gated)."))

# ---- trip info ----
KIDS = {"bait": "🧒 Kids: worms & spinners OK", "lures": "🧒 Kids: spinners OK, no bait", "flies": "🪰 Flies only (no spinners/bait)", "mixed": "🧒 Mixed — check reach"}
TRIP_INFO = {
 "au-sable-grayling": ("bait", 3, "Open on the trip: YES (Type 1/Type 2 season opens Apr 24, 2027). The water behind the house is Type 1 — the boys can fish worms and spinners right out the back door, and on through town to Burton's Landing (Type 2).",
     "Best kids' water of the trip. Mornings: worm under a small split shot dead-drifted into the bend pools; #0–#1 inline spinner across and down. Afternoons: watch for Hendricksons (#14) when water warms."),
 "au-sable-holy-water": ("flies", 9, "Open on the trip: YES (open all year), but artificial flies only and no-kill from Burton's Landing to Wakeley Bridge. No spinners, no bait, no beads.",
     "Adults' water. Hendricksons are the first big hatch (Hub: mid Apr – late May, early–mid afternoon, best near 55°F water). Nymph (#14–16 Pheasant Tail / Hare's Ear) in the morning, Hendrickson dun/emerger 1–4 pm, spinner fall toward evening if warm. Access: Burton's Landing, Louie's, Keystone, Whirlpool, Thendara, Stephan Bridge, Wakeley."),
 "manistee-upper": ("flies", 11, "Open on the trip: YES (open all year), artificial flies only from M-72 down to the CCC Bridge.",
     "Adults' water near the house: M-72 State Forest Campground access at the USGS gage. Same Hendrickson playbook; swing a small streamer if nothing is rising."),
 "howes-lake": ("bait", 12, "Open on the trip: YES (unclassified lake, trout open all year). Bait and lures legal.",
     "Plan B from the fly shop — but access (Camp Grayling) must be confirmed and the last DNR trout plant on record is Oct 2021. Mark's note: “They stock this with Trout at times so if the river is slow we can try this spot.”"),
 "bright-lake": ("bait", 12, "Open on the trip: YES (Type B, open all year). Bait and lures legal.",
     "Easiest sure-thing for the 8- and 9-year-olds: fishing pier, rainbows stocked every April. Pair with the East Branch trail walk."),
 "au-sable-east-branch": ("bait", 19, "Open on the trip: YES (Type 1 season opens Apr 24, 2027). Bait and lures legal.",
     "Small, brushy water — better for the 13-year-old with a short rod than for the younger boys."),
 "kneff-lake": ("bait", 20, "Open on the trip: YES (Type A season opens Apr 24, 2027). Worms and lures legal; no minnows.",
     "Reliable Plan B for the kids: ~1,000 rainbows stocked every April. Campground opens May 1 (USFS)."),
 "manistee-headwaters": ("lures", 26, "Open on the trip: YES. CR 612 → M-72 is lures only (spinners OK, no worms); above CR 612 is Type 2 (bait OK).",
     "Good water for the 13-year-old with a spinning rod: small spinners through the lures-only reach on state land."),
 "au-sable-south-branch": ("flies", 28, "Open on the trip: YES (open all year), flies only; no-kill through the Mason Tract.",
     "Adults' walk-and-wade (Mason Tract) — longer hike, not ideal for the younger boys."),
 "grayling-creeks": ("bait", 28, "Open on the trip: YES (Type 1 season opens Apr 24, 2027). Bait and lures legal.",
     "Exploration only — public access not verified."),
 "au-sable-north-branch": ("flies", 36, "Open on the trip: YES (open all year). Flies only from Sheep Ranch down; the Type 1 water above Sheep Ranch allows bait (not independently verified).",
     "Farthest; Lovells water. Adults' water, wild brookies on small dries if the hatch is on."),
}
def trip_for(i):
    k, hm, opn, tac = TRIP_INFO[i]
    return {"id": TRIP_ID, "house_min": hm, "house_mi": HOUSE[i][1], "kids": k, "kids_txt": KIDS[k], "open": opn, "tactics": tac}

TRIP = {"id": TRIP_ID, "name": "Grayling trip", "dates": "Fri Apr 30 – Sun May 2, 2027",
  "house": {"lat": 44.659, "lng": -84.7266, "label": "Trip house (Circle Ct, Au Sable)",
            "note": "Rental on the Au Sable just off M-72 on the west side of Grayling (pin approximate). The river behind the house is Type 1 trout water: open from Apr 24, 2027, worms and spinners legal for the boys. Flies-only water starts ~5 mi downstream at Burton's Landing."},
  "bounds": [[44.50, -84.95], [44.84, -84.44]],
  "summary": [OPEN27,
     "Kids' water (bait + spinners legal): the house stretch and town water (Type 1/2), East Branch, Bright Lake, Kneff Lake, Howes Lake. Lures-only (spinners, no worms): Manistee CR 612 → M-72.",
     "Adults' fly water: Holy Water (Burton's Landing → Wakeley), Manistee M-72 → CCC, North & South Branch GR reaches — flies only, no beads.",
     "Hendricksons usually come off in the early–mid afternoon in late April/May; median water temps on these dates are ~48–52°F at nearby gages, so afternoons fish best.",
     "Licences: Mark, his brother and brother-in-law each need a 2027 Michigan fishing licence (2026 licences expire Mar 31, 2027). The boys (under 17) need none but must follow the rules. An adult actively helping a child fish should be licensed."],
  "plan": [["Fri Apr 30", "Arrive · settle in · kids fish the house water with worms/spinners until dark; adults scout Burton's Landing (9 min)."],
           ["Sat May 1", "AM: Bright Lake pier (stocked rainbows) + East Branch trail walk at Hartwick Pines. Afternoon: dads take turns on the Holy Water for the Hendrickson hatch (1–4 pm) while kids fish the house. Evening: house water."],
           ["Sun May 2", "AM: Manistee — 13-yr-old spins the lures-only reach (CR 612 → M-72); fly guys fish M-72 flies-only. Late AM: Kneff Lake or Howes Lake for the younger boys if the river is slow. Head home after lunch (~3.5 h)."]],
  "plan_note": "Full game plan with sources: research/grayling-trip-2027.md (not published)."}

def apply(streams):
    ids = {s["id"] for s in streams}
    for s in streams:
        if s["id"] in TRIP_INFO: s["trip"] = trip_for(s["id"])
    missing = set(TRIP_INFO) - ids
    assert not missing, missing
