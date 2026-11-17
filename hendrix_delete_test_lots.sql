-- =====================================================================
-- Hendrix QMS  -  ONE-TIME CLEAN-UP: delete the TEST lots in Receiving / Inventory
--
--   For Black Fox (MAN000109). Hendrix never lets anyone delete a received lot from
--   the app (inspection records), so test lots are removed here, in Supabase.
--
--   HOW TO USE (Supabase > SQL Editor):
--     1. Run PART 1 only (select it, Run). Check the list: every lot in it will be deleted.
--     2. If the list is right, select PART 2 (from "do $$" to the last line) and Run.
--        It is one statement: it deletes those lots and their use records (amounts taken
--        in Batch Tracker), clears the lot from holds and plant batches, writes one line
--        per deleted lot in the Audit Trail, and says how many it deleted.
--
--   Which lots: status 'accepted' (approved) by default. To include lots still in
--   quarantine, rejected, on hold etc., change   array['accepted']   in BOTH parts to
--   array['accepted','quarantine','rejected','on_hold','returned','destroyed'].
--   Safe to run again: the second time there is nothing left to delete.
-- =====================================================================

-- ---------- PART 1: preview (deletes nothing) ----------
select l.number, l.item, l.status, l.quantity, l.unit, l.qty_used, l.metrc_tag, l.received_on,
       (select count(*) from hx_lot_uses u where u.lot_id = l.id) as use_records
  from hx_lots l join hx_licenses c on c.id = l.license_id
 where c.license_number = 'MAN000109' and l.status = any(array['accepted'])
 order by l.number;

-- ---------- PART 2: delete (one statement) ----------
do $$
declare v_ids text[]; v_n int;
begin
  select array_agg(l.id) into v_ids from hx_lots l join hx_licenses c on c.id = l.license_id
   where c.license_number = 'MAN000109' and l.status = any(array['accepted']);
  v_n := coalesce(array_length(v_ids, 1), 0);
  if v_n = 0 then raise notice 'Nothing to delete.'; return; end if;
  insert into hx_audit_log(table_name, row_id, action, state_id, license_id, user_id, user_name, reason, old_data)
    select 'hx_lots', l.id, 'DELETE', l.state_id, l.license_id, auth.uid(), 'Supabase admin', 'Test lot deleted (one-time clean-up)', to_jsonb(l)
      from hx_lots l where l.id = any(v_ids);
  alter table hx_lot_uses disable trigger user;
  alter table hx_holds disable trigger user;
  alter table hx_plant_batches disable trigger user;
  alter table hx_grow_events disable trigger user;
  alter table hx_lots disable trigger user;
  delete from hx_lot_uses where lot_id = any(v_ids);
  update hx_holds set lot_id = null where lot_id = any(v_ids);
  update hx_plant_batches set source_lot_id = null where source_lot_id = any(v_ids);
  update hx_plant_batches set media_lot_id = null where media_lot_id = any(v_ids);
  update hx_grow_events set lot_id = null where lot_id = any(v_ids);
  delete from hx_lots where id = any(v_ids);
  alter table hx_lots enable trigger user;
  alter table hx_grow_events enable trigger user;
  alter table hx_plant_batches enable trigger user;
  alter table hx_holds enable trigger user;
  alter table hx_lot_uses enable trigger user;
  raise notice 'Deleted % test lots.', v_n;
end $$;

-- check afterwards (optional): approved lots left on Black Fox, should be 0
select count(*) as approved_lots_left from hx_lots l join hx_licenses c on c.id = l.license_id
 where c.license_number = 'MAN000109' and l.status = any(array['accepted']);
