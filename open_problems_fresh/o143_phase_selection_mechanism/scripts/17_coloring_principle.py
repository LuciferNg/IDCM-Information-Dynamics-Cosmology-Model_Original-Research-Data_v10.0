#!/usr/bin/env python3
"""
O143 #17 — 著色揀選原則攻堅 + 寫入動力學 + k 分層身份
=====================================================
A. Vertex-transitivity 檢定: 60 個 vertex 嘅圖距profile 係咪全同?
   → 若係, 30 個著色全部係對稱像 → 冇結構原則可揀 (必須數據驅動)
B. 30 個著色嘅結構性質掃描: 有冇一個結構量令錨定版極端?
C. 寫入動力學: 縫合線翻轉模型 — 每條縫兩端 agreement 分佈
D. k 分層數值身份: 8 = F₆? 40 = 2B·F₅? 12 = B·N_gen?
"""
import numpy as np, math, json, re
from collections import defaultdict, deque, Counter

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
D = f'{BASE}/main_problems/p4_cmb_cold_spot/data'

nodes = np.loadtxt(f'{D}/a5_nodes.txt')
T = np.array(json.load(open(f'{BASE}/open_problems_fresh/o182_88grid_geometry/data/temps2_SMICA_4.17deg.json'))['A5_60'][:60])
A = 134.2
ac = np.loadtxt(f'{D}/anchored_coloring.txt'); color_anchor = ac[:,3].astype(int)
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
adj = defaultdict(set); edges = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j); adj[j].add(i); edges.append((i, j))
faces = []
for line in open(f'{D}/faces.txt'):
    m = re.match(r'^([TPS])\s*\[([\d,\s]+)\]', line.strip())
    if m: faces.append((m.group(1), [int(x) for x in m.group(2).split(',')]))
DE0 = {10,12,19,22,23,25,28,32,37,40,45,46}

print("="*78); print("  O143 #17 — 著色揀選原則 + 寫入動力學 + k 分層身份"); print("="*78)

# ═════ A. Vertex-transitivity ═════
print(f"\n{'='*78}"); print("A. Vertex-transitivity 檢定"); print(f"{'='*78}")
profiles = []
for root in range(60):
    dist = {root: 0}; q = deque([root])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in dist: dist[v] = dist[u]+1; q.append(v)
    prof = tuple(sorted(Counter(dist.values()).items()))
    profiles.append(prof)
n_prof = len(set(profiles))
print(f"  60 個 vertex 嘅圖距 profile: {n_prof} 種相異")
print(f"  全部相同 (vertex-transitive)? {n_prof == 1}")
print(f"  profile 例 (root 0): {profiles[0]}")

# ═════ B. 30 個著色嘅結構性質 ═════
print(f"\n{'='*78}"); print("B. 30 個著色嘅結構性質掃描"); print(f"{'='*78}")
uniq = {}
for root in range(60):
    c = {root: 1}; q = deque([root])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in c: c[v] = 1-c[u]; q.append(v)
    fs = frozenset(tuple(sorted((u,v))) for u,v in edges if c[u]==c[v])
    if fs not in uniq: uniq[fs] = root

def props(fs):
    nonfr = [(u,v) for u,v in edges if tuple(sorted((u,v))) not in fs]
    mid = np.array([(vecs[u]+vecs[v])/np.linalg.norm(vecs[u]+vecs[v]) for u,v in nonfr])
    G = mid @ mid.T
    off = G[~np.eye(88, dtype=bool)]
    # seam components
    fadj = defaultdict(set)
    for u,v in fs: fadj[u].add(v); fadj[v].add(u)
    seen=set(); comps=[]
    for i in range(60):
        if i in fadj and i not in seen:
            comp=[]; qq=deque([i])
            while qq:
                x=qq.popleft()
                if x in seen: continue
                seen.add(x); comp.append(x)
                for y in fadj[x]: qq.append(y)
            comps.append(comp)
    lengths = sorted(len(c)-1 for c in comps)
    # total angular seam length
    tot = 0
    for c in comps:
        cc = sorted(c)
        for a,b in fs:
            if a in cc and b in cc:
                tot += math.degrees(math.acos(np.clip(np.dot(vecs[a],vecs[b]),-1,1)))
    kd = np.zeros(60,int)
    for u,v in fs: kd[u]+=1; kd[v]+=1
    k0 = tuple(sorted(np.where(kd==0)[0].tolist()))
    return {'n_seams': len(comps), 'lens': tuple(lengths), 'tot_len': round(tot,3),
            'mid_nn_mean': round(float(np.sort(off)[::-1][:88].mean()), 6),
            'mid_min_off': round(float(off.min()), 6), 'k0': k0,
            'k2_eq_DE0': tuple(sorted(np.where(kd==2)[0].tolist())) == tuple(sorted(DE0))}

P = {}
for fs, root in uniq.items():
    P[root] = props(fs)

print(f"\n  {'root':>5} {'#seam':>6} {'lens':>22} {'tot_len':>9} {'midNN':>8} {'k2=DE0':>7}")
for root in sorted(P):
    p = P[root]
    mark = " ←錨定" if root == 0 else ""
    print(f"  {root:>5} {p['n_seams']:>6} {str(p['lens']):>22} {p['tot_len']:>9.2f} {p['mid_nn_mean']:>8.4f} {str(p['k2_eq_DE0']):>7}{mark}")

