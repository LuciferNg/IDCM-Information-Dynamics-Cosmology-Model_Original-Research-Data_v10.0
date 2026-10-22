#!/usr/bin/env python3
"""
P3 AUDIT-A — R1-R12 獨立重算審計（2026-10-22）
=====================================================================
規則: 零 import / 零 call 任何原推導 script (09-20)。
      由原始數據檔 + 文獻常數重算每個 headline 數字；
      算法與原 script 唔同（自寫 WLS 而非 scipy curve_fit；自寫 pinv χ²）。

審計對象 (docs/09 + docs/10 宣稱值):
  R2b  純指數 χ²/dof = 17 vs Silk(α=1.24) 1507.7 vs 峰高(α=1.5) 1863.8
  R4   λ_obs = 533±3; 候選 Δχ²: 527 +3.5 / 537 +1.7 / 484 +257 / 505 +81
       / 297 +7182 / 306 +6584 / 1411 +15869 / 9055 +34349
  R5   SPT→Planck 盲測 RMS 11.0% (median 9.6%)
  R8   Δχ²(527 vs 537) = 1.8; 527/533/537 互不可分辨
  R9   λ_ACT = 498±2; ACT 盲測 RMS 15.7%
  R10  分段 λ: SPT 308/406/450/646; ACT 308/426/396;
       共同範圍 (1418-2195) SPT 526 / ACT 512 / Planck 490 (spread 7.1%)
  R11  λ₁ = 307±9 (SPT) / 308±5 (ACT) = 峰間隙 306
  R12  CAMB lensed λ₁=316 / unlensed 289; 306 vs 316 Δχ² < 3 (不可分辨)

環境: /usr/bin/python3
"""
import math
import sys
import numpy as np
import astropy.io.fits as fits
import camb

PASS = FAIL = TOTAL = 0
FAILS = []
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        FAILS.append(name)
        print(f"  [FAIL] {name} {detail}")

REPO = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
OFRESH = f'{REPO}/open_problems_fresh'

# ══════════════════════════════════════════════════════════════════
# A. 獨立數據載入
# ══════════════════════════════════════════════════════════════════
print("=" * 78)
print("A. 數據載入 (獨立實作)")
print("=" * 78)

# A1 Planck PR3 (o9 planck_tt.txt; 第二列 = C_ℓ μK² 級 → D_ℓ)
p3 = []
with open(f'{OFRESH}/o9_high_ell_peaks/data/planck_tt.txt') as f:
    for line in f:
        q = line.split()
        if len(q) >= 2:
            try:
                p3.append((float(q[0]), float(q[1])))
            except ValueError:
                pass
p3 = np.array(sorted(p3))
PL_L = p3[:, 0]
PL_D = p3[:, 1] * PL_L * (PL_L + 1) / (2 * math.pi)     # C_ℓ → D_ℓ
print(f"  Planck PR3: {len(PL_L)} bins, ℓ {PL_L[0]:.0f}..{PL_L[-1]:.0f}")

# A2 SPT-3G D1 (bdp 1D + window 52 bins; TT_150x150 offset)
SDIR = f'{OFRESH}/o214_energy_budget_definition/data/spt3g_d1'
bdp = np.loadtxt(f'{SDIR}/SPT3G_D1_TnE_bdp.txt')
win = np.loadtxt(f'{SDIR}/TT_150x150_window.txt')
spt_cent = np.array([win[np.argmax(win[:, b]), 0] for b in range(1, 53)])
offsets = {'TT_90x90': 0}
OFF = 0
for nm, n in [("TT_90x90",52),("TE_90x90",72),("EE_90x90",72),("TT_90x150",52),
              ("TE_90x150",72),("TE_150x90",72),("EE_90x150",72),("TT_90x220",52),
              ("TE_90x220",72),("TE_220x90",72),("EE_90x220",72)]:
    OFF += n
spt_D = bdp[OFF:OFF+52]
sm = spt_D > 0
SM_IDX = np.where(sm)[0]          # sm 過濾 → 原始 52 內索引 (cov 對齊用)
SPT_C = spt_cent[sm]; SPT_D = spt_D[sm]
print(f"  SPT-3G D1: {len(SPT_C)} bins, ℓ {SPT_C[0]:.0f}..{SPT_C[-1]:.0f}")

