#!/usr/bin/env python3
"""
O7 — 19_channel_structure_tests.py (2026-10-11)
====================================================================
O7/natural-write-closure 第五輪: 通道 ℓ 譜結構強制檢定
====================================================================
承接 docs/06 (三通道: A5/G88 ℓ=3 主導 vs G32 阻挫 ℓ=4 主導):

  C7. null 檢定: G120 隨機 32-subset ×2000 → 主導 ℓ 分佈 vs 觀察 G32 ℓ=4
  C8. Δ 檢定: 120 中點隨機 88/32 分割 ×2000 → Δ=(ℓ4−ℓ3)_阻−(ℓ4−ℓ3)_透 分佈
  C9. 20 縫合線翻轉族: 翻轉 k 條縫合線 → 新阻挫邊集 → 新 G32 ℓ 譜
      → 「ℓ=4 主導」係咪位元空間普遍結構 (結構強制) 定單一著色特異

數據: O182 (g88/g32 中點座標 + temps2 json) + cmb_cold_spot (a5_nodes, faces,
      frustration_edges, anchored_coloring) — 全部由零重建, 唔 import 上游。
"""

import math, re, json
from collections import defaultdict, deque
import numpy as np
from scipy.optimize import linear_sum_assignment

DATA = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/cmb_cold_spot/data'
O182 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o182_88grid_geometry/data'

results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

print("=" * 76)
print("  O7 — 通道 ℓ 譜結構強制檢定 (C7-C9)")
print("=" * 76)

# ═══════════ 載入 + 幾何 ═══════════
nodes = []
for i, line in enumerate(open(f'{DATA}/a5_nodes.txt')):
    if line.startswith('#'): continue
    p = line.split(); nodes.append((float(p[0]), float(p[1])))
nodes = np.array(nodes)
ra, dec = np.radians(nodes[:, 0]), np.radians(nodes[:, 1])
xyz = np.array([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)]).T

def unit_radec(r, d):
    return np.array([np.cos(math.radians(d))*np.cos(math.radians(r)),
                     np.cos(math.radians(d))*np.sin(math.radians(r)),
                     np.sin(math.radians(d))])

def midpoint_radec(u, v):
    m = xyz[u] + xyz[v]; m = m/np.linalg.norm(m)
    return math.degrees(math.atan2(m[1], m[0])) % 360, math.degrees(math.asin(np.clip(m[2], -1, 1)))

def ang(a, b):
    return math.degrees(math.acos(np.clip(np.dot(unit_radec(*a), unit_radec(*b)), -1, 1)))

# 圖 + 著色 + frust
adj = defaultdict(set)
for line in open(f'{DATA}/faces.txt'):
    if line.startswith('#'): continue
    m = re.search(r'\[([^\]]+)\]', line)
    vs = [int(x) for x in m.group(1).split(',')]
    for i in range(len(vs)):
        adj[vs[i]].add(vs[(i+1) % len(vs)])
        adj[vs[(i+1) % len(vs)]].add(vs[i])
col = {}
for line in open(f'{DATA}/anchored_coloring.txt'):
    if line.startswith('#'): continue
    p = line.split(); col[int(p[0])] = int(p[3])

frust = []
for line in open(f'{DATA}/frustration_edges.txt'):
    if line.startswith('#'): continue
    p = line.split(); frust.append((int(p[0]), int(p[1])))
frust = [tuple(sorted(e)) for e in frust]
frust_set = set(frust)

# 全部 120 邊 + 中點 (座標)
g88 = np.loadtxt(f'{O182}/g88_nodes.txt')
g32m = np.loadtxt(f'{O182}/g32_frustration_midpoints.txt')
g120 = np.vstack([g88, g32m])
T120 = np.array(json.load(open(f'{O182}/temps2_SMICA_4.17deg.json'))['G120_all'])

# 邊 -> 120 idx (透明 via g88map, 阻挫 via 配對)
g88map = {}
for line in open(f'{O182}/g88_edge_map.txt'):
    if line.startswith('#'): continue
    p = line.split(); g88map[(int(p[1]), int(p[2]))] = int(p[0])

all_edges = []
all_coords = []
for (u, v), idx in g88map.items():
    all_edges.append((min(u, v), max(u, v)))
    all_coords.append(g88[idx])

# 阻挫邊配對
D = np.zeros((32, 32))
mid_of = {}
for i, (u, v) in enumerate(frust):
    mid_of[(u, v)] = (u, v)
    mr, md = midpoint_radec(u, v)
    for j in range(32):
        D[i, j] = ang((mr, md), g32m[j])
