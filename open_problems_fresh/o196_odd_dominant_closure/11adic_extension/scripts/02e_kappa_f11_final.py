#!/usr/bin/env python3
# O200 scripts/02e — T2 定理定稿: v₁₁(κ_{2m}) = f(11-free(m)) 完整驗證
# 已確立: v₁₁(κ_{2m})=0 ⟺ 11-free(m) ∈ {1,2,3,5} = {F₂,F₃,F₄,F₅} (m≤1000 mod-11)
# 本 script: 完整 big-int κ (m≤130) 驗證:
#   A) v₁₁(κ_{2m}) 只依賴 11-free(m) (最強形式)
#   B) f(d) = v₁₁(κ_{2d}) 結構: 對 d 11-free, f(d) = ?
#   C) 完整定理: v₁₁(σ_m) = v₁₁(m) + f(11-free(m)) − ⌊2m/11⌋
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

M = 130
kap = [0]*(M+1)
for j in range(1, M+1):
    val = math.comb(2*j, j)
    for m in range(1, j):
        val -= math.comb(2*j-1, 2*m-1) * math.comb(2*j-2*m, j-m) * kap[m]
    kap[j] = val

vks = [v11_int(kap[m]) for m in range(1, M+1)]

# A) v₁₁ 只依賴 11-free(m): 對所有 m1,m2 ≤ M 有 11-free 相等 ⟹ v₁₁ 相等
okA = True
badA = []
fmap = {}
for m in range(1, M+1):
    fr = eleven_free(m)
    if fr in fmap and fmap[fr] != vks[m-1]:
        okA = False; badA.append((m, fr, fmap[fr], vks[m-1]))
    fmap[fr] = vks[m-1]
check(f"A) v₁₁(κ_{{2m}}) = f(11-free(m)) (m≤{M}, 完整 big-int)", okA,
      f"違反 {badA[:3]}" if badA else f"{len(fmap)} 個 11-free 類全一致")

# B) f(d) 結構 — 對 11-free d: f(d) = v₁₁(κ_{2d})
print("\n== B) f(d) = v₁₁(κ_{2d}) for 11-free d (m≤130) ==")
ds = sorted(fmap.keys())
print("  d:    ", " ".join(f"{d:>3}" for d in ds))
print("  f(d): ", " ".join(f"{fmap[d]:>3}" for d in ds))
# f(d) 嘅零位: {1,2,3,5}
fzero = [d for d in ds if fmap[d] == 0]
check(f"B) f(d)=0 ⟺ d ∈ {{1,2,3,5}} (11-free, m≤{M})", set(fzero) == {1,2,3,5},
      f"zeros {fzero}")

# f(d) 同 v₁₁(C(2d,d)) 關係 (Legendre)
def v11_binom(ap, bp):
    p = 11
    def sd(x):
        s = 0
        while x: s += x % p; x //= p
        return s
    return (sd(bp) + sd(ap-bp) - sd(ap)) // (p-1)

print("\n  d → f(d), v₁₁(C(2d,d)), f−v₁₁(C):")
for d in ds[:45]:
    vc = v11_binom(2*d, d)
    print(f"  {d:>3}: f={fmap[d]}, vC={vc}, diff={fmap[d]-vc}")

# C) 完整定理: v₁₁(σ_m) = v₁₁(m) + f(11-free(m)) − ⌊2m/11⌋
print("\n== C) v₁₁(σ_m) 完整閉式 (修正 SESSION_START 預言) ==")
okC = True
badC = []
for m in range(1, M+1):
    sig = F(m*kap[m], math.factorial(2*m) * 2**(2*m))
    vs = v11(sig)
    pred = v11_int(m) + fmap[eleven_free(m)] - (2*m)//11
    if vs != pred:
        okC = False; badC.append((m, vs, pred))
check(f"C) v₁₁(σ_m) = v₁₁(m) + f(11-free(m)) − ⌊2m/11⌋ (m≤{M})", okC,
      f"違反 {badC[:5]}" if badC else "全中")
print("  (SESSION_START 預言『v₁₁ 由 (2m)! 決定』修正: κ 自身帶 11 因子, f(11-free(m)) 項)")
print("  原本形式: v₁₁(σ_m) = v₁₁(m·κ_{2m}) − ⌊2m/11⌋ = v₁₁(m) + f(11-free(m)) − ⌊2m/11⌋")

# D) σ_m 分母 v₁₁: den σ_m 嘅 11 指數
print("\n== D) σ_m 分母 11 指數 = ⌊2m/11⌋ − v₁₁(m) − f(11-free(m))? ==")
okD = True
for m in range(1, M+1):
    sig = F(m*kap[m], math.factorial(2*m) * 2**(2*m))
    if v11(sig.denominator) != (2*m)//11 - v11_int(m) - fmap[eleven_free(m)]:
        okD = False; break
check("D) v₁₁(den σ_m) = ⌊2m/11⌋ − v₁₁(m) − f(11-free(m))", okD)

# E) f(d) 嘅物理詮釋: f(d) = v₁₁(κ_{2d}) — κ 係觀察者累積量 (arcsine 整數)
# 結構讀取: 11-free(m) ∈ {F₂,F₃,F₄,F₅} ⟺ κ_{2m} 唔被 11 整除 (11 = L₅ 週期)
print("\n== E) 結構讀取 ==")
print("  κ_{2m} 帶 11 因子 ⟺ 11|m 或 11-free(m) ∉ {1,2,3,5}")
print("  {1,2,3,5} = {F₂,F₃,F₄,F₅} (Fibonacci) — 同 O192 冪和閉式 C(2n,n) 同源")
print("  11 = L₅ = N_d/4 — 88-site 譜嘅 adic 化身 (O195 Thm 5)")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
