#!/usr/bin/env python3
"""
O53 第二 session 最終驗證器
============================
Verifier: 獨立重算所有關鍵數字, 確認無幻覺

檢查清單:
  1. KS 存在性: (36,98) χ=-124
  2. 結構數: 134=Nd+Σγ, 62=Nd+L₆
  3. 946 = C(44,2)
  4. 66 = C(12,2)
  5. P̂ rank = 2 (原版缺陷)
  6. d_ijk rank-1 可分離
  7. 修正版 P̂ rank 109, Kähler 36
  8. tr(Y) ≈ 66 (0.54%)
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
sys.path.insert(0, os.path.join(BASE, "src"))

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

print("=" * 70)
print("O53 第二 session 最終驗證")
print("=" * 70)

# [1] KS 存在性
print("\n[1] KS 數據庫:")
pairs = []
with open(os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "alltoric.spec")) as f:
    for line in f:
        p = line.split()
        if len(p) >= 3:
            try:
                pairs.append((int(p[0]), int(p[1]), int(p[2])))
            except ValueError:
                pass
arr = np.array(pairs)
found = arr[(arr[:,0]==36) & (arr[:,1]==98)]
check("(36,98) 存在", len(found) == 1, f"→ {found[0] if len(found) else 'NOT FOUND'}")
check("χ = -124", len(found) > 0 and found[0][2] == -124)

# [2] 結構數
print("\n[2] K_Chain 結構數:")
B = phi**3 - phi**-3
L5 = phi**5 + (-phi)**-5
L6 = phi**6 + (-phi)**-6
S_gamma = sum(4 * math.sin(math.pi * n / 88)**2 for n in range(1, 45))
Nd = int(round(B * L5))
check("Nd = 44", Nd == 44)
check("Σγ = 90", abs(S_gamma - 90) < 1e-6, f"({S_gamma:.6f})")
check("134 = Nd+Σγ", Nd + round(S_gamma) == 134)
check("62 = Nd+L₆", Nd + round(L6) == 62)

# [3] 組合數
print("\n[3] 組合數:")
check("946 = C(44,2)", 44*43//2 == 946)
check("66 = C(12,2)", 12*11//2 == 66)

# [4] 原版 P̂ rank-2 缺陷
print("\n[4] 原版投影算子缺陷:")
from projection_operator import CY3ProjectionOperator
op = CY3ProjectionOperator()
P = op.compute_matrix()
rank_orig = np.linalg.matrix_rank(P, tol=1e-10)
check("原版 rank = 2 (缺陷)", rank_orig == 2, f"(實際 {rank_orig})")
# 行相關性
kahler_rows = P[:36, :]
cors = []
for i in range(0, 36, 7):
    for j in range(i+7, 36, 7):
        mask = (kahler_rows[i] != 0) & (kahler_rows[j] != 0)
        if mask.sum() > 3:
            cors.append(np.corrcoef(kahler_rows[i][mask], kahler_rows[j][mask])[0, 1])
check("Kähler 行 100% 相關", len(cors) > 0 and max(cors) > 0.999999, f"(max {max(cors):.10f})")

# [5] d_ijk rank-1
print("\n[5] d_{ijk} rank-1:")
from dijk_intersection import TripleIntersectionTensor
d36 = TripleIntersectionTensor().compute()
D0 = d36.reshape(36, 36*36)
rank_d = np.linalg.matrix_rank(D0, tol=1e-10)
check("d_{ijk} flatten rank = 1", rank_d == 1, f"(實際 {rank_d})")

# [6] 修正版 P̂
print("\n[6] 修正版投影算子:")
P_fixed = np.load(os.path.join(DATA, "P_fixed_v2.npy"))
rank_fixed = np.linalg.matrix_rank(P_fixed, tol=1e-10)
check("修正版 rank = 109", rank_fixed == 109, f"(實際 {rank_fixed})")
Pk = P_fixed[:36, :]
rank_k = np.linalg.matrix_rank(Pk, tol=1e-10)
check("Kähler 子秩 = 36", rank_k == 36, f"(實際 {rank_k})")

# 66 譜
PPT = P_fixed @ P_fixed.T
evals = np.linalg.eigvalsh(PPT)
evals_sorted = np.sort(evals)[::-1]
n_pos = np.sum(evals > 1e-10)
check("正本徵值 ≥ 66", n_pos >= 66, f"({n_pos})")
check("前 66 係真譜", evals_sorted[65] > 1e-6, f"(λ₆₆={evals_sorted[65]:.4e})")

# [7] tr(Y)
print("\n[7] tr(Y) ≈ 66:")
d12 = np.load(os.path.join(DATA, "d_tensor_final.npy"))
v = np.array([phi ** (-k/12) for k in range(12)])
d_iik = np.einsum('iik->i', d12)
trY = np.sum(d_iik * v)
err = abs(66 - trY) / 66 * 100
check("tr(Y) ≈ 66", err < 1.0, f"({trY:.4f}, 誤差 {err:.2f}%)")

# 12 維 rank
D12 = d12.reshape(12, 144)
rank_12 = np.linalg.matrix_rank(D12, tol=1e-10)
check("d12 rank = 12", rank_12 == 12, f"(實際 {rank_12})")

# [8] Z₃ 誠實修正: d_tensor 冇 Z₃ 對稱
print("\n[8] Z₃ 結構誠實檢查:")
err_shift = np.mean([abs(d12[i,j,k] - d12[(i+4)%12,(j+4)%12,(k+4)%12])
                     for i in range(12) for j in range(12) for k in range(12)])
d_scale = np.abs(d12).mean()
check("d_tensor 冇 Z₃ 對稱 (誠實)", err_shift > d_scale * 0.1,
      f"(4-shift 誤差 {err_shift:.3f} vs d 規模 {d_scale:.3f})")

# [9] CICY 排除
print("\n[9] CICY 家族排除:")
cicy_path = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "cicylist.txt")
if os.path.exists(cicy_path):
    import re
    with open(cicy_path) as f:
        content = f.read()
    entries = [e for e in content.split("Num    :") if e.strip()]
    h11_max = 0
    has_36_98 = False
    for e in entries:
        m11 = re.search(r"H11\s*:\s*(\d+)", e)
        m21 = re.search(r"H21\s*:\s*(\d+)", e)
        if m11 and m21:
            h11_max = max(h11_max, int(m11.group(1)))
            if (int(m11.group(1)), int(m21.group(1))) == (36, 98):
                has_36_98 = True
    check("CICY h¹¹ max < 36", h11_max < 36, f"(max={h11_max})")
    check("(36,98) 唔係 CICY", not has_36_98)
else:
    check("CICY 數據存在", False, "(cicylist.txt 缺失)")

# [10] 問題 3: 真實 polytope 數據
print("\n[10] 真實 polytope (問題 3):")
poly_path = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
if os.path.exists(os.path.join(poly_path, "cy36_98_sage_export.json")):
    with open(os.path.join(poly_path, "cy36_98_sage_export.json")) as f:
        pe = json.load(f)
    check("48 points", len(pe['points']) == 48, f"({len(pe['points'])})")
    check("144 simplices", len(pe['simplices']) == 144, f"({len(pe['simplices'])})")
    check("h11=36 h21=98", pe['h11'] == 36 and pe['h21'] == 98)
    # GLSM CY 條件
    glsm = np.array(pe['glsm_matrix'])
    check("GLSM 行和 = 0", np.all(glsm.sum(axis=1) == 0))
else:
    check("polytope 數據存在", False, "(cy36_98_sage_export.json 缺失)")

# [11] 問題 4: λ₁ = φ^(1/3) 閉合
print("\n[11] 真實幾何閉合 (問題 4):")
if os.path.exists(os.path.join(poly_path, "kappa_36d_raw.json")) and os.path.exists(os.path.join(poly_path, "Jstar_36D.json")):
    with open(os.path.join(poly_path, "kappa_36d_raw.json")) as f:
        kappa = json.load(f)
    with open(os.path.join(poly_path, "Jstar_36D.json")) as f:
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
    evals_Y = np.linalg.eigvalsh(Y)
    l1 = max(evals_Y)
    inv_l1 = 1/l1
    phi_m13 = phi ** (-1/3)
    err = abs(inv_l1 - phi_m13)/phi_m13*100
    check("λ₁ = φ^(1/3) (誤差 <1%)", err < 1.0, f"(1/λ₁={inv_l1:.6f}, φ^(-1/3)={phi_m13:.6f}, {err:.3f}%)")
    n_nz = np.sum(np.abs(evals_Y) > 1e-10)
    check("32 非零本徵值", n_nz == 32, f"({n_nz})")
    trY2 = np.trace(Y @ Y)
    check("tr(Y²) ≈ 5", abs(trY2-5)/5 < 0.05, f"({trY2:.4f})")
else:
    check("κ_ijk 數據存在", False, "(kappa_36d_raw.json 缺失)")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
for r in results:
    print(r)

if FAIL == 0:
    print("\n🎯 全部通過 — 第二 session 所有發現確認無幻覺")
else:
    print(f"\n⚠️ {FAIL} 個檢查失敗 — 需要修正!")
sys.exit(0 if FAIL == 0 else 1)
