#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O222 scripts/03_aut_stabilizer.py

R1 (Part B) -- C1 本體化: 波形態 / 粒子態 = Aut 破缺與穩定子階數之相變；ell_read 只係派生索引。

調律者裁定 (b) (2026-09-29):
  「果斷放棄純數值 ell_read 索引，直接以 Aut(自同構群)破缺與穩定子(Stabilizer)階數作為本體定義，
    讓 ell_read 僅作為派生數值表現。」
  ⟹ C1-def:  波動態 <=> |Stab_G(ctx)| >= 2      (讀取唔分辨 orbit 成員; memo 單一連通分量)
              粒子態 <=> |Stab_G(ctx)| = 1       (全 Aut 破缺; memo 拓樸分裂)
              ell_thresh (派生) = 最小秩 r，使【晶格原生】rank-r ctx 可達 |Stab| = 1

方法（全精確算術，零浮點）:
  1. Q(sqrt5): (p,q) = p + q sqrt5, p,q ∈ Fraction。
  2. 2I = <2T, q0> quaternion 閉包 -> 驗 |2I| = 120（unit、逆閉）。
  3. I = 2I/{+-1}（v -> q v qbar）-> 驗 |I| = 60；I_h = <I,-Id> -> 120。
  4. ★ 晶格原生軸【由群自己導出】（唔靠外部記入）：
       元素階 5 -> 12 頂點方向（5 重軸）
       元素階 3 -> 20 面心方向（3 重軸）
       元素階 4 -> 30 邊中點方向（2 重軸）
     再核對頂點方向 == (0,+-1,+-phi) 及循環置換（教科書座標）。
  5. 軌道-穩定子: |G| = |orbit| x |Stab| 逐一核對。
  6. 讀取階梯 r = 0..3: 由 12 頂點軸之【對稱無跡張量】窮舉構造 ctx，計 min|Stab_I|；
     rank 奇 = 反演奇 => |Stab_Ih| = |Stab_I|；rank 偶 => 2|Stab_I|。

