#!/usr/bin/env python3
"""
01_node57_region.py — O26: 節點 57 (冷斑對徑) 附近大尺度結構
================================================================
分析節點 57 (hop=8, 對徑, l=34.55°, b=+52.71°) 附近 5°-30° 區域,
同冷斑 (節點 0) 對比。方法參考 scripts/18_node45_region.py (O3)。

項目:
1. 節點 57 附近 5°-30° 區域結構 (mean/std/極值)
2. 三地圖一致 (SMICA/NILC/Commander @ 4.17°)
3. 冷斑↔對徑 30° 區域大尺度對比
4. 對徑對 (0↔57) 大尺度背景 (10° 平滑)
5. 「冷色但正溫」— 附近結構解釋
6. Null test: random 30° disc bootstrap (1000×)
"""
import healpy as hp
import numpy as np
import math
import os
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
CACHE = "/tmp/cache_o3"
OUT = os.path.join(BASE, "o26_node57_region", "data")
os.makedirs(OUT, exist_ok=True)

rng = np.random.default_rng(26)

# ============ 載入節點 ============
nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic

# 節點 57 同 0 嘅 galactic 座標 (驗證)
print("=== 座標驗證 ===")
print(f"  node 0 : RA={nodes[0,0]:.2f} Dec={nodes[0,1]:.2f} -> l={gal.l.deg[0]:.2f} b={gal.b.deg[0]:.2f}")
print(f"  node 57: RA={nodes[57,0]:.2f} Dec={nodes[57,1]:.2f} -> l={gal.l.deg[57]:.2f} b={gal.b.deg[57]:.2f}")
print(f"  角距離 0↔57 = {sc[0].separation(sc[57]).deg:.2f}°")

# 已知數據 (node_temps.txt, 4.17° SMICA)
T57_417 = 8.2073   # +8.21 μK
T0_417 = -134.1893 # 冷斑
hop57 = 8

def vec_of(i):
    return np.array([math.cos(math.radians(gal.b.deg[i]))*math.cos(math.radians(gal.l.deg[i])),
                     math.cos(math.radians(gal.b.deg[i]))*math.sin(math.radians(gal.l.deg[i])),
                     math.sin(math.radians(gal.b.deg[i]))])

def load_map(name, fw):
    """載入 cache 地圖 (RING, nside=2048)"""
    if name == 'SMICA':
        path = f"{CACHE}/SMICA_smooth{fw}.fits"
    else:
        path = f"{CACHE}/{name}_{fw}.fits"
    return hp.read_map(path)

results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line)
    results.append(line)

log("=" * 70)
log("O26: 節點 57 (對徑點) 附近大尺度結構")
log("=" * 70)

# ============ 1. 區域掃描 (5°-30°, 5° 平滑 SMICA) ============
log("\n=== 1. 節點 57 附近區域結構 (5° 平滑 SMICA) ===")
m5 = load_map('SMICA', 5.0)
nside = hp.get_nside(m5)
v57 = vec_of(57)
log(f"  5° 平滑 nside={nside}")
for rad in [5, 10, 15, 20, 30]:
    disc = hp.query_disc(nside, v57, np.radians(rad))
    vals = m5[disc] * 1e6
    pix57 = hp.ang2pix(nside, gal.l.deg[57], gal.b.deg[57], lonlat=True)
    log(f"  {rad:>2}° 半徑: mean={vals.mean():+7.2f} std={vals.std():6.2f}  "
        f"min={vals.min():+7.2f} max={vals.max():+7.2f}  node57={m5[pix57]*1e6:+7.2f}")

# ============ 2. 三地圖一致 @ 4.17° ============
log("\n=== 2. 三地圖一致 (4.17° 平滑) ===")
m417 = {name: load_map(name, 4.17) for name in ['SMICA', 'NILC', 'Commander']}
nside4 = hp.get_nside(m417['SMICA'])
pix57_4 = hp.ang2pix(nside4, gal.l.deg[57], gal.b.deg[57], lonlat=True)
pix0_4 = hp.ang2pix(nside4, gal.l.deg[0], gal.b.deg[0], lonlat=True)
t57 = {name: m417[name][pix57_4]*1e6 for name in m417}
t0 = {name: m417[name][pix0_4]*1e6 for name in m417}
log(f"  node 57 (4.17°): SMICA={t57['SMICA']:+.2f} NILC={t57['NILC']:+.2f} Commander={t57['Commander']:+.2f} "
    f"spread={max(t57.values())-min(t57.values()):.2f}")
