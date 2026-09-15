#!/usr/bin/env python3
# O200 scripts/02d — T2 定理: v₁₁(κ_{2m}) Fibonacci×11 自相似 (大域驗證)
# 定理候選: v₁₁(κ_{2m}) = 0 ⟺ 11-free part of m ∈ {1,2,3,5} = {F₂,F₃,F₄,F₅}
# 等價: κ_{2m} ≢ 0 (mod 11) ⟺ m = d·11^j, d ∈ {1,2,3,5}
# 驗證策略: mod-11 遞迴 (唔使完整大整數) → m ≤ 1000
#   κ_{2j} ≡ C(2j,j) − Σ_{m<j} C(2j−1,2m−1)·C(2j−2m,j−m)·κ_{2m} (mod 11)
#   每步 O(j) 模乘 — 快到 m=1000
import math

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

def v11_free(m):
    while m % 11 == 0: m //= 11
    return m

P = 11
M = 1000
# mod-11 遞迴
kap11 = [0]*(M+1)
for j in range(1, M+1):
    val = math.comb(2*j, j) % P
    for m in range(1, j):
        val -= (math.comb(2*j-1, 2*m-1) * math.comb(2*j-2*m, j-m) % P) * kap11[m]
    kap11[j] = val % P

# 定理: kap11[m] ≠ 0 ⟺ v11_free(m) ∈ {1,2,3,5}
pred = {1, 2, 3, 5}
nonzero = [m for m in range(1, M+1) if kap11[m] != 0]
pred_nz = [m for m in range(1, M+1) if v11_free(m) in pred]
check(f"H1' κ_{{2m}} ≢ 0 (mod 11) ⟺ 11-free(m) ∈ {{1,2,3,5}} (m≤{M})",
      set(nonzero) == set(pred_nz),
      f"命中 {len(nonzero)}/{M}")

# 交叉驗證: 頭 130 個 mod-11 nonzero 位 = 完整 κ v₁₁=0 位 (scripts/02c: [1,2,3,5,11,22,33,55,121])
nz130 = [m for m in range(1, 131) if kap11[m] != 0]
check(f"H1'' mod-11 nonzero (m≤130) = 完整 v₁₁=0 位 [1,2,3,5,11,22,33,55,121]",
      nz130 == [1, 2, 3, 5, 11, 22, 33, 55, 121], f"{nz130}")

# H2 大域: κ_{2·11k} ≡ κ_{2k} (mod 11) ∀k ≤ M/11
ok2 = all((kap11[11*k] - kap11[k]) % 11 == 0 for k in range(1, M//11 + 1))
check(f"H2 κ_{{2·11k}} ≡ κ_{{2k}} (mod 11) ∀k (m≤{M})", ok2)

# 更高模: mod 121 檢查 (v₁₁ ≥ 2 位)
# 用 mod 121 遞迴 (M=200) — 睇 v₁₁(κ) ≥ 2 嘅位
M2 = 200
P2 = 121
kap121 = [0]*(M2+1)
for j in range(1, M2+1):
    val = math.comb(2*j, j) % P2
    for m in range(1, j):
        val -= (math.comb(2*j-1, 2*m-1) * math.comb(2*j-2*m, j-m) % P2) * kap121[m]
    kap121[j] = val % P2

# v₁₁(κ) ≥ 1 ⟺ κ ≡ 0 mod 11; v₁₁ ≥ 2 ⟺ κ ≡ 0 mod 121
ge2 = [m for m in range(1, M2+1) if kap121[m] == 0]
print(f"\n  v₁₁(κ) ≥ 2 位 (m≤{M2}): {ge2}")
# 完整 κ 嘅 v₁₁ ≥ 2 (scripts/02b): 6, 17-21, 28-32, 39-43, 45-54, 50-54=3...
# mod 121 = 0 應該 = v₁₁ ≥ 2
from collections import Counter
# 完整 κ v₁₁ (m≤60) 已知: 0,0,0,1,0,2,1,1,1,1,0,1,1,1,1,1,2,2,2,2,2,0,1,1,1,1,1,2,2,2,2,2,0,1,1,1,1,1,2,2,2,2,2,1,2,2,2,2,2,3,3,3,3,3,0,1,1,1,1,1
full_v11_60 = [0,0,0,1,0,2,1,1,1,1,0,1,1,1,1,1,2,2,2,2,2,0,1,1,1,1,1,2,2,2,2,2,0,1,1,1,1,1,2,2,2,2,2,1,2,2,2,2,2,3,3,3,3,3,0,1,1,1,1,1]
ge2_full = [m for m in range(1, 61) if full_v11_60[m-1] >= 2]
check(f"H3 mod-121 = 0 ⟺ v₁₁(κ) ≥ 2 (m≤60)", [m for m in ge2 if m <= 60] == ge2_full,
      f"mod121: {[m for m in ge2 if m <= 60]} vs 完整: {ge2_full}")

# 11-free 部分嘅完整結構: v₁₁(κ_{2m}) 只依賴 11-free(m)?
# 檢查: v₁₁(κ_{2·11k}) vs v₁₁(κ_{2k}) — 完整 v₁₁ (m≤130 已知 zeros; ≥2 位待查)
# mod-121 層: κ_{2·11k} ≡ κ_{2k} (mod 121)? (H2' 之前 FAIL — 只 mod 11)
ok121 = all((kap121[11*k] - kap121[k]) % 121 == 0 for k in range(1, M2//11 + 1))
check("H2' κ_{2·11k} ≡ κ_{2k} (mod 121) (m≤200)", ok121)

# 全 11-adic 收縮階層: κ_{2·11^e·d} mod 11^e?
print("\n== H5: 11-adic 收縮階層 (κ_{2m} mod 11^a 依賴 11-free(m)?) ==")
# 對 d ∈ {1,2,3,5} (v₁₁=0) 同 d=4 (v₁₁=1): κ_{2d}, κ_{22d}, κ_{242d} 比較
for d in [1, 2, 3, 4, 5, 6]:
    vals = []
    m = d
    while m <= 500:
        # 計完整 κ_{2m} 嘅 v₁₁ — 用 mod 11^4 遞迴太慢; 用完整 big int 但只到 m ≤ 60
        vals.append(m)
        m *= 11
    if len(vals) > 1 and d <= 60:
        print(f"  d={d}: 位 {vals}")

# 完整 κ 嘅 v₁₁ (m ≤ 60) 同 11-free 關係:
# v₁₁(κ_{2m}) vs v₁₁(κ_{2·(m/11)}) for 11|m:
print("\n  11|m 時 v₁₁(κ) 比較 (完整 m≤60):")
for m in [11, 22, 33, 44, 55]:
    print(f"  m={m}: v₁₁(κ_{{2m}})={full_v11_60[m-1]}, v₁₁(κ_{{2·{m//11}}})={full_v11_60[m//11-1]}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
