#!/usr/bin/env python3
"""
05_exact_formula.py — 26.091346° 精確閉合 (深化搜索)
=====================================================
26.091346° 係 A₅ 軌道相似不變量。搜尋精確公式:

候選類別:
1. arccos 型: acos(x) 其中 x ∈ {φ 分數, √ 分數, 有理數}
2. arctan 型: atan(p/q) p,q 有理
3. π 分數組合
4. 球面幾何: 標準 RID 頂點對角
5. 群理論: A₅ 元素最短 rotation angle
"""
import numpy as np, math, itertools

phi = (1 + 5**0.5) / 2
target = 26.091346
print("=" * 66)
print(f"新O1: 26.091346° 精確閉合 (深化)")
print("=" * 66)

# 1. cos/sin/tan 值
c = math.cos(math.radians(target))
s = math.sin(math.radians(target))
t = math.tan(math.radians(target))
print(f"\n=== 三角值 ===")
print(f"cos = {c:.12f}")
print(f"sin = {s:.12f}")
print(f"tan = {t:.12f}")
print(f"1/cos = {1/c:.12f}")
print(f"1/tan = {1/t:.12f}")

# 候選代數數: 檢查 cos 係咪 φ 分數
print(f"\n=== cos 值對比 φ 組合 ===")
cos_cands = {
    "φ⁻¹": 1/phi, "φ⁻²": 1/phi**2, "φ⁻³": 1/phi**3, "φ⁻⁴": 1/phi**4,
    "1/√2": 1/math.sqrt(2), "1/√3": 1/math.sqrt(3), "1/√5": 1/math.sqrt(5),
    "√3/2": math.sqrt(3)/2, "√5/2": math.sqrt(5)/2,
    "φ/2": phi/2, "1/2φ": 1/(2*phi), "√φ/2": math.sqrt(phi)/2,
    "√(3-φ)/2": math.sqrt(3-phi)/2,
    "1/√(2φ)": 1/math.sqrt(2*phi),
    "√(5-√5)/8": math.sqrt((5-math.sqrt(5))/8),
    "√(5+√5)/8": math.sqrt((5+math.sqrt(5))/8),
    "√(10-2√5)/4": math.sqrt(10-2*math.sqrt(5))/4,
    "3/4": 0.75, "2/3": 2/3, "1/3": 1/3, "1/4": 0.25,
}
print(f"cos(26.091°) = {c:.8f}")
for name, val in cos_cands.items():
    diff = abs(val - c)
    if diff < 0.001:
        print(f"  ✅ {name} = {val:.8f} (差 {diff:.8f})")
    elif diff < 0.01:
        print(f"  🟡 {name} = {val:.8f} (差 {diff:.8f})")

# 2. arccos 反推: acos(x) = 26.0913° → x = ?
# 檢查 x 係咪 φ 組合
print(f"\n=== acos 反推: x = cos(26.0913°) ===")
print(f"x = {c:.12f}")
# x 嘅連分數
from fractions import Fraction
cf = Fraction(c).limit_denominator(1000)
print(f"x ≈ {cf} = {float(cf):.6f} (差 {abs(float(cf)-c):.6f})")
cf2 = Fraction(c).limit_denominator(10000)
print(f"x ≈ {cf2} = {float(cf2):.8f} (差 {abs(float(cf2)-c):.8f})")

# 3. atan 反推
print(f"\n=== atan 反推: t = tan(26.0913°) ===")
print(f"t = {t:.12f}")
cf3 = Fraction(t).limit_denominator(1000)
print(f"t ≈ {cf3} = {float(cf3):.6f} (差 {abs(float(cf3)-t):.6f})")
cf4 = Fraction(t).limit_denominator(10000)
print(f"t ≈ {cf4} = {float(cf4):.8f} (差 {abs(float(cf4)-t):.8f})")

