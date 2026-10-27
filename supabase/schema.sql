-- =====================================================================
-- Mark's Fishing Report — accounts schema (Supabase / Postgres)
-- Run once in Supabase Dashboard → SQL Editor → New query → paste → Run.
-- Safe to re-run: uses IF NOT EXISTS / CREATE OR REPLACE / DROP POLICY IF EXISTS.
--
-- Model
--   profiles       1 row per auth user: display name + home base (lat/lon/label)
--   groups         buddy groups ("Adamo family", "Grayling crew")
--   group_members  who is in which group (owner | member)
--   catches        the fishing log: catches AND tagged spots (type = 'fish' | 'spot');
--                  columns mirror the Apps Script / Google Sheet log row
--   saved_spots    the Explore "Want to fish" list
--   storage bucket catch-photos (private), objects at  <user_id>/<client_id>.jpg
--
-- Privacy: everything is private by default. A catch / saved spot is visible to
-- the members of ONE group only when visibility = 'group' and group_id is set.
-- =====================================================================

create extension if not exists pgcrypto;

-- ---------- profiles ----------
create table if not exists public.profiles (
  id            uuid primary key references auth.users(id) on delete cascade,
  email         text,
  display_name  text,
  home_label    text,                 -- e.g. "Sterling Heights" (never a street number in the UI)
  home_lat      double precision,
  home_lon      double precision,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  constraint home_lat_ok check (home_lat is null or home_lat between -90 and 90),
  constraint home_lon_ok check (home_lon is null or home_lon between -180 and 180)
);

-- auto-create a profile row when a user is invited / signs up
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, email, display_name)
  values (new.id, new.email, coalesce(new.raw_user_meta_data->>'display_name', split_part(new.email, '@', 1)))
  on conflict (id) do nothing;
  return new;
end $$;
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

-- ---------- groups ----------
create table if not exists public.groups (
  id          uuid primary key default gen_random_uuid(),
  name        text not null check (length(name) between 1 and 80),
  owner_id    uuid not null default auth.uid() references auth.users(id) on delete cascade,
  created_at  timestamptz not null default now()
);

create table if not exists public.group_members (
  group_id   uuid not null references public.groups(id) on delete cascade,
  user_id    uuid not null references auth.users(id) on delete cascade,
  role       text not null default 'member' check (role in ('owner','member')),
  added_at   timestamptz not null default now(),
  primary key (group_id, user_id)
);
create index if not exists group_members_user_idx on public.group_members(user_id);

-- helper functions (SECURITY DEFINER so RLS policies can call them without recursion)
create or replace function public.is_group_member(g uuid)
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.group_members m where m.group_id = g and m.user_id = auth.uid());
$$;
create or replace function public.is_group_owner(g uuid)
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.groups x where x.id = g and x.owner_id = auth.uid());
$$;
create or replace function public.shares_group_with(other uuid)
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.group_members a join public.group_members b on a.group_id = b.group_id
                 where a.user_id = auth.uid() and b.user_id = other);
$$;

-- group creator becomes owner-member automatically
create or replace function public.handle_new_group()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.group_members (group_id, user_id, role) values (new.id, new.owner_id, 'owner')
  on conflict do nothing;
  return new;
end $$;
drop trigger if exists on_group_created on public.groups;
create trigger on_group_created after insert on public.groups
  for each row execute function public.handle_new_group();

-- owner adds an EXISTING (already invited) user to a group by email
create or replace function public.add_group_member(p_group uuid, p_email text)
returns text language plpgsql security definer set search_path = public as $$
declare uid uuid;
begin
  if not public.is_group_owner(p_group) then raise exception 'Only the group owner can add members'; end if;
  select id into uid from auth.users where lower(email) = lower(trim(p_email));
  if uid is null then return 'not_found'; end if;   -- invite them first (Dashboard → Authentication → Users → Invite)
  insert into public.group_members (group_id, user_id) values (p_group, uid) on conflict do nothing;
  return 'added';
end $$;
revoke all on function public.add_group_member(uuid, text) from public, anon;
grant execute on function public.add_group_member(uuid, text) to authenticated;

