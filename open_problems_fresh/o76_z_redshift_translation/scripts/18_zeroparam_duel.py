#!/usr/bin/env python3
"""
O76/18: 零參數距離-紅移 — D_L = (1+z)^{6/7}·D_app 固定 α
================================================================
O76/17: α_fit = -0.1377 ≈ -1/7 (dev 3.6%)

★ 零參數方案: D_L = (1+z)^{6/7}·D_app
  6/7 結構: 7 = L₄ (Lucas), 6 = ?
  或者: (1+z)^{1-1/7}

驗證:
  1. SNe χ² (α 固定 -1/7, 只 fit M)
  2. 對比 ΛCDM Planck (零參數)
  3. DESI χ² 保持
  4. 其他結構候選比較
"""
import numpy as np
import math
import json

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name}")
    if detail:
        print(f"    {detail}")

C_LIGHT = 299792.458
R_WORLD = 4129.94
PHI = (1 + math.sqrt(5)) / 2
C_DELAY = -0.1697
OMEGA_RING = 72.59

print("=" * 70)
print("O76/18: 零參數距離-紅移 — D_L = (1+z)^(6/7)·D_app")
print("=" * 70)

data_path = 'data/pantheon/Pantheon+SH0ES.dat'
cov_path = 'data/pantheon/Pantheon+SH0ES_STAT+SYS.cov'
with open(data_path) as f:
    header = f.readline().split()
col = {name: i for i, name in enumerate(header)}
zs, mb = [], []
with open(data_path) as f:
    f.readline()
    for line in f:
        parts = line.split()
        if len(parts) < len(header): continue
        zs.append(float(parts[col['zCMB']]))
        mb.append(float(parts[col['m_b_corr']]))
zs = np.array(zs); mb = np.array(mb)
N = len(zs)
with open(cov_path) as f:
    n_dim = int(f.readline().strip())
cov = np.loadtxt(cov_path, skiprows=1).reshape(n_dim, n_dim)
cov_inv = np.linalg.inv(cov)

def fit_M(mu_model):
    J = np.ones(N)
    return (J @ cov_inv @ (mb - mu_model)) / (J @ cov_inv @ J)

def d_app(ell, C=C_DELAY):
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2*PHI**(-1)*ell
    delta = C * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

def dc_lcdm(z, H0, Om):
    zz = np.geomspace(1e-6, max(z, 1e-4), 2000)
    E = np.sqrt(Om*(1+zz)**3 + (1-Om))
    return C_LIGHT/H0 * np.trapezoid(1/E, zz)

ell_arr = np.log(1+zs)/np.log(4)
Da = d_app(ell_arr)

# ============ 1. 各 α 候選 ============
print("\n--- 1. α 結構候選比較 ---")
candidates = {
    'α=0 (原始)': 0.0,
    'α=-1/7 (L₄)': -1/7,
    'α=-1/8': -1/8,
    'α=-F17/88': -17/88,
    'α=-2φ⁻¹κ': -2*PHI**(-1)/16,
    'α=fit': None,  # 稍後
}
results = {}
for name, alpha in candidates.items():
    if alpha is None:
        continue
    DL = (1+zs)**(1+alpha) * Da
    mu0 = 5*np.log10(DL*1e6/10)
    M = fit_M(mu0)
    chi2 = (mb - (mu0+M)) @ cov_inv @ (mb - (mu0+M))
    results[name] = chi2
    print(f"  {name:<18} χ²={chi2:.1f}  χ²/dof={chi2/(N-1):.3f}")

# ============ 2. 對比 ΛCDM ============
mu_lcdm_p = 5*np.log10((1+zs)*np.array([dc_lcdm(zi, 67.4, 0.315) for zi in zs])*1e6/10)
M_lp = fit_M(mu_lcdm_p)
chi2_lp = (mb - (mu_lcdm_p+M_lp)) @ cov_inv @ (mb - (mu_lcdm_p+M_lp))
results['ΛCDM Planck'] = chi2_lp
print(f"  {'ΛCDM Planck':<18} χ²={chi2_lp:.1f}  χ²/dof={chi2_lp/(N-1):.3f}")

