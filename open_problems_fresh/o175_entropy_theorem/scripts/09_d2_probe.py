#!/usr/bin/env python3
"""
O175 遺留攻堅 D2: T_write = 192 μK 觀測對應探測 (用戶指示: 在 O175 內推)
=============================================================
Claim: T_write = γ = 4N_d + B^2 = 192 μK 應有 CMB 觀測特徵;
   ratio 192/134.2 = 1.4307 vs √2 (dev 1.2% — 唔係精確 √2)
探測: A5 60 節點集 (現有數據) — 有冇 |δT| ~ 192 μK?
"""
import numpy as np
import mpmath as mp
from pathlib import Path
mp.mp.dps = 30
BASE = Path(__file__).resolve().parent.parent.parent

rows = []
with open(str(BASE/"cmb_cold_spot/data/smica_smoothed.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split(); rows.append((int(p[0]), float(p[2])))
Ts = np.array([r[1] for r in rows])
dT = np.abs(Ts - Ts.mean())

r = mp.mpf(192)/mp.mpf('134.2')
print(f"192/134.2 = {mp.nstr(r,6)}  vs  √2 = {mp.nstr(mp.sqrt(2),6)}  dev = {mp.nstr(abs(r/mp.sqrt(2)-1)*100,3)}%")
print(f"A5 60 節點: max|dT| = {dT.max():.1f} μK; n(|dT|>150) = {(dT>150).sum()}; n(>180) = {(dT>180).sum()}; n(>192) = {(dT>192).sum()}")
print("判決: A5 節點集冇 192 μK 特徵 (max 132.9) — 192 μK 搜索需全圖 wavelet (data-gated)")
print("     192/134.2 = 1.4307 vs √2 dev 1.2% — 「≈√2」係鬆描述, 唔係結構身份")
