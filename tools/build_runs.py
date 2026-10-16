#!/usr/bin/env python3
"""Build run-calendar.json (Run calendar / Run status data).

Sources
  * Michigan Fly Fishing Hub salmon-run tracker (25 rivers, per-species typical windows,
    live status snapshot, dam / weir / access notes):
      https://michiganflyfishinghub.com/michigan-salmon-run/
  * Hub steelhead page (barriers, wild vs stocked; says DNR publishes no per-river steelhead timing):
      https://michiganflyfishinghub.com/michigan-steelhead-run/
  * Hub Clinton River page (qualitative: spring steelhead run Mar-May).
  * Regional month-level run windows already in explore-streams.json (forum / agency based)
    for rivers that are NOT on the Hub tracker (Clinton fall, Belle, St. Clair, Huron, Mill Cr, Ohio).

Usage:  python3 tools/build_runs.py            # fetch live pages
        python3 tools/build_runs.py --html /tmp/salmon.html   # parse a saved copy of the tracker page
"""
import json, re, sys, html, urllib.request, datetime, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB = "https://michiganflyfishinghub.com"
TRACKER = HUB + "/michigan-salmon-run/"
STEEL = HUB + "/michigan-steelhead-run/"
UA = {"User-Agent": "Mozilla/5.0 (river-dashboard build script)"}

def fetch(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read().decode("utf8", "ignore")

def totext(s):
    s = re.sub(r'<script.*?</script>|<style.*?</style>', '', s, flags=re.S)
    t = re.sub(r'<(br|/p|/h\d|/li|/tr|/div|/section)[^>]*>', '\n', s)
    t = re.sub(r'</t[dh]>', ' | ', t)
    t = html.unescape(re.sub(r'<[^>]+>', '', t))
    return [l.strip() for l in t.split('\n') if l.strip()]

MON = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}
def md(s):  # "Aug 25" -> "08-25"
    m, d = s.split()
    return "%02d-%02d" % (MON[m[:3]], int(d))

SP = {"Kings": "chinook", "Coho": "coho", "Steelhead": "steelhead", "Browns": "brown", "Pinks": "pink", "Atlantics": "atlantic"}
SLUG = {"Big Manistee River": "lower-manistee-river", "Little Manistee River": "little-manistee-river", "Pere Marquette River": "pere-marquette-river",
        "Muskegon River": "muskegon-river", "Betsie River": "betsie-river", "Platte River": "platte-river", "White River": "white-river", "Grand River": "grand-river",
        "St. Joseph River": "st-joseph-river", "Kalamazoo River": "kalamazoo-river", "Boardman River": "boardman-river", "Bear Creek": "bear-creek",
        "Manistique River": "manistique-river", "Au Sable River (Foote Dam water)": "au-sable-river-foote-dam", "Rifle River": "rifle-river",
        "Two-Hearted River": "two-hearted-river", "Rogue River": "rogue-river", "Black River (South Haven)": "black-river-south-haven", "Bear River": "bear-river-petoskey",
        "Cheboygan River": "cheboygan-river", "Ocqueoc River": "ocqueoc-river", "Thunder Bay River": "thunder-bay-river", "Au Gres River": "au-gres-river",
        "Chocolay River": "chocolay-river", "Huron River (Big Huron)": "big-huron-river"}
IDS = {"Big Manistee River": "manistee-lower", "Little Manistee River": "little-manistee", "Pere Marquette River": "pere-marquette", "Muskegon River": "muskegon",
       "Betsie River": "betsie", "Platte River": "platte", "White River": "white", "Grand River": "grand", "St. Joseph River": "st-joseph-mi", "Kalamazoo River": "kalamazoo",
       "Boardman River": "boardman", "Bear Creek": "bear-creek", "Manistique River": "manistique", "Au Sable River (Foote Dam water)": "au-sable-foote",
       "Rifle River": "rifle", "Two-Hearted River": "two-hearted", "Rogue River": "rogue", "Black River (South Haven)": "black-sh", "Bear River": "bear-petoskey",
       "Cheboygan River": "cheboygan", "Ocqueoc River": "ocqueoc", "Thunder Bay River": "thunder-bay", "Au Gres River": "au-gres", "Chocolay River": "chocolay",
       "Huron River (Big Huron)": "big-huron-baraga"}
