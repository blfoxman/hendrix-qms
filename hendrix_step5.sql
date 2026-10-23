-- =====================================================================
-- Hendrix QMS  -  Step 5: Products, SKUs, Flavors, Formulations
-- One source of truth per state: a SKU / flavor / recipe is created once
-- here and every module (Batch Tracker, Planner, labels, Testing) reads it.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-4.
-- Safe to run more than once.
--
-- Rules built into the database:
--   * every SKU belongs to one state; flavors and formulations inherit it
--   * a SKU cannot be switched ON until it has at least one formulation;
--     deleting its last formulation switches it back OFF
--   * a flavor-specific formulation must use a flavor of that same SKU
--   * a SKU limited to certain licenses may only list licenses of its state
--   * nothing can be moved to another state
--   * formulations and ingredient prices are admin-only (company IP)
-- =====================================================================

create or replace function hx_valid_product_type(p text) returns boolean
language sql immutable as $$
  select coalesce(p,'') in ('ethanol_extraction','butane_extraction','pre_rolls','cartridges',
                            'gummies','infused_flower','moon_rocks','snow_caps');
$$;

-- ---------- tables ----------
create table if not exists hx_skus (
  id            text primary key,
  state_id      text not null references hx_states(id),
  product_type  text not null check (hx_valid_product_type(product_type)),
  name          text not null check (length(trim(name)) > 0),
  spec          jsonb  not null default '{}'::jsonb,   -- production settings (joint weights, oil per cart, grams per gummy...)
  license_ids   text[] not null default '{}',          -- empty = every license in the state
  active        boolean not null default false,
  sort          int not null default 0,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
create unique index if not exists hx_skus_name on hx_skus(state_id, product_type, lower(trim(name)));

create table if not exists hx_flavors (
  id          text primary key,
  state_id    text not null references hx_states(id),
  sku_id      text not null references hx_skus(id) on delete cascade,
  name        text not null check (length(trim(name)) > 0),
  active      boolean not null default true,
  sort        int not null default 0,
  created_at  timestamptz not null default now()
);
create unique index if not exists hx_flavors_name on hx_flavors(sku_id, lower(trim(name)));

create table if not exists hx_formulations (
  id             text primary key,
  state_id       text not null references hx_states(id),
  sku_id         text not null references hx_skus(id) on delete cascade,
  flavor_id      text references hx_flavors(id) on delete cascade,   -- null = base recipe for every flavor
  name           text not null default '',
  batch_size     text not null default '',
  raw_materials  jsonb not null default '[]'::jsonb,
  packaging      jsonb not null default '[]'::jsonb,
  labor          jsonb not null default '[]'::jsonb,
  notes          text not null default '',
  created_by     uuid default auth.uid(),
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);
create unique index if not exists hx_formulations_one on hx_formulations(sku_id, coalesce(flavor_id,''));

create table if not exists hx_cost_library (
  id             text primary key,
  state_id       text not null references hx_states(id),
  category       text not null check (category in ('raw_material','packaging','labor')),
  name           text not null check (length(trim(name)) > 0),
  unit           text not null default '',
  cost_per_unit  numeric,
  product_types  text[] not null default '{}',   -- empty = every product type
  created_at     timestamptz not null default now()
);

-- ---------- guards ----------
create or replace function hx_sku_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_bad text;
begin
  if tg_op = 'UPDATE' and new.state_id is distinct from old.state_id then
    raise exception 'A SKU cannot be moved to another state.';
  end if;
  if tg_op = 'UPDATE' and new.product_type is distinct from old.product_type then
    raise exception 'The product type of a SKU cannot be changed. Create a new SKU instead.';
  end if;
  if coalesce(array_length(new.license_ids,1),0) > 0 then
    select x into v_bad from unnest(new.license_ids) x
     where not exists (select 1 from hx_licenses l where l.id = x and l.state_id = new.state_id) limit 1;
    if v_bad is not null then
      raise exception 'A SKU can only be limited to licenses in its own state.';
    end if;
  end if;
  if new.active and not exists (select 1 from hx_formulations f where f.sku_id = new.id) then
    raise exception 'Enter a formulation for this SKU before it can be switched on.';
  end if;
  new.updated_at := now();
  return new;
end $$;

-- flavors / formulations take their state from the SKU; a mismatch is refused
create or replace function hx_sku_child_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_state text; v_fsku text;
begin
  select state_id into v_state from hx_skus where id = new.sku_id;
  if v_state is null then
    raise exception 'Unknown SKU.';
  end if;
  if tg_op = 'UPDATE' and new.sku_id is distinct from old.sku_id then
    raise exception 'This cannot be moved to another SKU.';
  end if;
  if coalesce(new.state_id,'') = '' then
    new.state_id := v_state;
  elsif new.state_id <> v_state then
    raise exception 'This SKU belongs to a different state.';
  end if;
  if tg_table_name = 'hx_formulations' then
    if new.flavor_id is not null then
      select sku_id into v_fsku from hx_flavors where id = new.flavor_id;
      if v_fsku is distinct from new.sku_id then
        raise exception 'That flavor belongs to a different SKU.';
      end if;
    end if;
    new.updated_at := now();
  end if;
  return new;
end $$;

-- deleting the last formulation switches the SKU off again
create or replace function hx_formulation_after_delete() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if not exists (select 1 from hx_formulations where sku_id = old.sku_id) then
    update hx_skus set active = false where id = old.sku_id and active;
  end if;
  return old;
end $$;

create or replace function hx_cost_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'UPDATE' and new.state_id is distinct from old.state_id then
    raise exception 'Prices cannot be moved to another state.';
  end if;
  return new;
end $$;

drop trigger if exists hx_skus_guard on hx_skus;
create trigger hx_skus_guard before insert or update on hx_skus for each row execute function hx_sku_guard();
drop trigger if exists hx_flavors_guard on hx_flavors;
create trigger hx_flavors_guard before insert or update on hx_flavors for each row execute function hx_sku_child_guard();
drop trigger if exists hx_formulations_guard on hx_formulations;
create trigger hx_formulations_guard before insert or update on hx_formulations for each row execute function hx_sku_child_guard();
drop trigger if exists hx_formulations_after_delete on hx_formulations;
create trigger hx_formulations_after_delete after delete on hx_formulations for each row execute function hx_formulation_after_delete();
drop trigger if exists hx_cost_library_guard on hx_cost_library;
create trigger hx_cost_library_guard before update on hx_cost_library for each row execute function hx_cost_guard();

-- ---------- row level security ----------
alter table hx_skus         enable row level security;
alter table hx_flavors      enable row level security;
alter table hx_formulations enable row level security;
alter table hx_cost_library enable row level security;

do $$
declare t text;
begin
  foreach t in array array['hx_skus','hx_flavors','hx_formulations','hx_cost_library'] loop
    execute format('drop policy if exists %I on %I', t||'_read', t);
    execute format('drop policy if exists %I on %I', t||'_insert', t);
    execute format('drop policy if exists %I on %I', t||'_update', t);
    execute format('drop policy if exists %I on %I', t||'_delete', t);
    execute format('create policy %I on %I for insert to authenticated with check (hx_fl_is_admin())', t||'_insert', t);
    execute format('create policy %I on %I for update to authenticated using (hx_fl_is_admin()) with check (hx_fl_is_admin())', t||'_update', t);
    execute format('create policy %I on %I for delete to authenticated using (hx_fl_is_admin())', t||'_delete', t);
  end loop;
end $$;
-- SKUs and flavors: every approved user can read (they feed every module)
create policy hx_skus_read    on hx_skus    for select to authenticated using (hx_fl_is_approved());
create policy hx_flavors_read on hx_flavors for select to authenticated using (hx_fl_is_approved());
-- recipes and prices: admin only until Access Templates arrive
create policy hx_formulations_read on hx_formulations for select to authenticated using (hx_fl_is_admin());
create policy hx_cost_library_read on hx_cost_library for select to authenticated using (hx_fl_is_admin());

grant select, insert, update, delete on hx_skus, hx_flavors, hx_formulations, hx_cost_library to authenticated;
grant execute on function hx_valid_product_type(text) to anon, authenticated;

notify pgrst, 'reload schema';
