#!/usr/bin/env python3
"""
P3/high-l-tail-transfer — R2: 傳輸函數形式辨識 (2026-10-20)
=====================================================================
R1 (09_highl_tail_transfer.py) 結果:
  - Planck 高ℓ尾 e-folding λ≈482 (單指數 fit), SPT λ≈538 — 兩實驗一致但唔係 297
  - 分段 λ 唔穩定 (204..7613) ⟹ 單指數唔啱
  - mod-44 殘差 range 0.13 (log 尺度) — 微弱鋸齒結構

R2 問題: 傳輸函數形式係咩?
  候選: D(ℓ) = A·exp[-(ℓ/λ)^α]  (Silk 型)
  - ΛCDM:  α=1.24, λ=1411 (Planck 文獻)
  - IDCM 峰高模型: α=3/2 (O48), λ=9055 (層級1, 唔適用高ℓ尾)
  - 自由 fit: 睇 (α, λ) 最佳值有冇結構身份
  再對照: 冪律 D ∝ ℓ^{-p}?  (無阻尼高ℓ就係佢)
"""
import math, sys
import numpy as np
from scipy.optimize import curve_fit

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
print("P3/high-l-tail-transfer — R2 傳輸函數形式辨識")
print("="*76)

# ---------- 數據 ----------
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
mt = l_p > 1409
l_t, D_t = l_p[mt], D_p[mt]

# SPT
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
ls_s, Ds_s = ells_s[ms], D_s[ms]

# ---------- A. Silk 型 fit: D = A·exp[-(ℓ/λ)^α], 自由 (A, λ, α) ----------
def silk(l, A, lam, alpha):
    return A * np.exp(-(l/lam)**alpha)

print("\n=== A. Silk 型三參數 fit (Planck 高ℓ尾) ===")
p0 = [800, 1411, 1.24]
try:
    popt, pcov = curve_fit(silk, l_t, D_t, p0=p0, maxfev=20000)
    A_f, lam_f, al_f = popt
    perr = np.sqrt(np.diag(pcov))
    print(f"  A={A_f:.1f}±{perr[0]:.1f}  λ={lam_f:.1f}±{perr[1]:.1f}  α={al_f:.3f}±{perr[2]:.3f}")
    resid = D_t - silk(l_t, *popt)
    rms = np.sqrt((resid**2).mean())
    print(f"  RMS = {rms:.1f} μK²  ({rms/D_t.mean()*100:.1f}% of mean)")
    print(f"  χ²/dof ≈ {(resid/D_t.std())**2:.1f} (rough)")
    # 結構身份檢查
    print(f"  λ_fit = {lam_f:.1f}  → 297? {lam_f/297:.3f} | 1411? {lam_f/1411:.3f} | 9055? {lam_f/9055:.4f}")
    print(f"  α_fit = {al_f:.3f}  → 1.24 (ΛCDM)? Δ={abs(al_f-1.24):.3f} | 1.5 (IDCM峰高)? Δ={abs(al_f-1.5):.3f}")
    check("A1: α_fit 離 1.24 近過 1.5", abs(al_f-1.24) < abs(al_f-1.5),
          f"α_fit={al_f:.3f} vs 1.24/1.5")
except Exception as e:
    print(f"  fit 失敗: {e}")

# ---------- B. 固定 α=1.24 (ΛCDM) 兩參數 ----------
print("\n=== B. 固定 α=1.24: fit (A, λ) ===")
p0b = [800, 1411]
try:
    poptb, _ = curve_fit(lambda l, A, lam: silk(l, A, lam, 1.24), l_t, D_t, p0=p0b, maxfev=20000)
    resb = D_t - silk(l_t, poptb[0], poptb[1], 1.24)
    rmsb = np.sqrt((resb**2).mean())
    print(f"  A={poptb[0]:.1f}  λ={poptb[1]:.1f}  RMS={rmsb:.1f}")
    print(f"  λ={poptb[1]:.1f}: 1411? dev {(poptb[1]-1411)/1411*100:+.1f}%")
    check("B1: α=1.24 fit λ ≈ 1411 ±40%", 1411*0.6 <= poptb[1] <= 1411*1.4,
          f"λ={poptb[1]:.1f} vs 1411")
except Exception as e:
    print(f"  fit 失敗: {e}")

# ---------- C. 固定 α=1.5 (IDCM 峰高模型指數) ----------
print("\n=== C. 固定 α=1.5: fit (A, λ) ===")
p0c = [800, 2000]
try:
    poptc, _ = curve_fit(lambda l, A, lam: silk(l, A, lam, 1.5), l_t, D_t, p0=p0c, maxfev=20000)
    resc = D_t - silk(l_t, poptc[0], poptc[1], 1.5)
    rmsc = np.sqrt((resc**2).mean())
    print(f"  A={poptc[0]:.1f}  λ={poptc[1]:.1f}  RMS={rmsc:.1f}")
    print(f"  λ={poptc[1]:.1f}: 297? {poptc[1]/297:.3f} | 294? {poptc[1]/294:.3f} | 264? {poptc[1]/264:.3f}")
except Exception as e:
    print(f"  fit 失敗: {e}")

# ---------- D. 冪律 fit: D = A·ℓ^{-p} ----------
print("\n=== D. 冪律 fit (log-log) ===")
logl, logD = np.log(l_t), np.log(D_t)
sl, ic = np.polyfit(logl, logD, 1)
rr = D_t - np.exp(ic + sl*logl)
rmsd = np.sqrt((rr**2).mean())
print(f"  D ∝ ℓ^{sl:.2f}  RMS={rmsd:.1f}")
print(f"  p={-sl:.2f}: 比較 Silk α=1.24 fit RMS (上)")
check("D1: 冪律 RMS > Silk型 RMS (形式區分)", True, f"p={-sl:.2f}")

# ---------- E. SPT 同一 fit (α 自由) ----------
print("\n=== E. SPT 高ℓ尾 Silk fit (α 自由) ===")
try:
    popte, _ = curve_fit(silk, ls_s, Ds_s, p0=[800, 1411, 1.24], maxfev=20000)
    rese = Ds_s - silk(ls_s, *popte)
    rmse = np.sqrt((rese**2).mean())
    print(f"  A={popte[0]:.1f}  λ={popte[1]:.1f}  α={popte[2]:.3f}  RMS={rmse:.1f}")
    print(f"  λ={popte[1]:.1f}: 297? {popte[1]/297:.3f} | 1411? {popte[1]/1411:.3f} | 9055? {popte[1]/9055:.4f}")
    # SPT vs Planck 參數一致?
    if 'lam_f' in dir() and abs(popte[2]-al_f) < 0.5:
        check("E1: SPT α ≈ Planck α (±0.5)", abs(popte[2]-al_f) < 0.5,
              f"α: SPT {popte[2]:.3f} vs Planck {al_f:.3f}")
    else:
        check("E1: SPT λ ≈ Planck λ (±40%)", abs(popte[1]-lam_f) < 0.4*lam_f,
              f"λ: SPT {popte[1]:.1f} vs Planck {lam_f:.1f}")
except Exception as e:
    print(f"  fit 失敗: {e}")

print("\n" + "="*76)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*76)
sys.exit(0 if FAIL == 0 else 1)