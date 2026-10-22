#!/usr/bin/env python3
"""
O154 S06: 獨立審計 (Independent Audit) — 唔 import scripts/01-05, 由第一原理重算
================================================================
審計目標 (Task 1: 驗證過程中的推導和結果):
  A. 鏈譜: γ 和 (90/88/178/2), ω 和, ω_log = 352^(1/176) (mpmath 50 dps)
  B. beat 恆等 946/946 (獨立實現)
  C. LaH10 結構算術: 44 = 4+32+8, 11 = 1+10, 40 = 44−4, 32 = 2·4², 8 = F₆, 12 = 4+8
  D. λ: 88/33 = 8/3; 對比 2.58±0.11 (σ) 與 2.67 (%)
  E. Allen-Dynes: Tc/ω_log for μ* = {0.10, 0.13, 0.16}
  F. Tc 定律線性: 0.2605×Ω_log 表 vs S03 [D]
  G. 間隙比算術: 2×61.0/(k_B×291.4) = 4.86
  H. 盲測算術: YH10 (305/326 ÷ 0.2605), LaD10 (250/√2)
  I. ★ 獨立 Eliashberg 交叉驗證:
     I1: 正常態 Z₀ = 1+λ 數值恆等 (摺疊核 Σλ(n−m)sgn = λ(0))
     I2: Einstein 模 (Ω=96.4 meV, λ=8/3, μ*=0.13) → Tc 文獻範圍 ~0.16-0.25×Ω
     I3: 鏈 α²F 重解 Tc (獨立實現, 比較 S03 的 291.4 K)
"""
import numpy as np
from mpmath import mp, mpf

mp.dps = 50
k88 = np.arange(1, 89)

def p(label, val, target, tol=1e-6, note=""):
    ok = abs(val - target) < tol
    print(f"  [{'✅' if ok else '❌'}] {label}: {val} (目標 {target}) {note}")
    return (label, val, target, ok)

results = []

print("=" * 78)
print("  O154 S06: 獨立審計")
print("=" * 78)

# ---- A. 鏈譜 ----
print("\n[A] 鏈譜重算 (獨立)")
gam = 4.0 * np.sin(k88 * np.pi / 176) ** 2
om = 2.0 * np.sin(k88 * np.pi / 176)
ev, od = k88 % 2 == 0, k88 % 2 == 1
results.append(p("Σγ_even", gam[ev].sum(), 90))
results.append(p("Σγ_odd", gam[od].sum(), 88))
results.append(p("E−O", gam[ev].sum() - gam[od].sum(), 2))
results.append(p("Σγ_total", gam.sum(), 178))
results.append(p("Σω_even", om[ev].sum(), 57.01658986, 1e-6))
results.append(p("Σω_odd", om[od].sum(), 56.02551507, 1e-6))
results.append(p("零點 parity gap (Σω_odd−Σω_even)/2", (om[od].sum()-om[ev].sum())/2, -0.49553739, 1e-6))
wl = float(mpf(352) ** (mpf(1)/mpf(176)))
results.append(p("ω_log = 352^(1/176)", wl, 1.03387728197, 1e-10))
results.append(p("ω_log/ω_max", wl/2.0, 0.51693864, 1e-6))

# ---- B. beat 恆等 ----
print("\n[B] beat 恆等 946/946 (獨立實現, 44-chain 語言: ω_n = 2sin(nπ/88))")
n44 = np.arange(1, 45)
w44 = 2.0 * np.sin(n44 * np.pi / 88)
n = 0
for a in range(1, 45):
    for b in range(a + 1, 45):
        d = b - a
        lhs = abs(w44[a-1] - w44[b-1])
        rhs = 4.0 * np.sin(d * np.pi / 176) * np.cos((a + b) * np.pi / 176)
        n += 1 if abs(lhs - rhs) < 1e-12 else 0
results.append(p("beat 恆等 (O149 定理1, 44-chain)", n, 946))

# ---- C. LaH10 結構算術 ----
print("\n[C] LaH10 結構算術")
results.append(p("44 = 4+32+8", 4+32+8, 44))
results.append(p("11 = 1+10 (f.u.)", 1+10, 11))
results.append(p("40 = 44−4", 44-4, 40))
results.append(p("32 = 2·4²", 2*4**2, 32))
results.append(p("8 = F₆", 8, 8))
results.append(p("12 = 4+8 = B·N_gen", 4+8, 12, 1e-9, "= 4×3"))
results.append(p("{8,32,40} ⊂ {8,16,24,32,40}", {8,32,40} <= {8,16,24,32,40}, True, 0.5))

