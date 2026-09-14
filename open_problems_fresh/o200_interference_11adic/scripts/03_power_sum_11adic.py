#!/usr/bin/env python3
# O200 scripts/03 — T3: v₁₁(Σγ^n) 冪和閉式 11-adic 側 (SESSION_START §二 項 4)
# O192 冪和閉式: Σγ^n = 88·C(2n,n) + 2^{2n−1} (總), 奇 44·C(2n,n), 偶 44·C(2n,n)+2^{2n−1}
# 11-adic 預言:
#   v₁₁(88·C(2n,n)) = 1 + v₁₁(C(2n,n)) ≥ 1; v₁₁(2^{2n−1}) = 0 (11∤2)
#   ⟹ v₁₁(Σγ^n) = min(1+v₁₁(C), 0) = 0 ∀n  (估值唔等 ⟹ 冇相消)
#   v₁₁(Σγ^n_odd) = 1 + v₁₁(C(2n,n))  (44 = 4·11 提供一個 11)
#   v₁₁(Σγ^n_even) = 0               (2^{2n−1} 項保護)
# 交叉線索 (SESSION_START): Σ(1+δ̂)^n = 2^{−n}Σγ^n (O197 Π(1+δ̂)=88/2^86 同源)
import math
from fractions import Fraction as F

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

def v11(x):
    n = abs(x.numerator); d = x.denominator
    e = 0
    while n % 11 == 0: n //= 11; e += 1
    while d % 11 == 0: d //= 11; e -= 1
    return e

def v11_int(k):
    e = 0
    while k % 11 == 0: k //= 11; e += 1
    return e

def legendre_11(n):
    """v₁₁(C(2n,n)) = (s₁₁(n)·2 − s₁₁(2n))/10 = 進位數"""
    def sd(x):
        s = 0
        while x: s += x % 11; x //= 11
        return s
    return (sd(n) + sd(n) - sd(2*n)) // 10

N = 40
print("== T3a: Σγ^n 直接計算 vs 閉式 v₁₁ 預言 ==")
print(f"  {'n':>3} {'v₁₁(Σγ^n)':>10} {'預言 0':>8} {'v₁₁(odd)':>9} {'1+v₁₁(C)':>9} {'v₁₁(even)':>10} {'預言 0':>8}")
ok1 = ok2 = ok3 = True
for n in range(1, N+1):
    # 直接譜計算 (γ_k = 4sin²(kπ/176)) 太慢 — 用閉式 (O192 已證) + Fraction 驗證
    # Σγ^n 閉式: 88·C(2n,n) + 2^{2n−1} — 直接整數計算
    S_tot = 88 * math.comb(2*n, n) + 2**(2*n-1)
    S_odd = 44 * math.comb(2*n, n)
    S_even = 44 * math.comb(2*n, n) + 2**(2*n-1)
    vt = v11_int(S_tot); vo = v11_int(S_odd); ve = v11_int(S_even)
    pC = legendre_11(n)
    if vt != 0: ok1 = False
    if vo != 1 + pC: ok2 = False
    if ve != 0: ok3 = False
    if n <= 8 or n in (11, 12, 22, 33):
        print(f"  {n:>3} {vt:>10} {'0':>8} {vo:>9} {1+pC:>9} {ve:>10} {'0':>8}")
check(f"T3a v₁₁(Σγ^n) = 0 ∀n≤{N} (2^{{2n−1}} 項保護, 估值唔等冇相消)", ok1)
check(f"T3a v₁₁(Σγ^n_odd) = 1 + v₁₁(C(2n,n)) ∀n≤{N} (44 = 4·11)", ok2)
check(f"T3a v₁₁(Σγ^n_even) = 0 ∀n≤{N}", ok3)

# T3b: v₁₁(C(2n,n)) 週期性 (Legendre 進位計數)
print("\n== T3b: v₁₁(C(2n,n)) 結構 (Legendre 進位) ==")
print(f"  n=1..30: {[legendre_11(n) for n in range(1, 31)]}")
# 11 進位進位位: 2n 喺 base-11 進位 ⟺ C(2n,n) 帶 11
carry = [n for n in range(1, N+1) if legendre_11(n) > 0]
print(f"  C(2n,n) 帶 11 因子嘅 n (≤{N}): {carry}")
# 週期: 進位位 = 2n 喺 base 11 有進位 — n 嘅 base-11 表示
print("  base-11 進位規則: 2n 喺 base-11 進位 ⟺ n 嘅 base-11 某位 ≥ 6 (11/2)")
# 驗證: n ∈ [6,10] (base-11: 6..A), [17,21], [28,32], [39,43]...
pred_carry = [n for n in range(1, N+1) if any(((n // 11**k) % 11) >= 6 for k in range(0, 3))]
check(f"T3b v₁₁(C(2n,n)) > 0 ⟺ n 有 base-11 位 ≥ 6 (進位規則, n≤{N})", set(carry) == set(pred_carry),
      f"進位位 {carry}")

# T3c: Σ(1+δ̂)^n = 2^{−n}Σγ^n (O197 交叉線索) — v₁₁ 兩邊
print("\n== T3c: Σ(1+δ̂)^n = 2^{−n}Σγ^n (O197 交叉) — v₁₁(Σ(1+δ̂)^n) = ? ==")
# 1+δ̂_k = γ_k/2 (O197) ⟹ Σ(1+δ̂)^n = 2^{−n}Σγ^n
# v₁₁(Σ(1+δ̂)^n) = v₁₁(Σγ^n) − v₁₁(2^n) = 0 − 0 = 0 (2 冇 11)
for n in [1, 2, 3, 5, 11, 22]:
    S = 88 * math.comb(2*n, n) + 2**(2*n-1)
    Sd = F(S, 2**n)   # Σ(1+δ̂)^n
    print(f"  n={n}: Σ(1+δ̂)^n = {Sd}, v₁₁ = {v11(Sd)} (預言 0)")
check("T3c v₁₁(Σ(1+δ̂)^n) = 0 (2^{−n} 縮放唔影響 11-adic)", 
      all(v11(F(88*math.comb(2*n,n) + 2**(2*n-1), 2**n)) == 0 for n in range(1, N+1)))

# T3d: Π(1+δ̂) = 88/2^86 (O197) — n→0 極限, v₁₁ = 1 − 0 = 1
# v₁₁(88/2^86) = v₁₁(88) − v₁₁(2^86) = 1 − 0 = 1 (88 = 8·11)
pi_val = F(88, 2**86)
print(f"\n  Π(1+δ̂) = 88/2^86, v₁₁ = {v11(pi_val)} (預言 1: 88 = 8·11)")
check("T3d v₁₁(Π(1+δ̂)) = 1 (n→0 極限, 88 = 8·11)", v11(pi_val) == 1)

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
