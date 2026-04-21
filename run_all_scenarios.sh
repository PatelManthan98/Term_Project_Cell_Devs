#!/bin/bash
# run_all_scenarios.sh
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
BIN="$ROOT/build/wildfire_sim"

echo "=== Building ==="
bash "$ROOT/build_sim.sh"

if [ ! -f "$BIN" ]; then
    echo "ERROR: build failed, executable not found"; exit 1
fi

mkdir -p "$ROOT/results"

SCENARIOS="calm windy firebreak firebreak_spot urban fortmcmurray_nospot fortmcmurray_spot"

echo ""
echo "=== Running simulations ==="
for NAME in $SCENARIOS; do
    JSON="$ROOT/scenarios/scenario_${NAME}.json"
    LOG="$ROOT/results/grid_log_${NAME}.csv"

    if [ ! -f "$JSON" ]; then
        echo "  SKIP $NAME — scenario file not found"; continue
    fi

    echo "  $NAME ..."
    "$BIN" "$JSON" 500 42
    mv "$ROOT/build/grid_log.csv" "$LOG" 2>/dev/null || \
    mv grid_log.csv "$LOG" 2>/dev/null || true
done

echo ""
echo "=== Visualizing ==="
cd "$ROOT"
python3 visualize_wildfire.py

echo ""
echo "=== Done ==="
ls "$ROOT/results/"*.gif