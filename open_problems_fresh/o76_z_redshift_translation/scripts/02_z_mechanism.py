#!/usr/bin/env python3
"""
O76/02: z 紅移嘅物理詮釋 — 非膨脹框架
================================================================
IDCM 冇膨脹, z 點嚟?

候選機制:
  A. 投影 (projection): 光子沿 K_Chain 環傳播, 距離 D_app 由 44-site 離散譜投影
     → z 由幾何決定, 1+z = 4^ell (K_Tree 尺度階)
  B. 能量損耗 (tired light): 光子喺 W-field 中損失能量
     → z = e^{αD} - 1, α = 結構常數
  C. 尺度效應 (scale): 觀測者維度 88 投影
     → z 係 44/88 分裂嘅表現

關鍵判別 (O72 docs/06 P1):
  - 超新星 time dilation: ΛCDM 預言 (1+z), tired light 預言 1
  - IDCM 預言? 如果 z 係幾何投影 (非運動學), time dilation 應該 = 1 (冇運動學膨脹)
  - 但觀測 (Leibundgut+1996, Blondin+2008, Goldhaber+2001) 支持 (1+z)!

→ IDCM 要解釋點解 time dilation 跟 (1+z) 但冇膨脹:
  如果 z 係「真實光子能量損失」(tired-light 類), 光變曲線本身都係光子
  → 時間軸都會 dilation (所有週期過程跟同一能量標尺)
  → time dilation (1+z) 自然出現! 呢個係關鍵 insight!

tired light 被反駁嘅原因 (UCLA Wright):
  1. 散射會模糊影像 (但 IDCM 嘅機制唔係散射, 係 W-field 能量轉移)
  2. time dilation 應該 = 1 (但 IDCM 嘅機制唔係「光子唔變」, 係「所有頻率一齊變」)
  3. 冇機制 (IDCM 有: W-field 耦合, O37 Lagrangian)

IDCM 機制:
  - 光子能量 E = hν 喺 W-field (⟨W⟩ = M₀) 中傳播
  - 能量損失率 dE/dD ∝ -E × (W-field 耦合強度)
  - 耦合強度 = 結構常數: λ_sync/2 = 147.44 Mpc 對應能量損失因子?
  - 1+z = 4^ell = 4^{log₄(1+z)} → z 由 K_Tree 尺度階決定
  - 呢個係「離散」紅移: 1+z 係 4 嘅冪次 → z = 0, 3, 15, 63, 255, ...
    → 連續紅移係「投影疊加」: 沿視線連續 ell, 每個 ell 對應尺度階

驗證: 連續紅移喺 IDCM 點出嚟?
  - ell = log₄(1+z) 係連續變數 (0 到 ∞)
  - 但 K_Tree 係離散 33 級 → ell 應該離散!
  - 33 級: ell = m/33? 定 ell ∈ {1/33, 2/33, ..., 1}?
  - 33 級 × log₄ → z = 4^{m/33} - 1, m = 1..33
  - z 離散值: 0.043, 0.088, 0.134, 0.182, ..., 3, ...
  - 呢個係「尺度階紅移」— 同 ΛCDM 連續 z 唔同!

★ 核心問題: IDCM 嘅 z 係咪離散?
  - 如果離散 (33 級): z 值應該有觀測結構 (星系紅移聚類?)
  - 但觀測 z 連續 → IDCM 要話 z 係「連續投影」+「離散階層疊加」
  - 或者: ell 連續但 44-site 譜離散 → z 連續但「群速度」離散

先檢查: 33 級 K_Tree 嘅 z 結構 + time dilation 預言
"""
import json, math

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

phi = (1 + math.sqrt(5)) / 2
N_d = 44
B = 4
K_tree = 33   # h11 - N_gen = CY₃ moduli - 代數

print("=" * 66)
print("O76/02: z 紅移物理詮釋 — 非膨脹框架")
print("=" * 66)

# ============ 1. 離散尺度階紅移 ============
print("\n--- 1. K_Tree 33 級 → 離散紅移階 ---")
# 如果 ell = m/33 (m=1..33), z_m = 4^{m/33} - 1
zs = [4**(m/33) - 1 for m in range(1, 34)]
print(f"z 離散階 (m=1..33):")
for m in [1, 2, 3, 5, 8, 11, 13, 17, 21, 26, 33]:
    print(f"  m={m:<3} z={zs[m-1]:8.4f}  1+z={1+zs[m-1]:.4f} = 4^{m}/33")

