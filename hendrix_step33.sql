-- =====================================================================
-- Hendrix QMS  -  Step 33: Production Planner (from Black Fox / Michigan)
-- Same calculator as Black Fox: product type, SKU, flavors, units per
-- flavor, extra instructions ("5% waste buffer"):
--   * flavors with a saved formulation (Formulation Bank) are calculated
--     exactly from the recipe's reference batch; a SKU's base recipe covers
--     every flavor (the terpene is named per flavor)
--   * only flavors with no recipe at all go to the AI (hendrix-ai, module
--     'planner')
--   * per-flavor ingredients, grand total for the run, production worksheet
--     PDFs with the tracking blanks and signatures
-- Hendrix adds:
--   * plans are saved (PP-YYYY-###) with the date they are planned for;
--     batches made from the plan (Batch Tracker, "Start batch") show on it
--   * the grand total is checked against accepted inventory (Receiving)
--   * formulations stay private to the Formulation Bank: the planner reads
--     ingredient names and amounts only (no costs) through a function
-- Access module 'planner': View / Edit (plan, save, start batches) / Full
-- (cancel plans).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-32.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_production_plans (
  id               text primary key,
  state_id         text not null references hx_states(id),
  license_id       text not null references hx_licenses(id),
  number           text not null default '',
  product_type     text not null,
  sku_id           text references hx_skus(id),
  sku_name         text not null default '',
  planned_for      date not null default current_date,
  units_per_flavor int  not null check (units_per_flavor > 0),
  instructions     text not null default '',
  lines            jsonb not null default '[]'::jsonb,
  grand_total      jsonb not null default '[]'::jsonb,
  status           text not null default 'planned' check (status in ('planned','in_progress','completed','cancelled')),
  close_note       text,
  created_by       text not null default '',
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);
create unique index if not exists hx_production_plans_number on hx_production_plans(license_id, number);

create or replace function hx_plan_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then raise exception 'Plans are never deleted. Cancel the plan with a reason.'; end if;
  if tg_op = 'INSERT' then
    new.number := hx_next_number('hx_production_plans', new.license_id, 'PP');
    new.created_by := coalesce(hx_me(), ''); new.created_at := now(); new.status := 'planned'; new.close_note := null;
    perform set_config('hx.reason', 'Production plan saved', true);
  else
    new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
    if old.status in ('completed','cancelled') then raise exception 'This plan is %.', old.status; end if;
    if (new.product_type, new.sku_id, new.units_per_flavor, new.lines, new.grand_total) is distinct from (old.product_type, old.sku_id, old.units_per_flavor, old.lines, old.grand_total)
       and old.status <> 'planned' then
      raise exception 'Production has started on this plan. Cancel it and make a new plan to change the amounts.';
    end if;
    if new.status = 'cancelled' then
      if not hx_can('planner', 3, new.license_id) then raise exception 'Only Full access can cancel a plan.'; end if;
      if coalesce(trim(new.close_note), '') = '' then raise exception 'A reason is required to cancel a plan.'; end if;
      perform set_config('hx.reason', 'Plan cancelled: ' || trim(new.close_note), true);
    elsif new.status <> old.status then
      perform set_config('hx.reason', 'Plan ' || replace(new.status, '_', ' '), true);
    end if;
  end if;
  if jsonb_typeof(new.lines) <> 'array' or jsonb_array_length(new.lines) = 0 then raise exception 'Calculate the plan first (no flavors).'; end if;
  if new.sku_id is not null and not exists (select 1 from hx_skus s join hx_licenses l on l.id = new.license_id where s.id = new.sku_id and s.state_id = l.state_id) then
    raise exception 'That SKU belongs to another state.';
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_production_plans_guard on hx_production_plans;
create trigger hx_production_plans_guard before insert or update or delete on hx_production_plans for each row execute function hx_plan_guard();
drop trigger if exists hx_production_plans_place on hx_production_plans;
create trigger hx_production_plans_place before insert or update on hx_production_plans for each row execute function hx_fl_guard();
drop trigger if exists hx_production_plans_audit on hx_production_plans;
create trigger hx_production_plans_audit after insert or update on hx_production_plans for each row execute function hx_audit();

alter table hx_production_plans enable row level security;
drop policy if exists hx_production_plans_read on hx_production_plans;
drop policy if exists hx_production_plans_insert on hx_production_plans;
drop policy if exists hx_production_plans_update on hx_production_plans;
create policy hx_production_plans_read   on hx_production_plans for select to authenticated using (hx_can('planner',1,license_id));
create policy hx_production_plans_insert on hx_production_plans for insert to authenticated with check (hx_can('planner',2,license_id));
create policy hx_production_plans_update on hx_production_plans for update to authenticated using (hx_can('planner',2,license_id)) with check (hx_can('planner',2,license_id));
grant select, insert, update on hx_production_plans to authenticated;

-- recipe ingredients for the planner: names and amounts only, never costs, packaging or labor
create or replace function hx_planner_recipes(p_lic text, p_sku text) returns json
language plpgsql stable security definer set search_path = public as $$
begin
  if not (hx_can('planner', 1, p_lic) or hx_can('formbank', 1, p_lic)) then raise exception 'No access to the Production Planner at this license.'; end if;
  return coalesce((select json_agg(json_build_object('flavor_id', f.flavor_id, 'name', f.name, 'batch_size', f.batch_size,
            'raw_materials', coalesce((select json_agg(json_build_object('name', m->>'name', 'qty', m->>'qty', 'unit', coalesce(nullif(m->>'unit',''),'g')))
                                         from jsonb_array_elements(f.raw_materials) m where coalesce(trim(m->>'name'),'') <> ''), '[]'::json)))
     from hx_formulations f join hx_skus s on s.id = f.sku_id join hx_licenses l on l.id = p_lic
    where f.sku_id = p_sku and s.state_id = l.state_id), '[]'::json);
end $$;
revoke all on function hx_planner_recipes(text,text) from public;
grant execute on function hx_planner_recipes(text,text) to authenticated;

notify pgrst, 'reload schema';
