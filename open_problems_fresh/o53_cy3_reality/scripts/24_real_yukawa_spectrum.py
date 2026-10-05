#!/usr/bin/env python3
"""
O53 Q4 閉合: 真實 Yukawa 譜分析
=================================
發現: 真實 Y = κ_ijk J*^k 有 16 個非零本徵值 (36×36)
分析:
  1. Y 本徵值譜結構 (16 非零 + 20 零)
  2. 16 = ? (66 無關? 定係新結構?)
  3. 12 維 block rank=12 ×3 — 有冇 3 代結構?
  4. Y 嘅質量譜對 SM?
"""
import os, json, math
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53 Q4: 真實 Yukawa 譜")
print("=" * 70)

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
Y = np.einsum('ijk,k->ij', K, J)
Y = (Y + Y.T) / 2

print(f"\n[1] Y (36×36):")
evals = np.linalg.eigvalsh(Y)
n_nz = np.sum(np.abs(evals) > 1e-10)
print(f"    非零本徵值: {n_nz}")
print(f"    零本徵值: {36 - n_nz}")
print(f"    譜: {np.array2string(np.sort(evals)[::-1], precision=4)}")

# --- [1] 16 = ? ---
print("\n[2] 16 嘅身份:")
print(f"    16 = B² (K_Chain 分支數)")
print(f"    16 = 2⁴ (4 維)")
print(f"    16 = 4² (4×4)")
print(f"    16 = 44−28? 16 = 90−74?")
print(f"    16 = 12+4 (12 維 + 4 維)")
print(f"    16 = 66/4.125?")
print(f"    16 = h21/6.125? 98/16 = {98/16:.2f}")

# --- [2] 零本徵值 20 = ? ---
n_zero = 36 - n_nz
print(f"\n[3] 零本徵值 {n_zero}:")
print(f"    20 = 阻挫 (A₅ 32 阻挫邊? 20Δ+12⬠?)")
print(f"    20 = 正三角形面數 (20Δ)")
print(f"    20 = 4×5 = B×F₅")
print(f"    20 = 44−24? 20 = 33−13?")

# --- [3] 12 維 block rank 分析 ---
print("\n[4] 3×12 block 結構:")
for g in range(3):
    idx = slice(g*12, (g+1)*12)
    K12 = K[idx, idx, idx]
    # 12 維 Yukawa (用 global J 投影)
    Y12 = np.einsum('ijk,k->ij', K12, J[idx])
    ev12 = np.linalg.eigvalsh(Y12)
    nz12 = np.sum(np.abs(ev12) > 1e-10)
    print(f"    block {g}: non-zero κ={np.count_nonzero(K12)}, Y 非零本徵值={nz12}")

# --- [4] Y 有冇 3 代分塊? ---
print("\n[5] 3 代結構:")
# 36 = 3×12: 檢查 Y 係咪 block diagonal 或者有 3 組結構
Y_blocks = np.zeros((3, 3))
for bi in range(3):
    for bj in range(3):
        Y_blocks[bi, bj] = np.abs(Y[bi*12:(bi+1)*12, bj*12:(bj+1)*12]).sum()
print(f"    3×12 block 矩陣 (|Y| 總和):")
for bi in range(3):
    print(f"      {Y_blocks[bi,0]:8.2f} {Y_blocks[bi,1]:8.2f} {Y_blocks[bi,2]:8.2f}")

# --- [5] tr(Y²) 同 66 ---
print("\n[6] tr(Y²) 分析:")
trY2 = np.trace(Y @ Y)
print(f"    tr(Y²) = {trY2:.6f}")
print(f"    Σλ² = {np.sum(evals**2):.6f}")

# --- [6] 質量譜 ---
print("\n[7] 譜比:")
ev_nz = np.sort(evals)[::-1][:n_nz]
print(f"    非零譜: {np.array2string(ev_nz, precision=4)}")
# 有冇 φ 比例?
for i in range(min(8, len(ev_nz))):
    if ev_nz[0] != 0:
        ratio = ev_nz[0] / abs(ev_nz[i]) if ev_nz[i] != 0 else float('inf')
        print(f"      λ₁/λ_{i+1} = {ratio:.4f} (φ^({math.log(ratio)/math.log(phi):+.3f}))")

print("\n" + "=" * 70)
print("【結論】")
print("=" * 70)
print(f"""
  真實 Y (κ_ijk J*^k):
    - tr(Y) = -1.485 (負, 唔係 66)
    - {n_nz} 非零本徵值, {n_zero} 零
    - 3×12 block: {'全部 rank 12' if all(np.linalg.matrix_rank(K[g*12:(g+1)*12, g*12:(g+1)*12, g*12:(g+1)*12].reshape(12,144), tol=1e-10) == 12 for g in range(3)) else '有退化'}
    - 66 閉合唔直接 (κ 有負值)
""")
print("=" * 70)
