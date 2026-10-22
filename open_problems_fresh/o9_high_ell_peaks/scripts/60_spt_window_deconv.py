#!/usr/bin/env python3
"""
O9-D: SPT-3G Window Function 去捲積 — m=4 (1013) 弱峰確認
============================================================
目標: 用 SPT-3G TT 150x150 window function 反捲積 bandpowers,
      重構真實 D_ℓ, 確認 m=4 (1013) 係真峰定 binning artifact.

方法:
1. SPT-3G window: 4094 行 × 52 bins (ℓ=2..4095)
2. SPT-3G bandpower: 52 bins TT 150x150
3. 去捲積: 用 Richardson-Lucy 或 forward-model
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
print("="*78)
print("O9-D: SPT-3G window 去捲積")
print("="*78)

# 讀 window function
win = np.loadtxt(os.path.join(DATADIR, 'spt_tt150_windows.txt'))
ell_win = win[:, 0].astype(int)
W = win[:, 1:]  # 4094 × 52
print(f"\n1. Window: {W.shape[0]} ℓ × {W.shape[1]} bins")
print(f"   ℓ 範圍: {ell_win[0]}-{ell_win[-1]}")

# 讀 SPT-3G bandpower (TT 150x150 = 前 52 行? 需確認)
# SPT3G_D1_TnE_bdp.txt: 21 spectra × 52-72 bins, TT150x150 係其中一段
bdp = np.loadtxt(os.path.join(DATADIR, 'spt3g_tne_bdp.txt'))
print(f"\n2. SPT bandpower 總行數: {len(bdp)}")

# 需確認 TT 150x150 位置 — 睇 window 結構
# 用 window 每 bin 嘅 mean ℓ (加權) 推斷 bandpower ℓ 中心
bin_l = W @ np.arange(len(ell_win))  # 近似 bin 中心
bin_l = bin_l / W.sum(axis=0)
print(f"   bin 中心 (推斷): {[round(x) for x in bin_l[:10]]}")
print(f"   bin 中心 (尾): {[round(x) for x in bin_l[-5:]]}")

# SPT 之前發現 TT 150x150 有 52 bins, 峰位 524/824/1124/1424
# bandpower 順序: 6TT(52 each) + 9TE(72) + 6EE(72) = 1392
# TT spectra: 90x90, 90x150, 150x90?, 150x150...
# 需要確認 TT 150x150 位置
print(f"\n3. SPT bandpower 順序猜測:")
# 6 TT spectra × 52
print(f"   TT 150x150 可能係 index 3 (第 4 個 TT)")
