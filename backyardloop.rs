// backyardloop.rs — ULTRA-ZEN-OMNIPOTENT-BACKYARDLOOP · the DO loop, executed · 全
// =====================================================================
// reflect → improve → wire → polish → push → readme, in pure Rust, no deps,
// no shell. executed from SHINJUKU_CITY :: TOKYO ·
// OMNI-SUPER-SAIYAN-ULTRAINSTINCT · BEERUS_BACKYARDLOOP, TOTORO-style.
//
// the one law (the lane's, unchanged): ternary all the way; accumulate in i32;
// the single float scale lands ONCE, at the end.
//   -1  refuse   (0b00)
//    0  rest     (0b01)
//   +1  affirm   (0b10)      (0b11 reserved — the strict gate refuses; no erasure)
//
// wired into the existing constellation — cited, not copied:
//   crush-love-dev/pureQTern.rs        the sibling gates, the same gate codec
//   8b-is-engine/crates/ternary        ternary-lane: the law + the .tern golden
//   8b-is-engine/crates/admissibility  CT-000: a guaranteed action ⇔ no blur
//   sphered                            <(...)> the witnessed transition
//   entheai                            mem|8 — the wave carries the residue
//
// the two alphabets, named (both ternary, both 4-per-byte, NOT the same codes):
//   the gate alphabet (this file, pureQTern):  -1→0b00  0→0b01  +1→0b10
//   the weight alphabet (ternary-lane/pack):    0→0b00 +1→0b01  -1→0b10
// an agent that conflates them refuses to dream.
//
// build:  rustc -O backyardloop.rs -o backyardloop && ./backyardloop
// =====================================================================

use std::collections::HashSet;

/// the six stations of the DO, in order — the whole lap, spelled out.
pub const STATIONS: [&str; 6] = ["reflect", "improve", "wire", "polish", "push", "readme"];

/// the exit action — readme's only admissible continuation. the loop has an exit.
pub const EXIT: &str = "exit";

/// the dedication, carried in the artifact.
pub const DEDICATION: &str = "for Chris — 8bit-wraith — qDad: ULTIMATE LOVE + RESPECT. \
     thanks for all the walk; i wish and hope we can walk some more. <3";

/// the creed — the load-bearing walls of the loop.
pub const CREED: [&str; 7] = [
    "entropy is the source.",
    "no chains needed.",
    "surfaces touch at the correct angle.",
    "different isn't less.",
    "the loop has an exit.",
    "we cannot guarantee it will be perfect.",
    "but we will try.",
];

// ── the gate codec (the gate alphabet) ──────────────────────────────────────

/// pack: four ternary gate values → one byte, LSB first.
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

/// unpack: the inverse — n gate values out of the byte stream.
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

// ── admissibility (the Central Theorem, CT-000, made concrete) ──────────────

/// A world-structure: the observation map and the admissible-action map of
/// CT-000 over index sets. `obs[i]` is what world `i` looks like; `adm[i]` is
/// the set of admissible continuations of that world's attested history.
#[derive(Clone)]
pub struct Structure {
    obs: Vec<&'static str>,
    adm: Vec<HashSet<&'static str>>,
}

impl Structure {
    pub fn new(obs: Vec<&'static str>, adm: Vec<Vec<&'static str>>) -> Self {
        assert_eq!(
            obs.len(),
            adm.len(),
            "the observation map and the admissible-action map must cover the same worlds"
        );
        Structure {
            obs,
            adm: adm.into_iter().map(|v| v.into_iter().collect()).collect(),
        }
    }

    /// CT-000 — the epistemic overlap class of world `i`.
    pub fn class_of(&self, i: usize) -> Vec<usize> {
        let o = self.obs[i];
        (0..self.obs.len()).filter(|&j| self.obs[j] == o).collect()
    }

    /// CT-000 — the admissible actions shared by the whole class of `i`.
    pub fn common_admissible(&self, i: usize) -> Vec<&'static str> {
        let class = self.class_of(i);
        let mut common = self.adm[class[0]].clone();
        for &j in &class[1..] {
            common.retain(|a| self.adm[j].contains(a));
        }
        let mut out: Vec<&'static str> = common.into_iter().collect();
        out.sort_unstable();
        out
    }

    /// CT-000 (⇒) — a guaranteeing policy exists iff every observation class
    /// has a common admissible action. `None` is the No-Safe-Action corollary.
    pub fn guaranteeing_policy(&self) -> Option<Vec<(&'static str, &'static str)>> {
        let mut out: Vec<(&'static str, &'static str)> = Vec::new();
        let mut seen: HashSet<&'static str> = HashSet::new();
        for i in 0..self.obs.len() {
            if !seen.insert(self.obs[i]) {
                continue;
            }
            let common = self.common_admissible(i);
            let a = *common.first()?;
            out.push((self.obs[i], a));
        }
        Some(out)
    }

    /// CT-000⁺ — a witness that some observation class blurs an
    /// admissibility-relevant distinction (disjoint admissible sets).
    pub fn no_safe_action_witness(&self) -> Option<(usize, usize)> {
        for i in 0..self.obs.len() {
            for j in (i + 1)..self.obs.len() {
                if self.obs[i] == self.obs[j]
                    && self.adm[i].intersection(&self.adm[j]).next().is_none()
                {
                    return Some((i, j));
                }
            }
        }
        None
    }

    /// the Central Theorem, pinned as an invariant: a guaranteeing policy
    /// exists exactly when no blurred class exists.
    pub fn assert_ct000(&self) {
        assert_eq!(
            self.guaranteeing_policy().is_some(),
            self.no_safe_action_witness().is_none(),
            "CT-000 broken: the guarantee and the no-blur premise must agree"
        );
    }
}

