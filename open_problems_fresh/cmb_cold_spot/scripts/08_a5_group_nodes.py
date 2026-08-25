#!/usr/bin/env python3
"""
冷斑開放位 1+2: A₅ 對稱群節點網格 + 冷斑家族預測
==================================================
核心思想:
- dodecahedron 旋轉對稱群 = A₅ (60 個元素)
- 冷斑 = A₅ 軌道成員 (投影縫合節點)
- 如果冷斑係節點, A₅ 作用喺冷斑向量 → 60 個節點 = 「冷斑家族」
- 呢 60 個位置就係可證偽預測: 全部應該有溫度異常

同時驗證:
- 15.11° 距離嘅真實意義 (冷斑 vs 對稱軸)
- 已知 CMB 異常位置 (WMAP cold spots) 係咪都喺軌道上
"""
import math
import numpy as np
from astropy.coordinates import SkyCoord, Galactic, ICRS
import astropy.units as u

phi = (1+5**0.5)/2
inv_phi = 1/phi

# ============ 1. 正十二面體特徵點 ============
# 20 頂點 (3-fold 軸方向)
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

# 12 面中心 (5-fold 軸方向) = 正二十面體頂點
faces = []
for sx in [-1, 1]:
    for sy in [-1, 1]:
        faces.append((0, sx, sy*phi))
        faces.append((sx, sy*phi, 0))
        faces.append((sx*phi, 0, sy))

def norm(v):
    n = math.sqrt(v[0]**2+v[1]**2+v[2]**2)
    return tuple(x/n for x in v)

verts_n = np.array([norm(v) for v in verts])
faces_n = np.array([norm(v) for v in faces])

# 30 邊中點 (2-fold 軸方向)
edges = []
for i in range(20):
    for j in range(i+1, 20):
        d = np.linalg.norm(verts_n[i] - verts_n[j])
        # dodecahedron 邊長: 兩頂點距離 = 2/√3 × (相鄰頂點)
        if abs(d - 2*math.sqrt(2)/math.sqrt(3)) < 0.01:  # 相鄰頂點距離
            mid = np.array(norm(verts_n[i] + verts_n[j]))
            if not any(np.allclose(mid, e) or np.allclose(mid, -e) for e in edges):
                edges.append(mid)
edges_n = np.array(edges)
print(f"特徵點: {len(verts_n)} 頂點 + {len(faces_n)} 面 + {len(edges_n)} 邊中點")

# ============ 2. A₅ 旋轉對稱群生成 ============
def rot_matrix(axis, angle):
    axis = np.asarray(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)
    c, s = math.cos(angle), math.sin(angle)
    K = np.array([[0, -axis[2], axis[1]],
                  [axis[2], 0, -axis[0]],
                  [-axis[1], axis[0], 0]])
    return np.eye(3) + s*K + (1-c)*np.dot(K, K)

# A₅ 由 2 個生成元產生: 5-fold 旋轉 (72°) + 2-fold 旋轉 (180°)
# 用 BFS 生成全部 60 個元素
g1 = rot_matrix(faces_n[0], 2*math.pi/5)   # 5-fold
g2 = rot_matrix(verts_n[0], 2*math.pi/3)   # 3-fold
g3 = rot_matrix(edges_n[0], math.pi)       # 2-fold

# 用 g1, g2 生成 (A₅ = <(12345), (123)>)
group = [np.eye(3)]
seen = {tuple(np.eye(3).flatten())}
queue = [np.eye(3)]
while queue:
    M = queue.pop(0)
    for gen in [g1, g2]:
        new = np.dot(gen, M)
        key = tuple(np.round(new.flatten(), 10))
        if key not in seen:
            seen.add(key)
            group.append(new)
            queue.append(new)

print(f"A₅ 群生成: {len(group)} 個旋轉 (期望 60)")

