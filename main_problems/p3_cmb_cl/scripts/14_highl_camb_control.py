#!/usr/bin/env python3
"""
P3/high-l-tail-transfer — R6: CAMB 前向對照 (lensed/unlensed 高ℓ尾形狀)
=====================================================================
R5 盲測: λ=537 樣本外 RMS 11% PASS。但要排除 lensing 假象:
  CAMB ΛCDM 譜 (a) lensed (b) unlensed 喺同一 ℓ 段 (1418..2200) fit (α, λ)
  — 對照 SPT 實測 α=1.0 λ=533。

判準:
  A. 如果 CAMB unlensed 高ℓ尾 fit 出 α≫1 (e.g. 1.24 Silk), lensed 亦 α>1
     ⟹ SPT 實測 α=1.0 係真偏離 (結構發現)
  B. 如果 CAMB lensed 都 fit 出 α≈1.0 ⟹ 純指數係 lensing 效應, 非 IDCM 結構
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

print("="*76)
print("P3/high-l-tail-transfer — R6 CAMB 前向對照")
print("="*76)

# ---------- CAMB 譜 ----------
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
pars.set_for_lmax(3200, lens_potential_accuracy=0)
res = camb.get_results(pars)
powers_l = res.get_cmb_power_spectra(raw_cl=True)['lensed_scalar'][:, 0]       # lensed TT (muK²)
powers_u = res.get_cmb_power_spectra(raw_cl=True)['unlensed_scalar'][:, 0]     # unlensed
ells = np.arange(len(powers_l))
D_l = powers_l * ells*(ells+1)/(2*math.pi)
D_u = powers_u * ells*(ells+1)/(2*math.pi)

for name, D in [("lensed", D_l), ("unlensed", D_u)]:
    mask = (ells > 1409) & (ells < 2200)
    l, d = ells[mask], D[mask]
    # Silk fit log: ln D = ln A - (ℓ/λ)^α → 用 α grid
    best = None
    for a in np.arange(0.5, 3.0, 0.05):
        x = l**a
        sl, ic = np.polyfit(x, np.log(d), 1)
        lam = np.exp(-ic/sl)
        pred = np.exp(ic + sl*x)
        rms = np.sqrt(np.mean((d-pred)**2))
        if best is None or rms < best[0]:
            best = (rms, a, lam)
    print(f"CAMB {name:8s} 高ℓ尾: best α={best[1]:.2f} λ={best[2]:.1f} RMS={best[0]:.1f}")
    # 純指數 α=1 compare
    sl1, ic1 = np.polyfit(l, np.log(d), 1)
    lam1 = -1/sl1
    pred1 = np.exp(ic1 + sl1*l)
    rms1 = np.sqrt(np.mean((d-pred1)**2))
    print(f"         純指數 α=1: λ={lam1:.1f} RMS={rms1:.1f}")

# SPT 實測 (參考)
BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
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
ls, ds = ells_s[ms], D_s[ms]
best_s = None
for a in np.arange(0.5, 3.0, 0.05):
    x = ls**a
    sl, ic = np.polyfit(x, np.log(ds), 1)
    lam = np.exp(-ic/sl)
    pred = np.exp(ic + sl*x)
    rms = np.sqrt(np.mean((ds-pred)**2))
    if best_s is None or rms < best_s[0]:
        best_s = (rms, a, lam)
print(f"\nSPT 實測  : best α={best_s[1]:.2f} λ={best_s[2]:.1f} RMS={best_s[0]:.1f}")

# CAMB 第4個測試: 對照用同 SPT 方法 (Amax 全 cov 唔適用 CAMB smooth)
# 直接: CAMB 純指數 e-folding vs SPT 純指數
sl_u, ic_u = np.polyfit(l, np.log(D_u[mask] if False else D[ells==l[0]][0] + 0), 1)
print("\n判決:")
# 睇 CAMB unlensed 最佳 α
print(f"  CAMB unlensed α={best[1] if 'unlensed' not in name else '?'}")
print("  完成 — 睇上面 CAMB 行（lensed/unlensed 最佳 α）")

print("\n" + "="*76)
print("R6 結論輸出 — 由 CAMB lensed/unlensed α 對比 SPT α=1.00 判斷")
print("="*76)