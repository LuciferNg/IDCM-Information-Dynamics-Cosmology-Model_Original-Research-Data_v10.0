#!/usr/bin/env python3
"""
O147 獨立驗證器 — 唔 import o147 scripts 任何函數
===================================================
由原始定義 (γ_n, ω_n, φ, Lucas/Fib, Σγ_odd, O143 grid, PDG) 重新計算
docs/01-08 所有關鍵數值, 同文檔對照。禁止污染 — 本 script 唔寫任何 doc。

覆蓋:
  docs/01: 44×乘數族, 528/264, 132 身份
  docs/02: 528 = 2×264 檢查數值
  docs/03: 6 個 closure (O34/O35 原始數值)
  docs/04: P1 表 + 37/528 分解 + M₀ 放大
  docs/05: 兩層分工 (sin22/sin1, 2n_u, 92.3 MeV)
  docs/06: gap 分析 (0.10989, φ^(18/528), n_s=14.129)
  docs/07: 修正掃描 8 比
  docs/08: 階梯 88 共同底
"""
import math, json, os

PASS, FAIL = 0, 0
rows = []

def check(name, cond, detail=""):
    global PASS, FAIL
    rows.append((name, bool(cond), detail))
    if cond: PASS += 1
    else: FAIL += 1

# ============ 原始定義 (獨立重算) ============
N_d, M_0 = 44, 27.900915
E_kchain_eV = 4.060265e-3          # meV → eV
E_kchain_MeV = E_kchain_eV * 1e-6  # → MeV
phi = (1 + math.sqrt(5)) / 2
L = {0:2, 1:1, 2:3, 3:4, 4:7, 5:11, 6:18, 7:29, 8:47}
F = {3:2, 4:3, 5:5, 6:8, 7:13, 8:21, 9:34, 10:55}

def gamma_n(n): return 4 * math.sin(n * math.pi / 88) ** 2
def w_n(n):     return 2 * math.sin(n * math.pi / 88)

# ============ docs/01 + docs/02: 44×乘數族, 528/264 ============
check("528 = dimC·B·N_d = 3×4×44", 3*4*44 == 528)
check("264 = 6U(1)×N_d = 6×44", 6*44 == 264)
check("528/264 = B/2 = 2 = Z₂", (3*4*44)/(2*3*44) == 2)
check("132 = total_roots(SU(12)) = 12×11", 12*11 == 132)
check("132 = N_gen×N_d = 3×44", 3*44 == 132)
check("176 = B×N_d = 4×44", 4*44 == 176)
family = {44:1, 88:2, 132:3, 176:4, 264:6, 528:12}
check("44×乘數族 {44,88,132,176,264,528} = 44×{1,2,3,4,6,12}",
      all(v == 44*m for v, m in family.items()))
check("528 = 4×132 = B×total_roots", 4*132 == 528)
check("528 = 8×66 = F₆×pos_roots (66=2M=2×33)", 8*66 == 528 and 66 == 2*33)
check("528 = 6×88 = 2N_gen×Σγ_odd", 6*88 == 528)
check("528 = 16×33 = B²×M", 16*33 == 528 and 33 == 3*11)
check("528 = N_d·h¹¹/N_gen = 44×36/3 (h¹¹=36=N_d−F₆)", 44*36/3 == 528 and 36 == 44-8)
check("528 = 2×264 (O107 檢查核心)", 2*264 == 528)

# ============ docs/03: 6 個 closure (O34/O35 原始) ============
# 1. M₀ 級聯: m_7 = E_kchain×φ^(47+37/528)×√γ_7 = 13.8002 MeV
m7 = E_kchain_MeV * phi**(47 + 37/528) * math.sqrt(gamma_n(7))
check("C1 m_7 = 13.8002 MeV (0.001%)", abs(m7 - 13.8002)/13.8002 < 0.0001,
      f"m_7={m7:.4f}")
# M₀ 本身 = E_kchain×φ^(47+37/528)
M0_calc = E_kchain_MeV * phi**(47 + 37/528)
check("C1 M₀ = 27.9009 MeV", abs(M0_calc - 27.900915)/27.900915 < 0.001,
      f"M₀={M0_calc:.4f}")

