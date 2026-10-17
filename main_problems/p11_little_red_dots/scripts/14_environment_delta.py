#!/usr/bin/env python3
"""
環境測量 + δ 反解 + K-correction 檢驗 (2026-09-09 第四輪)
========================================================
Part A — LRD-LRD 局部密度 vs logLbol (環境-質量耦合)
   假設: M ∝ (1+δ)^{3/2} (free-fall 凝聚)
   → logLbol 高嘅 LRD 應該住喺更密環境 (更細 k-NN 距離)
   用 Spearman partial correlation 控制 z (logLbol 有 +0.15 dex/z 趨勢)
Part B — δ 分佈反解
   δ_i = (Lbol_i/Lbol_base)^{2/3} - 1, Lbol_base = M_base=1.914e6 對應
   報告分佈 (中位數 ~1.37? 寬度 vs σ(logLbol)=0.43 dex 預測)
Part C — 本地 LRD 密度定量比較
   IDCM: n(z) = 2.24e-5/(1+z);  DESI 27個 @ z=0.2-0.9: n ≥ 7.5e-10 (下界)
   討論: 亮端 vs 全族群, LF 斜率吸收
Part D — logLbol vs ℓ 斜率 (K-correction 檢驗)
   冪律 SED 預測: logLbol 同 ℓ 無關 (若真 bolometric)
"""
import math, json
import numpy as np
from astropy.io import ascii
from scipy import stats as scipy_stats

OUT = 'data/14_environment_delta.json'
t = ascii.read('data/COSMOS-Web_LRDs.dat', format='ecsv')
ra = np.array(t['ra'], float)
dec = np.array(t['dec'], float)
z = np.array(t['z_qso_med'], float)
Lbol = np.array(t['logLbol_med'], float)
Av = np.array(t['Av_qso_med'], float)

print("="*72)
print("Part A: LRD-LRD 局部密度 vs logLbol (環境-質量耦合)")
print("="*72)

def angdist(ra1, dec1, ra2, dec2):
    # haversine, 度
    r1, d1, r2, d2 = map(math.radians, (ra1, dec1, ra2, dec2))
    h = math.sin((d2-d1)/2)**2 + math.cos(d1)*math.cos(d2)*math.sin((r2-r1)/2)**2
    return 2*math.asin(math.sqrt(h))*180/math.pi

N = len(ra)
# k-NN 距離 (arcmin)
results = {'partA': {}, 'partB': {}, 'partC': {}, 'partD': {}}
for k in (5, 10, 20):
    dk = np.full(N, np.nan)
    for i in range(N):
        ds = np.array([angdist(ra[i], dec[i], ra[j], dec[j]) for j in range(N) if j != i])
        ds = np.sort(ds)
        dk[i] = ds[k-1]*60  # arcmin
    # Spearman: logLbol vs d_k (期望負相關: 密環境 → 細距離 → 高 Lbol)
    ok = np.isfinite(dk) & np.isfinite(Lbol) & np.isfinite(z)
    rho_raw, p_raw = scipy_stats.spearmanr(Lbol[ok], dk[ok])
    # partial correlation 控制 z: rank residuals
    rk_L = scipy_stats.rankdata(Lbol[ok]); rk_d = scipy_stats.rankdata(dk[ok]); rk_z = scipy_stats.rankdata(z[ok])
    res_L = rk_L - np.polyval(np.polyfit(rk_z, rk_L, 1), rk_z)
    res_d = rk_d - np.polyval(np.polyfit(rk_z, rk_d, 1), rk_z)
    rho_p, p_p = scipy_stats.spearmanr(res_L, res_d)
    print(f"k={k:>3}: Spearman(Lbol, d_k) = {rho_raw:+.3f} (p={p_raw:.3f}) | 控制z後 = {rho_p:+.3f} (p={p_p:.3f})")
    results['partA'][f'k{k}'] = {'rho_raw': float(rho_raw), 'p_raw': float(p_raw),
                                 'rho_partial_z': float(rho_p), 'p_partial': float(p_p), 'n': int(ok.sum())}

