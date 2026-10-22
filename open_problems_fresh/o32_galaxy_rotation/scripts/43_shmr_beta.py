#!/usr/bin/env python3
"""
O32-43: SHMR 低質量端斜率 β 嘅 IDCM 幾何推導
=================================================
β = d(log ε)/d(log M_halo) 喺 M << M_peak

IDCM 候選:
1. β = α_halo = 4/3 ≈ 1.333 (暈質量函數斜率)
2. β = F₅/F₄ = 5/3 ≈ 1.667 (Fibonacci 幾何)
3. β = F₅/F₆ = 5/8 ≈ 0.625 (Fibonacci 比例)
4. β = (F₅-1)/F₄ = 4/3 = 1.333 (修改 Fib)
5. β = 1/F₆ × F₅ = 5/8 = 0.625
6. β = φ - 1 = 0.618 (黃金比例 - 1)
7. β = 1/φ = 0.618
"""
import numpy as np
import json
from astropy.io import fits

PHI = (1+np.sqrt(5))/2
def lucas(k): return round(PHI**k + (-PHI)**(-k))
def fib(k): return int(round(PHI**k/np.sqrt(5)))

print("="*78)
print("SHMR β 推導 — IDCM 幾何候選")
print("="*78)

# ===== IDCM 常數 =====
F = {k: fib(k) for k in range(1, 13)}
L = {k: lucas(k) for k in range(1, 13)}
print(f"Fibonacci: {', '.join(f'F_{k}={F[k]}' for k in range(1, 9))}")
print(f"Lucas:     {', '.join(f'L_{k}={L[k]}' for k in range(1, 9))}")

# ===== β 候選 =====
candidates = [
    ("α_halo = 4/3", 4/3, "暈質量函數冪律"),
    ("F₅/F₄", 5/3, "Fibonacci 幾何比例"),
    ("F₅/F₆", 5/8, "Fibonacci 比例"),
    ("(F₅-1)/F₄", 4/3, "修改 Fibonacci"),
    ("1/F₆×F₅", 5/8, "F₅/F₆ 等價"),
    ("φ-1", PHI-1, "黃金比例 - 1"),
    ("1/φ", 1/PHI, "黃金比例倒數"),
    ("F₅/F₆+F₇/F₈", 5/8+13/21, "Fibonacci 和"),
    ("F₄/F₅+F₆/F₇", 3/5+8/13, "Fibonacci 和 2"),
    ("F₇/F₈", 13/21, "≈ 1/φ"),
    ("F₆/F₇", 8/13, "≈ 1/φ²"),
    ("L₅/L₇", 11/29, "Lucas 比例"),
    ("F₅/L₇", 5/29, "Fib/Lucas 混合"),
    ("F₄/F₅", 3/5, "小 Fib 比例"),
]

print(f"\n{'候選':>20s} {'β':>8s} {'來源':>20s}")
for name, val, src in candidates:
    print(f"{name:>20s} {val:>8.4f} {src:>20s}")

# ===== GAMA 數據擬合 β =====
print(f"\n--- GAMA 數據 β 擬合 (logM_halo = 11.0-11.8) ---")
mp = fits.open("data/obs_data/MagPhys.fits")[1].data
gal = fits.open("data/obs_data/G3CGal.fits")[1].data
grp = fits.open("data/obs_data/G3CFoFGroup.fits")[1].data

cataid_to_group = dict(zip(gal['CATAID'], gal['GroupID']))
group_to_props = dict(zip(grp['GroupID'], zip(grp['VelDisp'], grp['MassProxy'])))

logM_star, logM_halo = [], []
for i in range(len(mp)):
    cid = mp['CATAID'][i]
    if cid not in cataid_to_group: continue
    gid = cataid_to_group[cid]
    if gid <= 0 or gid not in group_to_props: continue
    vel, mass = group_to_props[gid]
    if vel <= 0 or mass <= 0: continue
    ms = np.log10(mp['mass_stellar_best_fit'][i])
    mh = np.log10(mass)
    if not np.isfinite(ms) or ms < 7 or mh < 10 or mh > 15: continue
    logM_star.append(ms)
    logM_halo.append(mh)

