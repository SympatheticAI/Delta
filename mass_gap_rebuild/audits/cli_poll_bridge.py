#!/usr/bin/env python3
"""Bidirectional polling bridge for two CLI agents.

Use this when two separate CLI tools need to exchange live status updates
without directly attaching to each other's TTY.

Example:
  # one-time init
  python3 cli_poll_bridge.py init --dir /tmp/bridge

  # Codex sends update
  python3 cli_poll_bridge.py send --dir /tmp/bridge --from codex --type status --msg "Step 3 done"

  # OpenClaw polls Codex updates
  python3 cli_poll_bridge.py poll --dir /tmp/bridge --to openclaw

  # OpenClaw sends
  python3 cli_poll_bridge.py send --dir /tmp/bridge --from openclaw --type status --msg "Running tests"

  # Codex watches OpenClaw stream live
  python3 cli_poll_bridge.py watch --dir /tmp/bridge --to codex --interval 1.0
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


AGENTS = ("codex", "openclaw")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_bridge_dir(bridge_dir: Path) -> None:
    bridge_dir.mkdir(parents=True, exist_ok=True)
    for agent in AGENTS:
        outbox = bridge_dir / f"{agent}.out.jsonl"
        outbox.touch(exist_ok=True)
    for reader in AGENTS:
        for writer in AGENTS:
            if reader == writer:
                continue
            cursor = bridge_dir / f"{reader}.cursor.from_{writer}.txt"
            if not cursor.exists():
                cursor.write_text("0")


def outbox_path(bridge_dir: Path, agent: str) -> Path:
    return bridge_dir / f"{agent}.out.jsonl"


def cursor_path(bridge_dir: Path, reader: str, writer: str) -> Path:
    return bridge_dir / f"{reader}.cursor.from_{writer}.txt"


def writer_for_reader(reader: str) -> str:
    return "openclaw" if reader == "codex" else "codex"


def read_cursor(path: Path) -> int:
    try:
        return int(path.read_text().strip() or "0")
    except (ValueError, OSError):
        return 0


def write_cursor(path: Path, value: int) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(str(value))
    tmp.replace(path)


def append_event(outbox: Path, event: dict) -> None:
    line = json.dumps(event, separators=(",", ":")) + "\n"
    with outbox.open("a", encoding="utf-8") as f:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())


def iter_new_lines(path: Path, start_offset: int) -> Iterator[tuple[int, str]]:
    with path.open("r", encoding="utf-8") as f:
        f.seek(start_offset)
        while True:
            pos = f.tell()
            line = f.readline()
            if not line:
                break
            yield pos, line


def cmd_init(args: argparse.Namespace) -> int:
    ensure_bridge_dir(args.dir)
    print(f"Bridge initialized: {args.dir}")
    return 0


def cmd_send(args: argparse.Namespace) -> int:
    ensure_bridge_dir(args.dir)
    event = {
        "ts": utc_now(),
        "from": args.sender,
        "type": args.type,
        "msg": args.msg,
        "meta": json.loads(args.meta) if args.meta else {},
    }
    append_event(outbox_path(args.dir, args.sender), event)
    print("sent")
    return 0


def poll_once(bridge_dir: Path, to_agent: str, limit: int | None, json_output: bool) -> int:
    writer = writer_for_reader(to_agent)
    outbox = outbox_path(bridge_dir, writer)
    cursor = cursor_path(bridge_dir, to_agent, writer)
    start = read_cursor(cursor)
    emitted = 0
    last_end = start

    for pos, line in iter_new_lines(outbox, start):
        end = pos + len(line.encode("utf-8"))
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            evt = {"raw": line.rstrip("\n"), "parse_error": True}
        if json_output:
            print(json.dumps(evt, ensure_ascii=True))
        else:
            ts = evt.get("ts", "?")
            sender = evt.get("from", writer)
            etype = evt.get("type", "event")
            msg = evt.get("msg", "")
            print(f"[{ts}] {sender}:{etype} {msg}")
        emitted += 1
        last_end = end
        if limit is not None and emitted >= limit:
            break

    write_cursor(cursor, last_end)
    return emitted


def cmd_poll(args: argparse.Namespace) -> int:
    ensure_bridge_dir(args.dir)
    count = poll_once(args.dir, args.to, args.limit, args.json)
    if count == 0 and args.empty_notice:
        print("no_new_events")
    return 0


def cmd_watch(args: argparse.Namespace) -> int:
    ensure_bridge_dir(args.dir)
    try:
        while True:
            poll_once(args.dir, args.to, None, args.json)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Bidirectional CLI polling bridge")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("--dir", type=Path, required=True)
    p_init.set_defaults(func=cmd_init)

    p_send = sub.add_parser("send")
    p_send.add_argument("--dir", type=Path, required=True)
    p_send.add_argument("--from", dest="sender", choices=AGENTS, required=True)
    p_send.add_argument("--type", default="status")
    p_send.add_argument("--msg", required=True)
    p_send.add_argument("--meta", default="", help="JSON object string")
    p_send.set_defaults(func=cmd_send)

    p_poll = sub.add_parser("poll")
    p_poll.add_argument("--dir", type=Path, required=True)
    p_poll.add_argument("--to", choices=AGENTS, required=True)
    p_poll.add_argument("--limit", type=int, default=None)
    p_poll.add_argument("--json", action="store_true")
    p_poll.add_argument("--empty-notice", action="store_true")
    p_poll.set_defaults(func=cmd_poll)

    p_watch = sub.add_parser("watch")
    p_watch.add_argument("--dir", type=Path, required=True)
    p_watch.add_argument("--to", choices=AGENTS, required=True)
    p_watch.add_argument("--interval", type=float, default=1.0)
    p_watch.add_argument("--json", action="store_true")
    p_watch.set_defaults(func=cmd_watch)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