# Hub tracker river -> dashboard Explore stream ids (only where it is the same water)
MATCH = {"Pere Marquette River": ["pere-marquette"], "Muskegon River": ["muskegon-croton"], "Grand River": ["grand-river-gr"], "Kalamazoo River": ["kalamazoo-allegan"],
         "Au Sable River (Foote Dam water)": ["au-sable-foote-dam"], "Rifle River": ["rifle-river"], "Au Gres River": ["au-gres-east-branch"], "Rogue River": ["rogue-river"]}
MATCH_NOTE = {
    "Big Manistee River": "Hub's run water is the LOWER Manistee below Tippy Dam. Explore's 'Upper Manistee' (flies-only M-72 to CCC Bridge) is a different, inland reach above the run - not matched.",
    "St. Joseph River": "Hub's St. Joseph is the Berrien County river (Lake Michigan, Niles / Berrien Springs). Explore's 'St. Joseph River of the Maumee' at Pittsford is a different river - not matched.",
    "Huron River (Big Huron)": "Hub's 'Huron River (Big Huron)' is the Big Huron in Baraga County (Lake Superior), NOT the Huron River of SE Michigan - not matched.",
    "Rifle River": "Run windows apply to the river as a whole (undammed to Saginaw Bay); Explore's pin is the upper reach near the Rifle River Recreation Area.",
    "Au Gres River": "Hub's steelhead run window; DNR plants go mostly to the East Branch (Whitney Drain), which Explore tracks.",
}

def parse_tracker(lines):
    i = next(n for n, l in enumerate(lines) if l == "River by river")
    L = lines[i:]
    rivers, cur = [], None
    species_re = r'^(Kings|Coho|Steelhead|Browns|Pinks|Atlantics)\s+(.*)$'
    for n, l in enumerate(L):
        m = re.match(r'^(.*) · Lake (Michigan|Huron|Superior) tributary$', l)
        if m:
            cur = {"hub_name": L[n - 1], "counties": m.group(1), "lake": m.group(2), "runs": [], "snap": {}}
            rivers.append(cur); continue
        if cur is None: continue
        m = re.match(species_re, l)
        if m and n + 2 < len(L) and L[n + 2].startswith("Typical:"):
            mm = re.match(r'Typical: (.+?) – (.+?), peak (.+?) – (.+)$', L[n + 2])
            a, b, c, d = mm.groups()
            r = {"sp": SP[m.group(1)], "start": md(a), "end": md(b), "peak": [md(c), md(d)], "hub_status": L[n + 1], "src": "hub-tracker"}
            if n + 3 < len(L) and not re.match(species_re, L[n + 3]) and not L[n + 3].startswith("Upstream limit"):
                r["note"] = L[n + 3]
            cur["runs"].append(r); continue
        m = re.match(r'^(Upstream limit|Access|Crowding|Regulations|What to throw)(.*)$', l)
        if m: cur[m.group(1)] = m.group(2).strip(); continue
        m = re.match(r'^(Peak|Building|First fish|Staging|Not yet|Over|Unknown)\s+(high|medium|low) confidence$', l)
        if m: cur["snap"]["status"], cur["snap"]["conf"] = m.group(1), m.group(2); continue
        m = re.match(r'^(Water temp|Flow|Gauge)((?:\d|no |not |No ).*|near .*|at .*|above .*|none)$', l)
        if m and m.group(1) not in cur["snap"]:
            cur["snap"][m.group(1)] = m.group(2).strip(); continue
        m = re.match(r'^DNR The DNR weekly report of (\w+ \d+) named (.+?) here\.', l)
        if m: cur["snap"]["dnr_weekly"] = "DNR weekly report %s named %s here" % (m.group(1), m.group(2)); continue
        if l.startswith("DNR weir") and n + 1 < len(L): cur["weir"] = L[n + 1]
    return rivers

def asof(lines):
    for l in lines:
        m = re.search(r'Live tracker · updated (.+)$', l)
        if m: return m.group(1)
    return None

