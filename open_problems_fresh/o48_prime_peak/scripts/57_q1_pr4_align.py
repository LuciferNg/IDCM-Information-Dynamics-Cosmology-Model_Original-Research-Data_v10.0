#!/usr/bin/env python3
"""
O48 Q1.39: PR4 ℓ 軸對齊檢查 — cross-correlate vs Plik
================================================================
56 script 發現: 峰 +29..+38 / 谷 -43..-61 / mod-9 全 ≡7
(−16 ≡ +2 mod 9) → 懷疑 PR4 ℓ 軸 offset ~+2..+3 vs Plik。

方法: detrend residual cross-correlation 掃 shift, 搵最佳對齊。
"""
import math, sys
import numpy as np
import astropy.io.fits as fits

# ---------- 載入 ----------
PR4 = '/home/wsl/.hermes/cache/scratch/planck_2020/hillipop/data/dl_PR4_v4.2_143Ax143B.fits'
h = fits.open(PR4)
D4 = h[1].data[0].copy() * 1e12
ell4 = np.arange(len(D4))
base='/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
o9_path=f'{base}/open_problems_fresh/o163_dm_identity/data/planck_tt.txt'
o9=[]
for line in open(o9_path):
    p=line.split()
    if len(p)>=2:
        try: o9.append((float(p[0]), float(p[1])))
        except: pass
ell3 = np.array([e for e,_ in o9]); C3 = np.array([d for _,d in o9])
D3 = C3*ell3*(ell3+1)/(2*math.pi)

def bin9(ells, D, lo=30, hi=2492):
    cs, ds = [], []
    for start in range(lo, hi, 9):
        m = (ells>=start)&(ells<start+9)
        if m.sum() >= 4:
            cs.append(start+4); ds.append(np.mean(D[m]))
    return np.array(cs), np.array(ds)

e4b, D4b = bin9(ell4, D4)

def detrend(ells, D, order=4, lo=100, hi=2500):
    m = (ells>lo)&(ells<hi)&(D>0)
    e, d = ells[m], D[m]
    c = np.polyfit(e, np.log(d), order)
    env = np.exp(np.polyval(c, e))
    return e, d/env

e3, r3 = detrend(ell3, D3)
e4, r4 = detrend(e4b, D4b)

# 統一 grid
lo, hi = 200, 1500
g3 = np.arange(lo, hi)
r3i = np.interp(g3, e3, r3)
# PR4 用不同 shift: ell4_shifted = ell4 - s
best = None
for s in range(-60, 61):
    g4 = np.arange(lo, hi) + s   # 如果 PR4 真 ℓ = idx + s'
    # 檢查 s 移動後 PR4 喺 grid g3 嘅相關
    r4i = np.interp(g3, e4 - s, r4)   # 將 PR4 曲線向左移 s? (e4-s)
    # 其實 e4 係 bin center (start+4); 測試 PR4 真中心 = e4 + delta
    r4d = np.interp(g3, e4 + s, r4)
    finite = np.isfinite(r4i) & np.isfinite(r4d) & np.isfinite(r3i)
    c = np.corrcoef(r3i[finite], r4d[finite])[0,1]
    if best is None or c > best[1]:
        best = (s, c)
print(f"最佳對齊: PR4 ℓ 軸 +{best[0]} → 相關 {best[1]:+.4f}")
print("(s>0 代表 PR4 峰位比 Plik 高 s, 係 beam/calibration 平移)")
print()
delta = best[0]
e4a = e4 - delta   # 對齊後 PR4 ℓ

# ---------- 對齊後重測峰位 ----------
print("="*72)
print("對齊後 (PR4 ℓ) 峰位重測")
print("="*72)
ref_peaks = [221, 527, 815, 1121, 1409]
found=[]
for p in ref_peaks:
    m=(e4a>p-40)&(e4a<p+40)
    if m.sum()==0: found.append(None); print(f"  {p}: 冇數據"); continue
    i=np.argmax(r4[m])
    found.append(e4a[m][i])
    print(f"  預測 {p:5d}: PR4 峰 {e4a[m][i]:5.0f} (Δ={e4a[m][i]-p:+.0f})")
print()
ref_valleys=[437,716,1040,1346]
vs=[]
for i,v in enumerate(ref_valleys):
    p_lo,p_hi=ref_peaks[i],ref_peaks[i+1]
    m=(e4a>p_lo+15)&(e4a<p_hi-15)
    if m.sum()==0: vs.append(None); print(f"  {v}: 冇數據"); continue
    j=np.argmin(r4[m])
    vs.append(e4a[m][j])
    print(f"  谷 {v:5d}: PR4 谷 {e4a[m][j]:5.0f} (Δ={e4a[m][j]-v:+.0f}, mod9={int(round(e4a[m][j]))%9})")
print()
vm=[int(round(x))%9 for x in vs if x is not None]
print(f"  對齊後谷 mod-9: {vm} (預測全 ≡5)")
print()
print(f"delta = {delta:+d} (PR4 峰位比 Plik 高 {delta})")
print("注意: 若 delta 係 constant, 即 PR4-NPIPE ℓ calibration 同 Plik 有系統偏移")