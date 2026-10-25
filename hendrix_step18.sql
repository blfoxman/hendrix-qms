-- =====================================================================
-- Hendrix QMS  -  Step 18: Traceability and Recall (CSQ 1.8, 1.11, 2A.10.1)
--   * Trace any received lot, batch or package tag one step back (supplier,
--     supplier lot, COA) and one step forward (batches that used it, shipments,
--     customers), with quantities made, shipped, on hand and on hold.
--   * Recall team and contact list per license: team with roles, emergency
--     services, customers, suppliers, regulators, certification body, lab;
--     each contact has a "verified on" date (kept up to date yearly).
--   * Mock recalls, recalls and withdrawals (MOCK-YYYY-### / RCL-YYYY-###):
--     the clock starts on the server when the exercise starts and stops when it
--     is closed, so the duration cannot be edited. A mock recall passes only
--     when every step is done within 2 hours. Real recalls and withdrawals
--     are started and closed by Full access. Never deleted (cancel with reason).
-- Access module 'recall': View / Edit (contacts, run mock recalls) / Full
--   (start and close real recalls and withdrawals, cancel).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-17.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_recall_contacts (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  kind          text not null default 'team' check (kind in ('team','emergency','regulator','certification','customer','supplier','lab','other')),
  name          text not null check (length(trim(name)) > 0),
  role          text not null default '',
  organization  text not null default '',
  phone         text not null default '',
  after_hours   text not null default '',
  email         text not null default '',
  notes         text not null default '',
  is_backup     boolean not null default false,
  verified_on   date,
  active        boolean not null default true,
  sort          int not null default 0,
  updated_by    text not null default '',
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
create index if not exists hx_recall_contacts_lic on hx_recall_contacts(license_id, kind);

create table if not exists hx_recalls (
  id                 text primary key,
  state_id           text not null references hx_states(id),
  license_id         text not null references hx_licenses(id),
  number             text not null default '',
  kind               text not null default 'mock' check (kind in ('mock','recall','withdrawal')),
  recall_class       text not null default '',
  target_type        text not null default 'batch' check (target_type in ('lot','batch','tag')),
  target_id          text not null default '',
  target_label       text not null default '',
  reason             text not null default '',
  started_at         timestamptz not null default now(),
  ended_at           timestamptz,
  duration_minutes   int,
  steps              jsonb not null default '{}'::jsonb,
  step_times         jsonb not null default '{}'::jsonb,
  notified           jsonb not null default '[]'::jsonb,
  trace              jsonb not null default '{}'::jsonb,
  qty_made           text not null default '',
  qty_shipped        text not null default '',
  qty_on_hand        text not null default '',
  qty_recovered      text not null default '',
  findings           text not null default '',
  actions            text not null default '',
  files              jsonb not null default '[]'::jsonb,
  status             text not null default 'open' check (status in ('open','closed','cancelled')),
  result             text not null default '',
  cancel_reason      text not null default '',
  started_by         text not null default '',
  started_by_id      uuid default auth.uid(),
  closed_by          text not null default '',
  updated_at         timestamptz not null default now()
);
create unique index if not exists hx_recalls_number on hx_recalls(license_id, number);
create index if not exists hx_recalls_lic on hx_recalls(license_id, started_at desc);

create or replace function hx_recall_contact_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then
    if hx_perm('recall') < 3 then raise exception 'Only someone with Full access to Recall can delete a contact. Switch it off instead.'; end if;
    return old;
  end if;
  new.updated_at := now(); new.updated_by := coalesce(hx_me(), new.updated_by);
  if tg_op = 'INSERT' then new.created_at := now(); end if;
  if new.verified_on is not null and new.verified_on > current_date then raise exception 'The verified date cannot be in the future.'; end if;
  if coalesce(current_setting('hx.reason', true), '') = '' then
    perform set_config('hx.reason', case when tg_op = 'INSERT' then 'Recall contact added' when new.verified_on is distinct from old.verified_on then 'Contact verified' else 'Recall contact updated' end, true);
  end if;
  return new;
end $$;

create or replace function hx_recall_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_full boolean := hx_perm('recall') >= 3; v_edit boolean := hx_perm('recall') >= 2; v_all boolean; k text;
begin
  if tg_op = 'DELETE' then raise exception 'Recall records are never deleted. Cancel with a reason.'; end if;
  new.updated_at := now();
  if tg_op = 'INSERT' then
    if new.kind = 'mock' and not v_edit then raise exception 'You need Edit access to Recall to start a mock recall.'; end if;
    if new.kind <> 'mock' and not v_full then raise exception 'Only someone with Full access to Recall can start a recall or withdrawal.'; end if;
    if coalesce(trim(new.target_label),'') = '' then raise exception 'Pick the lot, batch or package tag to trace.'; end if;
    if new.kind <> 'mock' and coalesce(trim(new.reason),'') = '' then raise exception 'Write the reason for the recall.'; end if;
    new.number := hx_next_number('hx_recalls', new.license_id, case when new.kind = 'mock' then 'MOCK' else 'RCL' end);
    new.started_at := now(); new.ended_at := null; new.duration_minutes := null; new.status := 'open'; new.result := ''; new.cancel_reason := ''; new.closed_by := '';
    new.started_by := coalesce(hx_me(), new.started_by); new.started_by_id := auth.uid();
    perform set_config('hx.reason', case new.kind when 'mock' then 'Mock recall started: ' else initcap(new.kind) || ' started: ' end || new.target_label, true);
    return new;
  end if;
  if new.number <> old.number or new.kind <> old.kind or new.started_at <> old.started_at or new.started_by_id is distinct from old.started_by_id
     or new.target_type <> old.target_type or new.target_id <> old.target_id or new.license_id <> old.license_id then
    raise exception 'The number, type, start time and traced product of a recall cannot be changed.';
  end if;
  if old.status <> 'open' then raise exception 'This % is % and cannot be changed.', case old.kind when 'mock' then 'mock recall' else old.kind end, old.status; end if;
  if not v_edit then raise exception 'You need Edit access to Recall.'; end if;
  -- stamp the time each step is first ticked
  for k in select key from jsonb_each(new.steps) where value = 'true'::jsonb loop
    if not (old.steps ? k and old.steps->k = 'true'::jsonb) then new.step_times := new.step_times || jsonb_build_object(k, to_char(now() at time zone 'utc', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')); end if;
  end loop;
  if new.status = 'cancelled' then
    if not v_full then raise exception 'Only someone with Full access to Recall can cancel.'; end if;
    if coalesce(trim(new.cancel_reason),'') = '' then raise exception 'A reason is required to cancel.'; end if;
    new.ended_at := now(); new.closed_by := coalesce(hx_me(),'');
    perform set_config('hx.reason', 'Cancelled: ' || trim(new.cancel_reason), true);
    return new;
  end if;
  if new.status = 'closed' then
    if old.kind <> 'mock' and not v_full then raise exception 'Only someone with Full access to Recall can close a recall or withdrawal.'; end if;
    if coalesce(trim(new.findings),'') = '' then raise exception 'Write the findings before closing.'; end if;
    new.ended_at := now(); new.closed_by := coalesce(hx_me(),'');
    new.duration_minutes := ceil(extract(epoch from (new.ended_at - new.started_at)) / 60.0)::int;
    v_all := not exists (select 1 from jsonb_each(new.steps) s where s.value <> 'true'::jsonb) and new.steps <> '{}'::jsonb;
    if old.kind = 'mock' then
      new.result := case when v_all and new.duration_minutes <= 120 then 'Pass' else 'Fail' end;
    else
      if not v_all then raise exception 'Complete every recall step before closing.'; end if;
      new.result := 'Completed';
    end if;
    perform set_config('hx.reason', 'Closed in ' || new.duration_minutes || ' min' || case when new.result <> '' then ' - ' || new.result else '' end, true);
    return new;
  end if;
  new.ended_at := null; new.duration_minutes := null; new.result := '';
  if coalesce(current_setting('hx.reason', true), '') = '' then perform set_config('hx.reason', 'Recall progress updated', true); end if;
  return new;
end $$;

-- everything needed to trace, for people with Recall access (they may not have Receiving or Shipping access)
create or replace function hx_trace_data(p_lic text) returns jsonb
language sql stable security definer set search_path = public as $$
  select case when not hx_can('recall',1,p_lic) then null else jsonb_build_object(
    'lots', coalesce((select jsonb_agg(jsonb_build_object('id',id,'number',number,'received_on',received_on,'supplier_id',supplier_id,'supplier_name',supplier_name,'item',item,'category',category,
              'supplier_lot',supplier_lot,'metrc_tag',metrc_tag,'quantity',quantity,'unit',unit,'qty_used',qty_used,'status',status,'coa_ok',coa_ok,'expiry_date',expiry_date,'location',location)) from hx_lots where license_id = p_lic), '[]'::jsonb),
    'uses', coalesce((select jsonb_agg(jsonb_build_object('id',id,'lot_id',lot_id,'batch_id',batch_id,'batch_number',batch_number,'quantity',quantity,'used_on',used_on)) from hx_lot_uses where license_id = p_lic and not voided), '[]'::jsonb),
    'batches', coalesce((select jsonb_agg(jsonb_build_object('id',id,'batch_number',batch_number,'batch_type',batch_type,'sku',sku,'flavor',flavor,'created_at',created_at,'status',status)) from hx_batches where license_id = p_lic and not voided), '[]'::jsonb),
    'tests', coalesce((select jsonb_agg(jsonb_build_object('id',id,'batch_id',batch_id,'tag',tag,'sample_tag',sample_tag,'status',status,'lab_name',lab_name,'created_at',created_at)) from hx_tests where license_id = p_lic and not voided), '[]'::jsonb),
    'ships', coalesce((select jsonb_agg(jsonb_build_object('id',id,'number',number,'ship_date',ship_date,'customer',customer,'customer_license',customer_license,'destination',destination,'manifest_number',manifest_number,'items',items,'status',status,'delivered_on',delivered_on)) from hx_shipments where license_id = p_lic and status <> 'cancelled'), '[]'::jsonb),
    'holds', coalesce((select jsonb_agg(jsonb_build_object('id',id,'number',number,'kind',kind,'lot_id',lot_id,'batch_id',batch_id,'tag',tag,'status',status,'quantity',quantity,'source',source,'reason',reason)) from hx_holds where license_id = p_lic), '[]'::jsonb),
    'suppliers', coalesce((select jsonb_agg(jsonb_build_object('id',id,'name',name,'status',status,'contact_name',contact_name,'contact_email',contact_email,'contact_phone',contact_phone)) from hx_suppliers where p_lic = any(license_ids)), '[]'::jsonb))
  end;
$$;
grant execute on function hx_trace_data(text) to authenticated;

drop trigger if exists hx_recall_contacts_guard on hx_recall_contacts;
create trigger hx_recall_contacts_guard before insert or update or delete on hx_recall_contacts for each row execute function hx_recall_contact_guard();
drop trigger if exists hx_recall_contacts_place on hx_recall_contacts;
create trigger hx_recall_contacts_place before insert or update on hx_recall_contacts for each row execute function hx_fl_guard();
drop trigger if exists hx_recall_contacts_audit on hx_recall_contacts;
create trigger hx_recall_contacts_audit after insert or update or delete on hx_recall_contacts for each row execute function hx_audit();
drop trigger if exists hx_recalls_guard on hx_recalls;
create trigger hx_recalls_guard before insert or update or delete on hx_recalls for each row execute function hx_recall_guard();
drop trigger if exists hx_recalls_place on hx_recalls;
create trigger hx_recalls_place before insert or update on hx_recalls for each row execute function hx_fl_guard();
drop trigger if exists hx_recalls_audit on hx_recalls;
create trigger hx_recalls_audit after insert or update on hx_recalls for each row execute function hx_audit();

alter table hx_recall_contacts enable row level security;
alter table hx_recalls enable row level security;
drop policy if exists hx_recall_contacts_read on hx_recall_contacts;
drop policy if exists hx_recall_contacts_insert on hx_recall_contacts;
drop policy if exists hx_recall_contacts_update on hx_recall_contacts;
drop policy if exists hx_recall_contacts_delete on hx_recall_contacts;
create policy hx_recall_contacts_read   on hx_recall_contacts for select to authenticated using (hx_can('recall',1,license_id));
create policy hx_recall_contacts_insert on hx_recall_contacts for insert to authenticated with check (hx_can('recall',2,license_id));
create policy hx_recall_contacts_update on hx_recall_contacts for update to authenticated using (hx_can('recall',2,license_id)) with check (hx_can('recall',2,license_id));
create policy hx_recall_contacts_delete on hx_recall_contacts for delete to authenticated using (hx_can('recall',3,license_id));
drop policy if exists hx_recalls_read on hx_recalls;
drop policy if exists hx_recalls_insert on hx_recalls;
drop policy if exists hx_recalls_update on hx_recalls;
create policy hx_recalls_read   on hx_recalls for select to authenticated using (hx_can('recall',1,license_id));
create policy hx_recalls_insert on hx_recalls for insert to authenticated with check (hx_can('recall',2,license_id));
create policy hx_recalls_update on hx_recalls for update to authenticated using (hx_can('recall',2,license_id)) with check (hx_can('recall',2,license_id));
grant select, insert, update, delete on hx_recall_contacts to authenticated;
grant select, insert, update on hx_recalls to authenticated;

notify pgrst, 'reload schema';
