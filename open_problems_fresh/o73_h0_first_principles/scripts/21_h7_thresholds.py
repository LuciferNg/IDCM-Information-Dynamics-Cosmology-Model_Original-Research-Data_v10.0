"""
O73 攻堅 21: H7 預言量化 — 判決閾值計算
=================================================================
每個可證偽預言嘅「否證/確認」閾值量化:
  P1: MCP 收斂 → 幾多星系先分辨 72.6 vs 73.9?
  P3: ngVLA σ<1% → 需要幾多星系?
  P5: θ* 收窄 → 幾多誤差先分辨 1.04110 vs 1.04125?
"""
import mpmath as mp
import numpy as np
mp.mp.dps = 20

print("=" * 74)
print("1. P1/P3: Maser 星系數量 vs 精度")
print("=" * 74)
# 單星系 Maser H₀ 誤差 ~3.0 (MCP 2024)
# N 個星系平均: σ_N = 3.0/√N
sigma_1 = 3.0
for N in [1, 5, 10, 20, 50, 100, 200]:
    s = sigma_1 / np.sqrt(N)
    # 分辨 72.6 vs 73.9 (差 1.3)
    z = 1.3 / s
    print(f"  N={N:4d}: σ = {s:.2f}, 分辨 72.6 vs 73.9 → z = {z:.2f}σ")
print()

print("=" * 74)
print("2. P3: ngVLA σ < 1% 需要幾多?")
print("=" * 74)
target_sigma = 0.01 * 72.59  # 1% of 72.59 = 0.73
print(f"  ngVLA 目標: σ < {target_sigma:.2f} (1% of 72.59)")
print(f"  假設 ngVLA 單星系 σ = 1.0 (改進 3x)")
for N in [10, 30, 50, 100, 200]:
    s = 1.0 / np.sqrt(N)
    print(f"  N={N:4d}: σ = {s:.3f} {'✅ < 0.73' if s < target_sigma else '❌'}")
print()

print("=" * 74)
print("3. P5: θ* 收窄測試")
print("=" * 74)
theta_idcm = 7*mp.pi/2112
theta_planck = mp.mpf('1.04110e-2')
diff = theta_idcm - theta_planck
print(f"  θ*_IDCM - θ*_Planck = {mp.nstr(diff, 4)} rad")
print(f"  要分辨呢個差, 需要 σ_θ < {mp.nstr(diff/2, 4)} (2σ 分辨)")
print(f"  Planck 現有 σ_θ = 3.1e-7 — 已經 < 7.4e-7!")
print(f"  → 但 Planck 話 1.04110 (偏離 4.76σ)")
print(f"  → 即係 Planck 已經夠精確分辨, 但量到嘅唔係 IDCM 值!")
print()
print(f"  需要: 獨立實驗 (ACT/CMB-S4) 量 θ* 到 ±0.005%")
sigma_needed = 0.00005 * theta_planck
print(f"  σ_needed = 0.005% × θ* = {mp.nstr(sigma_needed, 4)} rad")
print(f"  ACT DR6 現有 σ = 1.0e-6 — 已接近!")
print()

print("=" * 74)
print("4. P4: ACT/SPT 輕微偏高檢查")
print("=" * 74)
pred = 67.407
for name, val, err in [("Planck", 67.36, 0.54), ("ACT DR6", 68.3, 0.8), ("SPT-3G", 68.8, 0.8)]:
    z = (pred - val) / err
    print(f"  {name:10s}: 觀測 {val}±{err}, 預言 {pred}, z = {z:+.2f}σ")
print()
print(f"  三個實驗 z 加權平均:")
w = [1/0.54**2, 1/0.8**2, 1/0.8**2]
vals = [67.36, 68.3, 68.8]
wmean = sum(v*w[i] for i, v in enumerate(vals)) / sum(w)
werr = 1/np.sqrt(sum(w))
z_w = (pred - wmean) / werr
print(f"  加權平均 = {wmean:.2f} ± {werr:.2f}")
print(f"  預言 67.407 vs 加權平均: z = {z_w:+.2f}σ")
print()

print("=" * 74)
print("5. 總結: 預言閾值")
print("=" * 74)
print("""
  P1: 20+ Maser 星系 → σ ~0.67 → 分辨 72.6 vs 73.9 (z~2σ)
  P3: ngVLA 100 星系 (σ~0.1) → 明確分辨 (z~13σ)
  P5: σ_θ < 7.4e-7 已分辨 — 現有 Planck/ACT 已夠
      → 關鍵: 未來 θ* 會唔會「移動」到 1.04125?
  P4: 加權平均 67.93 ± 0.39 vs 預言 67.407 → z = -1.33σ
      (ACT/SPT 偏高 1-1.7σ — 統計漲落範圍內, 但輕微系統傾向)
      單獨 Planck: z = +0.09σ ✅ 最準
""")
