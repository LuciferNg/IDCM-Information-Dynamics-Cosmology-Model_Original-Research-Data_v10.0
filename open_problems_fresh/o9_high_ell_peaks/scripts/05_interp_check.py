#!/usr/bin/env python3
"""
O9: Planck binned 內插驗證 + 峰位真相
=======================================
問題: 之前用 cubic 內插製造咗假峰? 驗證:
1. 直接用 bin 中心 (唔內插) 峰偵測
2. 線性內插 vs cubic 內插對比
3. Planck 2015 官方峰位表 (如果搵到)
4. SPT-3G 原始 bandpowers 直接峰偵測 (唔過度平滑)
"""
import numpy as np
import math as _m
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def idcm_peak(m):
    return 44*(33 - _m.comb(9-m, 2)) + (((m-1)*9) % 25)

print("="*78)
print("O9: 內插驗證 — Planck binned 峰位係咪真?")
print("="*78)

# ---------- 1. 原始 bin 中心峰偵測 (唔內插) ----------
planck = np.loadtxt(os.path.join(DATADIR, 'planck_tt.txt'))
ell_p = planck[:,0].astype(int); C_p = planck[:,1]; err_p = planck[:,2]
# bin 中心直接 D_ℓ
D_bin = C_p * ell_p*(ell_p+1)/(2*np.pi)

from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

print("\n1. 原始 bin 中心 (ℓ={}..{}, n={})".format(ell_p.min(), ell_p.max(), len(ell_p)))
print("   bin 闊度檢查: 頭 10 個 Δℓ =", np.diff(ell_p[:11]))

for sigma in [0, 1, 2, 3]:
    if sigma == 0:
        s = D_bin
    else:
        s = gaussian_filter1d(D_bin, sigma=sigma)
    cand, props = find_peaks(s, distance=3, prominence=5)
    cand = np.array(cand)
    proms = np.array(props['prominences'])
    keep = (proms > 0.01*s[cand]) & (s[cand] > 100)
    pk = [ell_p[c] for c in cand[keep] if 300 < ell_p[c] < 2000]
    print(f"   sigma={sigma}: {pk}")

# ---------- 2. 線性 vs cubic 內插 ----------
from scipy.interpolate import interp1d
print("\n2. 內插方法對比 (σ=3 平滑後峰位):")
ell_i = np.arange(30, 2500)
for kind in ['linear', 'cubic']:
    C_int = interp1d(ell_p, C_p, kind=kind, fill_value='extrapolate')
    D_int = C_int(ell_i) * ell_i*(ell_i+1)/(2*np.pi)
    s3 = gaussian_filter1d(D_int, sigma=3)
    cand, props = find_peaks(s3, distance=30, prominence=10)
    cand = np.array(cand); proms = np.array(props['prominences'])
    keep = (proms > 0.01*s3[cand]) & (s3[cand] > 100)
    pk = [int(ell_i[c]) for c in cand[keep] if 300 < ell_i[c] < 2000]
    print(f"   {kind:7s}: {pk}")

# ---------- 3. 峰位誤差 (bootstrap, 用 bin 中心) ----------
print("\n3. bin 中心峰位 bootstrap 誤差 (100×):")
np.random.seed(42)
s3b = gaussian_filter1d(D_bin, sigma=2)
cand, props = find_peaks(s3b, distance=3, prominence=5)
cand = np.array(cand); proms = np.array(props['prominences'])
keep = (proms > 0.01*s3b[cand]) & (s3b[cand] > 100)
base_pk = [ell_p[c] for c in cand[keep] if 300 < ell_p[c] < 2000]
print(f"   基準峰: {base_pk}")
for bp in base_pk:
    shifts = []
    for _ in range(100):
        C_jit = C_p + np.random.normal(0, 1, len(C_p)) * err_p
        D_jit = C_jit * ell_p*(ell_p+1)/(2*np.pi)
        sj = gaussian_filter1d(D_jit, sigma=2)
        cj, pj = find_peaks(sj, distance=3, prominence=5)
        cj = np.array(cj); pj = np.array(pj['prominences'])
        kj = (pj > 0.01*sj[cj]) & (sj[cj] > 100)
        pks_j = [ell_p[c] for c in cj[kj] if 300 < ell_p[c] < 2000]
        if pks_j:
            d = np.abs(np.array(pks_j) - bp)
            shifts.append(pks_j[np.argmin(d)])
    if shifts:
        print(f"   ℓ={bp}: ±{np.std(shifts):.1f} (n={len(shifts)})")

# ---------- 4. SPT-3G 原始 bandpowers 直接偵測 ----------
print("\n4. SPT-3G D1 TT 150x150 原始 bandpowers:")
bdp = np.loadtxt(os.path.join(DATADIR, 'spt3g_tne_bdp.txt'))
spec_list = [
    ('TT 90x90',52), ('TE 90x90',72), ('EE 90x90',72), ('TT 90x150',52),
    ('TE 90x150',72), ('TE 150x90',72), ('EE 90x150',72), ('TT 90x220',52),
    ('TE 90x220',72), ('TE 220x90',72), ('EE 90x220',72), ('TT 150x150',52),
    ('TE 150x150',72), ('EE 150x150',72), ('TT 150x220',52), ('TE 150x220',72),
    ('TE 220x150',72), ('EE 150x220',72), ('TT 220x220',52), ('TE 220x220',72),
    ('EE 220x220',72),
]
idx = 0
for name, n in spec_list:
    if name == 'TT 150x150':
        tt150 = bdp[idx:idx+n]
        break
    idx += n
win = np.loadtxt(os.path.join(DATADIR, 'spt_tt150_windows.txt'))
ell_w = win[:, 0]; W = win[:, 1:]
bin_centers = np.array([(ell_w * W[:,b]).sum()/W[:,b].sum() for b in range(W.shape[1])])

# 唔平滑, 直接找局部極大 (用 3-point window)
print("   原始 bandpowers 局部極大 (連續 3 bin):")
for i in range(1, len(tt150)-1):
    if tt150[i] > tt150[i-1] and tt150[i] > tt150[i+1]:
        print(f"     ℓ≈{bin_centers[i]:.0f}  D_ℓ={tt150[i]:.1f}")

print("\n   高ℓ區 (1000-1600) 詳細:")
mask = (bin_centers > 900) & (bin_centers < 1700)
for l, d in zip(bin_centers[mask], tt150[mask]):
    marker = ""
    print(f"     ℓ={l:6.0f}  D_ℓ={d:8.1f}")

# ---------- 5. 結論 ----------
print("\n" + "="*78)
print("5. 對比總結")
print("="*78)
