#!/usr/bin/env python3
"""
03_spherical_analysis.py — 15.106° 球面幾何完整解
===================================================
用球面三角形 (冷斑, 3-fold軸, 5-fold軸) 精確解出 15.106° 嘅幾何根源。

已知:
- d3 = 15.1059° (冷斑到 3-fold)
- d5 = 22.6533° (冷斑到 5-fold)
- 3-5 軸角 = 37.3774°
- 3-fold 軸間角 = 41.8103° (dodecahedron 標準)
- 5-fold 軸間角 = 63.4350° (icosahedron 標準)

候選公式:
1. d3 = 41.81° - d5 ?
2. d3 = (41.81° - 15°) 修正?
3. d3 : d5 = 2 : 3 精確?
"""
import numpy as np, math

phi = (1 + 5**0.5) / 2
d3 = 15.1059
d5 = 22.6533
axis35 = 37.3774
axis33 = 41.8103
axis55 = 63.4350

print("=" * 66)
print("O1: 15.106° 球面幾何完整解")
print("=" * 66)

print(f"\n=== 已知量 ===")
print(f"d3 = {d3:.4f}° (冷斑→3-fold)")
print(f"d5 = {d5:.4f}° (冷斑→5-fold)")
print(f"3-5 軸角 = {axis35:.4f}°")
print(f"3-3 軸角 = {axis33:.4f}° (dodecahedron)")
print(f"5-5 軸角 = {axis55:.4f}° (icosahedron)")

print(f"\n=== 線性組合測試 ===")
combos = {
    "41.81 - 26.70": axis33 - 26.70,
    "41.81 - d5": axis33 - d5,
    "41.81 - 15.106": axis33 - d3,
    "63.435 - 41.81": axis55 - axis33,
    "d5 - d3": d5 - d3,
    "axis35 - d3": axis35 - d3,
    "axis35 - d5": axis35 - d5,
}
for name, val in combos.items():
    print(f"  {name} = {val:.4f}°")

print(f"\n=== 球面三角形完整解 ===")
# 球面三角形: 3-fold (A), 5-fold (B), 冷斑 (C)
# 邊: a = BC = d5, b = AC = d3, c = AB = axis35
a, b, c = d5, d3, axis35
# 用球面餘弦定律求角 A (喺 3-fold 位置嘅角)
cosA = (math.cos(math.radians(a)) - math.cos(math.radians(b))*math.cos(math.radians(c))) / \
       (math.sin(math.radians(b))*math.sin(math.radians(c)))
A = math.degrees(math.acos(np.clip(cosA, -1, 1)))
# 角 B (喺 5-fold 位置)
cosB = (math.cos(math.radians(b)) - math.cos(math.radians(a))*math.cos(math.radians(c))) / \
       (math.sin(math.radians(a))*math.sin(math.radians(c)))
B = math.degrees(math.acos(np.clip(cosB, -1, 1)))
# 角 C (喺冷斑位置)
cosC = (math.cos(math.radians(c)) - math.cos(math.radians(a))*math.cos(math.radians(b))) / \
       (math.sin(math.radians(a))*math.sin(math.radians(b)))
C = math.degrees(math.acos(np.clip(cosC, -1, 1)))
print(f"球面三角形 A(3-fold) = {A:.4f}°")
print(f"球面三角形 B(5-fold) = {B:.4f}°")
print(f"球面三角形 C(冷斑) = {C:.4f}°")
print(f"A + B + C = {A+B+C:.4f}° (球面三角形 > 180° = {A+B+C-180:.4f}° 過剩)")
print(f"球面過剩: {A+B+C-180:.4f}°")

print(f"\n=== 角 A 嘅結構意義 ===")
print(f"A = {A:.4f}°")
print(f"A/2 = {A/2:.4f}°")
print(f"A/3 = {A/3:.4f}°")
print(f"A/5 = {A/5:.4f}°")
print(f"90 - A = {90-A:.4f}°")
print(f"180 - A = {180-A:.4f}°")

print(f"\n=== 關鍵比例 ===")
print(f"d3/d5 = {d3/d5:.6f} vs 2/3 = {2/3:.6f} (偏差 {(d3/d5-2/3)/(2/3)*100:.4f}%)")
print(f"d3/axis33 = {d3/axis33:.6f}")
print(f"d5/axis55 = {d5/axis55:.6f}")
print(f"d3+d5 = {d3+d5:.4f}°")
print(f"axis35 = {axis35:.4f}°")
print(f"axis35 - (d3+d5) = {axis35-d3-d5:.4f}° (球面非共面修正)")

print(f"\n=== φ 組合測試 ===")
print(f"φ⁻³ rad = {math.degrees(phi**-3):.4f}° vs d3 = {d3:.4f}°")
print(f"φ⁻² rad = {math.degrees(phi**-2):.4f}° vs d5 = {d5:.4f}°")
print(f"φ⁻² - φ⁻³ = {math.degrees(phi**-2-phi**-3):.4f}° vs d3?")
print(f"2φ⁻³ = {math.degrees(2*phi**-3):.4f}°")
print(f"φ⁻³ × (1+1/16) = {math.degrees(phi**-3*(1+1/16)):.4f}° (κ 修正)")

# 儲存
with open("data/spherical_analysis.txt", "w") as f:
    f.write(f"A={A:.6f} B={B:.6f} C={C:.6f}\n")
    f.write(f"d3/d5={d3/d5:.6f}\n")
    f.write(f"axis35-d3-d5={axis35-d3-d5:.4f}\n")
print("\n✅ 已存: data/spherical_analysis.txt")
