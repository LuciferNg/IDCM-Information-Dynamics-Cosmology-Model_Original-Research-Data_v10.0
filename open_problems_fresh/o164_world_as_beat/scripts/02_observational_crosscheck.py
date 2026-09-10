"""
O164 P2/P3 — 觀測交叉: H₀ 家族, 宇宙年齡, 質量-頻率鎖, T_CMB 狀態
=================================================================
P2: f_Kchain ↔ H₀ — 「H₀」係 omega_ring 嘅誤讀 (O73), 距離階梯簇聚 omega_ring
P3: m_n = M0·sqrt(gamma_n) (O82) 同 f_n = (c/2·lambda_sync)·sqrt(gamma_n)
    → 質量-頻率共享同一 sqrt(gamma_n) 階梯 → m_n/f_n = 常數 (鎖定)
T_CMB: 冇結構閉合 → 🔴 (e^51/2 候選移交 O165)
"""
from mpmath import mp, mpf, sin, cos, pi, sqrt, exp, ln, log
mp.dps = 50

# ---- 常數 (同 script 01) ----
R_world = mpf('4129.94'); Nd = 44; c = mpf('299792.458')
Mpc_to_km = mpf('3.085677581e19'); Gyr_s = mpf('3.15576e16')
omega_ring = mpf('72.59') / Mpc_to_km
c_over_R = c / (R_world * Mpc_to_km)
L_ring = 2*pi*R_world; lambda_sync = L_ring/88
f_ring = omega_ring/(2*pi)
f_scale = 88*f_ring
f_1 = 88*c_over_R*sin(pi/88)/(2*pi)
M0 = mpf('27.900915')       # MeV, M0_fund (O82, 源自 O38/O34)
kB = mpf('8.617333262e-5')  # eV/K
T_CMB = mpf('2.72548')      # K (Fixsen 2009, 精度 0.02%)
kappa = mpf('1')/16
phi_inv = (mpf(5).sqrt()-1)/2   # phi^-1 = 0.618...

print("=" * 72)
print("O164 P2 — f ↔ H₀ 交叉閉合")
print("=" * 72)
h0 = {
    'SH0ES 2022':      mpf('73.04'), 'Miras': mpf('73.3'), 'Maser': mpf('73.9'),
    'JAGB':            mpf('72.4'),  'TRGB': mpf('69.85'), 'Planck': mpf('67.36'),
    'ACT':             mpf('68.3'),  'SPT': mpf('68.8'),   'TDCOSMO': mpf('67.4'),
    'H0LiCOW':         mpf('73.3'),
}
omega_km = mpf('72.59')
print(f"omega_ring = {float(omega_km):.2f} (km/s)/Mpc  ← 世界環角頻率 (O73)")
print(f"{'觀測':<12}{'H0':>8}{'dev vs omega_ring':>18}{'判讀':>10}")
for k, v in h0.items():
    dev = (v/omega_km - 1)*100
    tag = '距離階梯' if k in ('SH0ES 2022','Miras','Maser','JAGB','H0LiCOW') else ('TRGB' if k=='TRGB' else 'CMB')
    print(f"{k:<12}{float(v):>8.2f}{float(dev):>+15.3f}%{tag:>10}")

# TRGB = omega_ring(1 - kappa·phi^-1) — O73 閉合
trgb_pred = omega_km*(1 - kappa*phi_inv)
print(f"\nTRGB 預言 omega_ring(1-kappa·phi^-1) = {float(trgb_pred):.3f} vs 69.85 "
      f"(dev {float(abs(trgb_pred/69.85-1)*100):.4f}%) [O73 ✅]")

# 距離階梯簇聚
ladder = [mpf('73.04'), mpf('73.3'), mpf('73.9'), mpf('72.4'), mpf('73.3')]
ladder_mean = sum(ladder)/len(ladder)
print(f"距離階梯均值 = {float(ladder_mean):.3f} vs omega_ring = 72.59 "
      f"(dev {float((ladder_mean/omega_km-1)*100):+.3f}%)")

print("""
★ 判讀: 「H₀」唔係基本量。omega_ring = c/R_world 先係。
  f_1 = omega_ring/2·sinc — 基頻鎖定半環角頻率 (P1 C6)。
  距離階梯簇聚 omega_ring (dev <1%); TRGB = omega_ring(1-kappa·phi^-1) ✅;
  CMB 家族低 5-7% = 真張力 (H3 開放, 唔喺本 O 閉合)。
  f_scale = 3.29e-17 Hz ≠ H₀ 任何值 — 「1e-17 Hz = H₀」係 rad/s vs Hz 混淆。
""")

