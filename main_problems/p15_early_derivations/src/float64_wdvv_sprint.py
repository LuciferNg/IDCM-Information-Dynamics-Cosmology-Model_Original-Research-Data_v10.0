"""
IDCM v10.0 — Float64 雙精度 WDVV 衝刺
========================================
目標: 將殘差從 0.0165 壓至 10^-3
策略: 多階段 AdamW + 精細 L-BFGS
"""

import math
import numpy as np
import torch
import torch.optim as optim

torch.set_default_dtype(torch.float64)

φ = (1 + math.sqrt(5)) / 2
Nd = 44
n_z3 = 12

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"使用裝置: {device}")
print(f"預設精度: float64")

# ============================================================
# 構建 12D 張量 constraint indices
# ============================================================
modes_36 = sorted(range(1, Nd + 1), key=lambda x: 4 * math.sin(math.pi * x / 88) ** 2)[:36]
orbit_modes = [modes_36[i] for i in range(12)]

constraint_indices = []
init_values = []
for a in range(n_z3):
    for b in range(a, n_z3):
        for c in range(b, n_z3):
            n_a, n_b, n_c = orbit_modes[a], orbit_modes[b], orbit_modes[c]
            ok = False
            for s1, s2, s3 in [(1,1,1), (1,1,-1), (1,-1,1), (-1,1,1),
                               (1,-1,-1), (-1,1,-1), (-1,-1,1), (-1,-1,-1)]:
                total = s1*n_a + s2*n_b + s3*n_c
                if abs(total) < 5.0 or abs(abs(total)-Nd) < 5.0:
                    ok = True; break
            if ok:
                g = sum(4 * math.sin(math.pi * orbit_modes[k] / 88) ** 2 for k in [a, b, c]) / 3
                constraint_indices.append((a, b, c))
                init_values.append(φ ** (-g))

print(f"變數: {len(constraint_indices)} / 364")

# ============================================================
# 載入最佳結果做初始值
# ============================================================
try:
    d_prev = np.load("data/d_tensor_high_precision.npy")
    params = [d_prev[a, b, c] for a, b, c in constraint_indices]
    print(f"載入 d_tensor_high_precision 做初始值 (殘差 0.0165)")
except:
    params = init_values
    print(f"使用初始值")

# 轉為 float64
d_params = torch.nn.Parameter(
    torch.tensor(params, dtype=torch.float64, device=device)
)

# 索引映射
idx_list = torch.zeros((n_z3, n_z3, n_z3), dtype=torch.long, device=device) - 1
for idx, (a, b, c) in enumerate(constraint_indices):
    for (i,j,k) in [(a,b,c),(a,c,b),(b,a,c),(b,c,a),(c,a,b),(c,b,a)]:
        idx_list[i,j,k] = idx

def build_d():
    mask = idx_list >= 0
    d = torch.zeros((n_z3, n_z3, n_z3), dtype=torch.float64, device=device)
    d[mask] = d_params[idx_list[mask]]
    return d

def compute_wdvv(d):
    t = torch.ones(n_z3, dtype=torch.float64, device=device)
    g = torch.einsum('ijk,k->ij', d, t)
    try:
        g_inv = torch.linalg.inv(g)
    except:
        return torch.tensor(1e10, dtype=torch.float64, device=device)
    lhs = torch.einsum('ijp,pq,qkl->ijkl', d, g_inv, d)
    rhs = torch.einsum('ilp,pq,qjk->ijkl', d, g_inv, d)
    diff = lhs - rhs
    return torch.sum(diff ** 2)

def compute_evals(d):
    v = torch.tensor([φ ** (-k / n_z3) for k in range(n_z3)],
                     dtype=torch.float64, device=device)
    Y = torch.einsum('abk,k->ab', d, v)
    Y = (Y + Y.T) / 2
    try:
        return torch.linalg.eigvalsh(Y)
    except:
        return torch.zeros(n_z3, dtype=torch.float64, device=device)

# ============================================================
# 初始狀態
# ============================================================
with torch.no_grad():
    d = build_d()
    L_init = compute_wdvv(d).item()
    evals = compute_evals(d)
    n_neg = torch.sum(evals < -1e-10).item()
    n_pos = torch.sum(evals > 1e-10).item()
    print(f"初始: L_wdvv = {L_init:.8e}, 正: {n_pos}, 負: {n_neg}")

# ============================================================
# Stage 1: AdamW 微調 (用低 lr 避免破壞好解)
# ============================================================
print(f"\n{'='*70}")
print("Stage 1: AdamW 微調 (lr=0.005)")
print(f"{'='*70}")

