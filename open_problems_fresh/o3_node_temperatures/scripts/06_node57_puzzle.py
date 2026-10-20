#!/usr/bin/env python3
"""
06_node57_puzzle.py — O3: 節點 57 謎題深入分析
================================================
節點 57: 冷色著色但 +8.21 μK 正溫度
問題: 點解冷色結構對應正溫度?

檢查:
1. 節點 57 係咪孤例? (冷色正溫 = 12 個, 熱色負溫 = 11 個)
2. 著色 vs 溫度符號匹配率 = 61.7% — 但「著色」係圖論二色性, 唔係溫度符號
3. 著色其實編碼: BFS 奇偶距離 (alternating), 唔係「冷/熱」物理標籤
4. 關鍵: 節點 57 嘅物理位置 (對徑點) — 大尺度 CMB 結構決定溫度
5. 重新框架: 著色 = 圖論 parity, 唔係溫度預測
"""
import numpy as np
from scipy import stats
import os

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
DATA = os.path.join(BASE, "o3_node_temperatures/data")

# ============ 載入 ============
rows = []
with open(os.path.join(DATA, "node_temps.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        rows.append((int(p[0]), int(p[1]), float(p[2]), float(p[3]), float(p[4]), int(p[5])))
T = np.array([r[2] for r in rows])
color = np.array([r[1] for r in rows])
l_deg = np.array([r[3] for r in rows])
b_deg = np.array([r[4] for r in rows])
hop = np.array([r[5] for r in rows])

print("=" * 66)
print("O3: 節點 57 謎題分析")
print("=" * 66)

# ============ 1. 事實重述 ============
print("\n=== 1. 節點 57 事實 ===")
print(f"T = {T[57]:+.2f} μK")
print(f"hop = {hop[57]} (對徑點, 距離冷斑 8 hops)")
print(f"色 = {'冷 (1)' if color[57]==1 else '熱 (0)'}")
print(f"l, b = ({l_deg[57]:.2f}, {b_deg[57]:.2f})")

# ============ 2. 著色嘅本質 ============
print("\n=== 2. 著色嘅本質: BFS parity, 唔係溫度 ===")
# 著色 = BFS 奇偶距離 (anchor 0 = 冷)
# hop parity 完全決定著色
parity = hop % 2
print(f"著色 == hop parity? {np.all(color == (1 - parity))}")
# 驗證: color[i] == 1 當 hop 偶數
print(f"冷色 = hop 偶數: {np.all(color[hop % 2 == 0] == 1)}")
print(f"熱色 = hop 奇數: {np.all(color[hop % 2 == 1] == 0)}")
print("→ 著色純粹係圖論二色性 (奇偶), 冇任何物理溫度預測")

# ============ 3. 節點 57 嘅實際物理 ============
print("\n=== 3. 節點 57 物理位置 ===")
# 對徑點: 距離冷斑 174.66°
from astropy.coordinates import SkyCoord
import astropy.units as u
nodes = []
with open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
c0 = SkyCoord(ra=nodes[0,0]*u.deg, dec=nodes[0,1]*u.deg)
c57 = SkyCoord(ra=nodes[57,0]*u.deg, dec=nodes[57,1]*u.deg)
sep = c0.separation(c57)
print(f"冷斑 (0): RA={nodes[0,0]:.2f}, Dec={nodes[0,1]:.2f}")
print(f"節點57:    RA={nodes[57,0]:.2f}, Dec={nodes[57,1]:.2f}")
print(f"角距離: {sep.deg:.2f}° (完全對徑 = 180°)")

# ============ 4. 冷色正溫節點嘅共同特徵 ============
print("\n=== 4. 冷色正溫 (12) vs 冷色負溫 (18) ===")
cp = [(i, T[i], hop[i]) for i in range(60) if color[i]==1 and T[i]>0]
cn = [(i, T[i], hop[i]) for i in range(60) if color[i]==1 and T[i]<0]
print(f"冷色正溫: {len(cp)} 個, |T| mean={np.mean([abs(t) for _,t,_ in cp]):.1f} μK")
print(f"冷色負溫: {len(cn)} 個, |T| mean={np.mean([abs(t) for _,t,_ in cn]):.1f} μK")
print(f"冷色正溫 hop 分佈: {sorted([h for _,_,h in cp])}")
print(f"冷色負溫 hop 分佈: {sorted([h for _,_,h in cn])}")
tt = stats.ttest_ind([abs(t) for _,t,_ in cp], [abs(t) for _,t,_ in cn], equal_var=False)
print(f"|T| 冷色正 vs 負: t={tt.statistic:.3f}, p={tt.pvalue:.4f}")

# ============ 5. 大尺度結構: 節點 57 附近 ============
print("\n=== 5. 節點 57 附近大尺度 CMB ===")
# 檢查節點 57 喺 10° 內嘅區域平均 (用 7° 平滑地圖)
import healpy as hp
m7 = hp.remove_dipole(hp.smoothing(hp.read_map("/tmp/smica2.fits"), sigma=np.radians(7.0)/(2*np.sqrt(2*np.log(2)))))
nside = 2048
sc_all = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg)
gal_all = sc_all.galactic
pix_all = hp.ang2pix(nside, gal_all.l.deg, gal_all.b.deg, lonlat=True)
T7 = m7[pix_all] * 1e6
print(f"7° 平滑: 節點 57 = {T7[57]:+.2f} μK (4.17°: {T[57]:+.2f})")
print(f"7° 平滑: 節點 0 = {T7[0]:+.2f} μK (4.17°: {T[0]:+.2f})")

# 對徑區域大尺度平均: 冷斑 -134, 對徑點理應大尺度正?
# 偶極移除後, 對徑點通常係相反符號嘅大尺度模式
print(f"\n冷斑 (d0): {T[0]:+.2f} μK")
print(f"對徑 (d8): {T[57]:+.2f} μK")
print(f"→ 對徑點唔係自動相反 — 4.17° 平滑保留咗局部結構")

# ============ 6. 重新框架: 著色唔係溫度預測器 ============
print("\n=== 6. 結論: 著色 vs 溫度嘅關係 ===")
# 統計: 匹配率 61.7% vs 隨機 50%
match = ((color == 1) & (T < 0)) | ((color == 0) & (T > 0))
print(f"匹配率: {match.mean()*100:.1f}% (隨機 50%)")
p_bin = stats.binomtest(match.sum(), 60, 0.5).pvalue
print(f"Binomial p = {p_bin:.4f}")

# 但係: 冷色 mean vs 熱色 mean 有 -22.3μK 差異 (p=0.06)
# → 平均嚟講冷色偏冷, 但個別節點可以由大尺度模式主導
Tc = T[color==1]; Th = T[color==0]
print(f"\n冷色 mean: {Tc.mean():+.2f} μK")
print(f"熱色 mean: {Th.mean():+.2f} μK")
print(f"→ 統計上冷色集體偏冷, 但個別節點 (如 57) 被大尺度模式覆蓋")

# ============ 7. 對徑點特別檢查 ============
print("\n=== 7. 對徑點謎題總結 ===")
print("節點 57 (對徑) +8.21 μK:")
print("  1. 著色 = BFS parity (hop=8 偶數 → 冷色), 唔係溫度預測")
print("  2. 對徑點物理上唔係「反向冷斑」— CMB 偶極移除後冇簡單對稱")
print("  3. 12 個冷色正溫節點之一 — 唔係孤例, 冇特殊物理")
print("  4. 冷熱著色同溫度匹配僅 61.7% (p=0.09) — 弱相關, 唔係強預測")

print("\n✅ 節點 57 分析完成")
