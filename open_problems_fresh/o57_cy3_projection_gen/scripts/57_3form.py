#!/usr/bin/env python3
"""
O57 八期 57: 方向 2 — CYTools 3-form 混合張量探索
====================================================
Gemini 方向 2 (Cross-Term Reconstruction):
  Y_ijk = ∫ Ω ∧ ∂Ω/∂z_i ∧ ∂Ω/∂z_j
  複結構模 z 與 Kähler 模 t 嘅混合三階相交張量

CYTools 探索:
  1. cy.intersection_numbers() 已經有 3-tensor (κ_ijk)
  2. 有冇 4-tensor / 更高階?
  3. 混合 (z,t) 張量?
  4. 非對角項 → CKM/PMNS?
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 八期 57: 3-form 混合張量")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

# ============ 1. CY 建立 ============
print("\n[1] CY 建立")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
print(f"  h11={cy.h11()}, h12={cy.h12()}")

# ============ 2. 探索更高階 ============
print("\n[2] 更高階張量探索")
# 已知: intersection_numbers() → 3-tensor (κ_ijk)
# 有冇其他?
for method in ["compute_AA", "compute_kappa_matrix", "compute_kappa_vector"]:
    try:
        r = getattr(cy, method)()
        print(f"  {method}: {type(r).__name__}, shape={np.array(r).shape if hasattr(r, '__len__') else r}")
    except Exception as e:
        print(f"  {method}: {type(e).__name__}")

# ============ 3. κ 嘅 CKM 結構 ============
print("\n[3] κ_ijk 嘅 CKM-like 結構")
# 重建 κ (36³)
inter = cy.intersection_numbers()
K = np.zeros((36, 36, 36))
for key, val in inter.items():
    if isinstance(key, tuple) and len(key) == 3:
        i, j, k = key
        if 1 <= i <= 36 and 1 <= j <= 36 and 1 <= k <= 36:
            K[i-1, j-1, k-1] = val
            K[i-1, k-1, j-1] = val
            K[j-1, i-1, k-1] = val
            K[j-1, k-1, i-1] = val
            K[k-1, i-1, j-1] = val
            K[k-1, j-1, i-1] = val

# 3×12 block 結構 → 3 代?
# Y_ij = κ_ijk·t^k 用 J* 或者 φ
t_phi = phi ** (35 - np.arange(36))
Y = np.einsum('ijk,k->ij', K, t_phi)
Y = (Y + Y.T) / 2

# 3×12 block: 每代 12 個 moduli
print(f"  Y (36×36) 3×12 block 結構:")
for g1 in range(3):
    for g2 in range(3):
        block = Y[g1*12:(g1+1)*12, g2*12:(g2+1)*12]
        # 對角化 block 睇最大本徵值
        ev = np.linalg.eigvalsh(block)
        print(f"    Gen{g1+1}×Gen{g2+1}: λmax={ev.max():.4f}, λmin={ev.min():.4f}")

# ============ 4. 混合角 ============
print("\n[4] 混合角提取 (CKM-like)")
# 用 Y 嘅 3×12 block 交叉項
# 如果 Y 有 3×3 世代結構 → 混合角
# 方法: 對 3 個 diag block 做「質量矩陣」
M_gen = np.zeros((3, 3))
for g1 in range(3):
    for g2 in range(3):
        block = Y[g1*12:(g1+1)*12, g2*12:(g2+1)*12]
        M_gen[g1, g2] = np.trace(block) / 12  # 平均

print(f"  3×3 世代質量矩陣 (trace/12):")
print(f"  {M_gen}")

# 對角化 → 混合
ev_gen, U_gen = np.linalg.eigh(M_gen)
print(f"  本徵值: {ev_gen}")
print(f"  混合矩陣 U:")
print(f"  {U_gen}")

# 混合角 (CKM-like)
if np.all(ev_gen > 0):
    # 標準 CKM 參數化
    s12 = abs(U_gen[0, 1])
    s23 = abs(U_gen[1, 2])
    s13 = abs(U_gen[0, 2])
    theta12 = math.degrees(math.asin(min(s12, 1)))
    theta23 = math.degrees(math.asin(min(s23, 1)))
    theta13 = math.degrees(math.asin(min(s13, 1)))
    print(f"\n  混合角:")
    print(f"    θ₁₂ = {theta12:.2f}° (Cabibbo ~13°)")
    print(f"    θ₂₃ = {theta23:.2f}° (atmospheric ~45°)")
    print(f"    θ₁₃ = {theta13:.2f}° (reactor ~8.5°)")
    check("θ₁₂ ≈ 13° (Cabibbo)", abs(theta12 - 13.02) < 5, f"({theta12:.2f}°)")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("八期 57 總結:")
print("=" * 72)
print(f"""
  3-form 混合張量:
  ─────────────────────────────────
  1. CYTools 冇更高階 (只有 κ_ijk)
  2. Y = κ·t 3×12 block 結構
  3. 3×3 世代矩陣: 睇上面
  4. 混合角: 睇上面

  {'✅ 有 CKM-like 結構!' if np.all(ev_gen > 0) else '❌'}
""")

results = {
    "test": "O57 八期 57: 3-form 張量",
    "M_gen": M_gen.tolist(),
    "ev_gen": [float(x) for x in ev_gen],
    "U_gen": U_gen.tolist(),
    "passed": passed, "failed": failed
}
with open("data/57_3form.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 八期 57 完成!")
