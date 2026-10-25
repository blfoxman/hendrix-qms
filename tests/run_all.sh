#!/bin/bash
# Runs every Hendrix test: database checks (needs PostgreSQL via the normal PG* environment) and all browser suites.
# Usage: tests/run_all.sh            (all)      tests/run_all.sh mat qms   (only those browser suites)
# Env: HX_CHROME=<chromium binary> (optional), HX_SKIP_DB=1 to skip PostgreSQL parts.
cd "$(dirname "$0")"
SUITES=${*:-"lm sh im st pp tc mv qs rc haccp cul env lc eq share training online tr_upgrade scope rulebook std ops cmp recall mat suppliers qms sop s t acc b fl3 p2 a w"}
FAILED=0; TOTAL=0; LOG=browser/work/summary.log; mkdir -p browser/work; : > $LOG
if [ "$HX_SKIP_DB" != "1" ] && command -v psql >/dev/null; then
  db/setup_db.sh hxdb >/dev/null && python3 db/check_db.py hxdb | tail -1 | tee -a $LOG || FAILED=1
  db/setup_db.sh hxtest >/dev/null || FAILED=1
  export HX_PGDB=hxtest
else
  echo "database checks skipped" | tee -a $LOG; SUITES=$(echo " $SUITES " | sed 's/ lm / /; s/ sh / /')
fi
for t in $SUITES; do
  out=$(timeout 900 python3 browser/test_$t.py 2>&1)
  p=$(echo "$out" | grep -c '^PASS'); f=$(echo "$out" | grep -c '^FAIL'); tb=$(echo "$out" | grep -c 'Traceback'); TOTAL=$((TOTAL+p))
  line="$t pass=$p fail=$f$([ $tb -gt 0 ] && echo ' ERROR')"; echo "$line" | tee -a $LOG
  if [ $f -gt 0 ] || [ $tb -gt 0 ] || [ $p -eq 0 ]; then FAILED=1; echo "$out" > browser/work/fail_$t.txt; echo "$out" | grep -E '^FAIL|Error' | head -5; fi
done
echo "browser checks passed: $TOTAL" | tee -a $LOG
[ $FAILED -eq 0 ] && echo "ALL PASSED" || echo "SOME FAILED (see tests/browser/work/fail_*.txt)"
exit $FAILED
