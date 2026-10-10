#!/usr/bin/env python3
"""
O48 Q1.23: σ 寬度身份 χ² 分辨 — lensing/beam 寬度候選
=============================================================
Q1.21 corr 平台 (50-60 唔可分); Q1.22 谷深 χ² 分辨成功 (1/2 壓倒性)。
同一方法分辨 σ 候選 — 邊個係 lensing smoothing 寬度嘅結構身份?

候選:
  s1: 44  = N_d (模數)
  s2: 49.5 = 297/6 (峰週期/6)
  s3: 50  = 5×10
  s4: 55  = F₁₀
  s5: 60  = Q1.18 corr 最佳
  s6: 40  = 22 script 峰集
  s7: 297/6.6 = 45 (√2 相關?)
"""
import math, sys
import numpy as np

phi = (1+5**0.5)/2
F = lambda n: int(round((phi**n - (-phi)**(-n))/math.sqrt(5)))

base = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
DATA = f"{base}/o214_energy_budget_definition/data/spt3g_d1"

bdp = np.loadtxt(f"{DATA}/SPT3G_D1_TnE_bdp.txt")
cov = np.loadtxt(f"{DATA}/SPT3G_D1_TnE_cov.dat")
win = np.loadtxt(f"{DATA}/TT_150x150_window.txt")

spectra = [("TT_90x90",52),("TE_90x90",72),("EE_90x90",72),("TT_90x150",52),
           ("TE_90x150",72),("TE_150x90",72),("EE_90x150",72),("TT_90x220",52),
           ("TE_90x220",72),("TE_220x90",72),("EE_90x220",72),("TT_150x150",52),
           ("TE_150x150",72),("EE_150x150",72),("TT_150x220",52),("TE_150x220",72),
           ("TE_220x150",72),("EE_150x220",72),("TT_220x220",52),("TE_220x220",72),
           ("EE_220x220",72)]
off = 0
for name, n in spectra:
    if name == "TT_150x150":
        break
    off += n
tt150 = bdp[off:off+52]
C = cov[off:off+52, off:off+52]
lgr = win[:, 0]
centers = np.array([lgr[np.argmax(win[:, b])] for b in range(1, 53)])

mask = tt150 > 0
ells = centers[mask]
D = tt150[mask]
Cm = C[mask][:, mask]
logD = np.log(D)
coef = np.polyfit(ells, logD, 2)
env = np.exp(np.polyval(coef, ells))
r = D - env
rr = r - r.mean()
Cinv = np.linalg.pinv(Cm)

PEAKS = [221, 527, 815, 1013, 1121, 1337, 1409]
V34 = [221+0.75*306, 527+0.75*288, 815+0.75*306, 1121+0.75*288]

def peak_amp(ell):
    eps = phi**(-1)/4
    j_of = {221: 0, 527: 1, 815: 2, 1121: 3, 1409: 4}
    if int(round(ell)) not in j_of:
        return 0.5
    j = j_of[int(round(ell))]
    geo = [1.0, 1.0/F(1), 1.0/F(2), 1.0/F(3), 1.0/F(4)][j]
    return 3*eps*geo*(33/34)*math.exp(-(ell/9055.0)**1.5)

def model_t(ells_arr, sig, vdepth=0.5):
    t = np.zeros_like(ells_arr, dtype=float)
    for p in PEAKS:
        t += peak_amp(p)*np.exp(-0.5*((ells_arr-p)/sig)**2)
    for v in V34:
        t -= vdepth*np.exp(-0.5*((ells_arr-v)/sig)**2)
    return t

def chi2_model(sig, vdepth=0.5):
    t = model_t(ells, sig, vdepth)
    tc = (t - t.mean())/t.std()
    a = (tc.T @ Cinv @ rr) / (tc.T @ Cinv @ tc)
    resid = rr - a*tc
    return float(resid.T @ Cinv @ resid), a

print("="*72)
print("σ 身份 χ² 分辨 (SPT covariance, vdepth=1/2)")
print("="*72)
chi0 = float(rr.T @ Cinv @ rr)
print(f"null χ² = {chi0:.1f} (dof={len(ells)-1})")

cands = {
    "44 (N_d)": 44,
    "45 (297/6.6)": 45,
    "49.5 (297/6)": 49.5,
    "50 (5×10)": 50,
    "55 (F₁₀)": 55,
    "60 (Q1.18 最佳)": 60,
    "40 (22script 峰集)": 40,
    "297/7≈42.4": 297/7,
}
best = (1e9, None)
print(f"{'候選':<22} {'σ':>7} {'χ²':>8} {'Δχ²':>8}")
for lab, s in cands.items():
    chi2, a = chi2_model(s)
    dchi = chi0 - chi2
    print(f"  {lab:<20} {s:7.2f} {chi2:8.1f} {dchi:8.1f}")
    if chi2 < best[0]:
        best = (chi2, lab, s)

print()
print(f"最佳 σ: {best[1]} (σ={best[2]:.2f}), χ²={best[0]:.1f}")
sv = sorted([(chi2_model(s)[0], lab, s) for lab, s in cands.items()])
d12 = sv[1][0] - sv[0][0]
print(f"第一 vs 第二: Δχ²={d12:.1f} (Δχ²>6.6 => 1% 分辨, >13.8 => 0.1%)")
print("\n排名:")
for i, (chi2, lab, s) in enumerate(sv, 1):
    print(f"  {i}. {lab}: σ={s:.2f} χ²={chi2:.1f} Δ={chi2-sv[0][0]:+.1f}")

print("\n" + "="*72)
print(f"SUMMARY: σ 身份 {'已分辨: '+sv[0][1] if d12 > 6.6 else '平台未分辨'}")
print("="*72)
sys.exit(0 if d12 > 6.6 else 1)