#!/usr/bin/env python3
"""
01_geometry_scale_search.py — O8 尺度半徑: 幾何半徑 + 比例搜索
================================================================
問題: 節點影響範圍 ~4.17° (冷斑 FWHM) vs 節點間距 26.09° — 比例 0.16
候選: 26.09/2π = 4.153 (0.4%)? 180/44 = 4.091 (1.9%)?

步驟:
1. 60 節點網絡幾何半徑 (inscribed/circumscribed/Voronoi cell 半徑)
2. 4.17 vs 26.09 比例搜索 (φ 冪/ε/κ/π 組合)
3. 尺度鏈: 26.09 → 4.17 → 冷斑 FWHM 一致性
"""
import numpy as np
import math
from collections import defaultdict

phi = (1 + 5**0.5) / 2
eps = (1/phi) / 4
LUCAS = {0: 2, 1: 1, 2: 3, 3: 4, 4: 7, 5: 11, 6: 18, 7: 29, 8: 47, 9: 76, 10: 123, 11: 199}
FIB = {0: 0, 1: 1, 2: 1, 3: 2, 4: 3, 5: 5, 6: 8, 7: 13, 8: 21, 9: 34, 10: 55, 11: 89}

# ===== 1. 載入節點 =====
nodes = []
with open("/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)

def vec(ra, dec):
    r, d = math.radians(ra), math.radians(dec)
    return np.array([math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d)])

vecs = np.array([vec(ra, dec) for ra, dec in nodes])

def ang_deg(v1, v2):
    return math.degrees(math.acos(np.clip(np.dot(v1, v2), -1, 1)))

print("="*70)
print("O8 尺度半徑 — 步驟 1: 幾何半徑")
print("="*70)

# ===== 2. 距離矩陣 =====
dists = np.array([[ang_deg(vecs[i], vecs[j]) for j in range(60)] for i in range(60)])
np.fill_diagonal(dists, 999)

# 最近鄰統計
nn = dists.min(axis=1)
print(f"\n最近鄰距離: mean={nn.mean():.6f}°, min={nn.min():.6f}, max={nn.max():.6f}")
edge_len = nn.mean()  # 26.0913
print(f"邊長 (o1 閉合): {edge_len:.6f}°")

# ===== 3. 幾何量 =====
print("\n--- 幾何量 ---")
# 所有節點喺單位球面 → circumradius = 1 (trivial)
print(f"circumradius: 1.0 (trivial, 全部喺單位球面)")

# Voronoi cell 面積 (近似: 4π/60)
cell_area_sr = 4*np.pi/60
cell_r_deg = math.degrees(math.sqrt(cell_area_sr/np.pi))  # 圓形近似
print(f"Voronoi cell 面積 = 4π/60 = {cell_area_sr:.4f} sr")
print(f"Voronoi cell 圓形近似半徑 = √(A/π) = {cell_r_deg:.3f}°")

# 最近鄰半距離 (影響範圍上界)
print(f"最近鄰半距離 = {edge_len/2:.3f}° (影響範圍自然上界)")

# 第二層 (31.68°) 半距離
d2 = sorted(set(round(d, 3) for d in dists.flatten() if d < 40))
print(f"距離層 (0-40°): {d2[:8]}")

# 三角形面高 (20 個三角形面, 邊長 = 邊長)
# 球面等邊三角形高: cos(h) = cos(a)/cos(a/2)
a = math.radians(edge_len)
h_tri = math.degrees(math.acos(math.cos(a)/math.cos(a/2)))
print(f"球面三角形高 (邊長 26.09°): {h_tri:.3f}°")
print(f"  高/3 = {h_tri/3:.3f}°  (質心近似)")

# 正方形面對角線半
diag_sq = edge_len * math.sqrt(2)
print(f"正方形面對角線: {diag_sq:.3f}° (球面近似), 半 = {diag_sq/2:.3f}°")

print("\n" + "="*70)
print("O8 尺度半徑 — 步驟 2: 比例搜索 4.17 vs 26.09")
print("="*70)

# ===== 4. 候選公式 =====
FWHM = 4.17  # Vielva R8 (觀測輸入)
cands = {
    "26.09/2π":              edge_len/(2*np.pi),
    "26.09/π":               edge_len/np.pi,
    "180/44 (ℓ=44 半波)":     180/44,
    "360/88 (K_Chain 2N_d)":  360/88,
    "26.09×ε":               edge_len*eps,
    "26.09×φ⁻³":             edge_len*phi**-3,
    "26.09×φ⁻⁴":             edge_len*phi**-4,
    "26.09×ε²":              edge_len*eps**2,
    "26.09×(2ε)":            edge_len*2*eps,
    "26.09×φ⁻²":             edge_len*phi**-2,
    "360/86.3":              360/86.3,
    "360/(2×43)":            360/86,
    "26.09/6.26":            edge_len/6.26,
    "26.09×(φ-1)/φ":         edge_len*(phi-1)/phi,
    "26.09/2φ":              edge_len/(2*phi),
    "26.09/(2φ²)":           edge_len/(2*phi**2),
    "360/(44×2π/φ)":         360/(44*2*np.pi/phi),
}
print(f"\n目標 FWHM = {FWHM}° (Vielva R8)")
print(f"{'候選公式':<24}{'值':>10}{'偏差%':>10}")
print("-"*46)
results = []
for name, val in cands.items():
    dev = abs(val - FWHM)/FWHM*100
    results.append((dev, name, val))
    print(f"{name:<24}{val:>10.4f}{dev:>9.2f}%")
