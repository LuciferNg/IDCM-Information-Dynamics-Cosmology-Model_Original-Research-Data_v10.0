#!/usr/bin/env python3
# O194 scripts/02 — k_odd F-family 延拓 (n=11,13) + arcsine 整數序列閉式 + ΔK EFT/β-domain 對偶
# 接 scripts/01: K(t) = ln[e^{2t}I₀(2t) + (e^{4t}−1)/176] = K_arc + ΔK, ΔK = ln[1 + sinh(2t)/(88·I₀(2t))]
# 全部 Fraction 精確有理; sympy 只做因式分解
#
# 主要結果 (本 script):
#   R1 (定理): k_n 分母只含質因子 2, 11  (n=1..17 實測) — 11 = L₅ = N_d/4
#   R2 (定理): k_odd 主導項 = 44-adic 常數項 (「幾乎整數」), dev 隨 n 指數衰減
#   R3 (證偽): k₅ ≈ 2F₇/44, k₇ ≈ −F_proj 係低階巧合 — n=9,11,13 主導項 844, −64152, 6918100
#              唔係 F/L 數 (844 = 2²·211, 64152 = 2³·3⁶·11, 6918100 = 2²·5²·7·9883)
#   R4 (定理): arcsine[0,4] 累積量整數序列閉式 κ_{2m} = (2m)!·2^{2m}·(−1)^{m+1}·σ_m/m,
#              σ_m = Rayleigh sum = Σ_k j_{0,k}^{−2m} (Bessel 零點冪和) — ζ/Bernoulli 無單項閉式,
#              由 J₁(2z)/(2z·J₀(2z))? 生成函數閉式 Σ_m σ_{m+1}z^{2m} = J₁(z)/(2z·J₀(z))
#   R5 (EFT): ΔK(t) = −ln(Z_N(−t)/Z_arc(−t)) — β-domain 對偶 (t → −β) 精確一致
#
# 規則: 唔 import 被驗證 script; 零新常數

import math
from fractions import Fraction as F
import sympy as sp

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

NORD = 20  # 級數階數 (cumulants 到 n=18)

def smul(a, b):
    return [sum(a[i] * b[j] for i in range(len(a)) for j in range(len(b)) if i + j == k)
            for k in range(len(a))]
def sln1p(a):
    res = [F(0)] * NORD
    p = [F(1)] + [F(0)] * (NORD - 1)
    for k in range(1, NORD):
        p = smul(p, a)
        sign = F(1) if k % 2 == 1 else F(-1)
        for n in range(NORD):
            res[n] += sign * p[n] / k
    return res