-- ---------- catches (fishing log rows) ----------
create table if not exists public.catches (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null default auth.uid() references auth.users(id) on delete cascade,
  client_id      text not null,           -- the log's own id (same as the Sheet "id" column) → dedupe key
  type           text not null default 'fish' check (type in ('fish','spot')),
  ts             timestamptz not null,    -- Sheet "timestamp"
  lat            double precision not null,
  lng            double precision not null,
  nearest_gage   text,
  gage_name      text,
  gage_dist_mi   text,
  flow_cfs       text,
  pct_median     text,
  temp_f         text,
  rating         text,
  species        text,
  length_in      text,
  fly_lure       text,
  note           text,
  photo_path     text,                    -- object in storage bucket catch-photos: <user_id>/<client_id>.jpg
  photo_url      text,                    -- legacy Google Drive link from the Sheet import
  photo_file_id  text,                    -- legacy Google Drive file id from the Sheet import
  visibility     text not null default 'private' check (visibility in ('private','group')),
  group_id       uuid references public.groups(id) on delete set null,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now(),
  unique (user_id, client_id),
  constraint group_needs_id check (visibility = 'private' or group_id is not null)
);
create index if not exists catches_user_ts_idx on public.catches(user_id, ts desc);
create index if not exists catches_group_idx on public.catches(group_id) where visibility = 'group';

-- ---------- saved spots (Explore "Want to fish") ----------
create table if not exists public.saved_spots (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null default auth.uid() references auth.users(id) on delete cascade,
  stream_id   text not null,              -- explore-streams.json id, or 'custom-…'
  name        text not null,
  lat         double precision,
  lng         double precision,
  note        text,
  visibility  text not null default 'private' check (visibility in ('private','group')),
  group_id    uuid references public.groups(id) on delete set null,
  created_at  timestamptz not null default now(),
  unique (user_id, stream_id),
  constraint spot_group_needs_id check (visibility = 'private' or group_id is not null)
);

-- updated_at bumpers
create or replace function public.touch_updated_at() returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end $$;
drop trigger if exists catches_touch on public.catches;
create trigger catches_touch before update on public.catches for each row execute function public.touch_updated_at();
drop trigger if exists profiles_touch on public.profiles;
create trigger profiles_touch before update on public.profiles for each row execute function public.touch_updated_at();

-- =====================================================================
-- Row Level Security
-- =====================================================================
alter table public.profiles      enable row level security;
alter table public.groups        enable row level security;
alter table public.group_members enable row level security;
alter table public.catches       enable row level security;
alter table public.saved_spots   enable row level security;

-- profiles: read own + people you share a group with (for names); write own only
drop policy if exists profiles_select on public.profiles;
create policy profiles_select on public.profiles for select to authenticated
  using (id = auth.uid() or public.shares_group_with(id));
drop policy if exists profiles_insert on public.profiles;
create policy profiles_insert on public.profiles for insert to authenticated with check (id = auth.uid());
drop policy if exists profiles_update on public.profiles;
create policy profiles_update on public.profiles for update to authenticated
  using (id = auth.uid()) with check (id = auth.uid());

-- groups: members can see; anyone signed in can create (they become owner); owner edits/deletes
drop policy if exists groups_select on public.groups;
create policy groups_select on public.groups for select to authenticated
  using (owner_id = auth.uid() or public.is_group_member(id));
drop policy if exists groups_insert on public.groups;
create policy groups_insert on public.groups for insert to authenticated with check (owner_id = auth.uid());
drop policy if exists groups_update on public.groups;
create policy groups_update on public.groups for update to authenticated
  using (owner_id = auth.uid()) with check (owner_id = auth.uid());
drop policy if exists groups_delete on public.groups;
create policy groups_delete on public.groups for delete to authenticated using (owner_id = auth.uid());

-- group_members: members see the roster; owner removes anyone; a member can leave.
-- Adding goes through add_group_member() (no direct insert policy).
drop policy if exists gm_select on public.group_members;
create policy gm_select on public.group_members for select to authenticated
  using (public.is_group_member(group_id));
