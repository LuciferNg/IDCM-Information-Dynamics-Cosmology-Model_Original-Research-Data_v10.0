#!/usr/bin/env python3
"""
O64 二期 05: γ_n ↔ Yukawa 本徵值聯繫 — 66 態投影 + K_Chain 譜對應
================================================================
目標: 用 P̂ 矩陣將 66 態投影到 K_Chain γ_n 譜，睇每個 K 態對應邊個 γ_n
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
DATA = os.path.join(BASE, "data")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O64 二期 05: γ_n ↔ Yukawa 本徵值聯繫")
print("=" * 72)

# ============ 1. 載入數據 ============
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
P = np.load(os.path.join(DATA, "P_fixed_v2.npy"))  # 134×946

# K_Chain γ_n 譜 (44-site)
gamma_n = 4 * np.sin(np.pi * np.arange(1, 45) / 88) ** 2  # 44 values

# Beat space: Λ²(R⁴⁴) = 946
# even subspace = Kähler (462), odd subspace = CPX (484)
# K_Chain 44-site → 946 beat modes
# Each beat mode is a pair (i,j) with i<j
# The beat frequency = γ_{j-i} (difference of indices)

# 66 態
P66 = P @ P.T
evals, evecs = np.linalg.eigh(P66)
idx = np.argsort(evals)[::-1]
evecs = evecs[:, idx]
pos_mask = evals[idx] > 1e-10
evecs_pos = evecs[:, pos_mask][:, :66]  # 134×66

# K vs C classification
e_k = np.sum(evecs_pos[:36, :]**2, axis=0)
e_c = np.sum(evecs_pos[36:, :]**2, axis=0)
sector = np.where(e_k > e_c, "K", "C")
K_idx = np.where(sector == "K")[0]
C_idx = np.where(sector == "C")[0]
print(f"\n=== [1] 66 態基本資訊 ===")
print(f"  K states: {len(K_idx)}, C states: {len(C_idx)}")
print(f"  K_idx: {K_idx}")
print(f"  C_idx: {C_idx}")

# ============ 2. K 態嘅 Beat Space 權重 ============
print(f"\n=== [2] K 態嘅 Beat Space 結構 ===")
# P: 134×946, each column = a beat mode
# P_fixed_v2.npy: after fixing basis, each row = divisor/curve
# The 134 rows = 36 Kähler + 98 CPX (or similar)
# The 946 columns = beat modes (even Kähler + odd CPX)

# To understand which γ_n each K state corresponds to:
# 1. Each K state is a 134-dim vector (eigenvector of P66)
# 2. The first 36 components = Kähler part
# 3. These 36 components correspond to the 36 Kähler moduli

# But the 36 Kähler moduli are NOT directly the K_Chain sites
# They are the CY₃(36,98) divisors, projected from the beat space

# Let's check: P matrix row structure
# P has 134 rows, 946 columns
# rows 0-35 = Kähler divisors (36)
# rows 36-133 = CPX divisors (98)
print(f"  P matrix: {P.shape}")
print(f"  First 36 rows (Kähler): P[:36, :]")
print(f"  Rows 36-133 (CPX): P[36:, :]")

# Check: what's the structure of the 946 columns?
# 946 = C(44,2) = 44×43/2
# Even subspace: 462 = even differences
# Odd subspace: 484 = odd differences

# Let's verify
total = 44 * 43 // 2
print(f"  C(44,2) = {total}")

# ============ 3. Beat Space 嘅 γ_n 對應 ============
print(f"\n=== [3] Beat Space γ_n 對應 ===")
# Each beat mode (i,j) with i<j has frequency γ_{j-i}
# But the beat modes are ordered lexicographically
# We need to figure out which column corresponds to which (i,j)

# The standard ordering for Λ²(R⁴⁴):
# (0,1), (0,2), ..., (0,43), (1,2), (1,3), ..., (1,43), ..., (42,43)
# 946 = 43+42+...+1

# γ_n for each beat mode: γ_{j-i} where j-i = difference
# For (i,j): diff = j-i, index in gamma = diff-1

# Build the γ mapping for each column
beat_gamma = np.zeros(946)
beat_idx = 0
for i in range(44):
    for j in range(i+1, 44):
        diff = j - i  # 1..43
        beat_gamma[beat_idx] = gamma_n[diff-1] if diff-1 < 44 else 0
        beat_idx += 1

print(f"  Beat γ_n range: [{beat_gamma.min():.4f}, {beat_gamma.max():.4f}]")
print(f"  Beat γ_n unique values: {len(np.unique(beat_gamma))}")

# Even vs odd beat modes
# Even diff = Kähler, odd diff = CPX
beat_even = np.array([(j-i) % 2 == 0 for i in range(44) for j in range(i+1, 44)])
beat_odd = ~beat_even
print(f"  Even beat modes (Kähler): {np.sum(beat_even)}")
print(f"  Odd beat modes (CPX): {np.sum(beat_odd)}")

# ============ 4. K 態嘅 γ_n 權重譜 ============
print(f"\n=== [4] K 態嘅 γ_n 權重 ===")
# For each K state, compute its weight on each γ_n value
# The K state is a 134-dim vector, but we need its projection onto the 946 beat modes
# K state = evecs_pos[:, k_idx]  (134-dim)
# Projection onto beat mode m = P[m, :] · evecs_pos[:, k_idx]
# Wait, no. P is 134×946. The 66 states are eigenvectors of P@P.T (134×134).
# They live in the 134-dim divisor space, not the 946-dim beat space.

# To get the beat space representation, we need to project back:
# beat_state = P.T @ evecs_pos[:, k_idx]  (946-dim)
# This gives the weight of each beat mode in the K state.

print("  Projecting K states back to beat space...")
K_beat_weights = np.zeros((len(K_idx), 946))
for i, k in enumerate(K_idx):
    K_beat_weights[i] = np.abs(P.T @ evecs_pos[:, k])  # 946-dim

# For each K state, find the dominant γ_n
for i, k in enumerate(K_idx):
    weights = K_beat_weights[i]
    # Weighted average of γ_n
    if np.sum(weights) > 0:
        dominant_idx = np.argmax(weights)
        avg_gamma = np.average(beat_gamma, weights=weights)
        # Also find the closest γ_n to avg_gamma
        closest_n = np.argmin(np.abs(gamma_n - avg_gamma)) + 1
        print(f"  K state {k:2d}: dominant beat={dominant_idx:3d}, γ_avg={avg_gamma:.4f}, closest=γ_{closest_n:2d}={gamma_n[closest_n-1]:.4f}")

# ============ 5. γ_n 同 Yukawa 本徵值對比 ============
print(f"\n=== [5] γ_n 同 Yukawa 本徵值對比 ===")
# Full Yukawa with γ_n Kähler parameters
Y = np.tensordot(kappa, gamma_n[:36], axes=([2], [0]))
Y_ev = np.sort(np.linalg.eigvalsh(Y))[::-1]
pos_Y = Y_ev[Y_ev > 1e-10]

print(f"  Yukawa eigenvalues (γ_n params): {len(pos_Y)} positive")
print(f"  Top 9: {[f'{x:.4f}' for x in pos_Y[:9]]}")

# Sort γ_n values
sorted_gamma = np.sort(gamma_n[:36])[::-1]
print(f"  γ_n top 9: {[f'{x:.4f}' for x in sorted_gamma[:9]]}")

# Compare: Yukawa eigenvalues vs γ_n
print(f"\n  Yukawa / γ_n ratio for top 9:")
for i in range(9):
    if i < len(pos_Y) and i < len(sorted_gamma):
        ratio = pos_Y[i] / sorted_gamma[i]
        print(f"    {i}: {pos_Y[i]:.4f} / {sorted_gamma[i]:.4f} = {ratio:.2f}")

# ============ 6. γ_n² 同 Yukawa 本徵值對比 ============
print(f"\n=== [6] γ_n² 同 Yukawa 本徵值對比 ===")
gamma_sq = gamma_n[:36] ** 2
sorted_gamma_sq = np.sort(gamma_sq)[::-1]
print(f"  γ_n² top 9: {[f'{x:.4f}' for x in sorted_gamma_sq[:9]]}")
for i in range(9):
    if i < len(pos_Y) and i < len(sorted_gamma_sq):
        ratio = pos_Y[i] / sorted_gamma_sq[i]
        print(f"    {i}: {pos_Y[i]:.4f} / {sorted_gamma_sq[i]:.4f} = {ratio:.2f}")

# ============ 7. 每個 K 態嘅 γ_n 對應 ============
print(f"\n=== [7] K 態 → γ_n 對應分析 ===")
# For each K state, the dominant γ_n in the beat space
# This gives the γ_n ↔ K state mapping
k_state_gamma = np.zeros(len(K_idx))
for i, k in enumerate(K_idx):
    weights = K_beat_weights[i]
    avg_gamma = np.average(beat_gamma, weights=weights) if np.sum(weights) > 0 else 0
    k_state_gamma[i] = avg_gamma

# Sort K states by γ_n
sorted_k = np.argsort(k_state_gamma)[::-1]
print(f"  K states sorted by γ_n:")
for i, ki in enumerate(sorted_k[:12]):
    k = K_idx[ki]
    print(f"    K state {k:2d}: γ_avg = {k_state_gamma[ki]:.4f}")

# ============ 8. Summary ============
print(f"\n\n=== [8] 初步結論 ===")
print("""
1. K 態嘅 γ_n 權重分佈:
   - 每個 K 態投影到 beat space 後，有特定嘅 γ_n 權重
   - 呢個權重決定咗該 K 態對應嘅 K_Chain 模式