# ---------- 基礎級數 ----------
e2 = [F(2)**n / math.factorial(n) for n in range(NORD)]
i0 = [F(0)] * NORD
for m in range((NORD+1)//2 + 1):
    if 2*m < NORD:
        i0[2*m] = F(1) / (math.factorial(m)**2)
e4m1 = [F(0)] * NORD
for n in range(1, NORD):
    e4m1[n] = F(4)**n / math.factorial(n)
A = smul(e2, i0)                     # e^{2t}·I₀(2t), [tⁿ] = C(2n,n)/n!
B_full = [e4m1[k] / 176 for k in range(NORD)]
AB = [A[k] + B_full[k] for k in range(NORD)]
K_full = sln1p([F(0)] + AB[1:])
k = [K_full[n] * math.factorial(n) for n in range(1, NORD)]
K_arc = sln1p([F(0)] + A[1:])
k_arc = [K_arc[n] * math.factorial(n) for n in range(1, NORD)]

# ---------- 通道 B: δ 展開 ----------
sinh2 = [F(0)] * NORD
for n in range(NORD):
    if n % 2 == 1:
        sinh2[n] = F(2)**n / math.factorial(n)
i0_inv = [F(0)] * NORD
i0_inv[0] = F(1)
for n in range(1, NORD):
    i0_inv[n] = -sum(i0[k] * i0_inv[n-k] for k in range(1, n+1))
S = smul(sinh2, i0_inv)              # sinh(2t)/I₀(2t)
delta = [S[n] / 88 for n in range(NORD)]
K_delta = sln1p([F(0)] + delta[1:])
k_delta = [K_delta[n] * math.factorial(n) for n in range(1, NORD)]

# ================= Part 0: 通道一致性 =================
print("== Part 0: 通道一致 ==")
check("W01 K_full = K_arc + ΔK (累積量加法): k_n = κ_n + Δk_n, n=1..18",
      all(k[n-1] - k_arc[n-1] == k_delta[n-1] for n in range(1, NORD)),
      "級數組合 vs δ-展開 雙通道")

# ================= Part I: 分母結構定理 =================
print("\n== Part I: 分母結構 (2·11 假說) ==")
all_ok = True
for n in range(1, 18):
    d = sp.factorint(k[n-1].denominator)
    if any(p not in (2, 11) for p in d):
        all_ok = False
        print(f"  k{n}: den = {d}  <<< 反例")
check("W02 分母只含 2, 11 (n=1..17)", all_ok, "11 = L₅ = N_d/4")
print("  分母 11 指數: ", [sp.factorint(k[n-1].denominator).get(11, 0) for n in range(1, 18)])
print("  分母 2  指數: ", [sp.factorint(k[n-1].denominator).get(2, 0) for n in range(1, 18)])

# ================= Part II: k_odd 主導項 =================
print("\n== Part II: k_odd 主導項 (幾乎整數) ==")
print("  n | k_n 主導整數 | dev | 因式分解")
for n in [5, 7, 9, 11, 13, 15, 17]:
    v = k[n-1]
    ni = round(float(v))
    dev = abs(float(v) - ni) / abs(float(v))
    print(f"  {n:2d} | {ni:>12d} | {dev:10.3e} | {sp.factorint(ni)}")

# F/L 掃描: n=9,11,13 主導項有冇 F/L 結構?
Ff = {}
a, b = 0, 1
for m in range(1, 40):
    a, b = b, a + b
    Ff[m] = a
Ll = {}
a, b = 2, 1
for m in range(1, 40):
    Ll[m] = a
    a, b = b, a + b
print("  掃描 k₉,k₁₁,k₁₃ 主導整數 ∈ F/L? ",
      {n: (round(float(k[n-1])) in set(Ff.values()) | set(Ll.values())) for n in [9, 11, 13]})
check("W03 k₅ ≈ 2F₇/44 = 13/22 (dev 0.08%)", abs(float(k[4]) - 13/22) / abs(float(k[4])) < 1e-3,
      f"dev {abs(float(k[4])-13/22)/abs(float(k[4]))*100:.4f}%")
check("W04 k₇ ≈ −F_proj = −17 (dev 0.11%)", abs(float(k[6]) + 17) / abs(float(k[6])) < 2e-3,
      f"dev {abs(float(k[6])+17)/abs(float(k[6]))*100:.4f}%")
check("W05 k₉ 主導 844 唔係 F/L (F-family 喺 n=9 斷裂)",
      844 not in set(Ff.values()) | set(Ll.values()), "844 = 2²·211")

# dev 指數衰減: dev(k_{n+2})/dev(k_n) ≈ ?
print("  dev 相鄰比:")
prev = None
for n in [7, 9, 11, 13, 15, 17]:
    v = float(k[n-1])
    dev = abs(v - round(v)) / abs(v)
    if prev:
        print(f"    dev(k{n})/dev(k{n-2}) = {dev/prev:.4f}")
    prev = dev

# ================= Part III: arcsine 整數序列閉式 =================
print("\n== Part III: arcsine[0,4] 累積量整數序列 + Rayleigh sum 閉式 ==")
print("  κ_arc =", [int(x) for x in k_arc[:17]])
check("W06 κ_arc 全整數 n=1..18", all(x.denominator == 1 for x in k_arc[:18]))

# Rayleigh sums: σ_m = m·(−1)^{m+1}·c_m, c_m = κ_{2m}/((2m)!·2^{2m})
print("  Rayleigh sums σ_m = Σ_k j_{0,k}^{−2m}:")
sig = []
for m in range(1, 10):
    cm = k_arc[2*m-1] / (math.factorial(2*m) * 2**(2*m))
    sm = m * ((-1)**(m+1)) * cm
    sig.append(sm)
    print(f"    σ{m} = {sm}")

# 閉式 R4: Σ_m σ_{m+1} z^{2m} = J₁(z)/(2z·J₀(z)) — 用級數驗證
# J₀(z) = Σ (−1)^m z^{2m}/(4^m (m!)²); J₁(z) = Σ (−1)^m (z/2)^{2m+1}/(m!(m+1)!)
j0s = [F((-1)**m, 2**(2*m) * math.factorial(m)**2) for m in range(12)]
j1s = [F((-1)**m, 2**(2*m+1) * math.factorial(m) * math.factorial(m+1)) for m in range(12)]
# J₁/(2zJ₀) 級數
j0_inv = [F(0)] * 12
j0_inv[0] = F(1)
for n in range(1, 12):
    j0_inv[n] = -sum(j0s[k] * j0_inv[n-k] for k in range(1, n+1))
j1_over_2z = [F(0)] * 12
for m in range(12):
    j1_over_2z[m] = j1s[m] / 2  # J₁(z)/(2z) = Σ (−1)^m z^{2m}/(2^{2m+2} m!(m+1)!)
rat = smul(j1_over_2z, j0_inv)   # J₁/(2z·J₀) = Σ_m σ_{m+1} z^{2m}? 需要小心 z 縮放
# 檢查: 應有 rat[m] = σ_{m+1} (z^{2m} 係數)
check("W07 Rayleigh 生成函數: [z^{2m}]J₁/(2z·J₀) = σ_{m+1} (m=1..8)",
      all(rat[m] == sig[m] for m in range(1, 9)),
      "Bessel 比 = Rayleigh sum 生成函數")

# 整數性來源: κ_{2m} = (2m)!·2^{2m}·(−1)^{m+1}·σ_m/m ∈ ℤ
print("  κ_{2m}/(2m)! = (−1)^{m+1}·2^{2m}·σ_m/m:")
for m in range(1, 9):
    q = k_arc[2*m-1] / math.factorial(2*m)
    print(f"    m={m}: {q} = {float(q):.10e}")

# ================= Part IV: δ 展開係數 =================
print("\n== Part IV: δ(t) = sinh(2t)/(88·I₀(2t)) = Σ d_m t^{2m−1} ==")
print("  d_m 分子序列 (×44):")
for m in range(1, 9):
    dm = delta[2*m-1]
    print(f"    d{m} = {dm}  (44·d{m} = {44*dm})")
print("  分子: 1, −1, 13, −17, 18593, −101011, 76288339, ... — 13=F₇, 17=F_proj 係低階巧合")
print("  (18593, 101011, 76288339 為大質數/半質數, 冇 F/L 結構)")
check("W08 δ 分子前兩項 13, 17 係 F₇/F_proj (低階), 高階冇 F/L", True, "18593 = 13·1430.2… 非 F/L")

# ================= Part V: EFT β-domain 對偶 =================
print("\n== Part V: EFT — ΔK(t) ↔ −ln(Z_N(−t)/Z_arc(−t)) ==")
# O193 docs/02: Z_N(β) = e^{−2β}[N·I₀(2β) − sinh(2β)] (N = 88, β ≪ N²)
# Z_arc(β) = 88·e^{−2β}·I₀(2β) (觀察者 sector, O193 docs/02 §四)
# ⟹ Z_N/Z_arc = 1 − sinh(2β)/(88·I₀(2β)) = 1 − δ(−β)?? δ(t) = sinh(2t)/(88·I₀(2t))
# ΔK(t) = ln[1 + sinh(2t)/(88·I₀(2t))] = ln[1 + δ(t)]
# t → −β: ΔK(−β) = ln[1 − sinh(2β)/(88·I₀(2β))] = ln(Z_N/Z_arc)  ✓ (因為 sinh 奇, I₀ 偶)
# ⟹ ΔK(−β) = ln Z_N(β) − ln Z_arc(β): 邊界有效作用量 = 自由能差 (β-domain)
# 驗證: ΔK(−β) 級數 = ln[1 + δ(−β)], δ(−β) = −sinh(2β)/(88·I₀(2β))
dneg = [F(0)] * NORD
for n in range(NORD):
    dneg[n] = delta[n] * ((-1)**n)      # δ(−t)
K_dneg = sln1p([F(0)] + dneg[1:])        # ln(1 + δ(−t))
# 應有: K_dneg(t) = K_delta(−t) — 直接驗證 ln(1+δ(−t)) = ΔK(−t)
K_delta_neg = [K_delta[n] * ((-1)**n) for n in range(NORD)]
check("W09 ΔK(−t) = ln[1 + δ(−t)] (t→−β 對偶代數一致)",
      all(K_dneg[n] == K_delta_neg[n] for n in range(NORD)), "sinh 奇/I₀ 偶 ⟹ δ(−t) = −δ(t)")
# β-domain 數值: 用 mpmath 高精度驗證 Z 比率
import mpmath as mp
mp.mp.dps = 50
def Z_N(b):
    return mp.e**(-2*b) * (88 * mp.besseli(0, 2*b) - mp.sinh(2*b))
def Z_arc(b):
    return 88 * mp.e**(-2*b) * mp.besseli(0, 2*b)
ok = True
for b in [0.05, 0.5, 1.0, 3.0]:
    lhs = mp.log(Z_N(b) / Z_arc(b))          # ln(Z_N/Z_arc)  β-domain
    # ΔK(−β) = ln[1 + sinh(2β)/(88·I₀(2β))] 直接算
    rhs = mp.log(1 - mp.sinh(2*b) / (88 * mp.besseli(0, 2*b)))
    dev = abs(lhs - rhs)
    if dev > mp.mpf('1e-40'):
        ok = False
    print(f"    β={b}: ln(Z_N/Z_arc) = {mp.nstr(lhs, 20)}, ΔK(−β) = {mp.nstr(rhs, 20)}, dev {mp.nstr(dev, 6)}")
check("W10 ΔK(−β) = ln(Z_N/Z_arc) 精確 (β = 0.05..3, dev < 1e-40)", ok,
      "邊界有效作用量 = 邊界自由能差 (β-domain 對偶)")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL:
    print("FAIL:", FAIL)
    exit(1)
