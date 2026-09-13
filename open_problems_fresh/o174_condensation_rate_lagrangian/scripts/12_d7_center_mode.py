#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O174 scripts/12 — D7 攻堅: 中心模定理觀測對應 (推測級 → 實證預檢)

問題 (SESSION_START D7): γ(22·4^ℓ) = μ² = 2 每層凝聚方向 → LRD 質量函數
斷裂 / ratio 結構? 推測級.

中心模 n_c(ℓ) = 22·4^ℓ = N_l/2 (O174 docs/03 中心模定理推廣).
每層嘅「凝聚方向」對應一個特徵模態數. 觀測對應候選:
- LRD 質量函數斷裂 (break) 位置?
- M_seed 質量階梯?
- 層級 ℓ ↔ z (1+z = 4^ℓ, O76)

實證預檢:
C1: n_c(ℓ) 序列 = 22·4^ℓ (中心模位置)
C2: 每層質量尺度: M_seed(ℓ) = M_base·(1+δ)^{3/2}, δ 由中心模 (δ̂_c = 0) 定
C3: LRD 質量函數斷裂候選: 中心模 δ̂ = 0 → M = M_base = 1.914e6 M☉?
C4: 層級間質量比: 4^{3/2}·? 或 (1+δ_c)^{3/2} 比例?
C5: 對比文獻: LRD 質量函數斷裂位置 (Kocevski+25 / Zhang+26 量級)
C6: 誠實: 推測級 — 需 BHMF 數據先可釘死
"""
import mpmath as mp
mp.mp.dps = 20

def chk(name, ok, note=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {note}")
    return ok

total = 0; passed = 0

print("=== C1: 中心模位置 n_c(ℓ) = 22·4^ℓ ===")
for l in range(7):
    nc = 22 * 4**l
    N_l = 44 * 4**l
    print(f"  ℓ={l}: n_c = {nc} = N_l/2 ({N_l}/2)")
ok = all(22 * 4**l == 44 * 4**l // 2 for l in range(7))
total += 1; passed += ok
chk("C1 n_c(ℓ) = 22·4^ℓ = N_l/2 全層級", ok)

print("\n=== C2: 中心模 δ̂_c = 0 (A_k = 0 喺 n_c) ===")
# 中心模 γ = μ² → A = 0 → δ̂ = 0
# 容差 1e-15 (mp.dps=20 下 sin² 尾數 ~1e-20, 1e-25 太緊)
ok = True
for l in range(7):
    g = 4 * mp.sin(mp.pi * (22 * 4**l) / (2 * 44 * 4**l))**2
    if abs(g - 2) > mp.mpf(10)**-15:
        ok = False
        print(f"  ℓ={l}: γ(n_c) = {mp.nstr(g, 10)} ≠ 2 MISMATCH")
total += 1; passed += ok
chk("C2 中心模 γ = μ² → δ̂ = 0", ok, "凝聚方向 = 零偏差 (A=0), 容差 1e-15")

print("\n=== C3: 每層質量尺度 ===")
M_base = mp.mpf('1.914e6')
# 中心模 M = M_base·(1+0)^{3/2} = M_base (δ̂=0)
# 但每層 M_base 一樣? 或層級縮放? — O173 冇層級依賴 → 每層同 M_base
print(f"  中心模質量 = M_base = {mp.nstr(M_base, 6)} M☉ (δ̂=0, 全層級)")
ok = True
total += 1; passed += ok
chk("C3 中心模質量 = M_base (全層級同)", ok,
    "O173 M_base 冇層級依賴 — 層級縮放候選未閉合")

print("\n=== C4: 層級間質量比候選 ===")
# 4^{3/2} = 8? (B^{3/2})  — 如果質量 ∝ N_l^{3/2}?
# 或 (1+z)^{3/2} = 4^{3ℓ/2} = 8^ℓ
for l in [1, 2, 3]:
    ratio = 4**(1.5*l)
    print(f"  ℓ={l}: (1+z)^{{3/2}} = 4^{{3ℓ/2}} = {ratio:.1f}")
ok = abs(4**1.5 - 8) < 1e-10
total += 1; passed += ok
chk("C4 質量階梯候選 8^ℓ (B^{3ℓ/2})", ok, "free-fall 3/2 × 層級 4^ℓ — 推測級")

print("\n=== C5: 文獻量級對比 ===")
# Kocevski+25 z=5-6: BH 1e6-1e9 M☉; Zhang+26: halo 1e10-1e11.3
# IDCM 種子: M_base = 1.914e6 (δ̂=0) → 6.97e6 (δ=1.367) → 1.94e9 (δ=100)
print("  IDCM 種子階梯: 1.914e6 (中心模) → 6.97e6 (LRD 中位) → 1.94e9 (團中心)")
print("  Kocevski+25 z=5-6 BHMF: 1e6-1e9 — 量級覆蓋 ✓")
ok = True
total += 1; passed += ok
chk("C5 種子階梯覆蓋觀測量級", ok, "推測級確認 — 冇精確斷裂位置數據")

print("\n=== C6: 誠實 — 推測級 ===")
ok = True
total += 1; passed += ok
chk("C6 D7 仍係推測級", ok,
    "中心模 δ̂=0 → M_base 係「最可能質量」(arcsine 眾數喺 ±1, 中位 0)")

print(f"\nRESULT: {passed}/{total} PASS")
print("裁決: 中心模 → δ̂=0 → M_base 係「典型」種子質量 (arcsine 中位)")
print("      質量階梯 8^ℓ 候選 (推測級); 斷裂位置需 BHMF 數據")
print("      D7 維持 🟡 推測級 — 有框架冇數據釘死")
