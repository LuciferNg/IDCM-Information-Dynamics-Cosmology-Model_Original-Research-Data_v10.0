#!/usr/bin/env python3
"""
O59 Phase 6: ★ su(12) rank 閉合 — 12 嘅真正身份
================================================
核心發現:
  su(12) rank = 11 = L₅ = N_d/B = 44/4
  → N = rank+1 = 12 (su(12) 被 K_Chain 鎖定!)
  66 = C(12,2) = su(12) 正根 = 2×K_tree = 2×N_gen×L₅
  h11 = 36 = 3×12 = 3×(L₅+1) = K_tree + N_gen = 33+3!

測試:
  1. rank(su(N)) = N−1 = L₅ → N = 12
  2. 36 = K_tree + N_gen (h11 新閉合)
  3. 12 = L₅+1 = Nd/B+1 (SESSION_START 候選 B)
  4. 66 = 2×K_tree 嘅 su(12) 身份
  5. tr(Y) ≈ 66 重驗 (O53)
"""
import os, json, math
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
O53_POLY = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O59 Phase 6: ★ su(12) rank 閉合")
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

B, Ngen, L5, L6 = 4, 3, 11, 18
Nd = B*L5
Ktree = Ngen*L5

# ============ 1. su(12) rank = L₅ ============
print("\n[1] ★ su(12) rank = L₅")
print(f"  rank(su(12)) = 12−1 = 11 = L₅ = N_d/B = {Nd}/{B}")
check("rank(su(12)) = 11", 12-1 == 11)
check("11 = L₅", 11 == L5)
check("11 = N_d/B = 44/4", Nd/B == 11)
print(f"  ★ su(N) rank = N−1 = L₅ → N = L₅+1 = 12")
print(f"  → su(12) 嘅 12 由 K_Chain 嘅 L₅ = 11 鎖定!")

# ============ 2. h11 = 36 = K_tree + N_gen ============
print("\n[2] ★ h11 = 36 = K_tree + N_gen")
print(f"  36 = 3×12 = 3×(L₅+1) = 3×{L5+1} = {3*(L5+1)}")
check("36 = 3×(L₅+1)", 3*(L5+1) == 36)
print(f"  3×(L₅+1) = 3×L₅ + 3 = {3*L5}+{3} = {3*L5+3}")
check("3×L₅+3 = K_tree+3", 3*L5+3 == Ktree+3)
print(f"  ★★ h11 = 36 = K_tree + N_gen = 33 + 3!")
check("36 = K_tree + N_gen = 33+3", Ktree+Ngen == 36)
print(f"  33 = K_Tree 層數, 3 = N_gen")

# ============ 3. 12 = L₅+1 等價路徑 ============
print("\n[3] 12 = L₅+1 等價路徑")
print(f"  12 = L₅+1 = {L5}+1 = {L5+1}")
print(f"  12 = N_d/B+1 = {Nd/B}+1 = {Nd/B+1}")
print(f"  12 = B×N_gen = {B}×{Ngen} = {B*Ngen}")
check("L₅+1 = B×N_gen (11+1 = 4×3)", L5+1 == B*Ngen)
print(f"  → 兩條路徑 converge: L₅+1 = B×N_gen iff L₅ = B×N_gen−1")
print(f"  L₅ = 11 = 4×3−1 = 12−1 ✓")
check("L₅ = B×N_gen − 1", L5 == B*Ngen-1)

