#!/usr/bin/env python3
"""Build stockings.json: recent Michigan DNR fish stockings (last ~12 months, statewide).

Source: Michigan DNR Fish Stocking Database (public record, no use restrictions).
  Dashboard: https://www.michigandnr.com/fishstock/  (redirects to an ArcGIS Dashboard)
  Machine-readable table behind it (ArcGIS MapServer table 0 "FishStockReport"):
  https://utility.arcgis.com/usrsvcs/servers/fc7739be5f5247e7bf7f2c6bc9471140/rest/services/DNR/FishStockingReportGISAGO/MapServer/0
  Fields: County_Name, Water_Body_Name, waters_id, SPEC_COMM_Alt (species), str_comm (strain),
  stocking_date (epoch ms), Number_Fish_Stocked, Average_Length (cm), Operation (State/Federal/
  Private Plant (under permit)/Tribal/...), Marking_Group, sitename, town/range/sec (PLSS). No geometry.

Geocoding (in order, cached in tools/cache/ so scheduled runs only look up new places):
  1. PLSS section centroid from BLM CadNSDI (town/range/sec, Michigan Meridian) -> precision "section" (~1 mi)
  2. Most common section for the same waters_id+county in older DNR records -> "section (past plants)"
  3. County centroid (US Census TIGERweb) -> "county" (very approximate)
Drive time: OSRM public demo table API from home (12459 Plumbrook Rd, Sterling Heights), cached per point;
  falls back to a straight-line estimate (flagged drive_est) if the router is unreachable.

Run: python3 tools/build_stockings.py   (polite: ~1-2 DNR requests + lookups only for new places)
"""
import hashlib, json, math, os, sys, time, re, urllib.request, urllib.parse, datetime, collections
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "tools", "cache")
OUT = os.path.join(ROOT, "stockings.json")
DNR = "https://utility.arcgis.com/usrsvcs/servers/fc7739be5f5247e7bf7f2c6bc9471140/rest/services/DNR/FishStockingReportGISAGO/MapServer/0/query"
DASH = "https://www.michigandnr.com/fishstock/"
BLM = "https://gis.blm.gov/arcgis/rest/services/Cadastral/BLM_Natl_PLSS_CadNSDI/MapServer/2/query"
TIGER = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/1/query"
OSRM = "https://router.project-osrm.org/table/v1/driving/"
HOME = (42.5743976, -83.0018873)
TZ = ZoneInfo("America/Detroit")
DAYS = int(os.environ.get("STOCK_DAYS", "370"))
SMALL_CM = 15.24  # 6 in
UA = {"User-Agent": "mibluelining.com stocking builder (personal, non-commercial; github.com/markp-910/river-dashboard)"}
TROUT = {"brown trout", "rainbow trout", "brook trout", "lake trout", "splake", "tiger trout", "steelhead", "cutthroat trout"}
SALMON = {"coho salmon", "chinook salmon", "atlantic salmon", "pink salmon", "arctic grayling"}


def get(url, params=None, tries=3, timeout=60):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    for t in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return json.load(r)
        except Exception as e:
            if t == tries - 1:
                raise
            time.sleep(3 * (t + 1))


def post(url, data, tries=3, timeout=90):
    body = urllib.parse.urlencode(data).encode()
    for t in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=body, headers=UA), timeout=timeout) as r:
                return json.load(r)
        except Exception:
            if t == tries - 1:
                raise
            time.sleep(3 * (t + 1))


def lc(name, default):
    p = os.path.join(CACHE, name)
    try:
        return json.load(open(p))
    except Exception:
        return default


def sc(name, obj):
    os.makedirs(CACHE, exist_ok=True)
    with open(os.path.join(CACHE, name), "w") as f:
        json.dump(obj, f, indent=0, sort_keys=True)
        f.write("\n")


def s(v):
    return re.sub(r"\s+", " ", v).strip() if isinstance(v, str) else v


