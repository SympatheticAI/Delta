#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'data' / 'statements.ndjson'

if len(sys.argv) < 2:
    print('Usage: add_statements.py "statement 1" ["statement 2" ...]')
    raise SystemExit(1)

existing = []
if SRC.exists():
    with SRC.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            existing.append(json.loads(line))

by_text = {r['statement']: r['id'] for r in existing}
max_id = 0
for r in existing:
    try:
        max_id = max(max_id, int(r['id'].split('-')[1]))
    except Exception:
        pass

new_records = []
for s in sys.argv[1:]:
    s = s.strip()
    if not s or s in by_text:
        continue
    max_id += 1
    rid = f"S-{max_id:04d}"
    rec = {'id': rid, 'statement': s}
    new_records.append(rec)
    by_text[s] = rid

if new_records:
    with SRC.open('a', encoding='utf-8') as f:
        for rec in new_records:
            f.write(json.dumps(rec, ensure_ascii=True) + '\n')

print(f'Added {len(new_records)} new statements.')
for rec in new_records:
    print(f"{rec['id']}: {rec['statement']}")
