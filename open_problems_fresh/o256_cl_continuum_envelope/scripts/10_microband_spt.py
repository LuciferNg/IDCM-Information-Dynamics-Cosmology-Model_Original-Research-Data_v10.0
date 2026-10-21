#!/usr/bin/env python3
"""
O256 — Script 10: 微帶 decisive test v2 — SPT/ACT 高分辨 (P3 parsing)
=====================================================================
Script 09 用 Planck (每 9 ℓ 一格) 唔夠解像. 用 P3 18 script 嘅 SPT/ACT
高分辨 parsing 檢查 1452..1476 微帶 bump 預言:

  結構預言: 峰位公式 m≥8 飽和 → 37 模態全塌入 [1452,1476]
  觀測檢查: 1452..1476 有冇 local 增強 (bump)?
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

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"

def load_spt():
    DATA = f"{BASE}/open_problems_fresh/o214_energy_budget_definition/data/spt3g_d1"
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
    h = fits.open(f"{BASE}/open_problems_fresh/o9_high_ell_peaks/data/act_dr6_cmb_sacc.fits")
    d = h['data:cl_00'].data
    cmat = h['covariance'].data
    ell_a = np.array([r['ell'] for r in d])
    val_a = np.array([r['value'] for r in d])
    cov_tt = cmat[:45, :45]
    return ell_a, val_a, cov_tt

def load_planck():
    planck = []
    with open(f"{BASE}/open_problems_fresh/o9_high_ell_peaks/data/planck_tt.txt") as f:
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

print("="*76)
print("1. SPT 高分辨 1437..2962 — 微帶 1452..1476 附近逐 bin")
print("="*76)
print("  SPT bins (TT_150x150):")
for i in range(len(spt_l)):
    if 1350 <= spt_l[i] <= 1650:
        print(f"    ℓ={spt_l[i]:6.1f}  D={spt_d[i]:8.1f}")

print("\n  ACT DR6 bins:")
act_l_hi = act_l[act_l > 0]
for i in range(len(act_l)):
    if 1350 <= act_l[i] <= 1650 and act_d[i] > 0:
        print(f"    ℓ={act_l[i]:6.1f}  D={act_d[i]:9.2f}")

# ── 2. 殘差檢查 (detrend 微帶區) ──────────────────────────────────
print("\n" + "="*76)
print("2. 微帶内 detrend 殘差 (SPT/ACT/Planck)")
print("="*76)
def residual_bump(l, d, sig=None):
    m = (l >= 1400) & (l <= 2000)
    sl = np.polyfit(l[m], np.log(d[m]), 2)
    bg = np.exp(np.polyval(sl, l))
    res = d/bg - 1.0
    mm = (l >= 1452) & (l <= 1476)
    if mm.sum() >= 2:
        r = res[mm].mean()
        s = res[mm].std()/math.sqrt(mm.sum()) if sig is None else 1.0
        return r, s, mm.sum(), res
    return None

for name, l, d, cv in [("SPT", spt_l, spt_d, spt_cov), ("ACT", act_l, act_d, act_cov), ("Planck", pl_l, pl_d, None)]:
    m = l > 0
    r = residual_bump(l[m], d[m], cv)
    if r:
        rb, sb, nb, res = r
        print(f"  {name:>6}: 微帶 [1452,1476] 內 mean res = {rb*100:+5.1f}%  (n={nb} bins)")
        if name == "SPT":
            # SPT 有 cov — sigma 用 cov diag
            for i in range(len(l)):
                if 1440 <= l[i] <= 1490:
                    print(f"      ℓ={l[i]:6.1f}  D={d[i]:7.1f}  res={res[i]*100:+5.1f}%")
        elif name == "ACT":
            for i in range(len(l)):
                if 1440 <= l[i] <= 1490 and d[i] > 0:
                    print(f"      ℓ={l[i]:6.1f}  D={d[i]:8.1f}  res={res[i]*100:+5.1f}%")
        check(f"{name} 微帶殘差 |res|<3% (唔係 bump)", abs(rb) < 0.03, f"({rb*100:+.1f}%)")

print("\n" + "="*76)
print("3. 判決")
print("="*76)
print("""
  微帶預言 REFUTED ⟺ 三實驗喺 1452..1476 都冇 +5% 級 bump
  微帶預言 支持   ⟺ 有一實驗喺嗰段有明顯 local 增強
""")
print(f"RESULT: {PASS}/{TOTAL} PASS (FAIL={FAIL})")
sys.exit(0 if FAIL == 0 else 1)