# ---- D. λ ----
print("\n[D] λ = 8/3 對比")
lam = 88/33
results.append(p("88/33 = 8/3", lam, 8/3))
sig = (lam - 2.58) / 0.11
results.append(p("vs 實驗 2.58±0.11", sig, 0.79, 0.02, f"({sig:.2f}σ)"))
dev_th = abs(lam - 2.67) / 2.67 * 100
results.append(p("vs 理論 2.67 (%)", dev_th, 0.125, 0.01, f"({dev_th:.2f}%)"))

# ---- E. Allen-Dynes ----
print("\n[E] Allen-Dynes Tc/ω_log (λ=8/3)")
kB = 0.0861734
for mu in (0.10, 0.13, 0.16):
    tc_wl = np.exp(-1.04 * (1 + lam) / (lam - mu * (1 + 0.62 * lam))) / 1.2
    tc_K = tc_wl * 96.4 / kB
    print(f"  μ*={mu:.2f}: Tc/ω_log = {tc_wl:.4f}, Tc = {tc_K:.0f} K  (S03: 0.1703/190, 0.1613/180, 0.1521/170)")
    results.append(p(f"AD μ*={mu}", tc_wl, [0.1703, 0.1613, 0.1521][{0.10:0,0.13:1,0.16:2}[mu]], 0.001))

# ---- F. Tc 定律線性 ----
print("\n[F] Tc = 0.2605×Ω_log 線性 (S03 [D] 表)")
table = {900: 234.4, 1000: 260.5, 1100: 286.5, 1200: 312.6, 1300: 338.6,
         1400: 364.7, 1500: 390.7, 1600: 416.8}
ratios = [table[k] / k for k in table]
print(f"  比率: {['%.4f' % r for r in ratios]}")
results.append(p("比率一致 (0.2605±0.0002)", max(ratios) - min(ratios), 0.0004, 0.0005))
results.append(p("0.2605×1119.4", 0.2605 * 96.4 / kB, 291.4, 1.0, "≈ S03 主解"))

# ---- G. 間隙比 ----
print("\n[G] 間隙比算術")
results.append(p("2×61.0/(k_B×291.4)", 2*61.0/(kB*291.4), 4.86, 0.01))
results.append(p("量度重算 2×53/(k_B×250)", 2*53.0/(kB*250), 4.92, 0.01, "紙 5.6 (Tc 較低)"))

# ---- H. 盲測算術 ----
print("\n[H] 盲測算術")
results.append(p("YH10: 305/0.2605", 305/0.2605, 1171, 1, "→ Ω_log 1171 K"))
results.append(p("YH10: 326/0.2605", 326/0.2605, 1251, 1, "→ Ω_log 1251 K"))
results.append(p("YH10: 0.2605×1300", 0.2605*1300, 339, 1, "K"))
results.append(p("YH10: 0.2605×1400", 0.2605*1400, 365, 1, "K"))
results.append(p("LaD10: 250/√2", 250/np.sqrt(2), 176.8, 0.1, "K"))
results.append(p("ω_max 預言 96.4/0.516939", 96.4/0.516939, 186.48, 0.05, "meV"))

# ---- I. 獨立 Eliashberg 交叉驗證 ----
print("\n[I] 獨立 Eliashberg 交叉驗證 (唔用 S03 函數)")

def eliashberg_ind(T_meV, mu, Om_arr, a2f_arr, Nmax=800, wcs=8.0,
                   seed=1e-5, mix=0.5, tol=1e-10, max_iter=3000):
    """獨立實現: 摺疊 Matsubara (ω̂/Δ̂). T 同 Om 單位 meV."""
    wc = wcs * Om_arr.max()
    Nf = min(Nmax, int(wc / (2 * np.pi * T_meV)))
    if Nf < 8:
        return 0.0
    wn = (2 * np.arange(Nf) + 1) * np.pi * T_meV
    kk = np.arange(2 * Nf)
    wd = 2 * np.pi * T_meV * kk
    lamk = np.zeros(2 * Nf)
    for i in range(len(Om_arr)):
        lamk += 2.0 * a2f_arr[i] * Om_arr[i] / (Om_arr[i]**2 + wd**2)
    i1 = np.abs(np.arange(Nf)[:, None] - np.arange(Nf)[None, :])
    i2 = np.arange(Nf)[:, None] + np.arange(Nf)[None, :] + 1
    Lnm, Lnp = lamk[i1], lamk[i2]
    w, D = wn.copy(), np.full(Nf, seed)
    for _ in range(max_iter):
        denom = np.sqrt(w**2 + D**2)
        wnew = wn + np.pi * T_meV * ((Lnm - Lnp) @ (w / denom))
        Dnew = np.pi * T_meV * ((Lnm + Lnp - 2*mu) @ (D / denom))
        w = mix*wnew + (1-mix)*w
        D = mix*Dnew + (1-mix)*D
        if np.max(np.abs(wnew-w)) < tol and np.max(np.abs(Dnew-D)) < tol:
            break
        if _ == 20 and np.max(np.abs(D)) < seed * 0.3:
            return 0.0
    return float(D[0] / (w[0] / wn[0]))

