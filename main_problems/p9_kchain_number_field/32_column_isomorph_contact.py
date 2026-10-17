#!/usr/bin/env python3
"""
32_column_isomorph_contact.py — 整欄/整列同構與接觸點 (2026-10-17)
=================================================================
調律者指示: 「看看整欄或整列有什麼同構點或接觸點」

框架:
  44×44 beat 矩陣 (上三角), 列 n = 固定端點 n 同全部 j 嘅 beat
  「同構」: 兩列嘅結構 profile 相同 (deg/lcm 結構, 唔係數值)
  「接觸」: 列 n 嘅格 (n,j) 落入 magic row d (|n−j| ∈ magic) / data row

關鍵定理: deg(beat(i,j)) = lcm(deg ω_i, deg ω_j) ⟹ 列 profile 完全由 deg ω_n 決定

測試:
  T1 列同構分類: 44 列按 deg ω_n 分組 — 邊啲列結構完全一樣?
  T2 magic 接觸: 每列 n 有幾多格落入 magic row {7,14,20,22,33}?
  T3 data 接觸: 每列 n 有幾多格落入 data row {11,13,17,19,21,25}?
  T4 端點-端點相撞: data 格 (i,j) 嘅端點值同 magic 重合?
  T5 同構端點系: 有相同 deg 嘅端點群內, magic 代表 7 嘅位置

零 import 原推導; 純整數。
"""
import json
from math import gcd
from collections import Counter, defaultdict

MAGIC = [7, 14, 20, 22, 33]
DATA  = {11, 13, 17, 19, 21, 25}

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

def gcl(n):
    return gcd(abs(44 - n), 176)

def om_deg(n):
    return phi(176 // gcl(n)) // 2

def gm_deg(n):
    return phi(88 // gcd(n, 88)) // 2

# 端點基礎
n_info = {}
for n in range(1, 45):
    n_info[n] = {"gcd": gcl(n), "om_deg": om_deg(n), "gm_deg": gm_deg(n),
                 "in_magic": n in MAGIC, "in_data": n in DATA}

# T1: 列同構 = deg ω_n 相同層 (lcm 定理 ⟹ 層內 profile 全同)
deg_classes = defaultdict(list)
for n in range(1, 45):
    deg_classes[om_deg(n)].append(n)

T1 = {f"deg{de}": {"n": v, "magic_in": [x for x in v if x in MAGIC],
                    "data_in": [x for x in v if x in DATA]} for de, v in sorted(deg_classes.items(), reverse=True)}

# T2/T3: 每列 magic/data 接觸 (格水平)
col_contact = {}
for n in range(1, 45):
    magic_hits = [j for j in range(1, 45) if j != n and abs(n - j) in MAGIC]
    data_hits = [j for j in range(1, 45) if j != n and abs(n - j) in DATA]
    col_contact[n] = {
        "magic_hits": sorted(magic_hits), "n_magic": len(magic_hits),
        "data_hits": sorted(data_hits), "n_data": len(data_hits),
        "magic_ds": sorted(set(abs(n - j) for j in magic_hits)),
        "data_ds": sorted(set(abs(n - j) for j in data_hits)),
    }

# T4: data 格端點 × magic 重合
data_cells = [(30, 41), (7, 20), (8, 22), (10, 24), (19, 33), (1, 18), (19, 38), (1, 22), (8, 33)]
T4 = []
for (i, j) in data_cells:
    d = abs(i - j)
    T4.append({"cell": (i, j), "d": d,
               "mi": i in MAGIC, "mj": j in MAGIC,
               "magic_endpoints": [x for x in (i, j) if x in MAGIC],
               "data_row": d in DATA})

# T5: 同構端點系內 magic 代表位置 (gcd1 層 20 個, magic=7)
g1 = deg_classes.get(40, [])
T5 = {
    "deg40_layer": g1,
    "magic_in_layer": [x for x in g1 if x in MAGIC],   # expect [7]
    "data_in_layer": sorted([x for x in g1 if x in DATA]),  # expect 6 個 data 都喺 deg40!
    "position_of_7": {"index": g1.index(7) + 1, "total": len(g1),
                       "first_Lucas_prime": 7 == min(x for x in g1 if x in {3, 7, 29})},
}

res = {
    "test": "32_column_isomorph_contact",
    "T1_deg_layer_classes": T1,
    "T2_T3_col_contact": col_contact,
    "T4_data_cell_endpoints": T4,
    "T5_g1_layer": T5,
}

with open("data/32_column_isomorph_contact.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)

print("=== T1: 列同構 = deg ω_n 層 (lcm 定理) ===")
for de, v in sorted(deg_classes.items(), reverse=True):
    print(f"  deg={de:3d}: n = {v}")
    print(f"          magic 內 = {[x for x in v if x in MAGIC]}  data 內 = {[x for x in v if x in DATA]}")
print()
print("=== T2/T3: 每列 magic/data 接觸數 ===")
max_magic = max(col_contact.values(), key=lambda v: v["n_magic"])
print(f"  max magic 接觸 = {max_magic['n_magic']} (列 n=? 見 JSON)")
magic_contact_hist = Counter(v["n_magic"] for v in col_contact.values())
print(f"  magic 接觸數分佈 (列數): {dict(sorted(magic_contact_hist.items()))}")
data_contact_hist = Counter(v["n_data"] for v in col_contact.values())
print(f"  data 接觸數分佈 (列數): {dict(sorted(data_contact_hist.items()))}")
print()
print("=== T4: data 格端點 × magic ===")
for t in T4:
    print(f"  {t['cell']} d={t['d']:2d}: magic端點={t['magic_endpoints']!s:9s} data_row={t['data_row']}")
print()
print("=== T5: deg40 層 (gcd1) — 7 嘅位置 ===")
print(f"  n = {g1}")
print(f"  magic = {T5['magic_in_layer']}  data = {T5['data_in_layer']}")
print(f"  7 嘅位置: 第 {T5['position_of_7']['index']}/{T5['position_of_7']['total']} 個; 第一 Lucas 質數 = {T5['position_of_7']['first_Lucas_prime']}")
print()
print("輸出: data/32_column_isomorph_contact.json")