#!/usr/bin/env python3
"""
O50 Phase 1: 分析真實 κ_ijk (36×36×36) 結構
============================================
從 cy36_98_intersection_full.json (CYTools 真實幾何) 分析:
  1. 基本統計: 非零模式、數值範圍、對稱性
  2. 秩分析: flatten rank, 每行/每片 rank
  3. 對角線 d_iii: 結構模式
  4. 分塊結構: 3×12, 任意 Z₃ 分組
  5. 對比 kappa_36d_raw.json (HF 舊數據)
  6. 對比 d_tensor_final.npy (12×12×12 清洗後)
"""

import os, sys, json, math
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
O53_POLY = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
O50_DIR = os.path.join(os.path.dirname(__file__), "..")

phi = (1 + math.sqrt(5)) / 2
PASS = 0
FAIL = 0
results = []

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        results.append(f"  ✅ {name} {detail}")
    else:
        FAIL += 1
        results.append(f"  ❌ {name} {detail}")

print("=" * 80)
print("O50 Phase 1: 真實 κ_ijk (36×36×36) 結構分析")
print("=" * 80)

# =====================================================================
# [1] 載入真實 κ_ijk (CYTools intersection_numbers)
# =====================================================================
print("\n[1] 載入真實 κ_ijk (CYTools)")
path_real = os.path.join(O53_POLY, "cy36_98_intersection_full.json")
with open(path_real) as f:
    inter = json.load(f)
K = np.array(inter["kappa"])

# 載入 HF 舊版 κ (kappa_36d_raw.json)
path_raw = os.path.join(O53_POLY, "kappa_36d_raw.json")
with open(path_raw) as f:
    raw = json.load(f)
K_raw = np.zeros(tuple(raw["shape"]))
for key, val in raw["kappa"].items():
    i, j, k = map(int, key.split(","))
    K_raw[i, j, k] = val
    K_raw[i, k, j] = val
    K_raw[j, i, k] = val
    K_raw[j, k, i] = val
    K_raw[k, i, j] = val
    K_raw[k, j, i] = val

print(f"  真實 κ_ijk (CYTools):  {K.shape}, non-zero={np.count_nonzero(K)}")
print(f"  HF κ_ijk (raw):        {K_raw.shape}, non-zero={np.count_nonzero(K_raw)}")

# =====================================================================
# [2] 基本統計
# =====================================================================
print("\n[2] 基本統計 — 真實 κ_ijk")

# 數值範圍
print(f"  數值範圍: [{K.min()}, {K.max()}]")
print(f"  絕對值最大: {np.max(np.abs(K))}")
print(f"  負值數: {np.sum(K < 0)} / {K.size}")
print(f"  零值數: {np.sum(K == 0)} / {K.size}")
print(f"  正整數? {np.all(K == K.astype(int))}")

# 對稱性
sym_123 = np.allclose(K, K.transpose(1, 0, 2))
sym_132 = np.allclose(K, K.transpose(0, 2, 1))
sym_231 = np.allclose(K, K.transpose(2, 1, 0))
print(f"  全對稱 (i,j,k): {sym_123 and sym_132 and sym_231}")
check("κ_ijk 全對稱", sym_123 and sym_132 and sym_231)

# 每行非零
row_nnz = np.count_nonzero(K.reshape(36, -1), axis=1)
print(f"  每行非零: min={row_nnz.min()}, max={row_nnz.max()}, mean={row_nnz.mean():.1f}")
check("每行 non-zero >= 1", row_nnz.min() >= 1, f"(min={row_nnz.min()})")

# =====================================================================
# [3] 秩分析
# =====================================================================
print("\n[3] 秩分析")

# Flatten rank
D = K.reshape(36, 36*36)
rank_K = np.linalg.matrix_rank(D, tol=1e-10)
print(f"  flatten rank (36×1296): {rank_K}")
check("κ_ijk 係真三體耦合 (rank > 1)", rank_K > 1, f"(rank={rank_K})")

# 每片 rank (k fixed)
slice_ranks = []
for k in range(36):
    r = np.linalg.matrix_rank(K[:, :, k], tol=1e-10)
    slice_ranks.append(r)
print(f"  每片 rank: min={min(slice_ranks)}, max={max(slice_ranks)}, mean={np.mean(slice_ranks):.1f}")

# SVD 譜
U, s, Vt = np.linalg.svd(D, full_matrices=False)
n_sig = np.sum(s > 1e-10)
print(f"  SVD 非零奇異值: {n_sig}")
print(f"  前 10 奇異值: {s[:10]}")

