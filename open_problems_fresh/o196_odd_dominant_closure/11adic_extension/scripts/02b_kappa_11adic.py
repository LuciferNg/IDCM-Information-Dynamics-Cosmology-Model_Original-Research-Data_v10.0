#!/usr/bin/env python3
# O200 scripts/02b — T2 延伸: v₁₁(κ_{2m}) 自身 11-adic 結構
# 發現 (scripts/02): κ_{2m} 帶 11 因子 — v₁₁(κ) 序列 0,0,0,1,0,2,1,1,1,1,0,1,...
# SESSION_START 預言「v₁₁ 由 (2m)! 決定」錯 — κ 都有 11 因子
# 新問題: v₁₁(κ_{2m}) 有冇乾淨週期/機制? (11 = L₅)
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

# κ_{2m} 整數遞迴 (O195 Thm 2), 擴到 m=60
M = 60
kap = [0]*(M+1)
for j in range(1, M+1):
    val = math.comb(2*j, j)
    for m in range(1, j):
        val -= math.comb(2*j-1, 2*m-1) * math.comb(2*j-2*m, j-m) * kap[m]
    kap[j] = val

print("== T2e: v₁₁(κ_{2m}) 序列 (m=1..60) ==")
vks = [v11_int(kap[m]) for m in range(1, M+1)]
print("  m:        ", " ".join(f"{m:>2}" for m in range(1, M+1)))
print("  v₁₁(κ):  ", " ".join(f"{v:>2}" for v in vks))

# 分佈統計
from collections import Counter
cnt = Counter(vks)
print(f"\n  v₁₁ 分佈: {dict(sorted(cnt.items()))}")
zeros = [m for m in range(1, M+1) if vks[m-1] == 0]
print(f"  v₁₁(κ)=0 嘅 m: {zeros}")

# 假說: v₁₁(κ_{2m}) ≥ 1 ⟺ m ≥ 4 且 m ∉ {5} ∪ {11k}?
h1 = all(vks[m-1] >= 1 for m in range(4, M+1) if m not in zeros)
print(f"\n  假說 1: m≥4 且 m∉{zeros} ⟹ v₁₁≥1: {h1}")
# 假說: zeros = {1,2,3,5} ∪ {11,22,33,44,55} (11 倍數)?
z11 = [m for m in zeros if m % 11 == 0]
print(f"  zeros 中 11 倍數: {z11}")

# 假說 2: v₁₁(κ_{2m}) = v₁₁(C(2m,m) 嘅某種 11 部分) + 修正?
# C(2m,m) 嘅 v₁₁ (Legendre): s₁₁(2m) − 2s₁₁(m)) / 10? 
def v11_binom(ap, bp):
    """v_p(C(ap,bp)) = (s_p(bp) + s_p(ap-bp) − s_p(ap))/(p−1)"""
    p = 11
    def sd(x):
        s = 0
        while x: s += x % p; x //= p
        return s
    return (sd(bp) + sd(ap-bp) - sd(ap)) // (p-1)

vb = [v11_binom(2*m, m) for m in range(1, M+1)]
print("\n== T2f: v₁₁(C(2m,m)) (Legendre) vs v₁₁(κ_{2m}) ==")
print("  m:     ", " ".join(f"{m:>2}" for m in range(1, 31)))
print("  v₁₁(C):", " ".join(f"{v:>2}" for v in vb[:30]))
print("  v₁₁(κ):", " ".join(f"{v:>2}" for v in vks[:30]))
# C(2m,m) 有冇 11? (C(2m,m) 11-free ⟺ 2m 冇進位 in base 11)
cfree = [m for m in range(1, M+1) if v11_binom(2*m, m) == 0]
print(f"\n  v₁₁(C(2m,m))=0 嘅 m: {cfree}")
# 對比: κ 嘅 v₁₁ vs C 嘅 v₁₁ — 有冇簡單關係?
diff = [vks[m-1] - vb[m-1] for m in range(1, M+1)]
print(f"  v₁₁(κ) − v₁₁(C): {diff}")

# 核心問題: κ_{2m} mod 11 週期性?
print("\n== T2g: κ_{2m} mod 11 週期性 (Lucas 型) ==")
kmod = [kap[m] % 11 for m in range(1, M+1)]
print("  m:        ", " ".join(f"{m:>2}" for m in range(1, 61)))
print("  κ mod 11:", " ".join(f"{k:>2}" for k in kmod))
# 週期? 檢查 11-週期: κ_{m+11} ≡ κ_m (mod 11)?
per11 = all((kap[m+11] - kap[m]) % 11 == 0 for m in range(1, M-10))
check("T2g κ_{2m} mod 11 週期 11 (κ_{m+11} ≡ κ_m)", per11)
# 週期 22?
per22 = all((kap[m+22] - kap[m]) % 11 == 0 for m in range(1, M-21))
check("T2g κ_{2m} mod 11 週期 22 (κ_{m+22} ≡ κ_m)", per22)

# 更重要: v₁₁(κ_{2m}) 有冇「m ≥ 4 → 幾乎永遠 ≥ 1」+ 特殊零位?
# 零位分析
print(f"\n  v₁₁(κ)=0 位: {zeros}")
print(f"  11 倍數 m: {[m for m in range(1, M+1) if m % 11 == 0]}")
# 5 同 11 嘅關係?  m=5 係唯一 < 11 嘅零位
print(f"  假說: zeros = {{1,2,3,5}} ∪ {{11k}}?  ->", 
      set(zeros) == {1,2,3,5} | {11*k for k in range(1, 6)})

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
