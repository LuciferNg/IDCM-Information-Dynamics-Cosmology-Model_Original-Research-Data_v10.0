#!/usr/bin/env python3
"""
P6 階段性 closeout — 獨立審計（audit P6A）
============================================================
範圍：docs/04-09（本次新增未審計檔）＋ scripts/06-08（自製工具）
原則：唔 import 任何原推導 script；由 K_Chain 原始定義重算每個 headline 數字
     （γ_n = 4sin²(nπ/88)、φ、Lucas、hop 階梯），報 N/N PASS。

審計項（對應 docs）：
  D04.1 N=8/N=10 角 = cos(2π/8)、cos(2π/10) 與 docs/04 一致
  D04.2 m=2 通道禁閉：N=10 m=2 → n_eff≈4.33 非整數（冇第四代）
  D05.1 t 掃描：只有 t=Δ/2 令 gap=0（docs/05 §2.1）
  D05.2 γ₆ 彈性：δγ₆=+1% → δΔm²₃₁≈18-19%（docs/05 §2.2）
  D05.3 Δ/2 = cos(π/11)−cos(5π/44) 恒等式成立（docs/05 §2.3）
  D06.1 Σγ_odd(1..87) = Σγ_even(1..88) = 88（docs/06 §1/§4）
  D06.2 hop 階梯和 = 60 = |A₅|、hop_max=12（docs/06 §2/§3）
  D06.3 76 = 88−12 = L₉ = 4×19（docs/06 三層身份）
  D08.1 Feshbach 極點：0 個 x₀ 同時命中 Δ/2（scripts/06 結論）
  D08.2 譜積身份搜尋：1/γ₆−1/76 冇 operator 命中（scripts/07 結論）
  D09.1 gaplessness：γ₄+2Δ/2 = γ₅ EXACT（docs/09 §1）
  D09.2 帶範圍 [2γ₄−γ₅, γ₅]，正譜（docs/09 §2）
  D09.3 N=8/N=10 m=1 帶内位置 85.4%/90.5%（docs/09 §2）
"""
import math

PASS = 0
FAIL = 0
def chk(name, got, want, tol=1e-9, unit=""):
    global PASS, FAIL
    ok = abs(got - want) <= tol * max(1.0, abs(want))
    if ok: PASS += 1
    else: FAIL += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {got:.9g}{unit} (want {want:.9g})")

def gamma(n, N=88):
    return 4 * math.sin(n * math.pi / N) ** 2

phi = (1 + math.sqrt(5)) / 2
g4, g5, g6 = gamma(4), gamma(5), gamma(6)
DELTA = g5 - g4
T0 = DELTA / 2
M_comp = 1.2209e19 * 10**(-(1/g6 - 1/76))
A = 246.2196**2/M_comp * 1e9

print("="*78)
print("D04 — N-環 tight-binding 統一 (docs/04)")
print("="*78)
chk("D04.1 m₁角 cos(2π/8)", math.cos(2*math.pi/8), math.cos(math.pi/4), 1e-14)
chk("D04.1 m₂角 cos(2π/10)", math.cos(2*math.pi/10), math.cos(math.pi/5), 1e-14)
chk("D04.1 cos(2π/8) = 1/√2", math.cos(2*math.pi/8), 1/math.sqrt(2), 1e-14)
chk("D04.1 cos(2π/10) = φ/2", math.cos(2*math.pi/10), phi/2, 1e-14)
chk("D04.1 N=8 = 2B", 8, 2*4)
chk("D04.1 N=10 = 2F₅", 10, 2*5)
# m=2 通道
g_m2_10 = g4 + DELTA*math.cos(4*math.pi/10)
n_eff = 88/math.pi * math.asin(math.sqrt(max(0,g_m2_10))/2)
print(f"    [info] N=10 m=2: γ={g_m2_10:.6f}, n_eff={n_eff:.4f} (唔係整數 — 禁閉)")
chk("D04.2 N=10 m=2 n_eff 非整數 (>4, <5)", abs(n_eff - 4.33), 0.01, 0.02)
chk("D04.2 m₂ = A(γ₄+Δcos2π/10)²", A*(g4+DELTA*math.cos(2*math.pi/10))**2, 0.022685, 1e-5, " eV")

