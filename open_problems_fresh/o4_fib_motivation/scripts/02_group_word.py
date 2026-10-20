#!/usr/bin/env python3
"""
02_group_word.py — A₅ 群結構: word length, 路徑數, 特徵標, Green 函數
=====================================================================
O4 機制 2: 節點等級由群元素 word length / 最短路徑數決定?

核心問題:
1. BFS 距離 = Cayley 圖 word length (圖本身 = A₅ Cayley 圖, 生成元 {a,a⁻¹,b,b⁻¹})
2. A₅ 特徵標包含 φ (3, 3' irrep) — 呢個係 Fibonacci 嘅群論來源!
3. 圖 Laplacian Green 函數 G(d) = Σ_k φ_k(0)φ_k(i)/λ_k → 每層衰減
4. 如果 G(d) 衰減 ≈ φ 每層 → Fibonacci 整數閉合 (F_{5-d})

物理鏈: 冷斑 = ℓ=44 SYNC 源 → A₅ 網格傳播 → Green 函數 = φ 衰減
→ Fibonacci 整數閉合 = F₅, F₄, F₃
"""
import numpy as np
import math
from collections import defaultdict, deque

phi = (1 + 5**0.5) / 2
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]  # F_0..F_9

print("=" * 72)
print("O4 02: A₅ 群結構 — word length, 路徑數, 特徵標, Green 函數")
print("=" * 72)

# ---------- 1. 載入節點 + 建圖 ----------
nodes = np.loadtxt('/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt')
vecs = np.array([np.array([math.cos(math.radians(d))*math.cos(math.radians(r)),
                           math.cos(math.radians(d))*math.sin(math.radians(r)),
                           math.sin(math.radians(d))]) for r, d in nodes])

def ang(i, j):
    return math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))

adj = defaultdict(set)
edges = []
for i in range(60):
    for j in range(i+1, 60):
        if ang(i, j) < 28.0:
            adj[i].add(j); adj[j].add(i)
            edges.append((i, j))

# ---------- 2. BFS 距離 + 最短路徑數 ----------
def bfs_paths(src):
    dist = {src: 0}
    paths = {src: 1}
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                paths[v] = paths[u]
                q.append(v)
            elif dist[v] == dist[u] + 1:
                paths[v] += paths[u]
    return dist, paths

dist, paths = bfs_paths(0)

print(f"\n=== BFS 距離 + 最短路徑數 (由冷斑 node 0) ===")
print(f"{'d':>3} {'n':>4} {'Σ路徑':>7} {'路徑數set':>18} {'F_{5-d}':>7}")
shell_path_sum = {}
for d in range(9):
    idx = [i for i in range(60) if dist[i] == d]
    if not idx:
        continue
    p_uniq = sorted(set(paths[i] for i in idx))
    p_sum = sum(paths[i] for i in idx)
    shell_path_sum[d] = p_sum
    fv = F[5-d] if 0 <= 5-d <= 9 else '?'
    print(f"{d:>3} {len(idx):>4} {p_sum:>7} {str(p_uniq):>18} {str(fv):>7}")

# ---------- 3. A₅ 特徵標 (理論表) ----------
print(f"\n=== A₅ 特徵標 (含 φ!) ===")
print("A₅ 不可約表示: 1, 3, 3', 4, 5 (維數 1,3,3,4,5)")
print("維數包含 Fibonacci: 3 = F₄, 5 = F₅")
print("3 同 3' 表示嘅特徵值包含 φ = (1+√5)/2 同 1-φ = -φ⁻¹")
print("→ A₅ 特徵標結構上內建黃金比例!")

# 特徵標表: 類別 [e, 2A, 3A, 5A, 5B]
chi = {
    '1':  [1, 1, 1, 1, 1],
    '3':  [3, -1, 0, phi, 1-phi],
    '3p': [3, -1, 0, 1-phi, phi],
    '4':  [4, 0, 1, -1, -1],
    '5':  [5, 1, -1, 0, 0],
}
class_sizes = [1, 15, 20, 12, 12]
print(f"\n{'irrep':>5} {'dim':>3} {'χ(e)':>6} {'χ(2A)':>6} {'χ(3A)':>6} {'χ(5A)':>8} {'χ(5B)':>8}")
for name, row in chi.items():
    print(f"{name:>5} {row[0]:>3} {row[0]:>6} {row[1]:>6} {row[2]:>6} {row[3]:>8.4f} {row[4]:>8.4f}")

# 正交性驗證: Σ|χ|² = |G| = 60
print(f"\n正交性 Σ|χ|² (期望 60):")
for name, row in chi.items():
    s = sum(class_sizes[i] * row[i]**2 for i in range(5))
    ok = "✅" if abs(s - 60) < 1e-6 else "❌"
    print(f"  {name}: {s:.4f} {ok}")

