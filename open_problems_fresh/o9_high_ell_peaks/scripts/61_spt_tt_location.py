#!/usr/bin/env python3
"""
O9-D2: 確定 SPT-3G TT 150x150 bandpower 位置
===============================================
bdp = 1392 值 (1D)
結構: 6 TT + 9 TE + 6 EE
TT spectra: 90x90, 90x150, 150x150, 150x220, 220x220, 220x90?
每個 TT 52 bins? 但 6×52=312
9 TE × 72 = 648, 6 EE × 72 = 432 → 312+648+432 = 1392 ✓

TT 150x150 位置: 需揾出 6 個 TT spectra 每個 52 bins 嘅邊界
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
bdp = np.loadtxt(os.path.join(DATADIR, 'spt3g_tne_bdp.txt'))
print(f"bdp 總行數: {len(bdp)}")

# 6 TT spectra, 每 52 bins → TT 區 0..311 (312 rows)
# 每個 TT spectrum 52 rows: spec i 位置 = i*52 .. i*52+51
# 但 bdp 係 1D value, 需要 bin 中心 for each spectrum
# 假設每 spectrum 有自己嘅 bin 中心 (同 bin 數)

# 最簡單: 用峰值判斷邊個 TT spectrum 係 150x150 (應該有 5 峰: 524/824/1124/1424/1724/2024)
print("\n掃描每個候選 TT spectrum 嘅峰:")
for si in range(6):
    start = si*52
    seg = bdp[start:start+52]
    # 揾局部極大
    peaks = []
    for j in range(1,52-1):
        if seg[j] > seg[j-1] and seg[j] > seg[j+1] and seg[j] > 0:
            peaks.append(j)
    print(f"  TT spectrum {si} (rows {start}-{start+51}): 峰喺 bins {peaks[:6]}")
