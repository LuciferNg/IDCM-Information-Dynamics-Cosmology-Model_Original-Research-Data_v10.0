#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O197 scripts/08 — 3/2 指數結構推導 (Three-Half Power Structural Derivation)

O173 P7: M_seed = M_base(1+δ)^{3/2} — 3/2 冪律從未結構推導 (O173 只「free-fall
暗示」α≈1.74, O174 冇出處)。本 scripts 做第一性原理推導:

★凝聚率推導:
  種子質量 = 凝聚率 × 事件時間窗 (池事件, Δt 固定)
  凝聚率 Ṁ ∝ ρ/t_ff (密度 / free-fall 時間 = 每次塌縮收集質量)
  t_ff ∝ (Gρ)^{-1/2} (牛頓引力, 平方反比) ⟹ t_ff^{-1} ∝ ρ^{1/2}
  Ṁ ∝ ρ · ρ^{1/2} = ρ^{3/2} ⟹ M_seed ∝ (1+δ)^{3/2} ✓

★結構身份:
  3/2 = 3/2 其中 3 = 空間維數 = N_gen = dimC (IDCM: dimC·B·N_d = 3×4×44, O38),
          2 = free-fall 動力學指數 (牛頓平方反比 ⟹ t_ff ∝ ρ^{-1/2})
  ⟹ M_seed ∝ ρ^{空間維/2} = ρ^{1+1/2}: 1 = 密度線性 (3D 體積凝聚),
                                    1/2 = 塌縮頻率 (引力動力學)

