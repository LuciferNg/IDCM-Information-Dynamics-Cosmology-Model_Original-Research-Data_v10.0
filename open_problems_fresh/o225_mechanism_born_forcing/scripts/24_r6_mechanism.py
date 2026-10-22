#!/usr/bin/env python3
"""O225 scripts/24 -- R6 Part A：tie 宇稱動力效應之機制層（`r6-mechanism-v1`）。

A1 K-無關讀事件集（含人造 K ≡ 0）／A2 clean vs tie 分解／A3a 7440 條目恆等／A3b 四類事件表
A3c (T,T) 事件之 ε/γ 判定恆等／A4 差異只由 tie 事件承載／A5 中心不變 + A₅ 商／A6 Δ=0 之 6 態身份（預測）
A7 線 vs 相位（預測 k > 6）／A8 對 R5 data/21 之交叉核對／A9 聯合類表
精確算術；零浮點；上游唯讀。用法: /usr/bin/python3 scripts/24_r6_mechanism.py
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
RULES = 'r6-mechanism-v1'
COST = F(123, 88)
EMIN = F(123, 176)
BUDGET = F(10 ** 9)
MOD = (1 << 61) - 1
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


def same_line(u, x):
    t = None
    for j in range(3):
        if x[j] != (0, 0):
            t = j
            break
    if t is None:
        return False
    lam = qmul((F(u[t][0]), F(u[t][1])), qinv((F(x[t][0]), F(x[t][1]))))
    return all(qsub((F(u[j][0]), F(u[j][1])), qmul(lam, (F(x[j][0]), F(x[j][1])))) == (0, 0)
               for j in range(3))


def run(s0, Kt, MULt, hxt, pairs, sink=None):
    """逐字複製自 O222 scripts/30_g1g8_gaps.ledger_replay；sink(ctx, s_w, s_r) 於每次比較。"""
    L = []
    s = s0
    rem = BUDGET
    hits = 0
    for (a, b) in pairs:
        spent = 0
        for ctx in (a, b):
            if L and L[-1][0] == ctx:
                hits += 1
                if sink is not None:
                    sink(ctx, L[-1][2], s)
                continue
            if rem - COST * spent < EMIN:
                raise RuntimeError('terminal')
            L.append((ctx, Kt[s][ctx], s))
            s = MULt[s][hxt[ctx]]
            spent += 1
        _c, _v, s_at = L.pop()
        s = s_at
        if L and L[-1][0] == b:
            hits += 1
            if sink is not None:
                sink(b, L[-1][2], s)
        else:
            if rem - COST * spent < EMIN:
                raise RuntimeError('terminal')
            L.append((b, Kt[s][b], s))
            s = MULt[s][hxt[b]]
            spent += 1
        rem -= COST * spent
    return {'hits': hits, 'len': len(L)}


def main():
    os.makedirs(DATA, exist_ok=True)
    print('=' * 116)
    print('O225 scripts/24 -- R6 PART A: mechanism layer of the tie-parity dynamical effect   (%s)' % RULES)
    print('=' * 116, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'r6_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    G, _idxg, _M2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'r6_a2').build_group()
    n, ncol = len(K), len(K[0])
    KV = [mm.rot_ref(g, U[0]) for g in G]
    pairs = [(a, b) for a in range(ncol) for b in range(ncol)]

    def build_rule(mode):
        Kt = []
        for s in range(n):
            row = []
            for a in range(ncol):
                d = dot3(U[a], KV[s])
                sd = sgn(d)
                if sd:
                    row.append(sd)
                elif mode == 'machine':
                    row.append(firstsgn(KV[s]))
                else:
                    c = cross3(U[a], KV[s])
                    row.append(firstsgn((d, c[0], c[1], c[2]) if mode == 'prod'
                                        else (d, neg(c[0]), neg(c[1]), neg(c[2]))))
            Kt.append(row)
        return Kt
    Kp = build_rule('prod')
    Kn = build_rule('negprod')
    Ks = {'m': K, 'p': Kp, 'n': Kn}
    K0 = [[0] * ncol for _ in range(n)]
    tie = [[sgn(dot3(U[a], KV[s])) == 0 for a in range(ncol)] for s in range(n)]
    eps = [firstsgn(KV[s]) for s in range(n)]
    gam = {}
    for s in range(n):
        st = {}
        for a in range(ncol):
            if tie[s][a]:
                c = cross3(U[a], KV[s])
                st[a] = firstsgn(c)
        gam[s] = st
    n_tie_cells = sum(1 for s in range(n) for a in range(ncol) if tie[s][a])

    # ---------- A3a：7440 條目恆等 ----------
    ok_nt = ok_t = 0
    dev = []
    for s in range(n):
        for a in range(ncol):
            d = dot3(U[a], KV[s])
            sd = sgn(d)
            if sd:
                ok_nt += 1
                if not (K[s][a] == Kp[s][a] == Kn[s][a] == sd):
                    dev.append(('nt', s, a))
            else:
                ok_t += 1
                c = cross3(U[a], KV[s])
                if not (K[s][a] == eps[s] and Kp[s][a] == firstsgn(c) == -Kn[s][a]):
                    dev.append(('t', s, a))
    claim('A3a', '★ 7440 條目恆等：non-tie 三變體同值 = sgn(⟨u,r⟩)；tie 條目 K = ε(s)、K_prod = γ(a,s)、K_neg = −γ(a,s)',
          not dev and ok_nt + ok_t == n * ncol, 'non-tie = %d ; tie = %d ; 偏離 = %s' % (ok_nt, ok_t, dev[:4]))

    # ---------- A1：K-無關事件集（含 K ≡ 0）----------
    hashes = {k: [] for k in ('m', 'p', 'n', '0')}
    hits_l = []
    for s0 in range(n):
        for key, Kt in (('m', K), ('p', Kp), ('n', Kn), ('0', K0)):
            st = {'h': 0, 'c': 0}

            def sink(ctx, sw, sr, st=st):
                st['h'] = (st['h'] * 1000003 + ctx * 7 + sw * 11 + sr * 13) % MOD
                st['c'] += 1
            r = run(s0, Kt, MUL, hx, pairs, sink)
            hashes[key].append((r['hits'], st['c'], st['h']))
        hits_l.append(hashes['m'][s0][0])
    ind = all(hashes['m'][s0] == hashes['p'][s0] == hashes['n'][s0] == hashes['0'][s0] for s0 in range(n))
    claim('A1', '★★ K-無關讀事件集：三 K 變體 + 人造 K ≡ 0 之逐態（hits, 事件數, 事件雜湊）完全相同',
          ind, '事件數 = %d (每態) ; hits 值 = %s ; 逐態四變體全同 = %s'
          % (hashes['m'][0][1], sorted(set(hits_l)), ind))

    # ---------- A2/A3b/A3c/A4：逐事件累積 ----------
    accs = []
    for s0 in range(n):
        acc = {'n': 0, 'cls': collections.Counter(), 'mis': {v: collections.Counter() for v in 'mpn'},
               'clean': {'m': 0, 'p': 0, 'n': 0}, 'tieinv': {'m': 0, 'p': 0, 'n': 0},
               'ov': {'m': 0, 'p': 0, 'n': 0}, 'dsum': 0, 'dev_eps': 0, 'dev_gam': 0, 'offtie': 0}

        def sink(ctx, sw, sr, acc=acc):
            tw, tr = tie[sw][ctx], tie[sr][ctx]
            k2 = (tw, tr)
            acc['n'] += 1
            acc['cls'][k2] += 1
            mm_ = 1 if Ks['m'][sr][ctx] != Ks['m'][sw][ctx] else 0
            mp_ = 1 if Ks['p'][sr][ctx] != Ks['p'][sw][ctx] else 0
            mn_ = 1 if Ks['n'][sr][ctx] != Ks['n'][sw][ctx] else 0
            for v, mv in (('m', mm_), ('p', mp_), ('n', mn_)):
                acc['ov'][v] += mv
                acc['mis'][v][k2] += mv
                if tw or tr:
                    acc['tieinv'][v] += mv
                else:
                    acc['clean'][v] += mv
            acc['dsum'] += mp_ - mm_
            if (mp_ - mm_) != 0 and not (tw or tr):
                acc['offtie'] += 1
            if tw and tr:
                if Ks['m'][sr][ctx] != eps[sr] or Ks['m'][sw][ctx] != eps[sw]:
                    acc['dev_eps'] += 1
                if mm_ != (1 if eps[sr] != eps[sw] else 0):
                    acc['dev_eps'] += 1
                if mp_ != (1 if gam[sr][ctx] != gam[sw][ctx] else 0):
                    acc['dev_gam'] += 1
        run(s0, K, MUL, hx, pairs, sink)
        accs.append(acc)

    clean_same = all(a['clean']['m'] == a['clean']['p'] == a['clean']['n'] for a in accs)
    clsc = collections.Counter()
    misc = {v: collections.Counter() for v in 'mpn'}
    for a in accs:
        clsc.update(a['cls'])
        for v in 'mpn':
            misc[v].update(a['mis'][v])
    tot = {v: sum(a['ov'][v] for a in accs) for v in 'mpn'}
    clean_tot = {v: sum(a['clean'][v] for a in accs) for v in 'mpn'}
    tieinv_tot = {v: sum(a['tieinv'][v] for a in accs) for v in 'mpn'}
    claim('A2', '★★ 分解：overrides = OT^clean + OT^tie；OT^clean 於三變體**逐態完全相同**（差異全部由 tie 事件承載）',
          clean_same and clean_tot['m'] == clean_tot['p'] == clean_tot['n'],
          'OT^clean(%s) = %s ; OT^tie(%s) = %s ; 逐態全同 = %s'
          % (', '.join(tot.keys()), [clean_tot[v] for v in 'mpn'], 'm/p/n', [tieinv_tot[v] for v in 'mpn'], clean_same))
    e4 = sum(a['n'] for a in accs)
    cok = all(clean_tot[v] == misc[v][(False, False)] for v in 'mpn')
    claim('A3b', '★ 四類事件表（tie(寫入態), tie(讀取態)）：事件數與各變體錯配數；並核 OT^clean == (F,F) 類錯配',
          cok, '事件總 = %d ; (F,F) = %d ; (T,T) = %d ; (T,F) = %d ; (F,T) = %d ; (F,F) 類錯配 m/p/n = %s ; '
               '(T,T) 類錯配 m/p/n = %s ; 混合類錯配 m/p/n = %s ; OT^clean m/p/n = %s'
          % (e4, clsc[(False, False)], clsc[(True, True)], clsc[(True, False)], clsc[(False, True)],
             [misc[v][(False, False)] for v in 'mpn'], [misc[v][(True, True)] for v in 'mpn'],
             [misc[v][(True, False)] + misc[v][(False, True)] for v in 'mpn'], [clean_tot[v] for v in 'mpn']))
    claim('A3c', '★ (T,T) 事件之判定恆等：K 側 = [ε(s_r) ≠ ε(s_w)]（ε 只依 s）；K_prod 側 = [γ(a,s_r) ≠ γ(a,s_w)]',
          all(a['dev_eps'] == 0 and a['dev_gam'] == 0 for a in accs),
          'ε 偏離 = %d ; γ 偏離 = %d（全態合計）' % (sum(a['dev_eps'] for a in accs), sum(a['dev_gam'] for a in accs)))
    dsums = [a['dsum'] for a in accs]
    offt = sum(a['offtie'] for a in accs)
    claim('A4', '★ 差異承載：任一位 Δ_ind ≠ 0 之事件必為 tie 事件（非 tie 事件偏離數 = 0）',
          offt == 0, '非 tie 事件之 Δ_ind ≠ 0 計數 = %d ; Δ 總和 = %d' % (offt, sum(dsums)))

    # ---------- A8：對 R5 data/21 交叉核對 ----------
    ref = json.load(io.open(os.path.join(DATA, '21_r5_tie_global.json'), encoding='utf-8'))
    ov_m = [a['ov']['m'] for a in accs]
    ov_p = [a['ov']['p'] for a in accs]
    ov_n = [a['ov']['n'] for a in accs]
    xok = (ov_m == ref['overrides_machine'] and ov_p == ref['overrides_prod'] and ov_n == ref['overrides_negprod'])
    claim('A8', '★ 交叉核對：由讀事件集重算之 overrides（三變體）逐態等於 R5 scripts/21 之直接運行結果',
          xok, '相等 = %s ; Δ = ov_p − ov_m：相異態數 = %d ; 為 0 之態數 = %d'
          % (xok, sum(1 for s in range(n) if ov_p[s] != ov_m[s]), sum(1 for s in range(n) if ov_p[s] == ov_m[s])))

    # ---------- A5：中心不變 + A₅ 商 ----------
    ident = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))]
    cen = [i for i in range(n) if i not in ident and all(MUL[i][j] == MUL[j][i] for j in range(n))][0]
    ci = all(ov_m[MUL[s][cen]] == ov_m[s] and ov_p[MUL[s][cen]] == ov_p[s] and dsums[MUL[s][cen]] == dsums[s]
             for s in range(n))
    cls = [min(s, MUL[s][cen]) for s in range(n)]
    vt_m = len(set((cls[s], ov_m[s]) for s in range(n)))
    vt_d = len(set((cls[s], dsums[s]) for s in range(n)))
    joint = len(set((cls[s], ov_m[s], ov_p[s], dsums[s]) for s in range(n)))
    claim('A5', '★ 中心不變（R3 (ii′) λ ≡ −1）：overrides（三變體）與 Δ 皆 centre-invariant；於 60 個 A₅ 類上取值',
          ci and len(set(cls)) == 60,
          'A₅ 類數 = %d ; 中心不變 = %s ; overrides_m 之 (類→值) 值數 = %d ; Δ 之值數 = %d ; 聯合表值數 = %d'
          % (len(set(cls)), ci, vt_m, vt_d, joint))

    # ---------- A6：Δ = 0 之 6 態身份（預測：6 條相異線）----------
    vertex_keys = sorted(set(min(a, [b for b in range(ncol) if b != a and
                                     all(sgn(add(U[a][t], U[b][t])) == 0 for t in range(3))][0])
                            for a in range(ncol) if types[a] == 'vertex'))
    def line_of(s):
        for kk in vertex_keys:
            if same_line(U[kk], KV[s]):
                return kk
        return None
    zeros = [s for s in range(n) if dsums[s] == 0]
    zlines = sorted(set(line_of(s) for s in zeros))
    claim('A6', '★★ 預測（見數前）：Δ = 0 之 6 態位於 **6 條相異頂點線**（每線一態）',
          len(zeros) == 6 and len(zlines) == 6 and all(line_of(s) is not None for s in zeros),
          'Δ = 0 之態 = %s ; 其線 = %s ; 相異線數 = %d' % (zeros, zlines, len(zlines)))

    # ---------- A7：線 vs 相位（預測 k > 6）----------
    kvals = sorted(set(dsums))
    per_line = {}
    for s in range(n):
        per_line.setdefault(line_of(s), []).append(dsums[s])
    line_div = {str(kk): len(set(v)) for kk, v in sorted(per_line.items())}
    claim('A7', '★ 預測（見數前）：Δ **依相位**而非只依線 ⟹ 相異值數 k > 6',
          len(kvals) > 6, 'k = %d ; Δ 值域 = [%d, %d] ; 每線內 Δ 之相異值數 = %s'
          % (len(kvals), min(kvals), max(kvals), line_div))

    out = {'rules': RULES, 'A1': {'events_per_state': hashes['m'][0][1], 'hits': sorted(set(hits_l)),
                                  'kindependent': ind},
           'A3a': {'non_tie': ok_nt, 'tie': ok_t, 'deviations': dev[:8], 'tie_cells_recomputed': n_tie_cells},
           'A2': {'clean': clean_tot, 'tie_involved': tieinv_tot, 'total': tot, 'clean_statewise_equal': clean_same},
           'A3b': {'classes': {'(F,F)': clsc[(False, False)], '(T,T)': clsc[(True, True)],
                               '(T,F)': clsc[(True, False)], '(F,T)': clsc[(False, True)]},
                   'mismatch_by_class': {v: {'(F,F)': misc[v][(False, False)], '(T,T)': misc[v][(True, True)],
                                             '(T,F)+(F,T)': misc[v][(True, False)] + misc[v][(False, True)]}
                                         for v in 'mpn'}},
           'A3c': {'eps_dev': sum(a['dev_eps'] for a in accs), 'gam_dev': sum(a['dev_gam'] for a in accs)},
           'A4': {'off_tie_dev': offt, 'delta_total': sum(dsums)},
           'A8': {'match_21': xok, 'n_states_differ': sum(1 for s in range(n) if ov_p[s] != ov_m[s])},
           'A5': {'n_classes': len(set(cls)), 'centre_invariant': ci, 'ovm_values_on_classes': vt_m,
                  'delta_values_on_classes': vt_d, 'joint_values': joint},
           'A6': {'zeros': zeros, 'zero_lines': zlines, 'n_zero_lines': len(zlines)},
           'A7': {'k': len(kvals), 'range': [min(kvals), max(kvals)], 'per_line_distinct': line_div},
           'overrides_machine': ov_m, 'overrides_prod': ov_p, 'overrides_negprod': ov_n, 'delta': dsums,
           'line_of_state': [line_of(s) for s in range(n)], 'claims': CLAIMS}
    with io.open(os.path.join(DATA, '24_r6_mechanism.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 116)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 116)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
