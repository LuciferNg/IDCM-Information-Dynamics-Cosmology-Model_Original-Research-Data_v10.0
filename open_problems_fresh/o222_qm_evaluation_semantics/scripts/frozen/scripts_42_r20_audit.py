#!/usr/bin/env python3
"""O222 R20 -- INDEPENDENT audit of scripts/41_r20_closure.py (must NOT import it).

Every cell is re-derived through a different algorithm:
  A0  freeze hashes: pins + impl sha256 vs data/39_r20_freeze.json
  A1  rank_R(K) by Fraction row-reduction (machine uses fraction-free Bareiss) + explicit 6x6 minor
  A2  M1: counterexample determinant by cofactor expansion; witness submatrix = 2I-J; rank-1 sign lemma spot check
  A3  M3: re-verify the best certified realization with a transposed traversal + Fraction signs + Fraction rank
  A4  M4: reconstruct the minimal polynomial by Newton's identities from the power sums (machine multiplies factors)
  A5  M5: hit/override counts from the PINNED scripts/18 replay_protocol records (machine uses its own mirror)
  A6  M6: reads_used == sum(per_pair_misses) consistency + position of the unique minimum from data/15
  A7  scope: results file present with its numbers, cells M1..M6, verdict values legal
"""
import hashlib
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