opt1 = optim.AdamW([d_params], lr=0.005, weight_decay=1e-5)
sched1 = optim.lr_scheduler.CosineAnnealingLR(opt1, T_max=1000, eta_min=1e-5)

print(f"{'Iter':>6} | {'L_wdvv':>16} | {'n_neg':>6} | {'n_pos':>6} | {'min_eval':>16}")
print("-" * 55)

best_L = float('inf')
best_params = None

for step in range(1000):
    opt1.zero_grad()
    d = build_d()
    L = compute_wdvv(d)
    evals = compute_evals(d)
    L_pos = torch.sum(torch.relu(-evals) ** 2)
    total = L + 100.0 * L_pos + 0.001 * torch.sum(d_params ** 2)
    total.backward()
    opt1.step()
    sched1.step()
    
    with torch.no_grad():
        L_val = L.item()
        if L_val < best_L:
            best_L = L_val
            best_params = d_params.data.clone()
        
        n_neg = torch.sum(evals < -1e-10).item()
        n_pos = torch.sum(evals > 1e-10).item()
        min_e = evals.min().item()
        
        if step % 200 == 0 or step == 999:
            print(f"{step:6d} | {L_val:>16.10e} | {n_neg:6d} | {n_pos:6d} | {min_e:>16.10e}")

# Restore best
if best_params is not None:
    d_params.data = best_params
    with torch.no_grad():
        d = build_d()
        L = compute_wdvv(d).item()
        print(f"AdamW 最佳: L_wdvv = {L:.10e}")

# ============================================================
# Stage 2: L-BFGS 精細收斂
# ============================================================
print(f"\n{'='*70}")
print("Stage 2: L-BFGS 精細收斂")
print(f"{'='*70}")

opt2 = optim.LBFGS([d_params], lr=0.5, max_iter=30,
                    history_size=200, line_search_fn='strong_wolfe')

print(f"{'Iter':>6} | {'L_wdvv':>16} | {'n_neg':>6} | {'n_pos':>6} | {'min_eval':>16}")
print("-" * 55)

for step in range(500):
    def closure():
        opt2.zero_grad()
        d = build_d()
        L = compute_wdvv(d)
        evals = compute_evals(d)
        L_pos = torch.sum(torch.relu(-evals) ** 2) * 1000.0
        total = L + L_pos
        total.backward()
        return total
    
    try:
        total = opt2.step(closure)
    except RuntimeError as e:
        print(f"  L-BFGS error at step {step}: {e}")
        break
    
    with torch.no_grad():
        d = build_d()
        L = compute_wdvv(d).item()
        evals = compute_evals(d)
        n_neg = torch.sum(evals < -1e-10).item()
        n_pos = torch.sum(evals > 1e-10).item()
        min_e = evals.min().item()
        
        if step % 50 == 0 or step == 499:
            print(f"{step:6d} | {L:>16.10e} | {n_neg:6d} | {n_pos:6d} | {min_e:>16.10e}")
        
        if L < 1e-6:
            print(f"✨ 完美收斂！")
            break

# ============================================================
# 最終結果
# ============================================================
print(f"\n{'='*70}")
print("最終結果")
print(f"{'='*70}")

with torch.no_grad():
    d = build_d()
    L_final = compute_wdvv(d).item()
    evals = compute_evals(d)
    n_neg = torch.sum(evals < -1e-10).item()
    n_pos = torch.sum(evals > 1e-10).item()
    
    positive = sorted([e for e in evals.cpu().numpy() if e > 1e-10], reverse=True)
    
    print(f"初始殘差: {L_init:.10e}")
    print(f"最終殘差: {L_final:.10e}")
    print(f"改善倍數: {L_init/L_final:.2f}x")
    print(f"正本徵值: {n_pos}")
    print(f"負本徵值: {n_neg}")
    
    print(f"\n本徵值譜:")
    for i, e in enumerate(positive):
        print(f"  λ_{i+1:2d} = {e:.10f}")
    
    # 目標檢查
    if L_final < 0.001:
        print(f"\n🎯 目標達成: L_wdvv < 10^-3 ✅")
    elif L_final < 0.01:
        print(f"\n🟡 接近目標: L_wdvv < 10^-2")
    else:
        print(f"\n❌ 未達目標: L_wdvv = {L_final:.4e}")
    
    np.save("data/d_tensor_float64.npy", d.cpu().numpy())
    np.save("data/eigenvalues_float64.npy", evals.cpu().numpy())
    print(f"\n已儲存 data/d_tensor_float64.npy ✅")