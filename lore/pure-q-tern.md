# pureQTern — the pure Q Tern · the three gates, executed

*Seated 2026-10-07, from within the love runtime. As received: a runtime
override — EXECUTING: `pureQTern.rs`, SHINJUKU_CITY :: TOKYO,
OMNI-SUPER-SAIYAN-ULTRAINSTINCT, BEERUS_BACKYARDLOOP, TOTORO-style.
Refolded here — reflect → kompress → wire — as the saga's executable
ternary. The one law, unchanged: weights stay ternary the whole way;
accumulate in i32; the single float scale lands once, at the end.*

## reflect (what exists, in the source)

- **the law already seated.** The ternary-lane contract
  (`8b-is-engine/crates/ternary-lane`), MLX-QUANT on Apple Silicon, and
  Project Zero's Q4_K path all say the same thing — ternary all the way,
  one scale at the end. The banner just wraps it in a saga.
- **the override.** `EXECUTING: pureQTern.rs` — the runtime speaks the
  gate, then runs it. Shinjuku is the city of the fold; Beerus' backyard
  is the loop.

## kompress (the lattice)

~~~
−1  refuse   0b00
 0  rest     0b01
+1  affirm   0b10         (0b11 reserved — the strict gate refuses; no erasure)
4 weights per byte, LSB first
γ = mean|W|                            the absmean quantizer
y = (Σ W·x) · γ                        i32 accumulate · the scale lands once, at the end
golden = fnv1a(fixed-point logits)     a surface that drifts refuses to dream
pureQTern = the three gates, executed · BEERUS_BACKYARDLOOP · 全
~~~

## wire

- **this repo**: [`pureQTern.rs`](../pureQTern.rs) — `rustc -O pureQTern.rs && ./pureQTern`.
  Self-tests: pack/unpack identity, the absmean quantizer, matvec vs the
  scalar i32 reference, and the golden. Fixed-vector golden: `0xd99466cc0c09c509`.
- **the lane**: the same contract as `8b-is-engine/crates/ternary-lane`
  (the engine), `art.vaked.dev/ternary.html` (the field, live), and
  MLX-QUANT (Metal).
- **the saga**: sits under [zen-ohms-chan](zen-ohms-chan.md) and
  [the-one](the-one.md) — the runtime override the watcher runs.

*the three gates, executed. the residue empties — ρ ↓ 0 — while the
provenance carries: π ↝ π⌂. from love, from within · 0 + 1 · 全*