ri, ci = linear_sum_assignment(D)
edge2idx = dict(g88map)
for i, j in zip(ri, ci):
    edge2idx[frust[i]] = 88 + j

# 球面譜
from astropy.coordinates import SkyCoord
import astropy.units as AU
from scipy.special import lpmv
from math import factorial, sqrt
def sphere_spectrum(coords, vals, lmax=4):
    sc = SkyCoord(ra=coords[:, 0]*AU.deg, dec=coords[:, 1]*AU.deg, frame='icrs')
    xyzs = sc.cartesian.xyz.value
    x, y, z = xyzs[0], xyzs[1], xyzs[2]
    th = np.arccos(np.clip(z, -1, 1)); ph = np.arctan2(y, x)
    amps = {}
    for l in range(lmax+1):
        coefs = []
        for m in range(-l, l+1):
            plm = lpmv(abs(m), l, np.cos(th))
            norm = sqrt((2*l+1)*factorial(l-abs(m))/(4*math.pi*factorial(l+abs(m))))
            if m == 0: Y = norm * plm
            elif m > 0: Y = sqrt(2)*norm * plm * np.cos(m*ph)
            else: Y = sqrt(2)*norm * plm * np.sin(-m*ph)
            coefs.append(np.dot(Y, vals)/np.dot(Y, Y))
        amps[l] = sqrt(sum(c*c for c in coefs))
    return amps

def dom(arr):
    return max(range(5), key=arr.get)

# ── 觀察 G32 ──
obs32 = np.array([T120[edge2idx[e]] for e in frust])
obs_amps = sphere_spectrum(g32m, obs32)
print(f"  觀察 G32 ℓ 譜: " + " ".join(f"ℓ{l}={obs_amps[l]:.1f}" for l in range(5)) + f" → dom ℓ={dom(obs_amps)}")
obs_dom = dom(obs_amps)

# ═══════════════════════════════════════════════════════════════
# C7. 隨機 32-subset null
# ═══════════════════════════════════════════════════════════════
print("\n─── C7. 隨機 32-subset (2000×) vs 觀察 G32 dom ℓ=4 ───")
rng = np.random.default_rng(7)
null_dom = []
null_l4l3 = []
for k in range(2000):
    sub = rng.choice(120, 32, replace=False)
    amps = sphere_spectrum(g120[sub], T120[sub])
    null_dom.append(dom(amps))
    null_l4l3.append(amps[4] - amps[3])
null_dom = np.array(null_dom)
null_l4l3 = np.array(null_l4l3)
cnt4 = (null_dom == 4).mean()
print(f"  null dom ℓ 分佈: ℓ3={ (null_dom==3).mean():.3f} ℓ4={(null_dom==4).mean():.3f} 其他={(null_dom!=3)&(null_dom!=4)}")
print(f"  null P(dom=ℓ4) = {cnt4:.3f}")
obs_l4l3 = obs_amps[4] - obs_amps[3]
z_l4l3 = (obs_l4l3 - null_l4l3.mean()) / null_l4l3.std()
p_l4l3 = (np.abs(null_l4l3) >= abs(obs_l4l3)).mean()
print(f"  Δ(ℓ4−ℓ3): 觀察 {obs_l4l3:+.2f} vs null {null_l4l3.mean():+.2f}±{null_l4l3.std():.2f} → z={z_l4l3:+.2f}, |Δ| p={p_l4l3:.4f}")
check("C7a: 觀察 dom ℓ=4 唔係隨機 32-subset 偶然 (z>2)", abs(z_l4l3) > 2.0, f"z={z_l4l3:+.2f}")

# ═══════════════════════════════════════════════════════════════
# C8. 隨機 88/32 分割 Δ 檢定 (透明 vs 阻挫 標籤置換)
# ═══════════════════════════════════════════════════════════════
print("\n─── C8. 隨機 88/32 分割 Δ 檢定 (2000×) ───")
G88_c = g88; T88_c = T120[:88]
obs_delta = (obs_amps[4]-obs_amps[3]) - ((sphere_spectrum(G88_c, T88_c))[4] - sphere_spectrum(G88_c, T88_c)[3])
null_delta = np.zeros(2000)
for k in range(2000):
    perm = rng.permutation(120)
    sel32, sel88 = perm[:32], perm[32:]
    a32 = sphere_spectrum(g120[sel32], T120[sel32])
    a88 = sphere_spectrum(g120[sel88], T120[sel88])
    null_delta[k] = (a32[4]-a32[3]) - (a88[4]-a88[3])
