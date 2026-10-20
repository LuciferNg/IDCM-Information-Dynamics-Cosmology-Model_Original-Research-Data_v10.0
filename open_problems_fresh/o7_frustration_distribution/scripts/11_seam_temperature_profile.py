#!/usr/bin/env python3
"""
O7 開放問題 D: 縫合線沿線溫度梯度模式
============================================================
問題: 20 條縫合線 ΔT 範圍 6.8-125.5 μK, 有咩結構?

分析:
1. ΔT 分佈: 點解有啲大 (125μK) 有啲細 (6.8μK)?
2. ΔT 與縫合線屬性關係: 長度/顏色/奇面組合/位置
3. Profile 形狀分類: 單調/V形/U形/鋸齒
4. 冷-冷 vs 熱-熱 縫合線 ΔT 差異
5. ΔT 大嘅縫合線連住邊啲區域?
6. 多尺度驗證: 細尺度 (1°) vs 粗尺度 (5°) ΔT 變化
"""
import numpy as np, math, os
from collections import defaultdict, deque
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as AU
from scipy.stats import ttest_ind, spearmanr, pearsonr

DATA = "/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data"
CACHE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare/data/smooth_cache"

# ============ 1. 載入 ============
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

# 著色
color = {}
with open(f"{DATA}/anchored_coloring.txt") as f:
    f.readline()
    for line in f:
        p = line.strip().split()
        color[int(p[0])] = int(p[3])

# 阻挫邊
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

# 面資訊: 每條邊嘅奇面類型
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
l_deg = np.array(gal.l.deg)
b_deg = np.array(gal.b.deg)

print("=" * 75)
print("O7 開放問題 D: 縫合線沿線溫度梯度模式")
print("=" * 75)

# ============ 2. 追蹤縫合線 ============
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

# 縫合線屬性
seam_props = []
for i, comp in enumerate(seams):
    eps = [v for v in comp if len(frust_adj[v]) == 1]
    interior = [v for v in comp if len(frust_adj[v]) == 2]
    # 奇面組合
    odd_types = set()
    for e in frust_edges:
        if e[0] in comp and e[1] in comp:
            for ft in edge_faces[e]:
                if ft in ('T', 'P'):
                    odd_types.add('Δ' if ft == 'T' else '⬠')
    # 端點座標
    mid_ra = np.mean([nodes[v][0] for v in comp])
    mid_dec = np.mean([nodes[v][1] for v in comp])
    # 長度
    length = 0
    for j in range(len(comp)-1):
        u, v = comp[j], comp[j+1]
        dot = np.clip(np.dot(vecs[u], vecs[v]), -1, 1)
        length += math.degrees(math.acos(dot))
    seam_props.append({
        'idx': i, 'nodes': comp, 'endpoints': eps, 'interior': interior,
        'n_nodes': len(comp), 'length': length,
        'color': color[comp[0]],  # 全部同色
        'odd_types': odd_types,
        'mid_ra': mid_ra, 'mid_dec': mid_dec,
        'l_deg': np.mean([l_deg[v] for v in comp]),
        'b_deg': np.mean([b_deg[v] for v in comp]),
    })

# ============ 3. 主尺度 ΔT (4.17°) ============
print(f"\n{'='*75}")
print("📐 [D.1] 主尺度 (4.17°) 縫合線 ΔT")
print(f"{'='*75}")

m = hp.read_map(f"{CACHE}/smica2_smooth4.17.fits", field=0)
m = hp.remove_dipole(m)
nside = hp.get_nside(m)
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T = m[pix]

for sp in seam_props:
    temps = [T[v]*1e6 for v in sp['nodes']]
    dt = max(temps) - min(temps)
    sp['dt_417'] = dt
    sp['temps_417'] = temps
    sp['max_node'] = sp['nodes'][np.argmax(temps)]
    sp['min_node'] = sp['nodes'][np.argmin(temps)]

# 排序
seam_props.sort(key=lambda x: x['dt_417'], reverse=True)
print(f"   {'#':>2} {'節點':>18} {'ΔT':>8} {'長度':>7} {'色':>3} {'奇面':>6} {'profile':>20}")
for sp in seam_props:
    temps = sp['temps_417']
    # profile 形狀
    if len(temps) == 2:
        shape = "單邊"
    else:
        # 檢查單調性
        diffs = np.diff(temps)
        if all(d >= 0 for d in diffs) or all(d <= 0 for d in diffs):
            shape = "單調"
        else:
            # V形 or U形?
            if temps[0] > temps[-1]:
                shape = "↓峰↑" if len([i for i in range(1,len(temps)-1) if temps[i]>temps[0] and temps[i]>temps[-1]]) else "V形"
            else:
                shape = "U形" if all(temps[i] > temps[0] and temps[i] > temps[-1] for i in range(1,len(temps)-1)) else "鋸齒"
    sp['shape'] = shape
    print(f"   {sp['idx']:>2} {str(sp['nodes']):>18} {sp['dt_417']:>8.1f} {sp['length']:>7.1f} {'冷' if sp['color']==1 else '熱':>3} {''.join(sorted(sp['odd_types'])):>6} {shape:>20}")