drop policy if exists gm_delete on public.group_members;
create policy gm_delete on public.group_members for delete to authenticated
  using (user_id = auth.uid() or public.is_group_owner(group_id));

-- catches: own rows full access; group rows read-only for members of that group
drop policy if exists catches_select on public.catches;
create policy catches_select on public.catches for select to authenticated
  using (user_id = auth.uid() or (visibility = 'group' and public.is_group_member(group_id)));
drop policy if exists catches_insert on public.catches;
create policy catches_insert on public.catches for insert to authenticated
  with check (user_id = auth.uid() and (group_id is null or public.is_group_member(group_id)));
drop policy if exists catches_update on public.catches;
create policy catches_update on public.catches for update to authenticated
  using (user_id = auth.uid())
  with check (user_id = auth.uid() and (group_id is null or public.is_group_member(group_id)));
drop policy if exists catches_delete on public.catches;
create policy catches_delete on public.catches for delete to authenticated using (user_id = auth.uid());

-- saved_spots: same pattern
drop policy if exists spots_select on public.saved_spots;
create policy spots_select on public.saved_spots for select to authenticated
  using (user_id = auth.uid() or (visibility = 'group' and public.is_group_member(group_id)));
drop policy if exists spots_insert on public.saved_spots;
create policy spots_insert on public.saved_spots for insert to authenticated
  with check (user_id = auth.uid() and (group_id is null or public.is_group_member(group_id)));
drop policy if exists spots_update on public.saved_spots;
create policy spots_update on public.saved_spots for update to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid() and (group_id is null or public.is_group_member(group_id)));
drop policy if exists spots_delete on public.saved_spots;
create policy spots_delete on public.saved_spots for delete to authenticated using (user_id = auth.uid());

-- the anon role gets nothing
revoke all on public.profiles, public.groups, public.group_members, public.catches, public.saved_spots from anon;
grant select, insert, update, delete on public.profiles, public.groups, public.group_members, public.catches, public.saved_spots to authenticated;

-- =====================================================================
-- Storage: private bucket for catch photos
--   object name = '<owner user_id>/<client_id>.jpg'
-- =====================================================================
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('catch-photos', 'catch-photos', false, 5242880, array['image/jpeg','image/png','image/webp'])
on conflict (id) do update set public = false, file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

-- can the current user read this photo? owner, or member of the group the catch is shared to
create or replace function public.can_read_catch_photo(object_name text)
returns boolean language sql stable security definer set search_path = public as $$
  select exists (
    select 1 from public.catches c
    where c.photo_path = object_name
      and (c.user_id = auth.uid() or (c.visibility = 'group' and public.is_group_member(c.group_id)))
  );
$$;

drop policy if exists "catch photos read" on storage.objects;
create policy "catch photos read" on storage.objects for select to authenticated
  using (bucket_id = 'catch-photos'
         and ((storage.foldername(name))[1] = auth.uid()::text or public.can_read_catch_photo(name)));
drop policy if exists "catch photos insert own folder" on storage.objects;
create policy "catch photos insert own folder" on storage.objects for insert to authenticated
  with check (bucket_id = 'catch-photos' and (storage.foldername(name))[1] = auth.uid()::text);
drop policy if exists "catch photos update own folder" on storage.objects;
create policy "catch photos update own folder" on storage.objects for update to authenticated
  using (bucket_id = 'catch-photos' and (storage.foldername(name))[1] = auth.uid()::text)
  with check (bucket_id = 'catch-photos' and (storage.foldername(name))[1] = auth.uid()::text);
drop policy if exists "catch photos delete own folder" on storage.objects;
create policy "catch photos delete own folder" on storage.objects for delete to authenticated
  using (bucket_id = 'catch-photos' and (storage.foldername(name))[1] = auth.uid()::text);

-- =====================================================================
-- Quick self-check (optional): should list 5 tables with rowsecurity = true
--   select tablename, rowsecurity from pg_tables where schemaname = 'public';
-- =====================================================================
