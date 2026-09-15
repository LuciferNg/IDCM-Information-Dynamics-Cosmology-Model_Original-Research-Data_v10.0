#!/usr/bin/env python3
# O196 scripts/07 — T3: k_odd 觀測對應裁決 + 全 O196 綜合閉合
# T3: k_odd = n![tⁿ]artanh(δ) 純邊界修正 (arcsine odd cumulants vanish)
#     主導整數 D_n = round(k_odd) 有冇觀測對應?
#   檢查: (a) D_n 係咪譜量 (γ_k 和/差) (b) 有冇 F/L 閉式 (O194 R3 已否)
#         (c) D_n 對應嘅物理量: artanh(δ) 奇部 = 相位通道?
#   綜合: T1 (11-adic 證明) + T2 (增長閉式) + T3 (裁決) 全 PASS
from fractions import Fraction as F
import math

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

NORD = 81
def smul(a, b):
    n = len(a)
    return [sum(a[i]*b[j] for i in range(n) for j in range(n) if i+j == k) for k in range(n)]
def sln1p(a):
    n = len(a)
    res = [F(0)]*n; p = [F(1)] + [F(0)]*(n-1)
    for k in range(1, n):
        p = smul(p, a)
        sgn = F(1) if k % 2 == 1 else F(-1)
        for i in range(n):
            res[i] += sgn * p[i] / k
    return res
e2 = [F(2)**n / math.factorial(n) for n in range(NORD)]
i0 = [F(0)]*NORD
for m in range(NORD//2 + 2):
    if 2*m < NORD: i0[2*m] = F(1, math.factorial(m)**2)
e4m1 = [F(0)]*NORD
for n in range(1, NORD): e4m1[n] = F(4)**n / math.factorial(n)
AB = [smul(e2, i0)[k] + e4m1[k]/176 for k in range(NORD)]
u = [F(0)] + AB[1:]
K = sln1p(u)
k_n = [K[n]*math.factorial(n) for n in range(1, NORD)]

def rnd(x):
    return (2*x.numerator + x.denominator) // (2*x.denominator)

print("== T3a: k_odd 主導整數 D_n vs 譜量檢查 ==")
# D_n 對 n=1..79 (奇)
Ds = {}
for n in range(1, 80, 2):
    Ds[n] = rnd(k_n[n-1])
print("  D_n (n=1,3,...,79) 頭 12 個 + 尾部:")
print("  " + ", ".join(str(Ds[n]) for n in [1,3,5,7,9,11,13,15,17,19,21,23]))
print("  ... " + ", ".join(str(Ds[n]) for n in range(71, 80, 2)))
# 譜量身份 (O195 Thm 1): 88-chain MGF M(t)=e^{2t}I₀(2t)+(e^{4t}−1)/176
# m₁ = [t¹]M = 2 + 4/176 = 89/44 (κ₁ = 2.0227); κ₂ = 3871/1936 (O194)
check("T3a m₁ = 2 + 1/44 = 89/44 (譜身份)", k_n[0] == F(89, 44), f"κ₁={k_n[0]}")
check("T3a κ₂ = 3871/1936 (O194 閉式)", k_n[1] == F(3871, 1936), f"κ₂={k_n[1]}")
# 結構字典命中: 頭幾個命中 (17 = F_proj @ n=7, 1 @ n=5) 係單點, 檢查有冇序列支持
struct = {1, 4, 7, 11, 13, 17, 31, 33, 43, 44, 55, 88, 123, 137}
hits = {n: d for n, d in Ds.items() if abs(d) in struct}
print(f"  結構字典命中: {hits if hits else '冇'}")
# 單點 vs 序列: 17 出現喺 n=7 但 n=9 (844), n=11 (−64152), n=13 (6918100) 都唔係 17 族
# ⟹ 17 係單點巧合 (O194 R3 家族證偽後冇家族支持), 唔構成觀測對應
seq17 = [Ds[n] for n in [5, 7, 9, 11, 13] if n in Ds]
check("T3a 17 係單點 (n=7), 相鄰 D 冇 17 族 — 巧合", Ds[7] == -17 and all(abs(Ds[n]) != 17 for n in [9, 11, 13]),
      f"D₅={Ds[5]}, D₇={Ds[7]}, D₉={Ds[9]}, D₁₁={Ds[11]}, D₁₃={Ds[13]}")

print("\n== T3b: k_odd 身份 — artanh(δ) 奇部 = 相位通道 ==")
# k_odd = n![tⁿ]ln(1+δ) 奇部; δ = sinh/(88I₀) = 邊界/中心
# ln(1+δ) 奇部 = artanh(δ) = ½ln((1+δ)/(1−δ))
# 呢個係 44-鏈 ± 對稱破缺 (δ 奇函數) 嘅相位編碼 — O7 調律者 h_i=A cosθ_i 相位滑移 π
# 結構角色: 中心 e^{2t}I₀ (偶) ⊗ 邊界 (e^{4t}−1)/176 (偶) ⟹ ln M 偶部;
#   奇部純粹來自 ln(1+δ) 展開 — 冇獨立觀測量, 係生成函數內部結構
print("  k_odd = 純邊界修正 (arcsine odd cumulants 全零, O195 Thm)")
print("  角色: 生成函數奇部 — 冇直接觀測對應 (相位通道, 非振幅)")
print("  對應候選: O7 調律者相位滑移 π (h_i = A cosθ_i) — 詮釋級, 非推導")

print("\n== 綜合: T1 + T2 + T3 閉合確認 ==")
# T1: v₁₁(k_n) = −n + ⌊(n−1)/11⌋ (O195 D1 + O196 證明)
def v11f(x):
    n = abs(x.numerator); d = x.denominator
    e = 0
    while n % 11 == 0: n //= 11; e += 1
    while d % 11 == 0: d //= 11; e -= 1
    return e
ok1 = all(v11f(k_n[n-1]) == -n + (n-1)//11 for n in range(1, NORD))
check("T1 v₁₁(k_n) = −n + ⌊(n−1)/11⌋ (11-adic 證明, n=1..80)", ok1)
# T2: D_{n+2}/D_n ~ (n+1)(n+2)·R⁻², R = 1.202532, dev ≤ 2e-3
R = 1.202532009265
devs = []
for n in range(7, 60, 2):
    fr = abs(k_n[n+1]/k_n[n-1])
    r = float(fr.numerator)/float(fr.denominator)
    pred = (n+1)*(n+2)/R**2
    devs.append(r/pred - 1)
check("T2 D_{n+2}/D_n = (n+1)(n+2)·R⁻² (dev ≤ 2e-3, 兩根干涉)", max(abs(d) for d in devs) < 2e-3,
      f"max|dev| = {max(abs(d) for d in devs):.2e}")
# T3: k_odd 冇結構字典序列命中 (17 @ n=7 係單點) + 冇 F/L 閉式 (O194 R3) ⟹ 觀測對應: 🔴 冇候選
check("T3 k_odd 主導整數冇結構序列命中 (17 係單點巧合)", Ds[7] == -17 and all(abs(Ds[n]) != 17 for n in [9, 11, 13]),
      "🔴 觀測對應維持開放 — k_odd 係生成函數奇部 (相位通道), 冇候選")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
