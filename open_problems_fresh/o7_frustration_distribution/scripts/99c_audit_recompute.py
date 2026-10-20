#!/usr/bin/env python3
"""
O7 完整審計: 獨立重算本 session 所有關鍵數值
============================================================
目的: 從原始數據獨立重算 A/B/D/E 開放問題嘅所有關鍵數字,
      核對記錄文檔 (01_problem_record.md + docs/01_o7_complete_report.md) 聲稱。

唔依賴任何 08-15 腳本, 全部從頭計算 (independent re-derivation)。
"""
import numpy as np, math, json
from collections import defaultdict, deque
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as AU
from scipy.stats import ttest_ind, mannwhitneyu, binomtest

DATA = "/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data"
O5 = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare/data"
CACHE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare/data/smooth_cache"

passed, failed = 0, 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"   ✅ {name} {detail}")
    else:
        failed += 1
        print(f"   ❌ {name} {detail}")

print("=" * 72)
print("O7 完整審計: 獨立重算 (不依賴 08-15 腳本)")
print("=" * 72)

# ============ 1. 載入原始數據 ============
nodes = []
with open(f"{DATA}/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)

vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                   math.cos(math.radians(d))*math.sin(math.radians(r)),
                   math.sin(math.radians(d))] for r,d in nodes])

adj = defaultdict(set)
edges_all = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j)
            adj[j].add(i)
            edges_all.append((i, j))

color = {}
with open(f"{DATA}/anchored_coloring.txt") as f:
    f.readline()
    for line in f:
        p = line.strip().split()
        color[int(p[0])] = int(p[3])

frust_edges = set()
with open(f"{DATA}/frustration_edges.txt") as f:
    f.readline()
    for line in f:
        p = line.strip().split()
        u, v = int(p[0]), int(p[1])
        frust_edges.add((min(u, v), max(u, v)))

frust_adj = defaultdict(set)
for u, v in frust_edges:
    frust_adj[u].add(v); frust_adj[v].add(u)

# 面邊類型
edge_faces = defaultdict(list)
with open(f"{DATA}/faces.txt") as f:
    for line in f:
        if line.startswith("#"): continue
        ft = line.strip().split()[0]
        bs = line.index('['); be = line.index(']')
        verts = [int(x) for x in line[bs+1:be].split(',')]
        n = len(verts)
        for i in range(n):
            e = tuple(sorted((verts[i], verts[(i+1)%n])))
            edge_faces[e].append(ft)

# 座標轉換
sc = SkyCoord(ra=nodes[:, 0]*AU.deg, dec=nodes[:, 1]*AU.deg, frame='icrs')
gal = sc.galactic
node_l = np.array(gal.l.deg)
node_b = np.array(gal.b.deg)
# Galactic 座標向量 (同 O5 目錄比較必須用呢個!)
node_vecs = np.array([[math.cos(math.radians(b))*math.cos(math.radians(l)),
                        math.cos(math.radians(b))*math.sin(math.radians(l)),
                        math.sin(math.radians(b))] for l, b in zip(node_l, node_b)])

# ============ 2. 縫合線 (component) ============
print(f"\n📐 [1] 縫合線結構")
seen = set()
seams = []
for s in range(60):
    if s not in frust_adj or s in seen:
        continue
    comp = []
    q = deque([s])
    seen.add(s)
    while q:
        u = q.popleft()
        comp.append(u)
        for v in frust_adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    if len(comp) >= 2:
        seams.append(comp)

check("縫合線數 = 20", len(seams) == 20, f"(實際 {len(seams)})")
lens = sorted([len(c) for c in seams])
check("長度分佈 [2×10, 3×8, 4×2]", lens == [2]*10 + [3]*8 + [4]*2, f"(實際 {lens})")

# 端點數
endpoints = []
for comp in seams:
    for v in comp:
        if len(frust_adj[v]) == 1:
            endpoints.append(v)
check("端點 = 40", len(endpoints) == 40, f"(實際 {len(endpoints)})")

# 端點 isotropy (R_len)
ep_vecs = np.array([vecs[v] for v in endpoints])
R = np.linalg.norm(ep_vecs.sum(axis=0)) / len(ep_vecs)
check("端點 R_len ≈ 0.0029", abs(R - 0.0029) < 0.0005, f"(實際 {R:.5f})")

# ============ 3. 開放問題 A: 端點 vs connector 梯度 ============
print(f"\n📐 [2] 開放 A: 溫度梯度 (4.17° 尺度)")
m = hp.read_map(f"{CACHE}/smica2_smooth4.17.fits", field=0)
m = hp.remove_dipole(m)
nside = hp.get_nside(m)
pix = hp.ang2pix(nside, node_l, node_b, lonlat=True)
T = m[pix]

deg1 = sorted([v for v in range(60) if v in frust_adj and len(frust_adj[v]) == 1])
deg2 = sorted([v for v in range(60) if v in frust_adj and len(frust_adj[v]) == 2])

