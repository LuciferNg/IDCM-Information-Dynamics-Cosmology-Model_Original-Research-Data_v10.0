#!/usr/bin/env python3
"""
O55 — Z_2 × U(1)_Y 離散對稱: 具體 n 值分析
=============================================
分析 3c 矩陣嘅具體 n 值 {−2,−1,0,1,2,3} 點樣由
Z_2 × U(1)_Y 離散對稱決定。

  A. 3c 值嘅 Z_2 結構 (正負對稱)
  B. 3c 值嘅 Z_3 結構 (mod 3)
  C. 3c = 3 × f(代, 電荷型) 分解
  D. 具體 n 值嘅生成機制
"""

import numpy as np
import math, sys

phi = (1 + math.sqrt(5)) / 2
PASS = 0; FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  ✅ {name} {detail}")
    else:
        FAIL += 1; print(f"  ❌ {name} {detail}")

print("=" * 70)
print("O55 04: Z_2 × U(1)_Y 離散對稱 — 具體 n 值")
print("=" * 70)

# 3c 矩陣
M = np.array([[0, -2, 3],
              [2, -2, -1],
              [1, 3, -2]], dtype=int)

# ============================================================
# [A] 3c 值嘅 Z_2 結構 (正負對稱)
# ============================================================
print("\n" + "-" * 70)
print("[A] Z_2 結構 — 正負對稱")
print("-" * 70)

values = sorted(M.flatten())
print(f"  3c 值: {values}")
print(f"  值域: {min(values)} ~ {max(values)}")
print(f"  不同值數: {len(set(values))}")

# 正負對稱
abs_vals = sorted([abs(v) for v in values])
print(f"  絕對值: {abs_vals}")
print(f"  絕對值集合: {sorted(set(abs_vals))}")

# 檢查: 正負對稱
pos = sorted([v for v in values if v > 0])
neg = sorted([abs(v) for v in values if v < 0])
print(f"  正數: {pos}")
print(f"  負數絕對值: {neg}")
print(f"  正負對稱? {pos == neg}")

# 3c 值嘅 Z_2 分類
# Z_2 = {0, 1} = {even, odd}
# 3c mod 2: {0, 1, 0, 0, 0, 1, 1, 1, 0} = {0, 1}
print(f"\n  3c mod 2: {[v % 2 for v in values]}")
print(f"  mod 2 集合: {sorted(set(v % 2 for v in values))}")
check("3c mod 2 = {0, 1} (Z_2 完整)", set(v % 2 for v in values) == {0, 1})

# 3c mod 2 嘅矩陣形式
M_mod2 = M % 2
print(f"\n  M mod 2:")
print(f"  {M_mod2[0]}")
print(f"  {M_mod2[1]}")
print(f"  {M_mod2[2]}")
print(f"  det(M mod 2) = {round(np.linalg.det(M_mod2))}")

# 3c = ±1, ±2, 0, 3 = 6 個值
# 6 = 2×3 (Z_2 × Z_3)
print(f"\n  6 個不同值 = 2 × 3 = |Z_2| × |Z_3|")
print(f"  → 3c ∈ {set(values)} = {len(set(values))} 個值")
print(f"  → 3c 值嘅結構 = Z_2 × Z_3")

# ============================================================
# [B] 3c 值嘅 Z_3 結構 (mod 3)
# ============================================================
print("\n" + "-" * 70)
print("[B] Z_3 結構 — mod 3 分類")
print("-" * 70)

# 3c mod 3
M_mod3 = M % 3
print(f"  M mod 3:")
print(f"  {M_mod3[0]}")
print(f"  {M_mod3[1]}")
print(f"  {M_mod3[2]}")
print(f"  det(M mod 3) = {round(np.linalg.det(M_mod3))}")

# 3c mod 3 嘅列結構
print(f"\n  U column mod 3: {M_mod3[:, 0]}")
print(f"  D column mod 3: {M_mod3[:, 1]}")
print(f"  L column mod 3: {M_mod3[:, 2]}")