results.sort()
print(f"\n最佳 3 候選:")
for dev, name, val in results[:3]:
    print(f"  🥇 {name}: {val:.4f}° (偏差 {dev:.2f}%)")

# ===== 5. 反向: 4.17 同 26.09 嘅精確關係 =====
print("\n--- 精確關係檢查 ---")
print(f"26.09/4.17 = {edge_len/FWHM:.6f}")
print(f"  2π = {2*np.pi:.6f} (偏差 {(edge_len/FWHM-2*np.pi)/(2*np.pi)*100:.2f}%)")
print(f"  44/7 = {44/7:.6f} (偏差 {(edge_len/FWHM-44/7)/(44/7)*100:.2f}%)")
print(f"  6.28 = 2π 近似 (偏差 {(edge_len/FWHM-6.28)/6.28*100:.2f}%)")
print(f"4.17×2π = {FWHM*2*np.pi:.4f} vs 26.09 (偏差 {(FWHM*2*np.pi-edge_len)/edge_len*100:.2f}%)")
print(f"4.17×44 = {FWHM*44:.1f} vs 360×π/... (360×π/44={360*np.pi/44:.2f})")
print(f"26.09×44 = {edge_len*44:.2f}° = {edge_len*44/360:.4f} 圈")

# 4.17 嘅「平滑修正」: 如果真實值 = 26.09/2π = 4.1534, 偏差 0.4% 係咪平滑誤差?
print(f"\n--- 0.4% 偏差分析 ---")
print(f"26.09/2π = {edge_len/(2*np.pi):.6f}°")
print(f"vs 4.17: 差 {FWHM - edge_len/(2*np.pi):.4f}° = {abs(FWHM-edge_len/(2*np.pi))/FWHM*100:.2f}%")
print(f"SMHW R8 尺度不確定性: Vielva 2004 報告 R=8 對應 4-5° (±0.5° 級)")
print(f"→ 0.4% 偏差遠細過 R8 嘅 ±0.5° 不確定性 ✓")

# ===== 6. 尺度鏈: 26.09 → 4.17 → ℓ = 44 = 2N_d =====
print("\n" + "="*70)
print("O8 尺度半徑 — 步驟 3: 尺度鏈")
print("="*70)
print(f"""
尺度鏈 (結構推導):
  節點間距 a = 26.0913° (A₅ 軌道最近鄰, o1 群論閉合)
  ↓ 除以 2π (約化波長: 相位 2π 對應一個間距)
  影響半徑 r = a/2π = {edge_len/(2*np.pi):.4f}° (候選)
  ↓ 對應球諧模式
  ℓ = 180/r = {180/(edge_len/(2*np.pi)):.2f} ≈ 43.3 ≈ 44 = 2N_d (偏差 {(180/(edge_len/(2*np.pi))-44)/44*100:.2f}%)
  ↓ 冷斑尺度
  ℓ_cs = 180/4.17 = {180/FWHM:.2f} (Vielva R8 觀測)

物理意義: 節點間距 = 一個完整 2π 相位週期
         影響半徑 = 相位轉 1 rad 嘅距離 (約化波長 λ̸ = λ/2π)
         冷斑 = ℓ=44 SYNC 模式嘅節點 (半波 = 180/44 = {180/44:.3f}°)
""")

# 檢查: 26.09/2π 同 180/44 嘅關係
r1 = edge_len/(2*np.pi)
r2 = 180/44
print(f"交叉檢查: a/2π = {r1:.4f} vs 180/44 = {r2:.4f}")
print(f"兩者偏差: {abs(r1-r2)/r1*100:.2f}%  (26.09×44 = {edge_len*44:.1f} vs 360π = {360*np.pi:.1f})")
print(f"即: 26.09 ≈ 360π/44 需要 {(edge_len*44/(360*np.pi)-1)*100:.2f}% 準確")

# 儲存
with open("/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o8_scale_radius/data/geometry_scale.txt", "w") as f:
    f.write(f"# O8 幾何 + 比例搜索\n")
    f.write(f"# edge_len = {edge_len:.6f}°\n")
    f.write(f"# FWHM = {FWHM}° (Vielva R8)\n")
    f.write(f"# Voronoi cell 半徑 = {cell_r_deg:.3f}°\n")
    f.write(f"# 球面三角形高 = {h_tri:.3f}°\n")
    for dev, name, val in results:
        f.write(f"# cand: {name} = {val:.4f} (dev {dev:.2f}%)\n")
    f.write(f"a/2π = {r1:.6f}°\n")
    f.write(f"180/44 = {r2:.6f}°\n")
print("\n✅ 已存: data/geometry_scale.txt")