慣例標籤: [exact-Q(sqrt5) / 2I-120 / I-60 / I_h-120 / rank-r / negative-control]
"""

import itertools
import json
import os
import random
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
os.makedirs(DATA, exist_ok=True)

RESULTS = []


def chk(tag, name, ok, detail=""):
    RESULTS.append({"tag": tag, "name": name, "ok": bool(ok), "detail": detail})
    print("[%s] %-15s %-70s %s" % ("PASS" if ok else "FAIL", tag, name, detail))
    return ok


def claim(tag, name, text):
    RESULTS.append({"tag": tag, "name": name, "ok": None, "detail": text})
    print("[CLAIM] %-15s %-70s %s" % (tag, name, text))


# ================================================================ exact Q(sqrt5)
ZERO, ONE, HALF, SIXTH = (F(0), F(0)), (F(1), F(0)), (F(1, 2), F(0)), (F(1, 6), F(0))


def N(a, b=0):
    return (F(a), F(b))


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def neg(x):
    return (-x[0], -x[1])


def sub(x, y):
    return (x[0] - y[0], x[1] - y[1])


def mul(x, y):
    return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def inv(x):
    d = x[0] * x[0] - 5 * x[1] * x[1]
    return (x[0] / d, -x[1] / d)


def scale(x, k):
    return (x[0] * F(k), x[1] * F(k))


PHI = N(F(1, 2), F(1, 2))            # phi = (1+sqrt5)/2
PSI = sub(PHI, ONE)                  # 1/phi = phi - 1


def dot(a, b):
    return add(add(mul(a[0], b[0]), mul(a[1], b[1])), mul(a[2], b[2]))


def norm2(a):
    return dot(a, a)


def dir_canon(v):
    """canonical oriented direction: divide by the FIRST non-zero component (exact)."""
    for x in v:
        if x != ZERO:
            return tuple(mul(inv(x), y) for y in v)
    raise ValueError("zero vector")


def is_zero(x):
    return x == ZERO


# ================================================================ quaternions -> 2I
def qmul(a, b):
    a0, a1, a2, a3 = a
    b0, b1, b2, b3 = b
    return (sub(sub(sub(mul(a0, b0), mul(a1, b1)), mul(a2, b2)), mul(a3, b3)),
            add(add(mul(a0, b1), mul(a1, b0)), sub(mul(a2, b3), mul(a3, b2))),
            add(sub(mul(a0, b2), mul(a1, b3)), add(mul(a2, b0), mul(a3, b1))),
            add(add(mul(a0, b3), mul(a1, b2)), sub(mul(a3, b0), mul(a2, b1))))


def qconj(a):
    return (a[0], neg(a[1]), neg(a[2]), neg(a[3]))


gens = []
for s in (1, -1):
    gens += [(N(s), ZERO, ZERO, ZERO), (ZERO, N(s), ZERO, ZERO),
             (ZERO, ZERO, N(s), ZERO), (ZERO, ZERO, ZERO, N(s))]
for s1 in (1, -1):
    for s2 in (1, -1):
        for s3 in (1, -1):
            gens.append((scale(ONE, F(s1, 2)), scale(ONE, F(s2, 2)), scale(ONE, F(s3, 2)),
                         scale(ONE, F(s1 * s2 * s3, 2))))
gens.append((scale(PHI, F(1, 2)), scale(ONE, F(1, 2)), scale(PSI, F(1, 2)), ZERO))   # q0, unit

print("=" * 110)
print("O222 R1 Part B -- C1 = Aut breaking / stabilizer order   (exact Q(sqrt5), zero float)")
print("=" * 110)

G2I = set(gens)
frontier = list(G2I)
CAP = 20000
while frontier and len(G2I) <= CAP:
    nxt = []
    for a in frontier:
        for b in gens:
            c = qmul(a, b)
            if c not in G2I:
                G2I.add(c)
                nxt.append(c)
    frontier = nxt
G2I = sorted(G2I)
unit_ok = all(qmul(q, qconj(q)) == (ONE, ZERO, ZERO, ZERO) for q in G2I)
chk("[2I-120]", "2I = <2T, q0> closes to exactly 120 UNIT quaternions, inverse-closed",
    len(G2I) == 120 and unit_ok and all(qconj(q) in G2I for q in G2I),
    "|2I| = %d ; all unit = %s" % (len(G2I), unit_ok))


# ================================================================ rotations
def rot_matrix(q):
    cols = []
    for i in range(3):
        e = [ZERO, ZERO, ZERO]
        e[i] = ONE
        r = qmul(qmul(q, (ZERO, e[0], e[1], e[2])), qconj(q))
        cols.append((r[1], r[2], r[3]))
    return tuple(tuple(cols[j][i] for j in range(3)) for i in range(3))


def matvec(M, v):
    return tuple(add(add(mul(M[i][0], v[0]), mul(M[i][1], v[1])), mul(M[i][2], v[2])) for i in range(3))


def matmul(A, B):
    return tuple(tuple(add(add(mul(A[i][0], B[0][j]), mul(A[i][1], B[1][j])), mul(A[i][2], B[2][j]))
                       for j in range(3)) for i in range(3))


def matkey(M):
    return tuple(tuple(x for x in row) for row in M)


IM = tuple(tuple(ONE if i == j else ZERO for j in range(3)) for i in range(3))
I60 = sorted({matkey(rot_matrix(q)) for q in G2I})
NEG_I60 = [tuple(tuple(neg(x) for x in row) for row in M) for M in I60]
Ih120 = sorted(set(I60) | set(NEG_I60))
chk("[I-60]", "I = 2I/{+-1}: exactly 60 distinct rotations (map 2-to-1)", len(I60) == 60,
    "|I| = %d ; |2I|/|I| = %d" % (len(I60), len(G2I) // len(I60)))
chk("[I_h-120]", "I_h = <I,-Id>: exactly 120 elements (full achiral group)", len(Ih120) == 120,
    "|I_h| = %d" % len(Ih120))


def order_of(M):
    k, X = 1, M
    while X != IM:
        X = matmul(X, M)
        k += 1
        if k > 20:
            raise RuntimeError("no order")
    return k


# ================================================================ lattice axes DERIVED from the group
# LINES first (v ~ -v identified) to count the axes; then ORIENTED ranks built as full group
# orbits, so every member of a rank shares one common scale (metric tests then valid).
lines = {}
for q in G2I:
    k = order_of(matkey(rot_matrix(q)))              # matrix order in {1, 2, 3, 5}
    vec = (q[1], q[2], q[3])
    if all(is_zero(x) for x in vec):
        continue
    lines.setdefault(k, set()).add(dir_canon(vec))

L5, L3, L2 = sorted(lines.get(5, set())), sorted(lines.get(3, set())), sorted(lines.get(2, set()))
chk("[exact-Q(sqrt5)]", "axes DERIVED from element orders: 6 five-fold / 10 three-fold / 15 two-fold LINES",
    len(L5) == 6 and len(L3) == 10 and len(L2) == 15,
    "|L5|=%d |L3|=%d |L2|=%d" % (len(L5), len(L3), len(L2)))


def first_rep(k):
    for q in G2I:
        if order_of(matkey(rot_matrix(q))) == k and any(not is_zero(x) for x in (q[1], q[2], q[3])):
            return dir_canon((q[1], q[2], q[3]))
    raise RuntimeError("no element of order %d" % k)


def orbit(v0):
    return sorted({matvec(M, v0) for M in I60})


V, FC, EMx = orbit(first_rep(5)), orbit(first_rep(3)), orbit(first_rep(2))
chk("[rank-1]", "oriented axes = full group orbits: 12 vertices / 20 face centres / 30 edge midpoints (one common scale each)",
    len(V) == 12 and len(FC) == 20 and len(EMx) == 30, "|V|=%d |FC|=%d |EM|=%d" % (len(V), len(FC), len(EMx)))


def vsub(a, b):
    return tuple(sub(x, y) for x, y in zip(a, b))


norms = {norm2(v) for v in V}
dminV = min(norm2(vsub(V[i], V[j])) for i in range(12) for j in range(i + 1, 12))
EV = [(i, j) for i in range(12) for j in range(i + 1, 12) if norm2(vsub(V[i], V[j])) == dminV]
degV = {i: sum(1 for e in EV if i in e) for i in range(12)}
FV = {f for f in itertools.combinations(range(12), 3)
      if all(norm2(vsub(V[x], V[y])) == dminV for x, y in itertools.combinations(f, 2))}
chk("[rank-1]", "the 12 derived axes form a genuine icosahedron INTRINSICALLY: single radius, 30 min-distance edges, degree 5, 20 triangle faces",
    len(norms) == 1 and len(EV) == 30 and set(degV.values()) == {5} and len(FV) == 20,
    "radii=%d edges=%d degrees=%s faces=%d" % (len(norms), len(EV), sorted(set(degV.values())), len(FV)))

# --- chart relation to the textbook coordinates: same icosahedron in the reflected chart
#     (x,y,z)->(x,z,y) i.e. phi <-> psi = 1/phi.  Recorded as a convention, not a mismatch.
DER, TEXT = set(), set()
for s1 in (1, -1):
    for s2 in (1, -1):
        for perm in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
            for src, tgt in ((PSI, DER), (PHI, TEXT)):
                v = [ZERO, ZERO, ZERO]
                v[perm[0]], v[perm[1]], v[perm[2]] = ZERO, N(s1), mul(N(s2), src)
                tgt.add(dir_canon(tuple(v)))
chk("[exact-Q(sqrt5)]", "derived vertex lines == cyclic perms of (0,+-1,+-psi) ; SWAP (x,y,z)->(x,z,y) carries them onto the textbook (0,+-1,+-phi) lines",
    set(L5) == DER and {dir_canon(matvec(((ONE, ZERO, ZERO), (ZERO, ZERO, ONE), (ZERO, ONE, ZERO)), d)) for d in L5} == TEXT,
    "|L5|=%d == |DER|=%d ; SWAP(L5) == |TEXT|=%d" % (len(set(L5)), len(DER), len(TEXT)))


def oorb_stab(v, G):
    """oriented orbit / stabilizer, raw equality (scale-independent)."""
    orb = {matvec(g, v) for g in G}
    stab = sum(1 for g in G if matvec(g, v) == v)
    return len(orb), stab


o, s = oorb_stab(V[0], I60)
chk("[rank-1]", "vertex axis: |orbit| = 12, |Stab_I| = 5 ; orbit x stab = |G| (orbit-stabilizer)",
    o == 12 and s == 5 and o * s == 60, "orbit=%d stab=%d product=%d" % (o, s, o * s))
o_e, s_e = oorb_stab(EMx[0], I60)
o_f, s_f = oorb_stab(FC[0], I60)
chk("[rank-1]", "edge axis: 30 x 2 ; face axis: 20 x 3", o_e == 30 and s_e == 2 and o_f == 20 and s_f == 3,
    "edge %dx%d ; face %dx%d" % (o_e, s_e, o_f, s_f))
vgen = (add(ONE, PHI), mul(N(2), PHI), sub(N(3), PHI))
o_g, s_g = oorb_stab(vgen, I60)
chk("[negative-control]", "rank-1 NON-lattice direction: |Stab_I| = 1 (smooth read breaks Aut at once)",
    o_g == 60 and s_g == 1, "generic dir orbit=%d stab=%d" % (o_g, s_g))

# ================================================================ permutation + parity action on the 12 axes
VPLUS = {}
for i, d in enumerate(V):
    VPLUS[d] = (i, 1)
    VPLUS[tuple(neg(x) for x in d)] = (i, -1)
perms, ok_perm = [], True
for M in I60:
    p = []
    for d in V:
        hit = VPLUS.get(matvec(M, d))
        if hit is None:
            ok_perm = False
            p.append((-1, 1))
        else:
            p.append(hit)
    perms.append(tuple(p))
chk("[I-60]", "every rotation maps the oriented axis set EXACTLY onto +-itself (raw index + sign match)",
    ok_perm and len(set(perms)) == 60, "|distinct (index,sign) actions| = %d" % len(set(perms)))


# ================================================================ symmetric traceless tensors
def sym2_traceless(a, b):
    T = [[mul(HALF, add(mul(a[i], b[j]), mul(a[j], b[i]))) for j in range(3)] for i in range(3)]
    tr = add(add(T[0][0], T[1][1]), T[2][2])
    tr3 = scale(tr, F(1, 3))
    return tuple(tuple(sub(T[i][j], tr3 if i == j else ZERO) for j in range(3)) for i in range(3))


def sym3_traceless(a, b, c):
    S = [[[ZERO for _ in range(3)] for _ in range(3)] for _ in range(3)]
    for perm in itertools.permutations((a, b, c)):
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    S[i][j][k] = add(S[i][j][k], mul(mul(perm[0][i], perm[1][j]), perm[2][k]))
    S = [[[mul(SIXTH, S[i][j][k]) for k in range(3)] for j in range(3)] for i in range(3)]
    tr = [add(add(S[i][0][0], S[i][1][1]), S[i][2][2]) for i in range(3)]
    out = [[[ZERO for _ in range(3)] for _ in range(3)] for _ in range(3)]
    for i in range(3):
        for j in range(3):
            for k in range(3):
                t = ZERO
                if i == j:
                    t = add(t, tr[k])
                if i == k:
                    t = add(t, tr[j])
                if j == k:
                    t = add(t, tr[i])
                out[i][j][k] = sub(S[i][j][k], scale(t, F(1, 5)))
    return tuple(tuple(tuple(x for x in out[i][j]) for j in range(3)) for i in range(3))


print("\n--- rank ladder (lattice-primary symmetric traceless tensors) ---")
ladder = {0: {"rank": 0, "min_stab_I": 60, "min_stab_Ih": 120, "n_cand": 1, "witness": "scalar"}}

per_kind = {}
for kind, d in [("vertex", V), ("edge", EMx), ("face", FC)]:
    sI = oorb_stab(d[0], I60)[1]
    sIh = oorb_stab(d[0], Ih120)[1]
    per_kind.setdefault(kind, set()).add((sI, sIh))
ladder[1] = {"rank": 1, "min_stab_I": min(min(x[0] for x in per_kind[k]) for k in per_kind),
             "min_stab_Ih": min(min(x[1] for x in per_kind[k]) for k in per_kind),
             "n_cand": len(V) + len(EMx) + len(FC),
             "per_kind": {k: sorted(v) for k, v in per_kind.items()}, "witness": "edge axis"}

KEY2 = {(i, j): sym2_traceless(V[i], V[j]) for i in range(12) for j in range(12)}
KEY3 = {(i, j, k): sym3_traceless(V[i], V[j], V[k])
        for i in range(12) for j in range(12) for k in range(12)}


def neg_all(x):
    if isinstance(x, tuple) and x and isinstance(x[0], tuple):
        return tuple(neg_all(y) for y in x)
    return neg(x)


def stab_by_perm(keys, idx, rank):
    """g.T == T.  T is multilinear in the axes, so p axis sign flips rescale it by (-1)^p;
    compare against the sign-corrected target."""
    n = 0
    for pp in perms:
        sign, new = 1, []
        for t in idx:
            j, sg = pp[t]
            new.append(j)
            sign *= sg
        tgt = keys[idx] if sign == 1 else neg_all(keys[idx])
        if keys[tuple(new)] == tgt:
            n += 1
    return n


for rank, keys, combos in ((2, KEY2, list(itertools.combinations(range(12), 2))),
                           (3, KEY3, list(itertools.combinations(range(12), 3)))):
    best, wit = 10 ** 9, None
    for idx in combos:
        st = stab_by_perm(keys, idx, rank)
        if st < best:
            best, wit = st, idx
    ladder[rank] = {"rank": rank, "min_stab_I": best, "n_cand": len(combos), "witness": wit}


def stab_direct(ctx, prims, rank):
    n = 0
    for M in I60:
        rp = [matvec(M, p) for p in prims]
        T = sym2_traceless(rp[0], rp[1]) if rank == 2 else sym3_traceless(rp[0], rp[1], rp[2])
        if T == ctx:
            n += 1
    return n


random.seed(11)
direct_ok = True
for rank, keys in ((2, KEY2), (3, KEY3)):
    for _ in range(4):
        idx = tuple(sorted(random.sample(range(12), rank)))
        prims = [V[i] for i in idx]
        direct_ok = direct_ok and (stab_direct(keys[idx], prims, rank) == stab_by_perm(keys, idx, rank))
chk("[exact-Q(sqrt5)]", "permutation/parity shortcut == direct 60-element tensor action (sampled)",
    direct_ok, "ranks 2 and 3 agree on samples")

for rank in (2, 3):
    ladder[rank]["min_stab_Ih"] = ladder[rank]["min_stab_I"] * (2 if rank % 2 == 0 else 1)

for r in range(4):
    d = ladder[r]
    print("   rank %d : min|Stab_I| = %-3s (GeoAut 60)   min|Stab_Ih| = %-3s (Aut 120)   cands = %-4s witness = %s"
          % (r, d["min_stab_I"], d["min_stab_Ih"], d["n_cand"], d["witness"]))

# ================================================================ C1 verdicts
chk("[rank-0]", "r=0 invariant read: |Stab_I| = 60 -> resolution 1 -> WAVE-like (resolves no node)",
    ladder[0]["min_stab_I"] == 60, "|Stab| = 60 ; resolution = 1")
chk("[rank-1]", "r=1 lattice-primary (vertex/edge/face): min|Stab_I| = 2 -> PROTECTED (wave-like)",
    ladder[1]["min_stab_I"] == 2, "per-kind (stab_I, stab_Ih) = %s" % ladder[1]["per_kind"])
chk("[rank-2]", "r=2 lattice-primary quadrupoles: min|Stab_I| >= 2 -> PROTECTED (wave-like)",
    ladder[2]["min_stab_I"] >= 2, "min|Stab_I| = %s (witness %s)" % (ladder[2]["min_stab_I"], ladder[2]["witness"]))
chk("[rank-3]", "r=3 lattice-primary octupoles: min|Stab_I| = 1 -> FIRST FULL Aut BREAKING (particle-like)",
    ladder[3]["min_stab_I"] == 1, "min|Stab_I| = %s (witness %s)" % (ladder[3]["min_stab_I"], ladder[3]["witness"]))

r_break = min(r for r in (1, 2, 3) if ladder[r]["min_stab_I"] == 1)
chk("[derived]", "DERIVED ell_thresh = smallest rank whose lattice-primary ctx has trivial stabilizer",
    r_break == 3, "ell_thresh(derived) = %d   [O143/O223 claimed: ell<=2 protected / ell=3 first breaking]" % r_break)

res = {r: 60 // ladder[r]["min_stab_I"] for r in range(4)}
# HONEST STATEMENT (the first draft claimed monotonicity -- it is FALSE):
#   resolution = |G|/|Stab| = {r0:1, r1:30, r2:15, r3:60}  ->  NOT monotone in rank.
#   The deepest rank-1 read (edge axis, |Stab_I| = 2) resolves more of Aut than ANY rank-2 quadrupole
#   (min |Stab_I| = 4).  What C1 actually needs is the THRESHOLD, and the threshold is r = 3.
chk("[memo-topology]", "resolution = |G|/|Stab| is NOT monotone in rank (1, 30, 15, 60); full resolution (=|G|, 拓樸分裂) occurs first at r = 3",
    res[0] == 1 and res[3] == 60 and all(res[r] <= 60 for r in res) and not (res[1] <= res[2] <= res[3]),
    "resolution per rank = %s (edge-axis r=1 read beats every r=2 quadrupole)" % res)

claim("[finding]", "non-monotonic ladder", "rank-1 edge-axis reads (|Stab_I| = 2) break Aut more than any rank-2 quadrupole "
      "(min |Stab_I| = 4): the criterion is a threshold, NOT a monotone ladder in read depth. Recorded as a structural "
      "finding, not smoothed over.")
claim("[crosscheck]", "O143 / O223", "ell<=2 protected + ell=3 first breaking: REPRODUCED from the stabilizer ladder "
      "(r_break = %d) with ell now DERIVED, not posited. 'ell prime = 5 unique channel' is not a rank statement -- "
      "it needs the G-representation content; flagged for docs/02, not retrofitted." % r_break)
claim("[interpretation]", "physical naming", "WAVE/PARTICLE = candidate mapping only; frozen content = the stabilizer / "
      "memo-topology criterion. No claim that QM is derived.")

n_pass = sum(1 for r in RESULTS if r["ok"] is True)
n_fail = sum(1 for r in RESULTS if r["ok"] is False)
n_claim = sum(1 for r in RESULTS if r["ok"] is None)
print("\n" + "=" * 110)
print("RESULT: %d/%d PASS  (%d FAIL, %d claims excluded)" % (n_pass, n_pass + n_fail, n_fail, n_claim))
print("=" * 110)
with open(os.path.join(DATA, "03_aut_stabilizer.json"), "w", encoding="utf-8") as fh:
    json.dump({"pass": n_pass, "fail": n_fail, "claims": n_claim, "ladder": ladder, "resolution": res,
               "ell_thresh_derived": r_break, "checks": RESULTS}, fh, ensure_ascii=False, indent=1)
print("saved: data/03_aut_stabilizer.json")
