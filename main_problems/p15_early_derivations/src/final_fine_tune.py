"""
IDCM v10.0 — 最後微雕 + 結果整理
===================================
目標: 消滅最後 1 個幽靈，記錄最終質量譜
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

# 載入之前嘅結果
d_loaded = np.load("data/d_tensor_hybrid.npy")
evals_loaded = np.load("data/eigenvalues_hybrid.npy")
print(f"載入: d_tensor {d_loaded.shape}, eigenvalues {len(evals_loaded)}")

# 重新建立 constraint indices
modes_36 = sorted(range(1, Nd + 1), key=lambda x: 4 * math.sin(math.pi * x / 88) ** 2)[:36]
orbit_modes = [modes_36[i] for i in range(12)]

constraint_indices = []
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
                constraint_indices.append((a, b, c))

# 建立 solver + 載入已優化嘅參數
class FineTuner:
    def __init__(self, constraint_indices, d_init):
        self.constraint_indices = constraint_indices
        self.n = n_z3
        self.n_vars = len(constraint_indices)
        
        # 從 d_tensor 提取參數
        init_params = []
        for idx, (a, b, c) in enumerate(constraint_indices):
            init_params.append(d_init[a, b, c])
        
        self.d_params = torch.nn.Parameter(
            torch.tensor(init_params, dtype=torch.float64, device=device)
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
        return torch.sum((lhs - rhs) ** 2)
    
    def compute_evals(self, d):
        v = torch.tensor([φ ** (-k / self.n) for k in range(self.n)],
                         dtype=torch.float64, device=device)
        Y = torch.einsum('abk,k->ab', d, v)
        Y = (Y + Y.T) / 2
        try:
            return torch.linalg.eigvalsh(Y)
        except:
            return torch.zeros(self.n, dtype=torch.float64, device=device)
    
    def compute_loss(self, d, lambda_wdvv=1.0, lambda_pos=2000.0, lambda_reg=0.001):
        L_wdvv = self.compute_wdvv(d)
        evals = self.compute_evals(d)
        # Targeted log-barrier: 只針對最後一個負值
        negative = evals[evals < -1e-10]
        if len(negative) > 0:
            L_pos = torch.sum(torch.exp(-1000.0 * negative))  # 指數障礙
        else:
            L_pos = torch.tensor(0.0, dtype=torch.float64, device=device)
        L_reg = torch.sum(self.d_params ** 2)
        return lambda_wdvv * L_wdvv + lambda_pos * L_pos + lambda_reg * L_reg, L_wdvv, L_pos, L_reg
    
    def fine_tune(self, n_iter=200):
        """雙精度 L-BFGS 微雕"""
        optimizer = optim.LBFGS([self.d_params], lr=1.0, max_iter=20,
                                history_size=100, line_search_fn='strong_wolfe')
        
        print(f"\n{'Iter':>6} | {'L_wdvv':>14} | {'L_pos':>14} | {'n_neg':>6} | {'n_pos':>6} | {'min_eval':>14}")
        print("-" * 70)
        
        for step in range(n_iter):
            def closure():
                optimizer.zero_grad()
                d = self.build_d()
                total, _, _, _ = self.compute_loss(d)
                total.backward()
                return total
            
            try:
                total = optimizer.step(closure)
            except:
                break
            
            with torch.no_grad():
                d = self.build_d()
                _, L_wdvv, L_pos, L_reg = self.compute_loss(d)
                evals = self.compute_evals(d)
                n_neg = torch.sum(evals < -1e-10).item()
                n_pos = torch.sum(evals > 1e-10).item()
                min_eval = evals.min().item()
                
                if step % 20 == 0:
                    print(f"{step:6d} | {L_wdvv.item():>14.8e} | {L_pos.item():>14.8e} | "
                          f"{n_neg:6d} | {n_pos:6d} | {min_eval:>14.8e}")
                
                if n_neg == 0 and L_wdvv.item() < 1e-6:
                    print(f"✨ 完美收斂！零幽靈態！")
                    break
        
        return self.finalize()
    
    def finalize(self):
        with torch.no_grad():
            d = self.build_d()
            evals = self.compute_evals(d)
            L_wdvv = self.compute_wdvv(d)
            n_neg = torch.sum(evals < -1e-10).item()
            n_pos = torch.sum(evals > 1e-10).item()
            
            positive = evals[evals > 1e-10]
            sorted_evals, _ = torch.sort(positive, descending=True)
            
            print("\n" + "=" * 70)
            print("微雕最終結果")
            print("=" * 70)
            print(f"WDVV 殘差: {L_wdvv.item():.10e}")
            print(f"正本徵值: {n_pos}")
            print(f"負本徵值: {n_neg}")
            print(f"最小本徵值: {evals.min().item():.10e}")
            print(f"最大本徵值: {evals.max().item():.10e}")
            print(f"動態範圍: {evals.max().item()/max(evals.min().item(), 1e-20):.0e}")
            
            print(f"\n最終本徵值譜:")
            for i, e in enumerate(evals.cpu().numpy()):
                marker = " ✅" if e > 1e-10 else (" ❌" if e < -1e-10 else " ~0")
                print(f"  λ_{i+1:2d} = {e:.10e}{marker}")
            
            # 儲存
            np.save("data/d_tensor_final.npy", d.cpu().numpy())
            np.save("data/eigenvalues_final.npy", evals.cpu().numpy())
            
            with open("data/final_spectrum.txt", "w") as f:
                f.write("IDCM v10.0 — 最終本徵值譜\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"WDVV 殘差: {L_wdvv.item():.10e}\n")
                f.write(f"正本徵值: {n_pos}, 負本徵值: {n_neg}\n\n")
                f.write("本徵值譜:\n")
                for i, e in enumerate(evals.cpu().numpy()):
                    f.write(f"  λ_{i+1:2d} = {e:.10e}\n")
            
            print(f"\n已儲存 data/d_tensor_final.npy ✅")
            print(f"已儲存 data/final_spectrum.txt ✅")
            
            return {
                "d_tensor": d.cpu().numpy(),
                "eigenvalues": evals.cpu().numpy(),
                "n_pos": n_pos, "n_neg": n_neg,
                "L_wdvv": L_wdvv.item(),
            }


if __name__ == "__main__":
    print("=" * 70)
    print("IDCM v10.0 — 最後微雕")
    print("=" * 70)
    
    tuner = FineTuner(constraint_indices, d_loaded)
    result = tuner.fine_tune(n_iter=200)
    
    # 最終總結
    print("\n" + "=" * 70)
    print("🎯 IDCM v10.0 完整管道完成")
    print("=" * 70)
    print("""
    44 K_Chain modes
        │
        ↓ 946 beat states
    P̂_{CY₃}: 134×946 projection operator
        │
        ↓ Z₃ orbifold (36 → 12)
    12D Kähler invariant subspace
        │
        ↓ Mixed optimizer (AdamW + L-BFGS)
    WDVV residual: {:.6e}
        │
        ↓ 12 topological eigenvalues
    {} positive, {} negative
        │
        ↓ × exp(-V_cycle) × M_Pl
    SM mass spectrum
    """.format(result["L_wdvv"], result["n_pos"], result["n_neg"]))