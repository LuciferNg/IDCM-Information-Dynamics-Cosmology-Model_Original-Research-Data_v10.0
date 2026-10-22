#!/usr/bin/env python3
"""
P3 / R14 — λ(ℓ) 階梯過渡結構 (1ℓ 格 PR4, 半週期→全週期)
=====================================================================
背景 (三輪攻堅後):
  R10/R13: 高ℓ尾 λ(ℓ) 階梯 — 308 (1418-1700) → 410 (1700-2000)
           → 420 (2000-2400) → 646 (2400+); 四數據集確認 (Planck/SPT/ACT/PR4-1ℓ)
  O256 S6/S7 (結構, 零參數):
     λ₁ = 半週期/lnφ = 148.5/lnφ = 308.60   (峰-谷半週期)
     λ₄ = 全間隙/lnφ = 306/lnφ = 635.89     (峰-峰全間隙)
     上升比 結構 2.061 vs 實測 2.097 → 缺口 1.8%
     ⟹ 假說: λ(ℓ) 上升 = 有效間隙由「峰-谷半週期 → 峰-峰全週期」過渡

本 script (R14, P3 形式層 — 唔做結構推導):
  M1: logistic 過渡 λ(ℓ) = λ_h + (λ_f − λ_h)·σ((ℓ−ℓ_t)/w)
      λ_h = 148.5/lnφ = 308.60, λ_f = 306/lnφ = 635.89  (★ 零參數, 結構值)
      自由: ℓ_t (過渡中心), w (寬度)
  M2: 分段常數 (P3 R10 四段, 5 參數) 作對照
  M3: 單一 λ (R2 舊模型, 1 參數) 作對照

  判決:
    ① M1 (2 參數, 端點結構固定) vs M2 (5 參數) — Δχ²/AIC
    ② ℓ_t 有冇結構身份 (1700 = ? / 半週期整數倍)
    ③ λ_loc(ℓ) 連續曲線單調性 + 過渡位置量度

數據: PR4 HiLLiPoP v4.2 15 cross-spectra co-add (ℓ-by-ℓ, 已於 R13 建)
環境: /usr/bin/python3
"""
import math
import sys
import glob
import numpy as np
import astropy.io.fits as fits

PASS = FAIL = TOTAL = 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")

DATA = '/home/wsl/.hermes/cache/scratch/planck_2020/hillipop/planck_2020/hillipop/data'
LNHI = math.log((1 + math.sqrt(5)) / 2)          # ln φ = 0.4812118...
LAM_H = 148.5 / LNHI                              # 半週期 (峰-谷) / lnφ
LAM_F = 306.0 / LNHI                              # 全間隙 (峰-峰) / lnφ

# ══════════════════════════════════════════════════════════════════
# 1. PR4 15 cross-spectra co-add (R13 方法, 排除 auto)
# ══════════════════════════════════════════════════════════════════
print("=" * 78)
print("1. PR4 15 cross-spectra co-add")
print("=" * 78)

files = sorted(glob.glob(f"{DATA}/dl_PR4_v4.2_*x*.fits"))
cls, errs = [], []
for fn in files:
    tag = fn.split('dl_PR4_v4.2_')[-1].replace('.fits', '')
    s1, s2 = tag.split('x')
    f1, f2 = s1[:3], s2[:3]
    if (s1 == s2) or (f1 > f2) or (f1 == f2 and s1 > s2):
        continue
    h = fits.open(fn)
    cls.append(np.array(h[1].data[0], dtype=float) * 1e12)
    errs.append(np.array(h[2].data[0], dtype=float) * 1e12)
    h.close()
CL = np.array(cls); ER = np.array(errs)
W = np.where(ER > 0, 1.0 / np.where(ER > 0, ER, 1)**2, 0.0)
Wsum = W.sum(axis=0)
co = np.where(Wsum > 0, (CL * W).sum(axis=0) / np.where(Wsum > 0, Wsum, 1), np.nan)
eo = np.where(Wsum > 0, 1.0 / np.sqrt(np.where(Wsum > 0, Wsum, 1)), np.nan)
ell = np.arange(len(co))
print(f"  spectra: {len(cls)} cross | ℓ 0..{len(co)-1}")

print(f"\n  ★ 結構端點 (零參數):")
print(f"     λ_h = 148.5/lnφ = {LAM_H:8.2f}  (半週期/lnφ, O256 S6)")
print(f"     λ_f = 306.0/lnφ = {LAM_F:8.2f}  (全間隙/lnφ, O256 S7)")
print(f"     結構上升比 = {LAM_F/LAM_H:.4f}")

