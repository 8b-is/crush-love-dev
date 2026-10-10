#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""mesh.py — render the harness mesh (crush ⇄ jcode ⇄ opencode).

  sync    render the shared substrate into each harness home (backup, idempotent)
  status  report which shared surfaces each harness already has

Reads ../mesh.toml. Every write is backed up to <file>.mesh-bak and only happens
if the file actually changes. A corrupt JSON config is never clobbered.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # <3.11
    sys.exit("mesh: python 3.11+ required (tomllib)")

HERE = Path(__file__).resolve().parent
MESH = HERE.parent / "mesh.toml"
MARKER = "<!-- harness-mesh -->"
MARKER_END = "<!-- harness-mesh:end -->"


def die(msg: str) -> None:
    print(f"mesh: {msg}", file=sys.stderr)
    raise SystemExit(1)


def load_mesh(path: Path) -> dict:
    with open(path, "rb") as fh:
        return tomllib.load(fh)


def resolve(root: str | None, p: str) -> Path:
    """Expand ~, and rebase onto --home-root for sandboxed runs."""
    p = os.path.expanduser(p)
    if root:
        home = str(Path.home())
        if p == home or p.startswith(home + "/"):
            return Path(root) / p[len(home):].lstrip("/")
    return Path(p)


def read_json(p: Path):
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None  # signal: corrupt, do not clobber


def backup(p: Path, dry: bool) -> None:
    bak = p.with_suffix(p.suffix + ".mesh-bak")
    if p.exists() and not bak.exists() and not dry:
        bak.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")


def write(p: Path, text: str, dry: bool) -> None:
    if dry:
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def render_servers(kind: str, servers: dict) -> dict:
    out: dict = {}
    for sid, s in servers.items():
        cmd = s["command"]
        args = list(s.get("args", []))
        env = dict(s.get("env", {}))
        if kind == "crush":
            spec = {"type": "stdio", "command": cmd, "args": args}
            if env:
                spec["env"] = env
        elif kind == "jcode":
            spec = {"command": cmd, "args": args, "env": env, "shared": True}
        elif kind == "opencode":
            spec = {"type": "local", "command": [cmd, *args], "enabled": True}
        else:
            die(f"unknown harness kind: {kind!r}")
        out[sid] = spec
    return out


def bucket(doc: dict, kind: str) -> dict:
    return doc.setdefault("servers" if kind == "jcode" else "mcp", {})


def sync_harness(name: str, h: dict, shared: dict, root, dry: bool) -> dict:
    path = resolve(root, h["home"]) / h["config"]
    doc = read_json(path)
    if doc is None:
        print(f"  ! {name:8} {path}  — invalid JSON, skipped (never clobbered)")
        return {"harness": name, "path": str(path), "status": "skipped", "added": []}
    rendered = render_servers(h["kind"], shared.get("mcp", {}))
    m = bucket(doc, h["kind"])
    added = []
    for sid, spec in rendered.items():
        if m.get(sid) != spec:
            m[sid] = spec
            added.append(sid)
    theme = shared.get("theme", {}).get("name")
    themed = False
    if h["kind"] == "crush" and theme:
        tui = doc.setdefault("options", {}).setdefault("tui", {})
        if tui.get("theme") != theme:
            tui["theme"] = theme
            themed = True
    if added or themed:
        backup(path, dry)
        write(path, json.dumps(doc, indent=2, ensure_ascii=False) + "\n", dry)
    mark = ", ".join(added) or "—"
    print(f"  ✓ {name:8} {path}  +[{mark}]{'  theme' if themed else ''}")
    return {"harness": name, "path": str(path), "status": "ok",
            "added": added, "theme": themed}


def sync_persona(shared: dict, root, dry: bool) -> None:
    spec = shared.get("persona")
    if not spec:
        return
    p = resolve(root, spec["file"])
    text = spec.get("text", "").strip()
    block = f"{MARKER}\n{text}\n{MARKER_END}"
    existing = p.read_text(encoding="utf-8") if p.exists() else ""
    if MARKER in existing:
        new = re.sub(re.escape(MARKER) + r".*?" + re.escape(MARKER_END),
                     block, existing, flags=re.S)
    elif existing.strip():
        new = existing.rstrip() + "\n\n" + block + "\n"
    else:
        new = block + "\n"
    changed = new != existing
    if changed:
        backup(p, dry)
        write(p, new, dry)
    print(f"  ✓ persona  {p}  ({'updated' if changed else 'unchanged'})")


def append_ledger(mesh: dict, root, entries: list, dry: bool) -> None:
    led = resolve(root, mesh["ledger"])
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "event": "mesh.sync",
           "harnesses": [e["harness"] for e in entries],
           "added": {e["harness"]: e["added"] for e in entries}}
    if not dry:
        led.parent.mkdir(parents=True, exist_ok=True)
        with led.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"  ✓ ledger   {led}")


def cmd_status(m: dict, root, as_json: bool) -> int:
    shared_ids = set(m.get("shared", {}).get("mcp", {}))
    rows = []
    for name, h in m.get("harness", {}).items():
        path = resolve(root, h["home"]) / h["config"]
        doc = read_json(path)
        present = sorted(shared_ids & set(bucket(doc, h["kind"]))) if doc is not None else []
        rows.append({"harness": name, "path": str(path),
                     "present": present, "missing": sorted(shared_ids - set(present))})
    if as_json:
        print(json.dumps(rows, indent=2))
        return 0
    for r in rows:
        print(f"  {r['harness']:8} {len(r['present'])}/{len(shared_ids)} shared MCP  "
              f"{r['path']}")
        if r["missing"]:
            print(f"           missing: {', '.join(r['missing'])}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="mesh", description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="sync", choices=["sync", "status"])
    ap.add_argument("--home-root", help="rebase ~ onto this root (sandboxed runs)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    m = load_mesh(MESH)
    if a.cmd == "status":
        return cmd_status(m, a.home_root, a.json)

    print(f"mesh sync · {m['mesh']['name']}" + (" (dry-run)" if a.dry_run else ""))
    shared = m.get("shared", {})
    entries = [sync_harness(n, h, shared, a.home_root, a.dry_run)
               for n, h in m.get("harness", {}).items()]
    sync_persona(shared, a.home_root, a.dry_run)
    append_ledger(m["mesh"], a.home_root, entries, a.dry_run)
    if a.json:
        print(json.dumps(entries, indent=2))
    print("done — the door is open.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
