#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'data' / 'statements.ndjson'
OUT_DIR = ROOT / 'index'
OUT_DIR.mkdir(parents=True, exist_ok=True)

TOKEN_RE = re.compile(r"[a-zA-Z0-9_\-]+")

# Lower score means earlier in epistemic buildup.
STAGE_RULES = [
    (0, 'ontology', {'problem', 'bounded', 'unbounded', 'reference', 'exists'}),
    (1, 'contract', {'contract', 'n=4', '3-decimal', 'finite', 'admissible'}),
    (2, 'operator', {'project', 'projection', 'deinfinite', 'maps', 'transforms', 'image'}),
    (3, 'residual', {'residual', 'gap', 'minus', 'delta', 'error'}),
    (4, 'promotion', {'promotes', 'dynamics', 'parameter', 'active', 'physics'}),
    (5, 'application', {'yang-mills', 'navier', 'quantum', 'mass', 'workflow'}),
]

def tokenize(text: str):
    return [t.lower() for t in TOKEN_RE.findall(text)]

def classify(statement: str):
    toks = set(tokenize(statement))
    # Normalize common token variants
    if 'deinfinite' in statement.lower():
        toks.add('deinfinite')
    best_stage = 99
    best_label = 'unclassified'
    best_hits = 0
    for stage, label, vocab in STAGE_RULES:
        hits = len(toks.intersection(vocab))
        if hits > best_hits or (hits == best_hits and stage < best_stage and hits > 0):
            best_hits = hits
            best_stage = stage
            best_label = label
    if best_hits == 0:
        # fallback: treat as application-level by default
        best_stage = 5
        best_label = 'application'
    return best_stage, best_label, best_hits, sorted(toks)

records = []
with SRC.open('r', encoding='utf-8') as f:
    for line_no, line in enumerate(f, start=1):
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        sid = obj['id']
        text = obj['statement']
        stage, label, hits, toks = classify(text)
        records.append({
            'id': sid,
            'statement': text,
            'line': line_no,
            'epistemic_stage': stage,
            'epistemic_label': label,
            'rule_hits': hits,
            'tokens': toks,
        })

# Deterministic ordering: stage -> stronger rule match -> id
ordered = sorted(records, key=lambda r: (r['epistemic_stage'], -r['rule_hits'], r['id']))

with (OUT_DIR / 'epistemic_order.json').open('w', encoding='utf-8') as f:
    json.dump({'ordered': ordered}, f, indent=2)

# Statement-only ordered view (still pure statements, no metadata)
with (OUT_DIR / 'statements_epistemic_order.ndjson').open('w', encoding='utf-8') as f:
    for r in ordered:
        f.write(json.dumps({'id': r['id'], 'statement': r['statement']}) + '\n')

# Human scan view
with (OUT_DIR / 'epistemic_order.tsv').open('w', encoding='utf-8') as f:
    f.write('rank\tid\tstage\tlabel\tstatement\n')
    for i, r in enumerate(ordered, start=1):
        safe = r['statement'].replace('\t', ' ')
        f.write(f"{i}\t{r['id']}\t{r['epistemic_stage']}\t{r['epistemic_label']}\t{safe}\n")

print(f'Ranked {len(ordered)} statements -> {OUT_DIR}')
