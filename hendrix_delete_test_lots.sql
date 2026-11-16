-- =====================================================================
-- Hendrix QMS  -  ONE-TIME CLEAN-UP: delete the TEST lots in Receiving / Inventory
--
--   For Black Fox (MAN000109). Hendrix never lets anyone delete a received lot from
--   the app (inspection records), so test lots are removed here, in Supabase.
--
--   HOW TO USE (Supabase > SQL Editor):
--     1. Run PART 1 only (select it, Run). Check the list: every lot in it will be deleted.
--     2. If the list is right, run PART 2. It deletes those lots and their use records
--        (the amounts taken in Batch Tracker), clears the lot from holds and plant batches,
--        and writes one line per deleted lot in the Audit Trail.
--
--   Which lots: status 'accepted' (approved) by default. To include lots still in
--   quarantine, rejected, on hold etc., change   in ('accepted')   in BOTH parts to
--   in ('accepted','quarantine','rejected','on_hold','returned','destroyed').
--   Safe to run again: the second time there is nothing left to delete.
-- =====================================================================

-- ---------- PART 1: preview (deletes nothing) ----------
select l.number, l.item, l.status, l.quantity, l.unit, l.qty_used, l.metrc_tag, l.received_on,
       (select count(*) from hx_lot_uses u where u.lot_id = l.id) as use_records
  from hx_lots l join hx_licenses c on c.id = l.license_id
 where c.license_number = 'MAN000109' and l.status in ('accepted')
 order by l.number;

-- ---------- PART 2: delete ----------
begin;
create temp table x_lots on commit drop as
  select l.* from hx_lots l join hx_licenses c on c.id = l.license_id
   where c.license_number = 'MAN000109' and l.status in ('accepted');
insert into hx_audit_log(table_name, row_id, action, state_id, license_id, user_id, user_name, reason, old_data)
  select 'hx_lots', x.id, 'DELETE', x.state_id, x.license_id, auth.uid(), 'Supabase admin', 'Test lot deleted (one-time clean-up)', to_jsonb(x) from x_lots x;
alter table hx_lot_uses disable trigger user;
alter table hx_holds disable trigger user;
alter table hx_plant_batches disable trigger user;
alter table hx_grow_events disable trigger user;
alter table hx_lots disable trigger user;
delete from hx_lot_uses where lot_id in (select id from x_lots);
update hx_holds set lot_id = null where lot_id in (select id from x_lots);
update hx_plant_batches set source_lot_id = null where source_lot_id in (select id from x_lots);
update hx_plant_batches set media_lot_id = null where media_lot_id in (select id from x_lots);
update hx_grow_events set lot_id = null where lot_id in (select id from x_lots);
delete from hx_lots where id in (select id from x_lots);
alter table hx_lots enable trigger user;
alter table hx_grow_events enable trigger user;
alter table hx_plant_batches enable trigger user;
alter table hx_holds enable trigger user;
alter table hx_lot_uses enable trigger user;
select count(*) as lots_deleted from x_lots;
commit;
