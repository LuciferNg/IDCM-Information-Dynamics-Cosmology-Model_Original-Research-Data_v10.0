#!/usr/bin/env python3
"""
冷斑開放位 3+4: 熱斑等級 + 冷熱交替結構模擬
============================================
IDCM 節點 = 相位干涉消長節點: 冷熱交替
- 大冷斑 (209,-57) = 冷節點 (相位對消)
- 對應熱斑應該喺對跖點/對稱位置

等級結構 (Fibonacci):
- RMS = ε⁵/8 (1×)
- 冷斑 = 5×RMS = F₅×ε⁵/8
- 熱斑 = 8×RMS = F₆×ε⁵/8?
- 更大 = 13×RMS = F₇×ε⁵/8?

驗證: 冷斑 -150μK 係咪對應 F₅ 等級?
"""
import numpy as np
import math

phi = (1+5**0.5)/2
phi_inv = 1/phi
eps = phi_inv/4
kappa = 1/16

RMS = eps**5/8
T_CMB = 2.7284

print("=" * 66)
print("熱斑/冷斑 Fibonacci 等級結構")
print("=" * 66)

# 等級
levels = {
    "RMS (1×)": 1,
    "F₃=2": 2,
    "F₄=3": 3,
    "F₅=5 (冷斑)": 5,
    "F₆=8 (熱斑?)": 8,
    "F₇=13": 13,
    "F₈=21": 21,
}
print(f"\n{'等級':20s} {'×RMS':>5s} {'ΔT/T':>12s} {'ΔT μK':>10s}")
print("-" * 55)
for name, mult in levels.items():
    val = mult * RMS
    dT = val * T_CMB * 1e6
    print(f"  {name:18s} {mult:5.1f} {val:12.4e} {dT:9.1f} μK")

print()
print("觀測對比:")
print(f"  CMB 冷斑: ΔT ≈ -150 μK → ΔT/T = 5.50e-5 = {5.50e-5/RMS:.1f}× RMS")
print(f"  = F₅ = 5 ✅ (Fibonacci 等級)")
print()

# 其他已知 CMB 異常 (Planck 2015 paper XXIII):
# - 冷斑 -150μK
# - 最大熱斑? 
# - WMAP 熱斑位置?
print("熱斑候選 (文獻):")
print("  WMAP 最大熱斑 (Vielva 2007): 喺 (l,b) ≈ (205°, -30°)?")
print("  → 等我搵官方數據核對")

# ============ 冷熱交替結構 ============
print("\n" + "=" * 66)
print("冷熱交替結構")
print("=" * 66)
# IDCM 節點網格: 60 個節點, 一半冷一半熱?
# 大冷斑 (209,-57) 係冷節點
# 對跖點 (29, +57) 應該係熱節點 (對稱)
# A₅ 群係 60 個旋轉 (保向), 唔包含反演
# 所以對跖點唔一定喺軌道上!
# 
# 檢查: 對跖點 (209+180=29, +57) 喺唔喺 A₅ 軌道?
from astropy.coordinates import SkyCoord, Galactic, ICRS
import astropy.units as u

cs_antipode = SkyCoord(l=(209+180)%360*u.deg, b=57*u.deg, frame=Galactic)
eq_ant = cs_antipode.icrs
print(f"冷斑對跖點: (29°, +57°) → ICRS RA={eq_ant.ra.deg:.2f}° Dec={eq_ant.dec.deg:.2f}°")

# 讀節點清單
nodes = []
with open("data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))

# 對跖點到最近節點
ra_ant, dec_ant = eq_ant.ra.deg, eq_ant.dec.deg
v_ant = np.array([math.cos(math.radians(dec_ant))*math.cos(math.radians(ra_ant)),
                  math.cos(math.radians(dec_ant))*math.sin(math.radians(ra_ant)),
                  math.sin(math.radians(dec_ant))])

def ang_deg(v1, v2):
    dot = np.dot(v1, v2)
    return math.degrees(math.acos(max(-1, min(1, dot))))

best_ant = None
for ra, dec in nodes:
    v = np.array([math.cos(math.radians(dec))*math.cos(math.radians(ra)),
                  math.cos(math.radians(dec))*math.sin(math.radians(ra)),
                  math.sin(math.radians(dec))])
    a = ang_deg(v_ant, v)
    if best_ant is None or a < best_ant[0]:
        best_ant = (a, ra, dec)
print(f"對跖點最近節點: {best_ant[0]:.2f}° (RA={best_ant[1]:.1f}, Dec={best_ant[2]:.1f})")

# 冷斑自身到最近節點 (應該係 0)
v_cs = np.array([0.6234, 0.6996, -0.3492])
best_cs = None
for ra, dec in nodes:
    v = np.array([math.cos(math.radians(dec))*math.cos(math.radians(ra)),
                  math.cos(math.radians(dec))*math.sin(math.radians(ra)),
                  math.sin(math.radians(dec))])
    a = ang_deg(v_cs, v)
    if best_cs is None or a < best_cs[0]:
        best_cs = (a, ra, dec)
print(f"冷斑最近節點: {best_cs[0]:.4f}° (RA={best_cs[1]:.1f}, Dec={best_cs[2]:.1f})")

# 冷熱交替: 邊啲節點應該係熱? (對稱節點)
print()
print("冷熱交替機制:")
print("  如果冷斑 (209,-57) = 冷節點 (相位 0)")
print("  節點網格 = 60 個相位點")
print("  冷熱由相位決定: 相位 0 = 冷, 相位 π = 熱")
print("  A₅ 群旋轉唔改變「相位」→ 點判斷邊個節點冷熱?")
print()
print("  可能: 節點符號 = ± 交替 (chirality)")
print("  或: 符號由投影縫合方向決定")
print("  或: 最冷節點 = 冷斑 (觀測), 其他節點按 |ΔT| 排序")
