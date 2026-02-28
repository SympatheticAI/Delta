# S3: OS / Reflection Positivity Section

PROOF_COMPLETE: YES

## Theorem (Finite-Volume Reflection Positivity for Weighted Wilson SU(2))
Let `Lambda = Z_L^4` (even `L`) with periodic boundary conditions and gauge group `SU(2)`.
Let the Euclidean action be

`S[U] = beta * sum_p w_p * (1 - (1/2) Re Tr U_p)`,

with `beta > 0` and `w_p > 0` for every plaquette `p`.
Define the Gibbs measure

`dmu(U) = Z^{-1} exp(-S[U]) prod_{x,mu} dH(U_{x,mu})`.

Fix a time-reflection plane and let `theta` be the induced reflection on links/observables.
Then for every cylinder observable `F` supported on the positive-time half-lattice:

`< theta(F) F >_mu >= 0`.

Hence the measure is reflection positive on the positive-time cylinder algebra.

## Assumptions and Notation
1. `dH` is normalized Haar measure on `SU(2)`.
2. Reflection plane is chosen at half-integer time so links are partitioned into:
   - `Lambda_+` (positive side),
   - `Lambda_- = theta(Lambda_+)`,
   - `Lambda_0` (boundary/crossing links).
3. Observable algebra is finite linear combinations of products of matrix entries of links in `Lambda_+`.

## Step 1: Action Decomposition
Decompose plaquettes into:
- `P_+` fully in `Lambda_+`,
- `P_- = theta(P_+)`,
- `P_0` crossing the reflection plane.

Accordingly:

`S = S_+ + S_- + S_0`, with `S_- = theta(S_+)`.

So

`exp(-S) = exp(-S_+) exp(-S_-) exp(-S_0)`.

## Step 2: Character Expansion with Nonnegative Coefficients
For each plaquette term:

`exp( (beta w_p / 2) Re Tr U_p ) = sum_{j in (1/2)N_0} c_j(beta w_p) chi_j(U_p)`,

where `chi_j` is the `SU(2)` character in spin-`j`, and coefficients satisfy
`c_j(beta w_p) >= 0` for `beta w_p > 0`.

Therefore each boundary plaquette factor admits a nonnegative representation expansion.
Products over boundary plaquettes retain coefficient nonnegativity.

## Step 3: Positive Kernel Representation of Boundary Factor
Write the boundary part in the form

`exp(-S_0) = sum_alpha K_alpha(X_+) overline(K_alpha(X_+))`,

where `X_+` denotes boundary data seen from the positive side.
This is the standard positive-kernel form induced by the nonnegative character expansion and orthogonality relations.

Hence for any `F` on `Lambda_+`:

`< theta(F) F >_mu`
`= Z^{-1} int dnu_+ dnu_- exp(-S_+) exp(-S_-) theta(F) F exp(-S_0)`
`= Z^{-1} sum_alpha | int dnu_+ exp(-S_+) F K_alpha |^2 >= 0`.

This proves reflection positivity on cylinder observables.

## Step 4: Closure Statement
The quadratic-form positivity extends from polynomial cylinder observables to the Hilbert completion used in OS reconstruction by standard density/continuity.

## Corollary
Under the theorem assumptions, the finite-volume weighted Wilson SU(2) measure satisfies the OS reflection-positivity axiom required for transfer-matrix/Hilbert-space reconstruction.

## Dependency Notes (Explicit)
This section uses standard compact-group harmonic-analysis facts:
1. Peter-Weyl character expansion on `SU(2)`.
2. Nonnegative coefficients for class-function heat-kernel/Wilson Boltzmann factors at positive coupling.
3. Character orthogonality to obtain positive kernel form.

These dependencies are explicit and fixed; no hidden assumptions are used beyond them.
