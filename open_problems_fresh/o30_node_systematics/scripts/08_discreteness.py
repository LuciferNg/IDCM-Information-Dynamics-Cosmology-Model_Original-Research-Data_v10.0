#!/usr/bin/env python3
"""
08_discreteness.py — O30 完成: 溫度效應離散性
==============================================
O30 已否定「全部 60 節點有異常」(連續異常: z<1.5σ 全線)。
本 script 完成修正假說 — 溫度效應離散性:
  異常只存在於少數特定節點 (node0/node9/ΔE=0), 其餘節點 θ≈π/2 正交無效應。

測試:
  1. 方差檢驗 — 連續異常 ⇒ 節點方差膨脹; 節點 std vs 隨機場點統計 std (F-test)
  2. 相位正交檢驗 — δT=A·cos(θ), A=134.2 μK; |cosθ_i|=|T_i|/A 分佈
     mean|cosθ| vs 均勻相位期望 2/π=0.637; fraction(|cosθ|<0.5) vs 期望 1/3
  3. 跨尺度穩定異常計數 — 每節點 z_i(scale) 跨 0.5-10° mean|z̄_i|>2 嘅節點數
     vs 1000 組隨機 60 點模擬 (真異常跨尺度穩定, 隨機場漂移)
  4. BIC 模型比較 — |T| ~ 半高斯 (null, 1 param) vs
     2-component mixture (離散異常: 窄背景 + 寬異常, 3 params)
  5. 剩餘節點異常上限 — 剔除 {0,9}+ΔE=0 12 節點後, 剩餘 46 節點 mean|T|
     vs 隨機 46 點 95% 分位 + bootstrap CI
框架: 4.17° 平滑 SMICA (1-3), smooth_cache 全尺度 (3)
"""
import healpy as hp
import numpy as np
import os
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy import stats, optimize

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
CACHE_DIR = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")
NODES = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
OUT = os.path.join(BASE, "o30_node_systematics/data")

RNG = np.random.default_rng(20260817)
N_SIM = 1000
A_AMP = 134.2  # μK, 冷斑幅度 (相位模型 δT = A·cosθ)
ZERO_E = [10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46]  # ΔE=0 節點 (O3)
SCALES = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
MAPS = {0.5: "smica2_smooth0.5.fits", 1.0: "smica2_smooth1.0.fits",
        1.5: "smica2_smooth1.5.fits", 2.0: "smica2_smooth2.0.fits",
        3.0: "smica2_smooth3.0.fits", 4.0: "smica2_smooth4.0.fits",
        4.17: "smica2_smooth4.17.fits", 5.0: "smica2_smooth5.0.fits",
        7.0: "smica2_smooth7.0.fits", 10.0: "smica2_smooth10.0.fits"}

print("=" * 66)
print("O30-08: 溫度效應離散性 (完成修正假說)")
print("=" * 66)

# ---------- 載入 4.17° + 節點 ----------
m = hp.read_map(os.path.join(CACHE_DIR, MAPS[4.17]), field=0)
nside = hp.get_nside(m)
npix = hp.nside2npix(nside)
nodes = np.loadtxt(NODES)
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg, b_deg = gal.l.deg, gal.b.deg
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T = m[pix] * 1e6  # μK
A_node = np.abs(T)

print(f"SMICA 4.17°: NSIDE={nside}, map std={m.std()*1e6:.2f} μK")
print(f"節點: mean={T.mean():+.2f}, std={T.std(ddof=1):.2f}, mean|T|={A_node.mean():.2f} μK")

# ============================================================
# 1. 方差檢驗 — 連續異常 ⇒ 方差膨脹?
# ============================================================
print("\n" + "=" * 66)
print("1. 方差檢驗 (連續異常 = 方差膨脹)")
print("=" * 66)
std_map = m.std() * 1e6  # 隨機場點統計 σ (4.17° 平滑)
std_node = T.std(ddof=1)
F_obs = std_node**2 / std_map**2
# F-test: n=60 節點 vs 巨大 map 樣本 → 用 chi2 近似 (n-1)·s²/σ² ~ chi2(59)
chi2_obs = (60 - 1) * std_node**2 / std_map**2
p_var = 2 * min(stats.chi2.cdf(chi2_obs, 59), 1 - stats.chi2.cdf(chi2_obs, 59))
print(f"節點 std = {std_node:.2f} μK vs 隨機場 std = {std_map:.2f} μK")
print(f"F = {F_obs:.3f}, χ²(59) = {chi2_obs:.1f}, p = {p_var:.4f}")
print(f"→ {'🟢 方差膨脹 = 連續異常存在' if p_var < 0.05 else '🔴 方差無膨脹 = 冇連續異常 (離散或無)'}")

