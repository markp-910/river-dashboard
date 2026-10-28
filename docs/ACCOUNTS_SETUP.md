# Accounts setup — MI Blue Lining

This branch (`accounts`) adds optional sign-in, a per-person home base, and a private catch log
stored in Supabase. **Nothing turns on until `config.js` has a Supabase URL and key.** With the
blank `config.js` the site works exactly like today (local log + Google Sheet sync).

What you get once it's on:

- A sign-in screen (email + password, optional "email me a sign-in link", forgot password).
- Invite-only: only people you invite can get in.
- Each person's own **home base** (a town label + lat/lon). Explore's drive-time tiers are
  recalculated from it. Only the label is shown, never a street address.
- Catch log and tagged spots save to the person's account, photos go to private storage, and
  "Want to fish" spots save as `saved_spots`.
- **Buddy groups**: catches are private by default. Pick a group in the "Share with" box to let
  that group see a catch. Group members can view shared catches but can't edit or delete them.
- A one-time **Import my existing Google Sheet log** button in the account panel.

Time needed: about 20–30 minutes.

---

## 1. Create the Supabase project (free tier)

1. Go to <https://supabase.com> → **Start your project**. Sign in with **GitHub as `markp-910`**
   (same account that owns the repo; simplest) or with the email you want to own the project.
2. **New organization** → name it e.g. `Mark's Fishing Report`, plan **Free** ($0).
3. **New project**
   - Name: `fishing-report`
   - Database password: let it generate one and save it in your password manager (you rarely need it).
   - Region: **East US (North Virginia)** (closest to Michigan).
4. Wait ~2 minutes for it to finish provisioning.

> Free-tier notes: 500 MB database, 1 GB file storage, 50k monthly active users — far more than a
> family needs. A free project **pauses after 7 days with no activity**; un-pause it from the
> dashboard with one click (data is kept). Regular use keeps it awake.

## 2. Run the schema

1. Dashboard → **SQL Editor** → **New query**.
2. Paste the whole of [`supabase/schema.sql`](../supabase/schema.sql) → **Run**.
   It creates the tables (`profiles`, `groups`, `group_members`, `catches`, `saved_spots`), Row
   Level Security policies, the private `catch-photos` storage bucket and its policies. It's safe
   to run again later.
3. Check: **Table Editor** shows the 5 tables, each with a "RLS enabled" badge. **Storage** shows
   a `catch-photos` bucket marked **Private**.

## 3. Turn off open sign-up (invite-only)

