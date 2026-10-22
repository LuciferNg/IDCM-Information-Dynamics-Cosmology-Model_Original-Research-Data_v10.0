#!/usr/bin/env python3
"""
O9-D4: ACT DR4 極化峰位 vs IDCM π/2 相移預言
=================================================
ACT DR4 spectra:
0 = TT: 峰 550/850/1150/1350
2 = TE: 峰 400/700/950/1200 (極化峰)
4 = EE: 峰 750/1050/1350/1650

IDCM 預言: 極化峰 = (TT_m + TT_{m+1})/2 (π/2 相移)
TT 峰 (Planck): 220/537/815/1013/1121/1337/1400
→ 極化峰預言:
  P₁ = (220+537)/2 = 378
  P₂ = (537+815)/2 = 676
  P₃ = (815+1013)/2 = 914
  P₄ = (1013+1121)/2 = 1067
  P₅ = (1121+1337)/2 = 1229
  P₆ = (1337+1400)/2 = 1369
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
PYDIR = os.path.join(DATADIR, 'pyactlike', 'pyactlike', 'data')

print("="*80)
print("O9-D4: ACT DR4 極化峰 vs IDCM 預言")
print("="*80)

binning = np.loadtxt(os.path.join(PYDIR, 'Binning.dat'))
l_center = binning[:,2]
cl = np.loadtxt(os.path.join(PYDIR, 'cl_cmb_ap.dat'))
n_bins = len(binning)

TT = cl[0:n_bins, 1]
TE = cl[2*n_bins:3*n_bins, 1]
EE = cl[4*n_bins:5*n_bins, 1]

D_TT = TT * l_center*(l_center+1)/(2*np.pi)
D_TE = TE * l_center*(l_center+1)/(2*np.pi)
D_EE = EE * l_center*(l_center+1)/(2*np.pi)

# IDCM 極化預言
tt_peaks = [220, 537, 815, 1013, 1121, 1337, 1400]
print("\n1. IDCM 極化峰預言 (π/2 相移 = TT 峰中點):")
pred_pol = []
for i in range(len(tt_peaks)-1):
    p = (tt_peaks[i] + tt_peaks[i+1])/2
    pred_pol.append(p)
    print(f"   P{i+1} = ({tt_peaks[i]}+{tt_peaks[i+1]})/2 = {p:.0f}")

# 用修正 m=5 (1121) 版本
tt_peaks2 = [220, 537, 815, 1013, 1121, 1340, 1412]
print("\n2. IDCM 極化預言 (修正 m=5, m=6=1340, m=7=1412):")
pred_pol2 = []
for i in range(len(tt_peaks2)-1):
    p = (tt_peaks2[i] + tt_peaks2[i+1])/2
    pred_pol2.append(p)
    print(f"   P{i+1} = ({tt_peaks2[i]}+{tt_peaks2[i+1]})/2 = {p:.0f}")

# ACT DR4 極化峰
print("\n3. ACT DR4 極化峰 (TE + EE):")
def find_peaks(D, lo, hi):
    out = []
    for j in range(1, len(D)-1):
        if lo < l_center[j] < hi and D[j] > D[j-1] and D[j] > D[j+1] and D[j] > 0:
            out.append((l_center[j], D[j]))
    return out

te_peaks = find_peaks(D_TE, 300, 1600)
ee_peaks = find_peaks(D_EE, 300, 1600)
print("   TE 峰:")
for l, v in te_peaks:
    print(f"      ℓ={l:.0f}  D={v:.2f}")
print("   EE 峰:")
for l, v in ee_peaks:
    print(f"      ℓ={l:.0f}  D={v:.2f}")

# 對比預言
print("\n4. 對比 (ACT 峰 vs IDCM 預言):")
print(f"   {'預言':>6} {'TE':>6} {'EE':>6} {'TE dev':>8} {'EE dev':>8}")
for i, p in enumerate(pred_pol2):
    # 最近 TE/EE 峰
    te_l = min([l for l, v in te_peaks], key=lambda x: abs(x-p)) if te_peaks else None
    ee_l = min([l for l, v in ee_peaks], key=lambda x: abs(x-p)) if ee_peaks else None
    if te_l:
        te_dev = (te_l - p)/p*100
    else:
        te_dev = None
    if ee_l:
        ee_dev = (ee_l - p)/p*100
    else:
        ee_dev = None
    te_s = f"{te_l:.0f} ({te_dev:+.1f}%)" if te_l else "—"
    ee_s = f"{ee_l:.0f} ({ee_dev:+.1f}%)" if ee_l else "—"
    print(f"   {p:>6.0f} {te_s:>12} {ee_s:>12}")
