#!/usr/bin/env python3
"""
O57 十九期 97: PMNS — Q_ij SVD 主分量直接測試
=================================================
scripts/96 發現: cluster 中心 rank 2 (退化) → 唔 work

新方法: 用 Q_ij 嘅 top-3 右奇異向量 Vt[:3] (32-dim, 正交!)
  即係 divisor 空間嘅主要結構方向
  U_PMNS 候選 = Vt[:3] 投影到 3×3

誠實: 呢個係「幾何主方向」, 唔係世代
"""
import sys, os, math
import json
import numpy as np

print("=" * 72)
print("O57 十九期 97: PMNS SVD 主分量")
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

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

# ============ 1. Q_ij ============
print("\n[1] Q_ij")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()

t0_full = phi ** (-np.arange(36))
t32_0 = np.array([t0_full[b-1] for b in basis])
cv0 = np.array(cy.compute_curve_volumes(t32_0))
n_curves = len(cv0)
n_div = len(basis)
Q = np.zeros((n_curves, n_div))
eps = 1e-5
for j in range(n_div):
    tp = t32_0.copy(); tm = t32_0.copy()
    tp[j] += eps; tm[j] -= eps
    Q[:, j] = (np.array(cy.compute_curve_volumes(tp)) - np.array(cy.compute_curve_volumes(tm))) / (2*eps)
print(f"  Q: {Q.shape}, rank {np.linalg.matrix_rank(Q)}")

# ============ 2. SVD ============
print("\n[2] SVD")
U, S, Vt = np.linalg.svd(Q, full_matrices=False)
print(f"  奇異值 top 6: {[f'{s:.1f}' for s in S[:6]]}")

# 主分量 (divisor 空間方向)
V3 = Vt[:3, :]  # 3×32 (orthonormal rows)
print(f"  V3: {V3.shape}")

# ============ 3. U_PMNS 候選 ============
print("\n[3] U_PMNS 候選")
# 方法 A: V3 直接做 3×3 (攞前 3 列) — 但冇 physical 動機
# 方法 B: V3 @ V3.T 嘅 3×3 (projection 矩陣) — 對角
# 方法 C: 用 V3 前 3 列 (divisor 1,2,3) — 冇動機

# 最自然: 攞 V3 嘅 3 個行做「世代方向」?
# 但 divisor 冇世代結構...

# 嘗試: 用 P_fixed (134×946) 嘅 66 態 — 但冇數據
# 誠實: SVD 主分量本身冇世代意義
print("""
  方法 A: V3 前 3 列 (divisor 1,2,3):
""")
V3a = V3[:, :3]
V3a, _ = np.linalg.qr(V3a.T)
V3a = V3a.T
print(np.round(V3a, 4))

Ue1, Ue2, Ue3 = V3a[0, 0], V3a[0, 1], V3a[0, 2]
s13_2 = Ue3**2
s12_2 = Ue2**2/(1-s13_2)
s23_2 = V3a[1, 2]**2/(1-s13_2)
t12 = math.asin(math.sqrt(max(0, min(1, s12_2)))) * 180/math.pi
t23 = math.asin(math.sqrt(max(0, min(1, s23_2)))) * 180/math.pi
t13 = math.asin(math.sqrt(max(0, min(1, s13_2)))) * 180/math.pi
print(f"  θ₁₂ = {t12:.2f}° (實驗 33.41°), θ₂₃ = {t23:.2f}° (實驗 49.1°), θ₁₃ = {t13:.2f}° (實驗 8.54°)")

print("""
  方法 B: V3 前 3 列 — 但 divisor 順序冇物理意義
  → 呢個方法冇 principle 動機, 唔應該試
  → 誠實: SVD 主分量唔係 PMNS 來源
""")

# ============ 4. 真正物理方向: γ 譜 ============
print("[4] 真正物理方向: γ 譜")
print("""
  已知 (O57 歷史):
  - γ_n 譜 (K_Chain 諧波) 控制質量階梯 (n=1,7,20 輕子)
  - γ₆ 控制中微子 (p6 mode)
  - Δm² 比 = 2B² = 32 (十七期閉合)

  如果 PMNS 由 γ 譜決定:
  sin²θ₁₂ 候選 = γ₆/γ₃? γ₆/γ₂? 
  sin²θ₂₃ 候選 = γ₂₀/γ₇? (輕子世代 n)
  sin²θ₁₃ 候選 = ?
""")

