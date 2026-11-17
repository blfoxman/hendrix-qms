-- =====================================================================
-- Hendrix QMS  -  Step 56: update inventory from Excel (download current, fill out, upload)
--
--   Receiving > Inventory > "Download current inventory" gives the Hendrix inventory
--   template filled with every lot in stock, with its Hendrix Lot # in the first column.
--   Change what you counted and upload it with "Upload inventory":
--     * a row with a Hendrix Lot # updates that lot:
--         - On hand different from Hendrix -> an inventory count record (before, after,
--           file, who) in hx_lot_counts; the lot's used quantity is set so On hand = the
--           count (the received quantity never changes). 0 = used up.
--         - Storage location -> updated.
--         - METRC tag -> added when the lot has none (a different tag is refused: change
--           tags on the lot in Hendrix, with a reason).
--         - Item, supplier, dates and the rest stay as received.
--     * a row with no Lot # is a new lot (as in step 53).
--   All rows are saved together or none. Needs Full access to Receiving.
--   Every count is in the Audit Trail ("Inventory count from <file>: 1200 -> 1150 g").
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-55.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_lot_counts (
  id           text primary key,
  state_id     text not null references hx_states(id),
  license_id   text not null references hx_licenses(id),
  lot_id       text not null references hx_lots(id),
  counted_on   date not null default current_date,
  before_qty   numeric not null,
  counted_qty  numeric not null check (counted_qty >= 0),
  unit         text not null default '',
  source       text not null default '',
  notes        text not null default '',
  counted_by   text not null default '',
  created_at   timestamptz not null default now()
);
create index if not exists hx_lot_counts_lot on hx_lot_counts(lot_id, created_at desc);

create or replace function hx_lot_count_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  raise exception 'Inventory counts are never changed or deleted. Record a new count.';
end $$;
drop trigger if exists hx_lot_counts_guard on hx_lot_counts;
create trigger hx_lot_counts_guard before update or delete on hx_lot_counts for each row execute function hx_lot_count_guard();
drop trigger if exists hx_lot_counts_audit on hx_lot_counts;
create trigger hx_lot_counts_audit after insert on hx_lot_counts for each row execute function hx_audit();
alter table hx_lot_counts enable row level security;
drop policy if exists hx_lot_counts_read on hx_lot_counts;
create policy hx_lot_counts_read on hx_lot_counts for select to authenticated using (hx_can('receiving', 1, license_id));
grant select on hx_lot_counts to authenticated;

create or replace function hx_inventory_upload(p_lic text, p_rows jsonb, p_file text default '') returns jsonb
language plpgsql volatile security definer set search_path = public as $$
declare r jsonb; i int := 0; l record; v_new jsonb := '[]'::jsonb; v_qty numeric; v_left numeric; v_row text; v_tag text; v_loc text;
  v_me text := coalesce(hx_me(), ''); v_file text := coalesce(nullif(trim(coalesce(p_file, '')), ''), 'an Excel file');
  v_counts int := 0; v_moved int := 0; v_tags int := 0; v_same int := 0; v_seen text[] := '{}'; v_imp jsonb;
