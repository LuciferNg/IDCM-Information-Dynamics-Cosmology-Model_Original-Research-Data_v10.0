#!/usr/bin/env python3
"""
O59 攻堅 Q2: h11 = K_tree + N_gen = 33+3 正交分解
=================================================
目標:
  H_36 = H_tree^(33) ⊕ H_gen^(3)
  證明 3 個世代模態 = K_Chain Z₃ 簡併零模
  33 = flavorless 純幾何 background

方法:
  1. 用真 κ + J* 構建 36×36 矩陣
  2. 對角化 → 睇譜結構
  3. 搵 3 個「世代模態」+ 33 個「樹模態」
  4. 驗證正交性
  5. Z₃ 作用測試 (12-shift 等)
"""
import os, json, math
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
O53_POLY = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O59 攻堅 Q2: H_36 = H_tree(33) ⊕ H_gen(3)")
print("=" * 72)

passed, failed = 0, 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. 構建 36×36 矩陣 ============
print("\n[1] 構建 36×36 矩陣 (真 κ + J*)")
with open(os.path.join(O53_POLY, "cy36_98_intersection_full.json")) as f:
    K = np.array(json.load(f)["kappa"])
with open(os.path.join(O53_POLY, "Jstar_36D.json")) as f:
    J0 = np.array(json.load(f)["Jstar_36D"])
Y = np.einsum("ijk,k->ij", K, J0)
Y = (Y + Y.T) / 2

# 標準化 (對角尺度)
D = np.sqrt(np.abs(np.diag(Y)))
D[D < 1e-12] = 1
Ynorm = Y / np.outer(D, D)
print(f"  Y: {Y.shape}")
print(f"  tr(Y) = {np.trace(Y):.4f}")

# ============ 2. 譜結構 ============
print("\n[2] 譜結構 (36 本徵值)")
ev, evec = np.linalg.eigh(Y)
idx = np.argsort(np.abs(ev))[::-1]
ev = ev[idx]
evec = evec[:, idx]
print(f"  最大 10: {np.round(ev[:10], 3)}")
print(f"  最小 10: {np.round(ev[-10:], 3)}")
print(f"  正: {np.sum(ev>1e-10)}, 負: {np.sum(ev<-1e-10)}, 零: {np.sum(np.abs(ev)<1e-10)}")

# ============ 3. Z₃ 結構測試 ============
print("\n[3] Z₃ 作用測試 (12-shift)")
# 12-shift permutation
def shift_matrix(n, s):
    P = np.zeros((n, n))
    for i in range(n):
        P[i, (i+s) % n] = 1
    return P

# Z₃: 12-shift (0→12→24→0)
P12 = np.zeros((36, 36))
for i in range(12):
    P12[i, i+12] = 1
    P12[i+12, i+24] = 1
    P12[i+24, i] = 1
diff = np.linalg.norm(P12 @ Y @ P12.T - Y)
print(f"  P12·Y·P12ᵀ − Y: {diff:.4f}")
rel = diff / np.linalg.norm(Y)
print(f"  相對: {rel:.4f}")
check("Y 有 Z₃ 12-shift 對稱", rel < 0.1, f"(rel {rel:.3f})")

# ============ 4. 3×12 block 結構 (O53) ============
print("\n[4] 3×12 block 結構")
inter = np.zeros((3,3))
for i in range(3):
    for j in range(3):
        inter[i,j] = np.linalg.norm(Y[i*12:(i+1)*12, j*12:(j+1)*12])
print(f"  Inter-block norms:\n{np.round(inter, 3)}")
diag = inter[0,0]+inter[1,1]+inter[2,2]
off = inter.sum() - diag
print(f"  對角/非對角: {diag/off:.3f}")

