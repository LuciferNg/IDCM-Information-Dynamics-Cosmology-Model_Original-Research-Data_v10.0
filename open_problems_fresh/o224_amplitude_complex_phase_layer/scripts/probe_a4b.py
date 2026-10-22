#!/usr/bin/env python3
"""scratch: debug the A4b inner-automorphism transport failure at h = 5."""
import sys

sys.path.insert(0, '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o224_amplitude_complex_phase_layer/scripts')
import lib2i as L

G, idx, MUL, U, ids, types, hx, K = L.load_machine()
n, nax = len(G), len(ids)
e0 = idx[L.qkey(L.ID_ELEM)]
C1 = L.e1_table(K, MUL, hx, n, nax)
print('e0 =', e0)


def inv_of(h):
    x, k = h, 1
    while x != e0:
        x = MUL[x][h]
        k += 1
    y = e0
    for _ in range(k - 1):
        y = MUL[y][h]
    return y, k


for h in (0, 5, 61):
    hh, k = inv_of(h)
    ok_inv = (MUL[h][hh] == e0 and MUL[hh][h] == e0)
    finv = [MUL[MUL[hh][s]][h] for s in range(n)]
    perm = [MUL[MUL[h][s]][hh] for s in range(n)]
    valid_perm = sorted(perm) == list(range(n)) and sorted(finv) == list(range(n))
    # is conjugation a bijection on indices? check the orbit structure
    K2 = [K[finv[s]] for s in range(n)]
    MUL2 = [[perm[MUL[finv[a]][finv[b]]] for b in range(n)] for a in range(n)]
    hx2 = [finv[hx[a]] for a in range(nax)]
    # validity of the transported machine
    ok_id = all(MUL2[e0][a] == a and MUL2[a][e0] == a for a in range(n))
    ok_assoc = all(MUL2[MUL2[a][b]][c] == MUL2[a][MUL2[b][c]]
                   for a in range(0, n, 7) for b in range(0, n, 11) for c in range(0, n, 13))
    C1c = L.e1_table(K2, MUL2, hx2, n, nax)
    same = all(C1c[a][b] == C1[a][b] for a in range(nax) for b in range(nax))
    # direct check of the identity on a couple of pairs
    a, b = 0, 1
    lhs = sum(K[s][a] * K[MUL[s][hx[a]]][b] for s in range(n))
    rhs = sum(K[finv[x]][a] * K[finv[MUL2[x][hx2[a]]]][b] for x in range(n))
    print('h=%3d order=%2d inv_ok=%s valid_perm=%s id_ok=%s assoc=%s C1_same=%s direct %d/%d'
          % (h, k, ok_inv, valid_perm, ok_id, ok_assoc, same, rhs, lhs))
    print('      hx2 == finv-hx ?', hx2[:4], [finv[hx[a]] for a in range(4)],
          'identity of hh:', MUL[h][hh], MUL[hh][h], 'e0', e0)
