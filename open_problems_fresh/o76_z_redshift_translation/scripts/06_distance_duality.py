#!/usr/bin/env python3
"""
O76/06: IDCM 距離對偶 — D_L 同 D_A 嘅結構關係
================================================================
標準: Etherington (1933) D_L = (1+z)²·D_A (任何時空, 光子數守恆)
O76/04 顯示: IDCM D_L = (1+z)²·D_app 完全唔 work (χ²=8098)

問題: IDCM 嘅 D_L 同 D_A 關係係咩?

IDCM 冇膨脹 → 冇光子能量隨尺度衰減嘅「膨脹」部分
但光子能量損失 (W-field) 會同時影響:
  - 觀測頻率 ν_obs = ν_em/(1+z)  (能量損失)
  - 光度距離 (能量通量)
  - 角直徑距離 (幾何)

Etherington 嘅證明假設: 光沿 null geodesic 傳播, 冇吸收散射
IDCM: W-field 能量損失係「吸收」? 定係「幾何」?

如果能量損失係「幾何」(度規效應):
  → D_L = (1+z)²·D_A 仍然成立 (Etherington 時空獨立!)
  → 但 O76/04 顯示 (1+z)² 唔 work!

如果能量損失係「散射/吸收」(非度規):
  → Etherington 失效!
  → D_L 有額外衰減因子: D_L = (1+z)·D_A·√(1+z)^extra?

關鍵: D_L 同 D_A 喺 IDCM 嘅關係必須由 W-field 機制決定

候選: IDCM D_L = (1+z)·D_app (O76/03 用, χ²=2096)
      ΛCDM D_L = (1+z)²·D_A_ΛCDM

但兩者都有系統殘差 → 真正關係喺中間?

★ 全新方法: 唔用理論 D_L, 直接用觀測約束 D_L/D_A 比!
  Pantheon+ 有 MU_SH0ES (光度距離) + CMB/DESI 有 D_A
  直接量度 D_L/D_A vs z → 睇 IDCM 預言咩?

先做理論分析: IDCM 中光嘅能量演化
  光子能量 E ∝ 1/(1+z) (紅移定義)
  光度距離 D_L = √(L/4πF)  — L 固有光度, F 觀測通量
  通量 F = E_obs·N_ph/(4πD_A²·Δt_obs)  — N_ph 光子數
  = (E_em/(1+z))·N_ph/(4πD_A²·Δt_rest(1+z))
  = L/(4πD_A²·(1+z)⁴)·(1+z)³  [E_obs=E_em/(1+z), Δt_obs=Δt_rest(1+z)]
  等等 — 呢個係標準推導, 出 (1+z)⁴ 只係因為「膨脹」假設?

唔係 — 上面係通量衰減 (1+z)⁴ 嘅標準推導:
  (1+z)⁴ = ①光子能量 (1+z) ②光子數 (1+z)³ 體積
  如果冇膨脹: 光子數唔變 → (1+z)³ 冇咗
  → F = L/(4πD_A²·(1+z)²)  [能量損失 (1+z) + 時間 dilation (1+z)]
  → D_L² = L/(4πF) = D_A²·(1+z)²
  → D_L = (1+z)·D_A  ← O76/03 用嘅!

結論: IDCM 冇膨脹 → D_L = (1+z)·D_A (唔係 (1+z)²)
  「時間 dilation (1+z)」來自光子能量損失嘅伴隨效應
  「光子數」守恆 (冇膨脹體積) → 冇 (1+z)³ 因子

→ O76/03 嘅 D_L = (1+z)·D_app 係正確嘅 IDCM 距離對偶!
→ 但係殘差仲喺度 → D_app 形狀需要修正 (唔係 D_L 定義問題)
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

print("=" * 70)
print("O76/06: IDCM 距離對偶 — D_L 同 D_A 嘅結構關係")
print("=" * 70)

# ============ 1. 理論推導 ============
print("""
★ Etherington 對偶喺 IDCM 嘅修正:

ΛCDM (膨脹): D_L = (1+z)²·D_A
  因子分解:
    (1+z)¹ = 光子能量損失 (ν_obs = ν_em/(1+z))
    (1+z)³ = 光子數密度下降 (膨脹體積 (1+z)³)
    → 總共 (1+z)⁴ 通量衰減 → D_L² = D_A²(1+z)⁴ → D_L = (1+z)²·D_A

IDCM (冇膨脹, W-field 能量損失):
    (1+z)¹ = 光子能量損失 (ν_obs = ν_em/(1+z)) ← 一樣!
    (1+z)⁰ = 光子數守恆 (冇膨脹體積!) ← 唔同!
    + 時間 dilation (1+z)¹: 光變曲線跟能量標尺
    → 通量衰減 (1+z)² → D_L = (1+z)·D_A

