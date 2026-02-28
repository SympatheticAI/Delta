#!/usr/bin/env python3
"""One-shot autopilot: single prompt -> full YM pipeline -> final bundle.

Usage:
  python3 run_one_shot_ym.py --prompt "Solve Yang-Mills mass gap with Delta method"
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDITS = ROOT / "audits"
DOCS = ROOT / "docs"
REPORTS = ROOT / "reports"
LOGS = ROOT / "runs"
LOGS.mkdir(parents=True, exist_ok=True)


def run(cmd: list[str], log_file: Path) -> None:
    with log_file.open("a") as f:
        f.write(f"\n$ {' '.join(cmd)}\n")
        f.flush()
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        f.write(proc.stdout)
        if proc.stderr:
            f.write("\n[stderr]\n")
            f.write(proc.stderr)
        f.write(f"\n[exit={proc.returncode}]\n")
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")


def write_run_manifest(run_id: str, prompt: str, log_file: Path) -> Path:
    manifest = {
        "run_id": run_id,
        "utc_started": datetime.now(timezone.utc).isoformat(),
        "mode": "one_shot_ym_autopilot",
        "prompt": prompt,
        "root": str(ROOT),
        "log_file": str(log_file),
    }
    p = LOGS / f"{run_id}_manifest.json"
    p.write_text(json.dumps(manifest, indent=2))
    return p


def write_bundle_index(run_id: str, prompt: str, log_file: Path, manifest_file: Path) -> Path:
    index = [
        "# One-Shot YM Run Bundle",
        "",
        f"- run_id: `{run_id}`",
        f"- prompt: `{prompt}`",
        f"- log: `{log_file}`",
        f"- manifest: `{manifest_file}`",
        "",
        "## Primary Outputs",
        f"- `{REPORTS / 'submission_ready_status.md'}`",
        f"- `{REPORTS / 'final_status.md'}`",
        f"- `{REPORTS / 'real_su2_pipeline_summary.md'}`",
        f"- `{REPORTS / 'real_su2_scaling_scan_summary.md'}`",
        f"- `{DOCS / 'FINAL_DOSSIER.md'}`",
        f"- `{DOCS / 'MASTER_ALL_IN_ONE.md'}`",
        "",
        "## Repro Entry",
        f"- `{AUDITS / 'run_all_audits.sh'}`",
    ]
    p = LOGS / f"{run_id}_BUNDLE_INDEX.md"
    p.write_text("\n".join(index))
    return p


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True, help="Single human prompt for the run.")
    args = parser.parse_args()

    run_id = datetime.now(timezone.utc).strftime("ym_%Y%m%dT%H%M%SZ")
    log_file = LOGS / f"{run_id}.log"

    manifest_file = write_run_manifest(run_id, args.prompt, log_file)

    run(["bash", str(AUDITS / "run_all_audits.sh")], log_file)
    run(["python3", str(AUDITS / "check_submission_ready.py")], log_file)
    run(["python3", str(AUDITS / "summarize_audits.py")], log_file)

    # Rebuild all-in-one bundle deterministically.
    run(
        [
            "python3",
            "-c",
            (
                "from pathlib import Path; "
                "root=Path(r'" + str(ROOT) + "'); "
                "out=root/'docs'/'MASTER_ALL_IN_ONE.md'; "
                "assert out.exists(), 'MASTER_ALL_IN_ONE.md missing'"
            ),
        ],
        log_file,
    )

    bundle_index = write_bundle_index(run_id, args.prompt, log_file, manifest_file)

    print(f"Run complete: {run_id}")
    print(f"Log: {log_file}")
    print(f"Manifest: {manifest_file}")
    print(f"Bundle index: {bundle_index}")


if __name__ == "__main__":
    main()