for key in ['n_seams','lens','tot_len','mid_nn_mean','mid_min_off','k0']:
    vals = [P[r][key] for r in P]
    n_distinct = len(set(str(v) for v in vals))
    anchored_is_extreme = P[0][key] == (min(vals, key=str) if isinstance(vals[0],(int,float)) else None)
    print(f"  {key:>14}: {n_distinct} 種相異值" + (f", 錨定 = {P[0][key]}" if n_distinct <= 3 else ""))

# ═════ C. 寫入動力學: 縫合線翻轉 ═════
print(f"\n{'='*78}"); print("C. 寫入動力學: 縫合線翻轉模型"); print(f"{'='*78}")
signT = np.sign(T)
agree = (color_anchor == 1) == (signT < 0)
print(f"\n  整體 agreement = {agree.sum()}/60 = {100*agree.mean():.1f}%")
# per-seam: how many endpoints agree
fs_anchor = frozenset(tuple(sorted((u,v))) for u,v in edges if color_anchor[u]==color_anchor[v])
fadj = defaultdict(set)
for u,v in fs_anchor: fadj[u].add(v); fadj[v].add(u)
seen=set(); comps=[]
for i in range(60):
    if i in fadj and i not in seen:
        comp=[]; qq=deque([i])
        while qq:
            x=qq.popleft()
            if x in seen: continue
            seen.add(x); comp.append(x)
            for y in fadj[x]: qq.append(y)
        comps.append(sorted(comp))
dist_agree = Counter()
for c in comps:
    # endpoints = nodes with degree 1 within the component
    deg = Counter()
    for a,b in fs_anchor:
        if a in c and b in c: deg[a]+=1; deg[b]+=1
    ends = [x for x in c if deg[x]==1]
    n_ag = sum(1 for x in ends if agree[x])
    dist_agree[(len(ends), n_ag)] += 1
print(f"  每條縫嘅端點 agreement 分佈 (端點數, 一致數): 條數")
for kk in sorted(dist_agree):
    print(f"    {kk}: {dist_agree[kk]}")
print(f"  (若寫入 = 整條縫翻轉, 應只見 (2,2) 同 (2,0))")
n_full = dist_agree[(2,2)] + dist_agree[(2,0)]
n_tot = sum(dist_agree.values())
print(f"  完整縫 (兩端同狀態) = {n_full}/{n_tot} = {100*n_full/n_tot:.1f}%")
# 全 60 節點 agreement 由 color 決定? 檢定 flip 節點集合
flip = np.where(~agree)[0]
print(f"\n  唔一致節點 (疑似 flip) = {len(flip)}: {sorted(flip.tolist())}")
flip_k = Counter(int(np.array([sum(1 for e in fs_anchor if i in e) for i in range(60)])[i]) for i in flip)
print(f"  佢哋嘅 k 分佈: {dict(flip_k)}")
keep_k = Counter(int(np.array([sum(1 for e in fs_anchor if i in e) for i in range(60)])[i]) for i in range(60) if agree[i])
print(f"  一致節點嘅 k 分佈: {dict(keep_k)}")

# ═════ D. k 分層數值身份 ═════
print(f"\n{'='*78}"); print("D. k 分層數值身份"); print(f"{'='*78}")
B, N_gen, N_d = 4, 3, 44
F = {1:1,2:1,3:2,4:3,5:5,6:8,7:13,8:21,9:34,10:55,11:89}
L = {0:2,1:1,2:3,3:4,4:7,5:11,6:18,7:29,8:47,9:76,10:123}
print(f"  n(k=0) = 8  vs F₆={F[6]}, 2B={2*B}, B·μ²={B*2}, dim(SU(3))=8, N_d−h¹¹={44-36}  → 全部 = 8 ✅ (身份未定)")
print(f"  n(k=1) = 40 vs 2×20Δ=40, 2B·F₅={2*B*F[5]}, N_d−B={N_d-B}  → 全部 = 40 ✅")
print(f"  n(k=2) = 12 vs #⬠=12, B·N_gen={B*N_gen}, L₅+1={L[5]+1}, #PS邊=12  → 全部 = 12 ✅")
print(f"  60 = B(L₅+B) = {B*(L[5]+B)}; 15 = 2(1+F₅)+N_gen = {2*(1+F[5])+N_gen}")
print(f"  20 縫 = 10+8+2 (單/雙/三邊); 32 = 20Δ+12⬠")
print(f"\n  ★ 結構鏈 (唯一非 numerological 嘅推導):")
print(f"    32 阻挫邊 = 20 (Δ-□) + 12 (⬠-□)   [每奇面 1 條]")
print(f"    → 端點 40 = 2×20; 連接器 12 = PS∩ST; 自由 8 = 60−52")

res = {'vertex_transitive': n_prof == 1, 'n_profiles': n_prof,
       'n_colorings': len(uniq),
       'prop_distinct': {key: len(set(str(P[r][key]) for r in P)) for key in ['n_seams','lens','tot_len','mid_nn_mean','k0']},
       'anchor_props': {k: str(v) for k, v in P[0].items()},
       'write_agree': float(agree.mean()), 'write_dist': {str(k): v for k, v in dist_agree.items()},
       'n_flip': int(len(flip)), 'flip_nodes': sorted(flip.tolist()),
       'flip_k_dist': {str(k): v for k, v in flip_k.items()},
       'keep_k_dist': {str(k): v for k, v in keep_k.items()}}
with open(f'{O143}/data/step14_coloring_principle.json', 'w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step14_coloring_principle.json")
