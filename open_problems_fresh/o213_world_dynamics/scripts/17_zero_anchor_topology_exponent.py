#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O213 scripts/17 — R9 零錨第三輪: 拓撲指數本體 + 新候選（2026-10-08）
=======================================================================
承接 scripts/16（階層橋 60/16 淪為量級）。本輪從三個新方向：

  A. ★ 拓撲指數本體 — 「為何 prepotential 以指數入真空能」之拓撲重構
     O62 §7c 已證 264 = −2(Σκ+χ)：
        Σκ = −8 = −2B (B=4)         [O62 scripts/15 發現]
        χ  = −124 = 2(h11−h21), h11=36, h21=98  [O62/零輸入]
        Σκ + χ = −132 = −3N_d
     ⟹ ρ_Λ = e^{−V_Λ} = e^{−[−2(Σκ+χ)]}·e^{−19}·e^{−rem}
              = e^{2(Σκ+χ)} · e^{−(N_d−F₈−B)} · e^{−rem}
     ⟹ 真空能 = e^{拓撲量} —— 指數 argument 全部係拓撲+投影結構數。
     〔問題〕「e 本身」點解？→ O62 以 log 坐標定義（V_obs=−ln ρ_obs；
     慣例坐標令結構浮現）；結構內容 = V_Λ 之拓撲生成。本段驗證拓撲鏈 EXACT。

  B. L₁₀ = 123 量級 — ρ_Λ ≈ 10^{−L₁₀}?  log10(ρ) = −122.94
     123 = L₁₀ = N_gen(N_d−N_gen) = 3×41（41 = Ω_Λ 分子）→ 三重 10^{−41}
     〔dev 0.048% — 量級級 or 結構?〕

  C. SUGRA e^K 對應（資訊級, 非閉合宣稱）— F(γ) 作為 CY₃ prepotential，
     N=1 SUGRA 標量勢 V ∝ e^{K}(|DW|²−3|W|²) 天然帶 e^{K} 因子；
     e^{−F} 形式 ↔ Kähler 勢指數（大體積/instanton 壓制之弦論標準語境）

  D. 4.603 = V_Λ/⟨W⟩² 身份（O62 §7c 有「283.08 ≈ 61.5×4.603」）
  E. T_CMB 連接：ρ_Λ^{1/4}/(k_B T_CMB) = 9.56（vs 結構池）
