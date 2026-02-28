#!/usr/bin/env python3
"""Multi-L, multi-beta real SU(2) scaling scan with bootstrap uncertainties."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

OUT_CSV = REPORTS / "real_su2_scaling_scan.csv"
OUT_JSON = REPORTS / "real_su2_scaling_scan_summary.json"
OUT_MD = REPORTS / "real_su2_scaling_scan_summary.md"


def su2_from_quaternion(q: np.ndarray) -> np.ndarray:
    a, b, c, d = q
    return np.array([[a + 1j * d, c + 1j * b], [-c + 1j * b, a - 1j * d]], dtype=np.complex128)


def random_su2(rng: np.random.Generator) -> np.ndarray:
    q = rng.normal(size=4)
    q = q / np.linalg.norm(q)
    return su2_from_quaternion(q)


def random_su2_near_identity(rng: np.random.Generator, eps: float) -> np.ndarray:
    v = rng.normal(size=3)
    n = np.linalg.norm(v)
    axis = np.array([1.0, 0.0, 0.0]) if n < 1e-12 else v / n
    th = eps * rng.uniform(-1.0, 1.0)
    a = math.cos(th)
    s = math.sin(th)
    b, c, d = axis * s
    return su2_from_quaternion(np.array([a, b, c, d]))


def shift_idx(x: tuple[int, int, int, int], mu: int, step: int, L: int) -> tuple[int, int, int, int]:
    y = list(x)
    y[mu] = (y[mu] + step) % L
    return tuple(y)  # type: ignore[return-value]


def init_links(L: int) -> np.ndarray:
    U = np.zeros((L, L, L, L, 4, 2, 2), dtype=np.complex128)
    U[...] = np.eye(2, dtype=np.complex128)
    return U


def staple(U: np.ndarray, x: tuple[int, int, int, int], mu: int, L: int) -> np.ndarray:
    st = np.zeros((2, 2), dtype=np.complex128)
    for nu in range(4):
        if nu == mu:
            continue
        x_nu = shift_idx(x, nu, +1, L)
        x_mu = shift_idx(x, mu, +1, L)
        term_f = U[x + (nu,)] @ U[x_nu + (mu,)] @ U[x_mu + (nu,)].conj().T
        x_mnu = shift_idx(x, nu, -1, L)
        x_mnu_mu = shift_idx(x_mnu, mu, +1, L)
        term_b = U[x_mnu + (nu,)].conj().T @ U[x_mnu + (mu,)] @ U[x_mnu_mu + (nu,)]
        st += term_f + term_b
    return st


def metropolis_sweep(U: np.ndarray, beta: float, eps: float, rng: np.random.Generator) -> tuple[int, int]:
    L = U.shape[0]
    acc = 0
    tot = 0
    for x in np.ndindex((L, L, L, L)):
        x4 = (x[0], x[1], x[2], x[3])
        for mu in range(4):
            old = U[x4 + (mu,)]
            V = staple(U, x4, mu, L)
            cand = random_su2_near_identity(rng, eps) @ old
            dS = -(beta / 2.0) * np.real(np.trace((cand - old) @ V))
            tot += 1
            if dS <= 0.0 or rng.uniform() < np.exp(-dS):
                U[x4 + (mu,)] = cand
                acc += 1
    return acc, tot


def plaquette_trace(U: np.ndarray, x: tuple[int, int, int, int], mu: int, nu: int, L: int) -> complex:
    x_mu = shift_idx(x, mu, +1, L)
    x_nu = shift_idx(x, nu, +1, L)
    return np.trace(U[x + (mu,)] @ U[x_mu + (nu,)] @ U[x_nu + (mu,)].conj().T @ U[x + (nu,)].conj().T)


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


def random_gauge_field(L: int, rng: np.random.Generator) -> np.ndarray:
    G = np.zeros((L, L, L, L, 2, 2), dtype=np.complex128)
    for x in np.ndindex((L, L, L, L)):
        G[x] = random_su2(rng)
    return G


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


def timeslice_spatial_plaquette_sum(U: np.ndarray, t: int) -> float:
    L = U.shape[0]
    sdirs = [1, 2, 3]
    total = 0.0
    n = 0
    for x1 in range(L):
        for x2 in range(L):
            for x3 in range(L):
                x = (t, x1, x2, x3)
                for i in range(3):
                    for j in range(i + 1, 3):
                        total += np.real(plaquette_trace(U, x, sdirs[i], sdirs[j], L)) / 2.0
                        n += 1
    return total / max(n, 1)


def connected_correlator_from_ensemble(ops: np.ndarray) -> np.ndarray:
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
    out = []
    for t in range(1, len(C) - 1):
        if C[t] <= 0:
            out.append(np.nan)
            continue
        arg = (C[t - 1] + C[t + 1]) / (2.0 * C[t])
        if arg < 1.0:
            out.append(np.nan)
            continue
        out.append(float(np.arccosh(arg)))
    return np.array(out)


def mass_from_ops(ops: np.ndarray) -> float:
    C = connected_correlator_from_ensemble(ops)
    meff = effective_mass_cosh(C)
    valid = meff[np.isfinite(meff)]
    return float(np.mean(valid)) if valid.size > 0 else float("nan")


def bootstrap_mass(ops: np.ndarray, rng: np.random.Generator, n_boot: int = 100) -> tuple[float, float, float]:
    n_cfg = ops.shape[0]
    masses = []
    for _ in range(n_boot):
        idx = rng.integers(0, n_cfg, size=n_cfg)
        m = mass_from_ops(ops[idx])
        if np.isfinite(m):
            masses.append(m)
    if not masses:
        return float("nan"), float("nan"), float("nan")
    arr = np.array(masses)
    lo, hi = np.quantile(arr, [0.16, 0.84])
    return float(np.mean(arr)), float(np.std(arr)), float(0.5 * (hi - lo))


def run_case(
    L: int,
    beta: float,
    seed: int,
    n_therm: int = 20,
    n_cfg: int = 20,
    sweeps_between: int = 2,
    n_boot: int = 100,
) -> dict:
    rng = np.random.default_rng(seed)
    U = init_links(L)
    eps = 0.25

    acc = 0
    tot = 0
    for _ in range(n_therm):
        a, t = metropolis_sweep(U, beta, eps, rng)
        acc += a
        tot += t

    plaquettes = []
    creutz = []
    ts_ops = []
    for _ in range(n_cfg):
        for _ in range(sweeps_between):
            a, t = metropolis_sweep(U, beta, eps, rng)
            acc += a
            tot += t
        p = avg_plaquette(U)
        w11 = wilson_loop_plane01(U, 1, 1)
        w22 = wilson_loop_plane01(U, 2, 2)
        w12 = wilson_loop_plane01(U, 1, 2)
        ratio = (w22 * w11) / max(w12 * w12, 1e-15)
        c = -math.log(max(abs(ratio), 1e-15))
        plaquettes.append(p)
        creutz.append(c)
        ts_ops.append(np.array([timeslice_spatial_plaquette_sum(U, t0) for t0 in range(L)], dtype=float))

    G = random_gauge_field(L, rng)
    U2 = gauge_transform(U, G)
    gdiff = max(
        abs(avg_plaquette(U) - avg_plaquette(U2)),
        abs(wilson_loop_plane01(U, 1, 1) - wilson_loop_plane01(U2, 1, 1)),
        abs(wilson_loop_plane01(U, 2, 2) - wilson_loop_plane01(U2, 2, 2)),
    )

    ops_arr = np.array(ts_ops)
    m = mass_from_ops(ops_arr)
    m_boot_mean, m_boot_std, m_boot_halfwidth = bootstrap_mass(ops_arr, rng, n_boot=n_boot)

    return {
        "L": L,
        "beta": beta,
        "seed": seed,
        "acceptance_rate": acc / max(tot, 1),
        "plaquette_mean": float(np.mean(plaquettes)),
        "plaquette_std": float(np.std(plaquettes)),
        "creutz22_mean": float(np.mean(creutz)),
        "creutz22_std": float(np.std(creutz)),
        "gauge_abs_diff_max": float(gdiff),
        "m_eff_cosh_estimate": m,
        "m_boot_mean": m_boot_mean,
        "m_boot_std": m_boot_std,
        "m_boot_ci68_halfwidth": m_boot_halfwidth,
        "n_cfg": n_cfg,
        "m_eff_positive": bool(np.isfinite(m) and m > 0),
    }


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    L_values = [4, 6, 8]
    betas = [2.1, 2.3]
    rows = []
    seed = 121
    for L in L_values:
        for b in betas:
            # Keep runtime controlled as L grows.
            if L <= 6:
                cfg = 20
                therm = 20
                sep = 2
            else:
                cfg = 14
                therm = 14
                sep = 1
            rows.append(
                run_case(
                    L,
                    b,
                    seed=seed,
                    n_therm=therm,
                    n_cfg=cfg,
                    sweeps_between=sep,
                    n_boot=120,
                )
            )
            seed += 1

    with OUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    mass_pos = sum(1 for r in rows if r["m_eff_positive"])
    max_gdiff = max(r["gauge_abs_diff_max"] for r in rows)
    by_beta = {}
    for b in betas:
        sub = [r for r in rows if abs(r["beta"] - b) < 1e-12]
        # Linear fit m(L) ~ m_inf + c/L
        x = np.array([1.0 / r["L"] for r in sub], dtype=float)
        y = np.array([r["m_boot_mean"] for r in sub], dtype=float)
        coeff = np.polyfit(x, y, 1)
        m_inf = float(coeff[1])
        by_beta[str(b)] = {
            "m_inf_linear_1_over_L": m_inf,
            "m_L_values": [float(r["m_boot_mean"]) for r in sub],
            "L_values": [int(r["L"]) for r in sub],
        }

    summary = {
        "cases": len(rows),
        "mass_positive_cases": mass_pos,
        "max_gauge_abs_diff": max_gdiff,
        "beta_fits": by_beta,
        "status": "PASS" if mass_pos == len(rows) and max_gdiff < 1e-10 else "MIXED",
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2))
    lines = [
        "# Real SU(2) Scaling Scan Summary",
        "",
        f"- Cases: `{summary['cases']}`",
        f"- Positive mass cases: `{summary['mass_positive_cases']}`",
        f"- Max gauge-orbit |delta|: `{summary['max_gauge_abs_diff']:.3e}`",
        f"- Status: `{summary['status']}`",
        "",
        f"Data table: `{OUT_CSV.name}`",
        "",
        "## Finite-Size Extrapolation",
    ]
    for b in betas:
        fit = by_beta[str(b)]
        lines.append(f"- beta={b}: m_inf (linear in 1/L) = `{fit['m_inf_linear_1_over_L']}`")
    OUT_MD.write_text("\n".join(lines))
    print(f"Wrote: {OUT_CSV}")
    print(f"Wrote: {OUT_JSON}")
    print(f"Wrote: {OUT_MD}")
    print(f"Status: {summary['status']}")


if __name__ == "__main__":
    main()