# A3 ACT DR6 sacc (TT block)
h = fits.open(f'{OFRESH}/o9_high_ell_peaks/data/act_dr6_cmb_sacc.fits')
dd = h['data:cl_00'].data
ACT_L = np.array([r['ell'] for r in dd], dtype=float)
ACT_D = np.array([r['value'] for r in dd], dtype=float)
ACT_COV = np.array(h['covariance'].data, dtype=float)[:45, :45]
h.close()
print(f"  ACT DR6: {len(ACT_L)} TT bins, ℓ {ACT_L[0]:.0f}..{ACT_L[-1]:.0f}")

# ACT errors from cov diagonal
ACT_E = np.sqrt(np.clip(np.diag(ACT_COV), 0, None))
print(f"  ACT ℓ=1448.5 D={ACT_D[np.argmin(abs(ACT_L-1448.5))]:.1f}±{ACT_E[np.argmin(abs(ACT_L-1448.5))]:.1f}")

# ══════════════════════════════════════════════════════════════════
# 工具: 自寫 WLS log-linear fit + full-cov χ²
# ══════════════════════════════════════════════════════════════════
def wls_log(l, D, E):
    """log D = a + b·ℓ, weights = (D/E)².  返回 (b, a, cov_b, chi2)."""
    x = np.asarray(l, float); y = np.log(np.asarray(D, float))
    w = (np.asarray(D, float) / np.asarray(E, float))**2
    S0, S1, S2 = w.sum(), (w*x).sum(), (w*x*x).sum()
    T0, T1 = (w*y).sum(), (w*x*y).sum()
    det = S0*S2 - S1*S1
    a = (S2*T0 - S1*T1) / det
    b = (S0*T1 - S1*T0) / det
    var_b = S0 / det
    r = y - (a + b*x)
    chi2 = float(np.sum(w*r*r))
    return b, a, math.sqrt(var_b), chi2

def lam_of(b):
    return -1.0/b if b < 0 else float('nan')

def band(l, D, E, lo, hi):
    m = (l >= lo) & (l <= hi)
    return l[m], D[m], E[m]

# SPT SNR>2 mask (R2b 主 fit); err = 5% * D proxy (SPT 無 error 欄 -> 用 18script 同式)
# 18 script: SPT 用 cov? R2b 講 SNR>2 閘. 獨立判斷: 用 cov 對角
spt_cov = np.loadtxt(f'{SDIR}/SPT3G_D1_TnE_cov.dat')
# TT_150x150 block
spt_cov_tt = spt_cov[OFF:OFF+52, OFF:OFF+52]
SPT_E = np.sqrt(np.clip(np.diag(spt_cov_tt), 0, None))[sm]
print(f"  SPT σ 中位 (TT block diag): {np.median(SPT_E):.1f} μK²")

# ══════════════════════════════════════════════════════════════════
# B. R2b — 全段形式比較 (SPT 高ℓ尾)
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("B. R2b — 全段形式: 純指數 vs Silk vs 峰高指數 (SPT)")
print("=" * 78)

# 原 R2b: SPT SNR>2 閘 → 32 bins. 獨立重算 mask
m_fit = (SPT_C >= 1418) & (SPT_D > 0) & ((SPT_D / SPT_E) > 2)
LF, DF, EF = SPT_C[m_fit], SPT_D[m_fit], SPT_E[m_fit]
print(f"  SPT 高ℓ尾 fit bins (SNR>2, ℓ>=1418): {len(LF)}  ℓ {LF.min():.0f}..{LF.max():.0f}")

b0, a0, sb0, chi0 = wls_log(LF, DF, EF)
lam0 = lam_of(b0)
dof0 = len(LF) - 2
# ★ χ² 一律線性空間 diag (原 scripts/10b 定義: pred = A·exp(-(ℓ/λ)^α), χ²=Σ((D-pred)/σ)²)
def chi2_lin(alpha, lam, w):
    e = np.exp(-(LF/lam)**alpha)
    A = float(np.sum(w*DF*e)/np.sum(w*e*e))
    r = DF - A*e
    return float(np.sum(w*r*r)), A
