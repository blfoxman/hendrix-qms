-- =====================================================================
-- Hendrix QMS  -  Step 47: Batch Tracker picks tags from Receiving inventory
--
--   * hx_batch_lots(p_lic): the accepted, unexpired lots that still have
--     something left, for the Batch Tracker's tag search (type the last
--     digits of a METRC tag, pick the lot). Anyone who can see the Batch
--     Tracker or Receiving for that license may call it, even without
--     Receiving access (operators see only the lot, item and amount left).
--   * When the batch is submitted, Hendrix records the amount used against
--     the lot (hx_lot_uses, already in step 17): it is deducted from the lot
--     and shows on the lot's usage history with the batch number.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-46.
-- Safe to run more than once.
-- =====================================================================

create or replace function hx_batch_lots(p_lic text)
returns table (id text, number text, item text, category text, metrc_tag text, supplier_lot text, unit text,
               qty_left numeric, received_on date, expiry_date date)
language sql stable security definer set search_path = public as $$
  select l.id, l.number, l.item, l.category, l.metrc_tag, l.supplier_lot, l.unit,
         l.quantity - l.qty_used, l.received_on, l.expiry_date
  from hx_lots l
  where l.license_id = p_lic
    and (hx_can('batch', 1, p_lic) or hx_can('receiving', 1, p_lic))
    and l.status = 'accepted'
    and l.quantity - l.qty_used > 0
    and (l.expiry_date is null or l.expiry_date >= current_date)
  order by l.received_on, l.number;
$$;
revoke all on function hx_batch_lots(text) from public;
grant execute on function hx_batch_lots(text) to authenticated;
