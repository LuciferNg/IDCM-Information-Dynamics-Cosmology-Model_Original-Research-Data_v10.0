#!/usr/bin/env python3
"""
O50 文檔內容獨立核對
====================
獨立重算文檔中引用嘅所有關鍵數值，對照 docs/01_analysis.md,
docs/02_derivative_closure.md, final_result.md 內容。
只驗證唔改寫 — 發現偏差只報告。
"""

import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
O50_DIR = os.path.join(os.path.dirname(__file__), "..")
O53_POLY = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

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
print("O50 文檔內容獨立核對")
print("=" * 80)

# 載入原始數據
with open(os.path.join(O53_POLY, "cy36_98_intersection_full.json")) as f:
    K = np.array(json.load(f)["kappa"])
d_final = np.load(os.path.join(DATA, "d_tensor_final.npy"))
d_solved = np.load(os.path.join(DATA, "d_tensor_solved.npy"))
d_positive = np.load(os.path.join(DATA, "d_tensor_positive.npy"))

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

# 讀取所有文檔
doc_paths = {
    "docs/01_analysis.md": os.path.join(O50_DIR, "docs", "01_analysis.md"),
    "docs/02_derivative_closure.md": os.path.join(O50_DIR, "docs", "02_derivative_closure.md"),
    "final_result.md": os.path.join(O50_DIR, "final_result.md"),
}
docs = {}
for name, path in doc_paths.items():
    with open(path) as f:
        docs[name] = f.read()
    print(f"  ✅ 讀取 {name}")

# =====================================================================
# [A] 獨立重算所有關鍵數值
# =====================================================================
print("\n[A] 獨立重算關鍵數值")

# A1. κ_ijk 基本
check("κ shape (36,36,36)", K.shape == (36,36,36))
check("κ non-zero = 1341", np.count_nonzero(K) == 1341)
check("κ range [-360,180]", K.min() == -360 and K.max() == 180)
check("κ 整數", np.all(K == K.astype(int)))
check("κ 全對稱", np.allclose(K, K.transpose(1,0,2)))
check("κ flatten rank = 32", np.linalg.matrix_rank(K.reshape(36,-1), tol=1e-10) == 32)

# A2. κ 對角
diag = np.array([K[i,i,i] for i in range(36)])
check("κ 非零對角 = 33", np.count_nonzero(diag) == 33)
check("κ 對角和 = -380", diag.sum() == -380)
check("κ 對角 |和| = 824", np.abs(diag).sum() == 824)
check("κ d_000 = -360", diag[0] == -360)
check("κ d_008 = -232", diag[8] == -232)
check("κ d_033 = 40", diag[33] == 40)

# A3. 3×12 block
blocks = np.zeros((3,3,3))
for bi in range(3):
    for bj in range(3):
        for bk in range(3):
            blocks[bi,bj,bk] = np.abs(K[bi*12:(bi+1)*12, bj*12:(bj+1)*12, bk*12:(bk+1)*12]).sum()
diag_ratio = (blocks[0,0,0]+blocks[1,1,1]+blocks[2,2,2]) / blocks.sum()
check("3×12 對角塊比 ≈ 0.753", abs(diag_ratio - 0.753) < 0.005, f"({diag_ratio:.4f})")
check("Block[0,0,0] non-zero = 292", np.count_nonzero(K[:12,:12,:12]) == 292)
check("Block[1,1,1] non-zero = 86", np.count_nonzero(K[12:24,12:24,12:24]) == 86)
check("Block[2,2,2] non-zero = 54", np.count_nonzero(K[24:36,24:36,24:36]) == 54)

# A4. Z₃ 檢查
err4 = np.mean([abs(K[i,j,k]-K[(i+4)%36,(j+4)%36,(k+4)%36]) for i in range(36) for j in range(36) for k in range(36)])
check("κ 4-shift 誤差 = 0.305", abs(err4 - 0.305) < 0.01, f"({err4:.3f})")
check("κ d_scale = 0.160", abs(np.abs(K).mean() - 0.160) < 0.01, f"({np.abs(K).mean():.3f})")

