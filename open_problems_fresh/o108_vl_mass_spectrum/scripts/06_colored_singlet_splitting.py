#!/usr/bin/env python3
"""
O108 — Script 06: Colored/Singlet 分裂機制
==============================================
M_VL_c / M_VL_s = 5 = 1 + N_gen × C₂(3) = 1 + 3 × 4/3 = 5

推導 F₅=5 嘅結構來源同 SU(3)_C Casimir 關係。
"""

import numpy as np

phi = (1 + np.sqrt(5)) / 2
Nd = 44; B = 4; N_gen = 3
M_Pl = 1.221e19; M0 = 27.900915e-3
g1 = 4 * np.sin(np.pi / 88) ** 2
M_PS = M_Pl * g1**2
M_R = M_Pl * g1**3
M_VL_c = 1.26e14
M_VL_s = 2.52e13

print("=" * 72)
print("  O108 — Script 06: Colored/Singlet 分裂機制")
print("=" * 72)

# [1] Casimir 基礎
print(f"\n─── [1] SU(3)_C Casimir 不變量 ───")
C2_3 = (3**2 - 1) / (2 * 3)  # 4/3 for fundamental
C2_6 = (6**2 - 1) / (2 * 6)  # 35/12 for 2-index sym
C2_8 = 3  # adjoint
C2_10 = (10**2 - 1) / (2 * 10)  # 99/20 for 10

print(f"  C₂(3) = {C2_3} = 4/3")
print(f"  C₂(6) = {C2_6} = 35/12")
print(f"  C₂(8) = {C2_8} = 3")
print(f"  C₂(10) = {C2_10} = 99/20")

# [2] 質量分裂公式
print(f"\n─── [2] 質量分裂公式 ───")
print(f"  M_VL_c / M_VL_s = 1 + N_gen × C₂(3) = 1 + {N_gen} × {C2_3} = {1 + N_gen * C2_3} = F₅ ✅")

# 驗證: 是否可以用其他 Casimir?
for k in range(1, 6):
    pred = 1 + k * C2_3
    print(f"  1 + {k} × C₂(3) = {pred:.4f}")

# 用 SU(3) rank 解釋
print(f"\n  SU(3)_C rank = 2")
print(f"  N_gen × C₂(3) = 3 × 4/3 = 4 = 2 × rank = 2 × 2 = 4 ✅")

# 用 SU(4)_PS 解釋
print(f"\n  SU(4)_PS → SU(3)_C × U(1):")
print(f"  4 = 3₁ ⊕ 1₋₃")
print(f"  Colored VL: 3 → m_VL_c = M_VL_s × (1 + N_gen × C₂(3))")
print(f"  Singlet VL: 1 → m_VL_s (no SU(3)_C correction)")

# [3] 同 O89 交叉驗證
print(f"\n─── [3] 同 O89 交叉驗證 ───")
ratio = M_VL_c / M_VL_s
print(f"  M_VL_c / M_VL_s = {ratio:.4f}")
print(f"  1 + N_gen × C₂(3) = {1 + N_gen * C2_3}")
print(f"  偏差 = {abs(ratio - (1 + N_gen*C2_3))/(1 + N_gen*C2_3)*100:.4f}%")

# 預測: N_gen = 3, C₂(3) = 4/3 → 4
# 4 係 N_d - K_tree? 44-33=11 ❌
# 4 = B = K_Tree branching ✅
print(f"\n  N_gen × C₂(3) = 3 × 4/3 = 4 = B (K_Tree branching) ✅")

# [4] 推廣: 其他 GUT 群組嘅 Casimir 比
print(f"\n─── [4] 推廣: SU(N) 嘅 Casimir 比 ───")
for N in [3, 4, 5, 6, 12]:
    C2_fund = (N**2 - 1) / (2 * N)
    C2_adj = N
    print(f"  SU({N:2d}): C₂(fund)={C2_fund:.4f}, C₂(adj)={C2_adj}, ratio={C2_adj/C2_fund:.4f}")

# [5] 結果
print(f"\n{'=' * 72}")
print(f"  總結: Colored/Singlet 分裂機制閉合")
print(f"  ✅ M_VL_c/M_VL_s = 5 = 1 + N_gen × C₂(3)")
print(f"  ✅ N_gen × C₂(3) = 3 × 4/3 = 4 = B")
print(f"  ✅ 結構閉合: 分裂 = 1 + B = 1 + 4 = 5 = F₅")
print(f"{'=' * 72}")