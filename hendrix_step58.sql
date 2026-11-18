-- =====================================================================
-- Hendrix QMS  -  Step 58: Store complaint QR form
--
--   * Complaints > Store QR: a QR code / link per license. Dispensaries scan it and file a
--     complaint without a Hendrix account: store, name, phone or email, product, METRC
--     package tag or lot, what is wrong, description, "someone got sick or hurt", up to 3 photos.
--   * It arrives in Complaints as a new open Dispensary complaint (Adverse event when someone
--     got sick or hurt), received by "QR form", numbered CMP-..., audited, and alerts like any
--     complaint. The store sees its complaint number.
--   * Only through hx_complaint_qr (no table access for anonymous users). At most 20 QR
--     complaints per license per hour.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-57.
-- Safe to run more than once.
-- =====================================================================

alter table hx_complaints add column if not exists qr_photos jsonb not null default '[]'::jsonb;

-- step 19 guard, with one change: the QR form (hx_complaint_qr) may insert without a Hendrix sign-in
create or replace function hx_complaint_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare b record; d record; v_edit boolean := hx_perm('complaints') >= 2; v_full boolean := hx_perm('complaints') >= 3;
begin
  if tg_op = 'DELETE' then raise exception 'Complaints are never deleted. Cancel with a reason.'; end if;
  new.updated_at := now(); new.updated_by := coalesce(hx_me(), new.updated_by);
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
declare v_id text; v_num text; v_ae boolean; v_cat text; v_ph jsonb; v_n int; t text;
begin
  if hx_kiosk_check(p_state, p_lic) is null then raise exception 'This QR code is not linked to an active license.'; end if;
  if coalesce(trim(p->>'store'), '') = '' then raise exception 'Enter the store (dispensary) name.'; end if;
  if coalesce(trim(p->>'name'), '') = '' then raise exception 'Enter your name.'; end if;
  if coalesce(trim(p->>'contact'), '') = '' then raise exception 'Enter a phone number or email so we can reply.'; end if;
  if coalesce(trim(p->>'product'), '') = '' then raise exception 'Enter the product.'; end if;
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
          left(trim(p->>'product'), 200), left(trim(coalesce(p->>'lot', '')), 80), left(upper(regexp_replace(coalesce(p->>'tag', ''), '\s', '', 'g')), 40),
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
