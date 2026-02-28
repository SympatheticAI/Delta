#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'data' / 'statements.ndjson'

if len(sys.argv) != 2:
    print('Usage: add_statements_from_txt.py <text_file_with_one_statement_per_line>')
    raise SystemExit(1)

infile = Path(sys.argv[1]).expanduser().resolve()
if not infile.exists():
    print(f'Input file not found: {infile}')
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
with infile.open('r', encoding='utf-8') as f:
    for raw in f:
        s = raw.strip()
        if not s:
            continue
        if s in by_text:
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

print(f'Added {len(new_records)} new statements from {infile.name}.')
if new_records:
    print(f"First: {new_records[0]['id']}  Last: {new_records[-1]['id']}")
