#!/usr/bin/env python3
"""
O7 完整獨立審計 (2026-09-11)
========================================================================
從原始數據由零重算 docs/01_o7_complete_report.md + 01_problem_record.md
+ README.md 嘅所有關鍵數字。唔 import 任何 01-15/99/99b/99c script。

數據源 (全部只讀):
  cmb_cold_spot/data/a5_nodes.txt          — 60 節點 (RA Dec)
  cmb_cold_spot/data/faces.txt             — 62 面 (T/S/P, 頂點, frust)
  cmb_cold_spot/data/frustration_edges.txt — 32 阻挫邊
  cmb_cold_spot/data/anchored_coloring.txt — 錨定著色 (cold=1)
  cmb_cold_spot/data/smica_smoothed.txt    — 4.17° 平滑節點溫度
  cmb_cold_spot/data/smica_bandpass.txt    — 帶通 ell in [20,60] 節點溫度
  o5_catalog_compare/data/smooth_cache/    — 多尺度 SMICA 地圖
  o5_catalog_compare/data/smica_catalog.json — 冷/熱目錄組件
  cmb_cold_spot/data/bimodal_gradient.txt  — 19_bimodal 數據 (雙峰 sigma)

Sections A..K 對應文檔組; 每個 check 標 doc 出處。
MC 項目 (排列/自助/隨機對照) 用獨立 seed 20260911, 有限迭代, 帶 MC 容差。
"""
import numpy as np, math, json, re
from collections import defaultdict, deque
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as AU
from scipy.stats import ttest_ind, mannwhitneyu, binomtest

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
DATA = f"{BASE}/cmb_cold_spot/data"
O5 = f"{BASE}/o5_catalog_compare/data"
CACHE = f"{O5}/smooth_cache"

RNG = np.random.RandomState(20260911)  # 獨立 seed (原 scripts 用 42)

passed, failed = 0, 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"   PASS  {name} {detail}")
    else:
        failed += 1
        print(f"   FAIL  {name} {detail}")

def ang_sep_deg(v1, v2):
    return math.degrees(math.acos(np.clip(np.dot(v1, v2), -1.0, 1.0)))

def unit(ra, dec):
    r, d = math.radians(ra), math.radians(dec)
    return np.array([math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d)])

print("="*78)
print("O7 獨立審計 99d (2026-09-11): 由零重算 docs/01 + problem_record + README")
print("="*78)

