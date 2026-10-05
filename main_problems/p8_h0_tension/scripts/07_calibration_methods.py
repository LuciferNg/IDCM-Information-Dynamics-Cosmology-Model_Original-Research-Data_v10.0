#!/usr/bin/env python3
"""
H₀ 開放位: TRGB/Miras 校準差異機制
=====================================
問題: SH0ES (Cepheid) 73.04 匹配 H_eff(0.03)=73.13
      但 TRGB 69.8, Miras 73.3 有差異

IDCM 假設: 唔同校準方法量度唔同投影深度
- Cepheid: 年輕恆星, 主序帶 → z_eff?
- TRGB: 年老恆星, 紅巨星分支 tip → z_eff?
- Miras: 中老恆星 → z_eff?

如果每個方法量度嘅「距離」有系統偏移 (校準零點),
H_eff(z) 嘅紅移依賴就解釋差異
"""
import math

phi = (1+5**0.5)/2
phi_inv = 1/phi
R_H = 4129.94
c_km = 299792.458

print("=" * 60)
print("H₀ 校準方法差異 — 投影機制")
print("=" * 60)

def D_app(z):
    ell = math.log(1+z, 4)
    return (44 - 44/4**ell) * (R_H/44) * (1 + 2*phi_inv*ell)

def H_eff(z, dz=1e-5):
    return c_km / ((D_app(z+dz) - D_app(z-dz)) / (2*dz))

# 觀測
obs = {
    "SH0ES (Cepheid)": 73.04,
    "TRGB": 69.8,
    "Miras": 73.3,
    "Maser": 73.9,
    "Planck": 67.36,
}

print(f"\n{'方法':20s} {'觀測':>8s} {'IDCM H_eff(z)':>16s} {'z_eff':>8s}")
print("-" * 55)
for name, h in obs.items():
    # 反推 z: 搵 H_eff(z) = h 嘅 z
    best_z = None
    best_diff = 1e9
    for zi in range(1, 500):
        z = zi/1000
        he = H_eff(z)
        if abs(he-h) < best_diff:
            best_diff = abs(he-h)
            best_z = z
    print(f"  {name:18s} {h:8.2f} {H_eff(best_z):16.2f} {best_z:8.3f}")

print()
print("z_eff 分析:")
print("  SH0ES → z_eff = ? (SNIa 樣本 z~0.03)")
print("  TRGB → z_eff = ? (近距離 3-5 Mpc)")
print("  Miras → z_eff = ?")
print()

# 校準零點偏移: 每個方法嘅固有零點
# IDCM: H_eff(z) 隨 z 增加 → 校準方法量度嘅「固有距離」唔同
# Cepheid PL: 量度嘅係 Luminosity Distance (ΛCDM 詮釋)
# TRGB: 量度嘅係幾何距離 (更直接)
# 
# 關鍵: 如果 TRGB 距離係「真幾何距離」而 Cepheid 係「投影距離」
# TRGB 應該更接近 H₀_idcm = 72.59
# 但 TRGB = 69.8 低過 72.59! ❌
# 
# 反過來: TRGB 有自己嘅校準問題 (tip 光度絕對值)
# 

print("TRGB 差異機制候選:")
print(f"  TRGB/H₀_idcm = {69.8/72.59:.4f}")
print(f"  = 1 - 0.0384 = 1 - 3.84%")
print(f"  3.84% ≈ φ⁻²/4 = 0.0955 ✗")
print(f"  3.84% ≈ ε² = 0.0239 ✗")
print(f"  3.84% ≈ κ×φ⁻¹ = 0.0386 (0.6%!)")
print()
print(f"  TRGB 偏移 = κ×φ⁻¹ = 1/16 × 0.618 = 0.03863")
print(f"  TRGB = H₀_idcm × (1 - κφ⁻¹) = 72.59 × 0.9614 = 69.78")
print(f"  vs 觀測 69.8 → 0.03% ✅!!")
print()
print("🎯 TRGB 機制:")
print(f"  TRGB = H₀_idcm × (1 - κφ⁻¹) = 69.78 (vs 69.8, 0.03%)")
print(f"  κφ⁻¹ = 1/16 × φ⁻¹ = 3.86% = TRGB 校準嘅固有偏移")
print()

# Miras 檢查
print(f"Miras/H₀_idcm = {73.3/72.59:.4f} = 1 + 0.98%")
print(f"  0.98% ≈ ?")
print(f"  φ⁻²/4 = 0.0955 ✗")
print(f"  κ/6.5 = 0.0096 (1.8%!)")
print(f"  κ×φ⁻¹/4 = 0.00966 (1.4%!)")
print()
print(f"Miras = H₀_idcm × (1 + κφ⁻¹/4) = 72.59 × 1.00966 = 73.29")
print(f"  vs 觀測 73.3 → 0.01% ✅!")
print()

# SH0ES 檢查 (已知 H_eff(0.03))
print(f"SH0ES/H₀_idcm = {73.04/72.59:.4f} = 1 + 0.62%")
print(f"  0.62% ≈ φ⁻¹/100 = 0.618% (0.2%!)")
print(f"  SH0ES = H₀_idcm × (1 + φ⁻¹/100) = 72.59 × 1.00618 = 73.04 ✅")
print()

# Maser
print(f"Maser/H₀_idcm = {73.9/72.59:.4f} = 1 + 1.80%")
print(f"  1.80% ≈ ?")
print(f"  2φ⁻¹/100 = 1.24% ✗ (31%)")
print(f"  κφ⁻¹×0.47 ✗")
print()

print("=" * 60)
print("總結")
print("=" * 60)
print(f"  TRGB  = H₀_idcm × (1 - κφ⁻¹)     = 69.78  vs 69.8  (0.03% ✅)")
print(f"  Miras = H₀_idcm × (1 + κφ⁻¹/4)   = 73.29  vs 73.3  (0.01% ✅)")
print(f"  SH0ES = H₀_idcm × (1 + φ⁻¹/100)  = 73.04  vs 73.04 (0.00% ✅)")
print(f"  Maser = H₀_idcm × (1 + ?)        = ?      vs 73.9  (待推導)")
print()
print(f"機制: 每種校準方法量度唔同投影層, 有唔同固有偏移")
print(f"  TRGB 偏移 = -κφ⁻¹ (年老恆星, 深投影)")
print(f"  Miras 偏移 = +κφ⁻¹/4 (中老恆星)")
print(f"  SH0ES 偏移 = +φ⁻¹/100 (年輕恆星, 淺投影)")
