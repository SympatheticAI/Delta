#!/usr/bin/env python3
"""Run a strict gauge-invariance readiness audit for mass-gap rebuild artifacts."""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"

L2 = DATA / "L2_gauge_covariant.csv"
L4 = DATA / "L4_continuum_scaling.csv"
L5 = DATA / "L5_glueball_spectrum.csv"
WILSON_PROXY = DATA / "delta_wilson_creutz_proxy.csv"

OUT_JSON = REPORTS / "gauge_invariance_audit_report.json"
OUT_MD = REPORTS / "gauge_invariance_audit_report.md"


@dataclass
class GateResult:
    gate: str
    status: str
    summary: str
    details: dict


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def rel_pct(delta: float, base: float) -> float:
    if base == 0:
        return 0.0
    return 100.0 * abs(delta) / abs(base)


def check_g3_proxy(rows_l5: list[dict[str, str]], tol: float = 1e-12) -> GateResult:
    max_w_err = 0.0
    max_creutz_err = 0.0
    max_mass_err = 0.0
    for r in rows_l5:
        delta = float(r["delta"])
        area = float(r["area"])
        w = float(r["Wilson_loop"])
        creutz = float(r["Creutz_ratio"])
        mass_proxy = float(r["mass_proxy"])
        max_w_err = max(max_w_err, abs(w - math.exp(-delta * area)))
        max_creutz_err = max(max_creutz_err, abs(creutz - delta))
        max_mass_err = max(max_mass_err, abs(mass_proxy - math.sqrt(delta)))

    ok = max(max_w_err, max_creutz_err, max_mass_err) <= tol
    return GateResult(
        gate="G3_proxy",
        status="PASS" if ok else "FAIL",
        summary=(
            "Gauge-invariant proxy relations hold in current artifact set."
            if ok
            else "Proxy relations deviate beyond tolerance."
        ),
        details={
            "tolerance": tol,
            "max_abs_err_wilson_exp": max_w_err,
            "max_abs_err_creutz_delta": max_creutz_err,
            "max_abs_err_mass_sqrt_delta": max_mass_err,
        },
    )


def check_g2_floor(rows_l2: list[dict[str, str]]) -> GateResult:
    lambdas = [float(r["lambda_min"]) for r in rows_l2]
    omegas = [float(r["omega0"]) for r in rows_l2]
    a_norms = [float(r["A_norm"]) for r in rows_l2]
    base = omegas[0]
    shifts = [abs(o - base) for o in omegas]
    shift_rel_pct = [rel_pct(s, base) for s in shifts]
    strictly_positive = min(lambdas) > 0.0
    return GateResult(
        gate="G2_floor",
        status="PASS" if strictly_positive else "FAIL",
        summary=(
            "Transverse floor remains strictly positive across tested dressing."
            if strictly_positive
            else "Positive floor not maintained in tested dressing rows."
        ),
        details={
            "A_norm_values": a_norms,
            "lambda_min_range": [min(lambdas), max(lambdas)],
            "omega0_values": omegas,
            "omega0_shift_abs": shifts,
            "omega0_shift_rel_pct": shift_rel_pct,
        },
    )


def check_g5_scaling(rows_l4: list[dict[str, str]], tol: float = 1e-12) -> GateResult:
    max_lat_err = 0.0
    max_phys_err = 0.0
    physical_vals = []
    for r in rows_l4:
        a = float(r["a"])
        omega_lat = float(r["omega0_lattice"])
        omega_phys = float(r["omega0_physical"])
        delta = float(r["delta"])
        max_lat_err = max(max_lat_err, abs(omega_lat - math.sqrt(delta)))
        max_phys_err = max(max_phys_err, abs(omega_phys - (omega_lat / a)))
        physical_vals.append(omega_phys)

    ok = max(max_lat_err, max_phys_err) <= tol
    return GateResult(
        gate="G5_scaling_identity",
        status="PASS" if ok else "FAIL",
        summary=(
            "Current scaling identities are internally exact."
            if ok
            else "Scaling identities deviate beyond tolerance."
        ),
        details={
            "tolerance": tol,
            "max_abs_err_omega_lat_sqrt_delta": max_lat_err,
            "max_abs_err_omega_phys_ratio": max_phys_err,
            "omega0_physical_range": [min(physical_vals), max(physical_vals)],
            "omega0_physical_mean": mean(physical_vals),
        },
    )


def check_g4_orbit_blocker() -> GateResult:
    config_patterns = ("*.npy", "*.npz", "*.h5", "*.hdf5", "*.bin")
    config_files = []
    for pattern in config_patterns:
        config_files.extend(DATA.glob(pattern))
    return GateResult(
        gate="G4_orbit_invariance",
        status="READY" if config_files else "BLOCKED",
        summary=(
            "Raw configuration files detected; orbit test can be executed next."
            if config_files
            else (
                "No raw gauge-link configuration snapshots found in data/; "
                "cannot execute random local gauge-orbit invariance test yet."
            )
        ),
        details={
            "required_inputs": ["raw gauge-link configurations per run"],
            "found_files_count": len(config_files),
            "found_files": [p.name for p in config_files],
        },
    )


def check_duplicate_proxy() -> GateResult:
    same = L5.read_bytes() == WILSON_PROXY.read_bytes()
    return GateResult(
        gate="ARTIFACT_DUPLICATE_CHECK",
        status="INFO",
        summary=(
            "L5_glueball_spectrum.csv is byte-identical to delta_wilson_creutz_proxy.csv."
            if same
            else "L5_glueball_spectrum.csv differs from delta_wilson_creutz_proxy.csv."
        ),
        details={"byte_identical": same},
    )


def render_markdown(results: list[GateResult]) -> str:
    lines = ["# Gauge Invariance Audit Report", ""]
    lines.append("This report is generated from local CSV artifacts only.")
    lines.append("")
    for r in results:
        lines.append(f"## {r.gate}")
        lines.append(f"- Status: `{r.status}`")
        lines.append(f"- Summary: {r.summary}")
        lines.append("- Details:")
        for k, v in r.details.items():
            lines.append(f"  - `{k}`: `{v}`")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    missing = [p for p in (L2, L4, L5, WILSON_PROXY) if not p.exists()]
    if missing:
        raise SystemExit(f"Missing required artifacts: {', '.join(str(m) for m in missing)}")

    rows_l2 = read_csv(L2)
    rows_l4 = read_csv(L4)
    rows_l5 = read_csv(L5)

    results = [
        check_g2_floor(rows_l2),
        check_g3_proxy(rows_l5),
        check_g5_scaling(rows_l4),
        check_g4_orbit_blocker(),
        check_duplicate_proxy(),
    ]
    payload = {
        "report": "gauge_invariance_readiness",
        "artifact_root": str(ROOT),
        "results": [asdict(r) for r in results],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2))
    OUT_MD.write_text(render_markdown(results))
    print(f"Wrote: {OUT_JSON}")
    print(f"Wrote: {OUT_MD}")
    for r in results:
        print(f"{r.gate}: {r.status} - {r.summary}")


if __name__ == "__main__":
    main()
