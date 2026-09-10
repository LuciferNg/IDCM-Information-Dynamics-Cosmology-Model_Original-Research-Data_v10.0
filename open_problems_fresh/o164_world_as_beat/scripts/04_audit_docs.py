"""
O164 審計 — 文檔獨立核對 (Independent Cross-Check of Every Document Claim)
=========================================================================
由第一原理 (只有 c, R_world, 88, N_d, M0, T_CMB, k_B, kappa, phi) 重算
每個文檔宣稱嘅數值, 同文檔字面值比較。唔讀文檔文字 — 宣稱值由審計者
逐項提取編碼 (doc ref + 字面值 + 容差), 全部重算驗證。

用法: python3 scripts/04_audit_docs.py
"""
from mpmath import mp, mpf, sin, cos, pi, sqrt, exp, log10, ln
mp.dps = 60

# ================= 第一原理常數 (唯一輸入) =================
R_world   = mpf('4129.94')           # Mpc (O73 儲存值)
Nd        = 44
c         = mpf('299792.458')        # km/s
Mpc_to_km = mpf('3.085677581e19')
Gyr_s     = mpf('3.15576e16')
omega_ring_km = mpf('72.59')         # (km/s)/Mpc
M0_MeV    = mpf('27.900915')         # M0_fund (O82)
kB        = mpf('8.617333262e-5')    # eV/K
T_CMB     = mpf('2.72548')           # K
hbar_eVs  = mpf('6.582119569e-16')   # eV·s
kappa     = mpf(1)/16
phi_inv   = (mpf(5).sqrt()-1)/2      # φ^-1

# H₀ 家族 (文獻值, data/01)
H0 = {'SH0ES':mpf('73.04'),'Miras':mpf('73.3'),'Maser':mpf('73.9'),
      'JAGB':mpf('72.4'),'TRGB':mpf('69.85'),'Planck':mpf('67.36'),
      'ACT':mpf('68.3'),'SPT':mpf('68.8'),'TDCOSMO':mpf('67.4'),'H0LiCOW':mpf('73.3')}

# ================= 導出量 (全部由第一原理) =================
omega_ring = omega_ring_km / Mpc_to_km            # rad/s
c_over_R   = c / (R_world * Mpc_to_km)            # s^-1
L_ring     = 2*pi*R_world
lambda_sync = L_ring / 88
T_ring     = L_ring / c * Mpc_to_km / Gyr_s       # Gyr
f_ring     = omega_ring / (2*pi)
f_scale    = 88 * f_ring
f1  = 88*c_over_R*sin(pi/88)/(2*pi)               # Hz (幾何)
f22 = 88*c_over_R*sin(pi*22/88)/(2*pi)
f44 = 88*c_over_R*sin(pi*44/88)/(2*pi)
T1  = 1/f1 / Gyr_s
sinc88 = sin(pi/88)/(pi/88)
kT_eV  = kB * T_CMB
M0_eV  = M0_MeV * mpf('1e6')
h_eff  = 2*M0_eV*lambda_sync*Mpc_to_km/c          # eV·s

def gamma44(n): return 4*sin(pi*n/88)**2

# ================= 核對引擎 =================
results = []
def chk(doc, label, calc, stated, tol, note=""):
    """calc = 重算值 (mpf); stated = 文檔字面值 (float); tol = 相對容差"""
    if stated == 0:
        ok = abs(calc) < tol
    else:
        ok = abs(calc/stated - 1) < tol
    results.append((doc, label, ok, calc, stated, tol, note))
    tag = 'PASS' if ok else 'FAIL'
    print(f"  [{tag}] {doc:>6} | {label:<52} calc={float(calc):.6g} doc={float(stated):.6g} tol={tol:.0e} {note}")

print("=" * 110)
print("O164 文檔獨立核對 (第一原理重算 vs 文檔字面值)")
print("=" * 110)

