-- =====================================================================
-- Hendrix QMS  -  Step 10: Compliance Stickers (label templates)
-- Black Fox compliance stickers: per-product label templates (approval number,
-- ingredients, instructions, warning, servings, weight) printed on Avery sheets
-- from a Testing record (COA results fill the cannabinoid mg per serving).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-9.
-- Safe to run more than once.
--
-- Rules built into the database:
--   * a template belongs to one state and one license (never movable)
--   * it is linked to a SKU of that same state; a flavor (optional) must be that SKU's
--   * one template per license + SKU + flavor ("any flavor" counts once)
-- Access module: 'stickers'  View = print, Edit = add / change templates, Full = delete.
-- =====================================================================

create table if not exists hx_label_templates (
  id              text primary key,
  state_id        text not null references hx_states(id),
  license_id      text not null references hx_licenses(id),
  sku_id          text not null references hx_skus(id) on delete cascade,
  flavor_id       text references hx_flavors(id) on delete cascade,
  name            text not null check (length(trim(name)) > 0),
  stock           text not null default 'avery-94202',
  layout          text not null default '' check (layout in ('','tri')),
  approval_number text not null default '',
  servings        text not null default '',
  weight          text not null default '',
  instructions    text not null default '',
  ingredients     text not null default '',
  warning         text not null default '',
  info_heading    text not null default 'MARIJUANA PRODUCT INFORMATION',
  approval_label  text not null default 'MARIJUANA PRODUCT APPROVAL NUMBER',
  results_heading text not null default 'TEST RESULTS (mg/serving):',
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
create unique index if not exists hx_label_templates_one on hx_label_templates(license_id, sku_id, coalesce(flavor_id, ''));

create or replace function hx_label_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_state text; v_fsku text;
begin
  select state_id into v_state from hx_skus where id = new.sku_id;
  if v_state is null then raise exception 'Unknown SKU.'; end if;
  if v_state <> new.state_id then raise exception 'That SKU belongs to a different state.'; end if;
  if new.flavor_id is not null then
    select sku_id into v_fsku from hx_flavors where id = new.flavor_id;
    if v_fsku is distinct from new.sku_id then raise exception 'That flavor belongs to a different SKU.'; end if;
  end if;
  new.updated_at := now();
  return new;
end $$;

drop trigger if exists hx_label_templates_guard on hx_label_templates;
create trigger hx_label_templates_guard before insert or update on hx_label_templates for each row execute function hx_label_guard();
drop trigger if exists hx_label_templates_place on hx_label_templates;
create trigger hx_label_templates_place before insert or update on hx_label_templates for each row execute function hx_fl_guard();
drop trigger if exists hx_label_templates_audit on hx_label_templates;
create trigger hx_label_templates_audit after insert or update or delete on hx_label_templates for each row execute function hx_audit();

alter table hx_label_templates enable row level security;
drop policy if exists hx_label_templates_read on hx_label_templates;
drop policy if exists hx_label_templates_insert on hx_label_templates;
drop policy if exists hx_label_templates_update on hx_label_templates;
drop policy if exists hx_label_templates_delete on hx_label_templates;
create policy hx_label_templates_read   on hx_label_templates for select to authenticated using (hx_can('stickers',1,license_id));
create policy hx_label_templates_insert on hx_label_templates for insert to authenticated with check (hx_can('stickers',2,license_id));
create policy hx_label_templates_update on hx_label_templates for update to authenticated using (hx_can('stickers',2,license_id)) with check (hx_can('stickers',2,license_id));
create policy hx_label_templates_delete on hx_label_templates for delete to authenticated using (hx_can('stickers',3,license_id));
grant select, insert, update, delete on hx_label_templates to authenticated;

notify pgrst, 'reload schema';
