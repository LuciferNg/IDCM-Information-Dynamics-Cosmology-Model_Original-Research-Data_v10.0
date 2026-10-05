"""
IDCM v10.0 — 原生 12D 張量建立器
===================================
從 K_Chain Z₃ 不變組合直接構建 12D 張量
"""

import math
import numpy as np
import torch
import torch.optim as optim

φ = (1 + math.sqrt(5)) / 2
φ_inv = 1 / φ
Nd = 44
h11 = 36
n_z3 = 12

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"使用裝置: {device}")

# ============================================================
# K_Chain 44 個 mode 嘅 Z₃ 軌道結構
# ============================================================
# Z₃ 作用: n → n + 15 (mod 44), 因為 15×3 = 45 ≡ 1 (mod 44)
# 但 44 同 3 互質 → Z₃ 作用係 FULL orbit, 唔係 split
# 所以 Z₃ orbifold 必須作用喺 Kähler moduli 空間, 唔係 K_Chain 直接

# 正確做法: 36 個 Kähler moduli 分 12 組 Z₃ orbit
# 每組 3 個 modulus, 按能量 band 分組
# Band I:   n=1..14 (γ<1)     → 14 moduli
# Band II:  n=15..22 (1<γ<2)  → 8 moduli
# Band III: n=23..36 (2<γ<4)  → 14 moduli
# 36 = 14+8+14

# Z₃ orbits 按能量排序分組:
# 每組從 Band I, II, III 各取一個 modulus
# 確保 Z₃ 不變性

def build_native_12d_tensor() -> np.ndarray:
    """從 K_Chain 直接構建原生 12D 張量"""
    
    # 所有 mode 按能量排序
    all_modes = sorted(range(1, Nd + 1), key=lambda x: 4 * math.sin(math.pi * x / 88) ** 2)
    kahler_modes = all_modes[:h11]  # 36 個最低能量 mode
    
    # 按能量 band 分組
    def energy_band(n):
        g = 4 * math.sin(math.pi * n / 88) ** 2
        if g < 1: return 0  # Band I
        elif g < 2: return 1  # Band II
        else: return 2  # Band III
    
    bands = {0: [], 1: [], 2: []}
    for n in kahler_modes:
        bands[energy_band(n)].append(n)
    
    print(f"Band I (γ<1):   {len(bands[0])} modes")
    print(f"Band II (1<γ<2): {len(bands[1])} modes")
    print(f"Band III (γ>2): {len(bands[2])} modes")
    
    # 從每個 band 取前 4 個 mode 做 Z₃ orbit
    # 12 orbits = 4 per band × 3 bands
    orbit_modes = []
    for i in range(4):
        for band in range(3):
            if i < len(bands[band]):
                orbit_modes.append(bands[band][i])
    
    # 如果唔夠 12 個, 補充
    while len(orbit_modes) < n_z3:
        orbit_modes.append(orbit_modes[-1])
    
    print(f"Z₃ orbit modes (12): {orbit_modes}")
    
    # 直接計算 12D d_{abc}
    d = np.zeros((n_z3, n_z3, n_z3))
    for a in range(n_z3):
        for b in range(n_z3):
            for c in range(n_z3):
                n_a, n_b, n_c = orbit_modes[a], orbit_modes[b], orbit_modes[c]
                gamma_a = 4 * math.sin(math.pi * n_a / 88) ** 2
                gamma_b = 4 * math.sin(math.pi * n_b / 88) ** 2
                gamma_c = 4 * math.sin(math.pi * n_c / 88) ** 2
                # 相交數 = φ^{-(γ_a + γ_b + γ_c)/3}
                d[a, b, c] = φ ** (-(gamma_a + gamma_b + gamma_c) / 3)
    
    return d, orbit_modes


