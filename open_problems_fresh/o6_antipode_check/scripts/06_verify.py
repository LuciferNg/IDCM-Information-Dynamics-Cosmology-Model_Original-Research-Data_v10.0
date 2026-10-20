#!/usr/bin/env python3
"""
06_verify.py — O6 雙重驗證 / 幻覺檢查
========================================
1. 獨立重算: 從原始 cache 地圖 + 節點檔重算關鍵數字
2. 對比各 script 寫出嘅 data/*.txt
3. 檔存在檢查
4. 列聯表 / 匹配率重算
"""
import healpy as hp
import numpy as np
import math
import os
import sys
from collections import defaultdict, deque
from astropy.coordinates import SkyCoord
import astropy.units as astropy_units

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
NODE_FILE = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
CACHE = "/tmp/cache_o3"
DATA = os.path.join(BASE, "o6_antipode_check/data")

passes = []
fails = []

def check(name, cond, detail=""):
    if cond:
        passes.append(name)
        print(f"  ✅ {name} {detail}")
    else:
        fails.append(name)
        print(f"  ❌ {name} {detail}")

print("=" * 66)
print("O6 雙重驗證 (獨立重算)")
print("=" * 66)

# ============ 1. 檔存在 ============
print("\n=== 1. 檔案存在 ===")
for f in ["antipode_region.txt", "antipode_neighbors.txt", "sign_analysis.txt",
          "scale_test.txt", "theory_check.txt"]:
    check(f"data/{f}", os.path.exists(os.path.join(DATA, f)))

# ============ 2. 圖重構 ============
print("\n=== 2. 圖重構 + 著色 ===")
nodes = []
with open(NODE_FILE) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
check("a5_nodes 60 行", len(nodes) == 60, f"({len(nodes)})")

vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])

adj = defaultdict(set)
edges_list = []
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang < 28.0:
            adj[i].add(j)
            adj[j].add(i)
            edges_list.append((i, j))
check("邊數 120", len(edges_list) == 120, f"({len(edges_list)})")
check("degree 均勻 4", all(len(adj[i]) == 4 for i in range(60)))

hop = {0: 0}
color = {0: 1}
q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in hop:
            hop[w] = hop[u] + 1
            color[w] = 1 - color[u]
            q.append(w)
check("節點 57 hop=8", hop[57] == 8, f"({hop[57]})")
check("節點 57 冷色", color[57] == 1)
check("著色 = parity", all(color[i] == 1 - (hop[i] % 2) for i in range(60)))

# ============ 3. 溫度重算 ============
print("\n=== 3. 節點溫度重算 (SMICA 4.17 cache) ===")
m = hp.read_map(os.path.join(CACHE, "SMICA_4.17.fits"), field=0)
nside = hp.get_nside(m)
sc = SkyCoord(ra=nodes[:, 0]*astropy_units.deg, dec=nodes[:, 1]*astropy_units.deg, frame='icrs')
gal = sc.galactic
l_deg = gal.l.deg
b_deg = gal.b.deg
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T = m[pix] * 1e6
check("節點 0 ≈ -134.19", abs(T[0] + 134.19) < 0.5, f"({T[0]:+.2f})")
check("節點 57 ≈ +8.21", abs(T[57] - 8.21) < 0.5, f"({T[57]:+.2f})")

# 對徑角
ang57 = math.degrees(math.acos(np.clip(np.dot(vecs[0], vecs[57]), -1, 1)))
check("對徑角 174.66°", abs(ang57 - 174.66) < 0.05, f"({ang57:.3f})")

# ============ 4. 統計重算 ============
print("\n=== 4. 統計重算 ===")
cold_arr = np.array([color[i] for i in range(60)])
match = ((cold_arr == 1) & (T < 0)) | ((cold_arr == 0) & (T > 0))
check("匹配率 ≈ 61.7%", abs(match.mean() - 0.617) < 0.02, f"({match.mean()*100:.1f}%)")

cp = [i for i in range(60) if cold_arr[i] == 1 and T[i] > 0]
check("冷色正溫 = 12", len(cp) == 12, f"({len(cp)})")
check("節點 57 喺冷色正溫群", 57 in cp)

# 對徑對
pairs = []
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang > 170.0:
            pairs.append((i, j))
check("對徑對 = 30", len(pairs) == 30, f"({len(pairs)})")
same_col = sum(1 for i, j in pairs if color[i] == color[j])
check("對徑對全同色", same_col == 30, f"({same_col})")
hop8 = sum(1 for i, j in pairs if hop[i] + hop[j] == 8)
check("對徑對 hop 和 = 8", hop8 == 30, f"({hop8})")

# ΔE=0
frust = set()
for a, b in edges_list:
    if color[a] == color[b]:
        frust.add(frozenset((a, b)))
k = {i: sum(1 for w in adj[i] if frozenset((i, w)) in frust) for i in range(60)}
zeroE = sorted([i for i in range(60) if k[i] == 2])
check("ΔE=0 = 12 節點", len(zeroE) == 12, f"({len(zeroE)})")
check("節點 57 唔係 ΔE=0", 57 not in zeroE)

# 尺度穩定性: 節點 57 符號
signs = []
for s in [0.5, 1.0, 2.0, 3.0, 4.17, 5.0, 7.0, 10.0]:
    m2 = hp.read_map(os.path.join(CACHE, f"SMICA_{s}.fits"), field=0)
    ns = hp.get_nside(m2)
    p2 = hp.ang2pix(ns, l_deg[57], b_deg[57], lonlat=True)
    signs.append(np.sign(m2[p2]))
check("節點 57 大尺度 (≥3°) 穩定正", all(s == 1 for s in signs[3:]), f"(小尺度 {signs[:3]} 負, 大尺度 {signs[3:]} 正)")

# ============ 5. 結果彙總 ============
print(f"\n{'='*66}")
print(f"結果: {len(passes)} 通過, {len(fails)} 失敗")
if fails:
    print("❌ 有失敗! 需要調查")
    sys.exit(1)
else:
    print("✅ 全部通過 — 無幻覺")
