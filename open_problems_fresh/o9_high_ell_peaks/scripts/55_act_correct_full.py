#!/usr/bin/env python3
"""
O9-D11: ACT DR4 正確解析 — 完整峰位 + IDCM 對比
==================================================
正確結構:
deep: TT(40, 600-4125) TE(45, 350-4125) EE(45, 350-4125)
wide: TT(40) TE(45) EE(45)

TT deep 峰: 800.5/1100.5/1400.5
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
PYDIR = os.path.join(DATADIR, 'pyactlike', 'pyactlike', 'data')

print("="*80)
print("O9-D11: ACT DR4 正確完整分析")
print("="*80)

cl = np.loadtxt(os.path.join(PYDIR, 'cl_cmb_ap.dat'))
bval = cl[:, 0]; X = cl[:, 1]; Xerr = cl[:, 2]
nbintt, nbinte, nbinee, nbinw = 40, 45, 45, 130

def D_from(bval_arr, X_arr):
    return X_arr * bval_arr*(bval_arr+1)/(2*np.pi)

tt_d = D_from(bval[0:nbintt], X[0:nbintt])
te_d = D_from(bval[nbintt:nbintt+nbinte], X[nbintt:nbintt+nbinte])
ee_d = D_from(bval[nbintt+nbinte:nbintt+nbinte+nbinee], X[nbintt+nbinte:nbintt+nbinte+nbinee])
tt_w = D_from(bval[nbinw:nbinw+nbintt], X[nbinw:nbinw+nbintt])
te_w = D_from(bval[nbinw+nbintt:nbinw+nbintt+nbinte], X[nbinw+nbintt:nbinw+nbintt+nbinte])
ee_w = D_from(bval[nbinw+nbintt+nbinte:nbinw+nbintt+nbinte+nbinee], X[nbinw+nbintt+nbinte:nbinw+nbintt+nbinte+nbinee])

bval_tt = bval[0:nbintt]
bval_te = bval[nbintt:nbintt+nbinte]
bval_ee = bval[nbintt+nbinte:nbintt+nbinte+nbinee]

def find_peaks(b, D, lo, hi, thr=0):
    out = []
    for j in range(1, len(D)-1):
        if lo < b[j] < hi and D[j] > D[j-1] and D[j] > D[j+1] and D[j] > thr:
            out.append((b[j], D[j]))
    return out

print("\n1. ACT DR4 deep 峰:")
tt_p = find_peaks(bval_tt, tt_d, 300, 1600, 100)
te_p = find_peaks(bval_te, te_d, 300, 1600, 0)
ee_p = find_peaks(bval_ee, ee_d, 300, 1600, 0)
print("   TT deep:")
for l, v in tt_p: print(f"      ★ ℓ={l:.1f}  D={v:.2f}")
print("   TE deep:")
for l, v in te_p: print(f"      ★ ℓ={l:.1f}  D={v:.2f}")
print("   EE deep:")
for l, v in ee_p: print(f"      ★ ℓ={l:.1f}  D={v:.2f}")

print("\n2. wide 峰:")
tt_pw = find_peaks(bval[nbinw:nbinw+nbintt], tt_w, 300, 1600, 100)
print("   TT wide:")
for l, v in tt_pw: print(f"      ★ ℓ={l:.1f}  D={v:.2f}")

print("\n3. TT deep vs IDCM:")
idcm = {1: 220, 2: 537, 3: 810, 4: 1014, 5: 1121, 6: 1340, 7: 1412}
# deep TT 峰 800.5/1100.5/1400.5 → m=3, m=5, m=7?
for l, v in tt_p:
    # 最近 IDCM
    m = min(idcm, key=lambda x: abs(idcm[x]-l))
    dev = (l - idcm[m])/idcm[m]*100
    print(f"   ℓ={l:.1f} (D={v:.1f}) vs IDCM m={m} ({idcm[m]}) → dev={dev:+.1f}%")

print("\n4. TE/EE deep vs IDCM 極化預言:")
tt = [220, 537, 815, 1013, 1121, 1340, 1412]
pol_pred = [(tt[i]+tt[i+1])/2 for i in range(len(tt)-1)]
print(f"   極化預言: {[round(p) for p in pol_pred]}")
print("   TE:")
for l, v in te_p[:5]:
    p = min(pol_pred, key=lambda x: abs(x-l))
    dev = (l-p)/p*100
    print(f"      ℓ={l:.1f} vs {p:.0f} → dev={dev:+.1f}%")
print("   EE:")
for l, v in ee_p[:5]:
    p = min(pol_pred, key=lambda x: abs(x-l))
    dev = (l-p)/p*100
    print(f"      ℓ={l:.1f} vs {p:.0f} → dev={dev:+.1f}%")