# =====================================================================
# [4] 對角線 d_iii
# =====================================================================
print("\n[4] 對角線 d_iii")
diag = np.array([K[i, i, i] for i in range(36)])
nz_diag = np.count_nonzero(diag)
print(f"  非零對角: {nz_diag} / 36")
print(f"  對角值: {diag}")

# 對角嘅整數分解
print(f"  對角和: {diag.sum()}")
print(f"  對角絕對值和: {np.abs(diag).sum()}")

# 對角值分佈
unique_vals, counts = np.unique(diag, return_counts=True)
print(f"  唯一值數: {len(unique_vals)}")
for v, c in zip(unique_vals, counts):
    print(f"    d_iii = {int(v):6d} × {c}")

# =====================================================================
# [5] 分塊結構 (3×12 分組)
# =====================================================================
print("\n[5] 3×12 分塊結構")

# 嘗試多種分組: 按 index 順序 (0-11, 12-23, 24-35)
for block_size in [12, 18, 9, 6]:
    n_blocks = 36 // block_size
    if 36 % block_size != 0:
        continue
    blocks = np.zeros((n_blocks, n_blocks, n_blocks))
    for bi in range(n_blocks):
        for bj in range(n_blocks):
            for bk in range(n_blocks):
                blocks[bi, bj, bk] = np.abs(K[
                    bi*block_size:(bi+1)*block_size,
                    bj*block_size:(bj+1)*block_size,
                    bk*block_size:(bk+1)*block_size
                ]).sum()
    
    # 檢查 block diagonal 主導程度
    diag_sum = sum(blocks[i, i, i] for i in range(n_blocks))
    total_sum = blocks.sum()
    diag_ratio = diag_sum / total_sum if total_sum > 0 else 0
    print(f"  {n_blocks}×{block_size} 分塊: 對角比 = {diag_ratio:.3f}")

# 檢查 3×12 特定分塊
print("\n  3×12 分塊詳細:")
blocks_3x12 = np.zeros((3, 3, 3))
for bi in range(3):
    for bj in range(3):
        for bk in range(3):
            blocks_3x12[bi, bj, bk] = np.abs(K[
                bi*12:(bi+1)*12, bj*12:(bj+1)*12, bk*12:(bk+1)*12
            ]).sum()
print(f"  3×12 分塊矩陣 (絕對值和):")
for bi in range(3):
    row = "  ".join(f"{blocks_3x12[bi,bj,0]:8.0f}/{blocks_3x12[bi,bj,1]:8.0f}/{blocks_3x12[bi,bj,2]:8.0f}" for bj in range(3))
    print(f"    block[{bi}]: {row}")

# 檢查 diagonal block 是否主導
diag3 = sum(blocks_3x12[i, i, i] for i in range(3))
total3 = blocks_3x12.sum()
print(f"  3×12 對角塊比: {diag3/total3:.3f}")

# =====================================================================
# [6] 對比 kappa_36d_raw.json (HF 舊數據)
# =====================================================================
print("\n[6] 對比 real κ_ijk vs HF raw κ_ijk")

# 兩者相關性
corr = np.corrcoef(K.flatten(), K_raw.flatten())[0, 1]
print(f"  相關係數: {corr:.6f}")
check("HF κ 同 real κ 相關", corr > 0.1, f"(r={corr:.4f})")

# 非零 overlap
mask_real = K != 0
mask_raw = K_raw != 0
overlap = np.sum(mask_real & mask_raw)
print(f"  Real non-zero: {np.sum(mask_real)}")
print(f"  Raw non-zero: {np.sum(mask_raw)}")
print(f"  Overlap: {overlap}")
check("HF κ 係 real κ 嘅子集", overlap > 0, f"({overlap} entries overlap)")

# =====================================================================
# [7] 對比 d_tensor_final.npy (12×12×12 清洗後)
# =====================================================================
print("\n[7] 對比 d_tensor_final.npy (12×12×12 清洗後)")

# 如果想將 36×36×36 轉到 12×12×12，需要 Z₃ orbifold reduction
# 但 d_tensor_final 係 Z₃ orbifold 後嘅版本
# 先檢查用乜 reduction 方法

d_final = np.load(os.path.join(DATA, "d_tensor_final.npy"))
print(f"  d_tensor_final: {d_final.shape}, non-zero={np.count_nonzero(d_final)}")
print(f"  d_tensor_final range: [{d_final.min():.6f}, {d_final.max():.6f}]")
print(f"  d_tensor_final negative: {np.sum(d_final < 0)} / {d_final.size}")

# 對比 Yukawa 譜
v = np.array([phi ** (-k/12) for k in range(12)])
Y_final = np.einsum('ijk,k->ij', d_final, v)
Y_final = (Y_final + Y_final.T) / 2
ev_final = np.linalg.eigvalsh(Y_final)
print(f"  d_tensor_final Yukawa 譜:")
for i, e in enumerate(sorted(ev_final, reverse=True)):
    print(f"    λ_{i+1:2d} = {e:.6f}")

