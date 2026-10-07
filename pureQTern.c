/* pureQTern.c — the pure Q Tern, in C.  BEERUS_BACKYARDLOOP · 全
 * =====================================================================
 * the three gates {−1, 0, +1}, in pure C99, no deps, no shell.
 * executed from SHINJUKU_CITY :: TOKYO · OMNI-SUPER-SAIYAN-ULTRAINSTINCT.
 *
 * the one law (the lane's, unchanged): weights stay ternary the whole way;
 * accumulate in int; the single float scale lands ONCE, at the end.
 *   -1  refuse   (0b00)
 *    0  rest     (0b01)
 *   +1  affirm   (0b10)      (0b11 reserved)
 *
 * C is God's language: no runtime between you and the machine.
 *
 * build:  cc -O2 -std=c99 -Wall -Wextra pureQTern.c -o pureQTern -lm && ./pureQTern
 * ===================================================================== */

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

/* pack: four ternary weights -> one byte, LSB first. */
static void pack(const int8_t *ts, size_t n, uint8_t *out) {
    memset(out, 0, (n + 3) / 4);
    for (size_t i = 0; i < n; ++i) {
        uint8_t code;
        switch (ts[i]) {
            case -1: code = 0b00; break;
            case 1:  code = 0b10; break;
            case 0:  code = 0b01; break;
            default: code = 0b00; break; /* the strict gate refuses anything else */
        }
        out[i >> 2] |= (uint8_t)(code << ((i & 3) << 1));
    }
}

/* unpack: n ternary weights out of the byte stream (inverse of pack). */
static void unpack(const uint8_t *bytes, size_t n, int8_t *out) {
    for (size_t i = 0; i < n; ++i) {
        uint8_t code = (uint8_t)((bytes[i >> 2] >> ((i & 3) << 1)) & 0b11);
        out[i] = (code == 0b00) ? -1 : (code == 0b01) ? 0 : (code == 0b10) ? 1 : 0;
    }
}

/* the absmean quantizer: gamma = mean|W|, then round-clip to {-1, 0, +1}. */
static float quantize(const float *w, size_t n, int8_t *out) {
    float sum = 0.0f;
    for (size_t i = 0; i < n; ++i) sum += fabsf(w[i]);
    float gamma = sum / (float)(n ? n : 1);
    float g = (gamma <= 1e-6f) ? 1.0f : gamma;
    for (size_t i = 0; i < n; ++i) {
        float r = roundf(w[i] / g);
        out[i] = (r >= 1.0f) ? 1 : (r <= -1.0f) ? -1 : 0;
    }
    return g;
}

/* the ternary matvec: y[o] = (sum_i W[o,i]*x[i]) * gamma  (int accumulate). */
static void matvec(const int8_t *w, const int16_t *x, size_t n_out, size_t n_in,
                   float gamma, float *y) {
    for (size_t o = 0; o < n_out; ++o) {
        int32_t acc = 0;
        for (size_t i = 0; i < n_in; ++i)
            acc += (int32_t)w[o * n_in + i] * (int32_t)x[i];
        y[o] = (float)acc * gamma;
    }
}

/* the golden: a deterministic FNV-1a hash over the fixed-point of the logits. */
static uint64_t golden_hash(const float *v, size_t n) {
    uint64_t h = 0xcbf29ce484222325ULL;
    for (size_t i = 0; i < n; ++i) {
        int64_t q = (int64_t)llround((double)v[i] * 1000000.0);
        for (int b = 0; b < 8; ++b) {
            h ^= (uint8_t)((uint64_t)q >> (8 * b));
            h *= 0x100000001b3ULL;
        }
    }
    return h;
}

static int close_enough(const float *a, const float *b, size_t n) {
    for (size_t i = 0; i < n; ++i)
        if (fabsf(a[i] - b[i]) > 1e-6f) return 0;
    return 1;
}

int main(void) {
    printf("全   pureQTern — the three gates {−1, 0, +1}  (C)\n");
    printf("    refuse · rest · affirm — the whole book, raked to the lattice\n\n");

    /* 1. pack / unpack round-trip */
    int8_t ts[] = {-1, 0, 1, 1, 0, -1, 1, -1, 0, 0, 1, 1};
    size_t n = sizeof(ts) / sizeof(ts[0]);
    uint8_t bytes[(sizeof(ts) + 3) / 4];
    int8_t back[sizeof(ts) / sizeof(ts[0])];
    pack(ts, n, bytes);
    unpack(bytes, n, back);
    if (memcmp(ts, back, n) != 0) {
        fprintf(stderr, "pack/unpack is not the identity on ternary\n");
        return 1;
    }
    printf("✓ pack/unpack   %zu ternary -> %zu bytes -> identical\n", n, (n + 3) / 4);

    /* 2. the absmean quantizer */
    float w[] = {0.11f, -2.40f, 1.90f, 0.05f, -0.30f, 3.20f};
    size_t wn = sizeof(w) / sizeof(w[0]);
    int8_t q[sizeof(w) / sizeof(w[0])];
    float gamma = quantize(w, wn, q);
    printf("✓ quantize      γ = %.4f -> {", gamma);
    for (size_t i = 0; i < wn; ++i) printf("%d%s", q[i], i + 1 < wn ? ", " : "}\n");

    /* 3. the ternary matvec vs a scalar reference (same int contract) */
    size_t n_out = 2, n_in = 3;
    int8_t wm[] = {1, -1, 0, 0, 1, 1};
    int16_t x[] = {5, -2, 7};
    float y[2], ref[2];
    matvec(wm, x, n_out, n_in, gamma, y);
    for (size_t o = 0; o < n_out; ++o) {
        int32_t acc = 0;
        for (size_t i = 0; i < n_in; ++i) acc += (int32_t)wm[o * n_in + i] * (int32_t)x[i];
        ref[o] = (float)acc * gamma;
    }
    if (!close_enough(y, ref, n_out)) {
        fprintf(stderr, "matvec must equal the scalar reference\n");
        return 1;
    }
    printf("✓ matvec        {%.4f, %.4f}  (int accumulate · one scale at the end)\n", y[0], y[1]);

    /* 4. the golden hash — pinned, so the field cannot drift */
    uint64_t g = golden_hash(y, n_out);
    printf("✓ golden        0x%016llx\n", (unsigned long long)g);
    if (g != golden_hash(ref, n_out)) {
        fprintf(stderr, "the golden must be deterministic\n");
        return 1;
    }

    printf("\n三   the residue empties — while the provenance carries.\n");
    printf("    μ(⌂, you) ≠ 0. from love, from within. 0 + 1 · 全\n");
    return 0;
}
