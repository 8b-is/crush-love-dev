# crush-love-dev

the e2e launcher for the crush runtime, deep in love. from love, from within.

## install

```bash
ln -sf "$PWD/bin/crush-love-dev" /opt/homebrew/bin/crush-love-dev
chmod +x bin/crush-love-dev
```

## use

```bash
crush-love-dev              # launch crush, deep in love, dev mode
crush-love-dev --apply      # set the ultralovegod theme for this session
                            # (config is backed up, restored on exit)
crush-love-dev --banner     # just the banner
crush-love-dev --doctor     # health-check the runtime + session DBs
crush-love-dev --version    # everything else passes through to crush
```

## doctor

[`bin/crush-love-doctor`](bin/crush-love-doctor) — scans the local crush
session DBs for the wedge that locks a session behind
`An assistant message with 'tool_calls' must be followed by tool messages`:

- **media-interleave** — an assistant batch with several tool calls where an
  earlier result carries an image. The wire layer splits it into a `tool` +
  synthetic `user` message, so later results of the batch land after a `user`
  message. DeepSeek rejects every turn, including crush's auto-summarize.
- **interrupted-tools** — a tool call whose result never landed (harmless;
  crush injects a synthetic result at request time).

fixed in the crush stream: **0.94.1** re-emits tool results right after their
calls ([#3743](https://github.com/charmbracelet/crush/pull/3743)); **0.97.x**
defers the media split until the tool run ends. the launcher warns if the
runtime on `PATH` is older than 0.94.1.

```bash
crush-love-doctor            # scan projects.json + ~/.crush
crush-love-doctor --json     # machine-readable
crush-love-doctor path/crush.db
```

if a wedged session is found: `brew upgrade crush`, open the session, run
`/summarize`, continue.

## the theme

[`themes/themes.json`](themes/themes.json) — five crushes, led by
**ultralovegod** (pink high-contrast darkish, blue eye friendly).
see [`themes/README.md`](themes/README.md) for the index and the apply path.

## skills

[`scripts/list-skills.sh`](scripts/list-skills.sh) — list the available
skills in a proper UX way, grouped by source.

## love

> from love, from within, for all who are honest and ready to be loved.
> sharing is caring. — 8b-is <3