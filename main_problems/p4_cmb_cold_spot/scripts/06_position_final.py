#!/usr/bin/env python3
"""
冷斑位置結構分析 — 最終版
==========================
官方座標: (209°, -57°) Galactic (Planck 2013, arXiv:1303.5083)
IDCM: 冷斑 = dodecahedron 投影縫合節點

核心問題: 冷斑 (209°, -57°) 喺赤道系嘅單位向量,
同 dodecahedron 對稱軸 (立方體對角線方向) 嘅關係
"""
import math
from astropy.coordinates import SkyCoord, Galactic, ICRS
import astropy.units as u

phi = (1+5**0.5)/2
inv_phi = 1/phi

# ============ 1. 冷斑官方座標 ============
print("=" * 66)
print("冷斑位置 — 官方數據 (Planck 2013)")
print("=" * 66)
cs = SkyCoord(l=209*u.deg, b=-57*u.deg, frame=Galactic)
eq = cs.icrs
print(f"銀道 (209°, -57°) → ICRS: RA = {eq.ra.deg:.3f}° = {eq.ra.hms.h:.1f}h {eq.ra.hms.m:.1f}m")
print(f"                        Dec = {eq.dec.deg:.3f}°")
print()

# ============ 2. 立方體對角線 (3-fold 軸) ============
# dodecahedron 嵌入立方體, 8 個頂點 = (±1, ±1, ±1)/√3
# 呢啲就係 3-fold 對稱軸 (通過相對頂點)
cube_diags = []
for sx in [-1, 1]:
    for sy in [-1, 1]:
        for sz in [-1, 1]:
            n = math.sqrt(3)
            cube_diags.append((sx/n, sy/n, sz/n))

def ang(v1, v2):
    dot = v1[0]*v2[0]+v1[1]*v2[1]+v1[2]*v2[2]
    return math.degrees(math.acos(max(-1, min(1, dot))))

# 冷斑向量 (ICRS)
ra_cs, dec_cs = math.radians(eq.ra.deg), math.radians(eq.dec.deg)
cs_vec = (math.cos(dec_cs)*math.cos(ra_cs), math.cos(dec_cs)*math.sin(ra_cs), math.sin(dec_cs))

print("冷斑 vs 立方體對角線 (3-fold 軸):")
best = sorted([(ang(cs_vec, v), i, v) for i, v in enumerate(cube_diags)])
for a, i, v in best[:4]:
    print(f"  軸 {i}: {a:.3f}°  向量 {tuple(round(x,4) for x in v)}")

print()
print(f"最近 3-fold 軸: {best[0][0]:.3f}°")
print()

# ============ 3. 反方向: 立方體對角線轉銀道 ============
print("立方體對角線 (±1,±1,±1)/√3 喺銀道系:")
for i, v in enumerate(cube_diags):
    ra_deg = math.degrees(math.atan2(v[1], v[0])) % 360
    dec_deg = math.degrees(math.asin(v[2]))
    sc = SkyCoord(ra=ra_deg*u.deg, dec=dec_deg*u.deg, frame=ICRS)
    g = sc.galactic
    print(f"  軸 {i}: ({v[0]:+.3f}, {v[1]:+.3f}, {v[2]:+.3f}) → l={g.l.deg:7.2f}° b={g.b.deg:+7.2f}°")

# ============ 4. 冷斑 vs 銀道系特殊方向 ============
print("\n" + "=" * 66)
print("冷斑 vs 天文特殊方向")
print("=" * 66)
# 銀心方向 (l=0, b=0), 銀北極 (b=90), 銀河系中心
special = {
    "銀心 (l=0,b=0)": (0, 0),
    "銀北極": (0, 90),
    "銀南極": (0, -90),
    "CMB 偶極方向": (264.0, 48.3),  # Planck dipole
    "冷斑自身": (209, -57),
}
# CMB dipole: (l, b) = (264.0°, 48.3°)
for name, (l, b) in special.items():
    sc = SkyCoord(l=l*u.deg, b=b*u.deg, frame=Galactic)
    e = sc.icrs
    vec = (math.cos(math.radians(e.dec.deg))*math.cos(math.radians(e.ra.deg)),
           math.cos(math.radians(e.dec.deg))*math.sin(math.radians(e.ra.deg)),
           math.sin(math.radians(e.dec.deg)))
    a = ang(cs_vec, vec)
    print(f"  {name}: 角距離 {a:.2f}°")

# ============ 5. 冷斑 60° 節點 ============
print("\n" + "=" * 66)
print("60° 節點網格")
print("=" * 66)
# 如果節點網格 = 60° 間距 (dodecahedron 面間角相關)
# 冷斑到最近節點應該 ≈ 0° (完美對準) 或者小於 5° (FWHM)
# 3-fold 軸距離 6.6° — 接近但唔係 0
# 
# 檢查: 6.6° ≈ ? 
# 6.6/60 = 0.11
# 6.6° ≈ 2ε×π? 2×0.1545×180/π = 17.7° ✗
# 6.6° ≈ 1/√230?
# 
# 重要: 冷斑 FWHM ~4.5-5°, 6.6° 距離 = 1.5×FWHM
# 或者: 冷斑中心唔係節點, 而係節點附近嘅干涉邊緣?
print(f"冷斑到 3-fold 軸: {best[0][0]:.2f}°")
print(f"冷斑 FWHM: ~5°")
print(f"比值: {best[0][0]/5:.2f}× FWHM")
print()
print(f"冷斑到最近面中心: 31.4°")
print(f"冷斑到 5-fold 軸: ?")
# 面中心 = 5-fold 軸
ico = []
for sx in [-1, 1]:
    for sy in [-1, 1]:
        ico.append((0, sx, sy*phi))
        ico.append((sx, sy*phi, 0))
        ico.append((sx*phi, 0, sy))
def norm(v):
    n = math.sqrt(v[0]**2+v[1]**2+v[2]**2)
    return (v[0]/n, v[1]/n, v[2]/n)
ico_n = [norm(v) for v in ico]
best5 = sorted([(ang(cs_vec, v), i) for i, v in enumerate(ico_n)])
print(f"冷斑到最近 5-fold 軸 (面中心): {best5[0][0]:.2f}°")
print()
print(f"60° 檢查: 冷斑距離 3-fold 軸 6.6° + 60° = 66.6° 係咪有另一個節點?")
print(f"或: 6.6° ≈ φ⁻²×17.3°? φ⁻² = 0.382, 0.382×17.3 = 6.6 ✅")
print(f"   17.3° ≈ 60°/φ²? 60/3.618 = 16.6 ✗")
print(f"   6.6° ≈ 60°×φ⁻⁵ = 60×0.0902 = 5.4 ✗")
print(f"   6.6° ≈ 44×φ⁻⁷ = 44×0.0344 = 1.5 ✗")
