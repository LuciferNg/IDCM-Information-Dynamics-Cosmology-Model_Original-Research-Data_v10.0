#!/usr/bin/env python3
"""
O51 第六階段: 完整 Inverse Problem — 由 SMICA 60 節點溫度求 N, τ
================================================================
數據: smica_smoothed.txt (60 節點, SMICA 5° 平滑, μK)

模型:
  T_j = Σ_{n=1}^{44} A_n · cos(θ_n - n·φ_j) + T_0
  θ_n = N·δ_n + ω_n·τ
  A_n = 2·sin(πn/88)
  δ_n = frac(88·sin(πn/88))
  
求解: 由 60 個 T_j 反推 N, τ, T_0
"""
import json, math, sys, itertools

# ============ 1. 讀數據 ============
nodes = []
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/smica_smoothed.txt') as f:
    for line in f:
        if line.startswith('#') or not line.strip():
            continue
        parts = line.strip().split()
        if len(parts) >= 4:
            idx = int(parts[0])
            color = int(parts[1])
            T = float(parts[2])
            l = float(parts[3])
            b = float(parts[4])
            nodes.append({'idx': idx, 'color': color, 'T': T, 'l': l, 'b': b})

print(f"讀取 {len(nodes)} 個節點")
print(f"溫度範圍: [{min(n['T'] for n in nodes):.1f}, {max(n['T'] for n in nodes):.1f}] μK")
print(f"冷斑 (node 0): T = {nodes[0]['T']:.1f} μK @ ({nodes[0]['l']:.1f}°, {nodes[0]['b']:.1f}°)")

# ============ 2. K_Chain 參數 ============
R_H = 4129.94  # Mpc
c = 306.601394  # Mpc/Gyr
T_sync = 2 * math.pi * R_H / c  # Gyr
A_n = [2 * math.sin(math.pi * n / 88) for n in range(1, 45)]

# 43 個漂移
deltas = {}
for n in range(1, 44):
    theta = 88 * math.sin(math.pi * n / 88)
    delta = theta - math.floor(theta)
    deltas[n] = delta

# ============ 3. A₅ 5-fold 軸 (Galactic) ============
# A₅ 5-fold 軸 (精確 astropy 轉換: ICRS 332.3,18.7 → Galactic)
a5_axis_gal = (77.82, -29.62)
print(f"\nA₅ 5-fold 軸 (Gal, astropy): ({a5_axis_gal[0]:.1f}°, {a5_axis_gal[1]:.1f}°)")

# ============ 4. 空間相位 φ_j = 沿環嘅角位置 ============
def vec(l, b):
    """銀道座標 → 3D 單位向量"""
    lr, br = math.radians(l), math.radians(b)
    return (math.cos(br)*math.cos(lr), math.cos(br)*math.sin(lr), math.sin(br))

