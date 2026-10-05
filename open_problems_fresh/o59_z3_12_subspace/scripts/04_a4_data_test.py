#!/usr/bin/env python3
"""
O59 Phase 4: A₄ 對稱性實測 — 真 κ + J* 嘅 3×12 block 結構
=====================================================
核心問題: 36 = 3×12 = 3 × A₄ regular rep?
測試:
  1. 構建 Y = κ_ijk·J^k (真幾何)
  2. 檢查 Y 嘅 3×12 block 結構 (已有: block-triangular)
  3. ★ A₄ permutation 對稱測試: 12 個 A₄ 元素 P, P·Y·Pᵀ = Y?
  4. Block 譜分解: 每個 12D block 係咪 A₄ regular rep (1⊕1'⊕1''⊕3⊕3⊕3)?
  5. su(12) weight 結構同 A₄ 嘅關係
"""
import os, json, math
import numpy as np
from itertools import permutations

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
O53_POLY = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O59 Phase 4: A₄ 對稱性實測 (真 κ + J*)")
print("=" * 72)

passed, failed = 0, 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. 載入真實 κ + J* ============
print("\n[1] 載入真實 κ + J*")
with open(os.path.join(O53_POLY, "cy36_98_intersection_full.json")) as f:
    K = np.array(json.load(f)["kappa"])
with open(os.path.join(O53_POLY, "Jstar_36D.json")) as f:
    jd = json.load(f)
J0 = np.array(jd["Jstar_36D"])
print(f"  κ: {K.shape}, J*: {J0.shape}")

# Y = κ_ijk J^k (contraction)
Y = np.einsum("ijk,k->ij", K, J0)
Y = (Y + Y.T) / 2
print(f"  Y: {Y.shape}")
ev = np.linalg.eigvalsh(Y)
print(f"  Y 本徵值: pos={np.sum(ev>1e-10)}, neg={np.sum(ev<-1e-10)}, zero={np.sum(np.abs(ev)<1e-10)}")

# ============ 2. 3×12 block 結構 (重驗) ============
print("\n[2] 3×12 block 結構 (重驗)")
blocks = [Y[i*12:(i+1)*12, i*12:(i+1)*12] for i in range(3)]
for g, b in enumerate(blocks):
    bev = np.linalg.eigvalsh(b)
    print(f"  Block {g}: pos={np.sum(bev>1e-10)}, neg={np.sum(bev<-1e-10)}, zero={np.sum(np.abs(bev)<1e-10)}")
# inter-block Frobenius
inter = np.zeros((3,3))
for i in range(3):
    for j in range(3):
        inter[i,j] = np.linalg.norm(Y[i*12:(i+1)*12, j*12:(j+1)*12])
print(f"  Inter-block Frobenius norms:\n{np.round(inter, 3)}")
diag_ratio = (inter[0,0]+inter[1,1]+inter[2,2]) / (inter.sum() - (inter[0,0]+inter[1,1]+inter[2,2]))
print(f"  對角/非對角 ratio: {diag_ratio:.3f}")
check("3×12 block 對角主導", diag_ratio > 2, f"({diag_ratio:.2f})")

# ============ 3. A₄ permutation 對稱測試 ============
print("\n[3] ★ A₄ permutation 對稱測試")
# A₄ = 偶置換 of 4 元素. 但 12 維 block 嘅 A₄ 作用?
# 假設: A₄ 作用喺 4 個「tensor factor」上, 每個 factor 3 維
# 12 = 3×4: A₄ 作用喺 4 個 3D blocks 上 (permutation of 4 組 3 維)
# → 12 維 = 4 組 × 3 維, A₄ 置換 4 組

# 構建 A₄ 元素 (偶置換 of 4)
def perm_matrix(p, d=3):
    """置換 4 組 3D block: p = tuple of 4"""
    P = np.zeros((12, 12))
    for i, pi in enumerate(p):
        P[i*d:(i+1)*d, pi*d:(pi+1)*d] = np.eye(d)
    return P

# 生成 A₄ (偶置換)
A4 = []
for p in permutations(range(4)):
    # sign of permutation
    sign = 1
    for i in range(4):
        for j in range(i+1, 4):
            if p[i] > p[j]:
                sign *= -1
    if sign == 1:
        A4.append(p)
print(f"  A₄ 元素數: {len(A4)}")

# 測試: 每個 block 自己嘅 A₄ 對稱
# Y_block = Y[0:12, 0:12] 有冇 A₄ 對稱 (12 = 3×4)?
Y0 = blocks[0]
print(f"\n  Block 0 (12×12): A₄ permutation 對稱測試 (12 = 3×4)")
sym_viol = []
for p in A4:
    P = perm_matrix(p)
    diff = np.linalg.norm(P @ Y0 @ P.T - Y0)
    sym_viol.append(diff)
