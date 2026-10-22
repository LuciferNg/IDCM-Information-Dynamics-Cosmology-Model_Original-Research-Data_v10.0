#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O38/m0-scale — final_independent_check_3945.py
=============================================================
獨立審計 scripts/39-45 所有新推導 (2026-10-18/19 輪)：
  scripts/39 r_d 錨鏈 / 40 拆小鏈 / 41 音階 / 42 影子本體
  scripts/43 beat 判別 / 44 本底頻率 / 45 分間最終
方法: 零依賴重算 (唔 import 任何 O38 script, 唔讀任何 step txt),
      由第一原理 mpmath 50 位重算, 對照 docs/19-26 聲稱值。
注意: docs 值源自 scripts 自身輸出 ⟹ 獨立重算只驗「數學恆等」,
      「聲稱 vs 重算」偏差 > 輸入精度 1e−5 即 FAIL。
用法: /usr/bin/python3 final_independent_check_3945.py
"""
from mpmath import mp, mpf, sqrt, sin, cos, pi, ln, log, log10, nstr
mp.dps = 50

ok = fail = 0
def chk(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name} {info}")
    else:    fail += 1; print(f"  ❌ {name} {info}")

c = mpf("2.99792458e8")
Mpc_m = mpf("3.085677581e22")
r_d = mpf("147.4386")                       # O127 DESI DR2
M0_MeV = mpf("27.900915")
hbar_eVs = mpf("6.582119569e-16")
N38 = mpf("1.80188233461e40")               # 文檔值
phi = (1 + sqrt(5)) / 2
Gyr = mpf("3.15576e16")

print("=" * 72)
print("  O38 獨立審計 scripts/39-45 (零依賴重算, mpmath 50 位)")
print("=" * 72)

# ═══ S39: r_d 錨鏈 ═══
print("\n─── S39 r_d 錨鏈 (docs/20) ───")
R_world = 88 * r_d / pi
print(f"  R_world = 88·r_d/π = {nstr(R_world,8)} Mpc (docs: 4129.9424)")
chk("S39 R_world 值", abs(R_world - mpf("4129.9424")) < mpf("1e-3"))
d = abs(R_world/mpf("4129.94") - 1)
chk("S39 R_world ≈ R_H (dev 5.9e−7)", d < mpf("1e-5"), f"(dev {nstr(d,4)})")

t_site_a = R_world * Mpc_m / (44 * c)
t_site_b = 2 * r_d * Mpc_m / (pi * c)
chk("S39 t_site 兩式等價 (dev 0)", t_site_a == t_site_b)
print(f"  t_site = {nstr(t_site_a/Gyr,7)} Gyr (docs: 0.306138)")
chk("S39 t_site 值", abs(t_site_a/Gyr - mpf("0.306138")) < mpf("1e-5"))

tau_depth = 44 * t_site_a
chk("S39 τ_depth = R_world/c", abs(tau_depth*c/(R_world*Mpc_m) - 1) < mpf("1e-12"))
T_SYNC = 88 * t_site_a
print(f"  τ_depth = {nstr(tau_depth/Gyr,6)} Gyr, T_SYNC = {nstr(T_SYNC/Gyr,6)} Gyr")

Mr = M0_MeV * mpf("1e6") * r_d * Mpc_m / (hbar_eVs * c)
print(f"  M₀·r_d/(ħc) = {nstr(Mr,8)} (docs: 6.4327062e38)")
chk("S39 M₀·r_d/(ħc) 值", abs(Mr/mpf("6.4327062e38") - 1) < mpf("1e-5"))
N38_rd = (88/pi) * Mr
print(f"  (88/π)·M₀·r_d/(ħc) = {nstr(N38_rd,10)} (docs: 1.80188e40)")
chk("S39 N_O38 = (88/π)·M₀·r_d/(ħc)", abs(N38_rd/N38 - 1) < mpf("1e-5"), f"(dev {nstr(abs(N38_rd/N38-1),4)})")

# ═══ S40: 拆小鏈 ═══
print("\n─── S40 拆小鏈 (docs/21) ───")
Mts = M0_MeV * mpf("1e6") * t_site_a / hbar_eVs
print(f"  M₀·t_site/ħ = {nstr(Mts,8)} (docs: 4.0951856e38)")
chk("S40 最小缺口值", abs(Mts/mpf("4.0951856e38") - 1) < mpf("1e-6"))
chk("S40 N_O38 = 44·(M₀·t_site/ħ)", abs(44*Mts/N38 - 1) < mpf("1e-5"))
chk("S40 88/π×π/2 閉合因子", abs((88/pi)*(pi/2)/44 - 1) < mpf("1e-30"))

Nsp = t_site_a / mpf("5.391247e-44")
N_IDCM = mpf("7.884688925e60")
print(f"  t_site/t_Pl = {nstr(Nsp,6)} (docs: 1.79197e59)")
chk("S40 t_site/t_Pl = N_IDCM/44", abs(Nsp*44/N_IDCM - 1) < mpf("1e-6"))
M_Pl = mpf("1.2208901e22")
chk("S40 拆解 (t_site/t_Pl)(M₀/M_Pl)", abs(Nsp*(M0_MeV/M_Pl)/Mts - 1) < mpf("1e-5"))

# ═══ S41: 音階核心恆等式 ═══
print("\n─── S41 音階 (docs/22) ───")
P = mpf(1); P2 = mpf(1); Sg = mpf(0)
for n in range(1, 45):
    gn = 4 * sin(mp.pi*mpf(n)/88)**2
    P *= gn; P2 *= sqrt(gn); Sg += gn
chk("S41 Πγ_n = 176 = 2N (精確)", abs(P - 176) < mpf("1e-25"), f"(值 {nstr(P,8)})")
chk("S41 Π√γ_n = 4√11 (精確)", abs(P2 - 4*sqrt(11)) < mpf("1e-25"))
chk("S41 Σγ_n = 90 (精確)", abs(Sg - 90) < mpf("1e-25"))
inv = 1/sin(pi/88)
chk("S41 1/sin(π/88) ≈ 88/π (dev 2.1e−4)", abs(inv/(88/pi) - 1) < mpf("3e-4"), f"(dev {nstr(abs(inv/(88/pi)-1),5)})")
# 音階量對最小缺口
k176 = log(Mts)/log(176)
chk("S41 176^k 零命中 (log 尾數 0.195)", abs(k176 - mp.floor(k176 + mpf("0.5"))) > mpf("0.1"))
# 結構差距
g_range = mpf(4)/ (4*sin(pi/88)**2)
print(f"  γ 譜跨度 = {nstr(g_range,5)} vs 最小缺口 log₁₀ {nstr(log10(Mts),6)} (差 35 數量級)")

# ═══ S42: 影子本體 ═══
print("\n─── S42 影子本體 (docs/23) ───")
# 質量譜 m_n ∝ √γ_n
g1 = 4*sin(pi/88)**2
chk("S42 γ 譜範圍 [0.0051, 4]", abs(g1 - mpf("0.00509577")) < mpf("1e-5") and True)
chk("S42 M₀/M_Pl 唔喺 γ 譜範圍 (影子比)", (M0_MeV/M_Pl) < g1)
print(f"  M₀ 三單位: {nstr(M0_MeV,6)} MeV = {nstr(M0_MeV/1000,8)} GeV = {nstr(M0_MeV*1000,8)} keV (影子)")

# ═══ S43: beat 判別 — 抽樣獨立重算 (唔 full scan, 驗核心邏輯) ═══
print("\n─── S43 beat 判別 (docs/24, 抽樣核實) ───")
sqrt_g = [sqrt(4*sin(mp.pi*mpf(n)/88)**2) for n in range(1, 45)]
# 驗證兩個聲稱: m_τ/m_μ 對 beat 族 min dev 7.16e−6 — 抽樣找最細
tau_mu = mpf("1776.86")/mpf("105.6583755")
beats = []
for a in range(44):
    for b in range(a+1, 44):
        beats.append(abs(sqrt_g[a]-sqrt_g[b]))
best = mpf("1e9")
for i in range(len(beats)):
    for j in range(len(beats)):
        if i == j: continue
        r = beats[i]/beats[j]
        d = abs(r/tau_mu - 1)
        if d < best: best = d
print(f"  m_τ/m_μ beat√ min dev = {nstr(best,4)} (docs: 7.16e−6)")
chk("S43 beat 族對 τ/μ min dev < 1e−5", best < mpf("1e-5"))
# 密度: 期望命中 vs 命中 (抽樣統計 — 用 scripts/43 結果為準, 此處只驗 min dev)
# 已知閉合 μ/e 公式係駐波比×族因子 (唔係 beat)
mu_e = mpf("105.6583755")/mpf("0.51099895")
chk("S43 μ/e 唔係純 √γ 比", abs(mu_e - sqrt_g[43]/sqrt_g[0]) > mpf("0.5"))

# ═══ S44: 本底頻率 ═══
print("\n─── S44 本底頻率 (docs/25) ───")
w_site = 1/t_site_a
w_ring = 1/tau_depth
w_Pl = 1/mpf("5.391247e-44")
w_M0 = M0_MeV * mpf("1e6") / hbar_eVs
print(f"  ω_site = {nstr(w_site,6)} s⁻¹ (docs: 1.0351e−16)")
chk("S44 ω_site 值", abs(w_site/mpf("1.0351e-16") - 1) < mpf("1e-4"))
chk("S44 ω_ring = ω_site/44", abs(w_ring*44/w_site - 1) < mpf("1e-12"))
print(f"  ω_M0 = {nstr(w_M0,6)} s⁻¹, ω_Pl = {nstr(w_Pl,5)} s⁻¹")
chk("S44 分間 ω_M0/ω_site = 4.095e38", abs(w_M0/w_site/mpf("4.095188e38") - 1) < mpf("1e-5"))
chk("S44 分間 ω_M0/ω_ring = 1.801883e40", abs(w_M0/w_ring/mpf("1.801883e40") - 1) < mpf("1e-5"))
chk("S44 分間 ω_M0/ω_Pl = 2.28529e−21", abs(w_M0/w_Pl/mpf("2.28529e-21") - 1) < mpf("1e-4"))

# ═══ S45: 分間最終 ═══
print("\n─── S45 分間最終 (docs/26) ───")
ln_Mts = ln(Mts)
chk("S45 ln ≈ 89 唔過閘 (dev > 1e−3)", abs(ln_Mts/89 - 1) > mpf("1e-3"), f"(dev {nstr(abs(ln_Mts/89-1),5)})")
log4 = log(Mts)/log(4)
chk("S45 log₄ ≈ 513/8 dev 1.3e−4", abs(log4/mpf("64.125") - 1) < mpf("3e-4"))
# 質量譜頻率分間: ω_n = ω_M0·√γ_n/2 — 44 個全非 10 冪 (抽樣 n=7 最佳 frac)
best7 = None
for n in range(1, 45):
    gn = 4*sin(mp.pi*mpf(n)/88)**2
    r = Mts * sqrt(gn) / 2
    lr = log10(r)
    frac = abs(lr - mp.floor(lr + mpf("0.5")))
    if best7 is None or frac < best7: best7 = frac
print(f"  質量譜頻率分間 best frac = {nstr(best7,4)} (docs: 5.5e−3 @ n=7)")
chk("S45 質量譜頻率分間冇近 10 冪", best7 > mpf("1e-3"))

print(f"\n{'='*72}")
print(f"  獨立審計 scripts/39-45: {ok}/{ok+fail} PASS")
print("=" * 72)
import sys
sys.exit(0 if fail == 0 else 1)