#!/usr/bin/env python3
"""
Planck PSZ1 星系團目錄 — A₅ 節點對齊檢驗
============================================
數據: HEASARC TAP plancksz (1227 星系團, RA/Dec/redshift)
檢驗: H2 — 星系團到最近 A₅ 節點嘅距離 < 隨機期望?

IDCM 預測: 星系團 (物質凝聚點) 應該對齊 60 個 A₅ 節點投影
  如果 A₅ 網格係空間骨架, 節點 = 物質凝聚中心
"""
import struct
import xml.etree.ElementTree as ET
import base64
import math
import os
import json
import numpy as np

# ============ 1. 解碼 PSZ1 VOTable ============
tree = ET.parse('/tmp/psz_all.xml')
root = tree.getroot()
ns = 'http://www.ivoa.net/xml/VOTable/v1.3'

clusters = []
for stream in root.iter('{%s}STREAM' % ns):
    b64 = stream.text.strip()
    data = base64.b64decode(b64)
    # 解析: 每 row 3 doubles + null-terminated string
    pos = 0
    while pos + 24 <= len(data):
        ra, dec, z = struct.unpack('>ddd', data[pos:pos+24])
        pos += 24
        # 讀 string 直到 null
        end = data.find(b'\x00', pos)
        if end == -1: break
        name = data[pos:end].decode('ascii', errors='replace')
        pos = end + 1
        if math.isnan(z): z = None
        clusters.append({'ra': ra, 'dec': dec, 'z': z, 'name': name})
    break

print(f"星系團數目: {len(clusters)}")
print(f"樣本: {clusters[0]['name']} (RA={clusters[0]['ra']:.2f}, Dec={clusters[0]['dec']:.2f})")

# ============ 2. 載入 60 A₅ 節點 ============
CMB_DATA = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/cmb_cold_spot/data'
nodes = []
with open(os.path.join(CMB_DATA, 'a5_nodes.txt')) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        nodes.append((float(p[0]), float(p[1])))
nodes = np.array(nodes)
print(f"A₅ 節點: {len(nodes)}")

# ============ 3. 距離計算 ============
def ang_dist_mat(ra1, dec1, ra2, dec2):
    ra1, dec1 = np.radians(ra1), np.radians(dec1)
    ra2, dec2 = np.radians(ra2), np.radians(dec2)
    cosd = np.sin(dec1)[:, None]*np.sin(dec2)[None, :] + \
           np.cos(dec1)[:, None]*np.cos(dec2)[None, :]*np.cos(ra1[:, None]-ra2[None, :])
    return np.degrees(np.arccos(np.clip(cosd, -1, 1)))

cl_ra = np.array([c['ra'] for c in clusters])
cl_dec = np.array([c['dec'] for c in clusters])

D = ang_dist_mat(cl_ra, cl_dec, nodes[:, 0], nodes[:, 1])
d_min = D.min(axis=1)

print(f"\n{'='*70}")
print("星系團 vs A₅ 節點距離")
print(f"{'='*70}")
print(f"最近節點距離: 中位數 {np.median(d_min):.2f}°, 平均 {np.mean(d_min):.2f}°")
print(f"分佈: 10%={np.percentile(d_min,10):.1f}° 50%={np.median(d_min):.1f}° 90%={np.percentile(d_min,90):.1f}°")

# ============ 4. 蒙特卡羅 (打散 RA 保持 dec) ============
print(f"\n蒙特卡羅 (打散 RA, 保持 dec 視場)")
rng = np.random.default_rng(42)
N_MC = 5000

for r in [5, 8, 10, 15]:
    obs = int((d_min < r).sum())
    mc = np.zeros(N_MC, dtype=int)
    for i in range(N_MC):
        ra_r = rng.uniform(0, 360, len(cl_ra))
        D_r = ang_dist_mat(ra_r, cl_dec, nodes[:, 0], nodes[:, 1])
        mc[i] = (D_r.min(axis=1) < r).sum()
    p = float((mc >= obs).mean())
    sig = "🟢" if p < 0.05 else ("🟡" if p < 0.15 else "  ")
    print(f"  節點<{r:>2}°: {obs:>4}/{len(clusters)} ({obs/len(clusters)*100:.1f}%)  MC={mc.mean():.1f}±{mc.std():.1f}  p={p:.4f} {sig}")

# ============ 5. 紅移分層 ============
print(f"\n紅移分層 (z<0.1 低紅移, z>0.1 高紅移):")
for zmax, label in [(0.1, "z<0.1"), (10, "all z")]:
    mask = np.array([(c['z'] or 0) < zmax for c in clusters])
    sub = d_min[mask]
    if mask.sum() < 10: continue
    n8 = int((sub < 8).sum())
    # MC
    mc = np.zeros(2000, dtype=int)
    for i in range(2000):
        ra_r = rng.uniform(0, 360, mask.sum())
        D_r = ang_dist_mat(ra_r, cl_dec[mask], nodes[:, 0], nodes[:, 1])
        mc[i] = (D_r.min(axis=1) < 8).sum()
    p = float((mc >= n8).mean())
    print(f"  {label}: {mask.sum()} 星系團, <8°: {n8} ({n8/mask.sum()*100:.1f}%)  MC={mc.mean():.1f}±{mc.std():.1f}  p={p:.4f}")

# ============ 6. 保存 ============
results = {
    "n_clusters": len(clusters),
    "median_d_node": float(np.median(d_min)),
    "mean_d_node": float(np.mean(d_min)),
    "h2_check": "clusters vs nodes",
    "data_source": "HEASARC TAP plancksz (PSZ1 v2.1, 1227 clusters)"
}
os.makedirs('data', exist_ok=True)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/psz1_alignment.json'), 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n已保存 data/psz1_alignment.json")
