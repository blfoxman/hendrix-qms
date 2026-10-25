-- =====================================================================
-- Hendrix QMS  -  Step 12: CSQ in daily operations
-- Small changes to existing modules so CSQ clauses are met by the records
-- people already keep:
--   * Visitors (CSQ 2A.13.8): every sign-in records the GMP rules acknowledgement
--     and an illness declaration; the kiosk refuses sign-in without them
--   * Roles (2A.13.1): requirements (certifications, training, experience)
--   * Label templates (2A.12.7, 3C.2.6): allergen declaration, printed on stickers
--   * Sticker print log (2A.12.8 d, e): every sticker print is recorded
--     (batch, tag, template, count, who) and can never be changed or deleted
--   * Testing (2A.12.9 i): retention (reserve) sample quantity, location, keep-until
-- Sanitation verification, pest station checks and temp / humidity limits live in
-- the facility log forms and need no database change.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-11.
-- Safe to run more than once.
-- =====================================================================

-- ---------- visitors ----------
alter table hx_visitor_log add column if not exists gmp_ack boolean not null default false;
alter table hx_visitor_log add column if not exists ill boolean;
alter table hx_visitor_log add column if not exists ack_at timestamptz;

create or replace function hx_kiosk_visitor_in2(p_lic text, p jsonb) returns text
language plpgsql security definer set search_path = public as $$
declare l record; v_id text;
begin
  select id, state_id, active into l from hx_licenses where id = p_lic;
  if l.id is null or not coalesce(l.active, false) then
    raise exception 'This QR code is not linked to an active license.';
  end if;
  if length(trim(coalesce(p->>'visitor_name',''))) = 0 then raise exception 'Please enter your name.'; end if;
  if length(trim(coalesce(p->>'purpose',''))) = 0 then raise exception 'Please choose the purpose of your visit.'; end if;
  if length(coalesce(p->>'signature','')) < 50 then raise exception 'Please sign in the box.'; end if;
  if coalesce((p->>'gmp_ack')::boolean, false) is not true then raise exception 'Please confirm you have read and will follow the GMP rules.'; end if;
  if not (p ? 'ill') or jsonb_typeof(p->'ill') <> 'boolean' then raise exception 'Please answer the illness question.'; end if;
  v_id := 'vis-' || to_char(clock_timestamp(), 'YYMMDDHH24MISSMS') || substr(md5(random()::text), 1, 4);
  insert into hx_visitor_log(id, state_id, license_id, visitor_name, company, purpose, host, vehicle, signature, source, gmp_ack, ill, ack_at)
  values (v_id, l.state_id, l.id, left(trim(p->>'visitor_name'),120), left(trim(coalesce(p->>'company','')),120), left(p->>'purpose',80),
          left(trim(coalesce(p->>'host','')),120), left(trim(coalesce(p->>'vehicle','')),30), p->>'signature', 'kiosk', true, (p->>'ill')::boolean, now());
  return v_id;
end $$;
grant execute on function hx_kiosk_visitor_in2(text, jsonb) to anon, authenticated;

-- ---------- roles ----------
alter table hx_roles add column if not exists requirements text not null default '';

-- ---------- label templates ----------
alter table hx_label_templates add column if not exists allergens text not null default '';

-- ---------- testing: retention samples ----------
alter table hx_tests add column if not exists retention_qty text not null default '';
alter table hx_tests add column if not exists retention_location text not null default '';
alter table hx_tests add column if not exists retention_until date;

-- ---------- sticker print log ----------
create table if not exists hx_label_prints (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  test_id       text references hx_tests(id),
  template_id   text,
  batch_number  text not null default '',
  tag           text not null default '',
  sku           text not null default '',
  flavor        text not null default '',
  count         int  not null check (count > 0 and count <= 5000),
  start_pos     int  not null default 1,
  printed_by    text not null default '',
  created_by    uuid default auth.uid(),
  created_at    timestamptz not null default now()
);
create index if not exists hx_label_prints_lic on hx_label_prints(license_id, created_at desc);
create index if not exists hx_label_prints_test on hx_label_prints(test_id);

create or replace function hx_label_print_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_lic text;
begin
  if tg_op <> 'INSERT' then raise exception 'Sticker print records cannot be changed or deleted.'; end if;
  if new.test_id is not null then
    select license_id into v_lic from hx_tests where id = new.test_id;
    if v_lic is distinct from new.license_id then raise exception 'That testing record belongs to a different license.'; end if;
  end if;
  new.created_at := now(); new.created_by := auth.uid();
  perform set_config('hx.reason', 'Stickers printed', true);
  return new;
end $$;
drop trigger if exists hx_label_prints_guard on hx_label_prints;
create trigger hx_label_prints_guard before insert or update or delete on hx_label_prints for each row execute function hx_label_print_guard();
drop trigger if exists hx_label_prints_place on hx_label_prints;
create trigger hx_label_prints_place before insert on hx_label_prints for each row execute function hx_fl_guard();
drop trigger if exists hx_label_prints_audit on hx_label_prints;
create trigger hx_label_prints_audit after insert on hx_label_prints for each row execute function hx_audit();

alter table hx_label_prints enable row level security;
drop policy if exists hx_label_prints_read on hx_label_prints;
drop policy if exists hx_label_prints_insert on hx_label_prints;
create policy hx_label_prints_read   on hx_label_prints for select to authenticated using (hx_can('stickers',1,license_id));
create policy hx_label_prints_insert on hx_label_prints for insert to authenticated with check (hx_can('stickers',1,license_id));
grant select, insert on hx_label_prints to authenticated;

notify pgrst, 'reload schema';
