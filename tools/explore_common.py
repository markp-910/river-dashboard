"""Shared helpers/constants for tools/build_explore.py (US-only Explore tab, 4 drive tiers)."""
import json, os, re, datetime, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda *p: os.path.join(ROOT, "research", *p)
FO = "https://www.michigan.gov/dnr/-/media/Project/Websites/dnr/Documents/Orders/Fish-Orders/"
FO200 = FO + "FO_200.pdf (FO-200.25, trout & salmon regulations)"
FO210 = FO + "FO_210.pdf (FO-210.26, designated trout streams)"
FO213 = FO + "FO_213.pdf (FO-213.15, gear-restriction criteria)"
HUB = lambda s: f"https://michiganflyfishinghub.com/rivers/{s}/"
HUBBEST = "https://michiganflyfishinghub.com/best-fly-fishing-rivers-michigan.html"
DBURL = "https://www.dnr.state.mi.us/fishstock/ (DNR Fish Stocking Database, queried via its ArcGIS FishStockingReport service)"
TIERS = [(1, "Back Yard", 30), (2, "Quick Trip", 90), (3, "Half Day", 180), (4, "Fishing Trip!", 240)]
def tier_of(m):
    for n, _, mx in TIERS:
        if m <= mx: return n
    return None
SPG = [("steelhead", "Steelhead"), ("brown", "Brown trout"), ("rainbow", "Rainbow trout"), ("brook", "Brook trout"), ("chinook", "Salmon"), ("salmon", "Salmon"), ("coho", "Salmon"), ("smallmouth", "Smallmouth bass"), ("largemouth", "Largemouth bass"), ("pike", "Northern pike"), ("creek chub", "Creek chub")]
def groups(sp):
    g = []
    for s in sp:
        for k, v in SPG:
            if k in s.lower() and v not in g: g.append(v)
    return g

ALT = json.load(open(R("drive_alt.json"))) if os.path.exists(R("drive_alt.json")) else {}
def alt_min(key, lat, lng, home):
    """Valhalla cross-check of the one-way drive minutes (cached in research/drive_alt.json)."""
    if key in ALT: return ALT[key]
    try:
        body = {"locations": [{"lat": home["lat"], "lon": home["lng"]}, {"lat": lat, "lon": lng}], "costing": "auto"}
        r = urllib.request.Request("https://valhalla1.openstreetmap.de/route", data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "User-Agent": "fishing-dash/1.0"})
        ALT[key] = round(json.load(urllib.request.urlopen(r, timeout=40))["trip"]["summary"]["time"] / 60)
    except Exception:
        ALT[key] = None
    json.dump(ALT, open(R("drive_alt.json"), "w"))
    return ALT[key]

ev = {}
def _feats(f):
    d = json.load(open(R(f)))
    return d["features"] if isinstance(d, dict) and "features" in d else [x for v in d.values() for x in v]
for f in ("stock_region.json", "stock_named.json", "stock_new.json"):
    if os.path.exists(R(f)):
        for x in _feats(f):
            a = x["attributes"]
            if not a.get("stocking_date"): continue
            d = datetime.datetime.fromtimestamp(a["stocking_date"] / 1000, datetime.timezone.utc).strftime("%Y-%m-%d")
            k = (a["Water_Body_Name"].strip(), a["County_Name"].strip(), a["sitename"].strip(), a["SPEC_COMM_Alt"].strip(), d, a["Number_Fish_Stocked"])
            ev[k] = {"water": k[0], "county": k[1], "site": k[2].title() if k[2].isupper() else k[2], "species": k[3], "date": d, "count": k[5], "len_cm": a.get("Average_Length")}
EV = sorted(ev.values(), key=lambda e: e["date"], reverse=True)
TS = re.compile(r"trout|salmon|steelhead", re.I)
def stock_for(waters, sites=None, exclude_sites=None, counties=None, trout_only=True):
    return [e for e in EV if e["water"] in waters and e["date"] >= "2021-10-01"
            and (not counties or e["county"] in counties) and (not trout_only or TS.search(e["species"]))
            and (not sites or any(s.lower() in e["site"].lower() for s in sites))
            and not (exclude_sites and any(s.lower() in e["site"].lower() for s in exclude_sites))]
