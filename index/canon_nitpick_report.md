# Canon Nitpick Report

- Total statements: 2063
- Modules: 17
- Exact duplicate clusters: 0
- Near-duplicate pairs (>=0.92): 2

## Module Counts

- `deinfinite_core`: 23
- `oscillation_diagnostic`: 88
- `abstention_crl_bands`: 149
- `shr_and_low`: 115
- `delta_energy_decision_mdl`: 162
- `dyadic_ladder_e0e4`: 137
- `transport_pins_hats_receipts`: 219
- `delta_pinch_and_hinge`: 95
- `pentad_omega_subtractive_umk`: 182
- `cpl_corridor_hinf`: 179
- `copl_hazard_escalation`: 139
- `bedrock_flow_shear`: 51
- `locks_and_certificates`: 50
- `family_meter_lepton_ledger`: 55
- `baryonic_confinement`: 56
- `why_numbers_are_real`: 109
- `encyclopedia_core_variational_stack`: 254

## Exact Duplicates (Top 25 Clusters)

- None detected (exact normalized-text duplicates).

## Near Duplicates (Top 40 Pairs)

- S-1285 <-> S-1286 (module `transport_pins_hats_receipts`, sim=0.943)
  - A: "Transport falsifier is budget dishonesty with Qhat*Gammahat not approx 1."
  - B: "Transport falsifier is budget dishonesty with Shat+Jhat not approx 1."
- S-1256 <-> S-1257 (module `transport_pins_hats_receipts`, sim=0.942)
  - A: "Merge phase verifies budget honesty Qhat*Gammahat approx 1 inside bands."
  - B: "Merge phase verifies budget honesty Shat+Jhat approx 1 inside bands."

## Manual Nitpick Suggestions

- Standardize symbol naming variants per module (e.g., `DeltaE`, `Delta-Energy`, `Delta E`).
- Normalize threshold spacing (`<=0.01` vs `<= 0.01`) for clean machine diffs.
- Keep one authoritative statement for each invariant; tag alternates as explanatory variants.
- Keep procedural canon in imperative form (`Methods must ...`) for consistency.
