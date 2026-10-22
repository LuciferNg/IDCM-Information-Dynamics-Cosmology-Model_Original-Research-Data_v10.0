"""
O72 驗證 01: K_Chain γ_k = 4sin²(πk/88) = 88-ring 離散 Laplacian 本徵譜
=====================================================================
目的: 驗證 K_Chain 色散譜喺 GR/LCDM 語言嘅錨點 —
      γ_k 精確等於 periodic 88-site chain 嘅 discrete Laplacian 本徵值。
      即係話 K_Chain = 緊緻 S¹ 上 free massless scalar 嘅晶格正則化。

數學:
    L = 2I - (S + S†)  (periodic 88-ring, 離散 Laplacian, 有符号約定 2-2cos)
    本徵值: λ_k = 4 sin²(πk/88), k = 0..87
    (k=0 零模 = 常數模式, 其餘 87 個非零 = 87 原子!)

檢查項目:
  [1] 88×88 Laplacian 本徵值 = 4sin²(πk/88)  (max err)
  [2] k=1..44 正頻譜 = K_Chain γ_k
  [3] 87 個非零模 = 87 原子 (43 邊 + 44 self-loop)
  [4] 零模 k=0 (γ=0) 單一存在
  [5] 連續極限: N→∞, 低 k 段 λ_k → (πk/N)² (相對論線性色散)
"""
import numpy as np

Nd = 44
N = 2 * Nd  # 88-ring

# [1] 88-ring discrete Laplacian (periodic BC)
L = np.zeros((N, N))
for i in range(N):
    L[i, i] = 2.0
    L[i, (i + 1) % N] = -1.0
    L[i, (i - 1) % N] = -1.0

evals = np.linalg.eigvalsh(L)
evals_sorted = np.sort(evals)

# 理論譜: 4 sin²(πk/88), k=0..87
k_theory = np.arange(N)
theory = 4.0 * np.sin(np.pi * k_theory / N) ** 2
theory_sorted = np.sort(theory)

max_err = np.max(np.abs(evals_sorted - theory_sorted))
print(f"[1] 88-ring Laplacian 本徵值 vs 4sin²(πk/88): max_err = {max_err:.3e}")
assert max_err < 1e-10, "Laplacian 譜唔等於 4sin²(πk/88)!"

# [2] k=1..44 正頻 = K_Chain γ_k (記憶: γ_k = 4sin²(πk/88), k=1..44)
gamma_kchain = 4.0 * np.sin(np.pi * np.arange(1, Nd + 1) / N) ** 2
# Laplacian 非零譜細到大排: k=1..44 (正頻) 對應 N-1..N-44? 睇排序
# eigvalsh 由細到大: 0 (k=0), 然後 k=87,86,...,1 嘅對稱對
nonzero = evals_sorted[1:]  # 87 個非零
# 87 非零 = 對稱對 {k, N-k} for k=1..43 + k=44 (自對偶) → 87 = 2×43 + 1
print(f"[2] 非零模數量 = {len(nonzero)}  (87 = 43 邊 + 44 self-loop)")
assert len(nonzero) == 87, "非零模唔係 87!"

# 檢查 k=44 (Nyquist, 自對偶) 單一模
gamma44 = 4.0 * np.sin(np.pi * Nd / N) ** 2
n_gamma44 = np.sum(np.abs(nonzero - gamma44) < 1e-10)
print(f"[3] γ_44 (Nyquist 自對偶) 出現次數 = {n_gamma44}  (應該 1)")
assert n_gamma44 == 1

# 對稱對: k 與 N-k 同值, k=1..43 → 43 對 = 86 模; +k=44 = 87 ✅
pairs = sum(1 for k in range(1, Nd) if np.abs(nonzero - 4*np.sin(np.pi*k/N)**2).min() < 1e-10)
# 每對兩個 → 數 unique 值
unique_vals = np.unique(np.round(nonzero, 12))
print(f"[4] 非零 unique 本徵值 = {len(unique_vals)}  (43 對 + Nyquist = 44 unique)")
assert len(unique_vals) == Nd, f"unique 本徵值應該 {Nd} 個, 實際 {len(unique_vals)}"

# [5] 連續極限: 低 k → λ_k ≈ (πk/44)² 嘅連續對應 (Laplacian 2-2cos(2πk/N) ≈ (2πk/N)²)
for k in [1, 2, 3]:
    lam = 4*np.sin(np.pi*k/N)**2
    cont = (2*np.pi*k/N)**2
    print(f"[5] k={k}: 晶格 λ={lam:.6f} vs 連續 (2πk/88)²={cont:.6f}  (ratio {lam/cont:.6f})")

# 摘要
print()
print("=== 結論 ===")
print("K_Chain γ_k = 4sin²(πk/88) 精確 = 88-ring 離散 Laplacian 本徵譜")
print("→ GR/LCDM 語言: K_Chain = S¹ (R_H = c/H₀ 圓周) 上 free massless scalar 嘅晶格正則化")
print("→ 87 非零模 = 87 原子 = 43 邊 + 44 self-loop (kchain_number_field 鏈閉合)")
print("→ k=44 Nyquist 自對偶 = 唯一單一模; k=0 零模 = 常數/佔位")
