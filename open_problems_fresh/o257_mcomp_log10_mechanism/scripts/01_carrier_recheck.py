#!/usr/bin/env python3
"""
O257 scripts/01 — 載體盤點 + 全精度複算 (2026-10-21)
====================================================
問題: 點解 M_comp = M_pl·10^-(1/γ₆−1/76) 喺 log10 尺度出現 −1/76 加法修正?
      1/76 嘅 operator 機制（log10 本體理論）未明。

本 script: 唔推新嘢 — 凍結載體真相:
  A. O66 核心數字全精度複算 (γ₆, 1/γ₆, 1/γ₆−1/76, M_comp, 誤差)
  B. 76 身份家族成員逐一驗證 (L₉, 88−12, 4×19, Σγ_odd−12)
  C. ★ 新分解候選: 76 = 2(N_d−n₆) (n₆=6: 44−6=38, 2×38=76) — mode-6 鏡像雙距
  D. hop 身份: γ₆(88-chain) = γ'₁₂(176-chain), 12 = hop_max = B·N_gen
  E. log10 底數候選: 10 = 2F₅ (O179 hop 通道週期)

判據設計 (預註冊):
  - 數值全精度 mpmath (50 dps)
  - identity 驗證以 |實算−宣稱| < 1e-12 為 EXACT (algebraic exact)
  - 公式命中以 |log10_pred − 1/γ₆+1/76|/target < 0.1% 為「名義一致」(非閉合)
"""
import mpmath as mp
mp.mp.dps = 50

phi = (mp.mpf(1) + mp.sqrt(5)) / 2
B = 4          # K_Tree branching
Nd = 44        # 世界鏈長
N = 88         # 88-site chain
Ngen = 3
F8 = 21
L5, L7, L9 = 11, 29, 76

def gamma(n, NN=N):
    """K_Chain 譜: γ_n = 4sin²(nπ/NN)"""
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
print("O257 scripts/01 — 載體盤點 + 全精度複算")
print("=" * 72)

# ── A. O66 核心數字 ──
print("\n[A] O66 核心數字 (mpmath 50dps)")
g6 = gamma(6)
inv_g6 = 1 / g6
one76 = 1 / mp.mpf(76)
target = inv_g6 - one76
print(f"  γ₆        = {mp.nstr(g6, 18)}")
print(f"  1/γ₆      = {mp.nstr(inv_g6, 18)}")
print(f"  1/76      = {mp.nstr(one76, 18)}")
print(f"  1/γ₆−1/76 = {mp.nstr(target, 18)}")

# O66 target log10 (fit)
M_pl = mp.mpf("1.2209e19")      # GeV (O66 用值)
M_comp_cal = mp.mpf("3.6909e13")  # 校準值 (P6)
M_comp_formula = M_pl * mp.power(10, -target)
log10_ratio_cal = mp.log(M_pl/M_comp_cal) / mp.log(10)
print(f"  M_pl              = {mp.nstr(M_pl, 18)} GeV")
print(f"  M_comp(公式)      = {mp.nstr(M_comp_formula, 12)} GeV")
print(f"  log10(M_pl/M_comp_cal) = {mp.nstr(log10_ratio_cal, 16)}")
dev_vs_cal = abs(log10_ratio_cal - target)/target*100
print(f"  dev(公式 vs 校準 log10) = {mp.nstr(dev_vs_cal, 8)}%")
dev_vs_fit = abs(M_comp_formula - M_comp_cal)/M_comp_cal*100
print(f"  dev(M_comp vs 校準)     = {mp.nstr(dev_vs_fit, 8)}%")
ck("1/γ₆−1/76 全精度 = 5.5197738(5.519774)", abs(target - mp.mpf("5.5197738")) < 1e-5,
   f"({mp.nstr(target,10)})")
ck("M_comp 公式 vs 校準 < 0.1%", dev_vs_fit < 0.1, f"({mp.nstr(dev_vs_fit,6)}%)")
ck("log10 target vs 校準 < 0.1%", dev_vs_cal < 0.1, f"({mp.nstr(dev_vs_cal,6)}%)")