def dnr_rows(where, fields="*"):
    rows, off = [], 0
    while True:
        d = post(DNR, dict(where=where, outFields=fields, returnGeometry="false", orderByFields="ObjectID",
                           resultOffset=off, resultRecordCount=2000, f="json"))
        if "error" in d:
            raise RuntimeError(d["error"])
        feats = [f["attributes"] for f in d.get("features", [])]
        rows += feats
        if not d.get("exceededTransferLimit") or not feats:
            return rows
        off += len(feats)
        time.sleep(1)


def plssid(town, rng):
    m1, m2 = re.match(r"(\d+)([NS])", town or ""), re.match(r"(\d+)([EW])", rng or "")
    if not (m1 and m2):
        return None
    return f"MI19{int(m1[1]):03d}0{m1[2]}{int(m2[1]):03d}0{m2[2]}0"


def centroid(geom):
    best = None
    for ring in geom.get("rings", []):
        a = cx = cy = 0.0
        for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
            c = x1 * y2 - x2 * y1
            a += c; cx += (x1 + x2) * c; cy += (y1 + y2) * c
        if a and (best is None or abs(a) > abs(best[0])):
            best = (a, cx / (3 * a), cy / (3 * a))
    return (round(best[2], 5), round(best[1], 5)) if best else None


def geocode_sections(keys, cache):
    """keys: set of 'PLSSID|sec'. Fills cache with [lat,lng] or None."""
    todo = sorted(k for k in keys if k not in cache)
    by_t = collections.defaultdict(list)
    for k in todo:
        p, sec = k.split("|")
        by_t[p].append(sec)
    items = list(by_t.items())
    for i in range(0, len(items), 15):
        chunk = items[i:i + 15]
        where = " OR ".join(f"(PLSSID='{p}' AND FRSTDIVNO IN ({','.join(repr(x) for x in secs)}))" for p, secs in chunk)
        try:
            d = post(BLM, dict(where=where, outFields="PLSSID,FRSTDIVNO", returnGeometry="true", outSR=4326,
                               maxAllowableOffset=0.0005, f="json"))
        except Exception as e:
            print("BLM lookup failed:", e, file=sys.stderr); continue
        found = collections.defaultdict(list)
        for f in d.get("features", []):
            a = f["attributes"]; c = centroid(f.get("geometry") or {})
            if c:
                found[f"{a['PLSSID']}|{a['FRSTDIVNO']}"].append(c)
        for p, secs in chunk:
            for sec in secs:
                k = f"{p}|{sec}"; cs = found.get(k)
                cache[k] = [round(sum(c[0] for c in cs) / len(cs), 5), round(sum(c[1] for c in cs) / len(cs), 5)] if cs else None
        time.sleep(1)


def county_centroids(cache):
    if len(cache) >= 83:
        return cache
    d = get(TIGER, dict(where="STATE='26'", outFields="BASENAME,CENTLAT,CENTLON", returnGeometry="false", f="json"))
    for f in d.get("features", []):
        a = f["attributes"]; cache[a["BASENAME"]] = [round(float(a["CENTLAT"]), 4), round(float(a["CENTLON"]), 4)]
    return cache


def hav_mi(a, b):
    R = 3958.8; p1, p2 = math.radians(a[0]), math.radians(b[0]); dl = math.radians(b[1] - a[1]); dp = p2 - p1
    return 2 * R * math.asin(math.sqrt(math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2))


def drive_times(pts, cache):
    todo = sorted({f"{la:.4f},{ln:.4f}" for la, ln in pts} - set(cache))
    for i in range(0, len(todo), 80):
        chunk = todo[i:i + 80]
        coords = ";".join([f"{HOME[1]},{HOME[0]}"] + [f"{k.split(',')[1]},{k.split(',')[0]}" for k in chunk])
        try:
            d = get(OSRM + coords, dict(sources=0, annotations="duration,distance"), timeout=90)
            for k, du, di in zip(chunk, d["durations"][0][1:], d["distances"][0][1:]):
                if du is not None:
                    cache[k] = [round(du / 60), round(di / 1609.34, 1)]
        except Exception as e:
            print("OSRM failed:", e, file=sys.stderr)
        time.sleep(1.5)


