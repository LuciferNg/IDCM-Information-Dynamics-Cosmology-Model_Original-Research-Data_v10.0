#!/usr/bin/env python3
"""
11_lae_ceers_analysis.py
===========================
IDCM 驗證：CEERS DR1 光度目錄 LAE 計數分析

CEERS DR1 係 NIRCam 光度目錄（87,345 源），
比 JADES DR4 光譜目錄（5,190 源）更完整。
可以更準確驗證 N(z) ∝ 1/(1+z) 嘅 IDCM 預測。

IDCM v10.0 — 共震點宇宙學
"""

import sys
import math
import json
import gzip
import io
import numpy as np
from astropy.io import fits

# ================================================================
# IDCM Core
# ================================================================
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
EPS = PHI_INV / 4
B = 4

print("=" * 72)
print("IDCM LAE 驗證 — CEERS DR1 光度目錄分析")
print("=" * 72)

# ================================================================
# 載入 CEERS DR1
# ================================================================
fpath = 'data/ceers_dr1_catalog.fits.gz'
print(f"\n載入 {fpath}...")

with gzip.open(fpath, 'rb') as f:
    with fits.open(io.BytesIO(f.read())) as hdul:
        data = hdul[1].data
        n_total = len(data)
        print(f"總光源數: {n_total}")

        # 提取關鍵列
        z_best = data['LP_Z_BEST']  # 最佳光度紅移
        z_med = data['LP_Z_MED']     # 中位紅移
        z_lo = data['LP_Z_MED68_LOW']  # 68% 下限
        z_hi = data['LP_Z_MED68_HIGH'] # 68% 上限
        star_flag = data['STAR_FLAG']    # 恆星標記
        bad_region = data['BAD_REGION_FLAG']  # 壞區域標記
        chi2 = data['LP_FIT_CHI']      # 擬合 χ²
        nbands = data['LP_NBANDS']     # 波段數
        mass = data['LP_MASS_MED']     # 質量
        sfr = data['LP_SFR_MED']       # 恆星形成率
        ra = data['RA']                # 赤經
        dec = data['DEC']              # 赤緯

# ================================================================
# 品質過濾
# ================================================================
print(f"\n品質過濾：")

# 有效紅移
valid_z = np.isfinite(z_best) & (z_best > 0) & (z_best < 25)
print(f"  有效紅移: {np.sum(valid_z)}/{n_total}")

# 非恆星
not_star = (star_flag != 1) & (star_flag != 1.0)
print(f"  非恆星: {np.sum(not_star)}/{n_total}")

# 非壞區域
good_region = (bad_region != 1) & (bad_region != 1.0)
print(f"  非壞區域: {np.sum(good_region)}/{n_total}")

# 波段數夠多（≥5 個波段）
good_nbands = np.isfinite(nbands) & (nbands >= 5) & (nbands < 50)
print(f"  波段≥5: {np.sum(good_nbands)}/{n_total}")

# 擬合質量好（χ² < 10）
good_chi2 = np.isfinite(chi2) & (chi2 > 0) & (chi2 < 10)
print(f"  χ²<10: {np.sum(good_chi2)}/{n_total}")

# 綜合品質
quality = valid_z & not_star & good_region & good_nbands & good_chi2
print(f"  綜合品質: {np.sum(quality)}/{n_total}")

z_clean = z_best[quality]
n_clean = len(z_clean)
print(f"\n  用於分析嘅光源數: {n_clean}")

# ================================================================
# 紅移分佈
# ================================================================
print(f"\n{'=' * 72}")
print("紅移分佈")
print("=" * 72)

# 全域分佈
z_bins = np.arange(0, 16, 0.5)
z_hist, z_edges = np.histogram(z_clean, bins=z_bins)
z_centers = (z_edges[:-1] + z_edges[1:]) / 2

print(f"\n  z 範圍  | N(z) | ℓ=log₄(1+z) | IDCM N∝1/(1+z)")
print(f"  {'─'*7}|{'─'*6}|{'─'*14}|{'─'*18}")

