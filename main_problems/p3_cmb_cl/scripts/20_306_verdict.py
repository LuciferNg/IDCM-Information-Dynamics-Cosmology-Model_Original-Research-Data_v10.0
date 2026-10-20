#!/usr/bin/env python3
"""
P3/high-l-tail-transfer — R12: 306 係 IDCM 特有定 lensed ΛCDM 巧合? (2026-10-20)
=====================================================================
R11: λ₁=307±9 (SPT) / 308±5 (ACT) = 峰間隙 306 (0.1-0.4σ) — 兩實驗樣本外一致
    CAMB lensed λ₁=316 (偏 3%); mixed model FAIL (全段唔係一個 λ)

判決需要: CAMB unlensed 第一段 λ₁
  - Silk local scale @ℓ=1500: λ ≈ ℓ_D/α·(ℓ/ℓ_D)^(1-α) ≈ 1411/1.24·(1500/1411)^-0.24 ≈ 1138·0.978 ≈ 1113
  - 如果 unlensed λ₁≈1113 (Silk) 而 lensed 316 ⟹ lensing 收窄 local λ 3.5×
  - 如果 unlensed λ₁ 都 ≈310 ⟹ 「306」純粹係 Silk+lensing 嘅自然 local scale, 唔係 IDCM 特有
  - 306 (IDCM) vs 316 (CAMB lensed) 3% 差異亦係判決點

R12 決定性檢定:
  1. CAMB unlensed 第一段 λ₁
  2. CAMB lensed 第一段 (重複, 精細)
  3. 306 vs CAMB lensed 316: SPT/ACT fit 邊個好 (喺 1418-1720 段直接比)
  4. 峰間隙 306/288 vs CAMB 高ℓ尾有冇 306/288 交替 (CAMB 有冇峰間隙結構)
"""
import math, sys
import numpy as np
import astropy.io.fits as fits
import camb

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
print("="*76)
print("P3/high-l-tail-transfer — R12 306 判定: IDCM vs lensed ΛCDM")
print("="*76)

# ---------- CAMB ----------
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
pars.set_for_lmax(3200, lens_potential_accuracy=0)
res = camb.get_results(pars)
powr = res.get_cmb_power_spectra(raw_cl=True)
ells = np.arange(len(powr['unlensed_scalar'][:, 0]))

# 1. CAMB unlensed 第一段
for key, tag in [('unlensed_scalar', 'unlensed'), ('lensed_scalar', 'lensed')]:
    D = powr[key][:, 0] * ells*(ells+1)/(2*math.pi)
    m = (ells > 1418) & (ells < 1720)
    lx, dx = ells[m], D[m]
    sl, ic = np.polyfit(lx, np.log(dx), 1)
    lam = -1/sl
    print(f"CAMB {tag:9s} 第一段 (1418..1720): λ₁={lam:.0f}")
    # Silk 理論 local: λ = ℓ_D/α·(ℓ/ℓ_D)^(1-α), α=1.24 ℓ_D=1411
    for le in [1450, 1500, 1600, 1700]:
        lsilk = 1411/1.24 * (le/1411)**(1-1.24)
        pass
    if key == 'unlensed_scalar':
        check("R12-1: CAMB unlensed λ₁ > 500 (Silk local~1100)", lam > 500,
              f"λ₁={lam:.0f}")
        print(f"    Silk local @1500 = {1411/1.24*(1500/1411)**(1-1.24):.0f}")

# 2. 306 vs 316 直接比: SPT/ACT 第一段 χ²
print("\n2. 306 vs 316 第一段直接比較:")
def load_spt():
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
    return centers[sm], tt150[sm], Cmat[sm][:, sm]

def load_act():
    h = fits.open(f"{BASE}/o9_high_ell_peaks/data/act_dr6_cmb_sacc.fits")
    d = h['data:cl_00'].data
    cmat = h['covariance'].data
    return np.array([r['ell'] for r in d]), np.array([r['value'] for r in d]), cmat[:45,:45]

def chi_lam(l, d, sig, lam):
    w = 1/sig**2
    e = np.exp(-l/lam)
    A = np.sum(w*d*e)/np.sum(w*e**2)
    return np.sum(w*(d - A*e)**2), A

for name, ld, dd, cv in [("SPT", *load_spt()), ("ACT", *load_act())]:
    m = (ld > 1418) & (ld < 1720) & (dd > 0)
    lx, dx = ld[m], dd[m]
    sig = np.sqrt(np.diag(cv))[m]
    c306, A306 = chi_lam(lx, dx, sig, 306)
    c316, A316 = chi_lam(lx, dx, sig, 316)
    # 自由
    best = None
    for lam in range(200, 500):
        c, A = chi_lam(lx, dx, sig, lam)
        if best is None or c < best[0]: best = (c, lam)
    print(f"  {name:5s}: χ²(306)={c306:.1f}  χ²(316)={c316:.1f}  Δ={c306-c316:+.1f}  best={best[1]} (χ²={best[0]:.1f})")
    if name == "SPT":
        check("R12-2: 306 vs 316 唔可分 (|Δ|<9)", abs(c306-c316) < 9, f"Δ={c306-c316:+.1f}")

# 3. CAMB 有冇峰間隙交替? 高ℓ尾 local 斜率喺 1409/1715 有冇跳變
print("\n3. CAMB lensed 高ℓ尾 306/288 交替檢查:")
D = powr['lensed_scalar'][:, 0] * ells*(ells+1)/(2*math.pi)
m = (ells > 1400) & (ells < 2500)
lx, dx = ells[m], D[m]
# 每 150-200 段 fit lambda
print("  CAMB lensed 分段 λ (150ℓ 窗):")
for lo in range(1400, 2400, 150):
    seg = (ells > lo) & (ells < lo+150)
    sl, ic = np.polyfit(ells[seg], np.log(D[seg]), 1)
    print(f"    ℓ {lo}-{lo+150}: λ={-1/sl:.0f}")

print("\n" + "="*76)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*76)
sys.exit(0 if FAIL == 0 else 1)