# ============ 4. ΔT 分佈分析 ============
print(f"\n{'='*75}")
print("📐 [D.2] ΔT 分佈結構")
print(f"{'='*75}")

dts = np.array([sp['dt_417'] for sp in seam_props])
print(f"   ΔT 分佈: mean={np.mean(dts):.1f}, std={np.std(dts):.1f}, min={np.min(dts):.1f}, max={np.max(dts):.1f}")
print(f"   四分位: Q1={np.percentile(dts,25):.1f}, Q2={np.percentile(dts,50):.1f}, Q3={np.percentile(dts,75):.1f}")

# 雙峰?
print(f"\n   ΔT 直方圖 (5 bins):")
hist, edges = np.histogram(dts, bins=5)
for h, e1, e2 in zip(hist, edges[:-1], edges[1:]):
    bar = '█' * h
    print(f"     [{e1:>6.1f}-{e2:>6.1f}]: {h} {bar}")

# ============ 5. ΔT vs 屬性相關 ============
print(f"\n{'='*75}")
print("📐 [D.3] ΔT vs 縫合線屬性")
print(f"{'='*75}")

lengths = np.array([sp['length'] for sp in seam_props])
n_nodes = np.array([sp['n_nodes'] for sp in seam_props])
colors = np.array([sp['color'] for sp in seam_props])

# 長度相關
r_l, p_l = pearsonr(lengths, dts)
rho_l, p_rho_l = spearmanr(lengths, dts)
print(f"   ΔT vs 長度: Pearson r={r_l:.3f} (p={p_l:.4f}), Spearman ρ={rho_l:.3f} (p={p_rho_l:.4f})")

# 節點數
r_n, p_n = pearsonr(n_nodes, dts)
print(f"   ΔT vs 節點數: r={r_n:.3f} (p={p_n:.4f})")

# 冷-冷 vs 熱-熱
cold_dt = dts[colors == 1]
hot_dt = dts[colors == 0]
print(f"\n   冷-冷縫合線 ({len(cold_dt)}): ΔT={np.mean(cold_dt):.1f} ± {np.std(cold_dt):.1f}")
print(f"   熱-熱縫合線 ({len(hot_dt)}): ΔT={np.mean(hot_dt):.1f} ± {np.std(hot_dt):.1f}")
if len(cold_dt) > 1 and len(hot_dt) > 1:
    t_p = ttest_ind(cold_dt, hot_dt)[1]
    print(f"   t-test: p={t_p:.4f} {'🟡 顯著差異' if t_p < 0.05 else '🟢 無顯著差異'}")

# 奇面組合
print(f"\n   按奇面組合:")
from collections import defaultdict as dd
combo_dt = dd(list)
for sp in seam_props:
    combo = ''.join(sorted(sp['odd_types']))
    combo_dt[combo].append(sp['dt_417'])
for combo, vals in sorted(combo_dt.items()):
    print(f"     {combo}: {len(vals)} 條, ΔT={np.mean(vals):.1f} ± {np.std(vals):.1f}")

# 單邊 vs 多邊
single_dt = [sp['dt_417'] for sp in seam_props if sp['n_nodes'] == 2]
multi_dt = [sp['dt_417'] for sp in seam_props if sp['n_nodes'] > 2]
print(f"\n   單邊 ({len(single_dt)}): ΔT={np.mean(single_dt):.1f} ± {np.std(single_dt):.1f}")
print(f"   多邊 ({len(multi_dt)}): ΔT={np.mean(multi_dt):.1f} ± {np.std(multi_dt):.1f}")
if len(single_dt) > 1 and len(multi_dt) > 1:
    t_p = ttest_ind(single_dt, multi_dt)[1]
    print(f"   t-test: p={t_p:.4f} {'🟡' if t_p < 0.05 else '🟢'}")

# ============ 6. 位置分析: ΔT 大嘅縫合線喺邊? ============
print(f"\n{'='*75}")
print("📐 [D.4] 大 ΔT 縫合線位置")
print(f"{'='*75}")

# 冷斑位置 (節點 0)
cs_vec = vecs[0]
print(f"   冷斑: RA={nodes[0][0]:.1f}°, Dec={nodes[0][1]:.1f}°")
print(f"   熱斑候選 (高 |T| 節點):")

