#!/usr/bin/env python3
"""
34_blind_test_fib5_lucas5.py — R5 anchor 對盲測 (2026-10-17)
=============================================================
33 號發現 (後驗, 必須盲測): magic = {m·L₄, m·L₅, m·F₅ : m∈{1,2,3,4}}
  候選集 = [5,7,11,14,20,22,33] (7 個) — magic 5/5 全覆蓋!

預註冊規則 R5 (locked, 唔准事後改):
  R5a: 唔指定 anchor — 由 43 個 d 隨機揀 3 個 anchor {a,b,c}, 生成集
       G(a,b,c) = {m·a, m·b, m·c : m∈{1,2,3,4}} ∩ [1,43],
       㩗 P(|G ∩ magic| = 5)?  → 巧合概率 (任意 3 anchor 就覆蓋 magic 嘅機會)
  R5b: 固定 anchor = {L₄, L₅, F₅} = {7,11,5} — 呢個係「唯一 F₅/L₅ 同 index 對」?
       要計: 43 個 d 入面有幾多對 (x,y) 滿足「F_k=x, L_k=y 同一 index」?
       → F/L pair 唯一性 + 覆蓋唯一性
  R5c: 綁定乘數 {1,2,3,4} = 頭四個 Lucas 值 — 隨機乘數集覆蓋 magic 概率
  R5d: TEST C 對比 — R5 候選集 (7) vs 舊 R1+R2 候選集 (15)? 唯一性提升?

MC 10^6, seed 固定 20261017, 雙軌 closed-form.
零 import 原推導; 純整數.
"""
import json, random
from math import gcd
from collections import Counter

random.seed(20261017)
MAGIC = [7, 14, 20, 22, 33]
ALLD = list(range(1, 44))
N = 10**6

# anchor 生成集
def G(anchors, ms=(1, 2, 3, 4)):
    out = set()
    for a in anchors:
        for m in ms:
            v = m * a
            if 1 <= v <= 43:
                out.add(v)
    return out

# ---- R5a: 隨機 3 anchor — 巧合概率 ----
cnt = 0
for _ in range(N):
    a3 = random.sample(ALLD, 3)
    cnt += len(G(a3) & set(MAGIC)) == 5
p5a = cnt / N

# closed-form R5a: 要算幾多個 (43 揀 3) 組合覆蓋 magic 5/5 — 用枚舉
cover_count = 0
total_tri = 0
from itertools import combinations
for tri in combinations(ALLD, 3):
    total_tri += 1
    if len(G(tri) & set(MAGIC)) == 5:
        cover_count += 1
p5a_cf = cover_count / total_tri

# ---- R5b: F_k / L_k 同 index 對喺 43 內有幾多 ----
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
pairs = []
for k in range(2, 12):
    f, l = fib(k), luc(k)
    if f <= 43 and l <= 43:
        pairs.append((k, f, l))
# 其中幾多對 = (5,11) 且 anchor 覆蓋 magic?
g_pairs = []
for (k, f, l) in pairs:
    g = G([f, l, pairs[0][1]])  # 試第三 anchor = 第一個 F
    g_pairs.append((k, f, l, len(G([f, l]) & set(MAGIC))))
# (5,11) 對: 加第三 anchor 揀邊個先覆蓋 5/5?
best3 = []
for (k, f, l) in pairs:
    for third in ALLD:
        if len(G([f, l, third]) & set(MAGIC)) == 5:
            best3.append((k, f, l, third))
            break

# ---- R5c: 乘數隨機 — 4 個乘數隨機揀, 覆蓋 magic 概率 ----
cnt_c = 0
MS_POOL = list(range(1, 9))
for _ in range(N):
    ms = random.sample(MS_POOL, 4)
    cnt_c += len(G([7, 11, 5], ms) & set(MAGIC)) == 5
p5c = cnt_c / N

# ---- R5d: 候選集對比 ----
cand_r5 = sorted(G([7, 11, 5]))
# 舊 R1+R2 候選 (TEST C 26 號)
L = {0: 2, 1: 1, 2: 3, 3: 4, 4: 7, 5: 11, 6: 18, 7: 29}
lstar = sorted({m * Lk for Lk in L.values() for m in (1, 2, 3) if 1 <= m * Lk <= 43})
DATA = {11, 13, 17, 19, 21, 25}
old_cand = [d for d in lstar if d not in DATA]
rest = [d for d in cand_r5 if d not in MAGIC]

res = {
    "test": "34_blind_test_fib5_lucas5",
    "R5a": {"mc_1e6": round(p5a, 6), "closed_form": round(p5a_cf, 6),
            "cover_triples": cover_count, "total_triples": total_tri,
            "note": "隨機 3 anchor 就覆蓋 magic 5/5 嘅概率"},
    "R5b": {"pal_index_pairs": pairs,
            "note": "F_k/L_k 同 index 對 (兩者都 ≤43) — 只有 (5,11) 係質數對?",
            "first_third_hit": best3[:3]},
    "R5c": {"mc_1e6": round(p5c, 6), "note": "anchor 固定 {7,11,5}, 乘數 8 揀 4 覆蓋概率"},
    "R5d": {"cand_r5": cand_r5, "n": len(cand_r5),
            "old_R1R2_cand_n": len(old_cand),
            "magic_in_r5": [d for d in MAGIC if d in cand_r5],
            "non_magic_in_r5": rest,
            "uniqueness": "R5 候選 7 vs 舊 15 — 唯一性提升"},
}

with open("data/34_blind_test_fib5_lucas5.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)

print("=== R5a: 隨機 3 anchor 覆蓋 magic 5/5 概率 ===")
print(f"  MC 10^6: {p5a:.6f}   closed-form: {p5a_cf:.6f}  ({cover_count}/{total_tri} triples)")
print()
print("=== R5b: F_k/L_k 同 index 對 (≤43) ===")
for (k, f, l) in pairs:
    print(f"  k={k:2d}: F_k={f:2d} L_k={l:2d}  magic 覆蓋(2 anchor)={len(G([f,l])&set(MAGIC))}")
print(f"  (5,11) 加第三 anchor 就覆蓋: {best3[:3]}")
print()
print("=== R5c: 乘數隨機 (anchor 固定 {7,11,5}) ===")
print(f"  MC: {p5c:.6f}")
print()
print("=== R5d: 候選集唯一性 ===")
print(f"  R5 候選 = {cand_r5} ({len(cand_r5)} 個) vs 舊 R1+R2 = {len(old_cand)} 個")
print(f"  非 magic 殘餘 = {rest}")
print()
print("輸出: data/34_blind_test_fib5_lucas5.json")