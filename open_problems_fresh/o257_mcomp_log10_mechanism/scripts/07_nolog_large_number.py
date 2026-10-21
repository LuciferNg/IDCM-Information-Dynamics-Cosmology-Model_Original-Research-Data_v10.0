#!/usr/bin/env python3
"""
O257 scripts/07 — 無 log 大數約化探索 (2026-10-21)
=====================================================
調律者 steers: 「邏輯上好像不應該有log, 對數不像是天然產物」+
「大數是否存在天然機制約化」

轉向: 唔再問「log10 空間點解有 −1/76 修正」, 而係問:
  M_pl/M_comp ≈ 3.3096e5 呢個大數, 有冇唔經 log 嘅直接結構身份?

關鍵觀察: P6 docs/08 否定咗「譜積路」, 但佢掃嘅係 log(Πγ_sub)/ln 商 —
        即「乘法 → log」形式。佢冇掃過「純商譜 Πγ_A/Πγ_B (無 log)」。

本 script:
  A. M_pl/M_comp 直接結構掃描 (冪分解/γ組合/結構池)
  B. ★純商譜: Πγ_odd/Πγ_even、Πγ(1..k) 子集商 vs M_pl/M_comp (P6 冇做)
  C. seesaw 反向: M_pl/M_comp = M_pl·m_ν₃/(γ₆²v²) 檢驗
  D. 冪形式: (base)^{1/γ₆} 同 M_pl/M_comp 比對 — log 唔天然 → 冪先係本體
  E. 「10=2F₅ 冪」重構: M_comp = M_pl·(2F₅)^{−(1/γ₆−1/76)} = M_pl·(2F₅)^{−1/γ₆}·(2F₅)^{1/76}
     → 呢個係「指數 = 譜倒數」結構, log 只係人類計數
"""
import mpmath as mp
mp.mp.dps = 50

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
print("O257 scripts/07 — 無 log 大數約化探索")
print("=" * 72)

g6 = gamma(6)
target_log10 = 1/g6 - 1/mp.mpf(76)
M_pl = mp.mpf("1.2209e19")
M_comp_formula = M_pl * mp.power(10, -target_log10)
M_comp_o66 = mp.mpf("3.6890e13")
r_formula = M_pl / M_comp_formula
r_o66 = M_pl / M_comp_o66

print(f"M_pl/M_comp(formula) = {mp.nstr(r_formula, 16)}")
print(f"M_pl/M_comp(O66)     = {mp.nstr(r_o66, 16)}")
print(f"log10(r_formula)     = {mp.nstr(mp.log10(r_formula), 16)}")
print(f"target 1/γ₆−1/76     = {mp.nstr(target_log10, 16)}")
print()

# ── A. 冪分解 ──
print("[A] M_pl/M_comp 冪分解 (r = base^p)")
for name, base in [("88", 88), ("60", 60), ("10", 10), ("φ", phi), ("44", 44), ("90", 90), ("7744", 88*88), ("96", 96)]:
    p = mp.log(r_formula)/mp.log(base)
    print(f"  {name}^p: p = {mp.nstr(p, 10)}", end="")
    # 最近有理數
    near = mp.nint(p*100)/100
    if abs(p - near) < 0.02:
        print(f"  ← p≈{mp.nstr(near,4)} ({name}^{mp.nstr(near,4)} = {mp.nstr(mp.power(base, near), 8)})")
    else:
        print()

# γ 組合
print("\n  1/γ₆ = %s (O66 det ratio)" % mp.nstr(1/g6, 12))
print("  r×γ₆ =", mp.nstr(r_formula*g6, 10))
print("  r/(1/γ₆) =", mp.nstr(r_formula/(1/g6), 12))
print("  (88/γ₆)² =", mp.nstr((88/g6)**2, 8), " r/(88/γ₆)² =", mp.nstr(r_formula/(88/g6)**2, 8))
print("  r×γ₆/88² =", mp.nstr(r_formula*g6/7744, 8))
print("  r/(1/γ₆)/γ₆ =", mp.nstr(r_formula/(1/g6)/g6, 10), "(=r×γ₆²)")
print()

