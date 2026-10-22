#!/usr/bin/env python3
"""O225 scripts/26 -- R6 獨立審計（唔 import scripts/24,25）。

A 第二套讀事件記錄實作 → 對 24 抽樣核對（clean 分解、overrides、Δ）
B 獨立 7440 條目恆等（另一碼路）
C 獨立非邊正交檢查 + 型別對表 + edge 型別分解
D 獨立 C3 幾何核（edge 端點路線）
用法: /usr/bin/python3 scripts/26_r6_audit.py
"""
import collections
import importlib.util
import io
import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
COST = F(123, 88)
EMIN = F(123, 176)
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def A(x, y):
    return (x[0] + y[0], x[1] + y[1])


def M(x, y):
    return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + y[0] * x[1])


def Ng(x):
    return (-x[0], -x[1])


def sg(x):
    if x[1] == 0:
        return (x[0] > 0) - (x[0] < 0)
    if x[0] == 0:
        return (x[1] > 0) - (x[1] < 0)
    if (x[0] > 0) == (x[1] > 0):
        return 1 if x[0] > 0 else -1
    lhs, rhs = x[0] * x[0], 5 * x[1] * x[1]
    if lhs == rhs:
        return 0
    return (1 if lhs > rhs else -1) * (1 if x[0] > 0 else -1)


def Dt(u, r):
    return A(A(M(u[0], r[0]), M(u[1], r[1])), M(u[2], r[2]))


def V(u, w):
    """向量加法；注意 A 為純量加法。"""
    return (A(u[0], w[0]), A(u[1], w[1]), A(u[2], w[2]))


def Cr(u, r):
    return (A(M(u[1], r[2]), Ng(M(u[2], r[1]))),
            A(M(u[2], r[0]), Ng(M(u[0], r[2]))),
            A(M(u[0], r[1]), Ng(M(u[1], r[0]))))


def fs(v):
    for c in v:
        s = sg(c)
        if s:
            return s
    return 0


def n2(u):
    acc = (F(0), F(0))
    for c in u:
        acc = A(acc, M(c, c))
    return acc


def qsub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def qmul(a, b):
    return (a[0] * b[0] + 5 * a[1] * b[1], a[0] * b[1] + b[0] * a[1])


def qinv(a):
    nrm = a[0] * a[0] - 5 * a[1] * a[1]
    return (a[0] / nrm, -a[1] / nrm)


def toq(x):
    return (F(x[0]), F(x[1]))


def sameline(u, x):
    t = None
    for j in range(3):
        if x[j] != (0, 0):
            t = j
            break
    if t is None:
        return False
    lam = qmul(toq(u[t]), qinv(toq(x[t])))
    return all(qsub(toq(u[j]), qmul(lam, toq(x[j]))) == (0, 0) for j in range(3))


def replay_logged(s0, Kt, MULt, hxt, order):
    """第二套實作：記錄每次比較之 (ctx, s_w, s_r)（用 list-of-dict 狀態機風格）。"""
    buf = []
    st = s0
    ev = []
    for pr in order:
        spent = 0
        for ctx in pr:
            if buf and buf[-1]['ctx'] == ctx:
                ev.append((ctx, buf[-1]['sw'], st))
                continue
            buf.append({'ctx': ctx, 'v': Kt[st][ctx], 'sw': st})
            st = MULt[st][hxt[ctx]]
            spent += 1
        top = buf.pop()
        st = top['sw']
        if buf and buf[-1]['ctx'] == pr[1]:
            ev.append((pr[1], buf[-1]['sw'], st))
        else:
            buf.append({'ctx': pr[1], 'v': Kt[st][pr[1]], 'sw': st})
            st = MULt[st][hxt[pr[1]]]
            spent += 1
    return ev


