#!/usr/bin/env python3
"""
O55 — c_f = n/3: SU(3)_c Z_3 Center Analysis
=============================================
核心問題: 點解 c_f ∈ {±1, ±2/3, ±1/3, 0} 全部係 1/3 倍數？
假設: 「3」= SU(3)_c 嘅中心 Z_3

三條推導鏈:
  A. SU(3) Z_3 中心 → 1/3 量子化
  B. 3c 矩陣嘅 Z_3 結構分析
  C. 3 代 ↔ 3 個 Z_3 類別

Reference: O53 docs/15, docs/12, scripts/45, scripts/125
"""

import numpy as np
from scipy import linalg
import math, sys, json

phi = (1 + math.sqrt(5)) / 2
PASS = 0; FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  ✅ {name} {detail}")
    else:
        FAIL += 1; print(f"  ❌ {name} {detail}")

print("=" * 70)
print("O55 01: SU(3)_c Z_3 Center — c_f = n/3 結構分析")
print("=" * 70)

# ============================================================
# [A] SU(3) Z_3 中心代數
# ============================================================
print("\n" + "-" * 70)
print("[A] SU(3) Z_3 中心代數")
print("-" * 70)

# Z_3 = {e^{2πik/3} : k=0,1,2} = {1, ω, ω²}
z3 = [1, complex(-0.5, math.sqrt(3)/2), complex(-0.5, -math.sqrt(3)/2)]
print(f"\n  Z_3 = {{1, ω, ω²}}")
print(f"  ω = {z3[1]}")
print(f"  ω² = {z3[2]}")
print(f"  ω³ = {z3[1]**3:.6f}")

# SU(3) 表示嘅 triality
# 3 → triality 1 (ω)
# 3̄ → triality 2 (ω²)
# 1 → triality 0 (1)
# adjoint 8 → triality 0
print(f"\n  SU(3) 表示 Z_3 電荷:")
print(f"    3 (fundamental):     triality 1 → ω")
print(f"    3̄ (anti-fund):      triality 2 → ω²")
print(f"    1 (singlet):        triality 0 → 1")
print(f"    8 (adjoint):        triality 0 → 1")

# SM 粒子嘅 Z_3 分類
# Quarks: 3 → ω; Leptons: 1 → 1
print(f"\n  SM 粒子 Z_3 類別:")
print(f"    Quarks (3):  Z_3 = ω  (triality 1)")
print(f"    Leptons (1): Z_3 = 1  (triality 0)")

# Z_3 中心 → 1/3 量子化
# 如果 c_f = n/3, 個「3」來自 Z_3 嘅階
print(f"\n  Z_3 階 = 3 → 1/3 量子化:")
print(f"    c_f = n/3, n ∈ Z")
print(f"    3c_f ∈ Z (整數)")
print(f"    3c_f = triality × gen_charge + ...")

# 3c_f 整數性驗證
cf_values = [0, -2/3, 1, 2/3, -2/3, -1/3, 1/3, 1, -2/3]
cf3_values = [int(round(3*c)) for c in cf_values]
print(f"\n  c_f 值: {cf_values}")
print(f"  3c_f 值: {cf3_values}")
check("所有 3c_f 係整數", all(v == round(v) for v in [3*c for c in cf_values]))

# ============================================================
# [B] 3c 矩陣結構分析
# ============================================================
print("\n" + "-" * 70)
print("[B] 3c 矩陣結構分析")
print("-" * 70)

# 3c 矩陣 M: 3 代 × 3 電荷型 (u,d,e)
# 來自 README: [[0,-2,3], [2,-2,-1], [1,3,-2]]
M = np.array([[0, -2, 3],
              [2, -2, -1],
              [1, 3, -2]], dtype=int)

print(f"\n  3c 矩陣 M:")
print(f"  {M[0]}  ← gen1 (u, d, e)")
print(f"  {M[1]}  ← gen2 (c, s, μ)")
print(f"  {M[2]}  ← gen3 (t, b, τ)")

# 基本不變量
det_M = round(np.linalg.det(M))
sum_M = np.sum(M)
sum2_M = np.sum(M**2)
trace_M = np.trace(M)
print(f"\n  不變量:")
print(f"    det(M) = {det_M} = 2×3² = 18")
print(f"    tr(M) = {trace_M}")
print(f"    Σ(M) = {sum_M}")
print(f"    Σ(M²) = {sum2_M} = h11 = 36")

