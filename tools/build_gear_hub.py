#!/usr/bin/env python3
"""Adds sourced gear profiles for Explore streams that have a Michigan Fly Fishing Hub river page
(Au Sable Holy Water / North / South Branch, Pere Marquette, Upper Manistee, Muskegon, Rifle) to gear-guide.json.
Fetches the live hub pages (rod/line/leader/tippet/waders/boots tables + tips) - nothing is invented.
Other new Explore streams are mapped to existing profiles and flagged 'general guidance' by the UI.
Run after tools/build_gear.py:  python3 tools/build_gear_hub.py   (needs beautifulsoup4, lxml)"""
import json, os, re, urllib.request
from bs4 import BeautifulSoup
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GJ = os.path.join(ROOT, "gear-guide.json")
g = json.load(open(GJ))
BASE = "https://michiganflyfishinghub.com/rivers/"
PAGES = {  # profile id: (slug, title, summary extras, hatch_water, steelhead text or None)
 "au-sable-holy-water": ("au-sable-river-holy-water", "Au Sable - Holy Water (Grayling)", "Burton's Landing to Wakeley Bridge is flies-only, no-kill (FO-200); Wakeley to McMasters is artificial lures only; James St to Burton's Landing is Type 2.", None),
 "au-sable-north-branch": ("au-sable-river-north-branch", "Au Sable - North Branch (Lovells)", "North Branch from Sheep Ranch to the confluence is flies-only (FO-200): 2 trout, browns 18-in minimum.", None),
 "au-sable-south-branch": ("au-sable-river-south-branch", "Au Sable - South Branch / Mason Tract", "Chase Bridge to Lower High Banks (4.3 mi) is flies-only, no-kill; below that to the confluence is artificial lures only (FO-200).", None),
 "pere-marquette": ("pere-marquette-river", "Pere Marquette River (Baldwin)", "M-37 to Gleason's Landing is flies-only with zero trout/salmon kept all year; rules change by reach and date (FO-200).", "Steelhead/egg-run notes: swing articulated streamers on a sink tip, nymph stoneflies, eggs and Copper Johns size 8-14 (hub)."),
 "manistee-upper": ("upper-manistee-river", "Upper Manistee River", "CR 612 to M-72 is artificial lures only; M-72 to the CCC Bridge is flies-only (FO-200). Wild browns/brookies, lightly pressured.", None),
 "muskegon-croton": ("muskegon-river", "Muskegon River below Croton Dam", "Tailwater steelhead/brown river, Type 3 from Croton Dam to M-120 (15-in brook/brown minimum; up to 5 rainbows, 1 over 20 in).", "Steelhead tailwater - see hub Muskegon page for eggs/streamer/nymph approaches; Aug 1-Nov 15 terminal tackle is restricted (single-point hooks / small trebles on body baits)."),
 "rifle-river": ("rifle-river", "Rifle River (Ogemaw Co.)", "Wild brown trout water in the Rifle River Recreation Area; check FO-200 for the Type that applies at your reach (Type 3 listed from Sage Lake Rd to Saginaw Bay).", None),
}
def rng(m):
    lo, hi = int(m.group(1)), int(m.group(2) or m.group(1))
    lo, hi = min(lo, hi), max(lo, hi)
    return list(range(lo, hi + 1, 2)) if (hi - lo) % 2 == 0 and hi > lo else sorted({lo, hi})
def sizes(t):
    m = re.search(r"sizes?\s*(\d+)(?:\s*[–-]\s*(\d+))?(?!/)", t)
    return rng(m) if m else []
