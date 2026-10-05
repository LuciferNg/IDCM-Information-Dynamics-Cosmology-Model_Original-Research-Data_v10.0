#!/usr/bin/env python3
"""
O53 修正版投影算子: P̂_{CY₃} 重建 — 用 12 維 d_tensor 做 per-modulus weight
=============================================================================
問題: 原版 P̂ (134×946) rank-2 偽結構 (所有 Kähler 行相同)
修正: 用 d_tensor_final (12³, 真正三體耦合) 嘅結構做 per-modulus weight

設計:
  P̂_{α,(n,m)} = W_α(beat) × φ^(-γ(n,m)/3) × Z₃ 相位
  其中 W_α = 由 12 維 d_tensor 派生嘅 per-modulus 權重

目標: 真正 rank > 2, 且 66 個正本徵值係真物理譜 (唔係噪聲)

驗證:
  1. 秩應該遠大於 2
  2. 正本徵值應該有物理分佈 (唔係 1e-15 噪聲)
  3. 66 個「態」應該變成真正嘅 66 維結構
"""
import sys, os, math
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
sys.path.insert(0, os.path.join(BASE, "src"))

from projection_operator import (build_beat_hilbert_space, build_cy3_moduli_space,
                                  h11, h21, Nd)

phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53: 修正版投影算子 — per-modulus weight")
print("=" * 70)

# --- [1] 載入 12 維 d_tensor 做 weight 來源 ---
print("\n[1] 載入 d_tensor_final (12³):")
d12 = np.load(os.path.join(DATA, "d_tensor_final.npy"))
print(f"    shape: {d12.shape}")

# 從 d12 派生 12 維 weight 向量:
# w_i = Σ_jk d_ijk² (每行嘅總耦合強度)
w12 = np.einsum('ijk->i', d12**2)
w12 = w12 / w12.sum() * 12  # normalize
print(f"    12 維 weight: {np.array2string(w12, precision=4)}")

# 擴展到 36 (Kähler) + 98 (CPX)
# Kähler: 每 3 個 moduli 共用 1 個 Z₃ orbit weight
w_kahler = np.repeat(w12, 3)  # 36
# CPX: 用 φ 指數衰減 (98 個)
w_cpx = np.array([phi ** (-i / 98) for i in range(98)])  # 98

print(f"    Kähler weight (36): 範圍 [{w_kahler.min():.4f}, {w_kahler.max():.4f}]")
print(f"    CPX weight (98): 範圍 [{w_cpx.min():.4f}, {w_cpx.max():.4f}]")

# --- [2] 構建修正投影矩陣 ---
print("\n[2] 構建修正 P̂ (134×946):")
beats = build_beat_hilbert_space()
moduli = build_cy3_moduli_space()
P_new = np.zeros((134, 946))

for α, mod in enumerate(moduli):
    # per-modulus weight
    if mod.type == 'kahler':
        w_mod = w_kahler[mod.hodge_index]
    else:
        w_mod = w_cpx[mod.hodge_index]

    for β, beat in enumerate(beats):
        # 選擇律 (保留原本物理規則)
        if mod.parity != beat.parity:
            continue
        if mod.z2_charge != beat.z2_charge:
            continue

        q1, q2 = beat.quadrant
        if mod.type == 'kahler' and q1 > 2 and q2 > 2:
            continue
        if mod.type == 'cpx' and q1 < 3 and q2 < 3:
            continue

        gamma_n = 4 * math.sin(math.pi * beat.n / 88) ** 2
        gamma_m = 4 * math.sin(math.pi * beat.m / 88) ** 2
        avg_gamma = (gamma_n + gamma_m) / 2

        if mod.type == 'kahler' and avg_gamma > 2.0:
            continue
        if mod.type == 'cpx' and avg_gamma < 2.0:
            continue

        # 核心修正: per-modulus weight × 幾何因子
        if mod.type == 'kahler':
            weight = w_mod * phi ** (-avg_gamma)
        else:
            weight = w_mod * math.exp(-1.0 / avg_gamma)

        P_new[α, β] = weight

print(f"    P_new shape: {P_new.shape}")
print(f"    非零元素: {np.count_nonzero(P_new)} / {P_new.size}")

# --- [3] 秩驗證 ---
print("\n[3] 修正版秩分析:")
rank = np.linalg.matrix_rank(P_new, tol=1e-10)
print(f"    SVD 秩 (tol=1e-10): {rank}")

PPT = P_new @ P_new.T
evals, evecs = np.linalg.eigh(PPT)
evals_sorted = np.sort(evals)[::-1]
n_pos = np.sum(evals > 1e-10)
n_pos_loose = np.sum(evals > 1e-15)
print(f"    正本徵值 (>1e-10): {n_pos}")
print(f"    正本徵值 (>1e-15): {n_pos_loose}")
print(f"    最大 10 個:")
for i in range(min(10, len(evals_sorted))):
    print(f"      λ_{i+1:2d} = {evals_sorted[i]:.6e}")

# 本徵值譜結構
print(f"\n    本徵值分佈 (log10):")
log_ev = np.log10(evals[evals > 1e-15])
hist, edges = np.histogram(log_ev, bins=10)
for h, e1, e2 in zip(hist, edges[:-1], edges[1:]):
    print(f"      [{e1:8.2f}, {e2:8.2f}): {'#' * min(h, 40)} ({h})")

# --- [4] Kähler/CPX 子矩陣秩 ---
print("\n[4] 子矩陣秩:")
P_k = P_new[:36, :]
P_c = P_new[36:, :]
print(f"    Kähler (36×946) 秩: {np.linalg.matrix_rank(P_k, tol=1e-10)}")
print(f"    CPX (98×946) 秩: {np.linalg.matrix_rank(P_c, tol=1e-10)}")

# 行間相關性 (應該 < 1.0 而家!)
print(f"\n    行間相關性 (修正後):")
rng = np.random.default_rng(0)
cors = []
for _ in range(30):
    i, j = rng.integers(0, 36, 2)
    if i == j: continue
    mask = (P_k[i] != 0) & (P_k[j] != 0)
    if mask.sum() > 3:
        cors.append(np.corrcoef(P_k[i][mask], P_k[j][mask])[0, 1])
cors = np.array(cors)
print(f"    Kähler 行 corr: mean={cors.mean():.4f}, max={cors.max():.4f}")

# --- [5] 66 個態嘅物理內容 ---
print("\n[5] 修正版「66 態」檢查:")
if n_pos >= 66:
    top66 = evals_sorted[:66]
    print(f"    前 66 個本徵值範圍: [{top66[-1]:.4e}, {top66[0]:.4e}]")
    print(f"    最小/最大比: {top66[-1]/top66[0]:.2e}")
    print(f"    → {'✅ 有真正 66 維結構' if top66[-1] > 1e-6 else '⚠️ 尾部仍係噪聲'}")

# --- [6] 保存修正版 ---
np.save(os.path.join(DATA, "P_fixed.npy"), P_new)
print(f"\n[6] 修正版保存: data/P_fixed.npy")

print("\n" + "=" * 70)
print("【結果】")
print("=" * 70)
print(f"""
  原版 P̂:   rank = 2 (偽結構)
  修正版 P̂: rank = {rank}
  正本徵值: {n_pos} (>1e-10)
  {'✅ 修正成功 — 真正 per-modulus 結構' if rank > 10 else '❌ 修正失敗'}
""")
print("=" * 70)