norm = np.sum(z_hist)
for i in range(len(z_centers)):
    z_mid = z_centers[i]
    n_obs = z_hist[i]
    ell = math.log(1 + z_mid) / math.log(4)
    n_idcm = norm * (1/(1+z_mid)) / np.sum([1/(1+z_centers[j]) for j in range(len(z_centers))])
    print(f"  {z_mid-0.25:3.1f}-{z_mid+0.25:3.1f} | {n_obs:5d} | {ell:12.3f} | {n_idcm:16.1f}")

# ================================================================
# 擬合
# ================================================================
def fit_slope(z_vals, counts, label):
    """加權最小二乘法擬合 ln N = slope × ln(1+z) + intercept"""
    mask = (counts > 0) & np.isfinite(z_vals)
    z_fit = z_vals[mask]
    n_fit = counts[mask]
    
    if len(z_fit) < 3:
        print(f"  {label}: 數據點不足 (<3)")
        return None, None, None, 0, 0
    
    ln_1pz = np.array([math.log(1 + z) for z in z_fit])
    ln_N = np.array([math.log(n) for n in n_fit])
    w = np.array([math.sqrt(n) for n in n_fit])
    
    A = np.vstack([ln_1pz, np.ones_like(ln_1pz)]).T
    W = np.diag(w)
    Aw = np.sqrt(W) @ A
    bw = np.sqrt(W) @ ln_N
    
    try:
        fit, residuals, rank, s = np.linalg.lstsq(Aw, bw, rcond=None)
        slope, intercept = fit
        
        residual = Aw @ fit - bw
        chi2 = np.sum(residual**2)
        dof = len(z_fit) - 2
        red_chi2 = chi2 / dof if dof > 0 else 0
        
        cov = np.linalg.inv(A.T @ W @ A)
        slope_err = math.sqrt(cov[0, 0]) if cov[0, 0] > 0 else 0
        
        sigma_dev = abs(slope - (-1)) / slope_err if slope_err > 0 else float('inf')
        
        print(f"\n  {label}:")
        print(f"    ln N = ({slope:.4f} ± {slope_err:.4f}) × ln(1+z) + {intercept:.4f}")
        print(f"    χ²/dof = {red_chi2:.2f}")
        print(f"    IDCM 預測斜率 = -1.0000")
        print(f"    偏差 = {sigma_dev:.1f}σ")
        if sigma_dev < 1:
            print(f"    ✅ 吻合 IDCM 預測！")
        elif sigma_dev < 3:
            print(f"    🟡 偏差 {sigma_dev:.1f}σ")
        else:
            print(f"    ❌ 偏離（需考慮選擇效應/光度函數）")
        
        return slope, slope_err, intercept, red_chi2, len(z_fit)
    
    except np.linalg.LinAlgError:
        print(f"  {label}: 擬合失敗")
        return None, None, None, 0, 0

# 擬合 1：全部 z>0
print(f"\n{'─' * 72}")
print("擬合 1：全部紅移 (z>0)")
print("─" * 72)
s1, e1, i1, c1, n1 = fit_slope(z_centers, z_hist, "z>0")

# 擬合 2：z>1（排除低z 異常）
print(f"\n{'─' * 72}")
print("擬合 2：z>1")
print("─" * 72)
m1 = z_centers > 1
s2, e2, i2, c2, n2 = fit_slope(z_centers[m1], z_hist[m1], "z>1")

# 擬合 3：z>3（高紅移）
print(f"\n{'─' * 72}")
print("擬合 3：z>3")
print("─" * 72)
m3 = z_centers > 3
s3, e3, i3, c3, n3 = fit_slope(z_centers[m3], z_hist[m3], "z>3")

# 擬合 4：z>6（再電離區域）
print(f"\n{'─' * 72}")
print("擬合 4：z>6（再電離區域）")
print("─" * 72)
m4 = z_centers > 6
s4, e4, i4, c4, n4 = fit_slope(z_centers[m4], z_hist[m4], "z>6")

