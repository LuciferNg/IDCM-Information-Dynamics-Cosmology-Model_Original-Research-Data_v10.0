"""
IDCM v10.0 — WDVV 求解第二階段 (高 λ_pos)
"""
import math
import numpy as np
import torch
import torch.optim as optim
from derive_dijk_wdvv_solver import build_constraint_indices, WDVVSolver

φ = (1 + math.sqrt(5)) / 2
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

constraint_indices, all_indices, init_values, modes = build_constraint_indices()
print(f"C1 約束後: {len(constraint_indices)} / {len(all_indices)}")

# 載入之前嘅解
solver = WDVVSolver(constraint_indices, all_indices, init_values, modes)
try:
    prev_d = np.load("data/d_tensor_solved.npy")
    with torch.no_grad():
        for idx, (i, j, k) in enumerate(constraint_indices):
            solver.d_params[idx] = torch.tensor(prev_d[i, j, k], dtype=torch.float64, device=device)
    print("載入之前嘅解 ✅")
except:
    print("用初始值重新開始")

# 第二階段: 高 λ_pos
print("\n=== 第二階段: λ_pos=500 ===")
optimizer = optim.LBFGS([solver.d_params], lr=2.0, max_iter=20,
                        history_size=50, line_search_fn='strong_wolfe')

for step in range(300):
    def closure():
        optimizer.zero_grad()
        d = solver.build_d_tensor()
        total, _, _, _ = solver.compute_loss(d, lambda_wdvv=1.0, lambda_pos=500.0, lambda_reg=0.001)
        total.backward()
        return total
    
    try:
        total = optimizer.step(closure)
    except:
        break
    
    with torch.no_grad():
        d = solver.build_d_tensor()
        _, L_wdvv, L_pos, L_reg = solver.compute_loss(d, lambda_wdvv=1.0, lambda_pos=500.0, lambda_reg=0.001)
        evals = solver.compute_yukawa_eigenvalues(d)
        n_neg = torch.sum(evals < -1e-10).item()
        n_pos = torch.sum(evals > 1e-10).item()
        if step % 50 == 0:
            print(f"iter {step:3d}: L_wdvv={L_wdvv.item():.4e}, L_pos={L_pos.item():.4e}, n_neg={n_neg}, n_pos={n_pos}")

# 第三階段: 更高 λ_pos
print("\n=== 第三階段: λ_pos=5000 ===")
optimizer = optim.LBFGS([solver.d_params], lr=1.0, max_iter=20,
                        history_size=50, line_search_fn='strong_wolfe')

for step in range(300):
    def closure():
        optimizer.zero_grad()
        d = solver.build_d_tensor()
        total, _, _, _ = solver.compute_loss(d, lambda_wdvv=1.0, lambda_pos=5000.0, lambda_reg=0.001)
        total.backward()
        return total
    
    try:
        total = optimizer.step(closure)
    except:
        break
    
    with torch.no_grad():
        d = solver.build_d_tensor()
        _, L_wdvv, L_pos, L_reg = solver.compute_loss(d, lambda_wdvv=1.0, lambda_pos=5000.0, lambda_reg=0.001)
        evals = solver.compute_yukawa_eigenvalues(d)
        n_neg = torch.sum(evals < -1e-10).item()
        n_pos = torch.sum(evals > 1e-10).item()
        if step % 50 == 0:
            print(f"iter {step:3d}: L_wdvv={L_wdvv.item():.4e}, L_pos={L_pos.item():.4e}, n_neg={n_neg}, n_pos={n_pos}")

# 最終結果
print("\n=== 最終結果 ===")
with torch.no_grad():
    d = solver.build_d_tensor()
    evals = solver.compute_yukawa_eigenvalues(d)
    positive = evals[evals > 1e-10]
    sorted_evals, _ = torch.sort(positive, descending=True)
    n_neg = torch.sum(evals < -1e-10).item()
    
    print(f"正本徵值: {len(sorted_evals)}")
    print(f"負本徵值: {n_neg}")
    print(f"WDVV 殘差: {solver.compute_wdvv_loss(d).item():.4e}")
    if len(sorted_evals) > 0:
        print(f"範圍: {sorted_evals[-1].item():.6e} ~ {sorted_evals[0].item():.6e}")
        print("\nTop 21 本徵值:")
        for i in range(min(21, len(sorted_evals))):
            print(f"  λ_{i+1:2d} = {sorted_evals[i].item():.6e}")

np.save("data/d_tensor_solved_v2.npy", d.cpu().numpy())
np.save("data/eigenvalues_solved_v2.npy", sorted_evals.cpu().numpy())
print("\n已儲存 ✅")