#!/usr/bin/env python3
"""
O48 Q1.20: SPT-3G covariance χ² 檢驗 —「峰+谷」模型統計顯著性
=============================================================
最嚴格閉合: 唔止 correlation — 用 SPT-3G TT_150x150 完整 covariance (52×52)
檢驗「峰+谷 V¾」模型嘅結構信號係咪統計顯著。

方法:
  1. 抽出 TT_150x150 block (offset 732, 52 bins)
  2. detrend residual r (同 corr 分析一致, log-二次多項)
  3. 模型 t: 峰梳 + 谷梳 (V¾, vdepth=0.5, σ=50) @ band centers
  4. fit amplitude a (單一標量, 最小 χ²)
  5. 全 covariance: χ² = (r − a·t)ᵀ C⁻¹ (r − a·t)
  6. 對照: null (冇結構) / 峰only / V¾ / 正弦 — Δχ² 顯著性

注意: detrend 改變 covariance (非嚴格) — 標註; 用 covariance diagonal 交叉驗證
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

phi = (1+5**0.5)/2
F = lambda n: int(round((phi**n - (-phi)**(-n))/math.sqrt(5)))

base = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
DATA = f"{base}/o214_energy_budget_definition/data/spt3g_d1"

bdp = np.loadtxt(f"{DATA}/SPT3G_D1_TnE_bdp.txt")
cov = np.loadtxt(f"{DATA}/SPT3G_D1_TnE_cov.dat")
win = np.loadtxt(f"{DATA}/TT_150x150_window.txt")

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
C = cov[off:off+52, off:off+52]
lgr = win[:, 0]
centers = np.array([lgr[np.argmax(win[:, b])] for b in range(1, 53)])

# ---------- detrend residual ----------
mask = tt150 > 0
ells = centers[mask]
D = tt150[mask]
Cm = C[mask][:, mask]
logD = np.log(D)
coef = np.polyfit(ells, logD, 2)
env = np.exp(np.polyval(coef, ells))
r = D - env          # μK² 單位 residual (同 covariance 單位匹配)
tn = (r - r.mean())/r.std()
print(f"SPT TT150: {len(ells)} bins (mask {len(mask)-len(ells)} 負值), ℓ {ells[0]:.0f}..{ells[-1]:.0f}")

# ---------- 模型 ----------
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

def model_t(ells_arr, include_valleys=True, vdepth=0.5, sig=50.0):
    t = np.zeros_like(ells_arr, dtype=float)
    for p in PEAKS:
        t += peak_amp(p)*np.exp(-0.5*((ells_arr-p)/sig)**2)
    if include_valleys:
        for v in V34:
            t -= vdepth*np.exp(-0.5*((ells_arr-v)/sig)**2)
    return t

def chi2_given(t, r, Cmat):
    t = t - t.mean() if False else t  # 保留 fit amplitude 處理
    # fit amplitude a: 最小化 (r-a t)^T C^-1 (r-a t)
    Cinv = np.linalg.pinv(Cmat)
    a = (t.T @ Cinv @ r) / (t.T @ Cinv @ t)
    resid = r - a*t
    return float(resid.T @ Cinv @ resid), a

print("\n" + "="*72)
print("χ² 檢驗 (全 covariance)")
print("="*72)
rr = r - r.mean()   # 中心化 (detrend 後)
models = {
    "null (冇峰谷結構)": np.zeros_like(rr),
    "峰only": model_t(ells, include_valleys=False),
    "峰+谷 V¾": model_t(ells, include_valleys=True),
    "正弦對照": np.sin(2*np.pi*ells/297 + np.pi/3),
}
results = {}
for lab, t in models.items():
    if t.std() == 0:
        chi2, a = float(rr.T @ np.linalg.pinv(Cm) @ rr), 0.0
    else:
        tc = (t - t.mean())/t.std()  # 標準化模型 (幅度 fit)
        chi2, a = chi2_given(tc, rr, Cm)
    results[lab] = chi2
    dof = len(ells) - 1
    print(f"  {lab:<16}: χ²={chi2:8.1f}  χ²/dof={chi2/dof:6.2f}  (amp={a:+.3f})")

# Δχ² vs null
print("\nΔχ² vs null:")
base_chi = results["null (冇峰谷結構)"]
for lab in ["峰only", "峰+谷 V¾", "正弦對照"]:
    dchi = base_chi - results[lab]
    # Δχ² 顯著: Δχ²>6.6 (1 dof, 1%), >10.8 (1 dof, 0.1%)
    print(f"  {lab:<16}: Δχ²={dchi:8.1f}  (Δχ²>6.6 = 1% 顯著)")

best_model = min(results, key=lambda k: results[k] if k != "null (冇峰谷結構)" else 1e9)
best_chi = results[best_model]
# 判據: 峰+谷 係咪最佳 + 顯著改善
dchi_pv = base_chi - results["峰+谷 V¾"]
dchi_peak = base_chi - results["峰only"]
check("C1: 峰+谷 V¾ Δχ²>6.6 (1% 顯著)", dchi_pv > 6.6, f"Δχ²={dchi_pv:.1f}")
check("C2: 峰+谷 V¾ 勝過峰only", results["峰+谷 V¾"] < results["峰only"], 
      f"{results['峰+谷 V¾']:.1f} < {results['峰only']:.1f}")
check("C3: 峰+谷 V¾ 勝過正弦", results["峰+谷 V¾"] < results["正弦對照"],
      f"{results['峰+谷 V¾']:.1f} < {results['正弦對照']:.1f}")
check("C4: χ²/dof 最低模型係峰+谷", best_model == "峰+谷 V¾",
      f"best={best_model} (χ²={best_chi:.1f})")

print("\n" + "="*72)
print("交叉驗證: diagonal covariance 近似")
print("="*72)
sigi = np.sqrt(np.diag(Cm))
for lab, t in models.items():
    if t.std() == 0:
        chi2d = float(np.sum((rr/sigi)**2))
    else:
        tc = (t - t.mean())/t.std()
        a = np.sum(tc*rr/sigi**2)/np.sum(tc**2/sigi**2)
        chi2d = float(np.sum(((rr - a*tc)/sigi)**2))
    print(f"  {lab:<16}: χ²_diag={chi2d:8.1f}  χ²/dof={chi2d/(len(ells)-1):6.2f}")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)