check("det(M) = 18 = 2×3²", det_M == 18, f"({det_M})")
check("Σ(M²) = 36 = h11", sum2_M == 36, f"({sum2_M})")
check("Σ(M) = 2 = μ²", sum_M == 2, f"({sum_M})")

# 行 (generation) 結構
print(f"\n  Row sums (generation sum):")
for i, label in enumerate(["gen1 (u,d,e)", "gen2 (c,s,μ)", "gen3 (t,b,τ)"]):
    s = np.sum(M[i])
    print(f"    {label}: Σ = {s}")

# 列 (charge type) 結構
print(f"\n  Column sums (charge type):")
for j, label in enumerate(["U (up-type)", "D (down-type)", "L (lepton)"]):
    s = np.sum(M[:, j])
    print(f"    {label}: Σ = {s}")

# 關鍵: D 列模式 — d,s = -2, b = 3
d_col = M[:, 1]
print(f"\n  D column (down-type): {d_col}")
print(f"    d: 3c={d_col[0]}, s: 3c={d_col[1]}, b: 3c={d_col[2]}")
check("D column: d,s = -2, b = 3", d_col[0]==-2 and d_col[1]==-2 and d_col[2]==3, f"({d_col.tolist()})")
print(f"    d,s 同值 (-2), b 不同 (3) → 三代結構: gen1=gen2 ≠ gen3")

# U 列 = {0, 1, 2} = Z_3 完整集合
u_col = sorted(M[:, 0])
print(f"\n  U column (up-type): {M[:, 0]}")
check("U column = Z_3 完整集合 {0,1,2}", u_col == [0, 1, 2], f"({u_col})")

# L 列 = {-2, -1, 3} = 另一個 Z_3 完整集合 (-2≡1, -1≡2, 3≡0 mod 3)
l_col = sorted(M[:, 2])
l_mod3 = sorted([x % 3 for x in M[:, 2]])
print(f"\n  L column (lepton): {M[:, 2]}")
print(f"  L column mod 3: {l_mod3}")
check("L column mod 3 = Z_3 完整集合 {0,1,2}", l_mod3 == [0, 1, 2], f"({l_mod3})")

# ============================================================
# [C] Z_3 循環結構
# ============================================================
print("\n" + "-" * 70)
print("[C] Z_3 循環結構 — 世代循環")
print("-" * 70)

# 定義循環置換 P: gen1→gen2→gen3→gen1
P = np.array([[0, 0, 1],
              [1, 0, 0],
              [0, 1, 0]], dtype=int)

print(f"\n  循環置換 P (gen1→gen2→gen3→gen1):")
print(f"  {P[0]}")
print(f"  {P[1]}")
print(f"  {P[2]}")
check("P³ = I", np.allclose(P @ P @ P, np.eye(3)))

# P·M = ?
PM = P @ M
print(f"\n  P·M (循環後 3c 矩陣):")
print(f"  {PM[0]}")
print(f"  {PM[1]}")
print(f"  {PM[2]}")

# 比較 M 同 P·M
print(f"\n  M vs P·M — 循環下 3c 矩陣嘅變化:")
print(f"  M 的 U 列: {M[:, 0]}")
print(f"  PM 的 U 列: {PM[:, 0]}")
print(f"  M 的 D 列: {M[:, 1]}")
print(f"  PM 的 D 列: {PM[:, 1]}")
print(f"  M 的 L 列: {M[:, 2]}")
print(f"  PM 的 L 列: {PM[:, 2]}")

# 循環下, U 列循環置換, D 列亂序, L 列循環置換
print(f"\n  D column 喺循環下:")
print(f"    {M[:, 1].tolist()} → {PM[:, 1].tolist()}")
print(f"    D = [-2, -2, 3] 唔係常數, 所以循環下會亂")
print(f"    → 但 D 列只有 2 個不同值, 唔係 3 個")
print(f"    → d,s 同值 (-2) 暗示: 下型夸克嘅 c_f 由 K_Chain 結構決定?")

# U 列循環置換: [0,2,1] → [1,0,2] → [2,1,0] → [0,2,1]
print(f"\n  U column 循環軌跡:")
u_cycle = [M[:, 0].tolist()]
u_cur = M[:, 0].copy()
for _ in range(2):
    u_cur = P @ u_cur
    u_cycle.append(u_cur.tolist())