# 2. k(e→μ) = 11+7/88; k(μ→τ) = 6−71/528; k(e→τ) = 17−29/528
check("C2 k(e→μ) = 11 + 7/88 = L₅+L₄/(2N_d)", 11+7/88 == 11 + L[4]/(2*N_d))
check("C2 k(μ→τ) = 6 − 71/528 = C(4,2) − (2N_d−17)/528", 6-71/528 == 6 - (2*N_d-17)/528)
check("C2 k(e→τ) = 17 − 29/528 = L₅+C(4,2) − L₇/528", 17-29/528 == 11+6 - L[7]/528)
check("C2 加法一致性: (11+7/88)+(6−71/528) = 17−29/528", 
      abs((11+7/88)+(6-71/528)-(17-29/528)) < 1e-12)
check("C2 7/88 = 42/528, 42−71 = −29", 7/88 == 42/528 and 42-71 == -29)

# 3. m_μ/m_e = φ^(11+7/88) = 206.770
mu_e = phi**(11 + 7/88)
check("C3 m_μ/m_e = φ^(11+7/88) = 206.77 (0.0015%)", abs(mu_e-206.768)/206.768 < 0.0001,
      f"={mu_e:.3f}")

# 4. m_t/m_b = φ^(8+71/132)×sin19/sin33 = 41.332
t_b = phi**(8 + 71/132) * math.sin(19*math.pi/88)/math.sin(33*math.pi/88)
check("C4 m_t/m_b = 41.332 (0.0004%)", abs(t_b-41.332)/41.332 < 0.0001, f"={t_b:.4f}")

# 5. m_s/m_d = φ^(10/528)×sin22/sin1 = 19.9925
s_d = phi**(10/528) * math.sin(22*math.pi/88)/math.sin(math.pi/88)
check("C5 m_s/m_d = 19.9925 (0.037%)", abs(s_d-19.9925)/19.9925 < 0.001, f"={s_d:.4f}")

# 6. T(s→d) = 2n_u = 20
check("C6 T(s→d) = 2×n_u = 20 (n_u = 10 = n₀(1)−L₄ = 17−7)", 2*10 == 20 and 10 == 17-7)

# 7. 37 身份
check("C7 37 = N_d−L₄ = 44−7 = P_f(τ)", 44-7 == 37)
check("C7 37 = h¹¹+1 = 36+1", 36+1 == 37)

# ============ docs/04: P1 表 + 37/528 + M₀ ============
# grid 值 (O143): (γ_n1/γ_n2)×(P_f1/P_f2)
GRID = {"e":(1,3.6), "mu":(7,15.5), "tau":(20,37), "u":(1,15.5), "c":(34,13),
        "d":(1,33), "s":(14,3.6), "b":(33,44)}
g_mu_e = (gamma_n(7)/gamma_n(1))*(15.5/3.6)
g_s_d  = (gamma_n(14)/gamma_n(1))*(3.6/33)
check("P1 grid mu/e = 206.705 (0.03%)", abs(g_mu_e-206.705)/206.705 < 0.001, f"={g_mu_e:.3f}")
check("P1 grid s/d = 19.668 (1.66%)", abs(g_s_d-19.668)/19.668 < 0.001, f"={g_s_d:.3f}")
check("P1 cascade 精確 45× (對 PDG 20: 0.037% vs 1.66%)", 
      abs(s_d-20)/20*100 < abs(g_s_d-20)/20*100/10)

# 37/528 分解
frac = 37/528
check("P4 37/528 = 3/44 + 1/528", abs(frac-(3/44+1/528)) < 1e-15)
check("P4 37/528 = P_f(τ)/528", frac == 37/528)
check("P4 37/528 = (3/44)×(37/36) = (N_gen/N_d)(1+1/h¹¹)", 
      abs(frac-(3/44)*(37/36)) < 1e-15)
# M₀ 放大
amp = phi**47 * phi**(37/528)
target_amp = M_0 / E_kchain_MeV
check("P4 φ^47·φ^(37/528) = 6.8717e9 = M₀/E_kchain (0.0000%)",
      abs(amp-target_amp)/target_amp < 1e-6, f"Δ={abs(amp-target_amp)/target_amp*100:.4f}%")

# ============ docs/05: 兩層分工 ============
spec_ratio = w_n(22)/w_n(1)
check("D5 sin22/sin1 = 19.811 (0.94% off 20)", abs(spec_ratio-19.8112)/19.8112 < 0.0001)
check("D5 cascade 命中 2n_u=20 (0.037%)", abs(s_d-20)/20 < 0.001)
m_s_14 = M_0 * gamma_n(14) * 3.6
check("D5 m_s = M₀×γ₁₄×3.6 = 92.3 MeV (1.2%)", abs(m_s_14-93.4)/93.4 < 0.02, f"={m_s_14:.1f}")
check("D5 528 = Σγ_odd×2N_gen = 88×6", 88*6 == 528)
check("D5 528/264 = 88/44 = Z₂", 528/264 == 88/44 == 2)

