#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/34_domain_debug_hits.py — ★★ 重審 T30: 88 域全對 vs 176 域全對真實命中
scripts/32 census 結論: 10/10 目標最佳域=176 (spin 假說否證)
scripts/33 null control 發現: 176奇奇(1/4 空間) median 0.29x → 176 優勢
可能只係搜索空間效應。
本 script: 列出每個目標 88/176 域全對嘅 BEST 命中對 + dev, 睇有冇算子身份
"""
import math

def best_hits(n, target, k=5):
    """掃 n 域全對, 返回 top-k [(dev, a, b, r)]"""
    hits = []
    tb = float(target)
    sins = [math.sin(i*math.pi/(2*n)) for i in range(n+1)]
    for a in range(1, n+1):
        sa = sins[a]
        for b in range(1, n+1):
            if a == b: continue
            r = sa/sins[b]
            d = min(abs(r/tb-1), abs(tb/r-1))
            hits.append((d, a, b, r))
    hits.sort(key=lambda x: x[0])
    return hits[:k]

REAL = [
    ("W/Z", 0.88135354, 1), ("H/W", 1.55843672, 0), ("τ/b", 0.42508612, 0.5),
    ("t/b", 41.3301435, 0.5), ("s/d", 20.0, 0.5), ("c/s", 13.59743, 0.5),
    ("u/d", 0.4625257, 0.5), ("H/Z", 1.3735082, 0), ("H/t", 0.7250005, 0),
    ("H/b", 29.964115, 0),
]

print("%-5s %-4s | %-26s | %-26s" % ("tgt", "spin", "88域 top1", "176域 top1"))
print("-"*90)
for name, val, spin in REAL:
    hit88 = best_hits(88, val, 1)[0]
    hit176 = best_hits(176, val, 1)[0]
    d88, a88, b88, r88 = hit88
    d176, a176, b176, r176 = hit176
    print("%-5s %-4s | (%3d,%3d) dev %.2e  r=%.6f | (%3d,%3d) dev %.2e  r=%.6f | %s%s" % (
        name, spin, a88, b88, d88, r88, a176, b176, d176, r176,
        "SAME88" if (a176 % 2 == 0 and b176 % 2 == 0 and a176//2 == a88 and b176//2 == b88) else "new",
        ""))
print()

print("="*72)
print("★ 特別檢查: 已命名命中對係咪仲係「最佳」?")
print("="*72)
known = {"W/Z": (21, 24, 176), "τ/b": (13, 32, 176), "t/b": (46, 1, 176),
         "H/W": (86, 39, 176), "s/d": (44, 2, 176)}
for name, (a, b, n) in known.items():
    val = [v for nm, v, sp in REAL if nm == name][0]
    target = float(val)
    sins = [math.sin(i*math.pi/(2*n)) for i in range(n+1)]
    d = min(abs((sins[a]/sins[b])/target-1), abs(target/(sins[a]/sins[b])-1))
    hit1 = best_hits(n, target, 1)[0]
    print("%-5s 已知 (%3d,%3d)@%d dev=%.2e | 該域 top1 (%3d,%3d) dev=%.2e (%s)" % (
        name, a, b, n, d, hit1[1], hit1[2], hit1[0],
        "仍然第一" if (hit1[1], hit1[2]) == (a, b) else ("被超越, 差 %.1fx" % (d/hit1[0]))))