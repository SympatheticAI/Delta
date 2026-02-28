#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 "$ROOT/audits/run_gauge_invariance_audit.py"
python3 "$ROOT/audits/run_g4_orbit_invariance_demo.py"
python3 "$ROOT/audits/run_g3_glueball_correlator_demo.py"
python3 "$ROOT/audits/run_real_su2_mass_gap_pipeline.py"
python3 "$ROOT/audits/run_real_su2_scaling_scan.py"

python3 "$ROOT/audits/summarize_audits.py"

echo "All audits complete. See: $ROOT/reports/final_status.md"