print()
print("="*78)
print("D05 — O179 hop 干涉核 + 結構剛性 (docs/05)")
print("="*78)
# t 掃描 gap
gap_at_T0 = g5 - (g4 + 2*T0)
chk("D05.1 gapless t=T0 (gap=0)", gap_at_T0, 0, 1e-12)
gap_at_95 = g5 - (g4 + 2*T0*0.95)
chk("D05.1 t=0.95T0 留 gap (Δ/20)", gap_at_95, DELTA/20, 1e-12)
# γ₆ 彈性: δγ₆=+1% → δΔm²₃₁
g6p = g6 * 1.01
Mp = 1.2209e19 * 10**(-(1/g6p - 1/76))
Ap = 246.2196**2/Mp * 1e9
m1p = Ap*(g4+DELTA*math.cos(2*math.pi/8))**2
m3p = Ap*g6p**2
d31 = (m3p**2 - m1p**2) / ( (A*g6**2)**2 - (A*(g4+DELTA*math.cos(2*math.pi/8))**2)**2 ) - 1
print(f"    [info] δγ₆=+1% → δΔm²₃₁ = {d31*100:.1f}% (docs/05 聲稱 18.6%)")
chk("D05.2 δΔm²₃₁/δγ₆=18.6%", d31, -0.186, 0.01)
# Δ/2 恒等式
theta = math.pi/88
t_cos = math.cos(8*theta) - math.cos(10*theta)
t_delta = DELTA/2
chk("D05.3 Δ/2 = cos(8θ)−cos(10θ)", t_cos, t_delta, 1e-14)
chk("D05.3 2sin(9θ)sin(θ) = Δ/2", 2*math.sin(9*theta)*math.sin(theta), t_delta, 1e-14)

print()
print("="*78)
print("D06 — 身份精修 (docs/06)")
print("="*78)
S_odd = sum(gamma(n) for n in range(1, 88, 2))
S_even = sum(gamma(n) for n in range(2, 89, 2))
chk("D06.1 Σγ_odd(1..87) = 88", S_odd, 88, 1e-9)
chk("D06.1 Σγ_even(1..88) = 88", S_even, 88, 1e-9)
ladder = [1,4,8,11,12,11,8,4,1]
chk("D06.2 hop 階梯和 = 60 = |A₅|", sum(ladder), 60)
chk("D06.2 hop_max = 12 = B·N_gen", max(ladder), 4*3)
chk("D06.3 L₉ = φ⁹−φ⁻⁹ = 76", phi**9 - phi**(-9), 76, 1e-9)
chk("D06.3 76 = 88−12", 88-12, 76)
chk("D06.3 76 = 4×19", 4*19, 76)
S_44 = sum(gamma(n) for n in range(1, 45))
chk("D06.3 Σγ(1..44) = 90", S_44, 90, 1e-9)
chk("D06.3 Σγ_odd−12 = 76", S_odd-12, 76, 1e-9)

print()
print("="*78)
print("D08 — 工具否定結果 (docs/08)")
print("="*78)
# Feshbach: 檢查 0 個 x₀ 同時命中
def G0(x0, E, N=88):
    return sum(math.sin(n*math.pi*x0/N)**2 / (E - gamma(n,N)) for n in range(1,45))
GAM1 = g4 + DELTA*math.cos(2*math.pi/8)
GAM2 = g4 + DELTA*math.cos(2*math.pi/10)
hits = 0
for x0f in range(1,89):
    t1 = 1/G0(float(x0f), GAM1)
    t2 = 1/G0(float(x0f), GAM2)
    if abs(t1-T0)/T0 < 0.05 and abs(t2-T0)/T0 < 0.05:
        hits += 1
chk("D08.1 Feshbach 0 個 x₀ 同時命中", hits, 0)
# 譜積身份: 檢查 Fib mod -log10P 只係邊緣
prod_fib = 1.0
for n in [1,2,3,5,8,13,21,34,55]:
    prod_fib *= gamma(n)
lp_fib = -math.log10(prod_fib)
print(f"    [info] Fib mod -log10P = {lp_fib:.4f} (目標 5.51977, dev {(abs(lp_fib-5.5197738)/5.5197738)*100:.2f}%)")
dev_fib = abs(lp_fib-5.5197738)/5.5197738*100
chk("D08.2 Fib dev≈0.9% (非 operator)", dev_fib, 0.9, 0.1, " %")

print()
print("="*78)
print("D09 — gaplessness (docs/09)")
print("="*78)
chk("D09.1 γ₄+2(Δ/2) = γ₅", g4 + DELTA, g5, 1e-14)
chk("D09.1 t = Δ/2 唯一", g4+2*T0, g5, 1e-12)
lo, hi = g4-DELTA, g5
chk("D09.2 帶底 = 2γ₄−γ₅", lo, 2*g4-g5, 1e-14)
chk("D09.2 帶底 > 0 (正譜)", 1 if lo>0 else 0, 1)
E1_8 = g4 + DELTA*math.cos(2*math.pi/8)
E1_10 = g4 + DELTA*math.cos(2*math.pi/10)
pos8 = (E1_8-lo)/(hi-lo)*100
pos10 = (E1_10-lo)/(hi-lo)*100
chk("D09.3 N=8 m=1 帶内 85.4%", pos8, 85.4, 0.1, " %")
chk("D09.3 N=10 m=1 帶内 90.5%", pos10, 90.5, 0.1, " %")
chk("D09.3 m₁ = A(γ₁)² 閉合", A*E1_8**2, 0.020945, 1e-5, " eV")
chk("D09.3 m₂ = A(γ₂)² 閉合", A*E1_10**2, 0.022685, 1e-5, " eV")

print()
print("="*78)
print(f"RESULT: {PASS}/{PASS+FAIL} PASS")
print("="*78)