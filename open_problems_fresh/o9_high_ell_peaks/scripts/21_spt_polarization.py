#!/usr/bin/env python3
"""
O9-A2b: SPT-3G D1 極化 (TE/EE) 峰偵測 + IDCM 相移預言驗證
============================================================
SPT-3G D1 結構: 21 spectra
TT 90x90(52) TE 90x90(72) EE 90x90(72) TT 90x150(52) TE 90x150(72)
TE 150x90(72) EE 90x150(72) TT 90x220(52) TE 90x220(72) TE 220x90(72)
EE 90x220(72) TT 150x150(52) TE 150x150(72) EE 150x150(72) TT 150x220(52)
TE 150x220(72) TE 220x150(72) EE 150x220(72) TT 220x220(52) TE 220x220(72)
EE 220x220(72)
需要 window functions 檢查 TE/EE 嘅 bin 中心
"""
import numpy as np
import math as _m
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
phi = (1 + 5**0.5)/2
F = [0, 1]
for i in range(2, 15): F.append(F[-1]+F[-2])

def idcm_fix(m):
    if m == 5: return 44*(33 - F[6]) + F[8]
    C = _m.comb(9-m, 2) if 9-m >= 2 else 0
    return 44*(33 - C) + (((m-1)*9) % 25)

print("="*80)
print("O9-A2b: SPT-3G D1 極化峰驗證")
print("="*80)

# ---------- 1. SPT-3G windows ----------
print("\n1. SPT-3G D1 windows 文件:")
win = np.loadtxt(os.path.join(DATADIR, 'spt_tt150_windows.txt'))
print(f"   TT150 window: {win.shape[0]} ℓ 行, {win.shape[1]-1} bins")
ell_w = win[:, 0]
W = win[:, 1:]
bin_centers = np.array([(ell_w * W[:,b]).sum()/W[:,b].sum() for b in range(W.shape[1])])
print(f"   TT150 bin 中心: {[f'{l:.0f}' for l in bin_centers[:10]]}...")

# ---------- 2. 讀所有 spectrum ----------
bdp = np.loadtxt(os.path.join(DATADIR, 'spt3g_tne_bdp.txt'))
specs = [
    ('TT 90x90',52), ('TE 90x90',72), ('EE 90x90',72), ('TT 90x150',52),
    ('TE 90x150',72), ('TE 150x90',72), ('EE 90x150',72), ('TT 90x220',52),
    ('TE 90x220',72), ('TE 220x90',72), ('EE 90x220',72), ('TT 150x150',52),
    ('TE 150x150',72), ('EE 150x150',72), ('TT 150x220',52), ('TE 150x220',72),
    ('TE 220x150',72), ('EE 150x220',72), ('TT 220x220',52), ('TE 220x220',72),
    ('EE 220x220',72),
]
data = {}
idx = 0
for name, n in specs:
    data[name] = bdp[idx:idx+n]
    idx += n

# ---------- 3. 高頻譜 (150x150) 峰偵測 ----------
print("\n2. TT/TE/EE 150x150 峰偵測 (bin 中心 + 局部極大):")
from scipy.signal import find_peaks

for name in ['TT 150x150', 'TE 150x150', 'EE 150x150']:
    d = data[name]
    # 局部極大 (直接比較鄰居)
    peaks = []
    for i in range(1, len(d)-1):
        if d[i] > d[i-1] and d[i] > d[i+1] and d[i] > 20:
            peaks.append((bin_centers[i], d[i]))
    print(f"   {name}: {[(f'{l:.0f}', f'{v:.1f}') for l, v in peaks]}")

# ---------- 4. IDCM 預言對比 ----------
print("\n" + "-"*80)
print("3. IDCM TT 預言 vs SPT-3G TT 150x150:")
print("-"*80)
tt150 = data['TT 150x150']
for m in range(1, 8):
    pred = idcm_fix(m)
    j = np.argmin(np.abs(bin_centers - pred))
    dev = (bin_centers[j] - pred)/pred*100
    print(f"   m={m}: IDCM {pred} vs SPT {bin_centers[j]:.0f} (D={tt150[j]:.1f}) dev={dev:+.2f}%")

# ---------- 5. 極化峰相移 ----------
print("\n" + "-"*80)
print("4. 極化峰 vs TT 峰 (π/2 相移):")
print("-"*80)
tt_peaks_150 = []
for i in range(1, len(tt150)-1):
    if tt150[i] > tt150[i-1] and tt150[i] > tt150[i+1] and tt150[i] > 100:
        tt_peaks_150.append(bin_centers[i])

for name in ['EE 150x150', 'TE 150x150']:
    d = data[name]
    peaks = []
    for i in range(1, len(d)-1):
        if abs(d[i]) > abs(d[i-1]) and abs(d[i]) > abs(d[i+1]) and abs(d[i]) > 15:
            peaks.append(bin_centers[i])
    print(f"   {name} 峰: {[f'{l:.0f}' for l in peaks]}")
    print(f"   TT 峰: {[f'{l:.0f}' for l in tt_peaks_150]}")
    # 相移: 極化峰 vs 最近 TT 峰
    for pl in peaks:
        if len(tt_peaks_150):
            j = np.argmin(np.abs(np.array(tt_peaks_150) - pl))
            diff = pl - tt_peaks_150[j]
            print(f"     {name} ℓ={pl:.0f} vs TT {tt_peaks_150[j]:.0f} (Δ={diff:+.0f})")

# ---------- 6. IDCM 極化預言 ----------
print("\n" + "-"*80)
print("5. IDCM 極化峰預言 (TT 峰之間半週期):")
print("-"*80)
tt_pred = {m: idcm_fix(m) for m in range(1, 8)}
for m in range(1, 7):
    mid = (tt_pred[m] + tt_pred[m+1])/2
    print(f"   極化峰 {m} (TT{m}={tt_pred[m]} ↔ TT{m+1}={tt_pred[m+1]}): ℓ ≈ {mid:.0f}")