# ── B. ★純商譜 ──
print("[B] 純商譜 (無 log) — P6 冇掃過")
pg_odd = mp.fprod([gamma(k) for k in range(1,88,2)])
pg_even = mp.fprod([gamma(k) for k in range(2,89,2)])
pg_1_44 = mp.fprod([gamma(k) for k in range(1,45)])
pg_1_87 = mp.fprod([gamma(k) for k in range(1,88)])
pg_6_88 = mp.fprod([gamma(k) for k in range(6,89)])
print(f"  Πγ(1..87) = {mp.nstr(pg_1_87, 8)} (Chebyshev = 88² = 7744)")
print(f"  Πγ_odd    = {mp.nstr(pg_odd, 8)}")
print(f"  Πγ_even   = {mp.nstr(pg_even, 8)}")
print(f"  Πγ(1..44) = {mp.nstr(pg_1_44, 8)}")
print(f"  Πγ_odd/Πγ_even = {mp.nstr(pg_odd/pg_even, 8)}")
print(f"  Πγ_even/Πγ_odd = {mp.nstr(pg_even/pg_odd, 8)}")

# γ 商譜可能性: M_pl/M_comp 係 3.3e5; γ∈(0,4), 所以最少要 ~10 個 γ 嘅商
# 但 P6 掃過 log form。試「去 log 化」: M_pl/M_comp 直比的「對數」= 1/γ₆-1/76
# ln(r) = ln10×(1/γ₆−1/76) = 12.7097
# → r = e^{12.7097}。e 唔天然。但 r = Πγ_A/Πγ_B 天然。

# 子譜商: 搵 A,B disjoint, Πγ_A/Πγ_B ≈ 3.3e5
# Δln = ln(r) = 12.7097。γ_k 嘅 ln 分佈 — 用 greedy
import itertools
# 一個 γ 嘅 ln: ln γ ∈ (-inf, 1.386)
# 要總和 12.71 → 至少要 ~9-10 個「laeger γ」嘅 ln 差
# 試固定對稱組合:
# 對 k=1..44: γ_k = γ_{88-k}。全對 {k, 88-k} 商 = 1 平凡。
# 試: Πγ(1..6)/Πγ(7..12)?
def pg(ks): return mp.fprod([gamma(k) for k in ks])
cand_subs = {
  "Π(1..6)/Π(7..12)": pg(range(1,7))/pg(range(7,13)),
  "Π(1..8)/Π(9..16)": pg(range(1,9))/pg(range(9,17)),
  "Π(1..12)/Π(13..24)": pg(range(1,13))/pg(range(13,25)),
  "Π(1..22)/Π(23..44)": pg(range(1,23))/pg(range(23,45)),
  "Π(1..10)/Π(11..20)": pg(range(1,11))/pg(range(11,21)),
  "Π(1..44)/Π(45..88)": pg(range(1,45))/pg(range(45,89)),
}
print("\n  子譜商 (一大一小) vs r =", mp.nstr(r_formula, 6), ":")
for name, v in cand_subs.items():
    d_ln = abs(mp.log(v) - mp.log(r_formula))
    print(f"    {name} = {mp.nstr(v, 8)}  |ln差| = {mp.nstr(d_ln, 5)}")