# ================================================================
# 歸一化比較
# ================================================================
print(f"\n{'=' * 72}")
print("歸一化比較：N(z) vs 1/(1+z)")
print("=" * 72)

# 用 z>3 區域歸一化
m_high = z_centers > 3
z_high = z_centers[m_high]
n_high = z_hist[m_high]

# IDCM 預測：N(z) ∝ 1/(1+z)，歸一化到 z=3.25
norm_idcm = n_high[0] * (1 + z_high[0]) / (1 + z_high)
n_idcm = norm_idcm

print(f"\n  z      | N_obs | N_IDCM | 殘差 (σ)")
print(f"  {'─'*6}|{'─'*6}|{'─'*8}|{'─'*10}")
for i in range(len(z_high)):
    z = z_high[i]
    n_obs = n_high[i]
    n_pred = n_idcm[i]
    residual = (n_obs - n_pred) / math.sqrt(n_obs) if n_obs > 0 else 0
    marker = "✅" if abs(residual) < 3 else "🟡" if abs(residual) < 5 else "❌"
    print(f"  {z:5.2f} | {n_obs:5d} | {n_pred:6.1f} | {residual:+.2f}σ {marker}")

# ================================================================
# 總結
# ================================================================
print(f"\n{'=' * 72}")
print("總結")
print("=" * 72)

print(f"""
CEERS DR1 光度目錄分析結果：

全部紅移 (z>0): 斜率 = {s1:.3f} ± {e1:.3f}  (偏差 {abs(s1-(-1))/e1:.1f}σ)
z>1:          斜率 = {s2:.3f} ± {e2:.3f}  (偏差 {abs(s2-(-1))/e2:.1f}σ)
z>3:          斜率 = {s3:.3f} ± {e3:.3f}  (偏差 {abs(s3-(-1))/e3:.1f}σ)
z>6:          斜率 = {s4:.3f} ± {e4:.3f}  (偏差 {abs(s4-(-1))/e4:.1f}σ)

注意：CEERS DR1 係光度目錄（photometric redshifts），
紅移誤差較大（σ_z ~ 0.1-0.3），特別係高z 區域。
光度函數嘅完整度喺高z 亦會下降。

最準確嘅驗證需要：
1. 完整嘅光度函數分析（唔係簡單計數）
2. 考慮紅移誤差嘅 forward model
3. 或者 JWST NIRSpec 完整光譜樣本
""")

# ================================================================
# 儲存結果
# =================================================================
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

results = {
    'n_total': n_total,
    'n_clean': n_clean,
    'fit_all': {'slope': s1, 'slope_err': e1, 'intercept': i1, 'chi2_dof': c1, 'n_points': n1, 'idcm_pred': -1.0} if s1 is not None else None,
    'fit_z1':  {'slope': s2, 'slope_err': e2, 'intercept': i2, 'chi2_dof': c2, 'n_points': n2, 'idcm_pred': -1.0} if s2 is not None else None,
    'fit_z3':  {'slope': s3, 'slope_err': e3, 'intercept': i3, 'chi2_dof': c3, 'n_points': n3, 'idcm_pred': -1.0} if s3 is not None else None,
    'fit_z6':  {'slope': s4, 'slope_err': e4, 'intercept': i4, 'chi2_dof': c4, 'n_points': n4, 'idcm_pred': -1.0} if s4 is not None else None,
    'z_bins': z_centers.tolist(),
    'z_hist': z_hist.tolist(),
    'idcm_prediction': 'N(z) ∝ 1/(1+z)',
    'idcm_mechanism': 'K_Tree projection area narrowing: B^(-ℓ) = 4^(-log₄(1+z)) = 1/(1+z)'
}

with open('data/lae_ceers_results.json', 'w') as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)

print(f"結果已儲存至 data/lae_ceers_results.json")
print(f"CEERS 數據已儲存至 data/ceers_dr1_catalog.fits.gz (195 MB)")
print(f"{'=' * 72}")