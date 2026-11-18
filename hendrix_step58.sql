-- =====================================================================
-- Hendrix QMS  -  Step 58: Store complaint QR form
--
--   * Complaints > Store QR: a QR code / link per license. Dispensaries scan it and file a
--     complaint without a Hendrix account: store, name, phone or email, product, METRC
--     package tag or lot, what is wrong, description, "someone got sick or hurt", up to 3 photos.
--   * It arrives in Complaints as a new open Dispensary complaint (Adverse event when someone
--     got sick or hurt), received by "QR form", numbered CMP-..., audited, and alerts like any
--     complaint. The store sees its complaint number.
--   * The METRC package tag is required: Hendrix checks it against this license's shipments,
--     Testing and batch records and marks every complaint (QR or logged by staff) "Tag verified"
--     (batch, product, shipped to whom) or "Tag not found"; a verified tag links the batch.
--   * Only through hx_complaint_qr (no table access for anonymous users). At most 20 QR
--     complaints per license per hour.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-57.
-- Safe to run more than once.
-- =====================================================================

alter table hx_complaints add column if not exists qr_photos jsonb not null default '[]'::jsonb;
alter table hx_complaints add column if not exists tag_check text not null default '';
alter table hx_complaints add column if not exists tag_check_note text not null default '';

-- is this METRC package tag ours? shipments first (who it went to), then test records, then batch records
create or replace function hx_cmp_tag_find(p_lic text, p_tag text) returns jsonb
language plpgsql stable security definer set search_path = public as $$
declare t text := upper(regexp_replace(coalesce(p_tag, ''), '\s', '', 'g')); r jsonb; b record;
begin
  if t = '' then return null; end if;
  select jsonb_build_object('source', 'shipment', 'shipment', s.number, 'ship_date', s.ship_date, 'customer', s.customer, 'batch_id', nullif(i->>'batch_id', ''),
                            'batch_number', coalesce(i->>'batch_number', ''), 'product', coalesce(i->>'product', ''))
    into r from hx_shipments s, jsonb_array_elements(case when jsonb_typeof(s.items) = 'array' then s.items else '[]'::jsonb end) i
   where s.license_id = p_lic and s.status <> 'cancelled' and upper(regexp_replace(coalesce(i->>'tag', ''), '\s', '', 'g')) = t
   order by s.ship_date desc limit 1;
  if r is null then
    select jsonb_build_object('source', 'test', 'batch_id', x.batch_id, 'batch_number', x.batch_number, 'product', concat_ws(' · ', nullif(x.sku, ''), nullif(x.flavor, '')))
      into r from hx_tests x where x.license_id = p_lic and not coalesce(x.voided, false) and upper(regexp_replace(x.tag, '\s', '', 'g')) = t order by x.created_at desc limit 1;
  end if;
  if r is null then
    select jsonb_build_object('source', 'batch', 'batch_id', bb.id, 'batch_number', bb.batch_number, 'product', concat_ws(' · ', nullif(bb.sku, ''), nullif(bb.flavor, '')))
      into r from hx_batches bb
     where bb.license_id = p_lic and not coalesce(bb.voided, false) and jsonb_typeof(bb.data) = 'object'
       and exists (select 1 from jsonb_each_text(bb.data) e where upper(regexp_replace(e.value, '\s', '', 'g')) = t)
     order by bb.created_at desc limit 1;
  end if;
  if r is null then return null; end if;
  -- only link a batch that really is on this license; fill its number and product when the source had none
  select id, batch_number, sku, flavor into b from hx_batches where id = r->>'batch_id' and license_id = p_lic;
  if b.id is null then r := r || '{"batch_id": null}'::jsonb;
  else
    if coalesce(r->>'batch_number', '') = '' then r := r || jsonb_build_object('batch_number', b.batch_number); end if;
    if coalesce(r->>'product', '') = '' then r := r || jsonb_build_object('product', concat_ws(' · ', nullif(b.sku, ''), nullif(b.flavor, ''))); end if;
  end if;
  return r;
end $$;
revoke all on function hx_cmp_tag_find(text, text) from public, anon;

