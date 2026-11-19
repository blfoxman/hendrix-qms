-- =====================================================================
-- Hendrix QMS  -  Step 60: METRC -> Hendrix cannabis inventory sync
--
--   * hx_metrc_inventory_sync(license, rows, source): the active METRC packages of a license
--     (read from METRC in the browser every few minutes) update the on-hand quantity of the
--     Hendrix lots with the same METRC tag (count recorded, unit converted g / kg / lb / oz / mg,
--     each), and their location. A tagged lot that is no longer active in METRC goes to 0 on hand
--     (only when the list is complete and most tagged lots were found, so a partial read never
--     empties the inventory). METRC packages that are not in Hendrix are counted and listed in
--     METRC Check. Nothing is ever written to METRC.
--   * Full access to Receiving at that license. Every change is a lot count in the Audit Trail.
--   * hx_metrc_syncs: one row per sync (when, by whom, what changed). A METRC Check snapshot is
--     kept at most once an hour; automatic snapshots older than 14 days are removed.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-59.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_metrc_syncs (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  source        text not null default '',
  packages      int not null default 0,
  matched       int not null default 0,
  counted       int not null default 0,
  zeroed        int not null default 0,
  moved         int not null default 0,
  not_in_hendrix int not null default 0,
  skipped       jsonb not null default '[]'::jsonb,
  snapshot_id   text,
  synced_by     text not null default '',
  synced_by_id  uuid,
  created_at    timestamptz not null default now()
);
create index if not exists hx_metrc_syncs_lic on hx_metrc_syncs(license_id, created_at desc);
alter table hx_metrc_syncs enable row level security;
drop policy if exists hx_metrc_syncs_read on hx_metrc_syncs;
create policy hx_metrc_syncs_read on hx_metrc_syncs for select to authenticated using (hx_can('receiving', 1, license_id));
revoke all on hx_metrc_syncs from anon;
grant select on hx_metrc_syncs to authenticated;

-- grams per unit (weights) or 'each'
create or replace function hx_unit_g(p_unit text) returns numeric
language sql immutable as $$
  select case lower(regexp_replace(coalesce(p_unit, ''), '[^A-Za-z]', '', 'g'))
    when 'g' then 1 when 'gram' then 1 when 'grams' then 1 when 'gr' then 1
    when 'mg' then 0.001 when 'milligram' then 0.001 when 'milligrams' then 0.001
    when 'kg' then 1000 when 'kilogram' then 1000 when 'kilograms' then 1000
    when 'lb' then 453.59237 when 'lbs' then 453.59237 when 'pound' then 453.59237 when 'pounds' then 453.59237
    when 'oz' then 28.349523125 when 'ounce' then 28.349523125 when 'ounces' then 28.349523125
    else null end;
$$;
create or replace function hx_unit_each(p_unit text) returns boolean
language sql immutable as $$
  select lower(regexp_replace(coalesce(p_unit, ''), '[^A-Za-z]', '', 'g')) in ('ea', 'each', 'unit', 'units', 'pc', 'pcs', 'piece', 'pieces', 'count', 'ct');
$$;

create or replace function hx_metrc_inventory_sync(p_lic text, p_rows jsonb, p_source text default '', p_complete boolean default true) returns jsonb
language plpgsql volatile security definer set search_path = public as $$
declare l record; m record; v_lic record; v_me text := coalesce(hx_me(), ''); v_src text := left(coalesce(nullif(trim(p_source), ''), 'METRC'), 120);
  v_q numeric; v_left numeric; v_g numeric; v_lg numeric; v_tagged int := 0; v_matched int := 0; v_counted int := 0; v_zeroed int := 0; v_moved int := 0; v_new int := 0;
  v_skip jsonb := '[]'::jsonb; v_snap text; v_id text; v_loc text;
