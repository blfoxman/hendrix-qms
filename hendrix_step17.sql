-- =====================================================================
-- Hendrix QMS  -  Step 17: Receiving, Hold and Release, Shipping
-- (CSQ 2A.9.4, 2A.10.1, 2A.10.2, 2A.10.3, 2A.10.4, 2A.12.4, 3C.1)
--   * Receiving: every incoming lot gets a number (RCV-YYYY-###), comes only
--     from a supplier approved for that license, is inspected on arrival
--     (packaging, damage, pests, seals, labels, matches documents), keeps its
--     COA / certificate of conformance and documents, and waits in QUARANTINE
--     until someone with Full access accepts or rejects it. Rejected lots are
--     put on hold automatically (held apart until returned or destroyed).
--   * Inventory: what is used from each lot in which batch (one step back
--     traceability), quantity left, expiry; expired or held lots cannot be used.
--   * Hold and release: anyone with Edit can put a lot, batch, product tag or
--     customer return on hold (HOLD-YYYY-###); only Full can decide (release,
--     destroy, return to supplier, rework) and must write why. Held lots and
--     batches cannot be used or shipped. Holds are never deleted.
--   * Shipping: shipments (SHP-YYYY-###) list batches and package tags per
--     customer (one step forward traceability), the state manifest, the
--     transporter, and a pre-load inspection that must pass. Batches on hold
--     or with a failed test and no passing retest cannot be shipped.
-- Access modules 'receiving', 'holds', 'shipping': View / Edit / Full.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-16.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_lots (
  id              text primary key,
  state_id        text not null references hx_states(id),
  license_id      text not null references hx_licenses(id),
  number          text not null default '',
  received_on     date not null default current_date,
  supplier_id     text not null references hx_suppliers(id),
  supplier_name   text not null default '',
  supplier_status text not null default '',
  item            text not null check (length(trim(item)) > 0),
  category        text not null default 'Other',
  supplier_lot    text not null default '',
  metrc_tag       text not null default '',
  quantity        numeric not null check (quantity > 0),
  unit            text not null default 'each',
  qty_used        numeric not null default 0,
  expiry_date     date,
  location        text not null default '',
  po_number       text not null default '',
  coa_ok          boolean not null default false,
  checks          jsonb not null default '{}'::jsonb,
  checks_ok       boolean not null default false,
  inspection_notes text not null default '',
  files           jsonb not null default '[]'::jsonb,
  status          text not null default 'quarantine' check (status in ('quarantine','accepted','rejected','on_hold','returned','destroyed')),
  decision_notes  text not null default '',
  decided_by      text not null default '',
  decided_at      timestamptz,
  received_by     text not null default '',
  received_by_id  uuid default auth.uid(),
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
create unique index if not exists hx_lots_number on hx_lots(license_id, number);
create index if not exists hx_lots_lic on hx_lots(license_id, status, received_on desc);
create index if not exists hx_lots_sup on hx_lots(supplier_id);

create table if not exists hx_lot_uses (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  lot_id        text not null references hx_lots(id),
  batch_id      text references hx_batches(id),
  batch_number  text not null default '',
  used_on       date not null default current_date,
  quantity      numeric not null check (quantity > 0),
  notes         text not null default '',
  used_by       text not null default '',
  used_by_id    uuid default auth.uid(),
  created_at    timestamptz not null default now(),
  voided        boolean not null default false,
  void_reason   text,
  voided_by     uuid,
  voided_at     timestamptz
);
create index if not exists hx_lot_uses_lot on hx_lot_uses(lot_id);
create index if not exists hx_lot_uses_batch on hx_lot_uses(batch_id);

create table if not exists hx_holds (
  id             text primary key,
  state_id       text not null references hx_states(id),
  license_id     text not null references hx_licenses(id),
  number         text not null default '',
  kind           text not null default 'lot' check (kind in ('lot','batch','product','return','other')),
  lot_id         text references hx_lots(id),
  batch_id       text references hx_batches(id),
  tag            text not null default '',
  item           text not null default '',
  quantity       text not null default '',
  source         text not null default 'Other',
  reason         text not null check (length(trim(reason)) > 0),
  deviation_id   text,
  shipment_id    text,
  location       text not null default '',
  prev_status    text not null default '',
  status         text not null default 'open' check (status in ('open','released','destroyed','returned','reworked')),
  decision_notes text not null default '',
  decided_by     text not null default '',
  decided_at     timestamptz,
  placed_by      text not null default '',
  placed_by_id   uuid default auth.uid(),
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);
create unique index if not exists hx_holds_number on hx_holds(license_id, number);
create index if not exists hx_holds_lic on hx_holds(license_id, status, created_at desc);

create table if not exists hx_shipments (
  id                text primary key,
  state_id          text not null references hx_states(id),
  license_id        text not null references hx_licenses(id),
  number            text not null default '',
  ship_date         date not null default current_date,
  customer          text not null check (length(trim(customer)) > 0),
  customer_license  text not null default '',
  destination       text not null default '',
  manifest_number   text not null default '',
  transporter       text not null default '',
  driver            text not null default '',
  vehicle           text not null default '',
  items             jsonb not null default '[]'::jsonb,
  checks            jsonb not null default '{}'::jsonb,
  checks_ok         boolean not null default false,
  notes             text not null default '',
  files             jsonb not null default '[]'::jsonb,
  status            text not null default 'shipped' check (status in ('shipped','delivered','cancelled')),
  delivered_on      date,
  cancel_reason     text not null default '',
  shipped_by        text not null default '',
  shipped_by_id     uuid default auth.uid(),
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);
create unique index if not exists hx_shipments_number on hx_shipments(license_id, number);
create index if not exists hx_shipments_lic on hx_shipments(license_id, ship_date desc);

-- generic per-license numbering (same as QMS)
create or replace function hx_next_number(p_table text, p_lic text, p_prefix text) returns text
language plpgsql security definer set search_path = public as $$
declare v_year text := to_char(now(), 'YYYY'); v_max int;
begin
  perform pg_advisory_xact_lock(hashtext(p_table || p_lic));
  execute format('select coalesce(max((regexp_match(number, %L))[1]::int), 0) from %I where license_id = $1',
                 '^' || p_prefix || '-' || v_year || '-(\d+)$', p_table) into v_max using p_lic;
  return p_prefix || '-' || v_year || '-' || lpad((v_max + 1)::text, 3, '0');
end $$;

create or replace function hx_me() returns text language sql stable security definer set search_path = public as $$
  select coalesce(nullif(name,''), email) from hx_profiles where id::text = auth.uid()::text;
$$;

-- ---------- receiving ----------
create or replace function hx_lot_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare s record; v_full boolean := hx_perm('receiving') >= 3; a jsonb; n jsonb;
begin
  if tg_op = 'DELETE' then raise exception 'Received lots are never deleted. Reject the lot or put it on hold.'; end if;
  new.updated_at := now();
  if tg_op = 'INSERT' then
    select * into s from hx_suppliers where id = new.supplier_id;
    if s.id is null or not (new.license_id = any(s.license_ids)) then raise exception 'That supplier is not on file for this license.'; end if;
    if s.status not in ('approved','conditional','emergency') then
      raise exception '% is % - receive only from approved suppliers (CSQ 2A.11).', s.name, case s.status when 'pending' then 'not approved yet' else s.status end;
    end if;
    if new.received_on > current_date then raise exception 'The receiving date cannot be in the future.'; end if;
    new.number := hx_next_number('hx_lots', new.license_id, 'RCV');
    new.supplier_name := s.name; new.supplier_status := s.status;
    new.received_by := coalesce(hx_me(), new.received_by); new.received_by_id := auth.uid(); new.created_at := now();
    new.qty_used := 0; new.decided_by := ''; new.decided_at := null; new.decision_notes := '';
    new.checks_ok := not exists (select 1 from jsonb_each(new.checks) c where c.value <> 'true'::jsonb) and new.checks <> '{}'::jsonb;
    if new.status not in ('quarantine') then raise exception 'A received lot starts in quarantine until it is accepted.'; end if;
    perform set_config('hx.reason', 'Lot received from ' || s.name, true);
    return new;
  end if;
  if new.number <> old.number or new.supplier_id <> old.supplier_id or new.received_by_id is distinct from old.received_by_id or new.created_at <> old.created_at
     or new.state_id <> old.state_id or new.license_id <> old.license_id or new.supplier_name <> old.supplier_name or new.supplier_status <> old.supplier_status then
    raise exception 'The number, supplier, receiver and license of a lot cannot be changed.';
  end if;
  if current_setting('hx.internal', true) = 'on' then return new; end if;  -- quantity / hold updates from other triggers
  if new.qty_used <> old.qty_used then raise exception 'Use from a lot is recorded under Inventory, not by editing the lot.'; end if;
  new.checks_ok := not exists (select 1 from jsonb_each(new.checks) c where c.value <> 'true'::jsonb) and new.checks <> '{}'::jsonb;
  if new.status is distinct from old.status then
    if old.status = 'on_hold' or new.status in ('on_hold','returned','destroyed') then raise exception 'This lot is controlled by its hold. Decide the hold under Hold and Release.'; end if;
    if not v_full then raise exception 'Only someone with Full access to Receiving can accept or reject a lot.'; end if;
    if old.status <> 'quarantine' then raise exception 'Only a lot in quarantine can be accepted or rejected.'; end if;
    if coalesce(trim(new.decision_notes),'') = '' and new.status = 'rejected' then raise exception 'Write why the lot is rejected.'; end if;
    if new.status = 'accepted' then
      if not new.coa_ok then raise exception 'The lot needs its COA or certificate of conformance before it can be accepted (CSQ 2A.10.2).'; end if;
      if not new.checks_ok and coalesce(trim(new.decision_notes),'') = '' then raise exception 'The receiving inspection did not pass every check. Write why the lot is still accepted, or reject it.'; end if;
      if new.supplier_status = 'emergency' and coalesce(trim(new.decision_notes),'') = '' then raise exception 'This lot is from an emergency supplier. Write how it was verified before use (CSQ 2A.11 g).'; end if;
      if new.expiry_date is not null and new.expiry_date < current_date then raise exception 'This lot is past its expiry date and cannot be accepted.'; end if;
    end if;
    new.decided_by := coalesce(hx_me(),''); new.decided_at := now();
    perform set_config('hx.reason', 'Lot ' || new.status || coalesce(': ' || nullif(trim(new.decision_notes),''), ''), true);
    return new;
  end if;
  if old.status not in ('quarantine') then
    a := to_jsonb(old); n := to_jsonb(new);
    if (n - 'files' - 'location' - 'updated_at' - 'inspection_notes') is distinct from (a - 'files' - 'location' - 'updated_at' - 'inspection_notes') then
      raise exception 'After the decision only the storage location, files and notes of a lot can change.';
    end if;
  end if;
  if hx_perm('receiving') < 2 then raise exception 'You need Edit access to Receiving.'; end if;
  if coalesce(current_setting('hx.reason', true), '') = '' then perform set_config('hx.reason', 'Lot updated', true); end if;
  return new;
end $$;

-- after a rejection the lot is held apart automatically
create or replace function hx_lot_after() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.status = 'rejected' and old.status = 'quarantine' then
    perform set_config('hx.internal', 'on', true);
    insert into hx_holds(id, state_id, license_id, kind, lot_id, item, quantity, source, reason, location, prev_status)
    values ('hold-' || replace(gen_random_uuid()::text,'-',''), new.state_id, new.license_id, 'lot', new.id, new.item || ' (' || new.number || ')',
            new.quantity || ' ' || new.unit, 'Receiving inspection', 'Rejected at receiving: ' || new.decision_notes, new.location, 'rejected');
    perform set_config('hx.internal', 'off', true);
  end if;
  return null;
end $$;

create or replace function hx_lot_use_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare l record; b record; v_left numeric;
begin
  if tg_op = 'DELETE' then raise exception 'Use records are never deleted. Void the record with a reason.'; end if;
  if tg_op = 'INSERT' then
    select * into l from hx_lots where id = new.lot_id for update;
    if l.id is null or l.license_id <> new.license_id then raise exception 'Unknown lot for this license.'; end if;
    if l.status <> 'accepted' then raise exception 'Lot % is % and cannot be used.', l.number, case l.status when 'quarantine' then 'still in quarantine (not accepted yet)' when 'on_hold' then 'on hold' else l.status end; end if;
    if l.expiry_date is not null and l.expiry_date < new.used_on then raise exception 'Lot % expired on % and cannot be used.', l.number, l.expiry_date; end if;
    if new.used_on > current_date then raise exception 'The date cannot be in the future.'; end if;
    v_left := l.quantity - l.qty_used;
    if new.quantity > v_left then raise exception 'Only % % left in lot %.', v_left, l.unit, l.number; end if;
    if new.batch_id is not null then
      select * into b from hx_batches where id = new.batch_id;
      if b.id is null or b.license_id <> new.license_id then raise exception 'That batch belongs to a different license.'; end if;
      if b.voided then raise exception 'That batch is void.'; end if;
      new.batch_number := b.batch_number;
    end if;
    new.used_by := coalesce(hx_me(), new.used_by); new.used_by_id := auth.uid(); new.created_at := now();
    new.voided := false; new.void_reason := null; new.voided_by := null; new.voided_at := null;
    perform set_config('hx.reason', 'Used ' || new.quantity || ' ' || l.unit || ' of ' || l.number || coalesce(' in batch ' || nullif(new.batch_number,''), ''), true);
    perform set_config('hx.internal', 'on', true);
    update hx_lots set qty_used = qty_used + new.quantity where id = new.lot_id;
    perform set_config('hx.internal', 'off', true);
    -- the lot's audit row consumed the reason; set it again for this record
    perform set_config('hx.reason', 'Used ' || new.quantity || ' ' || l.unit || ' of ' || l.number || coalesce(' in batch ' || nullif(new.batch_number,''), ''), true);
    return new;
  end if;
  if old.voided then raise exception 'This use record is void.'; end if;
  if not new.voided or (to_jsonb(new) - 'voided' - 'void_reason' - 'voided_by' - 'voided_at') is distinct from (to_jsonb(old) - 'voided' - 'void_reason' - 'voided_by' - 'voided_at') then
    raise exception 'A use record cannot be changed. Void it with a reason and record it again.';
  end if;
  if hx_perm('receiving') < 3 then raise exception 'Only someone with Full access to Receiving can void a use record.'; end if;
  if coalesce(trim(new.void_reason),'') = '' then raise exception 'A reason is required to void a use record.'; end if;
  new.voided_by := auth.uid(); new.voided_at := now();
  perform set_config('hx.reason', 'Use voided: ' || trim(new.void_reason), true);
  perform set_config('hx.internal', 'on', true);
  update hx_lots set qty_used = greatest(qty_used - old.quantity, 0) where id = old.lot_id;
  perform set_config('hx.internal', 'off', true);
  perform set_config('hx.reason', 'Use voided: ' || trim(new.void_reason), true);
  return new;
end $$;

-- ---------- hold and release ----------
create or replace function hx_hold_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare l record; b record; v_int boolean := current_setting('hx.internal', true) = 'on';
begin
  if tg_op = 'DELETE' then raise exception 'Holds are never deleted. Decide the hold (release, destroy, return, rework) with a reason.'; end if;
  new.updated_at := now();
  if tg_op = 'INSERT' then
    if not v_int and hx_perm('holds') < 2 then raise exception 'You need Edit access to Hold and Release to place something on hold.'; end if;
    new.number := hx_next_number('hx_holds', new.license_id, 'HOLD');
    new.placed_by := coalesce(hx_me(), new.placed_by); new.placed_by_id := auth.uid(); new.created_at := now();
    new.status := 'open'; new.decided_by := ''; new.decided_at := null; new.decision_notes := '';
    perform set_config('hx.reason', 'Placed on hold: ' || trim(new.reason), true);
    if new.kind = 'lot' then
      select * into l from hx_lots where id = new.lot_id;
      if l.id is null or l.license_id <> new.license_id then raise exception 'Pick the lot to put on hold.'; end if;
      if l.status in ('returned','destroyed') then raise exception 'Lot % is already %.', l.number, l.status; end if;
      if l.status = 'on_hold' then raise exception 'Lot % is already on hold.', l.number; end if;
      if not v_int then new.prev_status := l.status; end if;
      new.item := coalesce(nullif(new.item,''), l.item || ' (' || l.number || ')');
      perform set_config('hx.internal', 'on', true);
      update hx_lots set status = 'on_hold' where id = l.id;
      perform set_config('hx.internal', case when v_int then 'on' else 'off' end, true);
      perform set_config('hx.reason', 'Placed on hold: ' || trim(new.reason), true);
    elsif new.kind in ('batch','return') or new.batch_id is not null then
      select * into b from hx_batches where id = new.batch_id;
      if new.kind = 'batch' and b.id is null then raise exception 'Pick the batch to put on hold.'; end if;
      if b.id is not null and b.license_id <> new.license_id then raise exception 'That batch belongs to a different license.'; end if;
      if b.id is not null then new.item := coalesce(nullif(new.item,''), coalesce(nullif(b.sku,''), b.batch_type) || ' batch ' || b.batch_number); end if;
    end if;
    if new.kind = 'product' and coalesce(trim(new.tag),'') = '' then raise exception 'Enter the package tag to put on hold.'; end if;
    if coalesce(trim(new.item),'') = '' then new.item := coalesce(nullif(trim(new.tag),''), 'Held item'); end if;
    return new;
  end if;
  if new.number <> old.number or new.kind <> old.kind or new.lot_id is distinct from old.lot_id or new.batch_id is distinct from old.batch_id or new.tag <> old.tag
     or new.created_at <> old.created_at or new.placed_by_id is distinct from old.placed_by_id or new.license_id <> old.license_id or new.reason <> old.reason then
    raise exception 'What is held and why cannot be changed. Decide this hold and open a new one.';
  end if;
  if old.status <> 'open' then raise exception 'This hold was already decided (%) and cannot be changed.', old.status; end if;
  if new.status = 'open' then
    if hx_perm('holds') < 2 then raise exception 'You need Edit access to Hold and Release.'; end if;
    if (to_jsonb(new) - 'location' - 'updated_at' - 'deviation_id') is distinct from (to_jsonb(old) - 'location' - 'updated_at' - 'deviation_id') then raise exception 'Only the location and the linked deviation of an open hold can change.'; end if;
    perform set_config('hx.reason', 'Hold updated', true);
    return new;
  end if;
  if hx_perm('holds') < 3 then raise exception 'Only someone with Full access to Hold and Release can decide a hold (CSQ 2A.10.4).'; end if;
  if coalesce(trim(new.decision_notes),'') = '' then raise exception 'Write the reason for the decision.'; end if;
  if new.status = 'released' and new.kind = 'lot' and old.prev_status = 'rejected' then raise exception 'This lot was rejected at receiving. Return it to the supplier or destroy it.'; end if;
  if new.status = 'released' and new.batch_id is not null and exists (select 1 from hx_tests t where t.batch_id = new.batch_id and not t.voided and t.status = 'Failed')
     and not exists (select 1 from hx_tests t where t.batch_id = new.batch_id and not t.voided and t.status = 'Passed' and t.created_at > (select max(created_at) from hx_tests f where f.batch_id = new.batch_id and not f.voided and f.status = 'Failed')) then
    raise exception 'This batch has a failed test and no passing retest after it. It cannot be released.';
  end if;
  new.decided_by := coalesce(hx_me(),''); new.decided_at := now();
  perform set_config('hx.reason', 'Hold ' || new.status || ': ' || trim(new.decision_notes), true);
  if new.kind = 'lot' then
    perform set_config('hx.internal', 'on', true);
    update hx_lots set status = case new.status when 'released' then coalesce(nullif(old.prev_status,''),'quarantine') when 'destroyed' then 'destroyed' when 'returned' then 'returned' else 'quarantine' end
     where id = new.lot_id;
    perform set_config('hx.internal', 'off', true);
    perform set_config('hx.reason', 'Hold ' || new.status || ': ' || trim(new.decision_notes), true);
  end if;
  return new;
end $$;

-- ---------- shipping ----------
create or replace function hx_shipment_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare it jsonb; b record; v_tag text;
begin
  if tg_op = 'DELETE' then raise exception 'Shipments are never deleted. Cancel with a reason.'; end if;
  new.updated_at := now();
  if tg_op = 'INSERT' then
    if hx_perm('shipping') < 2 then raise exception 'You need Edit access to Shipping.'; end if;
    if new.ship_date > current_date then raise exception 'The ship date cannot be in the future.'; end if;
    if jsonb_typeof(new.items) <> 'array' or jsonb_array_length(new.items) = 0 then raise exception 'Add at least one batch or package to the shipment.'; end if;
    new.checks_ok := not exists (select 1 from jsonb_each(new.checks) c where c.value <> 'true'::jsonb) and new.checks <> '{}'::jsonb;
    if not new.checks_ok then raise exception 'Every pre-load inspection check must pass before loading (CSQ 2A.9.4). Fix the problem first.'; end if;
    for it in select * from jsonb_array_elements(new.items) loop
      v_tag := coalesce(it->>'tag','');
      if coalesce(it->>'batch_id','') = '' then raise exception 'Every shipped item needs its batch (for traceability).'; end if;
      select * into b from hx_batches where id = it->>'batch_id';
      if b.id is null or b.license_id <> new.license_id then raise exception 'A batch in this shipment belongs to a different license.'; end if;
      if b.voided then raise exception 'Batch % is void.', b.batch_number; end if;
      if exists (select 1 from hx_holds h where h.status = 'open' and h.license_id = new.license_id and (h.batch_id = b.id or (v_tag <> '' and upper(regexp_replace(h.tag,'[^A-Za-z0-9]','','g')) = upper(regexp_replace(v_tag,'[^A-Za-z0-9]','','g'))))) then
        raise exception 'Batch % is on hold and cannot be shipped (CSQ 2A.10.4).', b.batch_number || case when v_tag <> '' then ' / tag ' || v_tag else '' end;
      end if;
      if exists (select 1 from hx_tests t where t.batch_id = b.id and not t.voided and t.status = 'Failed')
         and not exists (select 1 from hx_tests t where t.batch_id = b.id and not t.voided and t.status = 'Passed' and t.created_at > (select max(created_at) from hx_tests f where f.batch_id = b.id and not f.voided and f.status = 'Failed')) then
        raise exception 'Batch % has a failed test and no passing retest. It cannot be shipped.', b.batch_number;
      end if;
    end loop;
    new.number := hx_next_number('hx_shipments', new.license_id, 'SHP');
    new.shipped_by := coalesce(hx_me(), new.shipped_by); new.shipped_by_id := auth.uid(); new.created_at := now();
    new.status := 'shipped'; new.delivered_on := null; new.cancel_reason := '';
    perform set_config('hx.reason', 'Shipped to ' || new.customer, true);
    return new;
  end if;
  if (to_jsonb(new) - 'status' - 'delivered_on' - 'cancel_reason' - 'notes' - 'files' - 'updated_at' - 'manifest_number')
     is distinct from (to_jsonb(old) - 'status' - 'delivered_on' - 'cancel_reason' - 'notes' - 'files' - 'updated_at' - 'manifest_number') then
    raise exception 'What was shipped, to whom and when cannot be changed. Cancel the shipment with a reason and record it again.';
  end if;
  if old.status = 'cancelled' then raise exception 'This shipment is cancelled.'; end if;
  if hx_perm('shipping') < 2 then raise exception 'You need Edit access to Shipping.'; end if;
  if new.status = 'cancelled' and old.status <> 'cancelled' then
    if hx_perm('shipping') < 3 then raise exception 'Only someone with Full access to Shipping can cancel a shipment.'; end if;
    if coalesce(trim(new.cancel_reason),'') = '' then raise exception 'A reason is required to cancel a shipment.'; end if;
    perform set_config('hx.reason', 'Shipment cancelled: ' || trim(new.cancel_reason), true);
  elsif new.status = 'delivered' and old.status <> 'delivered' then
    new.delivered_on := coalesce(new.delivered_on, current_date);
    perform set_config('hx.reason', 'Delivered ' || new.delivered_on, true);
  elsif new.status = 'shipped' and old.status = 'delivered' then
    raise exception 'A delivered shipment cannot go back to shipped.';
  else
    perform set_config('hx.reason', 'Shipment updated', true);
  end if;
  return new;
end $$;

drop trigger if exists hx_lots_guard on hx_lots;
create trigger hx_lots_guard before insert or update or delete on hx_lots for each row execute function hx_lot_guard();
drop trigger if exists hx_lots_place on hx_lots;
create trigger hx_lots_place before insert or update on hx_lots for each row execute function hx_fl_guard();
drop trigger if exists hx_lots_a_audit on hx_lots;
create trigger hx_lots_a_audit after insert or update or delete on hx_lots for each row execute function hx_audit();
drop trigger if exists hx_lots_b_after on hx_lots;
create trigger hx_lots_b_after after update on hx_lots for each row execute function hx_lot_after();

drop trigger if exists hx_lot_uses_guard on hx_lot_uses;
create trigger hx_lot_uses_guard before insert or update or delete on hx_lot_uses for each row execute function hx_lot_use_guard();
drop trigger if exists hx_lot_uses_place on hx_lot_uses;
create trigger hx_lot_uses_place before insert or update on hx_lot_uses for each row execute function hx_fl_guard();
drop trigger if exists hx_lot_uses_audit on hx_lot_uses;
create trigger hx_lot_uses_audit after insert or update on hx_lot_uses for each row execute function hx_audit();

drop trigger if exists hx_holds_guard on hx_holds;
create trigger hx_holds_guard before insert or update or delete on hx_holds for each row execute function hx_hold_guard();
drop trigger if exists hx_holds_place on hx_holds;
create trigger hx_holds_place before insert or update on hx_holds for each row execute function hx_fl_guard();
drop trigger if exists hx_holds_audit on hx_holds;
create trigger hx_holds_audit after insert or update on hx_holds for each row execute function hx_audit();

drop trigger if exists hx_shipments_guard on hx_shipments;
create trigger hx_shipments_guard before insert or update or delete on hx_shipments for each row execute function hx_shipment_guard();
drop trigger if exists hx_shipments_place on hx_shipments;
create trigger hx_shipments_place before insert or update on hx_shipments for each row execute function hx_fl_guard();
drop trigger if exists hx_shipments_audit on hx_shipments;
create trigger hx_shipments_audit after insert or update on hx_shipments for each row execute function hx_audit();

alter table hx_lots enable row level security;
alter table hx_lot_uses enable row level security;
alter table hx_holds enable row level security;
alter table hx_shipments enable row level security;
drop policy if exists hx_lots_read on hx_lots;
drop policy if exists hx_lots_insert on hx_lots;
drop policy if exists hx_lots_update on hx_lots;
create policy hx_lots_read   on hx_lots for select to authenticated using (hx_can('receiving',1,license_id) or hx_can('holds',1,license_id));
create policy hx_lots_insert on hx_lots for insert to authenticated with check (hx_can('receiving',2,license_id));
create policy hx_lots_update on hx_lots for update to authenticated using (hx_can('receiving',2,license_id)) with check (hx_can('receiving',2,license_id));
drop policy if exists hx_lot_uses_read on hx_lot_uses;
drop policy if exists hx_lot_uses_insert on hx_lot_uses;
drop policy if exists hx_lot_uses_update on hx_lot_uses;
create policy hx_lot_uses_read   on hx_lot_uses for select to authenticated using (hx_can('receiving',1,license_id) or hx_can('batch',1,license_id));
create policy hx_lot_uses_insert on hx_lot_uses for insert to authenticated with check (hx_can('receiving',2,license_id) or hx_can('batch',2,license_id));
create policy hx_lot_uses_update on hx_lot_uses for update to authenticated using (hx_can('receiving',3,license_id)) with check (hx_can('receiving',3,license_id));
drop policy if exists hx_holds_read on hx_holds;
drop policy if exists hx_holds_insert on hx_holds;
drop policy if exists hx_holds_update on hx_holds;
create policy hx_holds_read   on hx_holds for select to authenticated using (hx_can('holds',1,license_id) or hx_can('receiving',1,license_id) or hx_can('shipping',1,license_id));
create policy hx_holds_insert on hx_holds for insert to authenticated with check (hx_can('holds',2,license_id) or hx_can('receiving',3,license_id));
create policy hx_holds_update on hx_holds for update to authenticated using (hx_can('holds',2,license_id)) with check (hx_can('holds',2,license_id));
drop policy if exists hx_shipments_read on hx_shipments;
drop policy if exists hx_shipments_insert on hx_shipments;
drop policy if exists hx_shipments_update on hx_shipments;
create policy hx_shipments_read   on hx_shipments for select to authenticated using (hx_can('shipping',1,license_id));
create policy hx_shipments_insert on hx_shipments for insert to authenticated with check (hx_can('shipping',2,license_id));
create policy hx_shipments_update on hx_shipments for update to authenticated using (hx_can('shipping',2,license_id)) with check (hx_can('shipping',2,license_id));
grant select, insert, update on hx_lots, hx_lot_uses, hx_holds, hx_shipments to authenticated;
grant execute on function hx_me() to authenticated;

notify pgrst, 'reload schema';
