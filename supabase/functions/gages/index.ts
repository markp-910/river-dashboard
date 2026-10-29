// My Blue Lining — USGS gage proxy (Supabase Edge Function "gages").
// Serves the gage cards from the modern USGS Water Data API (api.waterdata.usgs.gov,
// OGC "continuous" collection), replacing the legacy waterservices.usgs.gov /nwis/iv.
// Every visitor shares one cached copy (10 min) so we stay far under USGS rate limits.
// Optional: set a free USGS/api.data.gov key as the function secret USGS_API_KEY
// (Dashboard → Edge Functions → Secrets). It never reaches the browser.
//
// GET /functions/v1/gages?sites=04161820,04165500&params=00060,00065,00010&hours=168
// → {fetched:"ISO", stale?:true, series:{"04161820":{"00060":[[epochSec,value],...]}}}
const API = "https://api.waterdata.usgs.gov/ogcapi/v1/collections/continuous/items";
const OK_PARAMS = new Set(["00060", "00065", "00010", "00300", "63680"]);
const TTL_MS = 10 * 60 * 1000;
const KEY = Deno.env.get("USGS_API_KEY") || "";
const SB_URL = Deno.env.get("SUPABASE_URL") || "";
const SB_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
const CORS = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, OPTIONS", "Access-Control-Allow-Headers": "*" };
const mem = new Map<string, { t: number; body: string }>();
const inflight = new Map<string, Promise<string>>();

const reply = (body: string, status = 200, extra: Record<string, string> = {}) =>
  new Response(body, { status, headers: { ...CORS, "Content-Type": "application/json", "Cache-Control": "public, max-age=120", ...extra } });

async function dbGet(k: string) {
  if (!SB_URL || !SB_KEY) return null;
  try {
    const r = await fetch(`${SB_URL}/rest/v1/usgs_cache?k=eq.${encodeURIComponent(k)}&select=body,fetched_at`, { headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` } });
    const j = await r.json();
    return Array.isArray(j) && j[0] ? { t: Date.parse(j[0].fetched_at), body: JSON.stringify(j[0].body) } : null;
  } catch { return null; }
}
async function dbPut(k: string, body: string) {
  if (!SB_URL || !SB_KEY) return;
  try {
    await fetch(`${SB_URL}/rest/v1/usgs_cache?on_conflict=k`, {
      method: "POST",
      headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}`, "Content-Type": "application/json", Prefer: "resolution=merge-duplicates,return=minimal" },
      body: JSON.stringify({ k, body: JSON.parse(body), fetched_at: new Date().toISOString() }),
    });
  } catch { /* cache is best-effort */ }
}

async function fromUsgs(sites: string[], params: string[], hours: number): Promise<string> {
  const start = new Date(Date.now() - hours * 3600e3).toISOString().replace(/\.\d+Z$/, "Z");
  const q = new URLSearchParams({
    f: "json", skipGeometry: "true", limit: "50000",
    monitoring_location_id: sites.map((s) => "USGS-" + s).join(","),
    parameter_code: params.join(","), datetime: `${start}/..`,
    properties: "time_series_id,monitoring_location_id,parameter_code,time,value",
  });
  let url: string | null = `${API}?${q}`;
  // group per time series first: a site can carry two sensors for one parameter
  const ts = new Map<string, { s: string; p: string; v: [number, number][] }>();
  for (let page = 0; url && page < 10; page++) {
    const r = await fetch(url, { headers: KEY ? { "X-Api-Key": KEY } : {} });
    if (!r.ok) throw new Error("USGS HTTP " + r.status);
    const j = await r.json();
    for (const f of j.features || []) {
      const p = f.properties, val = p.value == null ? NaN : +p.value;
      if (!isFinite(val) || val <= -999999) continue;
      let o = ts.get(p.time_series_id);
      if (!o) ts.set(p.time_series_id, o = { s: String(p.monitoring_location_id).replace(/^USGS-/, ""), p: p.parameter_code, v: [] });
      o.v.push([Math.round(Date.parse(p.time) / 1000), val]);
    }
    url = (j.links || []).find((l: { rel: string; href: string }) => l.rel === "next")?.href || null;
  }
  // keep the freshest series (then the longest) per site+parameter, sorted by time
  const out: Record<string, Record<string, [number, number][]>> = {};
  for (const o of ts.values()) {
    o.v.sort((a, b) => a[0] - b[0]);
    const cur = (out[o.s] ??= {})[o.p];
    const better = !cur || o.v[o.v.length - 1][0] > cur[cur.length - 1][0] || (o.v[o.v.length - 1][0] === cur[cur.length - 1][0] && o.v.length > cur.length);
    if (better) out[o.s][o.p] = o.v;
  }
  return JSON.stringify({ fetched: new Date().toISOString(), source: "api.waterdata.usgs.gov/ogcapi/v1 continuous", series: out });
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  const u = new URL(req.url);
  const sites = [...new Set((u.searchParams.get("sites") || "").split(",").map((s) => s.trim()).filter((s) => /^0\d{7,14}$/.test(s)))].sort();
  const params = [...new Set((u.searchParams.get("params") || "00060,00065,00010").split(",").filter((p) => OK_PARAMS.has(p)))].sort();
  const hours = Math.min(168, Math.max(1, Math.round(+(u.searchParams.get("hours") || 24)) || 24));
  if (!sites.length || sites.length > 60 || !params.length) return reply(JSON.stringify({ error: "need 1-60 USGS site numbers in ?sites=" }), 400);
  const k = `${sites.join(",")}|${params.join(",")}|${hours}`;
  const now = Date.now();
  let hit = mem.get(k);
  if (!hit || now - hit.t > TTL_MS) { const d = await dbGet(k); if (d && (!hit || d.t > hit.t)) { hit = d; mem.set(k, d); } }
  if (hit && now - hit.t <= TTL_MS) return reply(hit.body, 200, { "X-Cache": "hit" });
  try {
    let p = inflight.get(k);
    if (!p) { p = fromUsgs(sites, params, hours); inflight.set(k, p); }
    const body = await p.finally(() => inflight.delete(k));
    mem.set(k, { t: Date.now(), body });
    await dbPut(k, body);
    return reply(body, 200, { "X-Cache": "miss" });
  } catch (e) {
    if (hit) return reply(hit.body.replace(/^\{/, '{"stale":true,'), 200, { "X-Cache": "stale" });
    return reply(JSON.stringify({ error: String((e as Error).message || e) }), 502);
  }
});
