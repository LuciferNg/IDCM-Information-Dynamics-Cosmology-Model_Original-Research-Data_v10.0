#!/usr/bin/env python3
"""
O76/03: Pantheon+ 1701 SNe — IDCM vs ΛCDM Hubble diagram 決鬥
================================================================
核心判決: IDCM D_app(ℓ) 距離-紅移 vs ΛCDM D_C(z) 邊個 fit 超新星好?

方法:
  1. 載入 Pantheon+ 1701 SNe (m_b_corr, zCMB, cov 矩陣)
  2. IDCM: μ(z) = 5log10((1+z)·D_app(ℓ)/10pc) + M, ℓ = log₄(1+z)
  3. ΛCDM: μ(z) = 5log10((1+z)·D_C(z)/10pc) + M, D_C = c∫dz'/E(z')
  4. 兩者都 fit M (單一常數) → 比較 χ²
  5. 用完整 covariance (stat+syst) — 唔係 diag only

★ IDCM 零自由參數: D_app 完全由結構決定 (R_world, 44, φ, C)
★ ΛCDM 兩個參數: H₀, Ωm (但 H₀ 由 ω_ring 鎖定 → 比較要公平)
  → 公平比較: ΛCDM 都用 ω_ring=72.59, fit Ωm
  → IDCM 零參數 vs ΛCDM 一個參數 (Ωm)
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
OMEGA_RING = 72.59
N_D = 44
C_DELAY = -0.1697  # O51 群延遲權重

print("=" * 70)
print("O76/03: Pantheon+ 1701 SNe — IDCM vs ΛCDM Hubble diagram")
print("=" * 70)

# ============ 1. 載入數據 ============
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
        if len(parts) < len(header):
            continue
        zs.append(float(parts[col['zCMB']]))
        mb.append(float(parts[col['m_b_corr']]))

zs = np.array(zs)
mb = np.array(mb)
N = len(zs)

with open(cov_path) as f:
    n_dim = int(f.readline().strip())
cov = np.loadtxt(cov_path, skiprows=1).reshape(n_dim, n_dim)
cov_inv = np.linalg.inv(cov)

print(f"\n載入 {N} 個 SNe (z range: {zs.min():.4f} - {zs.max():.3f})")
print(f"Covariance: {cov.shape}")

# 檢查 z 範圍
print(f"z > 2: {(zs > 2).sum()}, z > 1: {(zs > 1).sum()}, z < 0.1: {(zs < 0.1).sum()}")

# ============ 2. IDCM μ(z) ============
def d_app(ell):
    """D_app(ℓ) = R_world(1-4^{-ℓ})(1+2φ⁻¹ℓ+δ(ℓ))"""
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2*PHI**(-1)*ell
    delta = C_DELAY * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

def mu_idcm(z, M):
    ell = np.log(1+z) / np.log(4)
    DL = (1+z) * d_app(ell)
    return M + 5*np.log10(DL*1e6/10)

# ============ 3. ΛCDM μ(z) ============
def dc_lcdm(z, H0, Om):
    Ol = 1 - Om
    # 數值積分 (log-spaced 更準)
    zz = np.geomspace(1e-6, z, 2000) if z > 1e-5 else np.linspace(0, z, 100)
    E = np.sqrt(Om*(1+zz)**3 + Ol)
    return C_LIGHT/H0 * np.trapezoid(1/E, zz)

def mu_lcdm(z, M, H0, Om):
    DL = (1+z) * np.array([dc_lcdm(zi, H0, Om) for zi in z])
    return M + 5*np.log10(DL*1e6/10)

# ============ 4. Fit M (IDCM) ============
print("\n--- 4. IDCM fit M ---")
# μ = M + 5log10((1+z)D_app·1e5)
# 線性 fit: m_b = M + μ_model → M = mean(m_b - μ_model) (加權)
def fit_M(mu_model, cov_inv):
    """加權最小二乘: M = (J^T C^{-1} J)^{-1} J^T C^{-1} (m_b - mu_model)"""
    J = np.ones(N)
    denom = J @ cov_inv @ J
    num = J @ cov_inv @ (mb - mu_model)
    return num / denom

mu_idcm_0 = mu_idcm(zs, 0)  # 唔含 M
M_idcm = fit_M(mu_idcm_0, cov_inv)
mu_idcm_full = mu_idcm_0 + M_idcm
resid = mb - mu_idcm_full
chi2_idcm = resid @ cov_inv @ resid
print(f"M_IDCM = {M_idcm:.4f}")
print(f"χ²_IDCM = {chi2_idcm:.1f} / {N} dof")
print(f"χ²/dof = {chi2_idcm/(N-1):.3f}")

# ============ 5. Fit M + Ωm (ΛCDM) ============
print("\n--- 5. ΛCDM fit M + Ωm (H0=ω_ring 固定) ---")
from scipy import optimize

def lcdm_loss(params):
    Om, M = params[0], params[1]
    mu = mu_lcdm(zs, M, OMEGA_RING, Om)
    resid = mb - mu
    return resid @ cov_inv @ resid

# 粗掃瞄 + 精修
best = None
for Om0 in [0.2, 0.25, 0.3, 0.315, 0.35, 0.4]:
    M0 = M_idcm
    r = optimize.minimize(lcdm_loss, [Om0, M0], method='Nelder-Mead',
                          options={'maxiter': 200, 'xatol': 1e-6, 'fatol': 1e-3})
    if best is None or r.fun < best.fun:
        best = r

Om_best, M_lcdm = best.x
chi2_lcdm = best.fun
print(f"Ωm = {Om_best:.4f}, M_ΛCDM = {M_lcdm:.4f}")
print(f"χ²_ΛCDM = {chi2_lcdm:.1f} / {N} dof")
print(f"χ²/dof = {chi2_lcdm/(N-2):.3f}")

# ============ 6. 比較 ============
print("\n--- 6. 比較 ---")
print(f"{'模型':<12} {'參數':<8} {'χ²':<10} {'χ²/dof':<10}")
print(f"{'─'*44}")
print(f"{'IDCM':<12} {'0 (M)':<8} {chi2_idcm:<10.1f} {chi2_idcm/(N-1):<10.3f}")
print(f"{'ΛCDM':<12} {'2 (M,Ωm)':<8} {chi2_lcdm:<10.1f} {chi2_lcdm/(N-2):<10.3f}")

# Δχ² 同 ΔAIC
delta_chi2 = chi2_idcm - chi2_lcdm
aic_idcm = chi2_idcm + 2*1      # M
aic_lcdm = chi2_lcdm + 2*2      # M, Ωm
print(f"\nΔχ² = {delta_chi2:+.1f} (IDCM - ΛCDM)")
print(f"ΔAIC = {aic_idcm - aic_lcdm:+.1f} (負 = IDCM 好)")
if delta_chi2 < 0:
    print("→ IDCM 零參數 fit 得更好!")
else:
    print("→ ΛCDM fit 得更好")

# 關鍵: 高 z 殘差
print("\n--- 7. 分紅移殘差 ---")
bins = [(0, 0.1), (0.1, 0.3), (0.3, 0.5), (0.5, 1.0), (1.0, 2.0), (2.0, 2.6)]
print(f"{'z bin':<12} {'N':<6} {'IDCM <resid>':<14} {'ΛCDM <resid>':<14}")
for lo, hi in bins:
    m = (zs >= lo) & (zs < hi)
    if m.sum() == 0:
        continue
    r1 = (mb - mu_idcm_full)[m].mean()
    r2 = (mb[m] - mu_lcdm(zs[m], M_lcdm, OMEGA_RING, Om_best)).mean()
    print(f"{lo:.1f}-{hi:.1f}      {m.sum():<6} {r1:<+14.4f} {r2:<+14.4f}")

# ============ 8. 儲存 ============
result = {
    'N_sn': int(N),
    'M_idcm': round(float(M_idcm), 4),
    'chi2_idcm': round(float(chi2_idcm), 1),
    'chi2_idcm_dof': round(float(chi2_idcm/(N-1)), 3),
    'Om_lcdm': round(float(Om_best), 4),
    'M_lcdm': round(float(M_lcdm), 4),
    'chi2_lcdm': round(float(chi2_lcdm), 1),
    'chi2_lcdm_dof': round(float(chi2_lcdm/(N-2)), 3),
    'delta_chi2': round(float(delta_chi2), 1),
    'aic_idcm': round(float(aic_idcm), 1),
    'aic_lcdm': round(float(aic_lcdm), 1),
    'pass': PASS,
    'fail': FAIL
}
with open('data/03_pantheon_duel.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nPASS={PASS} FAIL={FAIL}")
print("-> data/03_pantheon_duel.json")
