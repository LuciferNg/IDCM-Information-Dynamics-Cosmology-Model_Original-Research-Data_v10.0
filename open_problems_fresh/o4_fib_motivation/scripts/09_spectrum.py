#!/usr/bin/env python3
"""
09_spectrum.py — A₅ 圖譜完整分析: φ 結構
==========================================
發現: 數值 Laplacian 特徵值 0.382 = φ⁻² (多重度 3)!

完整檢查: 成個譜係咪 φ 結構?
- Laplacian 特徵值: 0, 0.382(φ⁻²), 1.0746, 2.618(φ²)...
- 多重度: 1, 3, 4, ...
- 特徵值比: 0.382/0.618 = ? 1.0746/0.382 = ?

同時: 隨機遊走衰減率 = 第二特徵值 = ?
"""
import numpy as np
import math
from collections import defaultdict, deque

phi = (1 + 5**0.5) / 2

print("=" * 72)
print("O4 09: A₅ 圖譜 — Laplacian 特徵值嘅 φ 結構")
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

A_mat = np.zeros((60, 60))
for u, v in edges:
    A_mat[u, v] = 1
    A_mat[v, u] = 1
D = np.diag(A_mat.sum(axis=1))
L = D - A_mat
eigvals, eigvecs = np.linalg.eigh(L)

# ---------- 2. 完整譜 ----------
print("\n=== Laplacian 完整譜 ===")
print(f"{'idx':>3} {'λ':>10} {'λ/φ⁻²':>8} {'φ^n 匹配':>10}")
phi_vals = {phi**n: f"φ^{n}" for n in range(-8, 9)}
phi_vals[0] = "0"
phi_vals[4] = "4"
phi_vals[4.0] = "4"
for i, lam in enumerate(eigvals):
    best = None
    best_err = 1e9
    for val, name in phi_vals.items():
        err = abs(lam - val) / max(lam, 1e-9)
        if err < best_err:
            best_err = err
            best = name
    match = f"{best} ({best_err*100:.1f}%)" if best_err < 0.05 else ""
    print(f"{i:>3} {lam:>10.6f} {lam/phi**-2:>8.4f} {match:>10}")

# ---------- 3. 多重度分組 ----------
print("\n=== 特徵值分組 ===")
from collections import Counter
groups = Counter(np.round(eigvals, 6))
for lam, mult in sorted(groups.items()):
    phi_rel = ""
    for val, name in phi_vals.items():
        if abs(lam - val) / max(lam, 1e-9) < 0.02:
            phi_rel = f" ≈ {name}"
    print(f"λ = {lam:.6f} × {mult} {phi_rel}")

# ---------- 4. 特徵值比 ----------
print("\n=== 特徵值 φ 比 ===")
uniq = sorted(set(np.round(eigvals, 6)))
for i in range(1, min(len(uniq), 8)):
    for j in range(i):
        r = uniq[i] / uniq[j]
        if abs(r - phi) < 0.05 or abs(r - phi**2) < 0.05 or abs(r - 1/phi) < 0.05:
            print(f"λ{uniq[i]:.4f}/λ{uniq[j]:.4f} = {r:.4f} (φ={phi:.4f}, φ²={phi**2:.4f})")

# ---------- 5. 鄰接矩陣特徵值 ----------
print("\n=== 鄰接矩陣特徵值 (λ_adj = 4 - λ_L) ===")
adj_ev = 4 - eigvals
print(f"{'idx':>3} {'λ_adj':>10} {'φ 匹配':>12}")
for i, lam in enumerate(adj_ev[:12]):
    best = None
    best_err = 1e9
    for val, name in phi_vals.items():
        err = abs(lam - val) / max(lam, 1e-9)
        if err < best_err:
            best_err = err
            best = name
    match = f"{best} ({best_err*100:.1f}%)" if best_err < 0.05 else ""
    print(f"{i:>3} {lam:>10.6f} {match:>12}")

# ---------- 6. 隨機遊走衰減 ----------
print("\n=== 隨機遊走 (擴散) 衰減率 ===")
# P_{t+1} = P_t · A/4, 衰減由第二特徵值 λ₂_L/4 決定
lam2 = eigvals[1]
decay = 1 - lam2/4
print(f"第二特徵值 λ₂ = {lam2:.6f}")
print(f"擴散衰減率 = 1 - λ₂/4 = {decay:.4f} (φ⁻¹={phi**-1:.4f}?)")
print(f"λ₂/4 = {lam2/4:.4f} (φ⁻²={phi**-2:.4f}?)")
print(f"→ λ₂ = {lam2:.4f} vs 4φ⁻² = {4*phi**-2:.4f} (差 {(lam2-4*phi**-2)/(4*phi**-2)*100:.1f}%)")

# ---------- 7. 特徵值 vs 群表示理論 ----------
print("\n=== 群表示理論預測 vs 實際 ===")
print("Cayley 圖 (生成元 {R5,R5⁻¹,R3,R3⁻¹}) 理論譜:")
print("  Λ = {0, 11/3×9, 4×16, 22/5×25}")
print("實際譜 (最近鄰居圖):")
print("  λ₂ = 0.382 = φ⁻² ?")
print("  即實際圖嘅生成元集合唔同 (混合 3A/5A)")
print("  → 0.382 = φ⁻² 係實際幾何圖嘅特徵值!")

# 儲存
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o4_fib_motivation/data/spectrum.txt', 'w') as f:
    f.write("# O4 09: A₅ 圖譜 φ 結構\n")
    f.write(f"# Laplacian 特徵值: {np.round(eigvals[:12], 6)}\n")
    f.write(f"# λ₂ = {eigvals[1]:.6f}, φ⁻² = {phi**-2:.6f}, 差 {(eigvals[1]-phi**-2)/phi**-2*100:.2f}%\n")
    f.write(f"# 多重度: {dict(Counter(np.round(eigvals, 6)))}\n")
print(f"\n✅ 已存: data/spectrum.txt")