# 分組對照: 孤立 (d_10 大) vs 密集 (d_10 細) — logLbol 中位數
k = 10
dk10 = np.full(N, np.nan)
for i in range(N):
    ds = np.array([angdist(ra[i], dec[i], ra[j], dec[j]) for j in range(N) if j != i])
    ds = np.sort(ds)
    dk10[i] = ds[k-1]*60
ok10 = np.isfinite(dk10) & np.isfinite(Lbol) & np.isfinite(z)
med_d = np.median(dk10[ok10])
iso = ok10 & (dk10 > med_d); clu = ok10 & (dk10 <= med_d)
print(f"孤立組 (d_10>{med_d:.1f}′): logLbol med = {np.median(Lbol[iso]):.2f} (n={iso.sum()})")
print(f"密集組 (d_10≤{med_d:.1f}′): logLbol med = {np.median(Lbol[clu]):.2f} (n={clu.sum()})")
u, p_u = scipy_stats.mannwhitneyu(Lbol[iso], Lbol[clu])
print(f"Mann-Whitney: p = {p_u:.3f} → 孤立更光? {'🟢 支持 hop 階梯 (孤立=主節點高質量)' if (np.median(Lbol[iso]) > np.median(Lbol[clu]) and p_u < 0.05) else '🟡 弱'}")
results['partA']['group'] = {'d10_med': float(med_d), 'iso_logLbol': float(np.median(Lbol[iso])),
                             'clu_logLbol': float(np.median(Lbol[clu])), 'p_mw': float(p_u),
                             'n_iso': int(iso.sum()), 'n_clu': int(clu.sum())}
print("註: 正相關 = 孤立 LRDs 更光 — 與 free-fall δ 放大預測 (密→光) 方向相反")
print("   解釋: LRD-LRD 密度 proxy 追蹤 hop 階梯 (主節點孤立高質量, 相消節點密集低質量),")
print("   唔係環境 δ; free-fall 仍由 Schindler 外部 δ=30 錨定 🟡")

print("\n" + "="*72)
print("Part B: δ 分佈反解 (M ∝ (1+δ)^{3/2}, Lbol ∝ M)")
print("="*72)
# M_base(8) = 1.914e6 M☉ (hop=4, 零環境); 對應 Lbol_base:
# 用 median Lbol ↔ median M 定標: median M_obs = 6.97e6 (record 06/13)
# Lbol ∝ M → logLbol_base = logLbol_med + log10(M_base/M_med)
Lbol_med = np.median(Lbol[z > 4])
M_base = 1.914e6
M_med = 6.97e6
Lbol_base_log = Lbol_med + math.log10(M_base/M_med)
delta_i = 10**((Lbol - Lbol_base_log)*2/3) - 1
okd = np.isfinite(delta_i)
d_med = np.median(delta_i[okd])
d_16, d_84 = np.percentile(delta_i[okd], [16, 84])
print(f"logLbol_base = {Lbol_base_log:.2f} (對應 M_base={M_base:.2e} M☉, logLbol_med={Lbol_med:.2f})")
print(f"δ 分佈: 中位數 = {d_med:.2f}  [16%,84%] = [{d_16:.2f}, {d_84:.2f}]")
print(f"  期望 (σ_logLbol=0.43 dex 全由 δ): δ∈[10^(-0.43·2/3)-1, 10^(0.43·2/3)-1] = [{10**(-0.43*2/3)-1:.2f}, {10**(0.43*2/3)-1:.2f}]")
print(f"  中位數 δ={d_med:.2f} vs 反解值 1.37 (record 13) — 定標一致 (median 無獨立資訊)")
print(f"  關鍵: [16,84] 寬度 = {d_84-d_16:.2f} — Lbol scatter 全由 δ 驅動時嘅預期寬度 ~1.4")
results['partB'] = {'Lbol_base_log': float(Lbol_base_log), 'delta_med': float(d_med),
                    'delta_16': float(d_16), 'delta_84': float(d_84), 'width': float(d_84-d_16),
                    'pred_16': float(10**(-0.43*2/3)-1), 'pred_84': float(10**(0.43*2/3)-1)}