begin
  select * into v_lic from hx_licenses where id = p_lic;
  if v_lic.id is null then raise exception 'Unknown license.'; end if;
  if not hx_can('receiving', 3, p_lic) then raise exception 'The METRC inventory sync needs Full access to Receiving for this license.'; end if;
  if jsonb_typeof(p_rows) <> 'array' then raise exception 'No METRC packages were sent.'; end if;
  if jsonb_array_length(p_rows) > 30000 then raise exception 'Too many packages in one sync (more than 30,000).'; end if;

  create temp table if not exists hx_tmp_metrc (tag_key text primary key, tag text, qty numeric, unit text, item text, category text, location text, lab text, on_hold boolean, packaged date) on commit drop;
  truncate hx_tmp_metrc;
  insert into hx_tmp_metrc
    select distinct on (hx_tagkey(r->>'tag')) hx_tagkey(r->>'tag'), left(trim(r->>'tag'), 60),
           case when coalesce(r->>'qty', '') ~ '^-?[0-9]+(\.[0-9]+)?$' then (r->>'qty')::numeric end, coalesce(r->>'unit', ''),
           left(coalesce(r->>'item', ''), 200), left(coalesce(r->>'category', ''), 100), left(coalesce(r->>'location', ''), 100), left(coalesce(r->>'lab', ''), 60),
           coalesce((r->>'on_hold')::boolean, false), case when coalesce(r->>'packaged', '') ~ '^\d{4}-\d{2}-\d{2}' then left(r->>'packaged', 10)::date end
    from jsonb_array_elements(p_rows) r where hx_tagkey(r->>'tag') <> '';

  select count(*) into v_tagged from hx_lots where license_id = p_lic and trim(metrc_tag) <> '' and status not in ('rejected', 'returned', 'destroyed') and quantity - qty_used > 0;

  perform set_config('hx.internal', 'on', true);
  for l in select * from hx_lots where license_id = p_lic and trim(metrc_tag) <> '' and status not in ('rejected', 'returned', 'destroyed') order by received_on, number for update loop
    select * into m from hx_tmp_metrc where tag_key = hx_tagkey(l.metrc_tag);
    v_left := l.quantity - l.qty_used;
    if m.tag_key is null then continue; end if;
    v_matched := v_matched + 1;
    -- METRC quantity in the lot's unit
    v_g := hx_unit_g(m.unit); v_lg := hx_unit_g(l.unit);
    if m.qty is null then v_q := null;
    elsif v_g is not null and v_lg is not null then v_q := round(m.qty * v_g / v_lg, 4);
    elsif hx_unit_each(m.unit) and hx_unit_each(l.unit) then v_q := m.qty;
    elsif lower(m.unit) = lower(l.unit) then v_q := m.qty;
    else v_q := null; v_skip := v_skip || jsonb_build_object('lot', l.number, 'tag', l.metrc_tag, 'why', 'METRC counts in ' || m.unit || ', the lot in ' || l.unit);
    end if;
    if v_q is not null and v_q > l.quantity then
      v_skip := v_skip || jsonb_build_object('lot', l.number, 'tag', l.metrc_tag, 'why', 'METRC has ' || m.qty || ' ' || m.unit || ', more than the ' || l.quantity || ' ' || l.unit || ' received');
      v_q := null;
    end if;
    if v_q is not null and round(v_q, 3) <> round(v_left, 3) then
      insert into hx_lot_counts(id, state_id, license_id, lot_id, before_qty, counted_qty, unit, source, notes, counted_by)
      values ('cnt-' || replace(gen_random_uuid()::text, '-', ''), l.state_id, l.license_id, l.id, v_left, v_q, l.unit, v_src, 'METRC: ' || m.qty || ' ' || m.unit, v_me);
      perform set_config('hx.reason', 'METRC sync: ' || v_left || ' -> ' || v_q || ' ' || l.unit, true);
      update hx_lots set qty_used = quantity - v_q where id = l.id;
      v_counted := v_counted + 1;
    end if;
    v_loc := trim(coalesce(m.location, ''));
    if v_loc <> '' and v_loc <> coalesce(l.location, '') then
      perform set_config('hx.reason', 'Location from METRC', true);
      update hx_lots set location = v_loc where id = l.id;
      v_moved := v_moved + 1;
    end if;
  end loop;

  -- no longer active in METRC: 0 on hand, only when the list is complete and most tagged lots were found
  if p_complete and v_tagged > 0 and v_matched * 2 >= v_tagged then
    for l in select * from hx_lots x where x.license_id = p_lic and trim(x.metrc_tag) <> '' and x.status not in ('rejected', 'returned', 'destroyed') and x.quantity - x.qty_used > 0
               and not exists (select 1 from hx_tmp_metrc t where t.tag_key = hx_tagkey(x.metrc_tag)) for update loop
      v_left := l.quantity - l.qty_used;
      insert into hx_lot_counts(id, state_id, license_id, lot_id, before_qty, counted_qty, unit, source, notes, counted_by)
      values ('cnt-' || replace(gen_random_uuid()::text, '-', ''), l.state_id, l.license_id, l.id, v_left, 0, l.unit, v_src, 'No longer active in METRC (used, finished or transferred)', v_me);
      perform set_config('hx.reason', 'METRC sync: not active in METRC, ' || v_left || ' -> 0 ' || l.unit, true);
      update hx_lots set qty_used = quantity where id = l.id;
      v_zeroed := v_zeroed + 1;
    end loop;
  elsif p_complete and v_tagged > 0 then
    v_skip := v_skip || jsonb_build_object('why', 'Only ' || v_matched || ' of ' || v_tagged || ' tagged lots were found in METRC, so nothing was set to 0. Check the METRC tags on the lots.');
  end if;
  perform set_config('hx.internal', '', true);

  select count(*) into v_new from hx_tmp_metrc t where not exists (select 1 from hx_lots x where x.license_id = p_lic and hx_tagkey(x.metrc_tag) = t.tag_key);

  -- METRC Check snapshot at most once an hour; automatic snapshots are kept 14 days
  if hx_perm('metrc') >= 2 and not exists (select 1 from hx_metrc_snapshots where license_id = p_lic and source = 'api' and created_at > now() - interval '1 hour') then
    begin
      v_snap := hx_metrc_save(p_lic, 'api', v_src, (select coalesce(jsonb_agg(jsonb_build_object('tag', tag, 'item', item, 'category', category, 'quantity', qty::text, 'unit', unit, 'lab_state', lab,
                  'on_hold', on_hold, 'packaged_date', packaged::text, 'location', location)), '[]'::jsonb) from hx_tmp_metrc));
      delete from hx_metrc_snapshots where license_id = p_lic and source = 'api' and created_at < now() - interval '14 days';
    exception when others then v_snap := null;
    end;
  end if;

  v_id := 'msy-' || replace(gen_random_uuid()::text, '-', '');
  insert into hx_metrc_syncs(id, state_id, license_id, source, packages, matched, counted, zeroed, moved, not_in_hendrix, skipped, snapshot_id, synced_by, synced_by_id)
  values (v_id, v_lic.state_id, p_lic, v_src, (select count(*) from hx_tmp_metrc), v_matched, v_counted, v_zeroed, v_moved, v_new, v_skip, v_snap, v_me, auth.uid());
  delete from hx_metrc_syncs where license_id = p_lic and created_at < now() - interval '30 days';
  return jsonb_build_object('id', v_id, 'packages', (select count(*) from hx_tmp_metrc), 'tagged_lots', v_tagged, 'matched', v_matched, 'counted', v_counted, 'zeroed', v_zeroed,
                            'moved', v_moved, 'not_in_hendrix', v_new, 'skipped', v_skip, 'snapshot', v_snap);
end $$;
revoke all on function hx_metrc_inventory_sync(text, jsonb, text, boolean) from public, anon;
grant execute on function hx_metrc_inventory_sync(text, jsonb, text, boolean) to authenticated;

notify pgrst, 'reload schema';