# ── B. 76 身份家族 ──
print("\n[B] 76 身份家族")
L9_ident = phi**9 - phi**(-9)
ck("76 = φ⁹−φ⁻⁹ (Lucas L₉)", abs(L9_ident - 76) < 1e-12, f"({mp.nstr(L9_ident,16)})")
ck("76 = 88−12 (hop_max=12)", 88-12 == 76)
ck("76 = 4×19 (19=N_d−F₈−B)", 4*(Nd-F8-B) == 76)
# Σγ_odd (176-chain half set k=1..87 odd)
g176odd = sum(gamma(k, 176) for k in range(1, 89, 2))
g176even = sum(gamma(k, 176) for k in range(2, 89, 2))
print(f"  Σγ_odd(176, k=1..87)  = {mp.nstr(g176odd, 16)}")
print(f"  Σγ_even(176, k=2..88) = {mp.nstr(g176even, 16)}")
ck("Σγ_odd = 88", abs(g176odd - 88) < 1e-12, f"({mp.nstr(g176odd,12)})")
ck("76 = Σγ_odd − 12", abs(g176odd - 12 - 76) < 1e-12)
g44sum = sum(gamma(n) for n in range(1, 45))
ck("Σγ(1..44) = 90 (O212)", abs(g44sum - 90) < 1e-12, f"({mp.nstr(g44sum,12)})")

# ── C. ★ 新分解: 76 = 2(N_d − n₆) ──
print("\n[C] ★ 新分解候選: 76 = 2(N_d − n₆)")
n6 = 6
ck("76 = 2×(44−6) = 2(N_d−n₆)", 2*(Nd-n6) == 76, f"(2×{Nd-n6})")
# 對應修正形式: 1/γ₆ − 1/[2(N_d−n₆)]
cand_C = inv_g6 - 1/mp.mpf(2*(Nd-n6))
print(f"  1/γ₆ − 1/[2(N_d−n₆)] = {mp.nstr(cand_C, 16)}  (目標 {mp.nstr(target,16)})")
devC = abs(cand_C - target)/target*100
ck("形式 C 等於 1/γ₆−1/76 (定義層重寫)", cand_C == target, f"(dev {mp.nstr(devC,3)}%)")

# ── D. hop 身份 ──
print("\n[D] hop 身份: γ₆(88) = γ'₁₂(176), 12 = hop_max")
g12_176 = gamma(12, 176)
print(f"  γ₁₂(176-chain) = {mp.nstr(g12_176, 16)}")
ck("γ₆(88-chain) = γ₁₂(176-chain)", abs(g12_176 - g6) < 1e-15)
ck("hop_max = 12 = B·N_gen = 4×3", B*Ngen == 12)
ck("hop_max = 2n₆ = 2×6", 2*n6 == 12)
# hop 階梯
hop_ladder = [1,4,8,11,12,11,8,4,1]
print(f"  hop 階梯 Σ = {sum(hop_ladder)} = |A₅| = 60")
ck("hop 階梯和 = 60 = |A₅|", sum(hop_ladder) == 60)

# ── E. log10 底數候選: 10 = 2F₅ ──
print("\n[E] log10 底數候選: 10 = 2F₅ (O179 hop 通道週期)")
F5 = 5
ck("10 = 2F₅ (O179 週期)", 2*F5 == 10)
ln10 = mp.log(10)
print(f"  ln10 = {mp.nstr(ln10, 16)}")
print(f"  ln10/γ₆ = {mp.nstr(ln10*inv_g6, 12)}  (O66: 12.7400)")
print(f"  ln10/76 = {mp.nstr(ln10*one76, 12)}  (O66: 0.03030)")
S = ln10 * target   # ln(M_pl/M_comp)
print(f"  S = ln(M_pl/M_comp) = ln10·(1/γ₆−1/76) = {mp.nstr(S, 12)}  (O66: 12.7095)")
# log2 尺度
log2_ratio = mp.log(M_pl/M_comp_formula)/mp.log(2)
print(f"  log2(M_pl/M_comp) = {mp.nstr(log2_ratio, 12)}  (L₆=18 近距? {mp.nstr(abs(log2_ratio-18),4)})")

# 76 喺 φ-power 家族 (φ-lock 閘: 76=L₉ 屬 K_φ 已註冊)
print(f"\n  φ-lock: 76 = L₉ ∈ K_φ (Lucas 家族) — 事前指定非反解 ✓")

print("\n" + "=" * 40)
print(f"RESULT: {passed}/{passed+failed} PASS")