#!/usr/bin/env python3
"""
O32-42: IDCM SHMR 完善 — 參數擬合 + 幾何解釋
================================================
IDCM 固定參數: f_peak = 1/L₇ = 1/29, M_peak = M_c/F₄ = M_c/3
自由參數: β (低質量 slope), γ (高質量 slope)
擬合目標: GAMA 24,080 個星系-群對
"""
import numpy as np
import json
from astropy.io import fits

PHI = (1+np.sqrt(5))/2
def lucas(k): return round(PHI**k + (-PHI)**(-k))
def fib(k): return int(round(PHI**k/np.sqrt(5)))

MC = 1.8924e12
L7 = lucas(7)    # 29
F4 = fib(4)      # 3
f_peak = 1/L7    # 1/29
M_peak = MC/F4   # M_c/3

print("="*78)
print("IDCM SHMR 完善 — 參數擬合")
print("="*78)
print(f"固定參數: f_peak = 1/L₇ = 1/{L7} = {f_peak:.6f}")
print(f"固定參數: M_peak = M_c/F₄ = {MC:.3e}/{F4} = {M_peak:.3e}")

# 讀取數據
mp = fits.open("data/obs_data/MagPhys.fits")[1].data
gal = fits.open("data/obs_data/G3CGal.fits")[1].data
grp = fits.open("data/obs_data/G3CFoFGroup.fits")[1].data

# Cross-match
cataid_to_group = dict(zip(gal['CATAID'], gal['GroupID']))
group_to_props = dict(zip(grp['GroupID'], zip(grp['VelDisp'], grp['MassProxy'], grp['IterCenZ'])))

shmr_data = {'logM_star': [], 'logM_halo': []}
for i in range(len(mp)):
    cid = mp['CATAID'][i]
    if cid not in cataid_to_group: continue
    gid = cataid_to_group[cid]
    if gid <= 0 or gid not in group_to_props: continue
    vel, mass, z = group_to_props[gid]
    if vel <= 0 or mass <= 0: continue
    m_star = np.log10(mp['mass_stellar_best_fit'][i])
    if not np.isfinite(m_star) or m_star < 7: continue
    m_halo = np.log10(mass)
    if m_halo < 10 or m_halo > 15: continue
    shmr_data['logM_star'].append(m_star)
    shmr_data['logM_halo'].append(m_halo)

logM_star_arr = np.array(shmr_data['logM_star'])
logM_halo_arr = np.array(shmr_data['logM_halo'])
print(f"\n數據: {len(logM_star_arr)} 個星系-群對")

# Bin 平均
logM_bins = np.arange(10.5, 15.0, 0.3)
logM_c = (logM_bins[:-1] + logM_bins[1:]) / 2
bin_eps = []
for i in range(len(logM_bins)-1):
    mask = (logM_halo_arr >= logM_bins[i]) & (logM_halo_arr < logM_bins[i+1])
    if mask.sum() < 10: continue
    mean_mstar = logM_star_arr[mask].mean()
    mean_mhalo = logM_halo_arr[mask].mean()
    eps = 10**(mean_mstar - mean_mhalo)
    bin_eps.append({'logM_halo': mean_mhalo, 'eps': eps, 'N': int(mask.sum())})

# IDCM SHMR 函數
def idcm_shmr(M_halo, beta, gamma):
    x = M_halo / M_peak
    return 2 * f_peak / (x**(-beta) + x**gamma)

# 掃描 β, γ
print("\n--- 參數掃描 ---")
best = {'beta': 0, 'gamma': 0, 'chi2': 1e10}
results_list = []
for beta in np.arange(0.5, 3.0, 0.1):
    for gamma in np.arange(0.3, 1.5, 0.1):
        chi2 = 0
        for b in bin_eps:
            M = 10**b['logM_halo']
            pred = idcm_shmr(M, beta, gamma)
            err = max(b['eps'] * 0.1, 0.0001)
            chi2 += (b['eps'] - pred)**2 / err**2
        if chi2 < best['chi2']:
            best = {'beta': beta, 'gamma': gamma, 'chi2': chi2, 'dof': len(bin_eps)}
        results_list.append({'beta': beta, 'gamma': gamma, 'chi2': chi2})