def tc_ind(mu, Om_arr, a2f_arr):
    T_hi = 320.0
    while eliashberg_ind(T_hi * kB, mu, Om_arr, a2f_arr) > 1e-6:
        T_hi *= 2
    T_lo = 1.0
    for _ in range(50):
        Tm = 0.5 * (T_hi + T_lo)
        if eliashberg_ind(Tm * kB, mu, Om_arr, a2f_arr) > 1e-6:
            T_lo = Tm
        else:
            T_hi = Tm
    return 0.5 * (T_hi + T_lo)

# I1: 正常態 Z₀ = 1+λ (解析恆等)
print("\n  I1: 正常態 Z₀ = 1+λ")
# 用 Einstein 模: λ(n−m) = λ·Ω²/(Ω²+(ω_n−ω_m)²), λ(0) = λ
OmE, lamE = 96.4, 8/3
a2fE = np.array([lamE * OmE / 2.0])   # α²F = (λΩ/2)δ(ω−Ω) → 2∫α²F/ω dω = λ
# 手算正常態 Z₀: 1 + Σ_m λ(m)sgn 摺疊 = 1 + λ(0)
z0_analytic = 1.0 + lamE
# 數值: 一次正常態迭代
T = 50.0 * kB
Nf = min(800, int(8.0 * 2 * OmE / (2 * np.pi * T)))
wn = (2*np.arange(Nf)+1) * np.pi * T
kk = np.arange(2*Nf)
wd = 2*np.pi*T*kk
lamk = 2.0*a2fE[0]*OmE/(OmE**2 + wd**2)
i1 = np.abs(np.arange(Nf)[:,None]-np.arange(Nf)[None,:])
i2 = np.arange(Nf)[:,None]+np.arange(Nf)[None,:]+1
z0_num = 1.0 + (np.pi*T/wn[0]) * np.sum(lamk[i1[0]] - lamk[i2[0]])   # Σ[λ(n−m)−λ(n+m+1)] = λ(0)
results.append(p("Z₀ = 1+λ (Einstein)", z0_num, z0_analytic, 0.05))

# I2: Einstein 模 Tc 文獻範圍
print("  I2: Einstein 模 (Ω=96.4 meV, λ=8/3, μ*=0.13) Tc")
tc_E = tc_ind(0.13, np.array([OmE]), a2fE)
print(f"    Tc(Einstein) = {tc_E:.1f} K;  Tc/Ω = {tc_E/(OmE/kB):.3f}  (文獻範圍 0.16-0.25)")
results.append(p("Tc/Ω ∈ [0.16,0.25]", tc_E/(OmE/kB), 0.205, 0.05))

# I3: 鏈 α²F 重解 (對比 S03 291.4 K)
print("  I3: 鏈 α²F 重解 (對比 S03 291.4 K)")
Om_chain = 2.0 * np.sin(k88 * np.pi / 176) * (186.5 / 2.0)
a2f_chain = (lam / 2.0) * Om_chain / 88.0
tc_chain = tc_ind(0.13, Om_chain, a2f_chain)
print(f"    Tc(鏈) = {tc_chain:.1f} K  (S03: 291.4)")
results.append(p("Tc 鏈 vs S03", tc_chain, 291.4, 3.0))

# ---- 總結 ----
n_ok = sum(1 for r in results if r[3])
n_all = len(results)
print(f"\n  審計: {n_ok}/{n_all} PASS")
for r in results:
    if not r[3]:
        print(f"    ❌ {r[0]}: {r[1]} vs {r[2]}")
print()
print("PASS" if n_ok == n_all else "FAIL")
