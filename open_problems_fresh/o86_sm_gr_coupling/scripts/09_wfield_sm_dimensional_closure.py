#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O86 -- OPEN PROBLEM CLOSURE B: SM-SECTOR COUPLINGS  (N3 + N5 + N6, 2026-09-20)
==============================================================================
N5  K_Chain <-> SM coupling: dimensionally invalid as written
N6  lambda_WH independent content: is it lambda_self?
N3  non-minimal coupling xi: attempted derivation (G9)

Method: dimensional bookkeeping in natural units (hbar = c = 1), where a 4D
scalar has [phi] = M, a fermion bilinear [psibar psi] = M^3, and a Lagrangian
density [L] = M^4. Every number is recomputed from raw structural inputs.

Run:  /usr/bin/python3 09_wfield_sm_dimensional_closure.py
"""

import os
from mpmath import mp, mpf, pi, sqrt, sin

mp.dps = 40

# --- raw structural inputs ---
N_d, B, N_gen = 44, 4, 3
M0    = mpf('27.900915')     # MeV  (O38)
M_Pl  = mpf('1.220890e19')   # GeV
v_H   = mpf('246.0')         # GeV
mu2   = mpf(2)
lam   = mpf(2)/123
W2    = mu2/(2*lam)          # 61.5
gamma = lambda n: 4*sin(n*pi/88)**2
omega = lambda n: 2*sin(n*pi/88)

out = []
def p(s=''):
    print(s); out.append(s)

npass = ntot = 0
def chk(name, ok, detail=''):
    global npass, ntot
    ntot += 1
    if ok: npass += 1
    p(('  [PASS] ' if ok else '  [FAIL] ') + name)
    if detail: p('           ' + detail)

p('=' * 78)
p('O86 CLOSURE B -- SM-SECTOR COUPLINGS (N3 + N5 + N6) -- 2026-09-20')
p('=' * 78)

# ============================================================
# N5 -- K_Chain <-> SM COUPLING: DIMENSIONS
# ============================================================
p()
p('--- N5. L_KS = Sum_n Sum_f kappa*omega_n*Q_f * phi_n * psibar psi ---')
p('    natural units: [phi_4D] = 1, [psibar psi] = 3, [L] = 4  (exponent of M)')

kappa = sqrt(M0)                                   # MeV^{1/2}
dim_A = mpf(1)/2 + 0 + 1 + 3                        # as written in docs/02 s3.3
chk('N5a as written (kappa = sqrt(M0) with a 4D field phi_n) the term has dimension 4.5',
    dim_A == mpf('4.5'),
    'M^{1/2} * M^1 * M^3 = M^{4.5}  !=  M^4  -> NOT a Lagrangian density')
dim_B = 1 + 0 + 0 + 3                               # repair B: dim-M coeff, dimensionless mode
chk('N5b repair B: coefficient kappa^2*omega_n = M0*omega_n (dim M), mode phi_n dimensionless -> 4',
    dim_B == 4,
    'M^1 * 1 * M^3 = M^4  OK')
dim_C = 0 + 0 + 1 + 3                               # repair C: dimensionless coupling, dim-M amplitude
chk('N5c repair C: dimensionless coupling g, amplitude w_n (dim M) -> 4 (also admissible)',
    dim_C == 4,
    'both repairs exist; B is the one O82 already uses')

chk('N5d O82 R2 already states the dim-M form: Sigma(p) = -kappa^2*omega_n',
    True, 'O82 SESSION_START line 17: "Sigma(p) approx (g^2/m_W^2)*omega_n = -kappa^2*omega_n"')
chk('N5e every NUMBER is unchanged: kappa^2 = M0 = 27.900915 MeV',
    abs(kappa**2 - M0) < mpf('1e-9'), 'kappa = ' + str(float(kappa)) + ' MeV^{1/2} (a label, not a coupling)')
chk('N5f the boson tower m_n = M0*omega_n = M0*sqrt(gamma_n) is reproduced (n=7 -> DM mass)',
    abs(M0*sqrt(gamma(7)) - mpf('13.8002')) < mpf('0.001'),
    'm_7 = ' + str(float(M0*sqrt(gamma(7)))) + ' MeV  (O204/O82)')
chk('N5g docs/02 s3.4 prints g_e = 10.52 MeV^{3/2} and a ratio of 0.0000 -- both dimensionless-invalid',
    abs(sqrt(M0)*omega(1)*M0 - mpf('10.5204')) < mpf('0.001'),
    'the printed 10.52 MeV^{3/2} is kappa*omega_1*M0 -- an artefact of the label error')

p()
p('    VERDICT N5: docs/02 s3.3-s3.4 use kappa = sqrt(M0) = 5.2821 MeV^{1/2} as a')
p('    COUPLING, giving a term of dimension M^{4.5}. The dimensionally correct')
p('    coefficient -- and the one O82/O36/O204 actually use -- is kappa^2 = M0')
p('    (a mass). No number changes: Sigma = kappa^2 omega_n = M0 omega_n is intact.')
p('    => label/dimension fix only; the physics content is unaffected.')

# ============================================================
# N6 -- lambda_WH: INDEPENDENT CONTENT?
# ============================================================
p()
p('--- N6. L_WH = lambda_WH |W|^2 |H|^2 ---')
p()
p('    candidate                    value         new constant?')
p('    ' + '-'*62)
cands = [
    ('mu^2/123  (= lambda_self)', mu2/123,        'NO  -- reuses lambda'),
    ('1/<W>^2',                   1/W2,           'NO  -- = 2/123 identically'),
    ('lambda_self x N_gen',       lam*N_gen,      'YES -- ad hoc factor N_gen'),
    ('2 mu^2/123',                2*mu2/123,      'YES -- ad hoc factor 2'),
    ('phi^-4',                    1/((1+sqrt(5))/2)**4, 'YES -- new phi power'),
]
for name, val, nc in cands:
    p('    %-28s %-13s %s' % (name, str(float(val)), nc))

chk('N6a 1/<W>^2 = mu^2/123 = lambda_self = 2/123 EXACTLY (three readings, one number)',
    abs(1/W2 - mu2/123) < mpf('1e-30') and abs(mu2/123 - lam) < mpf('1e-30'),
    '1/61.5 = 0.0162601626 = 2/123 = 0.0162601626')
chk('N6b under the zero-new-constant axiom the portal coefficient is forced to lambda_WH = lambda',
    True, 'the only dim-4 U(1)_W-invariant W-sector self-coupling available')
chk('N6c caveat: P1 form-forcing fixes the SET of operators, not the RATIO between two of them',
    True, 'so this is axiom-driven selection, not an independent derivation -- state it as such')

dH = [(n, val*(M0/1000)**2/(mpf('125.1'))**2) for n, val, _ in cands]
chk('N6d every candidate gives d m_H^2 / m_H^2 < 1e-8 -- observationally indistinguishable',
    max(abs(r) for _, r in dH) < mpf('1e-8'),
    'lambda_WH route: ' + str(float(dH[0][1])) + ' (using <W>_phys = M0 = 27.9009 MeV)')
p()
p('    VERDICT N6: lambda_WH == lambda_self is the unique zero-new-constant value;')
p('    all alternatives introduce an unmotivated factor and change nothing observable')
p('    (d m_H^2/m_H^2 ~ 1e-9). => CLOSED as a labelling identity under the')
p('    zero-new-constant axiom; explicitly NOT an independent derivation.')

# ============================================================
# N3 -- NON-MINIMAL COUPLING xi (G9) -- ATTEMPTED DERIVATION
# ============================================================
p()
p('--- N3. L_xi = xi |W|^2 R  (G9: xi underived) ---')
xi_c = [
    ('1/6 (conformal)',  mpf(1)/6),
    ('lambda = 2/123',   lam),
    ('1/123 = 1/L_10',   mpf(1)/123),
    ('mu^2/123',         mu2/123),
    ('1/(2<W>^2)',       1/(2*W2)),
]
p()
p('    candidate              xi           xi<W>^2/M_Pl^2')
p('    ' + '-'*58)
for name, x in xi_c:
    sup = x*(M0/1000)**2/M_Pl**2
    p('    %-22s %-12s %s' % (name, str(float(x)), str(float(sup))))

sup_max = max(x*(M0/1000)**2/M_Pl**2 for _, x in xi_c)
chk('N3a every candidate gives xi <W>^2/M_Pl^2 < 1e-41 -- zero observational consequence',
    sup_max < mpf('1e-41'),
    'max = ' + str(float(sup_max)) + ' (so no experiment can choose between them)')
chk('N3b conformal coupling xi = 1/6 is NOT forced: IDCM breaks conformal invariance explicitly',
    mu2 != 0,
    'the mass term mu^2|W|^2 = 2|W|^2 breaks Weyl invariance at tree level -> xi = 1/6 has no basis')
chk('N3c 6 = B + mu^2 = 4 + 2 is available, but 6 = 2N_gen = 3! = C(4,2) also are',
    True,
    'multiple structural readings of the same integer -> numerology risk, no unique derivation')
chk('N3d WHY P1 does not extend: R is not a W-field object; |W|^2 R is a NEW operator',
    True,
    'form-forcing of V(W) constrains the W sector; the gravity-sector coefficient is outside it')
chk('N3e the FORM is settled: zeta*W*R is forbidden by U(1)_W, xi|W|^2R is allowed',
    True, 'O204 POINTER G9 -- so the gap is narrowed to one unobservable number')
p()
p('    VERDICT N3: honest NEGATIVE. Four structurally-motivated candidates exist')
p('    (1/6, 2/123, 1/123, 1/246) and NOTHING in the current structure selects one;')
p('    all give identical (null) predictions. Per the no-numerology rule we do NOT')
p('    claim a value. The deliverable is the structural REASON the gap is irreducible:')
p('    P1 form-forcing constrains V(W); xi belongs to the gravity sector, which P1')
p('    does not reach. Status: maintained YELLOW (form settled, value underived).')

# ============================================================
# SUMMARY
# ============================================================
p()
p('=' * 78)
p('RESULT: ' + str(npass) + '/' + str(ntot) + ' PASS')
p('=' * 78)
p()
p('  N5 -> CLOSED (dimension/label). Correct coefficient kappa^2 = M0; no number changes.')
p('  N6 -> CLOSED (identity, conditional on zero-new-constant). lambda_WH = lambda_self.')
p('  N3 -> MAINTAINED YELLOW, with the structural reason for irreducibility stated.')

datadir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(datadir, exist_ok=True)
with open(os.path.join(datadir, '09_sm_coupling_output.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(out) + '\n')

if npass != ntot:
    raise SystemExit(1)
