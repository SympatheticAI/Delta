#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDX = ROOT / 'index' / 'statements.index.json'

if len(sys.argv) < 2:
    print('Usage: query_statements.py <term1> [term2 ...]')
    raise SystemExit(1)

terms = [t.lower() for t in sys.argv[1:]]
with IDX.open('r', encoding='utf-8') as f:
    data = json.load(f)

inv = data['inverted_index']
records = {r['id']: r for r in data['records']}

hits = None
for t in terms:
    ids = set(inv.get(t, []))
    hits = ids if hits is None else hits & ids

if not hits:
    print('No matches.')
    raise SystemExit(0)

for sid in sorted(hits):
    r = records[sid]
    print(f"{sid}: {r['statement']}")
