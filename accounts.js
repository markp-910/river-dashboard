/* Mark's Fishing Report — optional accounts layer (Supabase).
 * Loaded before the app scripts. When window.FR_CONFIG has no SUPABASE_URL / SUPABASE_ANON_KEY,
 * window.FRA = {configured:false, on:false} and nothing else happens: no network calls, no UI.
 * Bridges used: window.FRLOG (catch log, set by the Home script), window.FRWISH (Explore wishlist).
 */
(() => {
  "use strict";
  const C = window.FR_CONFIG || {};
  const configured = !!(C.SUPABASE_URL && C.SUPABASE_ANON_KEY);
  const FRA = (window.FRA = { configured, get on() { return false; } });
  if (!configured) return;

  const SB_JS = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.118.0/dist/umd/supabase.min.js";
  const BUCKET = "catch-photos", OWNER_K = "fr_logOwner", SHARE_K = "fr_defaultShare", DRIVE_K = "fr_drive:";
  const $ = id => document.getElementById(id);
  const esc = x => String(x ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const toast = m => { let t = $("toast"); if (!t) { t = document.createElement("div"); t.id = "toast"; document.body.appendChild(t); } t.textContent = m; t.classList.add("on"); clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove("on"), 4500); };
  const LOG = () => window.FRLOG;
  // invite / recovery links land with #...type=invite|recovery — remember before supabase-js strips the hash
  const hashType = (/[#&]type=(invite|recovery|magiclink|signup)/.exec(location.hash) || [])[1] || "";
  if (hashType === "invite" || hashType === "recovery") sessionStorage.setItem("fr_needPw", hashType);

  let sb = null, session = null, profile = null, groups = [], names = {};
  Object.defineProperty(FRA, "on", { get: () => !!session });
  FRA.user = () => session?.user || null;
  FRA.profile = () => profile;
  FRA.groups = () => groups;

  // ---------- styles (army green + cream) ----------
  const css = document.createElement("style");
  css.textContent = `
  #acctBtn{position:absolute;top:14px;right:14px;z-index:2;background:rgba(246,240,225,.12);color:var(--cream);border:1px solid rgba(212,175,55,.7);border-radius:22px;min-height:40px;padding:6px 14px;font-weight:700;cursor:pointer;display:inline-flex;align-items:center;gap:6px;max-width:46vw;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  #acctBtn:hover{background:rgba(246,240,225,.22)}
  @media (max-width:560px){#acctBtn{top:8px;right:8px;min-height:36px;padding:4px 10px;font-size:.8em}}
  #acctdlg{position:fixed;inset:0;background:rgba(20,42,29,.62);display:none;align-items:flex-start;justify-content:center;z-index:10050;overflow:auto}
  #acctdlg.on{display:flex}
  #acctGate{position:fixed;inset:0;z-index:10040;display:none;align-items:center;justify-content:center;overflow:auto;background:linear-gradient(160deg,var(--g950),var(--g800) 60%,var(--g700))}
  #acctGate.on{display:flex}
  .acbox{background:var(--paper);margin:24px 12px;padding:20px;border-radius:14px;width:min(440px,100%);box-sizing:border-box;border:1px solid var(--line2);border-top:4px solid var(--brass);box-shadow:0 20px 50px rgba(0,0,0,.35);color:var(--ink)}
  .acbox h3{font-family:var(--serif);color:var(--g800);margin:0 0 6px;font-size:1.3em;display:flex;align-items:center;gap:10px}
  .acbox h3 img{width:44px;height:44px;border-radius:50%;box-shadow:0 0 0 2px var(--brass)}
  .acbox h4{font-family:var(--serif);color:var(--g800);margin:16px 0 4px;border-top:1px solid var(--line);padding-top:12px}
  .acbox label{display:block;margin:8px 0 2px;font-weight:600;font-size:.9em;color:var(--ink2)}
  .acbox input,.acbox select{width:100%;box-sizing:border-box;padding:10px;border:1px solid var(--line2);border-radius:8px;background:var(--field);font-size:1em;color:var(--ink)}
  .acbox .row{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
  .acbox .row>*{flex:1}
  .acbox .lnk{background:none;border:0;color:var(--link);text-decoration:underline;padding:4px 0;min-height:32px;cursor:pointer;font-weight:600}
  .acbox .acmsg{min-height:1.2em;font-size:.88em;color:var(--rust);margin-top:8px}
  .acbox .acmsg.ok{color:var(--good)}
  .acbox .grp{background:var(--cream2);border:1px solid var(--line);border-radius:8px;padding:8px 10px;margin:6px 0;font-size:.9em}
  .acbox .x{float:right;background:none;border:0;font-size:1.4em;min-height:36px;cursor:pointer;color:var(--ink)}
  .acbox .sub{font-size:.82em;color:var(--mute)}`;
  document.head.appendChild(css);

  // ---------- auth UI ----------
  const logo = '<img src="logo.png" alt="">';
  function signInHtml(gate) {
    return `<div class="acbox" role="dialog" aria-label="Sign in">${gate ? "" : '<button class="x" data-acclose aria-label="Close">✕</button>'}
      <h3>${logo}Mark's Fishing Report</h3>
      <div class="sub">Private site for family &amp; fishing buddies. Ask Mark for an invite.</div>
      <form id="acSignIn" autocomplete="on">
        <label for="acEmail">Email</label><input id="acEmail" name="email" type="email" autocomplete="username" required>
        <label for="acPw">Password</label><input id="acPw" name="password" type="password" autocomplete="current-password">
        <div class="row"><button type="submit" class="big" id="acGo">Sign in</button></div>
      </form>
      <div class="row" style="justify-content:space-between">${C.MAGIC_LINK !== false ? '<button class="lnk" id="acMagic" type="button">✉️ Email me a sign-in link</button>' : ""}<button class="lnk" id="acForgot" type="button">Forgot password?</button></div>
      <div class="acmsg" id="acMsg" aria-live="polite"></div></div>`;
  }
  const nice = t => /failed to fetch|network|load failed/i.test(t || "") ? "Can't reach the sign-in server. Check your connection and try again." : t;
  function wireSignIn(root) {
    const m = (t, ok) => { const e = root.querySelector("#acMsg"); e.textContent = nice(t); e.classList.toggle("ok", !!ok); };
    const email = () => root.querySelector("#acEmail").value.trim();
    const redirect = location.origin + location.pathname;
    root.querySelector("#acSignIn").onsubmit = async e => {
      e.preventDefault(); const pw = root.querySelector("#acPw").value;
      if (!email() || !pw) return m("Enter your email and password" + (C.MAGIC_LINK !== false ? " (or use a sign-in link)" : ""));
      m("Signing in…", true);
      try { const { error } = await (await ready()).auth.signInWithPassword({ email: email(), password: pw }); if (error) throw error; m("Signed in", true); }
      catch (err) { m(err.message || "Sign-in failed"); }
    };
    const mg = root.querySelector("#acMagic");
    if (mg) mg.onclick = async () => {
      if (!email()) return m("Enter your email first");
      m("Sending…", true);
      try { const { error } = await (await ready()).auth.signInWithOtp({ email: email(), options: { shouldCreateUser: false, emailRedirectTo: redirect } }); if (error) throw error; m("Check your email for a sign-in link", true); }
      catch (err) { m(err.message || "Couldn't send link"); }
    };
    root.querySelector("#acForgot").onclick = async () => {
      if (!email()) return m("Enter your email first");
      try { const { error } = await (await ready()).auth.resetPasswordForEmail(email(), { redirectTo: redirect }); if (error) throw error; m("Password reset email sent", true); }
      catch (err) { m(err.message || "Couldn't send reset email"); }
    };
  }
  function dlg(html) {
    let d = $("acctdlg"); if (!d) { d = document.createElement("div"); d.id = "acctdlg"; document.body.appendChild(d); d.addEventListener("click", e => { if (e.target === d || e.target.closest("[data-acclose]")) d.classList.remove("on"); }); }
    d.innerHTML = html; d.classList.add("on"); return d;
  }
  const closeDlg = () => $("acctdlg")?.classList.remove("on");
  function showGate(on) {
    if (C.REQUIRE_SIGN_IN === false) return;
    let g = $("acctGate");
    if (on && !g) { g = document.createElement("div"); g.id = "acctGate"; g.innerHTML = signInHtml(true); document.body.appendChild(g); wireSignIn(g); }
    if (g) g.classList.toggle("on", on);
    document.documentElement.style.overflow = on ? "hidden" : "";
  }
  function headerBtn() {
    const h = document.querySelector("header"); if (!h) return;
    let b = $("acctBtn"); if (!b) { b = document.createElement("button"); b.id = "acctBtn"; b.type = "button"; h.appendChild(b); }
    if (session) { b.textContent = "👤 " + (profile?.display_name || session.user.email.split("@")[0]) + " ▾"; b.onclick = accountPanel; b.title = "Account"; }
    else { b.textContent = "🔐 Sign in"; b.onclick = () => wireSignIn(dlg(signInHtml(false))); b.title = "Sign in"; }
  }
  function setPwPanel(kind) {
    const d = dlg(`<div class="acbox"><button class="x" data-acclose aria-label="Close">✕</button><h3>${logo}${kind === "invite" ? "Welcome! Set a password" : "Set a new password"}</h3>
      <form id="acPwF"><label for="acNew">New password (8+ characters)</label><input id="acNew" type="password" autocomplete="new-password" minlength="8" required>
      <label for="acName">Your name (shown to your group)</label><input id="acName" value="${esc(profile?.display_name || "")}">
      <div class="row"><button class="big" type="submit">Save</button></div></form><div class="acmsg" id="acMsg"></div></div>`);
    d.querySelector("#acPwF").onsubmit = async e => {
      e.preventDefault(); const m = d.querySelector("#acMsg");
      const { error } = await sb.auth.updateUser({ password: d.querySelector("#acNew").value });
      if (error) { m.textContent = error.message; return; }
      const nm = d.querySelector("#acName").value.trim(); if (nm) await saveProfile({ display_name: nm });
      sessionStorage.removeItem("fr_needPw"); m.className = "acmsg ok"; m.textContent = "Saved"; setTimeout(closeDlg, 700);
    };
  }

  // ---------- account panel: name, home base, groups, sharing, import, sign out ----------
  async function accountPanel() {
    await loadGroups();
    const p = profile || {}, def = localStorage.getItem(SHARE_K) || "";
    const d = dlg(`<div class="acbox" style="width:min(520px,100%)"><button class="x" data-acclose aria-label="Close">✕</button>
      <h3>${logo}Your account</h3><div class="sub">${esc(session.user.email)}</div>
      <label for="apName">Display name</label><input id="apName" value="${esc(p.display_name || "")}">
      <h4>🏠 Home base</h4><div class="sub">Explore drive-time tiers are measured from here. Only the label is shown on the site; use a town or neighborhood, not a street address.</div>
      <label for="apLabel">Label</label><input id="apLabel" placeholder="e.g. Sterling Heights" value="${esc(p.home_label || "")}">
      <div class="row"><div><label for="apLat">Latitude</label><input id="apLat" inputmode="decimal" value="${p.home_lat ?? ""}"></div><div><label for="apLon">Longitude</label><input id="apLon" inputmode="decimal" value="${p.home_lon ?? ""}"></div></div>
      <div class="row"><button type="button" id="apGeo">📍 Use my current location</button><button type="button" id="apFind">🔎 Look up town</button></div>
      <h4>👥 Buddy groups</h4><div class="sub">Catches are private unless you share them to a group. Everyone in the group can see what's shared to it.</div>
      <div id="apGroups">${groups.length ? groups.map(g => `<div class="grp"><b>${esc(g.name)}</b>${g.owner_id === session.user.id ? " · you own this" : ""}<br><span class="sub">${g.members.map(u => esc(names[u] || "member")).join(", ")}</span>${g.owner_id === session.user.id ? `<div class="row"><input placeholder="invited person's email" data-addto="${g.id}"><button type="button" data-addbtn="${g.id}">Add</button></div>` : ""}</div>`).join("") : '<div class="sub">No groups yet.</div>'}</div>
      <div class="row"><input id="apNewG" placeholder="New group name, e.g. Grayling crew"><button type="button" id="apMkG">Create group</button></div>
      <label for="apShare">New catches are shared with</label><select id="apShare"><option value="">Only me (private)</option>${groups.map(g => `<option value="${g.id}"${def === g.id ? " selected" : ""}>${esc(g.name)}</option>`).join("")}</select>
      <h4>⬇ Import my existing Google Sheet log</h4><div class="sub">One-time copy of your Sheet rows (catches, tagged spots, want-to-fish list) into your account. Re-running skips rows already imported.</div>
      <label for="apSheet">Apps Script web app URL (…/exec)</label><input id="apSheet" type="password" autocomplete="off" placeholder="${localStorage.getItem("sheetUrl") ? "using the URL saved on this device" : "paste your …/exec URL"}">
      <div class="row"><button type="button" id="apImport">Import from Sheet</button></div>
      <div class="row" style="margin-top:18px"><button type="button" class="big" id="apSave">Save</button><button type="button" id="apOut">Sign out</button></div>
      <div class="acmsg" id="acMsg" aria-live="polite"></div></div>`);
    const m = (t, ok) => { const e = d.querySelector("#acMsg"); e.textContent = t; e.className = "acmsg" + (ok ? " ok" : ""); };
    d.querySelector("#apGeo").onclick = () => navigator.geolocation?.getCurrentPosition(pos => { d.querySelector("#apLat").value = pos.coords.latitude.toFixed(4); d.querySelector("#apLon").value = pos.coords.longitude.toFixed(4); m("Location filled in — tap Save", true); }, e => m("Couldn't get location: " + e.message), { enableHighAccuracy: false, timeout: 15000 });
    d.querySelector("#apFind").onclick = async () => {
      const q = d.querySelector("#apLabel").value.trim(); if (!q) return m("Type a town in Label first");
      try { const r = await (await fetch("https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=us&q=" + encodeURIComponent(q))).json();
        if (!r[0]) return m("Not found"); d.querySelector("#apLat").value = (+r[0].lat).toFixed(4); d.querySelector("#apLon").value = (+r[0].lon).toFixed(4); m("Found " + r[0].display_name.split(",").slice(0, 3).join(",") + " — tap Save", true); }
      catch (e) { m("Lookup failed: " + e.message); }
    };
    d.querySelector("#apMkG").onclick = async () => {
      const n = d.querySelector("#apNewG").value.trim(); if (!n) return m("Name the group first");
      const { error } = await sb.from("groups").insert({ name: n }); if (error) return m(error.message); accountPanel();
    };
    d.querySelectorAll("[data-addbtn]").forEach(b => b.onclick = async () => {
      const g = b.dataset.addbtn, em = d.querySelector(`[data-addto="${g}"]`).value.trim(); if (!em) return m("Enter an email");
      const { data, error } = await sb.rpc("add_group_member", { p_group: g, p_email: em });
      if (error) return m(error.message);
      if (data === "not_found") return m("No account with that email yet. Invite them first from the Supabase dashboard (Authentication → Users → Invite user), then add them here.");
      accountPanel();
    });
    d.querySelector("#apImport").onclick = () => importSheet(d.querySelector("#apSheet").value.trim() || localStorage.getItem("sheetUrl") || "", m);
    d.querySelector("#apOut").onclick = signOut;
    d.querySelector("#apSave").onclick = async () => {
      const la = d.querySelector("#apLat").value.trim(), lo = d.querySelector("#apLon").value.trim();
      const patch = { display_name: d.querySelector("#apName").value.trim() || null, home_label: d.querySelector("#apLabel").value.trim() || null, home_lat: la === "" ? null : +la, home_lon: lo === "" ? null : +lo };
      if ((patch.home_lat === null) !== (patch.home_lon === null) || (patch.home_lat !== null && (!isFinite(patch.home_lat) || !isFinite(patch.home_lon)))) return m("Enter both latitude and longitude (or neither)");
      if (/^\s*\d+\s+\S/.test(patch.home_label || "")) return m("Use a town or area for the label, not a street address");
      localStorage.setItem(SHARE_K, d.querySelector("#apShare").value);
      const homeChanged = patch.home_lat !== (profile?.home_lat ?? null) || patch.home_lon !== (profile?.home_lon ?? null) || patch.home_label !== (profile?.home_label ?? null);
      const err = await saveProfile(patch); if (err) return m(err.message);
      m("Saved", true); headerBtn(); if (homeChanged) setTimeout(() => location.reload(), 600);
    };
  }
  async function saveProfile(patch) {
    const { data, error } = await sb.from("profiles").upsert({ id: session.user.id, ...patch }).select().single();
    if (!error) profile = data; return error;
  }
  async function loadGroups() {
    const [{ data: g }, { data: mem }] = await Promise.all([sb.from("groups").select("id,name,owner_id").order("created_at"), sb.from("group_members").select("group_id,user_id")]);
    groups = (g || []).map(x => ({ ...x, members: (mem || []).filter(r => r.group_id === x.id).map(r => r.user_id) }));
    const { data: ps } = await sb.from("profiles").select("id,display_name,email");
    for (const p of ps || []) names[p.id] = p.display_name || (p.email || "").split("@")[0];
  }

  // ---------- local log ownership (one device, several people) ----------
  const LS = localStorage, KEYS = ["fishTags", "wishlist"];
  function switchOwner(uid) {
    const cur = LS.getItem(OWNER_K) || "";
    if (cur === uid) return false;
    const stash = cur || "device", had = KEYS.some(k => LS.getItem(k + "@" + uid) !== null);
    for (const k of KEYS) { const v = LS.getItem(k); if (v !== null) LS.setItem(k + "@" + stash, v); }
    if (uid && !had && !cur) {
      // first sign-in on this device: adopt the device's log into the account (re-upload everything once)
      const t = JSON.parse(LS.getItem("fishTags") || "[]").map(x => ({ ...x, synced: false }));
      LS.setItem("fishTags", JSON.stringify(t));
      const w = JSON.parse(LS.getItem("wishlist") || "[]").map(x => ({ ...x, synced: false }));
      LS.setItem("wishlist", JSON.stringify(w));
      for (const k of KEYS) LS.removeItem(k + "@device");
      if (t.length || w.length) sessionStorage.setItem("fr_adopted", String(t.length + w.length));
    } else for (const k of KEYS) { const v = LS.getItem(k + "@" + (uid || "device")); v === null ? LS.removeItem(k) : LS.setItem(k, v); }
    uid ? LS.setItem(OWNER_K, uid) : LS.removeItem(OWNER_K);
    return true;
  }
  async function signOut() {
    try { await sb.auth.signOut(); } catch (e) {}
    switchOwner(""); location.reload();
  }

  // ---------- catch log: Supabase instead of the Google Sheet ----------
  const FIELDS = ["nearest_gage", "gage_name", "gage_dist_mi", "flow_cfs", "pct_median", "temp_f", "rating", "species", "length_in", "fly_lure", "note"];
  const toRow = (x, uid) => {
    const share = x.share ?? (LS.getItem(SHARE_K) || "");
    const r = { user_id: uid, client_id: String(x.id), type: x.type === "spot" ? "spot" : "fish", ts: x.timestamp || new Date().toISOString(), lat: +x.lat, lng: +x.lng,
      visibility: share ? "group" : "private", group_id: share || null, photo_url: x.photo_url || null, photo_file_id: x.photo_file_id || null };
    for (const f of FIELDS) r[f] = x[f] === undefined || x[f] === null ? null : String(x[f]);
    if (x.photo_path) r.photo_path = x.photo_path;
    return r;
  };
  const fromRow = (r, uid) => {
    const mine = r.user_id === uid, t = { id: mine ? r.client_id : "g:" + r.id, type: r.type, timestamp: r.ts, lat: r.lat, lng: r.lng, synced: true, photo_path: r.photo_path || "", photo_url: r.photo_url || "", photo_file_id: r.photo_file_id || "", share: r.group_id || "" };
    for (const f of FIELDS) t[f] = r[f] ?? "";
    if (!mine) { t.shared = true; t.owner_name = names[r.user_id] || "buddy"; }
    if (!t.photo_path && r.photo_file_id) t.photo_thumb = `https://drive.google.com/thumbnail?id=${r.photo_file_id}&sz=w400`;
    return t;
  };
  async function dataUrlBlob(u) { return await (await fetch(u)).blob(); }
  FRA.sync = async function () {
    const L = LOG(), uid = session.user.id, q = L.tags().filter(x => !x.synced && !x.shared);
    if (!q.length) return L.msg("Nothing to sync");
    L.msg("Syncing to your account…"); const done = {}; let warn = "";
    for (const x of q) {
      try {
        const extra = {};
        if (x.has_photo) {
          const ph = await L.photoGet(x.id).catch(() => null);
          if (ph) { const path = `${uid}/${x.id}.jpg`; const { error } = await sb.storage.from(BUCKET).upload(path, await dataUrlBlob(ph), { upsert: true, contentType: "image/jpeg" }); if (error) throw error; extra.photo_path = path; }
        }
        const { error } = await sb.from("catches").upsert(toRow({ ...x, ...extra }, uid), { onConflict: "user_id,client_id" }); if (error) throw error;
        done[x.id] = extra;
      } catch (e) { warn = " — " + (e.message || "sync failed") + " (rest kept in queue)"; break; }
    }
    L.saveTags(L.tags().map(x => done[x.id] ? { ...x, ...done[x.id], synced: true } : x));
    L.msg(`Synced ${Object.keys(done).length}/${q.length} to your account` + warn);
  };
  FRA.load = async function (quiet) {
    const L = LOG(), uid = session.user.id; if (!quiet) L.msg("Loading…");
    const { data, error } = await sb.from("catches").select("*").order("ts");
    if (error) { L.msg("Load failed: " + error.message); return; }
    const rows = (data || []).map(r => fromRow(r, uid)), keep = L.tags().filter(x => !x.synced), have = new Set(keep.map(x => x.id));
    const paths = rows.filter(r => r.photo_path).map(r => r.photo_path);
    if (paths.length) { const { data: s } = await sb.storage.from(BUCKET).createSignedUrls(paths, 3600 * 12); const by = Object.fromEntries((s || []).filter(z => z.signedUrl).map(z => [z.path, z.signedUrl])); rows.forEach(r => { if (by[r.photo_path]) r.photo_thumb = by[r.photo_path]; }); }
    // keep the local has_photo flag (IndexedDB copy) for my own rows
    const local = Object.fromEntries(L.tags().map(x => [x.id, x]));
    rows.forEach(r => { if (local[r.id]?.has_photo) r.has_photo = true; });
    L.saveTags([...rows.filter(r => !have.has(r.id)), ...keep].sort((a, b) => String(a.timestamp).localeCompare(String(b.timestamp))));
    if (!quiet) L.msg(`Loaded ${rows.length} from your account (${rows.filter(r => r.shared).length} shared by your group)`);
  };
  FRA.del = async function (x) {
    const L = LOG();
    if (x.shared) return "That catch belongs to " + (x.owner_name || "someone else") + " — only they can delete it";
    if (!x.synced) return "Deleted (was not yet synced)";
    const { error } = await sb.from("catches").delete().eq("user_id", session.user.id).eq("client_id", String(x.id));
    if (error) return "Deleted locally — account delete failed: " + error.message;
    if (x.photo_path) await sb.storage.from(BUCKET).remove([x.photo_path]).catch(() => {});
    return "Deleted locally and from your account";
  };
  FRA.isShared = x => !!x?.shared;

  // ---------- Explore "Want to fish" → saved_spots ----------
  FRA.saveSpot = async function (s) {
    const share = LS.getItem(SHARE_K) || "";
    const { error } = await sb.from("saved_spots").upsert({ user_id: session.user.id, stream_id: s.id, name: s.name, lat: s.lat, lng: s.lng, visibility: share ? "group" : "private", group_id: share || null }, { onConflict: "user_id,stream_id" });
    if (error) throw error;
  };
  FRA.removeSpot = async function (id) {
    const { error } = await sb.from("saved_spots").delete().eq("user_id", session.user.id).eq("stream_id", id); if (error) throw error;
  };
  async function loadSpots() {
    const { data } = await sb.from("saved_spots").select("stream_id,name,created_at,user_id").eq("user_id", session.user.id);
    if (data?.length) dispatchEvent(new CustomEvent("wishlist-merge", { detail: data.map(r => ({ id: "wish-" + r.stream_id, gage_name: r.name, timestamp: r.created_at })) }));
    // push any local-only wishlist entries
    const W = window.FRWISH; if (!W) return;
    const a = W.wl(), todo = a.filter(w => !w.synced); if (!todo.length) return;
    const { error } = await sb.from("saved_spots").upsert(todo.map(w => ({ user_id: session.user.id, stream_id: w.id, name: w.name || w.id, visibility: "private" })), { onConflict: "user_id,stream_id" });
    if (!error) W.setWl(W.wl().map(w => ({ ...w, synced: true })));
  }

  // ---------- one-time import from the Google Sheet (GET → {ok, rows}) ----------
  async function importSheet(url, m) {
    if (!url) return m("Paste your Apps Script …/exec URL (it isn't stored in the site)");
    if (!/^https:\/\/script\.google(usercontent)?\.com\//.test(url)) return m("That doesn't look like an Apps Script URL");
    m("Reading your Sheet…", true);
    let rows; try { const r = await (await fetch(url)).json(); if (r.ok === false) throw new Error(r.error || "script error"); rows = r.rows || []; } catch (e) { return m("Couldn't read the Sheet: " + e.message); }
    const uid = session.user.id, wish = rows.filter(r => r.type === "wishlist"), log = rows.filter(r => r.id && r.type !== "wishlist" && isFinite(+r.lat) && isFinite(+r.lng) && r.lat !== "");
    const cat = log.map(r => toRow({ ...r, id: String(r.id), share: "" }, uid));
    for (let i = 0; i < cat.length; i += 200) { const { error } = await sb.from("catches").upsert(cat.slice(i, i + 200), { onConflict: "user_id,client_id", ignoreDuplicates: true }); if (error) return m("Import failed: " + error.message); }
    if (wish.length) { const { error } = await sb.from("saved_spots").upsert(wish.map(r => ({ user_id: uid, stream_id: String(r.id).replace(/^wish-/, ""), name: r.gage_name || String(r.id), lat: +r.lat || null, lng: +r.lng || null, note: r.note || null })), { onConflict: "user_id,stream_id", ignoreDuplicates: true }); if (error) return m("Spots import failed: " + error.message); }
    await FRA.load(true); await loadSpots();
    m(`Imported ${cat.length} log rows and ${wish.length} want-to-fish spots. Sheet photos stay in Google Drive (linked).`, true);
  }

  // ---------- per-user home base → Explore drive tiers ----------
  const hav = (a, b, c, d) => { const r = Math.PI / 180; return 7917.6 * Math.asin(Math.sqrt(Math.sin((c - a) * r / 2) ** 2 + Math.cos(a * r) * Math.cos(c * r) * Math.sin((d - b) * r / 2) ** 2)); };
  FRA.applyHome = async function (XD) {
    try { await Promise.race([ready(), new Promise(r => setTimeout(r, 4000))]); } catch (e) {}
    if (!session || !XD?.home) return;
    const p = profile || {}, label = p.home_label || "your home base";
    const hasHome = p.home_lat != null && p.home_lon != null;
    const moved = hasHome && hav(XD.home.lat, XD.home.lng, p.home_lat, p.home_lon) > 0.6;
    XD.home = { ...XD.home, address: label, custom: moved };
    if (!moved) { if (hasHome) { XD.home.lat = p.home_lat; XD.home.lng = p.home_lon; } return; }
    XD.home.lat = p.home_lat; XD.home.lng = p.home_lon;
    const key = DRIVE_K + p.home_lat.toFixed(3) + "," + p.home_lon.toFixed(3) + ":" + XD.streams.length;
    let D = null; try { D = JSON.parse(LS.getItem(key) || "null"); } catch (e) {}
    if (!D) {
      try {
        const pts = [[p.home_lon, p.home_lat], ...XD.streams.map(s => [s.lng, s.lat])].map(c => c[0].toFixed(5) + "," + c[1].toFixed(5)).join(";");
        const j = await (await fetch(`https://router.project-osrm.org/table/v1/driving/${pts}?sources=0&annotations=duration,distance`)).json();
        if (j.code !== "Ok") throw new Error(j.code);
        D = { m: "osrm", v: XD.streams.map((s, i) => [j.durations[0][i + 1], j.distances[0][i + 1]]) };
        LS.setItem(key, JSON.stringify(D));
      } catch (e) { D = { m: "est", v: XD.streams.map(s => { const mi = hav(p.home_lat, p.home_lon, s.lat, s.lng) * 1.25; return [mi / 50 * 3600 + 300, mi * 1609.34]; }) }; }
    }
    const tierOf = min => { for (const t of XD.tiers || []) if (min <= t.max) return t.n; return 4; };
    XD.streams.forEach((s, i) => { const [sec, m] = D.v[i] || []; if (sec == null) return; s.drive_min = Math.round(sec / 60); s.drive_miles = Math.round(m / 1609.34); s.tier = tierOf(s.drive_min); delete s.drive_min_alt; });
    XD.drive_method = (D.m === "osrm" ? "One-way free-flow minutes from your home base by the OSRM public demo server (car), computed in your browser." : "Rough estimate (straight-line × 1.25 at ~50 mph) because the routing server was unreachable.") + " The stream list itself was built around Mark's home, so some water near you may be missing.";
  };

  // ---------- log-box + form tweaks when signed in ----------
  function decorateLog() {
    const s = document.querySelector(".logbox summary"); if (s) s.innerHTML = s.innerHTML.replace("Google Sheet sync", "account sync");
    const u = $("sheetUrl"); if (u) u.closest(".row").style.display = "none";
    const lb = $("loadBtn"); if (lb) lb.textContent = "⬇ Load from account";
    const f = $("tagform"); if (f && !$("acShare")) {
      const lab = document.createElement("label"); lab.innerHTML = 'Share with<select name="share" id="acShare"></select>';
      const notes = f.querySelector("textarea[name=note]")?.closest("label"); f.insertBefore(lab, notes || f.lastElementChild);
    }
    const sel = $("acShare"); if (sel) { const def = LS.getItem(SHARE_K) || ""; sel.innerHTML = `<option value="">Only me (private)</option>` + groups.map(g => `<option value="${g.id}"${def === g.id ? " selected" : ""}>${esc(g.name)}</option>`).join(""); }
  }

  // ---------- boot ----------
  let readyP = null;
  function ready() {
    if (readyP) return readyP;
    readyP = new Promise((ok, no) => {
      const go = () => { try { sb = window.supabase.createClient(C.SUPABASE_URL, C.SUPABASE_ANON_KEY, { auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true } }); ok(sb); } catch (e) { no(e); } };
      if (window.supabase?.createClient) return go();
      const s = document.createElement("script"); s.src = SB_JS; s.async = true; s.onload = go; s.onerror = () => no(new Error("Couldn't load the sign-in library")); document.head.appendChild(s);
    }).then(async c => {
      const { data } = await c.auth.getSession(); await onSession(data.session, "INITIAL");
      c.auth.onAuthStateChange((ev, s) => { if (ev === "INITIAL_SESSION") return; setTimeout(() => onSession(s, ev), 0); });
      return c;
    });
    return readyP;
  }
  FRA.ready = ready;
  async function onSession(s, ev) {
    const prev = session?.user?.id || "";
    session = s || null;
    if (!session) { headerBtn(); showGate(true); return; }
    if (switchOwner(session.user.id)) { location.reload(); return; }
    showGate(false); closeDlg();
    if (ev !== "INITIAL" && prev === session.user.id) { headerBtn(); return; }
    const { data } = await sb.from("profiles").select("*").eq("id", session.user.id).maybeSingle(); profile = data;
    await loadGroups().catch(() => {});
    headerBtn(); decorateLog();
    const need = sessionStorage.getItem("fr_needPw"); if (need || ev === "PASSWORD_RECOVERY") setPwPanel(need || "recovery");
    const ad = sessionStorage.getItem("fr_adopted"); if (ad) { sessionStorage.removeItem("fr_adopted"); toast(`Moved this device's log (${ad} items) into your account`); }
    try { await FRA.sync(); } catch (e) {}
    try { await FRA.load(true); } catch (e) {}
    try { await loadSpots(); } catch (e) {}
  }
  const boot = () => { headerBtn(); ready().catch(e => { headerBtn(); toast(e.message); showGate(true); }); };
  document.readyState === "loading" ? document.addEventListener("DOMContentLoaded", boot) : boot();
})();