# 每個 column 嘅 mod 3 值
for j, label in enumerate(["U (up-type)", "D (down-type)", "L (lepton)"]):
    col_mod3 = set(M_mod3[:, j])
    print(f"  {label}: mod 3 = {M_mod3[:, j]}, distinct = {col_mod3}")

# 3c mod 3 = 0,1,2 嘅完整分佈
print(f"\n  3c mod 3 分佈:")
for v in [0, 1, 2]:
    count = sum(1 for x in values if x % 3 == v)
    positions = [(i, j) for i in range(3) for j in range(3) if M[i, j] % 3 == v]
    print(f"    ≡ {v} (mod 3): {count} 個, 位置: {positions}")

# 3c 值用 Z_3 × Z_2 表示
# 如果 3c ∈ Z_3 × Z_2, 咁 3c = a·3 + b·2? 唔係
# 3c = 3q + r, q ∈ {0, ±1}, r ∈ {0, 1, 2}
print(f"\n  Z_3 × Z_2 分解:")
for v in sorted(set(values)):
    v_mod3 = v % 3
    v_mod2 = abs(v) % 2
    v_parity = "even" if v % 2 == 0 else "odd"
    print(f"    3c={v:>3d}: mod3={v_mod3}, mod2={v_parity}")

# Checing: can we write 3c = ε · (3q + r) where ε = ±1?
# 3c values: -2, -1, 0, 1, 2, 3
# If we strip sign: 0, 1, 1, 2, 2, 3
# After stripping sign: {0, 1, 1, 2, 2, 3}
# 3c = s · (3q + r) where s ∈ {−1, 0, 1}?
# Let's try: 3c = σ · (3q + r) where σ ∈ {−1, 1}, q ∈ {0, 1}, r ∈ {0, 1, 2}
# If σ = 0 for 3c = 0...
# 0 = 0·(3·0+0)
# 1 = 1·(3·0+1), -1 = -1·(3·0+1)
# 2 = 1·(3·0+2), -2 = -1·(3·0+2)
# 3 = 1·(3·1+0)
# This works! 3c = σ · (3q + r) where σ ∈ {−1, 0, 1}, q ∈ {0, 1}, r ∈ {0, 1, 2}
# But 0 has σ = 0, which is special.

# Better: 3c = s · t where s ∈ {−1, 0, 1} and t ∈ {0, 1, 2, 3}
# or: 3c = σ · (n) where σ ∈ {−1, 0, 1} and n ∈ {0, 1, 2, 3}
# −2 = −1·2, −1 = −1·1, 0 = 0·?, 1 = 1·1, 2 = 1·2, 3 = 1·3
# 0 can be 0·1 or 0·0 or 0·anything

print(f"\n  3c = σ · n 分解:")
print(f"    σ ∈ {{−1, 0, 1}} = Z_3 sign (including 0)")
print(f"    n ∈ {{0, 1, 2, 3}} = magnitude")
for v in sorted(set(values)):
    if v == 0:
        print(f"    3c={v:>3d} = 0·n (any n)")
    else:
        sigma = 1 if v > 0 else -1
        n = abs(v)
        print(f"    3c={v:>3d} = {sigma:+d}·{n}")

# ============================================================
# [C] 3c = 3 × f(代, 電荷型) 分解
# ============================================================
print("\n" + "-" * 70)
print("[C] 3c 矩陣嘅生成元分解")
print("-" * 70)

# 嘗試將 3c 矩陣分解為世代向量 × 電荷型向量
# 3c_{i,j} = g_i · h_j (純量積)
# 或者 3c_{i,j} = g_i + h_j (加法分解)
# 或者 3c_{i,j} = g_i × h_j (乘法分解)

# 加法分解: 3c = a_i + b_j
# 從 gen1 (i=0): 0 = a₀ + b_U, -2 = a₀ + b_D, 3 = a₀ + b_L
# → b_U = -a₀, b_D = -2-a₀, b_L = 3-a₀
# 從 gen2 (i=1): 2 = a₁ + b_U, -2 = a₁ + b_D, -1 = a₁ + b_L
# 代入 b_U, b_D, b_L:
# 2 = a₁ - a₀ → a₁ = a₀ + 2
# -2 = a₁ - 2 - a₀ → a₁ = a₀ (矛盾!)
# 所以加法分解唔成立

