#!/usr/bin/env python3
"""
16_decay_rate_check.py — 每步衰減率獨立檢查
============================================
O4 核心宣稱: A(d) = F₅·φ^(-d), 每 hop 衰減 φ⁻¹

問題: 0.5° 平滑顯示 d2/d1 = 0.571, 偏差 -7.7% — 唔係精確 φ⁻¹

檢查:
1. 每層衰減率 (d1/d0, d2/d1, d3/d2...) 係咪穩定 φ⁻¹?
2. 用唔同平滑尺度睇趨勢
3. 統計檢定: 偏差係咪顯著?
4. 如果唔係 φ⁻¹, 係咩?
"""
import numpy as np
import math
from collections import defaultdict, deque
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as astro_u

phi = (1 + 5**0.5) / 2
F5 = 5

print("=" * 72)
print("O4 16: 每步衰減率獨立檢查")
print("=" * 72)

# 載入數據
nodes = np.loadtxt('/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt')
vecs = np.array([np.array([math.cos(math.radians(d))*math.cos(math.radians(r)),
                           math.cos(math.radians(d))*math.sin(math.radians(r)),
                           math.sin(math.radians(d))]) for r, d in nodes])

adj = defaultdict(set)
edges = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j); adj[j].add(i)
            edges.append((i, j))

dist = {0: 0}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in dist:
            dist[v] = dist[u] + 1
            q.append(v)

m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)
sc = SkyCoord(ra=nodes[:, 0]*astro_u.deg, dec=nodes[:, 1]*astro_u.deg, frame='icrs')
gal = sc.galactic
pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)

# ---------- 1. 各平滑尺度嘅每層衰減 ----------
print("\n=== 1. 每層衰減率 (各平滑尺度) ===")
print(f"{'FWHM':>5} {'d0':>7} {'d1':>7} {'d2':>7} {'d3':>7} {'d1/d0':>7} {'d2/d1':>7} {'d3/d2':>7}")
for fwhm in [0.5, 1.0, 2.0, 3.0, 4.17, 5.0]:
    sigma_rad = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
    m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
    T = m_s[pix] * 1e6
    layer_mean = {}
    for d in range(4):
        idx = [i for i in range(60) if dist[i] == d]
        layer_mean[d] = np.mean([abs(T[i]) for i in idx])
    r1 = layer_mean[1]/layer_mean[0] if layer_mean[0] else 0
    r2 = layer_mean[2]/layer_mean[1] if layer_mean[1] else 0
    r3 = layer_mean[3]/layer_mean[2] if layer_mean[2] else 0
    print(f"{fwhm:>5.2f} {layer_mean[0]:>7.1f} {layer_mean[1]:>7.1f} {layer_mean[2]:>7.1f} {layer_mean[3]:>7.1f} {r1:>7.3f} {r2:>7.3f} {r3:>7.3f}")

print(f"\nφ⁻¹ = {phi**-1:.3f}")

# ---------- 2. 0.5° 詳細統計 ----------
print("\n=== 2. 0.5° 平滑: 每層節點值分佈 ===")
sigma_rad = np.radians(0.5) / (2 * np.sqrt(2 * np.log(2)))
m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
T = m_s[pix] * 1e6
for d in range(4):
    idx = [i for i in range(60) if dist[i] == d]
    vals = np.abs(T[idx])
    print(f"d={d}: n={len(idx)}, mean={np.mean(vals):.1f} ± {np.std(vals):.1f}, 個別={[f'{v:.0f}' for v in vals]}")

# ---------- 3. 統計檢定: d2/d1 係咪 φ⁻¹? ----------
print("\n=== 3. 統計檢定 (0.5° 平滑) ===")
from scipy import stats as st
d1_idx = [i for i in range(60) if dist[i] == 1]
d2_idx = [i for i in range(60) if dist[i] == 2]
d1_vals = np.abs(T[d1_idx])
d2_vals = np.abs(T[d2_idx])

# 對數空間: ln|T| 應該線性
# ln A(d) = ln F₅ - d·ln φ → 斜率 = -ln φ = -0.4812
all_d = []
all_ln = []
for d in range(4):
    idx = [i for i in range(60) if dist[i] == d]
    for i in idx:
        all_d.append(d)
        all_ln.append(math.log(abs(T[i]) + 1e-10))

slope, intercept, r, p, se = st.linregress(all_d, all_ln)
print(f"ln|T| vs d 線性迴歸:")
print(f"  斜率 = {slope:.4f} (理論 -ln φ = {-math.log(phi):.4f})")
print(f"  R²   = {r**2:.4f}")
print(f"  p    = {p:.2e}")
print(f"  斜率偏差 = {(slope - (-math.log(phi)))/(-math.log(phi))*100:+.1f}%")
print(f"  衰減比 = e^slope = {math.exp(slope):.4f} (φ⁻¹ = {phi**-1:.4f})")

# ---------- 4. 如果唔係 φ⁻¹ 係咩? ----------
print("\n=== 4. 候選衰減率 ===")
obs_decay = math.exp(slope)
print(f"觀測衰減比 (0.5°) = {obs_decay:.4f}")
print(f"φ⁻¹ = {phi**-1:.4f}")
print(f"2/3 = {2/3:.4f} (F₃/F₄)")
print(f"φ⁻² 半衰? = {math.sqrt(phi**-1):.4f}")
print(f"對比: d2/d1 直接 = {np.mean(d2_vals)/np.mean(d1_vals):.4f}")

# 測試: 係咪 F_{5-d} 離散模型更啱?
# F₅=5, F₄=3, F₃=2, F₂=1: 比例 5:3:2:1
print(f"\nF_{'{5-d}'} 離散比例: 5:3:2:1")
print(f"觀測比例 (0.5°): {layer_mean[0]:.1f}:{layer_mean[1]:.1f}:{layer_mean[2]:.1f}:{layer_mean[3]:.1f}")
ratios = [layer_mean[d]/layer_mean[0] for d in range(4)]
print(f"歸一化: {[f'{r:.3f}' for r in ratios]}")
print(f"F 比例:  [1.000, 0.600, 0.400, 0.200]")
print(f"φ 比例:  [1.000, 0.618, 0.382, 0.236]")

with open('/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o4_fib_motivation/data/decay_rate_check.txt', 'w') as f:
    f.write("# O4 16: 每步衰減率檢查\n")
    f.write(f"# 0.5° 平滑: d1/d0={np.mean(d1_vals)/layer_mean[0]:.4f}, d2/d1={np.mean(d2_vals)/np.mean(d1_vals):.4f}\n")
    f.write(f"# ln 迴歸斜率={slope:.4f} (理論 -lnφ={-math.log(phi):.4f}), R²={r**2:.4f}\n")
    f.write(f"# 衰減比={obs_decay:.4f} vs φ⁻¹={phi**-1:.4f} (偏差 {(obs_decay-phi**-1)/phi**-1*100:+.1f}%)\n")
print(f"\n✅ 已存: data/decay_rate_check.txt")
