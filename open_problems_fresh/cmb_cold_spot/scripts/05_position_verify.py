#!/usr/bin/env python3
"""astropy 核對冷斑座標 + dodecahedron 節點分析"""
import math
from astropy.coordinates import SkyCoord, Galactic, FK5, ICRS
import astropy.units as u

print("=" * 66)
print("冷斑座標 — astropy 核對")
print("=" * 66)

# 冷斑文獻座標: (l, b) = (209°, -57°) Galactic
c = SkyCoord(l=209*u.deg, b=-57*u.deg, frame=Galactic)
eq = c.icrs
print(f"\n冷斑銀道 (209°, -57°)")
print(f"  → ICRS: RA = {eq.ra.deg:.3f}° = {eq.ra.hms.h:.1f}h {eq.ra.hms.m:.1f}m {eq.ra.hms.s:.1f}s")
print(f"           Dec = {eq.dec.deg:.3f}°")
print(f"  文獻: RA ≈ 3.53h (52.9°), Dec ≈ -38.5° (?)")

# 冷斑實際文獻值 (Planck 2013/2015, arXiv:1303.5083 / 1506.06595):
# CMB Cold Spot 中心: (l, b) = (209.5°, -57.0°) 或 (RA, Dec) = (52.4°, -38.2°)?
# 試另一個銀道值
print("\n銀道 → 赤道對照:")
test_points = [
    (209.0, -57.0, "文獻銀道"),
    (209.5, -57.0, "Planck 2013"),
    (208.8, -57.4, "WMAP"),
]
for l, b, name in test_points:
    cc = SkyCoord(l=l*u.deg, b=b*u.deg, frame=Galactic)
    e = cc.icrs
    print(f"  ({l}, {b}) [{name}] → RA={e.ra.deg:.2f}° Dec={e.dec.deg:.2f}°")

# 反方向: 文獻赤道 (RA=52.4°, Dec=-38.2°) → 銀道?
print("\n赤道 → 銀道:")
for ra, dec, name in [(52.4, -38.2, "文獻赤道"), (52.9, -38.5, "另一文獻")]:
    cc = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame=ICRS)
    g = cc.galactic
    print(f"  RA={ra}° Dec={dec}° [{name}] → l={g.l.deg:.2f}° b={g.b.deg:.2f}°")

# ============ dodecahedron 節點 vs 冷斑 ============
print("\n" + "=" * 66)
print("dodecahedron 節點分析")
print("=" * 66)

phi = (1+5**0.5)/2
inv_phi = 1/phi

# 正十二面體 20 頂點 (unit sphere)
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

def norm(v):
    n = math.sqrt(v[0]**2+v[1]**2+v[2]**2)
    return (v[0]/n, v[1]/n, v[2]/n)

verts_n = [norm(v) for v in verts]

# 正二十面體 12 頂點 (= 正十二面體面中心)
ico = []
for sx in [-1, 1]:
    for sy in [-1, 1]:
        ico.append((0, sx, sy*phi))
        ico.append((sx, sy*phi, 0))
        ico.append((sx*phi, 0, sy))
ico_n = [norm(v) for v in ico]

def ang(v1, v2):
    dot = v1[0]*v2[0]+v1[1]*v2[1]+v1[2]*v2[2]
    return math.degrees(math.acos(max(-1, min(1, dot))))

# 冷斑單位向量 (用文獻赤道 RA=52.4, Dec=-38.2):
ra_cs, dec_cs = math.radians(52.4), math.radians(-38.2)
cs_vec = (math.cos(dec_cs)*math.cos(ra_cs), math.cos(dec_cs)*math.sin(ra_cs), math.sin(dec_cs))

print(f"\n冷斑單位向量 (RA=52.4°, Dec=-38.2°):")
print(f"  ({cs_vec[0]:.4f}, {cs_vec[1]:.4f}, {cs_vec[2]:.4f})")

# 最近 dodecahedron 頂點
best_v = sorted([(ang(cs_vec, v), i) for i, v in enumerate(verts_n)])
print(f"\n最近 dodecahedron 頂點:")
for a, i in best_v[:5]:
    print(f"  頂點 {i}: {a:.2f}°  {verts_n[i]}")

best_f = sorted([(ang(cs_vec, v), i) for i, v in enumerate(ico_n)])
print(f"\n最近面中心 (icosahedron 頂點):")
for a, i in best_f[:5]:
    print(f"  面 {i}: {a:.2f}°  {ico_n[i]}")

# 5-fold 軸 (通過面中心) 同 3-fold 軸 (通過頂點)
print(f"\n對稱軸檢查 (角距離 < 25°):")
for i, v in enumerate(ico_n):
    a = ang(cs_vec, v)
    if a < 25:
        print(f"  5-fold 軸 {i} (面中心): {a:.2f}°")
for i, v in enumerate(verts_n):
    a = ang(cs_vec, v)
    if a < 25:
        print(f"  3-fold 軸 {i} (頂點): {a:.2f}°")

# ============ 60° 節點網格 ============
print(f"\n60° 節點網格測試:")
# 如果冷斑 = 節點, 其他節點應該喺 60° 間距
# 檢查冷斑附近有冇 dodecahedron 特徵喺 60° ± 5°
print(f"冷斑同 dodecahedron 特徵嘅角距離:")
print(f"  最近頂點: {best_v[0][0]:.2f}°")
print(f"  最近面中心: {best_f[0][0]:.2f}°")
print(f"  60° - 最近頂點: {60-best_v[0][0]:.2f}°")
