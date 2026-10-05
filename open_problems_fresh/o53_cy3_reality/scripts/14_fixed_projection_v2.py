#!/usr/bin/env python3
"""
O53 修正版投影算子 v2: 真正 per-modulus 行向量
================================================
問題: 乘性 weight 唔會改變秩 (行縮放 = 線性相關保留)
修正: 每個 modulus 用「獨特嘅 beat 子集」— 由佢嘅 (n,m) 模式決定

關鍵結構:
  946 beats = C(44,2) 全部 (n,m) pairs
  36 Kähler moduli → 每個對應特定 (n,m) 子集 (由 d_tensor 結構決定)
  98 CPX moduli → 每個對應唔同 beat 子集

真正 per-modulus 依賴 = 唔同嘅 beat 支撐 (support)
"""
import sys, os, math
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
sys.path.insert(0, os.path.join(BASE, "src"))

from projection_operator import build_beat_hilbert_space, build_cy3_moduli_space

phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53: 修正版投影算子 v2 — 真正 per-modulus 行向量")
print("=" * 70)

beats = build_beat_hilbert_space()
moduli = build_cy3_moduli_space()
n_beats = len(beats)   # 946
n_moduli = len(moduli) # 134

# --- [1] beat 標籤: 每個 beat 有 (n, m) ---
print("\n[1] beat 空間結構:")
beat_n = np.array([b.n for b in beats])
beat_m = np.array([b.m for b in beats])
beat_parity = np.array([b.parity for b in beats])
beat_z2 = np.array([b.z2_charge for b in beats])

# --- [2] 構建真正 per-modulus 行 ---
print("\n[2] 構建真正 per-modulus 行向量:")
P = np.zeros((134, 946))

for α, mod in enumerate(moduli):
    # Kähler modulus α: 對應 K_Chain mode n = α+1 (mod 44)
    # 佢嘅 beat 支撐 = 包含 mode n 嘅所有 beats
    if mod.type == 'kahler':
        # 36 Kähler moduli ↔ 36 個低能量 mode (γ < 2)
        # mode index: 由低能量排序
        gamma_all = 4 * np.sin(np.pi * np.arange(1, 45) / 88) ** 2
        low_modes = np.argsort(gamma_all)[:36] + 1  # 36 個最低能量 mode
        n_mode = low_modes[mod.hodge_index]
        
        # 呢個 modulus 嘅 beats = 包含 n_mode 嘅 (n,m) pairs
        mask = (beat_n == n_mode) | (beat_m == n_mode)
        # 再加 parity/Z₂ 守恆
        mask &= (beat_parity == mod.parity)
        mask &= (beat_z2 == mod.z2_charge)
        
        # weight: 幾何因子 φ^(-γ)
        gamma_n = 4 * math.sin(math.pi * n_mode / 88) ** 2
        for β in np.where(mask)[0]:
            gm = 4 * math.sin(math.pi * beat_m[β] / 88) ** 2
            gn = 4 * math.sin(math.pi * beat_n[β] / 88) ** 2
            avg = (gn + gm) / 2
            P[α, β] = phi ** (-avg)
    
    else:  # CPX
        # 98 CPX moduli ↔ 98 個組合 (n,m) pairs (γ > 2)
        # 每個 CPX modulus 對應一個獨特 beat
        cpx_idx = mod.hodge_index
        # 用 (n,m) 對: n = 23..44, m = n+1..44 嘅組合
        # 對應高能量區
        all_pairs = [(n, m) for n in range(23, 45) for m in range(n+1, 45)]
        if cpx_idx < len(all_pairs):
            n_c, m_c = all_pairs[cpx_idx]
            # 呢個 modulus 嘅 beats = 包含 n_c 或 m_c
            mask = (beat_n == n_c) | (beat_m == m_c) | (beat_n == m_c) | (beat_m == n_c)
            mask &= (beat_parity == mod.parity)
            mask &= (beat_z2 == mod.z2_charge)
            for β in np.where(mask)[0]:
                gn = 4 * math.sin(math.pi * beat_n[β] / 88) ** 2
                gm = 4 * math.sin(math.pi * beat_m[β] / 88) ** 2
                avg = (gn + gm) / 2
                P[α, β] = math.exp(-1.0 / avg)

