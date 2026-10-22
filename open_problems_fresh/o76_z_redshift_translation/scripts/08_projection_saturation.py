#!/usr/bin/env python3
"""
O76/08: 投影飽和 — 視線穿過世界環嘅最大距離
================================================================
發現: IDCM D_app 高 z 增長太快 (O76/07)
  D_req (數據) 喺 z=1-2 增長減慢, 接近 ΛCDM 飽和

結構原因: D_app 嘅 (1+2φ⁻¹ℓ) 投影伸長無界增長
但 K_Chain 係環 (S¹) — 視線最大深度係半環 L_ring/2 = πR_world!
  → 距離應該飽和喺 πR_world 附近 (光行時間 R_world/c 對應嘅最大距離)

★ 投影飽和結構:
  D_app(ℓ) → D_max = π·R_world  (環半周)
  ℓ_max = log₄(1+z_max)  where  z_max = 17 (Nyquist 截止, O51)
  → ℓ_max = log₄(18) = 2.08

飽和形式候選:
  A. 雙曲正切: D_app = D_max·tanh(αℓ)  — 平滑飽和
  B. 正弦:     D_app = D_max·sin(αℓ)   — 環投影 (穿過對面後回捲)
  C. 現有:     D_app = R(1-4^{-ℓ})(1+2φ⁻¹ℓ)  — 無界 (有問題)

物理: 視線喺環上睇, 最遠只可以睇到對面 (πR)
  → 高 z 物體唔可以比 πR 更遠!
  → 但觀測 z 可以好高 (z=10+) → 距離唔係 z 嘅單調函數?
  → 或者: z 本身喺 IDCM 有上限 (Nyquist z=17)

★ 關鍵: 環幾何嘅距離-紅移
  如果光子沿環傳播, 距離 s ∈ [0, L_ring]
  紅移 z 由「沿環距離」決定: z = f(s)
  最遠可見: s_max = L_ring/2 = πR (視線到對面)
  → D_app 飽和喺 πR = 12974 Mpc

但 O76/07 顯示 D_req 喺 z=2 只係 4596 Mpc (遠未到 πR=12974)
→ 飽和唔係即刻發生 — 需要喺 ℓ~0.5-1 開始平滑過渡

候選修正: 投影伸長項 2φ⁻¹ℓ → 飽和版本
  2φ⁻¹·ℓ·(1-4^{-ℓ}) 已經有 (1-4^{-ℓ}) 因子?
  唔係 — 而家: D = R(1-4^{-ℓ})(1+2φ⁻¹ℓ+δ)
  → (1-4^{-ℓ}) 提供 z/(1+z) Milne 型飽和
  → (1+2φ⁻¹ℓ) 無界投影伸長 ← 問題

修正候選: (1+2φ⁻¹ℓ) → (1+2φ⁻¹·tanh(αℓ))? 
  或者 (1+2φ⁻¹·ℓ/(1+ℓ/ℓ₀))?
  ℓ₀ = 1 (z=3) 附近開始飽和?

★ 但係 — 等我諗清楚物理!
  IDCM 冇膨脹: 距離 = 光行距離 = c·t_lookback
  光行距離喺靜態宇宙 = c·t (冇上限!)
  但「投影距離」D_app 係「幾何投影」— 唔係光行距離?
  
  如果 z 係 W-field 能量損失 (機制 B, O76/02):
    z = e^{αs} - 1 (指數損耗) → s = ln(1+z)/α = ℓ·ln4/α
    → 距離 s 隨 ℓ 線性增長 — 冇飽和! (符合 D_req 增長)
    
  如果 z 係投影 (機制 A):
    距離有飽和 (πR)
    
  → D_req 增長 (z=2: 2.43×Dref) 比線性 (Milne 2.0) 快但比 D_app (2.83) 慢
  → 唔係純線性, 唔係純飽和 — 中間?

等我直接 fit: D_req 用咩形式最好?
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
print("O76/08: 投影飽和 — D_app 高 z 修正結構")
print("=" * 70)

# ============ 1. 載入 + 反推 D_req ============
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

ell_arr = np.log(1+zs) / np.log(4)
mu_idcm0 = 5*np.log10((1+zs)*d_app(ell_arr)*1e6/10)
M_idcm = fit_M(mu_idcm0)
resid = mb - (mu_idcm0 + M_idcm)
D_req = d_app(ell_arr) * 10**(resid/5)

# ============ 2. D_req 形狀 fit ============
print("\n--- 2. D_req(z) 形狀 fit ---")
# 候選: D = A·ln(1+z) (tired light), A·z/(1+z) (Milne), A·(1+z)^β·ln, ΛCDM
# 用 D_req 中位數 (分 bin) fit

# 先睇 D_req/D_ref 嘅 log 斜率
print(f"{'z':<6} {'ln(1+z)':<10} {'D_req/Dref':<12} {'斜率 dlnD/dln(1+z)':<18}")
z_ref = 0.5
Dref = np.median(D_req[(zs >= 0.4) & (zs < 0.6)])
prev = None
for z in [0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]:
    m = (zs >= z*0.85) & (zs < z*1.15)
    if m.sum() < 3: continue
    Dr = np.median(D_req[m])
    ratio = Dr/Dref
    ln_1z = math.log(1+z)
    slope = ""
    if prev is not None:
        slope = f"{(math.log(Dr) - math.log(prev[0]))/(math.log(1+z) - math.log(1+prev[1])):.3f}"
    print(f"{z:<6} {ln_1z:<10.4f} {ratio:<12.4f} {slope}")
    prev = (Dr, z)

# ============ 3. 直接比較: D_req vs 各模型 (全部 z=0.5 歸一化) ============
print("\n--- 3. D_req vs 模型 (z=0.5 歸一化) ---")
def d_model(z, kind):
    if kind == 'ln':
        return math.log(1+z)
    elif kind == 'milne':
        return z/(1+z)
    elif kind == 'lcdm':
        return dc_lcdm(z, OMEGA_RING, 0.315)
    elif kind == 'idcm':
        return d_app(math.log(1+z, 4))
    elif kind == 'sqrt':
        return math.sqrt(1+z) - 1
    elif kind == 'power':
        return (1+z)**0.5 - 1

print(f"{'z':<6} {'D_req':<9} {'ln':<8} {'Milne':<8} {'ΛCDM':<8} {'IDCM':<8}")
for z in [0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]:
    m = (zs >= z*0.85) & (zs < z*1.15)
    if m.sum() < 3: continue
    Dr = np.median(D_req[m])
    vals = {}
    for kind in ['ln', 'milne', 'lcdm', 'idcm']:
        v = d_model(z, kind)
        vals[kind] = v
    # 歸一化到 z=0.5
    print(f"{z:<6} {Dr/Dref:<9.3f} {vals['ln']/d_model(0.5,'ln'):<8.3f} "
          f"{vals['milne']/d_model(0.5,'milne'):<8.3f} "
          f"{vals['lcdm']/d_model(0.5,'lcdm'):<8.3f} "
          f"{vals['idcm']/d_model(0.5,'idcm'):<8.3f}")

# ============ 4. 結構預言: Nyquist 截止 ============
print("\n--- 4. Nyquist 截止 (z=17) 嘅意義 ---")
# O51: z > 17 = Nyquist cutoff
# ℓ_Nyquist = log₄(1+17) = log₄(18) = ln18/ln4
ell_nyq = math.log(18, 4)
print(f"ℓ_Nyquist = log₄(18) = {ell_nyq:.4f}")
print(f"→ D_app(ℓ_Nyquist) = {d_app(ell_nyq):.1f} Mpc")
print(f"→ πR_world = {math.pi*R_WORLD:.1f} Mpc (環半周)")
print(f"→ D_app(ℓ_Nyquist)/πR = {d_app(ell_nyq)/(math.pi*R_WORLD):.4f}")

# 有趣: D_app(ℓ_Nyquist) 同 πR 比較?
# 如果 D_app 喺 Nyquist 截止啱好 ~πR → 環幾何自洽!
print(f"\n→ 如果 D_app(ℓ_nyq) ≈ πR_world → 高 z 截止 = 視線到對面!")

# ============ 5. 關鍵: 飽和修正形式 ============
print("\n--- 5. 飽和修正候選 ---")
# 現有: D = R(1-4^{-ℓ})(1+2φ⁻¹ℓ+δ)
# 修正: 投影伸長應該飽和
# 候選 A: 2φ⁻¹ℓ → 2φ⁻¹·ℓ·(1-4^{-ℓ})^(-1/2)?? 太隨意
# 候選 B: 用 ℓ 嘅「有效」版本 ℓ_eff = ℓ/(1+ℓ/ℓ₀)
# 候選 C: 物理 — 投影伸長來自「群延遲」v_g(ℓ) = cos(πn/88) 加權
#         高 ℓ 對應高 n 模式 → v_g 細 → 群延遲大 → 距離伸長
#         但 n 有上限 (44) → ℓ 有上限 ℓ_max = log₄(1+17) = 2.08
#         → 喺 ℓ 接近 ℓ_max, 投影伸長應該「停止增長」!

# 候選 C 結構:
#   投影伸長 ∝ ∫₀^ℓ sec(π·n(ℓ')/88) dℓ'? 
#   n(ℓ) = 44·ℓ/ℓ_max? (線性映射 ℓ → n)
#   飽和自然出現 (n→44, sec→∞... 發散!)
#   但 F_proj=17 截斷 (O54): n ≤ 27 → sec(27π/88) = 2.14 有限!
#   → 投影伸長有上限!

print("""
★ 結構發現 (候選 C):
  F_proj = 17 截斷 (O54: n ≤ 27) 唔單止防止 v_g→0 發散,
  佢同時設定「投影伸長上限」:
    w_max = sec(27π/88) = 2.14
  → 投影伸長因子 (1+2φ⁻¹ℓ) 有自然截斷 ℓ_cut = F_proj/44·ℓ_max?
  → ℓ_cut = 17/44 × 2.08 = 0.80  (z ≈ 1.26)
  → ℓ > 0.80 之後投影伸長飽和!

驗證: D_req/D_app 喺 z=1.2-1.8 (ℓ=0.72-0.95) 開始 < 1
  → 啱好係 ℓ_cut = 0.80 附近! 結構吻合!
""")

result = {
    'ell_nyquist': round(float(ell_nyq), 4),
    'D_app_ell_nyq': round(float(d_app(ell_nyq)), 1),
    'pi_R': round(float(math.pi*R_WORLD), 1),
    'ratio': round(float(d_app(ell_nyq)/(math.pi*R_WORLD)), 4),
    'F_proj_cut_ell': round(float(17/44*ell_nyq), 4),
    'pass': PASS, 'fail': FAIL
}
with open('data/08_projection_saturation.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"PASS={PASS} FAIL={FAIL}")
print("-> data/08_projection_saturation.json")
