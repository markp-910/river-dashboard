# USGS gage data (Phase 0 migration, Oct 2026)

The legacy `waterservices.usgs.gov` (NWIS iv + stat) is throttled from Nov 16, 2026 and shut off Feb 22, 2027.
The site now uses the modern **USGS Water Data API** (`api.waterdata.usgs.gov`).

| What the cards show | Legacy call (removed) | Now |
|---|---|---|
| Flow 00060, gage height 00065, water temp 00010, DO 00300, turbidity 63680 — latest value + 7-day chart (Home) / 24 h (Explore) | `/nwis/iv/?period=P7D` | OGC `collections/continuous/items` (all sites + params in one request), via the `gages` Edge Function |
| "Median for today" / % of normal | `/nwis/stat/?statTypeCd=p50` | Statistics API `observationNormals` (DOY median of daily mean), prebuilt into `gage-normals.json` by `tools/build_normals.py` (monthly workflow `normals.yml`) |

## How a page load gets data
1. Browser → `https://lqbetpvutttwbumjnglk.supabase.co/functions/v1/gages?sites=…&params=…&hours=…`
   (source: `supabase/functions/gages/index.ts`). One shared copy is cached 10 min (memory + table `public.usgs_cache`,
   `supabase/usgs_cache.sql`), so USGS sees a handful of requests per hour no matter how many people visit.
2. If the function is down, the browser calls `api.waterdata.usgs.gov` directly (keyless, one batched request).
3. If both fail, the page shows "USGS gage data is unavailable right now" and everything else keeps working.

## Optional API key (raises USGS rate limits; never in the browser)
1. Get a free key at https://api.waterdata.usgs.gov/signup/ (emailed to you).
2. Supabase Dashboard → project *mibluelining* → Edge Functions → Secrets → add `USGS_API_KEY` = your key.
3. (Optional) GitHub repo → Settings → Secrets and variables → Actions → add `USGS_API_KEY` too (used by the monthly normals build).

Redeploy the function: `curl -X POST "https://api.supabase.com/v1/projects/lqbetpvutttwbumjnglk/functions/deploy?slug=gages" -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" -F 'metadata={"entrypoint_path":"index.ts","name":"gages","verify_jwt":false};type=application/json' -F "file=@supabase/functions/gages/index.ts;type=application/typescript"`
