#!/usr/bin/env python3
"""
08_wave_decay.py — 波方程衰減: 點解 φ 每層?
===============================================
O4 核心未解問題: 點解振幅按 BFS 距離 φ^(-d) 衰減?

候選機制: A₅ Cayley 圖上嘅波傳播
- 圖 Laplacian 譜: Λ = {0, 11/3×9, 4×16, 22/5×25} (解析)
- 波響應 ψ(d,t) = Σ_k cos(ω_k t) φ_k(0)φ_k(i), ω_k = √Λ_k
- 靜態 Green: G(d) = Σ_{k≠0} φ_k(0)φ_k(i)/Λ_k

但 G(d) 層比 = 0.42 (唔係 φ⁻¹=0.618) → 靜態 Green 唔係答案!

新方向: 檢查圖上隨機遊走 (熱擴散) P_t(d)
- P_t(d) = 層內平均轉移概率
- 喺時間 t, 擴散半徑 ~ √(λ₁t)
- 對 Cayley 圖, 隨機遊走有對數增長... 

或者: 特徵函數投影!
- A₅ 3-dim irrep 嘅特徵函數 φ_k(i) ∝ χ(g_i) (特徵標值)
- 冷斑 = e (恆等元素): φ_k(e) = dim(ρ_k) = 3
- 節點 i: φ_k(i) = χ_ρ(g_i)
- 對 3-irrep: χ₃(g_i) 取決於 g_i 嘅 class!
- class 5A/5B 嘅 χ₃ = φ 或 1-φ → |χ₃| ∈ {φ, 0.618}
- 投影 |φ_k(e)φ_k(i)| = 3×|χ₃(g_i)| → 每步 word length 增加 → class 變化
"""
import numpy as np
import math
from collections import defaultdict, deque

phi = (1 + 5**0.5) / 2
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

print("=" * 72)
print("O4 08: 波方程 + 特徵標投影衰減")
print("=" * 72)

# ---------- 1. 圖 ----------
nodes = np.loadtxt('/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt')
vecs = np.array([np.array([math.cos(math.radians(d))*math.cos(math.radians(r)),
                           math.cos(math.radians(d))*math.sin(math.radians(r)),
                           math.sin(math.radians(d))]) for r, d in nodes])
adj = defaultdict(set)
edges = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j); adj[j].add(i)
            edges.append((i, j))

dist = {0: 0}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in dist:
            dist[v] = dist[u] + 1
            q.append(v)

# ---------- 2. Laplacian 譜 ----------
A_mat = np.zeros((60, 60))
for u, v in edges:
    A_mat[u, v] = 1
    A_mat[v, u] = 1
D = np.diag(A_mat.sum(axis=1))
L = D - A_mat
eigvals, eigvecs = np.linalg.eigh(L)

# ---------- 3. 隨機遊走 (熱擴散) ----------
print("\n=== 隨機遊走 P_t(d) (熱擴散) ===")
P = np.zeros(60)
P[0] = 1.0
print(f"{'t':>3} {'P_t(0)':>8} {'P_t(1)':>8} {'P_t(2)':>8} {'P_t(3)':>8} {'<d>':>6} {'<d²>':>7}")
for t in range(0, 16):
    # 層內平均
    shell_mean = {}
    for d in range(9):
        idx = [i for i in range(60) if dist[i] == d]
        if idx:
            shell_mean[d] = np.mean(P[idx])
    d_avg = sum(d * shell_mean.get(d, 0) for d in range(9))
    d2_avg = sum(d*d * shell_mean.get(d, 0) for d in range(9))
    if t in [0,1,2,3,4,5,8,10,12,15]:
        print(f"{t:>3} {shell_mean.get(0,0):>8.4f} {shell_mean.get(1,0):>8.4f} {shell_mean.get(2,0):>8.4f} {shell_mean.get(3,0):>8.4f} {d_avg:>6.2f} {d2_avg:>7.2f}")
    P = P @ (A_mat / 4.0)  # 隨機遊走一步 (degree 4)

# ---------- 4. 特徵標投影理論 ----------
print("\n=== 特徵標投影 (A₅ 3-irrep) ===")
# 節點嘅群元素 class: 需要映射節點 → 群元素
# 用旋轉角 + 軸類型分類: 2A(180°), 3A(120°), 5A/5B(72°/144°)
# 用角度直方圖: 26.09° (3-fold 投影), 31.68° (2-fold), 42.97° (5-fold)

# 由 §9 skill: 邊長映射到群元素
# 26.09° ← 120° 3-fold (axis=vertex dir)
# 26.17° ← 72° 5-fold
# 31.68° ← 180° 2-fold
# 42.97° ← 144° 5-fold

