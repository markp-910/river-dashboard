# Fishing Log Sheet script (Apps Script)

The site talks to the Fishing Log Google Sheet through the Apps Script web app in
[`apps-script/Code.gs`](../apps-script/Code.gs). Never commit the deployed `/exec` URL; it works like a write key.

## Actions

| Request | What it does |
|---|---|
| `GET` | returns `{ok, rows:[...]}` |
| `POST [tag, ...]` | adds rows (skips ids already in the Sheet) |
| `POST {"action":"add","tags":[tag],"photo":{...}}` | adds a row and saves its photo to Drive |
| `POST {"action":"delete","id":"..."}` | deletes the row **and trashes its Drive photo** |
| `POST {"action":"update","id":"...","patch":{...}}` | edits one row in place. Only `lat, lng, nearest_gage, gage_name, gage_dist_mi, species, length_in, fly_lure, note` can be patched; id, type, timestamp and photo columns are never touched. Returns `{ok, action:"update", updated, fields}` |

"Move pin" on the map uses `update`. If the deployed script is older, `update` falls through to
`add`, which skips the existing id, so nothing changes. The site keeps the new spot on the device,
marks it "⏳ not yet saved to Sheet", and retries on the next sync or Sheet refresh.

## Redeploy after changing Code.gs (keeps the same /exec URL)

1. Open the **Fishing Log** Google Sheet, then **Extensions → Apps Script**.
2. Open `Code.gs`, select all, delete, and paste in the full contents of `apps-script/Code.gs` from this repo. Click **Save** (💾).
3. **Deploy → Manage deployments**. Select the existing **Web app** deployment and click the **pencil (Edit)** icon.
4. Under **Version**, choose **New version**. Leave *Execute as: Me* and *Who has access: Anyone* unchanged. Click **Deploy**.
5. The Web app URL stays the same, so there's nothing to change on your phone or computer. If Google asks you to authorize, allow it.

Don't use **Deploy → New deployment**: that creates a different URL, and every device would need the new link.