log(f"  node 0  (4.17°): SMICA={t0['SMICA']:+.2f} NILC={t0['NILC']:+.2f} Commander={t0['Commander']:+.2f} "
    f"spread={max(t0.values())-min(t0.values()):.2f}")

# 三地圖 30° 區域 mean
log("\n  30° 區域 mean (4.17°):")
for name in m417:
    disc = hp.query_disc(nside4, v57, np.radians(30))
    log(f"    {name}: {m417[name][disc].mean()*1e6:+7.2f} μK")
disc0_30 = hp.query_disc(nside4, vec_of(0), np.radians(30))
log(f"  node 0 (冷斑) 30° 區域 mean:")
for name in m417:
    log(f"    {name}: {m417[name][disc0_30].mean()*1e6:+7.2f} μK")

# ============ 3. 冷斑↔對徑 大尺度對比 ============
log("\n=== 3. 冷斑 vs 對徑 30° 區域對比 (5° 平滑) ===")
v0 = vec_of(0)
for rad in [10, 20, 30]:
    d0 = hp.query_disc(nside, v0, np.radians(rad))
    d57 = hp.query_disc(nside, v57, np.radians(rad))
    log(f"  {rad:>2}°: coldspot mean={m5[d0].mean()*1e6:+7.2f}  "
        f"antipode mean={m5[d57].mean()*1e6:+7.2f}  "
        f"Δ={m5[d0].mean()*1e6 - m5[d57].mean()*1e6:+7.2f}")

# ============ 4. 大尺度背景 (10° 平滑) ============
log("\n=== 4. 大尺度背景 (10° 平滑) ===")
m10 = load_map('SMICA', 10.0)
nside10 = hp.get_nside(m10)
pix57_10 = hp.ang2pix(nside10, gal.l.deg[57], gal.b.deg[57], lonlat=True)
pix0_10 = hp.ang2pix(nside10, gal.l.deg[0], gal.b.deg[0], lonlat=True)
log(f"  10° 平滑: node 57 = {m10[pix57_10]*1e6:+7.2f} μK, node 0 = {m10[pix0_10]*1e6:+7.2f} μK")
# 全天空 10° 平滑統計
allv = m10 * 1e6
log(f"  全天空 10° 平滑: mean={allv.mean():+.2f} std={allv.std():.2f} "
    f"min={allv.min():+.2f} max={allv.max():+.2f}")
# node 57 嘅 10° 值係幾多百分位
pct57 = (allv < m10[pix57_10]*1e6).mean() * 100
pct0 = (allv < m10[pix0_10]*1e6).mean() * 100
log(f"  node 57 10°值百分位: {pct57:.1f}% (大尺度背景好普通?)")
log(f"  node 0  10°值百分位: {pct0:.1f}%")

# ============ 5. 冷色正溫: 附近結構 ============
log("\n=== 5. 「冷色但正溫」— 區域解釋 ===")
disc30 = hp.query_disc(nside, v57, np.radians(30))
vals30 = m5[disc30] * 1e6
imax = np.argmax(vals30)
imin = np.argmin(vals30)
t_max, p_max = hp.pix2ang(nside, disc30[imax], lonlat=True)
t_min, p_min = hp.pix2ang(nside, disc30[imin], lonlat=True)
log(f"  30° 區域 max: {vals30.max():+.1f} μK @ (l={p_max:.0f}, b={t_max:.0f})")
log(f"  30° 區域 min: {vals30.min():+.1f} μK @ (l={p_min:.0f}, b={t_min:.0f})")
pix57_5 = hp.ang2pix(nside, gal.l.deg[57], gal.b.deg[57], lonlat=True)
log(f"  node 57 相對區域 mean: {m5[pix57_5]*1e6 - vals30.mean():+.1f} μK (區域 mean {vals30.mean():+.1f})")
# 區域 30° 有幾多正/負
log(f"  30° 區域正像素比例: {(vals30 > 0).mean()*100:.1f}%")

# ============ 6. Null test: random 30° disc bootstrap ============
log("\n=== 6. Null test: node 57 嘅 30° 區域 vs 1000 個 random 30° disc ===")
# 用較低解析度加速: 5° 平滑地圖原 nside=2048, downgrade 到 512
m5_512 = hp.ud_grade(m5, 512)
nside512 = 512
# 均勻 random 方向 (喺球面)
N = 1000
rvec = rng.normal(size=(N, 3))
rvec /= np.linalg.norm(rvec, axis=1, keepdims=True)
disc_means = np.empty(N)
disc_stds = np.empty(N)
disc_mins = np.empty(N)
disc_maxs = np.empty(N)
for k in range(N):
    d = hp.query_disc(nside512, rvec[k], np.radians(30))
    v = m5_512[d] * 1e6
    disc_means[k] = v.mean()
    disc_stds[k] = v.std()
    disc_mins[k] = v.min()
    disc_maxs[k] = v.max()

