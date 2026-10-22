#!/usr/bin/env python3
"""
O9-B: 重子拖曳張力 — m=2 vs m=3 殘差不對稱分析
=================================================
問題: m=2 (537→527, -1.86%) vs m=3 (810→815, +0.62%)
殘差符號唔對稱: m=2 負, m=3 正

標準宇宙學: 重子加載拖曳第一峰, 增強奇數峰, 壓抑偶數峰
(奇偶峰振幅差 = 重子信號)

檢查:
1. 殘差符號 vs 峰奇偶性
2. 重子一階修正: Δℓ_baryon ∝ ρ_b/ρ_m = Ω_b/Ω_m = 2/15
3. 預言: Δℓ₃ - Δℓ₂ 應該係幾多?
"""
import numpy as np
import math as _m
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
phi = (1 + 5**0.5)/2

print("="*80)
print("O9-B: 重子拖曳張力分析")
print("="*80)

# ---------- 1. 殘差 ----------
print("\n1. 峰位殘差 (IDCM 修正 vs Planck obs):")
obs = {1: 221, 2: 527, 3: 815, 4: 1013, 5: 1121, 6: 1337, 7: 1400}
pred = {1: 220, 2: 537, 3: 810, 4: 1014, 5: 1121, 6: 1340, 7: 1412}
print(f"{'m':>2} {'pred':>5} {'obs':>5} {'Δℓ':>5} {'dev%':>7} {'奇偶':>4}")
for m in range(1, 8):
    dl = obs[m] - pred[m]
    dev = dl/pred[m]*100
    parity = "奇" if m % 2 == 1 else "偶"
    print(f"{m:>2} {pred[m]:>5} {obs[m]:>5} {dl:>+5} {dev:>+6.2f}% {parity:>4}")

print("\n   奇偶統計:")
odd_devs = [obs[m]-pred[m] for m in [1, 3, 5, 7]]
even_devs = [obs[m]-pred[m] for m in [2, 4, 6]]
print(f"   奇峰 Δℓ: {odd_devs} → mean {np.mean(odd_devs):+.1f}")
print(f"   偶峰 Δℓ: {even_devs} → mean {np.mean(even_devs):+.1f}")
print(f"   奇偶差: {np.mean(odd_devs) - np.mean(even_devs):+.1f}")

# ---------- 2. 重子參數 ----------
print("\n2. 重子加載參數 (IDCM):")
omega_b_over_m = 2/15  # Ω_b/Ω_m
print(f"   Ω_b/Ω_m = 2/15 = {omega_b_over_m:.4f}")
# 標準: 重子拖曳尺標 r_b 影響 ~ Δℓ ≈ (π/2)·(Ω_b/Ω_m) 級
r_b = np.pi/2 * omega_b_over_m
print(f"   π/2 × Ω_b/Ω_m = {r_b:.4f} ℓ 單位")

# 峰間距平均
dls = [obs[m+1]-obs[m] for m in range(1, 7)]
avg_dl = np.mean(dls)
print(f"   平均峰間距: {avg_dl:.1f}")
print(f"   重子修正 (相對峰間距): {r_b/avg_dl*100:.2f}%")

# ---------- 3. 奇偶振幅比 (重子信號) ----------
print("\n3. 奇偶峰振幅比 (重子信號):")
planck = np.loadtxt(os.path.join(DATADIR, 'planck_tt.txt'))
ell_p = planck[:,0].astype(int); C_p = planck[:,1]
D_bin = C_p * ell_p*(ell_p+1)/(2*np.pi)
A = {1: 5816.5, 2: 2579.2, 3: 2552.7, 4: 1079.5, 5: 1246.3, 6: 757.9, 7: 830.2}
odd_amps = [A[m] for m in [1, 3, 5, 7]]
even_amps = [A[m] for m in [2, 4, 6]]
print(f"   奇峰振幅: {odd_amps}")
print(f"   偶峰振幅: {even_amps}")
print(f"   奇/偶 (m=3/2): {A[3]/A[2]:.3f} (重子增強 奇數峰)")
print(f"   奇/偶 (m=5/4): {A[5]/A[4]:.3f}")
print(f"   奇/偶 (m=7/6): {A[7]/A[6]:.3f}")
r_odd_even = [A[3]/A[2], A[5]/A[4], A[7]/A[6]]
print(f"   平均奇/偶: {np.mean(r_odd_even):.3f} ± {np.std(r_odd_even):.3f}")
# 標準預言: 奇/偶 ~ 1 + (重子比例)
print(f"   若重子比例 f_b = Ω_b/Ω_m = 2/15 = 0.133")
print(f"   預言奇/偶 ≈ 1 + f_b = {1+omega_b_over_m:.3f}")
print(f"   實測平均: {np.mean(r_odd_even):.3f}")

# ---------- 4. 峰位修正嘗試 ----------
print("\n4. 峰位重子修正嘗試:")
print("   m=2 偏差 -10 (537→527)")
print("   m=4 偏差 -1 (1014→1013)")
print("   m=6 偏差 -3 (1340→1337)")
print("   m=3 偏差 +5 (810→815)")
print("   m=5 偏差 0 (1121→1121)")
print("   m=7 偏差 -12 (1412→1400)")
print()
print("   偶峰 (m=2,4,6): -10, -1, -3 → mean -4.7 (負偏)")
print("   奇峰 (m=3,5,7): +5, 0, -12 → mean -2.3 (弱負)")
print()
print("   觀察: m=2 係最大殘差 (-10), m=7 係第二大 (-12)")
print("   → 唔係簡單奇偶效應, 似邊界效應 (m=2 第一偶峰, m=7 最後峰)")

# ---------- 5. 重子相位相消 ----------
print("\n5. 重子相位相消 (調律者提議):")
print("   聲波反彈相位相消於奇偶峰之間:")
print("   δφ = π × (Δℓ_m / ℓ_*)?")
# ℓ_* = 第一峰位置 ~ 220
print(f"   m=2: δℓ = -10 → δφ/π = {-10/220:.3f}")
print(f"   m=3: δℓ = +5 → δφ/π = {5/220:.3f}")
print(f"   m=2 vs m=3 對稱: {abs(-10)} vs {abs(5)} — 唔對稱!")
print()
print("   如果相消對稱: m=2 應該 +5 或 m=3 應該 -10")
print("   → 觀察: m=2=-10, m=3=+5 = -2×5 同 +5")
print("   → 比率 -2:1 — 有冇結構?")
print(f"   -2:1 = -2×L₀:1? -2×φ⁰ = -2")

# ---------- 6. 統計顯著性 ----------
print("\n6. 統計顯著性:")
planck_err = planck[:, 2]  # C_ℓ 誤差
print(f"   bin 誤差 (C_ℓ): {planck_err.min():.5f}..{planck_err.max():.5f}")
# m=2 峰 527 嘅誤差
i527 = np.where(ell_p == 527)[0][0]
sigD_527 = planck_err[i527]*527*528/(2*np.pi)
print(f"   m=2 (527): σ_D = {sigD_527:.1f} μK², D = {D_bin[i527]:.1f}")
print(f"   m=2 偏差 (IDCM-obs) = 10 ℓ = {10/avg_dl*100:.1f}% 峰間距")
