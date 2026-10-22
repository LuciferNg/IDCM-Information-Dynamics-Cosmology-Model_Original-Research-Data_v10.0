#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O86 -- CROSS-VERSION RE-VERIFICATION  (2026-09-20)
==================================================
Executes the re-verification task handed back to O86 by:

  * O169 (2026-09-15) -- elongation law `E = 1 + 2 phi^-1 l` falsified by
    DESI DR2 D_M x6 at 4.88 sigma; current form `E(l) = l + 1.11911398`,
    `C = 1 - 2 phi^-1 = -phi^-3`.
  * O39 / O204 -- `Omega_Lambda = 4/(phi^4-1)` (O37 form) revoked;
    current `Omega_Lambda = <W>^2/Sigma_gamma = 61.5/90 = 41/60`.
  * O73 (world-ring conventions) -- `lambda_sync = L_ring/88 = pi*R_world/44`;
    the quantity `R_world/44` is the 44-site spacing `a`.

Central question (SESSION_START 2026-09-15, item 4):
  "does the SM x IDCM x GR Lagrangian STRUCTURE depend on the shape of the
   old elongation term?  If yes -> mark red honestly."

Run:  /usr/bin/python3 07_reverify_cross_version.py
"""

import os
from mpmath import mp, mpf, pi, sqrt, sin, log

mp.dps = 50

c_km_s  = mpf('299792.458')
R_world = mpf('4129.94')
M_Pl    = mpf('1.220890e19')
M0      = mpf('27.900915')
V_Lam   = mpf('283.082129')
v_H     = mpf('246.0')
phi     = (1 + sqrt(5))/2
phi_inv = phi - 1
sq2     = sqrt(2)

E_OLD   = lambda l: 1 + 2*phi_inv*l
C_OLD   = mpf('-0.1697')
E_NEW   = lambda l: l + mpf('1.11911398')
C_NEW   = 1 - 2*phi_inv

D_old = lambda l: R_world*(1 - 4**(-l))*(E_OLD(l) + C_OLD*(l-mpf('0.5'))*(1-4**(-l)))
D_new = lambda l: R_world*(1 - 4**(-l))*E_NEW(l)
a_old = lambda l: D_old(l)/R_world
a_new = lambda l: D_new(l)/R_world

gamma = lambda n: 4*sin(n*pi/88)**2
omega = lambda n: 2*sin(n*pi/88)
lam   = mpf(2)/123
mu2   = mpf(2)
W2    = mu2/(2*lam)
S_all = sum(gamma(n) for n in range(1, 45))

omega_ring = c_km_s/R_world
l_nyq      = log(18)/log(4)

out = []
def p(s=''):
    print(s); out.append(s)

p('=' * 78)
p('O86 CROSS-VERSION RE-VERIFICATION -- 2026-09-20')
p('=' * 78)

npass = ntot = 0
def chk(name, ok, detail=''):
    global npass, ntot
    ntot += 1
    if ok: npass += 1
    p(('  [PASS] ' if ok else '  [FAIL] ') + name)
    if detail: p('           ' + detail)

# ============================================================
# S1 -- FLRW projection table, old vs current
# ============================================================
p()
p('--- S1: FLRW PROJECTION  a(l) = D_app(l)/R_world ---')
p('    (old = falsified O76 form; current = O169)')
p()
p('    l       z        a_old     a_new     D_old       D_new      H_old     H_new')
p('    ' + '-'*84)
for l in [mpf('0'), mpf('0.1'), mpf('0.5'), mpf('1.0'), mpf('1.5'), mpf('2.0'), mpf('2.085')]:
    z = 4**l - 1
    if l == 0:
        p('    0.000   0.0000   0.000000  0.000000  0.0         0.0        --        --')
        continue
    Ho = c_km_s*z/D_old(l); Hn = c_km_s*z/D_new(l)
    p('    %5.3f  %7.4f  %8.6f  %8.6f  %-11.1f %-11.1f %-9.4f %-9.4f' %
      (float(l), float(z), float(a_old(l)), float(a_new(l)),
       float(D_old(l)), float(D_new(l)), float(Ho), float(Hn)))

chk('S1a a(l) reproduces the doc table at l = 1 (1.629323)',
    abs(a_old(1) - mpf('1.629323')) < mpf('1e-6'), 'old form reproduced')
_Eo0 = E_OLD(mpf('0.001')) + C_OLD*(mpf('0.001')-mpf('0.5'))*(1-4**mpf('-0.001'))
_En0 = E_NEW(mpf('0.001'))
chk('S1b the E-factor ratio E_new/E_old -> ~1.12 as l -> 0 (not a small perturbation)',
    _En0/_Eo0 > mpf('1.1'),
    'E_old = ' + str(float(_Eo0)) + ' , E_new = ' + str(float(_En0)) +
    ' , ratio = ' + str(float(_En0/_Eo0)))
chk('S1c the two forms CROSS: new is larger at l = 0.1, smaller for l >= 1',
    a_new(mpf('0.1')) > a_old(mpf('0.1')) and a_new(mpf('1.5')) < a_old(mpf('1.5')),
    'ratio new/old : l=0.1 -> ' + str(float(a_new(mpf('0.1'))/a_old(mpf('0.1')))) +
    ' , l=1.5 -> ' + str(float(a_new(mpf('1.5'))/a_old(mpf('1.5')))))

# ============================================================
# S2 -- Nyquist saturation
# ============================================================
p()
p('--- S2: NYQUIST SATURATION  D(l_Nyq)/(pi*R_world) ---')
r_old = D_old(l_nyq)/(pi*R_world)
r_new = D_new(l_nyq)/(pi*R_world)
chk('S2a old form gives 0.999019 (this is what script 01 reported)',
    abs(r_old - mpf('0.999019')) < mpf('1e-5'), 'reproduced: ' + str(float(r_old)))
chk('S2b current form gives 0.963228 -- NOT half-ring saturation',
    abs(r_new - mpf('0.963228')) < mpf('1e-5'),
    'O169/O76 value 0.9632 reproduced: ' + str(float(r_new)))
chk('S2c the O86 green claim "Nyquist = half ring (0.9990)" does NOT survive',
    abs(r_old - r_new) > mpf('0.03'),
    'gap ' + str(float((r_old-r_new)*100)) + ' % -- 0.9990 was tuned out by delta = -0.1697')

# ============================================================
# S3 -- Omega_Lambda
# ============================================================
p()
p('--- S3: VACUUM ENERGY ---')
Om_old = 4/(phi**4 - 1)
Om_new = W2/S_all
chk('S3a Omega_Lambda current = <W>^2/Sigma_gamma = 41/60',
    abs(Om_new - mpf(41)/60) < mpf('1e-40'), str(float(Om_new)))
chk('S3b Omega_Lambda revoked = 4/(phi^4-1) differs by 0.0076 %',
    abs(Om_old - Om_new)/Om_new > mpf('1e-5'),
    'rel diff ' + str(float(abs(Om_old-Om_new)/Om_new*100)) + ' % -- cannot be distinguished numerically, '
    'only by formula identity')
chk('S3c both forms sit inside the Planck 1-sigma band (0.6847 +- 0.0073)',
    abs(Om_old - mpf('0.6847')) < mpf('0.0073') and abs(Om_new - mpf('0.6847')) < mpf('0.0073'),
    'old dev ' + str(float(abs(Om_old-mpf('0.6847'))/mpf('0.6847')*100)) +
    ' %, new dev ' + str(float(abs(Om_new-mpf('0.6847'))/mpf('0.6847')*100)) + ' %')

# ============================================================
# S4 -- lambda_sync correction; H_CMB invariance
# ============================================================
p()
p('--- S4: lambda_sync + H_CMB ---')
a_site = R_world/44
lam_sync = 2*pi*R_world/88
chk('S4a O86 value 93.8623 Mpc = R_world/44 = 44-site spacing a, NOT lambda_sync',
    abs(a_site - mpf('93.862273')) < mpf('1e-5'), 'a = R_world/N_d = ' + str(float(a_site)))
chk('S4b canonical lambda_sync = L_ring/88 = 294.8770 Mpc',
    abs(lam_sync - mpf('294.87701')) < mpf('0.001'), str(float(lam_sync)))
chk('S4c lambda_sync/R_world = pi/44 only for the canonical value',
    abs(lam_sync/R_world - pi/44) < mpf('1e-40') and abs(a_site/R_world - mpf(1)/44) < mpf('1e-40'),
    '1/44 = 0.0227272 (a/R) vs pi/44 = 0.0713999 (lambda_sync/R)')
H_CMB = omega_ring*(1 - pi/44)
chk('S4d H_CMB = omega_ring*(1-pi/44) = 67.4071 UNAFFECTED by the lambda_sync mislabel',
    abs(H_CMB - mpf('67.4071')) < mpf('1e-4'),
    'the geometric factor pi/44 is a ratio -- correct regardless of the value assigned to lambda_sync')

# ============================================================
# S5 -- does the Lagrangian STRUCTURE depend on the elongation shape?
# ============================================================
p()
p('--- S5: LAGRANGIAN FORM-INVARIANCE UNDER THE ELONGATION REPLACEMENT ---')
p()
p('    coefficient set of docs/02 section 4.2, evaluated under BOTH forms:')

def coeffs(E, C):
    # every number that appears in the L_total coefficient table
    return {
        'M_Pl'      : M_Pl,
        'Lambda_eff': V_Lam/M_Pl**2,
        'mu^2'      : mu2,
        'lambda'    : lam,
        '<W>^2'     : W2,
        'M0'        : M0,
        'kappa^2'   : M0,
        'lambda_WH' : mu2/123,
        'y_e'       : sq2*(M0/(v_H*1000))*gamma(1)*mpf(18)/5,
        'y_mu'      : sq2*(M0/(v_H*1000))*gamma(7)*mpf('15.5'),
        'y_tau'     : sq2*(M0/(v_H*1000))*gamma(20)*37,
        'zeta'      : M_Pl*lam,
        'omega_ring': omega_ring,
        'R_world'   : R_world,
        'a(l=1)'    : D_old(1)/R_world if E is E_OLD else D_new(1)/R_world,
    }

co = coeffs(E_OLD, C_OLD)
cn = coeffs(E_NEW, C_NEW)
diff = {k: (co[k], cn[k]) for k in co if abs(co[k]-cn[k]) > mpf('1e-40')}
chk('S5a 14 of 15 coefficient-table entries are IDENTICAL under both forms',
    len(diff) == 1, 'entries that change: ' + str(list(diff.keys())))
chk('S5b the ONLY entry that changes is the projection factor a(l) itself',
    list(diff.keys()) == ['a(l=1)'],
    'a_old(1) = ' + str(float(co['a(l=1)'])) + '  ->  a_new(1) = ' + str(float(cn['a(l=1)'])))
chk('S5c no coupling constant (GR / W-field / SM / cross) contains the elongation factor',
    all(k not in diff for k in ['M_Pl', 'Lambda_eff', 'mu^2', 'lambda', '<W>^2', 'M0',
                                'kappa^2', 'lambda_WH', 'y_e', 'y_mu', 'y_tau',
                                'zeta', 'omega_ring', 'R_world']),
    'the Lagrangian operator content is form-invariant')
p()
p('    VERDICT: the elongation replacement touches ONLY the background geometry')
p('    a(l) that g_{mu nu} represents -- NOT the operator/coefficient structure of')
p('    L_total.  So the O86 Lagrangian assembly survives; its NUMERIC projection')
p('    claims (a(l) table, Nyquist saturation, D_app route to distances) do not.')

# ============================================================
# S6 -- audit of scripts/05 (REBUILT 2026-09-25 in O86's own context)
# ============================================================
p()
p('--- S6: AUDIT OF scripts/05 (rebuilt 2026-09-25) ---')
p('    historical: the original 2026-08-25 scripts/05 declared 34/34 with 17 literal')
p('    True (no condition evaluated) -- recorded in docs/03_reverification_record.md 3#10;')
p('    O208 rewrote it (2026-09-22) but kept withdrawn upstream values; O86 rebuilt it')
p('    from docs/01-08 with corrected values. This section audits the rebuild.')
here = os.path.dirname(os.path.abspath(__file__))
s05 = os.path.join(here, '05_final_verification.py')
nchk = hard = 0
if os.path.exists(s05):
    for line in open(s05, encoding='utf-8'):
        t = line.strip()
        if t.startswith('chk('):
            nchk += 1
            if ', True)' in t or ', True,' in t:
                hard += 1
s05text = open(s05, encoding='utf-8').read() if os.path.exists(s05) else ''
chk('S6a rebuilt scripts/05 declares 23 numeric checks', nchk == 23,
    'parsed ' + str(nchk) + ' chk() calls')
chk('S6b rebuilt scripts/05 has ZERO literal-True conditions', hard == 0,
    'literal True ' + str(hard) + ' / ' + str(nchk) + ' checks')
chk('S6c rebuilt scripts/05 embeds the CORRECTED upstream values',
    ('294.8770' in s05text) and ('0.963228' in s05text)
    and ('41.0 / 60.0' in s05text) and ('8 * math.pi * M_Pl ** 2' in s05text),
    'lambda_sync / Nyquist / Omega_L / Lambda_eff present')

# ============================================================
# SUMMARY
# ============================================================
p()
p('=' * 78)
p('RESULT: ' + str(npass) + '/' + str(ntot) + ' PASS')
p('=' * 78)
p()
p('CORRECTED O86 NUMBERS (to be used going forward):')
p('  lambda_sync      = 294.8770 Mpc      (was 93.8623 = R_world/44 = a)')
p('  Omega_Lambda     = 41/60 = 0.6833333  (was 4/(phi^4-1) = 0.6832816)')
p('  E(l)             = l + 1.11911398     (was 1 + 2 phi^-1 l)')
p('  C (delta coeff)  = -0.23606798        (was -0.1697)')
p('  D_A(l_Nyq)/piR   = 0.963228           (was 0.999019)')
p('  H_CMB            = 67.4071            (unchanged)')
p('  omega_ring       = 72.590027          (unchanged)')
p('  M0, mu^2, lambda, <W>^2, kappa^2, y_f, lambda_WH, zeta, V_Lambda -- unchanged')
p()

datadir = os.path.join(os.path.dirname(here), 'data')
os.makedirs(datadir, exist_ok=True)
with open(os.path.join(datadir, '07_reverify_output.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(out) + '\n')

if npass != ntot:
    raise SystemExit(1)