# ============================================================
# 2. 相位正交檢驗 — |cosθ| = |T|/A 分佈
# ============================================================
print("\n" + "=" * 66)
print("2. 相位正交檢驗 (δT = A·cosθ, A = 134.2 μK)")
print("=" * 66)
cos_abs = A_node / A_AMP  # |cosθ_i|, 截斷到 1
cos_abs = np.clip(cos_abs, 0, 1)
mean_cos = cos_abs.mean()
frac_small = (cos_abs < 0.5).mean()  # |cosθ|<0.5 ⇒ θ∈(60°,120°) 正交帶
# 均勻相位期望
exp_mean_cos = 2 / np.pi  # 0.637
exp_frac_small = 1 / 3    # P(|cosθ|<0.5) = 1/3
# 隨機場噪聲校正: 觀察 |T| = |A·cosθ + ε|, ε~N(0,σ_map)
# 純噪聲 (cosθ=0) 期望 mean|T| = σ_map·√(2/π)
noise_mean_abs = std_map * np.sqrt(2 / np.pi)
print(f"mean|cosθ| = {mean_cos:.3f} vs 均勻期望 {exp_mean_cos:.3f} (2/π)")
print(f"fraction(|cosθ|<0.5) = {frac_small:.3f} vs 均勻期望 {exp_frac_small:.3f}")
print(f"純噪聲期望 mean|T| = {noise_mean_abs:.2f} μK (σ_map·√(2/π))")
print(f"觀察 mean|T| = {A_node.mean():.2f} μK — 相位貢獻 ≈ {A_node.mean()-noise_mean_abs:+.2f} μK")
# bootstrap 檢驗 mean|cosθ| < 0.5 (正交集中)
boot = np.empty(N_SIM)
for k in range(N_SIM):
    rpix = RNG.integers(0, npix, size=60)
    boot[k] = np.abs(m[rpix]).mean() * 1e6 / A_AMP
z_phase = (mean_cos - boot.mean()) / boot.std(ddof=1)
p_phase = stats.norm.cdf(z_phase)  # 單尾: 相位貢獻 < 隨機期望
print(f"bootstrap (1000 隨機場): mean|cosθ| = {boot.mean():.3f} ± {boot.std(ddof=1):.3f}")
print(f"z = {z_phase:+.2f}σ, p(單尾 幅度<隨機) = {p_phase:.4f}")
print(f"→ {'🟢🟢 相位集中正交 (離散性成立)' if z_phase < -2 else ('🟢 邊緣' if z_phase < -1.5 else '🔴 相位均勻 (連續性)')}")

# ============================================================
# 3. 跨尺度穩定異常計數
# ============================================================
print("\n" + "=" * 66)
print("3. 跨尺度穩定異常計數 (真異常跨 0.5-10° 穩定)")
print("=" * 66)
# 預先載入所有尺度 map (ud_grade nside 512 保留光束, 快+省記憶體)
NSD = 512
npix_d = hp.nside2npix(NSD)
maps_d = {}
for s in SCALES:
    ms = hp.read_map(os.path.join(CACHE_DIR, MAPS[s]), field=0)
    ms_d = hp.ud_grade(ms, NSD)
    maps_d[s] = ms_d
    if s == 4.17:
        std_map = ms_d.std() * 1e6  # 用 nside512 一致性

# 每尺度 z 分數 (map 全局標準化)
Z = np.zeros((len(SCALES), 60))
for si, s in enumerate(SCALES):
    ms = maps_d[s]
    pxs = hp.ang2pix(NSD, l_deg, b_deg, lonlat=True)
    T_s = ms[pxs] * 1e6
    mu_s, sd_s = ms.mean() * 1e6, ms.std() * 1e6
    Z[si] = (T_s - mu_s) / sd_s
