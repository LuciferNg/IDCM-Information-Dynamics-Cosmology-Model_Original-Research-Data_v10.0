"""
IDCM v10.0 — δ_CP 精確值分析
================================
最優 δ = 66.40° (平衡 V_td, V_ts, J_CP)
接近 2π/5 = 72° 但有小偏移
"""

import math
import numpy as np

φ = (1 + math.sqrt(5)) / 2

# 檢查 δ_optimal 嘅物理表達式
δ_opt = 66.40
δ_opt_rad = math.radians(δ_opt)

print("δ_CP 精確值分析\n")
print(f"δ_optimal = {δ_opt:.4f}°")
print(f"2π/5 = 72°")
print(f"偏差 = {72 - δ_opt:.4f}° = {math.radians(72 - δ_opt):.6f} rad\n")

# 檢查同 K_Chain 嘅關係
π_88 = math.pi / 88
print(f"π/88 = {math.degrees(π_88):.6f}° (K_Chain 相位量子)")
print(f"偏差 / (π/88) = {(72-δ_opt)/math.degrees(π_88):.4f}")

# 檢查 φ-power 表達式
for k in range(1, 20):
    δ_phi = math.degrees(2 * math.pi / 5 - φ**(-k))
    if abs(δ_phi - δ_opt) < 1:
        print(f"δ = 2π/5 - φ⁻^{k} = {δ_phi:.4f}° (diff {abs(δ_phi-δ_opt):.4f}°)")

# 檢查 K_Tree 修正
for M in [33, 32, 34]:
    δ_M = 72 - 360/M
    print(f"δ = 72° - 360°/{M} = {δ_M:.4f}° (diff {abs(δ_M-δ_opt):.4f}°)")

# 最佳 δ 表達式: δ = 72° - 1/π
δ_1π = 72 - 180/(math.pi**2)
print(f"\nδ = 72° - 180/π² = {δ_1π:.4f}° (diff {abs(δ_1π-δ_opt):.4f}°)")

# δ = 72° - 2π/φ?
δ_phi_corr = 72 - math.degrees(2*math.pi/φ)
print(f"δ = 72° - 2π/φ = {δ_phi_corr:.4f}° (diff {abs(δ_phi_corr-δ_opt):.4f}°)")

# δ = 2π/φ²?
δ_phi2 = 360 / φ**2
print(f"δ = 360/φ² = {δ_phi2:.4f}° (diff {abs(δ_phi2-δ_opt):.4f}°)")

# δ = 360/(φ+1)?
δ_phi1 = 360 / (φ + 1)
print(f"δ = 360/(φ+1) = {δ_phi1:.4f}° (diff {abs(δ_phi1-δ_opt):.4f}°)")

# δ = 360/φ - 180?
δ_phi_180 = 360/φ - 180
print(f"δ = 360/φ - 180 = {δ_phi_180:.4f}° (diff {abs(δ_phi_180-δ_opt):.4f}°)")

# δ = arctan(φ) approximately?
δ_atan_phi = math.degrees(math.atan(φ))
print(f"δ = arctan(φ) = {δ_atan_phi:.4f}° (diff {abs(δ_atan_phi-δ_opt):.4f}°)")

# δ = 360/(2π) × π/φ?
# 即 δ = 180/φ?
δ_180_phi = 180 / φ
print(f"δ = 180/φ = {δ_180_phi:.4f}° (diff {abs(δ_180_phi-δ_opt):.4f}°)")

# 睇下最佳 δ 同 beat frequency 嘅關係
# 用 44 個 mode 嘅 ω_n
ω = np.array([2 * abs(math.sin(math.pi * n / 88)) for n in range(1, 45)])
def beat(i, j):
    return abs(ω[i-1] - ω[j-1])

# δ = arctan(beat(a,b)/beat(c,d)) * 某個因子?
# 或者 δ = 180/π × 某個 beat ratio
print(f"\nBeat ratio 分析:")
for i, j, k, l in [(5,6,19,25), (33,35,3,22), (42,43,10,31), (4,13,9,25)]:
    ratio = beat(i,j) / beat(k,l)
    δ_from_beat = math.degrees(math.atan(ratio))
    print(f"  arctan(beat({i},{j})/beat({k},{l})) = {δ_from_beat:.4f}° (diff {abs(δ_from_beat-δ_opt):.4f}°)")

# 留意: 最佳 δ 其實係 66.40°, 接近 66.0° = 360/5.4545...
# 或 66.40° = 180 - 113.6° = 180 - 2π/φ²?
# 或 66.40° = 360/φ - 90?
print(f"\n其他候選:")
for expr in [360/φ - 90, 180 - 360/φ, 180/φ**2, 360/(φ**2), 360/φ - 180/φ**2]:
    print(f"  {expr:.4f}° (diff {abs(expr-δ_opt):.4f}°)")