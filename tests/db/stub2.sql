create schema auth;
create function auth.uid() returns uuid language sql stable as $$ select nullif(current_setting('test.uid',true),'')::uuid $$;
grant usage on schema auth to anon, authenticated; grant execute on function auth.uid() to anon,authenticated;
grant usage on schema public to anon, authenticated;
create table hx_profiles(id uuid primary key, name text, email text, role text default 'member', approved boolean default false, created_at timestamptz default now());
create table hx_states(id text primary key, name text, agency text, code text, rules jsonb);
create table hx_licenses(id text primary key, state_id text references hx_states(id), name text, license_number text, license_type text, active boolean default true);
insert into hx_profiles values ('11111111-1111-1111-1111-111111111111','Sam','s@x','admin',true),('22222222-2222-2222-2222-222222222222','Mem','m@x','member',true),('33333333-3333-3333-3333-333333333333','Wait','w@x','member',false);
insert into hx_states values ('st-mo','Missouri'),('st-mi','Michigan');
insert into hx_licenses values ('lic-mo','st-mo','Black Fox','MAN000109','Manufacturer',true),('lic-mi','st-mi','Key Stone','MI-1','Processor',true),('lic-off','st-mo','Old','X','',false);
-- Supabase Auth tables used by step 42 (password reset)
create table auth.users(id uuid primary key, email text, encrypted_password text, updated_at timestamptz);
insert into auth.users(id, email) select id, email from hx_profiles;
create table auth.sessions(id uuid primary key default gen_random_uuid(), user_id uuid);
create table auth.refresh_tokens(id bigserial primary key, user_id varchar(255), token text);
insert into auth.sessions(user_id) values ('22222222-2222-2222-2222-222222222222'),('11111111-1111-1111-1111-111111111111');
insert into auth.refresh_tokens(user_id, token) values ('22222222-2222-2222-2222-222222222222','r1');