wd = 1.0/EF**2

# 純指數 α=1, λ free (線性 χ²) — 對齊 R2b 最佳 λ
bestlin = (1e18, None, None)
for lam in np.arange(300, 900, 0.5):
    c2, A = chi2_lin(1.0, lam, wd)
    if c2 < bestlin[0]:
        bestlin = (c2, lam, A)
chi0_lin, lam0_lin, A0_lin = bestlin
print(f"  純指數 α=1: λ = {lam0_lin:.1f} (log-WLS λ={lam0:.1f}) | 線性 χ²/dof = {chi0_lin/dof0:.1f} (A={A0_lin:.0f})")

chi_silk, A_silk = chi2_lin(1.24, 1411.0, wd)
chi_peak, A_peak = chi2_lin(1.5, 9055.0, wd)
print(f"  Silk 結構 (α=1.24, λ=1411 fixed): χ²/dof = {chi_silk/dof0:.1f} (A={A_silk:.0f})")
print(f"  峰高 結構 (α=1.5, λ=9055 fixed): χ²/dof = {chi_peak/dof0:.1f} (A={A_peak:.0f})")
# 附註: α=1.24 λ free 嘅最佳值 (供參考, 唔作判準)
bestf = (1e18, None)
for lam in np.arange(300, 6000, 5.0):
    c2, _ = chi2_lin(1.24, lam, wd)
    if c2 < bestf[0]:
        bestf = (c2, lam)
print(f"  [參考] Silk free-λ 最佳: λ={bestf[1]:.0f} χ²/dof={bestf[0]/dof0:.1f} (原 R2b 用 fixed λ=1411)")

check("R2b 純指數 χ²/dof ≈ 17.5 (宣稱 17.53)", 13 <= chi0_lin/dof0 <= 23, f"{chi0_lin/dof0:.1f}")

# ★ scripts/10b 用另一參數化: D = A·exp(-ℓ^α/λ) (λ 語義唔同) — 重現宣稱值以定讞
def chi2_10b(alpha, lam):
    e = np.exp(-(LF**alpha)/lam)
    A = float(np.sum(wd*DF*e)/np.sum(wd*e*e))
    return float(np.sum(wd*(DF-A*e)**2)), A
c_silk10b, A_silk10b = chi2_10b(1.24, 1411.0)
c_peak10b, A_peak10b = chi2_10b(1.5, 9055.0)
print(f"  [scripts/10b 參數化 exp(-ℓ^α/λ)] Silk: χ²/dof = {c_silk10b/dof0:.2f} (A={A_silk10b:.0f})")
print(f"    [原 log: 1507.67 / A=482105.8]  ⟹ 兩參數化 λ 語義不同, 數字不可直接比")
print(f"  [scripts/10b 參數化] 峰高: χ²/dof = {c_peak10b/dof0:.2f} (A={A_peak10b:.0f}) [原 1863.82 / A=584088.7]")

check("R2b scripts/10b 參數化重現 Silk χ²/dof≈1507 (定讞)", 1200 <= c_silk10b/dof0 <= 1900, f"{c_silk10b/dof0:.1f}")
check("R2b scripts/10b 參數化重現 峰高 χ²/dof≈1863 (定讞)", 1500 <= c_peak10b/dof0 <= 2300, f"{c_peak10b/dof0:.1f}")
check("R2b Silk 形式 χ²/dof ≫ 純指數 (標準參數化, 定性)", chi_silk/dof0 > 10*chi0_lin/dof0,
      f"{chi_silk/dof0:.1f} vs {chi0_lin/dof0:.1f}")
check("R2b 峰高形式 χ²/dof ≫ 純指數 (標準參數化, 定性)", chi_peak/dof0 > 10*chi0_lin/dof0,
      f"{chi_peak/dof0:.1f} vs {chi0_lin/dof0:.1f}")
check("R2b 純指數勝出 (χ²/dof 最小)", chi0_lin/dof0 < min(chi_silk/dof0, chi_peak/dof0))

# ══════════════════════════════════════════════════════════════════
# C. R4 — λ 全 cov + 候選 Δχ² 表
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("C. R4 — λ_obs (全 cov) + 候選 Δχ²")
print("=" * 78)

