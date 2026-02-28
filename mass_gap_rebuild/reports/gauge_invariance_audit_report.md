# Gauge Invariance Audit Report

This report is generated from local CSV artifacts only.

## G2_floor
- Status: `PASS`
- Summary: Transverse floor remains strictly positive across tested dressing.
- Details:
  - `A_norm_values`: `[0.0, 0.025, 0.05]`
  - `lambda_min_range`: `[0.11377465145659024, 0.12100000000000036]`
  - `omega0_values`: `[0.3478505426185222, 0.3418637877056238, 0.33730498285170685]`
  - `omega0_shift_abs`: `[0.0, 0.0059867549128984066, 0.010545559766815371]`
  - `omega0_shift_rel_pct`: `[0.0, 1.7210710289056268, 3.0316352785973333]`

## G3_proxy
- Status: `PASS`
- Summary: Gauge-invariant proxy relations hold in current artifact set.
- Details:
  - `tolerance`: `1e-12`
  - `max_abs_err_wilson_exp`: `0.0`
  - `max_abs_err_creutz_delta`: `5.377642775528102e-17`
  - `max_abs_err_mass_sqrt_delta`: `0.0`

## G5_scaling_identity
- Status: `PASS`
- Summary: Current scaling identities are internally exact.
- Details:
  - `tolerance`: `1e-12`
  - `max_abs_err_omega_lat_sqrt_delta`: `3.552713678800501e-15`
  - `max_abs_err_omega_phys_ratio`: `0.0`
  - `omega0_physical_range`: `[0.23190036174568318, 0.6957010852370363]`
  - `omega0_physical_mean`: `0.4035066294374848`

## G4_orbit_invariance
- Status: `BLOCKED`
- Summary: No raw gauge-link configuration snapshots found in data/; cannot execute random local gauge-orbit invariance test yet.
- Details:
  - `required_inputs`: `['raw gauge-link configurations per run']`
  - `found_files_count`: `0`
  - `found_files`: `[]`

## ARTIFACT_DUPLICATE_CHECK
- Status: `INFO`
- Summary: L5_glueball_spectrum.csv is byte-identical to delta_wilson_creutz_proxy.csv.
- Details:
  - `byte_identical`: `True`
