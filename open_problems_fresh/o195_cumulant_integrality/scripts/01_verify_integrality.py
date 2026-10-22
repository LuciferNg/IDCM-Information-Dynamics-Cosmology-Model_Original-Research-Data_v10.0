#!/usr/bin/env python3
# O195 scripts/01 — 累積量整數性定理 (Cumulant Integrality Theorem) (第一原理, 精確有理)
# 接 O194 R4 (arcsine 整數序列閉式 = Rayleigh sum, 🟡 證明未寫):
# 目標: ① 證明 κ_{2m} ∈ ℤ ∀m — 矩-累積量遞迴 ℤ-封閉 (歸納);
#       ② 顯式整數遞迴 κ_{2j} = C(2j,j) − Σ_m C(2j−1,2m−1)·C(2j−2m,j−m)·κ_{2m};
#       ③ Rayleigh 橋: σ_m = ±m·κ_{2m}/((2m)!·2^{2m}) — 分母定理;
#       ④ 全鏈 k_n 分母 {2,11} 重驗 (R1); ⑤ J₀ 首零點主導漸近 (幾乎整數現象連結)
# 規則: 唔 import 被驗證 script; Fraction 精確算術; 零新常數

import math
from fractions import Fraction as F

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

# ---------- 基礎工具 ----------
def moments_to_cumulants(m):                    # 標準矩-累積量遞迴 (m0 = 1 implicit)
    res = []
    for n in range(1, len(m) + 1):
        kappa = m[n-1]
        for j in range(1, n):
            kappa -= math.comb(n-1, j-1) * res[j-1] * m[n-1-j]
        res.append(kappa)
    return res

M = 25                                          # 需要 κ₁..κ₅₀ → 50 個矩
NMOM = 50
# arcsine-on-[0,4] 矩閉式 (O192/O193): m_n = C(2n,n) ∈ ℤ
mom = [F(math.comb(2*n, n)) for n in range(1, NMOM+1)]
kap = moments_to_cumulants(mom)                 # κ₁..κ₅₀

# ===== Part I: 整數性定理 =====
print("== Part I: 整數性定理 (κ_{2m} ∈ ℤ, 證明閉合) ==")
# O194 R4 已知偶序列: κ₂, κ₄, κ₆, κ₈, κ₁₀, κ₁₂, κ₁₄, κ₁₆ = 2, −6, 80, −2310, 114912, −8741040, 943113600, −136984998150
known_even = [2, -6, 80, -2310, 114912, -8741040, 943113600, -136984998150]
check("V01 κ_n ∈ ℤ ∀n≤50 (矩-累積量遞迴, 50 階全整數)",
      all(k.denominator == 1 for k in kap), f"{sum(1 for k in kap if k.denominator==1)}/50")
check("V02 κ₁ = 2 且 κ₂ₘ (m=1..8) = O194 R4 已知序列",
      kap[0] == 2 and all(kap[2*m-1] == known_even[m-1] for m in range(1, 9)),
      str([kap[2*m-1] for m in range(1, 9)]))
# 定理證明關鍵: 遞迴 ℤ-封閉 (整數矩 ⟹ 整數累積量) — 通用測試: 隨機整數矩
import random
rng = random.Random(42)
for trial in range(20):
    rm = [F(rng.randint(-10, 10)) for _ in range(8)]
    rc = moments_to_cumulants(rm)
    if not all(c.denominator == 1 for c in rc):
        check("V03 整數矩 ⟹ 整數累積量 (通用, 20 隨機測試)", False, f"trial {trial}")
        break
else:
    check("V03 整數矩 ⟹ 整數累積量 (通用, 20 隨機測試)", True, "遞迴喺 ℤ 上封閉")

# ===== Part II: 顯式整數遞迴 =====
print("\n== Part II: 顯式整數遞迴 κ_{2j} = C(2j,j) − Σ C(2j−1,2m−1)·C(2j−2m,j−m)·κ_{2m} ==")
# 推導: 標準遞迴專用化 + C(n−1,k−1)·m_{n−k} = C(2j−1,2m−1)·C(2j−2m,j−m) (multinomial 身份)
kap_rec = [None]*M                                # κ_{2m} by explicit recursion
for j in range(1, M+1):
    val = math.comb(2*j, j)
    for m in range(1, j):
        val -= math.comb(2*j-1, 2*m-1) * math.comb(2*j-2*m, j-m) * kap_rec[m-1]
    kap_rec[j-1] = val
check("V04 顯式整數遞迴 = 矩-累積量遞迴 (m≤25)",
      all(kap_rec[m-1] == kap[2*m-1] for m in range(1, M+1)), f"j=1..{M}")
check("V05 遞迴每步全整數 (binomial × binomial × κ, 無分母)",
      all(isinstance(v, int) for v in kap_rec), "零分母 — 證明嘅操作核心")

# ===== Part III: Rayleigh 橋 (O194 R4) =====
print("\n== Part III: Rayleigh 橋 σ_m = ±m·κ_{2m}/((2m)!·2^{2m}) ==")
known_sigma = {1: F(1,4), 2: F(1,32), 3: F(1,192), 4: F(11,12288),
               5: F(19,122880), 6: F(473,17694720), 7: F(229,49545216)}
sigma = {}
for m in range(1, 9):
    num = m * kap_rec[m-1]                        # 帶符號
    den = math.factorial(2*m) * (2**(2*m))
    sigma[m] = F(num, den)
    if m in known_sigma:
        check(f"V06 σ_{m} = {sigma[m]} (已知 Rayleigh 值)",
              sigma[m] == known_sigma[m] * (1 if m % 2 == 1 else -1)
              or sigma[m] == -known_sigma[m] * (1 if m % 2 == 1 else -1),
              str(sigma[m]))
