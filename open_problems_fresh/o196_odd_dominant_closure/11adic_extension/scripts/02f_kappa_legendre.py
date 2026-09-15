#!/usr/bin/env python3
# O200 scripts/02f — T2 定稿: Legendre 完整和修正 + 定理三連
# 修正 C): v₁₁(σ_m) = v₁₁(m) + f(11-free(m)) − Σ_{k≥1} ⌊2m/11^k⌋
#          (v₁₁((2m)!) = Legendre 完整和, m≥61 時 2m≥121 多一個 11)
# 定理:
#   T2-1: v₁₁(κ_{2m}) = f(11-free(m)) 只依賴 11-free(m) (11-adic 自相似)
#   T2-2: f(d) = 0 ⟺ d ∈ {1,2,3,5} = {F₂,F₃,F₄,F₅}
#   T2-3: v₁₁(σ_m) = v₁₁(m) + f(11-free(m)) − v₁₁((2m)!)
import math
from fractions import Fraction as F

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

def v11_int(k):
    e = 0
    while k % 11 == 0: k //= 11; e += 1
    return e

def v11(x):
    n = abs(x.numerator); d = x.denominator
    e = 0
    while n % 11 == 0: n //= 11; e += 1
    while d % 11 == 0: d //= 11; e -= 1
    return e

def eleven_free(m):
    while m % 11 == 0: m //= 11
    return m

def legendre_11_fact(m):
    """v₁₁(m!) = Σ_{k≥1} ⌊m/11^k⌋"""
    s = 0; p = 11
    while p <= m:
        s += m // p; p *= 11
    return s

M = 130
kap = [0]*(M+1)
for j in range(1, M+1):
    val = math.comb(2*j, j)
    for m in range(1, j):
        val -= math.comb(2*j-1, 2*m-1) * math.comb(2*j-2*m, j-m) * kap[m]
    kap[j] = val

vks = [v11_int(kap[m]) for m in range(1, M+1)]
fmap = {}
for m in range(1, M+1):
    fmap[eleven_free(m)] = vks[m-1]

# T2-3 修正版: v₁₁(σ_m) = v₁₁(m) + v₁₁(κ_{2m}) − v₁₁((2m)!)
ok = True
bad = []
for m in range(1, M+1):
    sig = F(m*kap[m], math.factorial(2*m) * 2**(2*m))
    vs = v11(sig)
    pred = v11_int(m) + vks[m-1] - legendre_11_fact(2*m)
    if vs != pred:
        ok = False; bad.append((m, vs, pred))
check(f"T2-3 v₁₁(σ_m) = v₁₁(m) + v₁₁(κ₂ₘ) − v₁₁((2m)!) (Legendre 完整和, m≤{M})", ok,
      f"違反 {bad[:5]}" if bad else f"{M} 個全中")

# T2-1 再驗 (強形式): v₁₁(κ_{2m}) 只依賴 11-free(m)
ok1 = True
for m in range(1, M+1):
    if vks[m-1] != fmap[eleven_free(m)]:
        ok1 = False; break
check(f"T2-1 v₁₁(κ₂ₘ) = f(11-free(m)) (m≤{M})", ok1)

# T2-2: f(d)=0 ⟺ d ∈ {1,2,3,5}
fz = sorted(d for d in fmap if fmap[d] == 0)
check("T2-2 f(d)=0 ⟺ d ∈ {1,2,3,5} = {F₂,F₃,F₄,F₅}", fz == [1,2,3,5], f"{fz}")

# 結構註記: f(d) 同 v₁₁(C(2d,d)) 嘅關係
print("\n== f(d) vs v₁₁(C(2d,d)) 結構 (d 11-free ≤ 60) ==")
def v11_binom(ap, bp):
    p = 11
    def sd(x):
        s = 0
        while x: s += x % p; x //= p
        return s
    return (sd(bp) + sd(ap-bp) - sd(ap)) // (p-1)
print("  d:   " + " ".join(f"{d:>2}" for d in range(1, 61) if eleven_free(d) == d))
print("  f:   " + " ".join(f"{fmap[d]:>2}" for d in range(1, 61) if eleven_free(d) == d))
print("  vC:  " + " ".join(f"{v11_binom(2*d, d):>2}" for d in range(1, 61) if eleven_free(d) == d))
print("  diff:" + " ".join(f"{fmap[d]-v11_binom(2*d,d):>2}" for d in range(1, 61) if eleven_free(d) == d))

# 週期性檢查: f(d) 有冇 11-週期? (d 11-free 睇)
print("\n== f(d) 嘅區塊結構 (d 11-free) ==")
# 從序列睇: f 喺 d∈[6,10] = 2,1,1,1,1; [12,16] = 1,1,1,1,1; [17,21]=2,2,2,2,2; [23,27]=1,1,1,1,1; [28,32]=2,2,2,2,2
# 似係 v₁₁(C(2d,d)) + [d 喺某啲區間 +1]
# 直接檢查: f(d) = v₁₁(C(2d,d)) + δ(d), δ 係咪乾淨?
ds = [d for d in range(1, 61) if eleven_free(d) == d]
deltas = sorted(set(fmap[d] - v11_binom(2*d, d) for d in ds))
print(f"  f−vC 可能值: {deltas}")
# δ=2 嘅位: 45-54 (f=2,3 vs vC=0,1)
d2 = [d for d in ds if fmap[d] - v11_binom(2*d, d) == 2]
print(f"  δ=2 位: {d2}  (d 11-free ≤60)")
d1 = [d for d in ds if fmap[d] - v11_binom(2*d, d) == 1]
print(f"  δ=1 位 (頭 20): {d1[:20]}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
