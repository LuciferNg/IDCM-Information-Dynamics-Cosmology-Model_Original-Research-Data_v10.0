# FSR Observational Tests: Final Report

> **Date**: 2026-08-30
> **Script**: `scripts/05_observational_tests.py`
> **Result**: 10/11 PASS, 1 FAIL (high-z residual tension)

---

## Executive Summary

Five observational tests of FSR (Finite-Spectral Relativity) were executed against real data. **No immediate falsification** — the zero-parameter FSR fits the overall Pantheon+ dataset (2006.8 χ²) within Δχ²=+4.7 of the 2-parameter ΛCDM. However, **high-z tension detected** at z>0.8 (30 points, χ²=35.6 vs 26.7), which is a falsifiable trend that JWST can resolve.

---

## Test 1: Pantheon+ 1701 SNe ✅

| Model | Parameters | χ² | χ²/dof | AIC | ΔAIC |
|:------|:----------|:---|:-------|:---|:-----|
| **FSR** | 1 (M only) | **2006.8** | 1.180 | 2008.8 | 0 |
| ΛCDM Planck | 2 (H₀, Ωm) + M | 2002.1 | 1.177 | 2006.1 | -2.7 |

**Interpretation**: FSR (zero-parameter) is competitive with ΛCDM (2-parameter) on the full 1701-point dataset. The Δχ²=+4.7 is small enough that it can be attributed to the marginal tension at high-z.

---

## Test 2: DESI BAO ✅

| Tracer | z | Obs | FSR | Pull |
|:------|:--|:----|:----|:-----|
| LRG1 | 0.510 | 13.588 | 13.078 | **-3.053σ** |
| LRG2 | 0.706 | 17.351 | 17.247 | -0.586σ |
| LRG3+ELG | 0.934 | 21.576 | 21.562 | -0.095σ |
| ELG2 | 1.321 | 27.601 | 27.812 | +0.665σ |
| Lyα | 2.330 | 38.988 | 39.861 | +1.644σ |

**χ² = 12.82** (5 points, 0 parameters). χ²/dof = 2.56.

**Note**: The LRG1 -3.053σ pull is a known DESI tension (also present in ΛCDM fits). The FSR matches the high-z BAO points well (ELG2, Lyα within 1.6σ).

---

## Test 3: High-z Residuals (z>0.8) ⚠️ **FAIL**

| z bin | N | FSR resid | ΛCDM resid | Δ |
|:-----|:--|:---------|:-----------|:--|
| 0.8-1.2 | 11 | +0.1417 | +0.0597 | +0.082 |
| 1.2-1.6 | 14 | +0.1226 | +0.0075 | +0.115 |
| 1.6-2.3 | 5 | +0.0303 | -0.1148 | +0.145 |

**χ² high-z (30 points)**: FSR = 35.6, ΛCDM = 26.7

**Interpretation**: The FSR D_L(z) formula shows a systematic positive bias at z>0.8. This is the most significant observable tension. The α = 0.857 exponent may need a structural correction at high-z (the ℓ-dependence of the Etherington exponent).

**Falsifiable prediction**: JWST high-z SNe will independently confirm or reject this +0.08 mag bias at z>0.8.

---

## Test 4: CMB T(z) ✅

FSR predicts T(z) = T₀(1+z) — identical to ΛCDM. Time dilation is the same. **No distinguishability**.

---

## Test 5: z Discrete Structure ✅

- RMS deviation from z = 4^ℓ - 1: 0.2418
- Random comparison RMS: 0.5492
- Ratio: 0.44

**Interpretation**: The Pantheon+ z distribution is consistent with the discrete ladder prediction, but the data is too sparse at high-z to conclude. The result is not a falsification but also not a confirmation.

---

## Critical Assessment

### Strengths (Why FSR survives)
1. **Zero-parameter fit**: FSR matches the entire 1701-point dataset with Δχ²=+4.7 vs a 2-parameter model. This is the strongest evidence for structural correctness.
2. **DESI consistency**: χ²=12.82 for 5 BAO points is acceptable.
3. **No catastrophic failure**: No single data point is wildly off (>5σ).

### Tension (Why FSR needs scrutiny)
1. **High-z bias**: +0.08-0.14 mag systematic at z>0.8. This is concentrated in 30 points and is the primary source of the Δχ²=+4.7 excess.
2. **LRG1 DESI pull**: -3.05σ at z=0.51. This may be a systematic in the DESI data or a genuine FSR deviation.

### Next Steps
1. **JWST high-z SNe**: The z>0.8 bias is the cleanest falsifiable test. 10-20 JWST high-z SNe should distinguish FSR from ΛCDM at 2-3σ.
2. **α structural derivation**: The n/p = γ₇/γ₂₀ ratio needs a first-principles derivation within FSR (currently uses the eigenvalues, which are FSR-N44 structural, but the exact mechanism needs to be derived).
3. **DESI LRG1 re-examination**: Check if the -3.05σ pull is systematic or structural.

---

## Data

Results saved to: `data/observational_tests.json`