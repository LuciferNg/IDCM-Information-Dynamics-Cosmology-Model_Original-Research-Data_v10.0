#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ckm 50 — P7 (tanβ) 機制包: 跡恆等式 + 邊界模式 + 反週期性
==========================================================
候選: tanβ = L₄·43/L₅ = 7×43/11 = 27.363636 (0.004%, 0.005% 窗唯一)
機制包 (本輪):
  M1  跡恆等式: 301 = 7×43 = Σγ + L₁₀ = Tr(Δ_88) + Tr(T̂¹⁰)
      → tanβ = [Tr(Δ_88) + Tr(T̂¹⁰)]/Tr(T̂⁵) — 全跡算子形式
  M2  邊界模式: 43 = N_d−1 = 4L₅−1 = B·L₅−1; ω₄₃ = ω₄₅ (Z₂ 簡併);
      對 (43,45) 括住 44 = μ² site (O155 T20)
  M3  反週期性: n·L ≡ 44 mod 88, L = 44 → n 奇 (觀察者 sector); 43 ∈ 奇
  M4  v_d 一致: tanβ = 301/11, v = 246.22 → v_d = 8.993 ≈ L₆/2 = 9 (0.08%)
  M5  純跡包裝: tanβ = 4L₁₀/L₆ = 27.333 (0.107%) — 記錄 (精度差 25×)