# ── C. seesaw 反向 ──
print("\n[C] seesaw 反向: M_pl/M_comp = M_pl·m_ν₃/(γ₆²v²)")
m_nu3_eV = mp.mpf("0.05")
m_nu3_GeV = m_nu3_eV * mp.mpf("1e-9")
v = mp.mpf("246.2196")
num = M_pl * m_nu3_GeV
den = (g6*v)**2
ratio_ss = num/den
print(f"  (γ₆v)²/m_ν₃ = {mp.nstr((g6*v)**2/m_nu3_GeV, 8)} GeV  vs M_comp = {mp.nstr(M_comp_formula, 8)}")
print(f"  M_pl·m_ν/(γ₆v)² = {mp.nstr(ratio_ss, 8)}  vs M_pl/M_comp = {mp.nstr(r_formula, 6)}")
# m_ν₃ 幾多先啱? 反推
m_req = den/M_comp_formula/mp.mpf("1e-9")
print(f"  m_ν₃ 需要 = {mp.nstr(m_req, 8)} eV 先使 (γ₆v)²/M_comp = m_ν₃ (≈0.05)")
print(f"  對照 m_ν₃ IDCM: 0.0499 eV? (P6 m₃=(γ₆v)²/M_comp)")
ck("(γ₆v)²/M_comp 閉合 m_ν₃≈0.05eV (order check)", abs(m_req - mp.mpf("0.05"))/mp.mpf("0.05") < 0.1,
   f"(m_req={mp.nstr(m_req,6)} eV)")

# ── D. 冪形式: (base)^{1/γ₆} ──
print("\n[D] 冪形式: (base)^{1/γ₆} vs r")
for name, base in [("88",88),("60",60),("44",44),("90",90),("96",96),("φ",phi),("2F₅",10),("7744",7744)]:
    val = mp.power(base, 1/g6)
    d = abs(val - r_formula)/r_formula
    flag = "  ★" if d < 0.02 else ""
    print(f"  {name}^{{1/γ₆}} = {mp.nstr(val,9)} vs r={mp.nstr(r_formula,8)}: dev {mp.nstr(d*100,4)}%{flag}")
# 39.2: ln
print()
print("  ln(r) =", mp.nstr(mp.log(r_formula), 10), "= ln10×(1/γ₆−1/76)")
print("  ln10/γ₆ - ln10/76 =", mp.nstr(mp.log(10)/g6 - mp.log(10)/76, 10))
# γ 冪: γ₆^{-p}?
for p in [1, 2, 3, 4]:
    val = g6**(-p)
    print(f"  γ₆^(-{p}) = {mp.nstr(val, 10)} (x88 = {mp.nstr(val*88, 8)})", end="")
    print("  ← vs r/88 =", mp.nstr(r_formula/88, 8) if p==1 else "")

# ── E. 重构: (2F₅)^{1/γ₆}×(2F₅)^{−1/76} ──
print("\n[E] 冪重構 (log 只係計數壓縮)")
print(f"  M_comp = M_pl×(2F₅)^(1/76−1/γ₆) = {mp.nstr(M_comp_formula, 8)} GeV")
x = mp.power(10, 1/g6)
y = mp.power(10, -1/mp.mpf(76))
print(f"  → M_pl/M_comp = 10^(1/γ₆) × 10^(−1/76)")
print(f"                  = {mp.nstr(x, 9)} × {mp.nstr(y, 9)}")
print(f"                  = {mp.nstr(x*y, 9)}")
ck("冪重構代數", abs(x*y - r_formula) < 1e-20)
print("  「−1/76 修正」=? 10^(−1/76) = ⁷⁶√(1/10) = 1/⁷⁶√10 = 1/1.030756…")
print("  即 M_comp = M_pl × 10^{−1/γ₆} × (1/⁷⁶√10)")
# 呢個「×1/⁷⁶√10」有冇 operator 意義? 76次方根 = 「除一個 76th root」
print("\n  ★ 關鍵: log 唔天然 → 10^{1/γ₆} 先係 operator (冪, 非 log)")
print("    「1/γ₆−1/76 加法」= 冪空間嘅乘法因子 (×10^{−1/γ₆}×10^{1/76})")
print("    log 只係人類計數(magnitude counting), 冪先係 IDCM 本體(0,1→φ 乘法結構)")

print("\n" + "=" * 40)
print(f"RESULT: {passed}/{passed+failed} PASS")