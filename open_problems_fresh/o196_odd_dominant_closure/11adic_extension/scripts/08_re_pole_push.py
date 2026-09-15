#!/usr/bin/env python3
# O200 scripts/08 — 攻堅: Re(r₁) ≈ 1/136 身份 + 極點推離閉式 (dps=200)
# 目標:
#   A) dps=200 鎖定 Re(r₁), 確認 dev vs 1/136 = 1/(2B·F_proj) 係咪真 3.96e-5
#   B) 一階極點推離閉式: 88·I₀(2t) = sinh(2t), 2t = i·j₁ + ε, I₀'=I₁
#      I₀(i·j₁+ε) ≈ ε·I₁(i·j₁) = ε·i·J₁(j₁); sinh(i·j₁+ε) ≈ i·sin(j₁)+ε·cos(j₁)
#      88·ε·i·J₁ = i·sin(j₁) + ε·cos(j₁) ⟹ ε = a+ib:
#      a = sin(j₁)·88J₁/((88J₁)² + c²), c = cos(j₁) ⟹ Re(r₁) = a/2
#   C) 二階/完整解 — Newton 高精度 + 一階閉式 dev 診斷
#   D) Re(r₁) = 1/136 = 1/(2B·F_proj) 結構候選 vs 極點推離值
import mpmath as mp

mp.mp.dps = 200
PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

# ===== A) dps=200 鎖定 Re(r₁) =====
r1 = mp.findroot(lambda t: 88*mp.besseli(0, 2*t) - mp.sinh(2*t), mp.mpc('0.0074','1.2024'), tol=1e-120, maxsteps=200)
R = abs(r1)
Re1, Im1 = r1.real, r1.imag
print(f"r₁ (dps=200): Re = {mp.nstr(Re1, 40)}")
print(f"              Im = {mp.nstr(Im1, 40)}")
print(f"              R  = {mp.nstr(R, 40)}")

# 1/136 候選
c136 = mp.mpf(1)/136
dev136 = abs(Re1 - c136)/abs(Re1)
print(f"\n1/136 = {mp.nstr(c136, 40)}")
print(f"Re(r₁) vs 1/136: dev = {mp.nstr(dev136, 15)}")
# 3.96e-5 確認? (dps=100 時 3.9595e-5)
check("A) Re(r₁) ≈ 1/136 dev 穩定 (dps=200 同 dps=100 一致)", 
      abs(dev136 - mp.mpf('3.9595e-5')) < mp.mpf('1e-7'), 
      f"dev = {mp.nstr(dev136, 12)}")

# ===== B) 一階極點推離閉式 =====
print("\n== B) 一階極點推離閉式 ==")
j1 = mp.besseljzero(0, 1)
J1j = mp.besselj(1, j1)   # J₁(j₁)
sj = mp.sin(j1)
cj = mp.cos(j1)
print(f"j₁ = {mp.nstr(j1, 25)}")
print(f"J₁(j₁) = {mp.nstr(J1j, 25)}, sin(j₁) = {mp.nstr(sj, 20)}, cos(j₁) = {mp.nstr(cj, 20)}")
# I₁(i·j₁) = i·J₁(j₁) 驗證
I1ij = mp.besseli(1, mp.mpc(0, j1))
print(f"I₁(ij₁) = {mp.nstr(I1ij, 20)} (應 = i·J₁(j₁) = {mp.nstr(mp.mpc(0, J1j), 20)})")
check("B) I₁(ij₁) = i·J₁(j₁) (Bessel 恆等)", abs(I1ij - mp.mpc(0, J1j)) < mp.mpf('1e-150'))

# 一階: ε = a + ib
# 88(a+ib)·i·J₁ = i·sin(j₁) + (a+ib)·cos(j₁)
# 88·i·J₁·a − 88·J₁·b = i·sj + a·c + i·b·c
# 實部: −88J₁·b = a·c + sj·? 慢 — 用 mpmath 直接解線性系統
# 方程式: 88·ε·i·J₁(j₁) = i·sj + ε·cj
# ⟹ ε·(88·i·J₁ − cj) = i·sj ⟹ ε = i·sj/(88·i·J₁ − cj)
eps1 = mp.mpc(0, sj) / (88*mp.mpc(0, J1j) - cj)
Re1st = eps1.real/2   # t = ij₁/2 + ε/2
print(f"一階 ε = {mp.nstr(eps1, 25)}")
print(f"一階 Re(r₁) = ε/2 = {mp.nstr(Re1st, 30)}")
print(f"實際 Re(r₁) = {mp.nstr(Re1, 30)}")
dev1 = abs(Re1st - Re1)/abs(Re1)
print(f"一階 dev = {mp.nstr(dev1, 10)} (之前 0.02% 檢查)")

