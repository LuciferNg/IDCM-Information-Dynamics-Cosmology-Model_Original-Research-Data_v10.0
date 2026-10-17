#!/usr/bin/env python3
"""
37_r5_necessity_and_extension.py — 缺 {4,16} 結構必然性 + 88-site 前向預測 (2026-10-17)
========================================================================================
後驗補盲測前 — 先將 35/36 號「後驗拼湊」昇做結構必然:

T1: gcd4 缺 = 代數必然?  gcd4 候選 {8,16,24,32,40} 全 ≡0 mod 8;
    anchor {5,7,11} × m∈{1,2,3,4} mod 8 ∈ {1,2,3,4,5,6,7} 永不出 0
    ⟹ R5 生成集 ∩ gcd4 = ∅ 必然而非巧合
T2: gcd16 缺 = 撞層必然?  gcd16 = {12,28}; 12 ∉ R5 生成集;
    28 = 4×7 ∈ 生成集 但 deg5 層被 S3 (由 gcd8 20 佔) 排除
T3: 完整程序正式化 (可移植演算法, 任何 N)
T4: 88-site 前向預測: R5 程序 apply N=88 (9 gcd 類) — 輸出代表集?
    留意: 88-site 冇 P13 label (29 號), 預測輸出 = 程序自洽性檢查

零 import; 純整數。
"""
import json
from math import gcd

def gcl_N(d, N):
    return gcd(abs(2*N - d) if False else abs(N - d), 4*N) if False else gcd(abs(N - d), 2*N if False else 4*N)
# 通用: 44-site: gcd(|44−d|,176) = gcd(|N−d|,4N); 88-site: gcd(|88−d|,352)

def phi(n):
    r = n; m = n; p = 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            r -= r // p
        p += 1
    if m > 1:
        r -= r // m
    return r

def om_deg_N(d, N):
    g = gcl_N(d, N)
    m = 4 * N // g
    return phi(m) // 2

def luc(k):
    a, b = 2, 1
    for _ in range(k):
        a, b = b, a + b
    return a

def fib(k):
    a, b = 0, 1
    for _ in range(k):
        a, b = b, a + b
    return a

# ---- T1: gcd4 缺 = 代數必然 ----
print("=== T1: 缺 {4,16} 喺 R5 下嘅必然性 ===")
anchors = [7, 11, 5]
residues = set()
for a in anchors:
    for m in (1, 2, 3, 4):
        residues.add((m * a) % 8)
print(f"  anchor{{5,7,11}}×m{{1,2,3,4}} mod 8 = {sorted(residues)}  (0 ∈? {0 in residues})")
print(f"  gcd4 候選 {{8,16,24,32,40}} mod 8 = 全部 0")
print(f"  ⟹ gcd4 候選全部 ≡0 mod8 但 R5 生成集永不出 0 mod8 ⟹ 生成集 ∩ gcd4 = ∅ 必然!")

# 驗證 43 内全部 anchor×m
gen43 = sorted({m*a for a in anchors for m in (1,2,3,4) if 1 <= m*a <= 43})
gcd4 = [d for d in range(1, 44) if gcl_N(d, 44) == 4]
print(f"  R5 生成集 (44-site) = {gen43}")
print(f"  gcd4 類 = {gcd4}   交集 = {sorted(set(gen43) & set(gcd4))} (∅ = 必然 ✓)")

# ---- T2: gcd16 缺 = 撞層必然 ----
print()
print("=== T2: gcd16 缺 — 28 撞層機制 ===")
gcd16 = [d for d in range(1, 44) if gcl_N(d, 44) == 16]
print(f"  gcd16 = {gcd16}")
print(f"  12 喺 R5 生成集? {12 in gen43}")
print(f"  28 喺 R5 生成集? {28 in gen43}   deg(28) = {om_deg_N(28, 44)}")
deg5_cand = [(d, om_deg_N(d, 44)) for d in gen43]
print(f"  生成集 deg 分佈: {sorted(set(dg for _, dg in deg5_cand))}")
deg5_gen = sorted(d for d, dg in deg5_cand if dg == 5)
print(f"  deg5 生成候選 = {deg5_gen}  (gcd8: {[d for d in deg5_gen if gcl_N(d,44)==8]}, gcd16: {[d for d in deg5_gen if gcl_N(d,44)==16]})")
print(f"  ⟹ deg5 層兩個候選 20 (gcd8), 28 (gcd16) — S3 每 deg 層一代表, 前半優先 → 20")

