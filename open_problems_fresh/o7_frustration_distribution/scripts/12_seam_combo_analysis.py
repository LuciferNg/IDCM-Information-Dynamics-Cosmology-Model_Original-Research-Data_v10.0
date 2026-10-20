#!/usr/bin/env python3
"""
O7 開放問題 D 深入: 奇面組合 ΔT 差異 + S18 冷斑關聯
============================================================
發現:
- Δ⬠ 縫合線 ΔT=69.7 vs Δ-only ΔT=27.4 (2.5×!)
- 多邊 (69.7) vs 單邊 (34.9), p=0.031
- S18 (ΔT=125.5) 端點 47 靠近冷斑區?

問題:
1. Δ⬠ vs Δ-only 差異統計顯著性?
2. 控制長度/節點數後, 奇面組合仲有冇效應?
3. S18 嘅節點 47 係咪喺冷斑附近?
4. 縫合線端點溫度 (唔係 ΔT) 有冇奇面組合差異?
"""
import numpy as np, math
from collections import defaultdict, deque
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as AU
from scipy.stats import ttest_ind, mannwhitneyu, pearsonr, spearmanr

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

sc = SkyCoord(ra=nodes[:, 0]*AU.deg, dec=nodes[:, 1]*AU.deg, frame='icrs')
gal = sc.galactic
l_deg = np.array(gal.l.deg)
b_deg = np.array(gal.b.deg)

print("=" * 75)
print("O7 開放問題 D 深入: 奇面組合 + S18 分析")
print("=" * 75)

# ============ 2. 縫合線 ============
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

# 讀溫度 (4.17°)
m = hp.read_map(f"{CACHE}/smica2_smooth4.17.fits", field=0)
m = hp.remove_dipole(m)
nside = hp.get_nside(m)
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T = m[pix]

seam_data = []
for i, comp in enumerate(seams):
    eps = [v for v in comp if len(frust_adj[v]) == 1]
    odd_types = set()
    for e in frust_edges:
        if e[0] in comp and e[1] in comp:
            for ft in edge_faces[e]:
                if ft in ('T', 'P'):
                    odd_types.add('Δ' if ft == 'T' else '⬠')
    combo = ''.join(sorted(odd_types))
    temps = [T[v]*1e6 for v in comp]
    ep_temps = [T[v]*1e6 for v in eps]
    seam_data.append({
        'idx': i, 'nodes': comp, 'endpoints': eps, 'combo': combo,
        'n_nodes': len(comp), 'dt': max(temps)-min(temps),
        'mean_T': np.mean(temps), 'ep_mean': np.mean(ep_temps),
        'max_ep_T': max(ep_temps), 'min_ep_T': min(ep_temps),
    })

# ============ 3. Δ⬠ vs Δ-only 檢定 ============
print(f"\n{'='*75}")
print("📐 [D.3a] 奇面組合 ΔT 差異")
print(f"{'='*75}")

combos = defaultdict(list)
for sd in seam_data:
    combos[sd['combo']].append(sd)

for combo, lst in sorted(combos.items()):
    dts = [x['dt'] for x in lst]
    print(f"   {combo}: {len(lst)} 條, ΔT={np.mean(dts):.1f} ± {np.std(dts):.1f} μK")

if len(combos.get('Δ', [])) >= 2 and len(combos.get('Δ⬠', [])) >= 2:
    dt_d = [x['dt'] for x in combos['Δ']]
    dt_dp = [x['dt'] for x in combos['Δ⬠']]
    t_p = ttest_ind(dt_d, dt_dp)[1]
    u_p = mannwhitneyu(dt_d, dt_dp)[1]
    print(f"\n   Δ (n={len(dt_d)}) vs Δ⬠ (n={len(dt_dp)}):")
    print(f"   t-test: p={t_p:.4f} {'🟡 顯著!' if t_p < 0.05 else '🟢 未達顯著'}")
    print(f"   MW U-test: p={u_p:.4f} {'🟡 顯著!' if u_p < 0.05 else '🟢 未達顯著'}")

# ============ 4. 控制節點數後嘅組合效應 ============
print(f"\n{'='*75}")
print("📐 [D.3b] 控制節點數: 單邊 Δ vs 單邊 ⬠")
print(f"{'='*75}")

# 只有單邊 (n_nodes=2) 嘅縫合線
single_seams = [sd for sd in seam_data if sd['n_nodes'] == 2]
print(f"   單邊縫合線: {len(single_seams)} 條")
for sd in single_seams:
    print(f"     S{sd['idx']}: {sd['combo']} ΔT={sd['dt']:.1f}")

