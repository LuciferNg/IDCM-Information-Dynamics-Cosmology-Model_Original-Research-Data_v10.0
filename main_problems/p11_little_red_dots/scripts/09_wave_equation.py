#!/usr/bin/env python3
"""
圖上波動方程 + 拓撲應變能 M_0
================================
1. 波動方程 ∂²ψ/∂t² = -Lψ → ω_k = √λ_k
2. 干涉核: G(hop, t) = Σ_k sin(ω_k t)/ω_k φ_k(i) φ_k(j)
3. 冷斑點源傳播: hop 空間嘅干涉峰值
4. M_0 = 32 條阻挫邊嘅拓撲應變能
"""
import math, json, os
import numpy as np

OUT_DIR = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p11_little_red_dots/data'
phi = (1 + 5**0.5)/2
M_sun = 1.989e30

print("="*72)
print("圖上波動方程 + 拓撲應變能 M_0")
print("="*72)

# ============ 1. 載入圖 ============
CMB_DATA = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/cmb_cold_spot/data'
nodes = []
with open(f'{CMB_DATA}/a5_nodes.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        nodes.append({'id': len(nodes), 'ra': float(p[0]), 'dec': float(p[1])})
N = len(nodes)

def ang_dist(ra1, dec1, ra2, dec2):
    r1, d1 = math.radians(ra1), math.radians(dec1)
    r2, d2 = math.radians(ra2), math.radians(dec2)
    cosd = math.sin(d1)*math.sin(d2) + math.cos(d1)*math.cos(d2)*math.cos(r1-r2)
    return math.degrees(math.acos(max(-1, min(1, cosd))))

d_mat = np.zeros((N, N))
for i in range(N):
    for j in range(N):
        d_mat[i,j] = ang_dist(nodes[i]['ra'], nodes[i]['dec'], nodes[j]['ra'], nodes[j]['dec'])

# 阻挫邊
frust_set = set()
with open(f'{CMB_DATA}/frustration_edges.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        frust_set.add((min(int(p[0]), int(p[1])), max(int(p[0]), int(p[1]))))

# 建圖 (加權)
adj = {i: [] for i in range(N)}
for i in range(N):
    cand = [(d_mat[i,j], j) for j in range(N) if j != i]
    cand.sort()
    for _, j in cand[:4]:
        cost = 2 if (min(i,j), max(i,j)) in frust_set else 1
        adj[i].append((j, cost))

# 鄰接矩陣
A = np.zeros((N, N))
for i in range(N):
    for j, c in adj[i]:
        A[i,j] = 1.0/c
D = np.diag(np.sum(A, axis=1))
L = D - A

# 歸一化拉普拉斯
D_inv_sqrt = np.diag(1.0 / np.sqrt(np.maximum(np.sum(A, axis=1), 1e-10)))
L_norm = D_inv_sqrt @ L @ D_inv_sqrt

# ============ 2. 本徵值 + 本徵向量 ============
print(f"計算 60×60 本徵分解...")
eigvals, eigvecs = np.linalg.eigh(L_norm)
eigvals = [max(0, v) for v in eigvals]

# 波方程本徵頻率 ω_k = √λ_k
omega_k = [math.sqrt(v) for v in eigvals]
print(f"前 10 個本徵頻率 ω_k = √λ_k:")
for i in range(min(10, len(omega_k))):
    print(f"  ω_{i} = {omega_k[i]:.6f}  (λ_{i} = {eigvals[i]:.6f})")

# 頻率間隔
d_omega = [omega_k[i+1] - omega_k[i] for i in range(min(5, len(omega_k)-1))]
print(f"前 5 個頻率間隔: {[f'{d:.6f}' for d in d_omega]}")

# ============ 3. 干涉核計算 ============
# 冷斑節點 (source)
cs_node = min(range(N), key=lambda i: ang_dist(209, -57, nodes[i]['ra'], nodes[i]['dec']))
print(f"\n冷斑節點: {cs_node}")

# 點源脈衝 ψ(t=0) = δ_{cs_node}, ∂ψ/∂t(t=0) = 0
# 解: ψ(t) = Σ_k cos(ω_k t) φ_k(cs_node) φ_k
# 能量密度: E(i) = |ψ(i)|²

# 對每個 hop 距離, 計算平均能量密度
# hop 距離矩陣 (無加權 BFS)
adj_u = {i: [v for v,_ in adj[i]] for i in range(N)}
def bfs(start):
    dist = [-1]*N
    q = [start]
    dist[start] = 0
    for u in q:
        for v in adj_u[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist

hop_dist = np.array([bfs(i) for i in range(N)])

# 干涉核: 對每個 hop h, 計算平均能量密度隨時間演化
# 簡化: 用時間平均 <|ψ(i)|²>_t = (1/2) Σ_k |φ_k(cs_node) φ_k(i)|²
# 因為 <cos²(ω_k t)>_t = 1/2

# 時間平均能量密度
E_avg = np.zeros(N)
for k in range(N):
    E_avg += 0.5 * (eigvecs[cs_node, k] * eigvecs[:, k])**2

# 按 hop 距離分組
hop_vals = list(range(0, 9))
E_by_hop = {h: [] for h in hop_vals}
for i in range(N):
    h = hop_dist[cs_node, i]
    if h in E_by_hop:
        E_by_hop[h].append(E_avg[i])

print(f"\n時間平均能量密度 vs Hop 距離:")
print(f"{'Hop':>5} {'平均能量':>10} {'節點數':>8} {'標準差':>10}")
for h in hop_vals:
    vals = E_by_hop[h]
    if vals:
        print(f"{h:>5} {np.mean(vals):>10.6f} {len(vals):>8} {np.std(vals):>10.6f}")

# 睇能量密度最高嘅節點
print(f"\n能量密度最高嘅 10 個節點:")
sorted_nodes = sorted(range(N), key=lambda i: E_avg[i], reverse=True)
for i in sorted_nodes[:10]:
    h = hop_dist[cs_node, i]
    print(f"  節點 {i}: E_avg={E_avg[i]:.6f} (hop={h})")

# ============ 4. 拓撲應變能 M_0 ============
print(f"\n{'='*72}")
print("4. 拓撲應變能 M_0")
print(f"{'='*72}")

# 32 條阻挫邊喺 2D 球面上嘅剪應變
# 每條阻挫邊嘅應變: 理想晶格 = 5-fold 對稱
# 阻挫 = 5-fold vs 6-fold 嘅 mismatch
# 應變能密度 ∝ (shear modulus) × (strain)²

# 球面半徑 = R_H = 4129.94 Mpc (IDCM Hubble radius)
R_H = 4129.94 * 3.086e22  # m
G = 6.674e-11
c = 3e8
H0 = 72.59  # km/s/Mpc

# 宇宙臨界能量密度
H0_s = H0 * 1e3 / 3.086e22
rho_crit = 3*H0_s**2/(8*math.pi*G)  # kg/m³
print(f"ρ_crit = {rho_crit:.3e} kg/m³")

# 拓撲應變能:
# 每條阻挫邊 = 理想晶格嘅 twist defect
# 應變量 ε = 理想對稱性偏差
# 對 5-fold vs 6-fold: ε = 1/5 - 1/6 = 1/30 = 0.0333
# shear modulus μ_s = ρ_crit × c² (晶格尺度)
# 每條邊體積 V_edge = (λ_sync/44)³ × (缺陷核比例)

# 用更簡單嘅結構途徑:
# M_0 = M_Pl × (R_H / L_P) × (N_frust / N_total) × φ^?
# 或者: M_0 = ρ_crit × (λ_sync/44)³ × N_frust × (strain factor)

# 先試基本: 應變能 = 模量 × 應變² × 體積
# shear modulus = ρ_crit × c²
mu = rho_crit * c**2
print(f"shear modulus μ = {mu:.3e} Pa")

# 阻挫應變
strain = 1/30  # 5-fold vs 6-fold mismatch
# 每條邊體積: 節點胞尺度 ~ λ_sync/44
lambda_sync = 294.88 * 3.086e22  # m
V_edge = (lambda_sync / 44)**3
print(f"V_edge = {V_edge:.3e} m³")

# 32 條邊總應變能
E_strain = 32 * mu * strain**2 * V_edge  # J
M_0_strain = E_strain / c**2  # kg
print(f"\n拓撲應變能 M_0 = {M_0_strain:.3e} kg = {M_0_strain/M_sun:.3e} M☉")
print(f"vs 1e6 M☉ → ratio = {M_0_strain/M_sun/1e6:.2f}")

# 如果 M_0 太大/太細, 調整因子
# 可能: 應變係 1/30 嘅修正, 或者體積係 (λ_sync/88)³
V_edge2 = (lambda_sync / 88)**3
E_strain2 = 32 * mu * (1/30)**2 * V_edge2
M_0_2 = E_strain2 / c**2
print(f"\n修正 (λ_sync/88)³:")
print(f"  M_0 = {M_0_2:.3e} kg = {M_0_2/M_sun:.3e} M☉")
print(f"  vs 1e6 M☉ → ratio = {M_0_2/M_sun/1e6:.2f}")

# 試應變 = φ⁻³ = 0.236
strain_phi = 1/phi**3
E_strain3 = 32 * mu * strain_phi**2 * V_edge
M_0_3 = E_strain3 / c**2
print(f"\n修正 (應變 = φ⁻³ = {strain_phi:.4f}):")
print(f"  M_0 = {M_0_3:.3e} kg = {M_0_3/M_sun:.3e} M☉")
print(f"  vs 1e6 M☉ → ratio = {M_0_3/M_sun/1e6:.2f}")

# 保存
results = {
    'eigenfrequencies': [float(w) for w in omega_k[:20]],
    'cs_node': int(cs_node),
    'energy_by_hop': {str(h): {'mean': float(np.mean(E_by_hop[h])),
                                'std': float(np.std(E_by_hop[h])),
                                'n': len(E_by_hop[h])}
                      for h in hop_vals if E_by_hop[h]},
    'M_0_strain_1_30': float(M_0_strain/M_sun),
    'M_0_strain_phi3': float(M_0_3/M_sun),
    'M_0_strain_half_scale': float(M_0_2/M_sun),
    'phi3': float(strain_phi)
}
with open(f'{OUT_DIR}/wave_equation_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved wave_equation_results.json")