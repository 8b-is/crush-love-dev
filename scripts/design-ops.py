#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
design_ops.py — Sovereign Design Studio CLI for 8b-is & design.vaked.dev.

Commands:
  status                         Overview of design.vaked.dev & 8b-is/marketing
  palettes                       List all 5 official 8b-is color palettes
  tokens [--palette P] [--format F]
                                 Synthesize tokens in css, rust, swift, ghostty, or json
  logos                          List all 16 vector SVGs, 9 PNGs, and brand sheets
  audit [target_dir]             Verify 4-point Constellation + Modern Web contract
  sync                           Sync logos, palettes, and brand sheets from marketing -> design.vaked.dev
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

WORKSPACE_ROOT = Path("/Users/lodripeter/workspace/peterlodri-sec")
DESIGN_DIR = WORKSPACE_ROOT / "design.vaked.dev"
MARKETING_DIR = WORKSPACE_ROOT / "marketing"
PALETTES_JSON = DESIGN_DIR / "palettes" / "8b-is-palettes.json"

PALETTE_ALIASES = {
    "omnifold": "omnifold-industrial",
    "zen-bonfire": "kintsugi-zen",
    "zen": "kintsugi-zen",
    "ternary-mem8k": "ternary-matrix",
    "ternary": "ternary-matrix",
    "standard-galactic": "sakura-starlight",
    "sakura": "sakura-starlight",
}


def load_palettes() -> dict:
    path = PALETTES_JSON if PALETTES_JSON.exists() else (MARKETING_DIR / "palettes" / "8b-is-palettes.json")
    if not path.exists():
        raise FileNotFoundError(f"Could not find 8b-is-palettes.json at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    clean = hex_str.lstrip("#")
    if len(clean) >= 6:
        return int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16)
    return (0, 0, 0)


def resolve_palette(data: dict, key: str) -> tuple[str, dict]:
    palettes = data["palettes"]
    resolved = PALETTE_ALIASES.get(key, key)
    if resolved not in palettes:
        raise KeyError(f"Unknown palette '{key}'. Available: {', '.join(palettes.keys())}")
    return resolved, palettes[resolved]


def format_tokens(pid: str, palette: dict, fmt: str) -> str:
    t: dict[str, str] = palette["tokens"]
    name = palette["name"]
    used_by = ", ".join(palette.get("used_by", []))
    fmt = fmt.lower()
    vals = list(t.values())
    bg = vals[0] if vals else "#0B0914"
    pri = vals[2] if len(vals) > 2 else "#FF6AC1"
    sec = vals[3] if len(vals) > 3 else "#00E5C9"
    gold = "#FFD700"

    if fmt == "css":
        lines = [
            f"/* 8b-is Official Palette — {name} ({pid}) */",
            f"/* Used by: {used_by} */",
            ":root {",
        ]
        for k, hex_val in t.items():
            css_var = k.replace("_", "-")
            lines.append(f"  --8b-{css_var}: {hex_val};")
        lines.extend(
            [
                f"  --bg: {bg};",
                f"  --c1: {pri};",
                f"  --c2: {gold};",
                f"  --c3: {sec};",
                "}",
            ]
        )
        return "\n".join(lines)

    if fmt == "rust":
        mod_name = pid.replace("-", "_")
        lines = [
            f"// 8b-is Official Palette — {name} ({pid})",
            f"// Used by: {used_by}",
            f"pub mod palette_{mod_name} {{",
            "    #[derive(Debug, Clone, Copy, PartialEq, Eq)]",
            "    pub struct Rgb(pub u8, pub u8, pub u8);",
            "",
        ]
        for k, hex_val in t.items():
            const_name = k.upper().replace("-", "_")
            r, g, b = hex_to_rgb(hex_val)
            lines.append(f"    pub const {const_name}: Rgb = Rgb({r}, {g}, {b}); // {hex_val}")
        lines.append("}")
        return "\n".join(lines)

    if fmt == "swift":
        lines = [
            f"// 8b-is Official Palette — {name} ({pid})",
            f"// Used by: {used_by}",
            "import SwiftUI",
            "",
            "public enum EightBTheme {",
        ]
        for k, hex_val in t.items():
            parts = k.replace("-", "_").split("_")
            camel = parts[0] + "".join(p.capitalize() for p in parts[1:])
            r, g, b = hex_to_rgb(hex_val)
            lines.append(
                f"    /// {k} ({hex_val})\n"
                f"    public static let {camel} = Color(red: {r/255.0:.4f}, green: {g/255.0:.4f}, blue: {b/255.0:.4f})"
            )
        lines.append("}")
        return "\n".join(lines)

    if fmt == "ghostty":
        return "\n".join(
            [
                f"# 8b-is Ghostty Terminal Theme — {name} ({pid})",
                f"# Save to ~/.config/ghostty/themes/8b-{pid}",
                f"background = {bg}",
                "foreground = #F5ECFF",
                f"cursor-color = {gold}",
                f"selection-background = {vals[1] if len(vals) > 1 else '#1F1633'}",
                "selection-foreground = #F5ECFF",
                f"palette = 0={bg}",
                "palette = 1=#FF3366",
                "palette = 2=#00FF66",
                f"palette = 3={gold}",
                f"palette = 4={sec}",
                f"palette = 5={pri}",
                "palette = 6=#00E5C9",
                "palette = 7=#F5ECFF",
            ]
        )

    if fmt == "json":
        out = {
            "$schema": "https://design.vaked.dev/palettes/8b-is-palettes.json",
            "id": pid,
            "name": name,
            "used_by": palette.get("used_by", []),
            "tokens": t,
        }
        return json.dumps(out, indent=2)

    raise ValueError(f"Unsupported format: {fmt}. Choose css, rust, swift, ghostty, or json.")


