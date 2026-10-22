#!/usr/bin/env python3
"""scratch: which condition makes the 60-class sum divisible by 4 (numerator divisible by 8)?
Families: (A) generic rational directions; (B) A5-orbit points (random group images of the 62
frozen axes); (C) frozen axes with a random group element instead of a frozen h.
Exact arithmetic throughout (Q(sqrt5)); the only randomness is in choosing the objects.
"""
import sys
import collections

sys.path.insert(0, '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o224_amplitude_complex_phase_layer/scripts')
import lib2i as L

G, idx, MUL, U, ids, types, hx, K = L.load_machine()
n, nax = len(G), len(ids)
e = idx[L.qkey(L.ID_ELEM)]
invs = []
for s in range(n):
    x, k = s, 1
    while x != e:
        x = MUL[x][s]
        k += 1
    y = e
    for _ in range(k - 1):
        y = MUL[y][s]
    invs.append(y)
reps, seen = [], set()
for s in range(n):
    if s in seen:
        continue
    reps.append(s)
    seen.add(s)
    seen.add(invs[s])
print('reps =', len(reps))

ros = [L.rot_ref(G[s], U[0]) for s in range(n)]


def sign_of(vec, s):
    r = ros[s]
    d = L.add(L.add(L.mul(vec[0], r[0]), L.mul(vec[1], r[1])), L.mul(vec[2], r[2]))
    sg = L.sgn(d)
    if sg == 0:
        for c in r:
            if L.sgn(c) != 0:
                return L.sgn(c)
    return sg


def classes(vec):
    return [sign_of(vec, s) for s in reps]


def sum60(x, y, h):
    return sum(x[i] * y[MUL[reps[i]][h]] for i in range(len(reps)))


def mul_vec(R, v):
    # rotate v by the group element R (icosahedral rotation)
    u = [L.rot_ref(R, (L.ONE, L.ZERO, L.ZERO)), L.rot_ref(R, (L.ZERO, L.ONE, L.ZERO)),
         L.rot_ref(R, (L.ZERO, L.ZERO, L.ONE))]
    # matrix columns: image of the basis vectors
    out = []
    for row in range(3):
        acc = L.ZERO
        for col in range(3):
            acc = L.add(acc, L.mul(u[col][row], v[col]))
        out.append(acc)
    return tuple(out)


st = 987654321


def nxt():
    global st
    st = (st * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
    return st >> 17


# (A) generic rational directions
histA = collections.Counter()
for t in range(300):
    u = tuple(L.N(nxt() % 21 - 10) for _ in range(3))
    v = tuple(L.N(nxt() % 21 - 10) for _ in range(3))
    h = hx[nxt() % nax]
    histA[sum60(classes(u), classes(v), h) % 4] += 1

# (B) A5-orbit points: random group images of frozen axes
histB = collections.Counter()
for t in range(300):
    R1, R2 = G[nxt() % n], G[nxt() % n]
    a, b = nxt() % nax, nxt() % nax
    u = mul_vec(R1, U[a])
    v = mul_vec(R2, U[b])
    h = hx[nxt() % nax]
    histB[sum60(classes(u), classes(v), h) % 4] += 1

# (C) frozen axes, random group element as the shift
histC = collections.Counter()
for t in range(300):
    a, b, h = nxt() % nax, nxt() % nax, nxt() % n
    prev_h = L  # noqa
    x = [K[s][a] for s in reps]
    y = [K[s][b] for s in reps]
    histC[sum60(x, y, h) % 4] += 1

print('(A) generic rational directions, frozen h : mod4 hist =', dict(histA))
print('(B) A5-orbit points (random images), frozen h : mod4 hist =', dict(histB))
print('(C) frozen axes, random group shift : mod4 hist =', dict(histC))
# frozen baseline
hist0 = collections.Counter()
for a in range(nax):
    for b in range(nax):
        if a == b:
            continue
        hist0[sum60([K[s][a] for s in reps], [K[s][b] for s in reps], hx[a]) % 4] += 1
print('frozen 3844 pairs : mod4 hist =', dict(hist0))
