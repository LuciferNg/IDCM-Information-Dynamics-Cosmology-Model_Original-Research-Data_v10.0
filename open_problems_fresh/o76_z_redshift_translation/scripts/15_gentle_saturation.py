#!/usr/bin/env python3
"""
O76/15: 高 z 修正 — 溫和飽和 (唔破壞 DESI)
================================================================
O76/14: IDCM 對偶 D_L=(1+z)·D_A 啱, 但高 z 有 -4%~-9% 殘差
O76/09: 完全飽和 (tanh) 破壞 DESI (χ² 12.8→158)

★ 溫和修正: 只修正「投影伸長」項嘅高 z 行為, 保留 (1-4^{-ℓ}) 骨架
  投影伸長 2φ⁻¹ℓ → 2φ⁻¹·ℓ·G(ℓ)
  G(ℓ) = 飽和因子, 溫和版: G(ℓ) = 1/(1+ℓ/ℓ_cut)
  ℓ_cut = ? (fit or 結構)

  → 高 z: G→0, 投影伸長飽和
  → 低 z: G→1, 保持 IDCM 低 z 形狀 (fit 好!)

★ 目標: 同時 fit SNe (χ²↓) + DESI (χ² 保持 <15)

★ 結構選擇: ℓ_cut 由 F_proj 截斷決定?
  ℓ_cut = (F_proj/44)·ℓ_max? 但 ℓ_max 係咩?
  ℓ_max = ℓ_Nyquist = log₄(18) = 2.085?
  → ℓ_cut = 17/44 × 2.085 = 0.806 (O76/08)
  → z_cut = 4^0.806 - 1 = 2.05

  或者 ℓ_cut 用「投影伸長有效截止」:
  投影伸長 ∫₀^ℓ (1+2φ⁻¹ℓ')dℓ' 有上限?
  ∫₀^∞ ... 發散! 冇上限
  → 但 F_proj 截斷 → w_n = sec(πn/88) ≤ sec(27π/88) = 2.14
  → 有效群延遲有上限 → 投影伸長因子有上限
  → G(ℓ) = w(ℓ)/w_max? w(ℓ) = 1/v_g(ℓ)
  
  n(ℓ) = ? ℓ 點映射到 n?
  n = N_d·ℓ/ℓ_max (線性)? → n(ℓ_cut=0.806) = 44×0.806/2.085 = 17 = F_proj!
  → ℓ_cut 啱好係 n=F_proj 嘅位置!
  
  → G(ℓ) = v_g(n(ℓ))/v_g(0) = cos(π·n(ℓ)/88) = cos(π·N_d·ℓ/(88·ℓ_max))
  → 但 v_g(n)→0 at n=44 (Nyquist) → 太強

  溫和版: G(ℓ) = cos(π·F_proj·ℓ/(44·ℓ_cut))? 
  或者直接: G(ℓ) = cos(π·17·ℓ/(44·2.085)) = cos(π·ℓ/5.40)
  ℓ=0: cos0=1 ✅, ℓ=0.806: cos(0.469)=0.892 (輕微), ℓ=2.085: cos(1.213)=0.342

  測試幾個形式, 睇邊個同時 fit SNe + DESI
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
N_D = 44
F_PROJ = 17

print("=" * 70)
print("O76/15: 高 z 溫和飽和修正")
print("=" * 70)

ell_nyq = math.log(18, 4)
ell_cut = F_PROJ / N_D * ell_nyq
print(f"ℓ_Nyquist = {ell_nyq:.4f}, ℓ_cut = {ell_cut:.4f}")

# ============ 1. 修正形式 ============
def G_slow(ell):
    """溫和飽和: 1/(1+ℓ/ℓ_cut)"""
    return 1/(1 + ell/ell_cut)

def G_cos(ell):
    """cos 飽和: cos(π·ℓ/(2·ℓ_cut·k))"""
    return np.cos(math.pi * ell / (2*ell_cut*1.2))

def G_pow(ell, alpha=0.5):
    """冪次溫和: (1+ell/ell_cut)^{-alpha}"""
    return (1 + ell/ell_cut)**(-alpha)

def d_app_G(ell, G_func, C=C_DELAY):
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2*PHI**(-1)*ell*G_func(ell)
    delta = C * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

# 比較
print(f"\n--- 修正形式比較 (D 喺各 z) ---")
print(f"{'z':<6} {'原始':<8} {'G_slow':<8} {'G_cos':<8} {'G_pow0.5':<9}")
for z in [0.1, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0]:
    ell = math.log(1+z, 4)
    d0 = d_app_G(ell, lambda e: np.ones_like(e))
    d1 = d_app_G(ell, G_slow)
    d2 = d_app_G(ell, G_cos)
    d3 = d_app_G(ell, G_pow)
    print(f"{z:<6} {d0:<8.1f} {d1:<8.1f} {d2:<8.1f} {d3:<9.1f}")

# ============ 2. 載入數據 ============
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

def fit_M(mu_model, mask=None):
    if mask is None: mask = np.ones(N, bool)
    J = np.ones(mask.sum())
    Cm = cov_inv[np.ix_(mask, mask)]
    return (J @ Cm @ (mb[mask] - mu_model[mask])) / (J @ Cm @ J)

def mu_G(z, M, G_func, C=C_DELAY):
    ell = np.log(1+z)/np.log(4)
    DL = (1+z) * d_app_G(ell, G_func, C)
    return M + 5*np.log10(DL*1e6/10)

# ============ 3. SNe fit ============
print("\n--- 3. SNe fit (低 z M) ---")
mask_low = zs < 0.1
for name, Gf in [('原始', lambda e: np.ones_like(e)), ('G_slow', G_slow),
                 ('G_cos', G_cos), ('G_pow0.5', G_pow)]:
    mu0 = mu_G(zs, 0, Gf)
    Mv = fit_M(mu0, mask_low)
    chi2 = (mb - mu_G(zs, Mv, Gf)) @ cov_inv @ (mb - mu_G(zs, Mv, Gf))
    print(f"{name:<10} M={Mv:.4f} χ²={chi2:.1f} χ²/dof={chi2/(N-1):.3f}")

# ============ 4. DESI fit ============
print("\n--- 4. DESI BAO fit ---")
rd_idcm = math.pi * R_WORLD / 88 * 420/421
desi = [
    ('LRG1', 0.510, 13.588, 0.167),
    ('LRG2', 0.706, 17.351, 0.177),
    ('LRG3+ELG', 0.934, 21.576, 0.152),
    ('ELG2', 1.321, 27.601, 0.318),
    ('Lyα', 2.330, 38.988, 0.531),
]
for name, Gf in [('原始', lambda e: np.ones_like(e)), ('G_slow', G_slow),
                 ('G_cos', G_cos), ('G_pow0.5', G_pow)]:
    chi2_d = 0
    for sn, z, obs, err in desi:
        ell = math.log(1+z, 4)
        pred = d_app_G(ell, Gf)/rd_idcm
        chi2_d += ((pred-obs)/err)**2
    print(f"{name:<10} DESI χ²={chi2_d:.2f}")

# ============ 5. 綜合 ============
print("\n--- 5. 綜合 ---")
results = {}
for name, Gf in [('原始', lambda e: np.ones_like(e)), ('G_slow', G_slow),
                 ('G_cos', G_cos), ('G_pow0.5', G_pow)]:
    mu0 = mu_G(zs, 0, Gf)
    Mv = fit_M(mu0, mask_low)
    chi2_sn = (mb - mu_G(zs, Mv, Gf)) @ cov_inv @ (mb - mu_G(zs, Mv, Gf))
    chi2_d = 0
    for sn, z, obs, err in desi:
        ell = math.log(1+z, 4)
        pred = d_app_G(ell, Gf)/rd_idcm
        chi2_d += ((pred-obs)/err)**2
    results[name] = {'sn': chi2_sn, 'desi': chi2_d}
    print(f"{name:<10} SNe={chi2_sn:.1f} DESI={chi2_d:.2f}")

# 搵最佳
print("\n→ 目標: SNe < 2096 同時 DESI < 15")
for name, r in results.items():
    ok_sn = "✅" if r['sn'] < 2096 else "❌"
    ok_d = "✅" if r['desi'] < 15 else "❌"
    print(f"  {name:<10} SNe{ok_sn} DESI{ok_d}")

result = {k: {'sn': round(v['sn'],1), 'desi': round(v['desi'],2)} for k, v in results.items()}
with open('data/15_gentle_saturation.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nPASS={PASS} FAIL={FAIL}")
print("-> data/15_gentle_saturation.json")
