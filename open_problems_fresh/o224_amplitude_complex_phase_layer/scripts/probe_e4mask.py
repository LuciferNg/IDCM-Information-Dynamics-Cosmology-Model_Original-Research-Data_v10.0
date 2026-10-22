#!/usr/bin/env python3
"""scratch probe: masked maxima of |E4| under window constraints (round-3 planning)."""
import os
import sys

import numpy as np

SCR = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o224_amplitude_complex_phase_layer/scripts'
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
print('E4 built, absmax =', int(np.abs(E4).max()))

# index grids
i4 = np.arange(nax)
A, B, C, D = np.meshgrid(i4, i4, i4, i4, indexing='ij')
all_distinct = (A != B) & (A != C) & (A != D) & (B != C) & (B != D) & (C != D)
anti = np.array(L.antipodal(U, nax), dtype=np.int32).reshape(nax, nax).astype(bool)
no_anti = ~(anti[A, B] | anti[A, C] | anti[A, D] | anti[B, C] | anti[B, D] | anti[C, D])
absE4 = np.abs(E4)
print('all tuples           max|E4| =', int(absE4.max()))
print('all-distinct         max|E4| =', int(absE4[all_distinct].max()))
print('all-distinct+no-anti max|E4| =', int(absE4[all_distinct & no_anti].max()))
print('no-anti (any repeats) max|E4| =', int(absE4[no_anti].max()))
# coincidence-pattern maxima: number of distinct values in the tuple
cnt = np.zeros(5, dtype=np.int64)
k = np.zeros_like(A)
k = 4 - ((A == B).astype(int) + (A == C).astype(int) + (A == D).astype(int)
         + (B == C).astype(int) + (B == D).astype(int) + (C == D).astype(int))
# this counts equality-pairs, not distinct values; use explicit partitions instead
part = np.zeros_like(A)
part = np.where(all_distinct, 4, 0)
part = np.where((k == 1) & (part == 0), 3, part)   # exactly one equal pair -> 3 distinct
part = np.where((k >= 2) & (part == 0), 2, part)
part = np.where((A == B) & (B == C) & (C == D), 1, part)
for p in (1, 2, 3, 4):
    m = absE4[part == p]
    print('pattern with %d distinct slots: count = %d, max|E4| = %s'
          % (p, m.size, int(m.max()) if m.size else '-'))
# which E4 values are attainable with all-distinct settings
vals = np.unique(absE4[all_distinct]).tolist()
print('attainable |E4| (all-distinct):', vals)
vals2 = np.unique(absE4[all_distinct & no_anti]).tolist()
print('attainable |E4| (all-distinct+no-anti):', vals2)
print('8*max_distinct = %d/120 ; 8*max_distinct_anti = %d/120'
      % (8 * int(absE4[all_distinct].max()), 8 * int(absE4[all_distinct & no_anti].max())))
