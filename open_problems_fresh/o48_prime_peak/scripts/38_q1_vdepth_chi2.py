#!/usr/bin/env python3
"""
O48 Q1.22: 谷深身份 χ² 分辨 — 1/2 vs 3ε vs F₄/F₅
=============================================================
Q1.21: corr 對谷深唔敏感 (0.5 vs 0.4635 差 0.001)。用 χ² (amplitude-resolved)
分辨候選谷深身份。

方法: 同 Q1.20 script 36 — SPT TT_150x150 covariance, 但掃 vdepth 候選,
比較 Δχ² vs null。χ² 對絕對 amplitude 敏感 → 可分辨 0.5 vs 0.4635。

候選 (谷深身份):
  vd1: 1/2   = N_d/88 = F₂/F₃ (最簡結構候選)
  vd2: 3ε    = 3φ⁻¹/4 (O48 幅度公式同源)
  vd3: F₄/F₅ = 3/5 = 0.6 (O9 曾用谷深)
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

def model_t(ells_arr, vdepth, sig=50.0):
    t = np.zeros_like(ells_arr, dtype=float)
    for p in PEAKS:
        t += peak_amp(p)*np.exp(-0.5*((ells_arr-p)/sig)**2)
    for v in V34:
        t -= vdepth*np.exp(-0.5*((ells_arr-v)/sig)**2)
    return t

def chi2_model(vdepth, sig=50.0):
    t = model_t(ells, vdepth, sig)
    tc = (t - t.mean())/t.std()
    a = (tc.T @ Cinv @ rr) / (tc.T @ Cinv @ tc)
    resid = rr - a*tc
    return float(resid.T @ Cinv @ resid), a

print("="*72)
print("谷深身份 χ² 分辨 (SPT covariance, σ=50)")
print("="*72)
chi0 = float(rr.T @ Cinv @ rr)
print(f"null χ² = {chi0:.1f} (dof={len(ells)-1})")

cands = {
    "1/2 (N_d/88=F₂/F₃)": 0.5,
    "3ε (3φ⁻¹/4)": 3*phi**(-1)/4,
    "F₄/F₅ (3/5)": 3/5,
    "φ⁻¹ (0.618)": phi**(-1),
    "2/5 (F₃/F₅)": 2/5,
}
best = (1e9, None)
for lab, vd in cands.items():
    chi2, a = chi2_model(vd)
    dchi = chi0 - chi2
    print(f"  {lab:<22}: vd={vd:.4f} χ²={chi2:7.1f} Δχ²={dchi:7.1f} (a={a:+.2f})")
    if chi2 < best[0]:
        best = (chi2, lab, vd)

print()
print(f"最佳谷深身份: {best[1]} (vd={best[2]:.4f}), χ²={best[0]:.1f}")
# 分辨判據: 最佳 vs 次佳 Δχ²
sv = sorted([(chi2_model(vd)[0], lab) for lab, vd in cands.items()])
d12 = sv[1][0] - sv[0][0]
print(f"第一名 vs 第二名: Δχ²={d12:.1f} (Δχ²>6.6 => 1% 分辨)")

# 0.5 vs 3ε 具體
chi_05, _ = chi2_model(0.5)
chi_3e, _ = chi2_model(3*phi**(-1)/4)
dchi = abs(chi_05 - chi_3e)
print(f"\n1/2 vs 3ε: |Δχ²|={dchi:.1f}")
print(f"  Δχ²<1 => 不可分辨 (兩者等價); Δχ²>6.6 => 分辨")
print(f"  較佳: {'1/2' if chi_05 < chi_3e else '3ε'} ({min(chi_05,chi_3e):.1f} vs {max(chi_05,chi_3e):.1f})")

print("\n" + "="*72)
print(f"SUMMARY: 谷深身份 {'已分辨' if d12 > 6.6 else '不可分辨(需更多數據)'}")
print("="*72)
sys.exit(0 if d12 > 6.6 else 1)