#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <case_id>"
  exit 1
fi

CASE_ID="$1"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CASE_DIR="$ROOT/cases/$CASE_ID"

mkdir -p "$CASE_DIR"/{data,reports,docs,audits}

cp "$ROOT/templates/CASE_RUN_CARD_TEMPLATE.md" "$CASE_DIR/docs/CASE_RUN_CARD.md"
cp "$ROOT/templates/CASE_GATE_CHECKLIST_TEMPLATE.md" "$CASE_DIR/docs/CASE_GATE_CHECKLIST.md"

sed -i '' "s/<case_id>/$CASE_ID/g" "$CASE_DIR/docs/CASE_RUN_CARD.md" || true

cat > "$CASE_DIR/README.md" <<EOF
# Case: $CASE_ID

Initialized Delta case scaffold.

## Next Steps
1. Fill \`docs/CASE_RUN_CARD.md\`
2. Fill \`docs/CASE_GATE_CHECKLIST.md\`
3. Implement case-specific audits in \`audits/\`
4. Emit receipts to \`reports/\`
EOF

echo "Initialized case scaffold at: $CASE_DIR"
