#!/usr/bin/env python3
"""WoW! signal 分析 — 是否巧合校準了 A5 晶網頻道?

三項檢驗:
1. 幾何: WoW 位置 (RA 19h25m, Dec -27.5°) vs 60 個 A5 節點角距離
2. 頻率: 1420.4556 MHz vs IDCM 結構 (φ 比例, Fibonacci, K_Chain)
3. 統計: 最近節點距離 vs 隨機期望
"""
import sys, math
import numpy as np
sys.path.insert(0, ".")
from grt_common import load_nodes, PHI, PHI_INV

nodes, vecs = load_nodes()
N = len(nodes)

# WoW! signal 參數 (Big Ear 1977-08-15)
# 兩個 horn 各對應一個位置, RA range 19h22m24s - 19h25m17s
wow_positions = [
    (19*15 + 25/60*15 + 31/3600*15, -27.0),   # horn A: RA 19h25m31s
    (19*15 + 22/60*15 + 24/3600*15, -28.0),   # horn B: RA 19h22m24s
]
# 轉做度
wow_positions = [(ra, dec) for ra, dec in wow_positions]

def ang_deg(ra1, dec1, ra2, dec2):
    """球面角距離 (度)"""
    ra1, dec1, ra2, dec2 = map(math.radians, [ra1, dec1, ra2, dec2])
    d = math.acos(max(-1, min(1,
        math.sin(dec1)*math.sin(dec2) +
        math.cos(dec1)*math.cos(dec2)*math.cos(ra1-ra2))))
    return math.degrees(d)

print("=" * 72)
print("WOW! SIGNAL vs A5 晶網 — 幾何校準檢驗")
print("=" * 72)

for label, (wow_ra, wow_dec) in zip(["Horn A (RA 19h25m31s)", "Horn B (RA 19h22m24s)"], wow_positions):
    dists = []
    for i, (ra, dec) in enumerate(nodes):
        d = ang_deg(wow_ra, wow_dec, ra, dec)
        dists.append((d, i, ra, dec))
    dists.sort()
    print(f"\n{label}: (RA {wow_ra:.2f}°, Dec {wow_dec}°)")
    print(f"  最近 5 個 A5 節點:")
    for d, i, ra, dec in dists[:5]:
        print(f"    node {i:2d}: ({ra:.2f}, {dec:.2f})  distance = {d:.2f}°")
    nearest_d, nearest_i, _, _ = dists[0]
    print(f"  🎯 最近節點: node {nearest_i} @ {nearest_d:.2f}°")

    # 隨機期望: 60 個節點均勻分佈, 最近距離期望
    # E[min d] ≈ 0.5 * (4π/60)^(1/2) 半球近似 ~ 21.9°
    # 用 MC 計精確值
    rng = np.random.default_rng(42)
    n_mc = 2000
    nearest_mc = []
    for _ in range(n_mc):
        # 隨機生成 60 個點
        ra_rand = rng.uniform(0, 360, 60)
        dec_rand = np.degrees(np.arcsin(rng.uniform(-1, 1, 60)))
        ds = [ang_deg(wow_ra, wow_dec, r, d) for r, d in zip(ra_rand, dec_rand)]
        nearest_mc.append(min(ds))
    nearest_mc = np.array(nearest_mc)
    print(f"  隨機期望最近距離: {nearest_mc.mean():.1f}° ± {nearest_mc.std():.1f}°")
    print(f"  分位數: p5={np.percentile(nearest_mc, 5):.1f}°  p50={np.percentile(nearest_mc, 50):.1f}°  p95={np.percentile(nearest_mc, 95):.1f}°")
    p = np.mean(nearest_mc <= nearest_d)
    print(f"  最近距離 {nearest_d:.2f}° 嘅 MC 分位: p = {p:.4f} ({'🟢 顯著對齊' if p < 0.05 else '🟡 普通' if p < 0.5 else '🔴 冇特別'})")

print("\n" + "=" * 72)
print("頻率檢驗: 1420.4556 MHz vs IDCM 結構")
print("=" * 72)

f_wow = 1420.4556  # MHz (Big Ear 觀測中心頻率)
f_hydrogen = 1420.405751  # MHz 氫線 21cm

print(f"\nWoW 頻率: {f_wow:.4f} MHz")
print(f"氫線:     {f_hydrogen:.4f} MHz")
print(f"偏移:     {f_wow - f_hydrogen:+.4f} MHz ({abs(f_wow-f_hydrogen)/f_hydrogen*1e6:.0f} ppm)")
print(f"Big Ear 頻道帶寬: 10 kHz → 偏移約 5 個頻道")

# 試 φ 比例
print(f"\nφ 比例檢驗:")
print(f"  f_wow × φ⁻¹ = {f_wow * PHI_INV:.2f} MHz")
print(f"  f_wow × φ⁻² = {f_wow * PHI_INV**2:.2f} MHz")
print(f"  f_wow / φ²  = {f_wow / PHI**2:.2f} MHz")
print(f"  f_wow / 2   = {f_wow / 2:.2f} MHz")
print(f"  f_wow / 4   = {f_wow / 4:.2f} MHz")

# Fibonacci 分解
print(f"\nFibonacci 檢驗:")
F = [1, 1]
while F[-1] < 2000:
    F.append(F[-1] + F[-2])
print(f"  F 數列: {F}")
print(f"  f_wow / F₁₆(987) = {f_wow/987:.4f}")
print(f"  f_wow / F₁₅(610) = {f_wow/610:.4f}")
print(f"  f_wow / F₁₄(377) = {f_wow/377:.4f}")

# CMB peak 160.4 GHz 相關
f_cmb = 160.4e3  # MHz
print(f"\nCMB peak 相關:")
print(f"  f_cmb / f_wow = {f_cmb / f_wow:.1f}")
print(f"  f_cmb / f_hydrogen = {f_cmb / f_hydrogen:.1f}")

# 21cm = λ_sync 關係? λ_sync = 294.88 Mpc
# 21cm 對應頻率 1420 MHz; 試下同 K_Chain 尺度比
print(f"\nK_Chain 相關:")
print(f"  λ_sync = 294.88 Mpc")
print(f"  21cm 波長 vs λ_sync: ratio = {294.88e6/0.211:.2e}")
print(f"  1420.4 / 44 (K_Chain modes) = {1420.4/44:.2f}")

print("\n" + "=" * 72)
print("結論")
print("=" * 72)