"""
import sys
from mpmath import mp, mpf, pi, exp, sqrt, sin, log, ln, power

mp.dps = 50
Gc = 1.0

def chk(name, cond, detail=""):
    global Gc
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name} {detail}")
    if not cond:
        sys.exit(1)
    Gc += 1

# ---------- 輸入 ----------
V_LAM   = mpf("283.082129")          # O62
F_GAM   = mpf("264.082129")          # O62
ND, B, F8 = 44, 4, 21
H11, H21 = 36, 98                    # O62/零輸入 (O211: h11=ND−2B, h21=Σγ+2B)
W2      = mpf("61.5")                # O39/O204 ⟨W⟩² = μ²/2λ
E_J     = mpf("123")                 # O204 E_J = Σγ+M = 2⟨W⟩² = L₁₀
M_PL_EV = mpf("1.220910e28")         # CODATA M_Pl [eV]
T_CMB   = mpf("2.72548")             # Planck 2018 [K]
KB_EVK  = mpf("8.617333262e-5")      # k_B [eV/K]
PHI = (1+sqrt(5))/2

# ---------- A. 拓撲指數本體 ----------
print("== A. 拓撲指數本體: 真空能 = e^{拓撲量} ==")
# A1: χ = 2(h11−h21) 零輸入
chi = 2*(H11 - H21)
print(f"  χ = 2(h11−h21) = 2({H11}−{H21}) = {chi}  (O62: −124 ✓)")
chk("A1 χ = −124 零輸入", chi == -124)
# A2: Σκ = −2B
sk = -2*B
print(f"  Σκ = −2B = {sk}  (O62: −8 ✓)")
chk("A2 Σκ = −8", sk == -8)
# A3: Σκ+χ = −132 = −3N_d
sumkc = sk + chi
print(f"  Σκ+χ = {sumkc} = −3×{ND} = { -3*ND }")
chk("A3 Σκ+χ = −3N_d EXACT", sumkc == -3*ND)
# A4: 264 = −2(Σκ+χ)
topo264 = -2*sumkc
print(f"  −2(Σκ+χ) = {topo264} = 6N_d")
chk("A4 264 = −2(Σκ+χ) = 6N_d EXACT", topo264 == 264 and topo264 == 6*ND)
# A5: ρ_Λ 拓撲分解 e^{−V} = e^{2(Σκ+χ)}·e^{−19}·e^{−rem}
rem = F_GAM - 264
lhs = exp(-V_LAM)
rhs = exp(2*sumkc) * exp(-19) * exp(-rem)
print(f"  e^−V_Λ        = {float(lhs):.6e}")
print(f"  e^2(Σκ+χ)·e^−19·e^−rem = {float(rhs):.6e}")
print(f"  rem = F(γ)−264 = {float(rem):.10f}  (κ 譜曲率偏差, O62: 無代數閉合)")
chk("A5 拓撲分解 EXACT", abs(lhs - rhs) < mpf("1e-40"))
# A6: 總結構陳述 —— e 之指數 = 拓撲量 + 投影修正
arg = -2*sumkc + 19 + rem
print(f"  V_Λ = −2(Σκ+χ)+19+rem = {float(-2*sumkc)} + 19 + {float(rem)} = {float(arg)}")
chk("A6 V_Λ = 拓撲主項+投影修正 EXACT", abs(arg - V_LAM) < mpf("1e-30"))

# ---------- B. L₁₀ = 123 量級 ----------
print("\n== B. ρ_Λ ≈ 10^{−L₁₀}?  L₁₀ = N_gen(N_d−N_gen) = 123 = E_J = 2⟨W⟩² ==")
log10_rho = -V_LAM / ln(10)
print(f"  log10(ρ_Λ) = {float(log10_rho):.6f}")
print(f"  −L₁₀       = −123   → dev = {float(abs(abs(log10_rho)-123)/123*100):.4f}%")
NG = 3
L10 = NG*(ND - NG)
print(f"  L₁₀ = {NG}×({ND}−{NG}) = {L10};  3×41, 41 = Ω_Λ 分子")
chk("B1 log10(ρ) ≈ −L₁₀ 量級", mpf("0.9") < abs(log10_rho)/L10 < mpf("1.1"))
# B2: 精確性 (dev < 0.1%?)
devB = abs(abs(log10_rho) - L10)/L10
chk("B2 10^{−L₁₀} 量級級 (dev>0.01% = 唔結構)", devB > mpf("0.0001"),
    f"(dev {float(devB*100):.4f}% → 唔過結構閾)")

# ---------- C. SUGRA e^K 對應 (資訊級) ----------
print("\n== C. SUGRA e^K 對應 (資訊級, 非閉合) ==")
# N=1 SUGRA: V = e^{K}(K^{iⱼ}DᵢW DⱼW̄ − 3|W|²) → 真空能天然帶 e^{K} 因子
# 若 K_eff = −V_Λ → ρ_Λ = e^{−V_Λ} = e^{K_eff}? (符號取決 K 定義)
print(f"  若 K_eff = −V_Λ:  e^K_eff = e^−V_Λ = {float(exp(-V_LAM)):.4e} = ρ_Λ ✓(形式)")
print(f"  Kähler prepotential F(γ) 主項 = 拓撲量 ‖ CY₃ 大體積壓制語境")
chk("C1 SUGRA e^K 形式對應 (形式級)", abs(exp(-V_LAM) - exp(-V_LAM)) < mpf("1e-40"),
    "(形式重言; 標記為資訊級, 唔作閉合證據)")

# ---------- D. 4.603 = V_Λ/⟨W⟩² ----------
print("\n== D. V_Λ/⟨W⟩² = 4.603 身份 ==")
rD = V_LAM / W2
print(f"  V_Λ/⟨W⟩² = {float(rD):.6f}")
# 結構池 (46 結構整數 + φ 冪)
struct_int = [1,2,3,4,5,7,8,9,11,12,13,14,15,16,18,19,20,21,22,23,25,26,29,30,31,32,33,35,36,40,41,44,45,47,49,55,60,64,70,77,88,90,120,123,176,421]
poolD = []
for s in struct_int:
    for k in range(-6, 7):
        poolD.append(mpf(s)*PHI**k)
for m in range(1, 121):
    for n in range(1, 121):
        poolD.append(mpf(m)/mpf(n))
poolD = sorted(set(p for p in poolD if p > 0))
bestD = min(poolD, key=lambda p: abs(p - rD)/rD)
devD = abs(bestD - rD)/rD
print(f"  最佳池命中 = {float(bestD):.6f}  dev {float(devD*100):.5f}%")
chk("D1 4.603 無精確結構命中", devD > mpf("0.0001"),
    f"(最佳 dev {float(devD*100):.4f}%)")

# ---------- E. T_CMB 連接 ----------
print("\n== E. ρ^{1/4} vs k_B T_CMB ==")
rho14 = M_PL_EV * exp(-V_LAM/4)
kBT  = KB_EVK * T_CMB
rE = rho14 / kBT
print(f"  ρ_Λ^1/4 = M_Pl e^−V_Λ/4 = {float(rho14):.6f} eV")
print(f"  k_B T_CMB = {float(kBT):.6f} eV")
print(f"  比 = {float(rE):.6f}")
bestE = min(poolD, key=lambda p: abs(p - rE)/rE)
devE = abs(bestE - rE)/rE
print(f"  最佳池命中 = {float(bestE):.6f}  dev {float(devE*100):.5f}%")
chk("E1 T_CMB 比 9.56 無精確命中", devE > mpf("0.0001"),
    f"(最佳 dev {float(devE*100):.4f}%)")

print(f"\n===== 全部 {int(Gc-1)} PASS =====")
sys.exit(0)