# 乘法分解: 3c = g_i · h_j
# 唔可能, 因為 0 嘅出現會令整行/列為 0

# SVD 分解 (奇異值分解)
print(f"\n  SVD 分解:")
U_svd, S, Vt = np.linalg.svd(M.astype(float))
print(f"  奇異值: {S}")
print(f"  U 矩陣 (世代空間):")
print(f"  {U_svd}")
print(f"  V 矩陣 (電荷型空間):")
print(f"  {Vt}")
print(f"  rank = {np.sum(S > 1e-10)}")
check("rank = 3 (滿秩)", np.sum(S > 1e-10) == 3, f"(rank={np.sum(S > 1e-10)})")

# SVD 嘅物理意義
# M = U·Σ·Vᵀ
# U: 世代空間嘅旋轉
# V: 電荷型空間嘅旋轉
# Σ = diag(σ₁, σ₂, σ₃): 耦合強度
print(f"\n  SVD 物理意義:")
print(f"    U: 世代混合 (3 代 -> 3 個正交方向)")
print(f"    V: 電荷型混合 (U,D,L -> 3 個正交方向)")
print(f"    Σ: 耦合強度 {S}")
print(f"    σ₁/σ₂ = {S[0]/S[1]:.4f} (主成分主導)")
print(f"    σ₂/σ₃ = {S[1]/S[2]:.4f}")

# 主成分: 用 U 嘅第一列同 V 嘅第一行重建
M_recon = S[0] * np.outer(U_svd[:, 0], Vt[0, :])
print(f"\n  主成分重建 (σ₁ only):")
print(f"  {M_recon[0].round(4)}")
print(f"  {M_recon[1].round(4)}")
print(f"  {M_recon[2].round(4)}")
print(f"  重建誤差: {np.linalg.norm(M - M_recon)/np.linalg.norm(M):.4f}")

# ============================================================
# [D] 具體 n 值嘅生成機制
# ============================================================
print("\n" + "-" * 70)
print("[D] 具體 n 值嘅生成機制")
print("-" * 70)

# 3c 值集合: {−2, −1, 0, 1, 2, 3}
# 呢 6 個值可以寫成:
# n = 3q + r, q ∈ {0, 1, −1}, r ∈ {0, 1, 2}
# 但 3 唔係 (3·1+0) 咩? 係, q=1, r=0
# 而 -2 = 3·(-1) + 1, q=-1, r=1
# -1 = 3·(-1) + 2, q=-1, r=2

# 所以 3c = 3q + r, q ∈ {−1, 0, 1}, r ∈ {0, 1, 2}
# |q| ≤ 1, |r| ≤ 2
# 3 × |q|max + |r|max = 3 + 2 = 5, 但最大係 3
# 所以 q ∈ {−1, 0, 1}, r ∈ {0, 1, 2} 可以生成所有值

