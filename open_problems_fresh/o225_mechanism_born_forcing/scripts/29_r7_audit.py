#!/usr/bin/env python3
"""O225 scripts/29 -- R7 獨立審計（不 import 28）。

D1 獨立路線之主公式核（**不用 d**，直接用 ε/γ 原始比較）／D2 獨立 Σd = 600 + 中心不變
D3 獨立零態 pointwise（S=0 ⟺ Δ=0）＋ 對 R6 data/24 零態集交叉核對
D4 獨立 A7（線 ΣS 排序與零態線）／D5 獨立 B1（±p±q 路線）／D6 對 28 輸出之交叉核對
精確算術；零浮點；上游唯讀。用法: /usr/bin/python3 scripts/29_r7_audit.py
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
REPO = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O222 = os.path.join(REPO, 'open_problems_fresh/o222_qm_evaluation_semantics')
RULES = 'r7-delta-as-parity-count-v1'
COST = F(123, 88)
EMIN = F(123, 176)
BUDGET = F(10 ** 9)
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


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def mul(x, y):
    return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + y[0] * x[1])


def neg(x):
    return (-x[0], -x[1])


def vscale(c, v):
    return tuple(mul(c, comp) for comp in v)


def vadd(u, w):
    return tuple(add(u[j], w[j]) for j in range(3))


def sgn(x):
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


def dot3(u, r):
    return add(add(mul(u[0], r[0]), mul(u[1], r[1])), mul(u[2], r[2]))


def cross3(u, r):
    return (add(mul(u[1], r[2]), neg(mul(u[2], r[1]))),
            add(mul(u[2], r[0]), neg(mul(u[0], r[2]))),
            add(mul(u[0], r[1]), neg(mul(u[1], r[0]))))


def firstsgn(v):
    for c in v:
        s = sgn(c)
        if s:
            return s
    return 0


def qmul(a, b):
    return (a[0] * b[0] + 5 * a[1] * b[1], a[0] * b[1] + b[0] * a[1])


def qinv(a):
    nrm = a[0] * a[0] - 5 * a[1] * a[1]
    return (a[0] / nrm, -a[1] / nrm)


def qsub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def toq(x):
    return (F(x[0]), F(x[1]))


def same_line(u, x):
    t = None
    for j in range(3):
        if x[j] != (0, 0):
            t = j
            break
    if t is None:
        return False
    lam = qmul(toq(u[t]), qinv(toq(x[t])))
    return all(qsub(toq(u[j]), qmul(lam, toq(x[j]))) == (0, 0) for j in range(3))


def run(s0, Kt, MULt, hxt, pairs, sink=None):
    """獨立實作（與 28 分開寫）：協定逐字同 O222 scripts/30_g1g8_gaps.ledger_replay。"""
    stack = []
    s = s0
    rem = BUDGET
    hits = 0
    for (a, b) in pairs:
        spent = 0
        for ctx in (a, b):
            if stack and stack[-1][0] == ctx:
                hits += 1
                if sink:
                    sink(ctx, stack[-1][2], s)
                continue
            if rem - COST * spent < EMIN:
                raise RuntimeError('terminal')
            stack.append((ctx, Kt[s][ctx], s))
            s = MULt[s][hxt[ctx]]
            spent += 1
        _c, _v, s_back = stack.pop()
        s = s_back
        if stack and stack[-1][0] == b:
            hits += 1
            if sink:
                sink(b, stack[-1][2], s)
        else:
            if rem - COST * spent < EMIN:
                raise RuntimeError('terminal')
            stack.append((b, Kt[s][b], s))
            s = MULt[s][hxt[b]]
            spent += 1
        rem -= COST * spent
    return {'hits': hits, 'len': len(stack)}


def main():
    print('=' * 116)
    print('O225 scripts/29 -- R7 INDEPENDENT AUDIT   (%s)' % RULES)
    print('=' * 116, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'r7au_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    G, _ig, _M2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'r7au_a2').build_group()
    n, ncol = len(K), len(K[0])
    KV = [mm.rot_ref(g, U[0]) for g in G]
    pairs = [(a, b) for a in range(ncol) for b in range(ncol)]

    # 獨立建表：prod = firstsgn((⟨u,r⟩, u×r)) 之統一形式（tie 時自動等於 firstsgn(u×r)）
    Kp = []
    for s in range(n):
        row = []
        for a in range(ncol):
            d = dot3(U[a], KV[s])
            c = cross3(U[a], KV[s])
            row.append(firstsgn((d, c[0], c[1], c[2])))
        Kp.append(row)
    tie = [[dot3(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [firstsgn(KV[s]) for s in range(n)]
    gam = [{a: firstsgn(cross3(U[a], KV[s])) for a in range(ncol) if tie[s][a]} for s in range(n)]
    # 獨立重建 K（機器側）以交叉核對
    Km = []
    for s in range(n):
        row = []
        for a in range(ncol):
            d = dot3(U[a], KV[s])
            sd = sgn(d)
            row.append(sd if sd else eps[s])
        Km.append(row)
    claim('D0', '獨立重建機器 K（sgn⟨u,r⟩ / tie → ε(s)）與 O222 load_machine 之 K 逐條目相同',
          all(Km[s][a] == K[s][a] for s in range(n) for a in range(ncol)),
          'tie 條目 = %d ; 非 tie = %d' % (sum(1 for s in range(n) for a in range(ncol) if tie[s][a]),
                                           sum(1 for s in range(n) for a in range(ncol) if not tie[s][a])))

    # ---------- D1：獨立主公式核（不用 d）----------
    dev = 0
    acc_f = []
    acc_S = []
    ecount = 0
    for s0 in range(n):
        st = {'f': 0, 'S': 0, 'n': 0}

        def sink(ctx, sw, sr, st=st):
            tw, tr = tie[sw][ctx], tie[sr][ctx]
            dl = (1 if Kp[sr][ctx] != Kp[sw][ctx] else 0) - (1 if K[sr][ctx] != K[sw][ctx] else 0)
            if tw and tr:
                f = (1 if gam[sr][ctx] != gam[sw][ctx] else 0) - (1 if eps[sr] != eps[sw] else 0)
            elif tr:
                x = K[sw][ctx]
                f = (1 if x == eps[sr] else 0) - (1 if x == gam[sr][ctx] else 0)
            elif tw:
                x = K[sr][ctx]
                f = (1 if x == eps[sw] else 0) - (1 if x == gam[sw][ctx] else 0)
            else:
                f = 0
            if f != dl:
                st['dev'] = st.get('dev', 0) + 1
            st['f'] += f
            st['S'] += abs(f)
            st['n'] += 1
        run(s0, K, MUL, hx, pairs, sink)
        dev += st.get('dev', 0)
        ecount += st['n']
        acc_f.append(st['f'])
        acc_S.append(st['S'])
    claim('D1', '★ 獨立路線（不用 d）之主公式：Δ = Σ f 逐事件等於 Δ_ind（(T,T) 用 γ/ε 原始比較、(T,F)/(F,T) 用 '
                '[x≠tie 值] 之差）',
          dev == 0, '事件 = %d ; 偏離 = %d ; Δ 總和 = %d' % (ecount, dev, sum(acc_f)))

    # ---------- D2：獨立 Σd / 中心不變 ----------
    dind = [[(1 if (gam[s][a] != eps[s]) else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]
    dtot = sum(dind[s][a] for s in range(n) for a in range(ncol))
    ident = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))]
    cen = [i for i in range(n) if i not in ident and all(MUL[i][j] == MUL[j][i] for j in range(n))][0]
    dci = all(dind[MUL[s][cen]][a] == dind[s][a] for s in range(n) for a in range(ncol))
    claim('D2', '★ 獨立計數：Σ_tie d = 600（恰半）；d 中心不變', dtot == 600 and dci,
          'Σd = %d ; tie 條目 = %d ; 中心不變 = %s' % (dtot, sum(1 for s in range(n) for a in range(ncol) if tie[s][a]), dci))

    # ---------- D3：零態 pointwise + 對 R6 交叉核對 ----------
    zeros = [s for s in range(n) if acc_f[s] == 0]
    zpoint = [s for s in zeros if acc_S[s] == 0]
    r6 = json.load(io.open(os.path.join(DATA, '24_r6_mechanism.json'), encoding='utf-8'))
    r6z = r6['A6']['zeros']
    r6d = r6['delta']
    agree_d = all(r6d[s] == acc_f[s] for s in range(n))
    claim('D3', '★ 獨立零態核：Δ = 0 之態集 = R6 之零態集；且零態逐事件全零（pointwise，S = 0）',
          zeros == r6z and len(zpoint) == len(zeros) and agree_d,
          '零態 = %s ; R6 零態 = %s ; 全零 = %d/%d ; Δ 逐態等於 R6 = %s' % (zeros, r6z, len(zpoint), len(zeros), agree_d))

    # ---------- D4：獨立 A7 ----------
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(sgn(add(U[i][t], U[j][t])) == 0 for t in range(3)):
                partner[i] = j
    key = [min(a, partner[a]) for a in range(ncol)]
    keys = sorted(set(key))
    ktype = {kk: types[kk] for kk in keys}

    def line_of(s):
        for kk in keys:
            if ktype[kk] == 'vertex' and same_line(U[kk], KV[s]):
                return kk
        return None
    totS = {}
    for s in range(n):
        totS[line_of(s)] = totS.get(line_of(s), 0) + acc_S[s]
    rank = sorted(totS, key=lambda kk: (totS[kk], kk))
    zl = sorted(set(line_of(s) for s in zeros))
    claim('D4', '★ 獨立 A7：零態線 = Σ_{20 態} S 最小之 2 條線', zl == sorted(rank[:2]),
          '零態線 = %s ; 最小 2 = %s ; 各線 ΣS = %s' % (zl, sorted(rank[:2]), [(kk, totS[kk]) for kk in rank]))

    # ---------- D5：獨立 B1（±p±q 路線）----------
    tieset = {kk: sorted(set(key[a] for a in range(ncol) if dot3(U[a], U[kk]) == (0, 0))) for kk in keys}
    edge_keys = [kk for kk in keys if ktype[kk] == 'edge']
    ok = 0
    det = {}
    for kk in edge_keys:
        vs = [x for x in tieset[kk] if ktype[x] == 'vertex']
        es = [x for x in tieset[kk] if ktype[x] == 'edge']
        lines4 = []
        for sa in (1, -1):
            for sb in (1, -1):
                v = vadd(vscale((F(sa), F(0)), U[vs[0]]), vscale((F(sb), F(0)), U[vs[1]]))
                lines4.append(v)
        hit = set()
        for v in lines4:
            for z in es:
                if same_line(v, U[z]):
                    hit.add(z)
        if len(vs) == 2 and len(es) == 2 and hit == set(es) and all(sgn(dot3(U[z], U[kk])) == 0 for z in es):
            ok += 1
        det[str(kk)] = {'vertex': vs, 'edge': es, '命中': sorted(hit)}
    claim('D5', '★ 獨立 B1（±p±q 全四取向路線）：命中 = e 之 2 條 edge tie 軸', ok == len(edge_keys),
          '全符 = %d/%d ; 樣本 = %s' % (ok, len(edge_keys), det[str(edge_keys[0])]))

    # ---------- D6：對 28 輸出交叉核對 ----------
    p28 = os.path.join(DATA, '28_r7_mechanism2.json')
    ok6 = False
    if os.path.isfile(p28):
        d28 = json.load(io.open(p28, encoding='utf-8'))
        ok6 = (d28['delta'] == acc_f and d28['S'] == acc_S and d28['A3']['zeros'] == zeros
               and d28['A2']['sum_d'] == dtot and d28['A7']['zero_lines'] == zl
               and d28['B1']['ok'] == len(edge_keys))
    claim('D6', '★ 交叉核對：29 之 (Δ, S, 零態, Σd, 零態線, B1) 與 28 之輸出逐項相同', ok6,
          '28 存在 = %s ; 逐項相同 = %s' % (os.path.isfile(p28), ok6))

    out = {'audit_of': RULES, 'D0': {'tie_cells': sum(1 for s in range(n) for a in range(ncol) if tie[s][a])},
           'D1': {'events': ecount, 'deviation': dev}, 'D2': {'sum_d': dtot, 'centre_inv': dci},
           'D3': {'zeros': zeros, 'r6_zeros': r6z, 'pointwise': zpoint}, 'D4': {'zero_lines': zl, 'min2': sorted(rank[:2])},
           'D5': {'ok': ok, 'total': len(edge_keys), 'detail': det}, 'D6': {'match28': ok6},
           'delta': acc_f, 'S': acc_S, 'claims': CLAIMS}
    with io.open(os.path.join(DATA, '29_r7_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 116)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 116)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