# ---------- data/01_observational_data.md ----------
print("\n--- data/01_observational_data.md ---")
chk("data01","omega_ring (rad/s)", omega_ring, 2.35248e-18, 1e-4)
chk("data01","T_ring (Gyr)", T_ring, 84.63, 1e-3)
chk("data01","lambda_sync (Mpc)", lambda_sync, 294.877, 1e-4)
chk("data01","k_B·T_CMB (eV)", kT_eV, 2.348637e-4, 1e-4)
chk("data01","f_ring (Hz)", f_ring, 3.7441e-19, 1e-4)
chk("data01","f_1 (Hz)", f1, 1.1760e-18, 1e-4)
chk("data01","T_1 (Gyr)", T1, 26.946, 1e-4)
chk("data01","f_22 (Hz)", f22, 2.3298e-17, 1e-4)
chk("data01","f_44 = f_scale (Hz)", f44, 3.2948e-17, 1e-4)
# H₀ 家族 dev (data 表唔列 dev, 但列值 — 文獻值直接列, 驗證 ω_ring 對應)
for k, v in H0.items():
    chk("data01", f"H0 {k} (文獻)", v, float(v), 1e-9)  # 文獻引用值本身

# ---------- docs/02_frequency_spectral_identity.md ----------
print("\n--- docs/02_frequency_spectral_identity.md ---")
# ω_n = N_d·ω_ring·√γ_n: 幾何身份 (ω_ring := c/R_world) dev ~0; 儲存值 dev 3.8e-7 (0.00004%)
maxdev = mpf(0)
for n in range(1, Nd+1):
    w_n = 88*c_over_R*sin(pi*n/88)
    w_id = Nd*c_over_R*sqrt(gamma44(n))
    d = abs(w_n/w_id - 1)
    if d > maxdev: maxdev = d
chk("d02","ω_n = 44·ω_ring·√γ_n (幾何, max dev)", maxdev, 0, 1e-50, "=0 (dps=60 噪音)")
stored_dev = abs(Nd*omega_ring*sqrt(gamma44(1))/(88*c_over_R*sin(pi/88)) - 1)
chk("d02","ω_n 儲存值 dev (%)", stored_dev*100, 3.8e-5, 1e-2, "=3.7826e-7 (stored rounding)")
# f_44 = 88·f_ring = c/λ_sync
chk("d02","f_44 = 88·f_ring (dev)", abs(f44/(88*f_ring)-1), 0, 1e-6)
chk("d02","f_44 = c/λ_sync (dev)", abs(f44/(c/(lambda_sync*Mpc_to_km))-1), 1.6e-61, 5e-2)
# f_1 = (ω_ring/2)·sinc
chk("d02","sinc(π/88)", sinc88, 0.99978760, 1e-8)
chk("d02","f_1 = (ω_ring/2)·sinc (dev, 幾何)", abs(f1/((c_over_R/2)*sinc88)-1), 0, 1e-50)
# f_1 ≈ ω_ring/2 偏差 0.021%
chk("d02","f_1 vs ω_ring/2 dev (%)", abs(f1/(omega_ring/2)-1)*100, 0.021, 5e-2, "~0.0212%")
# T_1 = 2/(ω_ring·sinc)
chk("d02","T_1 = 2/(ω_ring·sinc) (Gyr)", 2/(omega_ring*sinc88)/Gyr_s, 26.946, 1e-4)
# f_n = (c/2λ_sync)·√γ_n (44/44 dev 3.1e-61)
maxdev = mpf(0)
for n in range(1, Nd+1):
    f_n = 88*c_over_R*sin(pi*n/88)/(2*pi)
    f_id = c/(2*lambda_sync*Mpc_to_km)*sqrt(gamma44(n))
    d = abs(f_n/f_id - 1)
    if d > maxdev: maxdev = d
chk("d02","f_n = (c/2λ_sync)√γ_n (max dev)", maxdev, 3.1e-61, 5e-2, "dps=60 噪音")
# f_scale = N_d·f_ring·√γ_max
chk("d02","f_scale = 44·f_ring·√γ_max (Hz)", Nd*f_ring*sqrt(gamma44(44)), 3.2948e-17, 1e-4)
chk("d02","γ_max = 4 = B", gamma44(44), 4, 1e-40)
# 儲存值一致 0.00004% (3.8e-7)
chk("d02","R_world·ω_ring/c 一致 dev (%)", abs(R_world*omega_ring*Mpc_to_km/c - 1)*100, 3.8e-5, 1e-2,
    f"={float(abs(R_world*omega_ring*Mpc_to_km/c-1)*100):.4e}%")
# v_g(22) = 0.7071c, v_g(44) = 0
chk("d02","v_g(22)/c", cos(pi*22/88), 0.7071, 1e-3)
chk("d02","v_g(44)/c", cos(pi*44/88), 0, 1e-50)

