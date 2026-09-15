#!/usr/bin/env python3
# O200 scripts/13 — 攻堅: f(d) = v₁₁(κ_{2d}) 完整閉式 (11-free d)
# 觀察 (scripts/02e/10): f(d) 喺每個長 5 區塊 [11q+1,11q+5] / [11q+6,11q+10] 內常數
#   f_low(q)  = f(11q+1..5)  : 0,1,1,1,2,1,3,? (q=0..6)
#   f_high(q) = f(11q+6..10) : 2,2,2,2,3,3,4
# 目標: f_low(q), f_high(q) 嘅閉式
# 線索: v₁₁(C(2d,d)) = 進位數 (Legendre); f = vC + δ, δ ∈ {0,1,2}
import math

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

def v11_int(k):
    e = 0
    while k % 11 == 0: k //= 11; e += 1
    return e

def eleven_free(m):
    while m % 11 == 0: m //= 11
    return m

M = 400
kap = [0]*(M+1)
for j in range(1, M+1):
    val = math.comb(2*j, j)
    for m in range(1, j):
        val -= math.comb(2*j-1, 2*m-1) * math.comb(2*j-2*m, j-m) * kap[m]
    kap[j] = val

# f(d) 區塊表
print("== f(d) 區塊 (q = d//11) ==")
print("  q:      ", " ".join(f"{q:>3}" for q in range(0, 15)))
flow, fhigh = [], []
for q in range(0, 15):
    lo = v11_int(kap[11*q+1])
    hi = v11_int(kap[11*q+6])
    flow.append(lo); fhigh.append(hi)
print("  f_low:  ", " ".join(f"{x:>3}" for x in flow))
print("  f_high: ", " ".join(f"{x:>3}" for x in fhigh))

# 假說: f_low(q) / f_high(q) 由 q+1 嘅 11-adic 決定? 定由 q 嘅 base-11 位和?
def s11(n):
    s = 0
    while n: s += n % 11; n //= 11
    return s

# v₁₁(C(2d,d)) = (2s₁₁(d) − s₁₁(2d))/10 = 進位數
def vC(d):
    return (2*s11(d) - s11(2*d)) // 10

print("\n  q  → f_low, vC(11q+1), f−vC:")
for q in range(0, 15):
    d = 11*q+1
    print(f"  {q:>2} → {flow[q]}, {vC(d)}, {flow[q]-vC(d)}")
print("\n  q  → f_high, vC(11q+6), f−vC:")
for q in range(0, 15):
    d = 11*q+6
    print(f"  {q:>2} → {fhigh[q]}, {vC(d)}, {fhigh[q]-vC(d)}")

# 假說: f_low(q) = v₁₁(κ_{2·(q+1)})?  (11 進位「除 11」對應?)
# κ_{2·11k} ≡ κ_{2k} (mod 11) (T2 收縮) — 但 v₁₁ 唔係
print("\n  f_low(q) vs v₁₁(κ_{2(q+1)}):")
for q in range(0, 10):
    print(f"  q={q}: f_low={flow[q]}, v₁₁(κ_{{2(q+1)}})={v11_int(kap[q+1])}")

# 假說: f_low(q) = v₁₁(C(2(11q+1), 11q+1)) + v₁₁(κ_{2q+2})? 
print("\n  f − vC vs s₁₁(q):")
for q in range(0, 15):
    print(f"  q={q:>2}: f−vC = {flow[q]-vC(11*q+1):>2}, s₁₁(q) = {s11(q)}")

# 直接猜: f_low(q) = ⌊log₁₁(88·(2q+2))⌋? 唔.
# 觀察 f_low: 0,1,1,1,2,1,3,3,? — 同 s₁₁(q) 有冇關?
# s₁₁(q): 0,1,2,3,4,5,6,7,8,9,10,1,2,3,4
# f_low:  0,1,1,1,2,1,3,3,?,?,?,?,?,?,?
# q=4: s₁₁=4, f=2; q=6: s₁₁=6, f=3; q=7: s₁₁=7, f=3?
for q in range(7, 15):
    d = 11*q+1
    print(f"  q={q}: f_low={flow[q]}, vC={vC(d)}, s₁₁(q)={s11(q)}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
