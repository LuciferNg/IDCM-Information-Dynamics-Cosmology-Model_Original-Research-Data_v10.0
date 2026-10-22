#!/usr/bin/env python3
"""
O76/17: 結構修正 — 群延遲權重飽和 (F_proj 完整推導)
================================================================
O76/08 發現: F_proj=17 截斷 → ℓ_cut = 0.806
O76/15 發現: 溫和飽和改善 SNe 但破壞 DESI

★ 真正結構: D_app 嘅投影伸長來自「群延遲權重」w_n = 1/v_g(n)
  D_app(ℓ) = ∫₀^ℓ dℓ'·(群延遲加權距離)
  
  原始 D_app: (1-4^{-ℓ}) 係「幾何骨架」, (1+2φ⁻¹ℓ) 係「線性投影」
  → 但投影伸長唔應該無界! F_proj 截斷 n≤27 → 群延遲有上限

★ 新公式候選: D_app = R_world·(1-4^{-ℓ})·(1 + 2φ⁻¹·S(ℓ))
  S(ℓ) = ∫₀^ℓ w(ℓ')dℓ', w(ℓ') = 群延遲權重

  群延遲權重由 n(ℓ) 決定: n(ℓ) = N_d·ℓ/ℓ_max (線性映射)
  w(ℓ) = sec(π·n(ℓ)/88) = sec(π·44·ℓ/(88·ℓ_max)) = sec(π·ℓ/(2·ℓ_max))
  S(ℓ) = ∫₀^ℓ sec(π·ℓ'/(2·ℓ_max)) dℓ'
       = (2·ℓ_max/π)·ln|sec(πℓ/(2ℓ_max)) + tan(πℓ/(2ℓ_max))|
       = (2·ℓ_max/π)·arcsinh(tan(πℓ/(2ℓ_max)))

  但 sec 喺 ℓ=ℓ_max 發散! F_proj 截斷: n≤27 → ℓ≤ℓ_cut=0.806
  → S 喺 ℓ_cut 截斷, 之後線性? 定飽和?

  簡化: S(ℓ) = ℓ_cut·ln|sec(...) + tan(...)|/arcsinh(tan(...))? 
  太複雜 — 直接用數值

★ 但 O76/15 已經證明: 任何「投影伸長飽和」都破壞 DESI
  → DESI 要求 D_app 高 z 長 (冇飽和)
  → SNe 要求 D_app 高 z 短 (飽和)
  → 兩者不可同時滿足 (用同一個 D_app)

★ 真正嘅出路: DESI 同 SNe 量嘅係唔同距離!
  DESI BAO: 量「幾何距離」→ D_app(ℓ) (冇飽和)
  SNe: 量「光度距離」→ D_L 有額外能量演化因子
  → D_L ≠ (1+z)·D_app 咁簡單!

  但 O76/14 證明 D_L = (1+z)·D_app 斜率 ≈ 0 (冇系統性偏差)?
  → 矛盾! 等我再諗...

  其實 O76/14 嘅 fit 係「全樣本」, 高 z 得 25 點, 影響細
  → 低 z 主導 fit → 斜率 ~0 係低 z 嘅結果
  → 高 z (z>0.3) 嘅真正偏差可能係「額外能量演化」

★ 候選: D_L = (1+z)·D_app·(1+z)^{α}
  α = 高 z 額外能量演化指數
  α>0 → 高 z 更暗 (更長 D_L)
  α<0 → 高 z 更亮 (更短 D_L)
  
  SNe 要求高 z 更亮 (D_L 短) → α<0!
  → D_L = (1+z)^{1-β}·D_app?
  → 但 β 要幾大? fit 一下!
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
print("O76/17: 光度距離額外能量演化")
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

def fit_M(mu_model, mask=None):
    if mask is None: mask = np.ones(N, bool)
    J = np.ones(mask.sum())
    Cm = cov_inv[np.ix_(mask, mask)]
    return (J @ Cm @ (mb[mask] - mu_model[mask])) / (J @ Cm @ J)

def d_app(ell, C=C_DELAY):
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2*PHI**(-1)*ell
    delta = C * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

# ============ 1. D_L = (1+z)^{1+α}·D_app fit α ============
print("\n--- 1. D_L = (1+z)^{1+α}·D_app ---")
ell_arr = np.log(1+zs)/np.log(4)
Da = d_app(ell_arr)

def loss_alpha(params):
    alpha, M = params
    DL = (1+zs)**(1+alpha) * Da
    mu = M + 5*np.log10(DL*1e6/10)
    return (mb - mu) @ cov_inv @ (mb - mu)

best = None
for a0 in [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2]:
    r = optimize.minimize(loss_alpha, [a0, -19.3], method='Nelder-Mead',
                          options={'maxiter': 300, 'xatol': 1e-6, 'fatol': 1e-2})
    if best is None or r.fun < best.fun:
        best = r
alpha_fit, M_fit = best.x
chi2_alpha = best.fun
print(f"α_fit = {alpha_fit:+.4f}, M={M_fit:.4f}")
print(f"χ² = {chi2_alpha:.1f} (vs α=0: 2096.0)")
print(f"→ α<0 = 高 z 更亮 (D_L 短)")

# ============ 2. α 嘅結構意義 ============
print("\n--- 2. α 結構分析 ---")
print(f"α_fit = {alpha_fit:+.4f}")
print(f"如果 α = -2φ⁻¹·κ? κ=1/16 → {-(2*PHI**(-1))*1/16:+.4f}")
print(f"如果 α = -2φ⁻¹/44? → {-(2*PHI**(-1))/44:+.4f}")
print(f"如果 α = -F_proj/88? → {-17/88:+.4f}")
print(f"如果 α = -1/8? → {-1/8:+.4f}")
print(f"如果 α = -1/7? → {-1/7:+.4f}")
# 重要: α_fit 會係咩?
# 如果 α ≈ -0.3 → 高 z 強烈修正
# 如果 α ≈ -0.05 → 輕微修正

# ============ 3. 分 bin 殘差 (fit α 後) ============
print("\n--- 3. 分 bin 殘差 (fit α 後) ---")
mu_alpha = M_fit + 5*np.log10((1+zs)**(1+alpha_fit) * Da * 1e6/10)
resid_alpha = mb - mu_alpha
bins = [(0, 0.1), (0.1, 0.3), (0.3, 0.5), (0.5, 0.8), (0.8, 1.2), (1.2, 2.3)]
print(f"{'z bin':<12} {'N':<5} {'<resid>':<9}")
for lo, hi in bins:
    m = (zs >= lo) & (zs < hi)
    if m.sum() < 3: continue
    print(f"{lo:.1f}-{hi:.1f}  {m.sum():<5} {resid_alpha[m].mean():<+9.4f}")

# ============ 4. DESI 影響 ============
print("\n--- 4. DESI BAO (α 修正後) ---")
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
print(f"DESI χ² (α 唔影響 D_app 幾何距離): {chi2_d:.2f}")
print(f"→ α 修正只影響 D_L (SNe), 唔影響 D_A (DESI)!")

# ============ 5. 總結 ============
print("\n--- 5. 總結 ---")
print(f"""
★ 結構方案: D_L = (1+z)^(1+a)·D_app
  a = {alpha_fit:+.4f} (fit)
  → SNe chi2: 2096 → {chi2_alpha:.1f} (改善 {2096-chi2_alpha:.0f})
  → DESI chi2: {chi2_d:.2f} (唔受影響!)

  a 嘅結構意義: 如果 a 有結構公式 (phi, gamma_k, F_proj...)
  → 就係「高 z 光度距離嘅能量演化修正」

  ★ 結構候選: a = -1/7 = -0.1429 (L4 = 7, O13 d->n)
    dev = {abs(alpha_fit - (-1/7))/abs(alpha_fit)*100:.1f}%

  ⚠️ 誠實: a 而家係 fit 出嚟 (1 個參數)
  → 要搵 a 嘅結構公式先可以恢復「零參數」
  → 候選: -1/7 = -1/L4 (Lucas), -F_proj/88, -2phi^-1 kappa...
""")

result = {
    'alpha_fit': round(float(alpha_fit), 4),
    'chi2_alpha': round(float(chi2_alpha), 1),
    'chi2_base': 2096.0,
    'chi2_desi': round(float(chi2_d), 2),
    'pass': PASS, 'fail': FAIL
}
with open('data/17_alpha_fit.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"PASS={PASS} FAIL={FAIL}")
print("-> data/17_alpha_fit.json")
