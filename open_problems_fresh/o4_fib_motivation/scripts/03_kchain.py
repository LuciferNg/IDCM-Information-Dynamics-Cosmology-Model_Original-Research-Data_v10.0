#!/usr/bin/env python3
"""
03_kchain.py — K_Chain 譜組合 vs Fibonacci 等級
================================================
O4 機制 3: 節點振幅等級 F₃/F₄/F₅ 係咪由 K_Chain 譜 γ_n 組合決定?

候選連接:
- γ₇ = 4sin²(7π/88) ≈ 0.0786 → 能量單位
- F₇ = 13 (Ω_DM/Ω_b = 13/2 已閉合)
- γ_n 嘅 sqrt (振幅 ∝ sin(πn/88))

物理: 節點振幅 = K_Chain 模式 n 嘅投影幅度?
- 冷斑 (d=0) = 主模式 n=44 (SYNC, ℓ=44)
- 高階模式疊加: F_m 係咪對應 γ_n 嘅代數組合?
"""
import numpy as np
import math

phi = (1 + 5**0.5) / 2
eps = (1/phi) / 4
RMS = eps**5 / 8
T_cmb = 2.72548

F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
L = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76]  # Lucas

print("=" * 72)
print("O4 03: K_Chain 譜 γ_n 組合 vs Fibonacci")
print("=" * 72)

# ---------- 1. K_Chain 模式 ----------
Nd = 44
gamma = {n: 4*math.sin(math.pi*n/88)**2 for n in range(1, Nd+1)}
amp = {n: 2*abs(math.sin(math.pi*n/88)) for n in range(1, Nd+1)}

print(f"\n=== K_Chain 關鍵模式 ===")
print(f"{'n':>3} {'γ_n':>10} {'γ_n/γ₁':>9} {'A_n':>8} {'A_n/A₁':>8}")
for n in [1, 3, 5, 7, 11, 13, 22, 33, 44]:
    print(f"{n:>3} {gamma[n]:>10.6f} {gamma[n]/gamma[1]:>9.4f} {amp[n]:>8.4f} {amp[n]/amp[1]:>8.4f}")

# ---------- 2. γ_n 與 Fibonacci 嘅關係 ----------
print(f"\n=== γ_n ↔ Fibonacci 候選 ===")
print(f"{'n':>3} {'γ_n':>10} {'1/γ_n':>9} {'F_ratio':>8} {'Lucas':>7} {'匹配?':>6}")
for n in range(1, 23):
    inv = 1/gamma[n]
    # 邊個 Fibonacci 最接近 1/γ_n
    best_f = min(range(1, 10), key=lambda k: abs(inv - F[k]))
    best_l = min(range(0, 10), key=lambda k: abs(inv - L[k]))
    match = ""
    if abs(inv - F[best_f]) / inv < 0.05:
        match = f"≈F{best_f}"
    elif abs(inv - L[best_l]) / inv < 0.05:
        match = f"≈L{best_l}"
    print(f"{n:>3} {gamma[n]:>10.6f} {inv:>9.3f} {F[best_f]:>8} {L[best_l]:>7} {match:>6}")

# ---------- 3. 關鍵: γ 數值平方根 = sin 振幅 ----------
# A_n = 2sin(πn/88): A₇? A₁₁? A₁₃?
print(f"\n=== A_n = 2sin(πn/88) vs Fibonacci 數值 ===")
print(f"A₁ = {amp[1]:.4f}, A₃ = {amp[3]:.4f}, A₅ = {amp[5]:.4f}")
print(f"A₇ = {amp[7]:.4f}, A₁₁ = {amp[11]:.4f}, A₁₃ = {amp[13]:.4f}, A₂₂ = {amp[22]:.4f}")
print(f"A₄₄ = {amp[44]:.4f}")
print(f"\nA₁₁/A₇ = {amp[11]/amp[7]:.4f} (φ={phi:.4f})?")
print(f"A₂₂/A₁₁ = {amp[22]/amp[11]:.4f} (φ={phi:.4f})?")
print(f"A₁₃/A₇ = {amp[13]/amp[7]:.4f} (F₇/F₅={13/5:.4f})?")

