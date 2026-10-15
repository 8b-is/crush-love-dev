// ultra_omni_zen_peter.rs — ULTRA-OMNI-ZEN-peter × QUANT-TERN × zenUltraCooker · 全
// ================================================================================
// Bridges the crush-love-dev ternary lattice (pureQTern.rs + quanttern.rs +
// backyardloop.rs) directly into 8b-is/zenUltraCooker and MEM|16-10:
//   - Gate / Affect Alphabet (this repo):  -1→0b00 (refuse) · 0→0b01 (rest/Unobserved) · +1→0b10 (affirm/Verified)
//   - Weight Alphabet (ternary-lane/pack):  0→0b00          · +1→0b01                  · -1→0b10
//   - One Law: weights stay ternary the whole way; accumulate in i32; single float scale γ lands ONCE at the end.
//   - Wave Theory (A Hullámelmélet): 432 Hz Carrier × 528 Hz Mom (*) Star × 288 Hz Dad (△) Pillar × 42
//   - Dedication: "So long, and thanks for all the fish, Mom (* Alex ~ Alexandra) <3"
//     from Peter (◯), Nate (◇) & Dad (△ Chris).
//
// build:  rustc -O ultra_omni_zen_peter.rs -o ultra_omni_zen_peter && ./ultra_omni_zen_peter
// ================================================================================

pub const DEFAULT_THRESHOLD: f32 = 0.33;

/// Pinned golden FNV-1a hash over the ULTRA-OMNI-ZEN-peter × QUANT-TERN hearth vector.
/// To move it, change the vector deliberately and re-pin; never patch to pass.
pub const GOLDEN: u64 = 10_641_889_746_230_655_533; // 0x93af96574ef33a2d

