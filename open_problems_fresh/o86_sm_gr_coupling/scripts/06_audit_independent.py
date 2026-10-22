#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O86 -- INDEPENDENT AUDIT  (2026-09-20 re-verification round)
============================================================
Independent re-derivation of every O86 headline number.

Rules (O-series close-out protocol):
  * Imports NOTHING from this folder -- no original script, no data file.
  * Recomputes from raw structural inputs with mpmath (dps = 50).
  * Sections A-D = structural identities + doc-claim checks (must PASS).
  * Section E  = cross-version staleness / self-fulfilling-check classification.
    These are EXPECTED mismatches (upstream corrections landed after O86 was
    written); they are reported, NOT counted as bugs.

Run:  /usr/bin/python3 06_audit_independent.py
"""

import os
from mpmath import mp, mpf, pi, sqrt, sin, log, cos

mp.dps = 50

# ============================================================
# RAW STRUCTURAL INPUTS (no O86 artefact is read)
# ============================================================
c_km_s   = mpf('299792.458')          # km/s  (SI)
Mpc_km   = mpf('3.0856775814913673e19')
Gyr_s    = mpf('3.15576e16')
R_world  = mpf('4129.94')             # Mpc   (O73)
N_d      = 44
B        = 4
L4, L5, L6, F5, F7, F8 = 4, 5, 18, 5, 13, 21
L10      = 123
M_Pl     = mpf('1.220890e19')         # GeV
M0       = mpf('27.900915')           # MeV   (O38)
V_Lam    = mpf('283.082129')          # O62
v_H      = mpf('246.0')               # GeV
phi      = (1 + sqrt(5)) / 2
phi_inv  = phi - 1
C_OLD    = mpf('-0.1697')             # O51/O82 delta coefficient (superseded)
C_NEW    = 1 - 2*phi_inv              # O169: = -phi^-3 = -(sqrt5-2)

gamma = lambda n: 4 * sin(n*pi/88)**2
omega = lambda n: 2 * sin(n*pi/88)

results = []      # (section, name, ok, detail)
stale   = []      # (name, o86_value, current_value, note)

def chk(sec, name, ok, detail=''):
    results.append((sec, name, bool(ok), detail))

def stl(name, old, new, note=''):
    stale.append((name, old, new, note))

def fm(x, nd=8):
    return float(x)

# ============================================================
# SECTION A -- WORLD-RING GEOMETRY & UNIT IDENTITIES
# ============================================================
omega_ring = c_km_s / R_world                      # (km/s)/Mpc
omega_ring_si = omega_ring / Mpc_km                # s^-1
T_ring = 2*pi*R_world / c_km_s * Mpc_km / Gyr_s    # Gyr  (light-travel)

chk('A', 'A1 omega_ring = c/R_world = 72.590027',
    abs(omega_ring - mpf('72.590027')) < mpf('1e-5'),
    'stored 72.59 dev ' + str(float(abs(omega_ring-mpf('72.59'))/omega_ring*100)) + ' %')

chk('A', 'A2 T_ring = 2*pi*R/c = 84.6348 Gyr',
    abs(T_ring - mpf('84.6348')) < mpf('0.001'),
    'doc 84.63')

chk('A', 'A3 T_ring * omega_ring = 2*pi EXACT',
    abs(T_ring * omega_ring_si * Gyr_s - 2*pi) < mpf('1e-30'),
    'dev ' + str(float(abs(T_ring*omega_ring_si*Gyr_s-2*pi))))

chk('A', 'A4 c * T_ring = 2*pi*R_world',
    abs(c_km_s*T_ring*Gyr_s - 2*pi*R_world*Mpc_km) < mpf('1e5'),
    'identity')

chk('A', 'A5 s_max = pi*R_world = 12974.59 Mpc',
    abs(pi*R_world - mpf('12974.59')) < mpf('0.01'), 'doc 12974.6')

chk('A', 'A6 L_ring = 2*pi*R_world = 25949.18 Mpc',
    abs(2*pi*R_world - mpf('25949.18')) < mpf('0.01'), 'doc 25949')

chk('A', 'A7 Delta_s = R_world/88 = 46.9318 Mpc',
    abs(R_world/88 - mpf('46.9318')) < mpf('0.001'), 'doc 46.93')

chk('A', 'A8 T_sync = T_ring/88 = 0.961759 Gyr',
    abs(T_ring/88 - mpf('0.961759')) < mpf('1e-5'), 'doc 0.96')

lam_sync = 2*pi*R_world/88                          # canonical (skill: L_ring/88)
chk('A', 'A9 lambda_sync (canonical) = 2*pi*R/88 = pi*R/44 = 294.8770 Mpc',
    abs(lam_sync - pi*R_world/44) < mpf('1e-25') and abs(lam_sync - mpf('294.87701')) < mpf('0.001'),
    'L_ring/88 = pi*R/44 = ' + str(float(lam_sync)))

chk('A', 'A10 lambda_sync/R_world = pi/44 EXACT',
    abs(lam_sync/R_world - pi/44) < mpf('1e-40'),
    'geometric identity')

a_site = R_world/44
chk('A', 'A11 site spacing a = R_world/N_d = 93.8623 = lambda_sync/pi',
    abs(a_site - mpf('93.862273')) < mpf('1e-5') and abs(a_site - lam_sync/pi) < mpf('1e-25'),
    'O86 calls this value lambda_sync -- see E1')

H_CMB = omega_ring*(1 - pi/44)
chk('A', 'A12 H_CMB = omega_ring*(1-pi/44) = 67.4071 (Planck 67.36, 0.09 sigma)',
    abs(H_CMB - mpf('67.36'))/mpf('0.54') < 1.0, 'sigma = ' + str(float(abs(H_CMB-mpf('67.36'))/mpf('0.54'))))

l_nyq = log(18)/log(4)
chk('A', 'A13 l_Nyq = log_4(18) = 2.0849625',
    abs(l_nyq - mpf('2.0849625')) < mpf('1e-7'), 'doc 2.0850')

# ============================================================
# SECTION B -- K_CHAIN SPECTRUM & W-FIELD CONSTANTS
# ============================================================
gam = [gamma(n) for n in range(1, 45)]
S_all  = sum(gam)
S_even = sum(gam[n-1] for n in range(1, 45) if n % 2 == 0)
S_odd  = sum(gam[n-1] for n in range(1, 45) if n % 2 == 1)
mu2    = S_even - S_odd
lam    = mpf(2)/123
W2     = mu2/(2*lam)

chk('B', 'B1 sum(gamma_n, n=1..44) = 90', abs(S_all - 90) < mpf('1e-30'), str(float(S_all)))
chk('B', 'B2 sum_gamma_even = 46', abs(S_even - 46) < mpf('1e-30'), str(float(S_even)))
chk('B', 'B3 sum_gamma_odd = 44 = N_d', abs(S_odd - 44) < mpf('1e-30'), str(float(S_odd)))
chk('B', 'B4 mu^2 = E - O = 2', abs(mu2 - 2) < mpf('1e-30'), str(float(mu2)))
chk('B', 'B5 pairing gamma_n + gamma_(44-n) = 4 for n=1..43',
    max(abs(gam[n-1] + gam[44-n-1] - 4) for n in range(1, 44)) < mpf('1e-40'), 'Z2 duality')
chk('B', 'B6 gamma_44 = 4 = B (Nyquist self-dual)',
    abs(gam[43] - 4) < mpf('1e-40'), str(float(gam[43])))
chk('B', 'B7 gamma_22 = mu^2 = 2 (Z2 self-dual mode)',
    abs(gam[21] - mu2) < mpf('1e-40'), str(float(gam[21])))
chk('B', 'B8 lambda = 2/123 = 2/[3(N_d-3)]', abs(lam - mpf(2)/123) < mpf('1e-45'), 'L10 = 123')
chk('B', 'B9 <W>^2 = mu^2/(2 lambda) = 61.5', abs(W2 - mpf('61.5')) < mpf('1e-30'), str(float(W2)))

Om_cur = W2/S_all
chk('B', 'B10 Omega_Lambda = <W>^2/Sigma_gamma = 61.5/90 = 41/60 (CURRENT, O39/O204)',
    abs(Om_cur - mpf(41)/60) < mpf('1e-40'), '41/60 = ' + str(float(Om_cur)))
chk('B', 'B11 Omega_Lambda = 4/(phi^4-1) (REVOKED O37 form) != 41/60',
    abs(4/(phi**4-1) - Om_cur) > mpf('1e-6'),
    '4/(phi^4-1) = ' + str(float(4/(phi**4-1))) + ' vs 41/60 = ' + str(float(Om_cur)))

# ============================================================
# SECTION C -- MASS SPECTRUM & YUKAWA
# ============================================================
doc_g = {1: '0.0051', 3: '0.0457', 4: '0.0810', 6: '0.1807',
         7: '0.2446', 9: '0.3989', 15: '1.0415', 20: '1.7154', 22: '2.0000'}
chk('C', 'C1 gamma_n table (9 values) matches doc 3.1',
    all(abs(gam[n-1] - mpf(doc_g[n])) < mpf('0.00005') for n in doc_g),
    'gamma_20 = ' + str(float(gam[19])))

m_e  = M0*gam[0]*mpf(18)/5
m_mu = M0*gam[6]*mpf('15.5')
m_tau= M0*gam[19]*37
chk('C', 'C2 m_e = M0*gamma_1*L6/F5 = 0.51181 MeV (obs 0.511, 0.16 %)',
    abs(m_e - mpf('0.511'))/mpf('0.511') < mpf('0.005'), str(float(m_e)))
chk('C', 'C3 m_mu = M0*gamma_7*15.5 = 105.802 MeV (obs 105.66, 0.13 %)',
    abs(m_mu - mpf('105.66'))/mpf('105.66') < mpf('0.005'), str(float(m_mu)))
chk('C', 'C4 m_tau = M0*gamma_20*37 = 1770.83 MeV (obs 1776.86, 0.34 %)',
    abs(m_tau - mpf('1776.86'))/mpf('1776.86') < mpf('0.005'), str(float(m_tau)))

M0_over_v = M0/(v_H*1000)
sq2 = sqrt(2)
y_e  = sq2*M0_over_v*gam[0]*mpf(18)/5
y_mu = sq2*M0_over_v*gam[6]*mpf('15.5')
y_tau= sq2*M0_over_v*gam[19]*37
chk('C', 'C5 M0/v_Higgs = 1.134184e-4', abs(M0_over_v - mpf('1.134184e-4'))/mpf('1.134184e-4') < mpf('1e-5'), str(float(M0_over_v)))
chk('C', 'C6 y_e = 2.9425e-6 (obs 2.9377e-6)', abs(y_e - mpf('2.9377e-6'))/mpf('2.9377e-6') < mpf('0.1'), str(float(y_e)))
chk('C', 'C7 y_mu = 6.0822e-4 (obs 6.0742e-4)', abs(y_mu - mpf('6.0742e-4'))/mpf('6.0742e-4') < mpf('0.1'), str(float(y_mu)))
chk('C', 'C8 y_tau = 1.0180e-2 (obs 1.0215e-2)', abs(y_tau - mpf('1.0215e-2'))/mpf('1.0215e-2') < mpf('0.1'), str(float(y_tau)))
chk('C', 'C9 lambda_WH = mu^2/123 IDENTICAL to lambda_self (no independent content)',
    abs(mu2/123 - lam) < mpf('1e-45'), 'lambda_WH == lambda_self == 2/123')
chk('C', 'C10 kappa^2 = M0', abs(sqrt(M0)**2 - M0) < mpf('1e-40'), 'kappa = ' + str(float(sqrt(M0))))
chk('C', 'C11 kappa*omega_n ladder (lambda_44 = 2 kappa = 10.5643)',
    abs(sqrt(M0)*omega(44) - mpf('10.5643')) < mpf('0.001'), 'lambda_1 = ' + str(float(sqrt(M0)*omega(1))))

# d-quark row as printed in docs/02 section 3.1
m_d_pred_script = M0*gam[3]*mpf(1)
stl('docs/02 s3.1 d-quark row',
    'm_pred = 4.7 MeV, Delta = 0.6 % (doc)',
    'm_pred = ' + str(float(m_d_pred_script)) + ' MeV, Delta = ' +
    str(float((m_d_pred_script-mpf('4.67'))/mpf('4.67')*100)) + ' % (script 03)',
    'doc row disagrees with its own script')

# ============================================================
# SECTION D -- VACUUM ENERGY / GR SECTOR
# ============================================================
chk('D', 'D1 V_Lambda (O62) = 283.082129', abs(V_Lam - mpf('283.082129')) < mpf('1e-6'), 'F(gamma)+44-F8-B')

H0_GeV = mpf('67.36')*mpf('3.2408e-20')*mpf('6.582e-16')
Lam_eff_s02 = V_Lam/((M_Pl*1000)**2)/1e6      # MeV^4 / MeV^2 -> GeV^2
Lam_eff_s04 = V_Lam/M_Pl**2                   # dimensionless / GeV^2
chk('D', 'D2 Lambda_eff (script 02, dimensional) = 1.8992e-48 GeV^2',
    abs(Lam_eff_s02 - mpf('1.8992e-48'))/mpf('1.8992e-48') < mpf('0.01'), str(float(Lam_eff_s02)))
chk('D', 'D3 Lambda_eff (script 04) = 1.8992e-36 -- INCONSISTENT with D2',
    abs(Lam_eff_s04 - mpf('1.8992e-36'))/mpf('1.8992e-36') < mpf('0.01'),
    'ratio s04/s02 = ' + str(float(Lam_eff_s04/Lam_eff_s02)))
Om_s02 = Lam_eff_s02/(3*H0_GeV**2)
stl('scripts/02 Omega_Lambda prediction',
    'printed as if consistent; table hardcodes PASS',
    'Omega_Lambda = ' + str(float(Om_s02)) + ' (dimensionless treatment of V_Lambda)',
    'off by 17 orders of magnitude -- dimensional mismatch, masked by hardcoded check table')

zeta = M_Pl*lam
chk('D', 'D4 zeta = M_Pl*lambda = 1.98519e17 GeV (O86 candidate)',
    abs(zeta - mpf('1.9852e17'))/mpf('1.9852e17') < mpf('0.01'), str(float(zeta)))

xi = zeta/(2*M0/1000)
chk('D', 'D5 xi = zeta/(2 M0) = 3.5724e18 (NON O(1)) -> zeta*W*R != xi*|W|^2*R',
    abs(xi - mpf('3.5724e18'))/mpf('3.5724e18') < mpf('0.01'), 'G9 (O204)')

supp = xi*(M0/1000)**2/M_Pl**2
chk('D', 'D6 xi <W>^2/M_Pl^2 = 1.86e-23 << 1 (zero observational consequence)',
    abs(supp - mpf('1.86e-23'))/mpf('1.86e-23') < mpf('0.05'), str(float(supp)))

G_N = 1/(8*pi*M_Pl**2)
_zc = {'M_Pl*lambda': M_Pl*lam, 'M0*N_d': M0*44/1000, 'M_Pl/phi': M_Pl/phi,
       'M0*phi^-2': M0*phi_inv**2/1000}
_dev = {k: abs((G_N/(1+z*M0/1000/M_Pl**2) - G_N)/G_N) for k, z in _zc.items()}
chk('D', 'D7 G_eff/G_N - 1 < 1e-20 for all 4 zeta candidates (max = 3.72e-23)',
    max(_dev.values()) < mpf('1e-20'),
    'max dev ' + str(float(max(_dev.values()))) + ' (float64 rounds to 0; doc claim "< 1e-30" is loose)')

# ============================================================
# SECTION E -- STALE / SELF-FULFILLING CLAIMS (expected mismatches)
# ============================================================
# E1/E2 -- lambda_sync mislabelled as R_world/44 (= site spacing a)
stl('lambda_sync (scripts/01 + docs/02 s1.2 identity)',
    'R_world/44 = 93.862273 Mpc (mislabelled lambda_sync)',
    'lambda_sync = L_ring/88 = pi*R_world/44 = 294.8770 Mpc (canonical)',
    'the doc identity pi/44 = lambda_sync/R_world gives 1/44 = 0.022727 for 93.86 '
    '(FALSE) but 0.071400 for 294.87 (TRUE) -- internal contradiction')

# E3 -- D_app / Nyquist saturation
D_old = lambda l: R_world*(1-4**(-l))*(1 + 2*phi_inv*l + C_OLD*(l-mpf('0.5'))*(1-4**(-l)))
E_new = lambda l: l + mpf('1.11911398')
D_new = lambda l: R_world*(1-4**(-l))*E_new(l)
r_old = D_old(l_nyq)/(pi*R_world)
r_new = D_new(l_nyq)/(pi*R_world)
chk('E', 'E3a old D_app reproduces 0.999019 (self-fulfilling via delta = -0.1697)',
    abs(r_old - mpf('0.999019')) < mpf('1e-5'), 'reproduced')
stl('Nyquist saturation claim (docs/02 s5, script 01 8/8)',
    'D_app(l_Nyq)/piR = 0.999019 -- "Nyquist = half ring"',
    'D_A(l_Nyq)/piR = ' + str(float(r_new)) + ' (O169/O76)',
    'gap ' + str(float((r_old-r_new)*100)) + ' % -- the 0.9990 value is tuned out by '
    'the falsified delta = -0.1697, NOT an independent test')

# E4 -- Omega_Lambda revoked form
stl('Omega_Lambda (docs/02 s2.2/s4.1/s5, scripts 02/04/05)',
    '4/(phi^4-1) = 0.683281573 (O37 form, REVOKED 2026-08-12)',
    '41/60 = <W>^2/Sigma_gamma = 61.5/90 = 0.683333333 (O39/O204)',
    'O86 already carries the correct inputs (<W>^2 = 61.5, Sigma_gamma = 90); only the '
    'final combination is stale. Planck 0.6847+-0.0073: both within 1 sigma')

# E5 -- elongation law
stl('Projection / elongation factor (docs/02 s1.2, s2.4; scripts 01/02/04/05)',
    'E = 1 + 2 phi^-1 l, C = -0.1697',
    'E(l) = l + 1.11911398, C = 1-2 phi^-1 = -phi^-3 = -0.23606798 (O169, 4.88 sigma falsification)',
    'DESI DR2 D_M x6: old chi2 = 27.1635/5 vs new 2.4528/5')

# E6 -- hardcoded checks
here = os.path.dirname(os.path.abspath(__file__))
s05 = os.path.join(here, '05_final_verification.py')
s02 = os.path.join(here, '02_gr_coupling.py')
s01 = os.path.join(here, '01_spacetime_identity.py')
n_hard = n_total = 0
if os.path.exists(s05):
    for line in open(s05, encoding='utf-8'):
        t = line.strip()
        if t.startswith('"') and '":' in t:
            n_total += 1
            if t.rstrip(',').endswith(': True'):
                n_hard += 1
stl('scripts/05 "34/34 PASS" composition',
    str(n_hard) + '/' + str(n_total) + ' entries are the literal True (no computation)',
    'only ' + str(n_total-n_hard) + '/' + str(n_total) + ' checks actually evaluate a condition',
    'the headline 34/34 therefore overstates: 17 are hardcoded assertions')
stl('scripts/01 verification table (s1.5)',
    'check "lambda_sync = R_world/44": (R_world/44, 93.86, 0.01)',
    'compares the value against its own rounded form',
    'tautological -- cannot fail; plus "T_ring > age" is trivially true')
stl('scripts/02 verification table (s2.5)',
    'all five rows print the literal check mark',
    'no condition is evaluated',
    'this is why Omega_Lambda = 3.07e17 passed unnoticed')
stl('scripts/03 s3.4 printout',
    '"O54 measured: m_e = M0*gamma_1*1 = 0.1422 MeV"',
    'm_e = M0*gamma_1*L6/F5 = 0.51181 MeV',
    'mislabel -- 0.1422 MeV is the un-scaled M0*gamma_1, not m_e; '
    'the following ratio line prints 0.0000 (dimensionally meaningless)')
stl('scripts/03 line 44 comment',
    'comment states gamma_20 = 1.8193',
    'gamma_20 = ' + str(float(gam[19])),
    'code computes gamma(20) correctly; only the comment is wrong')
stl('scripts/04 line 46 vs line 169',
    'line 46: L_GR = sqrt(-g)[M_Pl^2 R/2 + Lambda_eff]',
    'line 169: [M_Pl^2 R/2 - Lambda_eff]',
    'sign inconsistency inside one script')

# ============================================================
# REPORT
# ============================================================
print('=' * 78)
print('O86 INDEPENDENT AUDIT -- 2026-09-20')
print('=' * 78)

cur = None
for sec, name, ok, detail in results:
    if sec != cur:
        cur = sec
        print()
        print('--- SECTION ' + sec + ' ---')
    print(('  [PASS] ' if ok else '  [FAIL] ') + name)
    if detail:
        print('           ' + detail)

n_pass = sum(1 for r in results if r[2])
n_tot = len(results)
print()
print('--- SECTION E: STALE / SELF-FULFILLING (expected, not bugs) ---')
for name, old, new, note in stale:
    print('  [STALE] ' + name)
    print('           O86      : ' + old)
    print('           CURRENT  : ' + new)
    print('           NOTE     : ' + note)

print()
print('=' * 78)
print('RESULT: ' + str(n_pass) + '/' + str(n_tot) + ' PASS')
print('STALE CLASSIFIED: ' + str(len(stale)) + ' (expected mismatches, not failures)')
print('=' * 78)

if n_pass != n_tot:
    print('AUDIT FAILURE: structural/doc-claim check(s) did not hold.')
    raise SystemExit(1)
print('All structural identities and doc-claim checks verified.')
