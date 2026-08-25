#!/usr/bin/env python3
"""
PSZ1 星系團 — 修正對照: 全天空均勻 vs 打散 RA
================================================
發現: PSZ1 星系團 (1228 個, 全天) 到最近節點 12.5% < 8°,
      遠低於「打散 RA 保持 dec」MC 嘅 23.8% → p=1.0

問題: 打散 RA 保持 dec 對「全天樣本」唔啱用!
  - 呢個方法啱 Auger (視場覆蓋 ~85% 南半球)
  - 但 PSZ1 係全天 (Planck 掃描全天)
  - 正確對照: 天球均勻隨機 (RA 均勻 + sin(dec) 均勻)

修正: 用天球均勻隨機做 MC
  如果修正後仍然 p~1 (星系團避開節點) → 可能係真 signal!
  如果修正後 p~0.5 (冇差異) → 之前嘅結果係方法假象
"""
import struct
import xml.etree.ElementTree as ET
import base64
import math
import os
import json
import numpy as np

# ============ 1. 解碼 PSZ1 ============
tree = ET.parse('/tmp/psz_all.xml')
root = tree.getroot()
ns = 'http://www.ivoa.net/xml/VOTable/v1.3'

clusters = []
for stream in root.iter('{%s}STREAM' % ns):
    b64 = stream.text.strip()
    data = base64.b64decode(b64)
    pos = 0
    while pos + 24 <= len(data):
        ra, dec, z = struct.unpack('>ddd', data[pos:pos+24])
        pos += 24
        end = data.find(b'\x00', pos)
        if end == -1: break
        name = data[pos:end].decode('ascii', errors='replace')
        pos = end + 1
        if math.isnan(z): z = None
        clusters.append({'ra': ra, 'dec': dec, 'z': z, 'name': name})
    break

cl_ra = np.array([c['ra'] for c in clusters])
cl_dec = np.array([c['dec'] for c in clusters])
print(f"星系團: {len(clusters)}")

# ============ 2. 60 節點 ============
CMB_DATA = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/cmb_cold_spot/data'
nodes = []
with open(os.path.join(CMB_DATA, 'a5_nodes.txt')) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        nodes.append((float(p[0]), float(p[1])))
nodes = np.array(nodes)

def ang_dist_mat(ra1, dec1, ra2, dec2):
    ra1, dec1 = np.radians(ra1), np.radians(dec1)
    ra2, dec2 = np.radians(ra2), np.radians(dec2)
    cosd = np.sin(dec1)[:, None]*np.sin(dec2)[None, :] + \
           np.cos(dec1)[:, None]*np.cos(dec2)[None, :]*np.cos(ra1[:, None]-ra2[None, :])
    return np.degrees(np.arccos(np.clip(cosd, -1, 1)))

D = ang_dist_mat(cl_ra, cl_dec, nodes[:, 0], nodes[:, 1])
d_min = D.min(axis=1)
print(f"觀測: 最近節點中位數 {np.median(d_min):.2f}°")

# ============ 3. 兩種 MC 對照 ============
rng = np.random.default_rng(42)
N_MC = 5000

print(f"\n{'='*70}")
print("對照 A: 天球均勻隨機 (正確 for 全天樣本)")
print(f"{'='*70}")
for r in [5, 8, 10, 15]:
    obs = int((d_min < r).sum())
    mc = np.zeros(N_MC, dtype=int)
    for i in range(N_MC):
        ra_r = rng.uniform(0, 360, len(cl_ra))
        dec_r = np.degrees(np.arcsin(rng.uniform(-1, 1, len(cl_ra))))
        D_r = ang_dist_mat(ra_r, dec_r, nodes[:, 0], nodes[:, 1])
        mc[i] = (D_r.min(axis=1) < r).sum()
    p_hi = float((mc >= obs).mean())   # 過量?
    p_lo = float((mc <= obs).mean())   # 不足?
    sig_hi = "🟢 過量" if p_hi < 0.05 else ""
    sig_lo = "🟢 不足!" if p_lo < 0.05 else ""
    print(f"  節點<{r:>2}°: 觀測 {obs:>4} ({obs/len(clusters)*100:.1f}%)  MC={mc.mean():.1f}±{mc.std():.1f} ({mc.mean()/len(clusters)*100:.1f}%)  P(≥)={p_hi:.4f} {sig_hi}  P(≤)={p_lo:.4f} {sig_lo}")

print(f"\n{'='*70}")
print("對照 B: 打散 RA 保持 dec (之前用嘅方法)")
print(f"{'='*70}")
for r in [5, 8, 10, 15]:
    obs = int((d_min < r).sum())
    mc = np.zeros(3000, dtype=int)
    for i in range(3000):
        ra_r = rng.uniform(0, 360, len(cl_ra))
        D_r = ang_dist_mat(ra_r, cl_dec, nodes[:, 0], nodes[:, 1])
        mc[i] = (D_r.min(axis=1) < r).sum()
    p_hi = float((mc >= obs).mean())
    p_lo = float((mc <= obs).mean())
    sig_lo = "🟢 不足!" if p_lo < 0.05 else ""
    print(f"  節點<{r:>2}°: 觀測 {obs:>4} ({obs/len(clusters)*100:.1f}%)  MC={mc.mean():.1f}±{mc.std():.1f} ({mc.mean()/len(clusters)*100:.1f}%)  P(≥)={p_hi:.4f}  P(≤)={p_lo:.4f} {sig_lo}")

# ============ 4. 檢查 dec 分佈 ============
print(f"\n{'='*70}")
print("PSZ1 dec 分佈 vs 節點 dec 分佈")
print(f"{'='*70}")
# 星系團 dec 直方圖
hist_cl, bins = np.histogram(cl_dec, bins=18, range=(-90, 90))
# 節點 dec 直方圖
hist_no, _ = np.histogram(nodes[:, 1], bins=18, range=(-90, 90))
print(f"{'Dec bin':>10} {'星系團':>8} {'節點':>6}")
for i in range(18):
    b = bins[i]
    print(f"{b:>+8.0f}° {hist_cl[i]:>8} {hist_no[i]:>6}")

# 統計: 星系團 dec 中位數
print(f"\n星系團 dec 中位數: {np.median(cl_dec):.1f}°")
print(f"節點 dec 中位數:   {np.median(nodes[:,1]):.1f}°")

# ============ 5. 保存 ============
os.makedirs('data', exist_ok=True)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/psz1_alignment_corrected.json'), 'w') as f:
    json.dump({
        "n_clusters": len(clusters),
        "median_d_obs": float(np.median(d_min)),
        "note": "full-sky uniform MC is the correct null for PSZ1",
        "dec_median_clusters": float(np.median(cl_dec)),
        "dec_median_nodes": float(np.median(nodes[:,1]))
    }, f, indent=2)
print(f"\n已保存 data/psz1_alignment_corrected.json")
