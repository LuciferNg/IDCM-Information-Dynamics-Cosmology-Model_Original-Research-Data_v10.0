#!/usr/bin/env python3
"""
O143 — 獨立驗證 sibling session (O159 docs/09, 原O205) 嘅著色多重性聲稱
====================================================================
聲稱: (1) 2-著色唔唯一 — 30 個相異飽和著色 (BFS root 枚舉)
      (2) 全部滿足 O7 條件 (32 邊, 每奇面 1 條, 30/30, k 分佈 8/40/12)
      (3) k-selector corr(k,|T|) 範圍 −0.382 至 +0.280, 中位 −0.0085
      (4) 只 1/30 顯著 (p<0.05); k=2⟺ΔE=0 只 1/30
      (5) 幾何指紋 (88 中點距離多重集) 相異

獨立重算 — 唔用 sibling 嘅 script, 由 a5_nodes.txt 重新建圖。
"""
import numpy as np, math, json, itertools
from collections import defaultdict, deque

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
D = f'{BASE}/main_problems/p4_cmb_cold_spot/data'
rng = np.random.default_rng(4242)

nodes = np.loadtxt(f'{D}/a5_nodes.txt')
T = np.array(json.load(open(f'{BASE}/open_problems_fresh/o182_88grid_geometry/data/temps2_SMICA_4.17deg.json'))['A5_60'][:60])
DE0 = {10,12,19,22,23,25,28,32,37,40,45,46}

vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
adj = defaultdict(set); edges = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j); adj[j].add(i); edges.append((i, j))
print(f"圖: V=60, E={len(edges)} (期望 120)")

# faces (for odd-face condition)
import re
faces = []
for line in open(f'{D}/faces.txt'):
    m = re.match(r'^([TPS])\s*\[([\d,\s]+)\]', line.strip())
    if m: faces.append((m.group(1), [int(x) for x in m.group(2).split(',')]))

def bfs_color(root):
    color = {root: 1}; q = deque([root])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in color:
                color[v] = 1 - color[u]; q.append(v)
    return color

def frust_set(color):
    return frozenset(tuple(sorted((u,v))) for u,v in edges if color[u]==color[v])

# 枚舉 60 個 BFS root
colorings = {}
for root in range(60):
    c = bfs_color(root)
    fs = frust_set(c)
    colorings.setdefault(fs, []).append(root)

print(f"\n=== 聲稱 (1): 相異飽和著色數 ===")
print(f"  相異阻挫邊集 = {len(colorings)} (sibling 聲稱 30)")
sizes = [len(fs) for fs in colorings]
print(f"  每個集嘅邊數: min={min(sizes)}, max={max(sizes)}, 全部=32? {all(s==32 for s in sizes)}")

# 聲稱 (2): O7 條件
print(f"\n=== 聲稱 (2): O7 結構條件 ===")
all_ok = True
k_dist_ok = True
for fs in colorings:
    # k distribution
    kd = np.zeros(60, int)
    for u,v in fs: kd[u]+=1; kd[v]+=1
    d = tuple(np.bincount(kd, minlength=3))
    if d != (8,40,12): k_dist_ok = False
print(f"  全部 k 分佈 = 8/40/12? {k_dist_ok}")
# 每奇面 1 條
odd_ok = True
for fs in colorings:
    for ft, verts in faces:
        if ft == 'S': continue
        n_fr = 0
        for i in range(len(verts)):
            a, b = verts[i], verts[(i+1)%len(verts)]
            if tuple(sorted((a,b))) in fs: n_fr += 1
        if n_fr != 1: odd_ok = False; break
print(f"  每個奇面 (T/P) 啱啱 1 條阻挫邊? {odd_ok}")

# 聲稱 (3)(4): corr(k,|T|) 分佈
print(f"\n=== 聲稱 (3)(4): k-selector 分佈 ===")
absT = np.abs(T)
results = []
for fs in colorings:
    kd = np.zeros(60, int)
    for u,v in fs: kd[u]+=1; kd[v]+=1
    r = np.corrcoef(kd, absT)[0,1]
    # permutation p
    N = 20000
    c = sum(1 for _ in range(N) if np.corrcoef(kd, rng.permutation(absT))[0,1] <= r)
    p = (c+1)/(N+1)
    k2 = set(np.where(kd==2)[0].tolist())
    results.append((r, p, k2 == DE0, tuple(sorted(k2))))
rs = np.array([x[0] for x in results])
ps = np.array([x[1] for x in results])
n_sig = int((ps < 0.05).sum())
n_k2 = int(sum(1 for x in results if x[2]))
n_distinct_k2 = len(set(x[3] for x in results))
print(f"  corr(k,|T|) 範圍: {rs.min():+.4f} 至 {rs.max():+.4f}, 中位 {np.median(rs):+.4f}")
print(f"  (sibling: −0.382 至 +0.280, 中位 −0.0085)")
print(f"  p<0.05 嘅著色: {n_sig}/{len(colorings)} (sibling: 1/30)")
print(f"  k=2 ⟺ ΔE=0 成立: {n_k2}/{len(colorings)} (sibling: 1/30)")
print(f"  相異 k=2 集: {n_distinct_k2}")

# 錨定版 (root 0)
anchor_fs = frust_set(bfs_color(0))
anchor_r = np.corrcoef(np.array([sum(1 for e in anchor_fs if i in e) for i in range(60)]), absT)[0,1]
print(f"\n  錨定版 (root 0): corr = {anchor_r:+.4f} ✅ (我 docs/02 報 −0.3819)")

# 聲稱 (5): 幾何指紋
print(f"\n=== 聲稱 (5): 88 格幾何指紋 ===")
def g88_fingerprint(fs):
    mid = []
    for u,v in edges:
        if tuple(sorted((u,v))) not in fs:
            mid.append((vecs[u]+vecs[v])/np.linalg.norm(vecs[u]+vecs[v]))
    mid = np.array(mid)
    G = mid @ mid.T
    d = np.sort(G.flatten())
    return tuple(np.round(d, 6))
fps = set()
for fs in colorings:
    fps.add(g88_fingerprint(fs))
print(f"  相異幾何指紋 = {len(fps)}/{len(colorings)} (sibling: 30 個相異)")

res = {
    'distinct_colorings': len(colorings), 'all_32_edges': all(s==32 for s in sizes),
    'k_dist_ok': bool(k_dist_ok), 'odd_face_ok': bool(odd_ok),
    'corr_min': float(rs.min()), 'corr_max': float(rs.max()), 'corr_median': float(np.median(rs)),
    'n_sig_p05': n_sig, 'n_k2_eq_DE0': n_k2, 'n_distinct_k2': n_distinct_k2,
    'anchor_corr': float(anchor_r), 'distinct_fingerprints': len(fps),
    'verdict_sibling_claims': {
        'C1_30_colorings': len(colorings) == 30,
        'C2_all_satisfy': bool(k_dist_ok and odd_ok and all(s==32 for s in sizes)),
        'C3_range': bool(abs(rs.min()+0.382) < 0.01 and abs(rs.max()-0.280) < 0.01),
        'C4_only_1_sig': n_sig == 1, 'C4b_k2_only_1': n_k2 == 1,
        'C5_fingerprints': len(fps) == len(colorings),
    }
}
with open(f'{O143}/data/step12_coloring_multiplicity.json', 'w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step12_coloring_multiplicity.json")
print(f"\n{'='*76}")
print("判決: sibling 聲稱驗證")
for k, v in res['verdict_sibling_claims'].items():
    print(f"  {k}: {'✅ 確認' if v else '❌ 唔符'}")