# ---- T3: 完整程序正式化 ----
print()
print("=== T3: 完整選擇程序 (可移植, 兩階段) ===")

def is_lucas_chain(d):
    return any(d == m * luc(k) for m in (1, 2, 3, 4) for k in range(2, 7))

def r5_procedure(N, anchors=(7, 11, 5), ms=(1, 2, 3, 4)):
    """R5 完整程序 (兩階段):
       Phase A 類内:  生成 → data-free(44-site) → 每 gcd 類一代表 (S5 唯一Lucas∧質數, 否則 Lucas 鏈)
       Phase B 跨類: 每 deg 層一代表 (撞層半球優先 d<N/2)"""
    gen = sorted({m*a for a in anchors for m in ms if 1 <= m*a <= N-1})
    DATA_N = set()
    if N == 44:
        DATA_N = {11, 13, 17, 19, 21, 25}
    cand = [d for d in gen if d not in DATA_N]
    # S2 每 gcd 類 → Phase A 類内代表
    byg = {}
    for d in cand:
        byg.setdefault(gcl_N(d, N), []).append(d)
    reps = []
    for g, lst in sorted(byg.items()):
        if len(lst) == 1:
            reps.append(lst[0])
        else:
            # S5: 唯一 Lucas∧質數 (3,7,11,29)
            lp = [d for d in lst if d in (3, 7, 11, 29)]
            if len(lp) == 1:
                reps.append(lp[0])
            else:
                # Lucas 鏈優先 (14=2L₄ vs 10=2F₅)
                lch = [d for d in lst if is_lucas_chain(d)]
                if len(lch) == 1:
                    reps.append(lch[0])
                else:
                    reps.append(min(lst))
    # Phase B 跨類: 每 deg 層一代表 (撞層前半優先)
    bydeg = {}
    for d in reps:
        bydeg.setdefault(om_deg_N(d, N), []).append(d)
    final = []
    for de, lst in sorted(bydeg.items()):
        if len(lst) == 1:
            final.append(lst[0])
        else:
            final.append(min(lst, key=lambda x: (x >= N//2, x)))
    return sorted(final), {str(g): v for g, v in sorted(byg.items())}, {str(de): v for de, v in sorted(bydeg.items())}

res44, byg44, bydeg44 = r5_procedure(44)
print(f"  44-site: 程序輸出 = {res44}   magic = {{7,14,20,22,33}}  一致? {set(res44) == {7,14,20,22,33}}")
for g in sorted(byg44, key=int):
    print(f"    gcd{g:>2}: {byg44[g]}")

# ---- T4: 88-site 前向預測 ----
print()
print("=== T4: 88-site 前向預測 (R5 程序 push 去 N=88) ===")
res88, byg88, bydeg88 = r5_procedure(88)
print(f"  88-site 程序輸出 = {res88} ({len(res88)} 個代表)")
for g in sorted(byg88, key=int):
    print(f"    gcd{g:>2}: {byg88[g]}")
# 對比 magic 5 個喺 88-site 嘅 gcd 去向
magic88 = sorted({d: gcl_N(d, 88) for d in [7, 14, 20, 22, 33]}.items())
print(f"  magic{{7,14,20,22,33}} 喺 88-site 嘅 gcd: {magic88}")
print(f"  程序預測包含 magic 5 個? {all(d in res88 for d in [7,14,20,22,33])}")

res = {
    "test": "37_r5_necessity_and_extension",
    "T1": {"anchor_residues_mod8": sorted(residues), "gcd4_intersect": sorted(set(gen43) & set(gcd4))},
    "T2": {"gcd16": gcd16, "12_in_gen": 12 in gen43, "28_in_gen": 28 in gen43,
           "deg5_gen": deg5_gen},
    "T3": {"proc44_output": res44, "match_magic": set(res44) == {7, 14, 20, 22, 33}},
    "T4": {"proc88_output": res88, "magic_in_88": all(d in res88 for d in [7, 14, 20, 22, 33])},
}
with open("data/37_r5_necessity_extension.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)
print()
print("輸出: data/37_r5_necessity_extension.json")