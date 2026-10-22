#!/usr/bin/env python3
"""
O76/16: 全樣本 M fit — IDCM vs ΛCDM 公平對決
================================================================
O76/14: 低 z M 令 IDCM χ²=2386 vs ΛCDM 2061
O76/03: 全樣本 M 令 IDCM χ²=2096 vs ΛCDM 1989 (fit Ωm)

公平比較: 兩者都用全樣本 fit M
  IDCM: M 只有 1 個參數
  ΛCDM: M + Ωm 2 個參數 (但 Ωm fit 出 0.38 唔係 Planck 0.315)

★ 真正零參數對決: IDCM (0 參數 + M) vs ΛCDM (Planck 參數 + M)
  → ΛCDM Planck: H0=67.4, Ωm=0.315 固定 → 只 fit M

但 H0 有爭議! ΛCDM 用 67.4 (CMB) 定 72.59 (IDCM)?
  → 用 IDCM 嘅 H0=72.59 對 ΛCDM 公平 (大家都用同一個 H0)

★ 重點: SNe 數據 fit 邊個形狀?
  IDCM D_app 形狀 (零參數)
  ΛCDM Ωm=0.315 形狀 (H0 唔影響形狀, 只影響 M)
  ΛCDM Ωm fit 形狀 (1 參數)

比較 χ² 就知 SNe 數據嘅形狀偏好
"""
import numpy as np
import math
import json
from scipy import optimize

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
print("O76/16: 全樣本 M fit — 公平對決")
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

# ============ 1. IDCM (全樣本 M) ============
ell_arr = np.log(1+zs)/np.log(4)
mu_idcm0 = 5*np.log10((1+zs)*d_app(ell_arr)*1e6/10)
M_idcm = fit_M(mu_idcm0)
chi2_idcm = (mb - (mu_idcm0+M_idcm)) @ cov_inv @ (mb - (mu_idcm0+M_idcm))
print(f"\nIDCM:      M={M_idcm:.4f} χ²={chi2_idcm:.1f} χ²/dof={chi2_idcm/(N-1):.3f} (0 形狀參數)")

# ============ 2. ΛCDM Planck (固定) ============
mu_lcdm_p = 5*np.log10((1+zs)*np.array([dc_lcdm(zi, 67.4, 0.315) for zi in zs])*1e6/10)
M_lcdm_p = fit_M(mu_lcdm_p)
chi2_lcdm_p = (mb - (mu_lcdm_p+M_lcdm_p)) @ cov_inv @ (mb - (mu_lcdm_p+M_lcdm_p))
print(f"ΛCDM Planck (H0=67.4,Ωm=0.315): M={M_lcdm_p:.4f} χ²={chi2_lcdm_p:.1f} χ²/dof={chi2_lcdm_p/(N-1):.3f}")

# ============ 3. ΛCDM H0=72.59 (固定 Ωm=0.315) ============
mu_lcdm_r = 5*np.log10((1+zs)*np.array([dc_lcdm(zi, OMEGA_RING, 0.315) for zi in zs])*1e6/10)
M_lcdm_r = fit_M(mu_lcdm_r)
chi2_lcdm_r = (mb - (mu_lcdm_r+M_lcdm_r)) @ cov_inv @ (mb - (mu_lcdm_r+M_lcdm_r))
print(f"ΛCDM H0=72.59 (Ωm=0.315):   M={M_lcdm_r:.4f} χ²={chi2_lcdm_r:.1f} χ²/dof={chi2_lcdm_r/(N-1):.3f}")

# ============ 4. ΛCDM fit Ωm ============
def lcdm_loss(params):
    Om, M = params
    mu = 5*np.log10((1+zs)*np.array([dc_lcdm(zi, OMEGA_RING, Om) for zi in zs])*1e6/10)
    return (mb - (mu + M)) @ cov_inv @ (mb - (mu + M))

best = None
for Om0 in [0.2, 0.3, 0.315, 0.35, 0.4, 0.5]:
    r = optimize.minimize(lcdm_loss, [Om0, -19.3], method='Nelder-Mead',
                          options={'maxiter': 300, 'xatol': 1e-6, 'fatol': 1e-2})
    if best is None or r.fun < best.fun:
        best = r
Om_fit, M_fit = best.x
chi2_lcdm_fit = best.fun
print(f"ΛCDM fit Ωm:   Ωm={Om_fit:.4f} M={M_fit:.4f} χ²={chi2_lcdm_fit:.1f} χ²/dof={chi2_lcdm_fit/(N-2):.3f}")

# ============ 5. 比較表 ============
print("\n--- 5. 比較表 ---")
print(f"{'模型':<30} {'參數':<8} {'χ²':<9} {'χ²/dof':<8} {'ΔAIC':<8}")
models = [
    ('IDCM D_app', 1, chi2_idcm),
    ('ΛCDM Planck 67.4', 1, chi2_lcdm_p),
    ('ΛCDM 72.59', 1, chi2_lcdm_r),
    ('ΛCDM fit Ωm', 2, chi2_lcdm_fit),
]
best_aic = min(m[2] + 2*m[1] for m in models)
for name, npar, chi2 in models:
    aic = chi2 + 2*npar
    print(f"{name:<30} {npar:<8} {chi2:<9.1f} {chi2/(N-npar):<8.3f} {aic-best_aic:<+8.1f}")

# ============ 6. 結論 ============
print("\n--- 6. 結論 ---")
print(f"""
IDCM 零形狀參數 χ² = {chi2_idcm:.0f} (M 只係歸一化)
ΛCDM 零形狀參數 (Planck) χ² = {chi2_lcdm_p:.0f}
ΛCDM 1 形狀參數 (Ωm fit) χ² = {chi2_lcdm_fit:.0f}

Δχ² (IDCM - ΛCDM Planck) = {chi2_idcm - chi2_lcdm_p:+.0f}
Δχ² (IDCM - ΛCDM fit) = {chi2_idcm - chi2_lcdm_fit:+.0f}

→ IDCM D_app 形狀 vs ΛCDM: 邊個 fit 超新星好?
""")

result = {
    'chi2_idcm': round(float(chi2_idcm), 1),
    'chi2_lcdm_planck': round(float(chi2_lcdm_p), 1),
    'chi2_lcdm_ring': round(float(chi2_lcdm_r), 1),
    'chi2_lcdm_fit': round(float(chi2_lcdm_fit), 1),
    'Om_fit': round(float(Om_fit), 4),
    'pass': PASS, 'fail': FAIL
}
with open('data/16_fair_duel.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nPASS={PASS} FAIL={FAIL}")
print("-> data/16_fair_duel.json")
