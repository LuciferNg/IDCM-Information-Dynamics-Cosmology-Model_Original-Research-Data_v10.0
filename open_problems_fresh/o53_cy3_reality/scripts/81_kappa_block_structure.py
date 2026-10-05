#!/usr/bin/env python3
"""
O53 關鍵測試: CYTools 真 κ 嘅 3×12 block 結構（原基）
=========================================================
之前發現 (scripts/41-42, 舊 κ): 同塊強度 899 vs 跨塊 373 (ratio 2.41)
而家用 CYTools 真 κ 重做 — 睇 block 結構係咪 survive
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: CYTools 真 κ 3×12 block 結構")
print("=" * 70)

with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
    ct = json.load(f)
K = np.array(ct['kappa'])
print(f"CYTools κ: {K.shape}, nnz = {np.count_nonzero(K)}")

# [1] 原基 3×12 分組 {0-11, 12-23, 24-35}
blocks = [(0,12), (12,24), (24,36)]
print(f"\n[1] 原基 3×12 block 強度 (κ_ijk 3-tensor):")
print(f"    分組: {blocks}")
for bi, (a, b) in enumerate(blocks):
    for bj, (c, d) in enumerate(blocks):
        for bk, (e, f) in enumerate(blocks):
            sub = K[a:b, c:d, e:f]
            strength = np.abs(sub).sum()
            nnz = np.count_nonzero(sub)
            label = "同塊" if bi == bj == bk else "跨塊"
            print(f"    block ({bi},{bj},{bk}) [{label}]: |Σ| = {strength:10.2f}, nnz = {nnz:4d}")

# 同塊 vs 跨塊 統計
same_strength = sum(np.abs(K[a:b, a:b, a:b]).sum() for a, b in blocks)
cross_strength = np.abs(K).sum() - same_strength
same_nnz = sum(np.count_nonzero(K[a:b, a:b, a:b]) for a, b in blocks)
cross_nnz = np.count_nonzero(K) - same_nnz
print(f"\n[統計] 同塊 |Σ| = {same_strength:.2f} ({same_nnz} nnz)")
print(f"      跨塊 |Σ| = {cross_strength:.2f} ({cross_nnz} nnz)")
print(f"      ratio = {same_strength/max(cross_strength,1e-9):.3f}")

# 隨機對照: 隨機分組 ratio
rng = np.random.default_rng(0)
ratios = []
for _ in range(100):
    perm = rng.permutation(36)
    Kp = K[np.ix_(perm, perm, perm)]
    s_same = sum(np.abs(Kp[a:b, a:b, a:b]).sum() for a, b in blocks)
    s_cross = np.abs(Kp).sum() - s_same
    ratios.append(s_same / max(s_cross, 1e-9))
ratios = np.array(ratios)
print(f"\n[對照] 隨機分組 ratio 分佈: mean = {ratios.mean():.3f}, std = {ratios.std():.3f}")
print(f"      觀測 ratio = {same_strength/max(cross_strength,1e-9):.3f}")
z = (same_strength/max(cross_strength,1e-9) - ratios.mean()) / ratios.std()
print(f"      z-score = {z:.2f}σ")

# [2] 其他分組嘗試 (shift by 1, 2, ...)
print(f"\n[2] 唔同 offset 嘅 3×12 分組 ratio:")
best_offset = 0
best_ratio = 0
for offset in range(12):
    perm = [(offset + i) % 36 for i in range(36)]
    Kp = K[np.ix_(perm, perm, perm)]
    s_same = sum(np.abs(Kp[a:b, a:b, a:b]).sum() for a, b in blocks)
    s_cross = np.abs(Kp).sum() - s_same
    r = s_same / max(s_cross, 1e-9)
    if r > best_ratio:
        best_ratio = r
        best_offset = offset
    print(f"    offset {offset:2d}: ratio = {r:.3f}")
print(f"\n    最佳 offset = {best_offset}, ratio = {best_ratio:.3f}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)