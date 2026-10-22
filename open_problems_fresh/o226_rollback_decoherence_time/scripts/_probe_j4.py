#!/usr/bin/env python3
"""O226 diagnostic probe -- exact structure of the read kernel K (flat 62-sign vector per state)."""
import importlib.util, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('m226', os.path.join(HERE, '02_o226_ledger_machine.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
axes, U, ids, types, hvec = m.load_inputs()
G, idx, MUL = m.build_group()
hx = [idx[m.qkey(h)] for h in hvec]
K = m.build_K(G, U)
ONE = (m.ONE, m.ZERO, m.ZERO, m.ZERO)
IDX = idx[m.qkey(ONE)]
print('K is a list of', len(K), 'rows of', len(K[0]), 'signs; signs seen =', sorted({v for r in K for v in r}))
print('per-setting balance: #states with +1 per ctx =', sorted({sum(1 for s in range(120) if K[s][c] == 1) for c in range(62)}))
wt = sorted({sum(r) for r in K})
print('row weight (sum of signs) value set =', wt)
rows = [tuple(r) for r in K]
classes = {}
for s in range(120):
    classes.setdefault(rows[s], []).append(s)
print('distinct kernel rows =', len(classes), '; preimage sizes =', sorted({len(v) for v in classes.values()}))
def order_of(i):
    p, o = G[i], 1
    while m.qkey(p) != m.qkey(ONE):
        p = m.qmul(p, G[i]); o += 1
    return o
# stabiliser of a row class
for s in (0, 10, 37, 100):
    gs = [g for g in range(120) if rows[MUL[s][g]] == rows[s]]
    print('stab(class of s=%d): size %d ; orders %s' % (s, len(gs), sorted(order_of(g) for g in gs)))
cl = sorted(classes.keys()); rep = [classes[k][0] for k in cl]
print('class reps: order, row weight =', [(order_of(rep[i]), sum(K[rep[i]])) for i in range(12)])
D = [[sum(1 for x in range(62) if K[rep[i]][x] != K[rep[j]][x]) for j in range(12)] for i in range(12)]
vals = sorted({v for r in D for v in r})
print('class-pair Hamming value set =', vals, '; complement closed =', all((62 - v) in vals for v in vals))
for i in range(12):
    print('   ', D[i])
# is the class determined by the 5-fold axis / by the h-value?
print('K[s] == K[t] count over all pairs == expected (12*10*9 + 120) =', sum(1 for s in range(120) for t in range(120) if rows[s] == rows[t]))
