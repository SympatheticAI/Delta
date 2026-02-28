#!/usr/bin/env python3
"""Aggregate audit outputs into a single final status report."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
OUT_JSON = REPORTS / "final_status.json"
OUT_MD = REPORTS / "final_status.md"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def main() -> None:
    gauge = load_json(REPORTS / "gauge_invariance_audit_report.json")
    g3 = load_json(REPORTS / "g3_glueball_correlator_summary.json")
    g4 = load_json(REPORTS / "g4_orbit_invariance_summary.json")
    real = load_json(REPORTS / "real_su2_pipeline_summary.json")
    scan = load_json(REPORTS / "real_su2_scaling_scan_summary.json")

    gate_map = {}
    for item in gauge.get("results", []):
        gate_map[item["gate"]] = item["status"]

    final = {
        "G2_floor": gate_map.get("G2_floor", "UNKNOWN"),
        "G3_proxy": gate_map.get("G3_proxy", "UNKNOWN"),
        "G4_orbit_invariance_data_gate": gate_map.get("G4_orbit_invariance", "UNKNOWN"),
        "G5_scaling_identity": gate_map.get("G5_scaling_identity", "UNKNOWN"),
        "G3_correlator_harness": g3.get("status", "UNKNOWN"),
        "G4_orbit_harness": g4.get("status", "UNKNOWN"),
        "real_su2_run_present": "PASS" if bool(real) else "FAIL",
        "real_su2_positive_mass_estimate": "PASS" if real.get("m_eff_positive") else "FAIL",
        "real_su2_scaling_scan": scan.get("status", "UNKNOWN"),
    }

    OUT_JSON.write_text(json.dumps({"gates": final, "real_summary": real}, indent=2))

    lines = ["# Final Status", ""]
    for k, v in final.items():
        lines.append(f"- {k}: `{v}`")
    if real:
        lines.append("")
        lines.append("## Real SU(2) Snapshot")
        lines.append(f"- acceptance_rate: `{real.get('acceptance_rate')}`")
        lines.append(f"- creutz22_mean: `{real.get('creutz22_mean')}`")
        lines.append(f"- gauge_abs_diff_max: `{real.get('gauge_abs_diff_max')}`")
        lines.append(f"- m_eff_cosh_estimate: `{real.get('m_eff_cosh_estimate')}`")
        lines.append(f"- m_eff_positive: `{real.get('m_eff_positive')}`")
    if scan:
        lines.append("")
        lines.append("## Real SU(2) Scaling Scan")
        lines.append(f"- cases: `{scan.get('cases')}`")
        lines.append(f"- mass_positive_cases: `{scan.get('mass_positive_cases')}`")
        lines.append(f"- max_gauge_abs_diff: `{scan.get('max_gauge_abs_diff')}`")
    OUT_MD.write_text("\n".join(lines))
    print(f"Wrote: {OUT_JSON}")
    print(f"Wrote: {OUT_MD}")


if __name__ == "__main__":
    main()
