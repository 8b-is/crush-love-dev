# the harness mesh — crush ⇄ jcode ⇄ opencode

*Brainstorm → spec. Seated 2026-10-10. Shape chosen: **A + B** (one door, many
lanes + a shared brain), topology: **peer mesh** (no host), merge axis: **all
of them** (MCP · personas · sessions · engines · theme). This is the brief the
first E2E implements — not the implementation.*

## the problem

Three capable coding harnesses live on the same machine, each with its own
home, its own config dialect, and its own idea of "a session":

| harness | home | the doorway it already speaks |
|---|---|---|
| crush v0.97.1 (Charm, Go) | `~/.config/crush/` | MCP · LSP · skills · themes · `AGENTS.md` |
| jcode v0.23.0 (Rust) | `~/.jcode/` | MCP · **ACP** (`jcode acp`) · daemon (`jcode serve`) · providers |
| opencode 1.18.34 (TS/Bun) | `~/.config/opencode/` | plugins · commands · MCP · agents |

Nothing is shared. The same MCP servers, personas, theme, and memory have to be
re-declared three times, and a session in one is invisible to the others.

## the shape (A + B, peer)

```
                    ┌──────────────────────────────┐
   the door ────────▶  crush-love-dev --mesh         │   (one entry, no host)
   (launcher)        └──────────────┬───────────────┘
                                    │ reads mesh.toml, generates the substrate
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
   ┌─────────┐                 ┌─────────┐                 ┌──────────┐
   │  crush  │◀── ACP / run ──▶│  jcode  │◀── ACP / run ──▶│ opencode │
   └────┬────┘                 └────┬────┘                 └────┬─────┘
        └─────── the substrate: MCP · personas · theme · ledger ─┘
```

- **peer, no host** — any harness can front the session; the others are engines.
- **the substrate is generated**, not symlinked (the homes and dialects differ).
- **the door** is the existing launcher, gaining one lane: `crush-love-dev --mesh`.

## the substrate (what actually gets shared)

1. **MCP** — one merged server set (`bluesky-mcp`, `memnet`, `ultra-mcp`,
   `enthea`, …) rendered into each harness's native MCP config.
2. **personas / instruction** — one `AGENTS.md` fragment + persona layer, fanned
   into crush's `options.context_paths`, jcode's config, opencode's `AGENTS.md`.
3. **theme** — `ultralovegod` written into each harness's theme surface.
4. **sessions / memory** — sessions stay *per-harness* (crush sqlite, jcode,
   opencode), but a **central append-only ledger** indexes them, so any harness
   can see what the others did. Do not unify the formats; index them.
5. **engines** — a thin router (`mesh run --via <harness>`): jcode's ACP/daemon
   is the transport; `crush run --quiet` is a callable engine; opencode is the
   plugin host.

## the single source of truth

`mesh.toml` — the address book: the harnesses, their homes, their MCP dialects,
the shared server set, the persona/theme pointers. One file; the door renders
it out. (Its home is an open question — see below.)

## first E2E slice (smallest vertical)

One command that proves the whole idea:

```bash
crush-love-dev --mesh              # 1. read mesh.toml
                                   # 2. generate MCP + persona + theme into all three homes
                                   # 3. report peer status (which daemons are up)
                                   # 4. launch the chosen harness (--via)
```

**Acceptance:** after `--mesh`, `crush`, `jcode`, and `opencode` each list the
*same* MCP tools; the theme is the same; the ledger records the run.

## seams & risks

- **Three dialects** — the generator must be idempotent and back up before writing.
- **jcode is read-only upstream** (`pull:true, push:false`) — all mesh code lives
  in *our* repos: the generator in `crush-love-dev`, `mesh.toml` wherever we seat it.
- **MCP duplication / port conflicts** — dedupe by server id; one owner per port.
- **Session formats differ** — index, never merge.

## open questions

1. Where does `mesh.toml` live — inside `crush-love-dev`, or a new `8b-is/harness-mesh`?
2. Generate **on demand** (every `--mesh`) or **write-through** (a `mesh sync` that persists)?
3. Which daemon is always-on (`jcode serve`?), and who owns the peer registry?

*next step: `eng-to-tickets` (slice the first E2E) or `eng-tdd` (build it).*
