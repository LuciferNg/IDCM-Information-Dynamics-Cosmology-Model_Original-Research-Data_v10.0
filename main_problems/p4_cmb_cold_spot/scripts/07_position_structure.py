#!/usr/bin/env python3
"""
冷斑位置 — 15.11° 結構分析
==========================
冷斑 (209°, -57°) → ICRS (RA=48.30°, Dec=-20.44°)
到立方體對角線 (3-fold 軸): 15.11°
到面中心 (5-fold 軸): 22.65°
到銀南極: 33.0°

問題: 15.11° 有咩結構意義?
"""
import math
from astropy.coordinates import SkyCoord, Galactic, ICRS
import astropy.units as u

phi = (1+5**0.5)/2
phi_inv = 1/phi
eps = phi_inv/4
kappa = 1/16

cs = SkyCoord(l=209*u.deg, b=-57*u.deg, frame=Galactic)
eq = cs.icrs
ra_cs, dec_cs = math.radians(eq.ra.deg), math.radians(eq.dec.deg)
cs_vec = (math.cos(dec_cs)*math.cos(ra_cs), math.cos(dec_cs)*math.sin(ra_cs), math.sin(dec_cs))

def ang(v1, v2):
    dot = v1[0]*v2[0]+v1[1]*v2[1]+v1[2]*v2[2]
    return math.degrees(math.acos(max(-1, min(1, dot))))

# ============ 15.11° 結構分解 ============
print("=" * 60)
print("15.11° 結構分解")
print("=" * 60)
target = 15.109

# 候選
cands = {
    "60°/4 = 15": 60/4,
    "44×φ⁻⁶ = 6.9": 44*phi_inv**6,
    "60×φ⁻⁵ = 5.4": 60*phi_inv**5,
    "30×φ⁻² = 11.5": 30*phi_inv**2,
    "18×φ⁻¹ = 11.1": 18*phi_inv,
    "15 = 3×5": 15,
    "2π/24 = 15": 360/24,
    "360/24 = 15": 360/24,
    "360/44×1.846": 360/44*1.846,
    "90×φ⁻⁴ = 13.1": 90*phi_inv**4,
    "arctan(1/4) = 14.04": math.degrees(math.atan(1/4)),
    "arctan(1/φ²) = 20.9": math.degrees(math.atan(1/phi**2)),
    "arcsin(1/4) = 14.48": math.degrees(math.asin(1/4)),
    "arcsin(κ) = 3.58": math.degrees(math.asin(kappa)),
    "arcsin(2ε) = 18.0": math.degrees(math.asin(2*eps)),
    "π/12 = 15": 180/12,
    "15 = L₅+L₃+1?": 11+4,
    "15 = L₄+L₃+L₂?": 7+4+3,
    "15 = 3×F₅": 3*5,
    "15 = F₄+F₅+F₆?": 3+5+8,
}
print(f"目標: {target:.3f}°")
for name, val in cands.items():
    dev = abs(val-target)/target*100
    mark = "✅" if dev < 1 else ("🟡" if dev < 5 else " ")
    print(f"  {mark} {name:22s} = {val:8.3f}°  偏差 {dev:5.1f}%")

# ============ 15.11 = 60/4 = 15 (dodecahedron 面間角/4?) ============
print()
print("✅ 最簡單: 15° = 60°/4 = 2π/24")
print("  60° = dodecahedron 投影特徵角")
print("  4 = B (MERA branching) 或 N_d/11")
print("  15° = 一個「節點單元」嘅角尺度")
print()

# ============ 冷斑 = 節點網格邊界 ============
print("=" * 60)
print("冷斑 vs dodecahedron 邊緣 (edge)")
print("=" * 60)
# dodecahedron 邊緣中點 = ?
# 正十二面體: 30 條邊, 邊中點 = ?
# 邊中點係 2-fold 軸方向 (15 個)
# 2-fold 軸 = 邊中點 = 兩個面中心同兩個頂點嘅中點
# 可以用面中心加頂點平均?
# 
# 更簡單: dodecahedron 邊緣通過嘅大圓
# 或者: 冷斑位置 (209°, -57°) 嘅銀道緯度 -57° 
# -57° ≈ -60° + 3°! 
# 60° 節點網格 + 3° 偏差?
print(f"冷斑 b = -57°, -60° + 3° = -57° ✅!")
print(f"  60° = dodecahedron 特徵角")
print(f"  3° = ? 3° = 360/120, 或 1.5°×2")
print(f"  或者 b=-57° ≈ -60°×(1-ε/3)? 60×0.9485 = 56.9 ✗")
print(f"  57 = 3×19? 19 = L₇-10? L₇=29 ✗")
print(f"  57 = 44+13? 13 = F₇ ✅")
print(f"  l=209° = 180°+29° = 180+L₇? L₇ = 29 ✅!")
print()
print(f"銀道座標結構:")
print(f"  l = 209° = 180° + 29° = 180 + L₇ (Lucas!)")
print(f"  b = -57° = -(44° + 13°) = -(44 + F₇) (K_Chain + Fibonacci!)")
print(f"  l+b = 209-57 = 152° = ?")
print(f"  209 mod 60 = 29 = L₇ ✅")
print(f"  -57 mod 60 = 3")
print()

# ============ 209 = 180+29, 29 = L₇ ============
print("=" * 60)
print("銀道座標結構分解")
print("=" * 60)
# Lucas: L₀=2, L₁=1, L₂=3, L₃=4, L₄=7, L₅=11, L₆=18, L₇=29, L₈=47, L₉=76
L = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76]
# Fibonacci: F₀=0, F₁=1, F₂=1, F₃=2, F₄=3, F₅=5, F₆=8, F₇=13, F₈=21, F₉=34, F₁₀=55, F₁₁=89
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
print(f"l = 209° = 180° + 29° = 180° + L₇")
print(f"b = -57° = -(44° + 13°) = -(N_d + F₇)")
print()
print(f"檢查其他組合:")
# 209 嘅結構分解
for a in range(0, 10):
    for b_ in range(0, 10):
        if L[a] + L[b_] == 29:
            print(f"  29 = L_{a} + L_{b_} = {L[a]}+{L[b_]}")
        if L[a] + F[b_] == 29:
            print(f"  29 = L_{a} + F_{b_} = {L[a]}+{F[b_]}")
        if F[a] + F[b_] == 29:
            print(f"  29 = F_{a} + F_{b_}")
# 57 嘅分解
for a in range(0, 10):
    for b_ in range(0, 10):
        if L[a] + L[b_] == 57:
            print(f"  57 = L_{a} + L_{b_} = {L[a]}+{L[b_]}")
        if L[a] + F[b_] == 57:
            print(f"  57 = L_{a} + F_{b_} = {L[a]}+{F[b_]}")
        if F[a] + F[b_] == 57:
            print(f"  57 = F_{a} + F_{b_}")
print()
print(f"最乾淨: l = 180+L₇, b = -(44+F₇)")
print(f"  180 = 半圓 (對稱), 44 = N_d, L₇=29, F₇=13")
print(f"  → 冷斑 = 半圓邊界 × K_Chain/Lucas/Fibonacci 節點")
