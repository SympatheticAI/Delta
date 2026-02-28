# One-Shot Autopilot (Uncut Demo Mode)

## Goal
Launch a full YM run from one prompt, then do not touch the machine.

## Command
```bash
python3 "/Users/jakeaaron/Soliton Mechanics/Validation/mass_gap_rebuild/audits/run_one_shot_ym.py" \
  --prompt "Solve Yang-Mills mass gap with Delta method, run full pipeline, output final bundle."
```

## What It Does
1. Runs full audit pipeline (`run_all_audits.sh`)
2. Re-checks submission gates
3. Writes run log + manifest
4. Emits bundle index pointing to final artifacts

## Output Location
- `/Users/jakeaaron/Soliton Mechanics/Validation/mass_gap_rebuild/runs/<run_id>.log`
- `/Users/jakeaaron/Soliton Mechanics/Validation/mass_gap_rebuild/runs/<run_id>_manifest.json`
- `/Users/jakeaaron/Soliton Mechanics/Validation/mass_gap_rebuild/runs/<run_id>_BUNDLE_INDEX.md`

## Uncut Video Protocol
1. Start screen recording.
2. Paste one command above.
3. Hands off keyboard/mouse.
4. Stop recording only after run completion lines appear.
5. Open bundle index and show generated outputs.