def main():
    now = datetime.datetime.now(TZ)
    since = (now - datetime.timedelta(days=DAYS)).strftime("%Y-%m-%d")
    raw = dnr_rows(f"stocking_date >= DATE '{since}'")
    print("DNR rows:", len(raw))
    plss = lc("plss_sections.json", {}); wtrs = lc("waters_sections.json", {}); cty = lc("mi_counties.json", {}); drv = lc("drive_osrm.json", {})

    recs = []
    for a in raw:
        sp = s(a["SPEC_COMM_Alt"]) or "Unknown"; spl = sp.lower()
        dt = datetime.datetime.fromtimestamp(a["stocking_date"] / 1000, TZ).date().isoformat() if a["stocking_date"] else None
        cm = a["Average_Length"]; op = s(a["Operation"]) or ""; water = s(a["Water_Body_Name"]) or "Unknown water"
        r = dict(id=hashlib.sha1("|".join(str(x) for x in (a["stocking_date"], a["waters_id"], a["County_Name"], a["SPEC_COMM_Alt"], a["str_comm"], a["Number_Fish_Stocked"], a["Average_Length"], a["sitename"], a["town"], a["range"], a["sec"], a["Operation"], a["Marking_Group"])).encode()).hexdigest()[:12], date=dt, water=water, county=s(a["County_Name"]), waters_id=a["waters_id"],
                 species=sp, strain=s(a["str_comm"]) or None, count=a["Number_Fish_Stocked"],
                 len_cm=round(cm, 1) if cm else None, len_in=round(cm / 2.54, 1) if cm else None,
                 site=(s(a["sitename"]) or "").title() or None, operation=op, mark=s(a["Marking_Group"]) if s(a["Marking_Group"]) not in (None, "none") else None,
                 is_trout=spl in TROUT, is_salmonid=spl in TROUT or spl in SALMON)
        flags = []
        if op.startswith("Private"):
            flags.append("private_plant")
            if re.search(r"\b(pond|ponds|club|private)\b", water, re.I):
                flags.append("private_water")
        if cm is None:
            flags.append("size_unknown")
        elif cm < SMALL_CM:
            flags.append("small")
        if re.match(r"(Lake (Michigan|Huron|Superior|Erie)|Grid \d)", water):
            flags.append("great_lakes")
        r["flags"] = flags
        r["catchable"] = not ({"private_plant", "small"} & set(flags))
        pid = plssid(a["town"], a["range"])
        r["_k"] = f"{pid}|{a['sec']}" if pid and a["sec"] else None
        r["trs"] = f"T{a['town']} R{a['range']} S{a['sec']}" if r["_k"] else None
        recs.append(r)

    geocode_sections({r["_k"] for r in recs if r["_k"]}, plss)
    # fallback: most common section for this waters_id in past records
    miss = sorted({r["waters_id"] for r in recs if (not r["_k"] or not plss.get(r["_k"])) and r["waters_id"] and str(r["waters_id"]) not in wtrs})
    for i in range(0, len(miss), 50):
        ids = miss[i:i + 50]
        try:
            rows = dnr_rows(f"waters_id IN ({','.join(map(str, ids))}) AND town IS NOT NULL", "waters_id,County_Name,town,range,sec")
        except Exception as e:
            print("waters lookup failed:", e, file=sys.stderr); rows = []
        cnt = collections.defaultdict(collections.Counter)
        for a in rows:
            p = plssid(a["town"], a["range"])
            if p and a["sec"]:
                cnt[a["waters_id"]][(f"{p}|{a['sec']}", s(a["County_Name"]))] += 1
        for w in ids:
            wtrs[str(w)] = [[k, c, n] for (k, c), n in cnt[w].most_common(8)]
    geocode_sections({k for v in wtrs.values() for k, _, _ in v}, plss)
    county_centroids(cty)

    for r in recs:
        ll, prec = (plss.get(r["_k"]) if r["_k"] else None), "section"
        if not ll:
            for k, c, n in wtrs.get(str(r["waters_id"]), []):
                if c == r["county"] and plss.get(k):
                    ll, prec = plss[k], "section_past"; break
        if not ll and r["county"] in cty:
            ll, prec = cty[r["county"]], "county"
        r["lat"], r["lng"] = (ll or [None, None])
        r["precision"] = prec if ll else "none"
        r["approx"] = True  # DNR gives PLSS sections, never exact put-in points
        del r["_k"]

    drive_times([(r["lat"], r["lng"]) for r in recs if r["lat"]], drv)
    for r in recs:
        if r["lat"] is None:
            r["drive_min"] = r["drive_miles"] = None; continue
        k = f"{r['lat']:.4f},{r['lng']:.4f}"
        if k in drv:
            r["drive_min"], r["drive_miles"] = drv[k]
        else:
            mi = hav_mi(HOME, (r["lat"], r["lng"])) * 1.25
            r["drive_min"], r["drive_miles"], r["drive_est"] = round(mi / 50 * 60), round(mi, 1), True

    # Explore matching: same water name + county as an Explore stream's DNR stocking events
    try:
        X = json.load(open(os.path.join(ROOT, "explore-streams.json")))
        idx = collections.defaultdict(set)
        for st in X.get("streams", []):
            for e in st.get("stocking_events") or []:
                if e.get("water"):
                    idx[(e["water"].lower(), (e.get("county") or "").lower())].add(st["id"])
        for r in recs:
            ids = idx.get((r["water"].lower(), (r["county"] or "").lower()))
            if ids:
                r["explore"] = sorted(ids)
    except Exception as e:
        print("explore match skipped:", e, file=sys.stderr)

    recs.sort(key=lambda r: (r["date"] or "", r["water"], r["id"]), reverse=True)
    seen = collections.Counter()
    for r in recs:  # identical duplicate rows exist in the DNR table; keep them but give unique ids
        seen[r["id"]] += 1
        if seen[r["id"]] > 1:
            r["id"] += f"-{seen[r['id']]}"
    meta = dict(source="Michigan DNR Fish Stocking Database", source_url=DASH, api=DNR.rsplit("/query", 1)[0],
                license="Public record; DNR states no restrictions on use, reproduction or distribution (provided AS IS)",
                note="DNR enters plants in FSIS; they reach this public table after a DTMB clean-up step, so records can lag the actual stocking by days to weeks. "
                     "Locations are PLSS section centroids (~1 mi), not exact put-ins. 'catchable' = not a private plant and avg length >= 6 in.",
                home=dict(name="12459 Plumbrook Rd, Sterling Heights", lat=HOME[0], lng=HOME[1]),
                drive_method="OSRM public demo router (free-flow car) from home; drive_est=true means straight-line estimate",
                window_days=DAYS, since=since, latest_stocking=recs[0]["date"] if recs else None, count=len(recs))
    out = dict(meta=meta, stockings=recs)
    new = json.dumps(out, separators=(",", ":"), ensure_ascii=False)
    old = None
    try:
        o = json.load(open(OUT)); old = json.dumps(dict(meta={**o["meta"], "generated": None, "since": None}, stockings=o["stockings"]), separators=(",", ":"), ensure_ascii=False)
    except Exception:
        pass
    cmp_new = json.dumps(dict(meta={**meta, "generated": None, "since": None}, stockings=recs), separators=(",", ":"), ensure_ascii=False)
    if old == cmp_new:
        print("stockings.json unchanged")
    else:
        meta["generated"] = now.isoformat(timespec="minutes")
        with open(OUT, "w") as f:
            f.write(json.dumps(dict(meta=meta, stockings=recs), separators=(",", ":"), ensure_ascii=False) + "\n")
        print("wrote", OUT)
    for n, o in (("plss_sections.json", plss), ("waters_sections.json", wtrs), ("mi_counties.json", cty), ("drive_osrm.json", drv)):
        sc(n, o)
    d30 = (now - datetime.timedelta(days=30)).date().isoformat()
    r30 = [r for r in recs if r["date"] and r["date"] >= d30]
    print(f"last30: {len(r30)} all, {sum(r['catchable'] for r in r30)} catchable, "
          f"{sum(r['catchable'] and r['is_trout'] and (r['drive_min'] or 999) <= 90 for r in r30)} catchable trout <=90min; "
          f"precision {collections.Counter(r['precision'] for r in recs)}")


if __name__ == "__main__":
    main()