# ---- regional (non-Hub) entries: month-level, from explore-streams.json research ----
def month_win(months):
    """list of months -> (start 'MM-01', end 'MM-last') assuming one contiguous (possibly wrapping) block"""
    ms = sorted(set(months)); last = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    # find start: month whose predecessor is not in set
    st = next(m for m in ms if ((m - 2) % 12 + 1) not in ms)
    en = st
    while (en % 12 + 1) in ms: en = en % 12 + 1
    return "%02d-01" % st, "%02d-%02d" % (en, last[en])

REG = [
 dict(id="clinton", name="Clinton River (lower: Yates Dam to Lake St. Clair)", explore=["clinton-river"], home=["Clinton River (main stem)"], lake="St. Clair", runs=[
   dict(sp="steelhead", label="Steelhead fall run", start="09-01", end="11-30", peak=["10-01", "11-30"], src="regional", grain="month",
        note="Forum reports: fish in the system 'since October'; 2025 catches Sep 7 - Nov 23; best after rain + leaf drop. Month-level, forum-based.",
        url="https://www.michigan-sportsman.com/threads/clinton-river-2025-2026.772769/"),
   dict(sp="salmon", label="Salmon (species not specified)", start="10-01", end="11-30", peak=["11-01", "11-30"], src="regional", grain="month",
        note="Late Oct - mid Nov; redds 'peak salmon run' reported Nov 12, 2025 (forum). Minor run.",
        url="https://www.michigan-sportsman.com/threads/clinton-river-2025-2026.772769/"),
   dict(sp="steelhead", label="Steelhead spring run", start="02-01", end="05-31", peak=["03-01", "04-30"], src="regional+hub-page", grain="month",
        note="Hub's Clinton page: 'spring runs from March through May bring the best fishing'. Forum reports add Feb-Apr upper river after snowmelt, dropbacks into early May. Neither gives exact dates.",
        url=HUB + "/rivers/clinton-river/")],
   note="Not on the Hub salmon-run tracker (25 rivers, none of them SE Michigan). The Hub's Clinton page only says spring steelhead Mar-May (and a 'fall' run with no dates); fall timing here is forum-based and month-level."),
 dict(id="belle", name="Belle River (Memphis to Gratiot Rd)", explore=["belle-river"], home=[], lake="St. Clair", runs=[
   dict(sp="steelhead", label="Steelhead fall entry", start="10-01", end="11-30", peak=None, src="regional", grain="month", note="Entry late Oct - early Nov with rain (angler article).", url="https://www.glangler.com/blogs/articles/southeast-michigan-steelheading-eric-richard"),
   dict(sp="steelhead", label="Steelhead spring run", start="03-01", end="05-31", peak=None, src="regional", grain="month", note="Peak late Mar - early Apr; stragglers into May (angler article).", url="https://www.glangler.com/blogs/articles/southeast-michigan-steelheading-eric-richard")]),
 dict(id="st-clair", name="St. Clair River (Port Huron)", explore=["st-clair-river"], home=[], lake="St. Clair", runs=[
   dict(sp="steelhead", label="Steelhead / brown spring", start="03-01", end="05-31", peak=None, src="regional", grain="month", note="'Spring & fall' (angler article); month-level only.", url="https://www.glangler.com/blogs/articles/southeast-michigan-steelheading-eric-richard"),
   dict(sp="mixed", label="Fall run (steelhead / brown / chinook)", start="09-01", end="11-30", peak=None, src="regional", grain="month", note="'Spring & fall' (angler article); month-level only.", url="https://www.glangler.com/blogs/articles/southeast-michigan-steelheading-eric-richard")]),
 dict(id="huron-lower", name="Huron River (Flat Rock / Rockwood)", explore=["huron-lower"], home=[], lake="Erie", runs=[
   dict(sp="steelhead", label="Steelhead spring run", start="03-01", end="04-30", peak=None, src="regional", grain="month", note="Spring run stronger (Mar-Apr).", url="https://www.glangler.com/blogs/articles/southeast-michigan-steelheading-eric-richard"),
   dict(sp="steelhead", label="Steelhead fall run", start="09-01", end="11-30", peak=None, src="regional", grain="month", note="Fall run from late Sep (small fish); bigger fish Nov when water ~40F.", url="https://www.glangler.com/blogs/articles/southeast-michigan-steelheading-eric-richard")]),
 dict(id="mill-yale", name="Mill Creek / Black River at Yale", explore=["mill-creek-yale"], home=[], lake="Huron", runs=[
   dict(sp="steelhead", label="Steelhead spring run", start="03-01", end="05-31", peak=None, src="regional", grain="month", note="Late-spring steelhead; flashy creek. Unconfirmed which Mill Creek this is.", url="https://www.glangler.com/blogs/articles/southeast-michigan-steelheading-eric-richard")]),
 dict(id="vermilion-oh", name="Vermilion River, Ohio", explore=["vermilion-oh"], home=[], lake="Erie", runs=[
   dict(sp="steelhead", label="Steelhead (fall through spring)", start="10-01", end="05-31", peak=None, src="agency", grain="month", note="Ohio DNR: Oct-May; fish in harbor / lower river early and late, whole river mid-season.", url="https://ohiodnr.gov/buy-and-apply/hunting-fishing-boating/fishing-resources/steelhead-fishing-promo")]),
 dict(id="rocky-oh", name="Rocky River, Ohio", explore=["rocky-river-oh"], home=[], lake="Erie", runs=[
   dict(sp="steelhead", label="Steelhead (fall through spring)", start="10-01", end="05-31", peak=None, src="agency", grain="month", note="Ohio DNR: Oct-May.", url="https://ohiodnr.gov/buy-and-apply/hunting-fishing-boating/fishing-resources/steelhead-fishing-promo")]),
]