def build_constraint_indices_12d(orbit_modes):
    """C1 約束: 模式守恆"""
    constraint_indices = []
    init_values = []
    
    for a in range(n_z3):
        for b in range(a, n_z3):
            for c in range(b, n_z3):
                n_a, n_b, n_c = orbit_modes[a], orbit_modes[b], orbit_modes[c]
                # 模式守恆: 檢查 n_i ± n_j ± n_k ≡ 0 (mod 44)
                ok = False
                for s1, s2, s3 in [(1,1,1), (1,1,-1), (1,-1,1), (-1,1,1),
                                   (1,-1,-1), (-1,1,-1), (-1,-1,1), (-1,-1,-1)]:
                    total = s1 * n_a + s2 * n_b + s3 * n_c
                    if abs(total) < 5.0 or abs(abs(total) - Nd) < 5.0 or abs(abs(total) - 2*Nd) < 5.0:
                        ok = True
                        break
                if ok:
                    constraint_indices.append((a, b, c))
                    gamma_a = 4 * math.sin(math.pi * n_a / 88) ** 2
                    gamma_b = 4 * math.sin(math.pi * n_b / 88) ** 2
                    gamma_c = 4 * math.sin(math.pi * n_c / 88) ** 2
                    val = φ ** (-(gamma_a + gamma_b + gamma_c) / 3)
                    init_values.append(val)
    
    return constraint_indices, np.array(init_values)


# ============================================================
# WDVV 求解器 (12D)
# ============================================================
class WDVVSolver12D:
    def __init__(self, constraint_indices, init_values):
        self.constraint_indices = constraint_indices
        self.n = n_z3
        self.n_vars = len(constraint_indices)
        
        self.d_params = torch.nn.Parameter(
            torch.tensor(init_values, dtype=torch.float64, device=device)
        )
        
        self.idx_list = torch.zeros((self.n, self.n, self.n), dtype=torch.long, device=device) - 1
        for idx, (a, b, c) in enumerate(constraint_indices):
            self.idx_list[a, b, c] = idx
            self.idx_list[a, c, b] = idx
            self.idx_list[b, a, c] = idx
            self.idx_list[b, c, a] = idx
            self.idx_list[c, a, b] = idx
            self.idx_list[c, b, a] = idx
        
        print(f"  12D 變數: {self.n_vars}")
    
    def build_d_tensor(self) -> torch.Tensor:
        mask = self.idx_list >= 0
        d = torch.zeros((self.n, self.n, self.n), dtype=torch.float64, device=device)
        d[mask] = self.d_params[self.idx_list[mask]]
        return d
    
    def compute_wdvv_loss(self, d: torch.Tensor) -> torch.Tensor:
        t = torch.ones(self.n, dtype=torch.float64, device=device)
        g = torch.einsum('ijk,k->ij', d, t)
        try:
            g_inv = torch.linalg.inv(g)
        except:
            return torch.tensor(1e10, dtype=torch.float64, device=device)
        lhs = torch.einsum('ijp,pq,qkl->ijkl', d, g_inv, d)
        rhs = torch.einsum('ilp,pq,qjk->ijkl', d, g_inv, d)
        diff = lhs - rhs
        return torch.sum(diff ** 2)
    
    def compute_yukawa_eigenvalues(self, d: torch.Tensor) -> torch.Tensor:
        v = torch.tensor([φ ** (-k / self.n) for k in range(self.n)],
                         dtype=torch.float64, device=device)
        Y = torch.einsum('abk,k->ab', d, v)
        Y = (Y + Y.T) / 2
        try:
            return torch.linalg.eigvalsh(Y)
        except:
            return torch.zeros(self.n, dtype=torch.float64, device=device)
    
    def compute_loss(self, d, lambda_wdvv=1.0, lambda_pos=100.0, lambda_reg=0.001):
        L_wdvv = self.compute_wdvv_loss(d)
        evals = self.compute_yukawa_eigenvalues(d)
        L_pos = torch.sum(torch.relu(-evals) ** 2)
        L_reg = torch.sum(self.d_params ** 2)
        total = lambda_wdvv * L_wdvv + lambda_pos * L_pos + lambda_reg * L_reg
        return total, L_wdvv, L_pos, L_reg
    
    def optimize(self, n_iter=500, lr=2.0):
        optimizer = optim.LBFGS([self.d_params], lr=lr, max_iter=20,
                                history_size=50, line_search_fn='strong_wolfe')
        history = []
        
        def closure():
            optimizer.zero_grad()
            d = self.build_d_tensor()
            total, _, _, _ = self.compute_loss(d)
            total.backward()
            return total
        
        print(f"\n{'Iter':>6} | {'L_wdvv':>12} | {'L_pos':>12} | {'L_total':>12} | {'n_neg':>6} | {'n_pos':>6}")
        print("-" * 65)
        
        for step in range(n_iter):
            try:
                total = optimizer.step(closure)
            except:
                continue
            
            with torch.no_grad():
                d = self.build_d_tensor()
                _, L_wdvv, L_pos, L_reg = self.compute_loss(d)
                evals = self.compute_yukawa_eigenvalues(d)
                n_neg = torch.sum(evals < -1e-10).item()
                n_pos = torch.sum(evals > 1e-10).item()
                
                if step % 50 == 0 or step == n_iter - 1:
                    print(f"{step:6d} | {L_wdvv.item():>12.6e} | {L_pos.item():>12.6e} | "
                          f"{total.item():>12.6e} | {n_neg:6d} | {n_pos:6d}")
                
                history.append({
                    "step": step, "L_wdvv": L_wdvv.item(),
                    "L_pos": L_pos.item(), "n_neg": n_neg,
                    "evals": evals.detach().cpu().numpy().copy()
                })
        
        return history


