#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O222 scripts/04_b2_contract.py  —  B2 / B1 / B4 CONTRACT ENFORCER (Contract v1)

跑得到 = 合約有效；任何 [FAIL] = 禁止跑 scripts/05_b2_correlation.py。
本檔必須在【任何 C(theta) 數字存在之前】執行一次，並把 hash 寫入 data/04_b2_freeze.json。

做四件事:
  (1) L-SET   : 由 R1 規則導出 62 條晶格原生軸 -> setting 表 + 全部 3844 有序對之精確 cos^2 (Q(sqrt5))
                + DEV(144) / BLIND(3700) 分割 + SHA-256 承諾
  (2) L-ZERO  : AST 硬掃描 —— kernel 作用域禁 cos/sin/tan/pi/sqrt/exp/log、禁 numpy/scipy/math、
                禁非整數浮點字面值 (強制 Fraction 精確算術)。附陽性/陰性對照自測。
  (3) L-CAUSAL: P1 結構驗證 —— 單翼 marginal 必須 EXACT 1/2（二十面體中心對稱 6/6 + 軌道重數均勻），
                呢個係 no-signalling 嘅結構推導，唔係假設; 另做因子表局部性靜態檢查 (需 --freeze-impl)。
  (4) 閘      : 若 scripts/05_b2_correlation.py 存在但未登記 impl hash -> FAIL（未凍結之實作）。
                反之打印 [WAITING]。