print(f"    {u_cycle[0]} → {u_cycle[1]} → {u_cycle[2]} → ...")
print(f"    Z_3 orbit: {sorted(set(tuple(c) for c in u_cycle))}")
check("U column 3-cycle", len(set(tuple(c) for c in u_cycle)) == 3 or len(set(tuple(c) for c in u_cycle)) == 1)

# 3c 矩陣嘅 Z_3 特徵分解
print(f"\n  Z_3 特徵分解:")
evals, evects = np.linalg.eig(M)
print(f"    本徵值: {evals}")
print(f"    本徵值模: {[abs(e) for e in evals]}")

# 3c 矩陣唔係循環對稱, 但 n/3 結構仍成立
print(f"    → 3c 矩陣嘅本徵值唔係 Z_3 根 (1, ω, ω²)")
print(f"    → 証實 O53 發現: Z_3 循環對稱被排除 (scripts/50)")
print(f"    → 但 n/3 量子化仍成立, 所以 Z_3 係「量子化」機制唔係「對稱」機制")
check("3c 矩陣本徵值非 Z_3 根", 
      all(abs(e - z3[0]) > 1e-6 for e in evals) and
      all(abs(e - z3[1]) > 1e-6 for e in evals),
      "(Z_3 循環對稱排除)")

# ============================================================
# [D] 3×12 Block 結構同 Z_3 嘅連結
# ============================================================
print("\n" + "-" * 70)
print("[D] 3×12 Block 結構 → c_f = n/3")
print("-" * 70)

# 36 = 3 × 12 = Nd − 2B
Nd, B = 44, 4
h11 = Nd - 2*B
print(f"  h11 = {h11} = Nd − 2B = 44 − 8 = 36")
print(f"  12 = h11/3 = (Nd−2B)/3")
print(f"  → 36 Kähler moduli 分 3 個 12D block")

# 3×12 = 3 代嘅幾何證明
# 每個 block 12D = 12 Kähler moduli = 1 代嘅「幾何層」
print(f"\n  3×12 block 結構:")
print(f"    Block i (i=0,1,2): 12 個 moduli")
print(f"    Σ 3×12 = 36 = h11 ✅")
print(f"    c_f = n/3 → 3 個 block × 1/3 電荷結構")

# 係咪每個 block 貢獻一個 generation?
# 如果係, 咁 c_f = n/3 嘅「3」= 3 個 block
print(f"\n  假設: c_f = n/3 嘅「3」= 3 個 12D block")
print(f"    → 每個 block 對應一個 generation")
print(f"    → 3 個 block = 3 代")
print(f"    → c_f = n/3 嘅 n 由 block 內嘅 moduli 結構決定")

# 檢查: 12 同 SU(3) 嘅關係
# 12 = 4 × 3, 4 = SU(4) 味對稱, 3 = SU(3)_c
print(f"\n  12 = 4 × 3:")
print(f"    4 = SU(4) flavor (4 generations? 但 SM 只有 3 代)")
print(f"    3 = SU(3)_c color")
print(f"    (3, 4) = SU(3)_c × SU(4) 雙表示")

# ============================================================
# [E] 總結: 結構推導
# ============================================================
print("\n" + "-" * 70)
print("[E] 結構推導總結")
print("-" * 70)

print(f"""
  Z_3 中心 → 1/3 量子化:
    SU(3)_c 嘅中心 Z_3 有階 3
    → 所有 SU(3)_c 表示嘅 triality 係 Z_3 值
    → c_f = n/3 嘅「3」= |Z_3|

  3c 矩陣嘅 Z_3 結構:
    U column: {{0, 1, 2}} = Z_3 完整集合 ✅
    D column: {{-2, -2, 3}} = d,s 同值, b 不同 ✅
    L column: {{-2, -1, 3}} = Z_3 完整集合 (mod 3) ✅
    det(M) = 18 = 2×3² ✅
    Σ(M²) = 36 = h11 ✅

  3×12 到 3 代:
    h11 = 36 = 3 × 12
    12 = (Nd−2B)/3
    → 3 個 12D block = 3 代嘅幾何起源
    → c_f = n/3 嘅「3」= 3 個 block / 3 代

  🔴 未解決:
    □ 點解 n 嘅具體值係 {{−2,−1,0,1,2,3}} 唔係其他?
    □ D column 點解常數 -2?
    □ U/L column 嘅 Z_3 排列點解係特定次序?
    □ 3×12 block 同 3c 矩陣嘅直接連結?
""")

# ============================================================
# 結果
# ============================================================
print("=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)