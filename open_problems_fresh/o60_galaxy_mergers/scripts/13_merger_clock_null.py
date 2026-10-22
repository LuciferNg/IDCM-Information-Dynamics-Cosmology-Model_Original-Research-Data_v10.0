#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O60d 合併時鐘 — 過度擬合 Null Test
=====================================
問題: 4 事件 × 44 模式 = 176 組合, 揀 4 個最佳匹配 — 係咪巧合?

方法:
1. 隨機 4 個「假事件」時間 (均勻分佈 5-15 Gyr), 跑同一最佳匹配
2. 比較真實事件嘅平均偏差 vs 隨機事件
3. 如果真實偏差明顯細過隨機 → 有結構; 否則 → 巧合

另外: 檢查「結構意義」— n=7, 8, 15, 6 有冇 Fibonacci/Lucas 意義
"""
import numpy as np
import math

T_sync = 84.6349
rng = np.random.default_rng(20260824)

def best_match(t):
    """搵最接近嘅模式週期, 返回 (n, T_n, dev%)"""
    best_n, best_dev = None, 1e9
    for n in range(1, 45):
        T_n = T_sync * math.sin(math.pi/88) / math.sin(math.pi*n/88)
        dev = abs(T_n - t) / t * 100
        if dev < best_dev:
            best_dev = dev
            best_n = n
    return best_n, best_dev

events = {"LKH": 12.3, "GSE": 10.5, "Sgr": 6.0, "t_iso": 14.48}
real_devs = [best_match(t)[1] for t in events.values()]
real_mean = np.mean(real_devs)
print("=" * 72)
print("O60d: 合併時鐘 Null Test")
print("=" * 72)
print(f"真實事件: {real_devs}")
print(f"真實平均偏差: {real_mean:.2f}%")

# Null: 隨機 4 個事件 (均勻 5-16 Gyr)
N = 100000
null_means = []
null_best = []
for i in range(N):
    ts = rng.uniform(5, 16, 4)
    devs = [best_match(t)[1] for t in ts]
    null_means.append(np.mean(devs))
    null_best.append(min(devs))

null_means = np.array(null_means)
null_best = np.array(null_best)
print(f"\nNull 分佈 (100,000 隨機 4 事件):")
print(f"  平均偏差 mean = {null_means.mean():.2f}%, std = {null_means.std():.2f}%")
print(f"  真實平均偏差 = {real_mean:.2f}% → percentile = {(null_means < real_mean).mean()*100:.2f}%")
print(f"  → 真實優於 {(1-(null_means < real_mean).mean())*100:.2f}% 隨機案例")

# 單事件比較
print(f"\n單事件: 真實 vs null 最佳:")
for name, t, dev in zip(events.keys(), events.values(), real_devs):
    pct = (null_best < dev).mean() * 100
    print(f"  {name}: dev={dev:.2f}%, null 最佳分佈中優於 {pct:.2f}%")

# 結構意義檢查
print(f"""
結構意義檢查:
  n=7: L₄=7, DM 模式 (m₇=13.8MeV) — 強結構
  n=8: F₆=8 — Fibonacci
  n=15: 7+8=15 (和頻!) — O54 和頻對偶
  n=6: F₅+1=6 — 弱
  4 個中 3 個有強結構意義 (7, 8, 15) 
  隨機 4 個模式 (1-44) 全部有 Fibonacci/Lucas 意義嘅機率?
  Fibonacci/Lucas 數 (1-44): 1,2,3,4,5,7,8,11,13,18,21,29,34 (13 個)
  P(單個係 Fib/Lucas) = 13/44 = 0.295
  P(4 個中 ≥3 個) = C(4,3)·0.295³·0.705 + 0.295⁴ = 4×0.0257×0.705 + 0.0076 = 0.0725+0.0076 = 0.080
  → 8% — 邊際 (唔算強, 但唔係冇)
""")
