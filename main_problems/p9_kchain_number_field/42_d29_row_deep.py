#!/usr/bin/env python3
"""
42_d29_row_deep.py — SYNC pipeline 攻堅 r3: d=29 行終極結構 (2026-10-17)
========================================================================
目標: 閉合 06_blind_test_beat231 §4 三開放項
  ① SYNC→L₇→M 語義 🟡
  ② d=29 opcode 執行 🔴
  ③ d=29 行 15 成員角色 🟡

前兩輪已知:
  d=29 唔係 magic (R5 外 + TEST F); member count = 44−d = 15; 全 gcd1
  s=33 列單點 magic = m7 anchor; i 行冇特殊; s=33 beat 冇光譜
  (2,31) = s=33 × d=29 唯一交叉 = i=2 SYNC 家族

今輪 (d=29 行自身終極描寫):
  T1 15 成員完整表: (i,j,s), j 端點, gcd, deg, R5/magic/data/LF
  T2 mirror: d=29 ↔ d=15 (44−29) 行結構對比
  T3 端點分析: j ∈ [30,44] — j=44=N_d 唯一撞?  i ∈ [1,15]
  T4 同 data 格關聯: 15 成員有冇落入/貼近 data 格?
  T5 語義測試: d=29 行 s 值 [31..59] 同 magic 行 s 值域重疊?
  T6 統計檢驗: d=29 行 15 成員喺 943 格中有冇「意外」特殊?
      (任何 d 行都係 44−d 成員 — d=29 冇大細特異)

零 import; 純整數 + mpmath 60dps。
"""
import json
from math import gcd
from collections import Counter

def gc(d):
    return gcd(abs(44 - d), 176)

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

MAGIC = [7, 14, 20, 22, 33]
DATA  = {11, 13, 17, 19, 21, 25}
R5GEN = sorted({m*a for a in (7, 11, 5) for m in (1, 2, 3, 4) if 1 <= m*a <= 43})
DATA_CELLS = {(30,41),(7,20),(8,22),(10,24),(19,33),(1,18),(19,38),(1,22),(8,33)}

def om_deg(d):
    g = gc(d)
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

def is_luc(d): return any(d == m*luc(k) for m in (1,2,3,4) for k in range(2,8))
def is_fib(d): return any(d == m*fib(k) for m in (1,2,3,4) for k in range(2,9))

# ============ T1: d=29 行 15 成員完整 ============
print("=== T1: d=29 行 15 成員完整表 ===")
print(f"{'i':>3} {'j':>3} {'s':>4} {'gcd':>4} {'deg':>4} {'R5':>3} {'L':>3} {'F':>3} {'magic':>5} {'data':>4} notes")
d29 = [(i, i+29) for i in range(1, 16)]
for (i, j) in d29:
    d = j - i
    notes = []
    if (i, j) in DATA_CELLS: notes.append("DATA_CELL!")
    if j == 44: notes.append("j=N_d")
    if i == 2: notes.append("SYNC(i=2)")
    print(f"{i:>3} {j:>3} {i+j:>4} {gc(d):>4} {om_deg(d):>4} "
          f"{'Y' if d in R5GEN else 'N':>3} {str(is_luc(d))[0]:>3} {str(is_fib(d))[0]:>3} "
          f"{'Y' if d in MAGIC else 'N':>5} {'Y' if d in DATA else 'N':>4} {' '.join(notes)}")

# ============ T2: mirror d=29 ↔ d=15 ============
print()
print("=== T2: mirror d=29 ↔ d=15 (44−29) ===")
for d in [29, 15]:
    m = [(i, i+d) for i in range(1, 44-d+1)]
    print(f"  d={d:>2} (mirror {44-d:>2}): {len(m)} 成員  s∈[{m[0][0]+m[0][1]},{m[-1][0]+m[-1][1]}]  gcd={gc(d)}")

# ============ T3: 端點 ============
print()
print("=== T3: d=29 端點分析 ===")
js = sorted(set(j for (i, j) in d29))
print(f"  j 端點 = {js} ({len(js)} 個, 連續 30..44)")
print(f"  j=44 (N_d) 出現? {(15,44) in d29} — 最後成員 (15,44)")
print(f"  i 端點 = [1..15] — i=1..15 小型連")
is_small = all(i <= 15 for (i, _) in d29)
print(f"  i 全 ≤ 15 (細 i 區) = {is_small}")

# ============ T4: 同 data 格關聯 ============
print()
print("=== T4: d=29 行 vs data 格 ===")
print(f"  DATA_CELLS = {sorted(DATA_CELLS)}")
dc_29 = [(i, j) for (i, j) in DATA_CELLS if abs(j-i) == 29]
print(f"  d=29 data 格: {dc_29 if dc_29 else '冇'}")
near = []
for (i, j) in d29:
    for (a, b) in DATA_CELLS:
        if abs(i-a) + abs(j-b) == 2 or abs(i-a) + abs(j-b) == 1:
            near.append(((i, j), (a, b)))
print(f"  貼近 (曼哈頓距離 ≤2): {near if near else '冇'}")

# ============ T5: s 值域同 magic 重疊 ============
print()
print("=== T5: d=29 行 s 值 vs magic 行 s 值域 ===")
s29 = set(i + (i+29) for i in range(1, 16))
print(f"  d=29 s = {sorted(s29)}")
for d in MAGIC:
    sm = set(i + (i+d) for i in range(1, 44-d+1))
    inter = sorted(s29 & sm)
    print(f"  d={d:>2} s∈[{min(sm)},{max(sm)}]  同 d=29 交集 = {inter if inter else '∅'}")

# ============ T6: 統計位置 ============
print()
print("=== T6: d=29 行嘅「普通性」檢查 ===")
print("  全部 43 行 member count = 44−d — d=29 嘅 15 成員係普通 (mid-size)")
print("  落 data/magic 格機率: 943 格 (i<j), d=29 行 15 格")
print(f"  magic 格總數 = {sum(44-d for d in MAGIC)}")
print(f"  data 格總數 = {len(DATA_CELLS)}")
print(f"  d=29 行撞 magic/data: {sum(1 for (i,j) in d29 if (abs(j-i) in MAGIC))} magic + {sum(1 for (i,j) in d29 if (i,j) in DATA_CELLS)} data")

res = {
    "test": "42_d29_row_deep",
    "d29_members": [{"i": i, "j": j, "s": i+j} for (i, j) in d29],
    "mirror": {"29": 15, "15_members": 44-15},
    "j_endpoints": js, "i_small": is_small,
    "data_cell_d29": dc_29,
    "s_overlap": {str(d): sorted(set(i+(i+d) for i in range(1,44-d+1)) & s29) for d in MAGIC},
}
with open("data/42_d29_row_deep.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
print()
print("輸出: data/42_d29_row_deep.json")