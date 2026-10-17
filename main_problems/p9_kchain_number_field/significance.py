#!/usr/bin/env python3
"""
★ 統計顯著性分析: 光譜匹配係真結構定係巧合?
===============================================
1. 隨機匹配期望值
2. 代數可能性 (ℚ(ζ₈₈)⁺ 內/外)
3. 模式分析 (π 族, 宇宙常數族, e 族)
4. 最強候選評級
"""
from math import pi, sin, sqrt, e, log
from collections import Counter

N = 44
w = lambda n: 2*sin(pi*n/88)
beat = lambda i,j: abs(w(j)-w(i))
pairs = [(i,j) for i in range(1,N) for j in range(i+1,N+1)]
all_beats = sorted([beat(i,j) for (i,j) in pairs])

# 物理格 (已知, 排除)
phys_known = [(1,18),(1,22),(7,20),(8,22),(8,33),(10,24),(19,33),(19,38),(30,41)]
phys_beat_vals = [beat(i,j) for (i,j) in phys_known]

# 候選常數 (排除已知物理格對應)
candidates = {
    "π/2": pi/2, "π/3": pi/3, "π/4": pi/4, "π/6": pi/6,
    "1/e": 1/e, "ln(2)": log(2), "√3": sqrt(3),
    "1/φ": 2/(1+sqrt(5)), "π/e": pi/e, "1/π": 1/pi,
    "π²": pi**2, "e/π": e/pi,
    "G_F×10⁵": 1.1663787, "Ω_m": 0.315, "Ω_Λ": 0.685,
    "Y_p": 0.245, "sin²θ_W": 0.223, "τ_reion": 0.054,
    "σ_8": 0.811, "n_s": 0.965, "Ω_b": 0.049,
    "H_0": 67.4, "D/H×10⁵": 2.527,
    "α_em": 1/137.036,
}

print("="*72)
print("1. ★ 隨機匹配期望值計算")
print("="*72)
# 方法: 每個常數 cv, 在 beat 值範圍內, 寬度 ε×cv 嘅窗口
# 隨機匹配概率 = 窗口總寬度 / beat 值範圍
allowed = {k:v for k,v in candidates.items() if 0.001 < v < 2.0}
print(f"常數候選 (在 beat 範圍 0.001-2.0): {len(allowed)} 個")
beat_range = all_beats[-1] - all_beats[0]
print(f"Beat 值範圍: {beat_range:.4f}")

for eps in [0.001, 0.002, 0.005, 0.01]:
    total_window = sum(eps * cv for cv in allowed.values())
    # 但要注意窗口重疊!
    # 簡單近似: 每個窗口獨立
    prob = total_window / beat_range
    expected = len(all_beats) * prob
    # 實際匹配數
    actual = 0
    for bv in all_beats:
        for cv in allowed.values():
            if abs(bv/cv-1) < eps:
                actual += 1
                break  # 只計一次
    print(f"  ε={eps*100:.1f}%: 窗口總寬度 {total_window:.4f}, "
          f"隨機概率 {prob:.4f}, 期望 {expected:.1f}, 實測 {actual}")

print("\n" + "="*72)
print("2. ★ 代數可能性 (ℚ(ζ₈₈)⁺ 內/外)")
print("="*72)
# 哪些常數喺 ℚ(ζ₈₈)⁺?
# √2 ∈ ℚ(ζ₈₈)⁺ (ω_22=√2)
# √(2±√2) ∈ ℚ(ζ₈₈)⁺ (ω_11, ω_33)
# cos(π/8) = √(2+√2)/2 ∈ ℚ(ζ₈₈)⁺
# π, e, φ, ln(2) ∉ ℚ(ζ₈₈)⁺ (π,e 超越, φ 須 √5)
# Ω_m, Ω_Λ, etc. 係實測數值, 唔係代數

