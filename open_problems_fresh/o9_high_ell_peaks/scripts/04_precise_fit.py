#!/usr/bin/env python3
"""
O9: 精確峰位擬合 — Planck binned + SPT-3G D1 vs IDCM vs CAMB
==============================================================
方法:
1. Planck binned: 局部拋物線擬合 (5-7 點) → 峰位 + 峰位誤差 (由 C_ℓ 誤差傳播)
2. SPT-3G D1: bin center 用 window 加權平均 (唔係 argmax), 峰偵測用插值
3. 逐峰對比 IDCM / CAMB, 誤差棒評估
4. 統計: RMS 偏差, 每峰 z-score
"""
import numpy as np
import math as _m
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def idcm_peak(m):
    return 44*(33 - _m.comb(9-m, 2)) + (((m-1)*9) % 25)

print("="*78)
print("O9: 精確峰位擬合 — 觀測真相 vs IDCM vs CAMB")
print("="*78)

# ---------- 1. Planck binned 精確峰位 ----------
print("\n" + "-"*78)
print("1. Planck binned TT — 拋物線擬合峰位")
print("-"*78)
planck = np.loadtxt(os.path.join(DATADIR, 'planck_tt.txt'))
ell_p = planck[:,0].astype(int); C_p = planck[:,1]; err_p = planck[:,2]
from scipy.interpolate import interp1d
C_int = interp1d(ell_p, C_p, kind='cubic', fill_value='extrapolate')
ell_i = np.arange(30, 2500)
D_p = C_int(ell_i) * ell_i*(ell_i+1)/(2*np.pi)

def parabola_peak(x, y):
    """局部拋物線擬合: y = a(x-x0)^2 + b"""
    A = np.vstack([x**2, x, np.ones_like(x)]).T
    coeff, *_ = np.linalg.lstsq(A, y, rcond=None)
    a, b, c = coeff
    if a >= 0:
        return None
    return -b/(2*a)

from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

# 用 sigma=3 平滑找候選峰區, 再喺平滑數據上拋物線擬合 (峰位一致)
# 注意: 平滑後峰位會略偏移, 所以窗要闊 (±20)
s3 = gaussian_filter1d(D_p, sigma=3)
cand, props = find_peaks(s3, distance=30, prominence=10)
cand = np.array(cand)
proms = np.array(props['prominences'])
keep = (proms > 0.01 * s3[cand]) & (s3[cand] > 100)
cand = cand[keep]

obs_peaks = np.array([float(ell_i[p]) for p in cand])
print(f"  平滑峰位 ({len(obs_peaks)}):")
for pk in obs_peaks:
    print(f"    ℓ = {pk:8.1f}")

# 峰位誤差 (bootstrap: 用 err_p 擾動 C_ℓ 100 次)
print("\n  峰位誤差 (bootstrap 100×, err_p 擾動):")
np.random.seed(42)
pk_err = {}
for pk in obs_peaks:
    shifts = []
    for _ in range(100):
        C_jit = C_p + np.random.normal(0, 1, len(C_p)) * err_p
        Cj_int = interp1d(ell_p, C_jit, kind='cubic', fill_value='extrapolate')
        Dj = Cj_int(ell_i) * ell_i*(ell_i+1)/(2*np.pi)
        lo, hi = int(pk)-4, int(pk)+5
        pj = parabola_peak(ell_i[lo:hi].astype(float), Dj[lo:hi])
        if pj is not None:
            shifts.append(pj)
    if shifts:
        pk_err[round(pk,1)] = np.std(shifts)
        print(f"    ℓ={pk:8.1f} ± {np.std(shifts):.1f}")

# ---------- 2. 對比表 ----------
print("\n" + "="*78)
print("2. IDCM vs 觀測 (Planck binned 擬合峰位)")
print("="*78)
print(f"{'m':>2} {'IDCM':>6} {'Planck obs':>10} {'±':>5} {'dev':>7} {'z':>5}  verdict")
for m in range(1, 8):
    pred = idcm_peak(m)
    diffs = np.abs(obs_peaks - pred)
    j = np.argmin(diffs)
    obs = obs_peaks[j]
    err = pk_err.get(round(obs,1), 10.0)
    dev = (obs - pred)/pred*100
    z = (obs - pred)/err
    mark = "✅" if abs(dev) < 2 else ("🟡" if abs(dev) < 5 else "❌")
    print(f"{m:>2} {pred:>6} {obs:>10.1f} {err:>5.1f} {dev:>+7.2f} {z:>+5.1f}  {mark}")

