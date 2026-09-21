#!/usr/bin/env python3
"""
O57 十四期 80: 66 態真 Q_ij = C_i·D_j 相交矩陣 (CYTools)
==========================================================
Gemini 方向 1 (scripts/68 用 γ-weighted 近似):
  真 Q_ij = curve C_i 同 divisor D_j 嘅相交數

CYTools: curve volumes 係 Kähler 參數嘅線性函數
  V_i(t) = Σ_j Q_ij t_j → Q_ij = ∂V_i/∂t_j
  → 數值微分攞 Q_ij (117 curves × 32 divisors)

分析:
  1. Q_ij 矩陣結構
  2. 本徵值 → 零本徵值 = gauge singlet?
  3. 66 態對應 (36K + 30C)
  4. 3 代階梯 (用真 Q 唔係 γ 近似)
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 十四期 80: 真 Q_ij 相交矩陣")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

# ============ 1. 建立 CY ============
print("\n[1] 建立 CY")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()
print(f"  divisor basis: {len(basis)}")
print(f"  curves: {len(cy.curve_basis())}")

# ============ 2. Q_ij 數值微分 ============
print("\n[2] Q_ij = ∂V_i/∂t_j (數值微分)")
# 喺 t = φ^(-i) 附近 (全部 positive 區域)
t0 = phi ** (-np.arange(36))
t32_0 = np.array([t0[b-1] for b in basis])
cv0 = np.array(cy.compute_curve_volumes(t32_0))
n_curves = len(cv0)

# 數值微分: 中心差分
eps = 1e-5
Q = np.zeros((n_curves, len(basis)))
for j in range(len(basis)):
    t_plus = t32_0.copy()
    t_minus = t32_0.copy()
    t_plus[j] += eps
    t_minus[j] -= eps
    cv_plus = np.array(cy.compute_curve_volumes(t_plus))
    cv_minus = np.array(cy.compute_curve_volumes(t_minus))
    Q[:, j] = (cv_plus - cv_minus) / (2*eps)

print(f"  Q shape: {Q.shape}")
print(f"  Q range: [{Q.min():.3f}, {Q.max():.3f}]")
print(f"  Q 非零: {np.sum(np.abs(Q) > 1e-8)}/{Q.size}")

# ============ 3. 本徵分析 ============
print("\n[3] Q 本徵分析")
# Q 唔係方陣 (117×32), 用 SVD
U, S, Vt = np.linalg.svd(Q, full_matrices=False)
print(f"  SVD 奇異值 (top 10): {S[:10]}")
print(f"  rank: {np.sum(S > 1e-8)}/{min(Q.shape)}")

# 零奇異值 = 零模式?
n_zero = np.sum(S < 1e-6)
print(f"  零奇異值: {n_zero}")
check("有零模式 (gauge singlet 線索)", n_zero > 0, f"({n_zero})")

# ============ 4. Q 嘅行空間 ============
print("\n[4] Q 行空間 (divisor 空間)")
# Q^T Q (32×32): divisor 之間嘅相關
QtQ = Q.T @ Q
eigvals, eigvecs = np.linalg.eigh(QtQ)
print(f"  Q^TQ 本徵值 (top 8): {eigvals[::-1][:8]}")
n_pos = np.sum(eigvals > 1e-8)
print(f"  非零本徵值: {n_pos}/32")
check("Q 行空間維度", n_pos > 0, f"({n_pos})")

# ============ 5. 66 態對應 ============
print("\n[5] 66 態對應 (用 Q 行空間)")
# 66 態 = 36K + 30C, Q 行空間 = curve 相關 divisor 組合
# 用 P_fixed_v2.npy 提取 66 態
pf = os.path.join(BASE, "open_problems_fresh", "o57_cy3_projection_gen", "P_fixed_v2.npy")
if os.path.exists(pf):
    P = np.load(pf)
    print(f"  P: {P.shape}")
    # 66 態 = 36K + 30C (之前定義)
    # Q 行空間 (32-dim) 對應 divisor basis
    # 投影 66 態到 Q 行空間?
    # 66 態喺 134-dim, Q 喺 32-dim divisor — 唔可以直接乘
    print(f"  ⚠️ 66 態 (134-dim) 同 Q (32-dim divisor) 維度唔同")
    print(f"  → 需要 curve ↔ 態對應 (O61: sector-dependent 幾何)")
else:
    print(f"  P_fixed_v2.npy 唔存在")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("十四期 80 總結:")
print("=" * 72)
print(f"""
  真 Q_ij 相交矩陣:
  ─────────────────────────────────
  1. Q shape: {Q.shape} (117 curves × 32 divisors)
  2. rank: {np.sum(S > 1e-8)}/{min(Q.shape)}
  3. 零奇異值: {n_zero}

  {'✅ Q_ij 有零模式!' if n_zero > 0 else '❌ 冇零模式'}
  {'✅ Q 行空間非平凡!' if n_pos > 0 else '❌'}

  誠實: 66 態 (134-dim) 同 Q (32-dim divisor) 維度唔同
  → curve ↔ 態對應需要 sector-dependent 幾何 (O61)
""")

results = {
    "test": "O57 十四期 80: 真 Q_ij",
    "Q_shape": list(Q.shape),
    "rank": int(np.sum(S > 1e-8)),
    "n_zero": int(n_zero),
    "svd_top10": [float(s) for s in S[:10]],
    "QtQ_eig_top8": [float(e) for e in eigvals[::-1][:8]],
    "passed": passed, "failed": failed
}
with open("data/80_q_matrix.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十四期 80 完成!")
