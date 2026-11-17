-- =====================================================================
-- Hendrix QMS  -  Step 53: upload inventory from Excel (Receiving > Inventory)
--
--   Receiving > Inventory > "Download template" gives an Excel file with the columns
--   to fill (and the suppliers and lists to choose from). "Upload inventory" reads
--   the filled file, shows every row with any problem, and adds all rows as lots
--   in one go (all or nothing) through hx_lots_import():
--     * each row becomes a lot with its own RCV number, from a supplier on file for
--       this license that is approved, conditional or emergency (as in Receiving);
--     * Status "Accepted" (default) puts the lot straight into stock - it needs
--       "COA on file" = Yes and no past expiry date, as when a lot is accepted by hand;
--       "Quarantine" leaves it to be inspected and accepted in Receiving;
--     * a METRC tag already on another lot of this license (or twice in the file)
--       is refused;
--     * the Audit Trail shows each lot as received and accepted from the file.
--   Needs Full access to Receiving.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-52.
-- Safe to run more than once.
-- =====================================================================

create or replace function hx_lots_import(p_lic text, p_rows jsonb, p_file text default '') returns jsonb
language plpgsql volatile security definer set search_path = public as $$
declare r jsonb; i int := 0; v_state text; v_sup record; v_id text; v_tag text; v_status text; v_coa boolean;
  v_qty numeric; v_rec date; v_exp date; v_me text; v_nums text[] := '{}'; v_num text; v_file text := nullif(trim(coalesce(p_file, '')), '');
begin
  if not hx_can('receiving', 3, p_lic) then raise exception 'Uploading inventory needs Full access to Receiving for this license.'; end if;
  select state_id into v_state from hx_licenses where id = p_lic;
  if v_state is null then raise exception 'Unknown license.'; end if;
  if jsonb_typeof(p_rows) <> 'array' or jsonb_array_length(p_rows) = 0 then raise exception 'The file has no inventory rows.'; end if;
  if jsonb_array_length(p_rows) > 5000 then raise exception 'Upload at most 5000 rows at a time.'; end if;
  v_me := coalesce(hx_me(), '');
  for r in select * from jsonb_array_elements(p_rows) loop
    i := i + 1;
    if coalesce(trim(r->>'item'), '') = '' then raise exception 'Row %: enter the item.', i; end if;
    begin v_qty := nullif(trim(r->>'quantity'), '')::numeric; exception when others then raise exception 'Row %: quantity must be a number.', i; end;
    if v_qty is null or v_qty <= 0 then raise exception 'Row %: quantity must be more than 0.', i; end if;
    if coalesce(trim(r->>'unit'), '') = '' then raise exception 'Row %: enter the unit.', i; end if;
    select * into v_sup from hx_suppliers s where lower(trim(s.name)) = lower(trim(coalesce(r->>'supplier', ''))) and p_lic = any(s.license_ids) order by (s.status in ('approved','conditional','emergency')) desc limit 1;
    if v_sup.id is null then raise exception 'Row %: supplier "%" is not on file for this license. Add it in Suppliers or use a name from the Suppliers sheet of the template.', i, coalesce(r->>'supplier', ''); end if;
    if v_sup.status not in ('approved','conditional','emergency') then raise exception 'Row %: % is not approved - receive only from approved suppliers.', i, v_sup.name; end if;
    begin v_rec := coalesce(nullif(trim(r->>'received_on'), '')::date, current_date); v_exp := nullif(trim(r->>'expiry_date'), '')::date;
    exception when others then raise exception 'Row %: dates must be like 2026-11-16.', i; end;
    if v_rec > current_date then raise exception 'Row %: the received date cannot be in the future.', i; end if;
    v_status := lower(coalesce(nullif(trim(r->>'status'), ''), 'accepted'));
    if v_status not in ('accepted','quarantine') then raise exception 'Row %: status must be Accepted or Quarantine.', i; end if;
    v_coa := coalesce((r->>'coa_ok')::boolean, false);
    if v_status = 'accepted' and not v_coa then raise exception 'Row %: an accepted lot needs its COA or certificate of conformance on file (COA on file = Yes), or set Status to Quarantine.', i; end if;
    if v_status = 'accepted' and v_exp is not null and v_exp < current_date then raise exception 'Row %: past its expiry date - it cannot be accepted.', i; end if;
    v_tag := trim(coalesce(r->>'metrc_tag', ''));
    if v_tag <> '' then
      if exists (select 1 from hx_lots l where l.license_id = p_lic and hx_tagkey(l.metrc_tag) = hx_tagkey(v_tag) and l.status not in ('rejected','returned','destroyed')) then
        raise exception 'Row %: METRC tag % is already on a lot in Hendrix.', i, v_tag; end if;
      if (select count(*) from jsonb_array_elements(p_rows) x where hx_tagkey(x->>'metrc_tag') = hx_tagkey(v_tag)) > 1 then
        raise exception 'Row %: METRC tag % is in the file more than once.', i, v_tag; end if;
    end if;
    v_id := 'lot-' || replace(gen_random_uuid()::text, '-', '');
    insert into hx_lots(id, state_id, license_id, received_on, supplier_id, item, category, supplier_lot, metrc_tag, quantity, unit, expiry_date, location, po_number, coa_ok, inspection_notes, status)
    values (v_id, v_state, p_lic, v_rec, v_sup.id, trim(r->>'item'), coalesce(nullif(trim(r->>'category'), ''), 'Other'), trim(coalesce(r->>'supplier_lot', '')), v_tag,
            v_qty, trim(r->>'unit'), v_exp, trim(coalesce(r->>'location', '')), trim(coalesce(r->>'po_number', '')), v_coa, trim(coalesce(r->>'notes', '')), 'quarantine')
    returning number into v_num;
    if v_status = 'accepted' then
      perform set_config('hx.internal', 'on', true);
      perform set_config('hx.reason', 'Accepted: inventory uploaded from ' || coalesce(v_file, 'an Excel file'), true);
      update hx_lots set status = 'accepted', decided_by = v_me, decided_at = now(),
             decision_notes = 'Inventory uploaded from ' || coalesce(v_file, 'an Excel file') || ' by ' || v_me where id = v_id;
      perform set_config('hx.internal', '', true);
    end if;
    v_nums := v_nums || v_num;
  end loop;
  return jsonb_build_object('count', i, 'first', v_nums[1], 'last', v_nums[array_length(v_nums, 1)]);
end $$;
revoke all on function hx_lots_import(text, jsonb, text) from public;
grant execute on function hx_lots_import(text, jsonb, text) to authenticated;

notify pgrst, 'reload schema';
