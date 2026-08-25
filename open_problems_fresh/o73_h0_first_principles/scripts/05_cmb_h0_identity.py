"""
O73 攻堅 05: H3 — CMB 67.36 喺 IDCM 係咩?
=================================================================
問題: CMB (Planck) 量到 H₀ = 67.36, 距離階梯量到 73.0
      O11 解釋咗 TRGB/Miras/SH0ES (κφ⁻¹ 家族), 但 CMB 唔係!

IDCM 語境: H₀ 唔係膨脹率, 係世界環角頻率 ω_ring = c/R_world = 72.59
→ CMB 量到 67.36 係「另一種量度」— 唔同投影?

關鍵: CMB 嘅 H₀ 係從聲學視界 θ* 推導:
  θ* = r_s(z*)/D_A(z*)   (聲學視界角大小)
  r_s = 聲學視界 (sound horizon), D_A = 角直徑距離
  ΛCDM: H₀ 由 θ* 反推 (需要 r_s 模型 + 幾何)

IDCM 假設: θ* 係固定幾何量 (聲學視界角 = 結構常數?)
→ 如果 θ* 喺 IDCM 有結構值, 可以反推「CMB 量到嘅 ω_ring」
"""
import numpy as np
from scipy.special import gamma as gamma_func

# 基本常數
c = 299792.458          # km/s
Mpc_km = 3.085677581e19 # km/Mpc
Gyr_s = 3.15576e16      # s/Gyr

# IDCM 結構值
omega_ring = 72.59      # (km/s)/Mpc (世界環角頻率)
R_world = c / omega_ring  # 4129.94 Mpc

print("=" * 74)
print("1. CMB 聲學視界 H₀ 點樣嚟?")
print("=" * 74)
print("""
  Planck 2018: H₀ = 67.36 ± 0.54 (TT,TE,EE+lowE)
  來源: CMB 功率譜 → θ* (聲學視界角) + 物質密度
  θ* = 1.04110 ± 0.00031 × 10⁻² rad  (Planck 2018)

  ΛCDM 反推鏈:
    θ* = r_s(z*) / D_A(z*)
    r_s = ∫ c_s/(1+z) dz  (聲學視界, 依賴 Ω_b, Ω_m, H₀)
    D_A = 角直徑距離 (依賴 Ω_m, Ω_Λ, H₀)
    → H₀ 係自由度, fit θ* 觀測值

  關鍵: θ* 係「直接觀測量」(功率譜峰位置)
       H₀ 係「模型推導量」(fit 出嚟)
""")

print("=" * 74)
print("2. θ* 有冇結構身份? (IDCM 角度)")
print("=" * 74)
theta_star = 1.04110e-2  # rad
print(f"  θ* (Planck) = {theta_star:.6f} rad")
print(f"  θ* 單位換算: {theta_star*180/np.pi:.4f}°")
print(f"  θ* = 1/96.05 rad ≈ 1/96?")
print(f"  1/θ* = {1/theta_star:.2f} rad")
print(f"  360°/θ* = {2*np.pi/theta_star:.2f} (圓周/θ*)")
print()

# 44/88 系角度
for n in [44, 88, 176, 90, 178]:
    ang = 2 * np.pi / n
    print(f"  2π/{n:3d} = {ang*180/np.pi:8.4f}° = {ang:.6f} rad  "
          f"(對 θ*: {ang/theta_star:.4f}×)")
print()
print(f"  θ* = {theta_star:.6f} rad")
print(f"  2π/88 = {2*np.pi/88:.6f} rad")
print(f"  比例 = {(2*np.pi/88)/theta_star:.4f}")
print(f"  → θ* 係咪 = 2π/88 × 某因子?")
print(f"    2π/88/θ* = {(2*np.pi/88)/theta_star:.4f}")
print(f"    θ* = 2π/88 / {(2*np.pi/88)/theta_star:.4f}")

print()
print("=" * 74)
print("3. 聲學視界 r_s 喺 IDCM")
print("=" * 74)
# Planck 2018 聲學視界 (無量綱)
# r_s(z*) = 147.09 ± 0.26 Mpc (Planck 2018 TT,TE,EE+lowE)
r_s_planck = 147.09
print(f"  r_s (Planck) = {r_s_planck} Mpc")
print(f"  λ_sync/2 = {294.877/2:.2f} Mpc (IDCM 半同步波長)")
print(f"  r_s vs λ_sync/2: dev = {(147.09-147.44)/147.44*100:.2f}%")
print(f"  λ_sync = c·T_ring/88 = 294.88 Mpc")
print(f"  r_s = λ_sync/2 = 147.44 Mpc (O73 之前已知: dev 0.24%)")
print()
print(f"  ★ r_s = λ_sync/2: 聲學視界 = 半個同步波長!")
print(f"    λ_sync = 世界環周長/88 (觀察者維度分割)")
print(f"    r_s = λ_sync/2 → 聲學視界 = 世界環半波長")
print()