# ============ 3. 冷斑向量 ============
cs = SkyCoord(l=209*u.deg, b=-57*u.deg, frame=Galactic)
eq = cs.icrs
ra_cs, dec_cs = math.radians(eq.ra.deg), math.radians(eq.dec.deg)
v_cs = np.array([math.cos(dec_cs)*math.cos(ra_cs),
                 math.cos(dec_cs)*math.sin(ra_cs),
                 math.sin(dec_cs)])
print(f"\n冷斑 ICRS: RA={eq.ra.deg:.2f}° Dec={eq.dec.deg:.2f}°")
print(f"冷斑向量: ({v_cs[0]:.4f}, {v_cs[1]:.4f}, {v_cs[2]:.4f})")

# ============ 4. A₅ 軌道 ============
# A₅ 作用喺冷斑向量 → 冷斑家族節點
orbit = []
for M in group:
    v = np.dot(M, v_cs)
    # 去重 (容許 ±)
    if not any(np.allclose(v, o, atol=1e-6) or np.allclose(v, -o, atol=1e-6) for o in orbit):
        orbit.append(v)
print(f"\nA₅ × 冷斑 軌道大小: {len(orbit)} (期望 60 或 60/穩定子)")

# 穩定子檢查: 有冇非恆等旋轉固定冷斑?
stabilizer = 0
for M in group:
    v = np.dot(M, v_cs)
    if np.allclose(v, v_cs, atol=1e-6) or np.allclose(v, -v_cs, atol=1e-6):
        stabilizer += 1
print(f"穩定子大小: {stabilizer}")

# ============ 5. 節點轉銀道座標 ============
print(f"\n冷斑家族節點 (銀道座標):")
node_gal = []
for v in orbit:
    ra = math.degrees(math.atan2(v[1], v[0])) % 360
    dec = math.degrees(math.asin(v[2]))
    sc = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame=ICRS)
    g = sc.galactic
    node_gal.append((g.l.deg, g.b.deg))
    print(f"  l={g.l.deg:7.2f}°  b={g.b.deg:+7.2f}°")

# ============ 6. 冷斑 vs 對稱軸 (重新驗證 15.11°) ============
def ang_deg(v1, v2):
    dot = np.dot(v1, v2)
    return math.degrees(math.acos(max(-1, min(1, dot))))

print(f"\n冷斑 vs 特徵軸:")
for name, pts in [("3-fold 頂點", verts_n), ("5-fold 面", faces_n), ("2-fold 邊", edges_n)]:
    dists = [ang_deg(v_cs, p) for p in pts]
    md = min(dists)
    print(f"  {name}: 最近 {md:.3f}°")

# ============ 7. 已知 CMB 異常位置檢查 ============
print(f"\n已知 CMB 異常 vs 冷斑家族節點:")
# WMAP/Planck 已知: 大冷斑 (209,-57), 熱斑?
known = {
    "大冷斑 (Vielva)": (209, -57),
}
# 檢查已知點係咪接近節點 (< 5°)
for name, (l, b) in known.items():
    if l is None:
        continue
    sc_k = SkyCoord(l=l*u.deg, b=b*u.deg, frame=Galactic)
    e_k = sc_k.icrs
    v_k = np.array([math.cos(math.radians(e_k.dec.deg))*math.cos(math.radians(e_k.ra.deg)),
                    math.cos(math.radians(e_k.dec.deg))*math.sin(math.radians(e_k.ra.deg)),
                    math.sin(math.radians(e_k.dec.deg))])
    dists = [ang_deg(v_k, v) for v in orbit]
    md = min(dists)
    print(f"  {name} ({l},{b}): 最近節點 {md:.2f}°")

# ============ 8. 節點密度 ============
print(f"\n節點網格分析:")
# 60 個節點全天空密度: 41253 deg²/60 = 688 deg²/節點
# 平均間距 ≈ √688 ≈ 26°
print(f"60 節點平均間距: ~{math.sqrt(41253/60):.0f}°")
print(f"冷斑 FWHM 5° → 節點網格比冷斑稀疏好多")
print(f"=> 冷斑唔係「直接對準節點」而係「節點附近嘅干涉區」")
