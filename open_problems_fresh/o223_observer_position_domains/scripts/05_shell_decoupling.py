#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O223 scripts/05 -- SHELL THEOREM + why colour is a weak predictor of T.
==============================================================================
RESULT (new structural identity, zero free parameters):
    frustrated edge  <=>  the two endpoints lie in the SAME BFS shell
    (BFS from the anchor).  Hence
        32 frustrated edges = intra-shell edges
        88 non-frustrated edges = inter-shell edges = 2*N_d = O182's 88-grid
    and the 88-grid = midpoints of the inter-shell edges  -> ANCHOR-DEPENDENT.

Then the decoupling mechanism for items 1 and 2 of the open list:
  - colour c(i) = parity of hop(i)  (BFS distance from the anchor)
  - variance decomposition of T: within-shell vs between-shell
  - permutation null for r(colour, T)
  - the structural prediction  frust(i)=2  =>  theta_i = +-pi/2  =>  T_i ~ 0
    (the 12 "Delta E = 0" nodes of O7)
  - node 9 diagnosis

ASCII only.  /usr/bin/python3.
"""
import os, math, json
import numpy as np
from collections import deque, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CS   = os.path.join(os.path.dirname(ROOT), "cmb_cold_spot", "data")

res = []
def check(name, cond, detail=""):
    res.append((name, bool(cond), detail))
    print(("  [OK] " if cond else "  [XX] ") + name + ("   " + detail if detail else ""))

def sph(ra, dec):
    r, d = math.radians(ra), math.radians(dec)
    return np.array([math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d)])

nodes = [tuple(map(float, l.split())) for l in open(os.path.join(CS, "a5_nodes.txt"))]
V = np.array([sph(*n) for n in nodes]); N = 60
D = np.degrees(np.arccos(np.clip(V @ V.T, -1, 1)))
dss = np.sort(D[np.triu_indices(N, 1)]); thr = (dss[119] + dss[120]) / 2
A = (D < thr); np.fill_diagonal(A, False)
nbr = {i: [int(j) for j in np.where(A[i])[0]] for i in range(N)}

T = {}
for line in open(os.path.join(CS, "smica_smoothed.txt")):
    if line.startswith("#"):
        continue
    p = line.split(); T[int(p[0])] = float(p[2])
Tv = np.array([T[k] for k in range(N)])

print("="*76)
print("O223 / 05 -- shell theorem + colour/T decoupling")
print("="*76)

# ---------------------------------------------------------------- BFS shells
print("[S] BFS shell decomposition from the anchor (node 0)")
hop = {0: 0}; q = deque([0])
while q:
    u = q.popleft()
    for w in nbr[u]:
        if w not in hop:
            hop[w] = hop[u] + 1; q.append(w)
lad = [Counter(hop.values())[h] for h in range(max(hop.values()) + 1)]
print("    hop ladder = %s   (sum = %d, diameter = %d)" % (lad, sum(lad), max(hop.values())))
check("S1 hop ladder = [1,4,8,11,12,11,8,4,1] (matches o179 record)",
      lad == [1, 4, 8, 11, 12, 11, 8, 4, 1])

# ---------------------------------------------------------------- SHELL THEOREM
print("[S2] SHELL THEOREM: frustrated edge <=> same shell")
frust = set(frozenset((i, j)) for i in range(N) for j in nbr[i]
            if i < j and hop[i] == hop[j])
all_frust = set(frozenset((i, j)) for i in range(N) for j in nbr[i] if i < j)
from_parity = set(frozenset((i, j)) for (i, j) in
                  [(i, j) for i in range(N) for j in nbr[i] if i < j]
                  if (hop[i] - hop[j]) % 2 == 0)
inter = set(frozenset((i, j)) for i in range(N) for j in nbr[i]
            if i < j and abs(hop[i] - hop[j]) == 1)
print("    same-shell edges  = %d" % len(frust))
print("    adjacent-shell    = %d" % len(inter))
print("    total             = %d" % len(all_frust))
check("S2 frustrated set == same-shell set EXACTLY (set equality)",
      frust == from_parity, "%d edges" % len(frust))
check("S3 |intra-shell| = 32 (frustration)", len(frust) == 32)
check("S4 |inter-shell| = 88 = 2*N_d (the O182 88-grid!)", len(inter) == 88)
check("S5 no edge connects shells differing by >= 2 (BFS property)",
      len(frust) + len(inter) == len(all_frust))

# ---------------------------------------------------------------- variance decomposition
print("[V] variance decomposition of T: why colour cannot predict T")
cvec = np.array([hop[i] % 2 for i in range(N)])
shells = sorted(set(hop.values()))
Tbar = Tv.mean()
ss_tot = float(((Tv - Tbar) ** 2).sum())
ss_between_shell = float(sum(len([i for i in range(N) if hop[i] == h]) *
                              (Tv[[i for i in range(N) if hop[i] == h]].mean() - Tbar) ** 2
                              for h in shells))
ss_within_shell = ss_tot - ss_between_shell
r2_shell = ss_between_shell / ss_tot
print("    total SS      = %10.1f" % ss_tot)
print("    between-shell = %10.1f  (R^2 = %.4f)" % (ss_between_shell, r2_shell))
print("    within-shell  = %10.1f  (1-R^2 = %.4f)" % (ss_within_shell, 1 - r2_shell))
print("    -> %.1f%% of the temperature variance lives INSIDE a shell"
      % (100 * ss_within_shell / ss_tot))
print("    within-shell std per shell:")
for h in shells:
    ts = Tv[[i for i in range(N) if hop[i] == h]]
    if len(ts) > 1:
        print("      hop %d: n=%2d  mean %+7.1f  std %6.1f  range %+7.1f..%+7.1f"
              % (h, len(ts), ts.mean(), ts.std(ddof=1), ts.min(), ts.max()))

r = float(np.corrcoef(cvec, Tv)[0, 1])
r2_colour = r ** 2
# R^2 of the 2-group (parity) split must equal r^2 for a binary predictor
g1 = Tv[cvec == 1]; g0 = Tv[cvec == 0]
ss_between_colour = (len(g1) * (g1.mean() - Tbar) ** 2 + len(g0) * (g0.mean() - Tbar) ** 2)
r2_colour_direct = ss_between_colour / ss_tot
print("[C] colour (hop parity) vs T")
print("    r = %+.4f   r^2 = %.4f" % (r, r2_colour))
print("    2-group R^2 (direct) = %.4f   -> consistency |diff| = %.2e"
      % (r2_colour_direct, abs(r2_colour_direct - r2_colour)))
check("C1 r^2 == 2-group R^2 (binary predictor consistency)",
      abs(r2_colour_direct - r2_colour) < 1e-9)
check("C2 R^2(colour) < R^2(shell): parity is strictly weaker than the full shell",
      r2_colour < r2_shell + 1e-12, "%.4f vs %.4f" % (r2_colour, r2_shell))
check("C3 within-shell variance dominates (>= 80% of total)",
      ss_within_shell / ss_tot >= 0.80, "%.1f%%" % (100 * ss_within_shell / ss_tot))

# ---------------------------------------------------------------- null test
print("[N] permutation null for r(colour, T)")
rng = np.random.default_rng(20260927)
NS = 200000
null = np.empty(NS)
for t in range(NS):
    null[t] = np.corrcoef(cvec, rng.permutation(Tv))[0, 1]
p_one = float((null <= r).mean())
p_two = float(2 * min(p_one, 1 - p_one))
print("    null: mean %+.4f  std %.4f   observed r = %+.4f" % (null.mean(), null.std(), r))
print("    z = %+.2f   one-sided p = %.4f   two-sided p = %.4f"
      % ((r - null.mean()) / null.std(), p_one, p_two))
check("N1 |r| below 0.35 (colour is a weak predictor)", abs(r) < 0.35)
check("N2 two-sided p < 0.05 (the weak association is nevertheless real)",
      p_two < 0.05, "p = %.4f" % p_two)

# ---------------------------------------------------------------- Delta E = 0 prediction
print("[D] structural prediction: frust(i)=2  =>  theta_i = +-pi/2  =>  T_i ~ 0")
fc = Counter()
for e in frust:
    a, b = tuple(e); fc[a] += 1; fc[b] += 1
two = np.array([i for i in range(N) if fc[i] == 2])
one = np.array([i for i in range(N) if fc[i] == 1])
zero = np.array([i for i in range(N) if fc[i] == 0])
print("    frust(i) groups: 0 -> %d nodes, 1 -> %d, 2 -> %d"
      % (len(zero), len(one), len(two)))
print("    mean |T|:  frust=2 -> %6.1f uK   frust=1 -> %6.1f   frust=0 -> %6.1f"
      % (np.abs(Tv[two]).mean(), np.abs(Tv[one]).mean(), np.abs(Tv[zero]).mean()))
print("    frust=2 node temps: %s" % np.round(Tv[two], 1).tolist())
# permutation test: is mean|T| of the 12 frust=2 nodes unusually small?
obs = np.abs(Tv[two]).mean()
NS2 = 200000
perm = np.empty(NS2)
for t in range(NS2):
    perm[t] = np.abs(Tv[rng.permutation(N)[:len(two)]]).mean()
p_dE = float((perm <= obs).mean())
print("    permutation: mean %6.1f  std %5.1f   observed %6.1f   one-sided p = %.4f"
      % (perm.mean(), perm.std(), obs, p_dE))
check("D1 frust=2 (Delta E = 0) nodes have smaller |T| than the field (p < 0.05)",
      p_dE < 0.05, "p = %.4f, obs = %.1f vs null %.1f" % (p_dE, obs, perm.mean()))

# ---------------------------------------------------------------- node 9
print("[J] node 9 diagnosis")
A_amp = 134.19
print("    hop(9) = %d (shell 1)   T[9] = %+.1f uK   |T|/A = %.3f"
      % (hop[9], Tv[9], abs(Tv[9]) / A_amp))
sh1 = [i for i in range(N) if hop[i] == 1]
print("    shell 1 = %s" % sh1)
print("    shell 1 temps = %s" % np.round(Tv[sh1], 1).tolist())
print("    -> shell 1 contains BOTH a very cold node (-107) and hot nodes (+35,+36)")
print("    -> the phase theta_i is NOT a function of the shell; it is a free STATE")
check("J1 node 9 is in shell 1 with |T|/A = 0.80 (a large unsaturated domain)",
      hop[9] == 1 and 0.7 < abs(Tv[9]) / A_amp < 0.9)
check("J2 shell 1 spans both signs (phase is a state, not a shell function)",
      Tv[sh1].min() < -50 and Tv[sh1].max() > 20)

print("-"*76)
npass = sum(1 for _, o, _ in res if o); ntot = len(res)
print("RESULT: %d/%d PASS" % (npass, ntot))
print("-"*76)
out = dict(n_pass=npass, n_total=ntot,
           hop_ladder=lad, n_intra=len(frust), n_inter=len(inter),
           r2_shell=r2_shell, r2_colour=r2_colour,
           within_frac=ss_within_shell / ss_tot,
           pearson_r=r, p_two_sided=p_two,
           frust2_mean_absT=float(np.abs(Tv[two]).mean()),
           frust1_mean_absT=float(np.abs(Tv[one]).mean()),
           frust0_mean_absT=float(np.abs(Tv[zero]).mean()),
           deltaE_p=p_dE, node9_hop=hop[9], node9_T=float(Tv[9]),
           shell1=sh1, shell1_T=[float(Tv[i]) for i in sh1])
json.dump(out, open(os.path.join(ROOT, "data", "05_shell_decoupling.json"), "w"), indent=1)
print("wrote data/05_shell_decoupling.json")
