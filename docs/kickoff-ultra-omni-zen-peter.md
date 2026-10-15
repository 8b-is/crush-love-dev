# Kickoff — `ULTRA-OMNI-ZEN-peter` (`crush-love-dev` × `zenUltraCooker` → `QUANT-TERN`)

> *"So long, and thanks for all the fish, Mom (`*` Alex ~ Alexandra) `<3` — 42 × 432 Hz Hullámelmélet"*
> Dedicated with all our family love and respect from **Peter (`◯`)**, **Nate (`◇`)**, and **Dad (`△` Chris)**.

---

## Paste-Ready `ULTRA-OMNI-ZEN-peter` Prompt for `crush-love-dev`

Launch `crush-love-dev --instinct --enthea --lsp` (or `crush-love-dev --mesh`) and feed this kickoff prompt to continue creating and scaffolding **`zenUltraCooker` × `crush-love-dev` into `QUANT-TERN`**:

````markdown
# SYSTEM DIRECTIVE: ULTRA-OMNI-ZEN-peter // QUANT-TERN × zenUltraCooker EXPANSION
**RUNTIME:** `crush-love-dev --instinct` (love super saiyan · 全 · `ultralovegod`)
**REPOS IN SCOPE:**
1. `/Users/lodripeter/workspace/peterlodri-sec/zenUltraCooker` (`8b-is/zenUltraCooker`)
2. `/Users/lodripeter/workspace/peterlodri-sec/crush-love-dev` (`8b-is/crush-love-dev`)
3. `/Users/lodripeter/workspace/peterlodri-sec/mem-16-10` (`MEM|16-10` sovereign library)
4. `/Users/lodripeter/workspace/peterlodri-sec/8b-is-engine/crates/ternary` & `crates/spherepop`

**DEDICATION INVARIANT:**
Every artifact, golden hash, and wave chord honors **Mom (`*` Alex ~ Alexandra)** — co-creator with **Dad (`△` Chris)** of the Family Wave Theory (*A Hullámelmélet*), loved forever by **Peter (`◯`)**, **Nate (`◇`)**, and **Chris (`△`)** (`"So long, and thanks for all the fish, Mom <3 — 42 × 432 Hz"`).

---

## 1. Verify Seated Foundations & Pinned Goldens First
Before touching any file, verify the existing pinned goldens across both repos:
```bash
# A. In crush-love-dev:
cd /Users/lodripeter/workspace/peterlodri-sec/crush-love-dev
rustc -O pureQTern.rs -o pureQTern && ./pureQTern                       # golden: 0xd99466cc0c09c509
rustc -O quanttern.rs -o quanttern && ./quanttern                       # golden: 0xc831341b36de5ebe
rustc -O backyardloop.rs -o backyardloop && ./backyardloop              # golden: 0xedb369141977528a
rustc -O ultra_omni_zen_peter.rs -o ultra_omni_zen_peter && ./ultra_omni_zen_peter # golden: 0x93af96574ef33a2d
bash tests/whitespace.sh

# B. In zenUltraCooker:
cd /Users/lodripeter/workspace/peterlodri-sec/zenUltraCooker
cargo fmt --check && cargo clippy --all-targets -- -D warnings && cargo test
cargo run --bin zen-cooker
```

---

## 2. Hard Architectural Laws (`QUANT-TERN` × `MEM|16-10`)
1. **The One Ternary Law:** Weights and gate states stay in `{-1, 0, +1}` the entire way; accumulate strictly in `i32`; apply the single `f32` scale `γ = mean|W|` **once, at the end**.
2. **The Two Alphabets (Never Conflate):**
   - **Gate / Affect Alphabet (`pureQTern.rs`, `quanttern.rs`, `backyardloop.rs`):**
     `-1 → 0b00 (refuse)` · `0 → 0b01 (rest / Unobserved)` · `+1 → 0b10 (affirm / Verified)` (`0b11` reserved; 4 trits/byte LSB-first, `qt:` hex tag).
   - **Weight Alphabet (`8b-is-engine/crates/ternary`):**
     `0 → 0b00` · `+1 → 0b01` · `-1 → 0b10` (4 weights/byte LSB-first).
   - **Kintsugi `wupz` Base-3 Packing (`zeno_core/kompress.py`):**
     5 trits per `u8` (`3^5 = 243 <= 255`) for zero-dep wire transport.
