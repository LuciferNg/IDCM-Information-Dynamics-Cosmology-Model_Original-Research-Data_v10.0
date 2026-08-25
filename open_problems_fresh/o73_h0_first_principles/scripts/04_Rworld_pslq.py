"""
O73 攻堅 04: H2 深搜 — R_world = 4129.94 有冇結構分解?
=================================================================
用戶指示: 新參數唔可以再叫哈伯常數 → 身份 = 世界環角頻率 ω_ring。
但 ω_ring = c/R_world 仍然係「輸入」— R_world 有冇第一性原理?

目標: 搵 R_world = 4129.94 Mpc 嘅結構分解:
  1. 整數關係掃描: R_world ≈ 結構數 × 因子 (44, 88, 90, 178, φ 冪)
  2. φ 冪分解: R_world = A·φ^B? (A 整數/半整數)
  3. 週期/頻率空間: T_ring = 84.63 Gyr 有冇結構?
  4. 天文交叉: R_world 對應咩已知宇宙尺度?
"""
import numpy as np
from itertools import product

phi = (1 + np.sqrt(5)) / 2
R_world = 4129.94  # Mpc
c = 299792.458     # km/s

print("=" * 74)
print("1. 基礎結構數除法 (搵整數/半整數商)")
print("=" * 74)
struct_nums = {
    "44 (N_d)": 44, "88 (2N_d)": 88, "90 (Σγ_even)": 90,
    "178 (2F₁₁)": 178, "264 (3Σγ_odd)": 264, "61.5 (ρ_Λ)": 61.5,
    "123 (L₁₀)": 123, "36 (h11)": 36, "98 (h12)": 98,
    "33 (K_tree)": 33, "22 (N_d/2)": 22, "56 (阻挫)": 56,
    "32 (2B²)": 32, "11 (rank)": 11, "121 (11²)": 121,
}
print(f"  R_world = {R_world} Mpc")
for name, n in struct_nums.items():
    q = R_world / n
    flag = ""
    if abs(q - round(q)) < 1e-6:
        flag = " ★ 整數!"
    elif abs(q - round(q*2)/2) < 1e-6:
        flag = " ☆ 半整數"
    print(f"  {name:16s}: {q:12.6f}{flag}")

print()
print("=" * 74)
print("2. φ 冪分解: R_world = A·φ^B?")
print("=" * 74)
print("  檢查 B = -40..40, A 是否整數/半整數/簡單分數:")
hits = []
for B in range(-40, 41):
    A = R_world / phi**B
    if abs(A - round(A)) < 1e-5:
        hits.append((B, A, f"A={round(A)} 整數"))
    elif abs(A - round(A*2)/2) < 1e-5:
        hits.append((B, A, f"A={round(A*2)/2} 半整數"))
if hits:
    for B, A, desc in hits:
        print(f"  B={B:+3d}: A = {A:.6f} ({desc}) → R = {A}·φ^{B}")
else:
    print("  ❌ 冇 B ∈ [-40,40] 令 A 係整數/半整數")

# 更寬鬆: A 係細整數比 (m/n, m,n ≤ 50)
print()
print("  寬鬆掃描: A = m/n (m,n ≤ 50), 容差 1e-4:")
best = []
for B in range(-30, 31):
    A = R_world / phi**B
    for m in range(1, 51):
        n = round(A * m)
        if n < 1 or n > 50:
            continue
        if abs(A - n/m) / A < 1e-4:
            best.append((abs(A - n/m)/A, B, m, n, A))
best.sort()
for dev, B, m, n, A in best[:8]:
    print(f"  B={B:+3d}: A ≈ {m}/{n} = {m/n:.6f} (真 {A:.6f}, dev {dev*100:.4f}%)")

print()
print("=" * 74)
print("3. 週期空間: T_ring = 84.63 Gyr 有冇結構?")
print("=" * 74)
T_ring = 2 * np.pi * R_world * 3.085677581e19 / c / 3.15576e16
print(f"  T_ring = {T_ring:.4f} Gyr")
# 84.63 嘅分數近似
fracs = []
for q in range(1, 200):
    p = round(T_ring * q)
    if abs(T_ring - p/q) / T_ring < 1e-3:
        fracs.append((abs(T_ring - p/q)/T_ring, p, q))
fracs.sort()
for dev, p, q in fracs[:6]:
    print(f"  T_ring ≈ {p}/{q} = {p/q:.4f} Gyr (dev {dev*100:.3f}%)")
print(f"  T_ring/2π = {T_ring/(2*np.pi):.4f} Gyr = R_world/c (半徑光行時間)")

# 44-tone 週期結構: T_ring/44, T_ring/88
print(f"  T_ring/44 = {T_ring/44:.4f} Gyr (44 節點同步)")
print(f"  T_ring/88 = {T_ring/88:.4f} Gyr (88 對偶)")
print(f"  1.9235 × 44 = {1.9235*44:.2f} Gyr")

print()
print("=" * 74)
print("4. 天文交叉: R_world = 4129.94 Mpc 對應咩?")
print("=" * 74)
print("""
  宇宙微波背景最後散射面 (Planck): ~13800 Mpc (紅移 1089)
  可觀測宇宙粒子視界 (ΛCDM):        ~14000 Mpc
  R_world = 4129.94 Mpc = 0.295 × 粒子視界 ≈ 1/3.4
  類星體最遠: ~4.2 Gpc (J0313-1806, z=7.64)
  JWST 最遠星系: z~13-14 → 共動距離 ~ 3300-3600 Mpc

  R_world = 4129.94 Mpc ≈ 13.47 Gly (光行時間)
  → 光行時間 = R_world/c = 13.47 Gyr
  → 但 T_ring = 84.63 Gyr = 完整環周期 (2πR_world/c)

  ★ R_world/c = 13.47 Gyr 接近宇宙年齡 13.8 Gyr:
    13.47/13.8 = 0.976 偏差 2.4%
    → 但 IDCM 冇大爆炸, 冇宇宙年齡 — 呢個係 ΛCDM 概念!
    → 唔可以混埋 (PARADIGM BREAK: 冇膨脹, 冇年齡)
""")

print("=" * 74)
print("結論 (H2 預掃)")
print("=" * 74)
print("""
  🔴 冇任何整數/半整數/φ 冪分解:
     - 44, 88, 90, 178, 264, 61.5, 123... 全部無理數商
     - φ^B (B ∈ [-40,40]) 冇整數/半整數 A
     - 最接近: 需要 m/n ≤ 50 先有 1e-4 命中 (太多自由度)
  🟢 有意義嘅重詮釋:
     - R_world 係「半徑」唔係「周長」→ λ_sync = 2πR/88 = 294.88 解開
     - ω_ring = c/R_world = 世界環角頻率 (身份修正)
     - T_ring = 84.63 Gyr = 世界環周期 (冇熱寂, O39)
  🔴 H2 判決: R_world = 4129.94 冇結構分解 → 係幾何輸入
     → 新參數 ω_ring 嘅「數值」仍然係輸入 (身份已修正)
     → 「零參數」claim: 最少 1 個 (ω_ring 數值)
""")