sys.path.insert(0, HERE)
import importlib.util


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rd(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _det_frac(M):
    A = [row[:] for row in M]
    n = len(A)
    det = Fraction(1)
    for k in range(n):
        piv = None
        for i in range(k, n):
            if A[i][k]:
                piv = i
                break
        if piv is None:
            return Fraction(0)
        if piv != k:
            A[k], A[piv] = A[piv], A[k]
            det = -det
        det *= A[k][k]
        inv = A[k][k]
        for i in range(k + 1, n):
            f = A[i][k] / inv
            A[i] = [A[i][t] - f * A[k][t] for t in range(n)]
    return det


def rank_frac(M):
    """Exact rank by Fraction Gauss-Jordan (independent of the machine's Bareiss)."""
    A = [[Fraction(x) for x in row] for row in M]
    rows, cols = len(A), len(A[0])
    r = 0
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if A[i][c]:
                piv = i
                break
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        pv = A[r][c]
        A[r] = [x / pv for x in A[r]]
        for i in range(rows):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [A[i][k] - f * A[r][k] for k in range(cols)]
        r += 1
        if r == rows:
            break
    return r


def main():
    checks = []
    ok = True

    def chk(name, cond, detail):
        nonlocal ok
        ok = ok and bool(cond)
        checks.append({"check": name, "pass": bool(cond), "detail": str(detail)})
        print("[%s] %s  %s" % ("PASS" if cond else "FAIL", name, detail), flush=True)

    freeze = rd("data/39_r20_freeze.json")
    res = rd("data/41_r20_results.json")
    b5 = load(os.path.join(HERE, "12_b5_budget.py"), "b5_audit")
    _mm, K, MUL, hx, ids, types = b5.load_machine()
    m, n = len(K), len(K[0])

    # A0 hashes
    impl = sha(os.path.join(HERE, "41_r20_closure.py"))
    chk("A0a impl sha256 matches freeze", impl == freeze["impl_sha256"], "%s vs %s" % (impl[:16], freeze["impl_sha256"][:16]))
    pin_bad = []
    for k, rec in freeze["pins"].items():
        p = os.path.join(ROOT, rec["path"])
        if not os.path.exists(p) or sha(p) != rec["sha256"]:
            pin_bad.append(k)
    chk("A0b pin hashes match freeze", not pin_bad, "bad: %s" % (pin_bad or "none"))
    chk("A0c gate OPEN at freeze", freeze.get("gate") == "OPEN", freeze.get("gate"))

    # A1 rank
    r_frac = rank_frac(K)
    r_machine = res["cells"]["M1"]["numbers"]["rank_R_K_exact"]
    # explicit 6x6 minor (rows 0..5 of the first 6 pivot columns) determinant sign of nonzero
    cert_rows = [0, 1, 2, 4, 5, 6]
    minor = [[K[i][j] for j in range(6)] for i in cert_rows]
    r_minor = rank_frac(minor)
    det_minor = None
    try:
        import itertools
        det_minor = _det_frac([[Fraction(K[i][j]) for j in range(6)] for i in cert_rows])
    except Exception as exc:
        det_minor = "err:%s" % exc
    chk("A1a rank_R(K) by Fraction elimination", r_frac == 6 and r_frac == r_machine, "audit=%d machine=%d" % (r_frac, r_machine))
    chk("A1b explicit 6x6 certificate block (rows %s) has rank 6" % cert_rows, r_minor == 6,
        "rank = %d ; det = %s (R19 record: -64)" % (r_minor, det_minor))

    # A2 M1
    W = [tuple(x) for x in res["cells"]["M1"]["numbers"]["witness"]]
    sub = [[K[i][j] for (_i, j) in W] for (i, _j) in W]
    twoI_J = all(sub[i][j] == (1 if i == j else -1) for i in range(5) for j in range(5))
    Mc = [[Fraction(1), Fraction(-1, 5), Fraction(-1, 5)],
          [Fraction(-1, 5), Fraction(1), Fraction(-19, 5)],
          [Fraction(-1, 5), Fraction(-1, 5), Fraction(1)]]
    det = (Mc[0][0] * (Mc[1][1] * Mc[2][2] - Mc[1][2] * Mc[2][1])
           - Mc[0][1] * (Mc[1][0] * Mc[2][2] - Mc[1][2] * Mc[2][0])
           + Mc[0][2] * (Mc[1][0] * Mc[2][1] - Mc[1][1] * Mc[2][0]))
    diagpos = all(Mc[i][i] > 0 for i in range(3))
    offneg = all(Mc[i][j] < 0 for i in range(3) for j in range(3) if i != j)
    # rank-1 sign lemma spot check: sign(u v^T) = sgn(u) sgn(v)^T has rank <= 1
    u = [3, -7, 11, -2]
    v = [-5, 2, 13]
    S = [[1 if (u[i] * v[j]) > 0 else -1 for j in range(3)] for i in range(4)]
    rank1_ok = rank_frac(S) <= 1
    chk("A2a witness submatrix is 2I-J", twoI_J, "5x5 submatrix check")
    chk("A2b counterexample singular with diag>0 offdiag<0", det == 0 and diagpos and offneg,
        "det=%s" % det)
    chk("A2c rank-1 sign lemma (sgn(u_i v_j) factors, rank<=1)", rank1_ok, "rank=%d" % rank_frac(S))
    chk("A2d M1 verdict is the contracted one", res["cells"]["M1"]["verdict"] == "🔴",
        "verdict=%s" % res["cells"]["M1"]["verdict"])

    # A3 M3 -- best certified realization, transposed traversal
    best = None
    for c in res["cells"]["M3"]["numbers"]["candidates"]:
        if c["exact_mismatches"] == 0 and (best is None or c["exact_rank_bound"] < best["exact_rank_bound"]):
            best = c
    if best is None:
        chk("A3a a certified realization exists", False, "none certified")
    else:
        cands = rd("data/40_candidates.json")["candidates"]
        src = [x for x in cands if x["r"] == best["r"] and x["seed"] == best["seed"]][0]
        U, V, r = src["U"], src["V"], src["r"]
        bad = 0
        for j in range(n):
            for i in range(m):
                acc = 0
                for k in range(r - 1, -1, -1):  # transposed traversal, reversed k
                    acc += U[i][k] * V[j][k]
                if acc == 0 or (1 if acc > 0 else -1) != K[i][j]:
                    bad += 1
        rank_U = rank_frac(U)
        rank_V = rank_frac([[V[j][k] for k in range(r)] for j in range(n)])
        chk("A3a certified realization re-verified (transposed traversal)", bad == 0,
            "mismatches=%d over %d signs (r=%d seed=%s)" % (bad, m * n, r, src["seed"]))
        chk("A3b rank bound min(rank U, rank V)", min(rank_U, rank_V) == best["exact_rank_bound"],
            "audit min rank = %d ; machine = %d" % (min(rank_U, rank_V), best["exact_rank_bound"]))
        chk("A3c sign_rank upper bound < 6 (the improvement)", best["exact_rank_bound"] < 6,
            "upper bound = %d" % best["exact_rank_bound"])

    # A4 M4 -- Newton's identities
    phi = None
    # rebuild Phi_88 and G independently
    def polymul(a, b):
        out = [0] * (len(a) + len(b) - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                if x and y:
                    out[i + j] += x * y
        return out

    def polydiv(a, b):
        a = a[:]
        db = len(b) - 1
        q = [0] * (len(a) - db)
        for i in range(len(a) - 1, db - 1, -1):
            c = a[i]
            q[i - db] = c
            for j in range(db + 1):
                a[i - db + j] -= c * b[j]
        return q

    def onehot(nn):
        v = [0] * (nn + 1)
        v[0] = -1
        v[nn] = 1
        return v

    phi = polydiv(polymul(onehot(88), onehot(4)), polymul(onehot(8), onehot(44)))
    dp = len(phi) - 1

    def pmod(a):
        a = a[:]
        while len(a) > dp and any(a[dp:]):
            c = a[-1]
            s0 = len(a) - 1 - dp
            if c:
                for i in range(dp + 1):
                    a[s0 + i] -= c * phi[i]
            while a and a[-1] == 0:
                a.pop()
        return a + [0] * (dp - len(a))

    def rmul(a, b):
        return pmod(polymul(a, b))

    def trace_abs(a):
        tr = 0
        for i in range(dp):
            v = [0] * dp
            v[i] = 1
            tr += rmul(a, v)[i]
        return tr

    G = [0] * dp
    for nn in range(28, 45):
        for e in (nn % 88, (88 - nn) % 88):
            t = [0] * (e + 1)
            t[e] = 1
            red = pmod(t)
            G = [G[k] + red[k] for k in range(dp)]
    units = [a for a in range(1, 44) if all(a % q for q in (2, 11))]
    gals = []
    for a in units:
        out = [0] * dp
        for i, c in enumerate(G):
            if c:
                t = [0] * ((i * a) % 88 + 1)
                t[(i * a) % 88] = c
                red = pmod(t)
                out = [out[k] + red[k] for k in range(dp)]
        gals.append(pmod(out))
    sums = []
    for k in range(1, 21):
        tot = [0] * dp
        for g in gals:
            cur = [0] * dp
            cur[0] = 1
            for _ in range(k):
                cur = rmul(cur, g)
            tot = [tot[t] + cur[t] for t in range(dp)]
        tr = trace_abs(tot)
        if tr % 40:
            sums.append(None)
        else:
            sums.append(tr // 40)
    newton = []
    if all(s is not None for s in sums):
        e = [Fraction(0)] * 21
        e[0] = Fraction(1)
        for k in range(1, 21):
            acc = Fraction(0)
            for i in range(1, k + 1):
                acc += ((-1) ** (i - 1)) * e[k - i] * sums[i - 1]
            e[k] = acc / k
        # P(X) = prod (X - g) = sum_k (-1)^k e_k X^(20-k)
        newton = [int((-1) ** k * e[k]) for k in range(21)]
    machine_coefs = res["cells"]["M4"]["numbers"]["coefficients"]
    chk("A4a power sums p_1..p_20 rational (Newton route)", all(s is not None for s in sums),
        "p_1=%s p_20=%s" % (sums[0], sums[-1]))
    chk("A4b Newton polynomial == machine polynomial", newton == machine_coefs,
        "equal" if newton == machine_coefs else "DIFF: %s vs %s" % (newton[:4], machine_coefs[:4]))
    chk("A4c degree 20 monic integer", len(newton) == 21 and newton[0] == 1, "len=%d lead=%s" % (len(newton), newton[0] if newton else None))

    # A5 M5 via the pinned replay_protocol
    b18 = load(os.path.join(HERE, "18_d6_mapping.py"), "b18_audit")
    b15 = load(os.path.join(HERE, "15_b3r2_orderfair.py"), "b15_audit")
    l6 = rd("data/15_b3r2_results.json")
    oid = (res["cells"]["M5"]["numbers"]["matching_orders"] or l6["order_ids"])[0]
    order = b15.order_list(oid)
    BIG = 10 ** 15
    recs = b18.replay_protocol(order, K, MUL, hx, BIG)
    pushes = sum(r["pushes"] for r in recs)
    hits_pinned = 3 * len(recs) - pushes
    A_pinned = sum(1 for r in recs if r["first_hit"] and r["stored_vs_now"] and r["stored_vs_now"][0] != r["stored_vs_now"][1])
    out_m5 = res["cells"]["M5"]["numbers"]["per_order"][oid]
    chk("A5a pinned-replay hits == machine hits (all 120 states)", hits_pinned == 124
        and out_m5["hits_all_states"] == [124],
        "pinned=%d machine=%s" % (hits_pinned, out_m5["hits_all_states"]))
    chk("A5b class A from pinned stored_vs_now == machine class A", A_pinned == out_m5["s0_zero"][0],
        "pinned=%d machine=%d (R19 record asserted 28)" % (A_pinned, out_m5["s0_zero"][0]))
    po = res["cells"]["M5"]["numbers"]["per_order"]
    all_B_zero = all(v["min_B"] == 0 and v["max_B"] == 0 for v in po.values())
    chk("A5c machine honestly reports the class-B finding (contract criterion A>=1,B>=1 not met)",
        res["cells"]["M5"]["verdict"] == "🔴" and all_B_zero
        and res["cells"]["M5"]["numbers"]["matching_orders"] == [],
        "verdict=%s ; class B == 0 for all %d orders ; matching orders = %s"
        % (res["cells"]["M5"]["verdict"], len(po), res["cells"]["M5"]["numbers"]["matching_orders"]))
    first = l6["order_ids"][0]
    chk("A5d the frozen first order (%s) gives hits = 124 on all 120 states" % first,
        po[first]["hits_all_states"] == [124],
        "first-order hits = %s ; other orders are different passes: %s"
        % (po[first]["hits_all_states"], {k: v["hits_all_states"] for k, v in po.items() if k != first}))

    # A6 M6
    bad = [o for o in l6["order_ids"] if sum(l6["per_order"][o]["per_pair_misses"]) != l6["per_order"][o]["reads_used"]]
    reads = {o: l6["per_order"][o]["reads_used"] for o in l6["order_ids"]}
    mn = min(reads.values())
    argmin = [o for o in reads if reads[o] == mn]
    chk("A6a reads_used == sum(per_pair_misses)", not bad, "bad: %s" % (bad or "none"))
    chk("A6b unique minimum reads_used", len(argmin) == 1 and argmin[0] == "block" and mn == 42,
        "reads=%s min=%d unique=%s" % (reads, mn, argmin))

    # A7 scope
    cells = res["cells"]
    chk("A7a six cells with legal verdicts", set(cells) == {"M1", "M2", "M3", "M4", "M5", "M6"}
        and all(cells[c]["verdict"] in ("✅", "🟡", "🔴") for c in cells), res["verdicts"])
    chk("A7b interval statement present", res["cells"]["M2"]["numbers"]["L_max"] >= 1
        and res["cells"]["M3"]["numbers"]["sign_rank_upper_bound"] <= 6,
        "sign_rank in [%d, %s]" % (res["cells"]["M2"]["numbers"]["L_max"], res["cells"]["M3"]["numbers"]["sign_rank_upper_bound"]))

    payload = {"round": "R20", "audit_of": "scripts/41_r20_closure.py", "checks": checks,
               "pass": "%d/%d" % (sum(1 for c in checks if c["pass"]), len(checks))}
    with open(os.path.join(DATA, "42_r20_audit.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print("-" * 100)
    print("AUDIT %s" % payload["pass"])
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