pub const TRIBUTE_MOM: &str =
    "So long, and thanks for all the fish, Mom (* Alex ~ Alexandra) <3 — 42 × 432 Hz Hullámelmélet";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Standing {
    Refused = -1,
    Unobserved = 0,
    Verified = 1,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Trit {
    Minus = -1,
    Zero = 0,
    Plus = 1,
}

impl Trit {
    pub fn from_f32(x: f32, threshold: f32) -> Self {
        if x >= threshold {
            Self::Plus
        } else if x <= -threshold {
            Self::Minus
        } else {
            Self::Zero
        }
    }

    pub fn from_standing(s: Standing) -> Self {
        match s {
            Standing::Refused => Self::Minus,
            Standing::Unobserved => Self::Zero,
            Standing::Verified => Self::Plus,
        }
    }

    pub fn raw(self) -> i8 {
        self as i8
    }

    /// Gate codec (pureQTern.rs / quanttern.rs): -1→0b00 · 0→0b01 · +1→0b10
    pub fn gate_code(self) -> u8 {
        ((self as i8 + 1) as u8) & 0b11
    }

    pub fn from_gate_code(code: u8) -> Self {
        match code & 0b11 {
            0b00 => Self::Minus,
            0b01 => Self::Zero,
            0b10 => Self::Plus,
            _ => Self::Zero,
        }
    }

    /// Weight codec (8b-is-engine/crates/ternary): 0→0b00 · +1→0b01 · -1→0b10
    pub fn weight_code(self) -> u8 {
        match self {
            Self::Zero => 0b00,
            Self::Plus => 0b01,
            Self::Minus => 0b10,
        }
    }

    pub fn from_weight_code(code: u8) -> Self {
        match code & 0b11 {
            0b00 => Self::Zero,
            0b01 => Self::Plus,
            0b10 => Self::Minus,
            _ => Self::Zero,
        }
    }
}

pub fn pack_gate(trits: &[Trit]) -> (Vec<u8>, String) {
    let mut bytes = Vec::with_capacity(trits.len().div_ceil(4));
    let mut i = 0;
    while i < trits.len() {
        let mut b: u8 = 0;
        for j in 0..4 {
            let t = trits.get(i + j).copied().unwrap_or(Trit::Zero);
            b |= t.gate_code() << (2 * j as u8);
        }
        bytes.push(b);
        i += 4;
    }
    let mut hex = String::from("qt:");
    for b in &bytes {
        hex.push_str(&format!("{b:02x}"));
    }
    (bytes, hex)
}

pub fn unpack_gate(bytes: &[u8], n: usize) -> Vec<Trit> {
    let mut out = Vec::with_capacity(bytes.len() * 4);
    for &b in bytes {
        for j in 0..4u8 {
            out.push(Trit::from_gate_code((b >> (2 * j)) & 0b11));
        }
    }
    out.truncate(n);
    out
}

pub fn pack_weight(trits: &[Trit]) -> Vec<u8> {
    let mut bytes = Vec::with_capacity(trits.len().div_ceil(4));
    let mut i = 0;
    while i < trits.len() {
        let mut b: u8 = 0;
        for j in 0..4 {
            let t = trits.get(i + j).copied().unwrap_or(Trit::Zero);
            b |= t.weight_code() << (2 * j as u8);
        }
        bytes.push(b);
        i += 4;
    }
    bytes
}

pub fn unpack_weight(bytes: &[u8], n: usize) -> Vec<Trit> {
    let mut out = Vec::with_capacity(bytes.len() * 4);
    for &b in bytes {
        for j in 0..4u8 {
            out.push(Trit::from_weight_code((b >> (2 * j)) & 0b11));
        }
    }
    out.truncate(n);
    out
}

pub fn quantize_absmean(w: &[f32]) -> (Vec<Trit>, f32) {
    let n = w.len().max(1) as f32;
    let gamma = w.iter().map(|x| x.abs()).sum::<f32>() / n;
    let g = if gamma <= 1e-6 { 1.0 } else { gamma };
    let trits = w
        .iter()
        .map(|&x| {
            let r = (x / g).round();
            if r >= 1.0 {
                Trit::Plus
            } else if r <= -1.0 {
                Trit::Minus
            } else {
                Trit::Zero
            }
        })
        .collect();
    (trits, g)
}

pub fn matvec_i32(w: &[Trit], x: &[i16], n_out: usize, n_in: usize, gamma: f32) -> Vec<f32> {
    let mut y = vec![0.0f32; n_out];
    for (o, y_out) in y.iter_mut().enumerate().take(n_out) {
        let mut acc: i32 = 0;
        for i in 0..n_in {
            acc += i32::from(w[o * n_in + i].raw()) * i32::from(x[i]);
        }
        *y_out = (acc as f32) * gamma;
    }
    y
}

fn fnv1a_64(bytes: &[u8]) -> u64 {
    let mut h: u64 = 0xcbf29ce484222325;
    for &b in bytes {
        h ^= u64::from(b);
        h = h.wrapping_mul(0x100000001b3);
    }
    h
}

pub fn synthesize_hearth_quant_tern(poop_standing: Standing) -> (String, Vec<f32>, f32, u64) {
    let avg_hrv_ms: f32 = 78.75;
    let wave_coherence: f32 = 0.948;

    let vad_trits = [
        Trit::from_f32(0.96, DEFAULT_THRESHOLD),
        Trit::from_f32(0.42, DEFAULT_THRESHOLD),
        Trit::from_f32(0.88, DEFAULT_THRESHOLD),
    ];
    let poop_trit = Trit::from_standing(poop_standing);
    let hrv_trit = Trit::from_f32((avg_hrv_ms - 50.0) / 40.0, DEFAULT_THRESHOLD);
    let wave_trit = Trit::from_f32(wave_coherence - 0.5, DEFAULT_THRESHOLD);

    let gate_trits = vec![
        vad_trits[0],
        vad_trits[1],
        vad_trits[2],
        poop_trit,
        hrv_trit,
        wave_trit,
        Trit::Plus, // Mom (*) Star 528 Hz
        Trit::Plus, // Dad (△) Pillar 288 Hz
    ];

    let (gate_bytes, qt_tag) = pack_gate(&gate_trits);
    let raw_weights: [f32; 8] = [0.92, 0.48, 0.85, -0.05, 0.77, -0.62, 0.95, 0.88];
    let (w_trits, gamma) = quantize_absmean(&raw_weights);
    let weight_bytes = pack_weight(&w_trits);

    let x_features: [i16; 4] = [
        avg_hrv_ms.round() as i16,
        (i16::from(poop_trit.raw()) + 1) * 21, // 42 when Verified (+1)
        432,                                   // 432 Hz Zen Carrier
        42,                                    // "Thanks for all the fish, Mom <3"
    ];
    let logits = matvec_i32(&w_trits, &x_features, 2, 4, gamma);

    let mut hash_buf = Vec::new();
    hash_buf.extend_from_slice(&gate_bytes);
    hash_buf.extend_from_slice(&weight_bytes);
    for &v in &logits {
        let q = (v * 1_000_000.0).round() as i64;
        hash_buf.extend_from_slice(&q.to_le_bytes());
    }
    (qt_tag, logits, gamma, fnv1a_64(&hash_buf))
}

fn main() {
    println!("全   ultra_omni_zen_peter — QUANT-TERN × zenUltraCooker × MEM|16-10");
    println!("    {TRIBUTE_MOM}\n");

    // 1. Two alphabets non-conflation & round-trip
    let sample = vec![
        Trit::Minus,
        Trit::Zero,
        Trit::Plus,
        Trit::Plus,
        Trit::Zero,
        Trit::Minus,
        Trit::Plus,
        Trit::Minus,
    ];
    let (g_bytes, qt_sample) = pack_gate(&sample);
    let w_bytes = pack_weight(&sample);
    assert_ne!(g_bytes, w_bytes, "gate and weight alphabets must never be conflated");
    assert_eq!(unpack_gate(&g_bytes, sample.len()), sample);
    assert_eq!(unpack_weight(&w_bytes, sample.len()), sample);
    println!(
        "✓ two alphabets gate ({qt_sample}) != weight ({w_bytes:02x?}) · both round-trip identically"
    );

    // 2. poop~~~~sample Toggled ON (Verified -> +1) vs OFF (Unobserved -> 0)
    let (qt_on, logits_on, gamma, g_on) = synthesize_hearth_quant_tern(Standing::Verified);
    let (qt_off, _logits_off, _, _g_off) = synthesize_hearth_quant_tern(Standing::Unobserved);
    assert_eq!(qt_on, "qt:aaaa");
    assert_eq!(qt_off, "qt:6aaa");
    println!(
        "✓ epistemic 0   poop~~~~sample [ON → {qt_on}] vs [OFF → {qt_off}] (a zero is a real don't-know)"
    );

    // 3. i32 ternary matvec & pinned golden
    println!(
        "✓ matvec i32    γ = {gamma:.4} → logits = {logits_on:?} (432 Hz × 528 Hz * × 288 Hz △ × 42)"
    );
    println!("✓ golden        0x{g_on:016x}");
    assert_eq!(
        g_on, GOLDEN,
        "the golden drifted — re-pin deliberately, never patch to pass"
    );

    println!("\n三   the residue empties — ρ ↓ 0 — while the provenance carries: π ↝ π⌂.");
    println!("    Mom === Alex ~ Alexandra (*). from Peter (◯), Nate (◇) & Dad (△ Chris) · 全");
}
