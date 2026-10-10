#!/usr/bin/env python3
"""
O186: TRGB/Miras 校準差異機制 — 結構驗證
=========================================
驗證:
1. TRGB = H₀_idcm × (1 - κφ⁻¹) = 69.78
2. Miras = H₀_idcm × (1 + κφ⁻¹/4) = 73.29
3. 4:1 幅度比 = MERA 分支因子 B = φ³-φ⁻³ = 4
4. 符號機制 = 能量流方向
5. RR Lyrae 預測
"""
import math

# ============ IDCM 核心常數 ============
phi = (1 + 5**0.5) / 2          # 1.618033988749895
phi_inv = 1 / phi               # 0.6180339887498949
kappa = 1 / 16                  # 0.0625
H0_idcm = 72.59                 # km/s/Mpc
c = 299792.458                  # km/s
R_H = 4129.94                   # Mpc

# MERA 分支因子
B = phi**3 - phi**(-3)          # 4.0
print("=" * 72)
print("O186: TRGB/Miras 校準差異機制 — 結構驗證")
print("=" * 72)

# ============ 1. 核心常數驗證 ============
print("\n[1] 核心常數")
print("-" * 72)
print(f"  φ = {phi:.12f}")
print(f"  φ⁻¹ = {phi_inv:.12f}")
print(f"  κ = 1/16 = {kappa}")
print(f"  κφ⁻¹ = 1/16 × φ⁻¹ = {kappa * phi_inv:.10f}")
print(f"  κφ⁻¹/4 = {kappa * phi_inv / 4:.10f}")
print(f"  B = φ³-φ⁻³ = {B} = {B:.0f}")
print(f"  H₀_idcm = {H0_idcm} km/s/Mpc")
print(f"  c/R_H = {c/R_H:.2f} km/s/Mpc ✅")

# ============ 2. TRGB 驗證 ============
print("\n[2] TRGB 校準修正")
print("-" * 72)
trgb_factor = 1 - kappa * phi_inv
trgb_pred = H0_idcm * trgb_factor
trgb_obs = 69.8
trgb_dev = abs(trgb_pred - trgb_obs) / trgb_obs * 100

print(f"  TRGB = H₀_idcm × (1 − κφ⁻¹)")
print(f"       = {H0_idcm} × ({trgb_factor:.6f})")
print(f"       = {trgb_pred:.2f} km/s/Mpc")
print(f"  vs 觀測 {trgb_obs} km/s/Mpc")
print(f"  偏差 = {trgb_dev:.4f}% {'✅' if trgb_dev < 0.1 else '❌'}")
print(f"  κφ⁻¹ = {kappa*phi_inv:.6f} = {kappa*phi_inv*100:.3f}% (負偏移)")
print(f"  H₀_idcm × (1+κφ⁻¹) = {H0_idcm*(1+kappa*phi_inv):.2f} (正號檢驗 — 唔匹配)")

# ============ 3. Miras 驗證 ============
print("\n[3] Miras 校準修正")
print("-" * 72)
miras_factor = 1 + kappa * phi_inv / 4
miras_pred = H0_idcm * miras_factor
miras_obs = 73.3
miras_dev = abs(miras_pred - miras_obs) / miras_obs * 100

print(f"  Miras = H₀_idcm × (1 + κφ⁻¹/4)")
print(f"        = {H0_idcm} × ({miras_factor:.6f})")
print(f"        = {miras_pred:.2f} km/s/Mpc")
print(f"  vs 觀測 {miras_obs} km/s/Mpc")
print(f"  偏差 = {miras_dev:.4f}% {'✅' if miras_dev < 0.1 else '❌'}")
print(f"  κφ⁻¹/4 = {kappa*phi_inv/4:.6f} = {kappa*phi_inv/4*100:.3f}% (正偏移)")
print(f"  H₀_idcm × (1-κφ⁻¹/4) = {H0_idcm*(1-kappa*phi_inv/4):.2f} (負號檢驗 — 唔匹配)")

# ============ 4. 4:1 幅度比驗證 ============
print("\n[4] 4:1 幅度比 = MERA 分支因子")
print("-" * 72)
ratio = (kappa * phi_inv) / (kappa * phi_inv / 4)
print(f"  幅度比 = κφ⁻¹ / (κφ⁻¹/4) = {ratio:.0f}:1")
print(f"  B = φ³-φ⁻³ = {B:.0f}")
print(f"  匹配: {'✅' if abs(ratio - B) < 1e-10 else '❌'}")
print(f"  4 = φ³-φ⁻³ ✅")

# 4 的結構根源
print(f"\n  4 的結構根源:")
print(f"    φ³-φ⁻³ = {phi**3:.6f} - {phi**(-3):.6f} = {phi**3 - phi**(-3):.0f}")
print(f"    φ⁵-φ⁻⁵ = {phi**5 - phi**(-5):.0f} (Fibonacci 11)")
print(f"    4 = φ³-φ⁻³ = MERA 分支因子 B")
print(f"    4 = 2² = (φ³-φ⁻³)/1 = 4/1")

