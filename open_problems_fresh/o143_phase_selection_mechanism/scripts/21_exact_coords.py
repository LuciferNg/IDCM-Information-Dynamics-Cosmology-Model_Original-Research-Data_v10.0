#!/usr/bin/env python3
"""
O143 #21 — 精確 I_h 座標重生成 + 4-design 精確驗證
=================================================
a5_nodes.txt 邊長散佈 0.075° (相對 0.144%) → 座標有噪聲。
用標準 Rhombicosidodecahedron 精確座標 (φ 代數式) 重生成, 檢:
  1. 60 點, 120 邊, 4-regular, 全部邊等長
  2. 4-design 精確度 (應 ~1e-16, 唔係 1e-7)
  3. 同 a5_nodes.txt 係咪 congruent (Gram 譜)
  4. 30 個著色係咪精確 congruent
"""
import numpy as np, math, json, itertools
from collections import defaultdict, deque

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
phi = (1 + 5**0.5)/2

print("="*78); print("  O143 #21 — 精確 I_h 座標 + 4-design"); print("="*78)

# ── 標準 Rhombicosidodecahedron 座標 (edge length 2) ──
# 全部 even permutation of:
#   (±1, ±1, ±φ³), (±φ², ±φ, ±2φ), (±(2+φ), 0, ±φ²)
base = [(1,1,phi**3), (phi**2, phi, 2*phi), (2+phi, 0, phi**2)]
def even_perms(t):
    return [t, (t[1],t[2],t[0]), (t[2],t[0],t[1])]
verts = []
for b in base:
    for perm in even_perms(b):
        for signs in itertools.product([1,-1], repeat=3):
            v = tuple(s*x for s,x in zip(signs, perm))
            if v not in verts: verts.append(v)
V = np.array(verts, float)
print(f"\n  生成頂點: {len(V)} (期望 60)")
# 歸一化到單位球
V = V / np.linalg.norm(V, axis=1, keepdims=True)

# 邊: 最近鄰
d = np.linalg.norm(V[:,None,:] - V[None,:,:], axis=2)
np.fill_diagonal(d, np.inf)
nn = d.min(axis=1)
print(f"  最近鄰距離: min={nn.min():.6f}, max={nn.max():.6f}, 相對散佈={100*(nn.max()-nn.min())/nn.mean():.2e}%")
thr = nn.mean()*1.3
adjE = [(i,j) for i in range(60) for j in range(i+1,60) if d[i,j] < thr]
deg = np.zeros(60, int)
for i,j in adjE: deg[i]+=1; deg[j]+=1
print(f"  邊數 = {len(adjE)} (期望 120); degree 全部 4? {np.all(deg==4)}")

# ── 4-design 精確驗證 ──
def sym_tensor(Vv, p):
    T = np.zeros((3,)*p)
    for v in Vv:
        for idx in np.ndindex((3,)*p):
            pr = 1.0
            for dd in idx: pr *= v[dd]
            T[idx] += pr
    return T / len(Vv)
def iso_tensor(p):
    if p % 2 == 1: return np.zeros((3,)*p)
    def pairings(items):
        if not items: yield []; return
        first = items[0]
        for i in range(1, len(items)):
            rest = items[1:i] + items[i+1:]
            for p_ in pairings(rest):
                yield [(first, items[i])] + p_
    def dfact(m):
        r=1
        while m>0: r*=m; m-=2
        return r
    T = np.zeros((3,)*p)
    for pr in pairings(list(range(p))):
        arr = np.ones((3,)*p)
        for (a,b) in pr:
            sh=[1]*p; sh[a]=3; sh[b]=3
            arr = arr * np.eye(3).reshape(sh)
        T += arr
    return T / dfact(p+1)

print(f"\n  ★ 4-design 精確驗證 (精確座標):")
for p in [1,2,3,4,6]:
    dev = float(np.abs(sym_tensor(V,p) - iso_tensor(p)).max())
    print(f"    t={p}: 偏差 = {dev:.3e}" + ("  ✅ 精確" if dev < 1e-12 else ""))

# ── 同 a5_nodes.txt 比較 ──
a5 = np.loadtxt(f'{BASE}/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt')
A5 = np.array([[math.cos(math.radians(dd))*math.cos(math.radians(rr)),
                math.cos(math.radians(dd))*math.sin(math.radians(rr)),
                math.sin(math.radians(dd))] for rr, dd in a5])
def spec(X):
    G = X @ X.T
    return np.sort(np.linalg.eigvalsh(G))
s_exact, s_a5 = spec(V), spec(A5)
print(f"\n  同 a5_nodes.txt 比較:")
print(f"    Gram 譜差 max = {np.max(np.abs(s_exact - s_a5)):.3e}")
print(f"    → a5_nodes 係精確座標嘅 rotated version? {np.max(np.abs(s_exact-s_a5)) < 1e-3}")

# ── 30 個著色嘅精確 congruence ──
def build_adj(Vv, thr):
    dd = np.linalg.norm(Vv[:,None,:]-Vv[None,:,:], axis=2); np.fill_diagonal(dd, np.inf)
    return [(i,j) for i in range(60) for j in range(i+1,60) if dd[i,j] < thr], dd
eE, _ = build_adj(V, thr)
adjx = defaultdict(set)
for i,j in eE: adjx[i].add(j); adjx[j].add(i)
uniq = {}
for root in range(60):
    c = {root:1}; q = deque([root])
    while q:
        u = q.popleft()
        for w in adjx[u]:
            if w not in c: c[w]=1-c[u]; q.append(w)
    fs = frozenset(tuple(sorted((i,j))) for i,j in eE if c[i]==c[j])
    uniq.setdefault(fs, root)
print(f"\n  精確座標下相異飽和著色 = {len(uniq)}")
specs = {}
for fs, root in uniq.items():
    mid = np.array([(V[i]+V[j])/np.linalg.norm(V[i]+V[j]) for i,j in eE if tuple(sorted((i,j))) not in fs])
    specs[root] = np.sort(np.linalg.eigvalsh(mid @ mid.T))
devs = [float(np.max(np.abs(specs[r]-specs[0]))) for r in specs]
print(f"  30 個著色 88 格 Gram 譜差: max = {max(devs):.3e}")
print(f"  → 精確 congruent? {max(devs) < 1e-12}")

res = {'n_vertices': len(V), 'n_edges': len(eE), 'deg4': bool(np.all(deg==4)),
       'nn_rel_spread': float(100*(nn.max()-nn.min())/nn.mean()),
       'design_dev': {str(p): float(np.abs(sym_tensor(V,p)-iso_tensor(p)).max()) for p in [1,2,3,4,6]},
       'gram_vs_a5': float(np.max(np.abs(s_exact-s_a5))),
       'n_colorings_exact': len(uniq), 'coloring_congruence_max': float(max(devs))}
with open(f'{O143}/data/step18_exact_coords.json', 'w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step18_exact_coords.json")
