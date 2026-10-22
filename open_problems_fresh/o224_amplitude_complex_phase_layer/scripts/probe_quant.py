#!/usr/bin/env python3
"""scratch probe: where does the 1/15 (mod-8) quantisation of the frozen correlation come from?"""
import sys, os, collections
sys.path.insert(0, '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o224_amplitude_complex_phase_layer/scripts')
import lib2i as L
from fractions import Fraction as F

G, idx, MUL, U, ids, types, hx, K = L.load_machine()
Z = L.scale(L.ONE, -1)
m1 = idx[L.qkey((Z, L.ZERO, L.ZERO, L.ZERO))]
inv = [MUL[m1][s] for s in range(120)]
reps = sorted(set(min(s, inv[s]) for s in range(120)))
print('reps', len(reps))


def smix(state):
    return L.__dict__ and None


def splitmix64(state):
    state = (state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    z = z ^ (z >> 31)
    return state, z


def rv(state):
    """random integer 3-vector in [-5,5]^3, nonzero"""
    while True:
        v = []
        for _ in range(3):
            state, z = splitmix64(state)
            v.append(z % 11 - 5)
        if any(v):
            return state, tuple(L.N(x) for x in v)


def dot(a, b):
    return L.add(L.add(L.mul(a[0], b[0]), L.mul(a[1], b[1])), L.mul(a[2], b[2]))


n0 = U[0]
st = 4242
res = collections.Counter()
ties = 0
samples = 0
for trial in range(300):
    st, u = rv(st)
    st, v = rv(st)
    st, w = rv(st)
    st, z = splitmix64(st)
    h = z % 120
    tot = 0
    for s in reps:
        rs = L.rot_ref(G[s], n0)
        rsh = L.rot_ref(G[MUL[s][h]], n0)
        du = L.sgn(dot(u, rs))
        dv = L.sgn(dot(v, rsh))
        if du == 0 or dv == 0:
            ties += 1
            continue
        tot += du * dv
    samples += 1
    res[tot % 4] += 1
print('random generic axes+refs: (60-sum) mod 4 histogram ->', dict(res), 'ties', ties)

# control: single sign function
res1 = collections.Counter()
for trial in range(300):
    st, u = rv(st)
    h = 0
    tot = 0
    for s in reps:
        rs = L.rot_ref(G[s], n0)
        du = L.sgn(dot(u, rs))
        if du == 0:
            continue
        tot += du
    res1[tot % 4] += 1
print('single-sign 60-sum mod 4 ->', dict(res1))

# control: arbitrary +-1 function on the 60 reps
import itertools
res2 = collections.Counter()
for trial in range(300):
    tot = 0
    for s in reps:
        st, z = splitmix64(st)
        tot += 1 if (z & 1) else -1
    res2[tot % 4] += 1
print('arbitrary +-1 60-sum mod 4 ->', dict(res2))

# frozen: does the FROZEN set also give 0 mod 4 always (sanity)
bad = 0
for a in range(62):
    for b in range(62):
        if a == b:
            continue
        tot = sum(K[s][a] * K[MUL[s][hx[a]]][b] for s in reps)
        if tot % 4:
            bad += 1
print('frozen 60-sum mod4 != 0 count', bad)