★ 距離對偶: IDCM D_L = (1+z)·D_A  ← O76/03 正確!
""")

# ============ 2. 驗證: 用 Pantheon MU_SH0ES 直接量度 ============
print("--- 2. 直接量度 D_L/D_A 比 (Pantheon+ 光度距離 vs BAO) ---")
# Pantheon+ 有 MU_SH0ES 列 (光度距離模數)
data_path = 'data/pantheon/Pantheon+SH0ES.dat'
with open(data_path) as f:
    header = f.readline().split()
col = {name: i for i, name in enumerate(header)}
zs, mu_sh0es = [], []
with open(data_path) as f:
    f.readline()
    for line in f:
        parts = line.split()
        if len(parts) < len(header): continue
        zs.append(float(parts[col['zCMB']]))
        mu = float(parts[col['MU_SH0ES']])
        if mu > 0:
            mu_sh0es.append(mu)
        else:
            mu_sh0es.append(np.nan)
zs = np.array(zs); mu_sh0es = np.array(mu_sh0es)
print(f"MU_SH0ES 有效: {np.isfinite(mu_sh0es).sum()}/{len(zs)}")

# D_L 由 μ 推: D_L = 10^{(μ-25)/5} Mpc
DL_obs = 10**((mu_sh0es - 25)/5)

# 對照: IDCM D_A = D_app, ΛCDM D_A = D_C/(1+z)
R_WORLD = 4129.94
PHI = (1 + math.sqrt(5)) / 2
C_DELAY = -0.1697
C_LIGHT = 299792.458
OMEGA_RING = 72.59

def dc_lcdm(z, H0, Om):
    """ΛCDM comoving distance"""
    zz = np.geomspace(1e-6, max(z, 1e-4), 2000)
    E = np.sqrt(Om*(1+zz)**3 + (1-Om))
    return C_LIGHT/H0 * np.trapezoid(1/E, zz)

def d_app(ell, C=C_DELAY):
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2*PHI**(-1)*ell
    delta = C * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

print(f"\n{'z':<6} {'N':<4} {'<D_L/D_A> obs':<14} {'(1+z) IDCM':<12} {'(1+z)²':<8}")
# 分 bin: D_L/D_A where D_A = D_app (IDCM) 同 D_C/(1+z) (ΛCDM)
bins = [(0.01, 0.05), (0.05, 0.1), (0.1, 0.2), (0.2, 0.4), (0.4, 0.8), (0.8, 1.5)]
for lo, hi in bins:
    m = (zs >= lo) & (zs < hi) & np.isfinite(mu_sh0es)
    if m.sum() < 5: continue
    z_mid = zs[m].mean()
    ell_mid = math.log(1+z_mid, 4)
    Da_idcm = d_app(ell_mid)
    Da_lcdm = dc_lcdm(z_mid, 67.4, 0.315)/(1+z_mid)
    ratio_obs = np.nanmedian(DL_obs[m]/Da_idcm)
    print(f"{lo:.2f}-{hi:.2f}  {m.sum():<4} {ratio_obs:<14.3f} {(1+z_mid):<12.3f} {(1+z_mid)**2:<8.3f}")

# ============ 3. 殘差嘅真正來源 ============
print("\n--- 3. 殘差結構分析: D_app 形狀 vs ΛCDM D_C 形狀 ---")
# IDCM 殘差: S 形 (低 z 偏亮, 高 z 偏暗)
# → D_app 喺低 z 太短 (<0.1), 高 z 太長 (>0.5)
# → 呢個同 D_app 嘅 (1+2φ⁻¹ℓ) 投影項有關 — 佢係線性增長
# → ΛCDM D_C 喺高 z 飽和 (c/H0·const) — 亞線性

# 比較 D_app 同「理想」形狀: D ∝ ln(1+z) (tired light)
# 或 D ∝ z/(1+z) (Milne) 或 ΛCDM
print(f"{'z':<6} {'D_app':<9} {'R·ln(1+z)':<11} {'z/(1+z)·R':<11} {'ΛCDM D_C':<10}")
for z in [0.05, 0.1, 0.2, 0.5, 1.0, 2.0]:
    ell = math.log(1+z, 4)
    da = d_app(ell)
    tl = R_WORLD * math.log(1+z)
    milne = R_WORLD * z/(1+z)
    dc = dc_lcdm(z, OMEGA_RING, 0.315)
    print(f"{z:<6} {da:<9.1f} {tl:<11.1f} {milne:<11.1f} {dc:<10.1f}")

# D_app ≈ R(1-4^{-ℓ})(1+2φ⁻¹ℓ)
# (1-4^{-ℓ}) = (1 - 1/(1+z)) = z/(1+z)  ← Milne 形狀!
# (1+2φ⁻¹ℓ) = 投影伸長修正
# → D_app = R·(z/(1+z))·(1+2φ⁻¹ℓ) + δ 修正
# → 基礎形狀係 Milne (z/(1+z)), 唔係 ΛCDM!
# Milne: D_C = c/H0·z/(1+z)  — 空宇宙無質量
# ΛCDM: D_C 高 z 飽和 → 比 Milne 長

print("\n★ 發現: D_app 基礎形狀 = Milne (z/(1+z)) × 投影伸長")
print("  Milne: R·z/(1+z) — 冇質量冇暗能量嘅「空」宇宙")
print("  ΛCDM: 高 z 飽和 (暗能量主導後加速)")

# ============ 4. 殘差預言 ============
print("\n--- 4. 殘差預言: Milne vs ΛCDM vs IDCM ---")
# 如果 IDCM 基礎係 Milne: 高 z D_app 比 ΛCDM 短 (Milne 飽和更快)
# 但 O76/05 顯示 IDCM 高 z 偏暗 (距離太長)!
# → 矛盾? 睇下數值:
print(f"D_app(z=2) = {d_app(math.log(3,4)):.1f} vs Milne R·2/3 = {R_WORLD*2/3:.1f}")
print(f"D_app(z=5) = {d_app(math.log(6,4)):.1f} vs Milne R·5/6 = {R_WORLD*5/6:.1f}")
print(f"→ D_app 比 Milne 長! (投影伸長 (1+2φ⁻¹ℓ) 主導)")

result = {
    'DL_relation': 'D_L = (1+z)·D_A (IDCM 距離對偶)',
    'note': '冇膨脹 → 光子數守恆 → 冇 (1+z)³ 因子',
    'base_shape': 'Milne z/(1+z) × 投影伸長',
    'pass': PASS, 'fail': FAIL
}
with open('data/06_distance_duality.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nPASS={PASS} FAIL={FAIL}")
print("-> data/06_distance_duality.json")
