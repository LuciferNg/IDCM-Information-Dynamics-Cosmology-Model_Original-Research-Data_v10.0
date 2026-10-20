#!/usr/bin/env python3
"""
P3/high-l-tail-transfer — R7: local e-folding 判決 (2026-10-20)
=====================================================================
λ_loc(ℓ) = -d ln D/dℓ  (local exponential decay scale)
  純指數 (α=1):        λ_loc = const
  Silk (α=1.24):       λ_loc ∝ ℓ^{1-α} = ℓ^{-0.24} (緩慢下降)
  Silk (α=1.5):        λ_loc ∝ ℓ^{-0.5} (明顯下降)
  冪律 D∝ℓ^-p:         λ_loc = ℓ/p (線性上升!!) ← 最易分辨

量度: CAMB lensed/unlensed 理論譜 + SPT + Planck 同一 ℓ 段
判決: 斜率 dλ_loc/dℓ > 0 (冪律), = 0 (純指數), < 0 (Silk α>1)
"""
import math, sys
import numpy as np

PASS, FAIL, TOTAL = 0, 0, 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")

import camb

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
print("="*76)
print("P3/high-l-tail-transfer — R7 local e-folding 判決")
print("="*76)

def local_lam(l, D, half=5):
    """λ_loc 喺每點: 前後 half 點嘅 log-linear 斜率倒數"""
    out = np.full(len(l), np.nan)
    for i in range(half, len(l)-half):
        seg = slice(i-half, i+half+1)
        sl, _ = np.polyfit(l[seg], np.log(D[seg]), 1)
        out[i] = -1/sl
    return out

# ---------- CAMB ----------
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
pars.set_for_lmax(3200, lens_potential_accuracy=0)
res = camb.get_results(pars)
powers = res.get_cmb_power_spectra(raw_cl=True)
ells = np.arange(len(powers['unlensed_scalar'][:, 0]))
for name in ['unlensed_scalar', 'lensed_scalar']:
    D = powers[name][:, 0] * ells*(ells+1)/(2*math.pi)
    m = (ells > 1400) & (ells < 2200)
    l, d = ells[m], D[m]
    lam = local_lam(l, d, half=8)
    print(f"\nCAMB {name:16s} λ_loc 量度 (ℓ 1408..2200):")
    for i in range(0, len(l), 20):
        if not np.isnan(lam[i]):
            print(f"  ℓ={l[i]:5.0f}  λ_loc={lam[i]:7.1f}")
    lo, hi = int(len(l)*0.2), int(len(l)*0.8)
    vals = lam[lo:hi][~np.isnan(lam[lo:hi])]
    slope = np.polyfit(l[lo:hi][~np.isnan(lam[lo:hi])], vals, 1)[0]
    print(f"  → dλ_loc/dℓ = {slope:+.4f}  (起始均值 {np.nanmean(lam[lo:hi]):.0f})")

# ---------- SPT ----------
DATA = f"{BASE}/o214_energy_budget_definition/data/spt3g_d1"
bdp = np.loadtxt(f"{DATA}/SPT3G_D1_TnE_bdp.txt")
win = np.loadtxt(f"{DATA}/TT_150x150_window.txt")
centers = np.array([win[np.argmax(win[:, b]), 0] for b in range(1, 53)])
spectra = [("TT_90x90",52),("TE_90x90",72),("EE_90x90",72),("TT_90x150",52),
           ("TE_90x150",72),("TE_150x90",72),("EE_90x150",72),("TT_90x220",52),
           ("TE_90x220",72),("TE_220x90",72),("EE_90x220",72),("TT_150x150",52),
           ("TE_150x150",72),("EE_150x150",72),("TT_150x220",52),("TE_150x220",72),
           ("TE_220x150",72),("EE_150x220",72),("TT_220x220",52),("TE_220x220",72),
           ("EE_220x220",72)]
off = 0
for name, n in spectra:
    if name == "TT_150x150": break
    off += n
tt150 = bdp[off:off+52]
sm = tt150 > 0
ells_s, D_s = centers[sm], tt150[sm]
ms = ells_s > 1409
ls_s, ds_s = ells_s[ms], D_s[ms]
lam_s = local_lam(ls_s, ds_s, half=3)
print(f"\nSPT 實測 λ_loc (dense bins, half=3):")
for i in range(0, len(ls_s), 4):
    if not np.isnan(lam_s[i]):
        print(f"  ℓ={ls_s[i]:5.0f}  λ_loc={lam_s[i]:7.1f}")
vals = lam_s[~np.isnan(lam_s)]
slp_s = np.polyfit(ls_s[~np.isnan(lam_s)], vals, 1)[0]
print(f"  → dλ_loc/dℓ = {slp_s:+.4f}  (均值 {np.nanmean(vals):.0f})")
check("R7-SPT: λ_loc 斜率 ≈ 0 (純指數", abs(slp_s) < 1.0,
      f"dλ_loc/dℓ={slp_s:+.4f}")

# ---------- Planck ----------
planck = []
with open(f"{BASE}/o9_high_ell_peaks/data/planck_tt.txt") as f:
    for line in f:
        p = line.split()
        if len(p) >= 2:
            try: planck.append((float(p[0]), float(p[1])))
            except ValueError: pass
planck = np.array(sorted(planck))
l_p, C_p = planck[:, 0], planck[:, 1]
D_p = C_p * l_p*(l_p+1)/(2*math.pi)
mt = (l_p > 1409) & (l_p < 2200)
l_pt, D_pt = l_p[mt], D_p[mt]
lam_p = local_lam(l_pt, D_pt, half=3)
print(f"\nPlanck 實測 λ_loc (1418..2195, half=3):")
valsp = lam_p[~np.isnan(lam_p)]
slp_p = np.polyfit(l_pt[~np.isnan(lam_p)], valsp, 1)[0]
print(f"  → dλ_loc/dℓ = {slp_p:+.4f}  (均值 {np.nanmean(valsp):.0f})")
check("R7-Planck: λ_loc 斜率 ≈ 0 (純指數)", abs(slp_p) < 1.0,
      f"dλ_loc/dℓ={slp_p:+.4f}")

# ---------- 判決 ----------
print("\n" + "="*76)
print("判決:")
print("  λ_loc/dℓ > +1: 冪律 (λ=ℓ/p 線性上升) → 非指數")
print("  λ_loc/dℓ ≈ 0:  純指數 e^{-ℓ/λ} → 高ℓ尾 = 指數傳輸函數")
print("  λ_loc/dℓ < -1: Silk 型 (α>1: λ∝ℓ^{1-α} 下降) → ΛCDM Silk")
print("="*76)

print("\n" + "="*76)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*76)
sys.exit(0 if FAIL == 0 else 1)