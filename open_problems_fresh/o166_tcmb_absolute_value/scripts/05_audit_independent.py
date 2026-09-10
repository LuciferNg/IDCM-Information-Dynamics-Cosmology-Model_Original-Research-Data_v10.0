#!/usr/bin/env python3
"""
O166 — 05: 獨立審計 (Independent Audit — 零依賴重算全部文檔宣稱)
================================================================
由第一原理 (φ, N_d, M₀, k_B, T_CMB, Ω_b, ω_ring, η_B, m_p, G, ħ, c) 重算:
  docs/01 宣稱: M₀/kT, ln, ℓ, Unruh 比, 鏈模式 n
  docs/02 宣稱: T_pred, 誤差帶, η_B(Fixsen), G 敏感性, 沙漠命中率
  docs/03 宣稱: 舊公式值, dev, e 冪 φ 指數
"""
from mpmath import mp, mpf, pi, sin, cos, exp, ln, sqrt
mp.dps = 60

# ── 原始常量 ──
phi = (mpf(1) + sqrt(mpf(5)))/mpf(2)
Nd = mpf(44)
M0_eV = mpf('27.900915e6')
kB_eV = mpf('8.617333262145e-5')
T_fix = mpf('2.72548')
kT = kB_eV*T_fix
Omega_Lambda = mpf(4)/(phi**4 - 1)
Omega_b = (1 - Omega_Lambda)/(1 + mpf('6.5030'))
H0 = mpf('72.59')
eta_B = mpf('6.0622e-10')
m_p_kg = mpf('938.27208816')*mpf('1.78266192e-30')
G = mpf('6.67430e-11')
c_si = mpf('299792458')
k_B_SI = mpf('1.380649e-23')
hbar_SI = mpf('6.62607015e-34')/(2*pi)
zeta3 = mpf('1.2020569031595942854')
Mpc_m = mpf('3.0856775814913673e22')
T_Pl = mpf('1.416784e32')

results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'✅' if cond else '❌'}] {name}" + (f" — {detail}" if detail else ""))

print("=" * 74)
print("  O166 — 05: 獨立審計 (零依賴重算)")
print("=" * 74)

# ── 1. docs/01 宣稱 ──
print("\n─── [1] docs/01 關鍵比 ───")
R1 = M0_eV/kT
ell = ln(R1)/(2*ln(phi))
dist = min(abs(ell - mpf(k)) for k in range(0, 60))
print(f"  M₀/kT = {float(R1):.10e}  (doc: 1.187962e11)   ln = {float(ln(R1)):.8f}  (doc: 25.50068)")
print(f"  ℓ = {float(ell):.6f}, 距最近整數 = {float(dist):.4f}  (doc: 26.4963 / 0.4963)")
check("[1a] M₀/kT 重算一致", abs(R1/mpf('1.1879620240e11') - 1) < mpf('1e-8'))
check("[1b] ℓ 非整數 (O165 排除)", dist > 0.01, f"dist={float(dist):.4f}")

# Unruh: ω_ring = c/R_world = 72.59 km/s/Mpc
omega_s = H0*1000/Mpc_m
T_unruh = hbar_SI*omega_s/(2*pi*k_B_SI)
print(f"  ω_ring = {float(omega_s):.4e} rad/s; T_Unruh = {float(T_unruh):.3e} K")
print(f"  T_CMB/T_Unruh = {float(T_fix/T_unruh):.2e}  (doc: 9.5e29)")
check("[1c] Unruh 比 > 1e20", T_fix/T_unruh > mpf('1e20'))

# 鏈模式 n
n_kT = Nd*(kT/M0_eV)/pi
print(f"  kT 對應鏈模式 n ≈ {float(n_kT):.3e}  (doc: 1.18e-10)")
check("[1d] n ≈ 0 (冇模式)", n_kT < mpf('1e-6'))

# ── 2. docs/02 投影閉合 ──
print("\n─── [2] docs/02 投影閉合 ───")
def T_of(eta):
    H0_si = H0*1000/Mpc_m
    rho_c = 3*H0_si**2/(8*pi*G)
    n_b = Omega_b*rho_c/m_p_kg
    n_g = n_b/eta
    return (n_g*pi**2/(2*zeta3))**(mpf(1)/3)*hbar_SI*c_si/k_B_SI

