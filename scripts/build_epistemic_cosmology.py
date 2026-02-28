#!/usr/bin/env python3
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'index' / 'canon_curated.ndjson'
OUT = ROOT / 'index'

# Personal epistemic->cosmological spine for Jake.
ORDER = [
    ('deinfinite_core', 'Epistemic Primitive'),
    ('oscillation_diagnostic', 'Diagnostic Primitive'),
    ('why_numbers_are_real', 'Geometric Ontology'),
    ('bedrock_flow_shear', 'Flow-Shear Ontology'),
    ('abstention_crl_bands', 'Finite-Causal Contract'),
    ('shr_and_low', 'Control + Survival Law'),
    ('delta_energy_decision_mdl', 'Lyapunov + Selection Law'),
    ('transport_pins_hats_receipts', 'Objectivity Infrastructure'),
    ('cpl_corridor_hinf', 'Runtime Surface + Portability'),
    ('delta_pinch_and_hinge', 'Convergence Auditor'),
    ('pentad_omega_subtractive_umk', 'Global Sieve + Existence Gate'),
    ('encyclopedia_core_variational_stack', 'Unified Cosmology Core'),
]

# Keep cosmology-relevant lines from the encyclopedia-heavy module for compact view.
COSMOLOGY_KEYWORDS = {
    'cosmology', 'affe', 'mond', 'horizon', 'cavitation', 'gravitational', 'waves',
    'ringdown', 'echo', 'vacuum', 'expansion', 'inflation', 'dark', 'energy', 'rg',
    'renormalization', 'continuum', 'dal', 'hamiltonian', 'lagrangian', 'field',
    'stress', 'tensor', 'phase', 'sediment', 'density', 'closure', 'lyapunov'
}

records = []
with SRC.open('r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line))

by_module = defaultdict(list)
for r in records:
    by_module[r['module']].append(r)

for mod in by_module:
    by_module[mod].sort(key=lambda x: int(x['id'].split('-')[1]))

full_path = OUT / 'canon_epistemic_cosmology_for_jake.md'
core_path = OUT / 'canon_epistemic_cosmology_core_for_jake.md'

with full_path.open('w', encoding='utf-8') as f:
    f.write('# Epistemic Cosmology Canon (For Jake)\n\n')
    f.write('Personal ordering from epistemic foundations to unified cosmology.\n\n')
    sec = 1
    for mod, title in ORDER:
        items = by_module.get(mod, [])
        f.write(f'## {sec}. {title} (`{mod}` | {len(items)} statements)\n')
        for r in items:
            f.write(f'- {r["id"]}: {r["statement"]}\n')
        f.write('\n')
        sec += 1

with core_path.open('w', encoding='utf-8') as f:
    f.write('# Epistemic Cosmology Core (For Jake)\n\n')
    f.write('Compressed cosmology-forward subset for fast re-alignment.\n\n')

    # For non-encyclopedia modules, keep the first 12 statements each (enough signal, low bloat)
    sec = 1
    for mod, title in ORDER:
        items = by_module.get(mod, [])
        if mod == 'encyclopedia_core_variational_stack':
            selected = []
            for r in items:
                text = r['statement'].lower()
                if any(k in text for k in COSMOLOGY_KEYWORDS):
                    selected.append(r)
            # cap to keep core usable
            selected = selected[:220]
        else:
            selected = items[:12]

        f.write(f'## {sec}. {title} (`{mod}` | selected {len(selected)} of {len(items)})\n')
        for r in selected:
            f.write(f'- {r["id"]}: {r["statement"]}\n')
        f.write('\n')
        sec += 1

print(f'Wrote: {full_path}')
print(f'Wrote: {core_path}')
