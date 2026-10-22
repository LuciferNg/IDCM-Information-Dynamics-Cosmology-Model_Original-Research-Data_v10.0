#!/usr/bin/env python3
"""
O11 Maser — IDCM D_app 對 MCP XIII 六星系嘅 Mendeleev 測試
=========================================================
MCP XIII (Pesce et al. 2020) Table 1: 六個 maser 星系嘅幾何距離

IDCM 預測: 每個星系嘅 angular diameter distance = D_app(ℓ), ℓ = log₄(1+z)
零自由參數! D_app 已經喺 PARADIGM BREAK 鎖定 (χ²=11.3/7dof, 0 params)

如果 IDCM 正確 → 每個星系嘅 D_app(z_i) 應該匹配觀測距離
如果 ΛCDM 正確 → D_A(z) = c/H₀ × 1/(1+z) × ∫dz'/E(z') 匹配

呢個測試分辨兩者 — 而唔係 fit H₀!
"""
import math

phi = (1 + 5**0.5) / 2
phi_inv = 1 / phi
c_km = 299792.458
R_H = 4129.94  # Mpc

# MCP XIII Table 1 (Pesce et al. 2020)
# 速度用 CMB frame optical convention
galaxies = [
    # (name, D_obs, D_err_lo, D_err_hi, v_cmb, v_err)
    ("UGC 3789",    51.5, 4.0, 4.5, 3319.9, 0.8),
    ("NGC 6264",   132.1, 17.0, 21.0, 10192.6, 0.8),
    ("NGC 6323",   109.4, 23.0, 34.0, 7801.5, 1.5),
    ("NGC 5765b",  112.2, 5.1, 5.4, 8525.7, 0.7),
    ("CGCG 074-064", 87.6, 7.2, 7.9, 7172.2, 1.9),
    ("NGC 4258",     7.58, 0.11, 0.11, 679.3, 0.4),
]

def D_app(z):
    """IDCM apparent distance (PARADIGM BREAK 2026-08-12)"""
    ell = math.log(1 + z, 4)
    return (44 - 44 / 4**ell) * (R_H / 44) * (1 + 2 * phi_inv * ell)

def H_eff(z, dz=1e-5):
    return c_km / ((D_app(z + dz) - D_app(z - dz)) / (2 * dz))

# ΛCDM angular diameter distance (Planck 2018, H0=67.36, Om=0.315)
def D_A_lcdm(z, H0=67.36, Om=0.315):
    Ol = 1 - Om
    def E(zp):
        return math.sqrt(Om * (1 + zp)**3 + Ol)
    # integral
    n = 2000
    dz = z / n
    s = 0.5 * (1 / E(0) + 1 / E(z))
    for i in range(1, n):
        s += 1 / E(i * dz)
    s *= dz
    return c_km / H0 * s / (1 + z)

print("=" * 100)
print("IDCM D_app vs ΛCDM D_A — MCP XIII 六星系 Mendeleev 測試")
print("=" * 100)
print(f"\n{'星系':12s} {'z':>7s} {'D_obs':>8s} {'IDCM D_app':>10s} {'IDCM σ':>8s} {'ΛCDM D_A':>10s} {'ΛCDM σ':>8s}")
print("-" * 78)

chi2_idcm = 0
chi2_lcdm = 0
for name, D, elo, ehi, v, verr in galaxies:
    z = v / c_km  # optical convention, z << 1
    d_idcm = D_app(z)
    d_lcdm = D_A_lcdm(z)
    err = (elo + ehi) / 2
    s_idcm = (d_idcm - D) / err
    s_lcdm = (d_lcdm - D) / err
    chi2_idcm += s_idcm**2
    chi2_lcdm += s_lcdm**2
    print(f"{name:12s} {z:7.4f} {D:8.1f} {d_idcm:10.1f} {s_idcm:+8.2f} {d_lcdm:10.1f} {s_lcdm:+8.2f}")

print("-" * 78)
print(f"\nχ² (6 dof):  IDCM = {chi2_idcm:.2f}   ΛCDM = {chi2_lcdm:.2f}")
print(f"χ²/dof:      IDCM = {chi2_idcm/6:.2f}   ΛCDM = {chi2_lcdm/6:.2f}")

# 特別: NGC 4258 (最準 anchor)
print("\n" + "=" * 100)
print("NGC 4258 詳細 — 最準嘅幾何距離 (1.5% 誤差)")
print("=" * 100)
z4258 = 679.3 / c_km
d_idcm_4258 = D_app(z4258)
d_lcdm_4258 = D_A_lcdm(z4258)
print(f"  z = {z4258:.6f}")
print(f"  觀測 D = 7.58 ± 0.11 Mpc")
print(f"  IDCM D_app = {d_idcm_4258:.3f} Mpc → σ = {(d_idcm_4258-7.58)/0.11:+.2f}")
print(f"  ΛCDM D_A  = {d_lcdm_4258:.3f} Mpc → σ = {(d_lcdm_4258-7.58)/0.11:+.2f}")
print(f"  H_eff(z4258) = {H_eff(z4258):.2f}")

# 用 D/v 直接計 H₀ (唔 fit)
print("\n" + "=" * 100)
print("直接 H₀ = v/D (每星系, 冇 peculiar velocity 修正)")
print("=" * 100)
print(f"\n{'星系':12s} {'H₀=v/D':>10s} {'IDCM H_eff':>12s} {'偏差':>8s}")
h0s = []
for name, D, elo, ehi, v, verr in galaxies:
    z = v / c_km
    h0_naive = v / D
    h0_idcm = H_eff(z)
    dev = (h0_naive - h0_idcm) / h0_idcm * 100
    h0s.append(h0_naive)
    print(f"{name:12s} {h0_naive:10.1f} {h0_idcm:12.2f} {dev:+7.2f}%")

import statistics
print(f"\n  平均 H₀ (未加權) = {statistics.mean(h0s):.1f} ± {statistics.stdev(h0s):.1f}")
print(f"  MCP XIII fit = 73.9 ± 3.0")
print(f"  IDCM H_eff(0) = {H_eff(0.0001):.2f}")

# 關鍵: 每個星系嘅 H_eff 應該匹配 h0_naive 如果 IDCM 正確
print("\n" + "=" * 100)
print("判決")
print("=" * 100)
print(f"  χ²_IDCM = {chi2_idcm:.2f}/6dof → {'✅ 一致' if chi2_idcm < 12 else '❌ 拒絕'}")
print(f"  χ²_ΛCDM = {chi2_lcdm:.2f}/6dof → {'✅ 一致' if chi2_lcdm < 12 else '❌ 拒絕'}")