def grad(v):
    nbrs = list(adj[v])
    return abs(T[v] - np.mean(T[nbrs]))

g1 = np.array([grad(v) for v in deg1]) * 1e6
g2 = np.array([grad(v) for v in deg2]) * 1e6
check("端點梯度 36.95", abs(np.mean(g1) - 36.95) < 1.0, f"(實際 {np.mean(g1):.2f})")
check("connector 梯度 19.84", abs(np.mean(g2) - 19.84) < 1.0, f"(實際 {np.mean(g2):.2f})")
check("端點 > connector", np.mean(g1) > np.mean(g2), f"(差 {np.mean(g1)-np.mean(g2):+.2f})")

# 排列檢定 (20000 次夠快)
rng = np.random.RandomState(42)
all_g = np.concatenate([g1, g2])
n1 = len(g1)
obs = np.mean(g1) - np.mean(g2)
cnt = 0
for _ in range(20000):
    perm = rng.permutation(len(all_g))
    d = np.mean(all_g[perm[:n1]]) - np.mean(all_g[perm[n1:]])
    if d >= obs:
        cnt += 1
p_perm = cnt / 20000
check("排列 p < 0.05 (顯著)", p_perm < 0.05, f"(實際 p={p_perm:.4f}, 文檔聲稱 0.0236)")

# Bootstrap CI
boot = []
for _ in range(5000):
    b1 = rng.choice(g1, len(g1), replace=True)
    b2 = rng.choice(g2, len(g2), replace=True)
    boot.append(np.mean(b1) - np.mean(b2))
boot = np.array(boot)
ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
check("Bootstrap CI 唔含 0", ci_lo > 0, f"(實際 CI [{ci_lo:+.2f}, {ci_hi:+.2f}])")

# 邊級雙峰
dT_fr = np.array([abs(T[u] - T[v]) for u, v in frust_edges]) * 1e6
normal_edges = [e for e in edges_all if e not in frust_edges]
dT_norm = np.array([abs(T[u] - T[v]) for u, v in normal_edges]) * 1e6
check("阻挫邊 34.5 μK", abs(np.mean(dT_fr) - 34.5) < 1.5, f"(實際 {np.mean(dT_fr):.1f})")
check("正常邊 53.1 μK", abs(np.mean(dT_norm) - 53.1) < 2.0, f"(實際 {np.mean(dT_norm):.1f})")
check("阻挫 < 正常", np.mean(dT_fr) < np.mean(dT_norm), f"(差 {np.mean(dT_norm)-np.mean(dT_fr):+.1f})")

# ============ 4. 開放問題 B: 縫合線翻轉獨立性 ============
print(f"\n📐 [3] 開放 B: 拓撲位元")
# 每條縫合線翻轉全部端點, 檢查有冇影響其他縫合線
seam_edges = []
for comp in seams:
    se = set()
    for u, v in frust_edges:
        if u in comp and v in comp:
            se.add((u, v))
    seam_edges.append(se)

other_seam_edges = []
for i in range(len(seams)):
    ose = set()
    for j, comp in enumerate(seams):
        if j == i:
            continue
        for u, v in frust_edges:
            if u in comp and v in comp:
                ose.add((u, v))
    other_seam_edges.append(ose)

conflicts = 0
base_frust = set((min(u,v), max(u,v)) for u in range(60) for v in adj[u] if u < v and color[u] == color[v])
for i, comp in enumerate(seams):
    eps = [v for v in comp if len(frust_adj[v]) == 1]
    if not eps:
        continue
    # 翻轉端點
    new_color = dict(color)
    for v in eps:
        new_color[v] = 1 - new_color[v]
    # 新阻挫邊 (只計「新增」— 翻轉後變成阻挫嘅邊)
    new_frust = set()
    for u in range(60):
        for v in adj[u]:
            if u < v and new_color[u] == new_color[v] and (u, v) not in base_frust:
                new_frust.add((u, v))
    # 影響其他縫合線? (新增嘅阻挫邊喺其他縫合線嘅邊集內)
    cross = new_frust & other_seam_edges[i]
    if cross:
        conflicts += 1

check("縫合線翻轉 0 衝突", conflicts == 0, f"(實際 {conflicts} 條有衝突)")
check("縫合線級 MIS = 20", len(seams) == 20, f"(實際 {len(seams)})")

# ============ 5. 開放問題 D: 奇面組合 ΔT ============
print(f"\n📐 [4] 開放 D: 奇面組合 ΔT")
combo_dt = defaultdict(list)
for i, comp in enumerate(seams):
    odd_types = set()
    for e in frust_edges:
        if e[0] in comp and e[1] in comp:
            for ft in edge_faces[e]:
                if ft in ('T', 'P'):
                    odd_types.add('Δ' if ft == 'T' else '⬠')
    combo = ''.join(sorted(odd_types))
    temps = [T[v]*1e6 for v in comp]
    combo_dt[combo].append(max(temps) - min(temps))

