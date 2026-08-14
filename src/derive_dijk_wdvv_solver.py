"""
IDCM v10.0 — WDVV 數值求解器 (Vectorized)
===========================================
用 PyTorch + L-BFGS 求解 WDVV 方程
使用 vectorized operations 加速
"""

import math
import numpy as np
import torch
import torch.optim as optim

φ = (1 + math.sqrt(5)) / 2
φ_inv = 1 / φ
Nd = 44
M_Pl = 1.220890e22
h11 = 36

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"使用裝置: {device}")


def build_constraint_indices():
    """建立受 C1 約束嘅 d_{ijk} 索引"""
    n = h11
    modes = sorted(range(1, Nd + 1), key=lambda x: 4 * math.sin(math.pi * x / 88) ** 2)[:n]

    def mode_conservation(n_i, n_j, n_k):
        for s1 in [+1, -1]:
            for s2 in [+1, -1]:
                for s3 in [+1, -1]:
                    if (s1 * n_i + s2 * n_j + s3 * n_k) % Nd == 0:
                        return True
        return False

    constraint_indices = []
    all_indices = []
    for i in range(n):
        for j in range(i, n):
            for k in range(j, n):
                all_indices.append((i, j, k))
                n_i, n_j, n_k = modes[i], modes[j], modes[k]
                if mode_conservation(n_i, n_j, n_k):
                    constraint_indices.append((i, j, k))

    init_values = []
    for i, j, k in constraint_indices:
        n_i, n_j, n_k = modes[i], modes[j], modes[k]
        gamma_i = 4 * math.sin(math.pi * n_i / 88) ** 2
        gamma_j = 4 * math.sin(math.pi * n_j / 88) ** 2
        gamma_k = 4 * math.sin(math.pi * n_k / 88) ** 2
        val = φ ** (-(gamma_i + gamma_j + gamma_k) / 3)
        init_values.append(val)

    return constraint_indices, all_indices, np.array(init_values), modes