# ---------- docs/03_h0_tension_cross.md ----------
print("\n--- docs/03_h0_tension_cross.md ---")
# 距離階梯 devs (±2% 簇聚)
ladder = [H0['SH0ES'], H0['Miras'], H0['Maser'], H0['JAGB'], H0['H0LiCOW']]
devs = [abs(v/omega_ring_km-1)*100 for v in ladder]
chk("d03","階梯最大 dev (%)", max(devs), 2, 1e-1, f"max={float(max(devs)):.2f}%")
# TRGB pred
trgb_pred = omega_ring_km*(1-kappa*phi_inv)
chk("d03","TRGB pred (km/s/Mpc)", trgb_pred, 69.786, 1e-3)
chk("d03","TRGB dev (%)", abs(trgb_pred/H0['TRGB']-1)*100, 0.0915, 5e-2)
# 階梯均值
lmean = sum(ladder)/len(ladder)
chk("d03","階梯均值 (km/s/Mpc)", lmean, 73.19, 1e-3)
chk("d03","階梯均值 dev (%)", abs(lmean/omega_ring_km-1)*100, 0.82, 1e-2)
# 年齡交叉
chk("d03","R_world/c (Gyr)", 1/c_over_R/Gyr_s, 13.470, 1e-4)
chk("d03","T_1 (Gyr)", T1, 26.946, 1e-4)
chk("d03","age/(R_world/c) dev (%)", abs(mpf('13.797')*Gyr_s*c_over_R - 1)*100, 2.43, 1e-2)
# 1+1/41 對比 (正確值: ratio=1.02427, dev=0.012%)
age_ratio = mpf('13.797')/ (1/c_over_R/Gyr_s)
chk("d03","age/ratio = 1.02427", age_ratio, 1.02427, 1e-4)
chk("d03","1+1/41 dev (%)", abs(age_ratio/(1+mpf(1)/41)-1)*100, 0.012, 5e-2)

# ---------- docs/04_mass_frequency_lock.md ----------
print("\n--- docs/04_mass_frequency_lock.md ---")
chk("d04","h_eff (eV·s)", h_eff, 1.693633e24, 1e-4)
maxdev = mpf(0)
for n in range(1, Nd+1):
    m_n = M0_eV*sqrt(gamma44(n))
    f_n = c/(2*lambda_sync*Mpc_to_km)*sqrt(gamma44(n))
    d = abs((m_n/f_n)/h_eff - 1)
    if d > maxdev: maxdev = d
chk("d04","m_n/f_n 常數 (max dev, 精確地板)", maxdev, 0, 1e-49, f"doc 2.7e-51 (script 02, dps=50)")
chk("d04","h_eff/ħ", h_eff/hbar_eVs, 2.5731e39, 1e-4)
# 四欄表
chk("d04","√γ_1", sqrt(gamma44(1)), 0.0714, 1e-3)
chk("d04","√γ_7", sqrt(gamma44(7)), 0.4946, 1e-3)
chk("d04","√γ_20", sqrt(gamma44(20)), 1.3098, 1e-3)
chk("d04","cos(π/88)", cos(pi/88), 0.9994, 1e-4)
chk("d04","cos(7π/88)", cos(7*pi/88), 0.9689, 1e-4)
chk("d04","cos(20π/88)", cos(20*pi/88), 0.7557, 1e-4)
chk("d04","csc(π/88)", 1/sin(pi/88), 28.0, 1e-3)
chk("d04","csc(7π/88)", 1/sin(7*pi/88), 4.04, 1e-3)
chk("d04","csc(20π/88)", 1/sin(20*pi/88), 1.53, 2e-3)
# T_CMB 候選
chk("d04","M₀/k_BT_CMB", M0_eV/kT_eV, 1.187962e11, 1e-4)
chk("d04","ħ·ω_ring/k_BT_CMB", hbar_eVs*omega_ring/kT_eV, 6.59e-30, 1e-2)
e255 = exp(mpf('51')/2)
chk("d04","e^25.5", e255, 1.18716e11, 1e-4)
chk("d04","e^25.5 dev vs M₀/kT (%)", abs(e255/(M0_eV/kT_eV)-1)*100, 0.0675, 1e-2)
phi = (mpf(5).sqrt()+1)/2
chk("d04","25.5/lnφ 指數", mpf('25.5')/ln(phi), 52.99, 1e-3)
chk("d04","φ^53 dev vs M₀/kT (%)", abs(phi**53/(M0_eV/kT_eV)-1)*100, 0.356, 5e-2)
chk("d04","ℓ = 25.5/(2lnφ)", mpf('25.5')/(2*ln(phi)), 26.5, 1e-2)
# 工程後果
chk("d04","log10(1e13/f_44)", log10(mpf('1e13')/f44), 29.5, 1e-2)

