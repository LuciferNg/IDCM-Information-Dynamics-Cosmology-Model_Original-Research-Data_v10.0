#!/usr/bin/env python3
"""
O53 問題 2 深度驗證: 投影算子 rank-2 結構 vs 66 個「本徵態」
=============================================================
發現: SVD 秩 (tol=1e-12) = 2, 但 P P^T 有 66 個正本徵值 (>1e-15)

懷疑: 66 個「正本徵值」係浮點噪聲, 真正結構只有 2 (Kähler/CPX 兩類)
驗證方法:
  1. 行向量線性相關性 (rank-2 證明)
  2. 本徵值譜 gap 結構 (有冇真正嘅 66 群聚?)
  3. float128 / mpmath 高精度確認
  4. 檢查 P 矩陣嘅 row 結構 (per-modulus 依賴存在?)
"""
import sys, os, math
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))
from projection_operator import CY3ProjectionOperator

print("=" * 70)
print("O53 Q2: 投影算子 rank 真相調查")
print("=" * 70)

op = CY3ProjectionOperator()
P = op.compute_matrix()
print(f"\nP 形狀: {P.shape}  ({op.n_moduli} moduli × {op.n_beats} beats)")

# --- [1] 行向量結構: 每個 modulus 行有冇獨立權重? ---
print("\n[1] 行結構分析 — 每行係咪只由 (type, beat) 決定?")
# 如果 P[α,β] = f(type(α), β) 而唔依賴 α 具體 index → rank ≤ 2
kahler_rows = P[:36, :]
cpx_rows = P[36:, :]

# 檢查 Kähler 行之間嘅比例係咪常數 (即線性相關)
# 隨機抽 3 行, 計 cross-correlation
import itertools
print("    Kähler 行 (36 行) 線性相關性:")
rng = np.random.default_rng(42)
pairs = list(itertools.combinations(range(36), 2))[:5]
for i, j in pairs:
    vi, vj = kahler_rows[i], kahler_rows[j]
    # 只睇非零位置
    mask = (vi != 0) & (vj != 0)
    if mask.sum() > 0:
        ratio = vi[mask] / vj[mask]
        corr = np.corrcoef(vi[mask], vj[mask])[0, 1]
        print(f"      row{i} vs row{j}: corr={corr:.10f}, ratio std={ratio.std():.2e}")

# 全部行對 corr 分佈
print("    Kähler 全部行對 corr 分佈:")
cors = []
for i in range(36):
    for j in range(i+1, 36):
        mask = (kahler_rows[i] != 0) & (kahler_rows[j] != 0)
        if mask.sum() > 0:
            cors.append(np.corrcoef(kahler_rows[i][mask], kahler_rows[j][mask])[0, 1])
cors = np.array(cors)
print(f"      min={cors.min():.6f}, max={cors.max():.6f}, mean={cors.mean():.6f}")
print(f"      |corr| > 0.9999 比例: {np.mean(np.abs(cors) > 0.9999)*100:.1f}%")

print("\n    CPX 行 (98 行) 線性相關性:")
cors_c = []
for i in range(98):
    for j in range(i+1, 98):
        mask = (cpx_rows[i] != 0) & (cpx_rows[j] != 0)
        if mask.sum() > 0:
            cors_c.append(np.corrcoef(cpx_rows[i][mask], cpx_rows[j][mask])[0, 1])
cors_c = np.array(cors_c)
print(f"      min={cors_c.min():.6f}, max={cors_c.max():.6f}, mean={cors_c.mean():.6f}")
print(f"      |corr| > 0.9999 比例: {np.mean(np.abs(cors_c) > 0.9999)*100:.1f}%")

# --- [2] 本徵值譜 gap 分析 ---
print("\n[2] P P^T 本徵值譜")
PPT = P @ P.T
evals, evecs = np.linalg.eigh(PPT)
evals_sorted = np.sort(evals)[::-1]
print(f"    最大本徵值: {evals_sorted[0]:.6e}")
print(f"    第二大: {evals_sorted[1]:.6e}")
print(f"    第三大: {evals_sorted[2]:.6e}")
print(f"    最大 10 個:")
for i in range(10):
    print(f"      λ_{i+1:2d} = {evals_sorted[i]:.6e}")
# gap 分析
print(f"\n    前 20 個本徵值之間嘅相對 gap:")
for i in range(19):
    g = (evals_sorted[i] - evals_sorted[i+1]) / evals_sorted[i]
    print(f"      gap {i+1}→{i+2}: {g:.6f}")

# 睇有幾多本徵值 > 1e-10 (真正物理譜?)
print(f"\n    > 1e-10: {np.sum(evals_sorted > 1e-10)}")
print(f"    > 1e-8:  {np.sum(evals_sorted > 1e-8)}")
print(f"    > 1e-6:  {np.sum(evals_sorted > 1e-6)}")
print(f"    > 1e-4:  {np.sum(evals_sorted > 1e-4)}")
print(f"    > 1e-2:  {np.sum(evals_sorted > 1e-2)}")
print(f"    > 1:     {np.sum(evals_sorted > 1)}")

# --- [3] 秩嘅嚴格確定 (多個 tol) ---
print("\n[3] 秩 vs tol:")
for tol in [1e-6, 1e-8, 1e-10, 1e-12, 1e-14]:
    r = np.linalg.matrix_rank(P, tol=tol)
    print(f"    tol={tol:.0e}: rank = {r}")

# --- [4] 行空間基: P 嘅行係咪只由 2 個向量張成? ---
print("\n[4] 行空間基分析 (SVD)")
u, s, vh = np.linalg.svd(P, full_matrices=False)
print(f"    奇異值: {s[:6]}")
s_rel = s / s[0]
print(f"    相對奇異值: {s_rel[:6]}")
print(f"    σ₂/σ₁ = {s_rel[1]:.6e}")

# --- [5] 66 個正本徵值嘅「物理內容」--- 
print("\n[5] 66 個「正本徵值」係咪真物理譜?")
# 睇佢哋嘅本徵向量: 如果佢哋係噪聲, 本徵向量應該冇結構
n_pos = np.sum(evals > 1e-15)
print(f"    正本徵值數: {n_pos}")
# 本徵值分布直方圖 (log scale)
log_evals = np.log10(evals[evals > 0])
print(f"    log10 本徵值範圍: {log_evals.min():.2f} ~ {log_evals.max():.2f}")
hist, edges = np.histogram(log_evals, bins=15)
print(f"    直方圖 (log10 bins):")
for h, e1, e2 in zip(hist, edges[:-1], edges[1:]):
    bar = "#" * min(h, 40)
    print(f"      [{e1:8.2f}, {e2:8.2f}): {h:3d} {bar}")

# --- [6] 關鍵: 呢個發現嘅意義 ---
print("\n" + "=" * 70)
print("【初步判定】")
print("=" * 70)
print(f"""
  1. P 嘅列 (moduli) 只分 Kähler/CPX 兩類, 每類內部行向量
     幾乎完全相同 (corr ~ 1.0) → 真正秩 = 2
  2. 66 個「正本徵值」> 1e-15 但絕大多數 ~1e-15 級
     → 係 float64 捨入噪聲, 唔係物理譜
  3. 即係話現有 projection_operator.py:
     「66 個本徵態 → 3 代 × 22 態」嘅聲稱
     = 數值幻覺 (numerical artifact)
  4. 根本原因: 選擇律 weight 只依賴 (type, beat),
     冇 per-modulus 依賴 → 所有 Kähler 行相同
""")
print("=" * 70)
