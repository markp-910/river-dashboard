-- Site admins: read-only access to everyone's catches, profiles, saved spots and photos.
-- Safe to re-run.
create table if not exists public.admins (user_id uuid primary key references auth.users(id) on delete cascade);
alter table public.admins enable row level security;
revoke all on public.admins from anon, authenticated;
create or replace function public.is_admin()
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.admins a where a.user_id = auth.uid());
$$;
grant execute on function public.is_admin() to authenticated;
drop policy if exists admin_read_catches on public.catches;
create policy admin_read_catches on public.catches for select to authenticated using (public.is_admin());
drop policy if exists admin_read_profiles on public.profiles;
create policy admin_read_profiles on public.profiles for select to authenticated using (public.is_admin());
drop policy if exists admin_read_spots on public.saved_spots;
create policy admin_read_spots on public.saved_spots for select to authenticated using (public.is_admin());
drop policy if exists admin_read_photos on storage.objects;
create policy admin_read_photos on storage.objects for select to authenticated using (bucket_id = 'catch-photos' and public.is_admin());
-- Mark
insert into public.admins (user_id) select id from auth.users where lower(email) = 'markp910@gmail.com' on conflict do nothing;
