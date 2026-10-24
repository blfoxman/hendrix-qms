-- =====================================================================
-- Hendrix QMS  -  Step 22: Rulebook PDF import
-- Upload the state's official rules PDF (for example Missouri 19 CSR 100-1,
-- or the Michigan CRA administrative rules) in the Rulebook and Hendrix
-- splits it into rules, sorts them into categories and keeps them in the
-- official order. Uploading a newer PDF later shows what is new / changed
-- and updates the Rulebook.
--   * hx_rules.sort       official order of the rule in its PDF
--   * hx_rules.source_id  the PDF the rule came from (blank = typed by hand)
--   * hx_rule_sources     every PDF imported per state: file kept in the
--                         private hendrix-files bucket, date, who, counts
-- Access module 'rulebook': View (see) / Edit (import, add, edit) /
--   Full (delete rules, remove a PDF from the list).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-21.
-- Safe to run more than once.
-- =====================================================================

alter table hx_rules add column if not exists sort int;
alter table hx_rules add column if not exists source_id text;
create index if not exists hx_rules_state on hx_rules(state_id);

create table if not exists hx_rule_sources (
  id            text primary key,
  state_id      text not null references hx_states(id),
  name          text not null default '',
  file_path     text not null default '',
  pages         int not null default 0,
  format        text not null default '',
  rules_found   int not null default 0,
  added         int not null default 0,
  updated       int not null default 0,
  removed       int not null default 0,
  created_by    uuid default auth.uid(),
  created_by_name text not null default '',
  created_at    timestamptz not null default now()
);
create index if not exists hx_rule_sources_state on hx_rule_sources(state_id);

drop trigger if exists hx_rule_sources_audit on hx_rule_sources;
create trigger hx_rule_sources_audit after insert or update or delete on hx_rule_sources for each row execute function hx_audit();

alter table hx_rule_sources enable row level security;
drop policy if exists hx_rule_sources_read on hx_rule_sources;
drop policy if exists hx_rule_sources_insert on hx_rule_sources;
drop policy if exists hx_rule_sources_update on hx_rule_sources;
drop policy if exists hx_rule_sources_delete on hx_rule_sources;
create policy hx_rule_sources_read   on hx_rule_sources for select to authenticated using (hx_can('rulebook',1));
create policy hx_rule_sources_insert on hx_rule_sources for insert to authenticated with check (hx_can('rulebook',2));
create policy hx_rule_sources_update on hx_rule_sources for update to authenticated using (hx_can('rulebook',2)) with check (hx_can('rulebook',2));
create policy hx_rule_sources_delete on hx_rule_sources for delete to authenticated using (hx_can('rulebook',3));
grant select, insert, update, delete on hx_rule_sources to authenticated;

notify pgrst, 'reload schema';
