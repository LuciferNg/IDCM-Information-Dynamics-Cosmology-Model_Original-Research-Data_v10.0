#!/usr/bin/env python3
"""
O48 Q1.18: 谷深 × lensing σ 二維掃描（SPT 樣本外）
=============================================================
Q1.17 盲測 PASS (V¾ +0.475) 但谷深 0.6 同 σ=40 係擬合值。
本 script 掃 (vdepth, sigma) 網格, 答兩個問題:
  A. corr 平台存在? (穩健性 — 平台 = 結構真, 尖峰 = overfit)
  B. 最佳 (vdepth, σ) 係咪接近已用值 (0.6, 40)?
使用: SPT 樣本外 (V¾ 規則) + ACT 對照 + Plik 診斷
"""
import math, sys
import numpy as np

phi = (1+5**0.5)/2
F = lambda n: int(round((phi**n - (-phi)**(-n))/math.sqrt(5)))

base = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
DATA = f"{base}/o214_energy_budget_definition/data"
ACT = "/home/wsl/.hermes/cache/scratch/act_dr4/cmbonly_spectra_dr4.01/act_dr4.01_D_ell_TT_cmbonly.txt"

def load_plik():
    plik = []
    with open(f"{DATA}/planck2018_plik_lite/cl_cmb_plik_v22.dat") as f:
        for line in f:
            p = line.split()
            if len(p) >= 2:
                try:
                    plik.append((float(p[0]), float(p[1])))
                except ValueError:
                    pass
    return sorted(plik)

def load_spt():
    bdp = np.loadtxt(f"{DATA}/spt3g_d1/SPT3G_D1_TnE_bdp.txt")
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
    win = np.loadtxt(f"{DATA}/spt3g_d1/TT_150x150_window.txt")
    lgr = win[:, 0]
    return sorted([(lgr[np.argmax(win[:, b])], tt150[b-1]) for b in range(1, 53)])

def load_act():
    act = []
    with open(ACT) as f:
        for line in f:
            p = line.split()
            if len(p) >= 3 and p[0] != "#":
                try:
                    act.append((float(p[0]), float(p[1])))
                except ValueError:
                    pass
    return sorted(act)

plik = load_plik(); spt = load_spt(); act = load_act()

def detrend_resid(data):
    ells = np.array([e for e, d in data])
    D = np.array([d for e, d in data])
    mask = D > 0
    logD = np.log(D[mask])
    coef = np.polyfit(ells[mask], logD, 2)
    res = D[mask]/np.exp(np.polyval(coef, ells[mask]))
    return (res-res.mean())/res.std(), ells[mask]

resn_p, ells_p = detrend_resid([(e, d) for e, d in plik if 200 < e < 2500])
resn_s, ells_s = detrend_resid(spt)
resn_a, ells_a = detrend_resid(act)

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

def build(ells, sigma, vdepth):
    T = np.zeros_like(ells)
    for p in PEAKS:
        T += peak_amp(p)*np.exp(-0.5*((ells-p)/sigma)**2)
    for v in V34:
        T -= vdepth*np.exp(-0.5*((ells-v)/sigma)**2)
    return T

def corr(T, ells, resn):
    Tint = np.interp(ells, ell_grid, T)
    if Tint.std() == 0:
        return -9.9
    Tn = (Tint - Tint.mean())/Tint.std()
    return float(np.corrcoef(Tn, resn)[0, 1])

ell_grid = np.arange(32, 2500, 2.0)
sigmas = [20, 30, 35, 40, 50, 60, 80]
vdeps = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2]

print("="*72)
print("A. 谷深 × σ 掃描 (SPT 樣本外) — corr 平台存在?")
print("="*72)
print(f"{'vdepth\\σ':>8}", *[f"{s:>7}" for s in sigmas])
best = (-9.9, 0, 0)
for vd in vdeps:
    row = []
    for s in sigmas:
        T = build(ell_grid, s, vd)
        c = corr(T, ells_s, resn_s)
        row.append(c)
        if c > best[0]:
            best = (c, s, vd)
    print(f"{vd:>8.1f}", *[f"{c:>+7.3f}" for c in row])
print(f"\n最佳: vdepth={best[2]}, σ={best[1]}, corr={best[0]:+.3f}")

# 平台判據: 最佳±0.03 內嘅格數
print("\n平台分析 (SPT):")
T_best = build(ell_grid, best[1], best[2])
c_best = corr(T_best, ells_s, resn_s)
plateau = []
for vd in vdeps:
    for s in sigmas:
        T = build(ell_grid, s, vd)
        c = corr(T, ells_s, resn_s)
        if abs(c - c_best) < 0.03:
            plateau.append((vd, s, round(c, 4)))
print(f"  |corr−best|<0.03 格數: {len(plateau)} / {len(vdeps)*len(sigmas)}")
print(f"  平台格: {plateau}")

print("\n" + "="*72)
print("B. ACT 對照 (V¾)")
print("="*72)
c_a_best = (-9.9, 0, 0)
for vd in vdeps:
    for s in sigmas:
        T = build(ell_grid, s, vd)
        c = corr(T, ells_a, resn_a)
        if c > c_a_best[0]:
            c_a_best = (c, s, vd)
print(f"  ACT 最佳: vdepth={c_a_best[2]}, σ={c_a_best[1]}, corr={c_a_best[0]:+.3f}")

print("\n" + "="*72)
print("C. Plik 診斷")
print("="*72)
c_p_best = (-9.9, 0, 0)
for vd in vdeps:
    for s in sigmas:
        T = build(ell_grid, s, vd)
        c = corr(T, ells_p, resn_p)
        if c > c_p_best[0]:
            c_p_best = (c, s, vd)
print(f"  Plik 最佳: vdepth={c_p_best[2]}, σ={c_p_best[1]}, corr={c_p_best[0]:+.3f}")

print("\n" + "="*72)
print("裁決")
print("="*72)
print(f"  SPT 最佳 ({best[2]:.1f}, {best[1]}) corr {best[0]:+.3f} vs Q1.17 用 (0.6, 40) +0.475")
c_old = corr(build(ell_grid, 40, 0.6), ells_s, resn_s)
print(f"  (0.6,40) corr = {c_old:+.3f}")
n_flat = sum(1 for vd in vdeps for s in sigmas if abs(corr(build(ell_grid, s, vd), ells_s, resn_s) - c_old) < 0.03)
print(f"  (0.6,40)±0.03 平台格數: {n_flat}/{len(vdeps)*len(sigmas)}")
sys.exit(0)