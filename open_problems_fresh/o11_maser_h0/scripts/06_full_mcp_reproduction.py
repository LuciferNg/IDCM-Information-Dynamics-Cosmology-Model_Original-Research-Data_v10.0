#!/usr/bin/env python3
"""
O11 Maser — MCP XIII 完整 likelihood 重現 (nuisance z_i) [向量化]
=================================================================
MCP Eq (3)-(4): L = L_D × L_v
- L_D: D_i ~ N(D_model(z_i), σ_D,i²)
- L_v: v_i ~ N(c·z_i, σ_v,i² + σpec²)
- z_i 自由 nuisance, σpec = 250 km/s

比較: ΛCDM D_A vs IDCM D_app
"""
import math
import numpy as np

phi = (1 + 5**0.5) / 2
phi_inv = 1 / phi
c_km = 299792.458
H0_idcm = 72.59
SIGMA_PEC = 250.0

galaxies = [
    ("UGC 3789",    51.5, 4.0, 4.5, 3319.9, 0.8),
    ("NGC 6264",   132.1, 17.0, 21.0, 10192.6, 0.8),
    ("NGC 6323",   109.4, 23.0, 34.0, 7801.5, 1.5),
    ("NGC 5765b",  112.2, 5.1, 5.4, 8525.7, 0.7),
    ("CGCG 074-064", 87.6, 7.2, 7.9, 7172.2, 1.9),
    ("NGC 4258",     7.58, 0.11, 0.11, 679.3, 0.4),
]

def D_app_idcm_vec(z, H0):
    """IDCM D_app on array z"""
    z = np.asarray(z, dtype=float)
    RH = c_km / H0
    ell = np.log1p(z) / np.log(4.0)
    return (44 - 44 / 4.0**ell) * (RH / 44) * (1 + 2 * phi_inv * ell)

def D_A_lcdm_vec(z, H0, Om=0.315):
    """ΛCDM angular diameter distance (vectorized)"""
    z = np.asarray(z, dtype=float)
    Ol = 1 - Om
    # integrate ∫ dz'/E(z') via fixed grid, then interpolate at z
    zgrid = np.linspace(0, 0.05, 1001)
    E = np.sqrt(Om * (1 + zgrid)**3 + Ol)
    integ = np.cumsum(1.0 / E) * (zgrid[1] - zgrid[0])
    integ = np.concatenate([[0], integ])  # integ[0]=0
    # values at arbitrary z: interpolation
    idx = np.searchsorted(zgrid, z)
    idx = np.clip(idx, 0, len(zgrid) - 1)
    val = integ[idx]
    # linear correction
    zprev = np.where(idx > 0, zgrid[np.clip(idx - 1, 0, len(zgrid) - 1)], 0)
    val_prev = integ[np.clip(idx - 1, 0, len(zgrid) - 1)]
    frac = (z - zprev) / np.maximum(zgrid[1] - zgrid[0], 1e-12)
    dcomp = 1.0 / E[np.clip(idx, 0, len(E) - 1)]
    val = val_prev + frac * dcomp * (zgrid[1] - zgrid[0])
    return c_km / H0 * val / (1 + z)

def neg2ll(H0, model):
    """-2 ln L with z_i marginalized (per-galaxy grid optimize)"""
    total = 0.0
    for name, D, elo, ehi, v, verr in galaxies:
        err_d = (elo + ehi) / 2
        sig_v = math.sqrt(verr**2 + SIGMA_PEC**2)
        zc = v / c_km
        zgrid = np.linspace(max(0.0003, zc - 0.012), zc + 0.012, 1201)
        Dm = model(zgrid, H0)
        chi2_d = ((D - Dm) / err_d)**2
        chi2_v = ((v - c_km * zgrid) / sig_v)**2
        total += float(np.min(chi2_d + chi2_v))
    return total

print("=" * 90)
print("MCP XIII 完整 likelihood (z_i nuisance, σpec=250 km/s)")
print("=" * 90)

# 快速掃描
results = {}
for model_name, model in [("ΛCDM D_A", D_A_lcdm_vec), ("IDCM D_app", D_app_idcm_vec)]:
    hs = np.arange(60.0, 95.0, 0.25)
    vals = np.array([neg2ll(h, model) for h in hs])
    best_i = int(np.argmin(vals))
    best_h = hs[best_i]
    best_v = vals[best_i]
    lo = hi = best_h
    for i in range(best_i - 1, -1, -1):
        if vals[i] < best_v + 1:
            lo = hs[i]
        else:
            break
    for i in range(best_i + 1, len(hs)):
        if vals[i] < best_v + 1:
            hi = hs[i]
        else:
            break
    results[model_name] = (best_h, lo, hi, best_v)
    print(f"\n  {model_name}:")
    print(f"    H₀ = {best_h:.2f}  (1σ: {lo:.2f}–{hi:.2f})   min(-2lnL) = {best_v:.1f}")
    print(f"    vs MCP 73.9±3.0 → z = {(best_h - 73.9)/3.0:+.2f}σ")

print("\n" + "=" * 90)
print("零參數測試: H₀ = 72.59 (IDCM 結構值)")
print("=" * 90)
for model_name, model in [("ΛCDM D_A", D_A_lcdm_vec), ("IDCM D_app", D_app_idcm_vec)]:
    v72 = neg2ll(72.59, model)
    bh, lo, hi, bv = results[model_name]
    print(f"  {model_name}: -2lnL(72.59) = {v72:.1f} vs min {bv:.1f} → Δ = {v72-bv:+.1f}")
    print(f"    → 72.59 喺 1σ 內? {'✅ 係' if v72 < bv + 1 else '❌ 唔係'}")

# 逐星系 v_pec (IDCM, H₀=72.59)
print("\n" + "=" * 90)
print("逐星系 v_pec 診斷 (IDCM, H₀=72.59)")
print("=" * 90)
print(f"\n{'星系':12s} {'v_obs':>8s} {'cz_fit':>8s} {'v_pec':>8s} {'v_pec/σ':>7s} {'D_obs':>7s} {'D_fit':>7s}")
for name, D, elo, ehi, v, verr in galaxies:
    err_d = (elo + ehi) / 2
    sig_v = math.sqrt(verr**2 + SIGMA_PEC**2)
    zc = v / c_km
    zgrid = np.linspace(max(0.0003, zc - 0.012), zc + 0.012, 1201)
    Dm = D_app_idcm_vec(zgrid, H0_idcm)
    chi2 = ((D - Dm) / err_d)**2 + ((v - c_km * zgrid) / sig_v)**2
    best_z = zgrid[int(np.argmin(chi2))]
    v_pec = v - c_km * best_z
    print(f"{name:12s} {v:8.1f} {c_km*best_z:8.1f} {v_pec:+8.0f} {v_pec/sig_v:+7.2f} {D:7.1f} {D_app_idcm_vec(best_z, H0_idcm):7.1f}")

print("\n" + "=" * 90)
print("判定")
print("=" * 90)
