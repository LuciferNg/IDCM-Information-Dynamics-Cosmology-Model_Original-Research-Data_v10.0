"""
O73 攻堅 06: H6 — H₀ 張力完整地圖 (IDCM 語境)
=================================================================
所有 H₀ 測量方法 → IDCM 身份 (世界環角頻率 ω_ring = 72.59)

方法列表 (2024-2025):
  - CMB (Planck 2018): 67.36 ± 0.54
  - CMB (ACT DR6): 68.3 ± 0.8 (2024)
  - CMB (SPT-3G): 68.8 ± 0.8 (2024)
  - TRGB (SH0ES 2024): 69.85 ± 0.97
  - Cepheid/SH0ES: 73.04 ± 1.04
  - Miras: 73.3 ± 2.6
  - Maser (MCP): 73.9 ± 3.0 (2024, 幾何)
  - 強透鏡 TDCOSMO: 67.4 ± 3.6 (2024)
  - 強透鏡 H0LiCOW: 73.3 ± 1.8
  - 引力波 (GW170817): 70.0 ± 7.0
  - 紅巨星 (JAGB): 72.4 ± 2.0
  - 星系團: 74 ± 2
  - 21cm (未來): ?

IDCM: ω_ring = 72.59 係世界環角頻率
  每種方法量度「投影層」→ 理論偏移?
"""
import numpy as np

phi = (1 + np.sqrt(5)) / 2
omega_ring = 72.59

print("=" * 74)
print("H₀ 張力完整地圖 (IDCM 語境)")
print("=" * 74)
methods = [
    # (名稱, 值, 誤差, 類型)
    ("CMB Planck 2018",      67.36, 0.54, "CMB 聲學"),
    ("CMB ACT DR6 2024",     68.3,  0.8,  "CMB 聲學"),
    ("CMB SPT-3G 2024",      68.8,  0.8,  "CMB 聲學"),
    ("TRGB (SH0ES 2024)",    69.85, 0.97, "恆星投影"),
    ("JAGB",                 72.4,  2.0,  "恆星投影"),
    ("GW170817",             70.0,  7.0,  "引力波"),
    ("強透鏡 TDCOSMO",        67.4,  3.6,  "透鏡"),
    ("強透鏡 H0LiCOW",        73.3,  1.8,  "透鏡"),
    ("Cepheid SH0ES",        73.04, 1.04, "恆星投影"),
    ("Miras",                73.3,  2.6,  "恆星投影"),
    ("Maser MCP 2024",       73.9,  3.0,  "幾何"),
    ("星系團",                74.0,  2.0,  "星系團"),
]
print(f"\n  ω_ring (IDCM) = {omega_ring} (km/s)/Mpc")
print(f"  {'方法':<22s} {'值':>7s} {'σ':>5s} {'偏差':>8s} {'|z|':>6s}  類型")
print(f"  {'-'*22} {'-'*7} {'-'*5} {'-'*8} {'-'*6}  {'-'*10}")

tension_map = []
for name, val, err, typ in methods:
    dev = (val - omega_ring) / omega_ring * 100
    z = (val - omega_ring) / err
    tension_map.append((name, val, err, dev, z, typ))
    print(f"  {name:<22s} {val:7.2f} {err:5.2f} {dev:+7.2f}% {z:+5.2f}  {typ}")

print()
print("=" * 74)
print("張力結構分析")
print("=" * 74)
print("""
  1. CMB 家族 (67.4-68.8) 全部低於 ω_ring 3.8-7.2%
     - Planck 67.36: -7.20% (最大偏差)
     - ACT DR6 68.3: -5.91%
     - SPT-3G 68.8: -5.22%
     → CMB 一致偏低 ~5-7%

  2. 距離階梯家族 (72.4-74.0) 全部高於/接近 ω_ring
     - Maser 73.9: +1.80% (純幾何, O11 話 0.44σ)
     - Cepheid 73.04: +0.62%
     - TRGB 69.85: -3.77% (O11: κφ⁻¹ 偏移 → 69.78 ✅)

  3. 強透鏡分歧: TDCOSMO 67.4 vs H0LiCOW 73.3
     - 同一方法, 唔同模型假設
     → 系統誤差主導, 唔係物理

  4. IDCM 判讀:
     - 距離階梯 (除 TRGB) ≈ ω_ring 或略高
     - CMB 一致低 5-7% — 呢個係「真張力」
""")

print()
print("=" * 74)
print("CMB 偏低 5-7% 嘅結構候選")
print("=" * 74)
ratio_cmb = 67.36 / 72.59   # 0.92795
print(f"  目標: 67.36/72.59 = {ratio_cmb:.6f} (1 - {1-ratio_cmb:.4f})")
print()
candidates = {
    "cos(π/88)² 積分?": None,
    "(1 - 1/44)": 43/44,
    "(1 - 1/88)": 87/88,
    "(1 - 1/90)": 89/90,
    "(1 - 1/178)": 177/178,
    "1/√(1+2φ⁻²)": 1/np.sqrt(1+2*phi**-2),
    "2/√(π+1)": 2/np.sqrt(np.pi+1),
    "√(2/π+0.5)": np.sqrt(2/np.pi+0.5),
    "(1-φ⁻³)": 1-phi**-3,
    "(1-φ⁻⁴)": 1-phi**-4,
    "cos(π/60)": np.cos(np.pi/60),
    "sin(π/2 - π/44)": np.sin(np.pi/2 - np.pi/44),
    "γ_11/4": (4*np.sin(11*np.pi/88)**2)/4,
    "γ_22/4": (4*np.sin(22*np.pi/88)**2)/4,
    "γ_7/4": (4*np.sin(7*np.pi/88)**2)/4,
    "γ_20/4": (4*np.sin(20*np.pi/88)**2)/4,
}
for name, val in candidates.items():
    if val is None:
        continue
    dev = (val - ratio_cmb) / ratio_cmb * 100
    marker = " ★" if abs(dev) < 1 else ""
    print(f"  {name:22s} = {val:.6f}  dev {dev:+.2f}%{marker}")

print()
print("  更直接: 67.36 = ω_ring - Δ?")
delta = 72.59 - 67.36
print(f"  Δ = 72.59 - 67.36 = {delta:.2f}")
print(f"  Δ/72.59 = {delta/72.59:.6f} = {delta/72.59:.2%}")
print(f"  Δ/67.36 = {delta/67.36:.6f}")
# 1/13.9, 1/14, 1/(2×7)
for d in [14, 13.9, 44/3, 15]:
    print(f"  Δ ≈ 72.59/{d:.2f}? → {72.59/d:.3f} (Δ = {delta:.2f})")

print()
print("=" * 74)
print("結論 (H6 初步)")
print("=" * 74)
print("""
  1. 張力地圖完成: 12 方法, 兩大陣營
     - CMB 家族: 67.4-68.8 (低 5-7%)
     - 距離階梯: 72.4-74.0 (≈ω_ring ± 2%)
  2. CMB 偏低 5-7% 冇明顯 κφ⁻¹/44 系結構候選
     - 0.0720 偏差 ≈ 1/13.9 — 需要更精細 PSLQ
  3. 強透鏡內部矛盾 (TDCOSMO vs H0LiCOW) = 模型依賴
     → 唔係物理張力
  4. IDCM 真正要解釋: CMB 家族點解一致低 5-7%?
     → 候選機制: 聲學視界反推嘅「模型依賴」?
     → CMB H₀ 依賴 Ω_m, Ω_Λ, r_s 模型
     → IDCM 冇膨脹 → CMB 嘅 D_A(z) 喺 IDCM 係咩?
""")