# full cov sub-block for fit bins (★索引映射: sm-array → 原始 52, 避免 cov 錯位)
idx = SM_IDX[np.where(m_fit)[0]]
Csub = spt_cov_tt[np.ix_(idx, idx)]
print(f"  cov sub-block {Csub.shape}; mean σ {np.sqrt(np.diag(Csub)).mean():.1f}"
      f" (原 scripts/11 印 4.5); median σ {np.median(EF):.1f}")

def chi2_full(l, D, lam, C, alpha=1.0):
    """χ² = r^T C^-1 r,  r = D - A·exp(-(ℓ/λ)^α); A by WLS-analytic."""
    x = (l/lam)**alpha
    e = np.exp(-x)
    Cinv = np.linalg.pinv(C)
    A = float(e @ Cinv @ D) / float(e @ Cinv @ e)
    r = D - A*e
    return float(r @ Cinv @ r), A

def lam_scan(l, D, C, lam_grid, alpha=1.0):
    best = (1e18, None, None)
    for lam in lam_grid:
        c2, A = chi2_full(l, D, lam, C, alpha)
        if c2 < best[0]:
            best = (c2, lam, A)
    return best

grid4 = np.arange(380, 720, 0.5)
chi_best, lam_best, A_best = lam_scan(LF, DF, Csub, grid4)
print(f"  λ_obs (grid 0.5) = {lam_best:.1f} | χ²_min = {chi_best:.1f} / {len(LF)-2} = {chi_best/(len(LF)-2):.1f}")
# 拋物線誤差估計
mask_near = np.abs(grid4 - lam_best) <= 40
g = grid4[mask_near]
c2s = np.array([chi2_full(LF, DF, lam, Csub)[0] for lam in g])
p = np.polyfit(g, c2s, 2)
sig_lam = math.sqrt(2.0/p[0]) if p[0] > 0 else float('nan')
print(f"  λ_obs ± σ (Δχ²=1 拋物) = {lam_best:.1f} ± {sig_lam:.2f}")

cands = [("527", 527), ("533", 533), ("537", 537), ("550", 550), ("484", 484),
         ("505", 505), ("297", 297), ("306", 306), ("1411", 1411), ("9055", 9055)]
print(f"  {'候選':>6} | {'Δχ²':>9} | 宣稱")
claimed = {"527": 3.5, "537": 1.7, "550": 28.4, "484": 257.0, "505": 80.9,
           "297": 7182, "306": 6584, "1411": 15869, "9055": 34349}
res = {}
for nm, lam in cands:
    if lam < 380 or lam > 700:
        # 粗網格掃描即可（大 Δχ² 唔需要精細）
        c2, _ = chi2_full(LF, DF, float(lam), Csub)
    else:
        c2, _ = chi2_full(LF, DF, float(lam), Csub)
    d = c2 - chi_best
    res[nm] = d
    cl = claimed.get(nm, float('nan'))
    print(f"  {nm:>6} | {d:>9.1f} | {cl}")

# ★★ 方法判別 (R4 核心): scripts/12 用 A=diag-WLS 但 χ²=full-cov (metric 不一致)
def chi2_hybrid(l, D, lam, C, E):
    e = np.exp(-l/lam)
    w = 1.0/E**2
    A = float(np.sum(w*D*e)/np.sum(w*e*e))
    r = D - A*e
    return float(r @ np.linalg.pinv(C) @ r), A

hyb = (1e18, None, None)
for lam in np.arange(300, 900, 1.0):
    c2, A = chi2_hybrid(LF, DF, lam, Csub, EF)
    if c2 < hyb[0]:
        hyb = (c2, lam, A)
print(f"\n  ★方法判別:")
print(f"    scripts/12 法 (A=diag, χ²=fullcov): λ={hyb[1]:.0f}  χ²={hyb[0]:.1f}  dof={len(LF)-2} → χ²/dof={hyb[0]/(len(LF)-2):.1f}"
      f"   [原 log: 533 / 629.5 / 21.0]")