慣例標籤: [L-SET] [L-ZERO] [L-CAUSAL] [blind] [hash] [WAITING] [contract]
"""

import ast
import hashlib
import io
import itertools
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
SCRIPTS = os.path.join(ROOT, "scripts")
DOC = os.path.join(ROOT, "docs", "03_b2_contract.md")
os.makedirs(DATA, exist_ok=True)

HKT = timezone(timedelta(hours=8))
RESULTS = []


def chk(tag, name, ok, detail=""):
    RESULTS.append({"tag": tag, "name": name, "ok": bool(ok), "detail": detail})
    print("[%s] %-11s %-74s %s" % ("PASS" if ok else "FAIL", tag, name, detail))
    return ok


def claim(tag, name, text):
    RESULTS.append({"tag": tag, "name": name, "ok": None, "detail": text})
    print("[CLAIM] %-11s %-74s %s" % (tag, name, text))


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def sha256_text(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


# ================================================================ exact Q(sqrt5)
ZERO, ONE = (F(0), F(0)), (F(1), F(0))


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
    if d == 0:
        raise ZeroDivisionError("non-invertible element of Q(sqrt5)")
    return (x[0] / d, -x[1] / d)


def num_sign(x):
    """EXACT sign of p + q*sqrt5 (no floats, no sqrt)."""
    p, q = x
    if p == 0 and q == 0:
        return 0
    if q == 0:
        return 1 if p > 0 else -1
    if p == 0:
        return 1 if q > 0 else -1
    if p > 0 and q > 0:
        return 1
    if p < 0 and q < 0:
        return -1
    if p > 0 and q < 0:
        return 1 if p * p > 5 * q * q else -1
    return 1 if 5 * q * q > p * p else -1


def scale(x, k):
    return (x[0] * F(k), x[1] * F(k))


PHI = (F(1, 2), F(1, 2))
PSI = sub(PHI, ONE)


def dot(a, b):
    return add(add(mul(a[0], b[0]), mul(a[1], b[1])), mul(a[2], b[2]))


def norm2(a):
    return dot(a, a)


def dir_canon(v):
    for x in v:
        if x != ZERO:
            return tuple(mul(inv(x), y) for y in v)
    raise ValueError("zero vector")


def vkey_num(v):
    return [[str(y[0]), str(y[1])] for y in v]


# ================================================================ the R1 group (recomputed, zero-import)
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
    gens += [(scale(ONE, s), ZERO, ZERO, ZERO), (ZERO, scale(ONE, s), ZERO, ZERO),
             (ZERO, ZERO, scale(ONE, s), ZERO), (ZERO, ZERO, ZERO, scale(ONE, s))]
for s1 in (1, -1):
    for s2 in (1, -1):
        for s3 in (1, -1):
            gens.append((scale(ONE, F(s1, 2)), scale(ONE, F(s2, 2)), scale(ONE, F(s3, 2)),
                         scale(ONE, F(s1 * s2 * s3, 2))))
gens.append((scale(PHI, F(1, 2)), scale(ONE, F(1, 2)), scale(PSI, F(1, 2)), ZERO))

G2I = set(gens)
frontier, CAP = list(G2I), 20000
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


def order_of(M):
    k, X = 1, M
    while X != IM:
        X = matmul(X, M)
        k += 1
        if k > 20:
            raise RuntimeError("no order")
    return k


print("=" * 112)
print("O222 B2 CONTRACT ENFORCER (Contract v1) -- settings freeze / AST ban / structural no-signalling")
print("=" * 112)

chk("[contract]", "group reconstruction matches R1: |2I| = 120, |I| = 60",
    len(G2I) == 120 and len(I60) == 60, "|2I|=%d |I|=%d" % (len(G2I), len(I60)))

lines = {}
for q in G2I:
    k = order_of(matkey(rot_matrix(q)))
    vec = (q[1], q[2], q[3])
    if all(x == ZERO for x in vec):
        continue
    lines.setdefault(k, set()).add(dir_canon(vec))
L5, L3, L2 = sorted(lines[5]), sorted(lines[3]), sorted(lines[2])


def lift(ls):
    out = []
    for d in ls:
        out.append(d)
        out.append(tuple(neg(x) for x in d))
    return sorted(out)


def orbit(v0):
    return sorted({matvec(M, v0) for M in I60})


v_rep = dir_canon(([q for q in G2I if order_of(matkey(rot_matrix(q))) == 5
                    and any(x != ZERO for x in (q[1], q[2], q[3]))][0][1:4]))
V12 = orbit(v_rep)
F20 = orbit(dir_canon(([q for q in G2I if order_of(matkey(rot_matrix(q))) == 3
                       and any(x != ZERO for x in (q[1], q[2], q[3]))][0][1:4])))
E30 = orbit(dir_canon(([q for q in G2I if order_of(matkey(rot_matrix(q))) == 2
                       and any(x != ZERO for x in (q[1], q[2], q[3]))][0][1:4])))

AXES = ([("V%02d" % i, "vertex", v) for i, v in enumerate(V12)] +
        [("F%02d" % i, "face", v) for i, v in enumerate(F20)] +
        [("E%02d" % i, "edge", v) for i, v in enumerate(E30)])
chk("[L-SET]", "62 lattice-native axes (12 vertices / 20 faces / 30 edges), honest counts",
    len(AXES) == 62 and len(V12) == 12 and len(F20) == 20 and len(E30) == 30,
    "|V|=%d |F|=%d |E|=%d (lines 6/10/15)" % (len(V12), len(F20), len(E30)))

# ---- exact pairwise cos^2 table (all 3844 ordered pairs) ---------------------
COS2 = {}
for i, (ia, ta, ua) in enumerate(AXES):
    for j, (ib, tb, ub) in enumerate(AXES):
        d = dot(ua, ub)
        val = mul(mul(d, d), inv(mul(norm2(ua), norm2(ub))))
        COS2[(i, j)] = val
chk("[L-SET]", "3844 ordered pairs with EXACT cos^2 in Q(sqrt5) (no trig, no float)",
    len(COS2) == 3844 and all(len(v) == 2 for v in COS2.values()),
    "pairs = %d ; sample cos^2(V00,V01) = %s" % (len(COS2), COS2[(0, 1)]))

DEV = [(i, j) for i in range(12) for j in range(12)]
BLIND = [(i, j) for i in range(62) for j in range(62) if not (i < 12 and j < 12)]
chk("[blind]", "partition frozen: DEV = 144 (V x V), BLIND = 3700 (all the rest)",
    len(DEV) == 144 and len(BLIND) == 3700 and len(set(DEV) | set(BLIND)) == 3844,
    "DEV=%d BLIND=%d total=%d" % (len(DEV), len(BLIND), len(DEV) + len(BLIND)))

# ---- P1: structural marginal = 1/2 exactly (no-signalling, derived not assumed)
n_ref = V12[0]
bal = {}
ties = {}
for aid, typ, u in AXES:
    pos = negc = tie = 0
    for M in I60:
        s = num_sign(dot(u, matvec(M, n_ref)))
        if s > 0:
            pos += 1
        elif s < 0:
            negc += 1
        else:
            tie += 1
    bal[aid] = (pos, negc, tie)
    ties[aid] = tie
sym_ok = all(v[0] == v[1] for v in bal.values())
chk("[L-CAUSAL]", "P1 structural: single-wing marginal = 1/2 EXACT for all 62 axes (central symmetry 6/6 + uniform multiplicity)",
    sym_ok, "balanced axes = %d/62 ; max tie count = %d" % (sum(1 for v in bal.values() if v[0] == v[1]), max(ties.values())))

# robustness: every vertex used as the reference axis (H4)
pos_counts = []
for r in V12:
    p = sum(1 for M in I60 if num_sign(dot(V12[0], matvec(M, r))) > 0)
    pos_counts.append(p)
chk("[L-CAUSAL]", "P1 robustness: balance holds for every reference axis n-hat in the 12 vertices (H4)",
    all(p * 2 == len(I60) for p in pos_counts), "pos-counts (first 6) = %s" % pos_counts[:6])

# ---- P1b: ties ASSIGNED by H3 (not excluded) --------------------------------
def tie_sign_vec(vec):
    for comp in vec:
        s = num_sign(comp)
        if s != 0:
            return s
    return 0


tie_events = 0
unbal = []
for ref in V12:
    for aid, typ, u in AXES:
        pos = negc = 0
        for M in I60:
            w = matvec(M, ref)
            s = num_sign(dot(u, w))
            if s == 0:
                s = tie_sign_vec(w)
                tie_events += 1
            if s > 0:
                pos += 1
            elif s < 0:
                negc += 1
        if pos != negc:
            unbal.append((aid, typ, pos, negc))
orth_edge = sorted({sum(1 for v in V12 if num_sign(dot(u, v)) == 0)
                    for aid2, typ2, u in AXES if typ2 == "edge"})
orth_other = sorted({sum(1 for v in V12 if num_sign(dot(u, v)) == 0)
                     for aid2, typ2, u in AXES if typ2 != "edge"})
chk("[L-CAUSAL]", "P1b ties ASSIGNED by H3 (not excluded): 0 unbalanced over 12 refs x 62 axes x 60 rotations",
    len(unbal) == 0 and tie_events == 7200,
    "tie events = %d ; unbalanced = %d" % (tie_events, len(unbal)))
chk("[L-CAUSAL]", "tie origin structural: edge axes orthogonal to exactly 4 vertex directions (x5 multiplicity = 20); vertex/face axes 0",
    orth_edge == [4] and orth_other == [0],
    "edge = %s ; vertex/face = %s" % (orth_edge, orth_other))

# ---- L-ZERO: AST forbidden-token scanner ------------------------------------
FORBIDDEN_CALLS = {"cos", "sin", "tan", "acos", "asin", "atan", "atan2", "cosh", "sinh",
                   "sqrt", "exp", "log", "log10", "hypot", "degrees", "radians"}
FORBIDDEN_MODULES = {"numpy", "scipy", "math", "cmath", "random"}
KERNEL_SCOPE = ("kernel", "k_table", "ktable", "outcome", "corr", "C_pair", "pair", "expect", "marginal")
ALLOW_TRIG_FUNCS = ("embed_", "report_", "fmt_")


def _scope_kind(fname):
    n = fname.lower()
    if any(n.startswith(x) or n.startswith("x") and False for x in ALLOW_TRIG_FUNCS):
        return "allow"
    if any(n.startswith(k) or n.endswith(k) or k in n for k in KERNEL_SCOPE):
        return "kernel"
    return "other"


def scan_source(src, fname="<mem>"):
    """return list of findings (strings).  Empty = clean."""
    tree = ast.parse(src, filename=fname)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = []
            if isinstance(node, ast.Import):
                mods = [al.name.split(".")[0] for al in node.names]
            elif node.module:
                mods = [node.module.split(".")[0]]
            for m in mods:
                if m in FORBIDDEN_MODULES:
                    scope = "module"
                    out.append("%s: import of banned module '%s'" % (scope, m))
    for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        kind = _scope_kind(fn.name)
        for node in ast.walk(fn):
            if isinstance(node, ast.Call):
                fn_node = node.func
                nm = fn_node.attr if isinstance(fn_node, ast.Attribute) else getattr(fn_node, "id", None)
                if nm in FORBIDDEN_CALLS:
                    out.append("%s(): forbidden call '%s' at line %d" % (fn.name, nm, node.lineno))
                if isinstance(fn_node, ast.Attribute):
                    base = getattr(fn_node.value, "id", None)
                    if base in FORBIDDEN_MODULES:
                        out.append("%s(): call on banned module '%s' line %d" % (fn.name, base, node.lineno))
            if isinstance(node, ast.Constant) and isinstance(node.value, float):
                if node.value != int(node.value):
                    out.append("%s(): non-integral float literal %r at line %d (use Fraction)"
                               % (fn.name, node.value, node.lineno))
            if kind == "kernel" and isinstance(node, ast.Constant) and isinstance(node.value, float):
                out.append("%s(): float literal %r in KERNEL scope (exact arithmetic only)"
                           % (fn.name, node.value))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            v = abs(node.value)
            for magic in (0.7071067811865476, 1.4142135623730951, 2.8284271247461903):
                if abs(v - magic) < 1e-12:
                    out.append("magic constant near %.4f (QM value) at line %d" % (magic, node.lineno))
    return out


POS_CTRL = "import math\ndef kernel(a, g):\n    return -math.cos(a - g)\n"
NEG_CTRL = ("def k_table(setting, gen):\n"
            "    from fractions import Fraction as F\n"
            "    return [1 if sign(u_dot(setting, gen)) > 0 else -1]\n")
MAGIC_CTRL = "def corr(a, b):\n    return 0.7071067811865476 * a * b\n"
FLOAT_CTRL = "def k_table(s):\n    return [0.5]\n"

f_pos = scan_source(POS_CTRL, "pos")
f_magic = scan_source(MAGIC_CTRL, "magic")
f_float = scan_source(FLOAT_CTRL, "float")
f_neg = scan_source(NEG_CTRL, "neg")
chk("[L-ZERO]", "AST scanner SELF-TEST: rejects -cos kernel / magic 0.7071 constant / 0.5 float, accepts clean exact kernel",
    len(f_pos) > 0 and len(f_magic) > 0 and len(f_float) > 0 and len(f_neg) == 0,
    "pos=%d magic=%d float=%d neg=%d" % (len(f_pos), len(f_magic), len(f_float), len(f_neg)))


def check_locality(src, fname="<mem>"):
    """contract 4.1: the single-setting factor table must take ONE setting and never see the other."""
    tree = ast.parse(src, filename=fname)
    out = []
    fns = {n.name: n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    kt = None
    for nm in fns:
        if nm.startswith("k_table") or nm.startswith("kernel_table"):
            kt = fns[nm]
    if kt is None:
        out.append("no 'k_table(<setting>, ...)' factor-table function found (contract 4.1)")
        return out
    args = [a.arg for a in kt.args.args]
    if len([a for a in args if a not in ("gen", "g", "group", "ref", "n_hat", "measure", "w")]) != 1:
        out.append("k_table must take exactly ONE setting argument, got %s" % args)
    badnames = [a for a in args if any(t in a.lower() for t in ("remote", "second", "other", "setting_b", "b_axis"))]
    if badnames:
        out.append("k_table argument names leak the remote setting: %s" % badnames)
    for node in ast.walk(kt):
        if isinstance(node, ast.Name) and any(t in node.id.lower() for t in
                                              ("remote", "second_setting", "other_setting", "setting_b")):
            out.append("k_table body references remote setting name '%s' (line %d)" % (node.id, node.lineno))
        if isinstance(node, ast.Call):
            nm2 = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", None)
            if nm2 in ("k_table", "kernel_table"):
                out.append("k_table calls itself with a second setting (line %d)" % node.lineno)
    pair = None
    for nm in fns:
        if nm.startswith(("pair_", "c_pair", "build_c", "assemble")) or nm == "C":
            pair = fns[nm]
    if pair is None:
        out.append("no pair-assembly function found (contract 4.1: C[a][b] = sum_g w K(g,a) K(g,b))")
    return out


l_pos = check_locality("def k_table(setting, gen):\n    return [K_single(setting, gen, remote_setting)]\n")
l_neg = check_locality("def k_table(setting, gen):\n    return [K_single(setting, gen)]\n"
                       "def pair_build(K, w, a, b):\n    return sum(w[g]*K[a][g]*K[b][g] for g in range(3))\n")
chk("[L-CAUSAL]", "locality checker SELF-TEST: rejects remote-setting leak in k_table, accepts factor-table C assembly",
    len(l_pos) > 0 and len(l_neg) == 0, "leak-findings=%d clean-findings=%d" % (len(l_pos), len(l_neg)))

# ---- artefacts + hashes -----------------------------------------------------
settings = {
    "rules_version": "contract-v1",
    "axes": [{"id": aid, "type": typ, "vec": vkey_num(v)} for aid, typ, v in AXES],
    "cos2": {"%d,%d" % k: [str(v[0]), str(v[1])] for k, v in COS2.items()},
    "hyperparameters": {
        "H1_measure": "uniform on 2I (120) primary; uniform on I (60) control",
        "H2_binarisation": "O = sign(u_a . (g n_hat)) exact algebraic",
        "H3_tie_rule": "O = sign(first non-zero component of (g n_hat)); tie counts reported separately",
        "H4_reference_axis": "index 0 (V00); robustness over all 12 vertices",
        "H5_C_definition": "C[a][b] = sum_g w(g) K(g,a) K(g,b)",
        "H6_qm_comparison": "exact squared relation C^2 vs cos^2 in Q(sqrt5)",
        "H7_sign_convention": "report |C| vs |cos|; sign map reported separately",
        "H8_chsh_windows": "S<=2+1e-12 LHV-class; |S-2sqrt2|<=1e-9 QM-like; else third structural value",
        "H9_random_axis_null": "10000 draws, seed 222",
        "H10_ablation_independent_draw": "g_a independent g_b -> C = 0 EXACT",
        "H11_joint_feasibility": "exact LP over setting subsets, increasing cardinality",
        "H12_min_infeasible_subset": "report minimal cardinality + all of that cardinality",
    },
    "marginal_balance": {aid: list(v) for aid, v in bal.items()},
    "tie_audit": {"rule": "H3", "tie_events_12refs": tie_events, "unbalanced_with_ties_assigned": len(unbal),
                  "edge_axis_orthogonal_vertex_directions": orth_edge,
                  "other_axis_orthogonal_vertex_directions": orth_other},
}
sp = os.path.join(DATA, "04_b2_settings.json")
io.open(sp, "w", encoding="utf-8").write(json.dumps(settings, ensure_ascii=False, indent=1))
part = {"rules_version": "contract-v1", "dev": DEV, "blind": BLIND}
pp = os.path.join(DATA, "04_b2_partition.json")
io.open(pp, "w", encoding="utf-8").write(json.dumps(part, ensure_ascii=False, indent=1))

impl_path = None
if "--freeze-impl" in sys.argv:
    impl_path = sys.argv[sys.argv.index("--freeze-impl") + 1]
candidates = sorted(f for f in os.listdir(SCRIPTS) if f.startswith("05_") and f.endswith(".py"))
impl = None
if impl_path:
    src = io.open(impl_path, encoding="utf-8").read()
    ast_find = scan_source(src, impl_path)
    loc_find = check_locality(src, impl_path)
    ok = chk("[L-ZERO]", "implementation %s passes AST ban (no trig / no numpy / no float literals)" % os.path.basename(impl_path),
             len(ast_find) == 0, "findings = %d %s" % (len(ast_find), ast_find[:3]))
    ok2 = chk("[L-CAUSAL]", "implementation passes the static locality check (single-setting factor table)",
              len(loc_find) == 0, "findings = %d %s" % (len(loc_find), loc_find[:3]))
    impl = {"path": impl_path, "sha256": sha256_file(impl_path), "ast_ok": ok, "locality_ok": ok2}
elif candidates:
    chk("[contract]", "unfrozen implementation present -> must be frozen via --freeze-impl before any run",
        False, "found %s with no recorded impl hash" % candidates)
else:
    claim("[WAITING]", "scripts/05_b2_correlation.py", "not written yet - the contract gate is closed until "
          "04 is run with --freeze-impl and the implementation hash is recorded in data/04_b2_freeze.json")

freeze = {
    "rules_version": "contract-v1",
    "frozen_at": datetime.now(HKT).isoformat(timespec="seconds"),
    "doc": {"path": DOC, "sha256": sha256_file(DOC) if os.path.exists(DOC) else None},
    "enforcer": {"path": os.path.abspath(__file__), "sha256": sha256_file(os.path.abspath(__file__))},
    "settings": {"path": sp, "sha256": sha256_file(sp)},
    "partition": {"path": pp, "sha256": sha256_file(pp)},
    "impl": impl,
    "gate": "OPEN" if impl else "CLOSED (05 not frozen)",
}
fp = os.path.join(DATA, "04_b2_freeze.json")
prev = None
if os.path.exists(fp):
    prev = json.load(io.open(fp, encoding="utf-8"))
    if prev.get("impl") and not impl:
        freeze["impl"] = prev["impl"]
        freeze["gate"] = "OPEN" if prev["impl"].get("ast_ok") and prev["impl"].get("locality_ok") else "CLOSED"
io.open(fp, "w", encoding="utf-8").write(json.dumps(freeze, ensure_ascii=False, indent=1))

print()
chk("[hash]", "freeze attestation written (doc + enforcer + settings + partition%s)" % (" + impl" if impl else ""),
    os.path.exists(fp) and freeze["doc"]["sha256"] is not None,
    "doc=%s" % (freeze["doc"]["sha256"] or "-")[:16])
chk("[hash]", "settings sha256 recorded for the blind-commitment", len(freeze["settings"]["sha256"]) == 64,
    "settings=%s" % freeze["settings"]["sha256"][:16])

n_pass = sum(1 for r in RESULTS if r["ok"] is True)
n_fail = sum(1 for r in RESULTS if r["ok"] is False)
n_claim = sum(1 for r in RESULTS if r["ok"] is None)
print("\n" + "=" * 112)
print("RESULT: %d/%d PASS  (%d FAIL, %d claims excluded)   GATE = %s"
      % (n_pass, n_pass + n_fail, n_fail, n_claim, freeze["gate"]))
print("=" * 112)
with open(os.path.join(DATA, "04_b2_contract_results.json"), "w", encoding="utf-8") as fh:
    json.dump({"pass": n_pass, "fail": n_fail, "claims": n_claim, "checks": RESULTS,
               "gate": freeze["gate"], "freeze": freeze}, fh, ensure_ascii=False, indent=1)
print("saved: data/04_b2_settings.json | 04_b2_partition.json | 04_b2_freeze.json | 04_b2_contract_results.json")