z_d = (obs_delta - null_delta.mean()) / null_delta.std()
p_d = (np.abs(null_delta) >= abs(obs_delta)).mean()
print(f"  Δ_obs = {obs_delta:+.2f} vs null {null_delta.mean():+.2f}±{null_delta.std():.2f} → z={z_d:+.2f}, p={p_d:.4f}")
check("C8a: 透明/阻挫分割 Δ 顯著 (|z|>2)", abs(z_d) > 2.0, f"z={z_d:+.2f} p={p_d:.4f}")

# ═══════════════════════════════════════════════════════════════
# C9. 20 縫合線翻轉家族 — ℓ=4 主導係咪位元空間普遍
# ═══════════════════════════════════════════════════════════════
print("\n─── C9. 20 縫合線翻轉家族 (結構強制測試) ───")
dg = {v: sum(1 for e in frust if v in e) for v in range(60)}
frust_nodes = [v for v in range(60) if dg[v] > 0]
seen = set(); seams = []
for s in frust_nodes:
    if s in seen: continue
    comp = []; q = deque([s]); seen.add(s)
    while q:
        u = q.popleft(); comp.append(u)
        for w in [x for x in frust_nodes if (min(u,x),max(u,x)) in frust_set and x not in seen]:
            seen.add(w); q.append(w)
    if len(comp) >= 2: seams.append(sorted(comp))
seam_edges = []
for comp in seams:
    es = []
    for u in comp:
        for v in comp:
            if u < v and (u, v) in frust_set:
                es.append((u, v))
    seam_edges.append(es)
print(f"  縫合線: {len(seams)} 條; 邊數: {[len(e) for e in seam_edges]}")

def flip_frust(flipped):
    """翻轉指定縫合線(端點色反) → 新阻挫邊集"""
    newcol = dict(col)
    for si in flipped:
        for v in seams[si]:
            newcol[v] = 1 - newcol[v]
    F = set()
    for u in range(60):
        for v in adj[u]:
            if u < v and newcol[u] == newcol[v]:
                F.add((u, v))
    return F

# 單翻 20 條
fam_dom = []
fam_l4l3 = []
samples = list(range(20))
# 加多翻隨機 500 次 (結構空間抽樣)
for k in range(500):
    ns = int(rng.integers(1, 8))
    samples.append(tuple(int(x) for x in rng.choice(20, ns, replace=False)))
for tag in samples:
    F = flip_frust(tag if isinstance(tag, tuple) else (tag,))
    # F 嘅邊 -> 中點座標 + 溫度
    coords = []; vals = []
    for (u, v) in F:
        if (u, v) in edge2idx:
            idx = edge2idx[(u, v)]
            coords.append(g120[idx]); vals.append(T120[idx])
        elif (v, u) in edge2idx:
            idx = edge2idx[(v, u)]
            coords.append(g120[idx]); vals.append(T120[idx])
        else:
            coords.append(midpoint_radec(u, v)); vals.append(0.0)
    coords = np.array(coords); vals = np.array(vals)
    if len(vals) < 15: continue
    amps = sphere_spectrum(coords, vals)
    fam_dom.append(dom(amps))
    fam_l4l3.append(amps[4]-amps[3])
fam_dom = np.array(fam_dom); fam_l4l3 = np.array(fam_l4l3)
print(f"  家族點數: {len(fam_dom)} (20 單翻 + 500 多翻)")
print(f"  家族 dom ℓ 分佈: " + " ".join(f"ℓ{l}={ (fam_dom==l).mean():.3f}" for l in range(5)))
z_fam = (obs_l4l3 - fam_l4l3.mean()) / fam_l4l3.std()
p_fam = (np.abs(fam_l4l3) >= abs(obs_l4l3)).mean()
print(f"  家族 Δ(ℓ4−ℓ3): mean {fam_l4l3.mean():+.2f}±{fam_l4l3.std():.2f}; 觀察 {obs_l4l3:+.2f} → z={z_fam:+.2f}, p={p_fam:.4f}")
check("C9a: 觀察 ℓ4 主導喺翻轉家族內係優勢 (dom ℓ4 佔多數)", (fam_dom == 4).mean() > 0.5, f"domℓ4={(fam_dom==4).mean():.3f}")

# ── 總結 ──
print("\n" + "=" * 76)
print(f"  結果: {sum(results)}/{len(results)} PASS")
print("=" * 76)