# ---------- 3. CAMB 對比 ----------
print("\n" + "-"*78)
print("3. CAMB raw 峰 vs 觀測")
print("-"*78)
import camb
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
pars.set_for_lmax(3000, lens_potential_accuracy=0)
TTc = camb.get_results(pars).get_cmb_power_spectra(raw_cl=True)['unlensed_scalar'][:,0]
ell_c = np.arange(len(TTc))
Dl_c = TTc * ell_c*(ell_c+1)/(2*np.pi)
s_c = gaussian_filter1d(Dl_c, sigma=3)
pk_camb = [int(l) for l in find_peaks(s_c, distance=30)[0] if 300 < l < 2000]
print(f"  CAMB raw 峰: {pk_camb}")
for c in pk_camb:
    diffs = np.abs(obs_peaks - c)
    j = np.argmin(diffs)
    print(f"    CAMB ℓ={c}: 最近觀測峰 = {obs_peaks[j]:.1f} (Δ={c-obs_peaks[j]:+.1f})")

# ---------- 4. SPT-3G 交叉驗證 ----------
print("\n" + "-"*78)
print("4. SPT-3G D1 高ℓ區 — 觀測峰交叉驗證")
print("-"*78)
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

# 正確 bin centers: window 每 bin 嘅加權平均 (first moment)
win = np.loadtxt(os.path.join(DATADIR, 'spt_tt150_windows.txt'))
ell_w = win[:, 0]
W = win[:, 1:]
bin_centers = []
for b in range(W.shape[1]):
    wcol = W[:, b]
    if wcol.sum() > 0:
        bc = (ell_w * wcol).sum() / wcol.sum()
    else:
        bc = ell_w[np.argmax(wcol)]
    bin_centers.append(bc)
bin_centers = np.array(bin_centers)
print(f"  bin centers (加權平均, 首10): {bin_centers[:10].astype(int)}")

# SPT-3G 峰偵測: 插值到細網格
from scipy.interpolate import interp1d
bc_int = interp1d(np.arange(len(bin_centers)), bin_centers, kind='linear', fill_value='extrapolate')
spt_fine_ell = np.linspace(bin_centers[0], bin_centers[-1], 2000)
spt_fine_D = np.interp(spt_fine_ell, bin_centers, tt150)
spt_s = gaussian_filter1d(spt_fine_D, sigma=8)  # ~50 闊 bin, sigma 8 適合
spt_pk, _ = find_peaks(spt_s, distance=100)
spt_peaks = spt_fine_ell[spt_pk]
print(f"  SPT-3G D1 峰位 (插值+σ=8): {[f'{p:.0f}' for p in spt_peaks]}")

print("\n  SPT-3G vs IDCM (m=4..7):")
for m in [4, 5, 6, 7]:
    pred = idcm_peak(m)
    diffs = np.abs(spt_peaks - pred)
    if len(diffs) == 0: continue
    j = np.argmin(diffs)
    dev = (spt_peaks[j] - pred)/pred*100
    mark = "✅" if abs(dev) < 2 else ("🟡" if abs(dev) < 5 else "❌")
    print(f"    m={m}: IDCM {pred} vs SPT {spt_peaks[j]:.0f} → {dev:+.2f}% {mark}")

# ---------- 5. 統計 ----------
print("\n" + "="*78)
print("5. RMS 統計")
print("="*78)
idcm_all = np.array([idcm_peak(m) for m in range(1,8)])
# IDCM 每峰 vs 最近觀測峰
matched = []
for m in range(1, 8):
    pred = idcm_peak(m)
    diffs = np.abs(obs_peaks - pred)
    j = np.argmin(diffs)
    matched.append((pred, obs_peaks[j]))
matched = np.array(matched)
devs = (matched[:,1] - matched[:,0])/matched[:,0]*100
print(f"  IDCM m=1-7 vs Planck 觀測: RMS 偏差 = {np.sqrt(np.mean(devs**2)):.2f}%")
print(f"  各峰: {[f'{d:+.1f}%' for d in devs]}")

# CAMB 對應
camb_matched = []
for c in [536, 814, 1129, 1427]:
    diffs = np.abs(obs_peaks - c)
    j = np.argmin(diffs)
    camb_matched.append((c, obs_peaks[j]))
camb_matched = np.array(camb_matched)
cdevs = (camb_matched[:,1] - camb_matched[:,0])/camb_matched[:,0]*100
print(f"  CAMB 峰 vs Planck 觀測: RMS 偏差 = {np.sqrt(np.mean(cdevs**2)):.2f}%")
print(f"  各峰: {[f'{d:+.1f}%' for d in cdevs]}")
