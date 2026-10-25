#!/bin/bash
# Builds a Hendrix test database from nothing: auth stubs + steps 4-12 + the one-file install (13-41),
# runs the install a second time (must be safe), then loads the Line Map demo data.
# Uses the normal psql environment (PGHOST, PGUSER, PGPASSWORD, PGPORT). Database name: $1 (default hxtest).
set -e
DB=${1:-hxtest}
HERE=$(cd "$(dirname "$0")" && pwd); ROOT="$HERE/../.."
psql -X -q -d postgres -c "drop database if exists $DB" -c "create database $DB"
for r in anon authenticated; do psql -X -q -d postgres -tc "select 1 from pg_roles where rolname='$r'" | grep -q 1 || psql -X -q -d postgres -c "create role $r nologin"; done
run(){ out=$(psql -X -q -v ON_ERROR_STOP=1 -d $DB -f "$1" 2>&1) || { echo "FAILED: $1"; echo "$out" | tail -5; exit 1; }; }
run "$HERE/stub2.sql"; run "$HERE/stub3.sql"
for n in 4 5 6 7 8 9 10 11 12; do run "$ROOT/hendrix_step$n.sql"; done
run "$ROOT/hendrix_install_13_to_41.sql"
run "$ROOT/hendrix_install_13_to_41.sql"
psql -X -q -d $DB -f "$HERE/lm_seed.sql" >/dev/null
psql -X -q -d $DB -c "set session_replication_role=replica; update hx_batches set voided=true where id not like 'lm%';"
echo "database $DB ready (steps 4-41, installed twice)"