def cmd_palettes(_args: argparse.Namespace) -> int:
    data = load_palettes()
    print("╭──────────────────────────────────────────────────────────────────────────────────────╮")
    print("│  8b-is OFFICIAL 5-PALETTE SYSTEM · design.vaked.dev                                  │")
    print("╰──────────────────────────────────────────────────────────────────────────────────────╯")
    for pid, p in data["palettes"].items():
        t = p["tokens"]
        sample = "  ".join(f"{k}={v}" for k, v in list(t.items())[:4])
        print(f"  • {pid:<20} │ {p['name']}")
        print(f"    ↳ Tokens : {sample}")
        print(f"    ↳ Used by: {', '.join(p.get('used_by', []))}")
    return 0


def cmd_tokens(args: argparse.Namespace) -> int:
    data = load_palettes()
    try:
        pid, palette = resolve_palette(data, args.palette)
    except KeyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(format_tokens(pid, palette, args.format))
    return 0


def cmd_logos(_args: argparse.Namespace) -> int:
    org_svgs = sorted((DESIGN_DIR / "logos" / "org").glob("*.svg"))
    prod_svgs = sorted((DESIGN_DIR / "logos" / "products" / "svg").glob("*.svg"))
    prod_pngs = sorted((DESIGN_DIR / "logos" / "products" / "png").glob("*.png"))
    sheets = sorted((DESIGN_DIR / "assets" / "brand").glob("*.jpg"))

    print(f"=== Organization Master Marks ({len(org_svgs)} SVGs) ===")
    for p in org_svgs:
        rel = str(p.relative_to(DESIGN_DIR))
        print(f"  [SVG] {rel:<42} -> https://design.vaked.dev/{rel}")

    print(f"\n=== Product Constellation Vector Marks ({len(prod_svgs)} SVGs) ===")
    for p in prod_svgs:
        rel = str(p.relative_to(DESIGN_DIR))
        print(f"  [SVG] {rel:<42} -> https://design.vaked.dev/{rel}")

    print(f"\n=== High-Res Product App Icons ({len(prod_pngs)} PNGs) ===")
    for p in prod_pngs:
        rel = str(p.relative_to(DESIGN_DIR))
        print(f"  [PNG] {rel:<42} -> https://design.vaked.dev/{rel}")

    print(f"\n=== Brand Identity & Blueprint Sheets ({len(sheets)} JPGs) ===")
    for p in sheets:
        rel = str(p.relative_to(DESIGN_DIR))
        print(f"  [JPG] {rel:<42} -> https://design.vaked.dev/{rel}")
    return 0


def audit_surface(target: Path) -> tuple[bool, list[tuple[str, bool, str]]]:
    checks: list[tuple[str, bool, str]] = []

    robots = target / "robots.txt"
    has_robots = robots.exists() and "Sitemap:" in robots.read_text(encoding="utf-8", errors="ignore")
    checks.append(("Constellation #1: robots.txt + Sitemap", has_robots, str(robots)))

    headers = target / "_headers"
    htext = headers.read_text(encoding="utf-8", errors="ignore") if headers.exists() else ""
    has_headers = (
        "X-Robots-Tag: noai, noimageai" in htext
        and "X-Content-Type-Options: nosniff" in htext
        and "Referrer-Policy: strict-origin-when-cross-origin" in htext
    )
    checks.append(("Constellation #2: _headers (noai + security policy)", has_headers, str(headers)))

    index = target / "index.html"
    itext = index.read_text(encoding="utf-8", errors="ignore") if index.exists() else ""
    jtext = (target / "main.js").read_text(encoding="utf-8", errors="ignore") if (target / "main.js").exists() else ""
    combined = itext + "\n" + jtext

    has_audio = "music.vaked.dev" in combined and ("<iframe" in itext or "<audio" in itext)
    checks.append(("Constellation #3: music.vaked.dev soundtrack layer", has_audio, "index.html"))

    has_footer = "lovetta lane" in itext.lower() and "keep the weights warm" in itext.lower()
    checks.append(("Constellation #4: Lovetta Lane constellation footer", has_footer, "index.html"))

    has_container_style = "@container style(" in itext
    checks.append(("Modern Web #5: CSS @container style(--density) queries", has_container_style, "index.html"))

    has_view_transition = "startViewTransition" in combined
    checks.append(("Modern Web #6: View Transitions API (startViewTransition)", has_view_transition, "main.js"))

    has_reduced_motion = "prefers-reduced-motion" in combined
    checks.append(("Modern Web #7: prefers-reduced-motion accessibility guard", has_reduced_motion, "index.html/main.js"))

    has_qwave = (target / "qwave.txt").exists()
    checks.append(("Heritage #8: Preserved qwave.txt architecture spec", has_qwave, str(target / "qwave.txt")))

    all_ok = all(ok for _, ok, _ in checks)
    return all_ok, checks


