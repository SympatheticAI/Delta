# Yang-Mills Gauge Invariance DoD Card (Delta Ladder)

## Goal
Close the remaining gap from:
- `gauge-covariant lattice spectral floor` (already evidenced)
to:
- `gauge-invariant physical mass gap` suitable for full theorem packaging.

## Definitions of Done (Proof-Targeted)

### DoD-G1: Exact Local Gauge Symmetry
Show all core dynamics and actions are invariant under local site transforms:
- `U_{x,mu} -> g_x U_{x,mu} g_{x+mu}^{-1}`
- `g_x in SU(2)` (and generalizable to `SU(N)`).

Pass condition:
- Theory statements and extracted observables do not depend on gauge choice.

### DoD-G2: Physical Sector (Gauss-Law) Gap
Mass gap statement must be made in the gauge-invariant Hilbert sector, not only a gauge-fixed kernel floor.

Pass condition:
- A strict positive lower bound is shown for gauge-invariant excitation energies.

### DoD-G3: Gauge-Invariant Observables Carry the Gap
Extract mass from gauge-invariant correlators (e.g. glueball channel):
- `C_O(t) = sum_x <O(x,t) O(0)> ~ exp(-m t)`, with gauge-invariant `O` (example: `Tr F^2`).

Pass condition:
- Fitted `m > 0`, stable under volume increase and gauge transformations.

### DoD-G4: Gauge-Orbit Invariance Receipt
Random gauge transforms on configurations leave extracted physics invariant.

Pass condition:
- Invariance of key outputs (`m`, `sigma`, Wilson/Creutz summaries) within tolerance.

### DoD-G5: Continuum-Compatible Packaging
Demonstrate positive physical gap in scaling window as `a -> 0`, while preserving gauge invariance and positivity conditions used by theorem packaging.

Pass condition:
- Continuum scaling run with fixed physical target (`m_*`) and consistent invariant observables.

## Current Status (From Existing CSV Receipts)

### Confirmed
1. `L2_gauge_covariant.csv`: positive floor persists under tested dressing
   - `lambda_min in [0.113774651456590, 0.121000000000000]`
   - `omega0` shifts mildly with `|A|` (about `1.72%` at `0.025`, `3.03%` at `0.05`) but does not close.
2. `L5_glueball_spectrum.csv` (proxy-form):
   - `W = exp(-delta * area)` exact in table
   - `Creutz_ratio = delta` at machine precision
   - `mass_proxy = sqrt(delta)` exact in table
3. `L4_continuum_scaling.csv`:
   - algebraic identities hold exactly for current recipe:
   - `omega0_lattice = sqrt(delta)`
   - `omega0_physical = omega0_lattice / a`

### Not Yet Closed (for full gauge-invariant theorem claim)
1. Gauge-orbit invariance test ledger (explicit before/after random gauge transforms).
2. Gauge-invariant mass extraction from explicit gauge-invariant two-point correlator fits with error bars.
3. Continuum scaling run with `delta(a) = (a m_*)^2` dataset and fixed-physics fit stability across `a`.
4. Final theorem-facing positivity/continuum write-up bridge (OS/reflection-positivity packaging layer).

## Minimal Closure Plan (No Bloat)

1. **Orbit-invariance test**
   - Add a run that applies random local gauge transforms to each saved configuration.
   - Recompute invariant observables and emit delta tables.

2. **Glueball mass fit (invariant channel)**
   - Compute `C_O(t)` for invariant `O`.
   - Fit effective masses `m_eff(t)` and asymptotic `m`.
   - Report volume dependence (`L=8,12,16` or current available ladder).

3. **Continuum window sweep**
   - Use `delta(a)=(a m_*)^2`.
   - Hold physical target fixed and check extracted `m_phys` flatness vs `a`.

4. **Theorem packaging table**
   - One page: assumptions, invariant observables, positivity claim, mass-gap bound, falsifier card.

## Falsifier Card (Crisp)

Claim fails if any of:
1. Gauge transforms change invariant observables beyond tolerance.
2. Extracted gauge-invariant mass tends to zero with increasing volume.
3. Continuum scaling does not preserve a positive physical mass in the declared scaling window.

## Interpretation Guardrail

Current artifacts are strong operational receipts for the Delta ladder and gap mechanism.
For full Clay-style claim language, keep wording strict:
- "operational/lattice gap receipts confirmed"
- "full gauge-invariant continuum packaging in progress"