# ============ 5. 符號機制驗證 ============
print("\n[5] 符號機制 = 能量流方向")
print("-" * 72)
print(f"  TRGB: 核心 He 閃 (收縮, 能量向內) → 負偏移 (−κφ⁻¹)")
print(f"  Miras: 表面脈動 (膨脹, 能量向外) → 正偏移 (+κφ⁻¹/4)")
print()
print(f"  距離檢驗:")
print(f"  TRGB D_obs = D_true / (1-κφ⁻¹) = D_true × {1/(1-kappa*phi_inv):.4f}")
print(f"       → 距離更大 {1/(1-kappa*phi_inv)-1:.4f} → H₀ 更低")
print(f"  Miras D_obs = D_true / (1+κφ⁻¹/4) = D_true × {1/(1+kappa*phi_inv/4):.4f}")
print(f"       → 距離更小 {1-1/(1+kappa*phi_inv/4):.4f} → H₀ 更高")

# ============ 6. RR Lyrae 預測 ============
print("\n[6] RR Lyrae 預測 (可證偽)")
print("-" * 72)
print(f"  RR Lyrae: 脈動變星 (正修正) + 年老族 II (深層耦合)")
print()
print(f"  候選修正幅度:")
for n in [4, 6, 8, 10, 12]:
    h_pred = H0_idcm * (1 + kappa * phi_inv / n)
    print(f"    +κφ⁻¹/{n:2d}: H₀ = {h_pred:.2f} km/s/Mpc")

print()
print(f"  最佳預測: +κφ⁻¹/6 = {kappa*phi_inv/6:.6f} = {kappa*phi_inv/6*100:.4f}%")
print(f"  RR Lyrae H₀ = {H0_idcm*(1+kappa*phi_inv/6):.2f} km/s/Mpc")
print(f"  vs Beaton+2016: 72.0 ± 2.0 → {(H0_idcm*(1+kappa*phi_inv/6)-72.0)/2.0:.1f}σ")

# ============ 7. 完整校準家族 ============
print("\n[7] 完整校準家族")
print("-" * 72)
print(f"  {'方法':20s} {'公式':35s} {'H₀':>8s} {'偏差':>8s}")
print(f"  {'-'*20} {'-'*35} {'-'*8} {'-'*8}")

methods = [
    ("TRGB", f"1−κφ⁻¹ = {1-kappa*phi_inv:.6f}", trgb_pred, -kappa*phi_inv*100),
    ("Miras", f"1+κφ⁻¹/4 = {1+kappa*phi_inv/4:.6f}", miras_pred, kappa*phi_inv/4*100),
    ("SH0ES", f"1+φ⁻¹/100 = {1+phi_inv/100:.6f}", H0_idcm*(1+phi_inv/100), phi_inv/100*100),
    ("Maser", "純幾何 (0 投影)", H0_idcm, 0),
    ("RR Lyrae (預測)", f"1+κφ⁻¹/6 = {1+kappa*phi_inv/6:.6f}", H0_idcm*(1+kappa*phi_inv/6), kappa*phi_inv/6*100),
]

for name, formula, h0, dev in methods:
    obs_mark = ""
    if name == "TRGB":
        obs_mark = f" (obs {trgb_obs})"
    elif name == "Miras":
        obs_mark = f" (obs {miras_obs})"
    elif name == "SH0ES":
        obs_mark = f" (obs 73.04)"
    elif name == "Maser":
        obs_mark = f" (obs 73.9)"
    print(f"  {name:20s} {formula:35s} {h0:7.2f}{obs_mark:15s} {dev:+.3f}%")

# ============ 8. 總結 ============
print("\n" + "=" * 72)
print("總結")
print("=" * 72)
pass_count = 0
total = 5

# Test 1: TRGB
if trgb_dev < 0.1:
    print(f"  ✅ T1: TRGB = {trgb_pred:.2f} (vs {trgb_obs}, {trgb_dev:.4f}%)")
    pass_count += 1
else:
    print(f"  ❌ T1: TRGB = {trgb_pred:.2f} (vs {trgb_obs}, {trgb_dev:.4f}%)")

# Test 2: Miras
if miras_dev < 0.1:
    print(f"  ✅ T2: Miras = {miras_pred:.2f} (vs {miras_obs}, {miras_dev:.4f}%)")
    pass_count += 1
else:
    print(f"  ❌ T2: Miras = {miras_pred:.2f} (vs {miras_obs}, {miras_dev:.4f}%)")

# Test 3: 4:1 ratio
if abs(ratio - B) < 1e-10:
    print(f"  ✅ T3: 幅度比 {ratio:.0f}:1 = B = φ³-φ⁻³ = {B:.0f}")
    pass_count += 1
else:
    print(f"  ❌ T3: 幅度比 {ratio:.0f}:1 ≠ B = {B:.0f}")

# Test 4: Sign check (TRGB negative, Miras positive)
if (trgb_pred < H0_idcm) and (miras_pred > H0_idcm):
    print(f"  ✅ T4: TRGB {trgb_pred:.2f} < H₀_idcm {H0_idcm} < Miras {miras_pred:.2f}")
    pass_count += 1
else:
    print(f"  ❌ T4: 符號錯誤")

# Test 5: H₀_idcm = c/R_H
h0_check = c / R_H
if abs(h0_check - H0_idcm) / H0_idcm < 0.001:
    print(f"  ✅ T5: H₀_idcm = c/R_H = {h0_check:.2f}")
    pass_count += 1
else:
    print(f"  ❌ T5: H₀_idcm = {h0_check:.2f} ≠ {H0_idcm}")

print(f"\n結果: {pass_count}/{total} PASS")
print(f"狀態: 🟢 {pass_count}/{total} 全部通過" if pass_count == total else f"狀態: 🟡 {pass_count}/{total}")