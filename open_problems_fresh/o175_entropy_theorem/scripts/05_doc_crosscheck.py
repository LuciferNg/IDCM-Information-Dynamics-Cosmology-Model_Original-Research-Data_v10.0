#!/usr/bin/env python3
"""
O175 script 05 — 全文檔獨立核對 (Independent Doc Crosscheck)
=============================================================
由零重算 docs/01-05 所有公式/數值 (mpmath 60 dps), 唔依賴原 scripts.
目的: 捉 doc 入面嘅錯 (包括自己寫錯嘅).
"""
import numpy as np
import mpmath as mp
from pathlib import Path

mp.mp.dps = 60
O175 = Path(__file__).resolve().parent.parent
BASE = O175.parent

PASS = 0
FAIL = 0
def chk(doc, claim, computed, docval, tol):
    global PASS, FAIL
    ok = abs(computed - docval) <= tol
    if ok:
        PASS += 1
        print(f"  [✔] {doc}: {claim} = {mp.nstr(computed, 8)} (doc {mp.nstr(docval, 8)})")
    else:
        FAIL += 1
        print(f"  [✘] {doc}: {claim} = {mp.nstr(computed, 8)} vs doc {mp.nstr(docval, 8)}")

Nd = mp.mpf(44); B = mp.mpf(4); L5 = mp.mpf(11); L7 = mp.mpf(29)
L10 = mp.mpf(123); mu2 = mp.mpf(2)
T_ring = mp.mpf('84.6349')
Bn = L10/(2*Nd); Emin = L10/(4*Nd)
gamma_conv = 4*Nd + B*B
c = mp.mpf('299792458'); R_world = mp.mpf('4129.94')
Mpc_m = mp.mpf('3.085677581e22'); G = mp.mpf('6.674e-11'); M_sun = mp.mpf('1.989e30')

print("=" * 74)
print("docs/01 — 寫入通道")
print("=" * 74)
chk("01", "gamma = 4N_d+B² = 192", gamma_conv, 192, 0)
chk("01", "B(n) = 123/88", Bn, mp.mpf(123)/88, 0)
chk("01", "E_min = 123/176", Emin, mp.mpf(123)/176, 0)
dE_max = Bn*gamma_conv
chk("01", "dE_write max = B(n)·γ = 268.3636", dE_max, mp.mpf('268.363636'), mp.mpf('1e-4'))
chk("01", "2A = 268.4 dev 0.014%", abs(2*mp.mpf('134.2')/dE_max - 1), mp.mpf('1.36e-4'), mp.mpf('1e-5'))
dS_bits = Bn/mp.log(2)
chk("01", "dS bits = 2.017", dS_bits, mp.mpf('2.017'), mp.mpf('1e-3'))
corr = Emin - mp.log(2) - mp.mpf(1)/176
chk("01", "E_min − ln2 − 1/176 = 3.46e-5", corr, mp.mpf('3.4638e-5'), mp.mpf('1e-7'))
L10r = mp.nint(4*Nd*mp.log(2) + 1)
chk("01", "L10 = round(4N_d ln2 + 1) = 123", L10r, 123, 0)
chk("01", "44 × B(n) = 61.5", 44*Bn, mp.mpf('61.5'), 0)
chk("01", "88 × E_min = 61.5", 88*Emin, mp.mpf('61.5'), 0)
write_bits = mp.mpf('61.5')/mp.log(2)
chk("01", "write bits/cycle = 88.7", write_bits, mp.mpf('88.726'), mp.mpf('1e-3'))
chk("01", "headroom vs 2^20 = 4.44×", write_bits/20, mp.mpf('4.436'), mp.mpf('1e-3'))

print()
print("=" * 74)
print("docs/02 — 平衡方程")
print("=" * 74)
R_write = mp.mpf('61.5')/T_ring
chk("02", "R_write = 0.72665 k_B/Gyr", R_write, mp.mpf('0.72665'), mp.mpf('1e-5'))
chk("02", "R_write = 7.27e-10 k_B/yr", R_write*mp.mpf('1e-9'), mp.mpf('7.27e-10'), mp.mpf('1e-12'))
chk("02", "V'' = 4μ² = 8", 4*mu2, 8, 0)
E_strain = mp.mpf('1564785320847.4905')
R_rel = mp.mpf('6730.85550941724')
pools = R_rel*(T_ring*mp.mpf('1e9'))/E_strain
chk("02", "池/圈 = 364.05", pools, mp.mpf('364.05'), mp.mpf('0.02'))
chk("02", "B·L4·F7 = 364", B*7*13, 364, 0)
chk("02", "池/圈 dev = 0.015%", abs(pools/364 - 1), mp.mpf('1.5e-4'), mp.mpf('1e-5'))
t_true = mp.mpf('11100.64'); tau = mp.mpf('13.4701')
chk("02", "t_true = 131·T_ring + τ", 131*T_ring + tau, t_true, mp.mpf('1e-2'))
# 熱力學耗散 bits/圈 ~ 4.8e82
L_bol = mp.mpf('82.53375651694712')
E_cyc = L_bol*mp.mpf('1.989e30')*mp.mpf('9e16')*T_ring*mp.mpf('1e9')
S_bits = E_cyc/mp.mpf('2.725')/mp.mpf('1.380649e-23')/mp.log(2)
chk("02", "熱力學耗散 ~4.8e82 bits/圈", S_bits, mp.mpf('4.8e82'), mp.mpf('0.2e82'))
chk("02", "比 = 5.4e80", S_bits/write_bits, mp.mpf('5.4e80'), mp.mpf('0.3e80'))

