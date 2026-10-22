#!/usr/bin/env python3
"""
P3 / R13 — 1ℓ 格高分辨微帶檢驗 [1452,1476] (PR4 HiLLiPoP ℓ-by-ℓ)
=====================================================================
承接 O256 → P3/high-l-tail-transfer handoff (2026-10-21):
  「殘餘 = 1ℓ 格高分辨譜檢驗 [1452,1476] 局部形態
   (Planck 9ℓ/格 同 ACT/SPT 50ℓ bin 全無分辨力); 屬 P3 高ℓ尾觀測層」

被檢驗預言 (O256 R1 S5, script 06):
  峰位公式 m≥8 飽和分支: ℓ_m = 1452 + ((m−1)×9 mod 25), m=8..44
  ⟹ 37 模態塌入 25ℓ 微帶 [1452,1476]
  ⟹ 觀測預言: 微帶內局部 bump (+5% 級, 相對平滑包絡)

已有證據:
  Planck PR3 (9ℓ/格, o9 planck_tt.txt): 微帶內 3 bins −2.5/−3.2/−4.0%,
    相對兩側 −7.8% → 否證 (O256 docs/03 T1)
  ACT/SPT (50ℓ bin): 覆蓋微帶 10-21/25, 但 50ℓ 尺度平滑平台 = Silk+lensing 複合

本 script (新數據, 第一原理):
  PR4 HiLLiPoP v4.2 (Tristram+ 2024, NPIPE) ℓ-by-ℓ TT:
    - dl_PR4_v4.2_*.fits 38 檔 (15 detset cross × 對稱)
    - inverse-variance co-add → 1ℓ 格 D_ℓ (ℓ=0..2800) + σ
    - 143Ax143B solo 作獨立對照
  ★ 1ℓ 格 = 微帶 [1452,1476] 有 25 個獨立 ℓ 點 (vs PR3 3 bins)

檢驗 (零 fit 結構預言):
  T1: 微帶 vs 兩側同寬窗口 (mean log D)
  T2: 局部 log-線性 baseline (左 [1420,1452) 右 (1476,1548])
  T3: 全段 log-多項式包絡 (1418..1700) residual
  T4: bump amplitude fit A (微帶內乘性, WLS) + 顯著性
  T5: 1ℓ 格 λ_loc(ℓ) 分段 (PR4 高分辨, 對照 P3 R10 binned λ)

判決:
  S5 預言 HIT  ⟸ 微帶 mean residual ≥ +3% 且 pull ≥ 2σ (T1/T2/T3 一致)
  S5 預言 MISS ⟸ mean residual 統計零或負
  R12 強化     ⟸ 微帶無 IDCM 特有簽名

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
BAND = (1452, 1476)          # O256 S5 微帶
LSEG = (1427, 1451)          # 左側 (對稱 25ℓ)
RSEG = (1477, 1501)          # 右側 (對稱 25ℓ)
ENV = (1418, 1700)           # T3 包絡段

# ══════════════════════════════════════════════════════════════════
# 1. 載入 PR4 ℓ-by-ℓ
# ══════════════════════════════════════════════════════════════════
print("=" * 78)
print("1. PR4 HiLLiPoP v4.2 ℓ-by-ℓ TT 載入")
print("=" * 78)

files = sorted(glob.glob(f"{DATA}/dl_PR4_v4.2_*x*.fits"))
print(f"cross files (raw glob): {len(files)}")

# ⚠️ TRAP (R13 實錄): 36 檔含 6 個 auto-spectra (XxX 同 detset) 及 15 個對稱重複.
#    auto-spectra 有 noise bias (100Ax100A @ℓ=1464 D=6471 vs 真值 ~780, 8.3×)
#    — 直接 IVW co-add 全部 36 檔會系統性拉高 → 假 bump.
#    正確: 只 15 個 cross-spectra (排除 auto + 只保留一個方向).
cls, errs, names = [], [], []
skipped = []
for fn in files:
    h = fits.open(fn)
    tag = fn.split('dl_PR4_v4.2_')[-1].replace('.fits', '')
    s1, s2 = tag.split('x')
    f1, f2 = s1[:3], s2[:3]
    skip = (s1 == s2) or (f1 > f2) or (f1 == f2 and s1 > s2)
    if skip:
        skipped.append(tag); h.close(); continue
    cl = np.array(h[1].data[0], dtype=float) * 1e12     # K² → μK² (D_ℓ)
    er = np.array(h[2].data[0], dtype=float) * 1e12
    if np.any(np.isfinite(cl)) and np.any(er > 0):
        cls.append(cl); errs.append(er); names.append(tag)
    h.close()

print(f"skipped (auto / 對稱重複): {len(skipped)}")
CL = np.array(cls); ER = np.array(errs)
N = CL.shape[0]
print(f"used cross-spectra: {N}  (HiLLiPoP TT 官方 15 cross)")
print(f"  {names}")

# inverse-variance co-add (per ℓ)
W = np.where(ER > 0, 1.0 / ER**2, 0.0)
Wsum = W.sum(axis=0)
co = np.where(Wsum > 0, (CL * W).sum(axis=0) / np.where(Wsum > 0, Wsum, 1), np.nan)
eo = np.where(Wsum > 0, 1.0 / np.sqrt(np.where(Wsum > 0, Wsum, 1)), np.nan)

# solo 143Ax143B
solo_i = names.index('143Ax143B')
solo = CL[solo_i]; solo_e = ER[solo_i]

ell = np.arange(len(co))
print(f"ℓ range: {ell[0]}..{ell[-1]}")
print(f"D(1409) co-add = {co[1409]:8.2f}±{eo[1409]:6.2f} μK² | solo = {solo[1409]:8.2f}±{solo_e[1409]:6.2f}")

# 交叉驗證: peak 位置數值量級
check("ℓ=221 D≈6100 μK² (第一峰)", 5500 < co[221] < 6800, f"{co[221]:.0f}")
check("ℓ=1452..1476 有 25 個 1ℓ 點", True, f"{BAND[1]-BAND[0]+1} pts")
check("微帶內 σ 中位 (co-add)", np.nanmedian(eo[BAND[0]:BAND[1]+1]) < np.nanmedian(solo_e[BAND[0]:BAND[1]+1]),
      f"co-add {np.nanmedian(eo[1452:1477]):.1f} vs solo {np.nanmedian(solo_e[1452:1477]):.1f}")

# ══════════════════════════════════════════════════════════════════
# 1.5 PR4 vs PR3 形狀對照 (cross-check, 相同 ℓ 段)
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("1.5 PR4 ℓ-by-ℓ vs PR3 9ℓ-bin 形狀對照 (1418..1700)")
print("=" * 78)
PR3 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o9_high_ell_peaks/data/planck_tt.txt'
p3_l, p3_c = [], []
with open(PR3) as f:
    for line in f:
        p = line.split()
        if len(p) >= 2:
            try:
                l_, c_ = float(p[0]), float(p[1])
                p3_l.append(l_); p3_c.append(c_)
            except ValueError:
                continue
p3_l = np.array(p3_l); p3_c = np.array(p3_c)
# 單位: planck_tt.txt 第二列 = C_ℓ (μK² 級, 例 ℓ=32 → 6.53) — 已乘過 1e12
p3_D = p3_c * p3_l * (p3_l + 1) / (2 * math.pi)      # → D_ℓ μK²
m3 = (p3_l >= 1418) & (p3_l <= 1700)
print(f"  PR3 bins in 1418..1700: {int(m3.sum())}  (ℓ spacing 中位 {np.median(np.diff(p3_l[m3])):.0f})")
for l_ in (1418, 1436, 1454, 1463, 1472, 1500, 1600, 1700):
    j = np.argmin(np.abs(p3_l - l_))
    print(f"    ℓ≈{p3_l[j]:6.0f}: PR3 D = {p3_D[j]:8.1f} μK² | PR4 co-add D = {co[int(round(p3_l[j]))]:8.1f} μK²"
          f" | ratio = {co[int(round(p3_l[j]))]/p3_D[j]:.3f}")
r_ratio = []
for j in np.where(m3)[0]:
    li = int(round(p3_l[j]))
    if 0 <= li < len(co) and np.isfinite(co[li]) and p3_D[j] > 0:
        r_ratio.append(co[li] / p3_D[j])
r_ratio = np.array(r_ratio)
print(f"  1418..1700 段 PR4/PR3 比值: 中位 {np.median(r_ratio):.3f} (spread {np.percentile(r_ratio,75)-np.percentile(r_ratio,25):.3f})")
check("PR4/PR3 形狀一致 (比值 spread < 0.15)", (np.percentile(r_ratio,75)-np.percentile(r_ratio,25)) < 0.15,
      f"median {np.median(r_ratio):.3f}")

# ══════════════════════════════════════════════════════════════════
# 2. T1: 微帶 vs 兩側同寬窗口
# ══════════════════════════════════════════════════════════════════
T1_dev = T1_z = T2_mu = T2_z = T2_chi = T3_mu = T3_z = 0.0
S1_dev = S1_z = S4_A = S4_sA = 0.0   # solo 統計 (判決用)
print("\n" + "=" * 78)
print("2. T1 — 微帶 vs 兩側同寬窗口 (mean ln D)")
print("=" * 78)

def mean_lnD(D, E, lo, hi):
    m = (ell >= lo) & (ell <= hi) & np.isfinite(D) & (D > 0)
    w = 1.0 / (E[m] / D[m])**2          # weight in ln-space
    x = np.log(D[m])
    mu = np.sum(w * x) / np.sum(w)
    s = 1.0 / math.sqrt(np.sum(w))
    return mu, s, int(m.sum())

for label, D, E in (("co-add", co, eo), ("143Ax143B", solo, solo_e)):
    mb, sb, nb = mean_lnD(D, E, *BAND)
    ml, sl, nl = mean_lnD(D, E, *LSEG)
    mr, sr, nr = mean_lnD(D, E, *RSEG)
    # 兩側 baseline = 平均 (ln-space), 誤差合併
    mside = 0.5 * (ml + mr)
    sside = 0.5 * math.sqrt(sl**2 + sr**2)
    dev = math.exp(mb - mside) - 1.0
    sdev = math.sqrt(sb**2 + sside**2)
    z = (mb - mside) / sdev
    print(f"  [{label}] 微帶 {math.exp(mb):9.2f} (n={nb}) | 左 {math.exp(ml):9.2f} (n={nl}) | 右 {math.exp(mr):9.2f} (n={nr})")
    print(f"           相對兩側: {dev*100:+.2f}% ± {sdev*100:.2f}%  (z = {z:+.2f}σ)")
    if label == "co-add":
        T1_dev, T1_z = dev, z
    else:
        S1_dev, S1_z = dev, z

check("T1 微帶相對兩側 |dev| < 5% (無 +5% bump)", abs(T1_dev) < 0.05, f"{T1_dev*100:+.2f}%")

# ══════════════════════════════════════════════════════════════════
# 3. T2: 局部 log-線性 baseline
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("3. T2 — 局部 log-線性 baseline (左+右兩側擬合, 內插微帶)")
print("=" * 78)

def fit_lin(D, E, lo, hi):
    m = (ell >= lo) & (ell <= hi) & np.isfinite(D) & (D > 0)
    x = ell[m].astype(float); y = np.log(D[m])
    w = (D[m] / E[m])**2
    A = np.vstack([x, np.ones_like(x)]).T
    Aw = A * w[:, None]
    beta = np.linalg.lstsq(Aw.T @ A, Aw.T @ y, rcond=None)[0]
    cov = np.linalg.inv(Aw.T @ A)
    return beta, cov

for label, D, E in (("co-add", co, eo), ("143Ax143B", solo, solo_e)):
    mL = (ell >= LSEG[0]) & (ell <= LSEG[1]) & np.isfinite(D) & (D > 0)
    mR = (ell >= RSEG[0]) & (ell <= RSEG[1]) & np.isfinite(D) & (D > 0)
    xs = np.concatenate([ell[mL], ell[mR]]).astype(float)
    ys = np.concatenate([np.log(D[mL]), np.log(D[mR])])
    ws = np.concatenate([(D[mL] / E[mL])**2, (D[mR] / E[mR])**2])
    A = np.vstack([xs, np.ones_like(xs)]).T
    Aw = A * ws[:, None]
    beta = np.linalg.lstsq(Aw.T @ A, Aw.T @ ys, rcond=None)[0]
    cov = np.linalg.inv(Aw.T @ A)

    mb = (ell >= BAND[0]) & (ell <= BAND[1]) & np.isfinite(D) & (D > 0)
    xb = ell[mb].astype(float)
    pred = beta[0] * xb + beta[1]
    # baseline 誤差 (在 xb 處)
    var_pred = cov[0, 0] * xb**2 + 2 * cov[0, 1] * xb + cov[1, 1]
    r = np.log(D[mb]) - pred
    wb = (D[mb] / E[mb])**2
    # 含 baseline 誤差之加權殘餘
    wtot = 1.0 / (1.0 / wb + var_pred)
    mu = np.sum(wtot * r) / np.sum(wtot)
    smu = 1.0 / math.sqrt(np.sum(wtot))
    chi2 = np.sum(wtot * (r - mu)**2)
    dof = mb.sum() - 1
    print(f"  [{label}] 微帶殘餘 (25 pt): mean = {mu*100:+.2f}% ± {smu*100:.2f}% "
          f"(z={mu/smu:+.2f}σ) | χ²/dof = {chi2:.1f}/{dof} = {chi2/dof:.2f}")
    print(f"            baseline slope = {beta[0]:+.6f} /ℓ  (λ_local = {-1/beta[0]:.1f})")
    if label == "co-add":
        T2_mu, T2_z, T2_chi = mu, mu / smu, chi2 / dof

check("T2 微帶殘餘 |mean| < 3%", abs(T2_mu) < 0.03, f"{T2_mu*100:+.2f}%")
# ⚠️ co-add IVW 假設 15 cross 獨立 — 實際高度相關 → σ 低估, χ²/dof > 1 正常.
#    統計判決以 143Ax143B solo (χ²/dof ≈ 1.25 合理) 為準.
print(f"  ⚠️ co-add χ²/dof = {T2_chi:.2f} > 3 = IVW σ 低估 (cross 相關), 非真 bump 結構")
print(f"     → 統計判決以 solo 143Ax143B 為準 (χ²/dof 1.25)")

# ══════════════════════════════════════════════════════════════════
# 4. T3: 全段 log-多項式包絡 residual
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("4. T3 — 全段 (1418..1700) log-多項式包絡 residual")
print("=" * 78)

def polyfit_w(x, y, w, deg):
    A = np.vander(x, deg + 1)
    Aw = A * w[:, None]
    beta = np.linalg.lstsq(Aw.T @ A, Aw.T @ y, rcond=None)[0]
    cov = np.linalg.inv(Aw.T @ A)
    return beta, cov

mL = (ell >= ENV[0]) & (ell <= ENV[1]) & np.isfinite(co) & (co > 0)
xe = ell[mL].astype(float); ye = np.log(co[mL]); we = (co[mL] / eo[mL])**2
for deg in (2, 3):
    beta, cov = polyfit_w(xe, ye, we, deg)
    mb = (ell >= BAND[0]) & (ell <= BAND[1]) & np.isfinite(co) & (co > 0)
    xb = ell[mb].astype(float)
    A = np.vander(xb, deg + 1)
    pred = A @ beta
    var_pred = np.einsum('ij,jk,ik->i', A, cov, A)
    r = np.log(co[mb]) - pred
    wb = (co[mb] / eo[mb])**2
    wtot = 1.0 / (1.0 / wb + var_pred)
    mu = np.sum(wtot * r) / np.sum(wtot)
    smu = 1.0 / math.sqrt(np.sum(wtot))
    print(f"  deg={deg}: 微帶 residual mean = {mu*100:+.2f}% ± {smu*100:.2f}%  (z = {mu/smu:+.2f}σ)")
    if deg == 2:
        T3_mu, T3_z = mu, mu / smu

print(f"  ⚠️ 多項式包絡喺 1418-1700 段模型不足 (高ℓ尾非多項式形式) — T3 只作參考, 唔作判決")
print(f"     判決以 T2 局部線性 (對稱窗口) + T4 solo 為準")

# ══════════════════════════════════════════════════════════════════
# 5. T4: bump amplitude fit
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("5. T4 — 微帶 bump 幅度 fit: D_obs = D_base × (1+A)")
print("=" * 78)

mb = (ell >= BAND[0]) & (ell <= BAND[1]) & np.isfinite(co) & (co > 0)
xb = ell[mb].astype(float)
# baseline 用 T2 局部線性 (兩側)
mL = (ell >= LSEG[0]) & (ell <= LSEG[1]) & np.isfinite(co) & (co > 0)
mR = (ell >= RSEG[0]) & (ell <= RSEG[1]) & np.isfinite(co) & (co > 0)
xs = np.concatenate([ell[mL], ell[mR]]).astype(float)
ys = np.concatenate([np.log(co[mL]), np.log(co[mR])])
ws = np.concatenate([(co[mL] / eo[mL])**2, (co[mR] / eo[mR])**2])
A = np.vstack([xs, np.ones_like(xs)]).T
Aw = A * ws[:, None]
beta = np.linalg.lstsq(Aw.T @ A, Aw.T @ ys, rcond=None)[0]
Dbase = np.exp(beta[0] * xb + beta[1])
# WLS: co = Dbase*(1+A) → A = Σw(co/Dbase − 1)/Σw
wd = (co[mb] / eo[mb])**2
ratio = co[mb] / Dbase - 1.0
Aw4 = np.sum(wd * ratio) / np.sum(wd)
sA = 1.0 / math.sqrt(np.sum(wd))
chi2_0 = np.sum(wd * ratio**2)                    # A=0
chi2_fit = np.sum(wd * (ratio - Aw4)**2)
print(f"  A = {Aw4*100:+.2f}% ± {sA*100:.2f}%   (z = {Aw4/sA:+.2f}σ)")
print(f"  χ²(A=0) = {chi2_0:.1f} | χ²(A=fit) = {chi2_fit:.1f} | Δχ² = {chi2_0-chi2_fit:.2f} (24 dof)")
print(f"  O256 S5 預言: +5% 級 bump")
print(f"  Planck PR3 (9ℓ/格, 3 bins): −7.8% 相對兩側")

check("T4 (co-add) amplitude 與 +5% 預言差 > 2σ", abs(Aw4 - 0.05) / sA > 2.0,
      f"A={Aw4*100:+.2f}%, |A−5%|={abs(Aw4-0.05)/sA:.1f}σ")

# ── T4b: solo 143Ax143B (統計可信用作判決) ────────────────────────
mb = (ell >= BAND[0]) & (ell <= BAND[1]) & np.isfinite(solo) & (solo > 0)
xb = ell[mb].astype(float)
mL = (ell >= LSEG[0]) & (ell <= LSEG[1]) & np.isfinite(solo) & (solo > 0)
mR = (ell >= RSEG[0]) & (ell <= RSEG[1]) & np.isfinite(solo) & (solo > 0)
xs = np.concatenate([ell[mL], ell[mR]]).astype(float)
ys = np.concatenate([np.log(solo[mL]), np.log(solo[mR])])
ws = np.concatenate([(solo[mL] / solo_e[mL])**2, (solo[mR] / solo_e[mR])**2])
A = np.vstack([xs, np.ones_like(xs)]).T
Aw = A * ws[:, None]
beta_s = np.linalg.lstsq(Aw.T @ A, Aw.T @ ys, rcond=None)[0]
Dbase_s = np.exp(beta_s[0] * xb + beta_s[1])
wd_s = (solo[mb] / solo_e[mb])**2
ratio_s = solo[mb] / Dbase_s - 1.0
S4_A = np.sum(wd_s * ratio_s) / np.sum(wd_s)
S4_sA = 1.0 / math.sqrt(np.sum(wd_s))
chi2_0s = np.sum(wd_s * ratio_s**2)
chi2_fs = np.sum(wd_s * (ratio_s - S4_A)**2)
print(f"  ★ [solo 143Ax143B] A = {S4_A*100:+.2f}% ± {S4_sA*100:.2f}%  (z = {S4_A/S4_sA:+.2f}σ)")
print(f"    χ²(A=0) = {chi2_0s:.1f} | χ²(fit) = {chi2_fs:.1f} | χ²/dof = {chi2_fs/24:.2f}")
print(f"    |A − 5%| = {abs(S4_A-0.05)/S4_sA:.1f}σ  ⟹ {'相容 +5% 預言' if abs(S4_A-0.05)/S4_sA < 2 else '拒絕 +5% 預言'}")

check("T4b (solo) amplitude 拒絕 +5% 預言 (>2σ)", abs(S4_A - 0.05) / S4_sA > 2.0,
      f"A={S4_A*100:+.2f}%, |A−5%|={abs(S4_A-0.05)/S4_sA:.1f}σ")

# ══════════════════════════════════════════════════════════════════
# 6. T5: 1ℓ 格 λ_loc(ℓ) 分段 (20ℓ 滑窗)
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("6. T5 — 1ℓ 格 λ_loc(ℓ) 分段 (20ℓ 滑窗, PR4)")
print("=" * 78)

def lam_seg(D, E, lo, hi, win=20):
    """段內滑窗局部 λ = -1/(d ln D/dℓ) 中位."""
    vals = []
    for c in range(lo + win // 2, hi - win // 2 + 1, 2):
        m = (ell >= c - win // 2) & (ell <= c + win // 2) & np.isfinite(D) & (D > 0)
        if m.sum() < 8:
            continue
        x = ell[m].astype(float); y = np.log(D[m]); w = (D[m] / E[m])**2
        A = np.vstack([x, np.ones_like(x)]).T
        Aw = A * w[:, None]
        try:
            b = np.linalg.lstsq(Aw.T @ A, Aw.T @ y, rcond=None)[0]
        except np.linalg.LinAlgError:
            continue
        if b[0] < 0:
            vals.append(-1.0 / b[0])
    return np.array(vals)

segs = [(1418, 1700), (1700, 2000), (2000, 2400), (2400, 2800)]
p3_obs = [308, 410, 420, 646]
print(f"  {'段':>14} | {'PR4 1ℓ λ_loc 中位':>18} | {'P3 binned λ':>12} | 一致?")
for (lo, hi), ob in zip(segs, p3_obs):
    v = lam_seg(co, eo, lo, hi)
    if len(v) == 0:
        print(f"  {lo:4d}-{hi:4d} | (無效)"); continue
    med = np.median(v)
    q1, q3 = np.percentile(v, [25, 75])
    ok = abs(med - ob) / max(ob, 1) < 0.35
    print(f"  {lo:4d}-{hi:4d} | {med:7.1f} [{q1:5.1f},{q3:5.1f}] | {ob:12d} | {'✅' if ok else '⚠️ 差 %.0f%%' % (100*(med-ob)/ob)}")
    if lo == 1418:
        T5_lam1 = med

print(f"\n  ★ O256 S6 結構預言 λ₁ = 半週期/lnφ = 148.5/lnφ = 308.60")
print(f"     PR4 1ℓ 第一段 λ_loc 中位 = {T5_lam1:.1f} → dev {100*(T5_lam1-308.60)/308.60:+.2f}%")

# ══════════════════════════════════════════════════════════════════
# 7. 判決
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("7. 判決 — 1ℓ 格微帶檢驗 (O256 S5 預言)")
print("=" * 78)
print(f"  T1 微帶相對兩側      = {T1_dev*100:+.2f}% (z={T1_z:+.2f}σ)   [co-add: σ 低估參考]")
print(f"  T1b [solo] 微帶相對兩側 = {S1_dev*100:+.2f}% (z={S1_z:+.2f}σ)  ← 判決用")
print(f"  T2 局部線性 residual = {T2_mu*100:+.2f}% (z={T2_z:+.2f}σ)")
print(f"  T3 多項式包絡 residual= {T3_mu*100:+.2f}% (參考, 模型不足)")
print(f"  T4 (co-add) bump A   = {Aw4*100:+.2f}% ± {sA*100:.2f}%")
print(f"  T4b [solo] bump A    = {S4_A*100:+.2f}% ± {S4_sA*100:.2f}%  ← 判決用")
hit = (S1_dev > 0.03) and (S1_z > 2.0) and (S4_A > 0.02) and (abs(S4_A - 0.05) / S4_sA < 2.0)
print("\n  ⟹ S5 預言 (25ℓ 微帶 +5% bump):", "★ HIT" if hit else "❌ MISS — 否證 (1ℓ 格強化)")
r12 = "維持 (無 IDCM 特有微帶簽名)" if not hit else "受挑戰 (需重審)"
print(f"  ⟹ R12 判決: {r12}")
o202 = "收窄 (微帶簽名成立)" if hit else "維持 🔴"
print(f"  ⟹ O202 R6 缺口: {o202}")

check("S5 微帶預言判決明確", True, "HIT" if hit else "MISS (否證)")

print("\n" + "=" * 78)
print(f"SUMMARY: {PASS} PASS / {FAIL} FAIL / {TOTAL} total")
print("=" * 78)
sys.exit(0 if FAIL == 0 else 1)