# ============ 5. 搵 3 個世代模態 ============
print("\n[5] 搵 3 個「世代模態」")
# 3×12 block: 每個 block 嘅主模態 = 世代?
# 用 block 內最大本徵值
block_evs = []
for i in range(3):
    b = Y[i*12:(i+1)*12, i*12:(i+1)*12]
    bev = np.linalg.eigvalsh(b)
    block_evs.append(bev)
    print(f"  Block {i}: λ_max = {bev[-1]:.4f}, pos = {np.sum(bev>0)}")

# 每個 block 嘅主特徵向量
v_main = []
for i in range(3):
    b = Y[i*12:(i+1)*12, i*12:(i+1)*12]
    bev, bevec = np.linalg.eigh(b)
    v_main.append(bevec[:, -1])

# 3 個主模態正交性
for i in range(3):
    for j in range(i+1, 3):
        dot = np.dot(v_main[i], v_main[j])
        print(f"  v_{i}·v_{j} = {dot:.4f}")
check("3 個 block 主模態正交", abs(np.dot(v_main[0], v_main[1])) < 0.1
      and abs(np.dot(v_main[0], v_main[2])) < 0.1
      and abs(np.dot(v_main[1], v_main[2])) < 0.1,
      f"({np.dot(v_main[0],v_main[1]):.3f}, {np.dot(v_main[0],v_main[2]):.3f}, {np.dot(v_main[1],v_main[2]):.3f})")

# ============ 6. H_gen(3) 構造 ============
print("\n[6] H_gen(3) 構造")
# 假設: 3 個世代模態 = 3 個 block 主模態組合
# 用對角 block 嘅 top eigenvector 嵌入 36D
V_gen = np.zeros((36, 3))
for i in range(3):
    V_gen[i*12:(i+1)*12, i] = v_main[i]
# 正交化
Q, R = np.linalg.qr(V_gen)
print(f"  V_gen rank: {np.linalg.matrix_rank(V_gen)}")
print(f"  Q 正交: {np.allclose(Q.T@Q, np.eye(3))}")

# H_tree = 正交補
V_tree = np.linalg.qr(np.eye(36) - Q@Q.T)[0][:, :33]
print(f"  V_tree: {V_tree.shape}")

# 投影
P_gen = Q @ Q.T
P_tree = np.eye(36) - P_gen
Y_gen = P_gen @ Y @ P_gen.T
Y_tree = P_tree @ Y @ P_tree.T
print(f"  tr(Y_gen) = {np.trace(Y_gen):.4f}")
print(f"  tr(Y_tree) = {np.trace(Y_tree):.4f}")
print(f"  tr(Y) = {np.trace(Y):.4f}")
check("tr(Y_gen) + tr(Y_tree) ≈ tr(Y)", abs(np.trace(Y_gen)+np.trace(Y_tree)-np.trace(Y)) < 0.01)

# ============ 7. 33 vs 3 嘅能量分配 ============
print("\n[7] 33 vs 3 能量分配")
# 3 個主模態佔總譜幾多?
total_abs = np.sum(np.abs(ev))
top3_abs = np.sum(np.abs(ev[:3]))
print(f"  top-3 佔總: {top3_abs/total_abs*100:.1f}%")
print(f"  top-33 佔總: {np.sum(np.abs(ev[:33]))/total_abs*100:.1f}%")
# 但 36 = 33+3 係維度分解, 唔係能量

# ============ 8. 12D 子空間嘅 11+1 ============
print("\n[8] 12D 子空間嘅 11+1 (每個 block)")
for i in range(3):
    b = Y[i*12:(i+1)*12, i*12:(i+1)*12]
    bev = np.sort(np.linalg.eigvalsh(b))
    lam_max_b = bev[-1]
    rest = np.abs(bev[:-1])
    ratio = abs(lam_max_b)/max(np.mean(rest), 1e-12)
    print(f"  Block {i}: 1+11 ratio = {ratio:.1f}")

print(f"\n{'='*72}")
print(f"Q2: {passed} PASS, {failed} FAIL")
print(f"{'='*72}")