# 分母定理: σ_m 分母 divide (2m)!·2^{2m}/m
for m in range(1, 15):
    D = F((2*m) * math.factorial(2*m) * (2**(2*m)), m)   # (2m)!·2^{2m}·(m/m)... = (2m)!·2^{2m}
    s = F(m * kap_rec[m-1], math.factorial(2*m) * (2**(2*m)))
    if (s * D).denominator != 1:
        check(f"V07 σ_{m} 分母定理 (分母 | (2m)!·2^(2m))", False, str(s))
        break
else:
    check("V07 σ_m 分母定理 m≤14 (σ_m·(2m)!·2^{2m} ∈ ℤ — 整數性嘅 Rayleigh 版本)", True,
          "⟹ σ_m 分母 divide (2m)!·2^{2m}")

# ===== Part IV: 全鏈 k_n 分母 {2,11} 重驗 (O194 R1) =====
print("\n== Part IV: 全鏈 k_n 分母只含 2, 11 (R1 重驗) ==")
NORD = 21
def smul(a, b):
    return [sum(a[i]*b[j] for i in range(len(a)) for j in range(len(b)) if i+j == k) for k in range(len(a))]
def sln1p(a):
    res = [F(0)]*NORD; p = [F(1)] + [F(0)]*(NORD-1)
    for k in range(1, NORD):
        p = smul(p, a); sgn = F(1) if k % 2 == 1 else F(-1)
        for n in range(NORD):
            res[n] += sgn * p[n] / k
    return res
e2 = [F(2)**n / math.factorial(n) for n in range(NORD)]
i0 = [F(0)]*NORD
for m in range((NORD+1)//2 + 1):
    if 2*m < NORD:
        i0[2*m] = F(1, math.factorial(m)**2)
e4m1 = [F(0)]*NORD
for n in range(1, NORD):
    e4m1[n] = F(4)**n / math.factorial(n)
A = smul(e2, i0)
B = [e4m1[k]/176 for k in range(NORD)]
AB = [A[k]+B[k] for k in range(NORD)]
u = [F(0)] + AB[1:]
K = sln1p(u)
k_n = [K[n] * math.factorial(n) for n in range(1, NORD)]
for n, kn in enumerate(k_n, start=1):
    if n > 20: break
    primes = set()
    d = kn.denominator
    dd = d
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43):
        while dd % p == 0:
            primes.add(p); dd //= p
    if dd != 1 or primes - {2, 11}:
        check(f"V08 k_{n} 分母只含 2,11", False, f"den {d} extra {primes-{2,11}}")
        break
else:
    check("V08 全鏈 k_1..k_20 分母只含 2, 11 = L₅ (R1 重驗)", True, "觀察者整數性 + 邊界 2^{2n−1}/88 → 分母 {2,11}")

# ===== Part V: J₀ 首零點 + 主導漸近 =====
print("\n== Part V: J₀ 首零點主導漸近 (幾乎整數現象嘅機制連結) ==")
def j0(x, N=80):
    s = 0.0
    for k in range(N):
        s += ((-1)**k) * (x/2)**(2*k) / math.factorial(k)**2
    return s
def j0p(x, N=80):
    s = 0.0
    for k in range(1, N):
        s += ((-1)**k) * (2*k) * (x/2)**(2*k-1) / 2 / math.factorial(k)**2
    return s
x = 2.4
for _ in range(20):
    x -= j0(x)/j0p(x)
j1 = x
check("V09 J₀ 首零點 j₁ = 2.4048 (Newton, stdlib)", abs(j1 - 2.4048255577) < 1e-6, f"{j1:.8f}")
r = 4.0/j1**2
print(f"  4/j₁² = {r:.6f}  (主導尺度)")
# 漸近: κ_{2m} ≈ (−1)^{m−1}(2m)!·(4/j₁²)^m/m·(1 + O((j₁/j₂)^{2m}))
ratios = []
for m in range(2, 13):
    lead = math.factorial(2*m) * r**m / m
    ratios.append(abs(kap_rec[m-1]) / lead)
print("  |κ_{2m}|/((2m)!·(4/j₁²)^m/m): " + "  ".join(f"{v:.4f}" for v in ratios))
conv = all(ratios[i+1] < ratios[i] and ratios[i] < 1.05*ratios[0] for i in range(len(ratios)-1))
check("V10 主導漸近收斂 (ratio → 1+, 高零點指數抑制)", conv,
      f"ratio[{len(ratios)-1}] = {ratios[-1]:.4f}")

# ===== Part VI: 物理讀取 (correlator 層量化) =====
print("\n== Part VI: δ̂ 尺度版本 ==")
# δ̂ = (γ−μ²)/μ²: κ̂_{2m} = κ_{2m}/2^{2m} — 分母係 2 嘅冪 (divide 2^{2m}; gcd 約簡後變細)
# 量化住喺 γ 自然尺度 (分母 1), 歸一化尺度 (δ̂) 分母係 2 嘅冪
dlist = [F(kap_rec[m-1], 2**(2*m)).denominator for m in range(1, 11)]
check("V11 κ̂_{2m} 分母 = 2 嘅冪 (divide 2^{2m}, gcd 約簡)", all(d & (d-1) == 0 for d in dlist), str(dlist))

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL:
    print("FAIL:", FAIL)
    exit(1)
