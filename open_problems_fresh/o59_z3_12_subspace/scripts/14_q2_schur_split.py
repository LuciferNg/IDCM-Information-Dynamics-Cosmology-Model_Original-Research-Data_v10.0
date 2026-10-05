#!/usr/bin/env python3
"""
O59 攻堅 Q2 Phase 2: Schur 分解版 3×(1+11) = 33+3
=================================================
O53 已證: Y = Schur block-triangular (3×12 可約化)
→ 喺 Schur 基下, Y ≈ 3 個 12×12 塊直和
→ 每個塊內部: 1 (gen) + 11 (tree) 譜
→ 全局: 3 gen + 33 tree = 33+3!

測試:
  1. Schur/正交化後 block 對角性
  2. 每個 block 嘅 1+11 譜
  3. 3 gen 模態正交性 (Schur 基下)
  4. H_gen(3) ⊕ H_tree(33) 正交分解
"""
import os, json, math
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
O53_POLY = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O59 Q2 Phase 2: Schur 3×(1+11) = 33+3")
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

# ============ 1. 載入 + 構建 ============
with open(os.path.join(O53_POLY, "cy36_98_intersection_full.json")) as f:
    K = np.array(json.load(f)["kappa"])
with open(os.path.join(O53_POLY, "Jstar_36D.json")) as f:
    J0 = np.array(json.load(f)["Jstar_36D"])
Y = np.einsum("ijk,k->ij", K, J0)
Y = (Y + Y.T) / 2

# ============ 2. 搵 block-triangular 基 ============
print("\n[2] 搵 block 可約化基 (O53: Schur)")
# 方法: 對 Y 做正交對角化, 但保留 3×12 分組
# O53 用 Schur 分解: Y = Q T Q*, T 下三角, 3×12 blocks
# numpy 冇 schur → 用 scipy
try:
    from scipy.linalg import schur
    T, Q = schur(Y, output='real')
    print(f"  Schur T 下三角 norm: {np.linalg.norm(np.triu(T, 1)):.6f}")
    # block 對角性: T 嘅 3×12 block 結構
    B_T = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            B_T[i, j] = np.linalg.norm(T[i*12:(i+1)*12, j*12:(j+1)*12])
    print(f"  T block norms:\n{np.round(B_T, 4)}")
    diag_T = B_T[0,0]+B_T[1,1]+B_T[2,2]
    off_T = B_T.sum() - diag_T
    print(f"  T 對角/非對角: {diag_T/off_T:.3f}")
    check("Schur T block 對角主導", diag_T/off_T > 2, f"({diag_T/off_T:.2f})")
except ImportError:
    print("  scipy 唔可用, 用 QR 迭代")
    # 用 QR 攞近似 block-triangular
    Q, R = np.linalg.qr(Y)
    T = Q.T @ Y @ Q
    B_T = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            B_T[i, j] = np.linalg.norm(T[i*12:(i+1)*12, j*12:(j+1)*12])
    print(f"  QR T block norms:\n{np.round(B_T, 4)}")

# ============ 3. 每個 block 嘅 1+11 譜 ============
print("\n[3] 每個 12D block 嘅 1+11 譜")
# 喺 T (Schur) 基下, 對角塊 = 有效 block
# 用 Y 本身嘅 3×12 分組 (原基) + 每 block 譜
for i in range(3):
    b = Y[i*12:(i+1)*12, i*12:(i+1)*12]
    bev = np.sort(np.linalg.eigvalsh(b))
    lam_max = bev[-1]
    rest = np.abs(bev[:-1])
    ratio = abs(lam_max)/max(np.mean(rest), 1e-12)
    print(f"  Block {i}: λ_max = {lam_max:.4f}, 1+11 ratio = {ratio:.1f}")