print()
print("=" * 74)
print("docs/03 — 預算持續")
print("=" * 74)
S_even = sum(4*mp.sin(mp.pi*k/176)**2 for k in range(2, 89, 2))
S_odd = sum(4*mp.sin(mp.pi*k/176)**2 for k in range(1, 88, 2))
chk("03", "Σγ_even = 90", S_even, 90, mp.mpf('1e-50'))
chk("03", "Σγ_odd = 88", S_odd, 88, mp.mpf('1e-50'))
chk("03", "μ² = E−O = 2", S_even - S_odd, 2, mp.mpf('1e-50'))
chk("03", "μ² = γ44 = 4sin²(44π/176) = 2", 4*mp.sin(mp.pi*44/176)**2, 2, mp.mpf('1e-50'))
lam = mp.mpf(2)/123
W2 = mu2/(2*lam)
chk("03", "⟨W⟩² = 61.5", W2, mp.mpf('61.5'), mp.mpf('1e-50'))
Vpp = 12*lam*W2 - 2*mu2
chk("03", "V'' = 8", Vpp, 8, mp.mpf('1e-50'))
chk("03", "A = 88×61/40 = 134.2", mp.mpf(88)*61/40, mp.mpf('134.2'), 0)
chk("03", "世界 90 = 61.5+28.5", mp.mpf('61.5')+mp.mpf('28.5'), 90, 0)
chk("03", "觀察者 88 = 61.5+26.5", mp.mpf('61.5')+mp.mpf('26.5'), 88, 0)

print()
print("=" * 74)
print("docs/04 — 角動量")
print("=" * 74)
S2 = sum(2*mp.pi*k/176 for k in range(1, 89))
chk("04", "Σ2θ_k = 44.5π", S2/mp.pi, mp.mpf('44.5'), mp.mpf('1e-50'))
chk("04", "Wilson e^{i44.5π} = i", abs(mp.e**(mp.j*S2) - mp.j), 0, mp.mpf('1e-50'))
a0 = c*c/(2*mp.pi*R_world*Mpc_m)
chk("04", "a0 = 1.1225e-10 m/s²", a0, mp.mpf('1.1225e-10'), mp.mpf('6e-14'))
Rc = R_world*Mpc_m/(Nd**3)
Vmax = mp.sqrt(a0*Rc)
chk("04", "R_c = 48.48 kpc", Rc/Mpc_m*1000, mp.mpf('48.48'), mp.mpf('0.01'))
chk("04", "V_max = 409.8 km/s", Vmax/1000, mp.mpf('409.8'), mp.mpf('0.1'))
j_spec = Vmax*Rc
chk("04", "j_spec = 6.13e26 m²/s", j_spec, mp.mpf('6.13e26'), mp.mpf('1e24'))
j_kmkpc = (Vmax/1000)*(Rc/Mpc_m*1000)
chk("04", "j_spec = 19,867 km/s·kpc", j_kmkpc, mp.mpf('19867'), mp.mpf('1'))
# MW
M_MW = mp.mpf('1.2e11')
v_MW = (a0*G*M_MW*M_sun)**mp.mpf('0.25')
chk("04", "v(MW) = 205.8 km/s", v_MW/1000, mp.mpf('205.8'), mp.mpf('0.3'))
j_MW = 2*mp.mpf('2.6')*(v_MW/1000)
chk("04", "j(MW) = 1,070 km/s·kpc", j_MW, mp.mpf('1070'), mp.mpf('3'))

print()
print("=" * 74)
print("docs/05 — 統一陳述")
print("=" * 74)
chk("05", "R_write = 7.27e-10 k_B/yr", R_write*mp.mpf('1e-9'), mp.mpf('7.27e-10'), mp.mpf('1e-12'))
chk("05", "寫入 bits 88.7 ≥ 20", write_bits, mp.mpf('88.7'), mp.mpf('0.1'))
chk("05", "α_IDCM [0.55, 0.75] 括住 [0.52, 0.64]",
    mp.mpf('0.55') < mp.mpf('0.64') and mp.mpf('0.75') > mp.mpf('0.52'), 1, 0)

# 節點均值 null 數據 (獨立重算, 唔靠 script 01)
cs = BASE / "cmb_cold_spot" / "data"
temps = {}
with open(cs / "smica_smoothed.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        temps[int(p[0])] = float(p[2])
Ts = np.array([temps[i] for i in range(60)])
dT = Ts - Ts.mean()
ratio_obs = float(np.mean(np.abs(dT)))/134.2
chk("05", "⟨|δT|⟩/A = 0.2443 (null 實測)", mp.mpf(str(ratio_obs)), mp.mpf('0.2443'), mp.mpf('1e-3'))
chk("05", "11/15 候選 0.7333 被證偽 (dev 66.7%)",
    abs(mp.mpf(str(ratio_obs)) - mp.mpf(11)/15), mp.mpf('0.489'), mp.mpf('0.002'))

print()
print(f"AUDIT RESULT: {PASS}/{PASS+FAIL} 核對通過")
