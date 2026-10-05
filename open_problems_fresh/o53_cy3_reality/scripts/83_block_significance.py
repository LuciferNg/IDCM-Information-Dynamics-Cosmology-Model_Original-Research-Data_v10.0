#!/usr/bin/env python3
"""
O53 嚴謹測試: 隨機排列 divisor 對照 — block 結構係咪真?
============================================================
問題: block (0,0,0) = 5209 主要靠 divisor 0/8 主導
如果隨機排列 divisor 後 ratio 3 仍然出現, 咁 block 結構可能只係
「少數大 divisor 聚集」嘅偽影
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: block 結構嚴謹對照")
print("=" * 70)

with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
    ct = json.load(f)
K = np.array(ct['kappa'])
blocks = [(0,12), (12,24), (24,36)]

def ratio_for(perm):
    Kp = K[np.ix_(perm, perm, perm)]
    s_same = sum(np.abs(Kp[a:b, a:b, a:b]).sum() for a, b in blocks)
    s_cross = np.abs(Kp).sum() - s_same
    return s_same / max(s_cross, 1e-9)

# 觀測
obs = ratio_for(list(range(36)))
print(f"觀測 ratio (offset 0) = {obs:.3f}")

# 隨機排列 (1000 次)
rng = np.random.default_rng(42)
ratios = []
for _ in range(1000):
    perm = rng.permutation(36)
    ratios.append(ratio_for(perm))
ratios = np.array(ratios)
print(f"隨機排列 (1000 次): mean = {ratios.mean():.3f}, std = {ratios.std():.3f}")
print(f"  95% percentile = {np.percentile(ratios, 95):.3f}")
print(f"  99% percentile = {np.percentile(ratios, 99):.3f}")
z = (obs - ratios.mean()) / ratios.std()
print(f"  z-score = {z:.2f}σ")
p = np.mean(ratios >= obs)
print(f"  p-value (P(ratio >= {obs:.2f})) = {p:.5f}")

# 關鍵檢查: 移除 divisor 0 同 8 之後 block 結構仲喺唔喺?
print(f"\n[關鍵檢查] 移除 divisor 0, 8 後:")
mask = [i for i in range(36) if i not in (0, 8)]
K_no = K[np.ix_(mask, mask, mask)]
print(f"  κ shape: {K_no.shape}")
# 重新分組 34 → 唔係 12 嘅倍數, 用 3 組 (11, 11, 12)?
# 或者直接用剩餘 34 個做「同半 vs 跨半」?
# 簡化: 檢查 divisor 0/8 佔幾多 total strength
total = np.abs(K).sum()
d0 = np.abs(K[0]).sum() + np.abs(K[:,0]).sum() + np.abs(K[:,:,0]).sum()
d8 = np.abs(K[8]).sum() + np.abs(K[:,8]).sum() + np.abs(K[:,:,8]).sum()
# 避免重複計算, 用簡單方法
d0_only = np.abs(K[0, :, :]).sum()
d8_only = np.abs(K[8, :, :]).sum()
print(f"  total |κ| = {total:.0f}")
print(f"  divisor 0 強度 (axis 0) = {d0_only:.0f} ({d0_only/total*100:.1f}%)")
print(f"  divisor 8 強度 (axis 8) = {d8_only:.0f} ({d8_only/total*100:.1f}%)")

# 用減去 0/8 後嘅 34 維, 搵最佳 3 分組
print(f"\n[深入] 34 維 (去 0/8) 最佳 3 分組:")
# 嘗試所有 3 組大小 (11,11,12) 組合太多 — 用 spectral 方法
# 簡化: 檢查 34 個 divisor 有冇自然分組
div_strength = np.abs(K_no).sum(axis=(1,2))
print(f"  divisor 強度 (去 0/8 後):")
for i in np.argsort(div_strength)[::-1][:10]:
    print(f"    div {mask[i]:2d}: {div_strength[i]:8.1f}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)