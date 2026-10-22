#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O60 M31 RAR 檢驗 v3 — Zhang+2024 真實質量模型
================================================
Zhang+2024 (arXiv:2401.01517) 質量模型:
- Bulge: Hernquist, M_b = 10^10.57 = 3.72e10 M☉, q = 0.84 kpc
- Disk: Miyamoto-Nagai, M_d = 10^10.86 = 7.24e10 M☉, a = 5.77 kpc, b = 0.55 kpc
- Halo: NFW, M_vir = 1.14e12 M☉, c = 10^0.94 = 8.71, r_vir = 220 kpc

IDCM RAR: g_obs = g_bar·(1+√(1+4a₀/g_bar))/2
v² = R·g_obs(R) — 零參數!

方法: 只用 baryon (bulge + disk) 質量 → IDCM RAR 預測 V(R)
比較觀測 V_c (Zhang+2024 Table 2)
"""
import numpy as np

G = 4.3009e-6  # kpc (km/s)²/M☉
a0 = 1.1225e-10  # m/s² IDCM 零參數
kpc_to_m = 3.085677581e19

# Zhang+2024 參數 (Table 3 + Section 6.2)
M_b = 10**10.57   # bulge mass M☉
q = 0.84          # kpc Hernquist scale
M_d = 10**10.86   # disk mass M☉
a_mn = 5.77       # kpc Miyamoto-Nagai a
b_mn = 0.55       # kpc Miyamoto-Nagai b

def gbar_bulge(R):
    """Hernquist bulge circular velocity: v² = GM R / (R+q)²"""
    return G * M_b * R / (R + q)**2  # (km/s)²

def gbar_disk(R):
    """Miyamoto-Nagai disk: v² = GM R² / (R² + (a+√(z²+b²))²)^{3/2}, z=0"""
    s = a_mn + b_mn
    return G * M_d * R**2 / (R**2 + s**2)**1.5  # (km/s)²

def V_bar_baryon(R):
    """Total baryon circular velocity (km/s)"""
    v2 = gbar_bulge(R) + gbar_disk(R)
    return np.sqrt(max(v2, 0))

def gbar_ms2(R):
    """baryon gravitational accel in m/s²"""
    v2 = gbar_bulge(R) + gbar_disk(R)
    # v² [km²/s²] / R [kpc] → m/s²: × 1e6 / (kpc_to_m)
    return v2 / R * 1e6 / kpc_to_m

def V_idcm(R):
    """IDCM RAR prediction"""
    gbar = gbar_ms2(R)
    gobs = gbar * (1 + np.sqrt(1 + 4*a0/gbar)) / 2
    return np.sqrt(gobs * R * kpc_to_m) / 1e3  # km/s

# Zhang+2024 觀測 (Table 2: disk 同 halo, 唔重複)
obs = [
    (1.86, 223.8, 10.72), (3.19, 226.79, 7.96), (4.23, 213.74, 8.17),
    (5.32, 212.54, 7.55), (6.27, 221.94, 7.2), (7.2, 223.3, 8.49),
    (8.2, 225.97, 9.28), (9.14, 226.63, 9.07), (9.93, 223.45, 10.29),
    (10.62, 221.25, 10.24), (11.25, 221.17, 11.16), (11.83, 213.58, 9.75),
    (12.48, 215.04, 12.67), (13.37, 215.12, 12.82), (14.29, 217.92, 13.52),
    (15.2, 215.97, 13.09), (16.08, 223.22, 13.07), (17.21, 213.32, 13.44),
    (18.31, 213.85, 15.37), (19.38, 199.73, 15.19),
    (20.41, 220.27, 37.18), (24.12, 219.28, 36.73), (28.63, 222.84, 38.16),
    (34.28, 210.33, 38.76), (39.56, 221.84, 36.68), (46.21, 185.33, 38.68),
    (52.08, 182.05, 38.15), (67.26, 202.02, 40.67), (98.74, 192.59, 42.23),
    (123.56, 168.53, 41.34),
]

print("=" * 72)
print("M31 RAR 檢驗 v3 — Zhang+2024 baryon 質量 + IDCM RAR")
print("=" * 72)
print(f"Bulge: M_b = {M_b:.2e} M☉, q = {q} kpc (Hernquist)")
print(f"Disk : M_d = {M_d:.2e} M☉, a = {a_mn}, b = {b_mn} kpc (Miyamoto-Nagai)")
print(f"IDCM a₀ = {a0:.4e} m/s² (零參數)")
print(f"\n{'R(kpc)':>8} {'V_bar':>7} {'V_IDCM':>8} {'V_obs':>7} {'Δ(V_IDCM-obs)':>14} {'σ':>5}")

chi2 = 0
n = 0
diffs = []
for R, vc, err in obs:
    Vb = V_bar_baryon(R)
    V = V_idcm(R)
    diff = V - vc
    sig = diff / err if err > 0 else 0
    diffs.append(diff)
    chi2 += (diff/err)**2
    n += 1
    print(f"{R:8.2f} {Vb:7.1f} {V:8.1f} {vc:7.1f} {diff:+10.1f} {sig:+5.1f}")

print(f"\nχ² = {chi2:.1f} / {n} dof = {chi2/n:.2f}")
print(f"平均偏差 = {np.mean(diffs):.1f} km/s")
print(f"平均|偏差| = {np.mean(np.abs(diffs)):.1f} km/s")

# 外部區域 (R > 20 kpc, 純 halo 主導)
print(f"\n外部區域 (R>20 kpc, halo 主導):")
ext = [(R, vc, err) for R, vc, err in obs if R > 20]
chi2e = sum(((V_idcm(R)-vc)/err)**2 for R, vc, err in ext)
print(f"  χ² = {chi2e:.1f} / {len(ext)} = {chi2e/len(ext):.2f}")
for R, vc, err in ext:
    V = V_idcm(R)
    print(f"  R={R:7.2f}: V_IDCM={V:6.1f} vs obs {vc:6.1f} → Δ={V-vc:+6.1f} ({ (V-vc)/err:+.1f}σ)")

# 內部 (R<5 kpc, disk/bulge 主導)
print(f"\n內部區域 (R<5 kpc, baryon 主導):")
inn = [(R, vc, err) for R, vc, err in obs if R < 5]
chi2i = sum(((V_idcm(R)-vc)/err)**2 for R, vc, err in inn)
print(f"  χ² = {chi2i:.1f} / {len(inn)} = {chi2i/len(inn):.2f}")
for R, vc, err in inn:
    V = V_idcm(R)
    print(f"  R={R:6.2f}: V_IDCM={V:6.1f} vs obs {vc:6.1f} → Δ={V-vc:+6.1f} ({ (V-vc)/err:+.1f}σ)")

print(f"""
結論:
  IDCM RAR (零參數, 只用 baryon 質量) 對 M31 嘅預測:
  內部 (R<5 kpc): baryon 主導, RAR 修正細 → 應該準確
  外部 (R>20 kpc): baryon 佔比跌 → RAR 深修正區 → 最強檢驗
  ⚠️ 如果 IDCM 正確, 外部應該 match (零參數!)
  ⚠️ 如果 IDCM 錯, 外部會偏離 (需要 DM halo)
""")
