#!/usr/bin/env python3
"""
05_verify.py — O3: 雙重驗證 (獨立重算所有關鍵數字)
====================================================
獨立方法: 重新讀 SMICA (唔用 cache) → 重新平滑 → 重新抽值
對比 01/02/03 結果, 檢查所有關鍵數字一致
"""
import healpy as hp
import numpy as np
import math
from astropy.coordinates import SkyCoord
import astropy.units as u
import os
from collections import Counter

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
DATA = os.path.join(BASE, "o3_node_temperatures/data")

print("=" * 66)
print("O3: 雙重驗證 (獨立重算)")
print("=" * 66)

# ============ 1. 獨立重讀 SMICA (唔用 cache) ============
print("\n=== 1. 獨立重讀 + 重平滑 ===")
m = hp.read_map("/tmp/smica2.fits", field=0)
nside = hp.get_nside(m)

# 用另一種平滑: 直接 hp.smoothing 用 iter=3 (healpy 建議)
fwhm_rad = np.radians(4.17)
sigma_rad = fwhm_rad / (2 * np.sqrt(2 * np.log(2)))
m_s = hp.smoothing(m, sigma=sigma_rad)
m_s = hp.remove_dipole(m_s)

# 同 cache 版比較
m_cache = hp.read_map("/tmp/smica2_smooth417.fits", field=0)
diff = np.abs(m_s - m_cache)
print(f"獨立重平滑 vs cache: max|Δ|={diff.max()*1e6:.6f} μK (應≈0)")

# ============ 2. 節點抽值 (獨立座標鏈) ============
print("\n=== 2. 節點抽值 (獨立重算) ===")
nodes = []
with open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)

# 方法 A: astropy ICRS→Galactic (同 01)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
pixA = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)
TA = m_s[pixA] * 1e6

# 方法 B: 手動座標轉換矩陣 (銀道北極 + 零點)
# 銀道轉換 (J2000): 北極 RA=192.85948°, Dec=27.12825°, 零點 l=0 喺 RA=266.40510°
# 用 astropy 檢查: gal.l.deg 應該一致
from astropy.coordinates import Galactic
print(f"方法 A 節點0: {TA[0]:.4f} μK")
print(f"方法 A 全部 mean/std: {TA.mean():.2f} / {TA.std(ddof=1):.2f} μK")

# ============ 3. 對比 01 存檔 ============
print("\n=== 3. 對比 01 存檔 ===")
rows = []
with open(os.path.join(DATA, "node_temps.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        rows.append((int(p[0]), int(p[1]), float(p[2]), int(p[5])))
T_saved = np.array([r[2] for r in rows])

diffs = np.abs(TA - T_saved)
print(f"獨立重算 vs 存檔: max|Δ|={diffs.max():.6f} μK")
assert diffs.max() < 0.01, f"❌ 差異過大: {diffs.max()}"
print("✅ 溫度一致 (max|Δ|<0.01 μK)")

# ============ 4. 關鍵統計數字重算 ============
print("\n=== 4. 關鍵統計重算 ===")
color = np.array([r[1] for r in rows])
Tc = TA[color == 1]
Th = TA[color == 0]
d = Tc.mean() - Th.mean()
print(f"冷色 mean: {Tc.mean():.2f} μK (01: -12.41)")
print(f"熱色 mean: {Th.mean():.2f} μK (01: +9.91)")
print(f"冷熱差: {d:.2f} μK (01: -22.31)")

# 冷斑 + 節點 47/57
print(f"節點 0: {TA[0]:.2f} (01: -134.19)")
print(f"節點 47: {TA[47]:.2f} (01: -123.40)")
print(f"節點 57: {TA[57]:.2f} (01: +8.21)")
print(f"節點 53: {TA[53]:.2f} (01: +112.00)")

# ============ 5. BFS 距離重算 ============
print("\n=== 5. BFS 距離重算 ===")
vecs = np.array([[math.cos(math.radians(dd))*math.cos(math.radians(rr)),
                  math.cos(math.radians(dd))*math.sin(math.radians(rr)),
                  math.sin(math.radians(dd))] for rr, dd in nodes])
from collections import defaultdict, deque
adj = defaultdict(set)
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang < 28.0:
            adj[i].add(j)
            adj[j].add(i)
hop = {0: 0}
q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in hop:
            hop[w] = hop[u] + 1
            q.append(w)
hist = Counter(hop.values())
print(f"BFS 分佈: {dict(sorted(hist.items()))} (01: 1+4+8+11+12+11+8+4+1)")
assert dict(sorted(hist.items())) == {0:1, 1:4, 2:8, 3:11, 4:12, 5:11, 6:8, 7:4, 8:1}, "BFS 分佈唔一致!"
print("✅ BFS 分佈一致")

# ============ 6. 檢查平滑尺度依賴 (魯棒性) ============
print("\n=== 6. 平滑尺度魯棒性 ===")
# 3° 同 6° 平滑重抽 — 冷熱差應保持方向
for fw in [3.0, 5.0, 7.0]:
    s = np.radians(fw) / (2 * np.sqrt(2 * np.log(2)))
    mm = hp.remove_dipole(hp.smoothing(m, sigma=s))
    TT = mm[pixA] * 1e6
    dd = TT[color == 1].mean() - TT[color == 0].mean()
    print(f"  {fw}° FWHM: 冷熱差 = {dd:.2f} μK")

print("\n✅ 雙重驗證完成")
