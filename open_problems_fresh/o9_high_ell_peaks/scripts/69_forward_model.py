#!/usr/bin/env python3
"""
O9-D10: Forward-model — Planck 峰捲入 ACT bin 測試
====================================================
問題: ACT bin 寬 50 係咪足以吞併 m=4 (1013) 弱峰?

方法: 用 ACT DR6 window function, 將 Planck 形狀捲積到 ACT bins,
      睇 998.5/1048.5/1098.5 會唔會變成 ACT 觀測嘅形狀
"""
import numpy as np
from astropy.io import fits
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
print("="*78)
print("O9-D10: Forward-model 測試")
print("="*78)

# ACT DR6 window function
hdul = fits.open(os.path.join(DATADIR, 'act_dr6_cmb_sacc.fits'))
print("\n1. window HDUs:")
for h in hdul:
    if 'window' in h.name:
        print(f"   {h.name}: shape {h.data.shape}")

# 用 Bandpower window (其中一個)
win_hdu = hdul['window:Bandpower']
print(f"\n   Bandpower window data shape: {win_hdu.data.shape}")
print(f"   columns: {win_hdu.data.dtype.names}")
