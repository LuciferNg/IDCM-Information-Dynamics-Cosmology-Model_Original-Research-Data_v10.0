#!/usr/bin/env python3
"""scratch probe: is the (c,c')-separated relaxation of the n=4 Mermin maximum tight?

M4 = A(c,d) - B(c',d) + C(c',d') - D(c,d')  with
  A(c,d)  = E4[a,b,c,d]  - E4[a',b',c,d]
  B(c',d) = E4[a',b,c',d] + E4[a,b',c',d]
  C(c',d')= E4[a',b',c',d'] - E4[a,b,c',d']
  D(c,d') = E4[a',b,c,d'] + E4[a,b',c,d']
Relaxed upper bound for fixed (a,a',b,b'):
  U = max_c[Amax(c) - Dmin(c)] + max_c'[Cmax(c') - Bmin(c')]
Relaxed lower bound:
  L = min_c[Amin(c) - Dmax(c)] + min_c'[Cmin(c') - Bmax(c')]
Compare with the exact pool maximum of |M4| (= 480 for the raw party pool).
"""
import sys

import numpy as np

SCR = ('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/'
       'open_problems_fresh/o224_amplitude_complex_phase_layer/scripts')
sys.path.insert(0, SCR)
import lib2i as L

G, idx, MUL, U, ids, types, hx, K = L.load_machine()
n, nax = len(G), len(ids)
KA = np.array(K, dtype=np.int32)
NMUL = np.array(MUL, dtype=np.int32)
hxa = np.array(hx, dtype=np.int32)

E4 = np.zeros((nax, nax, nax, nax), dtype=np.int32)
s2b = NMUL[:, hxa]
for a in range(nax):
    Aa = KA[:, a]
    s2 = s2b[:, a]
    for b in range(nax):
        s3 = NMUL[s2, hxa[b]]
        Wa = Aa * KA[s2, b]
        for c in range(nax):
            s4 = NMUL[s3, hxa[c]]
            W = Wa * KA[s3, c]
            E4[a, b, c, :] = W @ KA[s4, :]
print('E4 built; absmax =', int(np.abs(E4).max()), flush=True)

pool = [i for i, ty in enumerate(types) if ty == 'vertex']


def relaxed(space_a, space_b):
    Ubest, Lbest = None, None
    argU, argL = None, None
    for a in space_a:
        for ap in space_a:
            for b in space_b:
                for bp in space_b:
                    A1 = E4[a, b, :, :] - E4[ap, bp, :, :]        # A(c,d)
                    B1 = E4[ap, b, :, :] + E4[a, bp, :, :]        # B(c',d)
                    C1 = E4[ap, bp, :, :] - E4[a, b, :, :]        # C(c',d')
                    D1 = E4[ap, b, :, :] + E4[a, bp, :, :]        # D(c,d')
                    Amax = A1.max(axis=1)
                    Amin = A1.min(axis=1)
                    Bmax = B1.max(axis=1)
                    Bmin = B1.min(axis=1)
                    Cmax = C1.max(axis=1)
                    Cmin = C1.min(axis=1)
                    Dmax = D1.max(axis=1)
                    Dmin = D1.min(axis=1)
                    u1 = int((Amax - Dmin).max())
                    u2 = int((Cmax - Bmin).max())
                    l1 = int((Amin - Dmax).min())
                    l2 = int((Cmin - Bmax).min())
                    u = u1 + u2
                    l = l1 + l2
                    if Ubest is None or u > Ubest:
                        Ubest, argU = u, (a, ap, b, bp)
                    if Lbest is None or l < Lbest:
                        Lbest, argL = l, (a, ap, b, bp)
    return Ubest, Lbest, argU, argL


import time
for space, name in ((pool, 'pool(12)'), (list(range(nax)), 'all(62) sampled')):  # noqa
    pass
t0 = time.time()
U1, L1, au, al = relaxed(pool, pool)
t1 = time.time()
print('pool outer: U = %d/120 = %.4f ; L = %d/120 = %.4f ; |.|max bound = %d/120 = %.4f ; %.1f s'
      % (U1, U1 / 120.0, L1, L1 / 120.0, max(U1, -L1), max(U1, -L1) / 120.0, t1 - t0))
print('  argU =', au, ' argL =', al)
# rough extrapolation to the full 62^4 outer space
est = (t1 - t0) * (62.0 ** 4) / (12.0 ** 4)
print('  estimated full 62^4 outer cost: %.0f s (%.1f min)' % (est, est / 60.0))