# 4. tan 同 φ 組合
print(f"\n=== tan 值對比 φ 組合 ===")
tan_cands = {
    "φ⁻¹": 1/phi, "φ⁻²": 1/phi**2, "φ⁻³": 1/phi**3,
    "1/2": 0.5, "2/3": 2/3, "1/√5": 1/math.sqrt(5),
    "√φ⁻¹": math.sqrt(1/phi), "φ⁻¹/2": 1/(2*phi),
    "√(φ-1)": math.sqrt(phi-1), "φ⁻²/2": 1/(2*phi**2),
}
for name, val in tan_cands.items():
    diff = abs(val - t)
    if diff < 0.01:
        print(f"  {'✅' if diff<0.001 else '🟡'} {name} = {val:.8f} (差 {diff:.8f})")

# 5. A₅ 群理論: 最短非平凡 rotation angle
print(f"\n=== A₅ 群 rotation angles ===")
# 標準 A₅ 元素旋轉角
print(f"5-fold: 72° (繞面中心)")
print(f"3-fold: 120° (繞頂點)")
print(f"2-fold: 180° (繞邊中點)")
print(f"呢啲都唔係 26.09°")
# 但「最短角」可能係兩元素乘積?
# g1·g2 嘅 rotation angle?
print(f"\n=== 群字乘積角度 ===")
def rot_matrix(axis, angle):
    axis = np.array(axis) / np.linalg.norm(axis)
    s, c = math.sin(angle), math.cos(angle)
    K = np.array([[0, -axis[2], axis[1]],
                  [axis[2], 0, -axis[0]],
                  [-axis[1], axis[0], 0]])
    return np.eye(3) + s*K + (1-c)*K@K

inv_phi = 1/phi
verts = []
for sx in [-1, 1]:
    for sy in [-1, 1]:
        for sz in [-1, 1]:
            verts.append((sx, sy, sz))
for sx in [-1, 1]:
    for sy in [-1, 1]:
        verts.append((0, sx*inv_phi, sy*phi))
        verts.append((sx*inv_phi, sy*phi, 0))
        verts.append((sx*phi, 0, sy*inv_phi))
faces = []
for sx in [-1, 1]:
    for sy in [-1, 1]:
        faces.append((0, sx, sy*phi))
        faces.append((sx, sy*phi, 0))
        faces.append((sx*phi, 0, sy))
def norm(v):
    n = math.sqrt(v[0]**2+v[1]**2+v[2]**2)
    return np.array(v)/n
verts_n = np.array([norm(v) for v in verts])
faces_n = np.array([norm(v) for v in faces])
g1 = rot_matrix(faces_n[0], 2*math.pi/5)
g2 = rot_matrix(verts_n[0], 2*math.pi/3)

# 所有 60 元素嘅旋轉角
angles = set()
group = [np.eye(3)]
seen = {tuple(np.eye(3).flatten())}
queue = [np.eye(3)]
while queue:
    M = queue.pop(0)
    for gen in [g1, g2]:
        new = gen @ M
        key = tuple(np.round(new.flatten(), 10))
        if key not in seen:
            seen.add(key)
            group.append(new)
            queue.append(new)
for g in group:
    tr = np.trace(g)
    ang = math.degrees(math.acos(np.clip((tr-1)/2, -1, 1)))
    angles.add(round(ang, 3))
print(f"A₅ 元素旋轉角: {sorted(angles)}")
print(f"最小非零: {sorted(angles)[1]}°")

# 6. 26.09 vs 72/3?
print(f"\n=== 幾何組合 ===")
print(f"72/3 = {72/3}° (唔係)")
print(f"120/5 = {120/5}°")
print(f"72/2.76 = {72/2.76:.4f}")
print(f"63.435-37.377 = {63.435-37.377:.3f}°")
print(f"41.81/1.6 = {41.81/1.6:.3f}")
print(f"180/6.9 = {180/6.9:.4f}")
print(f"72-45 = {72-45}°")
print(f"120-90-3.9 = {120-90-3.9:.1f}")
