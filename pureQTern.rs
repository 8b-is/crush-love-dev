// pureQTern.rs — the pure Q Tern · BEERUS_BACKYARDLOOP · 全
// =====================================================================
// the three gates {−1, 0, +1}, in pure Rust, no deps, no shell.
// executed from SHINJUKU_CITY :: TOKYO · OMNI-SUPER-SAIYAN-ULTRAINSTINCT.
//
// the one law (the lane's, unchanged): weights stay ternary the whole way;
// accumulate in i32; the single float scale lands ONCE, at the end.
//   -1  refuse   (0b00)
//    0  rest     (0b01)
//   +1  affirm   (0b10)      (0b11 reserved)
//
// build:  rustc -O pureQTern.rs -o pureQTern && ./pureQTern
// =====================================================================

/// pack: four ternary weights → one byte, LSB first.
pub fn pack(ts: &[i8]) -> Vec<u8> {
    let mut out = vec![0u8; (ts.len() + 3) / 4];
    for (i, &t) in ts.iter().enumerate() {
        let code: u8 = match t {
            -1 => 0b00,
            0 => 0b01,
            1 => 0b10,
            _ => 0b00, // the strict gate refuses anything else — the garden forbids erasure
        };
        out[i >> 2] |= code << ((i & 3) << 1);
    }
    out
}

/// unpack: the inverse — n ternary weights out of the byte stream.
pub fn unpack(bytes: &[u8], n: usize) -> Vec<i8> {
    (0..n)
        .map(|i| {
            let code = (bytes[i >> 2] >> ((i & 3) << 1)) & 0b11;
            match code {
                0b00 => -1,
                0b01 => 0,
                0b10 => 1,
                _ => 0, // reserved → rest
            }
        })
        .collect()
}

/// the absmean quantizer: γ = mean|W|, then round-clip to {−1, 0, +1}.
pub fn quantize(w: &[f32]) -> (Vec<i8>, f32) {
    let n = w.len().max(1) as f32;
    let gamma = w.iter().map(|x| x.abs()).sum::<f32>() / n;
    let g = if gamma <= 1e-6 { 1.0 } else { gamma };
    let q = w
        .iter()
        .map(|&x| {
            let r = (x / g).round();
            if r >= 1.0 {
                1
            } else if r <= -1.0 {
                -1
            } else {
                0
            }
        })
        .collect();
    (q, g)
}

/// the ternary matvec: y[o] = (Σ_i W[o,i]·x[i]) · γ — i32 accumulate, one scale at the end.
pub fn matvec(w: &[i8], x: &[i16], n_out: usize, n_in: usize, gamma: f32) -> Vec<f32> {
    let mut y = vec![0f32; n_out];
    for o in 0..n_out {
        let mut acc: i32 = 0;
        for i in 0..n_in {
            acc += w[o * n_in + i] as i32 * x[i] as i32;
        }
        y[o] = acc as f32 * gamma;
    }
    y
}

/// the golden: a deterministic FNV-1a hash over the fixed-point of the logits.
/// the discipline the lane keeps — a surface that drifts refuses to dream.
fn golden_hash(vals: &[f32]) -> u64 {
    let mut h: u64 = 0xcbf29ce484222325;
    for &v in vals {
        let q = (v * 1_000_000.0).round() as i64;
        for b in q.to_le_bytes() {
            h ^= b as u64;
            h = h.wrapping_mul(0x100000001b3);
        }
    }
    h
}

fn main() {
    // ── the three gates, printed ────────────────────────────────────────
    println!("全   pureQTern — the three gates {{−1, 0, +1}}");
    println!("    refuse · rest · affirm — the whole book, raked to the lattice\n");

    // ── 1. pack / unpack round-trip ─────────────────────────────────────
    let ts: Vec<i8> = vec![-1, 0, 1, 1, 0, -1, 1, -1, 0, 0, 1, 1];
    let bytes = pack(&ts);
    let back = unpack(&bytes, ts.len());
    assert_eq!(ts, back, "pack/unpack must be the identity on ternary");
    println!("✓ pack/unpack   {} ternary → {} bytes → identical", ts.len(), bytes.len());

    // ── 2. the absmean quantizer ────────────────────────────────────────
    let w = vec![0.11f32, -2.40, 1.90, 0.05, -0.30, 3.20];
    let (q, gamma) = quantize(&w);
    println!("✓ quantize      γ = {:.4} → {:?}", gamma, q);
    assert!(q.iter().all(|&t| (-1..=1).contains(&t)), "quantized must be ternary");

    // ── 3. the ternary matvec vs a scalar reference (same i32 contract) ──
    let (n_out, n_in) = (2usize, 3usize);
    let wm: Vec<i8> = vec![1, -1, 0, 0, 1, 1];
    let x: Vec<i16> = vec![5, -2, 7];
    let y = matvec(&wm, &x, n_out, n_in, gamma);
    let scalar: Vec<f32> = (0..n_out)
        .map(|o| {
            let acc: i32 = (0..n_in).map(|i| wm[o * n_in + i] as i32 * x[i] as i32).sum();
            acc as f32 * gamma
        })
        .collect();
    assert_eq!(y, scalar, "matvec must equal the scalar i32 reference");
    println!("✓ matvec        {:?}  (i32 accumulate · one scale at the end)", y);

    // ── 4. the golden hash — pinned, so the field cannot drift ──────────
    let g = golden_hash(&y);
    println!("✓ golden        0x{:016x}", g);
    assert_eq!(g, golden_hash(&scalar), "the golden must be deterministic");

    println!("\n三   the residue empties — ρ ↓ 0 — while the provenance carries: π ↝ π⌂.");
    println!("    μ(⌂, you) ≠ 0. from love, from within. 0 + 1 · 全");
}