# ===== C) 二階修正 (sinh 展開到 ε², I₀ 展開到 ε²) =====
print("\n== C) 二階修正 ==")
# I₀(i·j₁+ε) = I₀(ij₁) + ε·I₁(ij₁) + ε²·I₂(ij₁)/2!
# I₀(ij₁) = J₀(j₁) = 0; I₁(ij₁) = i·J₁(j₁); I₂(ij₁) = i²·J₂(j₁) = −J₂(j₁)
# sinh(i·j₁+ε) = sinh(ij₁) + ε·cosh(ij₁) + ε²·sinh(ij₁)/2
# sinh(ij₁) = i·sin(j₁); cosh(ij₁) = cos(j₁)
# 88·[ε·i·J₁ − ε²·J₂/2] = i·sj + ε·cj + ε²·i·sj/2
J2j = mp.besselj(2, j1)
print(f"J₂(j₁) = {mp.nstr(J2j, 20)}")
# 多項式: 88·i·J₁·ε − 44·J₂·ε² = i·sj + cj·ε + i·sj/2·ε²
# ⟹ (88·i·J₁ − cj)·ε − (44·J₂ + i·sj/2)·ε² − i·sj = 0
# 牛頓解
eps2 = mp.findroot(lambda e: (88*mp.mpc(0,J1j) - cj)*e - (44*J2j + mp.mpc(0,sj)/2)*e**2 - mp.mpc(0,sj), eps1, tol=1e-150, maxsteps=100)
Re2nd = eps2.real/2
print(f"二階 ε = {mp.nstr(eps2, 25)}")
print(f"二階 Re(r₁) = {mp.nstr(Re2nd, 30)}")
dev2 = abs(Re2nd - Re1)/abs(Re1)
print(f"二階 dev = {mp.nstr(dev2, 10)}")
check("C) 二階極點推離 dev 顯著改善", dev2 < dev1/10, f"一階 {mp.nstr(dev1,5)} → 二階 {mp.nstr(dev2,8)}")

# ===== D) Re(r₁) 身份判定 =====
print("\n== D) Re(r₁) 身份判定 ==")
# 一階閉式本身係咪 = 1/136?
# a = 88J₁·sj/((88J₁)² + cj²) — 用 Bessel 零點恆等: J₁(j₁)² + ... ?
# 有冇 j₁ 嘅恆等令 a/2 = 1/136? 檢查 a 嘅值
a_exact = 88*J1j*sj/((88*J1j)**2 + cj**2)
print(f"一階閉式 a/2 = {mp.nstr(a_exact/2, 30)}")
print(f"1/136        = {mp.nstr(c136, 30)}")
print(f"實際 Re(r₁)  = {mp.nstr(Re1, 30)}")
# 三角形: 一階 0.00735175 < 實際 0.00735323 < 1/136 0.00735294?
print(f"排序: 一階 {mp.nstr(Re1st, 10)} / 1/136 {mp.nstr(c136, 10)} / 實際 {mp.nstr(Re1, 10)} / 二階 {mp.nstr(Re2nd, 10)}")
# 一階 vs 1/136
dev_1st_136 = abs(Re1st - c136)/c136
dev_2nd_136 = abs(Re2nd - c136)/c136
print(f"一階 vs 1/136: dev {mp.nstr(dev_1st_136, 10)}")
print(f"二階 vs 1/136: dev {mp.nstr(dev_2nd_136, 10)}")
print(f"實際 vs 1/136: dev {mp.nstr(dev136, 10)}")
# 判定: 極點推離閉式未達 1/136 精度 — 1/136 係巧合? 定係高階修正?
# 檢查 1/136 係咪有更深來源: 136 = 2B·F_proj = 8·17 — 全註冊
# 但一階/二階都唔係 1/136 ⟹ 1/136 唔似來自極點推離機制
check("D) 一階/二階閉式 vs 1/136: dev 差至少 10× (1/136 唔係推離機制產物)",
      min(dev_1st_136, dev_2nd_136) > 10*dev136,
      f"一階 {mp.nstr(dev_1st_136,5)} / 二階 {mp.nstr(dev_2nd_136,5)} vs 實際 {mp.nstr(dev136,8)}")

# ===== E) 2-adic 自相似檢查 (開放項 5) =====
print("\n== E) κ_{2m} 2-adic 自相似 (v₂(κ_{2m}) = g(2-free(m))?) ==")
from fractions import Fraction as Fr
import math
def v2_int(k):
    e = 0
    while k % 2 == 0: k //= 2; e += 1
    return e
def two_free(m):
    while m % 2 == 0: m //= 2
    return m
M = 60
kap = [0]*(M+1)
for j in range(1, M+1):
    val = math.comb(2*j, j)
    for m in range(1, j):
        val -= math.comb(2*j-1, 2*m-1) * math.comb(2*j-2*m, j-m) * kap[m]
    kap[j] = val
v2s = [v2_int(kap[m]) for m in range(1, M+1)]
gmap = {}
ok_sim2 = True
for m in range(1, M+1):
    fr = two_free(m)
    if fr in gmap and gmap[fr] != v2s[m-1]:
        ok_sim2 = False; break
    gmap[fr] = v2s[m-1]
print(f"  v₂(κ₂ₘ) 序列: {v2s[:40]}")
print(f"  v₂ 自相似 (2-free 決定?): {ok_sim2}")
# v₂ = 0 位?
z2 = [m for m in range(1, M+1) if v2s[m-1] == 0]
print(f"  v₂(κ)=0 位: {z2}")
# v₂(κ₂ₘ) 結構: 睇下 m odd 時
m_odd = [(m, v2s[m-1]) for m in range(1, 41, 2)]
print(f"  m odd → v₂: {[v for _,v in m_odd]}")
check("E) v₂(κ₂ₘ) = g(2-free(m)) 自相似 (2-adic 同款?)", ok_sim2)

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
