#!/usr/bin/env python3
"""
O53 景觀統計篩選 — ⚠️ 已撤回「唯一性定理」身份 (2026-08-21)
==========================================================
用 Kreuzer-Skarke 完整景觀 (30,108 pairs) 統計:
弦理論內生約束 |χ|=124 ∩ h11+h21=134 → 命中 (36,98)

⚠️ 已撤回聲明 (見 SESSION_START.md):
- 呢個係「統計篩選」, 唔係「推導」/「唯一性定理」
- |χ|=124 嘅弦理論來源 (4|χ|=496=dim E8×E8) 係事後配數, 冇推導鏈
- 標準嵌入 n_gen=64≠3 → 弦理論標準準則反而排除 (36,98)
- 3 代候選大量存在 (|χ|=2 有 164 個, |χ|=10 有 184 個)
- 保留下來做統計記錄, 唔可以當結論引用

仍然有效嘅部分:
- (36,98) 係唯一同時滿足 h11+h21=134 且 h21−h11=62 嘅 pair
- 呢兩個約束本身來自 K_Chain 結構數 (scripts/03), 唔係來自弦理論

Run: /usr/bin/python3 scripts/02_uniqueness_theorem.py
Data: ../data/alltoric.spec
"""
import numpy as np
import os

DATA = os.path.join(os.path.dirname(__file__), '..', 'data', 'alltoric.spec')

pairs = []
with open(DATA) as f:
    for line in f:
        p = line.split()
        if len(p) >= 3:
            try:
                pairs.append((int(p[0]), int(p[1]), int(p[2])))
            except ValueError:
                pass
arr = np.array(pairs)
h11, h21, chi = arr[:, 0], arr[:, 1], arr[:, 2]

print("=" * 64)
print("O53: (36,98) 唯一性定理 — 景觀逆向工程")
print("=" * 64)
print(f"景觀總數: {len(arr)} pairs")
print(f"約束 A: |χ| = 124  (4|χ| = 496 = dim E8×E8)")

# 約束 A
nA = np.sum(np.abs(chi) == 124)
print(f"  A 命中: {nA} pairs")

# 約束 B
nB = np.sum((h11 + h21) == 134)
print(f"約束 B: h11+h21 = 134")
print(f"  B 命中: {nB} pairs")

# A ∩ B
mask = (np.abs(chi) == 124) & ((h11 + h21) == 134)
both = arr[mask]
print(f"\nA ∩ B: {len(both)} pairs")
for b in both:
    print(f"  ({b[0]}, {b[1]}) χ={b[2]}")

# 幾何交點
h1_sol = (134 - 62) / 2
print(f"\n幾何交點: h²¹=h¹¹+62 ∩ h²¹=134−h¹¹")
print(f"  h¹¹ = (134−62)/2 = {h1_sol}, h²¹ = {h1_sol}+62 = {h1_sol+62}")

# 驗證
assert np.sum((chi == -124) & ((h11 + h21) == 134)) == 1, "唯一性失敗!"
assert np.sum((chi == 124) & ((h11 + h21) == 134)) == 1, "mirror 唯一性失敗!"

print("\n" + "=" * 64)
print("⚠️ 統計篩選結果（已撤回「唯一性」身份）:")
print("   (36,98) 命中 |χ|=124 ∩ sum=134 — 但呢個係統計篩選, 唔係推導")
print("   |χ|=124 嘅弦理論來源係事後配數 (4|χ|=496=dim E8×E8 冇推導鏈)")
print("   標準嵌入 n_gen=64≠3 → 弦理論標準準則反而排除 (36,98)")
print("   仍然有效: (36,98) 係唯一同時滿足 h11+h21=134 且 h21−h11=62 嘅 pair")
print("   (呢兩個約束來自 K_Chain 結構數 scripts/03, 唔係來自弦理論)")
print("=" * 64)