# 單邊 Δ vs 單邊 ⬠
sd_d = [x['dt'] for x in single_seams if x['combo'] == 'Δ']
sd_p = [x['dt'] for x in single_seams if x['combo'] == '⬠']
if len(sd_d) >= 2 and len(sd_p) >= 2:
    t_p = ttest_ind(sd_d, sd_p)[1]
    print(f"\n   單邊 Δ ({len(sd_d)}): ΔT={np.mean(sd_d):.1f} ± {np.std(sd_d):.1f}")
    print(f"   單邊 ⬠ ({len(sd_p)}): ΔT={np.mean(sd_p):.1f} ± {np.std(sd_p):.1f}")
    print(f"   t-test: p={t_p:.4f} {'🟡 顯著!' if t_p < 0.05 else '🟢 未達顯著'}")

# 多邊全部係 Δ⬠? 檢查
multi_seams = [sd for sd in seam_data if sd['n_nodes'] > 2]
multi_combos = defaultdict(int)
for sd in multi_seams:
    multi_combos[sd['combo']] += 1
print(f"\n   多邊縫合線組合分佈: {dict(multi_combos)}")

# ============ 5. 端點溫度 vs 組合 ============
print(f"\n{'='*75}")
print("📐 [D.3c] 縫合線端點平均溫度 vs 組合")
print(f"{'='*75}")

for combo, lst in sorted(combos.items()):
    ep_means = [x['ep_mean'] for x in lst]
    mean_Ts = [x['mean_T'] for x in lst]
    print(f"   {combo}: 端點T={np.mean(ep_means):+.1f} ± {np.std(ep_means):.1f}, 節點T={np.mean(mean_Ts):+.1f} ± {np.std(mean_Ts):.1f}")

# ============ 6. S18 深入: 冷斑關聯 ============
print(f"\n{'='*75}")
print("📐 [D.4] S18 (最大 ΔT=125.5) 深入分析")
print(f"{'='*75}")

# S18 = nodes [37, 43, 47]
s18 = [sd for sd in seam_data if sd['idx'] == 18][0]
print(f"   S18: nodes={s18['nodes']}, combo={s18['combo']}")
print(f"   端點: {s18['endpoints']}")
for v in s18['nodes']:
    print(f"     節點 {v}: RA={nodes[v][0]:.1f}°, Dec={nodes[v][1]:.1f}°, T={T[v]*1e6:+.1f} μK, 色={'冷' if color[v]==1 else '熱'}")

# 節點 47 係咪特別?
cs_vec = vecs[0]
for v in s18['nodes']:
    dot = np.clip(np.dot(vecs[v], cs_vec), -1, 1)
    dist = math.degrees(math.acos(dot))
    print(f"     節點 {v} 到冷斑 (節點0): {dist:.1f}°")

# 節點 47 全網最冷?
all_T = [T[v]*1e6 for v in range(60)]
order = np.argsort(all_T)
print(f"\n   全網最冷 5 節點:")
for v in order[:5]:
    print(f"     #{v}: T={all_T[v]:+.1f} μK")
print(f"   節點 47 排名: {list(order).index(47)}/60 最冷")

# ============ 7. S12 深入 ============
print(f"\n{'='*75}")
print("📐 [D.5] S12 (第二大 ΔT=125.1) 深入")
print(f"{'='*75}")

s12 = [sd for sd in seam_data if sd['idx'] == 12][0]
print(f"   S12: nodes={s12['nodes']}, combo={s12['combo']}")
for v in s12['nodes']:
    print(f"     節點 {v}: RA={nodes[v][0]:.1f}°, Dec={nodes[v][1]:.1f}°, T={T[v]*1e6:+.1f} μK, 色={'冷' if color[v]==1 else '熱'}")

# ============ 8. 總結 ============
print(f"\n{'='*75}")
print("📋 總結")
print(f"{'='*75}")
print(f"""
   縫合線 ΔT 模式核心發現:

   1. 奇面組合係主要 driver:
      Δ⬠: ΔT={np.mean([x['dt'] for x in combos['Δ⬠']]):.1f} μK (跨兩種奇面)
      Δ:   ΔT={np.mean([x['dt'] for x in combos['Δ']]):.1f} μK (單一奇面)
      ⬠:   ΔT={np.mean([x['dt'] for x in combos['⬠']]):.1f} μK

   2. 多邊 > 單邊: p=0.031 (但多邊全係 Δ⬠, 同組合效應混淆)

   3. 單邊內: Δ vs ⬠ 差異需要檢查

   4. S18 (最大 ΔT): 節點 47 = 深冷區 (-123.4 μK), 端點 43 溫 (+2.1)
      → 縫合線跨越 冷/溫 邊界!
      → ΔT 大 = 縫合線連接極端溫度區

   5. 物理圖像:
      縫合線 ΔT ∝ 跨越溫度邊界嘅強度
      大 ΔT 縫合線 = 冷熱邊界嘅「縫」
      小 ΔT 縫合線 = 均勻區內嘅「紋」
""")