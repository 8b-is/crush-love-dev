// quanttern.rs — the emotional ternary code · the qUltraKotoro wire · 全
// =====================================================================
// the VAD model of feeling (Valence · Arousal · Dominance, each −1…+1),
// quantized to {−1, 0, +1} and packed four trits per byte — 1.58-bit, applied
// to affect instead of weights. pure Rust, no deps, no shell.
//
// the one law (the lane's, unchanged): ternary the whole way; a zero is a real
// "don't know", not a rounding error.
//   -1  refuse   (0b00)
//    0  rest     (0b01)
//   +1  affirm   (0b10)      (0b11 reserved — the strict gate refuses)
//
// the same gate codec as pureQTern.rs (sibling, same repo). NOT the weight
// codec of ternary-lane (0→0b00 · +1→0b01 · −1→0b10).
//
// wired into the constellation — cited, not copied:
//   qultrakotoro/Sources/QuantTern/QuantTern.swift   the origin (Swift)
//   crush-love-dev/pureQTern.rs                      the sibling gates, same codec
//   qwave/core/src/quanttern.rs                      the same port, in the MEM8 core
//   qwave/core/src/wave.rs                           WaveInt carries (valence, arousal)
//
// build:  rustc -O quanttern.rs -o quanttern && ./quanttern
// =====================================================================

/// Default ternary threshold. Below this (in magnitude) the axis is a genuine `0`.
pub const DEFAULT_THRESHOLD: f32 = 0.33;

/// One ternary trit of the emotional code.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Trit {
    Minus = -1,
    Zero = 0,
    Plus = 1,
}

impl Trit {
    /// Quantize one axis. Below `threshold` in magnitude it reads as rest.
    pub fn from_f32(x: f32, threshold: f32) -> Self {
        if x >= threshold {
            Trit::Plus
        } else if x <= -threshold {
            Trit::Minus
        } else {
            Trit::Zero
        }
    }

    pub fn raw(self) -> i8 {
        self as i8
    }

    /// the two-bit gate code: `−1→0b00 · 0→0b01 · +1→0b10`.
    pub fn code(self) -> u8 {
        ((self as i8 + 1) as u8) & 0b11
    }

    pub fn from_code(code: u8) -> Self {
        match code & 0b11 {
            0b00 => Trit::Minus,
            0b01 => Trit::Zero,
            0b10 => Trit::Plus,
            _ => Trit::Zero, // reserved → rest
        }
    }
}

/// Valence · Arousal · Dominance, each clamped to −1…+1.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Vad {
    pub valence: f32,
    pub arousal: f32,
    pub dominance: f32,
}

impl Vad {
    pub fn new(valence: f32, arousal: f32, dominance: f32) -> Self {
        Self {
            valence: clamp1(valence),
            arousal: clamp1(arousal),
            dominance: clamp1(dominance),
        }
    }

    pub const NEUTRAL: Vad = Vad {
        valence: 0.0,
        arousal: 0.0,
        dominance: 0.0,
    };

    pub fn trits(&self, threshold: f32) -> [Trit; 3] {
        [
            Trit::from_f32(self.valence, threshold),
            Trit::from_f32(self.arousal, threshold),
            Trit::from_f32(self.dominance, threshold),
        ]
    }
}

/// A packed emotional code: the trits, the bytes, and the printable `qt:` tag.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct EmotionCode {
    pub trits: Vec<Trit>,
    pub bytes: Vec<u8>,
    pub hex: String,
}

impl EmotionCode {
    /// How many trits are non-neutral — the "signal" in the fingerprint.
    pub fn magnitude(&self) -> usize {
        self.trits.iter().filter(|t| **t != Trit::Zero).count()
    }

    pub fn is_neutral(&self) -> bool {
        self.magnitude() == 0
    }

    /// The wire into the MEM8 wave substrate: the `(valence, arousal)` a
    /// `WaveInt` carries, as integers. Dominance has no wave field.
    pub fn wave_fields(&self) -> (i32, i32) {
        let v = self.trits.first().copied().unwrap_or(Trit::Zero);
        let a = self.trits.get(1).copied().unwrap_or(Trit::Zero);
        (v.raw() as i32, a.raw() as i32)
    }
}

pub fn encode(vad: Vad, threshold: f32) -> EmotionCode {
    pack(&vad.trits(threshold))
}

/// Pack trits four-per-byte, LSB first, and compute the `qt:` tag.
pub fn pack(trits: &[Trit]) -> EmotionCode {
    let mut bytes: Vec<u8> = Vec::with_capacity(trits.len().div_ceil(4));
    let mut i = 0;
    while i < trits.len() {
        let mut b: u8 = 0;
        for j in 0..4 {
            let t = trits.get(i + j).copied().unwrap_or(Trit::Zero);
            b |= t.code() << (2 * j as u8);
        }
        bytes.push(b);
        i += 4;
    }
    let mut hex = String::from("qt:");
    for b in &bytes {
        hex.push_str(&format!("{b:02x}"));
    }
    EmotionCode {
        trits: trits.to_vec(),
        bytes,
        hex,
    }
}