def main():
    args = sys.argv[1:]
    if "--html" in args: raw = open(args[args.index("--html") + 1], encoding="utf8", errors="ignore").read()
    else: raw = fetch(TRACKER)
    lines = totext(raw)
    when = asof(lines)
    hub = parse_tracker(lines)
    rivers = []
    for r in hub:
        n = r["hub_name"]
        o = dict(id=IDS[n], name=n.replace(" (Foote Dam water)", " (below Foote Dam)").replace("Huron River (Big Huron)", "Big Huron River (Baraga Co., L. Superior)").replace("Big Manistee River", "Manistee River (lower, below Tippy Dam)"),
                 hub_name=n, lake=r["lake"], counties=r["counties"], src="hub-tracker", url=HUB + "/rivers/" + SLUG[n] + "/",
                 explore=MATCH.get(n, []), home=[], match_note=MATCH_NOTE.get(n), runs=r["runs"],
                 barrier=r.get("Upstream limit"), access=r.get("Access"), crowding=r.get("Crowding"), regs=r.get("Regulations"), throw=r.get("What to throw"), weir=r.get("weir"),
                 snap=dict(r["snap"], asof=when))
        for x in o["runs"]:
            x["grain"] = "day"
        rivers.append(o)
    for g in REG:
        rivers.append(dict(id=g["id"], name=g["name"], lake=g["lake"], src="regional", explore=g["explore"], home=g["home"], runs=g["runs"], note=g.get("note"), url=None))
    iso = None
    try: iso = datetime.datetime.strptime(when, "%B %d, %Y, %I:%M %p").strftime("%Y-%m-%dT%H:%M:00-04:00")
    except Exception: pass
    out = dict(
        generated=datetime.date.today().isoformat(), hub_asof=when, hub_asof_iso=iso,
        sources=dict(tracker=TRACKER, steelhead=STEEL, clinton=HUB + "/rivers/clinton-river/"),
        method=("Hub-tracker windows are the Michigan Fly Fishing Hub's 'typical' start/end and peak dates per river and species (it says they are anchored to DNR weir operating "
                "dates - Little Manistee chinook weir ~Aug 15-Nov 15, Platte coho mid-Sep to late Oct - and shifted by latitude); they are a model, not a forecast. "
                "The Hub's own steelhead page says DNR publishes no per-river steelhead timing. Regional entries are month-level (first to last day of the month) from forum, angler-article or agency text."),
        species=dict(chinook="Chinook", coho="Coho", pink="Pink", steelhead="Steelhead", atlantic="Atlantic", brown="Lake-run brown", salmon="Salmon (unspecified)", mixed="Mixed fall run"),
        rivers=rivers)
    p = os.path.join(ROOT, "run-calendar.json")
    json.dump(out, open(p, "w"), indent=1, ensure_ascii=False)
    print("wrote", p, len(rivers), "rivers;", sum(len(r["runs"]) for r in rivers), "run windows; hub as-of:", when)

if __name__ == "__main__":
    main()
