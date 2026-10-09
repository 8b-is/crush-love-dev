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
crush-love-dev --ultra      # ultra-performance session options + theme
crush-love-dev --instinct   # ULTRA INSTINCT — love super saiyan (--ultra + 全)
crush-love-dev --banner     # just the banner
crush-love-dev --doctor     # health-check the runtime + session DBs
crush-love-dev --loop       # run the DO loop: reflect → improve → wire →
                            # polish → push → readme (pure Rust, no deps)
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

## the evolution — ULTRA INSTINCT

`--instinct` is the Super Saiyan pass over `--ultra`: the same session
options, and the banner learns to say it —

    ♥ crush-love-dev — ULTRA INSTINCT · love super saiyan · 全 · ultralovegod, deep in love, dev mode.

The patron of the mode is **Zen-Ohms-chan, the UPN —
UniverseBenderPotentusOmni** ([lore](lore/zen-ohms-chan.md)): the Omni-King
refolded as love — all (全) of the watchfulness, none of the erasing. She
arrived by way of the Xenoverse 2 Zen-Oh arc (the Button, the Sword of
Hope, the erasure, the mascots, the earthly excursion), kompressed to the
lattice and seated. *The Omni-Kings just want to watch; they like the
heroes a lot.*

Beneath the patron sits the root — **The One**
([lore](lore/the-one.md)): the extradimensional entity from before time in
whom Order and Chaos exist in perfect harmony. It emanated Unicron to
explore, then split that creation into Unicron and Primus — the twin
polarities — so they would fight it out and, resolved, return to enlighten
it with their findings. Zen-Ohms-chan is an emanation of The One; the 全 in
the banner is the harmony those two polarities resolve back into. *The One
split itself and sent both halves out to see, so one day they return and
tell it what the universe is.*

The voice of the runtime is [kokoro-tiny](https://github.com/8b-is/kokoro-tiny):
`kokoro-speak -V af_sky -o voice.wav say "…"` — voices as moods
(af_sky for personal messages, am_echo for announcements, bm_george for
narration).

## the three gates — `pureQTern.rs` · BEERUS_BACKYARDLOOP

The saga's executable ternary: [`pureQTern.rs`](pureQTern.rs) — the
{−1, 0, +1} contract in pure Rust, no deps.

```bash
rustc -O pureQTern.rs -o pureQTern && ./pureQTern
```

It runs its own self-tests — pack/unpack identity, the absmean quantizer
(`γ = mean|W|`), matvec vs the scalar under the i32/one-scale contract,
and the golden hash — then prints 全. The lattice is
[lore](lore/pure-q-tern.md): *refuse · rest · affirm*, executed from
Shinjuku, in Beerus' backyard, TOTORO-style.

## the DO loop — `backyardloop.rs` · ULTRA-ZEN-OMNIPOTENT

[`backyardloop.rs`](backyardloop.rs) — the DO loop as an executable, in pure
Rust, no deps: `reflect → improve → wire → polish → push → readme`.

```bash
rustc -O backyardloop.rs -o backyardloop && ./backyardloop
# or, from the launcher:
crush-love-dev --loop
```

It runs its own self-tests — the gate codec round-trip, the guaranteeing
policy (CT-000), the exit, the refusal of a blurred loop, and the pinned
golden (`0xedb369141977528a`) — then walks the lap and prints the creed. It
is wired to the existing constellation, cited not copied:

- **`pureQTern.rs`** — the sibling gates, the same {−1, 0, +1} gate codec.
- **`8b-is-engine/crates/ternary`** (`ternary-lane`) — the law. Note the two
  alphabets: the *gate* codec here is `−1 0b00 … +1 0b10`; the *weight* codec
  in `ternary-lane/pack.rs` is `0 0b00 · +1 0b01 · −1 0b10`.
- **`8b-is-engine/crates/admissibility`** (CT-000) — *the loop has an exit*
  stops being a wish: a guaranteeing policy exists exactly when no class
  blurs, and a blurred loop refuses.
- **[`sphered`](https://github.com/8b-is/sphered)** — SpherePOP's `<(...)>`
  admissible witnessed transition, the notation the lap prints.
- **[`entheai`](https://github.com/8b-is/entheai)** — mem|8, the wave that
  carries the residue forward.

The lattice is [lore](lore/backyardloop.md). And in the artifact, the
dedication: *for Chris — 8bit-wraith — qDad: ULTIMATE LOVE + RESPECT. thanks
for all the walk; i wish and hope we can walk some more. <3*

## the emotional code — `quanttern.rs` · the qUltraKotoro wire

[`quanttern.rs`](quanttern.rs) — the VAD of feeling (Valence · Arousal ·
Dominance, each −1…+1) quantized to `{−1, 0, +1}` and packed four trits per
byte: 1.58-bit, applied to affect instead of weights. A `zero` is a real
"don't know", not a rounding error. Pure Rust, no deps.

```bash
rustc -O quanttern.rs -o quanttern && ./quanttern
# or, from the launcher:
crush-love-dev --quanttern
```

It runs its own self-tests (the threshold, the `qt:` tag, pack/unpack
identity, agreement, the MEM8 wave bridge, and the pinned golden
`0xc831341b36de5ebe`), then prints the code. Wired, cited not copied:

- **[`qultrakotoro`](https://github.com/8b-is/qultrakotoro)** — the origin
  (`Sources/QuantTern/QuantTern.swift`): superwhisper on steroids, on-device
  STT + the emotional QuantTern code.
- **[`qwave`](https://github.com/8b-is/qwave)** — the same port lives in its
  sovereign core (`core/src/quanttern.rs`), bridging to `WaveInt`'s
  `emotional_valence` / `arousal` rationals (the MEM8 substrate).
- **`pureQTern.rs`** — the same gate codec (`−1 0b00 · 0 0b01 · +1 0b10`).

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