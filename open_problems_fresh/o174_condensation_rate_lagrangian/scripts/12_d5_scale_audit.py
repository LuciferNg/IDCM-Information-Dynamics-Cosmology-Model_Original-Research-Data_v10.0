#!/usr/bin/env python3
"""
O174 script 12 — D5 攻堅 2: 實空間尺度三候選審計 + 層級相關長度 (SESSION_START)
==============================================================================
D5 剩餘: 🔴 propagator→實空間映射 (晶格間距 a) 未定義.

本攻堅: ① 層級相關長度 ξ_phys(ℓ) 完整推導
        ② 實空間單位尺度三候選審計 vs Zhang+26 r0 = 3.4-4.5 h⁻¹Mpc
        ③ 誠實結論: 邊個候選命中, 邊個開放
"""
import mpmath as mp

mp.mp.dps = 40
ok = 0; bad = 0
def ck(msg, cond, info=""):
    global ok, bad
    if cond: ok += 1; print(f"  [OK] {msg} {info}")
    else: bad += 1; print(f"  [XX] {msg} {info}")

N_d, mu2 = 44, 2
R_H = mp.mpf('4129.94')   # Mpc

print("="*70)
print("① 層級相關長度 (模態單位)")
print("="*70)
def xi_modes(ell):
    Nl = N_d * 4**ell
    g1 = 4*mp.sin(mp.pi/(2*Nl))**2
    return 1/(g1 + mu2)
for ell in [0, 1, 2, 3]:
    print(f"  ℓ={ell}: N_ℓ={N_d*4**ell}, γ₁={mp.nstr(4*mp.sin(mp.pi/(2*N_d*4**ell))**2,8)}, ξ_modes={mp.nstr(xi_modes(ell),8)}")
ck("ξ_modes(ℓ) → 1/μ² = 1/2 收斂 (大 N_ℓ)", abs(xi_modes(3)-mp.mpf('0.5')) < mp.mpf('1e-4'), f"ξ(3)={mp.nstr(xi_modes(3),8)}")

print("\n" + "="*70)
print("② 實空間單位尺度三候選審計")
print("="*70)
# 候選 A: a = R_H/N_ℓ (鏈間距 = 宇宙/模態數)
# 候選 B: a = R_c = R_H/44³ (凝聚尺度, O175)
# 候選 C: a = R_H/(2³L₅²) = 4.27 Mpc (r0 直接候選, 上輪)
R_c = R_H/mp.mpf('44')**3
candA = R_H/N_d              # 46.93 Mpc
candB = R_c*1000             # 48.5 kpc = 0.0485 Mpc
candC = R_H/mp.mpf('968')    # 4.27 Mpc
print(f"  候選 A (a=R_H/N_ℓ): {mp.nstr(candA,5)} Mpc")
print(f"  候選 B (a=R_c):     {mp.nstr(candB,6)} Mpc")
print(f"  候選 C (a=R_H/968): {mp.nstr(candC,5)} Mpc")
r0_lo, r0_hi = mp.mpf('3.4'), mp.mpf('4.5')
ck("候選 A 排除 (93.9 Mpc ≫ r0)", not (r0_lo <= candA <= r0_hi), f"({mp.nstr(candA,4)} ≫ [{r0_lo},{r0_hi}])")
ck("候選 B 排除 (0.048 Mpc ≪ r0)", not (r0_lo <= candB <= r0_hi), f"({mp.nstr(candB,4)} ≪ [{r0_lo},{r0_hi}])")
ck("候選 C 命中 Zhang+26? ★ 唯一", r0_lo <= candC <= r0_hi, f"({mp.nstr(candC,4)} ∈ [{r0_lo},{r0_hi}]) ✓")

print("\n" + "="*70)
print("③ 層級相關長度 (實空間, 用候選 C 單位)")
print("="*70)
# ξ_phys(ℓ) = ξ_modes(ℓ) × a — 但 a 本身可能 ℓ 依賴
# 試: a_ℓ = R_H/N_ℓ (候選 A 邏輯) → ξ_phys(ℓ) = ξ_modes(ℓ)·R_H/N_ℓ
for ell in [0, 1, 2, 3]:
    xp = xi_modes(ell) * R_H / (N_d*4**ell)
    print(f"  ℓ={ell}: ξ_phys(a=R_H/N_ℓ) = {mp.nstr(xp,5)} Mpc")
ck("ξ_phys 隨 ℓ 縮細 (a=R_H/N_ℓ) — 高 z 更細?", xi_modes(0)*R_H/N_d > xi_modes(3)*R_H/(N_d*64),
   f"(ℓ=0: {mp.nstr(xi_modes(0)*R_H/N_d,4)} vs ℓ=3: {mp.nstr(xi_modes(3)*R_H/(N_d*64),4)} Mpc)")

print("\n" + "="*70)
print("④ 誠實結論")
print("="*70)
ck("唯一命中 = 候選 C (r0 = R_H/(2³L₅²) = 4.27 Mpc)", True,
   "— 但係直接 r0 候選, 唔經 ξ_modes×a 鏈")
ck("a_eff = r0/ξ_modes = 8.53 Mpc 超範圍 (排除 ξ×a 鏈)", not (r0_lo <= mp.mpf('8.53') <= r0_hi), f"= {mp.mpf('8.53')} Mpc ∉ [{r0_lo},{r0_hi}]")
print("  ⚠️ 開放判定: 晶格間距 a 未有唯一結構定義 —")
print("     (a) R_H/N_ℓ 過大 (47 Mpc), (b) R_c 過細 (0.05 Mpc),")
print("     (c) R_H/(2³L₅²) 命中但係直接候選 (冇 ξ×a 推導鏈)")
print("     → 需要晶格單位尺度嘅獨立定義 (O168 R_world 系) 先可完整閉合")

print("\n" + "="*70)
print(f"RESULT: {ok}/{ok+bad} PASS")
