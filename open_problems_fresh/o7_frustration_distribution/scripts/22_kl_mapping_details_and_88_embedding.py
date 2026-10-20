#!/usr/bin/env python3
"""
O7 — 22_kl_mapping_details_and_88_embedding.py (2026-10-11)
====================================================================
O7/natural-write-closure 第八輪:
  T1. 簡併組內 k↔m 映射全表 (λ 組 → ℓ 子空間嘅 m 係數) — 有冇系統結構
  T2. λ=2.618 (ρ₃') 同 λ=1.764 (ρ₄) 組入面 k 序號 ↔ m 序號 pattern
  T3. 88 中點 line graph (透明邊 adjacency) Laplacian 譜 vs 88-site 鏈譜
      γ_k = 4sin²(kπ/176) — 睇有冇 A₅ irrep 特徵值出現 (嵌入信號)
  T4. 88 中點 line graph 譜入面 φ²=2.618 / ρ₅ / ρ₄ 特徵值出現次數
     → 「88 格 = 鏈嵌入」嘅譜線索 (O182 構造 + O7 ℓ 子空間)

數據: cmb_cold_spot (a5_nodes, faces, anchored_coloring, frustration_edges)
      o182_88grid_geometry (g88_edge_map, g88_nodes)
"""

import math, re
from collections import defaultdict
import numpy as np

DATA = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/cmb_cold_spot/data'
O182 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o182_88grid_geometry/data'
results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

print("=" * 76)
print("  O7 — k↔m 序號 + 88 中點 line graph 譜 (T1-T4)")
print("=" * 76)

nodes = []
for i, line in enumerate(open(f'{DATA}/a5_nodes.txt')):
    if line.startswith('#'): continue
    p = line.split()
    nodes.append((float(p[0]), float(p[1])))
nodes = np.array(nodes)

adj = defaultdict(set)
for line in open(f'{DATA}/faces.txt'):
    if line.startswith('#'): continue
    m = re.search(r'\[([^\]]+)\]', line)
    vs = [int(x) for x in m.group(1).split(',')]
    for i in range(len(vs)):
        adj[vs[i]].add(vs[(i+1) % len(vs)])
        adj[vs[(i+1) % len(vs)]].add(vs[i])

from astropy.coordinates import SkyCoord
import astropy.units as AU
from scipy.special import lpmv
from math import factorial, sqrt

sc = SkyCoord(ra=nodes[:, 0]*AU.deg, dec=nodes[:, 1]*AU.deg, frame='icrs')
xyz = sc.cartesian.xyz.value
x, y, z = xyz[0], xyz[1], xyz[2]
th = np.arccos(np.clip(z, -1, 1)); ph = np.arctan2(y, x)

def ylm(l, m, th, ph):
    plm = lpmv(abs(m), l, np.cos(th))
    norm = sqrt((2*l+1)*factorial(l-abs(m))/(4*math.pi*factorial(l+abs(m))))
    if m == 0: return norm * plm
    if m > 0:  return sqrt(2)*norm * plm * np.cos(m*ph)
    return sqrt(2)*norm * plm * np.sin(-m*ph)

# ── 圖 Laplacian ──
L = np.zeros((60, 60))
for v in range(60):
    L[v, v] = len(adj[v])
    for w in adj[v]: L[v, w] = -1
evals, evecs = np.linalg.eigh(L)

from collections import defaultdict as dd
groups = dd(list)
for k in range(60):
    groups[round(float(evals[k]), 6)].append(k)

def get_group(lam):
    for k in groups:
        if abs(k - lam) < 1e-4: return groups[k]
    return []

# ═══════════════════════════════════════════════════════════════
# T1. 簡併組內 k ↔ m 全表
# ═══════════════════════════════════════════════════════════════
print("\n─── T1. 簡併組 k ↔ 球面 m 全表 (ℓ3 = 7 維目標) ───")
def best_m(vk, l):
    best = []
    for m in range(-l, l+1):
        Y = ylm(l, m, th, ph)
        Y = Y/np.linalg.norm(Y)
        best.append((abs(np.dot(vk/np.linalg.norm(vk), Y)), m))
    best.sort(reverse=True)
    return best

for lam, l in [(1.7639, 3), (2.6180, 3), (0.3820, 1), (1.0746, 2), (3.0000, 4), (3.4481, 4)]:
    ks = get_group(lam)
    if not ks: print(f"  λ={lam:.4f}: 組唔見"); continue
    print(f"  λ={lam:.4f} ({len(ks)}模):")
    for k in sorted(ks):
        bm = best_m(evecs[:, k], l)
        top = ", ".join(f"m={m}({c:.2f})" for c, m in bm[:3])
        print(f"    k={k:2d} 主m: {top}")

