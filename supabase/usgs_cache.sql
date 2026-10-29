-- Server-side cache for the "gages" Edge Function (USGS Water Data API proxy).
-- RLS on with no policies: only the function's service role can read/write it.
create table if not exists public.usgs_cache (
  k text primary key,
  body jsonb not null,
  fetched_at timestamptz not null default now()
);
alter table public.usgs_cache enable row level security;