zbar = Z.mean(axis=0)  # 每節點跨尺度 mean z
zbar_abs = np.abs(zbar)
n_stable = (zbar_abs > 2).sum()
max_zbar = zbar_abs.max()
stable_idx = np.where(zbar_abs > 2)[0]
print(f"跨尺度 mean|z̄| > 2 嘅節點: {n_stable} 個 {list(stable_idx)}")
print(f"max|z̄| = {max_zbar:.2f}σ (node {np.argmax(zbar_abs)})")

# 隨機模擬: 1000 組隨機 60 點跨尺度 (vectorized 抽樣, maps 已喺記憶體)
sim_stable = np.empty(N_SIM)
sim_max = np.empty(N_SIM)
for k in range(N_SIM):
    Zs = np.zeros((len(SCALES), 60))
    for si, s in enumerate(SCALES):
        ms = maps_d[s]
        rpix = RNG.integers(0, npix_d, size=60)
        T_s = ms[rpix] * 1e6
        Zs[si] = (T_s - ms.mean() * 1e6) / (ms.std() * 1e6)
    zbs = np.abs(Zs.mean(axis=0))
    sim_stable[k] = (zbs > 2).sum()
    sim_max[k] = zbs.max()

p_stable = (sim_stable >= n_stable).mean()
p_max = (sim_max >= max_zbar).mean()
print(f"隨機模擬: count(>2σ) = {sim_stable.mean():.2f} ± {sim_stable.std(ddof=1):.2f} (觀察 {n_stable})")
print(f"  p(count≥{n_stable}) = {p_stable:.4f}")
print(f"隨機模擬: max|z̄| = {sim_max.mean():.2f} ± {sim_max.std(ddof=1):.2f} (觀察 {max_zbar:.2f})")
print(f"  p(max≥{max_zbar:.2f}) = {p_max:.4f}")
print(f"→ {'🟢🟢 穩定異常節點超出隨機 = 離散異常存在' if p_max < 0.05 else '🔴 冇超出隨機嘅穩定異常'}")

# ============================================================
# 4. BIC 模型比較: null 半高斯 vs 離散 mixture
# ============================================================
print("\n" + "=" * 66)
print("4. BIC: |T| ~ 半高斯 (null) vs 2-component mixture (離散)")
print("=" * 66)
n = len(A_node)

def ll_halfnorm(x, s):
    """HalfNormal(0,s) log-likelihood"""
    return np.sum(np.log(2 / (s * np.sqrt(2 * np.pi))) - x**2 / (2 * s**2))

def ll_mix(params, x):
    ls1, ls2, logit_p = params
    s1, s2 = np.exp(ls1), np.exp(ls2)
    p = 1 / (1 + np.exp(-logit_p))
    if s1 > s2:  # 保證 σ1 < σ2
        s1, s2 = s2, s1
    pdf1 = (2 / (s1 * np.sqrt(2 * np.pi))) * np.exp(-x**2 / (2 * s1**2))
    pdf2 = (2 / (s2 * np.sqrt(2 * np.pi))) * np.exp(-x**2 / (2 * s2**2))
    return np.sum(np.log(p * pdf1 + (1 - p) * pdf2))

# M_null: MLE σ² = mean(|T|²)
s_null = np.sqrt((A_node**2).mean())
ll0 = ll_halfnorm(A_node, s_null)
k0, bic0 = 1, 1 * np.log(n) - 2 * ll0

# M_disc: 3 params
best = None
for seed in [(np.log(20), np.log(60), 0.0), (np.log(30), np.log(80), -1.0), (np.log(25), np.log(50), 1.0)]:
    res = optimize.minimize(lambda p: -ll_mix(p, A_node), seed, method="Nelder-Mead",
                            options={"maxiter": 5000, "xatol": 1e-8, "fatol": 1e-10})
    if best is None or res.fun < best.fun:
        best = res
ll1 = -best.fun
k1, bic1 = 3, 3 * np.log(n) - 2 * ll1
ls1, ls2, logit_p = best.x
s1m, s2m = np.exp(ls1), np.exp(ls2)
if s1m > s2m:
    s1m, s2m = s2m, s1m
pm = 1 / (1 + np.exp(-logit_p))