print("=" * 74)
print("4. CMB H₀ 反推: θ* + r_s → ω_ring,CMB")
print("=" * 74)
# ΛCDM: θ* = r_s/D_A(z*)
# IDCM: 冇膨脹 → D_A 係幾何距離?
# 如果 D_A(z*) = R_world (世界環半徑) 對應某紅移?

# Planck: θ* = 1.04110e-2, r_s = 147.09
# D_A = r_s/θ* = 147.09/1.04110e-2
D_A_planck = r_s_planck / theta_star
print(f"  D_A(z*) (Planck 反推) = r_s/θ* = {D_A_planck:.1f} Mpc")
print(f"  R_world = {R_world:.1f} Mpc")
print(f"  D_A/R_world = {D_A_planck/R_world:.4f}")
print(f"  R_world/D_A = {R_world/D_A_planck:.4f}")
print()

# IDCM: 如果 D_A(z*) 有結構值?
# 聲學視界角 θ* = r_s/D_A = (λ_sync/2)/D_A
# 如果 D_A = R_world: θ*_IDCM = (λ_sync/2)/R_world
theta_idcm = (294.877/2) / R_world
print(f"  若 D_A = R_world: θ*_IDCM = (λ_sync/2)/R_world = {theta_idcm:.6f} rad")
print(f"  Planck θ* = {theta_star:.6f} rad")
print(f"  dev = {(theta_idcm-theta_star)/theta_star*100:.2f}%")
print()

# 反推 CMB 量到嘅 H₀
# ΛCDM: H₀ 由 θ* fit → 如果 IDCM θ* 有結構值, 咁 CMB 量到嘅 H₀ = ?
# 粗略: H_CMB = ω_ring × (θ*_IDCM/θ*_Planck)? 唔啱, 要小心
print(f"  θ*_IDCM/θ*_Planck = {theta_idcm/theta_star:.4f}")
print(f"  72.59 × {theta_idcm/theta_star:.4f} = {72.59*theta_idcm/theta_star:.2f}")
print(f"  → 如果 θ* 係結構值 (λ_sync/2R), CMB 量到嘅 H₀ 應該 = 72.59")
print(f"    但 Planck 量到 67.36 → 唔係純幾何!")
print()

print("=" * 74)
print("5. 深入: 67.36 = 72.59 × 邊個因子?")
print("=" * 74)
ratio = 67.36 / 72.59
print(f"  67.36/72.59 = {ratio:.6f}")
print(f"  1 - ratio = {1-ratio:.6f} = {1-ratio:.2%}")
# 結構因子掃描
factors = {
    "φ⁻¹": 1/np.sqrt(5),  # 0.447
    "φ⁻¹/4": 1/(4*np.sqrt(5)),
    "κφ⁻¹": None,
    "cos(π/44)": np.cos(np.pi/44),
    "cos(π/88)": np.cos(np.pi/88),
    "sin(π/44)": np.sin(np.pi/44),
    "1/√3": 1/np.sqrt(3),
    "2/π": 2/np.pi,
    "√(2/3)": np.sqrt(2/3),
    "sin(π/3)": np.sin(np.pi/3),
    "3/4": 0.75,
    "44/45": 44/45,
    "88/89": 88/89,
    "176/177": 176/177,
}
print(f"  目標: 72.59 × f = 67.36 → f = {ratio:.6f}")
for name, val in factors.items():
    if val is None:
        continue
    if abs(val - ratio) < 0.02:
        print(f"  ★ {name:12s} = {val:.6f} (dev {(val-ratio)/ratio*100:.2f}%)")
    else:
        print(f"    {name:12s} = {val:.6f} (dev {(val-ratio)/ratio*100:.1f}%)")

# 更精細: 67.36 = 72.59 × (1 - x)?
x = 1 - ratio
print(f"\n  1 - 67.36/72.59 = {x:.6f} = {x:.2%}")
print(f"  候選: κφ⁻¹ 家族?")
kappa = 2 * np.sqrt(3)  # 假設? 需要查 IDCM κ 定義
print(f"  如果 κ = 2√3 = {kappa:.4f}, κφ⁻¹ = {kappa/np.sqrt(5):.4f}")
print(f"  x 需要 = {x:.4f}")

print()
print("=" * 74)
print("結論 (H3 初步)")
print("=" * 74)
print("""
  1. θ* (Planck 1.04110e-2 rad) 冇直接 44/88 結構身份
     - 2π/88 = 0.0714 rad, 比例 ~6.86
     - 唔係簡單分數關係
  2. r_s = λ_sync/2 閉合 (dev 0.24%) 但 λ_sync 有 H₀ 依賴
     - 所以 r_s 閉合係「re-label」唔係獨立結構
  3. 67.36/72.59 = 0.9280 = 1 - 0.0720
     - 0.0720 ≈ 1/13.89 ≈ φ⁻³/2? 需要更多掃描
     - 唔係 κφ⁻¹ 家族 (O11 話 CMB 唔係呢個家族)
  4. 初步判決: CMB 67.36 喺 IDCM 未有結構解釋
     → 張力地圖 (H6) 需要完整方法列表
     → 67.36 可能係「聲學視界反推」嘅模型依賴產物
""")
