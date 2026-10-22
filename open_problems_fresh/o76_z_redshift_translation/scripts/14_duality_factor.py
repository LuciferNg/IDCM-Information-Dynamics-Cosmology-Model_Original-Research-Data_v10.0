#!/usr/bin/env python3
"""
O76/14: D_app 嘅真正角色 — 紅移-尺度映射 vs 距離
================================================================
O76/13 矛盾: DESI 喜歡 D_app (χ²=12.8), SNe 要求 ΛCDM D_A 形狀

★ 重新詮釋: D_app 可能唔係「距離」, 而係「紅移-尺度映射」
  即係 D_app 定義咗「一個紅移 z 對應咩尺度」, 唔係「幾遠」

如果 D_app 係映射 (唔係距離):
  BAO: 角直徑 θ = λ_sync/D_app?  → fit 好 (χ²=12.8)
  SNe: D_L 由能量守恆決定, 唔一定 = (1+z)·D_app

★ 測試: SNe 要求嘅 D_L(z) 形狀 = 咩?
  用低 z M, 反推 D_L_req(z) = D_app·10^{resid/5}
  睇 D_L_req 有咩結構 (係咪 = (1+z)·f(ℓ) 有特定 f?)

關鍵: D_L_req/D_app = 10^{resid/5} 就係「對偶偏差因子」
  如果呢個因子有結構 (唔係 noise) → 對偶定義要改
  如果係 noise → D_app 形狀啱, 只係 M 問題

★ 另一個關鍵測試: SNe 自己 fit D_app 形狀參數
  如果 D_app 形狀啱, fit C 應該 ≈ -0.1697
  如果唔啱, fit 出嚟嘅 C 會好唔同 (O76/05: C=+0.65)
  → C_fit=+0.65 已顯示 D_app 形狀唔啱 SNe!

最終問題: IDCM 點樣同時 fit DESI + SNe?
  A. D_app 唔係距離 → SNe 距離要另一條公式
  B. D_app 距離啱但對偶錯 → D_L ≠ (1+z)·D_A
  C. D_app 形狀錯 → 要高階修正
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
print("O76/14: D_app 真正角色 — 距離 or 映射?")
print("=" * 70)

# ============ 1. 對偶偏差因子結構 ============
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

ell_arr = np.log(1+zs)/np.log(4)
mu_idcm0 = 5*np.log10((1+zs)*d_app(ell_arr)*1e6/10)
mask_low = zs < 0.1
M_idcm = fit_M(mu_idcm0, mask_low)
resid = mb - (mu_idcm0 + M_idcm)
duality_factor = 10**(resid/5)   # D_L_req/D_app

# 分 bin 睇結構
print("\n--- 1. 對偶偏差因子 D_L_req/D_app 結構 ---")
bins = [(0, 0.05), (0.05, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.5),
        (0.5, 0.8), (0.8, 1.2), (1.2, 2.3)]
print(f"{'z bin':<12} {'N':<5} {'<因子>':<9} {'<ln因子>':<10} {'σ':<7}")
for lo, hi in bins:
    m = (zs >= lo) & (zs < hi)
    if m.sum() < 3: continue
    f = duality_factor[m]
    print(f"{lo:.2f}-{hi:.2f}  {m.sum():<5} {np.median(f):<9.4f} {np.median(np.log(f)):<+10.4f} {np.log(f).std():<7.4f}")

# 因子係咪 smooth 函數?
print("\n→ 如果 ln(因子) 有系統性 z 依賴 (唔係 noise) → 對偶要改")
print("→ 0-0.05: +?, 0.3-0.5: ?, 0.5-0.8: ? → 睇上表")

# ============ 2. 因子嘅最佳擬合 ============
print("\n--- 2. ln(因子) vs z 擬合 ---")
mask = zs > 0.01
z_fit = zs[mask]
y = np.log(duality_factor[mask])
# 線性: y = a + b·z
from numpy.polynomial import polynomial as P
c_lin = np.polyfit(z_fit, y, 1)
print(f"線性 fit: ln(f) = {c_lin[0]:+.4f} + {c_lin[1]:+.4f}·z")
# 二次
c_quad = np.polyfit(z_fit, y, 2)
print(f"二次 fit: ln(f) = {c_quad[2]:+.4f} + {c_quad[1]:+.4f}·z + {c_quad[0]:+.4f}·z²")
# ln(1+z) fit
c_ln = np.polyfit(np.log1p(z_fit), y, 1)
print(f"ln(1+z) fit: ln(f) = {c_ln[0]:+.4f} + {c_ln[1]:+.4f}·ln(1+z)")
print(f"→ 如果 c_ln[1] ≈ -1 → D_L ∝ D_app/(1+z)? (奇!)")
print(f"→ 如果 c_ln[1] ≈ -2 → D_L ∝ D_app/(1+z)² (ΛCDM 對偶!)")
print(f"→ 如果 c_ln[1] ≈ 0 → D_L ∝ D_app (IDCM 對偶 OK)")

# ============ 3. 三種對偶 fit 比較 ============
print("\n--- 3. 三種對偶 fit (低 z M) ---")
def mu_variant(z, M, variant):
    ell = np.log(1+z)/np.log(4)
    Da = d_app(ell)
    if variant == 'idcm': DL = (1+z)*Da
    elif variant == 'lcdm': DL = (1+z)**2 * Da
    elif variant == 'none': DL = Da
    return M + 5*np.log10(DL*1e6/10)

for variant in ['idcm', 'lcdm', 'none']:
    mu0 = mu_variant(zs, 0, variant)
    Mv = fit_M(mu0, mask_low)
    chi2 = (mb - mu_variant(zs, Mv, variant)) @ cov_inv @ (mb - mu_variant(zs, Mv, variant))
    print(f"{variant:<6} M={Mv:.4f} χ²={chi2:.1f} χ²/dof={chi2/(N-1):.3f}")

# ============ 4. 總結 ============
print("\n--- 4. 總結 ---")
print(f"""
O76/14 結論:
  對偶偏差因子 ln(f) = ln(D_L_req/D_app) 嘅 z 依賴決定一切:
  - 如果係線性/ln 結構 → IDCM 對偶 D_L=(1+z)D_A 唔成立
  - 如果係 noise → D_app 形狀啱, 問題喺 M 或者高 z 尾部

  三種對偶 fit (低 z M):
  - idcm: (1+z)·D_app
  - lcdm: (1+z)²·D_app
  - none: D_app
  最低 χ² 嘅對偶 = 數據支持嘅對偶
""")

result = {
    'lin_fit': [round(x, 4) for x in c_lin],
    'ln_fit': [round(x, 4) for x in c_ln],
    'quad_fit': [round(x, 4) for x in c_quad],
    'pass': PASS, 'fail': FAIL
}
with open('data/14_duality_factor.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"PASS={PASS} FAIL={FAIL}")
print("-> data/14_duality_factor.json")
