#!/usr/bin/env python3
"""
O143 #16 — R3 身份嘅著色依賴性測試
==================================
問題: docs/03 R3 嘅「k=2 = PS端點 ∩ ST端點」係咪對全部 30 個飽和著色都成立?
      若成立 → 結構定理 (著色無關); 若只 1/30 → 同 k=2⟺ΔE=0 一樣係選擇效應
"""
import numpy as np, math, json, re
from collections import defaultdict, deque

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
D = f'{BASE}/main_problems/p4_cmb_cold_spot/data'

nodes = np.loadtxt(f'{D}/a5_nodes.txt')
T = np.array(json.load(open(f'{BASE}/open_problems_fresh/o182_88grid_geometry/data/temps2_SMICA_4.17deg.json'))['A5_60'][:60])
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

def bfs_color(root):
    c = {root: 1}; q = deque([root])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in c: c[v] = 1-c[u]; q.append(v)
    return c

def ftype(u, v, fs):
    ts = set()
    for ft, verts in faces:
        if u in verts and v in verts: ts.add(ft)
    return ''.join(sorted(ts))

# 收集 30 個相異著色 (用阻挫邊集去重)
uniq = {}
for root in range(60):
    c = bfs_color(root)
    fs = frozenset(tuple(sorted((u,v))) for u,v in edges if c[u]==c[v])
    if fs not in uniq: uniq[fs] = root

print("="*76); print("  R3 身份著色依賴性測試 (30 個飽和著色)"); print("="*76)
n_psst_ok = 0; n_k2_de0 = 0; n_k1_ok = 0; n_k0_ok = 0
rows = []
for fs, root in sorted(uniq.items(), key=lambda x: x[1]):
    PS_e = [(a,b) for a,b in fs if ftype(a,b,fs) == 'PS']
    ST_e = [(a,b) for a,b in fs if ftype(a,b,fs) == 'ST']
    PS_end = set(sum([list(e) for e in PS_e], []))
    ST_end = set(sum([list(e) for e in ST_e], []))
    kd = np.zeros(60, int)
    for u,v in fs: kd[u]+=1; kd[v]+=1
    k2 = set(np.where(kd==2)[0].tolist())
    k1 = set(np.where(kd==1)[0].tolist())
    k0 = set(np.where(kd==0)[0].tolist())
    ok2 = (k2 == (PS_end & ST_end))
    ok1 = (k1 == ((PS_end|ST_end)-(PS_end&ST_end)))
    ok0 = (k0 == (set(range(60))-(PS_end|ST_end)))
    n_psst_ok += ok2; n_k1_ok += ok1; n_k0_ok += ok0
    de0ok = (k2 == DE0)
    n_k2_de0 += de0ok
    rows.append((root, len(PS_e), len(ST_e), ok2, ok1, ok0, de0ok, len(k2 & DE0)))

print(f"\n  {'root':>5} {'#PS':>4} {'#ST':>4} {'k2=PS∩ST':>9} {'k1=對稱差':>9} {'k0=補集':>8} {'k2=ΔE0':>7} {'|k2∩DE0|':>9}")
for r in rows:
    print(f"  {r[0]:>5} {r[1]:>4} {r[2]:>4} {str(r[3]):>9} {str(r[4]):>9} {str(r[5]):>8} {str(r[6]):>7} {r[7]:>9}")

print(f"\n  ★ k=2 == PS端點 ∩ ST端點: {n_psst_ok}/{len(uniq)} 個著色成立")
print(f"  ★ k=1 == 對稱差:          {n_k1_ok}/{len(uniq)}")
print(f"  ★ k=0 == 補集:            {n_k0_ok}/{len(uniq)}")
print(f"  ★ k=2 == ΔE=0:            {n_k2_de0}/{len(uniq)}")

print(f"\n  判決:")
if n_psst_ok == len(uniq):
    print(f"    ✅ R3 集合身份係【結構定理】— 對全部 30 個飽和著色成立 (著色無關)")
    print(f"       即: 任何飽和著色下, deg-2 節點 = 同時屬於 ⬠-□ 同 Δ-□ 阻挫邊嘅端點")
    print(f"       ⟹ docs/03 R3 嘅集合運算部分不受著色非唯一性影響")
else:
    print(f"    ⚠️ R3 集合身份只 {n_psst_ok}/{len(uniq)} 成立 → 同 k=2⟺ΔE=0 一樣係著色選擇後果")

res = {'n_colorings': len(uniq), 'k2_eq_PSintST': n_psst_ok, 'k1_eq_symdiff': n_k1_ok,
       'k0_eq_complement': n_k0_ok, 'k2_eq_DE0': n_k2_de0,
       'per_coloring': [{'root': r[0], 'nPS': r[1], 'nST': r[2], 'k2_PSST': bool(r[3]),
                          'k1_sym': bool(r[4]), 'k0_comp': bool(r[5]), 'k2_DE0': bool(r[6]),
                          'overlap_DE0': r[7]} for r in rows]}
with open(f'{O143}/data/step13_r3_coloring_dependence.json', 'w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step13_r3_coloring_dependence.json")