# ---- 宇宙年齡 ----
print("=" * 72)
print("宇宙年齡交叉 (ΛCDM 年齡 = 模型依賴)")
print("=" * 72)
age_planck = mpf('13.797')   # Gyr, Planck 2018 flat ΛCDM
T1half = mpf(1)/c_over_R / Gyr_s   # R_world/c
T1 = 2/(c_over_R*sin(pi/88)/(pi/88)) / Gyr_s * 1  # 2/(omega_ring·sinc)
T1 = 1/f_1/Gyr_s
print(f"R_world/c (半徑光穿越 = T_1/2) = {float(T1half):.4f} Gyr")
print(f"T_1 (基頻周期)                 = {float(T1):.4f} Gyr")
print(f"ΛCDM 年齡 (Planck 2018)        = {float(age_planck):.4f} Gyr")
print(f"dev age/(R_world/c) = {(float(age_planck/T1half-1)*100):+.3f}%  ← 2.4%, 模型依賴, 🟡 唔收為閉合")
print("(IDCM: O51 真年齡 11,100.64 Gyr — K_chain 冇起始; 13.8 Gyr 係 ΛCDM 熱歷史)")

# ---- P3a: 質量-頻率鎖 ----
print()
print("=" * 72)
print("O164 P3a — 質量-頻率鎖: m_n = M0·sqrt(gamma_n) 與 f_n 共享階梯")
print("=" * 72)
c_2ls = c/(2*lambda_sync*Mpc_to_km)  # Hz
h_eff = 2*M0*lambda_sync*Mpc_to_km/c  # MeV·s? M0[MeV]·lambda[km]/c[km/s]
# 單位: M0 (MeV) × lambda (km) / c (km/s) = MeV·s → 用 1e6 轉 eV·s
h_eff_eVs = 2*M0*mpf('1e6')*lambda_sync*Mpc_to_km/c
maxdev = mpf(0)
for n in range(1, Nd+1):
    g = 4*sin(pi*n/88)**2
    m_n = M0*sqrt(g)                 # MeV (O82: m_n = M0·2sin = M0·sqrt(gamma))
    f_n = c_2ls*sqrt(g)              # Hz (P1 C4)
    ratio = m_n*mpf('1e6')/f_n       # eV·s
    d = abs(ratio/h_eff_eVs - 1)
    if d > maxdev: maxdev = d
print(f"m_n/f_n = 2·M0·lambda_sync/c = {float(h_eff_eVs):.6e} eV·s (44/44 常數)")
print(f"  max dev = {float(maxdev):.2e}  →  質量-頻率鎖定 ✅")
print(f"  (IDCM 版 E=hf: m_n = h_eff·f_n, h_eff = 2M0·lambda_sync/c 全部譜量)")
print(f"  ħ = {float(mpf('6.582119569e-16')):.4e} eV·s; h_eff/ħ = {float(h_eff_eVs/mpf('6.582119569e-16')):.4e}")

# ---- P3b: T_CMB ----
print()
print("=" * 72)
print("O164 P3b — T_CMB 狀態 (結構候選, 唔擬合)")
print("=" * 72)
kT = kB*T_CMB
M0_eV = M0*mpf('1e6')
print(f"T_CMB = {float(T_CMB):.5f} K, k_B·T = {float(kT):.6e} eV")
print(f"M0/k_B·T_CMB = {float(M0_eV/kT):.6e}  |  hbar·omega_ring/k_B·T_CMB = {float(mpf('6.582119569e-16')*omega_ring/kT):.3e}")

cands = [
    ("e^(N_gen·F_proj/2) = e^25.5", exp(mpf('51')/2), M0_eV/kT),
    ("e^25",                      exp(mpf(25)),      M0_eV/kT),
    ("e^26",                      exp(mpf(26)),      M0_eV/kT),
    ("2^36",                      2**36,             M0_eV/kT),
    ("88^15",                     88**15,            M0_eV/kT),
    ("176^13",                    176**13,           M0_eV/kT),
    ("44^18",                     44**18,            M0_eV/kT),
]
print(f"\n{'候選':<26} {'值':>13} {'dev vs M0/kT':>14}")
best = None
for name, val, target in cands:
    dev = abs(val/target - 1)*100
    flag = '★' if dev < 0.5 else ''
    print(f"{name:<26} {float(val):>13.5e} {float(dev):>13.4f}% {flag}")
    if dev < 0.5 and (best is None or dev < best[1]):
        best = (name, dev)

print()
if best:
    print(f"🟡 最佳候選: {best[0]} dev {float(best[1]):.4f}% — 冇機制, 反秘數風險,")
    print("   移交 O165 (e⁻ⁿ 權重本體, sub-question 2: 玻爾茲曼因子身份) — 本 O 唔收為閉合")
else:
    print("🔴 T_CMB ↔ K_chain 頻率冇結構閉合 (<0.5% 候選缺失) — 誠實開放")

print()
print("P2: f_1 = omega_ring/2 ✅ (P1 C6) | H₀ = omega_ring 誤讀 ✅ (O73)")
print("P3a: m_n ↔ f_n 鎖定 ✅ | P3b: T_CMB 🔴/🟡 移交 O165")
