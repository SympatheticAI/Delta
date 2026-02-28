#!/usr/bin/env python3
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'data' / 'statements.ndjson'
OUT_DIR = ROOT / 'index'
OUT_DIR.mkdir(parents=True, exist_ok=True)

TOKEN_RE = re.compile(r"[a-zA-Z0-9_\-]+")
STOP = {
    'a','an','and','are','as','at','be','by','for','from','in','into','is','it','of','on','or','that','the','to','with','this','then'
}

records = []
with SRC.open('r', encoding='utf-8') as f:
    for line_no, line in enumerate(f, start=1):
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        sid = obj['id']
        text = obj['statement']
        toks = [t.lower() for t in TOKEN_RE.findall(text)]
        kws = [t for t in toks if t not in STOP and len(t) > 1]
        records.append({'id': sid, 'statement': text, 'keywords': kws, 'line': line_no})

inv = defaultdict(list)
for r in records:
    seen = set()
    for k in r['keywords']:
        if k in seen:
            continue
        inv[k].append(r['id'])
        seen.add(k)

keyword_freq = Counter()
for r in records:
    keyword_freq.update(r['keywords'])

with (OUT_DIR / 'statements.index.json').open('w', encoding='utf-8') as f:
    json.dump({'records': records, 'inverted_index': inv, 'keyword_frequency': keyword_freq}, f, indent=2)

with (OUT_DIR / 'statements.search.tsv').open('w', encoding='utf-8') as f:
    f.write('id\tstatement\tkeywords\n')
    for r in records:
        f.write(f"{r['id']}\t{r['statement'].replace(chr(9), ' ')}\t{','.join(sorted(set(r['keywords'])))}\n")

print(f'Indexed {len(records)} statements -> {OUT_DIR}')
