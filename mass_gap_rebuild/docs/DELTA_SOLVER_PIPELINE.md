# Delta Solver Pipeline (De-Infinite -> Closure)

## Core Principle
A problem is solved when a bounded frame closes over a bounded reference.

Pipeline purpose:
- detect unbounded references early,
- rebind or quarantine them,
- run deterministic proof/validation gates,
- close with explicit pass/fail receipts.

## Non-Negotiable Constraints
1. `CRL`: no hidden infinite-precision dependence.
2. `LOW`: prefer lowest-order lawful mechanism with equal predictive power.
3. `Abstention/Theta`: if closure is not lawful, refuse with typed witness.
4. `Audit supremacy`: scores summarize; gates decide.
5. `Chain of custody`: every claim links to artifact, script, and run-card.

## Stage Pipeline

### Stage 0: Intake
Input:
- claim/problem statement
- scope/domain
- success condition

Output:
- `Run Card v0` with one-line Definition-of-Done.

### Stage 1: De-Infinite Audit
Check:
- infinite quantifiers (`all`, `every`, unrestricted universals)
- self-reference loops
- undefined boundary conditions

Route:
- `DIRECT`: already bounded
- `GROUND`: requires rebinding/splitting
- `THETA`: structurally ungroundable in current form

### Stage 2: Rebinding
For each unbounded token:
- `Bind`: replace with finite domain/operator/threshold
- `Split`: separate overloaded terms into explicit senses
- `Quarantine`: mark branch as out-of-domain with witness

Output:
- bounded problem statement with explicit symbols.

### Stage 3: Operator Model
Define:
- state variables
- evolution operators
- invariant observables
- acceptance metrics

Output:
- theorem-facing setup section.

### Stage 4: Gate Suite
Run fixed gates:
- `G-Existence`: construction exists
- `G-Invariance`: symmetry/gauge/orbit invariance
- `G-Gap/Closure`: strict positive closure metric
- `G-Scaling`: persistence under refinement/limit
- `G-Hostile`: red-team reread

### Stage 5: Receipts
Produce:
- markdown report
- machine-readable JSON
- raw tables (CSV)
- one-line verdict per gate

### Stage 6: Theorem Packaging
Write sections:
- statement + assumptions
- lemma chain
- proposition/theorem
- explicit dependency map

### Stage 7: Final Closure
Mark complete only when all submission gates are `PASS`.

## Standard Artifacts (Per Case)
1. `CASE_RUN_CARD.md`
2. `CASE_GATE_CHECKLIST.md`
3. `reports/final_status.md`
4. `reports/submission_ready_status.md`
5. `docs/FINAL_DOSSIER.md`
6. `docs/MASTER_ALL_IN_ONE.md`

## One-Command Discipline
Each case should have:
- one command to run all audits
- one command to summarize readiness

## Practical Rule
Never let narrative outrun gates.
If a gate is open, label it open.
If all gates pass, close it decisively.