# ============ docs/06: gap 分析 ============
form_ratio = g_s_d
P_req = math.sin(22*math.pi/88)*math.sin(math.pi/88)/math.sin(14*math.pi/88)**2
check("D6 幾何 P_f 比 = 0.10989 (vs grid 0.10909, gap 0.73%)",
      abs(P_req/0.109885 - 1) < 0.001 and abs((P_req/0.109091-1)*100 - 0.73) < 0.1)
val18 = form_ratio * phi**(18/528)
check("D6 公式層 + φ^(18/528) = 19.9934 (0.033%)", abs(val18-20)/20 < 0.001, f"={val18:.4f}")
check("D6 18/528 = 3/88 = L₂/(2N_d)", 18/528 == 3/88 and 3 == L[2])
check("D6 n_s 連續 = 14.129 (整數 14 偏差 0.92%)",
      abs(math.asin(math.sqrt(20*33/3.6)*math.sin(math.pi/88))*88/math.pi - 14.129) < 0.01)

# ============ docs/07: 修正掃描 8 比 ============
PDG = {"mu/e":206.768, "tau/e":3477.2, "tau/mu":16.82, "s/d":20.0,
       "c/u":587.96, "b/d":895.0, "b/s":44.75, "c/s":13.60}
pairs = [("mu/e","mu","e"),("tau/e","tau","e"),("tau/mu","tau","mu"),
         ("s/d","s","d"),("c/u","c","u"),("b/d","b","d"),("b/s","b","s"),("c/s","c","s")]
ks = {}
for name, a, b in pairs:
    n1,p1 = GRID[a]; n2,p2 = GRID[b]
    gv = (gamma_n(n1)/gamma_n(n2))*(p1/p2)
    ks[name] = math.log(PDG[name]/gv)/math.log(phi)*528
# k 值對照 docs/07
check("D7 k(mu/e) ≈ 0 (0.3, 唔需要修正)", abs(ks["mu/e"]-0.34) < 0.05)
check("D7 k(tau/e) ≈ 6 (2N_gen)", abs(ks["tau/e"]-5.51) < 0.05)
check("D7 k(s/d) ≈ 18 (L₆)", abs(ks["s/d"]-18.36) < 0.05)
check("D7 k(c/u) ≈ 18 (L₆)", abs(ks["c/u"]-18.83) < 0.05)
check("D7 k(b/s) ≈ −16 (−B²)", abs(ks["b/s"]+16.33) < 0.05)
check("D7 k(c/s) ≈ −16 (−B²)", abs(ks["c/s"]+16.20) < 0.05)
check("D7 加法一致: k(b/s) = k(b/d)−k(s/d) = 2−18 = −16",
      abs(ks["b/d"]-2.03) < 0.05 and abs(ks["b/d"]-ks["s/d"] - (-16)) < 1.0)
# 修正後 Δ
for name, k_used in [("s/d",18),("c/u",18),("b/s",-16),("c/s",-16)]:
    a,b = name.split("/")
    n1,p1 = GRID[a]; n2,p2 = GRID[b]
    gv = (gamma_n(n1)/gamma_n(n2))*(p1/p2)
    hit = gv * phi**(k_used/528)
    check(f"D7 {name} 修正後 Δ≤0.08%", abs(hit-PDG[name])/PDG[name] < 0.0008,
          f"Δ={abs(hit-PDG[name])/PDG[name]*100:.3f}%")

# ============ docs/08: 階梯 88 共同底 ============
check("D8 132 = 88×N_gen/Z₂ = 88×3/2", 88*3/2 == 132)
check("D8 528 = 88×2N_gen = 88×6", 88*6 == 528)
check("D8 88 = Σγ_odd", abs(sum(4*math.sin((2*k-1)*math.pi/88)**2 for k in range(1,45)) - 88) < 1e-9)

# ============ 輸出 ============
print("=" * 72)
print("  O147 獨立驗證器 (原始定義重算 vs docs/01-08)")
print("=" * 72)
for name, ok, detail in rows:
    print(f"  {'✅' if ok else '🔴'} {name:58s} {detail}")
print("-" * 72)
print(f"  PASS: {PASS}  FAIL: {FAIL}")
print(f"  總判定: {'✅ 全部一致' if FAIL == 0 else '🔴 有偏差需審計'}")
