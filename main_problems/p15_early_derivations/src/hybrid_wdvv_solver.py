"""
IDCM v10.0 — 混合優化 WDVV 求解器
===================================
Stage 1: AdamW + Cosine Annealing (逃離鞍點)
Stage 2: L-BFGS 雙精度 (收斂到 10^-10)
"""

import math
import numpy as np
import torch
import torch.optim as optim

φ = (1 + math.sqrt(5)) / 2
φ_inv = 1 / φ
Nd = 44
n_z3 = 12

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"使用裝置: {device}")

# ============================================================
# 原生 12D 張量建立
# ============================================================
def build_native_12d():
    modes_36 = sorted(range(1, Nd + 1), key=lambda x: 4 * math.sin(math.pi * x / 88) ** 2)[:36]
    orbit_modes = [modes_36[i] for i in range(12)]
    
    d = np.zeros((n_z3, n_z3, n_z3))
    for a in range(n_z3):
        for b in range(n_z3):
            for c in range(n_z3):
                g = sum(4 * math.sin(math.pi * orbit_modes[k] / 88) ** 2 for k in [a, b, c]) / 3
                d[a, b, c] = φ ** (-g)
    
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
                    if abs(total) < 5.0 or abs(abs(total)-Nd) < 5.0 or abs(abs(total)-2*Nd) < 5.0:
                        ok = True
                        break
                if ok:
                    g = sum(4 * math.sin(math.pi * orbit_modes[k] / 88) ** 2 for k in [a, b, c]) / 3
                    constraint_indices.append((a, b, c))
                    init_values.append(φ ** (-g))
    
    return d, constraint_indices, np.array(init_values), orbit_modes


