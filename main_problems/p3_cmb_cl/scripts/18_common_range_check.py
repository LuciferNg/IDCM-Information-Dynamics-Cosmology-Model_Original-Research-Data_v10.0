#!/usr/bin/env python3
"""
P3/high-l-tail-transfer — R10: 共同範圍 λ 收斂檢定 (2026-10-20)
=====================================================================
R9 FAIL 信號: λ_ACT=498±2 拒絕 527..537 (14-19σ); 但三實驗 λ 成序列
  482 (Planck, range→2492) < 498 (ACT, range→3324) < 533 (SPT, range→2962)
  範圍排序: Planck 2492 < SPT 2962 < ACT 3324 — 近似負相關
  ⟹ 單指數可能係範圍效應 (高ℓ段衰減更快 ⟹ 遠段拉低 λ)

R10 檢定:
  1. 共同 ℓ 範圍 (1418..2195) 三實驗 λ → 如果收斂 ≡ 單指數成立, 範圍差異係效應
  2. local λ_loc(ℓ) 三實驗齊面 — 真正形狀
  3. 分段 λ: 1418-1700 / 1700-2000 / >2000 — 睇 λ 有冇隨 ℓ 降
"""
import math, sys
import numpy as np
import astropy.io.fits as fits

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
print("P3/high-l-tail-transfer — R10 共同範圍收斂檢定")
print("="*76)

# ---------- 載入三實驗 ----------
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
    ell_a = np.array([r['ell'] for r in d])
    val_a = np.array([r['value'] for r in d])
    # cov 127×127 = 45 TT + 40 TE + 42 EE → TT block 前 45
    cov_tt = cmat[:45, :45]
    return ell_a, val_a, cov_tt

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
    return l, C * l*(l+1)/(2*math.pi), None

def fit_lam(l_all, d_all, cov_or_sig, mask):
    l, d = l_all[mask], d_all[mask]
    if cov_or_sig is None:
        sig = d*0.05  # Planck 冇 error: 5% 近似 (報告註明)
    elif cov_or_sig.ndim == 2:
        sig = np.sqrt(np.diag(cov_or_sig))[mask]
    else:
        sig = cov_or_sig[mask]
    w = 1/sig**2
    best = None
    for lam in np.arange(300, 900, 2):
        e = np.exp(-l/lam)
        A = np.sum(w*d*e)/np.sum(w*e**2)
        c = np.sum(w*(d - A*e)**2)
        if best is None or c < best[0]: best = (c, lam)
    return best[1], best[0]

spt_l, spt_d, spt_cov = load_spt()
act_l, act_d, act_cov = load_act()
pl_l, pl_d, _ = load_planck()

# ---------- 1. 全段 fit (參考) ----------
for name, l, d, cv in [("SPT", spt_l, spt_d, spt_cov),
                       ("ACT", act_l, act_d, act_cov),
                       ("Planck", pl_l, pl_d, None)]:
    m = (l > 1409) & (d > 0)
    if name == "Planck": m = m & (l < 2200)
    lam, chi = fit_lam(l, d, cv, m)
    print(f"{name:7s} 全段: λ={lam:.0f}  (ℓ {l[m].min():.0f}..{l[m].max():.0f}, {np.sum(m)} bins)")

# ---------- 2. 共同範圍 1418..2195 ----------
print(f"\n共同範圍 (1418..2195):")
lams = {}
for name, l, d, cv in [("SPT", spt_l, spt_d, spt_cov),
                       ("ACT", act_l, act_d, act_cov),
                       ("Planck", pl_l, pl_d, None)]:
    m = (l > 1418) & (l < 2195) & (d > 0)
    lam, chi = fit_lam(l, d, cv, m)
    lams[name] = lam
    print(f"  {name:7s}: λ={lam:.0f}  ({np.sum(m)} bins)")
spread = max(lams.values()) - min(lams.values())
print(f"  spread = {spread:.0f} ({spread/np.mean(list(lams.values()))*100:.1f}%)")
check("R10-1: 共同範圍三實驗 spread < 10%", spread < 0.10*np.mean(list(lams.values())),
      f"spread={spread:.0f} ({spread/np.mean(list(lams.values()))*100:.1f}%)")

# ---------- 3. 分段 λ: 高段 decay 更快? ----------
print(f"\n分段 λ (範圍效應檢查):")
sections = [(1418, 1700), (1700, 2000), (2000, 2400), (2400, 3000)]
for lo, hi in sections:
    row = f"  ℓ {lo}-{hi}: "
    for name, l, d, cv in [("SPT", spt_l, spt_d, spt_cov), ("ACT", act_l, act_d, act_cov)]:
        m = (l > lo) & (l < hi) & (d > 0)
        if np.sum(m) >= 4:
            lam, chi = fit_lam(l, d, cv, m)
            row += f"{name}: λ={lam:.0f} ({np.sum(m)})   "
        else:
            row += f"{name}: — ({np.sum(m)})   "
    print(row)

# 趨勢 fit: λ vs 段中心
print(f"\nλ 隨 ℓ 上升段: 收集 col1..4 斜率")

# ---------- 4. local λ (三實驗) ----------
print(f"\nlocal λ_loc (half=3, 高ℓ):")
def local_lam(l, d, half=3):
    out = np.full(len(l), np.nan)
    for i in range(half, len(l)-half):
        seg = slice(i-half, i+half+1)
        sl, _ = np.polyfit(l[seg], np.log(d[seg]), 1)
        out[i] = -1/sl
    return out
for name, l, d in [("SPT", spt_l, spt_d), ("ACT", act_l, act_d), ("Planck", pl_l, pl_d)]:
    m = (l > 1409) & (d > 0)
    lx, dx = l[m], d[m]
    ll = local_lam(lx, dx, 2)
    ok = ~np.isnan(ll)
    if ok.sum() >= 3:
        slope = np.polyfit(lx[ok], ll[ok], 1)[0]
        print(f"  {name:7s}: λ_loc mean={np.nanmean(ll):.0f}  slope={slope:+.4f}/ℓ  "
              f"(range {lx.min():.0f}..{lx.max():.0f})")

# 共同範圍 local
print(f"\n共同範圍 local λ_loc:")
for name, l, d in [("SPT", spt_l, spt_d), ("ACT", act_l, act_d), ("Planck", pl_l, pl_d)]:
    m = (l > 1418) & (l < 2195) & (d > 0)
    lx, dx = l[m], d[m]
    ll = local_lam(lx, dx, 2)
    ok = ~np.isnan(ll)
    if ok.sum() >= 3:
        slope = np.polyfit(lx[ok], ll[ok], 1)[0]
        print(f"  {name:7s}: λ_loc mean={np.nanmean(ll):.0f}  slope={slope:+.4f}/ℓ  "
              f"({np.sum(m)} bins)")

print("\n" + "="*76)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*76)
sys.exit(0 if FAIL == 0 else 1)