#!/usr/bin/env python3
"""Adds the 'brookie-creek' gear profile (tiny SE Michigan brook trout headwaters: upper North Branch Clinton, Kidder Creek) to gear-guide.json.
Rig table and fly sizes are read live from the Michigan Fly Fishing Hub Fox River (UP wild brook trout) page; rod length is shortened
for brushy SE Michigan headwaters (marked general). Run after build_gear.py / build_gear_hub.py:  python3 tools/build_gear_brookie.py"""
import json, os, re, urllib.request
from bs4 import BeautifulSoup
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GJ = os.path.join(ROOT, "gear-guide.json")
URL = "https://michiganflyfishinghub.com/rivers/fox-river/"
g = json.load(open(GJ))
s = BeautifulSoup(urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=40).read(), "lxml")
for t in s(["script", "style", "nav", "footer", "svg"]): t.decompose()
L = [x.strip() for x in s.get_text("\n").split("\n") if x.strip()]
i = L.index("Gear Recommendations"); k = L.index("Rod", i); rows = {}
for key in ("Rod", "Line", "Leader", "Tippet", "Waders", "Boots"):
    assert L[k] == key, (L[k], key); rows[key.lower()] = L[k + 1:k + 5]; k += 5
print("hub Fox River rods:", rows["rod"])
SHORT = "6-7.5 ft 3- or 4-weight"
rigs = {}
for ci, ck in enumerate(("dry", "nymph", "euro", "streamer")):
    r = {kk: rows[kk][ci] for kk in ("rod", "line", "leader", "tippet")}
    r.update(waders="Hip waders or wet wading (tiny creek)", boots="Light rubber-soled boots", general=False)
    if ck in ("dry", "nymph"): r["rod"] = SHORT + f" (hub lists {rows['rod'][ci]})"; r["general"] = True
    if ck == "dry": r["leader"] = "6-7.5 ft to 5X (shortened for brush)"; r["general"] = True
    rigs[ck] = r
g["sources"]["hub_fox"] = dict(label="Michigan Fly Fishing Hub - Fox River (UP wild brook trout: gear recommendations)", url=URL)
g["profiles"]["brookie-creek"] = dict(
    title="Tiny brook trout headwater (SE Michigan)",
    confidence="Rigs and fly sizes from the Michigan Fly Fishing Hub's wild brook trout page (Fox River, UP); rod/leader lengths shortened for brushy headwaters (* = adapted)",
    summary="Tiny, brushy, spring-fed creeks with small wild brook trout. Short rod, short leader, roll casts and dapping; stay low and fish upstream. Type 1 season (last Sat in April - Sep 30) on the designated reach; nearly all banks are private - stay in the road right-of-way unless you have permission.",
    rigs=rigs,
    flies=[["Dry flies", [["Elk Hair Caddis", [14, 16]], ["Adams / Parachute Adams", [14, 16]], ["Royal Wulff", [14, 16]]], "hub_fox"],
           ["Terrestrials (summer; general guidance)", [["Foam ant / beetle", [14, 16, 18]], ["Small hopper", [14]]], None],
           ["Nymphs / wets", [["Small bead-head nymphs (Hare's Ear, Pheasant Tail)", [14, 16, 18]], ["Soft hackles", [14, 16]]], "hub_fox"],
           ["Streamers", [["Small Muddler Minnow / sculpin", [8, 10]], ["Small black Woolly Bugger", [10, 12]]], "hub_fox"]],
    lures=None, steelhead=None,
    tips=["Hub (Fox River brook trout): wild brookies are aggressive on any visible adult dry - focus on pool tail-outs morning and evening; small bead-heads #14-16 and soft hackles below.",
          "Roll-cast or dap from the bank; one good first cast per pocket, then move on (general guidance).",
          "Terrestrials (ants, beetles) #14-18 under overhanging grass in July-September (general guidance).",
          "Brook trout spawn in fall - the Type 1 season closes Sep 30; avoid wading over gravel redds Oct-Nov (general guidance)."],
    safety=g["profiles"]["small-stream"]["safety"] + ["Private land: on non-navigable streams the riparian owner owns the bed and the public may not wade without permission (MSU/DNR 'Public Rights on Michigan Waters')."],
    shops=["Motor City Anglers (Rochester Hills) - fly shop and guide service (the hub lists them for Paint Creek)."],
    sources=["hub_fox", "hub_paint"], hatch_water="small")
for sid in ("north-branch-headwaters", "kidder-creek"): g["explore_profile"][sid] = "brookie-creek"
json.dump(g, open(GJ, "w"), indent=1)
print("brookie-creek profile written")