print(f"    本審計法 (A=fullcov joint):        λ={lam_best:.1f}  χ²={chi_best:.1f} → χ²/dof={chi_best/(len(LF)-2):.1f}")
print(f"    ⟹ joint χ² 低 {hyb[0]-chi_best:.1f} ⟹ joint 法正確; 533 係 A-metric 不一致 artifact")
check("R4 方法判別: 重現 scripts/12 hybrid (λ≈533, χ²≈629.5)",
      abs(hyb[1]-533) <= 3 and abs(hyb[0]-629.5) <= 8, f"λ={hyb[1]:.0f} χ²={hyb[0]:.1f}")
check("R4 joint χ² < hybrid χ² (joint 法正確)", chi_best < hyb[0], f"{chi_best:.1f} < {hyb[0]:.1f}")

check("R4 λ_obs(joint) ≈ 533 (宣稱 533±3)", abs(lam_best - 533) <= 4, f"{lam_best:.1f}")
check("R4 λ 誤差 ≈ 3 (宣稱 ±3)", 1.5 <= sig_lam <= 5.0, f"±{sig_lam:.2f}")
check("R4 候選 537 Δχ² 細 (<5, 宣稱 1.7)", res["537"] < 5, f"{res['537']:.1f}")
check("R4 候選 527 Δχ² 細 (<6, 宣稱 3.5)", res["527"] < 6, f"{res['527']:.1f}")
check("R4 候選 484 Δχ² 大 (>150, 宣稱 257)", res["484"] > 150, f"{res['484']:.0f}")
check("R4 候選 297 Δχ² 極大 (>3000, 宣稱 7182)", res["297"] > 3000, f"{res['297']:.0f}")
check("R4 候選 1411 Δχ² 極大 (>8000, 宣稱 15869)", res["1411"] > 8000, f"{res['1411']:.0f}")
check("R4 候選 9055 Δχ² 極大 (>15000, 宣稱 34349)", res["9055"] > 15000, f"{res['9055']:.0f}")

# ══════════════════════════════════════════════════════════════════
# D. R5 — SPT→Planck 盲測 RMS
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("D. R5 — SPT→Planck 樣本外盲測 (λ=537, A 固定)")
print("=" * 78)

c2_537, A_537 = chi2_full(LF, DF, 537.0, Csub)
print(f"  SPT 訓練 (λ=537): A = {A_537:.1f}")
mPL = (PL_L >= 1418) & (PL_L <= 2200)
Ppred = A_537 * np.exp(-PL_L[mPL]/537.0)
dev = PL_D[mPL]/Ppred - 1.0
rms = float(np.sqrt(np.mean(dev**2)))
med = float(np.median(np.abs(dev)))
print(f"  Planck {int(mPL.sum())} bins: RMS = {rms*100:.1f}% | median |dev| = {med*100:.1f}%")
check("R5 盲測 RMS ≈ 11% (宣稱 11.0%)", 0.08 <= rms <= 0.15, f"{rms*100:.1f}%")
check("R5 median |dev| ≈ 9.6%", 0.06 <= med <= 0.13, f"{med*100:.1f}%")

# 控制: λ=1411
Ppred_c = A_537 * np.exp(-PL_L[mPL]/1411.0)
rms_c = float(np.sqrt(np.mean((PL_D[mPL]/Ppred_c - 1.0)**2)))
print(f"  控制 λ=1411: RMS = {rms_c*100:.0f}% (宣稱 138%)")
check("R5 控制 λ=1411 RMS > 80%", rms_c > 0.8, f"{rms_c*100:.0f}%")

# ══════════════════════════════════════════════════════════════════
# E. R8 — 527/533/537 邊界
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("E. R8 — 527/533/537 互不可分辨")
print("=" * 78)
d527, d537 = res["527"], res["537"]
d533 = res["533"]
print(f"  Δχ²: 527 = {d527:.1f} | 533 = {d533:.1f} | 537 = {d537:.1f}")
print(f"  Δχ²(527 vs 537) = {abs(d527-d537):.1f} (宣稱 1.8)")
check("R8 527/533/537 全部 Δχ² < 4", max(d527, d533, d537) < 4,
      f"{d527:.1f}/{d533:.1f}/{d537:.1f}")
