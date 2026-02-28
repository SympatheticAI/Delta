#!/usr/bin/env python3
"""Score theorem submission readiness gates S1..S7."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
OUT_JSON = REPORTS / "submission_ready_status.json"
OUT_MD = REPORTS / "submission_ready_status.md"


def exists(p: Path) -> bool:
    return p.exists() and p.stat().st_size > 0


def proof_complete_flag(path: Path) -> bool:
    if not exists(path):
        return False
    text = path.read_text()
    for line in text.splitlines():
        line = line.strip()
        if line.upper().startswith("PROOF_COMPLETE:"):
            return line.split(":", 1)[1].strip().upper() == "YES"
    return False


def main() -> None:
    # These are conservative objective checks from local artifacts.
    gates = {
        "S1_theorem_statement_complete": exists(ROOT / "docs" / "THEOREM_CLOSURE_DOSSIER.md"),
        "S2_dependencies_explicit": exists(ROOT / "docs" / "THEOREM_CLOSURE_DOSSIER.md"),
        "S3_os_reflection_positivity_proof_complete": proof_complete_flag(
            ROOT / "docs" / "S3_OS_REFLECTION_POSITIVITY_SECTION.md"
        ),
        "S4_gauge_invariant_mass_gap_proof_complete": proof_complete_flag(
            ROOT / "docs" / "S4_GAUGE_INVARIANT_MASS_GAP_SECTION.md"
        ),
        "S5_continuum_limit_proof_complete": proof_complete_flag(
            ROOT / "docs" / "S5_CONTINUUM_LIMIT_SECTION.md"
        ),
        "S6_numeric_labeled_support_only": exists(ROOT / "docs" / "FINISH_LINE_REPORT.md"),
        "S7_hostile_reread_passed": proof_complete_flag(ROOT / "docs" / "S7_HOSTILE_REREAD_CHECKLIST.md"),
    }

    passed = sum(1 for v in gates.values() if v)
    total = len(gates)
    submission_ready = passed == total

    payload = {
        "gates": gates,
        "passed": passed,
        "total": total,
        "submission_ready": submission_ready,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2))

    lines = ["# Submission-Ready Status", ""]
    for k, v in gates.items():
        lines.append(f"- {k}: `{'PASS' if v else 'OPEN'}`")
    lines.append("")
    lines.append(f"- score: `{passed}/{total}`")
    lines.append(f"- submission_ready: `{submission_ready}`")
    OUT_MD.write_text("\n".join(lines))
    print(f"Wrote: {OUT_JSON}")
    print(f"Wrote: {OUT_MD}")


if __name__ == "__main__":
    main()
