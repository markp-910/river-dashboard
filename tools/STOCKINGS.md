# Fresh stockings: data source

**Source:** Michigan DNR Fish Stocking Database: https://www.michigandnr.com/fishstock/
(this page redirects to an ArcGIS Dashboard, item `77581b13c6984b919ab8ed927496a31f`).

**Machine-readable endpoint** (this is the table behind the dashboard; ArcGIS item `fc7739be5f5247e7bf7f2c6bc9471140`, owner Michigan DNR):

    https://utility.arcgis.com/usrsvcs/servers/fc7739be5f5247e7bf7f2c6bc9471140/rest/services/DNR/FishStockingReportGISAGO/MapServer/0/query

- It is table 0, `FishStockReport`. It holds every DNR-recorded stocking from Jan 1979 to now and has **no geometry**. You can request up to 2000 rows per call, and paging works.
- **Fields:** `County_Name`, `Water_Body_Name`, `waters_id`, `SPEC_COMM_Alt` (species), `str_comm` (strain), `stocking_date` (epoch ms), `Number_Fish_Stocked`, `Average_Length` (**cm**), `Operation`, `Marking_Group` (fin clips/tags), `sitename`, `town`/`range`/`sec` (PLSS section, Michigan Meridian).
- **`Operation` values:** State Plant, Federal Plant, Private Plant (under permit), Tribal Plant, Tribal/DNR Coop Plant, Transplant of Wild Fish, Educational Institution.
- **Update cadence:** Fisheries staff enter plants in FSIS, then a DTMB clean-up process loads them into this table. Records can show up days to weeks after the fish go in. The service item was last modified 2026-10-23, and the newest record on 2026-10-27 is dated 2026-10-14.
- **License:** a public record. The DNR states there are "no restrictions on the use, reproduction, or distribution", and the data is provided AS IS.

## Builder (`tools/build_stockings.py`)

- It pulls the last 370 days statewide (about 900 rows) in 1–2 requests.
- **Flags:** records are not dropped. `private_plant` (and `private_water` for names containing pond/club/private), `small` (average under 6 in / 15.24 cm), `size_unknown` and `great_lakes`. `catchable` means not a private plant and not small, which is what StockedMI shows. The site hides non-catchable records by default and has a toggle to show them.
- **Geocoding:**
  1. The BLM CadNSDI PLSS section centroid, about 1 mi accuracy.
  2. If the record has no section, the most common section for the same `waters_id` and county in past DNR plants.
  3. If that also fails, the county centroid from US Census TIGERweb.
  Every point is approximate. The DNR does not publish exact put-in points.
- **Drive time:** from the OSRM public demo table API (free-flow) from home, cached per point.
- **Explore link:** a stocking is tied to an Explore stream when it has the same water name and county as one of that stream's DNR stocking events.
- **Politeness:** lookups for sections, waters, counties and drive times are cached in `tools/cache/`, so scheduled runs only query places that are new. `stockings.json` is rewritten only when the data changes.

## Automation

`.github/workflows/stockings.yml` ("Refresh DNR stockings") runs at :23 every 6 hours and can also be started with workflow_dispatch. It commits `stockings.json` and `tools/cache` only when they changed.