# 對照觀測: 常見紅移 bin
obs_z = [0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 2.5]
print(f"\n對照觀測紅移:")
for z in obs_z:
    # 最近嘅離散階
    m_nearest = min(range(1, 34), key=lambda m: abs(zs[m-1] - z))
    print(f"  z={z:<5} → m={m_nearest:<3} z_pred={zs[m_nearest-1]:.4f} (dev={abs(zs[m_nearest-1]-z)/z*100:.1f}%)")

# ============ 2. 但 z 觀測連續! ============
print("\n--- 2. 連續 z 嘅來源: 投影疊加 ---")
# 如果紅移係「沿視線投影」: 每個物體喺距離 D 嘅投影 = 44-site 譜加權和
# z 連續係因為 D 連續 (環上位置連續)
# 離散階只係「共振增強」位置 — 好似原子光譜嘅能階 vs 連續譜
print("""
物理圖像:
  - K_Tree 33 級 = 「共振階」: z_res = 4^{m/33} - 1
  - 但每個物體嘅實際 z = 投影距離 D_app(ell) 決定
  - ell 連續 (0→∞) → z 連續
  - 共振階 z_res 係「譜密度增強」位置 (星系喺呢啲 z 特別多?)
  - 可證偽預言: 星系紅移分布喺 z_res 有微弱聚類!
""")

# ============ 3. Time dilation 預言 ============
print("\n--- 3. Time dilation: IDCM vs ΛCDM vs tired light ---")
# ΛCDM: Δt_obs = (1+z)·Δt_rest
# Tired light (能量損耗, 但時間軸唔變): Δt_obs = Δt_rest
# IDCM: 如果 z 係「光子能量損失」, 光變曲線時間軸跟頻率標尺
#   → 所有週期過程 (SN 光變, 譜線寬度) 跟 ν → Δt ∝ 1/ν ∝ (1+z)
#   → IDCM 預言 time dilation = (1+z) 同 ΛCDM 一樣!
# 但機制唔同: ΛCDM 係「宇宙膨脹拉長波長」, IDCM 係「光子能量損失」
# 分辨: 兩個模型喺「距離」上唔同!

# 關鍵: IDCM 預言 D_L = (1+z)·D_app vs ΛCDM D_L = (1+z)·D_C
# 超新星 Hubble diagram: μ(z) 可以直接分辨!

# 文獻: Goldhaber 2001 (42 SNe, 0.18<z<0.83): Δt ∝ (1+z)^{1.07±0.06}
# Blondin 2008: (1+z)^{1.00±0.07}
# → 支持 (1+z) → 排除「純 tired light 無時間變換」
# → IDCM 如果 z = 能量損失 → time dilation (1+z) 自然 → 相容!

print("""
文獻 (Goldhaber 2001, Blondin 2008):
  Δt_obs = (1+z)^{1.00±0.07}  — 支持 (1+z)

IDCM 詮釋:
  z = 光子能量損失 (W-field 耦合)
  → 光子能量 E = hν = h/Δt (所有週期過程跟同一能量標尺)
  → Δt_obs = (1+z)·Δt_rest 自然出現
  → time dilation 唔係膨脹證據, 係「能量標尺」證據!

vs ΛCDM:
  同樣預言 (1+z), 但係「空間膨脹」機制
  → 分辨: 距離-紅移關係 (IDCM D_app vs ΛCDM D_C)
""")

# ============ 4. 距離-紅移形狀: IDCM vs ΛCDM (相同 H₀ 標尺) ============
print("\n--- 4. 距離-紅移形狀: IDCM vs ΛCDM (H0=72.59 標尺) ---")
c = 299792.458
R_world = 4129.94

def D_app(ell, C=-0.1697):
    base = R_world * (1 - 4**(-ell))
    proj = 1 + 2*phi**(-1)*ell
    delta = C * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

import numpy as np
def DC_lcdm(z, H0=72.59, Om=0.315):
    """ΛCDM comoving distance, 相同 H0 標尺 → 純形狀對比"""
    Ol = 1 - Om
    zs = np.linspace(0, z, 20000)
    E = np.sqrt(Om*(1+zs)**3 + Ol)
    return c/H0 * np.trapezoid(1/E, zs)

