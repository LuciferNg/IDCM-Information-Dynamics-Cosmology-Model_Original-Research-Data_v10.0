#!/usr/bin/env python3
"""
O137 Phase 2c: v₂(n) 子環規則驗證
=====================================
假設: 費米子量子化 L = Nd/2^{v₂(n)} = 44/2^{v₂(n)}

  v₂(n) = 0 (odd)      → L = 44 = Nd
  v₂(n) = 1 (2 mod 4)  → L = 22 = Nd/2
  v₂(n) = 2 (4 mod 8)  → L = 11 = Nd/4 = L₅
  v₂(n) ≥ 3 (8 | n)    → L = 5.5, 2.75, ... 非整數 → 冇子環可繞 → 純玻色子

預測: 純玻色子 = {n : v₂(n) ≥ 3} = {8, 16, 24, 32, 40}
     費米子候選 = {1, 7, 20, 14, 33, 34} 全部 v₂ ≤ 2
"""
import numpy as np

def v2(n):
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k

N = 44
print("=" * 72)
print("O137 Phase 2c: v₂(n) 子環規則")
print("=" * 72)

print(f"\n[1] 所有模式嘅 v₂(n) 同 L 類:")
print(f"    {'n':>3} | {'v₂':>3} | {'L=Nd/2^v₂':>10} | 類別")
cand = {1: 'e⁻', 7: 'μ⁻', 20: 'τ⁻', 14: 's', 33: 'b', 34: 'c'}
boson_pure = []
for n in range(1, N+1):
    k = v2(n)
    L = 44 // (2**k)
    is_L_int = (44 % (2**k) == 0)
    tag = cand.get(n, '')
    if not is_L_int:
        boson_pure.append(n)
        cls = "純玻色子"
    else:
        cls = f"費米子 L={L}"
        if tag:
            cls += " ★"
    print(f"    {n:>3} | {k:>3} | {L if is_L_int else '—':>10} | {cls} {tag}")

print(f"\n[2] 純玻色子 (v₂ ≥ 3): {boson_pure}")
print(f"    預測: n ≡ 0 (mod 8) = {[n for n in range(1, 45) if n % 8 == 0]}")
print(f"    匹配: {boson_pure == [n for n in range(1, 45) if n % 8 == 0]}")

print(f"\n[3] 候選模式 v₂ 分析:")
for n, name in sorted(cand.items(), key=lambda x: x[1]):
    k = v2(n)
    L = 44 // (2**k)
    print(f"    {name} (n={n:2d}): v₂={k} → L={L}")

print(f"\n[4] 唯一性檢查:")
print(f"    v₂=0 (L=44): {[n for n in range(1,45) if v2(n)==0]}")
print(f"    v₂=1 (L=22): {[n for n in range(1,45) if v2(n)==1]}")
print(f"    v₂=2 (L=11): {[n for n in range(1,45) if v2(n)==2]}")
print(f"    v₂≥3 (純玻色子): {boson_pure}")

# [5] 統計: 六候選中 v₂≤2 嘅比例
print(f"\n[5] 統計: 六候選全部 v₂ ≤ 2: {all(v2(n) <= 2 for n in cand)}")
print(f"    44 模式中 v₂ ≤ 2 嘅比例: {sum(1 for n in range(1,45) if v2(n)<=2)}/44")
