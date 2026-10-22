#!/usr/bin/env python3
"""
O55 第 4 輪: 324 Co-Closure — CKM beat web ↔ 3c 矩陣
=====================================================
主定理 (第 4 輪發現):
  Σ(16 個 CKM beat 指數) = 324
  = det(3c M)² = 18²
  = (B·N_gen)² + 2·Σγ(44-site) = 12² + 2×90 = 144 + 180
  = ΣC6 (cos 參數) + 2Σγ

副定理:
  Σγ(44-site) = 90  EXACT (K_Chain 全譜)
  Σγ(88-site)  = 176 EXACT (= δ_CKM 嘅 176-Laplacian 維度!)
  ΣD6 = 58 = 2L₇ = 88 − 30 (30 = 21+9 = δ 指數和)
  ΣC6 = 144 = F₁₂ = (B·N_gen)²

盲測評估:
  B1: 未用 7 對 Σ = 318 ≠ 324 (弱判別器)
  B2: 44-complement web Σ = 380 = 324 + B·||L||² (56)
"""
import math, sys
import numpy as np

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  ✅ {name} {detail}")
    else:    FAIL += 1; print(f"  ❌ {name} {detail}")

print("=" * 72)
print("O55 第 4 輪: 324 Co-Closure 定理")
print("=" * 72)

# CKM beat 8 對 (docs/04 §1)
pairs = [((5,6),(19,25)), ((33,35),(3,22)), ((42,43),(10,31)), ((2,23),(8,17))]
all_idx = [i for (a,b),(c,d) in pairs for i in (a,b,c,d)]
S_total = sum(all_idx)
print(f"\n  CKM 16 指數: {all_idx}")
print(f"  Σ(16) = {S_total}")

# 3c 矩陣
M = np.array([[0,-2,3],[2,-2,-1],[1,3,-2]], dtype=int)
detM = 18
print(f"\n  det(3c M) = {detM},  det(M)² = {detM**2}")
check("主定理 1: Σ(16) = det(M)² = 324", S_total == detM**2, f"({S_total})")

# Σγ
S44 = sum(4*math.sin(n*math.pi/88)**2 for n in range(1,45))
S88 = sum(4*math.sin(n*math.pi/88)**2 for n in range(1,89))
print(f"\n  Σγ(44-site) = {S44:.10f}")
print(f"  Σγ(88-site) = {S88:.10f}")
check("Σγ(44) = 90 EXACT", abs(S44-90) < 1e-9, f"({S44:.8f})")
check("Σγ(88) = 176 EXACT", abs(S88-176) < 1e-9, f"({S88:.8f})")

# 分解
B, Ngen = 4, 3
BN = B*Ngen
C6 = [3,11,20,25,41,44]
print(f"\n  (B·N_gen)² = {BN}² = {BN**2}")
print(f"  ΣC6 = {sum(C6)} = F12 = (B·N_gen)²")
print(f"  2Σγ(44) = {2*S44:.1f}")
print(f"  (B·N_gen)² + 2Σγ(44) = {BN**2 + 2*S44:.1f}")
check("主定理 2: (B·N_gen)² + 2Σγ(44) = 324", abs(BN**2 + 2*S44 - 324) < 1e-9,
      f"({BN**2 + 2*S44:.1f})")
check("ΣC6 = F12 = 144", sum(C6) == 144, f"({sum(C6)})")

# D6
D6 = sorted({abs(a-b) for (a,b),(c,d) in pairs} | {abs(c-d) for (a,b),(c,d) in pairs})
print(f"\n  ΣD6 = {sum(D6)} = 2L7 = 2×29")
check("ΣD6 = 58 = 2L7", sum(D6) == 58, f"({sum(D6)})")
check("88 − ΣD6 = 30 = 21+9 (δ 指數和)", 88 - sum(D6) == 21+9, f"({88-sum(D6)})")

# 176 = Σγ(88) = δ Laplacian 維度
print(f"\n  ★ Σγ(88-site) = 176 = δ_CKM 176-Laplacian 維度")
check("176 = 2×88 = Σγ(88-site) 同 δ 慣例一致", abs(S88-176) < 1e-9 and 176 == 2*88)

# ============================================================
print("\n" + "=" * 72)
print("[盲測]")
print("=" * 72)
# B1: 未用 7 對 (docs §8.1)
unused_idx = [1,25,1,41,2,44,6,68,9,11,9,41,19,41]
print(f"  未用 7 對指數和 = {sum(unused_idx)} vs 324")
print(f"  差異 = {abs(sum(unused_idx)-324)} (弱判別器)")
check("盲測: 未用 web 唔係 324 (弱支持選擇)", sum(unused_idx) != 324, f"({sum(unused_idx)})")
# B2: 44-complement
comp_idx = [44-i for i in all_idx]
print(f"  44-complement 指數和 = {sum(comp_idx)} = 324 + {sum(comp_idx)-324}")
coln = [int((M[:,j]**2).sum()) for j in range(3)]
print(f"  56 = B·||L||² = 4×14? {56 == 4*coln[2]}")
check("44-complement Σ = 324 + B·||L||²", sum(comp_idx) == 324 + 4*coln[2],
      f"({sum(comp_idx)})")

# ============================================================
print("\n" + "=" * 72)
print("總結")
print("=" * 72)
print(f"""
  324 Co-Closure 鏈:
    Σ(16 CKM beat 指數) = 324
        = det(3c M)² = 18²
        = (B·N_gen)² + 2·Σγ(44-site) = 12² + 2×90 = 144 + 180
        = ΣC6 + 2Σγ

  結構意義:
    - CKM 混合 web 嘅總指數預算 = 3c 電荷矩陣行列式²
    - 分解: (代×B)² [block 結構] + 2×鏈能量 [K_Chain]
    - Σγ(88) = 176 = δ_CKM 176-Laplacian 維度 (慣例一致)

  誠實標註:
    - 全部係精確整數 co-closure (兩邊都係觀察結構)
    - 機制 (點解 web 總和 = det²) 仍未推導
    - 盲測: 未用 web (318) 同 44-complement (380) 提供弱判別;
      真正 out-of-sample 預言仍待構造
""")
print(f"  {PASS} PASS / {FAIL} FAIL")
print("=" * 72)
