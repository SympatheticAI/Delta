#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path('/Users/jakeaaron/Soliton Mechanics/Truth Ledger')
SRC = ROOT / 'index' / 'canon_curated.ndjson'
OUT = ROOT / 'index' / 'canon_cosmology_spine_tight_for_jake.md'

records = {}
with SRC.open('r', encoding='utf-8') as f:
    for line in f:
        if not line.strip():
            continue
        r = json.loads(line)
        records[r['id']] = r


def seq(a: int, b: int):
    return [f'S-{i:04d}' for i in range(a, b + 1)]

SECTIONS = [
    (
        'Scope And Inclusion Rule',
        'Keep only cosmological ontology, dynamics, regimes, and observables. Exclude solver/control machinery unless it is structurally required for cosmology claims.',
        ['S-0001', 'S-0002', 'S-0006', 'S-0011'],
    ),
    (
        'Substrate Ontology',
        'One-substrate flow/shear bedrock and the five-field primitive inventory.',
        seq(24, 29)
        + ['S-1825', 'S-1826', 'S-1827', 'S-1829', 'S-1831', 'S-1834', 'S-1835', 'S-1838', 'S-1839'],
    ),
    (
        'Unified Action And Field Equations',
        'Minimal action decomposition and Euler-Lagrange closure.',
        ['S-1840', 'S-1841', 'S-1842', 'S-1844', 'S-1845', 'S-1846', 'S-1847', 'S-1848', 'S-1849', 'S-1850', 'S-1852', 'S-1853', 'S-1854', 'S-1855'],
    ),
    (
        'Canonical And Quantum Layer',
        'Hamiltonian structure and quantized suppression hierarchy.',
        ['S-1856', 'S-1857', 'S-1860', 'S-1861', 'S-1862', 'S-1863', 'S-1866', 'S-1871', 'S-1872', 'S-1874', 'S-1875', 'S-1876'],
    ),
    (
        'AFFE Gravity Core',
        'Gravity as sediment-sourced vacuum reflow with time-density coupling.',
        seq(1877, 1886),
    ),
    (
        'Stress Tensor And Emergent MOND Regime',
        'Weak-field enhancement from vacuum elasticity without dark-matter add-ons.',
        seq(1887, 1893),
    ),
    (
        'Strong-Field Cavitation And Horizon Structure',
        'Finite-saturation collapse, memory interior, and non-singular horizon physics.',
        seq(1894, 1902),
    ),
    (
        'Gravitational Waves Ringdown And Echoes',
        'Density-wave gravitational sector with elastic ringdown and cavitation echoes.',
        seq(1903, 1913),
    ),
    (
        'Cosmological Dynamics',
        'Expansion, inflation, and dark-energy-like behavior from sediment-vacuum dynamics.',
        seq(1914, 1926),
    ),
    (
        'Continuum RG And DAL Bridge',
        'Discrete substrate to continuum flow plus RG thinning and scale-selection laws.',
        seq(1927, 1937) + seq(1960, 1970),
    ),
    (
        'Hazard Geometry And Saturation',
        'Geometric abstention and saturation layer used to avoid singular pathologies.',
        seq(2018, 2027),
    ),
    (
        'Cross-Ontological Phase Locking',
        'Cross-layer phase alignment as unification mechanism at the phase level.',
        seq(1990, 2001),
    ),
    (
        'Global Closure Claims',
        'Well-posedness, admissible manifold, Lyapunov descent, and closure assertions.',
        seq(1938, 1949),
    ),
]

with OUT.open('w', encoding='utf-8') as f:
    f.write('# Cosmology Spine (Tight, Additive, Solver-Minimized)\n\n')
    f.write('Purpose: a strict cosmology-forward canon you can keep extending without control-law clutter.\n\n')
    f.write('## Inclusion Contract\n')
    f.write('- Include: ontology, action, field equations, cosmological regimes, observables, falsifier-facing claims.\n')
    f.write('- Exclude: runtime controllers, certification mechanics, transport auditing, and procedural solver routing unless indispensable for a cosmology claim.\n')
    f.write('- Format: each claim stays atomic and keeps its source statement ID for chain-of-custody.\n\n')

    for i, (title, note, ids) in enumerate(SECTIONS, 1):
        f.write(f'## {i}. {title}\n')
        f.write(f'{note}\n\n')
        kept = 0
        for sid in ids:
            r = records.get(sid)
            if not r:
                continue
            f.write(f'- {sid}: {r["statement"]}\n')
            kept += 1
        f.write(f'\n_Section count: {kept}_\n\n')

    f.write('## Additions Protocol (Keep It Tight)\n')
    f.write('- Add new statements only if they map directly to one of the 13 sections above.\n')
    f.write('- If a new claim does not fit, create one new section with a one-line scope rule, not a mixed bucket.\n')
    f.write('- Preserve atomic style: one claim per line, one claim type per sentence.\n')
    f.write('- Keep equations or regime laws with explicit symbols and threshold conditions.\n')
    f.write('- Mark open hypotheses explicitly in a dedicated subsection before promotion to core claims.\n\n')

    f.write('## Parking Lot (Not Core Yet)\n')
    f.write('- Any solver/control or certification-specific mechanics that are useful operationally but not constitutive of cosmology.\n')
    f.write('- Candidate links to runtime stack can be referenced here without polluting the cosmology spine.\n')

print(f'Wrote: {OUT}')
