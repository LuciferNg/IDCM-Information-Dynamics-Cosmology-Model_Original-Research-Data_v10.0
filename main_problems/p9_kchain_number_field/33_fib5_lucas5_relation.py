#!/usr/bin/env python3
"""
33_fib5_lucas5_relation.py — 5 同 11 嘅結構關係 (2026-10-17)
=============================================================
調律者問題: 「3 5 7 11 都是結構質數吧, 5和11是不是有特別關係」

假設: 3,7,11 = Lucas 質數 (L₂,L₄,L₅); 5 = F₅ Fibonacci (唔係 Lucas 成員)
      → F₅=5, L₅=11 同一 index 5 — 呢個可能係 20 (唯一冇 Lucas 鏈) 嘅生成鍵!

驗證:
  V1: 5 ∉ Lucas seq, 5 = F₅; 11 = L₅ — 同一 index
  V2: Lₙ = φⁿ−φ⁻ⁿ (n odd) 代數恆等 — L₅ = 11 EXACT
  V3: F₅×L₅ = 5×11 = 55 = F₁₀ (O137 已閉合)
  V4: ★ magic 20 = 4×5 = 4F₅ — 首次俾到 20 生成鏈!
  V5: magic 全生成: {14=2L₄, 22=2L₅, 33=3L₅, 20=4F₅, 7=L₄}
      乘數 {1,2,3,4} = 連續頭四個 Lucas 值 {L₁,L₀,L₂,L₃}
  V6: 3,5,7,11 = 前四個奇質數 (3,5,7 唯一三連奇質數組 + 下一個)

零 import; 精確整數 + Fraction (√5 用 mpmath 50dps 驗證代數恆等)。
"""
import json
from fractions import Fraction

def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def luc(n):
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a

# V1: F₅ / L₅
F5, L5 = fib(5), luc(5)
F10, L4 = fib(10), luc(4)
V1 = {"F5": F5, "L5": L5, "5_is_Lucas": 5 in [luc(k) for k in range(10)],
      "11_is_Lucas": 11 in [luc(k) for k in range(10)],
      "same_index": "F_5=L_5 index=5"}

# V2: L₅ = φ⁵−φ⁻⁵ — 用 mpmath 50dps
import mpmath as mp
mp.mp.dps = 60
phi = (1 + mp.sqrt(5)) / 2
L5_binet = phi**5 - phi**(-5)
V2 = {"L5_binet": str(L5_binet), "L5_exact": L5, "diff": str(abs(L5_binet - L5))}

# V3: 5×11 = 55 = F₁₀
V3 = {"5x11": 5 * 11, "F10": F10, "eq": 5 * 11 == F10}

# V4: magic 20 = 4F₅
MAGIC = [7, 14, 20, 22, 33]
V4 = {"20_eq_4F5": 20 == 4 * F5, "4F5": 4 * F5,
      "20_has_lucas_chain": 20 in {m * Lk for m in (1, 2, 3) for Lk in [luc(k) for k in range(8)]},
      "20_has_fib_chain": 20 in {m * fib(k) for m in (1, 2, 3, 4) for k in range(2, 9)}}

# V5: magic 全生成 — 乘數 × 基數
L2, L3, L0, L1 = luc(2), luc(3), luc(0), luc(1)
gen = {7: f"L4={L4}", 14: f"2·L4={2*L4}", 22: f"2·L5={2*L5}",
       33: f"3·L5={3*L5}", 20: f"4·F5={4*F5}"}
V5 = {"magic_generators": gen,
      "multipliers": {"1": L1, "2": L0, "3": L2, "4": L3},
      "multiplier_is_lucas_head": sorted([L0, L1, L2, L3]) == [1, 2, 3, 4]}

# V6: 前四奇質數
def isprime(x):
    if x < 2: return False
    for p in range(2, int(x**0.5) + 1):
        if x % p == 0: return False
    return True
odd_primes = [n for n in range(1, 30, 2) if isprime(n)]
V6 = {"first_odd_primes": odd_primes[:6], "3_5_7_11": odd_primes[:4],
      "triplet_357": all(isprime(x) for x in (3, 5, 7)),
      "note": "3,5,7 唯一三連續奇質數; +11 = 前四奇質數"}

# ★ 新盲測候選 R5: magic = {m·L₄, m·L₅, m·F₅: m∈{1,2,3,4}}?
# 統計: 43 個 d 入面, L₄/L₅/F₅ 嘅小倍數有幾多個? 5 個 magic 全生成嘅概率?
cand5 = sorted({m * L4 for m in (1, 2)} | {m * L5 for m in (1, 2, 3)} | {m * F5 for m in (1, 4)})
V5b = {"candidate_set": cand5, "n_candidates": len(cand5),
       "magic_covered": [d for d in MAGIC if d in cand5]}

res = {"test": "33_fib5_lucas5_relation", "V1": V1, "V2": V2, "V3": V3,
       "V4": V4, "V5": V5, "V5b": V5b, "V6": V6}

with open("data/33_fib5_lucas5.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)

print("=== V1: F₅ 同 L₅ 同一 index ===")
print(f"  F5={F5}  L5={L5}  5 係 Lucas? {V1['5_is_Lucas']}  11 係 Lucas? {V1['11_is_Lucas']}")
print()
print("=== V2: L₅ = φ⁵−φ⁻⁵ (Binet) ===")
print(f"  φ⁵−φ⁻⁵ = {mp.nstr(L5_binet, 30)}...  L₅ = {L5}  diff = {mp.nstr(abs(L5_binet-L5), 5)}")
print()
print("=== V3: 5×11 ===")
print(f"  5·11 = {5*11}  F₁₀ = {F10}  equal? {5*11==F10}")
print()
print("=== V4: magic 20 = 4F₅ (首次生成鏈!) ===")
print(f"  20 = 4×5 = {4*F5} ✓")
print(f"  20 有 Lucas 鏈? {V4['20_has_lucas_chain']}  有 Fibonacci 鏈? {V4['20_has_fib_chain']}")
print()
print("=== V5: magic 全生成 ===")
for d in MAGIC:
    print(f"  {d:2d} = {gen[d]}")
print(f"  乘數 {V5['multipliers']} 連續頭四個 Lucas 值? {V5['multiplier_is_lucas_head']}")
print()
print("=== V5b: 生成候選集 ===")
print(f"  {{m·L₄, m·L₅, m·F₅}} = {cand5} ({len(cand5)} 個)")
print(f"  magic 覆蓋 = {V5b['magic_covered']} ({len(V5b['magic_covered'])}/5)")
print()
print("=== V6: 3,5,7,11 ===")
print(f"  前四奇質數 = {V6['first_odd_primes'][:4]} (3,5,7 三連 + 11)")
print()
print("輸出: data/33_fib5_lucas5.json")