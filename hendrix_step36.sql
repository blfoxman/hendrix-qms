-- =====================================================================
-- Hendrix QMS  -  Step 36: Production Line Map
-- A live "subway map" of production for general managers and executives:
-- every batch of the license sits at its real station (plan, line clearance,
-- the sections of its batch record, lab testing, QC release, labels,
-- shipped) and is shown as STOPPED with the reason when Hendrix sees:
--   * an open hold on the batch                         (Hold and Release)
--   * a failed test with no later passing test           (Testing)
--   * batch status QC Hold or Failed                     (Batch Tracker)
--   * no line clearance, or the last one not cleared     (Line Clearance)
--   * equipment of its line clearance out of service or
--     past its calibration date                          (Equipment)
--   * an open deviation raised from the batch            (QMS)
--   * a CCP reading out of limits not yet verified       (HACCP)
--   * no update for the license's idle time (default 4 h) (Settings)
--
-- The map reads all of this through ONE function, hx_line_map(license),
-- so a person needs only the new access module 'linemap' (View) for that
-- license - not access to every module behind it. The function returns
-- only what the map shows (no costs, no files, no personal data beyond
-- names already on the records).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-34.
-- Safe to run more than once.
-- =====================================================================

-- ---------- idle time per license (Settings > Time clock / Line Map) ----------
alter table hx_license_settings add column if not exists linemap_idle_hours int not null default 4;
do $$ begin
  if not exists (select 1 from pg_constraint where conname = 'hx_license_settings_idle_chk') then
    alter table hx_license_settings add constraint hx_license_settings_idle_chk check (linemap_idle_hours between 1 and 72);
  end if;
end $$;

-- ---------- the bridge: one call returns everything the map needs ----------
create or replace function hx_line_map(p_lic text, p_days int default 45) returns jsonb
language plpgsql stable security definer set search_path = public as $$
declare
  v_lic   record;
  v_idle  int;
  v_since timestamptz;
  v_out   jsonb;
