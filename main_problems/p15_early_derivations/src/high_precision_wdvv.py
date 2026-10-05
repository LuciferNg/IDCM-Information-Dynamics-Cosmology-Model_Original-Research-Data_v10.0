"""
IDCM v10.0 — 高精度 WDVV 求解器 (目標殘差 < 10^-3)
====================================================
多階段優化: AdamW → AdamW (高 lr) → L-BFGS
"""

import math
import numpy as np
import torch
import torch.optim as optim

φ = (1 + math.sqrt(5)) / 2
Nd = 44
n_z3 = 12

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"使用裝置: {device}")

# ============================================================
# 構建 12D 張量 (同之前)
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
# 高精度求解器
# ============================================================
class HighPrecisionSolver:
    def __init__(self):
        self.n = n_z3
        self.n_vars = len(constraint_indices)
        
        # 載入之前嘅結果做初始值
        try:
            d_prev = np.load("data/d_tensor_hybrid.npy")
            params = []
            for a, b, c in constraint_indices:
                params.append(d_prev[a, b, c])
            print(f"載入之前結果: {len(params)} params")
        except:
            params = init_values
            print(f"使用初始值: {len(params)} params")
        
        self.d_params = torch.nn.Parameter(
            torch.tensor(params, dtype=torch.float64, device=device)
        )
        
        self.idx_list = torch.zeros((self.n, self.n, self.n), dtype=torch.long, device=device) - 1
        for idx, (a, b, c) in enumerate(constraint_indices):
            self.idx_list[a, b, c] = idx
            self.idx_list[a, c, b] = idx
            self.idx_list[b, a, c] = idx
            self.idx_list[b, c, a] = idx
            self.idx_list[c, a, b] = idx
            self.idx_list[c, b, a] = idx
    
    def build_d(self):
        mask = self.idx_list >= 0
        d = torch.zeros((self.n, self.n, self.n), dtype=torch.float64, device=device)
        d[mask] = self.d_params[self.idx_list[mask]]
        return d
    
    def compute_wdvv(self, d):
        t = torch.ones(self.n, dtype=torch.float64, device=device)
        g = torch.einsum('ijk,k->ij', d, t)
        try:
            g_inv = torch.linalg.inv(g)
        except:
            return torch.tensor(1e10, dtype=torch.float64, device=device)
        lhs = torch.einsum('ijp,pq,qkl->ijkl', d, g_inv, d)
        rhs = torch.einsum('ilp,pq,qjk->ijkl', d, g_inv, d)
        diff = lhs - rhs
        # L2 norm of all elements
        return torch.sum(diff ** 2)
    
    def compute_evals(self, d):
        v = torch.tensor([φ ** (-k / self.n) for k in range(self.n)],
                         dtype=torch.float64, device=device)
        Y = torch.einsum('abk,k->ab', d, v)
        Y = (Y + Y.T) / 2
        try:
            return torch.linalg.eigvalsh(Y)
        except:
            return torch.zeros(self.n, dtype=torch.float64, device=device)
    
    def compute_loss(self, d, lam_wdvv=1.0, lam_pos=100.0, lam_reg=0.001):
        L_wdvv = self.compute_wdvv(d)
        evals = self.compute_evals(d)
        L_pos = torch.sum(torch.relu(-evals) ** 2)
        L_reg = torch.sum(self.d_params ** 2)
        return lam_wdvv * L_wdvv + lam_pos * L_pos + lam_reg * L_reg, L_wdvv, L_pos
    
    def stage_adamw(self, n_iter, lr, lam_pos=100.0, label=""):
        """AdamW 階段"""
        opt = optim.AdamW([self.d_params], lr=lr, weight_decay=1e-4)
        scheduler = optim.lr_scheduler.CosineAnnealingLR(opt, T_max=n_iter, eta_min=lr/100)
        
        print(f"\n--- {label}: AdamW lr={lr}, {n_iter} iter ---")
        print(f"{'Iter':>6} | {'L_wdvv':>14} | {'L_pos':>14} | {'n_neg':>6} | {'n_pos':>6} | {'min_eval':>14}")
        print("-" * 70)
        
        best_loss = float('inf')
        best_params = None
        
        for step in range(n_iter):
            opt.zero_grad()
            d = self.build_d()
            total, L_wdvv, L_pos = self.compute_loss(d, lam_wdvv=1.0, lam_pos=lam_pos)
            total.backward()
            opt.step()
            scheduler.step()
            
            with torch.no_grad():
                evals = self.compute_evals(d)
                n_neg = torch.sum(evals < -1e-10).item()
                n_pos = torch.sum(evals > 1e-10).item()
                min_e = evals.min().item()
                L_wdvv_val = L_wdvv.item()
                
                if L_wdvv_val < best_loss:
                    best_loss = L_wdvv_val
                    best_params = self.d_params.data.clone()
                
                if step % 100 == 0 or step == n_iter - 1:
                    print(f"{step:6d} | {L_wdvv_val:>14.8e} | {L_pos.item():>14.8e} | {n_neg:6d} | {n_pos:6d} | {min_e:>14.8e}")
        
        # Restore best
        if best_params is not None:
            self.d_params.data = best_params
            with torch.no_grad():
                d = self.build_d()
                L = self.compute_wdvv(d).item()
                print(f"  最佳 WDVV: {L:.8e}")
        
        return best_loss
    
    def stage_lbfgs(self, n_iter, lr=1.0, lam_pos=1000.0):
        """L-BFGS 精細收斂"""
        # 確保雙精度
        self.d_params.data = self.d_params.data.to(torch.float64)
        
        opt = optim.LBFGS([self.d_params], lr=lr, max_iter=20,
                          history_size=100, line_search_fn='strong_wolfe')
        
        print(f"\n--- L-BFGS 精細收斂, {n_iter} iter ---")
        print(f"{'Iter':>6} | {'L_wdvv':>14} | {'L_pos':>14} | {'n_neg':>6} | {'n_pos':>6} | {'min_eval':>14}")
        print("-" * 70)
        
        for step in range(n_iter):
            def closure():
                opt.zero_grad()
                d = self.build_d()
                total, _, _ = self.compute_loss(d, lam_wdvv=1.0, lam_pos=lam_pos)
                total.backward()
                return total
            
            try:
                total = opt.step(closure)
            except:
                break
            
            with torch.no_grad():
                d = self.build_d()
                L_wdvv = self.compute_wdvv(d).item()
                evals = self.compute_evals(d)
                n_neg = torch.sum(evals < -1e-10).item()
                n_pos = torch.sum(evals > 1e-10).item()
                min_e = evals.min().item()
                
                if step % 20 == 0 or step == n_iter - 1:
                    print(f"{step:6d} | {L_wdvv:>14.8e} | {0:>14.8e} | {n_neg:6d} | {n_pos:6d} | {min_e:>14.8e}")
                
                if L_wdvv < 1e-6:
                    print(f"✨ 收斂成功！")
                    break
    
    def finalize(self):
        with torch.no_grad():
            d = self.build_d()
            L = self.compute_wdvv(d).item()
            evals = self.compute_evals(d)
            n_neg = torch.sum(evals < -1e-10).item()
            n_pos = torch.sum(evals > 1e-10).item()
            
            print(f"\n{'='*70}")
            print(f"最終結果")
            print(f"{'='*70}")
            print(f"WDVV 殘差: {L:.10e}")
            print(f"正: {n_pos}, 負: {n_neg}")
            
            positive = sorted([e for e in evals.cpu().numpy() if e > 1e-10], reverse=True)
            print(f"正本徵值 ({len(positive)}):")
            for i, e in enumerate(positive):
                print(f"  λ_{i+1:2d} = {e:.10e}")
            
            np.save("data/d_tensor_high_precision.npy", d.cpu().numpy())
            np.save("data/eigenvalues_high_precision.npy", evals.cpu().numpy())
            print(f"已儲存 data/d_tensor_high_precision.npy ✅")
            
            return {"L_wdvv": L, "n_pos": n_pos, "n_neg": n_neg, "evals": positive}


if __name__ == "__main__":
    print("=" * 70)
    print("IDCM v10.0 — 高精度 WDVV 求解")
    print("=" * 70)
    
    solver = HighPrecisionSolver()
    
    # Stage 1: AdamW 低 lr 穩定
    solver.stage_adamw(n_iter=500, lr=1e-2, lam_pos=100.0, label="Stage 1: AdamW 穩定")
    
    # Stage 2: AdamW 高 lr 逃離鞍點
    solver.stage_adamw(n_iter=500, lr=5e-2, lam_pos=500.0, label="Stage 2: AdamW 高 lr")
    
    # Stage 3: L-BFGS 精細收斂
    solver.stage_lbfgs(n_iter=300, lr=1.0, lam_pos=1000.0)
    
    # Final
    result = solver.finalize()
    
    print(f"\n{'='*70}")
    print(f"🎯 完成: WDVV 殘差 {result['L_wdvv']:.6e}")
    print(f"{'='*70}")