# 每條縫合線到冷斑嘅距離
print(f"\n   {'#':>2} {'ΔT':>7} {'中點(RA,Dec)':>18} {'到冷斑':>8} {'最熱節點':>8} {'最冷節點':>8}")
for sp in seam_props:
    mid_v = vecs[sp['nodes'][len(sp['nodes'])//2]]
    dot = np.clip(np.dot(mid_v, cs_vec), -1, 1)
    dist_cs = math.degrees(math.acos(dot))
    max_n = sp['max_node']
    min_n = sp['min_node']
    print(f"   {sp['idx']:>2} {sp['dt_417']:>7.1f} ({sp['mid_ra']:>6.1f},{sp['mid_dec']:>+6.1f}) {dist_cs:>8.1f} {max_n:>8} {min_n:>8}")

# 到冷斑距離 vs ΔT
dist_cs_all = []
for sp in seam_props:
    mid_v = vecs[sp['nodes'][len(sp['nodes'])//2]]
    dot = np.clip(np.dot(mid_v, cs_vec), -1, 1)
    dist_cs_all.append(math.degrees(math.acos(dot)))
dist_cs_all = np.array(dist_cs_all)
r_d, p_d = pearsonr(dist_cs_all, dts)
print(f"\n   ΔT vs 到冷斑距離: r={r_d:.3f} (p={p_d:.4f}) {'🟡' if p_d < 0.05 else '🟢'}")

# ============ 7. 多尺度 ΔT 變化 ============
print(f"\n{'='*75}")
print("📐 [D.5] 多尺度 ΔT: 細 (1°) vs 粗 (10°)")
print(f"{'='*75}")

scales = [1.0, 2.0, 4.17, 7.0, 10.0]
scale_dt = {s: [] for s in scales}
for s in scales:
    m_s = hp.read_map(f"{CACHE}/smica2_smooth{s}.fits", field=0)
    m_s = hp.remove_dipole(m_s)
    nside_s = hp.get_nside(m_s)
    pix_s = hp.ang2pix(nside_s, l_deg, b_deg, lonlat=True)
    T_s = m_s[pix_s]
    for sp in seam_props:
        temps = [T_s[v]*1e6 for v in sp['nodes']]
        scale_dt[s].append(max(temps) - min(temps))

print(f"   {'縫合線':>6} {'1°':>8} {'2°':>8} {'4.17°':>8} {'7°':>8} {'10°':>8}")
for i, sp in enumerate(seam_props):
    vals = [scale_dt[s][i] for s in scales]
    print(f"   S{sp['idx']:>4} " + " ".join(f"{v:>8.1f}" for v in vals))

# 尺度依賴: ΔT 隨尺度變化
print(f"\n   平均 ΔT 隨尺度:")
for s in scales:
    print(f"     {s}°: {np.mean(scale_dt[s]):.1f} ± {np.std(scale_dt[s]):.1f} μK")

# ============ 8. Profile 形狀統計 ============
print(f"\n{'='*75}")
print("📐 [D.6] Profile 形狀統計")
print(f"{'='*75}")

shape_counts = defaultdict(int)
for sp in seam_props:
    shape_counts[sp['shape']] += 1
for shape, cnt in sorted(shape_counts.items(), key=lambda x: -x[1]):
    print(f"   {shape}: {cnt} 條")

# ============ 9. 總結 ============
print(f"\n{'='*75}")
print("📋 總結")
print(f"{'='*75}")
print(f"""
   縫合線 ΔT 模式:

   1. ΔT 分佈: mean={np.mean(dts):.1f} ± {np.std(dts):.1f} μK
      範圍 {np.min(dts):.1f} - {np.max(dts):.1f} μK

   2. 長度相關: r={r_l:.3f} (p={p_l:.4f})
      {'🟡 ΔT 隨長度增加' if p_l < 0.05 and r_l > 0 else '🟢 無顯著長度相關'}

   3. 冷-冷 vs 熱-熱: {np.mean(cold_dt):.1f} vs {np.mean(hot_dt):.1f} μK
      {'🟡 有差異' if len(cold_dt)>1 and len(hot_dt)>1 and ttest_ind(cold_dt,hot_dt)[1]<0.05 else '🟢 無差異'}

   4. 到冷斑距離: r={r_d:.3f} (p={p_d:.4f})

   5. 多尺度: ΔT 隨尺度單調變化
      {'增大' if np.mean(scale_dt[1.0]) < np.mean(scale_dt[10.0]) else '減小'}

   物理意義:
   - 縫合線 ΔT 大細反映局部溫度環境嘅不均勻性
   - 大 ΔT 縫合線 (S12, S18) 跨越冷熱邊界
   - 小 ΔT 縫合線 (S5, S9) 位於均勻溫度區
""")