# ---------- 4. Cayley 圖 Laplacian 譜 ----------
# 圖 = Cayley 圖 A₅, 生成元 {a (order3), a⁻¹, b (order5), b⁻¹}
# 鄰接矩陣特徵值 λ_ρ = [2χ_ρ(3A) + χ_ρ(5A) + χ_ρ(5B)] / dim(ρ)
print(f"\n=== Cayley 圖 Laplacian 譜 (解析) ===")
print(f"鄰接特徵值 λ_ρ = [2χ(3A) + χ(5A) + χ(5B)]/dim, Laplacian Λ = 4 - λ")
for name, row in chi.items():
    lam = (2*row[2] + row[3] + row[4]) / row[0]
    L = 4 - lam
    mult = row[0]**2
    print(f"  irrep {name}: λ={lam:.6f}, Λ={L:.6f}, 多重度={mult}")

# ---------- 5. 數值 Laplacian + Green 函數 ----------
print(f"\n=== 數值 Laplacian + Green 函數 ===")
A_mat = np.zeros((60, 60))
for u, v in edges:
    A_mat[u, v] = 1
    A_mat[v, u] = 1
D = np.diag(A_mat.sum(axis=1))
L_mat = D - A_mat

eigvals, eigvecs = np.linalg.eigh(L_mat)
print(f"數值特徵值 (前 8 個): {np.round(eigvals[:8], 4)}")
print(f"多重度: 0×{sum(1 for v in eigvals if v < 1e-8)}, " +
      f"11/3≈3.667×{sum(1 for v in eigvals if abs(v-11/3)<1e-6)}, " +
      f"4×{sum(1 for v in eigvals if abs(v-4)<1e-6)}, " +
      f"22/5=4.4×{sum(1 for v in eigvals if abs(v-22/5)<1e-6)}")

# Green 函數: Lψ = δ₀ → ψ = Σ_{k>0} φ_k(0)φ_k(i)/Λ_k
G = np.zeros(60)
for k in range(1, 60):
    G += eigvecs[:, k] * eigvecs[0, k] / eigvals[k]

print(f"\nGreen 函數 G(d) (靜態點源響應):")
print(f"{'d':>3} {'n':>4} {'G mean':>9} {'G/G₀':>8} {'φ^-d':>7} {'F_{5-d}/5':>9}")
G_by_d = {}
for d in range(9):
    idx = [i for i in range(60) if dist[i] == d]
    if not idx:
        continue
    g_mean = np.mean(G[idx])
    G_by_d[d] = g_mean
    ratio = g_mean / G_by_d[0]
    fval = F[5-d]/5 if 0 <= 5-d <= 9 else 0
    print(f"{d:>3} {len(idx):>4} {g_mean:>9.4f} {ratio:>8.4f} {phi**(-d):>7.4f} {fval:>9.3f}")

# Green 函數比 vs φ 比
print(f"\nGreen 函數層比: G(1)/G(0) = {G_by_d[1]/G_by_d[0]:.4f} (φ⁻¹={phi**-1:.4f}, F₄/F₅={3/5:.4f})")
print(f"              G(2)/G(0) = {G_by_d[2]/G_by_d[0]:.4f} (φ⁻²={phi**-2:.4f}, F₃/F₅={2/5:.4f})")
print(f"              G(2)/G(1) = {G_by_d[2]/G_by_d[1]:.4f} (φ⁻¹={phi**-1:.4f}, F₃/F₄={2/3:.4f})")

# ---------- 6. 波響應 (時間平均能量) ----------
print(f"\n=== 波響應 (時間平均 ⟨ψ²⟩) — 對比 §17 已知結果 ===")
E = np.zeros(60)
for k in range(60):
    E += 0.5 * (eigvecs[:, k] * eigvecs[0, k])**2
print(f"{'d':>3} {'n':>4} {'√E mean':>9} {'√E/√E₀':>8}")
E_by_d = {}
for d in range(9):
    idx = [i for i in range(60) if dist[i] == d]
    if not idx:
        continue
    E_mean = np.mean(np.sqrt(E[idx]))
    E_by_d[d] = E_mean
    print(f"{d:>3} {len(idx):>4} {E_mean:>9.4f} {E_mean/E_by_d[0]:>8.4f}")

# 儲存
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o4_fib_motivation/data/group_word.txt', 'w') as f:
    f.write("# O4 02: A₅ 群結構分析\n")
    f.write(f"# BFS d node path_count G_green sqrtE\n")
    for i in range(60):
        f.write(f"{dist[i]} {i} {paths[i]} {G[i]:.6f} {np.sqrt(E[i]):.6f}\n")
    f.write(f"\n# Green 函數層均: " + ", ".join(f"d{d}:{G_by_d[d]:.4f}" for d in sorted(G_by_d)) + "\n")
    f.write(f"# 層比 G1/G0={G_by_d[1]/G_by_d[0]:.4f} (φ⁻¹={phi**-1:.4f}, F4/F5={3/5:.4f})\n")
    f.write(f"# 層比 G2/G0={G_by_d[2]/G_by_d[0]:.4f} (φ⁻²={phi**-2:.4f}, F3/F5={2/5:.4f})\n")
print(f"\n✅ 已存: data/group_word.txt")