# ---------- 4. 振幅等級 = γ_n 組合? ----------
# 冷斑 5ε⁵/8: 5 = F₅
# 若 A(d) ∝ Σ 某組 γ_n... 試: γ 嘅和 = ?
print(f"\n=== γ_n 代數組合 ===")
print(f"Σγ (n=1..44) = {sum(gamma.values()):.4f} (已知 90)")
print(f"γ₁+γ₃+γ₅ = {gamma[1]+gamma[3]+gamma[5]:.6f} (×1000={1000*(gamma[1]+gamma[3]+gamma[5]):.2f})")
print(f"γ₇+γ₄₄ = {gamma[7]+gamma[44]:.6f}")
print(f"γ₁/γ₄₄ = {gamma[1]/gamma[44]:.6f}")
print(f"1/γ₁ = {1/gamma[1]:.3f} (≈196 = 44×4.45?)")

# Z₂ 對偶: γ_n + γ_{44-n} = 4
print(f"\nZ₂ 對偶 γ_n + γ_{44-n} = 4:")
print(f"γ₇ + γ₃₇ = {gamma[7] + gamma[37]:.6f} (期望 4)")

# ---------- 5. 關鍵洞察: A(d) 衰減嘅 K_Chain 解釋 ----------
print(f"\n=== 振幅等級嘅 K_Chain 解釋 ===")
print(f"RMS = ε⁵/8 = {RMS:.6e} → 30 μK")
print(f"F₅ = 5×30 = 150 μK, F₄ = 3×30 = 90 μK, F₃ = 2×30 = 60 μK")
print(f"\n即: 等級 n 振幅 = F_n × 30 μK")
print("Fibonacci 遞迴: F_n = F_{n-1} + F_{n-2}")
print(f"→ 150 = 90 + 60: 冷斑 = 第一層 + 第二層 (疊加原理!)")
print(f"→ 90 = 60 + 30: F₄ = F₃ + F₂ (30 μK = 1×RMS = F₂ 級)")

# Fibonacci 疊加結構
print(f"\n=== 疊加結構 (最關鍵) ===")
print(f"F₅ = F₄ + F₃ = 3 + 2 (5 = 3 + 2)")
print(f"即: A(冷斑) = A(鄰居) + A(次鄰居)")
print(f"振幅 = 干涉疊加: 冷斑係 3 階 + 2 階干涉嘅和")

# ---------- 6. ε 截斷檢查 ----------
print(f"\n=== ε 截斷 (機制 5 前置檢查) ===")
print(f"ε = φ⁻¹/4 = {eps:.6f}")
print(f"ε⁰ = 1, ε¹ = {eps:.4f}, ε² = {eps**2:.5f}, ε³ = {eps**3:.6f}")
print(f"ε⁵/8 = RMS (已知)")
print(f"ε 截斷階: ε³ = {eps**3:.6f} ≈ 1/41.6 (3 代截斷)")
print(f"RMS = ε⁵/8: 5 個管道量化單元, /8 = 2³ 二分")

# 儲存
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o4_fib_motivation/data/kchain_spectrum.txt', 'w') as f:
    f.write("# O4 03: K_Chain 譜分析\n")
    f.write(f"# n gamma 1/gamma amplitude\n")
    for n in range(1, 44):
        f.write(f"{n} {gamma[n]:.6f} {1/gamma[n]:.4f} {amp[n]:.4f}\n")
    f.write(f"\n# 關鍵: Σγ={sum(gamma.values()):.2f}, A₁₁/A₇={amp[11]/amp[7]:.4f}\n")
print(f"\n✅ 已存: data/kchain_spectrum.txt")
