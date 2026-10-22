#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/06_null_control.py — (21,24)@176 + 1/640 候選嘅 null-control
問題: 176-L 掃描 (3828 對) 對 m_W/m_Z 有 (21,24) 命中 0.0007%; rational 1/640
命中 0.0002% — 係真結構定密度假象?
Null: 對隨機 target 做同一掃描, 睇 best-hit 分佈。
"""
import mpmath as mp
import random
mp.mp.dps = 60
random.seed(20260908)

def sinp176(n): return mp.sin(n*mp.pi/176)
def sinp88(n): return mp.sin(n*mp.pi/88)

target = mp.mpf('80.369')/mp.mpf('91.1876')

# 176-L 全對表
pairs176 = [(a, b) for a in range(1, 89) for b in range(1, 89) if a != b]
rat176 = [(sinp176(a)/sinp176(b), a, b) for a, b in pairs176]
# 88-L 全對表
pairs88 = [(a, b) for a in range(1, 45) for b in range(1, 45) if a != b]
rat88 = [(sinp88(a)/sinp88(b), a, b) for a, b in pairs88]

def best_dev(ratios, t):
    best = None
    for r, a, b in ratios:
        d = abs(r/t - 1)
        if best is None or d < best[0]:
            best = (d, a, b)
    return best

# 實測
b176 = best_dev(rat176, target)
b88 = best_dev(rat88, target)
print("實測 target = 0.8813589")
print("  176-L best: (%d,%d) dev = %.5f%%" % (b176[1], b176[2], 100*b176[0]))
print("   88-L best: (%d,%d) dev = %.5f%%" % (b88[1], b88[2], 100*b88[0]))

# Null: 隨機 target 分佈 (target ∈ [0.85, 0.92], 同區域)
N = 200
null176 = []
null88 = []
for _ in range(N):
    t = mp.mpf('0.85') + mp.mpf(str(random.random()))*mp.mpf('0.07')
    null176.append(best_dev(rat176, t)[0])
    null88.append(best_dev(rat88, t)[0])

null176.sort()
null88.sort()
p176 = sum(1 for d in null176 if d < b176[0])/N
p88 = sum(1 for d in null88 if d < b88[0])/N
print()
print("Null-control (%d random targets in [0.85,0.92]):" % N)
print("  176-L: median best %.5f%%, p(best < 實測 %.5f%%) = %.3f"
      % (100*null176[N//2], 100*b176[0], p176))
print("   88-L: median best %.5f%%, p(best < 實測 %.5f%%) = %.3f"
      % (100*null88[N//2], 100*b88[0], p88))

# rational 1/640 null: 隨機 target 殘差倒數近整數概率
resid = b176[0]  # 用 176-L 實測? 唔係 — rational 用 IDCM 殘差
resid_idcm = abs(sinp88(30)/sinp88(41)/target - 1)
inv = 1/resid_idcm
print()
print("rational 候選: IDCM 殘差 %+.7f, 倒數 = %.3f (近 640 = 128×5 = α⁻¹(M_Z)×F₅)"
      % (resid_idcm, inv))
# null: 隨機殘差 r ∈ [0.0005, 0.005] 嘅 1/r 落入整數 ±0.15% 概率
M = 500
hits = 0
for _ in range(M):
    r = mp.mpf(str(random.uniform(0.0005, 0.005)))
    ir = 1/r
    n = mp.floor(ir + mp.mpf('0.5'))
    if n > 0 and abs(ir - n)/n < 0.0015:
        hits += 1
print("  null: 隨機殘差 (0.0005~0.005) 倒數近整數 (rel<0.15%%) 概率 = %.3f" % (hits/M))