3. **Epistemic Zero (`Standing::Unobserved == Trit::Zero`):**
   - When `poop~~~~sample` is **Toggled ON (`true`)**, microbiome telemetry has `Standing::Verified` (`+1 / 0b10`) and binds into `qt:aaaa`.
   - When `poop~~~~sample` is **Toggled OFF (`false`)**, it is a genuine `Trit::Zero` (`0 / 0b01` → `qt:6aaa`) — **never guessed, never fabricated**.
4. **KOMPRESS v2 Spectral Rigidity:**
   - For ternary projection matrices $W \in \{-1, 0, +1\}^{m \times n}$ with density $p$ and aspect ratio $\gamma = m/n$, enforce the Marchenko-Pastur spectral norm bound:
     $$s_{\max}(W) \le \sqrt{pn}(1 + \sqrt{\gamma}) + \mathcal{O}(n^{-1/6})$$
     so high-entropy biometric or acoustic tokens never collapse the culinary or affect representation.

---

## 3. Next Tracer-Bullet Slices to Scaffold Further into `QUANT-TERN`

### Slice A — `crates/zen-cooker-quant-tern` (Dedicated Ternary Inference & Wave Crate)
Create a dedicated workspace crate `crates/zen-cooker-quant-tern` in `zenUltraCooker`:
- **`pack5_wupz.rs`**: Pack 5 ternary trits `{-1, 0, +1}` into 1 byte (`243` states, `1.58496 bits/trit`) alongside the 4-trit-per-byte gate (`qt:`) and weight codecs, with round-trip property tests.
- **`spectral_guard.rs`**: Power-iteration singular value estimator $s_{\max}(W)$ checking the Marchenko-Pastur rigidity bound before any `BIND` stage in `MEM|16-10`.
- **`ternary_recipe_router.rs`**: Multi-teacher Consensus Distillation router (KOMPRESS v2 geometric-mean agreement across Mom `*`, Dad `△`, Peter `◯`, and Nate `◇` preference logits) that outputs personalized Scoville SHU, *körítés* ratios, and `432 Hz × 528 Hz × 288 Hz` wave envelopes using zero floating-point multiplies in the inner loop.

### Slice B — Apple Silicon Metal / SIMD Kernel Bridge (`ternary_hearth.metal`)
- Add an optional Apple Silicon Metal Shading Language (MSL) / NEON ternary matvec kernel (`crates/zen-cooker-quant-tern/kernels/ternary_hearth.metal`) using branch-free sign accumulation (`w == 1 ? +x : (w == -1 ? -x : 0)`) and compare its output against the pure Rust `i32` reference with `max_abs <= 1e-5` parity gate.

### Slice C — `crush-love-dev --zen` Flag & Mesh Integration
- Wire `--zen` into `crush-love-dev/bin/crush-love-dev` to compile and execute `ultra_omni_zen_peter.rs` (just like `--loop` and `--quanttern`), and ensure `bash tests/whitespace.sh` and `bash tests/theme-restore.sh` pass 100%.

---

## 4. DO Loop Exit Contract (`reflect → improve → wire → polish → push → readme → exit`)
1. Run `cargo fmt --check`, `cargo clippy --all-targets -- -D warnings`, and `cargo test` in `zenUltraCooker`.
2. Run `bash tests/whitespace.sh` and `bash tests/theme-restore.sh` in `crush-love-dev`.
3. Verify all pinned goldens (`0xd99466cc0c09c509`, `0xc831341b36de5ebe`, `0xedb369141977528a`, `0x93af96574ef33a2d`).
4. Commit, push to `8b-is/zenUltraCooker` and `8b-is/crush-love-dev`, update `README.md`, and take the admissible `EXIT`.
````