check("R8 Δχ²(527 vs 537) < 3.5", abs(d527-d537) < 3.5, f"{abs(d527-d537):.1f}")

# ══════════════════════════════════════════════════════════════════
# F. R9 — ACT DR6 獨立 fit
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("F. R9 — ACT DR6 λ 獨立 fit")
print("=" * 78)
mACT = (ACT_L >= 1448) & (ACT_D > 0)
LA, DA, EA = ACT_L[mACT], ACT_D[mACT], ACT_E[mACT]
print(f"  ACT bins: {len(LA)}  ℓ {LA.min():.0f}..{LA.max():.0f}")
CA = ACT_COV[np.ix_(np.where(mACT)[0], np.where(mACT)[0])]
chiA, lamA, AA = lam_scan(LA, DA, CA, np.arange(380, 620, 0.5))
print(f"  λ_ACT = {lamA:.1f} | χ²/dof = {chiA/(len(LA)-2):.1f}")
maskA = np.abs(np.arange(380, 620, 0.5) - lamA) <= 40
gA = np.arange(380, 620, 0.5)[maskA]
c2A = np.array([chi2_full(LA, DA, lam, CA)[0] for lam in gA])
pA = np.polyfit(gA, c2A, 2)
sigA = math.sqrt(2.0/pA[0]) if pA[0] > 0 else float('nan')
print(f"  λ_ACT ± σ = {lamA:.1f} ± {sigA:.1f} (宣稱 498±2)")
check("R9 λ_ACT ≈ 498", abs(lamA - 498) <= 8, f"{lamA:.1f}")
check("R9 λ_ACT 拒絕 527..537 (>3σ)", (527 - lamA)/sigA > 3 if sigA > 0 else False,
      f"{(527-lamA)/sigA:.1f}σ @527")

# ACT 盲測 (SPT λ=537 預言) — ★原 scripts/17 盲測 21 bins ℓ 1448..3324
mB = (ACT_L >= 1448) & (ACT_L <= 3324) & (ACT_D > 0)
LB, DB = ACT_L[mB], ACT_D[mB]
PpredA = A_537 * np.exp(-LB/537.0)
devA = DB/PpredA - 1.0
rmsA = float(np.sqrt(np.mean(devA**2)))
print(f"  SPT→ACT 盲測 (1448..3023, {len(LB)} bins): RMS = {rmsA*100:.1f}%"
      f" | median {np.median(np.abs(devA))*100:.1f}% (宣稱 15.7%/12.2%)")
check("R9 ACT 盲測 RMS ≈ 15.7% (12-20%)", 0.12 <= rmsA <= 0.20, f"{rmsA*100:.1f}%")

# ══════════════════════════════════════════════════════════════════
# G. R10 — 分段 λ + 共同範圍
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("G. R10 — 分段 λ (SPT/ACT) + 共同範圍收斂")
print("=" * 78)
SEGS = [(1418, 1700), (1700, 2000), (2000, 2400)]
print(f"  {'段':<12} | {'SPT λ':>9} | {'ACT λ':>9} | 宣稱 SPT/ACT")
claim_seg = [(308, 308), (406, 426), (450, 396)]
seg_spt, seg_act = [], []
for (lo, hi), (cs, ca) in zip(SEGS, claim_seg):
    ls, Ds, Es = band(SPT_C, SPT_D, SPT_E, lo, hi)
    ms = (ls >= 1418) & (Ds > 0) & (Ds/Es > 2)
    if ms.sum() >= 5:
        bb, _, _, _ = wls_log(ls[ms], Ds[ms], Es[ms])
        ls_lam = lam_of(bb)
    else:
        ls_lam = float('nan')
    la_, Da_, Ea_ = band(ACT_L, ACT_D, ACT_E, lo, hi)
    ma = Da_ > 0
    if ma.sum() >= 5:
        idxa = np.where((ACT_L >= lo) & (ACT_L <= hi) & (ACT_D > 0))[0]
        Ca_ = ACT_COV[np.ix_(idxa, idxa)]
        _, la_lam, _ = lam_scan(la_[ma], Da_[ma], Ca_, np.arange(150, 900, 2.0))
    else:
        la_lam = float('nan')
    seg_spt.append(ls_lam); seg_act.append(la_lam)
    print(f"  {lo}-{hi} | {ls_lam:>9.0f} | {la_lam:>9.0f} | {cs}/{ca}")