print(f"最佳: β={best['beta']:.2f}, γ={best['gamma']:.2f}, χ²/dof={best['chi2']/best['dof']:.2f}")

# 最接近 Fibonacci 嘅候選
candidates = [
    (5/3, 1/PHI, "F₅/F₄, 1/φ"),
    (1.0, 0.618, "1, 1/φ"),
    (1.5, 0.618, "3/2, 1/φ"),
    (2.0, 0.618, "2, 1/φ"),
    (5/3, 0.5, "F₅/F₄, 1/2"),
    (1.37, 0.61, "Moster+2013"),
]
for beta, gamma, label in candidates:
    chi2 = 0
    for b in bin_eps:
        M = 10**b['logM_halo']
        pred = idcm_shmr(M, beta, gamma)
        err = max(b['eps'] * 0.1, 0.0001)
        chi2 += (b['eps'] - pred)**2 / err**2
    print(f"  {label:20s}: β={beta:.3f}, γ={gamma:.3f}, χ²/dof={chi2/len(bin_eps):.2f}")

# 最終輸出
print(f"\n--- 最佳 SHMR 對比 ---")
print(f"{'logM_halo':>10} {'N':>6} {'ε_GAMA':>10} {'ε_IDCM':>10} {'O/C':>10}")
for b in bin_eps:
    M = 10**b['logM_halo']
    pred = idcm_shmr(M, best['beta'], best['gamma'])
    ratio = b['eps'] / pred if pred > 0 else 0
    print(f"{b['logM_halo']:>10.2f} {b['N']:>6d} {b['eps']:>10.4f} {pred:>10.4f} {ratio:>10.2f}")

# 幾何解釋
print(f"\n--- 幾何解釋 ---")
print(f"最佳 β = {best['beta']:.3f}")
print(f"IDCM 候選 β = F₅/F₄ = 5/3 ≈ 1.667")
print(f"偏差: {abs(best['beta']-5/3)/(5/3)*100:.1f}%")
print(f"")
print(f"另一候選: β = F₅/F₄ - 1/(F₇) = 5/3 - 1/13 = {5/3-1/13:.4f}")
print(f"另一候選: β = (F₅-1)/F₄ = 4/3 = {4/3:.4f} (= α_IDCM!)")

# 用 α = 4/3 做 β
print(f"\n--- 如果用 β = α = 4/3 ≈ 1.333 ---")
chi2_alpha = 0
for b in bin_eps:
    M = 10**b['logM_halo']
    pred = idcm_shmr(M, 4/3, best['gamma'])
    err = max(b['eps'] * 0.1, 0.0001)
    chi2_alpha += (b['eps'] - pred)**2 / err**2
print(f"  β=4/3: χ²/dof={chi2_alpha/len(bin_eps):.2f}")

# 最佳 γ 嘅幾何解釋
print(f"\n最佳 γ = {best['gamma']:.3f}")
print(f"IDCM 候選 γ = 1/φ = {1/PHI:.3f}")
print(f"偏差: {abs(best['gamma']-1/PHI)/(1/PHI)*100:.1f}%")

# 保存
output = {
    'best_beta': best['beta'],
    'best_gamma': best['gamma'],
    'best_chi2dof': best['chi2']/best['dof'],
    'f_peak': f_peak,
    'M_peak': M_peak,
    'f_peak_expr': '1/L7',
    'M_peak_expr': 'M_c/F4',
    'beta_candidates': {'5/3': 5/3, '4/3': 4/3, 'Moster': 1.37},
    'gamma_candidate': 1/PHI,
    'n_galaxies': len(logM_star_arr)
}
with open('data/idcm_shmr_fit.json', 'w') as f:
    json.dump(output, f, indent=2)
print("\n結果已存: data/idcm_shmr_fit.json")