begin
  if p_lic is null or not hx_can('linemap', 1, p_lic) then
    raise exception 'You need access to the Line Map for this license.';
  end if;
  select l.id, l.name, l.license_number, l.state_id into v_lic from hx_licenses l where l.id = p_lic;
  if v_lic.id is null then raise exception 'Unknown license.'; end if;
  select s.linemap_idle_hours into v_idle from hx_license_settings s where s.license_id = p_lic;
  v_idle  := coalesce(v_idle, 4);
  v_since := now() - make_interval(days => greatest(7, least(coalesce(p_days, 45), 180)));

  select jsonb_build_object(
    'now', now(),
    'idle_hours', v_idle,
    'license', jsonb_build_object('id', v_lic.id, 'name', v_lic.name, 'license_number', v_lic.license_number),
    'batches', coalesce((
      select jsonb_agg(x order by x->>'created_at') from (
        select jsonb_build_object(
          'id', b.id, 'batch_type', b.batch_type, 'batch_number', b.batch_number, 'sku', b.sku, 'flavor', b.flavor,
          'status', b.status, 'data', b.data - 'notes', 'performed_by', b.performed_by,
          'created_at', b.created_at, 'updated_at', b.updated_at,
          'tests', coalesce((select jsonb_agg(jsonb_build_object('id', t.id, 'status', t.status, 'tag', t.tag, 'lab_name', t.lab_name,
                      'submitted_at', t.submitted_at, 'result_at', t.result_at, 'created_at', t.created_at, 'updated_at', t.updated_at) order by t.created_at)
                    from hx_tests t where t.batch_id = b.id and not t.voided), '[]'::jsonb),
          'holds', coalesce((select jsonb_agg(jsonb_build_object('id', h.id, 'number', h.number, 'reason', h.reason, 'status', h.status,
                      'created_at', h.created_at, 'placed_by', h.placed_by, 'decided_at', h.decided_at) order by h.created_at)
                    from hx_holds h where h.batch_id = b.id), '[]'::jsonb),
          'clearances', coalesce((select jsonb_agg(jsonb_build_object('id', c.id, 'number', c.number, 'result', c.result, 'area', c.area,
                      'equipment_ids', to_jsonb(c.equipment_ids), 'issues', c.issues, 'recorded_by', c.recorded_by, 'created_at', c.created_at) order by c.created_at)
                    from hx_line_clearances c where c.batch_id = b.id and not c.voided), '[]'::jsonb),
          'deviations', coalesce((select jsonb_agg(jsonb_build_object('id', d.id, 'number', d.number, 'title', d.title, 'status', d.status,
                      'owner_name', d.owner_name, 'created_at', d.created_at) order by d.created_at)
                    from hx_deviations d where d.source_type = 'batch' and d.source_id = b.id and d.status in ('open', 'in_progress')), '[]'::jsonb),
          'ccp_out', coalesce((select jsonb_agg(jsonb_build_object('id', m.id, 'ccp_name', m.ccp_name, 'value', m.value, 'created_at', m.created_at) order by m.created_at)
                    from hx_haccp_monitoring m where m.batch_id = b.id and not m.voided and not m.within_limits and m.verified_at is null), '[]'::jsonb),
          'labels', (select jsonb_build_object('count', count(*), 'last_at', max(lp.created_at))
                    from hx_label_prints lp where lp.license_id = b.license_id and lower(trim(lp.batch_number)) = lower(trim(b.batch_number))),
          'shipments', coalesce((select jsonb_agg(jsonb_build_object('id', s.id, 'number', s.number, 'customer', s.customer, 'ship_date', s.ship_date,
                      'status', s.status, 'created_at', s.created_at) order by s.created_at)
                    from hx_shipments s where s.license_id = b.license_id and s.status in ('shipped', 'delivered')
                      and exists (select 1 from jsonb_array_elements(s.items) it where it->>'batch_id' = b.id)), '[]'::jsonb),
          'last_activity', greatest(b.updated_at,
                    (select max(c.created_at) from hx_line_clearances c where c.batch_id = b.id),
                    (select max(t.updated_at) from hx_tests t where t.batch_id = b.id),
                    (select max(m.created_at) from hx_haccp_monitoring m where m.batch_id = b.id))
        ) x
        from hx_batches b
        where b.license_id = p_lic and not b.voided and b.created_at >= v_since
      ) q), '[]'::jsonb),
    'equipment_issues', coalesce((
      select jsonb_agg(jsonb_build_object('id', e.id, 'number', e.number, 'name', e.name, 'status', e.status, 'cal_due', e.cal_due,
               'issue', case when e.status <> 'in_service' then 'out of service'
                             else 'past its calibration date (' || to_char(e.cal_due, 'Mon DD') || ')' end))
      from hx_equipment e
      where e.license_id = p_lic and (e.status <> 'in_service' or (e.cal_required and e.cal_due is not null and e.cal_due < current_date))), '[]'::jsonb),
    'plans', coalesce((
      select jsonb_agg(jsonb_build_object('id', pp.id, 'number', pp.number, 'product_type', pp.product_type, 'sku_name', pp.sku_name,
               'planned_for', pp.planned_for, 'units_per_flavor', pp.units_per_flavor, 'status', pp.status, 'created_at', pp.created_at,
               'flavors', coalesce((select jsonb_agg(li->>'flavor') from jsonb_array_elements(pp.lines) li where coalesce(li->>'flavor', '') <> ''), '[]'::jsonb))
             order by pp.planned_for nulls last, pp.created_at)
      from hx_production_plans pp where pp.license_id = p_lic and pp.status = 'planned'), '[]'::jsonb),
    'on_floor', (
      select count(*) from (
        select distinct on (tc.profile_id) tc.event_type, tc.ts
        from hx_time_clock tc
        where tc.license_id = p_lic and not tc.voided and tc.ts > now() - interval '16 hours'
        order by tc.profile_id, tc.ts desc
      ) z where z.event_type <> 'clockout')
  ) into v_out;
  return v_out;
end $$;

revoke all on function hx_line_map(text, int) from public, anon;
grant execute on function hx_line_map(text, int) to authenticated;

notify pgrst, 'reload schema';
select 'Hendrix step 36 (Production Line Map) installed' as result;
