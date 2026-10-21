#!/usr/bin/env python3
"""
O257 scripts/11 — R3 收口: 三形式精度比較 + ε 結構身份判定 (2026-10-21)
========================================================================
R2-R3 核心: M_pl/M_comp ≈ N_d³×γ₄₄×(1+ε)/⁷⁶√10 (≈ 88³/2 × ...)

本 script:
  A. 三形式精度比較 (vs 校準 3.6909e13):
     1. O66 log 形式: M_comp = M_pl·10^{−(1/γ₆−1/76)}
     2. 無log形式:    M_comp = M_pl·⁷⁶√10/(N_d³×γ₄₄)
     3. ε 修正形式:   M_comp = M_pl·⁷⁶√10/(N_d³×γ₄₄×(1+ε))
  B. ε 嘅 operator 候選結構掃描:
     ε = 0.0011835518938...
     - 1/845 (F₅×F₇²): dev 0.010%
     - 測 ε ≈ γ₆²/L?、ε ≈ 1/(88×9.6)?
  C. ★ 重大重寫: ε 有冇可能係 γ₆ 自身嘅函數?
     ε+1 = 10^{1/γ₆}/(88³/2) → ln(1+ε) = (1/γ₆)ln10 − ln(88³/2)
     睇 ln(1+ε) 有冇身份
  D. 判定: O257 無log重構是否「名義一致」(dev < 0.1% vs 校準)?
"""
import mpmath as mp
mp.mp.dps = 80

phi = (mp.mpf(1) + mp.sqrt(5)) / 2
B, Nd, N, Ngen = 4, 44, 88, 3

def gamma(n, NN=N):
    return 4 * mp.sin(n * mp.pi / NN) ** 2

