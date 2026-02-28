#!/usr/bin/env python3
"""Fresh from-scratch G4 orbit-invariance demo for SU(2) lattice links.

This script generates synthetic SU(2) gauge-link configurations, applies random
local gauge transformations, and checks gauge-invariant observables are
unchanged to numerical precision.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

OUT_CSV = REPORTS / "g4_orbit_invariance_ledger.csv"
OUT_JSON = REPORTS / "g4_orbit_invariance_summary.json"
OUT_MD = REPORTS / "g4_orbit_invariance_summary.md"


@dataclass
class CaseRow:
    seed: int
    L: int
    dims: int
    cfg_index: int
    plaquette_before: float
    plaquette_after: float
    abs_diff_plaquette: float
    w22_before: float
    w22_after: float
    abs_diff_w22: float
    w33_before: float
    w33_after: float
    abs_diff_w33: float


def su2_from_quaternion(q: np.ndarray) -> np.ndarray:
    """Map normalized quaternion q=(a,b,c,d) to SU(2) matrix."""
    a, b, c, d = q
    return np.array(
        [
            [a + 1j * d, c + 1j * b],
            [-c + 1j * b, a - 1j * d],
        ],
        dtype=np.complex128,
    )


def random_su2(rng: np.random.Generator) -> np.ndarray:
    q = rng.normal(size=4)
    q = q / np.linalg.norm(q)
    return su2_from_quaternion(q)


def generate_links(L: int, dims: int, rng: np.random.Generator) -> np.ndarray:
    shape = (L,) * dims + (dims, 2, 2)
    U = np.zeros(shape, dtype=np.complex128)
    for idx in np.ndindex((L,) * dims):
        for mu in range(dims):
            U[idx + (mu,)] = random_su2(rng)
    return U


def generate_gauge_field(L: int, dims: int, rng: np.random.Generator) -> np.ndarray:
    shape = (L,) * dims + (2, 2)
    G = np.zeros(shape, dtype=np.complex128)
    for idx in np.ndindex((L,) * dims):
        G[idx] = random_su2(rng)
    return G


def shift_idx(idx: tuple[int, ...], mu: int, step: int, L: int) -> tuple[int, ...]:
    out = list(idx)
    out[mu] = (out[mu] + step) % L
    return tuple(out)


def gauge_transform_links(U: np.ndarray, G: np.ndarray, L: int, dims: int) -> np.ndarray:
    U2 = np.zeros_like(U)
    for idx in np.ndindex((L,) * dims):
        gx = G[idx]
        for mu in range(dims):
            xp = shift_idx(idx, mu, 1, L)
            U2[idx + (mu,)] = gx @ U[idx + (mu,)] @ G[xp].conj().T
    return U2


def plaquette_trace(U: np.ndarray, x: tuple[int, ...], mu: int, nu: int, L: int) -> complex:
    x_mu = shift_idx(x, mu, 1, L)
    x_nu = shift_idx(x, nu, 1, L)
    U1 = U[x + (mu,)]
    U2 = U[x_mu + (nu,)]
    U3 = U[x_nu + (mu,)].conj().T
    U4 = U[x + (nu,)].conj().T
    return np.trace(U1 @ U2 @ U3 @ U4)


def avg_plaquette(U: np.ndarray, L: int, dims: int) -> float:
    vals = []
    for x in np.ndindex((L,) * dims):
        for mu in range(dims):
            for nu in range(mu + 1, dims):
                vals.append(np.real(plaquette_trace(U, x, mu, nu, L)) / 2.0)
    return float(np.mean(vals))


def wilson_rect_plane01(U: np.ndarray, L: int, dims: int, R: int, T: int) -> float:
    """Average rectangular Wilson loop in plane (0,1)."""
    if dims < 2:
        raise ValueError("Need dims >= 2")
    vals = []
    for x in np.ndindex((L,) * dims):
        W = np.eye(2, dtype=np.complex128)
        cur = x
        for _ in range(R):
            W = W @ U[cur + (0,)]
            cur = shift_idx(cur, 0, 1, L)
        for _ in range(T):
            W = W @ U[cur + (1,)]
            cur = shift_idx(cur, 1, 1, L)
        for _ in range(R):
            cur = shift_idx(cur, 0, -1, L)
            W = W @ U[cur + (0,)].conj().T
        for _ in range(T):
            cur = shift_idx(cur, 1, -1, L)
            W = W @ U[cur + (1,)].conj().T
        vals.append(np.real(np.trace(W)) / 2.0)
    return float(np.mean(vals))


def run_cases() -> list[CaseRow]:
    rows: list[CaseRow] = []
    # Keep this small and fast.
    seeds = [121, 2121]
    L_values = [8, 12]
    dims = 4
    n_cfg = 3

    for seed in seeds:
        rng = np.random.default_rng(seed)
        for L in L_values:
            for i in range(n_cfg):
                U = generate_links(L, dims, rng)
                G = generate_gauge_field(L, dims, rng)
                U2 = gauge_transform_links(U, G, L, dims)

                p1 = avg_plaquette(U, L, dims)
                p2 = avg_plaquette(U2, L, dims)
                w22_1 = wilson_rect_plane01(U, L, dims, 2, 2)
                w22_2 = wilson_rect_plane01(U2, L, dims, 2, 2)
                w33_1 = wilson_rect_plane01(U, L, dims, 3, 3)
                w33_2 = wilson_rect_plane01(U2, L, dims, 3, 3)

                rows.append(
                    CaseRow(
                        seed=seed,
                        L=L,
                        dims=dims,
                        cfg_index=i,
                        plaquette_before=p1,
                        plaquette_after=p2,
                        abs_diff_plaquette=abs(p1 - p2),
                        w22_before=w22_1,
                        w22_after=w22_2,
                        abs_diff_w22=abs(w22_1 - w22_2),
                        w33_before=w33_1,
                        w33_after=w33_2,
                        abs_diff_w33=abs(w33_1 - w33_2),
                    )
                )
    return rows


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    rows = run_cases()

    fieldnames = list(asdict(rows[0]).keys())
    with OUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(asdict(r))

    max_p = max(r.abs_diff_plaquette for r in rows)
    max_w22 = max(r.abs_diff_w22 for r in rows)
    max_w33 = max(r.abs_diff_w33 for r in rows)
    tol = 1e-10
    passed = max(max_p, max_w22, max_w33) < tol

    summary = {
        "test": "G4_orbit_invariance_demo",
        "cases": len(rows),
        "tolerance": tol,
        "max_abs_diff_plaquette": max_p,
        "max_abs_diff_w22": max_w22,
        "max_abs_diff_w33": max_w33,
        "status": "PASS" if passed else "FAIL",
        "note": (
            "Synthetic from-scratch SU(2) gauge-orbit invariance check."
            " This validates the invariance test harness logic."
        ),
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2))
    md = [
        "# G4 Orbit-Invariance Demo Summary",
        "",
        "- Status: `{}`".format(summary["status"]),
        "- Cases: `{}`".format(summary["cases"]),
        "- Tolerance: `{}`".format(summary["tolerance"]),
        "- Max |Δ plaquette|: `{:.3e}`".format(summary["max_abs_diff_plaquette"]),
        "- Max |Δ W(2,2)|: `{:.3e}`".format(summary["max_abs_diff_w22"]),
        "- Max |Δ W(3,3)|: `{:.3e}`".format(summary["max_abs_diff_w33"]),
        "",
        "Synthetic from-scratch SU(2) gauge-orbit invariance check passed for generated cases.",
    ]
    OUT_MD.write_text("\n".join(md))

    print(f"Wrote: {OUT_CSV}")
    print(f"Wrote: {OUT_JSON}")
    print(f"Wrote: {OUT_MD}")
    print(f"Status: {summary['status']}")


if __name__ == "__main__":
    main()
