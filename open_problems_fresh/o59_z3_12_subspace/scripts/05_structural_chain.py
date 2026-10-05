#!/usr/bin/env python3
"""
O59 Phase 5: ★ 12 = B×N_gen 結構鏈驗證
========================================
核心發現: 12 = B × N_gen = 4 × 3 (K_Tree branch × 代數)

驗證鏈:
  Nd = B×L₅ = 4×11 = 44
  L₅ = 3N_gen + 2 = 11 (Lucas 5 結構)
  K_tree = N_gen×L₅ = 3×11 = 33
  12 = B×N_gen = 4×3
  h11 = N_gen×12 = 3×12 = 36
  66 = C(12,2) = 2×N_gen×L₅ = 2×33 = 2×K_tree
"""
import math, json, os
import numpy as np

phi = (1 + math.sqrt(5)) / 2
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

print("=" * 72)
print("O59 Phase 5: ★ 12 = B×N_gen 結構鏈")
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

# ============ 1. 基本結構 ============
print("\n[1] 基本結構")
B = 4        # K_Tree branch
Ngen = 3     # 代數
L5 = 11      # Lucas 5
L6 = 18      # Lucas 6
Nd = B * L5
Ktree = 33

print(f"  B = {B} (K_Tree branch)")
print(f"  N_gen = {Ngen}")
print(f"  L₅ = {L5}, L₆ = {L6}")
print(f"  Nd = B×L₅ = {Nd}")
print(f"  K_tree = {Ktree}")

# ============ 2. 核心閉合: 12 = B×N_gen ============
print("\n[2] ★ 12 = B×N_gen")
twelve = B * Ngen
print(f"  12 = {B}×{Ngen} = {twelve}")
check("12 = B×N_gen = 4×3", twelve == 12)

# 等價路徑
print(f"\n  等價路徑:")
print(f"  a) 12 = (Nd−2B)/3 = ({Nd}−{2*B})/3 = {(Nd-2*B)/Ngen} (每代 Kähler moduli)")
print(f"  b) 12 = Nd/4+1 = {Nd/4}+1 = {Nd/4+1}")
print(f"  c) 12 = (Nd+B)/4 = ({Nd}+{B})/{B} = {(Nd+B)/B}")
print(f"  d) 12 = 2L₆/3 = {2*L6}/{Ngen} = {2*L6/Ngen}")
print(f"  e) 12 = B×N_gen = {B}×{Ngen} = {B*Ngen}")
check("(Nd−2B)/3 == B×N_gen", (Nd-2*B)/Ngen == B*Ngen)
check("Nd/4+1 == B×N_gen", Nd/4+1 == B*Ngen)

# ============ 3. 深層: Nd = B(3N_gen+2) ============
print("\n[3] ★ Nd = B(3N_gen+2)")
# (Nd−2B)/3 = B×N_gen → Nd−2B = 3B×N_gen → Nd = B(3N_gen+2)
Nd_pred = B * (3*Ngen + 2)
print(f"  Nd = B(3N_gen+2) = {B}×({3*Ngen}+2) = {B}×{3*Ngen+2} = {Nd_pred}")
check("Nd = B(3N_gen+2) = 44", Nd_pred == 44)
print(f"  3N_gen+2 = {3*Ngen+2} = L₅ = 11!")
check("3N_gen+2 = L₅ = 11", 3*Ngen+2 == L5)
print(f"  ★ L₅ = 3N_gen + 2 = 3×3+2 = 11 — Lucas 5 被 N_gen 同「2」鎖定!")
print(f"  2 = 對偶 chain 因子 (44-site ↔ 88-site 對偶)")

# ============ 4. K_tree = N_gen×L₅ ============
print("\n[4] ★ K_tree = N_gen×L₅")
Ktree_pred = Ngen * L5
print(f"  K_tree = N_gen×L₅ = {Ngen}×{L5} = {Ktree_pred}")
check("K_tree = N_gen×L₅ = 33", Ktree_pred == 33)

# ============ 5. h11 = N_gen×12 ============
print("\n[5] h11 = N_gen×12")
h11 = Ngen * twelve
print(f"  h11 = N_gen×12 = {Ngen}×{twelve} = {h11}")
check("h11 = 3×12 = 36", h11 == 36)
print(f"  36 = N_gen × B × N_gen = {Ngen}×{B}×{Ngen} = {Ngen*B*Ngen}")
check("36 = N_gen×B×N_gen = 3×4×3", Ngen*B*Ngen == 36)
print(f"  ★ 36 = 3×4×3 = (N_gen, B, N_gen) — 對稱結構!")