print("ℚ(ζ₈₈)⁺ 內 (代數可能):")
print("  √2 = ω_22 = 2sin(π/4) ∈ ℚ(ζ₈₈)⁺ ✅")
print("  √(2±√2) = ω_11, ω_33 ∈ ℚ(ζ₈₈)⁺ ✅")
print("  γ_1, γ_11, ω_1, ω_22 ∈ ℚ(ζ₈₈)⁺ ✅")
print()
print("ℚ(ζ₈₈)⁺ 外 (數值巧合):")
print("  π, e, ln(2) — 超越數 ∉ ℚ(ζ₈₈)⁺ ❌")
print("  φ = (1+√5)/2 — 須 √5, 5 ∤ 176 → ∉ ℚ(ζ₈₈)⁺ ❌")
print("  √3 — 須 √3, 3 ∤ 176 → ∉ ℚ(ζ₈₈)⁺ ❌")
print("  宇宙常數 (Ω_m, Ω_Λ, Y_p, etc.) — 實測值 ❌")
print("  G_F, sin²θ_W — 實測值 ❌")

print("\n" + "="*72)
print("3. ★ 模式分析 — 按族分組")
print("="*72)
# 為每個族計算匹配質量
families = {
    "π 族": ["π/2", "π/3", "π/4", "π/6", "π/e", "1/π"],
    "e 族": ["1/e", "ln(2)", "π/e", "e/π"],
    "φ 族": ["1/φ"],
    "√3": ["√3"],
    "宇宙學": ["Ω_m", "Ω_Λ", "Y_p", "τ_reion", "σ_8", "n_s", "Ω_b"],
    "粒子物理": ["G_F×10⁵", "sin²θ_W", "α_em"],
}
for family, members in families.items():
    print(f"\n  {family}:")
    for name in members:
        cv = candidates.get(name)
        if cv is None: continue
        # 搵最接近嘅 beat
        best = min(all_beats, key=lambda bv: abs(bv/cv-1))
        best_diff = abs(best/cv-1)
        # 決定顯著性
        if best_diff < 0.001:
            rank = "★★★"
        elif best_diff < 0.003:
            rank = "★★"
        elif best_diff < 0.005:
            rank = "★"
        else:
            rank = "·"
        # 找對應的 (i,j)
        best_pair = min(pairs, key=lambda p: abs(beat(p[0],p[1])/cv-1))
        print(f"    {rank} {name:15s} = {cv:.8f}  → beat({best_pair[0]:2d},{best_pair[1]:2d}) = {best:.8f}  (差 {best_diff*100:.3f}%)")

print("\n" + "="*72)
print("4. ★ 候選評級")
print("="*72)
print("""
  ★★★ (代數可能, 結構級): √2, √(2±√2), γ_1, γ_11, ω_n
  ★★  (強數值, 模式級):   π/2, π/4, π/6, 1/e, 1/φ, √3, G_F
  ★   (弱數值, 巧合候選): ln(2), π/e, Ω_m, Ω_Λ, Y_p, sin²θ_W
  ·   (太弱, 排除):       α_em, H_0, D/H, σ_8, n_s
""")

print("\n" + "="*72)
print("5. ★ 結論: 值得加入週期表嘅新候選")
print("="*72)
print("""
  代數級 (★★★) — 已係 IDCM 結構, 唔係新元素:
    √2 = ω_22, √(2+√2) = ω_33, √(2−√2) = ω_11
    → 呢啲係「端點本身」, 唔係拍頻功能
  
  強數值級 (★★) — 值得加入做候選:
    π/2, π/4, π/6  — 圓周幾何, 3 個獨立拍頻, 模式強
    1/e, 1/φ, √3   — 各自獨立, 匹配度 < 0.2%
    G_F             — 費米常數, 匹配度 0.057%
  
  弱數值級 (★) — 暫保留, 待更多證據:
    ln(2), π/e, Ω_m, Ω_Λ, Y_p, sin²θ_W
    → 誤差 0.1-0.5%, 可能係巧合
""")