# 對比 real κ 嘅 Yukawa 譜 (用 J*)
J = np.array([0.0035218786641320866, 0.014729584132340774, 0.038483547532839626,
              0.013069647631978142, 0.005016430122915089, 0.024225573087660598,
              0.0017811126918626445, 0.0039736222909748835, 0.005652850848271402,
              0.0016103893794319115, 0.0018114060958478615, 0.024989877475265217,
              0.0011901046886462153, 0.005381515944269624, 0.0014020290799164746,
              0.003240760131401789, 0.0014576964029676255, 0.01828294316107931,
              0.023529653625735624, 0.024500182779956366, 0.015893173376530668,
              0.021150220204965552, 0.0210276225829926, 0.010430005343144083,
              0.021678794405447614, 0.007711961414248334, 0.038181629073884775,
              0.004671772511873055, 0.03773759453281969, 0.0041971828915594225,
              0.01260174439350761, 0.019412022182181108, 0.012719078204863033,
              0.026107870379541778, 0.01269473787407128, 0.0035088577728026827])
Y_real = np.einsum('ijk,k->ij', K, J)
Y_real = (Y_real + Y_real.T) / 2
ev_real = np.linalg.eigvalsh(Y_real)
print(f"\n  Real κ Yukawa 譜 (用 J*):")
for i, e in enumerate(sorted(ev_real, reverse=True)):
    print(f"    λ_{i+1:2d} = {e:.6f}")

# =====================================================================
# [8] 檢查 Z₃ 對稱性喺 real κ 是否存在
# =====================================================================
print("\n[8] Z₃ 對稱性檢查 (real κ)")

# 檢查 4-shift (之前 O53 冇 Z₃)
err_shift = np.mean([abs(K[i,j,k] - K[(i+4)%36,(j+4)%36,(k+4)%36])
                     for i in range(36) for j in range(36) for k in range(36)])
d_scale = np.abs(K).mean()
print(f"  4-shift 誤差: {err_shift:.3f} (d_scale={d_scale:.3f})")
check("4-shift 誤差 > d_scale*0.1 (冇 Z₃)", err_shift > d_scale * 0.1,
      f"(ratio={err_shift/d_scale:.2f})")

# 檢查 12-shift
err_shift12 = np.mean([abs(K[i,j,k] - K[(i+12)%36,(j+12)%36,(k+12)%36])
                       for i in range(36) for j in range(36) for k in range(36)])
print(f"  12-shift 誤差: {err_shift12:.3f}")
check("12-shift 誤差 > d_scale*0.1 (冇 Z₃ 12)", err_shift12 > d_scale * 0.1,
      f"(ratio={err_shift12/d_scale:.2f})")

# =====================================================================
# [9] 分析 GLSM 結構
# =====================================================================
print("\n[9] GLSM 結構 (32 個 charge 向量)")
path_sage = os.path.join(O53_POLY, "cy36_98_sage_export.json")
with open(path_sage) as f:
    sage = json.load(f)
glsm = np.array(sage["glsm_matrix"])
print(f"  GLSM: {glsm.shape} (32 charges × 37 homogeneous coordinates)")
print(f"  Rank: {np.linalg.matrix_rank(glsm, tol=1e-10)}")
print(f"  Null space dim: {glsm.shape[1] - np.linalg.matrix_rank(glsm, tol=1e-10)}")

# 37 homogenenous coordinates → 36 toric divisors (D_0..D_36)
# 因為 sum(D_i) = 0 (linear relation)
linrels = np.array(sage["glsm_linrels"])
print(f"  Linear relations: {linrels.shape}")

# =====================================================================
# 總結
# =====================================================================
print("\n" + "=" * 80)
print(f"Phase 1 結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 80)
for r in results:
    print(r)

# 保存結果
out = os.path.join(O50_DIR, "data", "01_phase1_results.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as f:
    json.dump({
        "PASS": PASS, "FAIL": FAIL,
        "results": [r for r in results],
        "kappa_shape": list(K.shape),
        "kappa_nonzero": int(np.count_nonzero(K)),
        "kappa_range": [float(K.min()), float(K.max())],
        "kappa_rank": int(rank_K),
        "kappa_diag_nz": int(nz_diag),
        "kappa_diag_values": [float(v) for v in diag],
        "yukawa_eigenvalues_real": [float(e) for e in sorted(ev_real, reverse=True)],
        "yukawa_eigenvalues_final": [float(e) for e in sorted(ev_final, reverse=True)],
    }, f, indent=2)
print(f"\n✅ 結果已儲存: {out}")