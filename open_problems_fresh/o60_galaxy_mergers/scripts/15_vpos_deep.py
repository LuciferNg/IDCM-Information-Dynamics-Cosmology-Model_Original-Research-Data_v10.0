#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O60b VPOS 深層幾何 — 同 K_Chain 結構軸嘅關係
================================================
檢查:
1. VPOS 平面 vs 銀河盤 (傾角 -13.5°?)
2. VPOS 法向量 vs A₅ 冷斑結構軸
3. VPOS 法向量 vs 其他 IDCM 結構方向

A₅ 冷斑: (l,b) = (209°, -57°) (銀河座標)
VPOS 法向量: (l,b) = (188.5°, -13.5°)
"""
import numpy as np

def gal_to_vec(l, b):
    l, b = np.radians(l), np.radians(b)
    return np.array([np.cos(b)*np.cos(l), np.cos(b)*np.sin(l), np.sin(b)])

def angle(v1, v2):
    return np.degrees(np.arccos(np.clip(np.dot(v1, v2), -1, 1)))

print("=" * 72)
print("O60b: VPOS 深層幾何 vs IDCM 結構軸")
print("=" * 72)

v_vpos = gal_to_vec(188.5, -13.5)
v_disk = np.array([0, 0, 1])  # 銀河盤法向量
v_m31 = gal_to_vec(121.17, -21.57)
v_coldspot = gal_to_vec(209, -57)

print(f"[1] VPOS 法向量 (l=188.5°, b=-13.5°):")
print(f"    銀河座標向量: ({v_vpos[0]:.4f}, {v_vpos[1]:.4f}, {v_vpos[2]:.4f})")

# 1. VPOS vs 銀河盤
a1 = angle(v_vpos, v_disk)
print(f"\n[2] VPOS 法向量 vs 銀河盤法向量: {a1:.1f}°")
print(f"    → VPOS 平面同銀河盤傾角 = {90 - a1:.1f}° (如果 a1≈90 → 垂直盤)")
print(f"    → 實際: VPOS 平面同銀河盤夾角 {a1-90:.1f}° (接近平行盤!)")

# 2. VPOS vs 冷斑
a2 = angle(v_vpos, v_coldspot)
print(f"\n[3] VPOS 法向量 vs 冷斑方向 (209°, -57°): {a2:.1f}°")
print(f"    90° - 偏差: 如果垂直 → 90°")

# 3. VPOS 平面內嘅 M31?
# M31 投影到 VPOS 平面
proj = v_m31 - np.dot(v_m31, v_vpos) * v_vpos
print(f"\n[4] M31 喺 VPOS 平面嘅投影:")
print(f"    M31 距 VPOS 平面 = {90-angle(v_m31, v_vpos):.1f}° (0 = 喺平面內)")
print(f"    → M31 唔喺 VPOS 平面內 ({90-angle(v_m31, v_vpos):.1f}° 離開)")

# 4. VPOS 法向量 vs 已知結構
print(f"\n[5] VPOS 法向量同其他軸比較:")
axes = {
    "銀河盤法向量": v_disk,
    "M31 方向": v_m31,
    "冷斑方向": v_coldspot,
    "北銀極": gal_to_vec(0, 90),
}
for name, v in axes.items():
    print(f"    {name:14s}: 夾角 {angle(v_vpos, v):6.1f}°")

# 5. VPOS 平面內嘅特殊方向
# 搵 VPOS 平面內同冷斑/銀河中心最近嘅方向
print(f"\n[6] VPOS 平面內嘅軸:")
# 平面基向量
e1 = np.cross(v_vpos, v_disk)
e1 = e1 / np.linalg.norm(e1)
e2 = np.cross(v_vpos, e1)
e2 = e2 / np.linalg.norm(e2)
print(f"    平面基向量 e1: ({e1[0]:.4f}, {e1[1]:.4f}, {e1[2]:.4f})")
print(f"    平面基向量 e2: ({e2[0]:.4f}, {e2[1]:.4f}, {e2[2]:.4f})")

# 衛星喺平面內嘅方位角分佈 (定性)
print(f"""
[7] 物理詮釋:
    VPOS 平面幾乎同銀河盤平行 (傾角 -13.5°)
    → 衛星系平面 = 銀河盤嘅「延伸」?
    → 定係兩者都係同一個更大結構 (K_Chain 投影平面) 嘅部分?
    
    如果 VPOS = K_Chain 投影平面:
    → 銀河盤都應該喺同一平面 (係!)
    → M31 盤都應該喺同一平面? (M31 盤傾角 ~77° — 唔同!)
    → M31 衛星平面 (GPOA) 呢? (同 VPOS 唔同方向!)
    → ⚠️ MW 同 M31 嘅衛星平面唔對齊 — 呢個係已知觀測
    → 如果兩者都係「K_Chain 投影」, 點解唔對齊?
    → 除非: 每個星系有自己的投影軸 (局部投影)?

    🔴 結論: VPOS 同銀河盤接近平行係有趣嘅, 但
    MW/M31 衛星平面不對齊 → 唔似「單一 K_Chain 投影軸」
    → 需要每個星系局部投影機制 (未推導)
""")

# 8. 定量: VPOS 傾角同盤
print(f"[8] VPOS 傾角 (-13.5°) 有結構意義?")
print(f"    13.5° ≈ 44/3.26? 冇直接結構")
print(f"    13.5° = 27°/2? 27 = 3³ = N_gen³ (O13!)")
print(f"    27/2 = 13.5 → VPOS 傾角 = N_gen³/2 度?")
print(f"    ⚠️ 可能係巧合 — 但 27 = 3³ 係 IDCM 結構 (isospin)")
print(f"    檢查: 冷斑緯度 -57° = -(44+13) = -(44+F₇) (已知)")
print(f"    VPOS b = -13.5° = -27/2 → 27 = 3³?")
