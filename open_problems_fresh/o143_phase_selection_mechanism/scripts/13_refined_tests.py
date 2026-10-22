#!/usr/bin/env python3
"""
O143 final #2 — 三個項目精細化 (2026-09-19)
==========================================
R1: 相位符號 — anchored coloring 係「基態著色」? 測試 agreement 分 k 層
    (若 seams = 寫入位元, 則 k>0 節點 agreement 應較低)
R2: k=0 內部 — hop 分離檢定 (Fisher) + 3D 角距
R3: k 分層身份 — ★ 12 ⬠-type 阻挫邊 subgraph 係咪 2-regular → 12 節點 = k=2 集
                    20 Δ-type 阻挫邊 endpoints 係咪全 deg-1 → 40 節點 = k=1 集
"""
import numpy as np, math, json, re
from collections import defaultdict, deque
from scipy import stats
from astropy.coordinates import SkyCoord
import astropy.units as u_ast

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
D = f'{BASE}/main_problems/p4_cmb_cold_spot/data'

nodes = np.loadtxt(f'{D}/a5_nodes.txt')
T = np.array(json.load(open(f'{BASE}/open_problems_fresh/o182_88grid_geometry/data/temps2_SMICA_4.17deg.json'))['A5_60'][:60])
A = 134.2
ac = np.loadtxt(f'{D}/anchored_coloring.txt'); color = ac[:,3].astype(int)
frust = [tuple(map(int, l.split()[:2])) for l in open(f'{D}/frustration_edges.txt') if not l.startswith('#')]
faces = []
for line in open(f'{D}/faces.txt'):
    m = re.match(r'^([TPS])\s*\[([\d,\s]+)\]', line.strip())
    if m: faces.append((m.group(1), [int(x) for x in m.group(2).split(',')]))

vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
adj = defaultdict(set)
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j); adj[j].add(i)
hop = {0: 0}; q = deque([0])
while q:
    x = q.popleft()
    for y in adj[x]:
        if y not in hop: hop[y] = hop[x]+1; q.append(y)
kdeg = np.zeros(60, int)
for a, b in frust: kdeg[a] += 1; kdeg[b] += 1
signT = np.sign(T)

print("="*76); print("  O143 FINAL #2 — 精細化"); print("="*76)

# ═════ R1: coloring 基態 + seam 寫入 ═════
print(f"\n{'='*76}"); print("R1 相位符號: coloring = 基態著色?"); print(f"{'='*76}")
print(f"\n  一致率 (color vs sign(T)) 分 k 層:")
for kk in (0,1,2):
    m = kdeg == kk
    ag = np.mean((color[m]==1) == (signT[m]<0))
    nm = int(((color[m]==1)==(signT[m]<0)).sum())
    print(f"    k={kk}: n={m.sum():>2}, 一致 {nm}/{m.sum()} = {ag*100:.1f}%")
# Fisher: k=0 vs k>0
a1 = int(((color[kdeg==0]==1)==(signT[kdeg==0]<0)).sum())
a2 = int(((color[kdeg>0]==1)==(signT[kdeg>0]<0)).sum())
tab = [[a1, int((kdeg==0).sum())-a1], [a2, int((kdeg>0).sum())-a2]]
odds, pf = stats.fisher_exact(tab)
print(f"\n  Fisher (k=0 vs k>0 一致率): {tab}, p = {pf:.4f}")

# seam 端點寫入檢定: 每條縫合線 2 端點, 若寫入 = 同時翻轉 → 端點 agreement 反相關
print(f"\n  縫合線端點 agreement (若寫入=翻轉兩端點, 端點應較多唔一致):")
for a, b in frust:
    pass
seam_end_agree = []
for a, b in frust:
    seam_end_agree.append(((color[a]==1)==(signT[a]<0)) and ((color[b]==1)==(signT[b]<0)))
print(f"    兩端都一致嘅阻挫邊: {sum(seam_end_agree)}/32 ({100*np.mean(seam_end_agree):.1f}%)")
print(f"    (隨機基線 25% = 0.5²)")

# ═════ R2: k=0 內部 ═════
print(f"\n{'='*76}"); print("R2 k=0 組內部差異"); print(f"{'='*76}")
k0 = np.where(kdeg==0)[0]
hop0 = np.array([hop[i] for i in k0]); absT0 = np.abs(T[k0])
ext = absT0 > 100
# hop <= 3 vs >= 5
tab2 = [[int((ext & (hop0<=3)).sum()), int((~ext & (hop0<=3)).sum())],
        [int((ext & (hop0>=5)).sum()), int((~ext & (hop0>=5)).sum())]]
