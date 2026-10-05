#!/usr/bin/env python3
"""
O53 Q4 深化: 真實 tr(Y) 用 J* + 66 閉合
==========================================
用真實 κ_ijk + 真實 J* (Kähler 參數):
  Y_ij = κ_ijk · J*^k (volumes of curves)
  tr(Y) = ?

另外驗證:
  - 303 non-zero 係咪同 66/134 有結構關係
  - κ_ijk 嘅對稱 group 結構
  - 12 維子張量 (Z₃ 假設嘅替代)
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name} {detail}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")

print("=" * 70)
print("O53 Q4: 真實 tr(Y) 閉合")
print("=" * 70)

# --- [1] 載入 ---
with open(os.path.join(BASE, "kappa_36d_raw.json")) as f:
    kappa = json.load(f)
with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)

K = np.zeros(tuple(kappa['shape']))
for key, val in kappa['kappa'].items():
    i, j, k = map(int, key.split(','))
    K[i, j, k] = val
    K[i, k, j] = val
    K[j, i, k] = val
    K[j, k, i] = val
    K[k, i, j] = val
    K[k, j, i] = val

J = np.array(jstar['Jstar_36D'])
print(f"\n[1] 載入: K shape={K.shape}, J shape={J.shape}")
print(f"    J 範圍: [{J.min():.6f}, {J.max():.6f}]")
print(f"    J* 總和: {J.sum():.6f}")

# --- [2] 真實 Yukawa ---
print("\n[2] 真實 Yukawa 矩陣 Y_ij = κ_ijk J*^k:")
Y = np.einsum('ijk,k->ij', K, J)
print(f"    Y shape: {Y.shape}")
evals_Y = np.linalg.eigvalsh(Y)
print(f"    本徵值: {np.array2string(evals_Y, precision=6)}")
trY = np.trace(Y)
print(f"    tr(Y) = {trY:.6f}")
print(f"    66 vs tr(Y): 誤差 {abs(66-trY)/66*100:.2f}%")
check("tr(Y) 有意義", abs(trY) > 1e-3, f"({trY:.4f})")

# --- [3] κ 同 66 嘅結構 ---
print("\n[3] κ 嘅結構數:")
# 303 non-zero (raw) 但 symmetric 展開後 1122
# 獨立 entries (i≤j≤k)
n_indep = 0
for i in range(36):
    for j in range(i, 36):
        for k in range(j, 36):
            if K[i,j,k] != 0:
                n_indep += 1
print(f"    獨立 entries (i≤j≤k): {n_indep}")
print(f"    303 (raw dict) = ? {len(kappa['kappa'])}")
print(f"    66 = C(12,2) vs {n_indep}: 比例 {n_indep/66:.3f}")

# 對角+對稱 group
diag_count = sum(1 for i in range(36) if K[i,i,i] != 0)
print(f"    κ_iii non-zero: {diag_count}")

# --- [4] κ 嘅 12 維結構 (新嘗試: 每 3 個 moduli 一組) ---
print("\n[4] κ 嘅 group 結構:")
# 36 moduli 每 3 個一組 = 12 groups
# 檢查 group 內/間嘅耦合強度
group_size = 3
n_groups = 36 // group_size
g_intra = 0
g_inter = 0
for i in range(36):
    for j in range(36):
        for k in range(36):
            gi, gj, gk = i//group_size, j//group_size, k//group_size
            if gi == gj == gk:
                g_intra += abs(K[i,j,k])
            else:
                g_inter += abs(K[i,j,k])
print(f"    group 內耦合: {g_intra:.0f}")
print(f"    group 間耦合: {g_inter:.0f}")
print(f"    內/外比: {g_intra/max(g_inter,1):.3f}")
check("冇 3-group 結構", g_inter > g_intra, f"(內 {g_intra:.0f} vs 外 {g_inter:.0f})")

# --- [5] 66 = 3×22 喺 κ? ---
print("\n[5] 22 結構:")
# 36 moduli 分 3×12; 12 維子張量?
# 試所有 12 維 subsets? 太多。試順序 0-11, 12-23, 24-35
for g in range(3):
    idx = slice(g*12, (g+1)*12)
    K12 = K[idx, idx, idx]
    D12 = K12.reshape(12, 144)
    r = np.linalg.matrix_rank(D12, tol=1e-10)
    nz = np.count_nonzero(K12)
    print(f"    12 維 block {g} (moduli {g*12}-{(g+1)*12-1}): rank={r}, non-zero={nz}")

# --- [6] tr(Y) 目標: 66 需要咩 J*? ---
print("\n[6] tr(Y) = 66 條件:")
# tr(Y) = Σ_ijk K_ijk J_k 嘅對角部分... 實際 tr(Y) = Σ_i Y_ii = Σ_ijk K_ijk J_k δ_ij
# 即 tr(Y) = Σ_ik K_iik J_k
K_iik = np.einsum('iik->k', K)
print(f"    κ_iik 向量: {np.array2string(K_iik, precision=2)}")
print(f"    Σ κ_iik = {K_iik.sum():.0f}")
print(f"    tr(Y) = Σ κ_iik J_k = {np.dot(K_iik, J):.4f}")
# 66 = Σ κ_iik J_k 需要 J_k = 66/Σκ = ?
target_J = 66 / K_iik.sum()
print(f"    66 需要均勻 J = {target_J:.4f}")
print(f"    實際 J mean = {J.mean():.6f}")
check("J 唔均勻 (真實 Kähler 參數)", abs(J.mean() - target_J) > 0.001, 
      f"(J mean {J.mean():.6f} vs 66-need {target_J:.4f})")

# --- [7] 新閉合: tr(Y) 用 φ VEV? ---
print("\n[7] tr(Y) 用 φ^(-k/36) VEV:")
for n in [24, 36, 48, 72]:
    v = np.array([phi ** (-k/n) for k in range(36)])
    tr = np.dot(K_iik, v)
    print(f"    n={n}: tr(Y) = {tr:.4f} (誤差 {abs(66-tr)/66*100:.1f}%)")

# φ^(-k/36) 最佳
best_n, best_tr, best_err = None, None, 1e9
for n in range(10, 200):
    v = np.array([phi ** (-k/n) for k in range(36)])
    tr = np.dot(K_iik, v)
    err = abs(66 - tr)
    if err < best_err:
        best_err, best_tr, best_n = err, tr, n
print(f"    最佳 n={best_n}: tr(Y) = {best_tr:.4f} (誤差 {best_err:.4f})")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)
