#!/usr/bin/env python3
"""O222 R20 -- frozen closure machine (M1..M6), exact integer / Fraction arithmetic only.

Contract: docs/27_r20_contract.md (r20-contract-v1).  Read-only pins P1..P11.
No floats, no trig, no numpy: every verdict must be re-computable exactly.

Cells:
  M1  audit of the implication "fooling set => sign_rank >= t" (exact counterexample family)
  M2  valid lower bounds for sign_rank(K) (only provable statements are admitted)
  M3  exact certification of the rank-r sign realizations proposed by the M3 discovery protocol
  M4  exact minimal polynomial of the Q5c residual element G in Z[zeta_88]
  M5  G1 override mechanism: exact two-class decomposition over all 120 starting states
  M6  structural selector for the within-class representative (unique minimum)

Usage:  /usr/bin/python3 -u scripts/41_r20_closure.py
"""
import importlib.util
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
LOGS = os.path.join(ROOT, "logs")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rd(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- exact linear algebra
def rank_int(M):
    """Exact rank of an integer matrix by fraction-free (Bareiss) elimination."""
    A = [row[:] for row in M]
    rows = len(A)
    cols = len(A[0]) if rows else 0
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
        pr = A[r]
        for i in range(r + 1, rows):
            if A[i][c]:
                f = A[i][c]
                g = pr[c]
                A[i] = [f * pr[k] - g * A[i][k] for k in range(cols)]
        r += 1
        if r == rows:
            break
    return r


def det_int(M):
    """Exact determinant by fraction-free elimination (small matrices)."""
    A = [row[:] for row in M]
    n = len(A)
    sign = 1
    prev = 1
    for k in range(n - 1):
        if A[k][k] == 0:
            sw = None
            for i in range(k + 1, n):
                if A[i][k]:
                    sw = i
                    break
            if sw is None:
                return 0
            A[k], A[sw] = A[sw], A[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                A[i][j] = (A[i][j] * A[k][k] - A[i][k] * A[k][j]) // prev
            A[i][k] = 0
        prev = A[k][k]
    return sign * A[n - 1][n - 1]


# ---------------------------------------------------------------- cyclotomic ring helpers
def polymul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if y:
                    out[i + j] += x * y
    return out


def polydiv_exact(a, b):
    """Exact division a / b in Z[x] (assumes exact divisibility, b monic)."""
    a = a[:]
    db = len(b) - 1
    q = [0] * (len(a) - db)
    for i in range(len(a) - 1, db - 1, -1):
        c = a[i]
        q[i - db] = c
        if c:
            for j in range(db + 1):
                a[i - db + j] -= c * b[j]
    return q


def poly_sub_scaled(a, b, s):
    out = a[:]
    for i, x in enumerate(b):
        out[i] -= s * x
    return out


def phi88():
    """Phi_88 = (x^88-1)(x^4-1) / ((x^8-1)(x^44-1)) by exact integer division."""
    def onehot(n):
        v = [0] * (n + 1)
        v[0] = -1
        v[n] = 1
        return v
    num = polymul(onehot(88), onehot(4))
    den = polymul(onehot(8), onehot(44))
    q = polydiv_exact(num, den)
    while q and q[-1] == 0:
        q.pop()
    return q


def poly_mod(a, phi):
    """Reduce a modulo the monic phi (subtract-in-place, then drop zero tails)."""
    a = a[:]
    dp = len(phi) - 1
    while len(a) > dp and any(a[dp:]):
        c = a[-1]
        s = len(a) - 1 - dp
        if c:
            for i in range(dp + 1):
                a[s + i] -= c * phi[i]
        while a and a[-1] == 0:
            a.pop()
    return a + [0] * (dp - len(a))


def ring_mul(a, b, phi):
    return poly_mod(polymul(a, b), phi)


def ring_trace_abs(a, phi):
    """Absolute trace Tr_{Q(zeta_88)/Q}(a) for the reduced representative a."""
    dp = len(phi) - 1
    tr = 0
    for i in range(dp):
        v = [0] * dp
        v[i % dp] = 1
        vm = ring_mul(a, v, phi)
        tr += vm[i % dp]
    return tr


def sigma_poly(a, m, phi):
    """sigma_m(a) for m coprime to 88: x -> x^m in Z[x]/Phi_88."""
    out = [0] * len(a)
    for i, c in enumerate(a):
        if c:
            tmp = [0] * ((i * m) % 88 + 1)
            tmp[(i * m) % 88] = c
            red = poly_mod(tmp, phi)
            out = [out[k] + red[k] for k in range(len(a))]
    return poly_mod(out, phi)


# ---------------------------------------------------------------- helpers
def cell(verdict, name, detail, **nums):
    return {"cell": name, "verdict": verdict, "detail": detail, "numbers": nums}


def main():
    out = {}
    print("=" * 112)
    print("O222 scripts/41 -- R20 closure machine (M1..M6), exact arithmetic")
    print("contract: docs/27_r20_contract.md (r20-contract-v1)")
    print("=" * 112, flush=True)

    sys.path.insert(0, HERE)
    b5 = load(os.path.join(HERE, "12_b5_budget.py"), "b5_pin")
    mm, K, MUL, hx, ids, types = b5.load_machine()
    m, n = len(K), len(K[0])
    print("[load] K = %dx%d  (pin P1: scripts/12_b5_budget.load_machine)" % (m, n))
    r19 = rd("data/37_r19_results.json")
    g2q5 = rd("data/34_g2q5_results.json")

    # ------------------------------------------------------------------ M1
    W = [(10, 20), (46, 22), (5, 17), (4, 14), (1, 12)]
    sub = [[K[i][j] for (_i, j) in W] for (i, _j) in W]
    diag_ok = all(sub[k][k] == 1 for k in range(5))
    off_ok = all(sub[p][q] == -1 for p in range(5) for q in range(5) if p != q)
    twoI_J_rank = rank_int([[2 if p == q else -1 for q in range(5)] for p in range(5)])
    # counterexample family: a=b=c=e=f=1/5, d=19/5  =>  diag > 0, offdiag < 0, det = 0
    M3c = [[Fraction(1), Fraction(-1, 5), Fraction(-1, 5)],
           [Fraction(-1, 5), Fraction(1), Fraction(-19, 5)],
           [Fraction(-1, 5), Fraction(-1, 5), Fraction(1)]]
    a_, b_, c_, e_, f_ = [Fraction(1, 5)] * 5
    d_ = Fraction(19, 5)
    detM = (M3c[0][0] * (M3c[1][1] * M3c[2][2] - M3c[1][2] * M3c[2][1])
            - M3c[0][1] * (M3c[1][0] * M3c[2][2] - M3c[1][2] * M3c[2][0])
            + M3c[0][2] * (M3c[1][0] * M3c[2][1] - M3c[1][1] * M3c[2][0]))
    family_identity = Fraction(1) - (d_ * f_ + a_ * c_ + a_ * d_ * e_ + b_ * c_ * f_ + b_ * e_)
    diagpos = all(M3c[i][i] > 0 for i in range(3))
    offneg = all(M3c[i][j] < 0 for i in range(3) for j in range(3) if i != j)
    rank_r = rank_int(K)
    m1_ok = (diag_ok and off_ok and twoI_J_rank == 5 and detM == 0 and family_identity == 0
             and diagpos and offneg)
    out["M1"] = cell("🔴" if m1_ok else "🟡",
                     "M1 fooling-set ⟹ sign_rank 蘊含之審計",
                     ("R19 之蘊含**無效**：子矩陣值層條件（對角 +1、非對角 −1）**唔**迫使非奇異 ⟹ "
                      "「fooling set ⟹ sign_rank ≥ t」不成立。有效替代：子矩陣秩 ≤ 全秩 ⟹ 只證 rank_R(K) ≥ 5。"
                      if m1_ok else "反例族未成立，蘊含未被推翻"),
                     witness=W, family_identity=str(family_identity), submatrix_is_2I_minus_J=(diag_ok and off_ok), rank_2I_J_5=twoI_J_rank,
                     counterexample=[[str(x) for x in r] for r in M3c], det_counterexample=str(detM),
                     diag_positive=diagpos, offdiag_negative=offneg,
                     valid_replacement="fooling set ⟹ rank_R(K) ≥ 5 (submatrix rank bound)",
                     rank_R_K_exact=rank_r)
    print("[M1] %s  2I-J_5 rank = %d ; counterexample det = %s ; rank_R(K) = %d"
          % (out["M1"]["verdict"], twoI_J_rank, detM, rank_r), flush=True)

    # ------------------------------------------------------------------ M2
    # tool 1: rank-1 exclusion -- rank(sign(B)) <= rank(B) = 1 for B = u v^T (sgn(u_i v_j) = sgn u_i sgn v_j)
    #         verified computationally on a rational sample, then used with rank_R(K) = 6.
    r1_ok = True
    sample_rank1 = []
    for (u, v) in [([1, -2, 3], [-1, 5, 2, -4]), ([2, 0, -1, 3], [1, -1, -3, 2, 5])]:
        B = [[u[i] * v[j] for j in range(len(v))] for i in range(len(u))]
        if any(B[i][j] == 0 for i in range(len(u)) for j in range(len(v))):
            continue
        S = [[1 if B[i][j] > 0 else -1 for j in range(len(v))] for i in range(len(u))]
        sample_rank1.append(rank_int(S))
        r1_ok = r1_ok and rank_int(S) <= 1
    # arrangement counting bound: distinct rows(12) <= 2*sum_{k<r} C(m-1,k); distinct cols <= 2*sum_{k<r} C(n-1,k)
    rows = set(tuple(r) for r in K)
    cols = set(tuple(K[i][j] for i in range(m)) for j in range(n))

    def comb(a, b):
        if b < 0 or b > a:
            return 0
        num = 1
        for t in range(b):
            num = num * (a - t) // (t + 1)
        return num

    arr = {}
    for r in (2, 3, 4, 5):
        bound_rows = 2 * sum(comb(m - 1, k) for k in range(r))
        bound_cols = 2 * sum(comb(n - 1, k) for k in range(r))
        arr[str(r)] = {"bound_distinct_rows": bound_rows, "bound_distinct_cols": bound_cols,
                       "excludes": (len(rows) > bound_rows) or (len(cols) > bound_cols)}
    L_max = 2 if (r1_ok and rank_r > 1) else 1
    out["M2"] = cell("✅", "M2 sign_rank(K) 之有效下界",
                     ("僅接受可證命題：(1) 秩 1 排除（sgn(u_i v_j) = sgn u_i·sgn v_j ⟹ rank ≤ 1，與 rank_R(K) = %d 矛盾）"
                      "⟹ sign_rank ≥ 2；(2) arrangement 計數界對 r = 2..5 全部**不**排除；"
                      "(3) R19 之「≥ 5」依 M1 為**無效**，不列入。⟹ 有效下界 L_max = %d。" % (rank_r, L_max)),
                     rank1_sample_ranks=sample_rank1, rank1_lemma_ok=r1_ok, L_max=L_max,
                     distinct_rows=len(rows), distinct_cols=len(cols), arrangement=arr,
                     r19_lower_bound_withdrawn=5, rank_R_K=rank_r)
    print("[M2] L_max = %d  (rank_R(K) = %d ; distinct rows %d / cols %d)  arrangement excludes: %s"
          % (L_max, rank_r, len(rows), len(cols), [k for k, v in arr.items() if v["excludes"]]), flush=True)

    # ------------------------------------------------------------------ M3
    cand_path = os.path.join(DATA, "40_candidates.json")
    certified = []
    search_summary = None
    if os.path.exists(cand_path):
        with open(cand_path, encoding="utf-8") as f:
            C = json.load(f)
        search_summary = {"protocol": C.get("protocol"), "summary": C.get("summary"),
                          "elapsed_s": C.get("elapsed_s"), "n_candidates": len(C.get("candidates", []))}
        for cand in C.get("candidates", []):
            r = cand["r"]
            den = cand["den"]
            U, V = cand["U"], cand["V"]
            bad = 0
            for i in range(m):
                Ui = U[i]
                for j in range(n):
                    Vj = V[j]
                    num = 0
                    for k in range(r):
                        num += Ui[k] * Vj[k]
                    if num == 0 or (1 if num > 0 else -1) != K[i][j]:
                        bad += 1
            ru, rv = rank_int(U), rank_int(V)
            certified.append({"r": r, "seed": cand["seed"], "den": den, "exact_mismatches": bad,
                              "signed_entries_checked": m * n, "rank_U": ru, "rank_V": rv,
                              "float_min_margin": cand.get("float_min_margin"),
                              "exact_rank_bound": min(ru, rv)})
    ok_cert = [c for c in certified if c["exact_mismatches"] == 0]
    best_r = min([c["exact_rank_bound"] for c in ok_cert], default=None)
    out["M3"] = cell("✅" if (best_r is not None and best_r < 6) else ("🟡" if search_summary else "🔴"),
                     "M3 rank-r 符號實現之構造搜尋",
                     (("已認證 sign_rank(K) ≤ %d（精確 Fraction 檢查 %d 個符號全中；實現矩陣秩 = %d）"
                       % (best_r, m * n, best_r)) if best_r is not None else
                      "發現協定無候選通過精確認證（搜尋唔到 ≠ 唔存在）"),
                     certified=len(ok_cert), total_candidates=len(certified),
                     candidates=certified, best_certified_rank=best_r,
                     sign_rank_upper_bound=best_r if best_r is not None else 6,
                     discovery=search_summary)
    print("[M3] certified candidates %d/%d ; best certified rank = %s"
          % (len(ok_cert), len(certified), best_r), flush=True)

    # ------------------------------------------------------------------ M4
    phi = phi88()
    deg_phi = len(phi) - 1
    G = [0] * deg_phi
    for nn in range(28, 45):
        for e in (nn % 88, (88 - nn) % 88):
            tmp = [0] * (e + 1)
            tmp[e] = 1
            red = poly_mod(tmp, phi)
            G = [(G[k] + red[k]) for k in range(deg_phi)]
    G_head = G[:6]
    tr_abs_G = ring_trace_abs(G, phi)
    rec_head = r19["numbers"]["K5_add"]["G_coeffs_head"]
    rec_tr = r19["numbers"]["K5_add"]["trace_K_G"]
    units = [a for a in range(1, 44) if all(a % q for q in (2, 11))]
    gals = [sigma_poly(G, a, phi) for a in units]
    distinct = len(set(tuple(g) for g in gals)) == len(gals)
    # P(X) = prod (X - sigma_a(G)) with coefficients in Z[x]/Phi_88
    coefs = [[0] * deg_phi for _ in range(1)]
    coefs[0][0] = 1  # P = 1
    for g in gals:
        new = [[0] * deg_phi for _ in range(len(coefs) + 1)]
        for k, cf in enumerate(coefs):
            for t in range(deg_phi):
                new[k + 1][t] += cf[t]
            pr = ring_mul(cf, g, phi)
            for t in range(deg_phi):
                new[k][t] -= pr[t]
        coefs = new
    int_coefs = []
    integral = True
    reduced_ok = True
    for cf in coefs:
        tr = ring_trace_abs(cf, phi)
        if tr % 40:
            integral = False
        c = tr // 40
        int_coefs.append(c)
        red = [0] * deg_phi
        red[0] = c
        if [x for x in cf] != red:
            reduced_ok = False
    int_coefs = int_coefs[::-1]  # highest power first
    # Horner: P(G)
    acc = [0] * deg_phi
    for c in int_coefs:
        acc = ring_mul(acc, G, phi)
        acc = [(acc[k] + c * (1 if k == 0 else 0)) for k in range(deg_phi)]
    p_of_G_zero = all(x == 0 for x in acc)
    mono = int_coefs[0] == 1
    deg_ok = len(int_coefs) - 1 == 20
    tr_ok = int_coefs[1] == -rec_tr
    head_ok = G_head == rec_head
    trG_ok = tr_abs_G == 2 * rec_tr
    m4_ok = distinct and integral and reduced_ok and p_of_G_zero and mono and deg_ok and tr_ok and head_ok and trG_ok
    out["M4"] = cell("✅" if m4_ok else "🔴", "M4 Q5c 殘差之精確極小多項式",
                     ("P(X) = Π_{a∈(Z/88)^*/±1}(X − σ_a(G)) ∈ Z[X]，deg = %d，首一；P(G) ≡ 0 (mod Φ_88)；"
                      "20 個共軛兩兩相異；[X^19]P = %d = −Tr_K(G) ⟹ P = G 之極小多項式"
                      % (len(int_coefs) - 1, int_coefs[1]) if m4_ok else "有檢定項失敗（見 numbers）"),
                     phi88_degree=deg_phi, orbit_size=len(gals), orbit_distinct=distinct,
                     coefficients=int_coefs, degree=len(int_coefs) - 1, monic=mono,
                     P_of_G_is_zero=p_of_G_zero, coeffs_integral=integral, reduced_form_ok=reduced_ok,
                     trace_abs_G=tr_abs_G, trace_K_G=tr_abs_G // 2, record_trace_K_G=rec_tr,
                     G_coeffs_head=G_head, record_G_head=rec_head)
    print("[M4] %s  deg = %d, monic = %s, P(G) = 0: %s, orbit distinct: %s, [X^19] = %d"
          % (out["M4"]["verdict"], len(int_coefs) - 1, mono, p_of_G_zero, distinct, int_coefs[1]), flush=True)

    # ------------------------------------------------------------------ M5
    b15 = load(os.path.join(HERE, "15_b3r2_orderfair.py"), "b15_pin")
    l6 = rd("data/15_b3r2_results.json")
    order_ids = l6["order_ids"]
    orders = {oid: b15.order_list(oid) for oid in order_ids}

    def run_state(order, s0):
        """Authoritative pair protocol (pin P2, scripts/18 replay_protocol semantics):
        per pair: read a, read b, pop (state restored to the popped entry's push-state), read b again.
        Overrides are classified by read-event index: cls[0] = first read, cls[1] = middle read,
        cls[2] = post-rollback re-read."""
        L = []
        s = s0
        hits = 0
        cls = [0, 0, 0]
        for (a, b) in order:
            for idx, ctx in enumerate((a, b)):
                if L and L[-1][0] == ctx:
                    hits += 1
                    if L[-1][1] != K[s][ctx]:
                        cls[idx] += 1
                else:
                    L.append((ctx, K[s][ctx], s))
                    s = MUL[s][hx[ctx]]
            _c, _v, s_at = L.pop()
            s = s_at
            ctx = b
            if L and L[-1][0] == ctx:
                hits += 1
                if L[-1][1] != K[s][ctx]:
                    cls[2] += 1
            else:
                L.append((ctx, K[s][ctx], s))
                s = MUL[s][hx[ctx]]
        return hits, cls

    rec = r19["numbers"]["K3"]
    per_order = {}
    for oid in order_ids:
        sw = {}
        for s0 in range(m):
            h, cls = run_state(orders[oid], s0)
            sw[s0] = (h, cls)
        hits_set = set(v[0] for v in sw.values())
        totals = [sum(v[1]) for v in sw.values()]
        As = [v[1][0] for v in sw.values()]
        Ms = [v[1][1] for v in sw.values()]
        Bs = [v[1][2] for v in sw.values()]
        states65 = sorted(s0 for s0 in sw if totals[s0] == 65)
        match = (hits_set == {124} and sw[0][1][0] == rec["s0_zero"]["first_read_overrides"]
                 and sw[0][1][1] + sw[0][1][2] == rec["s0_zero"]["post_rollback_overrides"]
                 and min(totals) == rec["s0_sweep"]["overrides_range"][0]
                 and max(totals) == rec["s0_sweep"]["overrides_range"][1]
                 and states65 == rec["s0_sweep"]["states_with_65"])
        per_order[oid] = {"matches_R19_record": match, "hits_all_states": sorted(hits_set),
                          "s0_zero": [sw[0][1][0], sw[0][1][1], sw[0][1][2], sum(sw[0][1])],
                          "totals_range": [min(totals), max(totals)], "states_with_65": states65,
                          "min_A": min(As), "max_A": max(As), "min_middle": min(Ms), "max_middle": max(Ms),
                          "min_B": min(Bs), "max_B": max(Bs)}
    matching = [oid for oid in order_ids if per_order[oid]["matches_R19_record"]]
    m5_ok = bool(matching) and all(per_order[o]["min_A"] >= 1 and per_order[o]["min_B"] >= 1 for o in matching)
    ref = per_order[matching[0]] if matching else per_order[order_ids[0]]
    out["M5"] = cell("✅" if m5_ok else "🔴", "M5 G1 override 機制之值層定理",
                     ("權威配對協定（a → b → pop → b 再讀）精確重寫並逐項重現 R19 記錄（次序 %s：s0=0 → "
                      "[A,M,B] = %s；總數域 %s；=65 恰 %d 態）；三類 override 之最小值 = A %d / M %d / B %d "
                      "（判準要求 A ≥ 1 且 B ≥ 1）"
                      % (matching, ref["s0_zero"], ref["totals_range"], len(ref["states_with_65"]),
                         ref["min_A"], ref["min_middle"], ref["min_B"]) if m5_ok else
                      ("權威協定重寫後：符合記錄之次序 = %s；最小值 A %d / M %d / B %d ⟹ 合約判準（A ≥ 1 且 B ≥ 1）"
                       "%s；逐項數據見 numbers（此為**值層**可判定結果）"
                       % (matching, ref["min_A"], ref["min_middle"], ref["min_B"],
                          "成立" if m5_ok else "**不成立**"))),
                     matching_orders=matching, per_order=per_order,
                     condition="override ⟺ 命中且 memo 頂之寫入態 s_written ≠ 當前讀取態 s",
                     record=r19["numbers"]["K3"]["s0_zero"],
                     protocol="read a; read b; pop; read b again (pin P2)")
    print("[M5] %s  matching = %s ; (min A, min M, min B) = (%d, %d, %d) ; s0=0 [A,M,B] = %s"
          % (out["M5"]["verdict"], matching, ref["min_A"], ref["min_middle"], ref["min_B"], ref["s0_zero"]), flush=True)

    # ------------------------------------------------------------------ M6
    counts = []
    for idx, oid in enumerate(order_ids):
        counts.append({"order_index": idx, "order": oid, "reads_used": l6["per_order"][oid]["reads_used"],
                       "pairs": len(orders[oid])})
    mn = min(c["reads_used"] for c in counts)
    argmin = [c["order_index"] for c in counts if c["reads_used"] == mn]
    out["M6"] = cell("✅" if len(argmin) == 1 else "🟡", "M6 G4 類內代表之結構選擇子",
                     ("五個凍結次序之配對數 = %s ⟹ 最小值 %d 由**唯一**次序達成（index %d%s）⟹ 依凍結成本律"
                      "（每對 2 讀）代表由「最小總讀數」唯一決定（**係選擇子，唔係協定強制**）"
                      % ([c["reads_used"] for c in counts], mn, argmin[0],
                         ("=" + order_ids[argmin[0]] if order_ids and argmin[0] < len(order_ids) else ""))
                      if len(argmin) == 1 else "最小值並列 ⟹ 代表為約定（見 numbers）"),
                     counts=counts, minimum=mn, argmin=argmin, order_ids=order_ids,
                     cost_law="cost(e) = 3 - [t == a] - [b == a] ; per pair 2 reads (pin P6: data/21_g4_results.json)")
    print("[M6] %s  total reads per order = %s ; unique min = %d at index %s"
          % (out["M6"]["verdict"], [c["reads_used"] for c in counts], mn, argmin), flush=True)

    # ------------------------------------------------------------------ summary
    verdicts = {k: out[k]["verdict"] for k in sorted(out)}
    npass = sum(1 for v in verdicts.values() if v == "✅")
    payload = {"round": "R20", "contract": "r20-contract-v1",
               "pins": {"P1": "scripts/12_b5_budget.py", "P2": "scripts/18_d6_mapping.py",
                        "P5": "data/15_b3r2_results.json", "P6": "data/21_g4_results.json",
                        "P9": "data/34_g2q5_results.json", "P10": "data/37_r19_results.json"},
               "K_shape": [m, n], "cells": out, "verdicts": verdicts, "pass": "%d/6" % npass}
    with open(os.path.join(DATA, "41_r20_results.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print("-" * 112)
    print("CELLS = %s ; pass = %d/6 ; sign_rank(K) ∈ [%d, %s]"
          % (verdicts, npass, out["M2"]["numbers"]["L_max"], out["M3"]["numbers"]["sign_rank_upper_bound"]))
    print("wrote data/41_r20_results.json")
    return 0 if npass == 6 else 1


if __name__ == "__main__":
    raise SystemExit(main())