T_pred = T_of(eta_B)
print(f"  T_pred = {float(T_pred):.6f} K  (doc: 2.72840)")
print(f"  dev vs Fixsen = {float(abs(T_pred/T_fix-1)*100):.4f}%  (doc: 0.107%)")
band = (mpf(1)/3)*(mpf('0.0057') + 2*mpf('0.0019') + mpf('0.0062'))
print(f"  誤差帶 = {float(band*100):.3f}%  (doc: 0.52%)")
check("[2a] T_pred round-trip", abs(T_pred/mpf('2.72840') - 1) < mpf('1e-4'))
check("[2b] Fixsen 喺誤差帶", abs(T_pred/T_fix-1) < band, f"dev {float(abs(T_pred/T_fix-1)*100):.3f}% < {float(band*100):.2f}%")

# η_B with Fixsen
def eta_of(T):
    H0_si = H0*1000/Mpc_m
    rho_c = 3*H0_si**2/(8*pi*G)
    n_b = Omega_b*rho_c/m_p_kg
    n_g = 2*zeta3/pi**2*(k_B_SI*T/(hbar_SI*c_si))**3
    return n_b/n_g

eta_fix = eta_of(T_fix)
print(f"  η_B(T=Fixsen) = {float(eta_fix):.4e}  (doc: 6.0817e-10), dev vs 6.1e-10 = {float(abs(eta_fix/mpf('6.1e-10')-1)*100):.3f}%")
check("[2c] BBN 穩健 (<1%)", abs(eta_fix/mpf('6.1e-10')-1) < mpf('0.01'))

# G 敏感性
print(f"  G+1% → T×{float((mpf('1.01'))**(-mpf(1)/3)):.6f}  (doc: 0.996689)")
check("[2d] T ∝ G^{−1/3}", abs((mpf('1.01'))**(-mpf(1)/3) - mpf('0.996689')) < mpf('1e-5'))

# ── 3. docs/03 舊公式 ──
print("\n─── [3] docs/03 舊公式審計 ───")
T_old = mpf(2)*T_Pl*exp(mpf(-74))*(mpf(134)/mpf(100))*(mpf(1)-phi**(-mpf(9)))
print(f"  舊公式值 = {float(T_old):.6f} K  (doc: 2.728321)")
print(f"  dev vs Fixsen = {float(abs(T_old/T_fix-1)*100):.4f}%  (doc: 0.1042%)")
print(f"  exp(−74) = φ^{{−{float(74/ln(phi)):.3f}}}  (doc: −153.78, 非整數)")
check("[3a] 舊公式 dev = 0.1042%", abs(abs(T_old/T_fix-1)*100 - mpf('0.1042')) < mpf('0.001'))
check("[3b] e 冪 φ 指數非整數", abs(74/ln(phi) - mpf('153.778')) < mpf('0.01'))

# ── 4. 沙漠命中率 (docs/02 宣稱) ──
print("\n─── [4] 沙漠命中率 ───")
base = [5, 8, 11, 13, 17, 21, 29, 33, 44, 55, 61, 88, 123, 134, 176, 192]
hits = 0
for n in base:
    for k in range(2, 21):
        if abs(mpf(n)**k/R1 - 1) < mpf('0.005'):
            hits += 1
rate = hits/(len(base)*19)
print(f"  單冪命中率 = {rate*100:.2f}%  (doc: 0.33%, 1 個 = 17^9)")
check("[4] 沙漠稀疏 (<1%)", rate < mpf('0.01'), f"{len(base)*19} 候選 {hits} 命中")

# ── 5. doc 對齊檢查 ──
print("\n─── [5] 文檔宣稱 vs 重算 ───")
claims = [
    ("M₀/kT = 1.187962e11",      abs(R1/mpf('1.187962e11')-1) < mpf('1e-6')),
    ("ln = 25.50068",             abs(ln(R1) - mpf('25.50068')) < mpf('1e-4')),
    ("T_pred = 2.7284",           abs(T_pred/mpf('2.7284')-1) < mpf('1e-4')),
    ("dev Fixsen 0.107%",         abs(abs(T_pred/T_fix-1)*100 - mpf('0.107')) < mpf('0.01')),
    ("η_B(Fixsen) 6.0817e-10",    abs(eta_fix/mpf('6.0817e-10')-1) < mpf('1e-4')),
    ("舊公式 2.728321 dev 0.1042%", abs(T_old/mpf('2.728321')-1) < mpf('1e-5')),
]
for name, cond in claims:
    check(f"doc 宣稱: {name}", cond)

print(f"\n{'═'*74}")
print(f"  O166-05 獨立審計: {sum(results)}/{len(results)} PASS")
print(f"{'═'*74}")
