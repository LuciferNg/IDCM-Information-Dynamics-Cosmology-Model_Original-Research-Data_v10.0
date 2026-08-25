#!/usr/bin/env python3
"""
27_smica_sky_map.py — A₅ 拓撲網格天圖視覺化
=============================================
將 60 節點 + 120 邊 (Rhombicosidodecahedron) 疊加喺 Planck SMICA
5° 平滑全天圖:
- 88 條正常邊 (冷-熱): 青色
- 32 條阻挫邊 (同色): 紅色
- 60 節點: 冷=藍點, 熱=紅點
- 節點 0 (冷斑) + 57 (對徑點): 黃色大星

輸出: data/smica_sky_map.png (全天) + data/smica_coldspot_zoom.png (特寫)
"""
import healpy as hp
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math
from collections import defaultdict, deque
from astropy.coordinates import SkyCoord
import astropy.units as u

print("=" * 66)
print("A₅ 拓撲網格天圖視覺化")
print("=" * 66)

# ============ 1. 載入 SMICA + 5° 平滑 ============
m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)
fwhm_rad = np.radians(4.17)
sigma_rad = fwhm_rad / (2 * np.sqrt(2 * np.log(2)))
m_smooth = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
print(f"SMICA 5° 平滑載入完成 (std={m_smooth.std()*1e6:.1f} μK)")

# ============ 2. 節點 (ICRS → Galactic) ============
nodes = []
with open("data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)

sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = gal.l.deg
b_deg = gal.b.deg

# ICRS 三維向量 (用嚟建圖)
vecs = np.array([np.array([math.cos(math.radians(d))*math.cos(math.radians(r)),
                           math.cos(math.radians(d))*math.sin(math.radians(r)),
                           math.sin(math.radians(d))]) for r, d in nodes])

# 銀道三維向量 (用嚟畫大圓弧)
gal_vecs = np.array([np.array([math.cos(math.radians(b))*math.cos(math.radians(l)),
                               math.cos(math.radians(b))*math.sin(math.radians(l)),
                               math.sin(math.radians(b))]) for l, b in zip(l_deg, b_deg)])

# ============ 3. 建圖 + 錨定著色 ============
adj = defaultdict(set)
edges_list = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j)
            adj[j].add(i)
            edges_list.append((i, j))

color = {}
color[0] = 1
q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in color:
            color[w] = 1 - color[u]
            q.append(w)

frustration = set()
for u, v in edges_list:
    if color[u] == color[v]:
        frustration.add((u, v))

print(f"邊: {len(edges_list)} (正常 {len(edges_list)-len(frustration)}, 阻挫 {len(frustration)})")

# ============ 4. 大圓弧插值 (slerp) ============
def slerp_arc(v1, v2, n=80):
    """球面線性插值: v1 → v2, 返回 (lon[], lat[]) 銀道"""
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)
    omega = math.acos(np.clip(np.dot(v1, v2), -1, 1))
    ts = np.linspace(0, 1, n)
    if omega < 1e-10:
        pts = np.tile(v1, (n, 1))
    else:
        pts = (np.sin((1-ts)[:, None]*omega) * v1 + np.sin(ts[:, None]*omega) * v2) / math.sin(omega)
    lons = np.degrees(np.arctan2(pts[:, 1], pts[:, 0])) % 360
    lats = np.degrees(np.arcsin(np.clip(pts[:, 2], -1, 1)))
    return lons, lats

# ============ 5. 繪圖 ============
# 5.1 全天圖 (Mollweide)
print("繪製全天圖...")
fig = plt.figure(figsize=(20, 12))
hp.mollview(m_smooth, fig=fig, cmap='jet', min=-150e-6, max=150e-6,
            title='A5 Rhombicosidodecahedron Grid on Planck SMICA (5° smoothed)',
            cbar=False, hold=True, notext=True)