print("邊長 ↔ 群元素 (由 polyhedral-graph-analysis §9):")
print("  26.09° ← 3-fold 120° (axis = dodecahedron vertex)")
print("  26.17° ← 5-fold 72°")
print("  31.68° ← 2-fold 180°")
print("  42.97° ← 5-fold 144°")
print("\nA₅ 特徵標 χ₃ (3-irrep):")
print("  χ₃(e) = 3, χ₃(2A) = -1, χ₃(3A) = 0, χ₃(5A) = φ, χ₃(5B) = 1-φ")
print("  |χ₃|: e=3, 2A=1, 3A=0, 5A=1.618, 5B=0.618")
print("\n→ 3-irrep 特徵函數 φ_k(i) = χ₃(g_i)")
print("→ 冷斑 φ_k(0) = χ₃(e) = 3")
print("→ 第一層 (word length 1 = 生成元):")
print("   生成元 = 5-fold 72° (R5) 或 3-fold 120° (R3)")
print("   χ₃(R5) = φ → 投影 3φ")
print("   χ₃(R3) = 0 → 投影 0")
print("→ 混合生成元: 平均 |χ₃| 衰減!")

# ---------- 5. 測試: word length 每步 class 轉移 ----------
print("\n=== 隨機遊走特徵標衰減 (數值模擬) ===")
# 用特徵函數投影: 冷斑 = 3-irrep 嘅「源」
# ψ(i) = Σ_k c_k φ_k(i), 只保留 3-irrep 部分 (9 個特徵函數)
# 3-irrep = 特徵值 11/3 嘅特徵空間
mask_3 = np.abs(eigvals - 11/3) < 1e-6
print(f"3-irrep 特徵值 11/3 多重度: {mask_3.sum()} (期望 9)")
mask_4 = np.abs(eigvals - 4) < 1e-6
print(f"4-irrep 特徵值 4 多重度: {mask_4.sum()} (期望 16)")
mask_5 = np.abs(eigvals - 22/5) < 1e-6
print(f"5-irrep 特徵值 22/5 多重度: {mask_5.sum()} (期望 25)")

# 點源喺 3-irrep 子空間嘅投影
proj3 = np.zeros(60)
for k in range(60):
    if mask_3[k]:
        proj3 += eigvecs[:, k] * eigvecs[0, k]
print(f"\n3-irrep 點源投影 ψ₃(i):")
print(f"{'d':>3} {'n':>4} {'mean ψ₃':>10} {'|mean|':>8}")
for d in range(9):
    idx = [i for i in range(60) if dist[i] == d]
    if not idx:
        continue
    m = np.mean(proj3[idx])
    print(f"{d:>3} {len(idx):>4} {m:>10.4f} {abs(m):>8.4f}")

# 全譜投影 (所有非零模)
proj_all = np.zeros(60)
for k in range(1, 60):
    proj_all += eigvecs[:, k] * eigvecs[0, k] / eigvals[k]
print(f"\n全譜 Green 投影 G(i):")
print(f"{'d':>3} {'n':>4} {'mean G':>10} {'|G|':>8} {'φ^-d':>7} {'F_{5-d}/5':>9}")
for d in range(9):
    idx = [i for i in range(60) if dist[i] == d]
    if not idx:
        continue
    m = np.mean(proj_all[idx])
    fv = F[5-d]/5 if 0 <= 5-d <= 9 else 0
    print(f"{d:>3} {len(idx):>4} {m:>10.4f} {abs(m):>8.4f} {phi**(-d):>7.4f} {fv:>9.3f}")

# ---------- 6. 結論: 特徵標投影 vs 觀測 ----------
print(f"\n=== 對比: 理論投影 vs 觀測 |T| ===")
# 3-irrep 投影正比於 |ψ₃|, 同 |T| 對比
proj3_abs = np.abs(proj3)
proj3_norm = proj3_abs / proj3_abs[0] * 150  # 歸一化到冷斑 150
print(f"{'d':>3} {'n':>4} {'|T| obs':>8} {'ψ₃ 歸一':>8} {'φ^-d×150':>9}")
for d in range(9):
    idx = [i for i in range(60) if dist[i] == d]
    if not idx:
        continue
    # 觀測 |T| (由先前數據, 用 smica_fibonacci.txt 嘅 T_obs)
    pass
print("(需要 SMICA 數據, 見 09 腳本)")

# 儲存
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o4_fib_motivation/data/wave_decay.txt', 'w') as f:
    f.write("# O4 08: 波方程衰減\n")
    f.write(f"# Laplacian 譜: Λ = {{0, 11/3×9, 4×16, 22/5×25}}\n")
    f.write(f"# 3-irrep 特徵函數 = χ₃(g): |χ₃(5A)|=φ, |χ₃(5B)|=0.618\n")
    f.write(f"# 隨機遊走同靜態 Green 唔係 φ 律 (G1/G0=0.42)\n")
    f.write(f"# 待解: 波方程時間平均可能係 φ 律 (需要 09)\n")
print(f"\n✅ 已存: data/wave_decay.txt")