def parse(slug):
    html = urllib.request.urlopen(urllib.request.Request(BASE + slug + "/", headers={"User-Agent": "Mozilla/5.0"}), timeout=40).read()
    s = BeautifulSoup(html, "lxml")
    for t in s(["script", "style", "nav", "footer", "svg"]): t.decompose()
    L = [x.strip() for x in re.sub(r"\n\s*\n+", "\n", s.get_text("\n")).split("\n") if x.strip()]
    i = L.index("Gear Recommendations")
    intro = L[i + 1]
    j = L.index("Rod", i)
    rows = {}
    k = j
    for key in ("Rod", "Line", "Leader", "Tippet", "Waders", "Boots"):
        assert L[k] == key, (slug, L[k], key)
        rows[key.lower()] = L[k + 1:k + 5]; k += 5
    tips = {}
    names = ["Dry Fly Tips", "Nymphing Tips", "Euro Nymph Tips", "Streamer Tips"]
    end = L.index("Find Your Guide", k) if "Find Your Guide" in L[k:] else len(L)
    idx = [(n, L.index(n, k)) for n in names if n in L[k:end]]
    for n, p in idx:
        nxt = min([q for _, q in idx if q > p] + [end])
        tips[n] = L[p + 1:nxt]
    haddr = []
    if "Hatch Calendar" in L:
        h0 = L.index("Hatch Calendar")
        seg = L[h0 + 1:i]
        seg = [x for x in seg if x not in ("Species", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")]
        for a in range(0, len(seg) - 1, 2): haddr.append((seg[a], seg[a + 1]))
    return intro, rows, tips, haddr
for pid, (slug, title, extra, steel) in PAGES.items():
    intro, rows, tips, hat = parse(slug)
    src = "hub_" + pid
    g["sources"][src] = dict(label=f"Michigan Fly Fishing Hub - {title} (gear recommendations)", url=BASE + slug + "/")
    rigs = {}
    for ci, ck in enumerate(("dry", "nymph", "euro", "streamer")):
        rigs[ck] = dict({k: rows[k][ci] for k in ("rod", "line", "leader", "tippet", "waders", "boots")}, general=False)
    flies = []
    for n, lab in zip(["Dry Fly Tips", "Nymphing Tips", "Euro Nymph Tips", "Streamer Tips"], ["Dry flies", "Nymphs / wets", "Euro nymphs", "Streamers"]):
        items = [x for x in tips.get(n, [])[1:] if re.search(r"size|Hendrickson|Sulphur|Hex|Caddis|PMD|Drake|streamer|mouse|Woolly|Wooly|nymph|egg", x, re.I)]
        items = [x for x in items if not re.search(r"floatant|amadou|polarized|net$|forceps|headlamp|waterproof|wading staff|indicators?$|split shot", x, re.I)]
        if items: flies.append([lab, [[x, sizes(x)] for x in items], src])
    if hat: flies.append(["Hatches the hub lists for this river", [[f"{a} ({b})", []] for a, b in hat], src])
    g["profiles"][pid] = dict(title=title, confidence="High for rigs/tips (Michigan Fly Fishing Hub river page); regs from FO-200.25 (Michigan DNR)",
        summary=intro + " " + extra, rigs=rigs, flies=flies, lures=None, steelhead=steel,
        tips=[tips[n][0] + " (hub)" for n in tips if tips[n]] + ["Regulations change by reach - check FO-200 / the current Michigan Fishing Guide before you rig up (flies-only reaches ban bait, scent and beads)."],
        safety=g["profiles"]["big-water"]["safety"], shops=[], sources=[src, "hub_best"], hatch_water="all")
    print(pid, "ok", len(flies), "fly groups")
M = g["explore_profile"]
for pid in PAGES: M[pid] = pid
for pid, prof in {"au-gres-east-branch": "big-water", "au-sable-foote-dam": "big-water", "kalamazoo-allegan": "big-water", "grand-river-gr": "big-water", "rogue-river": "big-water",
                  "coldwater-barry": "small-stream", "augusta-creek": "small-stream", "rice-nottawa": "small-stream", "st-joseph-maumee": "small-stream",
                  "vermilion-oh": "big-water", "rocky-river-oh": "big-water"}.items(): M[pid] = prof
g["generated"] = "2026-10-15"
json.dump(g, open(GJ, "w"), indent=1)