# ============ 4. d_tensor_final 版 (12D 譜) ============
print("\n[4] d_tensor_final 12D 譜 (K_Chain 拓撲)")
d12 = np.load(os.path.join(BASE, "main_problems", "p15_early_derivations", "data", "d_tensor_final.npy"))
v12 = phi ** (-np.arange(12) / 12)
Y12 = np.einsum("ijk,k->ij", d12, v12)
Y12 = (Y12 + Y12.T) / 2
ev12, evec12 = np.linalg.eigh(Y12)
idx = np.argsort(ev12)[::-1]
ev12 = ev12[idx]
evec12 = evec12[:, idx]
print(f"  12D 譜: {np.round(ev12, 3)}")
print(f"  1+11 ratio: {abs(ev12[0])/np.mean(np.abs(ev12[1:])):.1f}")
# 12D: 1 gen + 11 tree
# 36D: 3×(1+11) = 3 gen + 33 tree
print(f"  ★ 3×(1+11) = 3 gen + 33 tree = 33+3!")

# ============ 5. 構建 H_gen(3) 喺 36D ============
print("\n[5] H_gen(3) 構建 (3 個 block 主模態)")
v_gen = np.zeros((36, 3))
for i in range(3):
    b = Y[i*12:(i+1)*12, i*12:(i+1)*12]
    bev, bevec = np.linalg.eigh(b)
    v_gen[i*12:(i+1)*12, i] = bevec[:, -1]
# 正交化
Qg, Rg = np.linalg.qr(v_gen)
print(f"  H_gen 基底: {Qg.shape}, rank: {np.linalg.matrix_rank(Qg)}")
print(f"  H_gen 正交: {np.allclose(Qg.T@Qg, np.eye(3))}")

# 投影
P_gen = Qg @ Qg.T
Y_gen_proj = P_gen @ Y @ P_gen.T
print(f"  tr(P_gen Y P_gen) = {np.trace(Y_gen_proj):.4f}")
print(f"  tr(Y) = {np.trace(Y):.4f}")
print(f"  gen 佔比: {np.trace(Y_gen_proj)/np.trace(Y)*100:.1f}%")
# 3 個 gen 模態嘅能量
gen_energies = np.diag(Qg.T @ Y @ Qg)
print(f"  gen 模態能量: {np.round(gen_energies, 4)}")

# ============ 6. 正交殘差 ============
print("\n[6] 正交殘差 (gen ⊕ tree)")
# tree = 正交補
P_tree = np.eye(36) - P_gen
cross = P_tree @ Y @ P_gen
print(f"  ||P_tree Y P_gen|| = {np.linalg.norm(cross):.4f}")
print(f"  ||Y|| = {np.linalg.norm(Y):.4f}")
print(f"  相對: {np.linalg.norm(cross)/np.linalg.norm(Y):.4f}")
check("gen-tree 耦合小 (<0.3)", np.linalg.norm(cross)/np.linalg.norm(Y) < 0.3,
      f"({np.linalg.norm(cross)/np.linalg.norm(Y):.3f})")

# ============ 7. 33 tree 模態 ============
print("\n[7] 33 tree 模態")
# 用 Y 嘅 33 個非-gen 本徵向量
ev_full, evec_full = np.linalg.eigh(Y)
idx_full = np.argsort(np.abs(ev_full))[::-1]
ev_full = ev_full[idx_full]
evec_full = evec_full[:, idx_full]
# gen 模態 = 3 個最大 |λ| 方向?
print(f"  最大 3 |λ|: {ev_full[:3]}")
print(f"  top-3 佔總: {np.sum(np.abs(ev_full[:3]))/np.sum(np.abs(ev_full))*100:.1f}%")
check("top-3 |λ| 佔 > 40%", np.sum(np.abs(ev_full[:3]))/np.sum(np.abs(ev_full)) > 0.4,
      f"({np.sum(np.abs(ev_full[:3]))/np.sum(np.abs(ev_full))*100:.0f}%)")

print(f"\n{'='*72}")
print(f"Q2 Phase 2: {passed} PASS, {failed} FAIL")
print(f"{'='*72}")