# A5. Yukawa 譜
Y_real = np.einsum('ijk,k->ij', K, J)
Y_real = (Y_real + Y_real.T)/2
ev_real = np.linalg.eigvalsh(Y_real)
ev_real_sorted = sorted(ev_real, reverse=True)
check("κ Yukawa 正 = 15", np.sum(ev_real > 1e-10) == 15)
check("κ Yukawa 負 = 17", np.sum(ev_real < -1e-10) == 17)
check("κ λ₁ = 3.697", abs(ev_real_sorted[0]-3.697) < 0.001, f"({ev_real_sorted[0]:.4f})")
check("κ λ₁/λ₂ = 4.712", abs(ev_real_sorted[0]/ev_real_sorted[1]-4.712) < 0.005, f"({ev_real_sorted[0]/ev_real_sorted[1]:.3f})")
check("κ tr(Y²) = 16.14", abs(np.trace(Y_real@Y_real)-16.14) < 0.01, f"({np.trace(Y_real@Y_real):.2f})")
check("κ λ₁/λ₁₅ = 403", abs(ev_real_sorted[0]/ev_real_sorted[14]-403) < 5, f"({ev_real_sorted[0]/ev_real_sorted[14]:.1f})")

# A6. d_tensor_final
v = np.array([phi**(-k/12) for k in range(12)])
Y_final = np.einsum('ijk,k->ij', d_final, v)
Y_final = (Y_final + Y_final.T)/2
ev_final = np.linalg.eigvalsh(Y_final)
ev_final_sorted = sorted(ev_final, reverse=True)
check("d_final non-zero = 1300", np.count_nonzero(d_final) == 1300)
check("d_final range [-0.286,3.078]", abs(d_final.min()-(-0.285764))<0.001 and abs(d_final.max()-3.077648)<0.001)
check("d_final 正 = 11", np.sum(ev_final > 1e-10) == 11)
check("d_final 零 = 1", abs(ev_final_sorted[10]) < 0.01)
check("d_final λ₁ = 51.56", abs(ev_final_sorted[0]-51.56) < 0.01, f"({ev_final_sorted[0]:.4f})")
check("d_final λ₁/λ₂ = 5.156", abs(ev_final_sorted[0]/ev_final_sorted[1]-5.156) < 0.005, f"({ev_final_sorted[0]/ev_final_sorted[1]:.3f})")

# A7. d_tensor_positive
check("d_positive non-zero = 1728 (全非零)", np.count_nonzero(d_positive) == 1728)
check("d_positive 全正", d_positive.min() > 0)

# A8. d_tensor_solved
v36 = np.array([phi**(-k/36) for k in range(36)])
Y_solved = np.einsum('ijk,k->ij', d_solved, v36)
Y_solved = (Y_solved + Y_solved.T)/2
ev_solved = np.linalg.eigvalsh(Y_solved)
check("d_solved 正 = 13", np.sum(ev_solved > 1e-10) == 13)
check("d_solved range [-0.081,1.857]", abs(d_solved.min()-(-0.081))<0.001 and abs(d_solved.max()-1.857)<0.001)

# A9. WDVV 誤差 (6×6×6×6)
K6 = K[:6,:6,:6]
g6 = np.einsum('ijk,k->ij', K6, np.ones(6))
g6_inv = np.linalg.inv(g6)
max_err_k = 0
for i in range(6):
    for j in range(6):
        for k in range(6):
            for l in range(6):
                lhs = np.einsum('p,pq,q->', K6[i,j], g6_inv, K6[:,k,l])
                rhs = np.einsum('p,pq,q->', K6[i,l], g6_inv, K6[:,j,k])
                max_err_k = max(max_err_k, abs(lhs-rhs))
check("κ WDVV max err = 14.86", abs(max_err_k-14.86) < 0.5, f"({max_err_k:.2f})")

d6 = d_final[:6,:6,:6]
g6d = np.einsum('ijk,k->ij', d6, np.ones(6))
g6d_inv = np.linalg.inv(g6d)
max_err_d = 0
for i in range(6):
    for j in range(6):
        for k in range(6):
            for l in range(6):
                lhs = np.einsum('p,pq,q->', d6[i,j], g6d_inv, d6[:,k,l])
                rhs = np.einsum('p,pq,q->', d6[i,l], g6d_inv, d6[:,j,k])
                max_err_d = max(max_err_d, abs(lhs-rhs))