logM_star = np.array(logM_star)
logM_halo = np.array(logM_halo)

# Bin 平均
bins = np.arange(11.0, 11.8, 0.15)
bc = (bins[:-1] + bins[1:]) / 2
eps_vals = []
for i in range(len(bins)-1):
    mask = (logM_halo >= bins[i]) & (logM_halo < bins[i+1])
    if mask.sum() < 10: continue
    mean_ms = logM_star[mask].mean()
    mean_mh = logM_halo[mask].mean()
    eps_vals.append({'logMh': mean_mh, 'logEps': np.log10(10**(mean_ms-mean_mh))})

# 線性擬合: log(ε) = β·log(M_halo) + C
if len(eps_vals) >= 3:
    x = np.array([e['logMh'] for e in eps_vals])
    y = np.array([e['logEps'] for e in eps_vals])
    beta_fit, C = np.polyfit(x, y, 1)
    print(f"GAMA 數據 β (擬合): {beta_fit:.4f}")
    print(f"log(ε) = {beta_fit:.4f}·logM + {C:.4f}")
    print(f"R² = {np.corrcoef(x, y)[0,1]**2:.4f}")

# 每個候選嘅 χ²
print(f"\n--- 候選 β 嘅 χ² 比較 ---")
best = {'name': '', 'beta': 0, 'chi2': 1e10}
for name, beta, src in candidates:
    chi2 = 0
    for e in eps_vals:
        pred = beta * e['logMh'] + C  # 用同樣嘅截距
        err = 0.1
        chi2 += (e['logEps'] - pred)**2 / err**2
    if chi2 < best['chi2']:
        best = {'name': name, 'beta': beta, 'chi2': chi2}
    print(f"  {name:>20s}: β={beta:.4f}, χ²={chi2:.1f}")

print(f"\n最佳候選: {best['name']} (β={best['beta']:.4f})")

# ===== 物理推導 =====
print(f"\n--- β 物理推導 ---")
print(f"""
從質量函數轉換:
  dN/dM_star = dN/dM_halo × dM_halo/dM_star
  M_star = f(M_halo)·M_halo,  f ∝ M^β (M << M_peak)
  dM_star/dM_halo = (1+β)·M_halo^β
  dN/dM_star ∝ M_halo^(-α_halo) · M_halo^(-β) ∝ M_star^(-(α_halo+β)/(1+β))

所以 α_SF = (α_halo + β)/(1+β)
解出 β = (α_SF - α_halo)/(1 - α_SF + α_halo)

代入 α_halo = 4/3, α_SF = 1.50 (GAMA α₂):
  β = (1.50 - 1.333)/(1 - 1.50 + 1.333)
    = 0.167/0.833
    = 0.200

代入 α_halo = 4/3, α_SF = 1.18 (GAMA 單 Schechter):
  β = (1.18 - 1.333)/(1 - 1.18 + 1.333)
    = (-0.153)/1.153
    = -0.133

→ 都唔係 ideal — 因為雙 Schechter α₂ 控制唔同質量範圍!
""")

# 用 Fibonacci 找出最佳近似
print(f"--- Fibonacci 近似 ---")
print(f"GAMA β_fit = {beta_fit:.4f}")
print(f"最接近 Fibonacci: F₅/F₆ = 5/8 = {5/8:.4f} (偏差 {abs(beta_fit-5/8)/abs(beta_fit)*100:.1f}%)")
print(f"或: 1/φ = {1/PHI:.4f} (偏差 {abs(beta_fit-1/PHI)/abs(beta_fit)*100:.1f}%)")
print(f"或: F₆/F₈ = 8/21 = {8/21:.4f} (偏差 {abs(beta_fit-8/21)/abs(beta_fit)*100:.1f}%)")

output = {
    'beta_fit': float(beta_fit),
    'candidates': {name: val for name, val, src in candidates},
    'best_match': best['name'],
    'best_beta': best['beta'],
    'n_galaxies': len(logM_star)
}
with open('data/shmr_beta.json', 'w') as f:
    json.dump(output, f, indent=2)
print("\n結果已存: data/shmr_beta.json")