def main():
    print('=' * 116)
    print('O225 scripts/26 -- R6 INDEPENDENT AUDIT')
    print('=' * 116, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'r6c_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    G, _ig, _M2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'r6c_a2').build_group()
    n, ncol = len(K), len(K[0])
    KV = [mm.rot_ref(g, U[0]) for g in G]
    order = [(a, b) for a in range(ncol) for b in range(ncol)]
    ref = json.load(io.open(os.path.join(DATA, '24_r6_mechanism.json'), encoding='utf-8'))
    refg = json.load(io.open(os.path.join(DATA, '25_r6_geometry.json'), encoding='utf-8'))
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(sg(A(U[i][t], U[j][t])) == 0 for t in range(3)):
                partner[i] = j
    key = [min(a, partner[a]) for a in range(ncol)]
    keys = sorted(set(key))
    ktype = {k: types[k] for k in keys}
    tieset = {k: sorted(set(key[a] for a in range(ncol) if sg(Dt(U[a], U[k])) == 0)) for k in keys}

    def rule(mode):
        Kt = []
        for s in range(n):
            row = []
            for a in range(ncol):
                d = Dt(U[a], KV[s])
                sd = sg(d)
                if sd:
                    row.append(sd)
                elif mode == 'm':
                    row.append(fs(KV[s]))
                else:
                    c = Cr(U[a], KV[s])
                    row.append(fs((d, c[0], c[1], c[2]) if mode == 'p' else (d, Ng(c[0]), Ng(c[1]), Ng(c[2]))))
            Kt.append(row)
        return Kt
    Kp, Kn = rule('p'), rule('n')
    tie = [[sg(Dt(U[a], KV[s])) == 0 for a in range(ncol)] for s in range(n)]
    eps = [fs(KV[s]) for s in range(n)]
    gam = {}
    for s in range(n):
        gam[s] = {a: fs(Cr(U[a], KV[s])) for a in range(ncol) if tie[s][a]}

    # ---- B：獨立 7440 條目恆等（另一碼路）----
    bad = []
    nt = tt = 0
    for s in range(n):
        r = KV[s]
        for a in range(ncol):
            d = Dt(U[a], r)
            sd = sg(d)
            vals = [K[s][a], Kp[s][a], Kn[s][a]]
            if sd:
                nt += 1
                if vals != [sd, sd, sd]:
                    bad.append((s, a))
            else:
                tt += 1
                c = Cr(U[a], r)
                if not (vals[0] == eps[s] and vals[1] == fs(c) and vals[2] == -vals[1]):
                    bad.append((s, a))
    claim('B', '獨立碼路：7440 條目（non-tie 三變體同值；tie K = ε(s)、K_prod = γ、K_neg = −γ）',
          not bad and nt + tt == n * ncol, 'non-tie = %d ; tie = %d ; 偏離 = %s' % (nt, tt, bad[:4]))

    # ---- A：第二套實作對 24 抽樣核對 ----
    samples = [0, 1, 3, 11, 42, 61, 88, 119]
    res = {}
    ok_clean = ok_ov = ok_d = ok_eps = True
    for s0 in samples:
        ev = replay_logged(s0, K, MUL, hx, order)
        ov = {'m': 0, 'p': 0, 'n': 0}
        clean = {'m': 0, 'p': 0, 'n': 0}
        for (ctx, sw, sr) in ev:
            tw, tr = tie[sw][ctx], tie[sr][ctx]
            for v, Kt in (('m', K), ('p', Kp), ('n', Kn)):
                m = 1 if Kt[sr][ctx] != Kt[sw][ctx] else 0
                ov[v] += m
                if not (tw or tr):
                    clean[v] += m
            if tw and tr:
                if K[sr][ctx] != eps[sr] or K[sr][ctx] != eps[sr]:
                    ok_eps = False
        res[s0] = (ov, clean)
        if not (clean['m'] == clean['p'] == clean['n']):
            ok_clean = False
        if [ov['m'], ov['p'], ov['n']] != [ref['overrides_machine'][s0], ref['overrides_prod'][s0], ref['overrides_negprod'][s0]]:
            ok_ov = False
        if (ov['p'] - ov['m']) != ref['delta'][s0]:
            ok_d = False
    claim('A', '第二套讀事件實作：抽樣 8 態之 overrides（三變體）、clean 分解、Δ 與 24 之輸出逐值一致',
          ok_clean and ok_ov and ok_d and ok_eps,
          'clean 全同 = %s ; overrides 對 24 一致 = %s ; Δ 一致 = %s ; ε 恆等 = %s ; 樣本 = %s'
          % (ok_clean, ok_ov, ok_d, ok_eps, {k: [v[0]['m'], v[0]['p'], v[1]['m']] for k, v in sorted(res.items())[:3]}))

    # ---- C：獨立正交圖 ----
    cor = collections.Counter()
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = keys[i], keys[j]
            if sg(Dt(U[a], U[b])) == 0:
                cor[tuple(sorted((ktype[a], ktype[b])))] += 1
    nz = {p: cor.get(p, 0) for p in (('face', 'face'), ('face', 'vertex'), ('vertex', 'vertex'))}
    claim('C', '獨立正交圖：非邊軸兩兩非正交（三類皆 0）；edge–vertex = 30、edge–face = 30、edge–edge = P 對照 25',
          all(v == 0 for v in nz.values()) and cor.get(('edge', 'vertex'), 0) == 30
          and cor.get(('edge', 'face'), 0) == 30
          and {('%s-%s' % k): v for k, v in sorted(cor.items())} == refg['C2']['by_type_pair'],
          '型別對 = %s ; 非邊三類 = %s' % ({('%s-%s' % k): v for k, v in sorted(cor.items())}, nz))

    # ---- C2b：獨立 edge 型別分解 ----
    ec = collections.Counter()
    for k in keys:
        if ktype[k] == 'edge':
            ec[tuple(sorted(collections.Counter(ktype[x] for x in tieset[k]).items()))] += 1
    sig = dict(sorted(ec)[0])
    verdict = (len(ec) == 1 and sig.get('vertex', 0) == 2
               and sig.get('face', 0) + sig.get('edge', 0) == 4 and sig.get('face', 0) % 2 == 0)
    claim('C2b', '獨立 edge 型別分解：15 條 edge 參考之型別簽名唯一，且 vertex = 2、f + e = 4',
          verdict, '簽名多重集 = %s ; 判 = %s' % ([(k, v) for k, v in ec.items()], verdict))

    # ---- D：獨立 C3 幾何核（entry 路線 + 端點識別 + 原預測之獨立複現）----
    import itertools
    vent = [a for a in range(ncol) if types[a] == 'vertex']
    vkeys = [k for k in keys if ktype[k] == 'vertex']
    fkeys = [k for k in keys if ktype[k] == 'face']

    def sc(s, u):
        z = (F(s), F(0))
        return (M(z, u[0]), M(z, u[1]), M(z, u[2]))

    def posadj(u, w):
        d = Dt(u, w)
        if sg(d) <= 0:
            return False
        return qsub(toq(M(d, d)), qmul(qmul(n2(u), n2(w)), (F(1, 5), F(0)))) == (0, 0)

    def axof(vec):
        for z in range(ncol):
            if sameline(vec, U[z]):
                return key[z]
        return None

    def ends_of(e):
        out = set()
        for i, j in itertools.combinations(range(len(vent)), 2):
            for si in (1, -1):
                for sj in (1, -1):
                    ua, ub = sc(si, U[vent[i]]), sc(sj, U[vent[j]])
                    if sameline(V(ua, ub), U[e]) and posadj(ua, ub):
                        out.add(key[vent[i]])
                        out.add(key[vent[j]])
        return sorted(out)
    ok_v = 0
    for k in vkeys:
        c = collections.Counter()
        for e in tieset[k]:
            for x in ends_of(e):
                c[x] += 1
        if len(c) == 5 and sorted(c.values()) == [2] * 5:
            ok_v += 1
    ok_f = 0
    for k in fkeys:
        c = collections.Counter()
        for e in tieset[k]:
            for x in ends_of(e):
                c[x] += 1
        if len(c) == 3 and sorted(c.values()) == [2, 2, 2]:
            ok_f += 1
    claim('D1', '獨立端點識別（entry 路線）：vertex 參考 → 5 條端點線 ×2；face 參考 → 3 條端點線 ×2',
          ok_v == 6 and ok_f == 10, 'vertex 全符 = %d/6 ; face 全符 = %d/10' % (ok_v, ok_f))

    # D2：獨立複現 C3 之 FAIL（鄰居五邊形邊之中點線 ≠ tie 集）
    matched = 0
    checked = 0
    for k in vkeys[:3]:
        ring = [w for w in vent if sg(Dt(U[k], U[w])) > 0 and qsub(toq(M(Dt(U[k], U[w]), Dt(U[k], U[w]))),
                qmul(qmul(n2(U[k]), n2(U[w])), (F(1, 5), F(0)))) == (0, 0)]
        pents = set()
        for x, y in itertools.combinations(ring, 2):
            if posadj(U[x], U[y]):
                z = axof(V(U[x], U[y]))
                if z is not None:
                    pents.add(z)
        checked += 1
        if pents == set(tieset[k]):
            matched += 1
    claim('D2', '獨立複現 C3 之 FAIL：鄰居五邊形邊之中點線集 ≠ tie 集（原預測被否證之獨立確認）',
          checked == 3 and matched == 0, '檢查 = %d ; 意外相符 = %d' % (checked, matched))

    out = {'audit_of': ['24_r6_mechanism.py', '25_r6_geometry.py'], 'samples': samples,
           'A': {'clean_all_same': ok_clean, 'overrides_match': ok_ov, 'delta_match': ok_d, 'eps_identity': ok_eps},
           'B': {'non_tie': nt, 'tie': tt, 'deviations': bad[:6]},
           'C': {'type_pairs': {('%s-%s' % k): v for k, v in sorted(cor.items())},
                 'nonedge': {('%s-%s' % k): v for k, v in sorted(nz.items())}},
           'C2b': {'signatures': [(str(k), v) for k, v in ec.items()]},
           'D1': {'vertex_ok': ok_v, 'face_ok': ok_f}, 'D2': {'checked': checked, 'matched': matched}, 'claims': CLAIMS}
    with io.open(os.path.join(DATA, '26_r6_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 116)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 116)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
