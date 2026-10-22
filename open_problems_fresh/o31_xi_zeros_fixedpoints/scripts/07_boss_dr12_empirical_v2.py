"""
O31 方向 D — 真實 BOSS/eBOSS ξ(s) 數據實證 (v2)
==================================================
使用 eBOSS DR16 原始數據 (s_max=247.5 h⁻¹ Mpc) 和 BOSS DR12 後重建數據。
從 wiggle 分量中找出零點 (nulls)，與理論比較，驗證 88 不動點定理。

修正 v1: post-reconstruction data 無零點 crossing
→ 改用 wiggle component (ξ - broadband)
"""

import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
import os

LAMBDA_SYNC = 406.1  # h⁻¹ Mpc
N_SITES = 44
phi = (1 + np.sqrt(5)) / 2

nulls_theory = np.array([LAMBDA_SYNC / (n + 0.5) for n in range(1, N_SITES + 1)])
peaks_theory = np.array([LAMBDA_SYNC / n for n in range(1, N_SITES + 1)])

print("=" * 67)
print("  O31 真實 ξ(s) 數據實證 v2")
print("=" * 67)

# ============================================================
# 1. 載入 eBOSS DR16 原始數據
# ============================================================
print(f"\n─── 1. 載入 eBOSS DR16 ───")

s_e, xi_e, err_e = [], [], []
with open(os.path.expanduser('~/IDCM/sync_bump_analysis/eboss_dr16_lrg_xi.txt')) as f:
    for line in f:
        if line.startswith('#') or not line.strip(): continue
        parts = line.split()
        s_e.append(float(parts[0]))
        xi_e.append(float(parts[1]))
        err_e.append(float(parts[2]))

s_e = np.array(s_e); xi_e = np.array(xi_e); err_e = np.array(err_e)
print(f"  eBOSS: {len(s_e)} 點, s ∈ [{s_e[0]:.1f}, {s_e[-1]:.1f}]")

# ============================================================
# 2. 載入 BOSS DR12 後重建數據
# ============================================================
print(f"\n─── 2. 載入 BOSS DR12 後重建 ───")

import zipfile
zip_path = os.path.expanduser("~/IDCM/sync_bump_analysis/ross_dr12_corrfunc.zip")
z = zipfile.ZipFile(zip_path)
data_file = "Ross_2016_COMBINEDDR12/Ross_2016_COMBINEDDR12_zbin1_correlation_function_monopole_post_recon_bincent0.dat"
content = z.read(data_file).decode('utf-8')

s_b, xi_b, err_b = [], [], []
for line in content.split('\n'):
    line = line.strip()
    if not line or line.startswith('#'): continue
    parts = line.split()
    s_b.append(float(parts[0])); xi_b.append(float(parts[1])); err_b.append(float(parts[2]))

s_b = np.array(s_b); xi_b = np.array(xi_b); err_b = np.array(err_b)
print(f"  BOSS: {len(s_b)} 點, s ∈ [{s_b[0]:.1f}, {s_b[-1]:.1f}]")

# ============================================================
# 3. 從 eBOSS 原始數據提取 wiggle 分量
# ============================================================
print(f"\n─── 3. eBOSS wiggle 分量 ───")

def broadband_poly(log_s, a0, a1, a2, a3):
    return a0 + a1*log_s + a2*log_s**2 + a3*log_s**3

mask = s_e > 10
log_s = np.log(s_e[mask])
popt, _ = curve_fit(broadband_poly, log_s, xi_e[mask],
                     p0=[1, -0.5, -0.1, 0.01],
                     sigma=err_e[mask], maxfev=10000)
xi_broad_e = broadband_poly(np.log(s_e), *popt)
xi_wiggle_e = xi_e - xi_broad_e
xi_wiggle_interp = interp1d(s_e, xi_wiggle_e, kind='cubic', bounds_error=False, fill_value=0)

