#!/usr/bin/env python3
import csv
import json
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'statements.ndjson'
OUT = ROOT / 'index'
OUT.mkdir(parents=True, exist_ok=True)

MODULE_RANGES = [
    (1, 23, 'deinfinite_core'),
    (24, 74, 'bedrock_flow_shear'),
    (75, 130, 'baryonic_confinement'),
    (131, 185, 'family_meter_lepton_ledger'),
    (186, 235, 'locks_and_certificates'),
    (236, 384, 'abstention_crl_bands'),
    (385, 521, 'dyadic_ladder_e0e4'),
    (522, 683, 'delta_energy_decision_mdl'),
    (684, 798, 'shr_and_low'),
    (799, 937, 'copl_hazard_escalation'),
    (938, 1032, 'delta_pinch_and_hinge'),
    (1033, 1141, 'why_numbers_are_real'),
    (1142, 1229, 'oscillation_diagnostic'),
    (1230, 1448, 'transport_pins_hats_receipts'),
    (1449, 1627, 'cpl_corridor_hinf'),
    (1628, 1809, 'pentad_omega_subtractive_umk'),
    (1810, 2063, 'encyclopedia_core_variational_stack'),
]

SPINE_ORDER = [
    'deinfinite_core',
    'oscillation_diagnostic',
    'abstention_crl_bands',
    'shr_and_low',
    'delta_energy_decision_mdl',
    'dyadic_ladder_e0e4',
    'transport_pins_hats_receipts',
    'delta_pinch_and_hinge',
    'pentad_omega_subtractive_umk',
    'cpl_corridor_hinf',
    'copl_hazard_escalation',
    'bedrock_flow_shear',
    'locks_and_certificates',
    'family_meter_lepton_ledger',
    'baryonic_confinement',
    'why_numbers_are_real',
    'encyclopedia_core_variational_stack',
]
SPINE_RANK = {name: i + 1 for i, name in enumerate(SPINE_ORDER)}
TOKEN_RE = re.compile(r"[a-zA-Z0-9_\-]+")


def parse_id(sid: str) -> int:
    return int(sid.split('-')[1])


def module_for(n: int) -> str:
    for lo, hi, name in MODULE_RANGES:
        if lo <= n <= hi:
            return name
    return 'unassigned'


def normalize(text: str) -> str:
    t = text.strip()
    t = re.sub(r"\s+", " ", t)
    return t


def keyish(text: str) -> str:
    t = text.lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


