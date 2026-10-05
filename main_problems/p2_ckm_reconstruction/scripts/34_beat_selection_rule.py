"""
IDCM v10.0 — Beat selection rule search (P3c + P1/P2 structural rule)
====================================================================
Questions:
Q0: verify the four framework beat formulas numerically
    theta12 = atan(beat(5,6)/beat(19,25))  = 13.0400
    theta23 = atan(beat(33,35)/beat(3,22)) = 2.3800
    theta13 = asin(beat(42,43)/beat(10,31))= 0.2010
    delta   = atan(beat(2,23)/beat(8,17))  = 66.399960  (new candidate)
    with beat(i,j) = |omega_i - omega_j|, omega_n = 2 sin(n pi/88)
Q1: minimality — for each target angle, the minimal max-index pair
    realization within tol (selection criterion test)
Q2: k-ladder (O149) with the framework omega-beat: what do g_k match?
Q3: Z5 charge structure of the 8 selected pairs (charge = index mod 5)
Q4: (diff,sum) web table for the 8 pairs
"""
import math

p = math.pi


def omega(n):
    return 2 * math.sin(n * p / 88)


def beat(i, j):
    return abs(omega(i) - omega(j))


# Q0
th12 = math.degrees(math.atan(beat(5, 6) / beat(19, 25)))
th23 = math.degrees(math.atan(beat(33, 35) / beat(3, 22)))
th13 = math.degrees(math.asin(min(beat(42, 43) / beat(10, 31), 1.0)))
dlt = math.degrees(math.atan(beat(2, 23) / beat(8, 17)))
print(f"Q0 theta12={th12:.6f} theta23={th23:.6f} theta13={th13:.6f} delta={dlt:.6f}")

# Q1 minimality scan
pairs = [(a, b) for a in range(1, 45) for b in range(1, 45) if a != b]
targets = {"theta12": (13.04, "atan"), "theta23": (2.38, "atan"),
           "theta13": (0.201, "asin"), "delta": (66.399960, "atan")}
TOL = 0.02
for name, (tgt, ftype) in targets.items():
    hits = []
    for (a, b) in pairs:
        for (c, d) in pairs:
            if (a, b) == (c, d):
                continue
            r = beat(a, b) / beat(c, d)
            ang = math.degrees(math.asin(min(r, 1.0))) if ftype == "asin" else math.degrees(math.atan(r))
            if abs(ang - tgt) < TOL:
                mx = max(a, b, c, d)
                hits.append((mx, abs(ang - tgt), (a, b), (c, d), ang))
    hits.sort()
    print(f"\nQ1 {name} (target {tgt}, tol {TOL}), minimal max-index realizations:")
    for h in hits[:6]:
        print(f"    maxidx={h[0]:2d} {h[4]:.6f} deg beat{h[2]}/beat{h[3]}")

# Q2 k-ladder with omega-beat
F = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
print("\nQ2 k-ladder g_k = beat(44-k,44-k+1)/beat(44-(k+1),F_{k+6}):")
refs = {"V_us": 0.225, "V_cb": 0.0405, "V_ub": 0.00369, "s13_PMNS": 0.149}
for k in range(1, 5):
    num = beat(44 - k, 44 - k + 1)
    den = beat(44 - (k + 1), F[k + 5])
    if den != 0:
        g = num / den
        print(f"    g_{k} = {g:.6f}", end="")
        for rn, rv in refs.items():
            if abs(g - rv) / rv < 0.3:
                print(f"  ~ {rn} ({abs(g-rv)/rv*100:.1f}%)", end="")
        print()

# Q3 Z5 charges of the 8 pairs
sel = [(5, 6), (19, 25), (33, 35), (3, 22), (42, 43), (10, 31), (2, 23), (8, 17)]
print("\nQ3 Z5 charge (index mod 5) of selected pairs:")
cdiffs = []
for (a, b) in sel:
    ca, cb = a % 5, b % 5
    cd = abs(ca - cb)
    cdiffs.append(cd)
    print(f"    ({a:2d},{b:2d}) charges ({ca},{cb}) cdiff={cd} sum_mod5={(a+b)%5}")
print(f"    charge-diff distribution: {cdiffs}")
# charge-diff=1 pairs: how many of the 1892 pairs? and how many hit near targets?
pairs_cd1 = [pr for pr in pairs if abs(pr[0] % 5 - pr[1] % 5) == 1]
print(f"    pairs with cdiff=1: {len(pairs_cd1)}/{len(pairs)}")
# do the four target pairs all have cdiff=1?
for name, (pa, pb) in {"theta12": ((5, 6), (19, 25)), "theta23": ((33, 35), (3, 22)),
                        "theta13": ((42, 43), (10, 31)), "delta": ((2, 23), (8, 17))}.items():
    ok = abs(pa[0] % 5 - pa[1] % 5) == 1 and abs(pb[0] % 5 - pb[1] % 5) == 1
    print(f"    {name}: both pairs cdiff=1? {ok}")

# Q4 (diff,sum) web
print("\nQ4 (diff,sum) web for the 8 pairs:")
rows = []
for (a, b) in sel:
    rows.append((a, b, abs(a - b), a + b, a * b))
print(f"    {'pair':>8} {'diff':>4} {'sum':>4} {'prod':>5} {'diff*sum':>8}")
for r in rows:
    print(f"    {str(r[0:2]):>8} {r[2]:>4} {r[3]:>4} {r[4]:>5} {r[2]*r[3]:>8}")