# ============================================================
# 混合優化 WDVV 求解器
# ============================================================
class HybridWDVVSolver:
    """
    Stage 1: AdamW + Cosine Annealing (鞍點逃逸)
    Stage 2: L-BFGS 雙精度 (極限收斂)
    """
    
    def __init__(self, constraint_indices, init_values):
        self.constraint_indices = constraint_indices
        self.n = n_z3
        self.n_vars = len(constraint_indices)
        
        # 初始用 float32 加速 AdamW
        self.d_params = torch.nn.Parameter(
            torch.tensor(init_values, dtype=torch.float32, device=device)
        )
        
        # 索引映射
        self.idx_list = torch.zeros((self.n, self.n, self.n), dtype=torch.long, device=device) - 1
        for idx, (a, b, c) in enumerate(constraint_indices):
            self.idx_list[a, b, c] = idx
            self.idx_list[a, c, b] = idx
            self.idx_list[b, a, c] = idx
            self.idx_list[b, c, a] = idx
            self.idx_list[c, a, b] = idx
            self.idx_list[c, b, a] = idx
        
        self.history = []
        print(f"  變數: {self.n_vars}")
    
    def build_d_tensor(self) -> torch.Tensor:
        mask = self.idx_list >= 0
        d = torch.zeros((self.n, self.n, self.n), dtype=self.d_params.dtype, device=device)
        d[mask] = self.d_params[self.idx_list[mask]]
        return d
    
    def compute_wdvv_loss(self, d: torch.Tensor) -> torch.Tensor:
        t = torch.ones(self.n, dtype=d.dtype, device=device)
        g = torch.einsum('ijk,k->ij', d, t)
        try:
            g_inv = torch.linalg.inv(g)
        except:
            return torch.tensor(1e10, dtype=d.dtype, device=device)
        lhs = torch.einsum('ijp,pq,qkl->ijkl', d, g_inv, d)
        rhs = torch.einsum('ilp,pq,qjk->ijkl', d, g_inv, d)
        return torch.sum((lhs - rhs) ** 2)
    
    def compute_evals(self, d: torch.Tensor) -> torch.Tensor:
        v = torch.tensor([φ ** (-k / self.n) for k in range(self.n)],
                         dtype=d.dtype, device=device)
        Y = torch.einsum('abk,k->ab', d, v)
        Y = (Y + Y.T) / 2
        try:
            return torch.linalg.eigvalsh(Y)
        except:
            return torch.zeros(self.n, dtype=d.dtype, device=device)
    
    def compute_loss(self, d, lambda_wdvv=1.0, lambda_pos=100.0, lambda_reg=0.001):
        L_wdvv = self.compute_wdvv_loss(d)
        evals = self.compute_evals(d)
        L_pos = torch.sum(torch.relu(-evals) ** 2)
        L_reg = torch.sum(self.d_params ** 2)
        return lambda_wdvv * L_wdvv + lambda_pos * L_pos + lambda_reg * L_reg, L_wdvv, L_pos, L_reg
    
    def stage1_adamw(self, n_iter=1000, lr=1e-2):
        """Stage 1: AdamW + Cosine Annealing"""
        print(f"\n{'='*50}")
        print(f"Stage 1: AdamW + Cosine Annealing ({n_iter} iter)")
        print(f"{'='*50}")
        
        optimizer = optim.AdamW([self.d_params], lr=lr, weight_decay=1e-4)
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_iter, eta_min=1e-5)
        
        print(f"{'Iter':>6} | {'L_wdvv':>12} | {'L_pos':>12} | {'L_total':>12} | {'n_neg':>6} | {'n_pos':>6} | {'lr':>10}")
        print("-" * 70)
        
        for step in range(n_iter):
            optimizer.zero_grad()
            d = self.build_d_tensor()
            total, L_wdvv, L_pos, L_reg = self.compute_loss(d)
            total.backward()
            optimizer.step()
            scheduler.step()
            
            with torch.no_grad():
                d = self.build_d_tensor()
                evals = self.compute_evals(d)
                n_neg = torch.sum(evals < -1e-10).item()
                n_pos = torch.sum(evals > 1e-10).item()
                current_lr = scheduler.get_last_lr()[0]
                
                if step % 100 == 0 or step == n_iter - 1:
                    print(f"{step:6d} | {L_wdvv.item():>12.6e} | {L_pos.item():>12.6e} | "
                          f"{total.item():>12.6e} | {n_neg:6d} | {n_pos:6d} | {current_lr:>10.2e}")
                
                self.history.append({
                    "step": step, "phase": 1,
                    "L_wdvv": L_wdvv.item(), "L_pos": L_pos.item(),
                    "n_neg": n_neg, "n_pos": n_pos,
                    "evals": evals.detach().cpu().numpy().copy()
                })
                
                # 提早退出
                if L_wdvv.item() < 0.01 and n_neg == 0:
                    print(f"✅ AdamW 突破成功！殘差 {L_wdvv.item():.5f}")
                    break
        
        return self.history
    
    def stage2_lbfgs(self, n_iter=200, lr=1.0):
        """Stage 2: L-BFGS 雙精度極限收斂"""
        print(f"\n{'='*50}")
        print(f"Stage 2: L-BFGS 雙精度收斂 ({n_iter} iter)")
        print(f"{'='*50}")
        
        # 切換到雙精度
        self.d_params.data = self.d_params.data.to(torch.float64)
        
        optimizer = optim.LBFGS([self.d_params], lr=lr, max_iter=20,
                                history_size=100, line_search_fn='strong_wolfe')
        
        print(f"{'Iter':>6} | {'L_wdvv':>12} | {'L_pos':>12} | {'L_total':>12} | {'n_neg':>6} | {'n_pos':>6}")
        print("-" * 65)
        
        for step in range(n_iter):
            def closure():
                optimizer.zero_grad()
                d = self.build_d_tensor()
                total, _, _, _ = self.compute_loss(d, lambda_wdvv=1.0, lambda_pos=1000.0, lambda_reg=0.001)
                total.backward()
                return total
            
            try:
                total = optimizer.step(closure)
            except:
                break
            
            with torch.no_grad():
                d = self.build_d_tensor()
                _, L_wdvv, L_pos, L_reg = self.compute_loss(d, lambda_wdvv=1.0, lambda_pos=1000.0, lambda_reg=0.001)
                evals = self.compute_evals(d)
                n_neg = torch.sum(evals < -1e-10).item()
                n_pos = torch.sum(evals > 1e-10).item()
                
                if step % 20 == 0 or step == n_iter - 1:
                    print(f"{step:6d} | {L_wdvv.item():>12.6e} | {L_pos.item():>12.6e} | "
                          f"{total.item():>12.6e} | {n_neg:6d} | {n_pos:6d}")
                
                self.history.append({
                    "step": step + 1000, "phase": 2,
                    "L_wdvv": L_wdvv.item(), "L_pos": L_pos.item(),
                    "n_neg": n_neg, "n_pos": n_pos,
                    "evals": evals.detach().cpu().numpy().copy()
                })
                
                if L_wdvv.item() < 1e-10:
                    print(f"✨ WDVV 殘差降至 10^-10！共振開眼完成！")
                    break
        
        return self.history
    
    def finalize(self):
        """輸出最終結果"""
        print("\n" + "=" * 70)
        print("混合優化最終結果")
        print("=" * 70)
        
        with torch.no_grad():
            d = self.build_d_tensor()
            evals = self.compute_evals(d)
            L_wdvv = self.compute_wdvv_loss(d)
            n_neg = torch.sum(evals < -1e-10).item()
            n_pos = torch.sum(evals > 1e-10).item()
            
            positive = evals[evals > 1e-10]
            sorted_evals, _ = torch.sort(positive, descending=True)
            
            print(f"WDVV 殘差: {L_wdvv.item():.10e}")
            print(f"正本徵值: {n_pos}")
            print(f"負本徵值: {n_neg}")
            print(f"最終譜:")
            for i, e in enumerate(evals.cpu().numpy()):
                marker = " ✅" if e > 1e-10 else (" ❌" if e < -1e-10 else " ~0")
                print(f"  λ_{i+1:2d} = {e:.10e}{marker}")
            
            if n_pos > 0:
                print(f"\n正本徵值排序:")
                for i in range(min(12, len(sorted_evals))):
                    print(f"  λ_{i+1:2d} = {sorted_evals[i].item():.10e}")
            
            return {
                "d_tensor": d.cpu().numpy(),
                "eigenvalues": evals.cpu().numpy(),
                "n_pos": n_pos, "n_neg": n_neg,
                "L_wdvv": L_wdvv.item(),
                "history": self.history,
            }