# ============ 6. 66 = C(12,2) = 2×K_tree ============
print("\n[6] 66 = C(12,2) = 2×K_tree")
C122 = twelve * (twelve-1) // 2
print(f"  C(12,2) = 12×11/2 = {C122}")
check("C(12,2) = 66", C122 == 66)
check("66 = 2×K_tree = 2×33", 66 == 2*Ktree)
print(f"  66 = 2×N_gen×L₅ = 2×{Ngen}×{L5} = {2*Ngen*L5}")
check("66 = 2×N_gen×L₅", 2*Ngen*L5 == 66)
print(f"  66 = B×N_gen×L₅/2 = {B}×{Ngen}×{L5}/2 = {B*Ngen*L5/2}")
check("66 = B×N_gen×L₅/2", B*Ngen*L5/2 == 66)

# ============ 7. 完整閉合鏈 ============
print("\n[7] ★ 完整閉合鏈")
print("""
  B = 4 (K_Tree branch) ─────────────────────────────┐
  N_gen = 3 (代數) ─────────────────────────────────┐│
                                                    ││
  L₅ = 3N_gen + 2 = 11 (Lucas 5) ◄───────────────────┼┘
  Nd = B×L₅ = 44 (K_Chain sites) ◄───────────────────┘
  K_tree = N_gen×L₅ = 33 (K_Tree levels)
  12 = B×N_gen = 4×3 ◄── 每代 Kähler moduli
  h11 = N_gen×12 = 36 ◄── Kähler moduli
  66 = C(12,2) = 2×K_tree = 2×N_gen×L₅ ◄── su(12) 正根
""")

# ============ 8. 其他 12 嘅身份 ============
print("\n[8] 其他 12 嘅身份")
print("  F. 12 ⬠ (Rhombicosidodecahedron): 幾何對象, 5 邊形面數")
print("     → 12 = B×N_gen? 冇直接證據 — 純幾何巧合")
print("  G. 12 = K_tree − F₈ = 33−21: 唔同組合, 但 33 = N_gen×L₅")
print("     → 33−21 = 12: 21 = F₈ = L₆+3 = 18+3")
print("  H. φ^(-k/12): φ 係 Pisot 數, φ^n 近整數 for 所有 n")
print("     → 12 冇特別 — 撤回近整數週期論")
print("  I. 12.92° θ₁₂: 角度近似, 13 = F₇ 巧合")
print("  D. 12 = 4!/2 = |A₄|: 已 FAIL (真 κ 冇 A₄ 對稱)")

# ============ 9. 真 κ 驗證 3×12 ============
print("\n[9] 真 κ + J* 嘅 3×12 block (重驗)")
O53_POLY = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
with open(os.path.join(O53_POLY, "cy36_98_intersection_full.json")) as f:
    K = np.array(json.load(f)["kappa"])
with open(os.path.join(O53_POLY, "Jstar_36D.json")) as f:
    J0 = np.array(json.load(f)["Jstar_36D"])
Y = np.einsum("ijk,k->ij", K, J0)
Y = (Y + Y.T) / 2

# 3×12 block 對角化後嘅 12 維結構
# 檢查 block 0 嘅 rank
b0 = Y[0:12, 0:12]
print(f"  Block 0 rank: {np.linalg.matrix_rank(b0)}")
print(f"  Block 0 譜: {np.round(np.sort(np.linalg.eigvalsh(b0)), 3)}")
# 12 = B×N_gen 有冇體現? 3×4 結構?
# 檢查 4 個 3D sub-blocks (12 = 4×3)
sub = np.zeros((4, 4))
for i in range(4):
    for j in range(4):
        sub[i, j] = np.linalg.norm(b0[i*3:(i+1)*3, j*3:(j+1)*3])
print(f"  4×4 block norms (3D sub-blocks):")
print(np.round(sub, 3))
diag_ratio = (sub[0,0]+sub[1,1]+sub[2,2]+sub[3,3]) / (sub.sum() - (sub[0,0]+sub[1,1]+sub[2,2]+sub[3,3]))
print(f"  3D sub-block 對角/非對角: {diag_ratio:.3f}")
check("Block 0 有 4×3 結構 (4 = B)", diag_ratio > 1.5, f"({diag_ratio:.2f})")

print(f"\n{'='*72}")
print(f"Phase 5 結果: {passed} PASS, {failed} FAIL")
print(f"{'='*72}")