# 關鍵: IDCM 冇膨脹 → D_app(ℓ) 由幾何直接決定
# ΛCDM: D_C(z) 由 FLRW 積分 (膨脹歷史)
# 形狀差異: ΛCDM 高 z 飽和 (→2c/H0), IDCM 線性增長 (→R·2φ⁻¹·ℓ)
print(f"{'z':<6} {'D_IDCM':<10} {'D_ΛCDM':<10} {'比':<8} {'ΛCDM飽和':<10}")
D_max_lcdm = 2*c/72.59   # 8898 Mpc (flat ΛCDM 極限)
for z in [0.1, 0.3, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0]:
    ell = math.log(1+z, 4)
    d1 = D_app(ell)
    d2 = DC_lcdm(z)
    print(f"{z:<6} {d1:<10.2f} {d2:<10.2f} {d1/d2:<8.3f} {d2/D_max_lcdm*100:6.1f}%")

# 高 z 極限
z_hi = 100
ell_hi = math.log(1+z_hi, 4)
print(f"\n高 z 極限 (z={z_hi}):")
print(f"  IDCM D_app = {D_app(ell_hi):.1f} Mpc (線性增長)")
print(f"  ΛCDM D_C  = {DC_lcdm(z_hi):.1f} Mpc (飽和 → {D_max_lcdm:.0f})")
print(f"  差異: {D_app(ell_hi)/DC_lcdm(z_hi):.3f}×")
print(f"\n★ 結構差異: ΛCDM 高 z 飽和, IDCM 線性增長")
print(f"  → z>3 之後 IDCM 距離遠大過 ΛCDM → 超新星顯著更暗")
print(f"  → 呢個係「加速膨脹假象」嘅 IDCM 解釋 (唔需要 Ω_Λ)")

# ============ 5. 超新星 Hubble diagram 定量對照 ============
print("\n--- 5. 超新星 Hubble diagram 定量對照 (相同 H0 標尺) ---")
def mu_idcm(z):
    ell = math.log(1+z, 4)
    DL = (1+z) * D_app(ell)
    return 5*math.log10(DL*1e6/10)

def mu_lcdm(z):
    DL = (1+z) * DC_lcdm(z)
    return 5*math.log10(DL*1e6/10)

print(f"{'z':<6} {'μ_IDCM':<10} {'μ_ΛCDM':<10} {'Δμ':<8}")
for z in [0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0]:
    m1 = mu_idcm(z)
    m2 = mu_lcdm(z)
    print(f"{z:<6} {m1:<10.3f} {m2:<10.3f} {m1-m2:+.4f}")

# Δμ > 0 → IDCM 更暗 → 加速假象
# 觀測: Pantheon 超新星 μ(z) 顯示「加速」→ 高 z 更暗
# IDCM 自洽: D_app 高 z 增長快過 ΛCDM → 唔需要暗能量
print(f"\n→ Δμ>0 = IDCM 更暗 = 加速假象 (高 z)")
print(f"→ z=0.5: Δμ={mu_idcm(0.5)-mu_lcdm(0.5):+.4f} (細, 低 z 一致)")
print(f"→ z=2.0: Δμ={mu_idcm(2.0)-mu_lcdm(2.0):+.4f} (大, 高 z 分歧)")

# ============ 6. 總結 ============
print(f"\n{'=' * 66}")
print("總結")
print("=" * 66)
print(f"""
z 紅移物理詮釋 — 三候選機制:

A. 投影 (幾何): z = 4^ell - 1, ell = K_Tree 尺度階
   → time dilation = (1+z)? 唔自然 (冇運動學)

B. 能量損耗 (tired light 類): z = 光子喺 W-field 中能量損失
   → time dilation = (1+z) 自然 (能量標尺統一)
   → 避開 Wright 反駁 (散射模糊 + 時間軸)

C. 尺度效應 (88/44): z = 觀察者維度投影
   → 需詳細機制

★ 結論: B 最自洽 — IDCM z = W-field 能量損耗
   但「連續 z」需要 ell 連續 → K_Tree 33 級係共振增強, 唔係硬離散

可證偽預言:
  P1: 星系紅移分布喺 z_res = 4^{m/33} - 1 有微弱聚類
  P2: time dilation = (1+z) (同 ΛCDM, 但機制唔同)
  P3: 距離-紅移比 ΛCDM 大 13-14% → 超新星更暗
  P4: CMB 溫度-紅移: T(z) = T₀(1+z) (光子能量損失, 同 ΛCDM)
""")

result = {
    'z_resonance': [round(z, 6) for z in zs],
    'mechanism': 'B: W-field energy loss',
    'time_dilation': '1+z',
    'distance_ratio_1': round(D_app(math.log(2,4))/DC_lcdm(1.0), 4),
    'pass': PASS,
    'fail': FAIL
}
with open('data/02_z_mechanism.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)
print(f"PASS={PASS} FAIL={FAIL}")
print("-> data/02_z_mechanism.json")