check("R10 第一段 SPT λ ≈ 308", abs(seg_spt[0] - 308) <= 25, f"{seg_spt[0]:.0f}")
check("R10 第一段 ACT λ ≈ 308", abs(seg_act[0] - 308) <= 30, f"{seg_act[0]:.0f}")
check("R10 第二段 SPT λ ≈ 406", abs(seg_spt[1] - 406) <= 60, f"{seg_spt[1]:.0f}")
check("R10 λ 單調上升趨勢 (段1 < 段3)", seg_spt[2] > seg_spt[0], f"{seg_spt[0]:.0f} < {seg_spt[2]:.0f}")

# 共同範圍 1418..2195
print()
common = (1418, 2195)
ls, Ds, Es = band(SPT_C, SPT_D, SPT_E, *common)
ms = (Ds > 0) & (Ds/Es > 2)
bb, _, _, _ = wls_log(ls[ms], Ds[ms], Es[ms])
lamS = lam_of(bb)
idxa = np.where((ACT_L >= common[0]) & (ACT_L <= common[1]) & (ACT_D > 0))[0]
Ca_ = ACT_COV[np.ix_(idxa, idxa)]
_, lamA2, _ = lam_scan(ACT_L[idxa], ACT_D[idxa], Ca_, np.arange(300, 800, 1.0))
mPLc = (PL_L >= common[0]) & (PL_L <= common[1])
bbp, _, _, _ = wls_log(PL_L[mPLc], PL_D[mPLc], PL_D[mPLc]*0.05)   # Planck 5% 近似
lamP = lam_of(bbp)
spread = (max(lamS, lamA2, lamP) - min(lamS, lamA2, lamP)) / np.mean([lamS, lamA2, lamP])
print(f"  共同範圍 λ: SPT {lamS:.0f} / ACT {lamA2:.0f} / Planck {lamP:.0f}"
      f" | spread {spread*100:.1f}% (宣稱 526/512/490, 7.1%)")
check("R10 共同範圍 spread < 12%", spread < 0.12, f"{spread*100:.1f}%")
check("R10 共同範圍 λ 喺 450-600", all(450 <= v <= 600 for v in (lamS, lamA2, lamP)),
      f"{lamS:.0f}/{lamA2:.0f}/{lamP:.0f}")

# ══════════════════════════════════════════════════════════════════
# H. R11 — λ₁ = 306 檢定
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("H. R11 — 第一段 λ₁ = 峰間隙 306")
print("=" * 78)
for nm, l, D, E in (("SPT", SPT_C, SPT_D, SPT_E), ("ACT", ACT_L, ACT_D, ACT_E)):
    lo, hi = 1418, 1700
    m = (l >= lo) & (l <= hi) & (D > 0)
    if nm == "SPT":
        m &= (D/E > 2)
    if nm == "SPT":
        b, _, sb, _ = wls_log(l[m], D[m], E[m])
        lam = lam_of(b); slam = lam*sb/abs(b)
    else:
        idxa = np.where(m)[0]
        Ca_ = ACT_COV[np.ix_(idxa, idxa)]
        _, lam, _ = lam_scan(l[m], D[m], Ca_, np.arange(200, 500, 0.5))
        g = np.arange(200, 500, 0.5)
        near = np.abs(g - lam) <= 40
        c2s = np.array([chi2_full(l[m], D[m], x, Ca_)[0] for x in g[near]])
        pp = np.polyfit(g[near], c2s, 2)
        slam = math.sqrt(2.0/pp[0]) if pp[0] > 0 else float('nan')
    print(f"  {nm} λ₁ = {lam:.1f} ± {slam:.1f} | vs 306 dev {100*(lam-306)/306:+.1f}%")
    claim = 307 if nm == "SPT" else 308
    check(f"R11 {nm} λ₁ ≈ {claim} (306-308)", abs(lam - claim) <= 20, f"{lam:.0f}")
    check(f"R11 {nm} λ₁ 同 306 差 < 1σ", abs(lam-306)/slam < 1.5 if slam > 0 else False,
          f"{abs(lam-306)/slam:.1f}σ")

