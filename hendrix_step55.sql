-- =====================================================================
-- Hendrix QMS  -  Step 55: METRC tags on cannabis inventory
--
--   * A received lot in a cannabis category ("Cannabis (flower, trim, biomass)" or
--     "Distillate / extract") needs its METRC package tag: when it is received
--     (by hand or from the Excel upload) and before it can be accepted.
--   * A METRC tag can be on only one live lot of a license (rejected, returned and
--     destroyed lots do not count). Spaces, dashes and case are ignored.
--   * hx_lot_set_tag(): adds the METRC tag to a lot that has none, at any status
--     (Edit access to Receiving) - for lots already in stock. Changing a tag that is
--     already there needs Full access and a reason. Both go to the Audit Trail.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-54.
-- Safe to run more than once.
-- =====================================================================

create or replace function hx_lot_canna(p_cat text) returns boolean
language sql immutable as $$ select coalesce(p_cat, '') in ('Cannabis (flower, trim, biomass)', 'Distillate / extract'); $$;

create or replace function hx_lot_tag_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_other text;
begin
  new.metrc_tag := trim(coalesce(new.metrc_tag, ''));
  if hx_lot_canna(new.category) and new.metrc_tag = '' and new.status not in ('rejected','returned','destroyed')
     and (tg_op = 'INSERT' or (new.status = 'accepted' and old.status <> 'accepted')) then
    raise exception 'A cannabis lot needs its METRC package tag (%).', new.item;
  end if;
  if new.metrc_tag <> '' and new.status not in ('rejected','returned','destroyed')
     and (tg_op = 'INSERT' or hx_tagkey(new.metrc_tag) is distinct from hx_tagkey(old.metrc_tag) or old.status in ('rejected','returned','destroyed')) then
    select number into v_other from hx_lots l where l.license_id = new.license_id and l.id <> new.id and hx_tagkey(l.metrc_tag) = hx_tagkey(new.metrc_tag)
      and l.status not in ('rejected','returned','destroyed') limit 1;
    if v_other is not null then raise exception 'METRC tag % is already on lot %.', new.metrc_tag, v_other; end if;
  end if;
  return new;
end $$;
drop trigger if exists hx_lots_tag on hx_lots;
create trigger hx_lots_tag before insert or update on hx_lots for each row execute function hx_lot_tag_guard();

create or replace function hx_lot_set_tag(p_lot text, p_tag text, p_reason text default '') returns text
language plpgsql volatile security definer set search_path = public as $$
declare l record; v_tag text := trim(coalesce(p_tag, '')); v_why text := trim(coalesce(p_reason, ''));
begin
  select * into l from hx_lots where id = p_lot;
  if l.id is null then raise exception 'Unknown lot.'; end if;
  if not hx_can('receiving', 2, l.license_id) then raise exception 'Adding a METRC tag needs Edit access to Receiving.'; end if;
  if v_tag = '' then raise exception 'Enter the METRC tag.'; end if;
  if hx_tagkey(v_tag) = hx_tagkey(l.metrc_tag) then return l.metrc_tag; end if;
  if trim(l.metrc_tag) <> '' then
    if not hx_can('receiving', 3, l.license_id) then raise exception 'Only Full access to Receiving can change a METRC tag that is already on a lot.'; end if;
    if v_why = '' then raise exception 'Give the reason for changing the METRC tag.'; end if;
  end if;
  perform set_config('hx.internal', 'on', true);
  perform set_config('hx.reason', case when trim(l.metrc_tag) = '' then 'METRC tag added' else 'METRC tag changed from ' || l.metrc_tag || ': ' || v_why end, true);
  update hx_lots set metrc_tag = v_tag where id = p_lot;
  perform set_config('hx.internal', '', true);
  return v_tag;
end $$;
revoke all on function hx_lot_set_tag(text, text, text) from public;
grant execute on function hx_lot_set_tag(text, text, text) to authenticated;
grant execute on function hx_lot_canna(text) to authenticated;

notify pgrst, 'reload schema';
