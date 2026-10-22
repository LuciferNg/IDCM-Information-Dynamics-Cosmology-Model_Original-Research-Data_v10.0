#!/usr/bin/env python3
"""scratch: why does my V8 parity check disagree with probe_quant.py's control?
Compute both ways on the SAME draws and print the mismatch."""
import sys

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
ros = [L.rot_ref(G[s], U[0]) for s in range(n)]
print('reps', len(reps), 'first 6', reps[:6])


def sgn_vec(w):
    out = []
    for s in range(n):
        r = ros[s]
        d = L.add(L.add(L.mul(L.N(w[0]), r[0]), L.mul(L.N(w[1]), r[1])), L.mul(L.N(w[2]), r[2]))
        sg = L.sgn(d)
        if sg == 0:
            for c in r:
                if L.sgn(c) != 0:
                    sg = L.sgn(c)
                    break
        out.append(sg)
    return out


st = 20260930
mismatches = 0
for draw in range(8):
    ws = []
    for _ in range(2):
        w = []
        for _c in range(3):
            st = (st * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
            w.append((st >> 33) % 2000001 - 1000000)
        ws.append(w)
    st = (st * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
    h = hx[(st >> 17) % nax]
    x = sgn_vec(ws[0])
    y = sgn_vec(ws[1])
    # way 1 (my V8): 60-class match count
    m = sum(1 for s in reps if x[s] == y[MUL[s][h]])
    nnum = 2 * (2 * m - 60)
    # way 2 (probe): sum over reps of x[s]*y[s h]
    s60 = sum(x[s] * y[MUL[s][h]] for s in reps)
    # way 3: full 120-state sum
    s120 = sum(x[s] * y[MUL[s][h]] for s in range(n))
    print('draw %d: m=%d 2m-60=%d nnum=%d s60=%d s120=%d h=%d  (s60==2m-60: %s, nnum==2*s60: %s)'
          % (draw, m, 2 * m - 60, nnum, s60, s120, h, s60 == 2 * m - 60, nnum == 2 * s60))
