#!/usr/bin/env python3
"""
09_delta_formula.py — δ = 15.1085° 結構公式攻關
================================================
δ = 冷斑向量 v 到最近 3-fold 軸 (頂點方向) 夾角

思路:
1. δ 可能由「冷斑喺球面三角形 (最近頂點, 次近頂點, v)」決定
2. δ 同 A₅ 群字 (shortest word) 有關?
3. δ 可能係 φ 冪/分數組合
4. δ 可能由「冷斑到最近邊 (2-fold)」同「到最近面 (5-fold)」共同決定
"""
import numpy as np, math

print("=" * 66)
print("任務2: δ = 15.1085° 結構公式攻關")
print("=" * 66)

phi = (1 + 5**0.5) / 2
inv_phi = 1/phi

# 標準幾何
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
edges_n = []
for i in range(20):
    for j in range(i+1, 20):
        d = np.linalg.norm(verts_n[i]-verts_n[j])
        if abs(d - 2*math.sqrt(2)/math.sqrt(3)) < 0.01:
            mid = np.array(norm(verts_n[i]+verts_n[j]))
            if not any(np.allclose(mid, e) or np.allclose(mid, -e) for e in edges_n):
                edges_n.append(mid)
edges_n = np.array(edges_n)

# 冷斑向量
nodes = []
with open("../cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
ra0, dec0 = nodes[0]
v = np.array([math.cos(math.radians(dec0))*math.cos(math.radians(ra0)),
              math.cos(math.radians(dec0))*math.sin(math.radians(ra0)),
              math.sin(math.radians(dec0))])

# 三個距離
def min_angle(vec, axes):
    return min(math.degrees(math.acos(np.clip(np.dot(vec, a), -1, 1))) for a in axes)
d3 = min_angle(v, verts_n)
d5 = min_angle(v, faces_n)
d2 = min_angle(v, edges_n)
print(f"\n冷斑到軸距離:")
print(f"  δ3 (頂點) = {d3:.6f}°")
print(f"  δ5 (面)   = {d5:.6f}°")
print(f"  δ2 (邊)   = {d2:.6f}°")

# 1. 球面三角形: 最近頂點, 次近頂點, v
print(f"\n=== 1. 最近頂點周圍結構 ===")
# 最近頂點
n3 = min(verts_n, key=lambda a: math.degrees(math.acos(np.clip(np.dot(v, a), -1, 1))))
d_n3 = math.degrees(math.acos(np.clip(np.dot(v, n3), -1, 1)))
print(f"最近頂點 n3, δ = {d_n3:.6f}°")
# 其他頂點距離
other_verts = [math.degrees(math.acos(np.clip(np.dot(v, a), -1, 1))) for a in verts_n]
other_verts_sorted = sorted(other_verts)
print(f"到頂點距離排序: {[f'{d:.2f}' for d in other_verts_sorted[:6]]}")
# 最近頂點喺邊個球面三角形?
# 頂點間角 (3-fold 軸間): 41.81°
# δ 同 41.81° 關係?
print(f"3-fold 軸間角: {41.8103:.4f}°")
print(f"δ3 + δ3' = ? (最近兩個頂點)")
d_n3b = other_verts_sorted[1]
print(f"  δ3 = {d_n3:.4f}°, 次近 δ3' = {d_n3b:.4f}°")
print(f"  δ3 + δ3' = {d_n3 + d_n3b:.4f}° vs 41.81°")
print(f"  δ3' − δ3 = {d_n3b - d_n3:.4f}°")

# 2. 冷斑喺「頂點-頂點大圓」上?
print(f"\n=== 2. 大圓幾何 ===")
# 最近同次近頂點
idx = np.argsort(other_verts)
n3a = verts_n[idx[0]]
n3b = verts_n[idx[1]]
axis_angle = math.degrees(math.acos(np.clip(np.dot(n3a, n3b), -1, 1)))
print(f"最近-次近頂點角: {axis_angle:.4f}° (期望 41.81°?)")
print(f"δ3 + δ3' = {d_n3 + d_n3b:.4f}°")
if abs(axis_angle - (d_n3 + d_n3b)) < 0.5:
    print(f"  ✅ v 喺兩頂點大圓上")
else:
    print(f"  ❌ v 唔喺大圓上 (差 {abs(axis_angle-d_n3-d_n3b):.2f}°)")

# 3. δ 同 φ 冪深化
print(f"\n=== 3. δ 結構搜索 ===")
target = d3
cands = {
    "15° (π/12)": 15,
    "60°/4": 15,
    "2π/24": 15,
    "φ⁻³ rad": math.degrees(phi**-3),
    "φ⁻² rad": math.degrees(phi**-2),
    "φ⁻³ + φ⁻⁵ rad": math.degrees(phi**-3 + phi**-5),
    "φ⁻² − φ⁻³ rad": math.degrees(phi**-2 - phi**-3),
    "φ⁻³ × (1+φ⁻²) rad": math.degrees(phi**-3 * (1+phi**-2)),
    "φ⁻³ × 1.117": math.degrees(phi**-3 * 1.117),
    "2φ⁻³ + φ⁻⁴ rad": math.degrees(2*phi**-3 + phi**-4),
    "φ⁻³ + κ rad": math.degrees(phi**-3 + 1/16),
    "φ⁻³ + 2κ rad": math.degrees(phi**-3 + 2/16),
    "φ⁻³ × (1+1/16) rad": math.degrees(phi**-3*(1+1/16)),
    "atan(φ⁻¹/3)": math.degrees(math.atan(1/(3*phi))),
    "atan(φ⁻²/2)": math.degrees(math.atan(1/(2*phi**2))),
    "asin(φ⁻¹/4)": math.degrees(math.asin(1/(4*phi))),
    "asin(1/φ³)": math.degrees(math.asin(1/phi**3)),
    "2*atan(1/8)": 2*math.degrees(math.atan(1/8)),
    "atan(1/4)": math.degrees(math.atan(1/4)),
    "asin(1/4)": math.degrees(math.asin(1/4)),
    "atan(1/3.7)": math.degrees(math.atan(1/3.7)),
}
print(f"目標 δ = {target:.6f}°")
for name, val in cands.items():
    diff = abs(val - target)
    mark = "✅" if diff < 0.01 else ("🟡" if diff < 0.1 else "")
    print(f"  {mark} {name:24s} = {val:10.6f}°  偏差 {diff:8.4f}°")

# 4. δ 由軌道唯一決定? 冷斑係「特殊」位置?
print(f"\n=== 4. 冷斑位置嘅特殊結構 ===")
# 冷斑 ICRS 喺銀道 (l, b) = (209, -57)
# b = -57 = -(44+13) = -(N_d + F₇)
# l = 209 = 180 + 29 = 180 + L₇
print(f"冷斑銀道: l=209° = 180+L₇, b=-57° = -(N_d+F₇)")
print(f"δ = 15.1085° 同位置碼關係?")
print(f"L₇ = 29, F₇ = 13, N_d = 22")
print(f"29-13 = 16, 29/2 = 14.5, 13+2 = 15")
print(f"(F₇ + L₀) = 13+2 = 15 → δ ≈ 15.1085? (偏差 0.7%)")
print(f"(L₇ - F₇)/2 = 8, 15.1085-8 = 7.1085?")
print(f"δ rad = {math.radians(target):.8f}")
print(f"δ/15 = {target/15:.8f}")

# 5. 睇下 δ 係咪 41.81° (3-3 軸角) 嘅某部分
print(f"\n=== 5. δ vs 軸角 ===")
print(f"3-3 軸角: 41.8103°")
print(f"δ × 2.768 = {target*2.768:.3f}")
print(f"41.81 - 2δ = {41.8103 - 2*target:.4f}°")
print(f"(41.81 - 2δ) = 11.59°?")
print(f"41.81/δ = {41.8103/target:.6f}")
print(f"180/δ = {180/target:.6f}")
print(f"360/δ = {360/target:.6f}")
print(f"δ × φ = {target*phi:.4f}°")
print(f"δ × φ² = {target*phi**2:.4f}°")
print(f"δ × 2φ = {target*2*phi:.4f}° (≈ 48.9?)")
print(f"63.435 - 2δ = {63.435 - 2*target:.4f}° (5-5 軸角相關?)")

# 儲存
with open("data/delta_analysis.txt", "w") as f:
    f.write(f"d3={d3:.8f} d5={d5:.8f} d2={d2:.8f}\n")
    f.write(f"d_n3={d_n3:.8f} d_n3b={d_n3b:.8f}\n")
    f.write(f"axis_angle={axis_angle:.8f}\n")
    f.write(f"delta/15={target/15:.8f}\n")
print("\n✅ 已存: data/delta_analysis.txt")