-- the store form checks the tag while it is typed (only says whether it is ours and the product)
create or replace function hx_complaint_tag_check(p_state text, p_lic text, p_tag text) returns jsonb
language plpgsql stable security definer set search_path = public as $$
declare r jsonb;
begin
  if hx_kiosk_check(p_state, p_lic) is null then raise exception 'This QR code is not linked to an active license.'; end if;
  r := hx_cmp_tag_find(p_lic, p_tag);
  return case when r is null then jsonb_build_object('found', false) else jsonb_build_object('found', true, 'product', coalesce(r->>'product', ''), 'batch_number', coalesce(r->>'batch_number', '')) end;
end $$;
revoke all on function hx_complaint_tag_check(text, text, text) from public;
grant execute on function hx_complaint_tag_check(text, text, text) to anon, authenticated;

-- step 19 guard, with one change: the QR form (hx_complaint_qr) may insert without a Hendrix sign-in
create or replace function hx_complaint_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_t jsonb; b record; d record; v_edit boolean := hx_perm('complaints') >= 2; v_full boolean := hx_perm('complaints') >= 3;
begin
  if tg_op = 'DELETE' then raise exception 'Complaints are never deleted. Cancel with a reason.'; end if;
  new.updated_at := now(); new.updated_by := coalesce(hx_me(), new.updated_by);
  -- step 58: check the METRC package tag against this license's shipments, tests and batches
  new.tag := upper(regexp_replace(coalesce(new.tag, ''), '\s', '', 'g'));
  if new.tag = '' then new.tag_check := ''; new.tag_check_note := '';
  elsif tg_op = 'INSERT' or new.tag is distinct from old.tag then
    v_t := hx_cmp_tag_find(new.license_id, new.tag);
    if v_t is null then
      new.tag_check := 'not_found'; new.tag_check_note := 'This tag is not in this license''s shipments, test records or batch records - check it is our product.';
    else
      new.tag_check := 'verified';
      new.tag_check_note := concat_ws(' · ', nullif('Batch ' || coalesce(v_t->>'batch_number', ''), 'Batch '), nullif(v_t->>'product', ''),
        case when v_t->>'source' = 'shipment' then 'shipped ' || (v_t->>'ship_date') || ' to ' || (v_t->>'customer') || ' (' || (v_t->>'shipment') || ')'
             when v_t->>'source' = 'test' then 'found in Testing' else 'found in the batch record' end);
      if v_t->>'source' = 'shipment' and coalesce(trim(new.customer), '') <> ''
         and not exists (select 1 from regexp_split_to_table(lower(new.customer), '[^a-z0-9]+') w
                          where length(w) >= 4 and w not in ('dispensary', 'dispensaries', 'cannabis', 'store', 'wellness', 'company', 'missouri', 'michigan')
                            and position(w in lower(v_t->>'customer')) > 0) then
        new.tag_check_note := new.tag_check_note || ' · NOTE: shipped to a different customer than ' || new.customer;
      end if;
      if new.batch_id is null and (v_t->>'batch_id') is not null then new.batch_id := v_t->>'batch_id'; end if;
      if coalesce(trim(new.product), '') = '' then new.product := coalesce(v_t->>'product', ''); end if;
    end if;
  end if;
  if new.batch_id is not null then
    select * into b from hx_batches where id = new.batch_id;
    if b.id is null or b.license_id <> new.license_id then raise exception 'That batch belongs to a different license.'; end if;
    if coalesce(trim(new.lot_number),'') = '' then new.lot_number := b.batch_number; end if;
  end if;
  if new.deviation_id is not null then
    select id, number into d from hx_deviations where id = new.deviation_id and license_id = new.license_id;
    if d.id is null then raise exception 'Unknown deviation for this license.'; end if;
    new.deviation_number := d.number;
  end if;
  if new.type <> 'feedback' then new.rating := null; end if;
  if tg_op = 'INSERT' then
    if hx_perm('complaints') < 1 and coalesce(current_setting('hx.cmp_qr', true), '') <> '1' then raise exception 'You need access to Complaints.'; end if;
    if new.received_on > current_date then raise exception 'The received date cannot be in the future.'; end if;
    new.number := hx_next_number('hx_complaints', new.license_id, case when new.type = 'feedback' then 'FBK' else 'CMP' end);
    new.created_by := coalesce(hx_me(), new.created_by); new.created_by_id := auth.uid(); new.created_at := now();
    if new.status not in ('open','investigating') then raise exception 'A new complaint starts open.'; end if;
    new.closed_by := ''; new.closed_at := null; new.cancel_reason := '';
    perform set_config('hx.reason', case when coalesce(current_setting('hx.cmp_qr', true), '') = '1' then 'Complaint filed by a store (QR form)' when new.type = 'feedback' then 'Customer feedback logged' else 'Complaint logged' end, true);
    return new;
  end if;
  if new.number <> old.number or new.created_at <> old.created_at or new.created_by_id is distinct from old.created_by_id or new.license_id <> old.license_id then
    raise exception 'The number, date logged and license of a complaint cannot be changed.';
  end if;
  if old.status in ('closed','cancelled') then
    if not v_full then raise exception 'This complaint is %. Only someone with Full access can reopen it.', old.status; end if;
    if new.status = old.status then raise exception 'This complaint is %. Reopen it first.', old.status; end if;
    new.closed_by := ''; new.closed_at := null; new.cancel_reason := '';
    perform set_config('hx.reason', 'Complaint reopened', true);
    return new;
  end if;
  if not v_edit then raise exception 'You need Edit access to Complaints to investigate.'; end if;
  if new.status = 'cancelled' then
    if not v_full then raise exception 'Only someone with Full access can cancel a complaint.'; end if;
    if coalesce(trim(new.cancel_reason),'') = '' then raise exception 'A reason is required to cancel.'; end if;
    new.closed_by := coalesce(hx_me(),''); new.closed_at := now();
    perform set_config('hx.reason', 'Complaint cancelled: ' || trim(new.cancel_reason), true);
    return new;
  end if;
  if new.status = 'closed' then
    if new.type <> 'feedback' then
      if coalesce(trim(new.investigator),'') = '' then raise exception 'Name who investigated the complaint (CSQ 1.7 a).'; end if;
      if coalesce(trim(new.investigation),'') = '' then raise exception 'Record the investigation before closing.'; end if;
      if coalesce(trim(new.resolution),'') = '' then raise exception 'Record the resolution before closing.'; end if;
      if (coalesce(trim(new.complainant_contact),'') <> '' or coalesce(trim(new.customer),'') <> '') and new.responded_on is null then
        raise exception 'Record when the complainant was answered before closing (CSQ 1.7 a).';
      end if;
      if new.type = 'adverse_event' and new.regulator_reported_on is null then
        raise exception 'An adverse event must be reported to the state regulator before it is closed.';
      end if;
    end if;
    new.closed_by := coalesce(hx_me(),''); new.closed_at := now();
    perform set_config('hx.reason', 'Complaint closed: ' || left(coalesce(nullif(trim(new.resolution),''), 'feedback recorded'), 200), true);
    return new;
  end if;
  if coalesce(current_setting('hx.reason', true), '') = '' then perform set_config('hx.reason', 'Complaint updated', true); end if;
  return new;