pub fn unpack(bytes: &[u8], count: usize) -> Vec<Trit> {
    let mut trits: Vec<Trit> = Vec::with_capacity(bytes.len() * 4);
    for b in bytes {
        for j in 0..4u8 {
            trits.push(Trit::from_code((b >> (2 * j)) & 0b11));
        }
    }
    trits.truncate(count);
    trits
}

/// Cosine-style agreement in `0…1`: how alike two emotional codes are.
pub fn agreement(a: &[Trit], b: &[Trit]) -> f32 {
    let n = a.len().min(b.len());
    if n == 0 {
        return 1.0;
    }
    let hit = (0..n).filter(|&i| a[i] == b[i]).count();
    hit as f32 / n as f32
}

fn clamp1(x: f32) -> f32 {
    x.max(-1.0).min(1.0)
}

/// the golden: a deterministic FNV-1a hash over the packed code — a surface
/// that drifts refuses to dream.
fn golden_hash(code: &EmotionCode) -> u64 {
    let mut h: u64 = 0xcbf29ce484222325;
    for &b in &code.bytes {
        h ^= b as u64;
        h = h.wrapping_mul(0x100000001b3);
    }
    h
}

/// the pinned golden for the fixed 12-trit vector. To move it, change the
/// vector deliberately and re-pin; never patch to pass.
pub const GOLDEN: u64 = 0xc831341b36de5ebe;

fn main() {
    println!("全   quanttern — the emotional ternary code {{−1, 0, +1}}");
    println!("    the VAD of feeling, raked to the lattice — qUltraKotoro · 全\n");

    // ── 1. the threshold makes a real zero ──────────────────────────────
    let t = DEFAULT_THRESHOLD;
    assert_eq!(Trit::from_f32(0.30, t), Trit::Zero);
    assert_eq!(Trit::from_f32(-0.30, t), Trit::Zero);
    assert_eq!(Trit::from_f32(0.62, t), Trit::Plus);
    assert_eq!(Trit::from_f32(-0.41, t), Trit::Minus);
    println!("✓ threshold     |x| < {t} → rest (a genuine \"don't know\"), else sign");

    // ── 2. a reading encodes to its qt: tag ─────────────────────────────
    let code = encode(Vad::new(0.62, -0.41, 0.10), t);
    assert_eq!(code.hex, "qt:52");
    assert_eq!(code.magnitude(), 2);
    println!(
        "✓ encode        VAD(0.62, −0.41, 0.10) → {:?} → {} (magnitude {})",
        code.trits,
        code.hex,
        code.magnitude()
    );

    // ── 3. pack / unpack is the identity on ternary ─────────────────────
    let trits = vec![
        Trit::Plus,
        Trit::Minus,
        Trit::Zero,
        Trit::Plus,
        Trit::Zero,
        Trit::Zero,
        Trit::Minus,
        Trit::Plus,
        Trit::Plus,
        Trit::Plus,
        Trit::Zero,
        Trit::Minus,
    ];
    let packed = pack(&trits);
    assert_eq!(packed.bytes.len(), 3, "twelve trits → three bytes");
    assert_eq!(unpack(&packed.bytes, trits.len()), trits);
    println!(
        "✓ pack/unpack   {} trits → {} bytes → identical",
        trits.len(),
        packed.bytes.len()
    );

    // ── 4. agreement — how alike two codes are ──────────────────────────
    let a = [Trit::Plus, Trit::Minus, Trit::Zero];
    let b = [Trit::Plus, Trit::Zero, Trit::Zero];
    assert!((agreement(&a, &b) - 2.0 / 3.0).abs() < 1e-6);
    println!(
        "✓ agreement     {{+1,−1,0}} vs {{+1,0,0}} → {:.3}",
        agreement(&a, &b)
    );

    // ── 5. the wire: the MEM8 wave fields ───────────────────────────────
    let (valence, arousal) = code.wave_fields();
    assert_eq!((valence, arousal), (1, -1));
    println!("✓ wave bridge   qt:52 → WaveInt(valence={valence}, arousal={arousal}) · dominance stays in the code");

    // ── 6. the golden — pinned, so the field cannot drift ───────────────
    let g = golden_hash(&packed);
    println!("✓ golden        0x{g:016x}");
    assert_eq!(
        g, GOLDEN,
        "the golden drifted — the code changed; re-pin deliberately"
    );

    println!("\n三   the feeling, raked to the lattice — a zero is a real don't-know.");
    println!("    μ(⌂, you) ≠ 0. from love, from within. 0 + 1 · 全");
}