1. **Authentication → Sign In / Providers** (older dashboards: Authentication → Providers / Settings).
2. Under **User Signups**, turn **Allow new users to sign up** **off** → Save.
3. Leave the **Email** provider **enabled** (it's what invites, passwords and sign-in links use).
   "Confirm email" can stay on.

Invites still work with sign-up off; strangers who find the site can't create an account.

## 4. Set the site URLs (needed for invite / reset / sign-in links)

**Authentication → URL Configuration**

- **Site URL**: your final address, e.g. `https://www.yourdomain.com`
  (until the domain is live, use `https://markp-910.github.io/river-dashboard/`).
- **Redirect URLs** → add each of these:
  - `https://yourdomain.com/**`
  - `https://www.yourdomain.com/**`
  - `https://markp-910.github.io/river-dashboard/**`  (keeps working during the switch)

## 5. Put the keys in `config.js`

1. **Project Settings → API Keys** (or **Settings → API**).
2. Copy the **Project URL** (`https://xxxx.supabase.co`) and the **publishable** key
   (`sb_publishable_…`) — or, on older projects, the **anon public** key.
3. Edit `config.js`:

   ```js
   window.FR_CONFIG = {
     SUPABASE_URL: "https://xxxx.supabase.co",
     SUPABASE_ANON_KEY: "sb_publishable_…",
     REQUIRE_SIGN_IN: true,
     MAGIC_LINK: true
   };
   ```

   The publishable/anon key is designed to be public. Row Level Security protects the data.
   **Never** put the `service_role` / secret key in the site.

## 6. Invite people

1. **Authentication → Users → Add user → Send invitation** → enter their email.
2. They get an email, tap the link, land on the site already signed in, and are asked to **set a
   password** and their name.
3. Invite yourself first.

> Supabase's built-in email sender is rate-limited (a few emails per hour) and meant for testing.
> For a handful of family invites that's fine; if emails stop arriving, wait an hour, or set up
> free custom SMTP (e.g. Resend or Brevo) under **Authentication → Emails → SMTP Settings**.

## 7. First sign-in (Mark)

1. Sign in. Anything already in **My log on that phone** is moved into your account and uploaded,
   including photos stored on the phone.
2. Tap your name (top-right) → set **Home base**: Label `Sterling Heights`, then
   **📍 Use my current location** at home or **🔎 Look up town**. Save. Explore redraws its tiers.
3. **Import from Sheet**: paste your Apps Script `…/exec` URL into the box (it isn't stored in the
   site) → **Import from Sheet**. Re-running it skips rows already imported. Sheet photos stay in
   Google Drive and show as links/thumbnails.
4. **Buddy groups**: **Create group** (e.g. `Grayling crew`). Invite the people first (step 6),
   then type each email into the group's box → **Add**.
5. Pick a default under **New catches are shared with**, or choose per catch in the **Share with**
   box on the 🐟 form.

## 8. Custom domain (GitHub Pages)

You're buying the domain through your own registrar. Do this **when you're ready to switch the
live site**; it only matters on `main`.

1. **DNS at your registrar**
   - Apex (`yourdomain.com`): four **A** records → `185.199.108.153`, `185.199.109.153`,
     `185.199.110.153`, `185.199.111.153` (optionally **AAAA** → `2606:50c0:8000::153`,
     `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153`).
   - `www`: **CNAME** → `markp-910.github.io`
   - Remove any registrar "parking" / forwarding records for those names.
2. **Verify the domain with GitHub** (stops anyone else from claiming it): GitHub → your profile
   **Settings → Pages → Add a domain** → add the TXT record it shows → **Verify**.
3. **Repo → Settings → Pages → Custom domain** → enter `www.yourdomain.com` → Save.
   GitHub commits a `CNAME` file to `main` (or add one yourself: a file named `CNAME` in the repo
   root containing just `www.yourdomain.com`).
4. Wait for the DNS check to pass (minutes to a few hours), then tick **Enforce HTTPS**.
5. Update Supabase **Site URL / Redirect URLs** (step 4) if you used the github.io address before.
6. Old `markp-910.github.io/river-dashboard/` links redirect to the new domain automatically.

## 9. Going live

1. Test on the `accounts` branch first: either a second GitHub Pages site or a free Cloudflare
   Pages preview.
2. Merge `accounts` → `main` with real keys in `config.js`.
3. To switch accounts off again, blank the two keys in `config.js`. The site goes back to the
   local log + Sheet sync, and nothing is deleted from Supabase.

## Important: what "private" means here

The sign-in screen keeps people out of the **app**: everyone's catches, photos, spots and home
bases are protected by Supabase Row Level Security and are never public. But GitHub Pages serves
the site's **static files** (`index.html`, `explore-streams.json`, research notes, etc.) to
anyone who knows the URLs, even with the sign-in screen on. If the borrowed content
(TroutRoutes / Michigan Fly Fishing Hub / Fishbrain notes) must be truly private too, host on
**Cloudflare Pages + Cloudflare Access** (free for up to 50 users, email-code gate in front of
every file) instead of GitHub Pages. GitHub Pages can't password-protect files on a personal
plan.

## How it's wired (for later edits)

| File | What it does |
| --- | --- |
| `config.js` | Keys. Blank = accounts off. |
| `accounts.js` | Loads `supabase-js` from jsDelivr only when configured; sign-in UI, account panel, groups, sync, Sheet import, home-base drive tiers (OSRM table API, cached per home; falls back to a straight-line estimate). |
| `index.html` | Small hooks: `sync()`, **Load**, delete, auto-sync and Explore "Want to fish" call `window.FRA` when signed in; `window.FRLOG` / `window.FRWISH` bridges. |
| `supabase/schema.sql` | Tables, RLS, storage bucket + policies, `add_group_member()` RPC. |

Data rules (enforced in the database, not just the UI):

- You can read/write only your own rows.
- You can **read** rows shared to a group you belong to.
- Only a group's owner can add members (by email of an already-invited user). Members can leave.
- Photos live at `catch-photos/<your user id>/<catch id>.jpg`. Only you can upload, change or
  delete them. Group members can view photos of catches shared to their group (via short-lived
  signed links).
