#!/usr/bin/env python3
"""
O136 — Script 29: A₅ 網阻挫模式選擇
================================================================
幾何基礎 (O182/O171):
  60 頂點 A₅ 網 (Rhombicosidodecahedron), 120 邊, 度 4
  2-著色 → 透明邊 88 (異色) + 阻挫邊 32 (同色)
  88 透明邊中點 = IDCM 88 格
  ⚠️ O171 已證: A₅ **唔**作用於 88 中點 (穩定子階 2)

本 script:
  1. 重建 A₅ 網 + 著色
  2. 構建 88 中點的線圖 (兩中點相鄰 ⟺ 對應邊共享頂點)
  3. 計算線圖 Laplacian 譜
  4. 對比環譜 γ_n = 4sin²(nπ/88)
  5. 阻挫擾動: 睇是否選出特定模式
"""
import numpy as np, json, math
from pathlib import Path
from itertools import combinations
from collections import Counter

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = ROOT / "cmb_cold_spot/data"
O182 = ROOT / "o182_88grid_geometry/data"
OUT = Path(__file__).parent.parent / "data"
OUT.mkdir(exist_ok=True)

Nd, B_, dimC = 44, 4, 3
def v2(x):
    c = 0
    while x % 2 == 0: x //= 2; c += 1
    return c

print("=" * 96)
print("O136 Script 29: A₅ 網阻挫模式選擇")
print("=" * 96)

# ═══ 1. 重建 A₅ 網 ═══════════════════════════════════
print(f"\n{'─'*96}")
print("1. 重建 A₅ 網 (60 頂點, 120 邊) + 著色")
print(f"{'─'*96}")

