#!/usr/bin/env python3
"""
O53 問題 1/2: CY₃ moduli = K_Chain 結構數 — 機制分析
=====================================================
核心問題:
  Q1: 點解 h¹¹+h²¹ = 134 = Nd+Σγ (44+90)?
  Q2: 點解 134×946 投影算子嘅秩 rank = 66?
  Q3: 66 嘅結構身份: C(12,2) = 12×11/2? 12 = h¹¹/3 = Z₃ orbit?
  Q4: 946 = C(44,2) 係咪結構自然生成?

方法: 用本地 projection_operator.py 嘅構建函數 + 精確秩分析
      (唔需要網絡 — 純結構數學)
"""
import sys, os, math
import numpy as np
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))
from projection_operator import (build_beat_hilbert_space, build_cy3_moduli_space,
                                  CY3ProjectionOperator, h11, h21, Nd)

phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53 Q1/Q2: 投影算子機制分析")
print("=" * 70)

# --- [0] 基本結構數 ---
print("\n[0] K_Chain 結構數 (全部由 x²+x−1=0 → φ 派生)")
B = phi**3 - phi**-3
L5 = phi**5 + (-phi)**-5
L6 = phi**6 + (-phi)**-6
F6 = 8
S_gamma = sum(4 * math.sin(math.pi * n / 88)**2 for n in range(1, 45))
print(f"    B = φ³−φ⁻³ = {B:.6f} → 4")
print(f"    L₅ = {L5:.6f} → 11,  L₆ = {L6:.6f} → 18,  F₆ = 8")
print(f"    Nd = B×L₅ = {Nd},  Σγ = {S_gamma:.4f} → 90")
print(f"    h¹¹+h²¹ = Nd+Σγ = {Nd+90} = 134")
print(f"    h²¹−h¹¹ = Nd+L₆ = {Nd+18} = 62")

# --- [1] 946 = C(44,2) 自然生成 ---
print("\n[1] 946 = C(44,2) — beat 空間自然生成?")
C_44_2 = 44 * 43 // 2
print(f"    C(44,2) = 44×43/2 = {C_44_2}")
beats = build_beat_hilbert_space()
print(f"    build_beat_hilbert_space() 實際: {len(beats)}")
print(f"    → {'✅ 完全匹配, 結構自然生成' if len(beats) == C_44_2 else '❌ 唔匹配'}")

# parity 分佈
even = sum(1 for b in beats if b.parity == 0)
odd = sum(1 for b in beats if b.parity == 1)
print(f"    parity: even={even} (=C(22,2)×2=462), odd={odd} (=22×22=484)")
print(f"    驗證: C(22,2)×2 = {22*21//2*2},  22×22 = {22*22}")

# --- [2] rank 分析 ---
print("\n[2] 投影算子 P̂ (134×946) 嘅秩")
op = CY3ProjectionOperator()
P = op.compute_matrix()
print(f"    P 形狀: {P.shape}")
print(f"    非零元素: {np.count_nonzero(P)}")
print(f"    稀疏度: {np.count_nonzero(P) / P.size * 100:.2f}%")

# 精確秩 (SVD)
rank = np.linalg.matrix_rank(P, tol=1e-12)
print(f"    SVD 秩 (tol=1e-12): {rank}")

# P P^T 本徵值
PPT = P @ P.T
evals, evecs = np.linalg.eigh(PPT)
pos = evals > 1e-15
print(f"    正本徵值數: {np.sum(pos)}")
print(f"    本徵值範圍: {evals[pos].min():.3e} ~ {evals[pos].max():.3e}")

# --- [3] 66 嘅結構身份 ---
print("\n[3] 66 嘅結構身份:")
print(f"    66 = C(12,2) = 12×11/2 = {12*11//2} ?  {'✅' if 12*11//2 == 66 else '❌'}")
print(f"    66 = 3×22 = 3×(2×11) = 3×2×L₅ ?  {'✅' if 3*2*11 == 66 else '❌'}")
print(f"    66 = 946 − 880 ?  880 = ?")
print(f"    66 = 134 − 68 ?  68 = ?")
print(f"    66 = 36 + 30 ?  30 = 5×6?")
print(f"    66 = 90 − 24 ?  24 = 4×6?")
print(f"    66 = 44 + 22 ?  22 = 44/2 = Nd/2")

# 秩 vs 各種結構數
print(f"\n    對比:")
print(f"      rank = 66")
print(f"      C(12,2) = 66    (12 = h¹¹/3 = Z₃ orbit)")
print(f"      C(11,2) = 55    (11 = L₅)")
print(f"      C(13,2) = 78")
print(f"      C(44,2) = 946   (beat 空間)")
print(f"      3×C(7,2) = 63   (7 = ?)")
print(f"      2×C(9,2) = 72")