passed = 0
failed = 0
def ck(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  [PASS] {name} {detail}")
    else:
        failed += 1
        print(f"  [FAIL] {name} {detail}")

print("=" * 72)
print("O257 scripts/11 — R3 收口: 三形式精度 + ε 判定")
print("=" * 72)

g6 = gamma(6)
M_pl = mp.mpf("1.2209e19")
M_cal = mp.mpf("3.6909e13")
target_log10 = 1/g6 - 1/mp.mpf(76)

# ── A. 三形式 ──
print("[A] 三形式 vs 校準")
M_o66 = M_pl * mp.power(10, -target_log10)          # O66 log form
Nd3g44 = Nd**3 * gamma(44)                          # 88³/2 = N_d³×γ₄₄
root76 = mp.power(10, mp.mpf(1)/76)                 # ⁷⁶√10
M_nolog = M_pl * root76 / Nd3g44                    # 無log
eps = mp.power(10, 1/g6)/Nd3g44 - 1                 # ε
M_eps = M_pl * root76 / (Nd3g44 * (1+eps))          # ε 修正 (厳密 = M_o66)

for name, M in [("O66 log", M_o66), ("無log", M_nolog), ("ε修正(=O66)", M_eps)]:
    dev_cal = abs(M - M_cal)/M_cal*100
    dev_o66 = abs(M - M_o66)/M_o66*100
    print(f"  {name:10s}: {mp.nstr(M, 12)}  dev vs 校準 {mp.nstr(dev_cal, 6)}%  vs O66 {mp.nstr(dev_o66, 6)}%")
ck("無log形式名義一致 (<0.1% vs 校準)", abs(M_nolog - M_cal)/M_cal < 0.001,
   f"(dev {mp.nstr(abs(M_nolog-M_cal)/M_cal*100,5)}%)")
ck("無log形式誤差級同 O66 相若 (Δdev < 0.05%)", abs(abs(M_nolog-M_cal)/M_cal - abs(M_o66-M_cal)/M_cal) < 0.0005,
   f"(Δ = {mp.nstr(abs(abs(M_nolog-M_cal)/M_cal - abs(M_o66-M_cal)/M_cal)*100,5)}%)")
print()

# ── B. ε 候選 ──
print("[B] ε operator 候選")
eps = mp.power(10, 1/g6)/(88**3/2) - 1
print(f"  ε = {mp.nstr(eps, 16)}")
cands = {
  "1/845 (F₅F₇²)": 1/mp.mpf(845),
  "1/844": 1/mp.mpf(844),
  "1/(L₄×L₇×4)": 1/mp.mpf(812),
  "1/(88×9.6)": 1/mp.mpf(88*9.6),
  "1/(88×9.602)": None,
  "γ₆/152.7": g6/mp.mpf(152.7),
  "1/(L₆×47)": 1/mp.mpf(18*47),
  "1/(L₆×L₈)": 1/mp.mpf(18*47),
  "1/(44×19.2)": 1/mp.mpf(44*19.2),
  "1/(90×9.388)": None,
}
for name, v in cands.items():
    if v is None: continue
    dev = abs(eps - v)/eps*100
    print(f"    {name} = {mp.nstr(v, 12)}  dev {mp.nstr(dev, 6)}%")
# ε×88^n 家族
print(f"  ε×88   = {mp.nstr(eps*88, 12)}")
print(f"  ε×90   = {mp.nstr(eps*90, 12)}")
print(f"  ε×176  = {mp.nstr(eps*176, 12)}")
print(f"  ε×7744 = {mp.nstr(eps*7744, 12)}  (9.165?)")
print(f"  ε/γ₆   = {mp.nstr(eps/g6, 12)}")
print()

# ── C. ln(1+ε) 身份 ──
print("[C] ln(1+ε) = (1/γ₆)ln10 − ln(88³/2)")
l = mp.log(1+eps)
print(f"  ln(1+ε) = {mp.nstr(l, 16)}")
print(f"  = (1/γ₆)ln10 − ln(88³/2)")
term1 = mp.log(10)/g6
term2 = mp.log(mp.mpf(88)**3/2)
print(f"  = {mp.nstr(term1, 12)} − {mp.nstr(term2, 12)}")
print(f"  ln(1+ε)×88 = {mp.nstr(l*88, 12)}")
print(f"  ln(1+ε)×7744 = {mp.nstr(l*7744, 12)}")
# 若能 = γ₆/88^2? 
cand_l = g6/7744
print(f"  γ₆/88² = {mp.nstr(cand_l, 14)}  dev {mp.nstr(abs(l-cand_l)/cand_l*100,5)}%")
one_88sq = 1/mp.mpf(88)**2
print(f"  1/88²  = {mp.nstr(one_88sq, 14)}  dev {mp.nstr(abs(l-one_88sq)/one_88sq*100,5)}%")
print()

# ── D. 判定 ──
print("[D] 判定")
print("  1. O66 log 形式 (dev 0.052% vs 校準) = ω0 本體公式 — 有 1/γ₆−1/76")
print("  2. 無log形式 (dev 0.066% vs 校準) = 譜積/root 重構, 零任意常數:")
print("     M_comp ≈ M_pl × ⁷⁶√10 / (N_d³ × γ₄₄)")
print("     = M_pl × 10^{1/(88−hop_max)} / (44³ × 4·sin²(44π/88))")
print("  3. ε 殘差 (0.012% off 無log) 未有 EXACT operator 身份:")
print("     1/ε = 844.914 vs 845 = F₅×F₇² dev 0.010% — 近對偶, 唔升格")
print("  4. 結論: 無log重構達成「名義一致」, log 確認為觀測者計數壓縮;")
print("     精確閉合仍由 O66 原式持有 (0.052% vs 校準)")
print("  5. 「大數約化」答案: M_pl/M_comp ≈ 44³×4 / ⁷⁶√10 —")
print("     大數 = 鏈體積(三維 44³) × Nyquist 譜值(4) ÷ hop-root(⁷⁶√10)")

print("\n" + "=" * 40)
print(f"RESULT: {passed}/{passed+failed} PASS")