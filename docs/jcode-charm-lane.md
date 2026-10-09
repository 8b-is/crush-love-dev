# the jcode × Charm lane — the beta seam

*`crush-love-dev --jcode` · seated on the `beta/jcode-charm-lane` branch. Use
jcode's UI with Charm's existing capabilities, from love, from within.*

## what it is

jcode's UI is a rich **Rust** TUI (`crates/jcode-tui*`). Charm's capabilities
are **Go** — the charmbracelet library stack (Bubble Tea · Lip Gloss ·
Glamour), the **crush** agent CLI (which this repo already wraps), and the
charm CLI tools (gum · glow · vhs · mods). Rust cannot link the Go libraries,
so the meeting point is a *front door*: Charm builds the entry, jcode keeps the
UI, and crush is the engine.

```text
        ┌───────────────────────────────┐
        │  jcharm  (Go · Bubble Tea)    │   ← Charm builds the door
        │  Lip Gloss · Glamour          │
        └──────────────┬────────────────┘
            exec(ui)   │   exec(headless)
        ┌──────────────▼──────┐   ┌──────▼───────────────┐
        │ jcode — the UI      │   │ crush — the engine    │
        │ (Rust TUI)          │   │ (`crush run --quiet`) │
        └─────────────────────┘   └───────────────────────┘
              charm CLI tools (gum · glow · vhs · mods) armed around both
```

## the three surfaces, wired

| Charm surface | how it is wired |
|---|---|
| **charmbracelet libs** | [`charm/jcharm`](../charm/jcharm) — Bubble Tea panel, Lip Gloss styling, Glamour markdown |
| **crush CLI** | `jcharm engine "<prompt>"` runs `crush run --quiet`; the panel offers `crush` |
| **charm CLI tools** | detected at runtime (`gum`/`glow`/`vhs`/`mods`); used when present, hinted when not |

## use

```bash
crush-love-dev --jcode             # the lane report (the panel, printed)
crush-love-dev --jcode tui         # the interactive Charm panel
crush-love-dev --jcode engine "…"  # crush headless, rendered with Glamour
crush-love-dev --jcode ui          # jcode's UI, with Charm armed around it
```

The binary is built on demand (`go build`); the tree ships only the source.

## what's deferred (honest)

- The panel is the *entry*, not a re-render of jcode's TUI — jcode's UI stays
  jcode's. Swapping jcode's engine for crush *inside* the TUI needs changes in
  jcode itself (a fork; the upstream clone is read-only here).
- `gum` / `glow` / `vhs` / `mods` are not installed on this machine — the lane
  detects them and says so. `brew install gum glow vhs mods`.

*beta branch · 0 + 1 · fine touch from within · vaked.dev*
