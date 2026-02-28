#!/usr/bin/env python3
"""Real (non-synthetic) SU(2) lattice pipeline for mass-gap rebuild.

Produces:
- ensemble observables (plaquette, Wilson loops, Creutz proxy)
- gauge-orbit invariance receipt on measured observables
- connected glueball-like correlator and effective-mass estimate
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
DATA = ROOT / "data"

OUT_ENSEMBLE = REPORTS / "real_su2_ensemble_observables.csv"
OUT_GAUGE = REPORTS / "real_su2_gauge_orbit_receipt.csv"
OUT_CORR = REPORTS / "real_su2_glueball_correlator.csv"
OUT_SUMMARY_JSON = REPORTS / "real_su2_pipeline_summary.json"
OUT_SUMMARY_MD = REPORTS / "real_su2_pipeline_summary.md"


def su2_from_quaternion(q: np.ndarray) -> np.ndarray:
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


def random_su2_near_identity(rng: np.random.Generator, eps: float) -> np.ndarray:
    v = rng.normal(size=3)
    n = np.linalg.norm(v)
    if n < 1e-12:
        axis = np.array([1.0, 0.0, 0.0])
    else:
        axis = v / n
    theta = eps * rng.uniform(-1.0, 1.0)
    a = math.cos(theta)
    s = math.sin(theta)
    b, c, d = axis * s
    return su2_from_quaternion(np.array([a, b, c, d]))


def shift_idx(x: tuple[int, int, int, int], mu: int, step: int, L: int) -> tuple[int, int, int, int]:
    y = list(x)
    y[mu] = (y[mu] + step) % L
    return tuple(y)  # type: ignore[return-value]


def init_links(L: int) -> np.ndarray:
    U = np.zeros((L, L, L, L, 4, 2, 2), dtype=np.complex128)
    I = np.eye(2, dtype=np.complex128)
    U[...] = I
    return U


def staple(U: np.ndarray, x: tuple[int, int, int, int], mu: int, L: int) -> np.ndarray:
    st = np.zeros((2, 2), dtype=np.complex128)
    for nu in range(4):
        if nu == mu:
            continue
        # forward staple
        x_nu = shift_idx(x, nu, +1, L)
        x_mu = shift_idx(x, mu, +1, L)
        term_f = U[x + (nu,)] @ U[x_nu + (mu,)] @ U[x_mu + (nu,)].conj().T

        # backward staple
        x_mnu = shift_idx(x, nu, -1, L)
        x_mnu_mu = shift_idx(x_mnu, mu, +1, L)
        term_b = U[x_mnu + (nu,)].conj().T @ U[x_mnu + (mu,)] @ U[x_mnu_mu + (nu,)]
        st += term_f + term_b
    return st


def metropolis_sweep(U: np.ndarray, beta: float, eps: float, rng: np.random.Generator) -> tuple[int, int]:
    L = U.shape[0]
    accepted = 0
    total = 0
    for x in np.ndindex((L, L, L, L)):
        for mu in range(4):
            x4 = (x[0], x[1], x[2], x[3])
            old = U[x4 + (mu,)]
            V = staple(U, x4, mu, L)
            R = random_su2_near_identity(rng, eps)
            cand = R @ old
            dS = -(beta / 2.0) * np.real(np.trace((cand - old) @ V))
            total += 1
            if dS <= 0.0 or rng.uniform() < np.exp(-dS):
                U[x4 + (mu,)] = cand
                accepted += 1
    return accepted, total


def plaquette_trace(U: np.ndarray, x: tuple[int, int, int, int], mu: int, nu: int, L: int) -> complex:
    x_mu = shift_idx(x, mu, +1, L)
    x_nu = shift_idx(x, nu, +1, L)
    return np.trace(
        U[x + (mu,)] @ U[x_mu + (nu,)] @ U[x_nu + (mu,)].conj().T @ U[x + (nu,)].conj().T
    )


def avg_plaquette(U: np.ndarray) -> float:
    L = U.shape[0]
    vals = []
    for x in np.ndindex((L, L, L, L)):
        x4 = (x[0], x[1], x[2], x[3])
        for mu in range(4):
            for nu in range(mu + 1, 4):
                vals.append(np.real(plaquette_trace(U, x4, mu, nu, L)) / 2.0)
    return float(np.mean(vals))


def wilson_loop_plane01(U: np.ndarray, R: int, T: int) -> float:
    L = U.shape[0]
    vals = []
    for x in np.ndindex((L, L, L, L)):
        cur = (x[0], x[1], x[2], x[3])
        W = np.eye(2, dtype=np.complex128)
        for _ in range(R):
            W = W @ U[cur + (1,)]
            cur = shift_idx(cur, 1, +1, L)
        for _ in range(T):
            W = W @ U[cur + (0,)]
            cur = shift_idx(cur, 0, +1, L)
        for _ in range(R):
            cur = shift_idx(cur, 1, -1, L)
            W = W @ U[cur + (1,)].conj().T
        for _ in range(T):
            cur = shift_idx(cur, 0, -1, L)
            W = W @ U[cur + (0,)].conj().T
        vals.append(np.real(np.trace(W)) / 2.0)
    return float(np.mean(vals))


def gauge_transform(U: np.ndarray, G: np.ndarray) -> np.ndarray:
    L = U.shape[0]
    out = np.zeros_like(U)
    for x in np.ndindex((L, L, L, L)):
        x4 = (x[0], x[1], x[2], x[3])
        gx = G[x4]
        for mu in range(4):
            xp = shift_idx(x4, mu, +1, L)
            out[x4 + (mu,)] = gx @ U[x4 + (mu,)] @ G[xp].conj().T
    return out


def random_gauge_field(L: int, rng: np.random.Generator) -> np.ndarray:
    G = np.zeros((L, L, L, L, 2, 2), dtype=np.complex128)
    for x in np.ndindex((L, L, L, L)):
        G[x] = random_su2(rng)
    return G


def timeslice_spatial_plaquette_sum(U: np.ndarray, t: int) -> float:
    L = U.shape[0]
    # spatial directions 1,2,3
    sdirs = [1, 2, 3]
    total = 0.0
    count = 0
    for x1 in range(L):
        for x2 in range(L):
            for x3 in range(L):
                x = (t, x1, x2, x3)
                for i in range(3):
                    for j in range(i + 1, 3):
                        mu = sdirs[i]
                        nu = sdirs[j]
                        total += np.real(plaquette_trace(U, x, mu, nu, L)) / 2.0
                        count += 1
    return total / max(count, 1)


def connected_correlator_from_ensemble(ops: np.ndarray) -> np.ndarray:
    # ops shape: (n_cfg, Lt)
    n_cfg, Lt = ops.shape
    mu = np.mean(ops)
    C = np.zeros(Lt, dtype=float)
    for dt in range(Lt):
        acc = 0.0
        n = 0
        for c in range(n_cfg):
            for t in range(Lt):
                acc += (ops[c, t] - mu) * (ops[c, (t + dt) % Lt] - mu)
                n += 1
        C[dt] = acc / max(n, 1)
    return C


def effective_mass_cosh(C: np.ndarray) -> np.ndarray:
    vals = []
    for t in range(1, len(C) - 1):
        if C[t] <= 0:
            vals.append(np.nan)
            continue
        arg = (C[t - 1] + C[t + 1]) / (2.0 * C[t])
        if arg < 1.0:
            vals.append(np.nan)
            continue
        vals.append(float(np.arccosh(arg)))
    return np.array(vals)


@dataclass
class ObsRow:
    cfg_index: int
    plaquette: float
    w11: float
    w22: float
    creutz_22: float


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(121)
    L = 6
    beta = 2.3
    eps = 0.25
    n_therm = 25
    n_cfg = 30
    sweeps_between = 3

    U = init_links(L)

    # Thermalization
    acc_sum = 0
    tot_sum = 0
    for _ in range(n_therm):
        a, t = metropolis_sweep(U, beta=beta, eps=eps, rng=rng)
        acc_sum += a
        tot_sum += t

    # Measurement ensemble
    rows: list[ObsRow] = []
    timeslice_ops = []
    for i in range(n_cfg):
        for _ in range(sweeps_between):
            a, t = metropolis_sweep(U, beta=beta, eps=eps, rng=rng)
            acc_sum += a
            tot_sum += t

        p = avg_plaquette(U)
        w11 = wilson_loop_plane01(U, 1, 1)
        w22 = wilson_loop_plane01(U, 2, 2)
        w12 = wilson_loop_plane01(U, 1, 2)
        ratio = (w22 * w11) / max(w12 * w12, 1e-15)
        creutz = -math.log(max(abs(ratio), 1e-15))
        rows.append(ObsRow(cfg_index=i, plaquette=p, w11=w11, w22=w22, creutz_22=creutz))

        op_t = np.array([timeslice_spatial_plaquette_sum(U, t0) for t0 in range(L)], dtype=float)
        timeslice_ops.append(op_t)

    # Save ensemble observables
    with OUT_ENSEMBLE.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for r in rows:
            writer.writerow(asdict(r))

    # Gauge-orbit invariance test on final configuration
    G = random_gauge_field(L, rng)
    U2 = gauge_transform(U, G)
    p1, p2 = avg_plaquette(U), avg_plaquette(U2)
    w11_1, w11_2 = wilson_loop_plane01(U, 1, 1), wilson_loop_plane01(U2, 1, 1)
    w22_1, w22_2 = wilson_loop_plane01(U, 2, 2), wilson_loop_plane01(U2, 2, 2)
    with OUT_GAUGE.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "observable",
                "before",
                "after",
                "abs_diff",
            ],
        )
        writer.writeheader()
        writer.writerow({"observable": "plaquette", "before": p1, "after": p2, "abs_diff": abs(p1 - p2)})
        writer.writerow({"observable": "W11", "before": w11_1, "after": w11_2, "abs_diff": abs(w11_1 - w11_2)})
        writer.writerow({"observable": "W22", "before": w22_1, "after": w22_2, "abs_diff": abs(w22_1 - w22_2)})

    # Correlator from ensemble
    ops = np.array(timeslice_ops)  # (n_cfg, Lt=L)
    C = connected_correlator_from_ensemble(ops)
    meff = effective_mass_cosh(C)
    meff_clean = meff[np.isfinite(meff)]
    m_est = float(np.mean(meff_clean)) if meff_clean.size >= 1 else float("nan")
    with OUT_CORR.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["dt", "C_dt", "m_eff_cosh"])
        writer.writeheader()
        for dt in range(L):
            mval = meff[dt - 1] if 1 <= dt <= L - 2 else np.nan
            writer.writerow({"dt": dt, "C_dt": float(C[dt]), "m_eff_cosh": float(mval) if np.isfinite(mval) else ""})

    acc_rate = acc_sum / max(tot_sum, 1)
    plaquettes = [r.plaquette for r in rows]
    creutz_vals = [r.creutz_22 for r in rows]

    summary = {
        "run_type": "real_su2_metropolis",
        "lattice_size": L,
        "beta": beta,
        "proposal_eps": eps,
        "n_thermal_sweeps": n_therm,
        "n_configs": n_cfg,
        "sweeps_between": sweeps_between,
        "acceptance_rate": acc_rate,
        "plaquette_mean": float(np.mean(plaquettes)),
        "plaquette_std": float(np.std(plaquettes)),
        "creutz22_mean": float(np.mean(creutz_vals)),
        "creutz22_std": float(np.std(creutz_vals)),
        "gauge_abs_diff_max": float(max(abs(p1 - p2), abs(w11_1 - w11_2), abs(w22_1 - w22_2))),
        "m_eff_cosh_estimate": m_est,
        "m_eff_positive": bool(np.isfinite(m_est) and m_est > 0),
    }
    OUT_SUMMARY_JSON.write_text(json.dumps(summary, indent=2))
    md = [
        "# Real SU(2) Pipeline Summary",
        "",
        f"- Lattice: `L={L}` (4D)",
        f"- Beta: `{beta}`",
        f"- Acceptance rate: `{acc_rate:.4f}`",
        f"- Plaquette mean ± std: `{summary['plaquette_mean']:.6f} ± {summary['plaquette_std']:.6f}`",
        f"- Creutz(2,2) mean ± std: `{summary['creutz22_mean']:.6f} ± {summary['creutz22_std']:.6f}`",
        f"- Gauge-orbit max |delta|: `{summary['gauge_abs_diff_max']:.3e}`",
        f"- Glueball-like m_eff(cosh) estimate: `{summary['m_eff_cosh_estimate']}`",
        f"- Positive mass estimate: `{summary['m_eff_positive']}`",
    ]
    OUT_SUMMARY_MD.write_text("\n".join(md))

    print(f"Wrote: {OUT_ENSEMBLE}")
    print(f"Wrote: {OUT_GAUGE}")
    print(f"Wrote: {OUT_CORR}")
    print(f"Wrote: {OUT_SUMMARY_JSON}")
    print(f"Wrote: {OUT_SUMMARY_MD}")


if __name__ == "__main__":
    main()