check("d_final WDVV max err = 0.56", abs(max_err_d-0.56) < 0.3, f"({max_err_d:.2f})")

# A10. GLSM / Sage
with open(os.path.join(O53_POLY, "cy36_98_sage_export.json")) as f:
    sage = json.load(f)
glsm = np.array(sage["glsm_matrix"])
check("GLSM (32,37)", glsm.shape == (32,37))
check("GLSM rank 32", np.linalg.matrix_rank(glsm, tol=1e-10) == 32)
check("Sage h11=36 h21=98", sage["h11"]==36 and sage["h21"]==98)
check("Sage 48 points", len(sage["points"]) == 48)
check("Sage 144 simplices", len(sage["simplices"]) == 144)
check("Sage χ = -124", sage["chi"] == -124)

# =====================================================================
# [B] 文檔引用數值核對
# =====================================================================
print("\n[B] 文檔引用數值核對")

# docs/01_analysis.md
d1 = docs["docs/01_analysis.md"]
check("01: κ non-zero 1341", "1341" in d1)
check("01: κ range [-360,180]", "[-360, 180]" in d1)
check("01: κ rank 32", "32" in d1)
check("01: 3×12 對角 75.3%", "75.3%" in d1)
check("01: Z₃ 誤差 0.305", "0.305" in d1)
check("01: κ λ₁ 3.697", "3.697" in d1)
check("01: d_final λ₁ 51.56", "51.56" in d1)
check("01: κ WDVV 14.86", "14.86" in d1)
check("01: d_final WDVV 0.56", "0.56" in d1)
check("01: κ 15 正本徵值", "15" in d1)
check("01: d_final 11 正本徵值", "11" in d1)
check("01: 對角和 -380", "-380" in d1)
check("01: 對角|和| 824", "824" in d1)

# docs/02_derivative_closure.md
d2 = docs["docs/02_derivative_closure.md"]
check("02: κ λ₁/λ₁₅ = 403", "403" in d2)
check("02: SM 338,000", "338,000" in d2)
check("02: κ WDVV 14.86", "14.86" in d2)
check("02: d_final WDVV 0.56", "0.56" in d2)
check("02: 3×12 75.3%", "75.3%" in d2)
check("02: 58/58 PASS", "58/58" in d2)
check("02: Z₃ center 定理", "Z₃" in d2 and "center" in d2)

# final_result.md
d3 = docs["final_result.md"]
check("final: 狀態 🟢 已閉合", "🟢 已閉合" in d3)
check("final: κ non-zero 1341", "1341" in d3)
check("final: rank 32", "rank = 32" in d3)
check("final: 3×12 = 3×12", "3 × 12" in d3)
check("final: WDVV 14.86/0.56", "14.86" in d3 and "0.56" in d3)
check("final: 403 ≪ 338,000", "403" in d3 and "338,000" in d3)
check("final: 依賴 O53→O50→O55", "O53 → O50 → O55" in d3)

# =====================================================================
# [C] 推導時序索引核對
# =====================================================================
print("\n[C] 推導時序索引核對")
with open(os.path.join(O50_DIR, "01_problem_record.md")) as f:
    pr = f.read()
check("problem_record: 推導時序索引存在", "推導時序索引" in pr)
check("problem_record: 9 個時序步驟", "| 9 |" in pr)
check("problem_record: 時序規則", "時序規則" in pr)
check("problem_record: 禁止回溯", "禁止" in pr)

# =====================================================================
print("\n" + "=" * 80)
print(f"文檔獨立核對: {PASS} PASS / {FAIL} FAIL")
print("=" * 80)
for r in results:
    print(r)

if FAIL == 0:
    print("\n🎯 所有文檔引用數值與獨立重算一致！")
else:
    print(f"\n⚠️ {FAIL} 個偏差 — 需要修正文檔！")

sys.exit(0 if FAIL == 0 else 1)