class WDVVSolver:
    """
    Vectorized WDVV 求解器
    用批次張量運算代替 Python 循環
    """

    def __init__(self, constraint_indices, all_indices, init_values, modes):
        self.constraint_indices = constraint_indices
        self.n = h11
        self.n_vars = len(constraint_indices)
        self.modes = modes

        # 初始變數
        self.d_params = torch.nn.Parameter(
            torch.tensor(init_values, dtype=torch.float64, device=device)
        )

        # 構建索引映射: 從 (i,j,k) 到參數 idx
        # 用於快速構建完整張量
        self.idx_list = torch.zeros((self.n, self.n, self.n), dtype=torch.long, device=device) - 1
        for idx, (i, j, k) in enumerate(constraint_indices):
            self.idx_list[i, j, k] = idx
            self.idx_list[i, k, j] = idx
            self.idx_list[j, i, k] = idx
            self.idx_list[j, k, i] = idx
            self.idx_list[k, i, j] = idx
            self.idx_list[k, j, i] = idx

    def build_d_tensor(self) -> torch.Tensor:
        """Vectorized: 從 698 參數構建 36×36×36 張量"""
        # 用索引映射直接填充
        mask = self.idx_list >= 0
        d = torch.zeros((self.n, self.n, self.n), dtype=torch.float64, device=device)
        d[mask] = self.d_params[self.idx_list[mask]]
        return d

    def compute_wdvv_loss(self, d: torch.Tensor) -> torch.Tensor:
        """Vectorized WDVV 殘差"""
        # 度量 g_{ij} = d_{ijk} t^k
        t = torch.ones(self.n, dtype=torch.float64, device=device)
        g = torch.einsum('ijk,k->ij', d, t)

        try:
            g_inv = torch.linalg.inv(g)
        except:
            return torch.tensor(1e10, dtype=torch.float64, device=device)

        # 計算 LHS: d_{ijp} g^{pq} d_{qkl}
        # 用 einstein summation
        lhs = torch.einsum('ijp,pq,qkl->ijkl', d, g_inv, d)

        # 計算 RHS: d_{ilp} g^{pq} d_{qjk}
        rhs = torch.einsum('ilp,pq,qjk->ijkl', d, g_inv, d)

        # 殘差 = Σ (lhs - rhs)²
        # 取前 6 個 index 做計算 (平衡速度)
        n_check = 6
        diff = lhs[:n_check, :n_check, :n_check, :n_check] - rhs[:n_check, :n_check, :n_check, :n_check]
        loss = torch.sum(diff ** 2)

        return loss

    def compute_yukawa_eigenvalues(self, d: torch.Tensor) -> torch.Tensor:
        """Vectorized 湯川矩陣本徵值"""
        # Y_{ab} = Σ_k d_{abk} v_k
        v = torch.tensor([φ ** (-k / self.n) for k in range(self.n)],
                         dtype=torch.float64, device=device)
        Y = torch.einsum('abk,k->ab', d, v)
        Y = (Y + Y.T) / 2

        try:
            return torch.linalg.eigvalsh(Y)
        except:
            return torch.zeros(self.n, dtype=torch.float64, device=device)

    def compute_loss(self, d: torch.Tensor,
                     lambda_wdvv: float = 1.0,
                     lambda_pos: float = 100.0,
                     lambda_reg: float = 0.001) -> tuple:
        """Vectorized 損失函數"""
        L_wdvv = self.compute_wdvv_loss(d)

        evals = self.compute_yukawa_eigenvalues(d)
        L_pos = torch.sum(torch.relu(-evals) ** 2)

        L_reg = torch.sum(self.d_params ** 2)

        total = lambda_wdvv * L_wdvv + lambda_pos * L_pos + lambda_reg * L_reg
        return total, L_wdvv, L_pos, L_reg

    def optimize(self, n_iter: int = 200, lr: float = 1.0) -> list[dict]:
        """L-BFGS 優化"""
        optimizer = optim.LBFGS([self.d_params], lr=lr, max_iter=10,
                                history_size=20, line_search_fn='strong_wolfe')

        history = []

        def closure():
            optimizer.zero_grad()
            d = self.build_d_tensor()
            total, _, _, _ = self.compute_loss(d)
            total.backward()
            return total

        print(f"{'Iter':>6} | {'L_wdvv':>12} | {'L_pos':>12} | {'L_total':>12} | {'n_neg':>6} | {'n_pos':>6}")
        print("-" * 60)

        for step in range(n_iter):
            try:
                total = optimizer.step(closure)
            except RuntimeError:
                print(f"  Step {step}: L-BFGS 收斂失敗, 重啟...")
                optimizer = optim.LBFGS([self.d_params], lr=lr*0.5, max_iter=10,
                                        history_size=20)
                continue

            with torch.no_grad():
                d = self.build_d_tensor()
                _, L_wdvv, L_pos, L_reg = self.compute_loss(d)
                evals = self.compute_yukawa_eigenvalues(d)
                n_neg = torch.sum(evals < -1e-10).item()
                n_pos = torch.sum(evals > 1e-10).item()

                if step % 20 == 0 or step == n_iter - 1:
                    print(f"{step:6d} | {L_wdvv.item():>12.6e} | {L_pos.item():>12.6e} | "
                          f"{total.item():>12.6e} | {n_neg:6d} | {n_pos:6d}")

                history.append({
                    "step": step,
                    "L_wdvv": L_wdvv.item(),
                    "L_pos": L_pos.item(),
                    "L_total": total.item(),
                    "n_neg": n_neg,
                    "evals": evals.detach().cpu().numpy().copy()
                })

        return history

    def finalize(self, history: list[dict]) -> dict:
        """輸出最終結果"""
        with torch.no_grad():
            d = self.build_d_tensor()
            evals = self.compute_yukawa_eigenvalues(d)

            positive = evals[evals > 1e-10]
            sorted_evals, _ = torch.sort(positive, descending=True)

            print("\n" + "=" * 70)
            print("WDVV 求解完成")
            print("=" * 70)
            print(f"WDVV 殘差: {history[-1]['L_wdvv']:.6e}")
            print(f"正本徵值數: {len(sorted_evals)}")
            print(f"負本徵值數: {history[-1]['n_neg']}")

            if len(sorted_evals) > 0:
                print(f"本徵值範圍: {sorted_evals[-1].item():.6e} ~ {sorted_evals[0].item():.6e}")

                print("\n前 21 個本徵值:")
                for i in range(min(21, len(sorted_evals))):
                    print(f"  λ_{i+1:2d} = {sorted_evals[i].item():.6e}")

            return {
                "d_tensor": d.cpu().numpy(),
                "eigenvalues": sorted_evals.cpu().numpy() if len(sorted_evals) > 0 else np.array([]),
                "history": history,
                "n_positive": len(sorted_evals),
            }


if __name__ == "__main__":
    print("=" * 70)
    print("IDCM v10.0 — WDVV 數值求解器 (Vectorized)")
    print("=" * 70)

    print("\n[1/4] 建立約束索引...")
    constraint_indices, all_indices, init_values, modes = build_constraint_indices()
    print(f"  C1 約束後: {len(constraint_indices)} / {len(all_indices)}")
    print(f"  排除率: {(1 - len(constraint_indices)/len(all_indices))*100:.1f}%")

    print("\n[2/4] 初始化求解器...")
    solver = WDVVSolver(constraint_indices, all_indices, init_values, modes)

    with torch.no_grad():
        d_init = solver.build_d_tensor()
        evals_init = solver.compute_yukawa_eigenvalues(d_init)
        n_neg_init = torch.sum(evals_init < -1e-10).item()
        n_pos_init = torch.sum(evals_init > 1e-10).item()
        print(f"  優化前: {n_neg_init} 負, {n_pos_init} 正")

    print("\n[3/4] L-BFGS 優化...")
    history = solver.optimize(n_iter=200, lr=1.0)

    print("\n[4/4] 最終結果")
    result = solver.finalize(history)

    if result["n_positive"] > 0:
        np.save("data/d_tensor_solved.npy", result["d_tensor"])
        np.save("data/eigenvalues_solved.npy", result["eigenvalues"])
        print("\n  結果已儲存")

    print("\n" + "=" * 70)
    print("WDVV 求解完畢")
    print("=" * 70)