if __name__ == "__main__":
    print("=" * 70)
    print("IDCM v10.0 — 混合優化 WDVV 求解器")
    print("=" * 70)
    
    print("\n[1/4] 構建原生 12D 張量...")
    d_init, constraint_indices, init_values, orbit_modes = build_native_12d()
    print(f"  張量: 12×12×12, 分量: {len(constraint_indices)}/364")
    print(f"  初始值: {init_values.min():.4f} ~ {init_values.max():.4f}")
    
    print("\n[2/4] 初始化求解器...")
    solver = HybridWDVVSolver(constraint_indices, init_values)
    
    with torch.no_grad():
        d = solver.build_d_tensor()
        evals = solver.compute_evals(d)
        print(f"  初始: {torch.sum(evals < -1e-10).item()} 負, "
              f"{torch.sum(evals > 1e-10).item()} 正")
    
    print("\n[3/4] 執行混合優化...")
    solver.stage1_adamw(n_iter=1000, lr=1e-2)
    solver.stage2_lbfgs(n_iter=200, lr=1.0)
    
    print("\n[4/4] 最終結果")
    result = solver.finalize()
    
    np.save("data/d_tensor_hybrid.npy", result["d_tensor"])
    np.save("data/eigenvalues_hybrid.npy", result["eigenvalues"])
    print("\n已儲存 data/d_tensor_hybrid.npy ✅")
    
    print("\n" + "=" * 70)
    print("混合優化完成")
    print("=" * 70)