// Fishing Log sync — paste into the "Fishing Log" sheet via Extensions > Apps Script.
// Deploy > New deployment > Web app; Execute as: Me; Who has access: Anyone.
// POST bodies (sent as text/plain JSON):
//   [ {tag}, ... ]                                      add tags (legacy plain array)
//   {"action":"add","tags":[{tag}],"photo":{"id","mime","base64"}}   add tags + optional photo for tags[0]
//   {"action":"delete","id":"..."}                      delete row (and trash its photo)
//   {"action":"update","id":"...","patch":{"lat":..,"lng":..,...}}  edit fields of one row in place
//                                                       (photo, id, type, timestamp are never touched)
// GET returns {ok, rows:[...]}.
const HEADERS = ["id","type","timestamp","lat","lng","nearest_gage","gage_name","gage_dist_mi","flow_cfs","pct_median","temp_f","rating","species","length_in","fly_lure","note","photo_url","photo_preview","photo_file_id"];
const PHOTO_FOLDER = "Fishing Log Photos";

function sheet_() {
  const sh = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  if (sh.getLastRow() === 0) { sh.appendRow(HEADERS); return sh; }
  // Backward compatible: append any missing headers to row 1.
  const lastCol = Math.max(sh.getLastColumn(), 1);
  const have = sh.getRange(1, 1, 1, lastCol).getValues()[0].map(String);
  const missing = HEADERS.filter(h => have.indexOf(h) < 0);
  if (missing.length) sh.getRange(1, lastCol + 1, 1, missing.length).setValues([missing]);
  return sh;
}
function headers_(sh) { return sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0].map(String); }
function json_(obj) { return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON); }

function folder_() {
  const it = DriveApp.getFoldersByName(PHOTO_FOLDER);
  return it.hasNext() ? it.next() : DriveApp.createFolder(PHOTO_FOLDER);
}
function savePhoto_(p, tagId) {
  const mime = p.mime || "image/jpeg";
  const ext = mime.indexOf("png") >= 0 ? "png" : "jpg";
  const blob = Utilities.newBlob(Utilities.base64Decode(String(p.base64).replace(/^data:[^,]+,/, "")), mime, "catch-" + tagId + "." + ext);
  const f = folder_().createFile(blob);
  try { f.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW); } catch (e) { /* domain policy may block link sharing */ }
  return { fileId: f.getId(), url: f.getUrl(), thumb: "https://drive.google.com/thumbnail?id=" + f.getId() + "&sz=w400" };
}

function addRows_(sh, rows, photo) {
  const H = headers_(sh), idCol = H.indexOf("id") + 1, last = sh.getLastRow();
  const existing = new Set(last > 1 ? sh.getRange(2, idCol, last - 1, 1).getValues().map(r => String(r[0])) : []);
  const added = [], photos = {};
  rows.forEach((r, i) => {
    if (!r || !r.id || existing.has(String(r.id))) return;
    if (i === 0 && photo && photo.base64) {
      const s = savePhoto_(photo, r.id);
      r.photo_url = s.url; r.photo_file_id = s.fileId; r.photo_preview = '=IMAGE("' + s.thumb + '")';
      photos[r.id] = { url: s.url, thumb: s.thumb, fileId: s.fileId };
    }
    sh.appendRow(H.map(h => r[h] === undefined || r[h] === null ? "" : r[h]));
    existing.add(String(r.id)); added.push(r.id);
  });
  return { ok: true, added: added, received: rows.length, photos: photos };
}

function deleteRow_(sh, id) {
  const H = headers_(sh), idCol = H.indexOf("id") + 1, fCol = H.indexOf("photo_file_id") + 1, last = sh.getLastRow();
  let deleted = 0, photosTrashed = 0;
  if (id && last > 1) {
    const vals = sh.getRange(2, 1, last - 1, sh.getLastColumn()).getValues();
    for (let i = vals.length - 1; i >= 0; i--) {
      if (String(vals[i][idCol - 1]) !== id) continue;
      const fid = fCol ? String(vals[i][fCol - 1] || "") : "";
      if (fid) { try { DriveApp.getFileById(fid).setTrashed(true); photosTrashed++; } catch (e) {} }
      sh.deleteRow(i + 2); deleted++;
    }
  }
  return { ok: true, action: "delete", id: id, deleted: deleted, photosTrashed: photosTrashed };
}

// Fields the site may patch in place (e.g. "Move pin"). id/type/timestamp/photo_* are never editable here.
const PATCHABLE = ["lat","lng","nearest_gage","gage_name","gage_dist_mi","species","length_in","fly_lure","note"];
function updateRow_(sh, id, patch) {
  const H = headers_(sh), idCol = H.indexOf("id") + 1, last = sh.getLastRow();
  const keys = Object.keys(patch || {}).filter(k => PATCHABLE.indexOf(k) >= 0 && H.indexOf(k) >= 0);
  let updated = 0;
  if (id && keys.length && last > 1) {
    const ids = sh.getRange(2, idCol, last - 1, 1).getValues();
    for (let i = 0; i < ids.length; i++) {
      if (String(ids[i][0]) !== id) continue;
      keys.forEach(k => { const v = patch[k]; sh.getRange(i + 2, H.indexOf(k) + 1).setValue(v === null || v === undefined ? "" : v); });
      updated++;
    }
  }
  return { ok: true, action: "update", id: id, updated: updated, fields: keys };
}

function doPost(e) {
  const lock = LockService.getScriptLock(); lock.waitLock(30000);
  try {
    const sh = sheet_();
    const body = JSON.parse(e.postData.contents);
    if (Array.isArray(body)) return json_(addRows_(sh, body, null));
    if (body && body.action === "delete") return json_(deleteRow_(sh, String(body.id || "")));
    if (body && body.action === "update") return json_(updateRow_(sh, String(body.id || ""), body.patch || {}));
    if (body && body.action === "add") return json_(addRows_(sh, body.tags || [], body.photo || null));
    return json_(addRows_(sh, [body], null));
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  } finally { lock.releaseLock(); }
}

function doGet() {
  const sh = sheet_(), v = sh.getDataRange().getValues(), h = v.shift().map(String);
  return json_({ ok: true, rows: v.map(r => Object.fromEntries(h.filter(k => k !== "photo_preview").map(k => [k, r[h.indexOf(k)] instanceof Date ? r[h.indexOf(k)].toISOString() : r[h.indexOf(k)]]))) });
}

// Run once from the editor to trigger the Drive permission prompt.
function authorize() { folder_(); }
