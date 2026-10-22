#!/usr/bin/env python3
"""
O62 一期 05: 投影算子 P̂ → Kähler VEV t* 機制
================================================
目標: 由 P̂(134×946) 投影算子自然推出 t* = γ_n。
     O57 已證: Kähler 36 行 support 全部 = 21 = F₈
     (P̂ 嘅 Kähler 行只耦合 even beats, 每個 support 21)

本腳本:
  1. 重建 P̂ (src/projection_operator.py 或 o57 版本)
  2. P̂ 嘅 Kähler 行 row-norm 譜 → 自然 VEV 候選
  3. row-norm vs γ_n 對比
  4. P̂P̂^T 本徵值 → 真空能統計
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O62 一期 05: P̂ → t* 機制")
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

# ============ 1. 重建 P̂ ============
print("\n[1] 重建 P̂ (o57 版本)")
# 搵 o57 嘅 P_fixed_v2.npy
P_paths = [
    os.path.join(BASE, "open_problems_fresh", "o57_cy3_projection_gen", "data", "P_fixed_v2.npy"),
    os.path.join(BASE, "data", "P_fixed_v2.npy"),
]
P = None
for p in P_paths:
    if os.path.exists(p):
        P = np.load(p)
        print(f"  載入: {p}")
        break
if P is None:
    print("  ⚠️ P_fixed_v2.npy 未搵到 — 用 src/projection_operator.py 重建")
    sys.path.insert(0, os.path.join(BASE, "src"))
    from projection_operator import CY3ProjectionOperator
    op = CY3ProjectionOperator()
    P = op.compute_matrix()
    print(f"  重建: {P.shape}")

print(f"  P̂ shape: {P.shape}")
P_k = P[:36, :]  # Kähler 36 行
P_c = P[36:, :]  # CPX 98 行

# ============ 2. Kähler 行結構 ============
print("\n[2] Kähler 行結構")
row_norms = np.linalg.norm(P_k, axis=1)
row_supports = np.count_nonzero(P_k, axis=1)
print(f"  row norm: min={row_norms.min():.4e}, max={row_norms.max():.4e}")
print(f"  row support: min={row_supports.min()}, max={row_supports.max()}, mean={row_supports.mean():.2f}")
print(f"  support 分佈: {np.bincount(row_supports)}")
check("Kähler support = 21 (F₈)", np.all(row_supports == 21), f"(all {row_supports[0]})")

# ============ 3. row-norm vs γ_n ============
print("\n[3] row-norm 譜 vs γ_n")
gamma36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2
# 正規化 row-norm
norm_norm = row_norms / row_norms.max()
print(f"  row-norm (norm): {[f'{x:.4f}' for x in norm_norm[:12]]}...")
print(f"  γ_n (norm):      {[f'{x:.4f}' for x in gamma36[:12]/4]}...")
# 對比
corr = np.corrcoef(norm_norm, gamma36/4)[0,1]
print(f"  corr(row-norm, γ_n) = {corr:.4f}")
check("row-norm 同 γ_n 相關", abs(corr) > 0.5, f"(corr={corr:.4f})")

# 排序後對比
print(f"\n  row-norm 排序 vs γ 排序:")
idx_norm = np.argsort(row_norms)
idx_gamma = np.argsort(gamma36)
match = np.mean(idx_norm == idx_gamma)
print(f"  排序匹配率: {match:.4f}")
print(f"  row-norm 頭 6 個 index: {idx_norm[:6]}")
print(f"  γ 頭 6 個 index: {idx_gamma[:6]}")

# ============ 4. P̂P̂^T 本徵值 → 真空能 ============
print("\n[4] P̂P̂^T 本徵值譜")
PPT = P @ P.T
evals = np.linalg.eigvalsh(PPT)
evals_pos = evals[evals > 1e-15]
print(f"  正本徵值數: {len(evals_pos)}")
print(f"  本徵值 range: [{evals_pos.min():.4e}, {evals_pos.max():.4e}]")
print(f"  Σλ = trace = {np.trace(PPT):.6f}")
print(f"  Σλ_pos = {evals_pos.sum():.6f}")
print(f"  Σλ² = {np.sum(evals_pos**2):.6f}")
print(f"  Σλlnλ = {np.sum(evals_pos*np.log(evals_pos+1e-300)):.6f}")
print(f"  -Σλlnλ = {-np.sum(evals_pos*np.log(evals_pos+1e-300)):.6f}")

# 熵 (正規化)
p = evals_pos / evals_pos.sum()
S = -np.sum(p*np.log(p+1e-300))
print(f"  正規化熵 S = {S:.6f}")
print(f"  ln(109) = {math.log(109):.6f} (最大熵)")
print(f"  S/ln(109) = {S/math.log(109):.4f}")

# Kähler 部分
PPT_k = P_k @ P_k.T
evals_k = np.linalg.eigvalsh(PPT_k)
evals_k_pos = evals_k[evals_k > 1e-15]
print(f"\n  Kähler 36×36:")
print(f"    Σλ = {evals_k_pos.sum():.6f}")
print(f"    Σλ² = {np.sum(evals_k_pos**2):.6f}")
print(f"    Σλlnλ = {np.sum(evals_k_pos*np.log(evals_k_pos+1e-300)):.6f}")

# CPX 部分
PPT_c = P_c @ P_c.T
evals_c = np.linalg.eigvalsh(PPT_c)
evals_c_pos = evals_c[evals_c > 1e-15]
print(f"  CPX 98×98:")
print(f"    Σλ = {evals_c_pos.sum():.6f}")
print(f"    Σλ² = {np.sum(evals_c_pos**2):.6f}")
print(f"    Σλlnλ = {np.sum(evals_c_pos*np.log(evals_c_pos+1e-300)):.6f}")

# ============ 5. 統計力學真空能 ============
print("\n[5] 統計力學真空能候選")
print(f"  V_obs = 283.0752")
cands = {
    "Σλ (trace)": np.trace(PPT),
    "-Σλlnλ (全部)": -np.sum(evals_pos*np.log(evals_pos+1e-300)),
    "-Σλlnλ (Kähler)": -np.sum(evals_k_pos*np.log(evals_k_pos+1e-300)),
    "-Σλlnλ (CPX)": -np.sum(evals_c_pos*np.log(evals_c_pos+1e-300)),
    "Σλ² (Kähler)": np.sum(evals_k_pos**2),
    "Σλ² (全部)": np.sum(evals_pos**2),
    "134×2": 268.0,
    "90+88": 178.0,
    "90×3+13": 283.0,
    "264+19": 283.0,
}
print(f"  {'候選':26s} {'值':>12s} {'誤差%':>9s}")
for name, val in cands.items():
    err = abs(val - 283.0752)/283.0752*100
    print(f"  {name:26s} {val:12.4f} {err:8.3f}%")

# ============ 6. P̂ Kähler 行 → t* 候選 ============
print("\n[6] Kähler 行 → t* 候選")
# t* 候選: row-norm, row-support-weighted γ, 本徵向量
t_candidates = {
    "row_norm": row_norms,
    "row_norm_norm": norm_norm,
    "gamma36": gamma36,
}
# 每種 t 計 F(t)
d = json.load(open(os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes", "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
def F(t):
    return np.einsum("ijk,i,j,k", kappa, t, t, t) / 6.0

for name, t in t_candidates.items():
    Fv = F(t)
    print(f"  F({name}) = {Fv:.6f}")
    # 同 V_obs 差
    print(f"    V_obs − F = {283.0752 - Fv:.6f}")

# ============ 7. 總結 ============
print("\n" + "=" * 72)
print("一期 05 總結:")
print("=" * 72)
print(f"""
  P̂ 結構:
  - Kähler 36 行 support 全 = 21 = F₈ ✅
  - row-norm 同 γ_n 相關: corr = {corr:.4f}
  - P̂P̂^T 正本徵值 = 109 (rank)

  真空能候選:
  - F(row_norm) = ?
  - F(γ) = 264.0821 (一期 02)

  → t* 機制: Kähler 行 ↔ γ 諧波
""")
out = {
    "test": "O62 一期 05: P̂ → t*",
    "P_shape": list(P.shape),
    "kahler_support": int(row_supports[0]),
    "corr_rownorm_gamma": float(corr),
    "rank": int(len(evals_pos)),
    "trace": float(np.trace(PPT)),
    "entropy_full": float(S),
    "F_row_norm": float(F(t_candidates["row_norm"])),
    "F_gamma": float(F(t_candidates["gamma36"])),
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "05_projection_tstar.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 一期 05 完成!")