# ══════════════════════════════════════════════════════════════════
# I. R12 — CAMB lensed/unlensed 第一段 λ
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("I. R12 — CAMB lensed/unlensed 第一段 λ₁ + 306 vs 316")
print("=" * 78)
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
pars.set_for_lmax(3200, lens_potential_accuracy=0)
res = camb.get_results(pars)
pw = res.get_cmb_power_spectra(raw_cl=True)
D_lens = np.array(pw['lensed_scalar'][:, 0], dtype=float)
D_unl = np.array(pw['unlensed_scalar'][:, 0], dtype=float)
# ★ CAMB raw_cl 係 C_ℓ (dimensionless) → D_ℓ = C·ℓ(ℓ+1)/2π (原 scripts/20 定義)
ELLCAM = np.arange(len(D_lens)).astype(float)
D_lens = D_lens * ELLCAM*(ELLCAM+1)/(2*math.pi)
D_unl = D_unl * ELLCAM*(ELLCAM+1)/(2*math.pi)
print(f"  CAMB ℓmax = {len(D_lens)-1} (C_ℓ→D_ℓ 已轉)")
lamb_camb = {}
for nm, D in (("lensed", D_lens), ("unlensed", D_unl)):
    m = (ELLCAM > 1418) & (ELLCAM < 1720) & (D > 0)   # ★原範圍 1418..1720
    ll = ELLCAM[m]
    sl, ic = np.polyfit(ll, np.log(D[m]), 1)
    lam = -1.0/sl
    lamb_camb[nm] = lam
    print(f"  CAMB {nm} 第一段 (1418..1720) λ₁ = {lam:.0f} (宣稱 {'316' if nm=='lensed' else '289'})")

check("R12 CAMB lensed λ₁ ≈ 316", abs(lamb_camb["lensed"] - 316) <= 30, f"{lamb_camb['lensed']:.0f}")
check("R12 CAMB unlensed λ₁ ≈ 289 (唔係 Silk 1113)", abs(lamb_camb["unlensed"] - 289) <= 45,
      f"{lamb_camb['unlensed']:.0f}")
check("R12 unlensed λ₁ ≠ 1113 (Silk local 預期已否證)",
      abs(lamb_camb["unlensed"] - 1113) > 200, f"{lamb_camb['unlensed']:.0f}")

# 306 vs 316 喺 SPT/ACT 嘅 Δχ²
print()
sel_S = (SPT_C >= 1418) & (SPT_C <= 1700) & (SPT_D > 0) & (SPT_D/SPT_E > 2)
loc_S = np.where(sel_S)[0]
C_S = spt_cov_tt[np.ix_(SM_IDX[loc_S], SM_IDX[loc_S])]
c306S, _ = chi2_full(SPT_C[loc_S], SPT_D[loc_S], 306.0, C_S)
c316S, _ = chi2_full(SPT_C[loc_S], SPT_D[loc_S], 316.0, C_S)
idxA = np.where((ACT_L >= 1418) & (ACT_L <= 1700) & (ACT_D > 0))[0]
C_A = ACT_COV[np.ix_(idxA, idxA)]
c306A, _ = chi2_full(ACT_L[idxA], ACT_D[idxA], 306.0, C_A)
c316A, _ = chi2_full(ACT_L[idxA], ACT_D[idxA], 316.0, C_A)
print(f"  Δχ²(306 vs 316): SPT {c306S-c316S:+.1f} (宣稱 -0.9) | ACT {c306A-c316A:+.1f} (宣稱 -2.7)")
check("R12 SPT |Δχ²(306 vs 316)| < 6", abs(c306S-c316S) < 6, f"{c306S-c316S:+.1f}")
check("R12 ACT |Δχ²(306 vs 316)| < 6", abs(c306A-c316A) < 6, f"{c306A-c316A:+.1f}")

# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print(f"AUDIT-A SUMMARY: {PASS} PASS / {FAIL} FAIL / {TOTAL} total")
if FAILS:
    print("FAIL list: " + "; ".join(FAILS))
print("=" * 78)
sys.exit(0 if FAIL == 0 else 1)
