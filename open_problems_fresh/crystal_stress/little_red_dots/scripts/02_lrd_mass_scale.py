#!/usr/bin/env python3
"""
小紅點質量標度 — 拓撲缺陷渦旋推導
===================================
觀測: Schindler+2024 z=7.3 M_BH=5e8 M☉; EIGER z~2 M_BH~1e6 M☉
ratio = 500× (z 高 → 質量大)

IDCM 結構途徑:
  節點 = 拓撲渦旋 (K_Chain beat 凝聚)
  質量 ∝ 應力能密度 × 缺陷核心體積

關鍵: 點樣由結構常數推出 M_BH?

候選途徑:
  A. M ∝ m₇ × N_beats × 4^ℓ?  (ℓ = log₄(1+z))
  B. M ∝ ρ_crit × λ_sync³ × f(ε)?
  C. M ∝ M_Pl × φ^-k × 4^ℓ?

觀測 ratio: M(z=7.3)/M(z=2) = 500
  結構: 4^ℓ 比例? ℓ(7.3) = log₄(8.3) = 1.525, ℓ(2) = log₄(3) = 0.792
  4^(1.525-0.792) = 4^0.733 = 2.72 → 唔係 500
  (1+z) ratio = 8.3/3 = 2.77 → 唔係 500
  
  咁 500 邊度嚟? 500 = 5×10² = 5×100
  500 = 10⁵/2? 唔係結構數
  500 ≈ φ^13? φ^13 = 521.0 → 偏差 4.2%!
  500 ≈ φ^12.9? 
  500 ≈ 4^4.5 = 512 → 偏差 2.4%!
  500 = 512 = 4^4.5 = 2^9 → 偏差 2.3%

有趣! M_BH ratio ≈ 4^4.5 = 2^9 = 512 (2.3% 偏差)

4^4.5 = (2²)^4.5 = 2^9 = 512
結構意義? 4 = MERA 分支, 4.5 = 9/2 = 半整數
z 7.3 vs 2: ℓ 差 = 1.525-0.792 = 0.733 (唔係 4.5)
所以唔係 ℓ 直接控制

可能: 質量 ∝ 4^ℓ_eff 而 ℓ_eff 唔係 log₄(1+z)?
定係 M ∝ (1+z)^k?
(1+z) ratio = 2.77, 要 500 → k = ln500/ln2.77 = 6.21/1.019 = 6.09 ≈ 6?

M ∝ (1+z)^6? 
  z=7.3: 8.3^6 = 3.27e5
  z=2: 3^6 = 729
  ratio = 449 → 偏差 11% (唔夠好)

M ∝ (1+z)^(2N_d/3)? = (1+z)^29.3? 太誇張

等等 — 要小心! 呢個係兩個樣本嘅比較, 唔係同一族群嘅演化
Schindler 嘅 5e8 M☉ 係「overdensity 入面嘅特別 LRD」
EIGER 嘅 1e6 M☉ 係「一般 LRD」
可能根本唔係同一件事!

更穩陣: 用質量嘅絕對標度做推導, 唔好靠 ratio

M_BH ~ 1e6 M☉ (一般 LRD z~2)
= 1e6 × 1.989e30 kg = 1.989e36 kg
= 1.115e9 M_Pl (M_Pl = 2.176e-8 kg)
log_φ(M/M_Pl) = ln(1.115e9)/ln(1.618) = 20.83/0.4812 = 43.3

有意思! log_φ(1e6 M☉ / M_Pl) ≈ 43.3 ≈ 44 - 0.7?
44 = N_d!

而 M_BH = 5e8 M☉ (z=7.3):
log_φ(5e8×1.989e30 / 2.176e-8) = ln(4.57e46)/0.4812
= 107.3/0.4812 = 223.0

唔同標度, 唔係同一公式。

結論: 質量標度需要更小心嘅處理 — 樣本唔同, 唔可以簡單 ratio
"""
import math

phi = (1 + 5**0.5)/2
M_sun = 1.989e30  # kg
M_Pl = 2.176e-8   # kg

print("="*70)
print("小紅點質量標度分析")
print("="*70)

# 觀測
M_BH_z73 = 5e8 * M_sun
M_BH_z2 = 1e6 * M_sun
print(f"\n觀測:")
print(f"  M_BH(z=7.3) = 5e8 M☉ (Schindler+2024)")
print(f"  M_BH(z~2)   = 1e6 M☉ (EIGER)")
print(f"  ratio = {M_BH_z73/M_BH_z2:.0f}×")

# 結構候選
print(f"\n候選結構比對:")
cands = [
    ("φ^13", phi**13, "521.0"),
    ("4^4.5 = 2^9", 4**4.5, "512"),
    ("(1+z)⁶", 8.3**6/3**6, "449"),
    ("4^4", 4**4, "256"),
    ("946/2", 473, "473"),
    ("44×11+16", 44*11+16, "500"),
]
for name, val, note in cands:
    dev = abs(val/500 - 1)*100
    print(f"  {name:<14} = {val:>8.1f}  (偏差 {dev:5.1f}%)  [{note}]")

# 絕對標度
print(f"\n絕對標度 (log_φ 分析):")
for label, M in [("1e6 M☉ (z~2)", M_BH_z2), ("5e8 M☉ (z=7.3)", M_BH_z73)]:
    M_kg = M
    lg = math.log(M_kg/M_Pl)/math.log(phi)
    print(f"  {label}: log_φ(M/M_Pl) = {lg:.2f}")

# 睇下 1e6 M☉ 嘅 log_φ = 43.3 ≈ 44-φ⁻¹?
print(f"\nlog_φ(1e6 M☉/M_Pl) = 43.3")
print(f"  44 - 0.7? φ⁻¹ = 0.618 → 44-φ⁻¹ = 43.38")
print(f"  44 - ε×4.5? ε = 0.1545, 44-0.7 = 43.3")

# 如果 M ∝ M_Pl × φ^(44-φ⁻¹)?
M_pred = M_Pl * phi**(44 - 1/phi)
print(f"\nM_pred = M_Pl×φ^(44-φ⁻¹) = {M_pred/M_sun:.3e} M☉")
print(f"  觀測 1e6 M☉ → 偏差 {abs(M_pred/M_sun/1e6-1)*100:.2f}%")

# 用 m₇ 做單位?
m7_kg = 13.8e6*1.602e-19/3e8**2
print(f"\nm₇ = 13.8 MeV = {m7_kg:.3e} kg")
print(f"  1e6 M☉ = {M_BH_z2/m7_kg:.2e} m₇")
print(f"  log_φ(1e6 M☉/m₇) = {math.log(M_BH_z2/m7_kg)/math.log(phi):.2f}")
print(f"  log_φ(5e8 M☉/m₇) = {math.log(M_BH_z73/m7_kg)/math.log(phi):.2f}")