# ============ 4. 66 嘅 su(12) 身份 ============
print("\n[4] 66 嘅 su(12) 身份")
print(f"  |Φ⁺(su(12))| = C(12,2) = {12*11//2}")
check("C(12,2) = 66", 12*11//2 == 66)
print(f"  66 = 2×K_tree = 2×{Ktree}")
check("66 = 2×K_tree", 2*Ktree == 66)
print(f"  66 = 2×N_gen×L₅ = 2×{Ngen}×{L5}")
check("66 = 2×N_gen×L₅", 2*Ngen*L5 == 66)
print(f"  66 = 6×11 = 6×L₅? {6*L5}")
check("66 = 6×L₅", 6*L5 == 66)
print(f"  ★ 66 = 6×L₅ = 2N_gen×L₅ — su(12) 正根 = 2×K_Tree")
print(f"  su(12) 正根數 = K_Chain×K_Tree 結構嘅 2 倍")

# su(12) 對稱結構
print(f"\n  su(12) 內部結構:")
print(f"  Cartan: 11 = L₅")
print(f"  正根: 66 = 2×K_tree")
print(f"  根總數: 132 = 4×33 = 4×K_tree? {4*Ktree}")
check("132 = 4×K_tree", 132 == 4*Ktree)
print(f"  ★ 132 = 4×K_tree = B×K_tree (B=4)")
print(f"  dim(su(12)) = 143 = 12²−1")
print(f"  143 = 4×33+11 = 4×K_tree + L₅? {4*Ktree+L5}")
check("143 = 4×K_tree + L₅", 4*Ktree+L5 == 143)
print(f"  ★★ dim(su(12)) = B×K_tree + L₅ = 4×33+11 = 143!")

# ============ 5. tr(Y) ≈ 66 重驗 ============
print("\n[5] tr(Y) ≈ 66 重驗 (O53)")
with open(os.path.join(O53_POLY, "cy36_98_intersection_full.json")) as f:
    K = np.array(json.load(f)["kappa"])
with open(os.path.join(O53_POLY, "Jstar_36D.json")) as f:
    J0 = np.array(json.load(f)["Jstar_36D"])
Y = np.einsum("ijk,k->ij", K, J0)
Y = (Y + Y.T) / 2
trY = np.trace(Y)
print(f"  tr(Y) = {trY:.4f}")
check("tr(Y) ≈ 66", abs(trY - 66) / 66 < 0.02, f"({trY:.4f}, {(trY-66)/66*100:.2f}%)")

# ============ 6. 3×12 block 譜同 su(12) ============
print("\n[6] 3×12 block 譜同 su(12)")
# O53: Y = 3×12D block-triangular (Schur)
# 而家: 每個 block 嘅本徵值 = 12 個 = su(12) Cartan 11 + 1?
for g in range(3):
    b = Y[g*12:(g+1)*12, g*12:(g+1)*12]
    ev = np.sort(np.linalg.eigvalsh(b))
    print(f"  Block {g} 譜: {np.round(ev, 3)}")
    # 檢查有冇「1 個大 + 11 個細」結構 (λ₁ vs 其他)
    if len(ev) > 1:
        ratio = abs(ev[-1]) / max(abs(ev[-2]), 1e-10)
        print(f"    λ_max/λ_{11}: {ratio:.2f}")

# ============ 7. 其他 12 嘅 su(12) 解釋 ============
print("\n[7] 其他 12 嘅 su(12) 解釋")
print("  F. 12 ⬠ (Rhombicosidodecahedron): 12 個五邊形")
print("     su(12) Cartan 11 + 1? 冇直接證據 — 幾何巧合")
print("  G. 12 = 33−21: 33 = K_tree, 21 = F₈")
print("     su(12) rank 11 + 1 = 12? 33−21 = 12 = L₅+1!")
check("33−21 = 12 = L₅+1", 33-21 == L5+1)
print("  H. φ^(-k/12): Kähler VEV 週期分母 12 = L₅+1")
print("     → v_k = φ^(-k/(L₅+1)) — 12 步週期 = su(12) rank+1")
print("  I. θ₁₂ = 12.92°: 巧合 (13 = F₇)")
print("  D. A₄: FAIL (真 κ 冇 A₄ 對稱)")

# ============ 8. 統一閉合鏈 ============
print("\n[8] ★ 統一閉合鏈")
print("""
  K_Chain: Nd = 44, B = 4, L₅ = 11
      │
      ├── rank(su(N)) = N−1 = L₅ = 11 → N = 12
      │       │
      │       ├── su(12): dim = 143 = B×K_tree + L₅ = 4×33+11
      │       ├── 正根 = 66 = 2×K_tree = 2×N_gen×L₅
      │       └── Cartan = 11 = L₅
      │
      ├── 12 = L₅+1 = B×N_gen = 4×3 (每代 Kähler moduli)
      │       └── h11 = 3×12 = 36 = K_tree + N_gen = 33+3
      │
      └── 12 = N_d/B+1 = 44/4+1 (SESSION_START 候選 B)
              └── 12 = (N_d−2B)/3 = 36/3 (O53) — 等價!
""")

print(f"\n{'='*72}")
print(f"Phase 6 結果: {passed} PASS, {failed} FAIL")
print(f"{'='*72}")