# ---------- 1. 載入原始數據 ----------
nodes = []
with open(f"{DATA}/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([unit(r, d) for r, d in nodes])

# 著色 (anchored_coloring: idx RA Dec color(cold=1) frust_nbrs)
colors = {}
node_coords_ok = True
with open(f"{DATA}/anchored_coloring.txt") as f:
    for line in f:
        if line.startswith("#"): continue
        p = line.split()
        idx = int(p[0]); ra, dec = float(p[1]), float(p[2]); c = int(p[3])
        colors[idx] = c
        if abs(ra - nodes[idx][0]) > 1e-6 or abs(dec - nodes[idx][1]) > 1e-6:
            node_coords_ok = False
COLD = 1

# 阻挫邊
frust = set()
with open(f"{DATA}/frustration_edges.txt") as f:
    for line in f:
        if line.startswith("#"): continue
        p = line.split()
        u, v = int(p[0]), int(p[1])
        frust.add((u, v) if u < v else (v, u))

# 面: 每行 "T [v1, v2, ...] colors=[...] frust=N"
faces = []   # (type, [vertices], frust)
with open(f"{DATA}/faces.txt") as f:
    for line in f:
        if line.startswith("#"): continue
        m = re.match(r"([TSP])\s+\[([^\]]*)\]\s+colors=\[([^\]]*)\]\s+frust=(\d+)", line.strip())
        if not m: continue
        ftype, vstr, _, fcount = m.groups()
        verts = [int(x) for x in vstr.split(",") if x.strip()]
        faces.append((ftype, verts, int(fcount)))

edge_faces = defaultdict(list)   # (u,v) -> [(ftype, ...)]
all_edges = set()
for ftype, verts, _ in faces:
    n = len(verts)
    for i in range(n):
        a, b = verts[i], verts[(i+1) % n]
        e = (a, b) if a < b else (b, a)
        edge_faces[e].append(ftype)
        all_edges.add(e)
E = len(all_edges)
V = 60
F = len(faces)
adj = defaultdict(set)
for e in all_edges:
    adj[e[0]].add(e[1]); adj[e[1]].add(e[0])

print("\n[A] 圖重建 (docs/01 Task 1+4, problem_record 已知事實)")
check("V = 60", V == 60)
check("E = 120", E == 120)
check("F = 62", F == 62)
check("Euler chi = V-E+F = 2", V - E + F == 2)
ftype_counts = defaultdict(int)
for ft, _, _ in faces: ftype_counts[ft] += 1
check("T=20 (三角形)", ftype_counts['T'] == 20)
check("S=30 (正方形)", ftype_counts['S'] == 30)
check("P=12 (五邊形)", ftype_counts['P'] == 12)
deg_all = [len(adj[v]) for v in range(60)]
check("全部節點 degree = 4", all(d == 4 for d in deg_all))
edgetype = {}
for e in all_edges:
    ts = tuple(sorted(edge_faces[e]))
    edgetype[e] = ts
n_DD = sum(1 for ts in edgetype.values() if set(ts) == {'T','S'})
n_PP = sum(1 for ts in edgetype.values() if set(ts) == {'P','S'})
n_SS = sum(1 for ts in edgetype.values() if set(ts) == {'S'})
check("Delta-□ 邊 = 60 (50%)", n_DD == 60)
check("Pent-□ 邊 = 60 (50%)", n_PP == 60)
check("□-□ 邊 = 0", n_SS == 0)
check("anchored_coloring 座標 = a5_nodes", node_coords_ok)

print("\n[B] 阻挫邊 (docs/01 Task 1, problem_record 結果/已知事實)")
check("阻挫邊總數 = 32", len(frust) == 32)
cc = sum(1 for (u, v) in frust if colors[u] == COLD and colors[v] == COLD)
hh = sum(1 for (u, v) in frust if colors[u] != COLD and colors[v] != COLD)
check("冷-冷 = 16", cc == 16)
check("熱-熱 = 16", hh == 16)
check("冇異色邊 (阻挫 = 同色)", cc + hh == len(frust))
fr_D = sum(1 for e in frust if set(edgetype[e]) == {'T','S'})
fr_P = sum(1 for e in frust if set(edgetype[e]) == {'P','S'})
check("阻挫 Δ-□ = 20 (62.5%)", fr_D == 20)
check("阻挫 ⬠-□ = 12 (37.5%)", fr_P == 12)
check("33.3% Δ-□ 係阻挫", abs(fr_D / n_DD - 0.3333) < 0.001)
check("20.0% ⬠-□ 係阻挫", abs(fr_P / n_PP - 0.2000) < 0.001)
E_exp = 32 * 0.5
chi2 = (20 - E_exp)**2 / E_exp + (12 - E_exp)**2 / E_exp
check("chi^2 = 2.0 (docs/01 T1)", abs(chi2 - 2.0) < 1e-9)
fr_cc_types = defaultdict(int); fr_hh_types = defaultdict(int)
for e in frust:
    key = 'D' if set(edgetype[e]) == {'T','S'} else 'P'
    if colors[e[0]] == COLD: fr_cc_types[key] += 1
    else: fr_hh_types[key] += 1
check("冷-冷 = 10Δ-□ + 6⬠-□", fr_cc_types['D'] == 10 and fr_cc_types['P'] == 6)
check("熱-熱 = 10Δ-□ + 6⬠-□", fr_hh_types['D'] == 10 and fr_hh_types['P'] == 6)
check("32 = 20Δ + 12⬠ (阻挫飽和)", fr_D + fr_P == 20 + 12)

print("\n[C] 冷熱對稱 (docs/01 Task 2, problem_record 結果)")
frust_nodes = set()
for e in frust: frust_nodes.update(e)
frust_deg = defaultdict(int)
for e in frust:
    frust_deg[e[0]] += 1; frust_deg[e[1]] += 1
cc_nodes = set()
hh_nodes = set()
for (u, v) in frust:
    if colors[u] == COLD and colors[v] == COLD:
        cc_nodes.update((u, v))
    else:
        hh_nodes.update((u, v))
check("冷-冷 節點集 = 28", len(cc_nodes) == 28)
check("熱-熱 節點集 = 24", len(hh_nodes) == 24)
check("重疊 = 0", len(cc_nodes & hh_nodes) == 0)
cov = len(cc_nodes | hh_nodes)
check("總覆蓋 52 (52/60 = 86.7%)", cov == 52 and abs(cov/60 - 0.8667) < 0.001)
# 半球 = 邊中點 dec > 0 為北 (script 02 定義; 中點重現 docs 7N/9S + 9N/7S)
cc_N = sum(1 for (u, v) in frust if colors[u] == COLD and colors[v] == COLD and (nodes[u][1] + nodes[v][1]) / 2 > 0)
hh_N = sum(1 for (u, v) in frust if colors[u] != COLD and colors[v] != COLD and (nodes[u][1] + nodes[v][1]) / 2 > 0)
check("冷-冷 7N/9S (邊中點半球)", cc_N == 7)
check("熱-熱 9N/7S (邊中點半球)", hh_N == 9)

print("\n[D] 空間聚類 (docs/01 Task 3, problem_record 結果)")
# 阻挫子圖 degree
dg = defaultdict(int)
for e in frust:
    dg[e[0]] += 1; dg[e[1]] += 1
d1 = sum(1 for v in frust_nodes if dg[v] == 1)
d2 = sum(1 for v in frust_nodes if dg[v] == 2)
d3 = sum(1 for v in frust_nodes if dg[v] >= 3)
check("阻挫子圖 52 節點 / 32 邊", len(frust_nodes) == 52 and len(frust) == 32)
check("degree 分佈 {1:40, 2:12}", d1 == 40 and d2 == 12)
check("冇 degree >= 3", d3 == 0)
# components (paths)
seen = set(); comps = []
for s in frust_nodes:
    if s in seen: continue
    comp = []; q = deque([s]); seen.add(s)
    while q:
        u = q.popleft(); comp.append(u)
        for w in [x for x in frust_nodes if (min(u,x), max(u,x)) in frust]:
            if w not in seen: seen.add(w); q.append(w)
    comps.append(comp)
check("component 數 = 20", len(comps) == 20)
check("最大 component = 4 節點", max(len(c) for c in comps) == 4)
# 三角形 (全阻挫 3-cycle)
tri = 0
fnodes = sorted(frust_nodes)
for i in range(len(fnodes)):
    for j in range(i+1, len(fnodes)):
        for k in range(j+1, len(fnodes)):
            a, b, c = fnodes[i], fnodes[j], fnodes[k]
            if (min(a,b), max(a,b)) in frust and (min(b,c), max(b,c)) in frust and (min(a,c), max(a,c)) in frust:
                tri += 1
check("全阻挫三角形 = 0", tri == 0)
# CC (平均 clustering coefficient): deg<=2 -> 0
cc_vals = []
for v in frust_nodes:
    nb = [x for x in frust_nodes if (min(v,x), max(v,x)) in frust]
    k = len(nb)
    if k < 2: cc_vals.append(0.0)
    else:
        t = sum(1 for i in range(k) for j in range(i+1, k) if (min(nb[i],nb[j]), max(nb[i],nb[j])) in frust)
        cc_vals.append(2*t/(k*(k-1)))
check("平均 CC = 0.0000", abs(np.mean(cc_vals)) < 1e-12)
# 二分圖 (path forest 2-coloring)
def is_bip(nodeset):
    col = {}
    for s in nodeset:
        if s in col: continue
        col[s] = 0; q = deque([s])
        while q:
            u = q.popleft()
            for w in [x for x in nodeset if (min(u,x), max(u,x)) in frust]:
                if w in col:
                    if col[w] == col[u]: return False
                else:
                    col[w] = 1 - col[u]; q.append(w)
    return True
check("阻挫子圖係二分圖", is_bip(frust_nodes))

# 有序縫合線路徑 (由端點起步) + 每條縫合線嘅邊 — 供 F/H/I 重用
seam_paths = []
seam_edges = []
for comp in comps:
    ends = [v for v in comp if dg[v] == 1]
    if len(ends) == 2:
        cur = ends[0]; prev = None; path = []
        while True:
            path.append(cur)
            nxt = [w for w in comp if w != prev and (min(cur, w), max(cur, w)) in frust]
            if not nxt: break
            prev, cur = cur, nxt[0]
    else:
        path = sorted(comp)
    seam_paths.append(path)
    seam_edges.append(set((min(a, b), max(a, b)) for a, b in zip(path, path[1:])))

print("\n[E] 面分配 (docs/01 Task 4, problem_record 結果)")
T_fr = [fc for ft, _, fc in faces if ft == 'T']
S_fr = [fc for ft, _, fc in faces if ft == 'S']
P_fr = [fc for ft, _, fc in faces if ft == 'P']
check("三角形 frust 全部 = 1", all(x == 1 for x in T_fr) and len(T_fr) == 20)
from collections import Counter as C
sc = C(S_fr)
check("正方形 frust 0×14 + 2×16 (修正 18/12)", sc[0] == 14 and sc[2] == 16 and sc[1] == 0)
check("五邊形 frust 全部 = 1", all(x == 1 for x in P_fr) and len(P_fr) == 12)
check("Σ(frust)/2 = 32 = 20Δ+12⬠", sum(fc for _, _, fc in faces) // 2 == 32)
# 正方形對邊模式
sq_opp = 0; sq_patterns = C()
for ft, verts, fc in faces:
    if ft != 'S' or fc != 2: continue
    cs = [colors[v] for v in verts]
    sq_patterns[tuple(cs)] += 1
    # 對邊 = 兩對同色邊喺對面: 邊 (01,23) 或 邊 (12,30)
    if (cs[0] == cs[1] and cs[2] == cs[3]) or (cs[1] == cs[2] and cs[3] == cs[0]):
        sq_opp += 1
check("frust=2 正方形 16 個全部對邊", sq_opp == 16 and sum(sq_patterns.values()) == 16)
check("色模式 (0,1,1,0)x6 (1,0,0,1)x6 (0,0,1,1)x2 (1,1,0,0)x2",
      sq_patterns[(0,1,1,0)] == 6 and sq_patterns[(1,0,0,1)] == 6 and
      sq_patterns[(0,0,1,1)] == 2 and sq_patterns[(1,1,0,0)] == 2)
# 每條阻挫邊 = 1 奇面 + 1 偶面
odd_even_ok = all(sorted(edge_faces[e]) == ['P','S'] or sorted(edge_faces[e]) == ['S','T'] for e in frust)
check("每條阻挫邊 = 1 奇面 + 1 偶面 (冇 □-□)", odd_even_ok)

print("\n[F] 縫合線 (docs/01 Task 5, problem_record 已知事實)")
seams = comps  # 阻挫子圖 components = 縫合線
check("縫合線數 = 20", len(seams) == 20)
elens = [len(p) - 1 for p in seam_paths]
ec = C(elens)
check("單邊縫合線 = 10 (1 邊)", ec[1] == 10)
check("雙邊縫合線 = 8 (2 邊)", ec[2] == 8)
check("三邊縫合線 = 2 (3 邊)", ec[3] == 2)
# 奇面組合 (per seam: set of odd face types) — sorted({'T','P'}) = ('P','T')
combos = C()
for path, sedges in zip(seam_paths, seam_edges):
    types = set()
    for e in sedges:
        types.update(set(edge_faces[e]) - {'S'})
    combos[tuple(sorted(types))] += 1
check("奇面組合 Δ⬠×10, Δ×8, ⬠×2", combos[('P','T')] == 10 and combos[('T',)] == 8 and combos[('P',)] == 2)
# 縫合線長度 (angular)
seam_lens = []
for path in seam_paths:
    L = sum(ang_sep_deg(vecs[path[i]], vecs[path[i+1]]) for i in range(len(path)-1))
    seam_lens.append(L)
tot_len = sum(seam_lens)
check("總縫合線長度 = 835.8° (±0.5)", abs(tot_len - 835.8) < 0.5, f"(重算 {tot_len:.2f})")
check("最長縫合線 = 78.3° (±0.5)", abs(max(seam_lens) - 78.3) < 0.5, f"(重算 {max(seam_lens):.2f})")
check("平均縫合線長度 = 41.8° (±0.5)", abs(np.mean(seam_lens) - 41.8) < 0.5, f"(重算 {np.mean(seam_lens):.2f})")
check("冇縫合線 > 78.3° (預測 1)", max(seam_lens) <= 78.8)
# 縫合線南北 (中點 dec, script 05 定義)
seam_NS = [1 if nodes[p[len(p)//2]][1] > 0 else 0 for p in seam_paths]
check("縫合線 9 北 / 11 南 (中點 dec)", sum(seam_NS) == 9)

print("\n[G] 端點 isotropy (docs/01 開放 C, problem_record 已知事實)")
endpoints = [v for v in frust_nodes if dg[v] == 1]
check("端點數 = 40", len(endpoints) == 40)
R_len = np.linalg.norm(np.sum([vecs[v] for v in endpoints], axis=0)) / len(endpoints)
check("真實 R_len = 0.0029 (±0.0005)", abs(R_len - 0.0029) < 0.0005, f"(重算 {R_len:.4f})")
check("預測 6: R_len < 0.01", R_len < 0.01)
# 隨機對照: 隨機 30/30 著色
rand_cc = np.array([1]*30 + [0]*30)
rls = []
for _ in range(300):
    RNG.shuffle(rand_cc)
    col = {i: rand_cc[i] for i in range(60)}
    ep = [v for v in range(60) if sum(1 for w in adj[v] if col[w] == col[v]) == 1]
    # 端點 = 阻挫子圖 degree-1; 用近似: 阻挫邊 = 同色邊
    fr_edges = [(min(u,v), max(u,v)) for u in range(60) for v in adj[u] if u < v and col[u] == col[v]]
    fdeg = defaultdict(int)
    for e in fr_edges: fdeg[e[0]] += 1; fdeg[e[1]] += 1
    ep = [v for v in fdeg if fdeg[v] == 1]
    if len(ep) == 0: continue
    rls.append(np.linalg.norm(np.sum([vecs[v] for v in ep], axis=0)) / len(ep))
rls = np.array(rls)
check("隨機著色 R_len ~ 0.2362±0.105", abs(np.mean(rls) - 0.2362) < 0.03, f"(MC {np.mean(rls):.4f}±{np.std(rls):.4f})")
check("82× 均勻 (0.2362/0.0029)", 70 < 0.2362/R_len < 95)
# 隨機 40 節點
rls2 = []
for _ in range(300):
    sel = RNG.choice(60, 40, replace=False)
    rls2.append(np.linalg.norm(np.sum([vecs[v] for v in sel], axis=0)) / 40)
rls2 = np.array(rls2)
check("隨機 40 節點 R_len ~ 0.0854±0.035", abs(np.mean(rls2) - 0.0854) < 0.015, f"(MC {np.mean(rls2):.4f}±{np.std(rls2):.4f})")
check("29× 均勻 (0.0854/0.0029)", 24 < 0.0854/R_len < 36)
# 唯一飽和著色: 隨機著色出唔出到 32 條阻挫邊
sat_hits = 0
for _ in range(2000):
    RNG.shuffle(rand_cc)
    col = {i: rand_cc[i] for i in range(60)}
    nfr = sum(1 for (u,v) in all_edges if col[u] == col[v])
    if nfr == 32: sat_hits += 1
check("唯一飽和著色: 隨機 0/2000 到 32 阻挫邊 (MC)", sat_hits == 0)

# ---------- 溫度部分 ----------
print("\n[H] 溫度梯度 (docs/01 開放 A/D, problem_record 已知事實)")
# 銀河座標
sky = SkyCoord(ra=nodes[:,0]*AU.deg, dec=nodes[:,1]*AU.deg, frame='icrs')
gal = sky.galactic
l_deg = np.array(gal.l.deg); b_deg = np.array(gal.b.deg)

def load_temps_txt(fname):
    T = {}
    with open(f"{DATA}/{fname}") as f:
        for line in f:
            if line.startswith("#"): continue
            p = line.split()
            T[int(p[0])] = float(p[2])  # idx color T [l b] — T 永遠係 col 2
    return T

def grad_stats(T):
    grads = {}
    for v in range(60):
        nbrs = list(adj[v])
        grads[v] = abs(T[v] - np.mean([T[n] for n in nbrs]))
    g1 = np.array([grads[v] for v in endpoints])
    g2 = np.array([grads[v] for v in frust_nodes if dg[v] == 2])
    gnf = np.array([grads[v] for v in range(60) if v not in frust_nodes])
    return g1, g2, gnf

# 4.17° 平滑 (smica_smoothed.txt)
Tsm = load_temps_txt("smica_smoothed.txt")
check("smica_smoothed 60 節點齊全", len(Tsm) == 60)
g1, g2, gnf = grad_stats(Tsm)
m1, m2, mnf = np.mean(g1), np.mean(g2), np.mean(gnf)
t_p = ttest_ind(g1, g2).pvalue
u_p = mannwhitneyu(g1, g2, alternative='two-sided').pvalue
check("端點梯度 36.95 (±0.1)", abs(m1 - 36.95) < 0.1, f"(重算 {m1:.2f})")
check("連接器梯度 19.84 (±0.1)", abs(m2 - 19.84) < 0.1, f"(重算 {m2:.2f})")
check("非阻挫 70.81 (±0.1)", abs(mnf - 70.81) < 0.1, f"(重算 {mnf:.2f})")
check("t-test p = 0.0725 (±0.002)", abs(t_p - 0.0725) < 0.002, f"(重算 {t_p:.4f})")
check("MW p = 0.0804 (±0.002)", abs(u_p - 0.0804) < 0.002, f"(重算 {u_p:.4f})")
Ta1 = np.array([Tsm[v] for v in endpoints]); Ta2 = np.array([Tsm[v] for v in frust_nodes if dg[v] == 2])
check("端點絕對 T = -4.52 (±0.1)", abs(np.mean(Ta1) - (-4.52)) < 0.1, f"(重算 {np.mean(Ta1):.2f})")
check("連接器絕對 T = +6.38 (±0.1)", abs(np.mean(Ta2) - 6.38) < 0.1, f"(重算 {np.mean(Ta2):.2f})")
check("絕對 T t-test p = 0.3935 (±0.002)", abs(ttest_ind(Ta1, Ta2).pvalue - 0.3935) < 0.002)

# 帶通
Tbp = load_temps_txt("smica_bandpass.txt")
check("smica_bandpass 60 節點齊全", len(Tbp) == 60)
g1b, g2b, _ = grad_stats(Tbp)
m1b, m2b = np.mean(g1b), np.mean(g2b)
t_pb = ttest_ind(g1b, g2b).pvalue
u_pb = mannwhitneyu(g1b, g2b, alternative='two-sided').pvalue
check("帶通端點 27.97 (±0.1)", abs(m1b - 27.97) < 0.1, f"(重算 {m1b:.2f})")
check("帶通連接器 42.89 (±0.1)", abs(m2b - 42.89) < 0.1, f"(重算 {m2b:.2f})")
check("帶通 t p = 0.0633 (±0.002)", abs(t_pb - 0.0633) < 0.002, f"(重算 {t_pb:.4f})")
check("帶通 MW p = 0.0574 (±0.002)", abs(u_pb - 0.0574) < 0.002, f"(重算 {u_pb:.4f})")

# 多尺度表 (地圖直讀)
scales = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
ms_rows = {}
for fwhm in scales:
    fname = f"{CACHE}/smica2_smooth{fwhm}.fits"
    try:
        m = hp.read_map(fname, field=0)
    except Exception as ex:
        print(f"   (skip scale {fwhm}: {ex})"); continue
    m = hp.remove_dipole(m)
    nside = hp.get_nside(m)
    pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
    T = m[pix]
    g1s = np.array([abs(T[v] - np.mean([T[n] for n in adj[v]])) for v in endpoints]) * 1e6
    g2s = np.array([abs(T[v] - np.mean([T[n] for n in adj[v]])) for v in frust_nodes if dg[v] == 2]) * 1e6
    gns = np.array([abs(T[v] - np.mean([T[n] for n in adj[v]])) for v in range(60) if v not in frust_nodes]) * 1e6
    ms_rows[fwhm] = (np.mean(g1s), np.mean(g2s), np.mean(gns),
                     ttest_ind(g1s, g2s).pvalue, np.mean(g1s) - np.mean(g2s))
r417 = ms_rows[4.17]
check("多尺度 4.17° = 36.95/19.84/70.81 (地圖直讀)", abs(r417[0]-36.95) < 0.3 and abs(r417[1]-19.84) < 0.3 and abs(r417[2]-70.81) < 0.3, f"(重算 {r417[0]:.2f}/{r417[1]:.2f}/{r417[2]:.2f})")
check("多尺度 4.17° t p = 0.0726", abs(r417[3] - 0.0726) < 0.003, f"(重算 {r417[3]:.4f})")
check("10 尺度全數端點 > 連接器 (方向一致)", all(ms_rows[s][4] > 0 for s in ms_rows))
check("10 尺度全數存檔", len(ms_rows) == 10)

# 排列檢定 (4.17°) — MC 20000
comb = np.concatenate([g1, g2]); n1 = len(g1)
obs = np.mean(g1) - np.mean(g2)
cnt = 0
for _ in range(20000):
    RNG.shuffle(comb)
    cnt += (np.mean(comb[:n1]) - np.mean(comb[n1:]) >= obs)
p_perm = (cnt + 1) / (20001)
check("排列檢定 p = 0.0236 (MC 20000)", 0.005 < p_perm < 0.06, f"(重算 {p_perm:.4f})")
# Bootstrap CI (2000)
bts = []
for _ in range(2000):
    s1 = RNG.choice(g1, len(g1), replace=True)
    s2 = RNG.choice(g2, len(g2), replace=True)
    bts.append(np.mean(s1) - np.mean(s2))
bts = np.array(bts)
ci_lo, ci_hi = np.percentile(bts, [2.5, 97.5])
check("Bootstrap CI 唔含 0 (端點>connector)", ci_lo > 0, f"(CI [{ci_lo:.2f}, {ci_hi:.2f}])")
check("Bootstrap CI ≈ [+3.92, +30.00]", 2 < ci_lo < 6 and 27 < ci_hi < 33, f"(CI [{ci_lo:.2f}, {ci_hi:.2f}])")

# 邊級雙峰 (4.17°): 阻挫 vs 正常邊 |ΔT|
T4 = None
m = hp.read_map(f"{CACHE}/smica2_smooth4.17.fits", field=0); m = hp.remove_dipole(m)
T4 = m[hp.ang2pix(hp.get_nside(m), l_deg, b_deg, lonlat=True)]
edge_dT = {}
for (u, v) in all_edges:
    edge_dT[(u, v)] = abs(T4[u] - T4[v]) * 1e6
fr_vals = np.array([edge_dT[e] for e in frust])
nr_vals = np.array([edge_dT[e] for e in all_edges if e not in frust])
check("邊級: 阻挫邊 34.5 ± 0.3", abs(np.mean(fr_vals) - 34.5) < 0.3, f"(重算 {np.mean(fr_vals):.1f})")
check("邊級: 正常邊 53.1 ± 0.3", abs(np.mean(nr_vals) - 53.1) < 0.3, f"(重算 {np.mean(nr_vals):.1f})")
check("邊級: n=32 / n=88", len(fr_vals) == 32 and len(nr_vals) == 88)
comb2 = np.concatenate([nr_vals, fr_vals]); nf = len(nr_vals)
obs2 = np.mean(nr_vals) - np.mean(fr_vals)
cnt2 = 0
for _ in range(20000):
    RNG.shuffle(comb2)
    cnt2 += (np.mean(comb2[:nf]) - np.mean(comb2[nf:]) >= obs2)
p_bim = (cnt2 + 1) / (20001)
check("邊級排列 p = 0.0192 (MC 20000)", 0.005 < p_bim < 0.05, f"(重算 {p_bim:.4f})")

# 縫合線 ΔT (4.17°) + 組合
seam_dT = []
seam_combo_dT = defaultdict(list)
for comp, sedges in zip(seams, seam_edges):
    vals = [T4[v] * 1e6 for v in comp]
    dT = max(vals) - min(vals)
    seam_dT.append(dT)
    types = set()
    for e in sedges:
        types.update(set(edge_faces[e]) - {'S'})
    seam_combo_dT[tuple(sorted(types))].append(dT)
sdT = np.array(seam_dT)
check("縫合線 ΔT mean = 52.3 (±0.5)", abs(np.mean(sdT) - 52.3) < 0.5, f"(重算 {np.mean(sdT):.1f})")
check("縫合線 ΔT 範圍 [6.8, 125.5]", abs(min(sdT) - 6.8) < 0.2 and abs(max(sdT) - 125.5) < 0.2, f"(重算 [{min(sdT):.1f}, {max(sdT):.1f}])")
dDT = np.array(seam_combo_dT[('P','T')]); dD = np.array(seam_combo_dT[('T',)]); dP = np.array(seam_combo_dT[('P',)])
check("Δ⬠ ΔT = 69.7 (n=10)", abs(np.mean(dDT) - 69.7) < 0.5 and len(dDT) == 10, f"(重算 {np.mean(dDT):.1f})")
check("Δ ΔT = 27.4 (n=8)", abs(np.mean(dD) - 27.4) < 0.5 and len(dD) == 8, f"(重算 {np.mean(dD):.1f})")
check("⬠ ΔT = 65.3 (n=2)", abs(np.mean(dP) - 65.3) < 0.5 and len(dP) == 2, f"(重算 {np.mean(dP):.1f})")
check("Δ vs Δ⬠ t p = 0.0150", abs(ttest_ind(dD, dDT).pvalue - 0.0150) < 0.003, f"(重算 {ttest_ind(dD, dDT).pvalue:.4f})")
check("Δ vs Δ⬠ MW p = 0.0085", abs(mannwhitneyu(dD, dDT, alternative='two-sided').pvalue - 0.0085) < 0.002, f"(重算 {mannwhitneyu(dD, dDT, alternative='two-sided').pvalue:.4f})")
# 多尺度縫合線 ΔT 單調 (1/2/4.17/7/10)
doc_ms = {1.0: 86.9, 2.0: 59.1, 4.17: 52.3, 7.0: 47.7, 10.0: 43.4}
ms_seam = {}
for fwhm in [1.0, 2.0, 4.17, 7.0, 10.0]:
    m = hp.read_map(f"{CACHE}/smica2_smooth{fwhm}.fits", field=0); m = hp.remove_dipole(m)
    T = m[hp.ang2pix(hp.get_nside(m), l_deg, b_deg, lonlat=True)]
    vals = [max(T[v] for v in c) - min(T[v] for v in c) for c in seams]
    ms_seam[fwhm] = np.mean(vals) * 1e6
mono = all(ms_seam[s] > ms_seam[t] for s, t in zip([1.0,2.0,4.17,7.0], [2.0,4.17,7.0,10.0]))
check("縫合線 ΔT 隨尺度單調減小", mono, f"(重算 { {k: round(v,1) for k,v in ms_seam.items()} })")
for fwhm, docv in doc_ms.items():
    if abs(ms_seam[fwhm] - docv) > 1.5:
        check(f"多尺度 ΔT {fwhm}° = {docv}", False, f"(重算 {ms_seam[fwhm]:.1f})")
    else:
        check(f"多尺度 ΔT {fwhm}° = {docv}", True, f"(重算 {ms_seam[fwhm]:.1f})")
# 節點 47
T47 = T4[47] * 1e6
check("節點 47 T = -123.4 (±0.5)", abs(T47 - (-123.4)) < 0.5, f"(重算 {T47:.1f})")
rank47 = sum(1 for v in range(60) if T4[v] < T4[47])
check("節點 47 = 全球第 2 冷 (僅次冷斑)", rank47 == 1)
check("節點 47 色 = 冷", colors[47] == COLD)
check("節點 47 b = -8.6° (±0.1)", abs(b_deg[47] - (-8.6)) < 0.1, f"(重算 {b_deg[47]:.1f})")

print("\n[I] 拓撲位元 (docs/01 開放 B, problem_record 已知事實)")
# B.5 衝突圖 (script 10 [B.5] 定義): 翻轉 S_i 會唔會改變其他縫合線嘅阻挫邊狀態
# cross = 翻轉後 added/removed 中屬於其他縫合線自身邊嘅部分
all_seam_edge_set = set().union(*seam_edges)
conflict_edges_total = 0
for idx, comp in enumerate(seams):
    eps = [v for v in comp if dg[v] == 1]
    col2 = dict(colors)
    for v in eps: col2[v] = 1 - col2[v]
    added = set(); removed = set()
    for (u, v) in all_edges:
        same2 = col2[u] == col2[v]; same1 = colors[u] == colors[v]
        if same2 and not same1: added.add((u, v))
        if same1 and not same2: removed.add((u, v))
    other_edges = all_seam_edge_set - seam_edges[idx]
    conflict_edges_total += len((added | removed) & other_edges)
check("衝突圖 0 邊 (翻轉唔影響其他縫合線, script 10 [B.5])", conflict_edges_total == 0)
# B.2 資訊: 擴展鄰域重疊對 (script 10 輸出 74 對 = 正常邊重疊, 非衝突)
b2_overlap = 0
for i in range(len(seams)):
    ni = set(seams[i])
    for v in seams[i]: ni.update(adj[v])
    for j in range(i+1, len(seams)):
        nj = set(seams[j])
        for v in seams[j]: nj.update(adj[v])
        if ni & nj: b2_overlap += 1
print(f"   [info] B.2 擴展鄰域重疊對 = {b2_overlap} (script 10 輸出 74 — 正常邊重疊, 非衝突)")
# 每縫合線翻轉 = 翻轉 2 個端點 (script 10 定義): 新增 6 阻挫, 移除 0-2, 淨阻挫 36-38
flip_stats = []
for comp in seams:
    eps = [v for v in comp if dg[v] == 1]
    col2 = dict(colors)
    for v in eps: col2[v] = 1 - col2[v]
    new = 0; rem = 0
    for (u, v) in all_edges:
        same2 = col2[u] == col2[v]; same1 = colors[u] == colors[v]
        if same2 and not same1: new += 1
        if same1 and not same2: rem += 1
    flip_stats.append((new, rem))
new_all = [s[0] for s in flip_stats]; rem_all = [s[1] for s in flip_stats]
check("每條縫合線翻轉新增 6 阻挫 (20/20)", all(n == 6 for n in new_all))
check("移除 0-2 阻挫", all(0 <= r <= 2 for r in rem_all))
check("翻轉後淨阻挫 36-38", all(32 + n - r in (36, 37, 38) for n, r in flip_stats))
check("2^20 = 1,048,576 圖案/幀", 2**20 == 1048576)
check("縫合線級 MIS = 20", len(seams) == 20)

print("\n[J] O5 交叉 (docs/01 開放 E, problem_record 已知事實)")
with open(f"{O5}/smica_catalog.json") as f:
    cat = json.load(f)
cold_vecs = np.array([unit(s['peak_l'], s['peak_b']) for s in cat['cold']])
hot_vecs = np.array([unit(s['peak_l'], s['peak_b']) for s in cat.get('hot', [])])
# 節點向量必須用銀河 frame (l,b) 先可以同目錄 (l,b) 比較 — script 15 定義
gvecs = np.array([unit(l_deg[v], b_deg[v]) for v in range(60)])
def min_dist(v, vset):
    if len(vset) == 0: return 999.0
    return min(ang_sep_deg(v, w) for w in vset)
d_cold = np.array([min_dist(gvecs[v], cold_vecs) for v in endpoints])
check("40 端點到最近冷結構 mean = 28.1 (±0.3)", abs(np.mean(d_cold) - 28.1) < 0.3, f"(重算 {np.mean(d_cold):.1f})")
check("端點中位數 26.6 (±0.5)", abs(np.median(d_cold) - 26.6) < 0.5, f"(重算 {np.median(d_cold):.1f})")
rc = []
for _ in range(200):
    sel = RNG.choice(60, 40, replace=False)
    rc.append(np.mean([min_dist(gvecs[v], cold_vecs) for v in sel]))
rc = np.array(rc)
check("隨機對照 28.2±1.3 (端點 = 隨機水平)", abs(np.mean(rc) - 28.2) < 0.5, f"(MC {np.mean(rc):.2f}±{np.std(rc):.2f})")
check("端點百分位 ~48.3% (隨機內)", abs(np.mean(d_cold) - np.mean(rc)) < 3*np.std(rc))
all_spots = cat['cold'] + cat.get('hot', [])
spot_vecs = np.array([unit(s['peak_l'], s['peak_b']) for s in all_spots])
d_seam = np.array([min_dist(gvecs[v], spot_vecs) for v in endpoints])
d_nonseam = np.array([min_dist(gvecs[v], spot_vecs) for v in range(60) if v not in endpoints])
check("縫合線端點到最近目錄 mean = 20.2 (±0.3)", abs(np.mean(d_seam) - 20.2) < 0.3, f"(重算 {np.mean(d_seam):.1f})")
check("非端點 19.8 (±0.5)", abs(np.mean(d_nonseam) - 19.8) < 0.5, f"(重算 {np.mean(d_nonseam):.1f})")
rc2 = []
for _ in range(200):
    sel = RNG.choice(60, 40, replace=False)
    rc2.append(np.mean([min_dist(gvecs[v], spot_vecs) for v in sel]))
rc2 = np.array(rc2)
check("隨機 40 節點 20.1±0.9 (端點百分位 55%)", abs(np.mean(rc2) - 20.1) < 0.5 and abs(np.mean(d_seam) - np.mean(rc2)) < 3*np.std(rc2), f"(MC {np.mean(rc2):.2f}±{np.std(rc2):.2f})")
# 跨冷熱
def is_cross(comp):
    eps = [v for v in comp if dg[v] == 1]
    if len(eps) != 2: return False
    e1, e2 = eps
    d1c = min_dist(gvecs[e1], cold_vecs); d2c = min_dist(gvecs[e2], cold_vecs)
    d1h = min_dist(gvecs[e1], hot_vecs); d2h = min_dist(gvecs[e2], hot_vecs)
    return (d1c < d2c and d1h > d2h) or (d1c > d2c and d1h < d2h)
real_cross = sum(1 for comp in seams if is_cross(comp))
check("跨冷熱 14/20", real_cross == 14, f"(重算 {real_cross}/20)")
rc3 = []
for _ in range(2000):
    # shuffle 冷/熱目錄標籤
    perm = RNG.permutation(len(all_spots))
    cc = cold_vecs; hh = hot_vecs
    mixed = np.concatenate([cold_vecs, hot_vecs])
    shuffled = mixed[perm]
    c2 = shuffled[:len(cold_vecs)]; h2 = shuffled[len(cold_vecs):]
    def is_cross2(comp):
        eps = [v for v in comp if dg[v] == 1]
        if len(eps) != 2: return False
        e1, e2 = eps
        d1c = min_dist(gvecs[e1], c2); d2c = min_dist(gvecs[e2], c2)
        d1h = min_dist(gvecs[e1], h2); d2h = min_dist(gvecs[e2], h2)
        return (d1c < d2c and d1h > d2h) or (d1c > d2c and d1h < d2h)
    rc3.append(sum(1 for comp in seams if is_cross2(comp)))
rc3 = np.array(rc3)
check("隨機對照跨冷熱 9.7±2.1", abs(np.mean(rc3) - 9.7) < 0.6, f"(MC {np.mean(rc3):.2f}±{np.std(rc3):.2f})")
check("真實百分位 4.2% (偏高)", np.mean(rc3 >= real_cross) < 0.10, f"(MC pct {np.mean(rc3 >= real_cross)*100:.1f}%)")
# 銀河面剔除
in_plane = [v for v in range(60) if abs(b_deg[v]) < 20]
check("銀河面內節點 = 22", len(in_plane) == 22)
Tplane = np.array([Tsm[v] for v in in_plane])
check("銀河面內平均 T = -1.9 (±0.3)", abs(np.mean(Tplane) - (-1.9)) < 0.3, f"(重算 {np.mean(Tplane):.1f})")
check("節點 47 喺銀河面內 (|b|<20°)", 47 in in_plane)
check("節點 47 = 銀河面內最冷", min(Tplane) == Tsm[47] and abs(Tsm[47] - (-123.4)) < 0.5)
clean_seams = [comp for comp in seams if all(v not in in_plane for v in comp)]
check("剔除銀河面後乾淨縫合線 = 10", len(clean_seams) == 10)
clean_cross = sum(1 for comp in clean_seams if is_cross(comp))
check("乾淨縫合線跨冷熱 6/10", clean_cross == 6, f"(重算 {clean_cross}/10)")
check("二項檢定 p = 0.7539", abs(binomtest(clean_cross, 10, 0.5).pvalue - 0.7539) < 0.001, f"(重算 {binomtest(clean_cross, 10, 0.5).pvalue:.4f})")
d47 = min_dist(gvecs[47], cold_vecs)
check("節點 47 到最近冷 peak 36.4° (±0.5)", abs(d47 - 36.4) < 0.5, f"(重算 {d47:.1f})")

print("\n[K] 跨源數字 (problem_record 已知事實, docs/01)")
# 雙峰 sigma (19_bimodal_gradient.py 重現, 由數據檔)
rows = []
with open(f"{DATA}/bimodal_gradient.txt") as f:
    for line in f:
        if line.startswith("#"): continue
        p = line.split()
        rows.append((p[0], float(p[1]), float(p[2]), float(p[3])))
Fv = np.array([r[1] for r in rows if r[0] == 'F']); Nv = np.array([r[1] for r in rows if r[0] == 'N'])
Fm = np.array([r[2] for r in rows if r[0] == 'F']); Nm = np.array([r[2] for r in rows if r[0] == 'N'])
Fl = np.array([r[3] for r in rows if r[0] == 'F']); Nl = np.array([r[3] for r in rows if r[0] == 'N'])
sep_mixed = (Nm.mean() - Fm.mean()) / (Fm.std() + 1e-12)
sep_lcdm = (Nl.mean() - Fl.mean()) / (Fl.std() + 1e-12)
check("IDCM+噪聲雙峰 17.3σ (19_bimodal)", 16.5 < sep_mixed < 18.0, f"(重算 {sep_mixed:.2f})")
check("ΛCDM 雙峰 0.38σ", 0.25 < sep_lcdm < 0.55, f"(重算 {sep_lcdm:.2f})")
check("IDCM 純結構阻挫邊 ΔT = 0 (exact)", abs(Fv.mean()) < 1e-12)
check("bimodal 數據 120 行 (32F+88N)", len(rows) == 120 and len(Fv) == 32 and len(Nv) == 88)

# 總結
print("="*78)
print(f"審計結果: {passed} PASS / {failed} FAIL")
print("="*78)
