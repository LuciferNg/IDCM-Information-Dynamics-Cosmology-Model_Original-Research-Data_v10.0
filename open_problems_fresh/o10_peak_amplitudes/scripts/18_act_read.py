#!/usr/bin/env python3
"""
O10 18: ACT DR6 sacc 讀取 + P₄ 交叉驗證
========================================
ACT DR6 CMB sacc file:
  HDU: data:cl_00 = TT bandpowers
  HDU: window:Bandpower = bin windows
"""
import numpy as np, os, json
from astropy.io import fits

path = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "act_dr6_cmb_sacc.fits")
hdul = fits.open(path)

# ============ 讀 TT bandpowers ============
tt = hdul['data:cl_00'].data
print("TT bandpowers columns:", tt.names)
print("行數:", len(tt))
for col in tt.names:
    print(f"  {col}: {tt[col][:5]}")

# 讀 tracer (bin centers?)
tracer = hdul['tracer:Misc'].data
print("\ntracer columns:", tracer.names)
for col in tracer.names:
    print(f"  {col}: {tracer[col][:5]}")