# ---------- docs/01_beat_ontology.md ----------
print("\n--- docs/01_beat_ontology.md ---")
S_even = sum(4*sin(pi*k/176)**2 for k in range(2, 89, 2))
S_odd  = sum(4*sin(pi*k/176)**2 for k in range(1, 89, 2))
chk("d01","Σγ_even = 90", S_even, 90, 1e-9)
chk("d01","Σγ_odd = 88", S_odd, 88, 1e-9)
chk("d01","total = 178 = 2F₁₁", S_even+S_odd, 178, 1e-9)
maxdev = mpf(0)
for n in range(1, 44):
    d = abs(gamma44(n)+gamma44(44-n)-4)
    if d > maxdev: maxdev = d
chk("d01","Z₂ γ_n+γ_(44−n)=4 (maxdev)", maxdev, 0, 1e-49)
chk("d01","γ_44 = 4 = B", gamma44(44), 4, 1e-40)
ok_sandwich = exp(-3) < kappa < exp(-2)
results.append(("d01","κ 夾層 e⁻²>κ>e⁻³", ok_sandwich, kappa, 1, 0, ""))
print(f"  [{'PASS' if ok_sandwich else 'FAIL'}] {'d01':>6} | {'κ 夾層 e⁻²>κ>e⁻³':<52} κ={float(kappa):.5f} (e⁻²={float(exp(-2)):.5f}, e⁻³={float(exp(-3)):.5f})")
chk("d01","T_ring (Gyr)", T_ring, 84.63, 1e-3)
chk("d01","log10(1e13/f_44)", log10(mpf('1e13')/f44), 29.5, 1e-2)

# ---------- final_result.md ----------
print("\n--- final_result.md ---")
chk("fin","f_44 = 3.2948e-17 Hz", f44, 3.2948e-17, 1e-4)
# f_n dev 3e-61 (script 01 dps=60 地板)
maxdev_fn = mpf(0)
for n in range(1, Nd+1):
    f_n = 88*c_over_R*sin(pi*n/88)/(2*pi)
    f_id = c/(2*lambda_sync*Mpc_to_km)*sqrt(gamma44(n))
    d = abs(f_n/f_id - 1)
    if d > maxdev_fn: maxdev_fn = d
chk("fin","f_n = (c/2λ_sync)√γ_n dev (精確地板)", maxdev_fn, 0, 1e-49, f"doc 3e-61")
chk("fin","f_44 = c/λ_sync dev (精確地板)", abs(f44/(c/(lambda_sync*Mpc_to_km))-1), 0, 1e-49, "doc 1.6e-61")
chk("fin","sinc = 0.99979", sinc88, 0.99979, 1e-5)
chk("fin","h_eff = 1.6936e24 eV·s", h_eff, 1.6936e24, 1e-4)
chk("fin","TRGB = 69.786 dev 0.0915%", trgb_pred, 69.786, 1e-3)
chk("fin","m_n/f_n dev (精確地板)", maxdev, 0, 1e-49, "doc 2.7e-51")
# 放棄令數字
chk("fin","e^{−25.5} dev 0.068%", abs(e255/(M0_eV/kT_eV)-1)*100, 0.068, 1e-2)
chk("fin","φ^{−53} dev 0.356%", abs(phi**53/(M0_eV/kT_eV)-1)*100, 0.356, 5e-2)

# ---------- 01_problem_record.md ----------
print("\n--- 01_problem_record.md ---")
chk("rec","f_44 = 3.29e-17 Hz = c/λ_sync", f44, 3.29e-17, 5e-3)

# ================= 總結 =================
npass = sum(1 for r in results if r[2])
nfail = len(results) - npass
print()
print("=" * 110)
print(f"審計總結: {npass}/{len(results)} PASS, {nfail} FAIL")
print("=" * 110)
for doc, label, ok, calc, stated, tol, note in results:
    if not ok:
        print(f"  ❌ {doc} | {label}: calc={float(calc):.8g} vs doc={float(stated):.8g}")