# node 57 嘅 30° 區域 (512)
d57_512 = hp.query_disc(nside512, v57, np.radians(30))
v57_30 = m5_512[d57_512] * 1e6
mean57 = v57_30.mean()
# z-score
z_mean = (mean57 - disc_means.mean()) / disc_means.std()
pct_mean = (disc_means < mean57).mean() * 100
log(f"  node 57 30° mean = {mean57:+.2f} μK")
log(f"  random disc mean: {disc_means.mean():+.2f} ± {disc_means.std():.2f} μK")
log(f"  z = {z_mean:+.2f}, percentile = {pct_mean:.1f}%")
# node 0 冷斑對照
d0_512 = hp.query_disc(nside512, v0, np.radians(30))
v0_30 = m5_512[d0_512] * 1e6
mean0 = v0_30.mean()
z0 = (mean0 - disc_means.mean()) / disc_means.std()
pct0m = (disc_means < mean0).mean() * 100
log(f"  node 0 (冷斑) 30° mean = {mean0:+.2f} μK, z = {z0:+.2f}, percentile = {pct0m:.1f}%")
# 對徑對相關: 檢查 random 對徑對嘅 mean 差異分佈
log(f"\n  對徑對 (0↔57) 30° mean 差 = {mean0 - mean57:+.2f} μK")
# random 對徑對: 每對 random 方向 + 其對徑
diffs = np.empty(500)
for k in range(500):
    # random 方向
    v = rng.normal(size=3); v /= np.linalg.norm(v)
    d1 = hp.query_disc(nside512, v, np.radians(30))
    d2 = hp.query_disc(nside512, -v, np.radians(30))
    diffs[k] = m5_512[d1].mean()*1e6 - m5_512[d2].mean()*1e6
pct_diff = (np.abs(diffs) < abs(mean0 - mean57)).mean() * 100
log(f"  random 對徑對 30° mean 差: median={np.median(np.abs(diffs)):.2f} μK")
log(f"  |0↔57 差| = {abs(mean0-mean57):.2f} μK 百分位 = {pct_diff:.1f}% (越高越普通)")

# ============ 7. 多尺度曲線 (node 57 vs node 0, 三地圖) ============
log("\n=== 7. 多尺度曲線 (0.5°-10°) ===")
scales = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
log(f"  {'scale':>5} | {'SMICA57':>8} {'NILC57':>8} {'Cmd57':>8} | {'SMICA0':>8} {'NILC0':>8} {'Cmd0':>8}")
for fw in scales:
    row = [fw]
    for name in ['SMICA', 'NILC', 'Commander']:
        m = load_map(name, fw)
        ns = hp.get_nside(m)
        p57 = hp.ang2pix(ns, gal.l.deg[57], gal.b.deg[57], lonlat=True)
        p0 = hp.ang2pix(ns, gal.l.deg[0], gal.b.deg[0], lonlat=True)
        row.append(m[p57]*1e6); row.append(m[p0]*1e6)
    log(f"  {row[0]:>5} | {row[1]:+8.2f} {row[2]:+8.2f} {row[3]:+8.2f} | {row[4]:+8.2f} {row[5]:+8.2f} {row[6]:+8.2f}")

# ============ 8. 30° 區域內 60 節點有幾多個 ============
log("\n=== 8. 節點 57 附近 30° 內其他 A₅ 節點 ===")
cnt = 0
for i in range(60):
    if i == 57:
        continue
    sep = sc[57].separation(sc[i]).deg
    if sep <= 30:
        cnt += 1
        log(f"  node {i}: 距離 {sep:.1f}°, T={T57_417 if False else ''}")
# 簡單版: 列出 30° 內節點
near = [(i, sc[57].separation(sc[i]).deg) for i in range(60) if i != 57 and sc[57].separation(sc[i]).deg <= 30]
near.sort(key=lambda x: x[1])
log(f"  30° 內節點數: {len(near)}")
for i, d in near:
    log(f"    node {i}: {d:.1f}°")

# 寫入檔案
with open(os.path.join(OUT, "node57_region_results.txt"), "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/node57_region_results.txt")