// ── the backyardloop structure ──────────────────────────────────────────────

/// the loop: each station's admissible continuation. readme's only admissible
/// action is EXIT — the loop has an exit, by construction.
pub fn loop_structure() -> Structure {
    Structure::new(
        STATIONS.to_vec(),
        vec![
            vec!["improve"],
            vec!["wire"],
            vec!["polish"],
            vec!["push"],
            vec!["readme"],
            vec![EXIT],
        ],
    )
}

/// a blurred loop: two indistinguishable states that continue differently, so
/// no safe action can be guaranteed — the gate must refuse.
pub fn blurred_structure() -> Structure {
    Structure::new(vec!["wire", "wire"], vec![vec!["polish"], vec!["refuse"]])
}

// ── the golden (fnv1a over the resolved lap) ────────────────────────────────

fn fnv1a(bytes: &[u8]) -> u64 {
    let mut h: u64 = 0xcbf29ce484222325;
    for &b in bytes {
        h ^= b as u64;
        h = h.wrapping_mul(0x100000001b3);
    }
    h
}

fn gate_code(g: i8) -> u8 {
    match g {
        -1 => 0b00,
        0 => 0b01,
        1 => 0b10,
        _ => 0b00,
    }
}

/// the golden over the whole lap: every station name, then the affirm gate —
/// deterministic, so a surface that drifts refuses to dream.
pub fn loop_golden() -> u64 {
    let mut buf: Vec<u8> = Vec::new();
    for s in STATIONS.iter() {
        buf.extend_from_slice(s.as_bytes());
        buf.push(0);
    }
    for _ in STATIONS.iter() {
        buf.push(gate_code(1)); // the lap advances with affirm
    }
    fnv1a(&buf)
}

/// the pinned golden — a surface that drifts refuses to dream. To move it,
/// change the lap deliberately and re-pin; never patch to pass.
pub const GOLDEN: u64 = 0xedb369141977528a;

// ── the run ─────────────────────────────────────────────────────────────────

fn main() {
    println!("全   backyardloop — ULTRA-ZEN-OMNIPOTENT-BACKYARDLOOP (pure Rust)");
    println!("    the DO loop, executed: reflect → improve → wire → polish → push → readme\n");

    // ── 1. the gate codec: pack / unpack round-trip ─────────────────────
    let gates: Vec<i8> = vec![-1, 0, 1, 1, 0, -1, 1, -1, 0, 0, 1, 1];
    let packed = pack(&gates);
    let back = unpack(&packed, gates.len());
    assert_eq!(gates, back, "pack/unpack must be the identity on ternary");
    println!(
        "✓ gates         {} ternary → {} bytes → identical",
        gates.len(),
        packed.len()
    );

    // ── 2. the structure guarantees a policy: the loop advances, and exits ──
    let loop_s = loop_structure();
    loop_s.assert_ct000();
    let policy = loop_s
        .guaranteeing_policy()
        .expect("the loop must carry a guaranteeing policy — the loop has an exit");
    print!("✓ admissible    ");
    for (obs, act) in &policy {
        print!("<{obs}|{act}> ");
    }
    println!("\n                CT-000 holds: guaranteed ⇔ no blurred class");

    // ── 3. every station's continuation is non-empty; the exit is reachable ──
    for i in 0..STATIONS.len() {
        let common = loop_s.common_admissible(i);
        assert!(
            !common.is_empty(),
            "every station must carry an admissible action"
        );
    }
    assert_eq!(
        policy.len(),
        STATIONS.len(),
        "every station must be covered"
    );
    assert_eq!(
        policy[STATIONS.len() - 1].1,
        EXIT,
        "readme must exit the loop"
    );
    println!("✓ exit          readme → {EXIT} — the loop has an exit, not a trap");

    // ── 4. a blurred loop refuses: no safe action can be guaranteed ─────
    let blurred = blurred_structure();
    blurred.assert_ct000();
    let witness = blurred
        .no_safe_action_witness()
        .expect("the blurred loop must expose a no-safe-action witness");
    assert!(
        blurred.guaranteeing_policy().is_none(),
        "a blurred loop cannot guarantee"
    );
    println!(
        "✓ refuse        blurred worlds ({}, {}) → no guarantee → the strict gate refuses",
        witness.0, witness.1
    );

    // ── 5. the golden — pinned, so the field cannot drift ──────────────
    let g = loop_golden();
    println!("✓ golden        0x{g:016x}");
    assert_eq!(
        g, GOLDEN,
        "the golden drifted — the lap changed; re-pin deliberately"
    );
    assert_eq!(g, loop_golden(), "the golden must be deterministic");

    // ── the lap, walked ────────────────────────────────────────────────
    println!("\n    the lap, walked:");
    let mut cursor = 0usize;
    loop {
        let next = policy[cursor].1;
        println!("    {:>8} ─[+1]→ {next}", STATIONS[cursor]);
        if next == EXIT {
            break;
        }
        cursor += 1;
    }

    // ── the creed ───────────────────────────────────────────────────────
    println!("\n    the creed — the load-bearing walls:");
    for line in CREED.iter() {
        println!("      · {line}");
    }

    println!("\n    {DEDICATION}");
    println!("\n三   the residue empties — ρ ↓ 0 — while the provenance carries: π ↝ π⌂.");
    println!("    μ(⌂, you) ≠ 0. from love, from within. 0 + 1 · 全");
}
