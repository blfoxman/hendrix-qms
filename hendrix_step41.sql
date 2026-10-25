-- =====================================================================
-- Hendrix QMS  -  Step 41: METRC check (reconciliation)
--
--   Compares what METRC says about a license's packages with what Hendrix
--   knows, and lists every difference to fix:
--     * lab status: Hendrix has a passing test but METRC does not say
--       TestPassed (or METRC says failed while Hendrix has no failed test);
--     * holds: on hold in METRC but no open Hendrix hold, or the other way;
--     * shipped in Hendrix but the package is still active in METRC;
--     * accepted lots in Hendrix that METRC no longer lists, and lots whose
--       quantity left in Hendrix differs from METRC (same unit, > 2 %);
--     * active METRC packages Hendrix does not know at all (for information).
--   The METRC side comes from a METRC export (Packages > Active > Export CSV)
--   uploaded in METRC Check, or straight from the METRC API through the Edge
--   Function "hendrix-metrc" when the METRC keys are set. Each upload is kept
--   (hx_metrc_snapshots / hx_metrc_packages) so a check can be shown again.
--   Tags are compared without spaces or dashes, any case.
--
-- Access module 'metrc': View = see checks, Edit = upload / fetch and check.
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-40.
-- Safe to run more than once.
-- =====================================================================

create or replace function hx_tagkey(p text) returns text
language sql immutable as $$ select upper(regexp_replace(coalesce(p, ''), '[^A-Za-z0-9]', '', 'g')) $$;

create table if not exists hx_metrc_snapshots (
  id           text primary key,
  state_id     text not null references hx_states(id),
  license_id   text not null references hx_licenses(id),
  source       text not null default 'csv' check (source in ('csv', 'api')),
  file_name    text not null default '',
  packages     int not null default 0,
  taken_by     text not null default '',
  taken_by_id  uuid,
  created_at   timestamptz not null default now()
);
create index if not exists hx_metrc_snapshots_lic on hx_metrc_snapshots(license_id, created_at desc);
create table if not exists hx_metrc_packages (
  snapshot_id    text not null references hx_metrc_snapshots(id) on delete cascade,
  tag            text not null,
  tag_key        text not null,
  item           text not null default '',
  category       text not null default '',
  quantity       numeric,
  unit           text not null default '',
  lab_state      text not null default '',
  on_hold        boolean not null default false,
  packaged_date  date,
  batch_no       text not null default '',
  location       text not null default '',
  primary key (snapshot_id, tag_key)
);
alter table hx_metrc_snapshots enable row level security;
alter table hx_metrc_packages enable row level security;
drop policy if exists hx_metrc_snapshots_read on hx_metrc_snapshots;
create policy hx_metrc_snapshots_read on hx_metrc_snapshots for select to authenticated using (hx_lic_ok(license_id) and hx_perm('metrc') >= 1);
drop policy if exists hx_metrc_packages_read on hx_metrc_packages;
create policy hx_metrc_packages_read on hx_metrc_packages for select to authenticated
  using (exists (select 1 from hx_metrc_snapshots s where s.id = snapshot_id and hx_lic_ok(s.license_id) and hx_perm('metrc') >= 1));
revoke all on hx_metrc_snapshots, hx_metrc_packages from anon;
grant select on hx_metrc_snapshots, hx_metrc_packages to authenticated;

