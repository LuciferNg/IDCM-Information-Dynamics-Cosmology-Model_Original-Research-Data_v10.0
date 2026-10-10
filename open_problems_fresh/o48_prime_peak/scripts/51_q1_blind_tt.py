#!/usr/bin/env python3
"""
O48 Q1.33: 盲測重跑 — 純 TT (215 bins) vs 613-rows 污染版
=============================================================
Q1.31-32 發現: 613 rows = TT+TE+EE; 33 script 讀晒 613 rows →
Plik 平排 ~0.17 係污染假象。重跑 Q1.17 盲測用純 TT:

  純 TT corr (峰+谷 V¾) = +0.607 (50 script D1)
  → Plik 唔係「非判據」, 反而係最強支持!

重驗: 峰only/峰+谷(V63/V¾)/後驗谷/正弦 喺純 TT 下嘅 corr
"""
import math, sys
from collections import defaultdict
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

base = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
DATA = f"{base}/o214_energy_budget_definition/data"
ACT = "/home/wsl/.hermes/cache/scratch/act_dr4/cmbonly_spectra_dr4.01/act_dr4.01_D_ell_TT_cmbonly.txt"

def load_plik():  # 純 TT
    plik = []
    with open(f"{DATA}/planck2018_plik_lite/cl_cmb_plik_v22.dat") as f:
        for line in f:
            p = line.split()
            if len(p) >= 2:
                try:
                    plik.append((float(p[0]), float(p[1])))
                except ValueError:
                    pass
    # 每 ℓ 取最大 (TT), 去重
    d = defaultdict(list)
    for e, v in plik:
        d[e].append(v)
    return sorted((e, max(vs)) for e, vs in d.items())

def load_plik_613():  # 原本污染版 (重現 33)
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
            if len(p) >= 2:
                try:
                    act.append((float(p[0]), float(p[1])))
                except ValueError:
                    pass
    return sorted(act)

def detrend_resid(pairs, order=2):
    ells = np.array([e for e, d in pairs])
    D = np.array([d for e, d in pairs])
    m = D > 0
    ells, D = ells[m], D[m]
    logD = np.log(D)
    c = np.polyfit(ells, logD, order)
    r = D/np.exp(np.polyval(c, ells))
    rn = (r - r.mean())/r.std()
    return rn, ells

phi = (1+5**0.5)/2
F = lambda n: int(round((phi**n - (-phi)**(-n))/math.sqrt(5)))
PEAKS = [221, 527, 815, 1013, 1121, 1337, 1409]
V34 = [221+0.75*306, 527+0.75*288, 815+0.75*306, 1121+0.75*288]
V63 = [527-63, 815-63, 1121-63, 1409-63]

def peak_amp(ell):
    eps = phi**(-1)/4
    j_of = {221: 0, 527: 1, 815: 2, 1121: 3, 1409: 4}
    if int(round(ell)) not in j_of:
        return 0.5
    j = j_of[int(round(ell))]
    geo = [1.0, 1.0/F(1), 1.0/F(2), 1.0/F(3), 1.0/F(4)][j]
    return 3*eps*geo*(33/34)*math.exp(-(ell/9055.0)**1.5)

def model_corr(ds, ells, sigma=50.0, vdepth=0.5, mode="full"):
    """mode: peak / v63 / v34 / post / sine"""
    grid = np.arange(32, 2500, 2.0)
    T = np.zeros_like(grid)
    for p in PEAKS:
        T += peak_amp(p)*np.exp(-0.5*((grid-p)/sigma)**2)
    if mode in ("v63", "full"):
        for v in V63:
            T -= vdepth*np.exp(-0.5*((grid-v)/sigma)**2)
    if mode in ("v34", "full", "post"):
        for v in V34:
            T -= vdepth*np.exp(-0.5*((grid-v)/sigma)**2)
    if mode == "post":
        # 後驗谷 (純 TT 實測) — 唔喺呢度, 用 v34 替代
        pass
    if mode == "sine":
        # 正弦對照: 單一正弦喺峰間距 297
        T = np.sin(2*np.pi*grid/297.0 + 0.3)
    Tint = np.interp(ells, grid, T)
    if Tint.std() == 0:
        return 0.0
    Tn = (Tint - Tint.mean())/Tint.std()
    return float(np.corrcoef(Tn, ds)[0, 1])

print("="*72)
print("純 TT (215 bins) vs 613-rows 污染版 — 盲測重跑")
print("="*72)
plik_tt = load_plik()
plik_613 = load_plik_613()
print(f"純 TT bins: {len(plik_tt)} | 613版 bins: {len(plik_613)}")

tt_res, tt_ells = detrend_resid(plik_tt)
pl_res, pl_ells = detrend_resid(plik_613)

print("\nV¾ corr (510=before? skip)")
print(f"  純 TT (dem.{len(tt_ells)} pts): 峰only {model_corr(tt_res,tt_ells,mode='peak'):+.3f} | "
      f"V63 {model_corr(tt_res,tt_ells,mode='v63'):+.3f} | "
      f"V¾ {model_corr(tt_res,tt_ells,mode='v34'):+.3f} | "
      f"正弦 {model_corr(tt_res,tt_ells,mode='sine'):+.3f}")
print(f"  613版 (dem.{len(pl_ells)} pts): 峰only {model_corr(pl_res,pl_ells,mode='peak'):+.3f} | "
      f"V63 {model_corr(pl_res,pl_ells,mode='v63'):+.3f} | "
      f"V¾ {model_corr(pl_res,pl_ells,mode='v34'):+.3f} | "
      f"正弦 {model_corr(pl_res,pl_ells,mode='sine'):+.3f}")

print("\n" + "="*72)
print("關鍵判斷")
print("="*72)
v34_tt = model_corr(tt_res, tt_ells, mode="v34")
v34_613 = model_corr(pl_res, pl_ells, mode="v34")
peak_tt = model_corr(tt_res, tt_ells, mode="peak")
sine_tt = model_corr(tt_res, tt_ells, mode="sine")
check("K1: 純 TT V¾ corr ≫ 0.17 (舊 Plik 記錄)", v34_tt > 0.45,
      f"{v34_tt:+.3f} vs 0.17")
check("K2: 純 TT V¾ 勝峰only", v34_tt > peak_tt,
      f"{v34_tt:+.3f} vs {peak_tt:+.3f}")
check("K3: 純 TT V¾ 勝正弦", v34_tt > sine_tt,
      f"{v34_tt:+.3f} vs {sine_tt:+.3f}")
check("K4: 純 TT 比 613 版高 (污染壓平)", v34_tt > v34_613,
      f"{v34_tt:+.3f} vs {v34_613:+.3f}")

# 變化量: V¾ − 峰only (谷層面增益)
gain_tt = v34_tt - peak_tt
gain_613 = v34_613 - model_corr(pl_res, pl_ells, mode="peak")
print(f"谷層面增益: 純TT {gain_tt:+.3f} vs 613版 {gain_613:+.3f}")
check("K5: 純 TT 谷增益 ≥ 613 版", gain_tt >= gain_613,
      f"{gain_tt:+.3f} vs {gain_613:+.3f}")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)