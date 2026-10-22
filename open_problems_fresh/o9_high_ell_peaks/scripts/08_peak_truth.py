#!/usr/bin/env python3
"""
O9: 峰位真相 — 內插假峰排查 (誠實核查)
=========================================
發現: bin 中心偵測峰 = 230/518/815/1121/1409/1716
     但 cubic 內插顯示 1014/1338/1401 等峰
問題: cubic 內插 (Runge 現象) 有冇製造假峰?

核查:
1. 唔同內插方法 (linear/cubic/pchip) 峰位對比
2. 對 bin 中心直接做峰偵測 (sigma=0,1,2,3)
3. Planck binned 喺 900-1250 嘅真實形狀 (有冇 1014 峰?)
4. 用 Planck 官方 full-sky 譜 (CAMB 生成) 對比
5. 結論: 邊啲峰係真, 邊啲係內插假峰?
"""
import numpy as np
import math as _m
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

print("="*80)
print("O9: 峰位真相 — 內插假峰排查")
print("="*80)

planck = np.loadtxt(os.path.join(DATADIR, 'planck_tt.txt'))
ell_p = planck[:,0].astype(int); C_p = planck[:,1]
D_bin = C_p * ell_p*(ell_p+1)/(2*np.pi)

from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

# ---------- 1. bin 中心直接峰偵測 (唔內插) ----------
print("\n1. bin 中心直接峰偵測 (原始 bin, 唔內插):")
for sigma in [0, 1, 2, 3]:
    s = D_bin if sigma == 0 else gaussian_filter1d(D_bin, sigma=sigma)
    cand, props = find_peaks(s, distance=3, prominence=3)
    cand = np.array(cand); proms = np.array(props['prominences'])
    keep = (proms > 0.005*s[cand]) & (s[cand] > 50)
    pk = [ell_p[c] for c in cand[keep]]
    print(f"   sigma={sigma}: {pk}")

# ---------- 2. 內插方法對比 ----------
print("\n2. 內插方法 (σ=3 平滑後):")
from scipy.interpolate import interp1d, PchipInterpolator
ell_i = np.arange(30, 2500)
for name, C_int in [("linear", interp1d(ell_p, C_p, kind='linear', fill_value='extrapolate')),
                    ("cubic", interp1d(ell_p, C_p, kind='cubic', fill_value='extrapolate')),
                    ("pchip", PchipInterpolator(ell_p, C_p, extrapolate=True))]:
    D_int = C_int(ell_i) * ell_i*(ell_i+1)/(2*np.pi)
    s3 = gaussian_filter1d(D_int, sigma=3)
    cand, props = find_peaks(s3, distance=30, prominence=10)
    cand = np.array(cand); proms = np.array(props['prominences'])
    keep = (proms > 0.01*s3[cand]) & (s3[cand] > 100)
    pk = [int(ell_i[c]) for c in cand[keep] if 300 < ell_i[c] < 2000]
    print(f"   {name:7s}: {pk}")

# ---------- 3. 900-1250 形狀 (m=4/m=5 區) ----------
print("\n3. 900-1250 區間真實形狀 (無內插):")
print("   用二次插值 (3-point) 局部極大檢查:")
for i in range(1, len(ell_p)-1):
    l = ell_p[i]
    if 900 <= l <= 1250:
        # 3-point 局部極大
        if D_bin[i] > D_bin[i-1] and D_bin[i] > D_bin[i+1]:
            print(f"   ★ 局部極大: ℓ={l}  D={D_bin[i]:.1f}")
# 同時睇上升/下降趨勢
print("\n   趨勢 (900-1250):")
prev_d = None
for i, l in enumerate(ell_p):
    if 900 <= l <= 1250:
        d = D_bin[i]
        trend = "—"
        if prev_d is not None:
            trend = "↑" if d > prev_d else "↓"
        print(f"   ℓ={l:5d}  D={d:8.1f}  {trend}")
        prev_d = d

# ---------- 4. SPT-3G 交叉 (1124 區) ----------
print("\n4. SPT-3G D1 TT 150x150 (高ℓ區, 1124 附近):")
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
print("   SPT-3G 900-1500:")
for i, l in enumerate(bin_centers):
    if 900 <= l <= 1500:
        d = tt150[i]
        trend = "—"
        if i > 0 and i < len(bin_centers)-1:
            trend = "↑" if d > tt150[i-1] else "↓"
        print(f"   ℓ={l:6.0f}  D={d:8.1f}  {trend}")

# ---------- 5. 結論 ----------
print("\n" + "="*80)
print("5. 峰位真相總結")
print("="*80)
print("bin 中心峰: 230/518/815/1121/1409/1716 (sigma=1)")
print("cubic 內插峰: 221/512/557/816/1014/1124/1293/1338/1401/1731")
print("")
print("→ 1014 (cubic) vs 1121 (bin): cubic 喺 950-1121 上升段製造咗假峰")
print("→ 但 m=5 (1124) 同 m=6 (1338/1409?) 需要進一步核實")