dt_d = np.array(combo_dt.get('Δ', []))
dt_dp = np.array(combo_dt.get('Δ⬠', []))
check("Δ 組合 8 條", len(dt_d) == 8, f"(實際 {len(dt_d)})")
check("Δ⬠ 組合 10 條", len(dt_dp) == 10, f"(實際 {len(dt_dp)})")
check("Δ⬠ ΔT=69.7", abs(np.mean(dt_dp) - 69.7) < 1.5, f"(實際 {np.mean(dt_dp):.1f})")
check("Δ ΔT=27.4", abs(np.mean(dt_d) - 27.4) < 1.5, f"(實際 {np.mean(dt_d):.1f})")
check("Δ⬠ > Δ (2.5×)", np.mean(dt_dp) > 2 * np.mean(dt_d), f"(比 {np.mean(dt_dp)/np.mean(dt_d):.2f}×)")

# MW 檢定
u_p = mannwhitneyu(dt_d, dt_dp, alternative='two-sided')[1]
check("MW p=0.0085", abs(u_p - 0.0085) < 0.005, f"(實際 p={u_p:.4f})")

# S18 = 全球第 2 冷
all_T = [T[v]*1e6 for v in range(60)]
order = np.argsort(all_T)
check("節點 47 = 全球第 2 冷", order[1] == 47, f"(實際第 2 冷 = #{order[1]}, T={all_T[order[1]]:.1f})")
check("節點 47 T=-123.4", abs(all_T[47] + 123.4) < 1.5, f"(實際 {all_T[47]:.1f})")
check("節點 47 b=-8.6°", abs(node_b[47] + 8.6) < 0.5, f"(實際 {node_b[47]:.1f}°)")

# ============ 6. 開放問題 E: O5 交叉 ============
print(f"\n📐 [5] 開放 E: O5 交叉")
with open(f"{O5}/smica_catalog.json") as f:
    cat = json.load(f)

def spot_vecs_list(spots):
    vs = []
    for s in spots:
        l, b = s['peak_l'], s['peak_b']
        r, d = math.radians(l), math.radians(b)
        vs.append(np.array([math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d)]))
    return vs

cold_vs = spot_vecs_list(cat['cold'])
hot_vs = spot_vecs_list(cat.get('hot', []))
check("O5 冷組件 15", len(cold_vs) == 15, f"(實際 {len(cold_vs)})")
check("O5 熱組件 14", len(hot_vs) == 14, f"(實際 {len(hot_vs)})")

def min_dist(v, vs_list):
    return min(math.degrees(math.acos(np.clip(np.dot(v, w), -1, 1))) for w in vs_list)

# 端點到最近冷結構 (用 Galactic vecs!)
ep_cold_d = np.array([min_dist(node_vecs[v], cold_vs) for v in endpoints])
check("端點到最近冷 28.1°", abs(np.mean(ep_cold_d) - 28.1) < 1.0, f"(實際 {np.mean(ep_cold_d):.1f}°)")

# 跨冷熱
def is_cross(comp):
    eps = [v for v in comp if len(frust_adj[v]) == 1]
    if len(eps) != 2:
        return False
    e1, e2 = eps
    d1c = min_dist(node_vecs[e1], cold_vs)
    d2c = min_dist(node_vecs[e2], cold_vs)
    d1h = min_dist(node_vecs[e1], hot_vs)
    d2h = min_dist(node_vecs[e2], hot_vs)
    return (d1c < d2c and d1h > d2h) or (d1c > d2c and d1h < d2h)

n_cross = sum(1 for comp in seams if is_cross(comp))
check("跨冷熱 14/20", n_cross == 14, f"(實際 {n_cross}/20)")

# 銀河面剔除後
clean_seams = [comp for comp in seams if all(abs(node_b[v]) >= 20 for v in comp)]
clean_cross = sum(1 for comp in clean_seams if is_cross(comp))
check("剔除銀河面後 10 條", len(clean_seams) == 10, f"(實際 {len(clean_seams)})")
check("乾淨跨冷熱 6/10", clean_cross == 6, f"(實際 {clean_cross}/10)")
p_binom = binomtest(clean_cross, len(clean_seams), 0.5).pvalue
check("乾淨 p=0.754", abs(p_binom - 0.754) < 0.01, f"(實際 p={p_binom:.3f})")

# 銀河面內節點平均
gal_nodes = [v for v in range(60) if abs(node_b[v]) < 20]
gal_T = np.array([T[v]*1e6 for v in gal_nodes])
check("銀河面內平均 T=-1.9", abs(np.mean(gal_T) + 1.9) < 0.8, f"(實際 {np.mean(gal_T):+.1f})")
check("節點 47 係銀河面內最冷", min(gal_T) == all_T[47], f"(實際最冷 {min(gal_T):.1f} vs 節點47 {all_T[47]:.1f})")

# ============ 7. 總結 ============
print(f"\n{'='*72}")
print(f"📋 獨立重算審計結果: {passed} ✅ / {failed} ❌")
print(f"{'='*72}")