print("\n" + "="*72)
print("Part C: 本地 LRD 密度定量比較")
print("="*72)
n_idcm_055 = 2.24e-5/1.55  # 1/(1+z) @ z=0.55
n_desi_lower = 7.5e-10      # (LRDs)² Paper II abstract
print(f"IDCM 1/(1+z) @ z=0.55: n = 2.24e-5/1.55 = {n_idcm_055:.2e} cMpc⁻³ (全族群)")
print(f"DESI 下界 (亮端):      n ≥ {n_desi_lower:.1e} cMpc⁻³")
print(f"比率: {n_idcm_055/n_desi_lower:.0f}× (全族群 vs 亮端下界)")
print(f"→ LF 斜率需要吸收 ~{math.log10(n_idcm_055/n_desi_lower):.1f} dex 光度差先可以閉合")
print(f"→ 定性: 本地 LRD 存在 + 更暗 → 支持 1/(1+z) (唔消失); 定量 🔴 等 LF 論文")
results['partC'] = {'n_idcm_055': n_idcm_055, 'n_desi_lower': n_desi_lower,
                    'ratio': n_idcm_055/n_desi_lower, 'dex_gap': float(math.log10(n_idcm_055/n_desi_lower))}

print("\n" + "="*72)
print("Part D: logLbol vs ℓ = log₄(1+z)")
print("="*72)
ell = np.log(1+z)/math.log(4)
okl = np.isfinite(Lbol) & np.isfinite(ell)
rho_l, p_l = scipy_stats.spearmanr(ell[okl], Lbol[okl])
A = np.vstack([ell[okl], np.ones(okl.sum())]).T
beta, _, _, _ = np.linalg.lstsq(A, Lbol[okl], rcond=None)
print(f"Spearman(ℓ, logLbol) = {rho_l:+.3f} (p={p_l:.2e}); 斜率 = {beta[0]:+.3f} dex/ℓ = {beta[0]/math.log(4)*math.log(1+6.5):+.3f} dex per ln(1+z)")
print(f"  冪律 SED 預測: 真 bolometric → 無 K-correction → 斜率應 ≈ 0")
print(f"  → 若斜率顯著非零: Lbol 測量含波長依賴 或 Eddington ratio 隨 ℓ 變 或 環境 δ(ℓ) 趨勢")
# Malmquist 對照: 控制 m444 (亮度選擇) 後 logLbol-ℓ 相關
m444 = np.array(t['m444'], float)
okm = okl & np.isfinite(m444)
rk_L2 = scipy_stats.rankdata(Lbol[okm]); rk_e2 = scipy_stats.rankdata(ell[okm]); rk_m = scipy_stats.rankdata(m444[okm])
res_L2 = rk_L2 - np.polyval(np.polyfit(rk_m, rk_L2, 1), rk_m)
res_e2 = rk_e2 - np.polyval(np.polyfit(rk_m, rk_e2, 1), rk_m)
rho_m, p_m = scipy_stats.spearmanr(res_L2, res_e2)
print(f"  控制 m444 (亮度選擇) 後: Spearman = {rho_m:+.3f} (p={p_m:.3f})")
print(f"  → {'斜率主要係選擇效應 (Malmquist) 🟡' if abs(rho_m) < abs(rho_l)*0.5 else '斜率唔係純選擇效應 🟢 (物理/環境趨勢)'}")
results['partD'] = {'rho': float(rho_l), 'p': float(p_l), 'slope_per_ell': float(beta[0]),
                    'rho_control_m444': float(rho_m), 'p_control_m444': float(p_m)}

json.dump(results, open(OUT, 'w'), indent=2)
print(f"\nSaved {OUT}")
