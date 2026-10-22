#!/usr/bin/env python3
"""
O62 八期 31: 目標二 — GLSM 真空流形 7+29=36
============================================
背景: γ_7 (動態模態) + L_7 (Lucas 拓撲荷 29) = 36 = h¹¹

GLSM: V_D = Σ_a (1/2e_a²) (Σ_i Q_i^a |φ_i|² − ζ^a)² = 0
  → 真空: Σ_i Q_i^a |φ_i|² = ζ^a ∀a

推導:
  1. 理解 glsm_matrix (32×37): 32 個 U(1) × 37 個 field?
  2. Charge matrix 嘅 rank, kernel → 幾何維度
  3. D-term 方程: 解空間 = 真空流形
  4. 7+29=36: 7 個動態方向 + 29 個固定 = 36 Kähler 參數
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 八期 31: GLSM 真空流形")
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

d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
Q = np.array(d["glsm_matrix"], dtype=float)  # 32×37?
print(f"[1] GLSM charge matrix")
print(f"  shape: {Q.shape}")
print(f"  dtype: {Q.dtype}")
# 可能係 32×48 但載入成 32×37? 檢查
# 或者 glsm_matrix 已經 reduced

# 睇原始 sage export 嘅完整結構
print(f"\n  glsm_shape: {d['glsm_shape']}")
print(f"  glsm_linrels: {len(d['glsm_linrels'])}")

# ============ 1. Rank 分析 ============
print("\n[2] Rank 分析")
rank_Q = np.linalg.matrix_rank(Q)
print(f"  rank(Q) = {rank_Q}")
print(f"  Q 形狀: {Q.shape}")
# kernel 維度 = n_cols − rank
if Q.shape[1] > rank_Q:
    print(f"  kernel dim = {Q.shape[1]} − {rank_Q} = {Q.shape[1]-rank_Q}")

# ============ 2. 睇 charge matrix 結構 ============
print("\n[3] Charge matrix 結構")
# 每行 (每個 U(1)) 嘅非零 charge 數
row_nnz = np.count_nonzero(Q, axis=1)
print(f"  每 U(1) 非零 charge 數: {row_nnz.tolist()}")
print(f"  有 charges 嘅 U(1): {np.count_nonzero(row_nnz)}/{Q.shape[0]}")

# 每列 (每個 field) 嘅非零 charge 數
col_nnz = np.count_nonzero(Q, axis=0)
print(f"  每 field 非零 charge 數: {col_nnz.tolist()}")
print(f"  有 charge 嘅 field: {np.count_nonzero(col_nnz)}/{Q.shape[1]}")

# ============ 3. D-term 方程 ============
print("\n[4] D-term 真空方程")
print(f"  V_D = 0 ⇔ Σ_i Q_i^a |φ_i|² = ζ^a (a=1..32)")
print(f"  未知數: |φ_i|² (37 個, 半正定)")
print(f"  方程: 32 個線性方程 (rank {rank_Q})")
n_free = Q.shape[1] - rank_Q
print(f"  自由方向: {n_free}")
check("自由方向 = 7?", n_free == 7, f"({n_free})")

# ============ 4. FI 參數 ζ ============
print("\n[5] FI 參數")
print(f"  ζ^a 有 {Q.shape[0]} 個 (Kähler 參數)")
# Kähler 參數數 = ? h11 = 36
# GLSM: Kähler moduli = dim(Picard) = ?

# ============ 5. 7+29 結構 ============
print("\n[6] 7+29 = 36 探索")
print(f"  h11 = 36 (Kähler 模)")
print(f"  γ_7 mode: n=7 嘅 K_Chain 諧波")
print(f"  L_7 = 29 (Lucas 數)")
# 檢查: GLSM 有冇 natural 7-dim 結構?
# charge matrix 嘅 zero columns? 重複 columns?
col_sum = Q.sum(axis=0)
print(f"  每 field charge 總和: {col_sum.tolist()[:40]}")
# 有冇 field 嘅 charge 全部係 0?
zero_cols = [i for i in range(Q.shape[1]) if col_nnz[i] == 0]
print(f"  零 charge field: {zero_cols}")

# kernel basis?
print("\n[7] 線性關係 (glsm_linrels)")
for i, lr in enumerate(d["glsm_linrels"]):
    print(f"  linrel {i}: len={len(lr)}, 前 10: {lr[:10]}")

# ============ 8. 總結 ============
print("\n" + "=" * 72)
print("八期 31 總結:")
print("=" * 72)
print(f"""
  GLSM 結構:
  charge matrix: {Q.shape} (32 U(1) × 37 field?)
  rank: {rank_Q}
  D-term 自由方向: {n_free}

  {'🎉 自由方向 = 7 = γ_7 動態模態!' if n_free == 7 else '⚠️ 需要更深入分析'}
""")
out = {
    "test": "O62 八期 31: GLSM",
    "Q_shape": list(Q.shape),
    "rank_Q": int(rank_Q),
    "n_free": int(n_free),
    "row_nnz": row_nnz.tolist(),
    "col_nnz": col_nnz.tolist(),
    "zero_cols": zero_cols,
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "31_glsm.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 八期 31 完成!")