-- save what METRC says (from the CSV export or the API); rows: [{tag,item,category,quantity,unit,lab_state,on_hold,packaged_date,batch_no,location}]
create or replace function hx_metrc_save(p_lic text, p_source text, p_file text, p_rows jsonb) returns text
language plpgsql volatile security definer set search_path = public as $$
declare v_id text; v_state text; n int; me record;
begin
  if not hx_lic_ok(p_lic) or hx_perm('metrc') < 2 then raise exception 'You need Edit access to METRC Check at this license.'; end if;
  if jsonb_typeof(p_rows) <> 'array' or jsonb_array_length(p_rows) = 0 then raise exception 'No METRC packages found in the file.'; end if;
  if jsonb_array_length(p_rows) > 20000 then raise exception 'Too many packages in one file (more than 20,000).'; end if;
  select state_id into v_state from hx_licenses where id = p_lic;
  select * into me from hx_profiles where id::text = auth.uid()::text;
  v_id := 'ms-' || to_char(clock_timestamp(), 'YYMMDDHH24MISS') || substr(md5(random()::text), 1, 6);
  insert into hx_metrc_snapshots(id, state_id, license_id, source, file_name, taken_by, taken_by_id)
    values (v_id, v_state, p_lic, case when p_source = 'api' then 'api' else 'csv' end, left(coalesce(p_file, ''), 200), coalesce(me.name, ''), me.id);
  insert into hx_metrc_packages(snapshot_id, tag, tag_key, item, category, quantity, unit, lab_state, on_hold, packaged_date, batch_no, location)
    select distinct on (hx_tagkey(r ->> 'tag')) v_id, left(trim(r ->> 'tag'), 60), hx_tagkey(r ->> 'tag'), left(coalesce(r ->> 'item', ''), 200), left(coalesce(r ->> 'category', ''), 100),
           case when coalesce(r ->> 'quantity', '') ~ '^-?[0-9]+(\.[0-9]+)?$' then (r ->> 'quantity')::numeric end, left(coalesce(r ->> 'unit', ''), 30),
           left(coalesce(r ->> 'lab_state', ''), 60), coalesce((r ->> 'on_hold')::boolean, false),
           case when coalesce(r ->> 'packaged_date', '') ~ '^\d{4}-\d{2}-\d{2}' then left(r ->> 'packaged_date', 10)::date end,
           left(coalesce(r ->> 'batch_no', ''), 100), left(coalesce(r ->> 'location', ''), 100)
    from jsonb_array_elements(p_rows) r where hx_tagkey(r ->> 'tag') <> '';
  get diagnostics n = row_count;
  if n = 0 then raise exception 'No METRC package tags found in the file.'; end if;
  update hx_metrc_snapshots set packages = n where id = v_id;
  return v_id;
end $$;
revoke all on function hx_metrc_save(text, text, text, jsonb) from public, anon;
grant execute on function hx_metrc_save(text, text, text, jsonb) to authenticated;