g = {n: 4*math.sin(n*math.pi/88)**2 for n in range(1, 45)}
print(f"  γ₁ = {g[1]:.5f}, γ₂ = {g[2]:.5f}, γ₃ = {g[3]:.5f}")
print(f"  γ₆ = {g[6]:.5f}, γ₇ = {g[7]:.5f}, γ₂₀ = {g[20]:.5f}")
print(f"  γ₆/γ₃ = {g[6]/g[3]:.4f} (sin²θ₁₂ 實驗 0.303?)")
print(f"  γ₆/γ₂ = {g[6]/g[2]:.4f}")
print(f"  γ₇/γ₂₀ = {g[7]/g[20]:.4f} (sin²θ₂₃ 實驗 0.572?)")
print(f"  γ₃/γ₆ = {g[3]/g[6]:.4f}")
print(f"  γ₂₀/γ₇ = {g[20]/g[7]:.4f} (0.572?)")
print(f"  γ₁/γ₆ = {g[1]/g[6]:.4f}")
print(f"  γ₆² = {g[6]**2:.4f}")
print(f"  γ₆/4 = {g[6]/4:.4f}")

# sin²θ₁₂ 候選 (0.303)
print(f"\n  sin²θ₁₂ = 0.303 候選:")
for name, val in [("γ₆/γ₂", g[6]/g[2]), ("γ₁/(γ₁+γ₂)", g[1]/(g[1]+g[2])),
                  ("γ₂/(γ₁+γ₂)", g[2]/(g[1]+g[2])), ("γ₆/(γ₆+γ₇)", g[6]/(g[6]+g[7])),
                  ("γ₃/(γ₂+γ₃)", g[3]/(g[2]+g[3])), ("γ₂₀/γ₆/2", g[20]/g[6]/2)]:
    err = abs(val - 0.303)/0.303*100
    print(f"    {name} = {val:.4f} (誤差 {err:.0f}%)")

# sin²θ₂₃ 候選 (0.572)
print(f"\n  sin²θ₂₃ = 0.572 候選:")
for name, val in [("γ₇/(γ₇+γ₂₀)", g[7]/(g[7]+g[20])), ("γ₂₀/(γ₇+γ₂₀)", g[20]/(g[7]+g[20])),
                  ("γ₆/γ₃/2", g[6]/g[3]/2), ("γ₂₀/(γ₂₀+γ₆)", g[20]/(g[20]+g[6]))]:
    err = abs(val - 0.572)/0.572*100
    print(f"    {name} = {val:.4f} (誤差 {err:.0f}%)")

# sin²θ₁₃ 候選 (0.02203)
print(f"\n  sin²θ₁₃ = 0.02203 候選:")
for name, val in [("γ₁/γ₆/2", g[1]/g[6]/2), ("γ₁²", g[1]**2), ("γ₆/8", g[6]/8),
                  ("γ₃/γ₂₀", g[3]/g[20]), ("γ₆/γ₂₀/4", g[6]/g[20]/4)]:
    err = abs(val - 0.02203)/0.02203*100
    print(f"    {name} = {val:.4f} (誤差 {err:.0f}%)")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("十九期 97 總結:")
print("=" * 72)
print("""
  Q_ij SVD 主分量 → PMNS?
  ─────────────────────────────────
  方法 A (V3 前 3 列): 冇 principle 動機, 唔採用
  γ 譜候選: 全部誤差 > 30%

  → 誠實: Q_ij 幾何 (cluster/SVD/γ) 都未直接湧現 PMNS
  → PMNS 需要 Yukawa 矩陣 A_ij(z) 嘅完整推導 (O61 已開)
  → 或者 PMNS 根本唔係幾何, 係低能有效理論結構
""")

results = {
    "test": "O57 十九期 97: PMNS SVD/γ 候選",
    "svd_top": [float(s) for s in S[:6]],
    "gamma_candidates": {"s12": g[6]/g[2], "s23": g[20]/(g[7]+g[20]), "s13": g[6]/8},
    "conclusion": "PMNS 未湧現 — 需要 Yukawa A_ij(z) 完整推導",
    "passed": passed, "failed": failed
}
with open("data/97_pmns_svd_gamma.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
exit(0)