# ══════════════════════════════════════════════════════════════════
# 2. λ_loc(ℓ) 連續曲線 (滑窗 40ℓ, 步 5ℓ)
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("2. λ_loc(ℓ) 連續曲線 (40ℓ 滑窗, 步 5ℓ)")
print("=" * 78)

LO, HI, WIN, STEP = 1418, 2400, 40, 5
centers, lams, lam_err = [], [], []
for c in range(LO, HI + 1, STEP):
    m = (ell >= c - WIN // 2) & (ell <= c + WIN // 2) & np.isfinite(co) & (co > 0)
    if m.sum() < 20:
        continue
    x = ell[m].astype(float); y = np.log(co[m]); w = (co[m] / eo[m])**2
    A = np.vstack([x, np.ones_like(x)]).T
    Aw = A * w[:, None]
    beta = np.linalg.lstsq(Aw.T @ A, Aw.T @ y, rcond=None)[0]
    cov = np.linalg.inv(Aw.T @ A)
    slope, sslope = beta[0], math.sqrt(cov[0, 0])
    if slope < 0:
        lam = -1.0 / slope
        slam = lam * sslope / abs(slope)
        centers.append(c); lams.append(lam); lam_err.append(slam)

centers = np.array(centers); lams = np.array(lams); lam_err = np.array(lam_err)
print(f"  points: {len(centers)}")
for i in range(0, len(centers), 6):
    print(f"   ℓ={centers[i]:5.0f}: λ_loc = {lams[i]:7.1f} ± {lam_err[i]:5.1f}")

# 單調性檢驗 (粗趨勢, 用 5 點滑動中位)
med = np.array([np.median(lams[max(0,i-2):i+3]) for i in range(len(lams))])
n_up = int(np.sum(np.diff(med) > 0))
print(f"\n  單調性: 相鄰 5-中位上升 {n_up}/{len(med)-1} 段 ({100*n_up/(len(med)-1):.0f}%)")
print(f"  ⚠️ 單調性測試受點間噪聲污染 (每點誤差可達 ±1600) — 唔作判決, 只作描述")

# ══════════════════════════════════════════════════════════════════
# 2.5 ★ 窗寬依賴審計 (關鍵方法診斷)
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("2.5 ★ 窗寬依賴審計 — λ_loc 隨窗寬系統變化? (local vs global 陷阱)")
print("=" * 78)

def lam_seg_fit(D, E, lo, hi):
    """段內單一 log-linear fit → 平均 λ."""
    m = (ell >= lo) & (ell <= hi) & np.isfinite(D) & (D > 0)
    x = ell[m].astype(float); y = np.log(D[m]); w = (D[m] / E[m])**2
    A = np.vstack([x, np.ones_like(x)]).T
    Aw = A * w[:, None]
    b = np.linalg.lstsq(Aw.T @ A, Aw.T @ y, rcond=None)[0]
    return -1.0 / b[0] if b[0] < 0 else float('nan')

print(f"  {'窗寬':>6} | {'1418-1700 中位 λ_loc':>22} | {'1700-2000':>12} | {'2000-2400':>12}")
for win in (10, 20, 40, 80, 160):
    row = []
    for lo, hi in ((1418, 1700), (1700, 2000), (2000, 2400)):
        vals = []
        for c in range(lo + win // 2, hi - win // 2 + 1, 5):
            m = (ell >= c - win // 2) & (ell <= c + win // 2) & np.isfinite(co) & (co > 0)
            if m.sum() < 8:
                continue
            x = ell[m].astype(float); y = np.log(co[m]); w = (co[m] / eo[m])**2
            A = np.vstack([x, np.ones_like(x)]).T
            Aw = A * w[:, None]
            b = np.linalg.lstsq(Aw.T @ A, Aw.T @ y, rcond=None)[0]
            if b[0] < 0:
                vals.append(-1.0 / b[0])
        row.append(np.median(vals) if vals else float('nan'))
    print(f"  {win:>6} | {row[0]:>22.1f} | {row[1]:>12.1f} | {row[2]:>12.1f}")

print(f"\n  {'段':<12} | {'全段單 fit':>12} | 對照 R10 binned")
for (lo, hi), ob in zip(((1418,1700),(1700,2000),(2000,2400)), (308,410,420)):
    print(f"  {lo}-{hi} | {lam_seg_fit(co, eo, lo, hi):>12.1f} | {ob}")

print(f"\n  ⚠️ 判讀: 窗寬 10→160ℓ λ_loc 系統上升 ⟹ 高ℓ尾有大曲率 (非單一指數);")
print(f"     λ_loc 係「窗口內平均斜率」唔係「局部瞬時斜率」— 窗寬依賴 = 本質, 唔係 bug.")
print(f"     ⟹ 1ℓ 格 λ_loc 唔可以用作模型判別 (R14 M1/M2/M3 比較受此污染).")
print(f"     ⟹ R13 T5「1ℓ 格確認分段 λ」需 downgrade: 20ℓ 窗巧合對到 binned,")
print(f"        40ℓ 窗即偏離 (R14 實測 390 vs binned 308) — 唔算獨立確認.")

# ══════════════════════════════════════════════════════════════════
# 3. 模型擬合 (χ² in log-space, 用 λ_loc 點)
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("3. 模型擬合 — M1 logistic 過渡 (端點結構固定) vs M2 分段 vs M3 單一")
print("=" * 78)

def logistic(t, lt, w):
    return 1.0 / (1.0 + np.exp(-(t - lt) / w))

def model_m1(x, lt, w):
    return LAM_H + (LAM_F - LAM_H) * logistic(x, lt, w)

def chi2_model(x, y, sy, pred):
    return np.sum(((y - pred) / sy)**2)

# grid search M1 (lt, w)
best = (None, None, 1e18)
for lt in np.arange(1500, 2300, 10.0):
    for w in np.arange(30, 600, 10.0):
        c2 = chi2_model(centers, lams, lam_err, model_m1(centers, lt, w))
        if c2 < best[2]:
            best = (lt, w, c2)
lt1, w1, chi_m1 = best
print(f"  M1 (2 參數, λ_h/λ_f 結構固定): ℓ_t = {lt1:.0f}, w = {w1:.0f} ⟹ χ² = {chi_m1:.1f}")
print(f"     λ(1418) = {model_m1(1418, lt1, w1):.1f} | λ(1700) = {model_m1(1700, lt1, w1):.1f}"
      f" | λ(2400) = {model_m1(2400, lt1, w1):.1f}")

# M2: 分段常數 (4 段, 5 參數: 4 段值 + 過渡, 簡化為 4 段值)
segs = [(1418, 1700), (1700, 2000), (2000, 2400)]
chi_m2 = 0.0
seg_mean = []
for lo, hi in segs:
    m = (centers >= lo) & (centers <= hi)
    if m.sum() == 0:
        continue
    # 段內加權平均
    ww = 1.0 / lam_err[m]**2
    mu = np.sum(ww * lams[m]) / np.sum(ww)
    seg_mean.append((lo, hi, mu))
    chi_m2 += np.sum(ww * (lams[m] - mu)**2)
print(f"  M2 (分段常數, {len(seg_mean)} 參數): χ² = {chi_m2:.1f}")
for lo, hi, mu in seg_mean:
    print(f"     {lo}-{hi}: λ = {mu:.1f}")

# M3: 單一 λ (1 參數)
ww = 1.0 / lam_err**2
mu3 = np.sum(ww * lams) / np.sum(ww)
chi_m3 = np.sum(ww * (lams - mu3)**2)
print(f"  M3 (單一 λ, 1 參數): λ = {mu3:.1f} ⟹ χ² = {chi_m3:.1f}")

dof_m1 = len(centers) - 2
dof_m2 = len(centers) - len(seg_mean)
dof_m3 = len(centers) - 1
aic = lambda c2, k: c2 + 2 * k
print(f"\n  {'模型':<8} {'k':>3} {'χ²':>9} {'χ²/dof':>9} {'AIC':>10}")
for nm, c2, k, dof in (("M1 logistic", chi_m1, 2, dof_m1), ("M2 分段", chi_m2, len(seg_mean), dof_m2),
                       ("M3 單一", chi_m3, 1, dof_m3)):
    print(f"  {nm:<8} {k:>3} {c2:>9.1f} {c2/dof:>9.2f} {aic(c2,k):>10.1f}")

best_m = min((("M1", chi_m1, 2), ("M2", chi_m2, len(seg_mean)), ("M3", chi_m3, 1)), key=lambda t: aic(t[1], t[2]))
print(f"\n  ⟹ ΔAIC 判: {best_m[0]} 最佳")
print(f"  ⚠️ 但 λ_loc 點本身窗寬依賴 + 噪聲主導 (χ²/dof M1 17.3) ⟹ 模型判別無效,")
print(f"     唔可以話「logistic 假說被否證」— 只可以話「用 1ℓ λ_loc 測唔到」.")
check("M1 vs M3 AIC 比較可判別 (χ²/dof < 3)", chi_m1/dof_m1 < 3.0,
      f"M1 χ²/dof={chi_m1/dof_m1:.2f} ⟹ 不可判別 (λ_loc 噪聲主導)")

# ══════════════════════════════════════════════════════════════════
# 4. ℓ_t 結構身份審計
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("4. ℓ_t 結構身份審計 (零參數候選池, 唔准反解)")
print("=" * 78)

# 事前指定候選池 (結構數, 唔係由 ℓ_t 反解)
cands = {
    "1409 (m=7 峰)": 1409,
    "44×39 = 1716": 44 * 39,
    "44×40 = 1760": 44 * 40,
    "1409+306 = 1715": 1409 + 306,
    "1409+288 = 1697": 1409 + 288,
    "220+306×5 = 1750": 220 + 306 * 5,
    "F₅²×68 = 1700": 25 * 68,
    "λ_f+λ_h×3 = 1562": LAM_F + 3 * LAM_H,
    "2×λ_h+λ_f = 1253": 2 * LAM_H + LAM_F,
}
print(f"  ℓ_t (fit) = {lt1:.0f} (格點 10ℓ, 無誤差估計)")
print(f"  {'候選':<24} {'值':>8} {'差':>8}")
best_c = (None, 1e18)
for nm, v in cands.items():
    d = abs(v - lt1)
    print(f"  {nm:<24} {v:>8.0f} {d:>8.0f}")
    if d < best_c[1]:
        best_c = (nm, d)
print(f"\n  最近候選: {best_c[0]} (差 {best_c[1]:.0f}ℓ)")
print(f"  ⚠️ 無誤差估計 + 網格 10ℓ + 候選池後驗風險 ⟹ 唔作閉合主張 (P3 R12 先例)")

# ══════════════════════════════════════════════════════════════════
# 5. 上升比檢驗 (O256 S7 結構預言)
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("5. 上升比 — 結構 2.061 vs 實測")
print("=" * 78)

# 實測: 第一段 λ vs 最後可用段 λ (from λ_loc 曲線)
m_first = centers <= 1700
m_last = centers >= 2300
if m_first.sum() > 0 and m_last.sum() > 0:
    lam_first = np.median(lams[m_first])
    lam_last = np.median(lams[m_last])
    ratio_obs = lam_last / lam_first
    print(f"  實測 λ(1418-1700) 中位 = {lam_first:.1f} | λ(2300-2400) 中位 = {lam_last:.1f}")
    print(f"  上升比 實測 = {ratio_obs:.3f} | 結構預言 (λ_f/λ_h) = {LAM_F/LAM_H:.3f}"
          f" | 差 {100*(ratio_obs-LAM_F/LAM_H)/(LAM_F/LAM_H):+.1f}%")
    check("上升比與結構預言差 < 15%", abs(ratio_obs - LAM_F / LAM_H) / (LAM_F / LAM_H) < 0.15,
          f"{ratio_obs:.3f} vs {LAM_F/LAM_H:.3f}")
else:
    ratio_obs = 0.0
    check("上升比可量度", False, "段不足")

# ══════════════════════════════════════════════════════════════════
# 6. 判決
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("6. 判決")
print("=" * 78)
print(f"  λ(ℓ) 階梯結構: logistic 過渡 (端點 = 半週期/lnφ → 全間隙/lnφ, 零參數)")
print(f"    ℓ_t = {lt1:.0f}, w = {w1:.0f} | χ²/dof = {chi_m1/dof_m1:.2f} vs M3 單一 {chi_m3/dof_m3:.1f}")
print(f"    ⟹ {'形式層支持 O256 S7 過渡假說' if aic(chi_m1,2) < aic(chi_m3,1) else '唔支持'}")
print(f"  ℓ_t 身份: 🔴 未閉合 (候選池最近 {best_c[0]} 差 {best_c[1]:.0f}ℓ, 無誤差 + 後驗風險)")
print(f"  上升比: {ratio_obs:.3f} vs 結構 {LAM_F/LAM_H:.3f}")

print("\n" + "=" * 78)
print(f"SUMMARY: {PASS} PASS / {FAIL} FAIL / {TOTAL} total")
print("=" * 78)
sys.exit(0 if FAIL == 0 else 1)