print(f"  A₄ 對稱違反: min={min(sym_viol):.4f}, max={max(sym_viol):.4f}, mean={np.mean(sym_viol):.4f}")
scale = np.linalg.norm(Y0)
print(f"  Y0 norm: {scale:.4f}, 相對違反: {np.mean(sym_viol)/scale:.4f}")
check("Block 0 A₄ 對稱 (rel < 0.3)", np.mean(sym_viol)/scale < 0.3,
      f"({np.mean(sym_viol)/scale:.3f})")

# 全 Y 嘅 A₄ 對稱 (36 = 3×12, 3 個 block 各自置換?)
print(f"\n  全 Y (36×36): A₄ ⊗ Z₃ 對稱測試")
# 36 = 3 (gen) × 12 (block), Z₃ 置換 gen?
# 先試: Z₃ 循環置換 3 個 block
P3 = np.zeros((36, 36))
P3[0:12, 12:24] = np.eye(12)
P3[12:24, 24:36] = np.eye(12)
P3[24:36, 0:12] = np.eye(12)
diff3 = np.linalg.norm(P3 @ Y @ P3.T - Y)
print(f"  Z₃ block 置換違反: {diff3:.4f} (rel {diff3/np.linalg.norm(Y):.4f})")
check("Z₃ block 置換對稱", diff3/np.linalg.norm(Y) < 0.3,
      f"(rel {diff3/np.linalg.norm(Y):.3f})")

# ============ 4. Block 譜嘅 A₄ regular rep 分解 ============
print("\n[4] Block 譜 A₄ regular rep 分解")
# A₄ regular rep = 1 ⊕ 1' ⊕ 1'' ⊕ 3 ⊕ 3 ⊕ 3
# 12D block 本徵值應該有 3 重簡併 (3 個 3 維表示) + 3 個 singlet
print("  A₄ regular rep: 1 ⊕ 1' ⊕ 1'' ⊕ 3 ⊕ 3 ⊕ 3")
print("  → 3 個 singlet + 3 個三重簡併")
for g, b in enumerate(blocks):
    bev = np.linalg.eigvalsh(b)
    # 檢查簡併
    sorted_ev = np.sort(bev)
    degen = []
    i = 0
    while i < 12:
        j = i
        while j+1 < 12 and abs(sorted_ev[j+1] - sorted_ev[j]) < 1e-6:
            j += 1
        if j > i:
            degen.append((sorted_ev[i], j-i+1))
        i = j + 1
    print(f"  Block {g}: 簡併結構 {degen}")
    n3 = sum(1 for _, m in degen if m == 3)
    n1 = sum(1 for _, m in degen if m == 1)
    print(f"    三重簡併: {n3}, singlet: {n1}")
    check(f"Block {g} 有 3 重簡併 (A₄ 3 維表示)", n3 >= 1, f"({n3})")

# ============ 5. su(12) weight 同 A₄ ============
print("\n[5] su(12) ⊃ A₄ 分支")
# su(12) fundamental 12 → A₄ regular rep?
# A₄ regular rep = 1⊕1'⊕1''⊕3⊕3⊕3 (12 維)
print("  su(12) fundamental (12) → A₄: 1⊕1'⊕1''⊕3⊕3⊕3")
print("  su(12) adjoint (143) → A₄ 分支:")
# 143 = 12⊗12̄−1: (1⊕1'⊕1''⊕3⊕3⊕3)⊗(same)̄ − 1
# 1⊗1 = 1, 1'⊗1̄' = 1, 1''⊗1̄'' = 1, 3⊗3̄ = 1⊕3' (A₄ 中 3⊗3̄ = 1⊕3)
# 大致: 3×3 singlet + 3×(1⊕3) + 3×3 doublets...
print("  粗略: 143 → 含 3 個 3⊗3̄ = 3×(1⊕3) + ...")
print("  66 正根 (wedge² 12): A₄ 分支:")
print("  wedge²(1⊕1'⊕1''⊕3⊕3⊕3) = 3×wedge²(3) ⊕ ...")
print("  wedge²(3) = 3̄* (A₄ 中 3 維表示嘅外積 = 3)")
print("  → 66 含 3×3 = 9 個 3 維 block? 有待驗證")

print(f"\n{'='*72}")
print(f"Phase 4 結果: {passed} PASS, {failed} FAIL")
print(f"{'='*72}")