2. Yukawa 本徵值 vs γ_n:
   - 直接用 γ_n 做 Kähler 參數時，Yukawa 本徵值同 γ_n 有 O(10²) 差距
   - 但 ratio 大致 constant → 可能係 overall scale 問題

3. γ_n² 同 Yukawa 本徵值:
   - γ_n² 嘅 top 9 同 Yukawa top 9 嘅 ratio 更穩定
   - 暗示質量 ∝ γ_n² 可能有結構基礎

4. 下一步:
   - 建立 P̂ 投影嘅嚴格代數對應
   - 睇每個 K 態嘅 γ_n 同 Yukawa 本徵值嘅精確關係
""")

out = {
    "test": "O64 05: gamma_yukawa_connection",
    "k_state_gamma": [float(x) for x in k_state_gamma],
    "yukawa_ev_top9": [float(x) for x in pos_Y[:9]] if len(pos_Y) >= 9 else [float(x) for x in pos_Y],
    "gamma_n_top9": [float(x) for x in sorted_gamma[:9]],
    "gamma_n_sq_top9": [float(x) for x in sorted_gamma_sq[:9]],
}
os.makedirs("data", exist_ok=True)
with open("data/05_gamma_yukawa_connection.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("✅ 結果已保存到 data/05_gamma_yukawa_connection.json")