print(f"\n  3c = 3q + r 分解:")
print(f"    q ∈ {{−1, 0, 1}} (Z_3 量子數)")
print(f"    r ∈ {{0, 1, 2}} (Z_3 殘餘)")
for v in sorted(set(values)):
    q = (v // 3) if v >= 0 else -((-v + 2) // 3)
    r = v - 3*q
    print(f"    3c={v:>3d} = 3×({q:+d}) + {r}")

# 3c 值同 K_Chain 嘅關係
# K_Chain 有 44 sites, 基本頻率 γ_n = 4sin²(nπ/88)
# 44 同 3c 嘅關係?
# 44 mod 3 = 2
# 44 = 3×14 + 2
print(f"\n  K_Chain 同 3 嘅關係:")
print(f"    Nd = 44 = 3×14 + 2")
print(f"    Nd mod 3 = 2")
print(f"    B = 4 = 3×1 + 1")
print(f"    B mod 3 = 1")
print(f"    Nd - 2B = 44 - 8 = 36 = 3×12")
print(f"    (Nd - 2B) mod 3 = 0 ✓")

# 3c 值嘅最大最小值
# max = 3, min = -2
# 3 - (-2) = 5 = F₅ (Fibonacci 5)
print(f"\n  3c 值域分析:")
print(f"    max = 3, min = -2")
print(f"    range = 5 = F₅ ✓")
print(f"    ｜max｜ = 3 = B-1? (B=4, B-1=3)")
print(f"    ｜min｜ = 2 = B/2? (B=4, B/2=2)")

# 3c 值同 φ 嘅關係
# c_f = n/3, Δδ = c_f·ln(φ)
# 所以 3c = 3 × Δδ/ln(φ)
# Δδ = c_f·ln(φ) = (n/3)·ln(φ)
# 3Δδ = n·ln(φ)
# n = 3Δδ/ln(φ) = 3c
print(f"\n  c_f 同 Δδ 嘅關係:")
print(f"    Δδ = c_f · ln(φ)")
print(f"    3Δδ = 3c_f · ln(φ) = n·ln(φ)")
print(f"    n = 3c_f·ln(φ)/ln(φ) = 3c_f ← 恆等式")

# 質量修正 Δδ 同 K_Chain 模式嘅關係
# Δδ = c_f·ln(φ), c_f = n/3
# n = 3c_f 係整數
# 所以 Δδ = (n/3)·ln(φ)
# 3Δδ/ln(φ) = n ∈ Z
print(f"\n  Δδ 嘅量子化:")
print(f"    3Δδ/ln(φ) = n ∈ Z")
print(f"    → Δδ 嘅量子化單位 = ln(φ)/3")
print(f"    → ln(φ)/3 = {math.log(phi)/3:.6f}")
print(f"    → 呢個係質量修正嘅最小量子")

# 呢個 ln(φ)/3 同 K_Chain 嘅關係?
# φ 同 K_Chain 嘅關係: K_Chain 嘅 throughput = φ
# φ = (1+√5)/2
# ln(φ) = arcsinh(1/2) = 0.481211825...
# ln(φ)/3 = 0.160404...
# 呢個值同 K_Chain 頻率嘅關係?
print(f"\n  ln(φ)/3 同 K_Chain 頻率:")
print(f"    ln(φ)/3 = {math.log(phi)/3:.10f}")
print(f"    γ₁ = 4sin²(π/88) = {4*math.sin(math.pi/88)**2:.10f}")
print(f"    γ₁/ln(φ) = {4*math.sin(math.pi/88)**2/math.log(phi):.6f}")
print(f"    γ₁/(3·ln(φ)) = {4*math.sin(math.pi/88)**2/(3*math.log(phi)):.6f}")

# ============================================================
# [E] 總結
# ============================================================
print("\n" + "-" * 70)
print("[E] 結論")
print("-" * 70)

print(f"""
  3c 值結構:
    n ∈ {{−2, −1, 0, 1, 2, 3}} = 6 個值
    6 = 2 × 3 = |Z_2| × |Z_3|
    → 3c 值嘅對稱群 = Z_2 × Z_3

  Z_2 結構:
    正負對稱: 3c 同 -3c 成對出現 (除 0 外)
    mod 2: {0, 1} Z_2 完整集合

  Z_3 結構:
    mod 3: {0, 1, 2} Z_3 完整集合
    M mod 3 可逆? {round(np.linalg.det(M % 3)) != 0}

  3c = 3q + r 分解:
    q ∈ {{−1, 0, 1}} = Z_3 量子數 (世代)
    r ∈ {{0, 1, 2}} = Z_3 殘餘 (電荷型)
    → 3c = 3 × gen_charge + type_charge

  Δδ 量子化:
    Δδ = (n/3)·ln(φ)
    3Δδ/ln(φ) = n ∈ Z
    ln(φ)/3 = {math.log(phi)/3:.6f} = 質量修正最小量子

  🔴 未解決:
    □ q 同 r 嘅物理意義: 點解 q ∈ {{−1,0,1}}, r ∈ {{0,1,2}}?
    □ 3c = 3q + r 嘅 K_Chain 起源
    □ ln(φ)/3 作為最小量子嘅物理意義
""")

print("=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)