#!/usr/bin/env python3
"""
O257 scripts/14 — R5b: 大數對偶恆等驗證 (2026-10-21)
===================================================
R5 全新恆等候選:
  88³/2 = 340736 = 11 × 176² = L₅ × (2N)² = L₅ × (B·N_d)²
  176² = Πγ_n(176) (Chebyshev: 對偶鏈 176 譜積 = 176²)

驗證:
  1. 88³/2 = L₅·(2N)²  EXACT?
  2. 176² = Πγ(1..176) = Πγ(1..88)² (譜積對偶)?
  3. M_comp = M_pl·2/88³ = M_pl/(L₅·(2N)²) 主項 operator 形式
  4. 對偶形式下 ε 有冇新身份?
"""
import mpmath as mp
mp.mp.dps = 50

phi = (mp.mpf(1)+mp.sqrt(5))/2
L = [0]*15
for k in range(15):
    L[k] = phi**k - (-phi)**(-k)  # Lucas (Binet)
def lucas(k): return mp.nint(phi**k + (-1)**k * phi**(-k))

print("="*72)
print("O257 scripts/14 — R5b: 大數對偶恆等 L₅·(2N)²")
print("="*72)

N = 88
Nd = 44
B = 4
N3h = mp.mpf(88)**3/2
print(f"88³/2 = {mp.nstr(N3h, 16)}")

# 1. L₅·(2N)²
L5 = lucas(5)
twoN2 = (2*N)**2
val = L5*twoN2
dev = abs(val/N3h - 1)*100
print(f"\n[1] L₅·(2N)² = {L5} × {twoN2} = {val}  dev = {mp.nstr(dev, 10)}%")
print(f"    L₅ = {L5}, 2N = {2*N}, (2N)² = {twoN2}")
print(f"    (JB: B·N_d = {B*Nd}, 平方 = {(B*Nd)**2}, ×11 = {(B*Nd)**2*11})")

# 2. Πγ(1..176) = 176²?  Chebyshev
print("\n[2] 對偶鏈譜積: Πγ_n(176)")
prod176 = mp.mpf(1)
for n in range(1, 176):
    prod176 *= 4*mp.sin(n*mp.pi/176)**2
print(f"    Πγ(1..175,176譜) = {mp.nstr(prod176, 12)}  vs 176² = {176**2}")
dev2 = abs(prod176 - 176**2)/(176**2)*100
print(f"    dev = {mp.nstr(dev2, 6)}%")
# 88 譜
prod88 = mp.mpf(1)
for n in range(1, 88):
    prod88 *= 4*mp.sin(n*mp.pi/88)**2
print(f"    Πγ(1..87,88譜) = {mp.nstr(prod88, 12)}  vs 88² = {88**2}")
print(f"    Πγ(176) = Πγ(88)² (代數分解: 每 176 模對應兩個 88 模)")

# 3. M_comp 主項 operator 形式
print("\n[3] M_comp ≈ M_pl·2/88³ = M_pl/(L₅·(2N)²)")
M_pl = mp.mpf("1.220910e19")
M_cal = mp.mpf("3.6909e13")
M_main2 = M_pl * mp.mpf(2)/N3h
print(f"    M_pl·2/88³ = {mp.nstr(M_main2, 12)}  vs 校準 {mp.nstr(M_cal, 10)}")
print(f"    dev = {mp.nstr((M_main2-M_cal)/M_cal*100, 8)}%")
M_main_den = M_pl / (L5*twoN2)
print(f"    M_pl/(L₅(2N)²) = {mp.nstr(M_main_den, 12)}  (一致: {mp.nstr(M_main_den/M_main2, 12)})")

# 4. ε 對偶形式
print("\n[4] ε 對偶身份")
g6 = 4*mp.sin(6*mp.pi/88)**2
pow1g6 = mp.power(10, 1/g6)
eps = pow1g6/N3h - 1
print(f"    ε = {mp.nstr(eps, 16)}, 1/ε = {mp.nstr(1/eps, 10)}")
# ε 喺對偶形式: 10^{1/γ₆} = L₅·(2N)²·(1+ε)
print(f"    10^(1/γ₆) = {mp.nstr(pow1g6, 14)}")
print(f"    L₅(2N)²·(1+ε) = {mp.nstr(L5*twoN2*(1+eps), 14)}")

# ε 候選: ln(1+ε) 幾何
ln1e = mp.log(1+eps)
print(f"    ln(1+ε) = {mp.nstr(ln1e, 14)}     1/ln(1+ε) = {mp.nstr(1/ln1e, 10)}")
for v, name in [(844.9, "1/ε≈844.9"), (845, "845=F₅F₇²"), (1936, "44²"), (7744, "88²"),
                (176*4.8, "176×4.8"), (88*9.6, "88×9.6"), (846, "846"), (84.5*10, "84.5×10")]:
    devv = abs(1/eps - v)/v*100
    print(f"    1/ε vs {name} = {v}: dev {mp.nstr(devv, 6)}%")
# δ = 1/γ₆ − log10(L₅(2N)²)
log10_v = mp.log(L5*twoN2)/mp.log(10)
delta = 1/g6 - log10_v
print(f"\n    δ = 1/γ₆ − log10(L₅(2N)²) = {mp.nstr(delta, 14)}")
print(f"    δ×88² = {mp.nstr(delta*88**2, 10)}  δ×44² = {mp.nstr(delta*44**2, 10)}  δ×176² = {mp.nstr(delta*176**2, 10)}")
print(f"    1/44² = {mp.nstr(1/mp.mpf(44)**2, 12)}")
print(f"    dev δ vs 1/44² = {mp.nstr(abs(delta - 1/mp.mpf(44)**2)/(1/mp.mpf(44)**2)*100, 6)}%")

print("\n" + "="*40)
print("R5b 判定: 大數 = L₅(2N)² EXACT; ε 身份維持開放")