def stock_summary(evs, extra=""):
    if not evs: return "No trout/salmon stocking records found in the DNR database (Oct 2021–now)." + (" " + extra if extra else "")
    by = {}
    for e in evs: by[e["species"]] = by.get(e["species"], 0) + (e["count"] or 0)
    yrs = sorted({e["date"][:4] for e in evs})
    return "DNR DB (Oct 2021–now): " + ", ".join(f"{n:,} {s.lower()}" for s, n in by.items()) + f" in {len(evs)} stockings ({yrs[0]}–{yrs[-1]})." + (" " + extra if extra else "")

def state(types, designated, badge, lines, refs, prio=False, verified="FO text read", note=""):
    return dict(types=types, designated=designated, badge=badge, lines=lines, refs=refs, prio=prio, verified=verified, note=note)
NONE = lambda why, refs="FO-210.26 and FO-200.25 searched": state([], False, "Not state-designated", [why], refs, False, "not listed in FO-210/FO-200")
TR_NOTE = "TroutRoutes class read by Mark from his Pro account (county labels in the app are unreliable). Class: 1 best … 3; 'unknown' = not checked."
# Upper North Branch Clinton brook trout water (research/nb-clinton-brookies.md, 2026-10-20)
SR39 = "https://www2.dnr.state.mi.us/publications/pdfs/DNRFishLibrary/Special-ManagementReports/SR39.pdf (DNR Fisheries Special Report 39, Clinton River Assessment, Francis & Haas 2006)"
CRWC_CW = "https://www.crwc.org/clinton-river-coldwater-conservation-project (Clinton River Watershed Council: North Branch headwaters brook trout)"
CRWC_FISH = "https://www.crwc.org/recreation/fishing"
UMMZ = ["https://www.gbif.org/occurrence/1888987618 (UMMZ 82625, 1927, 'Almont Creek (=N Branch of Clinton River)' at the county-line bridges)",
        "https://www.gbif.org/occurrence/1888987648 (UMMZ 82620, 1927, Burr Creek, Bruce Twp)"]
NAS98 = "https://nas.er.usgs.gov/queries/SpecimenViewer.aspx?SpecimenID=1420679 (USGS NAS: brook trout 1998-08-04, McKay Ditch-North Branch Clinton HUC12, 'established')"
NAVSRC = ["https://www.eastgrmi.gov/DocumentCenter/View/2415/Public-Rights-on-Michigan-Waters-History-State-of-Michigan (State of Michigan, 'Public Rights on Michigan Waters', D. Public Rights in Streams)",
          "https://www.canr.msu.edu/michiganlakes/uploads/files/FAQPage/MI%20Water%20Laws.pdf (same document, MSU mirror)"]
NBHIST = ("Stocked with brook trout 1949–64, when the headwaters were called 'Townsend Creek'; DNR has no record of why it stopped (SR39 p.50). "
          "Brook trout were already here before any stocking: University of Michigan museum specimens collected in 1927 at the county-line bridges and in Burr Creek, Bruce Twp. "
          "Conservation-officer creel checks logged brookies on opening days 1930–63 (e.g. 48 anglers kept 112 on 4/30/1960; SR39 App. 2). "
          "Brown trout were stocked 1971–91 with 'marginal' survival; no trout stocked on the North Branch since 2009 (steelhead) and no brook trout since 1964 (DNR stocking DB). "
          "The 2001–02 DNR survey found brook trout only in Kidder Creek (8.6% of the catch at Boardman Rd), none at the three North Branch sites (all below Almont); "
          "SR39 still says the North Branch above Almont 'continues to have a self-sustaining brook trout population', and CRWC says native brookies were 'rediscovered' and are being monitored with DNR.")
NAVCAUTION = ("Private water caution: in Michigan the riparian landowner owns the streambed, and on a non-navigable (private) stream 'the public can neither wade nor float' "
              "(State of Michigan, Public Rights on Michigan Waters). Creeks this small are very likely non-navigable, so treat them as private: fish only from the public road right-of-way "
              "and get the landowner's permission before wading or walking past it. Don't park on the shoulder where it is posted or unsafe.")