print(f"    P shape: {P.shape}")
print(f"    非零元素: {np.count_nonzero(P)} / {P.size}")

# --- [3] 秩驗證 ---
print("\n[3] 秩分析:")
rank = np.linalg.matrix_rank(P, tol=1e-10)
print(f"    SVD 秩 (tol=1e-10): {rank}")

PPT = P @ P.T
evals, evecs = np.linalg.eigh(PPT)
evals_sorted = np.sort(evals)[::-1]
n_pos = np.sum(evals > 1e-10)
n_pos_loose = np.sum(evals > 1e-15)
print(f"    正本徵值 (>1e-10): {n_pos}")
print(f"    正本徵值 (>1e-15): {n_pos_loose}")
print(f"    最大 10 個:")
for i in range(min(10, len(evals_sorted))):
    print(f"      λ_{i+1:2d} = {evals_sorted[i]:.6e}")

# --- [4] 子矩陣秩 ---
print("\n[4] 子矩陣秩:")
P_k = P[:36, :]
P_c = P[36:, :]
rk = np.linalg.matrix_rank(P_k, tol=1e-10)
rc = np.linalg.matrix_rank(P_c, tol=1e-10)
print(f"    Kähler (36×946) 秩: {rk}")
print(f"    CPX (98×946) 秩: {rc}")
print(f"    rank_k + rank_c = {rk + rc}")

# 行間相關性
print(f"\n    行間相關性:")
rng = np.random.default_rng(1)
cors = []
for _ in range(50):
    i, j = rng.integers(0, 36, 2)
    if i == j: continue
    mask = (P_k[i] != 0) & (P_k[j] != 0)
    if mask.sum() > 3:
        cors.append(np.corrcoef(P_k[i][mask], P_k[j][mask])[0, 1])
if len(cors) > 0:
    cors = np.array(cors)
    print(f"    Kähler 行 corr: mean={cors.mean():.4f}, max={cors.max():.4f}")
    print(f"    → {'✅ 有真正 per-modulus 差異' if cors.max() < 0.999 else '❌ 仍然相關'}")
else:
    print(f"    (冇足夠重疊對)")

# --- [5] 66 態檢查 ---
print("\n[5] 66 態檢查:")
if n_pos >= 66:
    top66 = evals_sorted[:66]
    print(f"    前 66 個本徵值: [{top66[-1]:.3e}, {top66[0]:.3e}]")
    print(f"    尾部/頭部比: {top66[-1]/top66[0]:.2e}")
    print(f"    → {'✅ 有真正 66 維譜' if top66[-1] > 1e-8 else '⚠️ 尾部偏噪聲'}")
else:
    print(f"    只有 {n_pos} 個正本徵值")

# --- [6] 本徵值分佈 ---
print("\n[6] 本徵值譜 (log10):")
log_ev = np.log10(evals[evals > 1e-15])
if len(log_ev) > 0:
    hist, edges = np.histogram(log_ev, bins=12)
    for h, e1, e2 in zip(hist, edges[:-1], edges[1:]):
        print(f"      [{e1:8.2f}, {e2:8.2f}): {'#' * min(h, 40)} ({h})")

# 保存
np.save(os.path.join(DATA, "P_fixed_v2.npy"), P)
print(f"\n✅ 保存: data/P_fixed_v2.npy")

print("\n" + "=" * 70)
print("【結果】")
print("=" * 70)
print(f"""
  修正版 v2: rank = {rank}
  Kähler 子秩 = {rk}, CPX 子秩 = {rc}
  正本徵值 (>1e-10) = {n_pos}
  {'✅ 修正成功' if rank > 10 else '❌ 仍需改進'}
""")
print("=" * 70)