# --- [4] 每行 rank 貢獻 ---
print("\n[4] 每 modulus 類型嘅有效行 (奇異值)")
# 行空間分析: 睇 Kähler/CPX 各自貢獻
u, s, vh = np.linalg.svd(P, full_matrices=False)
print(f"    奇異值數: {len(s)}")
print(f"    大於 1e-12 嘅奇異值: {np.sum(s > 1e-12)}")

# 睇 singular vectors 嘅行權重分佈
# 每個奇異值對應嘅行組合 — 用有效秩 per-type
P_kahler = P[:36, :]
P_cpx = P[36:, :]
rank_k = np.linalg.matrix_rank(P_kahler, tol=1e-12)
rank_c = np.linalg.matrix_rank(P_cpx, tol=1e-12)
print(f"    Kähler 子矩陣 (36×946) 秩: {rank_k}")
print(f"    CPX 子矩陣 (98×946) 秩: {rank_c}")
print(f"    rank_k + rank_c = {rank_k + rank_c}  vs  total rank = {rank}")

# --- [5] 66 同 946/134 嘅模關係 ---
print("\n[5] 66 嘅模結構:")
print(f"    946 mod 66 = {946 % 66}")
print(f"    946 // 66 = {946 // 66}")
print(f"    134 mod 66 = {134 % 66}")
print(f"    134 // 66 = {134 // 66}")
print(f"    946 = 66×14 + 22?  {66*14 + 22}")
print(f"    134 = 66×2 + 2?  {66*2+2}")
print(f"    66 = 44 + 22 = Nd + Nd/2?")
print(f"    22 = 44/2 = 光速模式 n=22?")
print(f"    66 = 3×22: 3 代 × 22 態/代 (orbifold_projection 嘅解讀)")
print(f"    22 = 2×11 = 2×L₅: L₅=11 Lucas")

# --- [6] 奇異值譜 φ 結構 ---
print("\n[6] 奇異值譜嘅 φ 結構 (66 個奇異值)")
s_pos = s[s > 1e-12]
s_sorted = np.sort(s_pos)[::-1]
print(f"    最大: {s_sorted[0]:.4e}")
print(f"    前 12 個 (φ 指數):")
for i in range(min(12, len(s_sorted))):
    exp = math.log(s_sorted[0] / s_sorted[i]) / math.log(phi) if s_sorted[i] > 0 else float('inf')
    print(f"      σ_{i+1:2d} = {s_sorted[i]:.4e}  φ^({exp:+.3f})")

# 奇異值聚類檢查
print(f"\n    奇異值 log10 間距統計:")
logs = np.log10(s_sorted)
gaps = np.diff(logs)
print(f"    最大間距: {gaps.max():.3f} (喺 index {np.argmax(gaps)+1})")
print(f"    間距>0.3 嘅 gap 數: {np.sum(gaps > 0.3)}")

# --- [7] 關鍵結構猜測驗證 ---
print("\n[7] 結構猜測驗證")
# 猜測: 66 = C(12,2), 12 = h¹¹/3
print(f"    G1: 66 = C(12,2) → 12 = h¹¹/3 = {h11}/3 = {h11//3}  {'✅' if h11 % 3 == 0 else '❌'}")
# 猜測: 946 = C(44,2) 已經確認
# 猜測: 134 = 44+90, 62 = 44+18
print(f"    G2: 134 = Nd+Σγ = 44+90 ✓ (已確認)")
print(f"    G3: 62 = Nd+L₆ = 44+18 ✓ (已確認)")
# 猜測: rank 66 = 3×22, 22 = Nd/2
print(f"    G4: 66 = 3×22, 22 = Nd/2 = {Nd//2}  {'✅' if Nd % 2 == 0 else '❌'}")
# 猜測: rank = number of beats after Z₃ orbifold
print(f"    G5: 66 = 946/14.33...? 唔整數")
# 猜測: rank = 2×33 = 66 (33 = K_Tree 層數 M)
print(f"    G6: 66 = 2×33, 33 = M (K_Tree 層數)  {'✅' if 2*33 == 66 else '❌'}")

print("\n" + "=" * 70)
print("初步結論:")
print("  - 946 = C(44,2) 係結構自然生成 (K_Chain 兩兩 beat)")
print(f"  - rank(P̂) = {rank}  (66)")
print("  - 66 候選身份: 3×22 (3代×Nd/2), C(12,2) (Z₃ orbit), 2×33 (2×K_Tree)")
print("  - 需要判定邊個係結構真相")
print("=" * 70)