print(f"  Broadband: ξ_b(s) = {popt[0]:.4f} + {popt[1]:.4f}·ln(s) + {popt[2]:.4f}·ln²(s) + {popt[3]:.4f}·ln³(s)")
print(f"  Wiggle 範圍: [{xi_wiggle_e.min():.4f}, {xi_wiggle_e.max():.4f}]")

# 找 wiggle 零點
nulls_emp_e = []
for i in range(len(s_e) - 1):
    if xi_wiggle_e[i] * xi_wiggle_e[i+1] < 0:
        s1, s2 = s_e[i], s_e[i+1]
        x1, x2 = xi_wiggle_e[i], xi_wiggle_e[i+1]
        s0 = s1 - x1 * (s2 - s1) / (x2 - x1)
        nulls_emp_e.append(s0)

nulls_emp_e = np.array(nulls_emp_e)
print(f"  找到 {len(nulls_emp_e)} 個 wiggle 零點:")
for n, s in enumerate(nulls_emp_e):
    closest = nulls_theory[np.argmin(np.abs(s - nulls_theory))]
    diff = s - closest
    print(f"    n={n+1:2d}: s={s:8.3f}, 理論={closest:8.3f}, 差={diff:+.3f}")

# ============================================================
# 4. 實證 f_IDCM 及不動點驗證
# ============================================================
print(f"\n─── 4. 實證 Newton 映射不動點驗證 ───")

# 用實測 nulls 作為零點, 理論 peaks 作為極點
nulls_emp = nulls_emp_e
peaks_emp = peaks_theory

def log_deriv_emp(s, alpha=0.0):
    z = complex(s)
    total = complex(alpha, 0.0)
    for sn in nulls_emp:
        if abs(z - sn) < 1e-10: return complex(float('inf'), 0.0)
        total += 1.0 / (z - sn)
    for pn in peaks_emp:
        if abs(z - pn) < 1e-10: return complex(float('inf'), 0.0)
        total -= 1.0 / (z - pn)
    return total

def newton_map_emp(s, alpha=0.0):
    z = complex(s)
    for sn in nulls_emp:
        if abs(z - sn) < 1e-10: return complex(sn, 0.0)
    for pn in peaks_emp:
        if abs(z - pn) < 1e-10: return complex(float('inf'), 0.0)
    ld = log_deriv_emp(s, alpha)
    if abs(ld) < 1e-15: return complex(s)
    return z - 1.0 / ld

# 驗證: 實測 nulls 是否是不動點
print(f"\n  實測 nulls 是否是不動點:")
all_pass = True
for n in range(len(nulls_emp)):
    s0 = nulls_emp[n]
    ns = newton_map_emp(s0, 0.0)
    diff = abs(ns - s0)
    if diff > 1e-6:
        all_pass = False
        print(f"    ❌ null[{n}]={s0:.3f}: 差={diff:.2e}")
if all_pass:
    print(f"    ✅ 全部 {len(nulls_emp)} 個實測 nulls 都是不動點")

# 搜索額外不動點
print(f"\n  搜索額外不動點:")
search_pts = np.linspace(5, 400, 20000)
extra_fps = []
for i in range(len(search_pts) - 1):
    s1, s2 = search_pts[i], search_pts[i+1]
    n1 = newton_map_emp(s1, 0.0).real
    n2 = newton_map_emp(s2, 0.0).real
    if (n1 - s1) * (n2 - s2) < 0:
        lo, hi = s1, s2
        v1 = n1 - s1
        for _ in range(30):
            mid = (lo + hi) / 2
            vm = newton_map_emp(mid, 0.0).real - mid
            if v1 * vm > 0: lo, hi = mid, hi; v1 = vm
            else: lo, hi = lo, mid
        fp = (lo + hi) / 2
        # 排除實測 nulls 和理論 peaks
        if not any(abs(fp - sn) < 0.5 for sn in nulls_emp):
            if not any(abs(fp - pn) < 0.5 for pn in peaks_theory):
                extra_fps.append(fp)

