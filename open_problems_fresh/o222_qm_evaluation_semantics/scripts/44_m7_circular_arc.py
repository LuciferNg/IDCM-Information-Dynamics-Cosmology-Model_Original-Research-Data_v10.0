#!/usr/bin/env python3
"""O222 R20/M7 -- combinatorial exclusion of rank-2 sign realizations (contract docs/29_r20_m7_contract.md).

Lemma (proved in the contract): a rank-2 realization forces, for every column j, the +1 set over the 12 distinct
row classes to be a contiguous ARC in the circular order of those classes.  Hence:

    no common cyclic order making all 62 (+1)-sets arcs  =>  no rank-2 realization  =>  sign_rank(K) >= 3

combined with the certified upper bound sign_rank(K) <= 3 it yields sign_rank(K) = 3 exactly.

Exact integer arithmetic only (stdlib); controls are mandatory (a decider without a passing control is void).
Usage: /usr/bin/python3 -u scripts/44_m7_circular_arc.py
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
NODE_CAP = 5000000


def load_K():
    spec = importlib.util.spec_from_file_location("b5_m7", os.path.join(HERE, "12_b5_budget.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    _mm, K, MUL, hx, _ids, _types = m.load_machine()
    return K


def lcg(seed):
    x = seed & 0xFFFFFFFFFFFFFFFF

    def nxt():
        nonlocal x
        x = (6364136223846793005 * x + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
        return x
    return nxt


def classes_of(K):
    seen = {}
    classes = []
    for row in K:
        t = tuple(row)
        if t not in seen:
            seen[t] = len(classes)
            classes.append(t)
    return classes


def plus_sets(classes):
    m = len(classes)
    n = len(classes[0])
    return [frozenset(i for i in range(m) if classes[i][j] == 1) for j in range(n)]


def partial_ok(order, sets, m):
    """Necessary condition for the prefix `order` (positions 0..L-1) to be extendable to a valid circular order."""
    pos = {c: k for k, c in enumerate(order)}
    L = len(order)
    done = (L == m)
    for S in sets:
        ps = sorted(pos[i] for i in S if i in pos)
        if not ps or len(ps) == len(S):
            continue
        blocks = []
        start = prev = ps[0]
        for p in ps[1:]:
            if p == prev + 1:
                prev = p
            else:
                blocks.append((start, prev))
                start = prev = p
        blocks.append((start, prev))
        merged = False
        if len(blocks) == 2 and blocks[-1][1] == L - 1 and blocks[0][0] == 0:
            merged = True  # prefix block + suffix block merge across the wrap
        if len(blocks) > 1 and not merged:
            return False
        if merged:
            continue
        if done:
            continue
        a, b = blocks[0]
        # a single block is extendable iff at least one of its two circular neighbours is still unplaced
        left = (a - 1) % m
        right = (b + 1) % m
        left_placed = left < L
        right_placed = right < L
        left_blocked = left_placed and order[left] not in S
        right_blocked = right_placed and order[right] not in S
        if left_blocked and right_blocked:
            return False                      # sealed on both sides, yet elements remain
    return True


def find_order(classes, sets, cap=NODE_CAP):
    m = len(classes)
    order = [0]
    used = {0}
    nodes = [0]

    def dfs(L):
        nodes[0] += 1
        if nodes[0] > cap:
            raise RuntimeError("node cap reached")
        if L == m:
            return verify_order(order, sets, m) == 0   # strict final check: only truly arc-consistent orders
        for c in range(m):
            if c in used:
                continue
            order.append(c)
            used.add(c)
            if partial_ok(order, sets, m) and dfs(L + 1):
                return True
            used.discard(c)
            order.pop()
        return False

    try:
        ok = dfs(1)
    except RuntimeError:
        return None, nodes[0], order[:]
    return (order[:] if ok else False), nodes[0], order[:]


def _is_circ_interval(ps, m):
    if not ps or len(ps) == m:
        return True
    runs = 1
    for k in range(1, len(ps)):
        if ps[k] != ps[k - 1] + 1:
            runs += 1
    if ps[0] == 0 and ps[-1] == m - 1:
        runs -= 1
    return runs <= 1


def verify_order(order, sets, m):
    """count columns whose (+1) set is NOT a circular interval of the given order (0 = valid order)."""
    pos = {c: k for k, c in enumerate(order)}
    bad = 0
    for S in sets:
        ps = sorted(pos[i] for i in S)
        if not _is_circ_interval(ps, m):
            bad += 1
    return bad


def control_rank2(seed, npts=12, ndirs=62, scale=1000):
    """A genuine rank-2 realizable pattern: points and lines in R^2, integer coordinates."""
    rnd = lcg(seed)
    pts = []
    while len(pts) < npts:
        x = ((rnd() >> 21) % (2 * scale + 1)) - scale
        y = ((rnd() >> 21) % (2 * scale + 1)) - scale
        if x or y:
            pts.append((x, y))
    dirs = []
    while len(dirs) < ndirs:
        x = ((rnd() >> 21) % (2 * scale + 1)) - scale
        y = ((rnd() >> 21) % (2 * scale + 1)) - scale
        if x or y:
            dirs.append((x, y))
    K2 = []
    for (px, py) in pts:
        row = []
        for (vx, vy) in dirs:
            d = px * vx + py * vy
            row.append(1 if d > 0 else (-1 if d < 0 else 0))
        K2.append(row)
    return K2


def control_random(seed, npts=12, ndirs=62):
    rnd = lcg(seed)
    return [[1 if ((rnd() >> 33) & 1) else -1 for _ in range(ndirs)] for _ in range(npts)]


def main():
    out = {}
    print("=" * 110)
    print("O222 scripts/44 -- M7 rank-2 exclusion by circular-arc consistency (contract docs/29_r20_m7_contract.md)")
    print("=" * 110, flush=True)

    # --- controls first (a decider is void without them)
    c1 = []
    for s in (11, 2222):
        K2 = control_rank2(s)
        if any(0 in row for row in K2):
            c1.append(("degenerate", None))
            continue
        cl = classes_of(K2)
        res, nodes, _ = find_order(cl, plus_sets(cl))
        c1.append((res, nodes))
    c2 = []
    for s in (33, 4444):
        K3 = control_random(s)
        cl = classes_of(K3)
        res, nodes, _ = find_order(cl, plus_sets(cl))
        c2.append((res, nodes))
    c1_ok = all(isinstance(r, list) for r, _ in c1) and all(r is not False for r, _ in c1)
    c2_ok = all(r in (False, None) for r, _ in c2)
    print("[CTRL C1] rank-2 realizable targets  -> PASS expected : %s" % [(type(r).__name__ if r is not False and r is not None else r, nd) for r, nd in c1])
    print("[CTRL C2] random +-1 targets         -> FAIL expected : %s" % [(r, nd) for r, nd in c2])
    print("[CTRL] decider valid = %s" % (c1_ok and c2_ok), flush=True)
    out["controls"] = {"C1_rank2_targets": [[("order" if isinstance(r, list) else r), nd] for r, nd in c1],
                       "C2_random_targets": [[r, nd] for r, nd in c2], "decider_valid": bool(c1_ok and c2_ok)}
    if not (c1_ok and c2_ok):
        print("!! decider invalid -- M7 verdict withheld !!")
        with open(os.path.join(DATA, "44_m7_results.json"), "w", encoding="utf-8") as f:
            json.dump({"verdict": "VOID (controls failed)", "controls": out["controls"]}, f, ensure_ascii=False, indent=1)
        return 1

    # --- the real instance
    K = load_K()
    classes = classes_of(K)
    sets = plus_sets(classes)
    m = len(classes)
    res, nodes, _ = find_order(classes, sets)
    ncols = len(sets)
    if isinstance(res, list):
        bad = verify_order(res, sets, m)
        verdict = "✅ 存在共同圓序（秩 2 未被此必要條件排除；**唔算證明**）"
        out["verdict"] = "✅ arc-consistent"
        out["order"] = res
        out["violating_columns"] = bad
        print("[M7] ✅ common cyclic order found (nodes %d): %s ; violating columns %d" % (nodes, res, bad))
    else:
        exhausted = (res is False)
        verdict = ("🔴 窮盡而無共同圓序 ⟹ **秩 2 實現不可能** ⟹ `sign_rank(K) ≥ 3`；配合已認證上界 3 ⟹ "
                   "**sign_rank(K) = 3 EXACT**" if exhausted else "🟡 節點上限未窮盡（不可下任何結論）")
        out["verdict"] = "🔴 rank-2 impossible (search exhausted)" if exhausted else "🟡 node cap reached"
        print("[M7] %s  nodes = %d" % (out["verdict"], nodes))
    out.update({"classes": m, "columns": ncols, "nodes": nodes, "search_exhausted": bool(res is False),
                "statement": verdict, "rows_deduplicated_from": len(K)})
    with open(os.path.join(DATA, "44_m7_results.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("-" * 110)
    print(verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
