#!/usr/bin/env python3
"""
B01_spectrum_check.py — O4_renew B 部分: 圖譜獨立重驗證
=================================================================
B1: λ₂ = 0.381966011250? (numpy 直接算)
B2: 多重度 3?
B3: vertex-transitive 60/60?
B4: 隨機對照 λ₂ ≈ 0?
"""
import numpy as np
import math
from collections import defaultdict, deque

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh'
phi = (1 + 5**0.5) / 2
print("=" * 72)
print("O4_renew B01: 圖譜獨立驗證")
print("=" * 72)

# ---------- 圖 ----------
nodes = np.loadtxt(f'{BASE}/cmb_cold_spot/data/a5_nodes.txt')
def radec_to_vec(ra, dec):
    r = math.radians(ra); d = math.radians(dec)
    return np.array([math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d)])
vecs = np.array([radec_to_vec(r, d) for r, d in nodes])

adj = defaultdict(set)
edges = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j); adj[j].add(i)
            edges.append((i, j))

# ---------- B1: Laplacian 譜 ----------
A = np.zeros((60, 60))
for u, v in edges:
    A[u, v] = 1; A[v, u] = 1
D = np.diag(A.sum(axis=1))
L = D - A
eigvals = np.linalg.eigvalsh(L)
eigvals_sorted = np.sort(eigvals)

print(f"\nB1: Laplacian 特徵值 (numpy 直接計算)")
print(f"    λ₀ = {eigvals_sorted[0]:.15f}")
print(f"    λ₁ = {eigvals_sorted[1]:.15f}")
print(f"    λ₂ = {eigvals_sorted[2]:.15f}")
print(f"    λ₃ = {eigvals_sorted[3]:.15f}")
print(f"    λ₄ = {eigvals_sorted[4]:.15f}")

# 目標: λ₂ = φ⁻² = 0.381966011250
target = phi**-2
dev = abs(eigvals_sorted[1] - target)  # 注意: λ₁ (index 1) 先係非零
print(f"\n    φ⁻² = {target:.15f}")
print(f"    λ₁ vs φ⁻² 偏差 = {dev:.3e}")
print(f"    → {'✅ λ₂ = φ⁻²' if dev < 1e-10 else '❌ 唔等於'}")

# 注意: 應該用 λ₁ (第一個非零) 定 λ₂ (第二個非零)?
# 如果 λ₀=0 且 λ₁=λ₂=λ₃ (多重度 3), 咁 λ₁ 就係「第二小」(即 λ₂ 嘅意思)
print(f"\n    檢查: λ₁ = λ₂ = λ₃ (多重度 3)?")
print(f"    λ₁={eigvals_sorted[1]:.10f}, λ₂={eigvals_sorted[2]:.10f}, λ₃={eigvals_sorted[3]:.10f}")
m3 = abs(eigvals_sorted[1]-eigvals_sorted[2]) < 1e-10 and abs(eigvals_sorted[2]-eigvals_sorted[3]) < 1e-10
print(f"    → {'✅ 多重度 3' if m3 else '❌ 唔係多重度 3'}")

# 全部特徵值
print(f"\n    完整譜 (前 15):")
for k in range(15):
    print(f"      λ_{k} = {eigvals_sorted[k]:.6f}")

# ω = √λ
w2 = math.sqrt(eigvals_sorted[1])
print(f"\nB1b: ω = √λ₁ = {w2:.15f}")
print(f"    φ⁻¹ = {phi**-1:.15f}")
print(f"    偏差 = {abs(w2 - phi**-1):.3e}")
print(f"    → {'✅ ω = φ⁻¹' if abs(w2 - phi**-1) < 1e-10 else '❌ 唔等於'}")

# ---------- B3: vertex-transitive ----------
print(f"\nB3: vertex-transitive 檢查")
profiles = {}
for seed in range(60):
    d = {seed: 0}
    q = deque([seed])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in d:
                d[v] = d[u] + 1
                q.append(v)
    prof = tuple(sorted(d.values()).count(k) for k in range(max(d.values())+1))
    profiles[prof] = profiles.get(prof, 0) + 1
print(f"    唔同 profile 數 = {len(profiles)}")
for p, c in profiles.items():
    print(f"      {p}: {c} 個節點")
print(f"    → {'✅ vertex-transitive (60/60 同一 profile)' if len(profiles)==1 else '❌ 唔係 vertex-transitive'}")

# ---------- B4: 隨機對照 ----------
print(f"\nB4: 隨機 60 點圖對照 (λ₂)")
rng = np.random.default_rng(42)
lam2_random = []
connected = 0
for trial in range(30):
    # 隨機 60 點喺球面
    pts = rng.normal(size=(60, 3))
    pts = pts / np.linalg.norm(pts, axis=1, keepdims=True)
    # 建圖 (最近鄰, 保證 degree 4)
    radj = defaultdict(set)
    for i in range(60):
        d_all = np.degrees(np.arccos(np.clip(pts @ pts[i], -1, 1)))
        nn = np.argsort(d_all)[1:5]  # 4 最近
        for j in nn:
            radj[i].add(int(j)); radj[int(j)].add(i)
    # 連通性檢查
    seen = {0}
    q = deque([0])
    while q:
        u = q.popleft()
        for v in radj[u]:
            if v not in seen:
                seen.add(v); q.append(v)
    if len(seen) < 60:
        continue
    connected += 1
    rA = np.zeros((60, 60))
    for u in range(60):
        for v in radj[u]:
            rA[u, v] = 1
    rL = np.diag(rA.sum(axis=1)) - rA
    rev = np.sort(np.linalg.eigvalsh(rL))
    lam2_random.append(rev[1])
lam2_random = np.array(lam2_random)
print(f"    連通隨機圖: {connected}/30")
if len(lam2_random):
    print(f"    隨機 λ₂: mean={np.mean(lam2_random):.4f} ± {np.std(lam2_random):.4f}")
    print(f"    A₅ λ₂ = {target:.4f}")
    print(f"    → {'✅ A₅ λ₂ 結構性稀有' if abs(np.mean(lam2_random) - target) > 3*np.std(lam2_random) else '❌ 隨機圖都出到'}")
else:
    print(f"    ❌ 冇連通隨機圖")

with open(f'{BASE}/o4_renew/data/B01_spectrum.txt', 'w') as f:
    f.write("# O4_renew B01: 圖譜驗證\n")
    f.write(f"lambda1={eigvals_sorted[1]:.15f} target={target:.15f} dev={dev:.3e}\n")
    f.write(f"omega={w2:.15f} phi_inv={phi**-1:.15f} dev={abs(w2-phi**-1):.3e}\n")
    f.write(f"mult3={m3} vertex_transitive={len(profiles)==1}\n")
    if len(lam2_random):
        f.write(f"random_lambda2_mean={np.mean(lam2_random):.4f} std={np.std(lam2_random):.4f} n={len(lam2_random)}\n")
print(f"\n✅ 已存: data/B01_spectrum.txt")