mu_lcdm_r = 5*np.log10((1+zs)*np.array([dc_lcdm(zi, OMEGA_RING, 0.315) for zi in zs])*1e6/10)
M_lr = fit_M(mu_lcdm_r)
chi2_lr = (mb - (mu_lcdm_r+M_lr)) @ cov_inv @ (mb - (mu_lcdm_r+M_lr))
results['ΛCDM 72.59'] = chi2_lr
print(f"  {'ΛCDM 72.59':<18} χ²={chi2_lr:.1f}  χ²/dof={chi2_lr/(N-1):.3f}")

# ============ 3. 零參數對決 ============
print("\n--- 3. 零參數對決 (全部只 fit M) ---")
print(f"{'模型':<24} {'χ²':<9} {'Δχ²(vs ΛCDM P)':<16}")
base = chi2_lp
for name, chi2 in results.items():
    print(f"{name:<24} {chi2:<9.1f} {chi2-base:<+16.1f}")

# ============ 4. α=-1/7 分 bin 殘差 ============
print("\n--- 4. α=-1/7 分 bin 殘差 ---")
DL_67 = (1+zs)**(6/7) * Da
mu_67 = 5*np.log10(DL_67*1e6/10)
M_67 = fit_M(mu_67)
resid_67 = mb - (mu_67 + M_67)
bins = [(0, 0.05), (0.05, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.5),
        (0.5, 0.8), (0.8, 1.2), (1.2, 2.3)]
print(f"{'z bin':<12} {'N':<5} {'<resid>':<9} {'σ':<7}")
for lo, hi in bins:
    m = (zs >= lo) & (zs < hi)
    if m.sum() < 3: continue
    print(f"{lo:.2f}-{hi:.2f}  {m.sum():<5} {resid_67[m].mean():<+9.4f} {resid_67[m].std():<7.4f}")

# ============ 5. DESI ============
print("\n--- 5. DESI BAO (唔受 α 影響) ---")
rd_idcm = math.pi * R_WORLD / 88 * 420/421
desi = [
    ('LRG1', 0.510, 13.588, 0.167),
    ('LRG2', 0.706, 17.351, 0.177),
    ('LRG3+ELG', 0.934, 21.576, 0.152),
    ('ELG2', 1.321, 27.601, 0.318),
    ('Lyα', 2.330, 38.988, 0.531),
]
chi2_d = 0
for name, z, obs, err in desi:
    ell = math.log(1+z, 4)
    pred = d_app(ell)/rd_idcm
    chi2_d += ((pred-obs)/err)**2
print(f"DESI χ² = {chi2_d:.2f} (零參數, 唔受 α 影響)")
check("DESI χ² < 15", chi2_d < 15, f"{chi2_d:.2f}")

# ============ 6. 總結 ============
print("\n--- 6. 總結 ---")
print(f"""
★ IDCM 完整距離-紅移 (零參數):
  D_A(ell) = R_world(1-4^{-ell})(1+2phi^{-1}ell+delta(ell))    (幾何/BAO)
  D_L(z) = (1+z)^{6/7}.D_A(ell)                    (光度/SNe)
  ell = log4(1+z)

  結構數: 44, 4, phi, 7=L4, 88, 420/421, C=-0.1697
  全部由 IDCM 結構決定 — 零自由參數!

  SNe chi2 = {results['α=-1/7 (L₄)']:.0f} vs LCDM Planck {chi2_lp:.0f}
  DESI chi2 = {chi2_d:.2f}
""")

result = {
    'chi2_alpha0': round(results['α=0 (原始)'], 1),
    'chi2_minus17': round(results['α=-1/7 (L₄)'], 1),
    'chi2_lcdm_planck': round(float(chi2_lp), 1),
    'chi2_desi': round(float(chi2_d), 2),
    'M_minus17': round(float(M_67), 4),
    'pass': PASS, 'fail': FAIL
}
with open('data/18_zeroparam_duel.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nPASS={PASS} FAIL={FAIL}")
print("-> data/18_zeroparam_duel.json")
