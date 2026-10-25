create schema if not exists storage; create table if not exists storage.buckets(id text primary key, name text, public boolean); create table if not exists storage.objects(id uuid default gen_random_uuid() primary key, bucket_id text, name text); alter table storage.objects enable row level security;







CREATE TABLE public.hx_rules (
    id text NOT NULL,
    state_id text,
    category text,
    citation text,
    title text,
    body text,
    created_at timestamp with time zone DEFAULT now(),
    sort integer,
    source_id text
);




CREATE TABLE public.hx_visitor_log (
    id text NOT NULL,
    state_id text,
    license_id text,
    visitor_name text,
    company text,
    purpose text,
    host text,
    vehicle text,
    signature text,
    source text DEFAULT 'kiosk'::text,
    time_in timestamp with time zone DEFAULT now(),
    time_out timestamp with time zone,
    edit_reason text,
    voided boolean DEFAULT false NOT NULL,
    void_reason text,
    voided_by uuid,
    voided_at timestamp with time zone,
    gmp_ack boolean DEFAULT false NOT NULL,
    ill boolean,
    ack_at timestamp with time zone
);




GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.hx_rules TO authenticated;



GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.hx_visitor_log TO authenticated;




