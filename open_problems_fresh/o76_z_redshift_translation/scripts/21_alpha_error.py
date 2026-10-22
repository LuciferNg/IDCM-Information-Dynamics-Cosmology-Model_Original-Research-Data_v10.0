#!/usr/bin/env python3
"""
O76/21: α 誤差分析 + n/p 交叉連接
================================================================
O76/17: α_fit = -0.1377
結構候選: α = -1/7 = -0.1429 (L₄=7, O13 DM 模式)
          α = -1/8 = -0.1250
          α = -F17/88 = -0.1932
          α = -2φ⁻¹/16 = -0.0773

★ 新詮釋: α = -(n/p 結構比) = -γ₇/γ₂₀ = -0.14262?
  γ₇ = 4sin²(7π/88) = 0.244642
  γ₂₀ = 4sin²(20π/88) = 1.715370
  γ₇/γ₂₀ = 0.14262 (O13 閉合, 0.17%)

  0.14262 vs α_fit 0.1377: dev = 3.4%?
  0.14286 (1/7) vs α_fit: dev = 3.6%

→ 兩個都喺 3-4% 內, 分辨唔到 (需要 α 誤差)

★ 誤差分析: 用 Fisher matrix / bootstrap
  1. fit α 嘅 1σ 誤差
  2. 睇 -1/7, -γ₇/γ₂₀, -1/8 邊個喺誤差內
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
print("O76/21: α 誤差分析 + n/p 交叉連接")
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

ell_arr = np.log(1+zs)/np.log(4)
Da = d_app(ell_arr)

# ============ 1. α + M 聯合 fit ============
print("\n--- 1. α + M 聯合 fit ---")
def loss(params):
    alpha, M = params
    DL = (1+zs)**(1+alpha) * Da
    mu = M + 5*np.log10(DL*1e6/10)
    return (mb - mu) @ cov_inv @ (mb - mu)

best = None
for a0 in [-0.2, -0.15, -0.1, -0.05, 0.0]:
    r = optimize.minimize(loss, [a0, -19.3], method='Nelder-Mead',
                          options={'maxiter': 400, 'xatol': 1e-8, 'fatol': 1e-3})
    if best is None or r.fun < best.fun:
        best = r
alpha_fit, M_fit = best.x
chi2_min = best.fun
print(f"α_fit = {alpha_fit:.6f}, M = {M_fit:.4f}, χ²_min = {chi2_min:.1f}")

# ============ 2. α 誤差 (Δχ²=1 方法) ============
print("\n--- 2. α 1σ 誤差 (Δχ²=1) ---")
# 掃描 α, fit M, 搵 Δχ²=1 邊界
def chi2_at_alpha(alpha):
    DL = (1+zs)**(1+alpha) * Da
    mu0 = 5*np.log10(DL*1e6/10)
    M = fit_M(mu0)
    return (mb - (mu0+M)) @ cov_inv @ (mb - (mu0+M))

# 精細掃描
alphas = np.linspace(alpha_fit - 0.1, alpha_fit + 0.1, 201)
chi2s = np.array([chi2_at_alpha(a) for a in alphas])
# 搵 Δχ² = 1 邊界
dchi2 = chi2s - chi2_min
lo_idx = np.where(dchi2 <= 1)[0]
alpha_lo = alphas[lo_idx[0]] if len(lo_idx) else alpha_fit - 0.1
alpha_hi = alphas[lo_idx[-1]] if len(lo_idx) else alpha_fit + 0.1
sigma_a = max(abs(alpha_fit - alpha_lo), abs(alpha_hi - alpha_fit))
print(f"α 1σ 範圍: [{alpha_lo:.4f}, {alpha_hi:.4f}]")
print(f"α = {alpha_fit:.4f} ± {sigma_a:.4f}")

# ============ 3. 結構候選分辨 ============
print("\n--- 3. 結構候選分辨 ---")
g7 = 4*math.sin(7*math.pi/88)**2
g20 = 4*math.sin(20*math.pi/88)**2
np_ratio = g7/g20
candidates = {
    '-1/7 (L₄)': -1/7,
    '-γ₇/γ₂₀ (n/p)': -np_ratio,
    '-1/8': -1/8,
    '-F17/88': -17/88,
    '-2φ⁻¹κ': -2*PHI**(-1)/16,
}
print(f"n/p = γ₇/γ₂₀ = {np_ratio:.6f} (O13: 0.14262)")
print(f"{'候選':<18} {'值':<10} {'在 1σ?':<8} {'dev vs fit':<10}")
for name, val in candidates.items():
    in_err = alpha_lo <= val <= alpha_hi
    dev = abs(val - alpha_fit)/abs(alpha_fit)*100
    print(f"{name:<18} {val:<10.6f} {'✅' if in_err else '❌'} {dev:<10.2f}%")

# ============ 4. 兩者 χ² 比較 ============
print("\n--- 4. 候選 χ² 比較 ---")
for name, val in candidates.items():
    chi2_c = chi2_at_alpha(val)
    print(f"  {name:<18} χ²={chi2_c:.1f}  Δχ²(vs min)={chi2_c-chi2_min:+.2f}")

result = {
    'alpha_fit': round(float(alpha_fit), 6),
    'alpha_lo': round(float(alpha_lo), 4),
    'alpha_hi': round(float(alpha_hi), 4),
    'sigma': round(float(sigma_a), 4),
    'np_ratio': round(float(np_ratio), 6),
    'pass': PASS, 'fail': FAIL
}
with open('data/21_alpha_error.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nPASS={PASS} FAIL={FAIL}")
print("-> data/21_alpha_error.json")