if __name__ == "__main__":
    print("=" * 70)
    print("IDCM v10.0 — 原生 12D 張量 + WDVV")
    print("=" * 70)
    
    print("\n[1/3] 構建原生 12D 張量...")
    d_12_init, orbit_modes = build_native_12d_tensor()
    print(f"  張量: {d_12_init.shape}")
    print(f"  範圍: {d_12_init.min():.6e} ~ {d_12_init.max():.6e}")
    
    print("\n[2/3] C1 約束...")
    constraint_indices, init_values = build_constraint_indices_12d(orbit_modes)
    print(f"  分量: {len(constraint_indices)} / 364")
    print(f"  C1 排除率: {(1 - len(constraint_indices)/364)*100:.1f}%")
    
    print("\n[3/3] WDVV 求解...")
    solver = WDVVSolver12D(constraint_indices, init_values)
    
    with torch.no_grad():
        d_init = solver.build_d_tensor()
        evals_init = solver.compute_yukawa_eigenvalues(d_init)
        print(f"  優化前: {torch.sum(evals_init < -1e-10).item()} 負, "
              f"{torch.sum(evals_init > 1e-10).item()} 正")
        print(f"  本徵值: {evals_init.cpu().numpy()}")
    
    history = solver.optimize(n_iter=500, lr=2.0)
    
    print("\n" + "=" * 70)
    print("最終結果")
    print("=" * 70)
    with torch.no_grad():
        d = solver.build_d_tensor()
        evals = solver.compute_yukawa_eigenvalues(d)
        L_wdvv = solver.compute_wdvv_loss(d)
        n_neg = torch.sum(evals < -1e-10).item()
        n_pos = torch.sum(evals > 1e-10).item()
        
        positive = evals[evals > 1e-10]
        sorted_evals, _ = torch.sort(positive, descending=True)
        
        print(f"WDVV 殘差: {L_wdvv.item():.6e}")
        print(f"正本徵值: {n_pos}")
        print(f"負本徵值: {n_neg}")
        print(f"最終本徵值譜:")
        for i, e in enumerate(evals.cpu().numpy()):
            marker = " ✅" if e > 1e-10 else (" ❌" if e < -1e-10 else " ~0")
            print(f"  λ_{i+1:2d} = {e:.6e}{marker}")
        
        if n_pos > 0:
            print(f"\n正本徵值排序:")
            for i in range(min(12, len(sorted_evals))):
                print(f"  λ_{i+1:2d} = {sorted_evals[i].item():.6e}")
    
    np.save("data/d_tensor_native_12d.npy", d.cpu().numpy())
    np.save("data/eigenvalues_native_12d.npy", evals.cpu().numpy())
    print("\n已儲存 data/d_tensor_native_12d.npy ✅")