begin
  if not hx_can('receiving', 3, p_lic) then raise exception 'Uploading inventory needs Full access to Receiving for this license.'; end if;
  if jsonb_typeof(p_rows) <> 'array' or jsonb_array_length(p_rows) = 0 then raise exception 'The file has no inventory rows.'; end if;
  if jsonb_array_length(p_rows) > 5000 then raise exception 'Upload at most 5000 rows at a time.'; end if;
  for r in select * from jsonb_array_elements(p_rows) loop
    i := i + 1;
    v_row := coalesce(nullif(r->>'_row', ''), i::text);
    if coalesce(trim(r->>'lot_number'), '') = '' then
      v_new := v_new || jsonb_build_array(r - 'lot_number' - '_row');
      continue;
    end if;
    select * into l from hx_lots where license_id = p_lic and upper(number) = upper(trim(r->>'lot_number')) for update;
    if l.id is null then raise exception 'Row %: lot % is not in Hendrix for this license. Clear the Lot # to add it as a new lot.', v_row, trim(r->>'lot_number'); end if;
    if l.id = any(v_seen) then raise exception 'Row %: lot % is in the file more than once.', v_row, l.number; end if;
    v_seen := v_seen || l.id;
    if l.status in ('rejected','returned','destroyed') then raise exception 'Row %: lot % is % and is not in stock.', v_row, l.number, l.status; end if;
    begin v_qty := nullif(trim(r->>'quantity'), '')::numeric; exception when others then raise exception 'Row %: On hand must be a number.', v_row; end;
    if v_qty is null or v_qty < 0 then raise exception 'Row %: On hand must be 0 or more.', v_row; end if;
    if coalesce(trim(r->>'unit'), '') <> '' and lower(trim(r->>'unit')) <> lower(l.unit) then
      raise exception 'Row %: lot % is counted in % (the file says %).', v_row, l.number, l.unit, trim(r->>'unit'); end if;
    v_left := l.quantity - l.qty_used;
    v_tag := trim(coalesce(r->>'metrc_tag', ''));
    if v_tag <> '' and trim(l.metrc_tag) <> '' and hx_tagkey(v_tag) <> hx_tagkey(l.metrc_tag) then
      raise exception 'Row %: METRC tag % is different from the tag on lot % (%). Change a tag on the lot in Hendrix, with a reason.', v_row, v_tag, l.number, l.metrc_tag; end if;
    v_loc := trim(coalesce(r->>'location', ''));
    if round(v_qty, 4) = round(v_left, 4) and (v_loc = '' or v_loc = l.location) and (v_tag = '' or trim(l.metrc_tag) <> '') then v_same := v_same + 1; continue; end if;
    if round(v_qty, 4) <> round(v_left, 4) then
      insert into hx_lot_counts(id, state_id, license_id, lot_id, before_qty, counted_qty, unit, source, notes, counted_by)
      values ('cnt-' || replace(gen_random_uuid()::text, '-', ''), l.state_id, l.license_id, l.id, v_left, v_qty, l.unit, v_file, trim(coalesce(r->>'notes', '')), v_me);
      perform set_config('hx.internal', 'on', true);
      perform set_config('hx.reason', 'Inventory count from ' || v_file || ': ' || v_left || ' -> ' || v_qty || ' ' || l.unit, true);
      update hx_lots set qty_used = quantity - v_qty where id = l.id;
      perform set_config('hx.internal', '', true);
      v_counts := v_counts + 1;
    end if;
    if v_loc <> '' and v_loc <> l.location then
      perform set_config('hx.internal', 'on', true);
      perform set_config('hx.reason', 'Location from ' || v_file, true);
      update hx_lots set location = v_loc where id = l.id;
      perform set_config('hx.internal', '', true);
      v_moved := v_moved + 1;
    end if;
    if v_tag <> '' and trim(l.metrc_tag) = '' then
      perform set_config('hx.internal', 'on', true);
      perform set_config('hx.reason', 'METRC tag added from ' || v_file, true);
      update hx_lots set metrc_tag = v_tag where id = l.id;
      perform set_config('hx.internal', '', true);
      v_tags := v_tags + 1;
    end if;
  end loop;
  if jsonb_array_length(v_new) > 0 then v_imp := hx_lots_import(p_lic, v_new, p_file); end if;
  return jsonb_build_object('added', coalesce((v_imp->>'count')::int, 0), 'first', v_imp->>'first', 'last', v_imp->>'last',
                            'counted', v_counts, 'moved', v_moved, 'tagged', v_tags, 'unchanged', v_same);
end $$;
revoke all on function hx_inventory_upload(text, jsonb, text) from public;
grant execute on function hx_inventory_upload(text, jsonb, text) to authenticated;

notify pgrst, 'reload schema';
