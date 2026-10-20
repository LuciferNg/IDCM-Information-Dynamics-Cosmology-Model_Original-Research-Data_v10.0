#!/usr/bin/env python3
"""
04_formula_search.py — 15.1059° 精確代數式搜索
=================================================
搜尋 d3=15.1059° 嘅結構公式: φ 冪, π 分數, √ 組合
"""
import numpy as np, math, itertools

phi = (1 + 5**0.5) / 2
d3 = 15.1059
d5 = 22.6533
targets = {'d3': d3, 'd5': d5, 'L45': 45.3122, 'delta': 163.64}

# 候選基本量 (度)
bases = {
    'π/12': 15.0, 'π/8': 22.5, 'π/6': 30.0, 'π/5': 36.0,
    '2π/5': 72.0, 'π/4': 45.0, 'π/3': 60.0,
    'φ⁻¹ rad': math.degrees(1/phi), 'φ⁻² rad': math.degrees(1/phi**2),
    'φ⁻³ rad': math.degrees(1/phi**3), 'φ⁻⁴ rad': math.degrees(1/phi**4),
    'φ⁻⁵ rad': math.degrees(1/phi**5),
    'acos(1/√5)': math.degrees(math.acos(1/math.sqrt(5))),
    'acos(1/√3)': math.degrees(math.acos(1/math.sqrt(3))),
    'acos(1/√15)': math.degrees(math.acos(1/math.sqrt(15))),
    'asin(1/√5)': math.degrees(math.asin(1/math.sqrt(5))),
    'asin(1/√3)': math.degrees(math.asin(1/math.sqrt(3))),
    'asin(1/φ)': math.degrees(math.asin(1/phi)),
    'atan(1/φ)': math.degrees(math.atan(1/phi)),
    'atan(1/φ²)': math.degrees(math.atan(1/phi**2)),
    'atan(φ⁻¹/2)': math.degrees(math.atan(1/(2*phi))),
    'ε rad': math.degrees(1/(4*phi)),
    'κ rad': math.degrees(1/16),
}

print("=" * 66)
print("O1: 15.1059° 公式搜索")
print("=" * 66)

# 單量測試
print(f"\n=== 單一候選 (偏差 < 0.1°) ===")
for name, val in bases.items():
    for tname, t in targets.items():
        if abs(val - t) < 0.1:
            print(f"  {tname} = {t:.4f} ≈ {name} = {val:.4f} (偏差 {abs(val-t):.4f}°)")

# 兩量組合 (a ± b, a*b/θ)
print(f"\n=== 兩量組合 (偏差 < 0.01°) ===")
names = list(bases.keys())
vals = list(bases.values())
found = []
for i in range(len(vals)):
    for j in range(len(vals)):
        if i == j: continue
        combos = {
            f'{names[i]}+{names[j]}': vals[i] + vals[j],
            f'{names[i]}-{names[j]}': vals[i] - vals[j],
            f'({names[i]}+{names[j]})/2': (vals[i] + vals[j])/2,
            f'({names[i]}-{names[j]})/2': (vals[i] - vals[j])/2,
        }
        for cname, cval in combos.items():
            for tname, t in targets.items():
                if abs(cval - t) < 0.01:
                    found.append((tname, t, cname, cval, abs(cval-t)))
for tname, t, cname, cval, diff in found[:15]:
    print(f"  {tname} = {t:.4f} ≈ {cname} = {cval:.4f} (偏差 {diff:.5f}°)")

# 特別: d3 同 d5 嘅關係
print(f"\n=== d3/d5 組合 ===")
print(f"d3+d5 = {d3+d5:.4f}°")
print(f"d5-d3 = {d5-d3:.4f}°")
print(f"2*d3 = {2*d3:.4f}°")
print(f"3*d3 = {3*d3:.4f}°")
print(f"2*d5 = {2*d5:.4f}°")
print(f"3*d3-2*d5 = {3*d3-2*d5:.4f}° (0 = 完美2:3)")
print(f"d3*d5 = {d3*d5:.1f}")

# 41.81° (3-3) 同 63.435° (5-5) 嘅球面三角形
print(f"\n=== dodecahedron 標準球面三角形 ===")
# 3-3 間角: 41.8103°; 5-5 間角: 63.4349°
# 冷斑喺 3-fold 同 5-fold 之間: 邊 = d3, d5, axis35
# 球面三角形面積 = 過剩
excess = 0.8795
print(f"球面過剩 = {excess:.4f}° = {math.radians(excess):.6f} rad")
print(f"ε³ = {math.degrees(1/(4*phi)**3):.4f}°")
print(f"ε⁴ = {math.degrees(1/(4*phi)**4):.4f}°")
print(f"ε⁵ = {math.degrees(1/(4*phi)**5):.4f}°")
print(f"κ² = {math.degrees(1/256):.4f}°")
print(f"κ²×2 = {math.degrees(2/256):.4f}°")