def cmd_audit(args: argparse.Namespace) -> int:
    target = Path(args.target).expanduser()
    if not target.is_absolute():
        target = (WORKSPACE_ROOT / target).resolve()
    ok, checks = audit_surface(target)
    print(f"=== Auditing Design Surface: {target} ===")
    for label, passed, detail in checks:
        mark = "PASS" if passed else "FAIL"
        print(f"  [{mark}] {label:<54} ({detail})")
    print(f"\nResult: {'ALL 8 CHECKS PASSED' if ok else 'AUDIT FAILED'}")
    return 0 if ok else 1


def cmd_sync(_args: argparse.Namespace) -> int:
    if not MARKETING_DIR.exists():
        print(f"Error: marketing repo not found at {MARKETING_DIR}", file=sys.stderr)
        return 1
    for sub in ["logos", "palettes", "assets/brand"]:
        src = MARKETING_DIR / sub
        dst = DESIGN_DIR / sub
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f"  [SYNC] {src} -> {dst}")
    shutil.copy2(DESIGN_DIR / "logos" / "org" / "8b-is-avatar.svg", DESIGN_DIR / "favicon.svg")
    shutil.copy2(DESIGN_DIR / "logos" / "org" / "8b-is-wordmark-dark.svg", DESIGN_DIR / "og.svg")
    print("  [SYNC] Updated favicon.svg & og.svg")
    return 0


def cmd_status(_args: argparse.Namespace) -> int:
    data = load_palettes()
    org_svgs = list((DESIGN_DIR / "logos" / "org").glob("*.svg"))
    prod_svgs = list((DESIGN_DIR / "logos" / "products" / "svg").glob("*.svg"))
    prod_pngs = list((DESIGN_DIR / "logos" / "products" / "png").glob("*.png"))
    sheets = list((DESIGN_DIR / "assets" / "brand").glob("*.jpg"))
    ok, checks = audit_surface(DESIGN_DIR)
    passed_count = sum(1 for _, p, _ in checks if p)

    print("╭──────────────────────────────────────────────────────────────────────────────╮")
    print("│  8b-is // DESIGN.VAKED.DEV STUDIO & /design SKILL STATUS                     │")
    print("├──────────────────────────────────────────────────────────────────────────────┤")
    print(f"│  Studio Path      : {str(DESIGN_DIR):<56} │")
    print(f"│  Marketing Repo   : {str(MARKETING_DIR):<56} │")
    print(f"│  Official Palettes: {len(data['palettes'])} palettes (Ultralovegod · Omnifold · Kintsugi · Ternary · Sakura) │")
    print(f"│  Vector Logos     : {len(org_svgs)} Org SVGs + {len(prod_svgs)} Product SVGs ({len(org_svgs)+len(prod_svgs)} total)                 │")
    print(f"│  Raster Assets    : {len(prod_pngs)} Product PNGs + {len(sheets)} Brand/Blueprint Sheets                 │")
    print(f"│  Contract Audit   : {passed_count}/{len(checks)} checks passing ({'READY' if ok else 'NEEDS ATTENTION'})                          │")
    print("╰──────────────────────────────────────────────────────────────────────────────╯")
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="8b-is /design Studio CLI (design.vaked.dev)")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("status", help="Show design.vaked.dev & /design skill status")
    sub.add_parser("palettes", help="List all 5 official 8b-is palettes")

    p_tok = sub.add_parser("tokens", help="Synthesize design tokens in css, rust, swift, ghostty, or json")
    p_tok.add_argument("--palette", "-p", default="ultralovegod", help="Palette ID (default: ultralovegod)")
    p_tok.add_argument("--format", "-f", default="css", choices=["css", "rust", "swift", "ghostty", "json"])

    sub.add_parser("logos", help="List all vector SVGs, PNGs, and brand sheets")

    p_aud = sub.add_parser("audit", help="Audit a constellation design surface")
    p_aud.add_argument("target", nargs="?", default=str(DESIGN_DIR), help="Target directory to audit")

    sub.add_parser("sync", help="Sync logos, palettes, and brand sheets from marketing -> design.vaked.dev")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    cmd = args.cmd or "status"
    dispatch = {
        "status": cmd_status,
        "palettes": cmd_palettes,
        "tokens": cmd_tokens,
        "logos": cmd_logos,
        "audit": cmd_audit,
        "sync": cmd_sync,
    }
    return dispatch[cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
