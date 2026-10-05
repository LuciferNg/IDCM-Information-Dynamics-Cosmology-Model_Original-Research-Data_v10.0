#!/usr/bin/env python3
"""
O53 新方向: K_Chain 譜嘅 1/3 諧波 ↔ c_f
============================================
c_f = n/3 → 可能對應 K_Chain 譜嘅「1/3 諧波」

γ_n = 4sin²(nπ/88), n=1..44
88/3 ≈ 29.33 — 1/3 諧波位置?
44/3 ≈ 14.67

測試: γ 譜入面有冇特別嘅 1/3 結構?
"""
import os, json, math, sys
import numpy as np

print("=" * 70)
print("O53: K_Chain 1/3 諧波")
print("=" * 70)

Nd = 44
n = np.arange(1, Nd + 1)
gamma = 4 * np.sin(n * np.pi / (2 * Nd)) ** 2

# 1. 完整譜
print(f"[1] γ_n (n=1..44):")
print(f"  γ_1..γ_10: {gamma[:10]}")
print(f"  γ_35..γ_44: {gamma[34:]}")

# 2. 1/3 位置
print(f"\n[2] 1/3 諧波位置:")
for frac, name in [(1/3, "1/3"), (2/3, "2/3")]:
    pos = Nd * frac
    print(f"  {name} 位置: n = {pos:.2f} (44×{frac})")
    print(f"  γ 喺附近: γ_{int(np.floor(pos))} = {gamma[int(np.floor(pos))-1]:.4f}, γ_{int(np.ceil(pos))} = {gamma[int(np.ceil(pos))-1]:.4f}")

# 3. 特殊: γ_n = 1/3 附近?
print(f"\n[3] γ_n = 1/3 嘅 n?")
idx13 = np.where(np.abs(gamma - 1/3) < 0.05)[0]
for i in idx13:
    print(f"  n={i+1}: γ={gamma[i]:.4f}")

# 4. Σγ 嘅 1/3 分解
print(f"\n[4] Σγ = 90 嘅 1/3 分解:")
# 前 1/3 和
n13 = Nd // 3
print(f"  前 {n13} 個 (n=1..{n13}): Σ = {gamma[:n13].sum():.4f}")
print(f"  中 {n13} 個: Σ = {gamma[n13:2*n13].sum():.4f}")
print(f"  後 {Nd-2*n13} 個: Σ = {gamma[2*n13:].sum():.4f}")

# 5. γ 值域 — 有冇 1/3 倍數?
print(f"\n[5] γ_n 值 (全部):")
vals = np.sort(gamma)
print(f"  min = {vals[0]:.6f}, max = {vals[-1]:.6f}")
print(f"  γ_n ∈ [0, 4] (理論)")
print(f"  有冇 γ = 1/3? {np.any(np.abs(gamma - 1/3) < 1e-6)}")
print(f"  有冇 γ = 2/3? {np.any(np.abs(gamma - 2/3) < 1e-6)}")

# 6. 正弦結構: sin²(nπ/88) — 1/3 係咪特別?
print(f"\n[6] sin²(nπ/88) 嘅有理值:")
for n_test in range(1, 45):
    s = np.sin(n_test * np.pi / 88) ** 2
    # 檢查 s 近有理數 m/k
    for k in [3, 4, 6, 8]:
        for m in range(1, k):
            if abs(s - m/k) < 1e-6:
                print(f"  n={n_test}: sin² = {s:.6f} = {m}/{k} 精確!")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)