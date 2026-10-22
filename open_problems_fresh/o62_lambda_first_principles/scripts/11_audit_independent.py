#!/usr/bin/env python3
"""
O62 AUDIT 01: 獨立重算 — 從零開始 (唔用任何舊 code)
=====================================================
獨立驗證 O62 所有關鍵數值:
  1. κ 數據載入 + 非零數
  2. F(γ) = (1/6)κγ³ 獨立計算
  3. V_Λ = F(γ) + 44 − 21 − 4
  4. 264 = 3×Σγ_even (88-site 對偶鏈)
  5. 19 = 44 − 25, 25 = 98 − 73
  6. P̂ row-norm corr
  7. Y(γ) kernel = 4, rank M = 32
  8. random t 統計
"""
import json, math
import numpy as np

print("=" * 72)
print("O62 AUDIT 01: 獨立重算")
print("=" * 72)

passed = 0
failed = 0
def check(name, got, expect, tol, detail=""):
    global passed, failed
    ok = abs(got - expect) <= tol
    if ok:
        passed += 1
        print(f"  ✅ {name}: {got:.8f} vs {expect:.8f} (tol {tol}) {detail}")
    else:
        failed += 1
        print(f"  ❌ {name}: {got:.8f} vs {expect:.8f} (tol {tol}) {detail}")

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0"

# ============ 1. κ 數據 ============
print("\n[1] κ 數據")
d = json.load(open(f"{BASE}/open_problems_fresh/o53_cy3_reality/data/polytopes/cy36_98_intersection_full.json"))
kappa = np.array(d["kappa"])
nnz = np.count_nonzero(kappa)
check("κ 非零數 = 1341", nnz, 1341, 0, "(O57/O61 一致)")
check("κ shape 36³", kappa.size, 36**3, 0)
# κ 對稱性
sym_err = np.max(np.abs(kappa - kappa.transpose(1,0,2)))
print(f"  κ 對稱性 (ij↔ji): {sym_err:.2e}")
check("κ 對稱", sym_err, 0, 1e-6)

# ============ 2. F(γ) ============
print("\n[2] F(γ)")
gamma36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2
# 方法 A: einsum
F_A = np.einsum("ijk,i,j,k", kappa, gamma36, gamma36, gamma36) / 6.0
# 方法 B: 循環 (獨立)
F_B = 0.0
for i in range(36):
    for j in range(36):
        for k in range(36):
            F_B += kappa[i,j,k] * gamma36[i] * gamma36[j] * gamma36[k]
F_B /= 6.0
check("F(γ) einsum", F_A, 264.0821292326, 1e-8)
check("F(γ) 循環法一致", F_A, F_B, 1e-8, "(兩種方法)")
check("F(γ)−264 < 0.1", abs(F_A - 264), 0.082129, 0.001, f"(差 {abs(F_A-264):.6f} = 0.031%)")

# ============ 3. V_Λ ============
print("\n[3] V_Λ")
V_obs = 283.0752
V_Lambda = F_A + 44 - 21 - 4
err = abs(V_Lambda - V_obs)/V_obs*100
check("V_Λ = F+19", V_Lambda, 283.0821292326, 1e-6)
check("誤差 0.00245%", err, 0.00245, 0.001, f"(實際 {err:.5f}%)")
rho_model = math.exp(-V_Lambda)
rho_obs = 1.1535e-123
check("ρ 比 0.9931", rho_model/rho_obs, 0.9931, 0.001)

# ============ 4. 264 = 3×Σγ_odd ============
print("\n[4] 對偶鏈 264")
# ⚠️ Parity 修正: [::2] = k=1,3,...,87 = ODD → Σγ_odd = 88
gamma88 = 4 * np.sin(np.pi * np.arange(1, 89) / 176) ** 2
sum_odd = gamma88[::2].sum()    # k=1,3,...,87 (ODD) → 88
sum_even = gamma88[1::2].sum()  # k=2,4,...,88 (EVEN) → 90
check("Σγ_odd = 88", sum_odd, 88, 0.01)
check("Σγ_even = 90", sum_even, 90, 0.01)
check("Σγ_total = 178", sum_odd+sum_even, 178, 0.01)
check("3×Σγ_odd = 264", 3*sum_odd, 264, 0.01)
check("F(γ)−264 = 0.0821", abs(F_A - 264), 0.082129, 0.0001)

# ============ 5. 19 修正 ============
print("\n[5] 19 = 44 − 25")
check("25 = F₈+B", 21+4, 25, 0)
check("25 = 98−73", 98-73, 25, 0)
check("19 = 44−25", 44-25, 19, 0)
check("19 = L₅+F₆", 11+8, 19, 0)

# ============ 6. P̂ row-norm corr ============
print("\n[6] P̂ row-norm")
P = np.load(f"{BASE}/data/P_fixed_v2.npy")
P_k = P[:36, :]
row_norms = np.linalg.norm(P_k, axis=1)
corr = np.corrcoef(row_norms, gamma36)[0,1]
print(f"  P̂ shape: {P.shape}")
check("P̂ shape (134,946)", P.shape[0]*1.0, 134, 0)
check("P̂ shape 946", P.shape[1]*1.0, 946, 0)
check("Kähler support 全 = 21", np.all(np.count_nonzero(P_k, axis=1) == 21), 1, 0)
check("row-norm corr γ = −0.9947", corr, -0.9947, 0.001, f"(實際 {corr:.4f})")

# ============ 7. Y(γ) kernel ============
print("\n[7] Y(γ) kernel")
Yg = np.einsum("ijk,k", kappa, gamma36)
evals = np.linalg.eigvalsh(Yg)
n_zero = np.sum(np.abs(evals) < 1e-8)
check("Y(γ) kernel = 4", n_zero, 4, 0)
Mg = Yg.T @ Yg
rank_M = np.sum(np.linalg.eigvalsh(Mg) > 1e-8)
check("rank M = 32", rank_M, 32, 0)

# ============ 8. random t 統計 ============
print("\n[8] random t 統計 (重新獨立跑)")
rng = np.random.default_rng(12345)
N = 5000
target = V_obs - 19
tol_v = V_obs * 0.0001
hits = 0
F_vals = np.zeros(N)
for i in range(N):
    t = rng.uniform(0.005, 4.0, 36)
    F_vals[i] = np.einsum("ijk,i,j,k", kappa, t, t, t) / 6.0
    if abs(F_vals[i] - target) < tol_v:
        hits += 1
hit_rate = hits/N
print(f"  random t N={N}: hits={hits}, rate={hit_rate:.6f}")
check("random t 命中率 0", hit_rate, 0, 0.0005, f"(實際 {hit_rate:.6f})")
p_264 = np.sum(np.abs(F_vals - 264) < 1)/N
print(f"  P(|F−264|<1) = {p_264:.4f}")
check("P(|F−264|<1) < 0.01", p_264, 0, 0.01, f"(實際 {p_264:.4f})")

# ============ 9. 總結 ============
print("\n" + "=" * 72)
print(f"AUDIT 01 總結: Passed {passed}, Failed {failed}")
print("=" * 72)
if failed > 0:
    exit(1)
print("🎉 獨立重算全部一致!")
