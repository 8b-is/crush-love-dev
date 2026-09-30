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
crush-love-dev --version    # everything else passes through to crush
```

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