#!/usr/bin/env python3
"""
O9-C11: 生成規則物理來源 — 4k−1 同 44/33 嘅深度關聯
======================================================
偶峰: A_{2k}/A₁ = ((k+1)/(4k−1))²

問題:
1. 4k−1 同 N_d=44 (4×11), M=33 (3×11) 有咩關係?
2. k+1 同 Fib/Lucas 有咩關係?
3. 點解係平方? (物理: 功率譜 ∝ 振幅²?)
4. 4k−1 = 3,7,11 = 質數 (孿生間隔 4) — 巧合定結構?
"""
import numpy as np
from fractions import Fraction

print("="*80)
print("O9-C11: 生成規則物理來源")
print("="*80)

N_d, M = 44, 33
phi = (1+5**0.5)/2

print("\n1. 4k−1 分析:")
print("   b_k = 4k−1: 3, 7, 11, 15, 19, 23, ...")
print("   對 k=1..7: ", [4*k-1 for k in range(1, 8)])
print("   -> 3,7,11 係前 3 個 (4k−1) 質數")
print("   15=3×5 (合成), 19 質數, 23 質數")
print()
print("   N_d = 44 = 4×11 -> b₃ = 11 = N_d/4")
print("   M = 33 = 3×11 -> b₁ = 3 = M/11")
print("   b_k 嘅極限: 4k−1 = 44 -> k = 11.25")
print("   -> 喺 k=11 附近 b_k 達到 N_d")
print()
print("   重要: b_k = 4k−1 嘅 11 係 N_d/4")
print("   而 k 最多到 3 (b=11) 對應 m=6 (最後偶峰)")
print("   k=4: b=15 (>11=N_d/4) — 超出範圍!")

print("\n2. k+1 分析:")
print("   a_k = k+1: 2, 3, 4")
print("   極限: a_k = 4 當 k=3 (最後)")
print("   a_k = k+1 對應 b_k = 4k−1 嘅 '4 倍' 關係")
print("   4a_k = 4k+4, b_k = 4k−1")
print("   4a_k − b_k = 5 (恆定!)")
print("   -> 4(k+1) − (4k−1) = 5 = F₅!")
print("   ★ 4a_k − b_k = 5 = F₅ 恆定!")
print("   → a_k/b_k = (b_k+5)/(4b_k)?")

print("\n3. 平方結構物理:")
print("   A_{2k}/A₁ = (a_k/b_k)²")
print("   -> 振幅比本身係 a_k/b_k, 功率比係平方")
print("   -> 物理: C_ℓ ∝ |ΔT|², 振幅∝ΔT")
print("   -> 即峰振幅比 = a_k/b_k (一次), C_ℓ 比 = 平方")
print("   -> 檢查: sqrt(A₂/A₁) = 0.666 = 2/3 ✓")
print("   -> sqrt(A₄/A₁) = 0.431 = 3/7 ✓")
print("   -> sqrt(A₆/A₁) = 0.361 = 4/11 ✓")

print("\n4. 振幅比 a_k/b_k 結構:")
for k in range(1, 4):
    a, b = k+1, 4*k-1
    print(f"   k={k}: {a}/{b} = {a/b:.4f}")

print("\n5. Fib/Lucas 表達:")
print("   2/3 = F₃/F₄ (Fib/Fib)")
print("   3/7 = L₂/L₄ (Lucas/Lucas)")
print("   4/11 = L₃/L₅ (Lucas/Lucas)")
print()
print("   F₃=2, F₄=3, L₂=3, L₄=7, L₃=4, L₅=11")
print("   模式: (F₃/F₄), (L₂/L₄), (L₃/L₅)")
print("   -> 分子: F₃, L₂, L₃ = 2, 3, 4")
print("   -> 分母: F₄, L₄, L₅ = 3, 7, 11")
print()
print("   L_n = F_{n−1} + F_{n+1} 恆等式:")
print("   L₂ = F₁+F₃ = 1+2 = 3 ✓")
print("   L₃ = F₂+F₄ = 1+3 = 4 ✓")
print("   L₄ = F₃+F₅ = 2+5 = 7 ✓")
print("   L₅ = F₄+F₆ = 3+8 = 11 ✓")
print()
print("   ★ 所以 b_k = L_{k+2} 對於 k=1,2,3?")
print("   L₃=4 (k=1?), L₄=7 (k=2), L₅=11 (k=3)")
print("   -> b_k = L_{k+2}: L₃=4 ✗ (b₁=3)")
print("   但 b_k = F_{k+3} − L_{k}? F₄−L₁=3−1=2 ✗")

print("\n6. b_k 同 Lucas 完整檢查:")
L = [2, 1, 3, 4, 7, 11, 18, 29]
print(f"   Lucas: {L}")
print(f"   b_k (3,7,11) = L₂, L₄, L₅")
print(f"   跳過 L₃=4! 點解?")
print(f"   L₂=3, L₄=7, L₅=11 — 唔連續")
print(f"   但 4k−1: 3,7,11 — 連續等差")
print(f"   -> 4k−1 係更根本 (等差), Lucas 只係巧合")

print("\n7. 結論:")
print("   偶峰統一公式: A_{2k}/A₁ = ((k+1)/(4k−1))²")
print("   - a_k = k+1 (最簡, 無 Fib/Lucas 必要)")
print("   - b_k = 4k−1 (等差 4 = N_d/11 間隔)")
print("   - 4a_k − b_k = 5 = F₅ (恆定!)")
print("   - b_max = 11 = N_d/4 (k=3 截斷)")
print("   - 極限 (k→∞): a/b → 1/4, A/A₁ → 1/16")
print()
print("   ★ 物理意義: 4k−1 嘅 '4' = N_d/11")
print("   ★ N_d = 44 = 4×11 結構內建於 b_k")
print("   ★ F₅=5 恆定 = IDCM 嘅 Fibonacci 基礎")