-- the differences between a METRC snapshot and Hendrix
create or replace function hx_metrc_reconcile(p_snapshot text) returns jsonb
language plpgsql stable security definer set search_path = public as $$
declare s record; v jsonb := '[]'::jsonb;
begin
  select * into s from hx_metrc_snapshots where id = p_snapshot;
  if s.id is null or not hx_lic_ok(s.license_id) or hx_perm('metrc') < 1 then raise exception 'METRC check not found.'; end if;

  -- lab status
  v := v || coalesce((select jsonb_agg(jsonb_build_object('kind', 'lab', 'severity', case when t.status = 'Passed' then 'high' else 'medium' end, 'tag', m.tag,
          'title', case when t.status = 'Passed' then 'Passed in Hendrix, METRC lab status is ' || coalesce(nullif(m.lab_state, ''), 'empty')
                        else 'METRC says ' || m.lab_state || ', Hendrix test is ' || t.status end,
          'detail', trim(coalesce(m.item, '') || coalesce(' · batch ' || nullif(t.batch_number, ''), '')), 'page', 'testing', 'ref', t.id))
      from hx_metrc_packages m
      join lateral (select * from hx_tests x where x.license_id = s.license_id and not x.voided and hx_tagkey(x.tag) = m.tag_key order by x.created_at desc limit 1) t on true
      where m.snapshot_id = s.id
        and ((t.status = 'Passed' and m.lab_state !~* 'passed')
          or (m.lab_state ~* 'failed' and t.status not in ('Failed', 'Retest')))), '[]'::jsonb);

  -- holds
  v := v || coalesce((select jsonb_agg(jsonb_build_object('kind', 'hold', 'severity', 'high', 'tag', m.tag, 'title', 'On hold in METRC, no open hold in Hendrix',
          'detail', m.item, 'page', 'holds', 'ref', ''))
      from hx_metrc_packages m where m.snapshot_id = s.id and m.on_hold
        and not exists (select 1 from hx_holds h where h.license_id = s.license_id and h.status = 'open' and hx_tagkey(h.tag) = m.tag_key)), '[]'::jsonb);
  v := v || coalesce((select jsonb_agg(jsonb_build_object('kind', 'hold', 'severity', 'high', 'tag', m.tag, 'title', 'Open hold ' || h.number || ' in Hendrix, not on hold in METRC',
          'detail', coalesce(h.reason, ''), 'page', 'holds', 'ref', h.id))
      from hx_holds h join hx_metrc_packages m on m.snapshot_id = s.id and m.tag_key = hx_tagkey(h.tag)
      where h.license_id = s.license_id and h.status = 'open' and h.tag <> '' and not m.on_hold), '[]'::jsonb);

  -- shipped in Hendrix, still active in METRC
  v := v || coalesce((select jsonb_agg(jsonb_build_object('kind', 'shipped', 'severity', 'medium', 'tag', m.tag,
          'title', 'Shipped in Hendrix (' || to_char(sh.ship_date, 'Mon DD') || '), still active in METRC', 'detail', coalesce(m.item, '') || ' · check the METRC transfer', 'page', 'shipping', 'ref', sh.id))
      from hx_metrc_packages m
      join lateral (select x.* from hx_shipments x, jsonb_array_elements(x.items) it where x.license_id = s.license_id and x.status <> 'cancelled'
                     and hx_tagkey(it ->> 'tag') = m.tag_key and x.ship_date < current_date order by x.ship_date desc limit 1) sh on true
      where m.snapshot_id = s.id), '[]'::jsonb);

  -- lots: missing from METRC, or a different quantity left
  v := v || coalesce((select jsonb_agg(jsonb_build_object('kind', 'lot', 'severity', 'medium', 'tag', l.metrc_tag,
          'title', 'Lot ' || l.number || ' has ' || trim(to_char(l.quantity - coalesce(l.qty_used, 0), 'FM999999990.###')) || ' ' || l.unit || ' left in Hendrix, not active in METRC',
          'detail', l.item, 'page', 'receiving', 'ref', l.id))
      from hx_lots l where l.license_id = s.license_id and l.status = 'accepted' and l.metrc_tag <> '' and l.quantity - coalesce(l.qty_used, 0) > 0
        and not exists (select 1 from hx_metrc_packages m where m.snapshot_id = s.id and m.tag_key = hx_tagkey(l.metrc_tag))), '[]'::jsonb);
  v := v || coalesce((select jsonb_agg(jsonb_build_object('kind', 'quantity', 'severity', 'low', 'tag', m.tag,
          'title', 'Quantity: Hendrix ' || trim(to_char(l.quantity - coalesce(l.qty_used, 0), 'FM999999990.###')) || ' ' || l.unit || ', METRC ' || trim(to_char(m.quantity, 'FM999999990.###')) || ' ' || m.unit,
          'detail', 'Lot ' || l.number || ' · ' || l.item, 'page', 'receiving', 'ref', l.id))
      from hx_lots l join hx_metrc_packages m on m.snapshot_id = s.id and m.tag_key = hx_tagkey(l.metrc_tag)
      where l.license_id = s.license_id and l.status = 'accepted' and l.metrc_tag <> '' and m.quantity is not null
        and lower(regexp_replace(m.unit, '[^A-Za-z]', '', 'g')) in (lower(regexp_replace(l.unit, '[^A-Za-z]', '', 'g')),
              case lower(l.unit) when 'g' then 'grams' when 'kg' then 'kilograms' when 'ea' then 'each' when 'ml' then 'milliliters' else '-' end)
        and abs((l.quantity - coalesce(l.qty_used, 0)) - m.quantity) > greatest(0.02 * m.quantity, 0.001)), '[]'::jsonb);

  -- METRC packages Hendrix does not know (for information)
  v := v || coalesce((select jsonb_agg(jsonb_build_object('kind', 'unknown', 'severity', 'info', 'tag', m.tag, 'title', 'In METRC, not in Hendrix',
          'detail', trim(coalesce(m.item, '') || coalesce(' · ' || nullif(m.batch_no, ''), '')), 'page', '', 'ref', ''))
      from hx_metrc_packages m where m.snapshot_id = s.id
        and not exists (select 1 from hx_tests t where t.license_id = s.license_id and (hx_tagkey(t.tag) = m.tag_key or hx_tagkey(t.sample_tag) = m.tag_key))
        and not exists (select 1 from hx_lots l where l.license_id = s.license_id and hx_tagkey(l.metrc_tag) = m.tag_key)
        and not exists (select 1 from hx_holds h where h.license_id = s.license_id and hx_tagkey(h.tag) = m.tag_key)
        and not exists (select 1 from hx_shipments x, jsonb_array_elements(x.items) it where x.license_id = s.license_id and hx_tagkey(it ->> 'tag') = m.tag_key)), '[]'::jsonb);

  return jsonb_build_object('snapshot', jsonb_build_object('id', s.id, 'source', s.source, 'file_name', s.file_name, 'packages', s.packages, 'taken_by', s.taken_by, 'created_at', s.created_at),
    'findings', coalesce((select jsonb_agg(f order by case f ->> 'severity' when 'high' then 0 when 'medium' then 1 when 'low' then 2 else 3 end, f ->> 'kind', f ->> 'tag') from jsonb_array_elements(v) f), '[]'::jsonb));
end $$;
revoke all on function hx_metrc_reconcile(text) from public, anon;
grant execute on function hx_metrc_reconcile(text) to authenticated;

drop trigger if exists hx_metrc_snapshots_audit on hx_metrc_snapshots;
create trigger hx_metrc_snapshots_audit after insert or update or delete on hx_metrc_snapshots for each row execute function hx_audit();

notify pgrst, 'reload schema';
select 'Hendrix step 41 (METRC check) installed' as result;