裁決: 機制包一致但「v_u/v_d 為何投影至此」仍未推導 → P7 🟡 (強化), 定理開放
"""
import math
import mpmath as mp

mp.mp.dps = 60
PASS = 0
FAIL = 0

def chk(name, val, target, tol, unit=""):
    global PASS, FAIL
    ok = abs(val - target) <= tol * max(1.0, abs(target))
    if ok:
        PASS += 1
        print(f"  [✔] {name} = {val:.8f} {unit} (dev {(val-target)/max(abs(target),1e-30)*100:+.5f}%)")
    else:
        FAIL += 1
        print(f"  [✘] {name} = {val:.8f} {unit} ≠ {target:.8f} (dev {(val-target)/max(abs(target),1e-30)*100:+.5f}%)")

TANB = 27.3625
# 框架基本量
SIGMA_GAMMA = 178       # Σγ 88 模總和 = 2F₁₁ (memory)
phi = (1+math.sqrt(5))/2
L = {n: round(phi**n + (-phi)**(-n)) for n in range(1, 13)}  # Lₙ = φⁿ+(−φ)⁻ⁿ
F = [0, 1]
for i in range(2, 14):
    F.append(F[-1] + F[-2])

print("=" * 72)
print("M1. 跡恆等式: tanβ = (Σγ + L₁₀)/L₅ = (Tr(Δ)+Tr(T̂¹⁰))/Tr(T̂⁵)")
print("=" * 72)
print(f"  Σγ = 178 (Tr(Δ_88), 88-site Laplacian 跡), L₁₀ = {L[10]} (Tr(T̂¹⁰)), L₅ = {L[5]} (Tr(T̂⁵))")
print(f"  Σγ + L₁₀ = {SIGMA_GAMMA + L[10]} = 301")
print(f"  L₄·43 = 7×43 = {7*43} = 301 ✓ (L₄ = {L[4]})")
t1 = (SIGMA_GAMMA + L[10]) / L[5]
print(f"  tanβ = (178+123)/11 = {t1:.8f}")
chk("M1 跡形式 = 27.363636", t1, 27.3636363636, 1e-9)
chk("M1 vs 半經驗 27.3625", t1, TANB, 5e-5)
print(f"  身份鏈: L₄·43 = L₄(B·L₅−1) = 7(4×11−1) = 28×11−7 = 301; tanβ = L₄(B−1/L₅) = 7(4−1/11)")

print()
print("=" * 72)
print("M2. 邊界模式身份: 43 = N_d−1 = B·L₅−1; (43,45) 括住 μ² site 44")
print("=" * 72)
print(f"  43 = 44−1 = N_d−1 = 4×11−1 = B·L₅−1 ✓; 45 = N_d+1")
w43 = 2*mp.sin(43*mp.pi/88); w45 = 2*mp.sin(45*mp.pi/88)
print(f"  ω₄₃ = {mp.nstr(w43, 12)}, ω₄₅ = {mp.nstr(w45, 12)} — Z₂ 簡併 ω₄₃ = ω₄₅ (對偶 n ↔ 88−n)")
chk("ω₄₃ = ω₄₅ (Z₂ 簡併)", float(w43), float(w45), 1e-30)
g44 = 4*mp.sin(44*mp.pi/88)**2
print(f"  γ₄₄ = {mp.nstr(g44, 8)} = μ² — 對 (43,45) 括住嘅中央 site (O155 T20 邊界對)")

print()
print("=" * 72)
print("M3. 反週期性: n·L ≡ 44 (mod 88), L = 44 → n 奇 = 觀察者 sector")
print("=" * 72)
for Lv in (44, 88):
    sols = [n for n in range(1, 89) if (n*Lv) % 88 == 44]
    print(f"  L = {Lv}: n·{Lv} ≡ 44 mod 88 → n ∈ {{{','.join(map(str, sols[:8]))}{'...' if len(sols)>8 else ''}}} (共 {len(sols)} 個)")
print(f"  43 奇 (觀察者 sector) ✓ — 邊界模式係反週期費米子模式 (O137: 費米子反週期 n·L≡44)")

print()
print("=" * 72)
print("M4. v_d 一致: tanβ = 301/11, v = 246.22 → v_d ≈ L₆/2 = 9")
print("=" * 72)
v = 246.22
tanb = 301/11
cosb = 1/math.sqrt(1 + tanb**2)
sinb = tanb*cosb
vd = v*cosb
vu = v*sinb
print(f"  cosβ = 11/√(301²+11²) = {cosb:.8f}")
print(f"  v_d = v·cosβ = {vd:.4f} GeV vs L₆/2 = {L[6]/2} (N_gen² = 9): dev {(vd-L[6]/2)/9*100:+.3f}%")
print(f"  v_u = v·sinβ = {vu:.2f} GeV vs 2L₁₀ = {2*L[10]}: dev {(vu-2*L[10])/(2*L[10])*100:+.3f}%")
chk("v_d ≈ L₆/2 = 9 GeV", vd, L[6]/2, 1e-3)
chk("v ≈ 2L₁₀ = 246", v, 2*L[10], 1e-3)

print()
print("=" * 72)
print("M5. 純跡包裝對照: tanβ = 4L₁₀/L₆ = 27.333 (v_u = 2L₁₀, v_d = L₆/2)")
print("=" * 72)
t5 = 4*L[10]/L[6]
print(f"  4×123/18 = {t5:.4f} (dev {(t5-TANB)/TANB*100:+.3f}%) — 機制更直接但精度 25× 差")
print(f"  兩個包裝: (Σγ+L₁₀)/L₅ = 27.3636 (0.004%) vs 4L₁₀/L₆ = 27.333 (0.107%)")

print()
print("=" * 72)
print("裁決: P7 機制包狀態")
print("=" * 72)
print("  ✅ 一致包裝: tanβ = (Tr(Δ_88)+Tr(T̂¹⁰))/Tr(T̂⁵) = L₄·43/L₅ (全跡/全結構量)")
print("  ✅ 邊界: 43 = B·L₅−1, (43,45) 括 μ², ω 簡併, 反週期奇 sector")
print("  ✅ v_d = 8.993 ≈ L₆/2 = N_gen² (0.08%)")
print("  🔴 未推導: 點解 v_u/v_d 必然 = [Tr(Δ)+Tr(T̂¹⁰)]/Tr(T̂⁵) — 機制包係一致描述, 唔係定理")
print("  ⇒ P7 維持 🟡 (強化), 唔宣稱 🟢")
print()
print(f"RESULT: {PASS}/{PASS+FAIL} PASS")
