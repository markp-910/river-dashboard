#!/usr/bin/env python3
"""Build gage-normals.json: day-of-year median daily discharge (00060) for every gage the site shows.

Source: USGS Water Data Statistics API (api.waterdata.usgs.gov/statistics/v0/observationNormals,
normal_type=DOY, computation_type=median) — the replacement for the legacy
waterservices.usgs.gov/nwis/stat p50 ("median for today") that retires Feb 2027.
Normals only change when USGS approves another water year, so this runs monthly (normals.yml).
Values are rounded like legacy NWIS p50_va (2 sig figs under 10 cfs, else 3 sig figs, whole cfs).

Run: python3 tools/build_normals.py     (optional env USGS_API_KEY raises the rate limit)
"""
import json, os, re, sys, time, datetime, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "gage-normals.json")
API = "https://api.waterdata.usgs.gov/statistics/v0/observationNormals"
UA = {"User-Agent": "mybluelining.com normals builder (personal, non-commercial; github.com/markp-910/river-dashboard)"}
KEY = os.environ.get("USGS_API_KEY", "").strip()
DAYS = [(datetime.date(2024, 1, 1) + datetime.timedelta(d)).strftime("%m-%d") for d in range(366)]  # leap-year index


def site_ids():
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    grp = re.search(r"const GROUPS=\{(.*?)\};", html, re.S).group(1)
    home = re.findall(r'\["(\d{8,15})"', grp)
    ex = json.load(open(os.path.join(ROOT, "explore-streams.json"), encoding="utf-8"))
    exp = [g["id"] for s in ex["streams"] for g in s.get("gages", [])]
    return sorted(set(home) | set(exp))


def nwis_round(v):
    if v < 10:
        return float(f"{v:.2g}")
    return int(round(float(f"{v:.3g}")))


def get(params):
    hdr = dict(UA, **({"X-Api-Key": KEY} if KEY else {}))
    url = API + "?" + urllib.parse.urlencode(params, doseq=True)
    for t in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=120) as r:
                return json.load(r)
        except Exception as e:
            print("retry", t + 1, e, file=sys.stderr)
            time.sleep(5 * (t + 1))
    raise SystemExit("statistics API unreachable")


def main():
    ids = site_ids()
    out = {}
    for i in range(0, len(ids), 25):
        base = [("monitoring_location_id", "USGS-" + s) for s in ids[i:i + 25]] + [
            ("parameter_code", "00060"), ("normal_type", "DOY"), ("computation_type", "median"), ("page_size", "1000")]
        tok = None
        while True:
            j = get(base + ([("next_token", tok)] if tok else []))
            for f in j.get("features", []):
                p = f["properties"]; sid = p["monitoring_location_id"].replace("USGS-", "")
                for d in p.get("data", []):
                    if d.get("parameter_code") != "00060" or d.get("parent_statistic_id") not in (None, "00003"):
                        continue
                    arr = out.setdefault(sid, [None] * 366)
                    for v in d.get("values", []):
                        if v.get("computation") == "median" and v.get("time_of_year") in DAYS and v.get("value") not in (None, ""):
                            arr[DAYS.index(v["time_of_year"])] = nwis_round(float(v["value"]))
            tok = j.get("next")
            if not tok:
                break
        time.sleep(1)
    missing = [s for s in ids if s not in out]
    meta = dict(source="USGS Water Data Statistics API observationNormals (DOY median of daily mean discharge, 00060)",
                url=API, index="p50[site][i] where i = day of a leap year (0 = Jan 1, 59 = Feb 29, 365 = Dec 31)",
                sites=len(out), missing=missing)
    new = dict(meta=meta, p50=dict(sorted(out.items())))
    old = None
    try:
        old = json.load(open(OUT, encoding="utf-8"))
    except Exception:
        pass
    if old and old.get("p50") == new["p50"] and old.get("meta", {}).get("missing") == missing:
        print("normals unchanged"); return
    new["meta"]["built"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(new, fh, separators=(",", ":"))
    print(f"wrote {OUT}: {len(out)} sites; missing: {missing or 'none'}")


if __name__ == "__main__":
    main()
