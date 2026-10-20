#!/usr/bin/env python3
"""
P3/high-l-tail-transfer — R8: λ=527 vs 537 邊界檢定 (2026-10-20)
=====================================================================
R4: λ_obs=533±3; λ=537 (P3 obs, 44×12+9) Δχ²=+1.7 NS
O9 binned m=2 = 527 (44×12−1) — 同一峰位嘅 Planck binned 值
本檢定: λ=527 同 λ=537 邊界 (Δχ² 對比), 並列全部 m=2 相關候選
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

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
DATA = f"{BASE}/o214_energy_budget_definition/data/spt3g_d1"
bdp = np.loadtxt(f"{DATA}/SPT3G_D1_TnE_bdp.txt")
cov = np.loadtxt(f"{DATA}/SPT3G_D1_TnE_cov.dat")
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
Cmat = cov[off:off+52, off:off+52]
sm = tt150 > 0
ells_s, D_s = centers[sm], tt150[sm]
ms = ells_s > 1409
ls, ds = ells_s[ms], D_s[ms]
idx = np.where(ms)[0]
Csub = Cmat[np.ix_(idx, idx)]
sigs = np.sqrt(np.diag(Csub))
n = len(ls)

def Amax(lam):
    w = 1/sigs**2
    e = np.exp(-np.array(ls)/lam)
    return np.sum(w*ds*e)/np.sum(w*e**2)

def chi2_full(lam):
    A = Amax(lam)
    pred = A*np.exp(-np.array(ls)/lam)
    r = ds - pred
    return r @ np.linalg.pinv(Csub) @ r, A

print("="*76)
print("P3/high-l-tail-transfer — R8 λ 邊界檢定")
print("="*76)

# 最佳 λ (精細)
b0 = None
for lam in np.arange(490, 580, 0.5):
    c, A = chi2_full(lam)
    if b0 is None or c < b0[0]: b0 = (c, lam, A)
print(f"最佳: λ={b0[1]:.1f} χ²={b0[0]:.1f} A={b0[2]:.1f}")

cands = [(527, "44×12−1 (O9 binned m=2)"), (533, "50×? fit"),
         (537, "44×12+9 (P3 obs m=2)"), (484, "44×11 L₅×N_d"),
         (505, "484+21"), (297, "33×9"), (306, "峰距 306")]
print(f"\n{'(λ)':>5} {('身份'):34s} {'χ²':>9} {'Δχ²':>8} {'判決':>6}")
for c, label in cands:
    chi2v, A = chi2_full(c)
    dchi = chi2v - b0[0]
    mark = "NS" if dchi < 9 else "❌"
    print(f"{c:5d} {label:34s} {chi2v:9.1f} {dchi:+8.1f} {mark:>6}")

# 527 vs 537 Δχ²
c527, _ = chi2_full(527); c537, _ = chi2_full(537)
print(f"\nλ=527 vs λ=537: Δχ² = {c527-c537:+.1f}")
check("R8-1: 527 vs 537 Δχ² < 9 (不可分辨)", abs(c527-c537) < 9, f"Δχ²={c527-c537:+.1f}")
# 但兩個 vs 最佳都要 <9 先係 candidate
c533, _ = chi2_full(533)
check("R8-2: λ=527 NS vs best", c527-b0[0] < 9, f"Δχ²={c527-b0[0]:+.1f}")

print("\n" + "="*76)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*76)
sys.exit(0 if FAIL == 0 else 1)