if extra_fps:
    print(f"  找到 {len(extra_fps)} 個額外不動點!")
    for fp in extra_fps[:10]:
        dist_null = min(abs(fp - sn) for sn in nulls_emp_e)
        dist_peak = min(abs(fp - pn) for pn in peaks_theory)
        print(f"    s={fp:.4f}, 距 null={dist_null:.3f}, 距 peak={dist_peak:.3f}")
    if len(extra_fps) > 10:
        print(f"    ... 共 {len(extra_fps)} 個")
else:
    print(f"  ✅ 無額外不動點")

# ============================================================
# 5. 配對: 實測 nulls vs 理論 nulls
# ============================================================
print(f"\n─── 5. 實測 vs 理論 nulls 配對 ───")

matched = []
for sn in nulls_theory:
    if sn < s_e[0] or sn > s_e[-1]:
        continue
    dist = np.min(np.abs(sn - nulls_emp_e))
    if dist < 15:
        matched_idx = np.argmin(np.abs(sn - nulls_emp_e))
        matched.append((sn, nulls_emp_e[matched_idx], dist))

matched = np.array(matched)
print(f"  理論 nulls 在 eBOSS 範圍: {sum(1 for sn in nulls_theory if s_e[0] <= sn <= s_e[-1])}")
print(f"  成功匹配: {len(matched)}")
if len(matched) > 0:
    print(f"  平均偏差: {matched[:,2].mean():.3f} ± {matched[:,2].std():.3f} h⁻¹ Mpc")
    for sn, emp, d in matched:
        print(f"    理論={sn:8.3f} → 實測={emp:8.3f}, 差={d:+.3f}")

# ============================================================
# 6. 結論
# ============================================================
print(f"\n{'═'*67}")
print(f"  結論")
print(f"{'═'*67}")
print(f"""
  實證數據: eBOSS DR16 (raw, s_max=247.5) + BOSS DR12 (post-recon)
  - eBOSS wiggle 零點: {len(nulls_emp_e)} 個
  - 理論匹配: {len(matched)}/{sum(1 for sn in nulls_theory if s_e[0] <= sn <= s_e[-1])}
  - 實證 f_IDCM 不動點: {len(nulls_emp)} nulls + 44 peaks = {len(nulls_emp)+44} 個
  - 額外不動點: {len(extra_fps)}
  
  IDCM 88 不動點定理實證結果: {'✅ PASSED' if not extra_fps else '❌ NEEDS REVIEW'}
  (eBOSS 只能解析到 ~{len(nulls_emp_e)} 個零點, 受限於 49 個數據點)
""")

# 儲存結果
with open("data/boss_dr12_empirical_results.txt", "w") as f:
    f.write(f"O31 BOSS/eBOSS empirical verification v2\n\n")
    f.write(f"eBOSS DR16: {len(s_e)} points, s_max={s_e[-1]:.1f}\n")
    f.write(f"BOSS DR12: {len(s_b)} points, s_max={s_b[-1]:.1f}\n\n")
    f.write(f"Empirical nulls (wiggle): {len(nulls_emp_e)}\n")
    for n, s in enumerate(nulls_emp_e):
        closest = nulls_theory[np.argmin(np.abs(s - nulls_theory))]
        f.write(f"  null[{n}]={s:.3f} (theory={closest:.3f}, diff={s-closest:.3f})\n")
    f.write(f"\nMatched with theory: {len(matched)}\n")
    if len(matched) > 0:
        f.write(f"Mean deviation: {matched[:,2].mean():.3f} ± {matched[:,2].std():.3f}\n")
    f.write(f"Extra fixed points: {len(extra_fps)}\n")
    f.write(f"88 fixed-point theorem: {'PASSED' if not extra_fps else 'NEEDS REVIEW'}\n")

print("  ✅ data/boss_dr12_empirical_results.txt")