nodes = np.loadtxt(DATA / "a5_nodes.txt")
ra, dec = np.radians(nodes[:,0]), np.radians(nodes[:,1])
V = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
col = {}
for line in (DATA / "anchored_coloring.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split(); col[int(p[0])] = int(p[3])
color = np.array([col[i] for i in range(60)])

dist = np.arccos(np.clip(V @ V.T, -1, 1))
edges = [(i,j) for i in range(60) for j in range(i+1,60) if dist[i,j] < np.radians(28.0)]
transp = [(i,j) for (i,j) in edges if color[i] != color[j]]
frust  = [(i,j) for (i,j) in edges if color[i] == color[j]]
print(f"\n邊數: {len(edges)} (透明 {len(transp)} / 阻挫 {len(frust)})")
print(f"著色: {int(color.sum())} 冷 / {60-int(color.sum())} 非冷")
print(f"✅ 120 = 88 + 32 = 2N_d + 32")

# 度分佈
deg_all = Counter()
for i,j in edges: deg_all[i]+=1; deg_all[j]+=1
print(f"全網度分佈: {dict(Counter(deg_all.values()))}")

# 頂點的透明度 / 阻挫度
deg_t = Counter(); deg_f = Counter()
for i,j in transp: deg_t[i]+=1; deg_t[j]+=1
for i,j in frust: deg_f[i]+=1; deg_f[j]+=1
print(f"透明度分佈: {dict(Counter(deg_t.values()))}")
print(f"阻挫度分佈: {dict(Counter(deg_f.values()))}")

# ═══ 2. 88 中點的線圖 ════════════════════════════════
print(f"\n{'─'*96}")
print("2. 88 中點的線圖 (兩中點相鄰 ⟺ 對應邊共享頂點)")
print(f"{'─'*96}")

# g88_edge_map 對應
emap = []
for line in (O182 / "g88_edge_map.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split()
    emap.append((int(p[0]), int(p[1]), int(p[2])))
emap.sort()
print(f"\ng88_edge_map 條目: {len(emap)}")

# 驗證 emap 與 transp 一致
transp_set = set(tuple(sorted(e)) for e in transp)
emap_set = set(tuple(sorted((u,v))) for _,u,v in emap)
print(f"emap 邊集 == 透明邊集: {emap_set == transp_set} {'✅' if emap_set==transp_set else '🔴'}")
if emap_set != transp_set:
    print(f"  差集 (emap − transp): {sorted(emap_set - transp_set)[:5]}")
    print(f"  差集 (transp − emap): {sorted(transp_set - emap_set)[:5]}")

# 線圖: 共享頂點
vertex_to_mids = {}
for mid, u, v in emap:
    vertex_to_mids.setdefault(u, []).append(mid)
    vertex_to_mids.setdefault(v, []).append(mid)

adj = {i: set() for i in range(88)}
for vtx, mids in vertex_to_mids.items():
    for a, b in combinations(mids, 2):
        adj[a].add(b); adj[b].add(a)

nE = sum(len(s) for s in adj.values())//2
degs = Counter(len(s) for s in adj.values())
print(f"\n線圖: 88 頂點, {nE} 邊")
print(f"度分佈: {dict(degs)}")
print(f"平均度: {sum(len(s) for s in adj.values())/88:.3f}")

# 連通性
seen = set()
comp = []
for st in range(88):
    if st in seen: continue
    stack = [st]; c = []
    while stack:
        x = stack.pop()
        if x in seen: continue
        seen.add(x); c.append(x)
        stack.extend(adj[x] - seen)
    comp.append(c)
print(f"連通分量: {len(comp)} 個, 大小分佈 {dict(Counter(len(c) for c in comp))}")

# ═══ 3. Laplacian 譜 ═════════════════════════════════
print(f"\n{'─'*96}")
print("3. 線圖 Laplacian 譜 vs 環譜 γ_n = 4sin²(nπ/88)")
print(f"{'─'*96}")

Lmat = np.zeros((88,88))
for i in range(88):
    Lmat[i,i] = len(adj[i])
    for j in adj[i]:
        Lmat[i,j] = -1
ev = np.linalg.eigvalsh(Lmat)
ev = np.sort(ev)
print(f"\n最小 6 個本徵值: {[round(x,6) for x in ev[:6]]}")
print(f"最大 6 個本徵值: {[round(x,6) for x in ev[-6:]]}")

gamma = np.array([4*math.sin(n*math.pi/88)**2 for n in range(1,45)])
print(f"\n環譜 γ_n (n=1..44) 範圍: [{gamma.min():.6f}, {gamma.max():.6f}]")

# 對比: 線圖譜是否匹配 γ_n 的某個子集?
print(f"\n{'─'*96}")
print("4. 匹配分析: 線圖本徵值 ↔ γ_n")
print(f"{'─'*96}")

TOL = 0.05
matches = []
for i, e in enumerate(ev):
    if e < 1e-9: continue
    for n in range(1,45):
        if abs(e - gamma[n-1])/gamma[n-1] < TOL:
            matches.append((i, round(e,6), n, round((e-gamma[n-1])/gamma[n-1]*100,3)))

print(f"\n容差 {TOL*100:.0f}% 下匹配數: {len(matches)}")
if matches:
    print(f"\n{'本徵值#':>8} {'λ':>12} {'γ_n':>6} {'n':>4} {'偏差%':>9}")
    print("-" * 44)
    for i, e, n, d in matches[:30]:
        print(f"{i:>8} {e:>12.6f} {n:>4} {'':>4} {d:>+9.3f}")

# ═══ 5. 阻挫擾動 ═════════════════════════════════════
print(f"\n{'─'*96}")
print("5. 阻挫擾動: 加入 32 阻挫邊的效應")
print(f"{'─'*96}")

# 全 120 邊線圖 (含阻挫邊中點)
all_edges = transp + frust
v2m = {}
for k, (u,v) in enumerate(all_edges):
    v2m.setdefault(u, []).append(k)
    v2m.setdefault(v, []).append(k)
adj120 = {i: set() for i in range(120)}
for vtx, mids in v2m.items():
    for a, b in combinations(mids, 2):
        adj120[a].add(b); adj120[b].add(a)

# 88 子集在全網中的耦合: 88 中點 ↔ 32 阻挫中點的連接
frust_idx = {tuple(sorted(e)): 88+k for k, e in enumerate(frust)}
cross = 0
for i in range(88):
    u, v = emap[i][1], emap[i][2]
    for vtx in (u, v):
        for j in range(88, 120):
            if j in adj120[i]:
                cross += 1
print(f"\n全 120 邊線圖: 120 頂點, {sum(len(s) for s in adj120.values())//2} 邊")
print(f"88↔32 跨界連接數: {cross}")

# 檢查 32 阻挫中點的度
deg32 = Counter()
for k, (u,v) in enumerate(frust):
    idx = 88+k
    # 只數與 88 中點的連接
    n88 = len(adj120[idx] & set(range(88)))
    deg32[n88] += 1
print(f"32 阻挫中點連到 88 中點的度分佈: {dict(deg32)}")

# ═══ 6. ★ 關鍵: 阻挫結構是否編碼特定模式? ═══════════
print(f"\n{'─'*96}")
print("6. ★ 阻挫結構的模 88 / 模 44 分析")
print(f"{'─'*96}")

# 88 中點按某種順序排列? 用 g88_nodes 的幾何
nodes88 = np.loadtxt(O182 / "g88_nodes.txt")
print(f"\n88 節點座標 shape: {nodes88.shape}")
print(f"座標範圍: RA [{nodes88[:,0].min():.2f}, {nodes88[:,0].max():.2f}], "
      f"Dec [{nodes88[:,1].min():.2f}, {nodes88[:,1].max():.2f}]")

# 檢查是否所有節點在某個帶上 (環?)
dec_std = nodes88[:,1].std()
print(f"Dec 標準差: {dec_std:.4f}")
print(f"→ {'🔴 唔係環 (球面分佈)' if dec_std > 20 else '🟡 可能係帶狀'}")

# 阻挫中點的幾何
fnodes = np.loadtxt(O182 / "g32_frustration_midpoints.txt")
print(f"\n32 阻挫中點: Dec 範圍 [{fnodes[:,1].min():.2f}, {fnodes[:,1].max():.2f}], std = {fnodes[:,1].std():.4f}")

# ═══ 7. 保存 ════════════════════════════════════════
with open(OUT / "29_a5_frustration_modes.json", "w") as f:
    json.dump({
        "n_edges": len(edges), "n_transparent": len(transp), "n_frustrated": len(frust),
        "coloring": {"cold": int(color.sum()), "warm": int(60-color.sum())},
        "line_graph": {"n_vertices": 88, "n_edges": nE, "degree_dist": {str(k):v for k,v in degs.items()},
                       "n_components": len(comp), "comp_sizes": [len(c) for c in comp]},
        "laplacian_eigs": [round(float(x),8) for x in ev],
        "ring_spectrum": [round(float(x),8) for x in gamma],
        "n_matches": len(matches),
        "matches": [{"eig_idx": i, "lambda": e, "n": n, "dev_pct": d} for i,e,n,d in matches],
        "cross_88_32": cross,
        "verdict": "待分析",
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/29_a5_frustration_modes.json")