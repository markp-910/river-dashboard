// MI Blue Lining — accounts config.
// Leave SUPABASE_URL / SUPABASE_ANON_KEY blank and the site behaves exactly like the
// no-accounts version (local log + optional Google Sheet sync). Fill both in to turn on
// sign-in, per-user home base, and the Supabase-backed catch log (see docs/ACCOUNTS_SETUP.md).
// The anon key is meant to be public (Row Level Security protects the data). NEVER put the
// service_role key here.
window.FR_CONFIG = {
  SUPABASE_URL: "",        // e.g. "https://abcdefghijkl.supabase.co"
  SUPABASE_ANON_KEY: "",   // Project Settings → API → Project API keys → anon / publishable
  REQUIRE_SIGN_IN: true,   // show a sign-in screen over the site until someone signs in
  MAGIC_LINK: true         // offer "email me a sign-in link" in addition to password
};
