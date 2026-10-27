#!/bin/bash
# Runs every Hendrix test: database checks (needs PostgreSQL via the normal PG* environment) and all browser suites.
# Usage: tests/run_all.sh            (all)      tests/run_all.sh mat qms   (only those browser suites)
# Env: HX_CHROME=<chromium binary> (optional), HX_SKIP_DB=1 to skip PostgreSQL parts.
cd "$(dirname "$0")"
SUITES=${*:-"up req pw mc off tk sec lm sh im st pp tc mv qs rc haccp cul env lc eq share training online tr_upgrade scope rulebook std ops cmp recall mat suppliers qms sop s t acc b fl3 p2 a w"}
# on GitHub Actions, failures are also written as annotations (readable without the log)
note(){ [ -n "$GITHUB_ACTIONS" ] && echo "::error title=$1::$(echo "$2" | tr '\n' '|' | cut -c1-900)"; return 0; }
FAILED=0; TOTAL=0; LOG=browser/work/summary.log; mkdir -p browser/work; : > $LOG
if [ "$HX_SKIP_DB" != "1" ] && command -v psql >/dev/null; then
  if db/setup_db.sh hxdb > browser/work/setup_hxdb.txt 2>&1; then
    python3 db/check_db.py hxdb > browser/work/check_db.txt 2>&1; tail -1 browser/work/check_db.txt | tee -a $LOG
    grep -q 'DB checks: all passed' browser/work/check_db.txt || { FAILED=1; note "database checks" "$(grep -E 'FAIL|Error|Traceback' browser/work/check_db.txt | head -8)"; }
  else FAILED=1; echo "database setup FAILED" | tee -a $LOG; note "database setup" "$(tail -8 browser/work/setup_hxdb.txt)"; fi
  db/setup_db.sh hxtest > browser/work/setup_hxtest.txt 2>&1 || { FAILED=1; note "database setup (hxtest)" "$(tail -8 browser/work/setup_hxtest.txt)"; }
  export HX_PGDB=hxtest
else
  echo "database checks skipped" | tee -a $LOG; SUITES=$(echo " $SUITES " | sed 's/ lm / /; s/ sh / /; s/ tk / /; s/ off / /; s/ mc / /; s/ req / /')
fi
if command -v node >/dev/null; then
  for ef in notify metrc; do
    eo=$(node --experimental-strip-types --no-warnings edge/test_$ef.mjs 2>&1); echo "$eo" | tail -1 | tee -a $LOG
    echo "$eo" | grep -q ', 0 failed' || { FAILED=1; echo "$eo" > browser/work/fail_edge_$ef.txt; note "hendrix-$ef" "$(echo "$eo" | grep -E '^FAIL|Error' | head -6)"; }
  done
fi
for t in $SUITES; do
  out=$(timeout 900 python3 browser/test_$t.py 2>&1)
  p=$(echo "$out" | grep -c '^PASS'); f=$(echo "$out" | grep -c '^FAIL'); tb=$(echo "$out" | grep -c 'Traceback'); TOTAL=$((TOTAL+p))
  line="$t pass=$p fail=$f$([ $tb -gt 0 ] && echo ' ERROR')"; echo "$line" | tee -a $LOG
  if [ $f -gt 0 ] || [ $tb -gt 0 ] || [ $p -eq 0 ]; then FAILED=1; echo "$out" > browser/work/fail_$t.txt; echo "$out" | grep -E '^FAIL|Error' | head -5; note "suite $t" "$(echo "$out" | grep -E '^FAIL|Error|rror:' | head -6)"; fi
done
echo "browser checks passed: $TOTAL" | tee -a $LOG
[ $FAILED -eq 0 ] && echo "ALL PASSED" || echo "SOME FAILED (see tests/browser/work/fail_*.txt)"
exit $FAILED
