#!/usr/bin/env python3
"""
P3/high-l-tail-transfer — R11: 峰距 306 檢定 + mixed model (2026-10-20)
=====================================================================
R10: 分段 λ 拆解 — λ 隨 ℓ 上升 (非單一純指數):
  1418-1700: SPT λ=308 ACT λ=308 (精確一致!) ≈ 峰間隙 306 (0.65%)
  1700-2000: λ=406 vs 426        2000-2400: 450 vs 396
  2400-3000: λ=646 (lensing floor 出現 → local λ 上升)

R11:
  1. 第一段 λ₁ bootstrap 誤差 + vs 306 檢定 (2σ?)
  2. Mixed model: D(ℓ) = A·exp(-ℓ/λ₁) + B(lensing floor), λ₁=306 FIXED, fit (A,B)
     vs 自由 λ₁ — 睇 λ₁=306 夠唔夠
  3. IDCM 結構旁證: 峰間隙 306/288 交替 (m: 221→527=306, 527→815=288,
     815→1121=306, 1121→1409=288); 1409→(m=8 唔存在) 第一衰減段 = 306?
  4. ΛCDM 對照: CAMB lensed 譜同段 fit λ₁ — 睇 306 係咪 IDCM 特有
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
print("P3/high-l-tail-transfer — R11 峰距 306 檢定 + mixed model")
print("="*76)

# ---------- 載入 ----------
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

def load_planck():
    planck = []
    with open(f"{BASE}/o9_high_ell_peaks/data/planck_tt.txt") as f:
        for line in f:
            p = line.split()
            if len(p) >= 2:
                try: planck.append((float(p[0]), float(p[1])))
                except ValueError: pass
    planck = np.array(sorted(planck))
    l, C = planck[:, 0], planck[:, 1]
    return l, C * l*(l+1)/(2*math.pi)

spt_l, spt_d, spt_cov = load_spt()
act_l, act_d, act_cov = load_act()
pl_l, pl_d = load_planck()

def fit_lam(l_all, d_all, cov_or_sig, mask):
    l, d = l_all[mask], d_all[mask]
    if cov_or_sig is None:
        sig = d*0.05
    elif cov_or_sig.ndim == 2:
        sig = np.sqrt(np.diag(cov_or_sig))[mask]
    else:
        sig = cov_or_sig[mask]
    w = 1/sig**2
    best = None
    for lam in np.arange(150, 1200, 1):
        e = np.exp(-l/lam)
        A = np.sum(w*d*e)/np.sum(w*e**2)
        c = np.sum(w*(d - A*e)**2)
        if best is None or c < best[0]: best = (c, lam)
    return best[1], best[0]

# ---------- 1. 第一段 (1418-1700) λ₁ ----------
print("1. 第一段 (1418..1700) λ₁ bootstrap:")
rng = np.random.default_rng(11)
for name, l, d, cv in [("SPT", spt_l, spt_d, spt_cov), ("ACT", act_l, act_d, act_cov)]:
    m = (l > 1418) & (l < 1720) & (d > 0)
    lx, dx = l[m], d[m]
    sig = np.sqrt(np.diag(cv))[m]
    lam0, _ = fit_lam(l, d, cv, m)
    boots = []
    for b in range(1000):
        db = dx + rng.normal(0, 1, len(dx))*sig
        bb = None
        for lam in np.arange(150, 700, 2):
            w = 1/sig**2
            e = np.exp(-lx/lam)
            A = np.sum(w*db*e)/np.sum(w*e**2)
            c = np.sum(w*(db - A*e)**2)
            if bb is None or c < bb[0]: bb = (c, lam)
        boots.append(bb[1])
    boots = np.array(boots)
    z306 = abs(lam0-306)/(boots.std())
    print(f"  {name:5s}: λ₁={lam0:.0f} ± {boots.std():.0f}  ({len(lx)} bins)  vs 306: {z306:.1f}σ")
    if name == "SPT":
        check("R11-1: SPT λ₁ ≈ 306 (2σ)", z306 < 2, f"λ₁={lam0:.0f}±{boots.std():.0f}, z={z306:.1f}")

# 合併 SPT+ACT? 唔同 cov 唔合; 分列
# 峰間隙表
gaps = [(527-221, "m1→2"), (815-527, "m2→3"), (1121-815, "m3→5"), (1409-1121, "m5→7")]
print(f"\n  峰間隙序列 (O48): {gaps}")
lam1_sp = fit_lam(spt_l, spt_d, spt_cov, (spt_l > 1418) & (spt_l < 1720))[0]
lam1_ac = fit_lam(act_l, act_d, act_cov, (act_l > 1418) & (act_l < 1720))[0]
print(f"  → λ₁: SPT={lam1_sp:.0f}  ACT={lam1_ac:.0f}  (306 峰距: dev {abs(lam1_sp-306)/306*100:.1f}%/{abs(lam1_ac-306)/306*100:.1f}%)")

# ---------- 2. Mixed model: D = A·exp(-ℓ/306) + B ----------
print("\n2. Mixed model (λ₁=306 FIXED + lensing floor):")
for name, l, d, cv in [("SPT", spt_l, spt_d, spt_cov), ("ACT", act_l, act_d, act_cov)]:
    m = (l > 1418) & (l < 3000) & (d > 0)
    lx, dx = l[m], d[m]
    sig = np.sqrt(np.diag(cv))[m]
    w = 1/sig**2
    # 2-param fit (A, B): 線性化
    E = np.exp(-lx/306)
    # χ² = Σw(dx - A·E - B)² → normal equations
    # Σw E² A + Σw E B = Σw E dx ; Σw E A + Σw 1 B = Σw dx
    M = np.array([[np.sum(w*E**2), np.sum(w*E)],
                  [np.sum(w*E), np.sum(w)]])
    rhs = np.array([np.sum(w*E*dx), np.sum(w*dx)])
    A_, B_ = np.linalg.solve(M, rhs)
    pred = A_*E + B_
    chi = np.sum(w*(dx-pred)**2)
    # 純指數對照 (自由 λ)
    lamf, chif_ = fit_lam(l, d, cv, m)
    print(f"  {name:5s}: A·exp(-ℓ/306)+B: A={A_:.0f} B={B_:.1f} χ²/dof={chi/(len(lx)-2):6.1f}")
    print(f"       純指數(自由λ): λ={lamf:.0f} χ²/dof={chif_/(len(lx)-1):6.1f}")
    print(f"       Δχ² = {chi-chif_:+.0f} ({'306+floor 好' if chi < chif_ else '自由λ 好'})")
    if name == "SPT":
        # floor B 應該細 (lensing ~ 0.1-1% of D(1400)=800 → B≈1-8)
        check("R11-2: SPT floor B 合理 (<20)", B_ < 20, f"B={B_:.1f}")

# ---------- 3. CAMB 對照: 第一段 λ₁ ----------
print("\n3. CAMB lensed 對照 (第一段 1418..1720):")
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
pars.set_for_lmax(3200, lens_potential_accuracy=0)
res = camb.get_results(pars)
powr = res.get_cmb_power_spectra(raw_cl=True)['lensed_scalar'][:, 0]
ells = np.arange(len(powr))
Dc = powr * ells*(ells+1)/(2*math.pi)
m = (ells > 1418) & (ells < 1720)
sl, ic = np.polyfit(ells[m], np.log(Dc[m]), 1)
lam_camb = -1/sl
print(f"  CAMB lensed λ₁ = {lam_camb:.0f}  vs SPT {lam1_sp:.0f} / 306")
check("R11-3: CAMB λ₁ ≠ 306 (>5σ)", abs(lam_camb-306) > 5*30, f"CAMB={lam_camb:.0f}")

# ---------- 4. 尾段訊號: 有冇 lensing floor 線索 ----------
print("\n4. 高段 (2400..3000) 有冇 floor 跡象:")
for name, l, d in [("SPT", spt_l, spt_d), ("ACT", act_l, act_d)]:
    m = (l > 2400) & (l < 3020) & (d > 0)
    if np.sum(m) >= 5:
        lx, dx = l[m], d[m]
        # 如果仲係指數衰減 λ≈306: D(2962) 應該 ≈ D(2400)·exp(-562/306) ≈ 100·0.16 = 16
        # 但實際 D(2962)=45 (SPT) — 高過指數預言 3×!
        l0 = d[(l > 2380) & (l < 2430)]
        extrap = l0.mean()*np.exp(-(lx.max()-2400)/306) if len(l0) else np.nan
        print(f"  {name:5s}: D({lx.min():.0f})={dx[0]:.1f}, D({lx.max():.0f})={dx[-1]:.1f}"
              f"  306-指數外推@{lx.max():.0f}≈{extrap:.1f} → {dx[-1]/extrap if not np.isnan(extrap) else np.nan:.1f}×")

print("\n" + "="*76)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*76)
sys.exit(0 if FAIL == 0 else 1)