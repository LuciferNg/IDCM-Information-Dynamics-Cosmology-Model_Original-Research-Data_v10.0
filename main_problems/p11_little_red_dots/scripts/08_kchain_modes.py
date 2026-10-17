#!/usr/bin/env python3
"""
K_Chain 駐波模態 + 應力傳播格林函數
=======================================
1. 44 個 K_Chain 模態: ω_n = 2|sin(πn/88)|, v_g = dω/dk
   - Channel 22 (n=22): v_g=0 駐波
   - Channel 44 (n=44): v_g=0 駐波
   - 零點能 M_0 = Σ (1/2) ħ ω_n × (幾何因子)

2. 應力傳播格林函數:
   - 加權圖上嘅離散熱核/擴散核
   - G(i,j) = Σ_k λ_k^(-hop) φ_k(i) φ_k(j)
   - 檢查本徵值 λ_k 係咪收斂到 φ
"""
import math, json, os
import numpy as np

OUT_DIR = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p11_little_red_dots/data'
phi = (1 + 5**0.5)/2
M_sun = 1.989e30
M_Pl = 2.176e-8
hbar = 1.054571817e-34
c = 3e8
H0 = 72.59  # km/s/Mpc

print("="*72)
print("K_Chain 駐波模態 + 應力張量場")
print("="*72)

# ============ 1. K_Chain 44 模態 ============
N_d = 44
print(f"\n1. K_Chain 44 模態 (n=1..{N_d})")
print(f"{'n':>4} {'γ_n':>10} {'ω_n':>10} {'v_g':>10} {'駐波?':>6}")

# M_0 = 零點能總和
# 每個模態能量: E_n = (1/2) ħ ω_n × ω_sync? 
# 物理: ω_n 係 γ_n 嘅平方根, γ_n = 4 sin²(πn/88)
# 同步頻率: ω_sync = 2π/T_sync
T_sync = 84.64e9 * 3.156e7  # s
omega_sync = 2*math.pi / T_sync

M_0_kg = 0
M_0_modes = {}

for n in range(1, N_d + 1):
    gamma_n = 4 * math.sin(math.pi * n / (2*N_d))**2
    omega_n = 2 * abs(math.sin(math.pi * n / (2*N_d)))
    # v_g ∝ dω/dk = cos(πn/88) (離散近似)
    v_g = abs(math.cos(math.pi * n / (2*N_d)))
    is_standing = v_g < 0.01  # 駐波判據
    
    # 零點能: E = hbar * omega_n * omega_sync / 2?
    # 更合理: 每個模態貢獻 M_Pl × ω_n / N_d
    E_n = hbar * omega_n * omega_sync / 2
    M_n = E_n / c**2
    
    if is_standing:
        M_0_modes[n] = M_n
        M_0_kg += M_n
    
    print(f"{n:>4} {gamma_n:>10.6f} {omega_n:>10.6f} {v_g:>10.4f} {'✓' if is_standing else '':>6}")

print(f"\n駐波模態 (v_g ≈ 0): n = {list(M_0_modes.keys())}")
print(f"M_0 (零點能) = {M_0_kg:.3e} kg = {M_0_kg/M_sun:.3e} M☉")
print(f"vs 觀測 1e6 M☉ → ratio = {M_0_kg/M_sun/1e6:.2e}")

# 如果 M_0 太細, 需要「凝聚增強因子」
# 駐波模態嘅能量唔係直接加, 而係乘 N_beat (凝聚嘅 beat 數)
# 每個節點嘅 N_beat ∝ degree = 4
# 增強因子 = 4 × 44 × (幾何因子)?
enhance = 4 * N_d * phi**2  # 猜測: 度數 × 維度 × φ²
print(f"M_0 × 增強因子 (4×44×φ²): {M_0_kg*enhance/M_sun:.3e} M☉")
print(f"  vs 1e6 M☉ → ratio = {M_0_kg*enhance/M_sun/1e6:.2f}")

# ============ 2. 應力傳播格林函數 ============
print(f"\n{'='*72}")
print("2. 應力傳播格林函數 — φ^(-hop) 驗證")
print(f"{'='*72}")

# 載入加權圖
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

# 建圖 (加權鄰接矩陣)
adj = {i: [] for i in range(N)}
for i in range(N):
    cand = [(d_mat[i,j], j) for j in range(N) if j != i]
    cand.sort()
    for _, j in cand[:4]:
        cost = 2 if (min(i,j), max(i,j)) in frust_set else 1
        adj[i].append((j, cost))

# 拉普拉斯矩陣 L = D - A
# D = degree matrix (加權)
A = np.zeros((N, N))  # 鄰接矩陣 (加權)
for i in range(N):
    for j, c in adj[i]:
        A[i,j] = 1.0/c  # 權重 = 1/cost

D = np.diag(np.sum(A, axis=1))
L = D - A

# 歸一化拉普拉斯 L_norm = D^(-1/2) L D^(-1/2)
D_inv_sqrt = np.diag(1.0 / np.sqrt(np.maximum(np.sum(A, axis=1), 1e-10)))
L_norm = D_inv_sqrt @ L @ D_inv_sqrt

eigvals = np.linalg.eigvalsh(L_norm)
eigvals = sorted([max(0, v) for v in eigvals])

print(f"歸一化拉普拉斯本徵值 (最小 10 個):")
for i in range(min(10, len(eigvals))):
    print(f"  λ_{i} = {eigvals[i]:.8f}")

# 第二小本徵值 λ₁ (譜隙)
lambda_1 = eigvals[1] if len(eigvals) > 1 else 0
print(f"\n譜隙 λ₁ = {lambda_1:.8f}")
print(f"ln(φ) = {math.log(phi):.8f}")
print(f"λ₁ vs ln(φ): 偏差 {abs(lambda_1 - math.log(phi))/math.log(phi)*100:.2f}%")

# 擴散核: exp(-λ₁ × hop) vs φ^(-hop) = exp(-hop × ln(φ))
print(f"\n擴散核比較:")
for hop in range(1, 9):
    g_actual = math.exp(-lambda_1 * hop)
    g_phi = phi ** (-hop)
    print(f"  hop={hop}: exp(-λ₁·hop)={g_actual:.6f} vs φ^(-{hop})={g_phi:.6f} (ratio={g_actual/g_phi:.4f})")

# 保存
results = {
    'k_chain_modes': {str(n): {'gamma': float(4*math.sin(math.pi*n/(2*N_d))**2),
                                'omega': float(2*abs(math.sin(math.pi*n/(2*N_d)))),
                                'v_g': float(abs(math.cos(math.pi*n/(2*N_d)))),
                                'is_standing': abs(math.cos(math.pi*n/(2*N_d))) < 0.01}
                      for n in range(1, N_d+1)},
    'M_0_zero_point': float(M_0_kg),
    'M_0_solar': float(M_0_kg/M_sun),
    'M_0_enhanced': float(M_0_kg*enhance/M_sun),
    'laplacian_eigenvalues': [float(v) for v in eigvals[:10]],
    'lambda_1': float(eigvals[1]),
    'phi_inv': 1/phi,
    'exp_lambda_1': float(math.exp(-eigvals[1])),
    'exp_lambda_2': float(math.exp(-eigvals[2])) if len(eigvals) > 2 else None
}

os.makedirs(OUT_DIR, exist_ok=True)
with open(f'{OUT_DIR}/k_chain_modes.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved k_chain_modes.json")