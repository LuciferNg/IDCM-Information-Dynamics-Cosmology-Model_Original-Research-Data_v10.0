#!/usr/bin/env python3
# O200 scripts/02c — T2 深化: v₁₁(κ_{2m}) Fibonacci×11 模式外推驗證
# 發現 (scripts/02b): v₁₁(κ_{2m})=0 ⟺ m ∈ {1,2,3,5,11,22,33,55}
#   = {F₂,F₃,F₄,F₅} ∪ 11·{F₂,F₃,F₄,F₅} (F₂=1,F₃=2,F₄=3,F₅=5)
# 假說 H1: zeros = {1,2,3,5}·11^j (j=0,1,2,...) — 11-adic 自相似
# 假說 H2: κ_{2·11k} ≡ κ_{2k} (mod 11) ∀k — 11-倍數收縮
# 驗證域: m ≤ 130 (κ_{260} 大整數)
import math
from collections import Counter

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

def v11_int(k):
    e = 0
    while k % 11 == 0: k //= 11; e += 1
    return e

M = 130
kap = [0]*(M+1)
for j in range(1, M+1):
    val = math.comb(2*j, j)
    for m in range(1, j):
        val -= math.comb(2*j-1, 2*m-1) * math.comb(2*j-2*m, j-m) * kap[m]
    kap[j] = val

vks = [v11_int(kap[m]) for m in range(1, M+1)]
zeros = [m for m in range(1, M+1) if vks[m-1] == 0]
print(f"v₁₁(κ)=0 位 (m≤{M}): {zeros}")

# H1: zeros = {1,2,3,5}·11^j ∩ [1,M]
h1_set = set()
for base in (1, 2, 3, 5):
    x = base
    while x <= M:
        h1_set.add(x)
        x *= 11
pred_zeros = sorted(h1_set)
print(f"H1 預言 zeros: {pred_zeros}")
check(f"H1 v₁₁(κ)=0 ⟺ m ∈ {{1,2,3,5}}·11^j (m≤{M})", set(zeros) == set(pred_zeros),
      f"實際 {zeros}")

# H2: κ_{2·11k} ≡ κ_{2k} (mod 11) ∀k, 11k ≤ M
ok2 = True
bad2 = []
for k in range(1, M//11 + 1):
    if (kap[11*k] - kap[k]) % 11 != 0:
        ok2 = False; bad2.append(k)
check(f"H2 κ_{{2·11k}} ≡ κ_{{2k}} (mod 11) ∀k (11k≤{M})", ok2,
      f"違反 k={bad2[:5]}" if bad2 else f"{M//11} 個 k 全中")

# H2 強化: mod 11^e? κ_{2·11k} ≡ κ_{2k} (mod 11^?) — 檢查 mod 121
ok3 = all((kap[11*k] - kap[k]) % 121 == 0 for k in range(1, M//11 + 1))
check("H2' κ_{2·11k} ≡ κ_{2k} (mod 121) ∀k", ok3)

# H3: v₁₁(κ_{2m}) 嘅完整結構 — 同 m 嘅 11-adic 分解關係?
# 觀察: v₁₁(κ) 序列 0,0,0,1,0,2,1,1,1,1,0,1,1,1,1,1,2,2,2,2,2,0,1,1,1,1,1,2,2,2,2,2,0,1,1,1,1,1,2,2,2,2,2,1,2,2,2,2,2,3,3,3,3,3,0,1,1,1,1,1
# 塊結構: m=6:2, 7-10:1, 12-16:1, 17-21:2, 23-27:1, 28-32:2, 34-38:1, 39-43:2, 44:1, 45-49:2, 50-54:3, 56-60:1
# 呢個好似同 m 喺 11 進位嘅數字和相關?
print("\n== H3: v₁₁(κ_{2m}) 結構探索 ==")
# 對比 v₁₁(κ_{2m}) 同 v₁₁(C(2m,m)) + 修正項
def v11_binom(ap, bp):
    p = 11
    def sd(x):
        s = 0
        while x: s += x % p; x //= p
        return s
    return (sd(bp) + sd(ap-bp) - sd(ap)) // (p-1)

vb = [v11_binom(2*m, m) for m in range(1, M+1)]
diff = [vks[m-1] - vb[m-1] for m in range(1, M+1)]
print("  m=1..60 diff (v₁₁(κ)−v₁₁(C)):", diff[:60])
# diff 非零位?
dnz = [m for m in range(1, M+1) if diff[m-1] != 0]
print(f"  diff≠0 位: {dnz}")
# diff = 1 位? (κ 比 C 多一個 11)
d1 = [m for m in range(1, M+1) if diff[m-1] == 1]
print(f"  diff=1 位 (m≤60): {[m for m in d1 if m <= 60]}")
print(f"  diff=1 位 (m=61..130): {[m for m in d1 if m > 60]}")
d2 = [m for m in range(1, M+1) if diff[m-1] == 2]
print(f"  diff=2 位: {d2}")

# 模式: diff≥1 ⟺ m ≥ 12 且 m ∉ {22,33,55}? (m=12..21 diff=1, 22 diff=0, 23..32 diff=1, 33 diff=0...)
# 睇嚟 diff = 1 喺 m ∈ [12,21] ∪ [23,32] ∪ [34,43] ∪ [45,49]∪[50,54] 部分...
# 可能同 11-進位嘅 m 數字有關: m = 11a + b → diff 依賴 a?
print("\n  m → diff (m=12..65):")
for m in range(12, 66):
    print(f"  {m}:{diff[m-1]}" if m % 11 in (0, 1) or m in range(12, 23) else "", end="")
print()

# 核心: κ_{2m} = C(2m,m) − Σ ... 嘅 Bell 遞迴 — 11-adic 由矩 m_j = C(2j,j) 決定
# C(2j,j) 嘅 11-adic: j ≥ 6 開始有 11 (j=6: C(12,6)=924=11·84)
# Bell 遞迴嘅 11-adic 轉移: v₁₁(κ_{2m}) 至少 = min over terms
print("\n== H4: 矩 C(2j,j) 首個帶 11 嘅 j = 6 (C(12,6)=924=11·84) ==")
j11 = [j for j in range(1, 40) if v11_binom(2*j, j) > 0]
print(f"  C(2j,j) 帶 11 因子嘅 j (≤39): {j11}")
# m=4 時 κ₈ 有 11 但 C(8,4)=70 冇 — 所以 κ 嘅 11 來自遞迴 (Bell) 唔係直接 C
print("  κ₈ = −2310 = −2·3·5·7·11 — C(8,4)=70 冇 11 ⟹ 11 由遞迴組合產生")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