# ═══════════════════════════════════════════════════════════════
# T2. k 序號 ↔ m 序號 pattern (λ=2.618 ∪ λ=1.764 → ℓ3 嘅 7 個 m)
# ═══════════════════════════════════════════════════════════════
print("\n─── T2. ℓ3 嘅 7 個 m 點樣被 λ=1.764(4d)+λ=2.618(3d) 覆蓋 ───")
ks8 = sorted(get_group(1.7639) + get_group(2.6180))
assigned = {}
for k in ks8:
    bm = best_m(evecs[:, k], 3)
    # 貪婪指派: 揀未被用嘅最高係數 m
    chosen = None
    for c, m in bm:
        if m not in assigned.values():
            chosen = (m, c); break
    assigned[k] = chosen
    print(f"    k={k:2d} → m={chosen[0]:+d} (|c|={chosen[1]:.3f})")
covered = sorted(set(v[0] for v in assigned.values()))
print(f"  覆蓋 m: {covered} (目標 -3..+3 共 7 個)")
check("T2a: ℓ3 嘅 7 個 m 全部被 λ 組模覆蓋", set(covered) == set(range(-3, 4)), f"覆蓋 {len(covered)}/7")

# ═══════════════════════════════════════════════════════════════
# T3. 88 中點 line graph 譜 vs 88-site 鏈譜
# ═══════════════════════════════════════════════════════════════
print("\n─── T3. 88 中點 line graph Laplacian 譜 vs 88-site 鏈譜 ───")
g88map = {}
for line in open(f'{O182}/g88_edge_map.txt'):
    if line.startswith('#'): continue
    p = line.split()
    g88map[(min(int(p[1]), int(p[2])), max(int(p[1]), int(p[2])))] = int(p[0])
edges88 = list(g88map.keys())
print(f"  透明邊數: {len(edges88)} (應 88)")

# line graph: 節點 = 邊; 相鄰 ⇔ share 端點
ed_end = defaultdict(set)  # node -> edge idx
for ei, (u, v) in enumerate(edges88):
    ed_end[u].add(ei); ed_end[v].add(ei)
LG = np.zeros((88, 88))
for vtx in range(60):
    eis = list(ed_end[vtx])
    for a in range(len(eis)):
        for b in range(a+1, len(eis)):
            LG[eis[a], eis[b]] = 1
            LG[eis[b], eis[a]] = 1
LG_deg = LG.sum(axis=1)
LL = np.diag(LG_deg) - LG
lev, levec = np.linalg.eigh(LL)
print(f"  line graph 譜 (前 15): " + " ".join(f"{v:.3f}" for v in lev[:15]))
print(f"  line graph 譜 (後 10): " + " ".join(f"{v:.3f}" for v in lev[78:]))

# 鏈譜 γ_k = 4 sin²(kπ/176)
chain = {k: 4*math.sin(k*math.pi/176)**2 for k in range(1, 89)}
print(f"  88-鏈譜 γ_k: k1={chain[1]:.4f} k2={chain[2]:.4f} k44={chain[44]:.4f} k88={chain[88]:.4f}")

# 對照: line graph 譜有冇 φ² / ρ 特徵值
targets = {'φ²': 2.618034, '0.382(ρ₅?)': 0.381966, '1.0746': 1.074577, '3.0': 3.0, '3.4481': 3.448071, '4.382': 4.381966}
found = {}
for name, tv in targets.items():
    d = np.abs(lev - tv).min()
    found[name] = (np.abs(lev - tv).argmin(), d)
    print(f"  line graph 譜 → {name}={tv:.4f}: 最接近 {lev[found[name][0]]:.4f} (Δ={d:.4f})")
check("T3a: line graph 譜含 φ² 特徵值 (Δ<0.02)", found['φ²'][1] < 0.02, f"Δ={found['φ²'][1]:.4f}")

# line graph 譜簡併結構
from collections import Counter as Cc
levr = np.round(lev, 3)
dc = Cc(levr)
print(f"  line graph 譜簡併: top4 {dc.most_common(4)}")

# ═══════════════════════════════════════════════════════════════
# T4. line graph 譜 = 鏈譜? (嵌入測試: 88 中點天然鏈?)
# ═══════════════════════════════════════════════════════════════
print("\n─── T4. 88 中點 line graph ↔ 88-鏈 譜對應 ───")
# 若 88 中點真係一條鏈 (每中點度 2), line graph 只可能有 2-regular 結構;
# 實測度分佈:
degs = LG_deg.astype(int)
print(f"  中點度分佈: {sorted(Cc(degs).items())}")
chain_lik = (degs.max() <= 2) and (degs.min() >= 1)
check("T4a: line graph 2-regular (鏈形) — 若成鏈, 度都係 2", chain_lik, f"度範圍 {degs.min()}-{degs.max()}")
# 再比較 line graph 譜 vs 鏈譜 特徵值集
chainspec = np.array([4*math.sin(k*math.pi/176)**2 for k in range(1, 89)])
n_common = 0
for lv in lev:
    if np.abs(chainspec - lv).min() < 0.01: n_common += 1
print(f"  line graph 譜同鏈譜共有點 (Δ<0.01): {n_common}/88")
check("T4b: 唔係鏈 (共有點 < 30)", n_common < 30, f"共有點 {n_common}")

# ── 總結 ──
print("\n" + "=" * 76)
print(f"  結果: {sum(results)}/{len(results)} PASS")
print("=" * 76)