end $$;

create or replace function hx_complaint_qr(p_state text, p_lic text, p jsonb) returns text
language plpgsql volatile security definer set search_path = public as $$
declare v_id text; v_num text; v_tag text; v_ae boolean; v_cat text; v_ph jsonb; v_n int; t text;
begin
  if hx_kiosk_check(p_state, p_lic) is null then raise exception 'This QR code is not linked to an active license.'; end if;
  if coalesce(trim(p->>'store'), '') = '' then raise exception 'Enter the store (dispensary) name.'; end if;
  if coalesce(trim(p->>'name'), '') = '' then raise exception 'Enter your name.'; end if;
  if coalesce(trim(p->>'contact'), '') = '' then raise exception 'Enter a phone number or email so we can reply.'; end if;
  if coalesce(trim(p->>'product'), '') = '' then raise exception 'Enter the product.'; end if;
  v_tag := upper(regexp_replace(coalesce(p->>'tag', ''), '\s', '', 'g'));
  if v_tag = '' then raise exception 'Enter the METRC package tag from the package label.'; end if;
  if v_tag !~ '^1A[0-9A-Z]{22}$' then raise exception 'The METRC package tag is 24 characters and starts with 1A - copy it from the package label.'; end if;
  if hx_cmp_tag_find(p_lic, v_tag) is null and not coalesce((p->>'tag_confirmed')::boolean, false) then
    raise exception 'We cannot find this METRC tag in our records. Check the tag on the package label, or tick "The tag is correct" to send anyway.'; end if;
  if length(trim(coalesce(p->>'description', ''))) < 10 then raise exception 'Describe the problem (at least a sentence).'; end if;
  v_cat := coalesce(p->>'category', '');
  if v_cat not in ('', 'Taste / smell', 'Potency / effect', 'Foreign matter', 'Mold / contamination', 'Hardware / packaging failure', 'Labeling', 'Leaking / damage', 'Adverse health effect', 'Delivery / service', 'Other') then
    raise exception 'Unknown category.'; end if;
  v_ae := coalesce((p->>'health')::boolean, false) or v_cat = 'Adverse health effect';
  v_ph := case when jsonb_typeof(p->'photos') = 'array' then p->'photos' else '[]'::jsonb end;
  if jsonb_array_length(v_ph) > 3 then raise exception 'Up to 3 photos.'; end if;
  for t in select jsonb_array_elements_text(v_ph) loop
    if t !~ '^data:image/(jpeg|png|webp);base64,' or length(t) > 900000 then raise exception 'A photo is too large or not an image.'; end if;
  end loop;
  select count(*) into v_n from hx_complaints where license_id = p_lic and channel = 'QR form' and created_at > now() - interval '1 hour';
  if v_n >= 20 then raise exception 'Too many complaints from this QR code in the last hour. Please call or email us instead.'; end if;
  v_id := 'cmp-' || replace(gen_random_uuid()::text, '-', '');
  perform set_config('hx.cmp_qr', '1', true);
  insert into hx_complaints (id, state_id, license_id, received_on, title, type, priority, channel, complainant, complainant_contact, customer, category,
                             product, lot_number, tag, description, status, created_by, qr_photos)
  values (v_id, p_state, p_lic, current_date,
          left(trim(p->>'store') || ': ' || coalesce(nullif(v_cat, ''), 'Complaint') || ' - ' || trim(p->>'product'), 200),
          case when v_ae then 'adverse_event' else 'dispensary' end,
          case when v_ae then 'major' else 'minor' end,
          'QR form', left(trim(p->>'name'), 120), left(trim(p->>'contact'), 160), left(trim(p->>'store'), 160), v_cat,
          left(trim(p->>'product'), 200), left(trim(coalesce(p->>'lot', '')), 80), v_tag,
          left(trim(p->>'description'), 4000)
            || case when coalesce(trim(p->>'purchased'), '') <> '' then E'\nDate of sale / issue: ' || left(trim(p->>'purchased'), 40) else '' end
            || case when v_ae then E'\nThe store reports that someone got sick or hurt.' else '' end,
          'open', 'QR form (' || left(trim(p->>'name'), 80) || ', ' || left(trim(p->>'store'), 80) || ')', v_ph);
  perform set_config('hx.cmp_qr', '', true);
  select number into v_num from hx_complaints where id = v_id;
  -- tell the complaint team (email alert + My Tasks), like a critical complaint
  insert into hx_notify_queue(state_id, license_id, module, kind, title, detail, page, ref)
  select state_id, license_id, 'complaints', 'complaint_store', left('Store complaint ' || number || ': ' || title, 300), left(description, 300), 'complaints', id
    from hx_complaints where id = v_id;
  return v_num;
end $$;
revoke all on function hx_complaint_qr(text, text, jsonb) from public;
grant execute on function hx_complaint_qr(text, text, jsonb) to anon, authenticated;

notify pgrst, 'reload schema';
