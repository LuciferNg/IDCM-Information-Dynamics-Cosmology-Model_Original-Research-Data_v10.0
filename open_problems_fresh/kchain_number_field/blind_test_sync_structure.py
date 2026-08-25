#!/usr/bin/env python3
"""
盲測批量 v4: SYNC 家族 (i=2) 結構分析 — 佢係咪「貫穿所有 magic rows」嘅主幹線?
===============================================================================
發現: i=2 行 (SYNC 家族, s−d=4=B) 嘅成員, d 由 1→42 連續,
     穿過全部 5 個 magic rows: d=7 (m7), d=14 (GEN), d=20 (T), d=22 (half), d=33 (K_tree)
→ 問題: SYNC 家族係咪唯一一條「貫穿全 magic」嘅行? 其他 i 值呢?
"""
from math import pi, sin
from collections import Counter

Nd = 44
w = lambda n: 2*sin(pi*n/88)
pairs = [(i,j) for i in range(1,Nd) for j in range(i+1,Nd+1)]
magic = {7, 14, 20, 22, 33}

print("="*70)
print("分析: 每條 i 行 (固定細端) 穿過幾多個 magic rows?")
print("="*70)
print(f"{'i':>3} {'成員數':>5} {'穿過 magic':>10} {'magic d 值':>30} {'連續?':>6}")
results = []
for i in range(1, 44):
    members = [(i,j) for (i,j) in pairs if i == j and False]  # placeholder
    members = [(ii,jj) for (ii,jj) in pairs if ii == i]
    ds = set(j-i for (ii,j) in members)
    hit = sorted(magic & ds)
    cont = "✅" if len(hit) == 5 else ""
    results.append((i, len(members), len(hit), hit, cont))
    print(f"{i:>3} {len(members):>5} {len(hit):>10} {str(hit):>30} {cont}")

print("\n" + "="*70)
print("同樣分析: 每條 j 行 (固定大端) 穿過幾多個 magic rows?")
print("="*70)
print(f"{'j':>3} {'成員數':>5} {'穿過 magic':>10} {'magic d 值':>30}")
for j in range(2, 45):
    members = [(ii,jj) for (ii,jj) in pairs if jj == j]
    ds = set(jj-ii for (ii,jj) in members)
    hit = sorted(magic & ds)
    print(f"{j:>3} {len(members):>5} {len(hit):>10} {str(hit):>30}")

# 總結: 有幾多條 i 行穿過全部 5 個 magic?
full = [r for r in results if r[2] == 5]
print(f"\n穿過全部 5 個 magic rows 嘅 i 行: {[r[0] for r in full]}")