odds2, pf2 = stats.fisher_exact(tab2)
print(f"  hop≤3 vs hop≥5: {tab2}, Fisher p = {pf2:.4f}")
print(f"  node20 例外: hop=1 但 |T|=35.4 (nbr_meanT={np.mean([T[j] for j in adj[20]]):.1f})")
# 3D 角距 to node0
d0 = np.degrees(np.arccos(np.clip(vecs @ vecs[0], -1, 1)))
print(f"\n  {'node':>5} {'|T|':>7} {'hop':>4} {'ang2node0':>10} {'nbr_meanT':>10}")
for i in k0:
    print(f"  {i:>5} {abs(T[i]):>7.1f} {hop[i]:>4} {d0[i]:>10.2f} {np.mean([T[j] for j in adj[i]]):>10.1f}")
print(f"  corr(hop,|T|) = {np.corrcoef(hop0, absT0)[0,1]:+.3f} (n=8)")
print(f"  corr(ang2node0,|T|) = {np.corrcoef(d0[k0], absT0)[0,1]:+.3f}")

# ═════ R3: k 分層身份 ═════
print(f"\n{'='*76}"); print("R3 k 分層譜身份 — ★ 阻挫邊 subgraph 結構"); print(f"{'='*76}")
def ftype(u, v):
    ts = set()
    for ft, verts in faces:
        if u in verts and v in verts: ts.add(ft)
    return ''.join(sorted(ts))
edges_by_type = defaultdict(list)
for a, b in frust:
    edges_by_type[ftype(a, b)].append((a, b))
print(f"\n  阻挫邊按面類型:")
for t in sorted(edges_by_type):
    print(f"    {t}: n={len(edges_by_type[t])}")

# ⬠-type subgraph degree
for t in sorted(edges_by_type):
    es = edges_by_type[t]
    dg = defaultdict(int)
    for a, b in es: dg[a] += 1; dg[b] += 1
    verts = set(dg)
    degs = sorted(set(dg.values()))
    print(f"\n  {t}-type subgraph: {len(verts)} 個端點, degree 分佈 = {degs}")
    if t == 'PS':
        print(f"    2-regular? {all(dg[x]==2 for x in verts)}")
        print(f"    節點集 = {sorted(verts)}")
        print(f"    k=2 集   = {sorted(np.where(kdeg==2)[0].tolist())}")
        print(f"    相同? {set(verts) == set(np.where(kdeg==2)[0].tolist())}")
    if t == 'ST':
        print(f"    全 deg-1? {all(dg[x]==1 for x in verts)}")
        print(f"    端點集 = {sorted(verts)}")
        print(f"    k=1 集  = {sorted(np.where(kdeg==1)[0].tolist())}")
        print(f"    相同? {set(verts) == set(np.where(kdeg==1)[0].tolist())}")

print(f"\n  ★ 譜身份總結:")
print(f"    n(k=1) = 40 = 2 × 20 = 2 × (#Δ 面) = 2 × (#ST 阻挫邊)")
print(f"    n(k=2) = 12 = #⬠ 面 = #PS 阻挫邊")
print(f"    n(k=0) = 8 = 60 − 40 − 12 = 2B = B·μ² = dim(SU(3))")
print(f"    60 = B(L₅+B) = 4×15; 15 = 2(1+F₅)+N_gen = 12+3")

res = {
    'R1_agree_by_k': {str(kk): float(np.mean((color[kdeg==kk]==1)==(signT[kdeg==kk]<0))) for kk in (0,1,2)},
    'R1_fisher_p': float(pf), 'R1_seam_both_agree': int(sum(seam_end_agree)),
    'R2_fisher_p': float(pf2), 'R2_corr_hop_absT': float(np.corrcoef(hop0, absT0)[0,1]),
    'R2_corr_ang_absT': float(np.corrcoef(d0[k0], absT0)[0,1]),
    'R3_edge_types': {t: len(v) for t, v in edges_by_type.items()},
    'R3_PS_2regular': bool(all(sum(1 for a,b in edges_by_type['PS'] if a==x or b==x)==2 for x in set(sum([list(e) for e in edges_by_type['PS']], [])))),
    'R3_ST_all_deg1': bool(all(sum(1 for a,b in edges_by_type['ST'] if a==x or b==x)==1 for x in set(sum([list(e) for e in edges_by_type['ST']], [])))),
}
with open(f'{O143}/data/step10_refined.json', 'w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step10_refined.json")