records = []
with DATA.open('r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        sid = obj['id']
        n = parse_id(sid)
        stmt = normalize(obj['statement'])
        toks = [t.lower() for t in TOKEN_RE.findall(stmt)]
        mod = module_for(n)
        records.append({
            'id': sid,
            'n': n,
            'statement': stmt,
            'module': mod,
            'spine_rank': SPINE_RANK.get(mod, 999),
            'token_count': len(toks),
            'char_count': len(stmt),
            'norm_key': keyish(stmt),
        })

by_key = defaultdict(list)
for r in records:
    by_key[r['norm_key']].append(r)
exact_dupe_clusters = [v for v in by_key.values() if len(v) > 1]

# near duplicates: same module and same 3-word prefix bucket
near_dupes = []
for mod in sorted({r['module'] for r in records}):
    group = [r for r in records if r['module'] == mod]
    buckets = defaultdict(list)
    for r in group:
        words = r['norm_key'].split()
        key = ' '.join(words[:3]) if words else ''
        buckets[key].append(r)
    for bucket in buckets.values():
        if len(bucket) < 2:
            continue
        for i in range(len(bucket)):
            for j in range(i + 1, len(bucket)):
                a, b = bucket[i], bucket[j]
                score = SequenceMatcher(None, a['norm_key'], b['norm_key']).ratio()
                if 0.92 <= score < 1.0:
                    near_dupes.append((score, a, b))
near_dupes.sort(key=lambda x: x[0], reverse=True)

module_stats = Counter(r['module'] for r in records)
curated = sorted(records, key=lambda r: (r['spine_rank'], r['module'], r['n']))

with (OUT / 'canon_curated.tsv').open('w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t')
    w.writerow(['spine_rank', 'module', 'id', 'token_count', 'char_count', 'statement'])
    for r in curated:
        w.writerow([r['spine_rank'], r['module'], r['id'], r['token_count'], r['char_count'], r['statement']])

with (OUT / 'canon_curated.ndjson').open('w', encoding='utf-8') as f:
    for r in curated:
        f.write(json.dumps({'id': r['id'], 'module': r['module'], 'spine_rank': r['spine_rank'], 'statement': r['statement']}, ensure_ascii=True) + '\n')

with (OUT / 'canon_spine.md').open('w', encoding='utf-8') as f:
    f.write('# Canon Spine (Curated)\n\n')
    f.write('Primary reading order for fast alignment.\n\n')
    for i, name in enumerate(SPINE_ORDER, start=1):
        f.write(f'{i}. {name} ({module_stats.get(name,0)} statements)\n')

with (OUT / 'canon_nitpick_report.md').open('w', encoding='utf-8') as f:
    f.write('# Canon Nitpick Report\n\n')
    f.write(f'- Total statements: {len(records)}\n')
    f.write(f'- Modules: {len(module_stats)}\n')
    f.write(f'- Exact duplicate clusters: {len(exact_dupe_clusters)}\n')
    f.write(f'- Near-duplicate pairs (>=0.92): {len(near_dupes)}\n\n')

    f.write('## Module Counts\n\n')
    for name, count in sorted(module_stats.items(), key=lambda x: (SPINE_RANK.get(x[0],999), x[0])):
        f.write(f'- `{name}`: {count}\n')

    f.write('\n## Exact Duplicates (Top 25 Clusters)\n\n')
    if not exact_dupe_clusters:
        f.write('- None detected (exact normalized-text duplicates).\n')
    else:
        for cluster in sorted(exact_dupe_clusters, key=lambda c: len(c), reverse=True)[:25]:
            f.write(f'- Cluster size {len(cluster)}: ' + ', '.join(r['id'] for r in cluster) + '\n')
            f.write(f'  - "{cluster[0]["statement"]}"\n')

    f.write('\n## Near Duplicates (Top 40 Pairs)\n\n')
    if not near_dupes:
        f.write('- None detected at threshold >=0.92.\n')
    else:
        for score, a, b in near_dupes[:40]:
            f.write(f'- {a["id"]} <-> {b["id"]} (module `{a["module"]}`, sim={score:.3f})\n')
            f.write(f'  - A: "{a["statement"]}"\n')
            f.write(f'  - B: "{b["statement"]}"\n')

    f.write('\n## Manual Nitpick Suggestions\n\n')
    f.write('- Standardize symbol naming variants per module (e.g., `DeltaE`, `Delta-Energy`, `Delta E`).\n')
    f.write('- Normalize threshold spacing (`<=0.01` vs `<= 0.01`) for clean machine diffs.\n')
    f.write('- Keep one authoritative statement for each invariant; tag alternates as explanatory variants.\n')
    f.write('- Keep procedural canon in imperative form (`Methods must ...`) for consistency.\n')

# All-in-one grouped master doc.
with (OUT / 'canon_master_ordered.md').open('w', encoding='utf-8') as f:
    f.write('# Canon Master Ordered\n\n')
    f.write('Raw statement canon grouped in curated spine order.\n\n')
    by_mod = defaultdict(list)
    for r in curated:
        by_mod[r['module']].append(r)
    for idx, mod in enumerate(SPINE_ORDER, start=1):
        group = by_mod.get(mod, [])
        f.write(f'## {idx}. {mod} ({len(group)} statements)\n')
        for r in group:
            f.write(f'- {r["id"]}: {r["statement"]}\n')
        f.write('\n')

print(f'Curated {len(records)} statements')
print(f'Near duplicate pairs: {len(near_dupes)}')
print(f'Master doc: {OUT / "canon_master_ordered.md"}')