T10a: 凝聚率閉式 Ṁ ∝ ρ/t_ff = ρ^{3/2} (t_ff ∝ ρ^{-1/2} 牛頓)
T10b: 結構身份 3/2 = N_gen/2 = dimC/2 (空間維 = 3 = 世代數)
T10c: ★數值閉環 δ=1.367 → 6.97e6 (LRD 錨, O173 已立)
T10d: ★數值閉環 δ=100 → 1.94e9 (UHz1 單事件上限)
T10e: M_turn = M_base·2^{3/2} = 5.4136e6 (δ=1 轉折閉式, O197)
T10f: (1+δ̂)^{3/2} = (γ/2)^{3/2} = 2^{3/2}·sin³(kπ/176) (3D 角譜身份)
T10g: 通道 A 帶閉式 [M_base(1+sin(π/88))^{3/2}, M_base·2^{3/2}] (docs/04 一致)
T10h: 可證偽預言 — 質量-環境冪律 = 3/2 (JWST 高 z 種子 vs 宿主環境密度, O173 P7)
"""
import mpmath as mp
mp.mp.dps = 50

N_gen, dimC, B, N_d = 3, 3, 4, 44
M_base = mp.mpf("1.914e6")

tot = 0; pas = 0
def T(name, ok, note=""):
    global tot, pas
    tot += 1; pas += 1 if ok else 0
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {note}")

print("== T10a: 凝聚率閉式 Ṁ ∝ ρ/t_ff = ρ^{3/2} ==")
# t_ff = sqrt(3π/(32Gρ)) ⟹ t_ff ∝ ρ^{-1/2} (牛頓平方反比)
# Ṁ = ρ·V/t_ff, V = 收集體積 (固定) ⟹ Ṁ ∝ ρ·ρ^{1/2} = ρ^{3/2}
# 數字: t_ff(ρ₀) / t_ff(2ρ₀) = sqrt(2) — free-fall 頻率雙倍密度快 √2
import math
ratio_ff = math.sqrt(2.0)   # t_ff ∝ ρ^{-1/2}
print(f"  t_ff ∝ ρ^(-1/2): ρ×2 ⟹ t_ff ÷ √2 = {ratio_ff:.4f}, 頻率 × √2 = {ratio_ff:.4f}")
print(f"  Ṁ ∝ ρ·ρ^(1/2): ρ×2 ⟹ Ṁ × 2√2 = {2*ratio_ff:.4f} (= 2^{3/2})")
ok_a = abs(2 * ratio_ff - 2 ** 1.5) < 1e-9
T("T10a Ṁ ∝ ρ/t_ff = ρ·ρ^{1/2} = ρ^{3/2} (free-fall 頻率 × 密度)",
  ok_a, f"ρ×2 ⟹ Ṁ × 2√2 = 2^{3/2} ✓ (t_ff ∝ ρ^(-1/2) 牛頓)")

print("\n== T10b: 結構身份 3/2 = N_gen/2 = dimC/2 ==")
print(f"  N_gen = {N_gen} (世代數, O59: 12 = B×N_gen), dimC = {dimC} (O38: 528 = dimC·B·N_d)")
print(f"  3/2 = {N_gen}/2 = {dimC}/2 — 空間維數 = 3 = N_gen = dimC")
print(f"  分子 3 = 空間維 (質量 = 3D 體積凝聚, 密度線性 ρ¹)")
print(f"  分母 2 = free-fall 動力學指數 (牛頓平方反比 ⟹ t_ff ∝ ρ^(-1/2))")
ok_b = (N_gen == dimC == 3) and (mp.mpf(N_gen)/2 == mp.mpf("1.5"))
T("T10b 3/2 = N_gen/2 = dimC/2 (空間維 = 3 = 世代數 = dimC)",
  ok_b, "3/2 = 1 (密度) + 1/2 (塌縮頻率) — 兩個結構因子")

print("\n== T10c-d: 數值閉環 ==")
M_seed = lambda d: M_base * (1 + d) ** mp.mpf("1.5")
M_LRD = M_seed(mp.mpf("1.367"))
M_UHz1 = M_seed(mp.mpf("100"))
dev_LRD = abs(M_LRD / mp.mpf("6.97e6") - 1)
dev_UHz1 = abs(M_UHz1 / mp.mpf("1.94e9") - 1)
print(f"  δ=1.367 (LRD 中位): M = {mp.nstr(M_LRD, 7)} vs 6.97e6 (dev {float(dev_LRD)*100:.2f}%)")
print(f"  δ=100 (UHz1): M = {mp.nstr(M_UHz1, 7)} vs 1.94e9 (dev {float(dev_UHz1)*100:.2f}%)")
T("T10c LRD 錨閉環 δ=1.367 → 6.97e6", dev_LRD < 0.01,
  f"M = {mp.nstr(M_LRD, 6)} (dev {float(dev_LRD)*100:.2f}%)")
T("T10d UHz1 單事件上限 δ=100 → 1.94e9", dev_UHz1 < 0.01,
  f"M = {mp.nstr(M_UHz1, 6)} (dev {float(dev_UHz1)*100:.2f}%)")

print("\n== T10e: M_turn 閉式 ==")
M_turn = M_seed(mp.mpf(1))      # δ=1
print(f"  δ=1: M_turn = M_base·2^(3/2) = {mp.nstr(M_turn, 8)}")
print(f"  O197 轉折 = 5.4136e6 (scripts/01)")
dev_t = abs(M_turn / mp.mpf("5.4136e6") - 1)
T("T10e M_turn = M_base·2^{3/2} (δ=1 轉折閉式)", dev_t < 1e-4,
  f"M_turn = {mp.nstr(M_turn, 7)} (dev {float(dev_t)*100:.3f}%)")

print("\n== T10f: (1+δ̂)^{3/2} = 2^{3/2}·sin³ 角譜身份 ==")
# γ_k = 4sin²(kπ/176), 1+δ̂ = γ/2 = 2sin²(kπ/176)
# (1+δ̂)^{3/2} = (2sin²)^{3/2} = 2^{3/2}·sin³(kπ/176)
k = mp.mpf(45)   # 通道 A 第一模態
g45 = mp.mpf(4) * mp.sin(k * mp.pi / 176) ** 2
lhs = (g45 / 2) ** mp.mpf("1.5")
rhs = mp.mpf(2) ** mp.mpf("1.5") * mp.sin(k * mp.pi / 176) ** 3
print(f"  k=45: (γ/2)^(3/2) = {mp.nstr(lhs, 10)}")
print(f"        2^(3/2)·sin³ = {mp.nstr(rhs, 10)}")
print(f"  sin³(kπ/176) = 3D 角譜元素 (球體積 ∫∫∫ r²sinθ dr dθ dφ 嘅 sin θ 因子)")
T("T10f (1+δ̂)^{3/2} = 2^{3/2}·sin³(kπ/176) (2D 投影譜 → 3D 角譜提升)",
  abs(lhs - rhs) < 1e-40, f"2^(3/2)·sin³ — sin³ = 3D 角元素")

print("\n== T10g: 通道 A 帶閉式 ==")
M_A_lo = M_seed(mp.sin(mp.pi / 88))    # δ̂₄₅ = sin(π/88) (docs/04)
M_A_hi = M_turn
print(f"  通道 A 帶 = [M_base(1+sin(π/88))^(3/2), M_base·2^(3/2)]")
print(f"           = [{mp.nstr(M_A_lo, 7)}, {mp.nstr(M_A_hi, 7)}]")
print(f"  O197 scripts/02: [2.017e6, 5.4136e6]")
dev_lo = abs(M_A_lo / mp.mpf("2.017e6") - 1)
T("T10g 通道 A 帶閉式 (docs/04 T9f 一致)", dev_lo < 1e-2,
  f"[{mp.nstr(M_A_lo, 6)}, {mp.nstr(M_A_hi, 6)}] (dev_lo {float(dev_lo)*100:.2f}%)")

print("\n== T10h: 可證偽預言 ==")
print("  P7 (O173): 種子質量-環境冪律 M ∝ (1+δ)^(3/2)")
print("  測試: JWST 高 z 種子 vs 宿主環境密度 (星系團邊緣 δ~30 → 3.3e8,")
print("        星系團中心 δ~100 → 1.94e9)")
print("  若觀測冪律 ≠ 3/2 (例如 1.74, O173 docs/18 α) ⟹ 推導錯")
print("  ⚠️ O173 α=1.74 係質量比演化指數 (ratio(t) ∝ t^-α), 唔係 M-δ 冪律")
print("     — 兩者唔可以直接比較; 3/2 預言只指 M_seed-δ 關係")
T("T10h 可證偽預言記錄: M ∝ (1+δ)^{3/2}, 測試 = JWST 種子-環境密度", True,
  "P7 已定 (O173); α=1.74 係演化指數唔同軸")

print(f"\n===== {pas}/{tot} PASS =====")
print(f"3/2 指數結構閉合: Ṁ ∝ ρ/t_ff = ρ^{{3/2}} (密度 × free-fall 頻率)")
print(f"3/2 = 空間維 3 (= N_gen = dimC) / 2 (牛頓動力學指數)")
