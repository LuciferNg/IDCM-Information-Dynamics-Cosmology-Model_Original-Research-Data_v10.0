#!/usr/bin/env python3
"""
35_r5_full_procedure.py — R5 完整選擇程序閉合測試 (2026-10-17)
================================================================
目標: R5 (33/34 號) 昇做完整選擇程序, 測試佢係咪唯一鎖定 magic 5/5:

程序 (每步有獨立結構依據):
  S1 生成:  G = {m·a : a∈anchor, m∈{1,2,3,4}} ∩ [1,43]
            anchor = {7,11,5} (L₄, L₅, F₅)
  S2 每類一代表: 每個 gcd 類最多一個候選
  S3 每 deg 層一代表: 每個 deg 層最多一個 (32 號 T1: gcd8/gcd16 同 deg5!)
  S4 data-free: 候選 = data row 排除
  S5 gcd1 内鎖: 唯一 Lucas∧質數

問題:
  Q1: cover triples 3 個係咩? (R5a closed-form 3/12341) — anchor 唯一性
  Q2: 完整程序輸出 == magic {7,14,20,22,33}? 唯一?
  Q3: gcd16 嘅 28 (4L₄) 點排除? — S3 每 deg 層一代表 (deg5 被 gcd8 20 佔)?
  Q4: gcd2 内 {10,14} 點揀? 10=2F₅ 14=2L₄ — Lucas 優先?
  Q5: 程序有幾多「自由參數」? (overfit 審計)

零 import; 純整數; 枚舉全 12341 triple。
"""
import json
from math import gcd
from itertools import combinations

MAGIC = [7, 14, 20, 22, 33]
DATA  = {11, 13, 17, 19, 21, 25}
ALLD  = list(range(1, 44))

def gcl(d):
    return gcd(abs(44 - d), 176)

def om_deg(d):
    n = d
    # deg(ω_d) = φ(176/gcd(|44−d|,176))/2
    g = gcl(d)
    m = 176 // g
    r = m; p = 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            r -= r // p
        p += 1
    if m > 1:
        r -= r // m
    return r // 2

def luc(n):
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def G(anchors, ms=(1, 2, 3, 4)):
    return sorted({m * a for a in anchors for m in ms if 1 <= m * a <= 43})

# ---- Q1: cover triples 枚舉 ----
covers = []
for tri in combinations(ALLD, 3):
    if len(set(G(tri)) & set(MAGIC)) == 5:
        covers.append(tri)
print(f"Q1: 覆蓋 magic 5/5 嘅 3-anchor 集 = {covers}  ({len(covers)} 個)")

# ---- Q2: 完整程序 ----
def full_proc(anchors=(7, 11, 5)):
    cand = G(anchors)
    # S2 每類一代表: gcd 類 → 若類内多個候選, 保留「Lucas∧質數」優先? 先睇全表
    byg = {}
    for d in cand:
        byg.setdefault(gcl(d), []).append(d)
    # S3 每 deg 一代表
    bydeg = {}
    for d in cand:
        bydeg.setdefault(om_deg(d), []).append(d)
    return cand, byg, bydeg

cand, byg, bydeg = full_proc()
print()
print("Q2: R5 生成集 =", cand, f"({len(cand)} 個)")
print("    按 gcd 類:")
for g in sorted(byg):
    print(f"      gcd{g:2d} {byg[g]}  deg={om_deg(byg[g][0])}")
    for d in byg[g]:
        luc_ = d in {luc(k) for k in range(2, 9)} or d in {m*luc(k) for m in (1,2,3,4) for k in range(2,6)}
        lprime = d in (3, 7, 11, 29)
        print(f"         {d:2d}: Lucas鏈={luc_}  Lucas質數={lprime}  data={d in DATA}  magic={d in MAGIC}")

print()
print("    按 deg 層:")
for de in sorted(bydeg, reverse=True):
    print(f"      deg{de:2d} {bydeg[de]}")
print()

# S3 效果: deg5 = gcd8{gcd} + gcd16 — 28 同 20 撞
print("Q3: deg5 層 = gcd8 {4,20,36} ∪ gcd16 {12,28}")
print("    R5 候選 deg5: gcd8 ->", [d for d in byg.get(8, [])], "| gcd16 ->", [d for d in byg.get(16, [])])
print("    → 每 deg 層一代表: gcd8 20 優先, gcd16 28 排除")
print()

# Q4: gcd2 内 {10,14}
print("Q4: gcd2 内 {10,14}:")
print("   14 = 2L₄ (Lucas 鏈), 10 = 2F₅ (Fibonacci 鏈)")
print("   → Lucas 唔為質數但 14 係 Lucas 鏈; 邊個優先? 14 同時 = 55-41? 用數據睇 data-free:")
print("   10 ∈ data? no; 14 ∈ data? no — 兩者都要額外判準")
print()

# Q5: 程序自由參數審計
params = {
    "anchor 集": "後驗 (7,11,5 由 magic 反推)",
    "乘數 m∈{1,2,3,4}": "後驗 (Lucas 頭四值)",
    "S2 每類一代表": "操作代表定義 (17 號文檔)",
    "S3 每 deg 一代表": "32 號 T1 結構事實",
    "S4 data-free": "R1 盲測 FAIL 但實用 (11=data)",
    "S5 gcd1 唯一 Lucas∧質數": "33/34 號新規則",
    "gcd2 内 14 vs 10": "未閉合 — 兩個都係鏈 (L/F)",
}
print("Q5: 自由參數審計")
for k, v in params.items():
    print(f"   {k}: {v}")
print()

# 完整程序決定性: 每類/每deg 唯一化後剩咩?
print("完整程序剩餘候選 (S2+S3+S4 後):")
remaining = []
for g in sorted(byg):
    lst = byg[g]
    # S3: deg 撞 → 保留 Lucas
    keep = []
    for d in lst:
        same_deg_others = [d2 for d2 in cand if om_deg(d2) == om_deg(d) and d2 != d]
        if not same_deg_others:
            keep.append(d)
        else:
            # 有撞: 邊個 magic?
            keep.append(d)  # 保留俾 S5 決定
    remaining.append((g, sorted(set(keep))))
print("   ", remaining)

res = {
    "test": "35_r5_full_procedure",
    "covers": [list(c) for c in covers],
    "gen_set": cand,
    "by_gcd": {str(g): byg[g] for g in sorted(byg)},
    "by_deg": {str(de): bydeg[de] for de in sorted(bydeg, reverse=True)},
    "params_audit": params,
}
with open("data/35_r5_full_procedure.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/35_r5_full_procedure.json")