# 邊
for u, v in edges_list:
    is_fr = (u, v) in frustration
    lons, lats = slerp_arc(gal_vecs[u], gal_vecs[v])
    hp.projplot(lons, lats, lonlat=True,
                color='red' if is_fr else 'cyan',
                lw=1.5 if is_fr else 0.8,
                alpha=0.9 if is_fr else 0.5)

# 節點
for i in range(60):
    c = 'blue' if color[i] == 1 else 'red'
    hp.projscatter(l_deg[i], b_deg[i], lonlat=True, color=c, marker='o',
                   s=25, edgecolors='white', linewidths=0.3)

# 冷斑 (節點 0) + 對徑點 (節點 57)
hp.projscatter(l_deg[0], b_deg[0], lonlat=True, color='yellow', marker='*',
               s=600, edgecolors='black', linewidths=1.5, zorder=10)
hp.projscatter(l_deg[57], b_deg[57], lonlat=True, color='yellow', marker='*',
               s=400, edgecolors='black', linewidths=1.2, zorder=10)

# 銀河遮罩線 |b|=20°
hp.projplot([0, 360], [20, 20], lonlat=True, color='white', lw=0.5, ls='--', alpha=0.4)
hp.projplot([0, 360], [-20, -20], lonlat=True, color='white', lw=0.5, ls='--', alpha=0.4)

# 圖例
import matplotlib.patches as mpatches
handles = [
    mpatches.Patch(color='cyan', label=f'Normal edge (88, cold-hot)'),
    mpatches.Patch(color='red', label=f'Frustrated edge (32, same-sign)'),
    mpatches.Patch(color='blue', label='Cold node (30)'),
    mpatches.Patch(color='red', label='Hot node (30)'),
    mpatches.Patch(color='yellow', label='Cold spot (node 0) + antipode (node 57)'),
]
plt.legend(handles=handles, loc='lower center', bbox_to_anchor=(0.5, -0.08),
           ncol=3, fontsize=11, frameon=True)

plt.tight_layout()
plt.savefig('data/smica_sky_map.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ data/smica_sky_map.png 已存")

# ============ 6. 特寫: 冷斑區域 (orthview) ============
print("繪製冷斑特寫...")
fig2 = plt.figure(figsize=(12, 12))
hp.orthview(m_smooth, fig=fig2, cmap='jet', min=-150e-6, max=150e-6,
            rot=[l_deg[0], b_deg[0]], half_sky=True,
            title=f'Cold Spot Region (l={l_deg[0]:.1f}, b={b_deg[0]:.1f}) — 3-fold axis at 15.1°',
            cbar=False, hold=True, notext=True)

# 冷斑附近嘅邊
for u, v in edges_list:
    is_fr = (u, v) in frustration
    lons, lats = slerp_arc(gal_vecs[u], gal_vecs[v])
    hp.projplot(lons, lats, lonlat=True,
                color='red' if is_fr else 'cyan',
                lw=1.8 if is_fr else 1.0,
                alpha=0.95 if is_fr else 0.6)

# 節點
for i in range(60):
    c = 'blue' if color[i] == 1 else 'red'
    hp.projscatter(l_deg[i], b_deg[i], lonlat=True, color=c, marker='o',
                   s=40, edgecolors='white', linewidths=0.5)

hp.projscatter(l_deg[0], b_deg[0], lonlat=True, color='yellow', marker='*',
               s=800, edgecolors='black', linewidths=2, zorder=10)

# 3-fold 軸位置 (dodecahedron 頂點方向) — 由之前分析: 最近 3-fold 軸喺 15.11° 外
plt.title(f'Cold Spot (l={l_deg[0]:.1f}, b={b_deg[0]:.1f}) — A5 node 0\n'
          f'Nearest 3-fold axis 15.1° away — general orbit member',
          fontsize=14)
plt.tight_layout()
plt.savefig('data/smica_coldspot_zoom.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ data/smica_coldspot_zoom.png 已存")
print("\n🎉 完成!")