print(f"M_null (1 param): σ={s_null:.2f}, BIC={bic0:.1f}")
print(f"M_disc (3 params): σ1={s1m:.2f} ({pm:.2f}), σ2={s2m:.2f} ({1-pm:.2f}), BIC={bic1:.1f}")
print(f"ΔBIC = {bic0 - bic1:+.1f} ({'M_disc 勝' if bic1 < bic0 else 'M_null 勝'})")
print(f"→ {'🟢🟢 離散模型勝 (異常節點分離)' if bic1 < bic0 - 6 else ('🟢 微弱' if bic1 < bic0 else '🔴 冇離散結構')}")

# ============================================================
# 5. 剩餘節點異常上限
# ============================================================
print("\n" + "=" * 66)
print("5. 剩餘節點異常上限 (剔除 {0,9}+ΔE=0 12 節點)")
print("=" * 66)
drop = set([0, 9] + ZERO_E)
keep_idx = np.array([i for i in range(60) if i not in drop])
A_keep = A_node[keep_idx]
print(f"剩餘 {len(keep_idx)} 節點 (剔除 {60-len(keep_idx)}: node0, node9, ΔE=0×12)")
print(f"剩餘 mean|T| = {A_keep.mean():.2f} μK")

# 隨機 46 點 mean|T| 分佈
ctrl46 = np.empty(N_SIM)
for k in range(N_SIM):
    rpix = RNG.integers(0, npix, size=len(keep_idx))
    ctrl46[k] = np.abs(m[rpix]).mean() * 1e6
pct95 = np.percentile(ctrl46, 95)
z_keep = (A_keep.mean() - ctrl46.mean()) / ctrl46.std(ddof=1)
print(f"隨機 {len(keep_idx)} 點 mean|T| = {ctrl46.mean():.2f} ± {ctrl46.std(ddof=1):.2f} μK")
print(f"95% 分位 = {pct95:.2f} μK | 剩餘節點 = {A_keep.mean():.2f} μK")
print(f"z = {z_keep:+.2f}σ | 剩餘節點喺隨機 95% 內? {'✅ 係' if A_keep.mean() < pct95 else '❌ 唔係'}")
# 異常幅度上限: 剩餘節點 mean|T| 超出隨機期望嘅量
excess = A_keep.mean() - ctrl46.mean()
upper = excess + 2 * ctrl46.std(ddof=1)
print(f"剩餘節點異常幅度上限 (mean|T| 超出隨機): {excess:+.2f} ± {2*ctrl46.std(ddof=1):.2f} μK (2σ)")
print(f"→ 每節點殘餘異常 < {max(0, upper):.1f} μK (mean|T|) — 遠低於 F₅=150 μK 預測")

# ============================================================
# 儲存
# ============================================================
with open(os.path.join(OUT, "08_discreteness.txt"), "w") as f:
    f.write("# O30-08: 溫度效應離散性\n")
    f.write(f"# 日期: 2026-08-21, A={A_AMP} μK, 模擬 {N_SIM}\n")
    f.write(f"# 1_VARIANCE: std_node={std_node:.3f} std_map={std_map:.3f} F={F_obs:.3f} p={p_var:.4f}\n")
    f.write(f"# 2_PHASE: mean_cos={mean_cos:.4f} frac_small={frac_small:.4f} z={z_phase:+.3f} p1={p_phase:.4f}\n")
    f.write(f"# 3_STABLE: n_stable={n_stable} max_zbar={max_zbar:.3f} p_count={p_stable:.4f} p_max={p_max:.4f} idx={list(stable_idx)}\n")
    f.write(f"# 4_BIC: null_bic={bic0:.2f} disc_bic={bic1:.2f} d_bic={bic0-bic1:+.2f} s1={s1m:.2f} s2={s2m:.2f} p_mix={pm:.3f}\n")
    f.write(f"# 5_REMAIN: n_keep={len(keep_idx)} mean_abs={A_keep.mean():.3f} ctrl_mean={ctrl46.mean():.3f} pct95={pct95:.3f} z={z_keep:+.3f} excess={excess:+.3f}\n")
    f.write("# zbar per node (跨尺度 mean z)\n")
    for i in range(60):
        f.write(f"{i} {zbar[i]:+.4f}\n")

print(f"\n✅ 已存: {os.path.join(OUT, '08_discreteness.txt')}")
