#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P11 攻堅 — 𝒫∘W 模態對對稱性測試 (2026-10-17)
================================================
問題: 視線遮蔽算子 τ(v) 從缺 (records 27-29). 但 IDCM 有兩個已閉合結構:
  - O143 𝒫: 88-site 環 → 60 A₅ 天球節點投影 (高斯窗口, Galactic longitude 環相位)
  - O179 W(i): 60 節點位置權重 w = (frust+1)·[1+C·cos(π·hop/4)], C=B/L₅=4/11

結構假設: 模態 k 嘅「觀察者投影權重」= τ_mode(k) = (𝒫^T W)_k = Σ_i P[i,k]·W(i)
若對共軛模態對 (k, 88−k) [≡(k,176−k) mod 88] 失衡 ⟹ 結構性遮蔽失衡 (零新常數)
若對稱 ⟹ 遮蔽唔可能由已閉合結構產生 (再集中搵新結構)

注意: 呢個係結構測試, 唔係 fit 任何觀測 dip — 零參數, 禁凑.
"""
import math
import numpy as np

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
NODES = f'{BASE}/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
FRUST = f'{BASE}/main_problems/p4_cmb_cold_spot/data/frustration_edges.txt'

# ── 譜量 (O179) ──
B, L5, C = 4, 11, 4/11
N_sites = 88

print("="*74)
print("𝒫∘W 模態對對稱性 — 零參數結構測試")
print("="*74)

# ── 1. 節點 + 阻挫邊 (O179 同款) ──
nodes = np.loadtxt(NODES)
assert nodes.shape == (60, 2)
N = 60
frust_set = set()
with open(FRUST) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        p = line.split()
        u, v = int(p[0])-1, int(p[1])-1
        frust_set.add((min(u, v), max(u, v)))
assert len(frust_set) == 32

def ang_dist(ra1, dec1, ra2, dec2):
    r1, d1 = math.radians(ra1), math.radians(dec1)
    r2, d2 = math.radians(ra2), math.radians(dec2)
    cosd = math.sin(d1)*math.sin(d2) + math.cos(d1)*math.cos(d2)*math.cos(r1-r2)
    return math.degrees(math.acos(max(-1, min(1, cosd))))

d_mat = np.zeros((N, N))
for i in range(N):
    for j in range(N):
        d_mat[i, j] = ang_dist(nodes[i,0], nodes[i,1], nodes[j,0], nodes[j,1])

adj = {i: [] for i in range(N)}
for i in range(N):
    cand = sorted((d_mat[i,j], j) for j in range(N) if j != i)
    adj[i] = [j for _, j in cand[:4]]
adj_sym = {i: set(adj[i]) for i in range(N)}
for i in range(N):
    for j in list(adj_sym[i]):
        adj_sym[j].add(i)

def bfs(start):
    dist = [-1]*N
    q = [start]; dist[start] = 0
    for u in q:
        for v in adj_sym[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist

cs_node = min(range(N), key=lambda i: ang_dist(209, -57, nodes[i,0], nodes[i,1]))
hop = bfs(cs_node)

frust_count = {i: 0 for i in range(N)}
for (u, v) in frust_set:
    frust_count[u] += 1
    frust_count[v] += 1

# ── 2. W(i) (O179 已閉合) ──
W = np.zeros(N)
for i in range(N):
    E_i = 1 + C*math.cos(math.pi*hop[i]/4)
    W[i] = E_i * (frust_count[i] + 1)
W_norm = W / W.sum()
print(f"\nW(i): Σ={W.sum():.4f}, min={W.min():.4f}, max={W.max():.4f}, "
      f"max/min={W.max()/W.min():.3f}")

# ── 3. 𝒫 (O143 同款, 用 Galactic longitude — astropy 精確) ──
from astropy.coordinates import SkyCoord
import astropy.units as u
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_arr = np.array([float(g.l.deg) for g in gal])
b_arr = np.array([float(g.b.deg) for g in gal])

x_k = np.linspace(0, 2*np.pi, N_sites, endpoint=False)
sigma_site = 2*np.pi / N_sites
P = np.zeros((N, N_sites))
for i in range(N):
    phi_i = math.radians(l_arr[i] % 360)
    dphi = np.abs(x_k - phi_i)
    dphi = np.minimum(dphi, 2*np.pi - dphi)
    P[i, :] = np.exp(-0.5*(dphi/sigma_site)**2)
# 歸一化每節點
P = P / P.sum(axis=1, keepdims=True)

# ── 4. 複合: τ_mode(k) = (𝒫^T W)_k ──
tau_mode = P.T @ W_norm
# 對稱化測試: k vs 88−k (0-indexed site; 模態對 k,176−k → site 88−(k+1))
pairs = []
for k in range(N_sites//2):
    k2 = (N_sites - k) % N_sites  # 對偶 site
    r = tau_mode[k] / tau_mode[k2]
    pairs.append((k+1, k2+1, tau_mode[k], tau_mode[k2], r))

print(f"\n模態對 (k, 176−k) 投影權重比:")
print(f"{'k':>4} {'176−k':>6} {'τ(k)':>12} {'τ(176−k)':>12} {'ratio':>10}")
devs = []
for k, k2, t1, t2, r in pairs:
    devs.append(abs(math.log(r)))
    flag = '⚠' if abs(math.log(r)) > 0.01 else ''
    if k <= 8 or abs(math.log(r)) > 0.01:
        print(f"{k:>4} {k2:>6} {t1:>12.6f} {t2:>12.6f} {r:>10.5f} {flag}")

max_dev = max(devs)
mean_dev = float(np.mean(devs))
print(f"\n最大 |ln ratio| = {max_dev:.5f}  (1% 對應 0.01)")
print(f"平均 |ln ratio| = {mean_dev:.5f}")
print(f"⚠ threshold: |ln|>0.01 的對數目 = {sum(1 for d in devs if d>0.01)}/44")

# ── 5. 判定 ──
print("\n" + "="*74)
if max_dev < 0.01:
    print("[PASS 對稱] 𝒫^T·W 對模態對完全對稱 ⟹ 已閉合結構唔可能產生遮蔽失衡")
    print("          遮蔽算子需新結構 (唔係 𝒫∘W)")
else:
    print("[FAIL 失衡] 𝒫^T·W 對模態對失衡 ⟹ 結構性遮蔽失衡存在 (零新參數!)")
    worst = max(pairs, key=lambda p: abs(math.log(p[4])))
    print(f"          最失衡: k={worst[0]}/176−{worst[1]}, ratio={worst[4]:.4f}")
    print(f"          需檢查係咪孤點 (單模態) 定系統性 (全譜)")
print("="*74)

# 存 JSON
import json, os
out = {
    'tau_mode_ratio': {f'{k}': {f'pair_{k2}': float(r)} for k, k2, t1, t2, r in pairs},
    'max_abs_ln_ratio': float(max_dev),
    'mean_abs_ln_ratio': float(mean_dev),
    'n_over_1pct': int(sum(1 for d in devs if d > 0.01)),
}
os.makedirs(f'{BASE}/main_problems/p11_little_red_dots/data', exist_ok=True)
with open(f'{BASE}/main_problems/p11_little_red_dots/data/33_pw_projection_weights.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f"\nSaved: data/33_pw_projection_weights.json")