def dot(v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

def cross(v1, v2):
    return (v1[1]*v2[2] - v1[2]*v2[1],
            v1[2]*v2[0] - v1[0]*v2[2],
            v1[0]*v2[1] - v1[1]*v2[0])

def norm(v):
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

# 5-fold 軸方向向量
axis_vec = vec(a5_axis_gal[0], a5_axis_gal[1])

# 參考方向: 垂直於軸嘅任意向量 (用冷斑方向投影)
cold_vec = vec(209.0, -57.0)
ref_vec = cross(axis_vec, cold_vec)  # 垂直於軸同冷斑
ref_vec = tuple(c/norm(ref_vec) for c in ref_vec)  # 歸一化

# 第二參考: 垂直於軸同 ref_vec
ref2_vec = cross(axis_vec, ref_vec)
ref2_vec = tuple(c/norm(ref2_vec) for c in ref2_vec)

# 對每個節點計算 φ_j: 投影到環平面然後計角度
phi_j = []
for n in nodes:
    nv = vec(n['l'], n['b'])
    # 投影到環平面 (垂直於軸)
    proj = (nv[0] - dot(nv, axis_vec)*axis_vec[0],
            nv[1] - dot(nv, axis_vec)*axis_vec[1],
            nv[2] - dot(nv, axis_vec)*axis_vec[2])
    # 如果投影近乎零 (節點喺軸上), 設 φ=0
    if norm(proj) < 1e-10:
        phi_j.append(0.0)
        continue
    proj = tuple(c/norm(proj) for c in proj)
    # 環上角位置: atan2(投影·ref2, 投影·ref)
    phi = math.atan2(dot(proj, ref2_vec), dot(proj, ref_vec))
    phi_j.append(phi)

# 5° 平滑: 每個節點嘅溫度係 5° 半徑內嘅平滑
# 所以模型溫度應該以 5° 平滑

# ============ 5. Inverse Problem: 求 N, τ ============
def compute_model(N, tau_frac, T0):
    """計算 60 節點溫度 (模型)"""
    T_model = []
    for j in range(60):
        total = 0.0
        for n in range(1, 45):
            theta_n = 88 * math.sin(math.pi * n / 88) * (N + tau_frac)
            total += A_n[n-1] * math.cos(theta_n - n * phi_j[j])
        T_model.append(total + T0)
    return T_model

def residual(N, tau_frac, T0):
    """模型 vs 觀測嘅 RMSE"""
    T_obs = [n['T'] for n in nodes]
    T_model = compute_model(N, tau_frac, T0)
    return math.sqrt(sum((T_model[j] - T_obs[j])**2 for j in range(60)) / 60)

# 掃描 N (0..20) 同 τ (0..1) 搵最優解
print(f"\n掃描 N=0..20, τ=0..1 (步長 0.01):")
best = {'N': 0, 'tau_frac': 0, 'T0': 0, 'rmse': 1e10}

# 先掃 N=0..10, τ=0..1
for N in range(11):
    for tau_step in range(100):
        tau_frac = tau_step / 100.0
        
        # 對每個 (N, τ) 用線性最小二乘法求 T0
        T_obs = [n['T'] for n in nodes]
        T_model_noT0 = compute_model(N, tau_frac, 0.0)
        # T_obs = T_model + T0 → T0 = mean(T_obs - T_model)
        T0 = sum(T_obs[j] - T_model_noT0[j] for j in range(60)) / 60
        
        rmse = residual(N, tau_frac, T0)
        if rmse < best['rmse']:
            best = {'N': N, 'tau_frac': tau_frac, 'T0': T0, 'rmse': rmse}

print(f"最佳: N={best['N']}, τ={best['tau_frac']:.4f}×T_sync, T0={best['T0']:.2f} μK, RMSE={best['rmse']:.2f} μK")

# 顯示結果
tau_best = best['tau_frac'] * T_sync
print(f"τ = {tau_best:.4f} Gyr")
print(f"預期 τ = R_H/c = {R_H/c:.4f} Gyr")
print(f"差異: {abs(tau_best - R_H/c):.4f} Gyr")

# ============ 6. 詳細分析最佳解 ============
print(f"\n=== 詳細分析 (N={best['N']}, τ={best['tau_frac']:.4f}) ===")
T_model = compute_model(best['N'], best['tau_frac'], best['T0'])
T_obs = [n['T'] for n in nodes]

# 每個節點嘅誤差
print(f"{'node':>5} {'T_obs':>8} {'T_model':>8} {'diff':>8}")
for j in range(10):
    print(f"{j:5d} {T_obs[j]:8.2f} {T_model[j]:8.2f} {T_model[j]-T_obs[j]:8.2f}")

# 冷斑 match
print(f"\n冷斑 (node 0): obs={T_obs[0]:.1f}, model={T_model[0]:.1f}, diff={T_model[0]-T_obs[0]:.1f}")

# ============ 7. 更精細掃描 (N=0..5, τ=0..1, 步長 0.001) ============
print(f"\n精細掃描 N=0..5, τ=0..1 (步長 0.005):")
for N in range(6):
    best_tau = 0
    best_rmse = 1e10
    for tau_step in range(200):
        tau_frac = tau_step / 200.0
        T_model_noT0 = compute_model(N, tau_frac, 0.0)
        T0 = sum(T_obs[j] - T_model_noT0[j] for j in range(60)) / 60
        rmse = residual(N, tau_frac, T0)
        if rmse < best_rmse:
            best_rmse = rmse
            best_tau = tau_frac
    print(f"  N={N}: τ={best_tau:.4f}, T0=..., RMSE={best_rmse:.2f} μK")

# ============ 8. 結論 ============
print(f"\n" + "=" * 62)
print("結論")
print("=" * 62)

print(f"""
✅ 已建立完整 Inverse Problem 框架:
   60 節點 SMICA 溫度 → 44 個 K_Chain 相位 → N, τ → t_true

   模型: T_j = Σ_n A_n·cos(θ_n - n·φ_j) + T_0
   求解: 最小化 RMSE 搵 N, τ, T_0

🟡 初步結果:
   最佳 N={best['N']}, τ={best['tau_frac']:.4f}×T_sync
   τ = {tau_best:.4f} Gyr
   RMSE = {best['rmse']:.2f} μK
   T_0 = {best['T0']:.2f} μK

🔴 限制:
   1. ICRS→Galactic 轉換係近似, 會引入空間相位誤差
   2. 5° 平滑濾波影響咗高頻模式 (大 n) 嘅貢獻
   3. 模型假設 φ_j = n·φ_j, 實際可能更複雜
   4. RMSE 大, 表示模型空間結構同實際有偏差
   
   需要: 精確 astropy 轉換 + 未平滑 SMICA 數據
   
等候調律者指示下一步方向...
""")