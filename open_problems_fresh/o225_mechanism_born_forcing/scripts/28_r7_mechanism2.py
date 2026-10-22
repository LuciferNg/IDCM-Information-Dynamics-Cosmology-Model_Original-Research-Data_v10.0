#!/usr/bin/env python3
"""O225 scripts/28 -- R7：Δ 化為 tie 宇稱分歧之帶號計數（#1+#2 合流）＋ edge 之 vertex tie 幾何身份。

Part A：A1 主公式逐事件核（0 偏離）／A2 d 分佈（600/1200、中心不變）／A3 零態 pointwise（預測）
        ／A5 S(s0) 與 S=0 態集（對 R6 交叉核對）／A6 A₅ 商聯合表／A7 零態線 = ΣS 最小 2 線（預測）
Part B：B1 預測（p ± q = e 之 2 條 edge tie 軸）／B2 六 tie 軸精確點積表／B3 face tie 身份刻畫
精確算術；零浮點；上游 O222 唯讀。用法: /usr/bin/python3 scripts/28_r7_mechanism2.py
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
    """向量 × 純量（Q(√5)）"""
    return tuple(mul(c, comp) for comp in v)


def vadd(u, w):
    """3 維向量加法（注意：`add` 係純量加法）"""
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


def qstr(a):
    p, q = a
    if q == 0:
        return str(p)
    sign = '+' if q > 0 else '-'
    return '%s%s%s√5' % (p, sign, abs(q))


def toq(x):
    return (F(x[0]), F(x[1]))


def nrm2(u):
    acc = (F(0), F(0))
    for c in u:
        acc = add(acc, mul(c, c))
    return acc


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
    print('O225 scripts/28 -- R7: Delta as a signed tie-parity-disagreement count   (%s)' % RULES)
    print('=' * 116, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'r7_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    G, _ig, _M2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'r7_a2').build_group()
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
    tie = [[sgn(dot3(U[a], KV[s])) == 0 for a in range(ncol)] for s in range(n)]
    eps = [firstsgn(KV[s]) for s in range(n)]
    gam = {}
    for s in range(n):
        gam[s] = {a: firstsgn(cross3(U[a], KV[s])) for a in range(ncol) if tie[s][a]}
    # A0：宇稱分歧指標
    dind = [[(1 if (gam[s][a] != eps[s]) else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]

    # ---------- A2：d 之全域分佈 ----------
    dtot = sum(dind[s][a] for s in range(n) for a in range(ncol))
    n_tie_cells = sum(1 for s in range(n) for a in range(ncol) if tie[s][a])
    ident = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))]
    cen = [i for i in range(n) if i not in ident and all(MUL[i][j] == MUL[j][i] for j in range(n))][0]
    dci = all(dind[MUL[s][cen]][a] == dind[s][a] for s in range(n) for a in range(ncol))
    per_state = [sum(dind[s]) for s in range(n)]
    claim('A2', '★ d 之全域分佈：Σ_tie d = 600（= 1200/2）；d(a,−s) = d(a,s)（中心不變）；報告每態 d 之和',
          dtot == 600 and n_tie_cells == 1200 and dci,
          'tie 條目 = %d ; Σd = %d ; 中心不變 = %s ; 每態 d 和之值集 = %s'
          % (n_tie_cells, dtot, dci, sorted(set(per_state))))

    # ---------- A1 / A3 / A5：逐事件主公式 ----------
    accs = []
    for s0 in range(n):
        acc = {'f': 0, 'S': 0, 'dev': 0, 'nz': 0, 'cls': collections.Counter(), 'byc': {'+': 0, '-': 0},
               'f_tf': 0, 'f_ft': 0, 'f_tt': 0, 'n_tf': 0, 'n_ft': 0, 'n_tt': 0, 'f0_events': 0}

        def sink(ctx, sw, sr, acc=acc):
            tw, tr = tie[sw][ctx], tie[sr][ctx]
            mw, mr = K[sw][ctx], K[sr][ctx]
            pw, pr = Kp[sw][ctx], Kp[sr][ctx]
            dl = (1 if pr != pw else 0) - (1 if mr != mw else 0)
            if tw and tr:
                f = (1 if dind[sr][ctx] != dind[sw][ctx] else 0) * eps[sr] * eps[sw]
                acc['n_tt'] += 1
                acc['f_tt'] += f
            elif tr:
                f = dind[sr][ctx] * eps[sr] * mw
                acc['n_tf'] += 1
                acc['f_tf'] += f
            elif tw:
                f = dind[sw][ctx] * eps[sw] * mr
                acc['n_ft'] += 1
                acc['f_ft'] += f
            else:
                f = 0
            acc['cls'][(tw, tr)] += 1
            if f != dl:
                acc['dev'] += 1
            if f:
                acc['nz'] += 1
                acc['byc']['+' if f > 0 else '-'] += 1
                acc['S'] += abs(f)
            acc['f'] += f
        run(s0, K, MUL, hx, pairs, sink)
        accs.append(acc)
    dev_tot = sum(a['dev'] for a in accs)
    ev_tot = sum(sum(a['cls'].values()) for a in accs)
    claim('A1', '★★★ 主公式（推導自 R6 A3a）：Δ = Σ_events f，(F,F) 0；(T,T) [d(s_r)≠d(s_w)]·ε(s_r)ε(s_w)；'
                '(T,F) d(s_r)ε(s_r)·x；(F,T) d(s_w)ε(s_w)·x —— 逐事件與 Δ_ind 相等',
          dev_tot == 0, '事件總 = %d ; 逐事件偏離 = %d ; Δ 總和 = %d' % (ev_tot, dev_tot, sum(a['f'] for a in accs)))

    # A3：預測（零態 pointwise）
    dsum = [a['f'] for a in accs]
    Ssum = [a['S'] for a in accs]
    zeros = [s for s in range(n) if dsum[s] == 0]
    zpoint = [s for s in zeros if Ssum[s] == 0]
    claim('A3', '★★ 預測（見數前）：Δ = 0 之 6 態其事件貢獻**逐事件全為 0**（pointwise，非正負相消）',
          len(zeros) == 6 and len(zpoint) == 6,
          'Δ = 0 之態 = %s ; 逐事件全零（S=0）之態 = %s ; S=0 之態數 = %d' % (zeros, zpoint, len(zpoint)))
    claim('A5', '★ S(s0) := Σ|f|；宣稱 Δ(s0) = 0 ⟺ S(s0) = 0；S = 0 態集應 = R6 零態集',
          all((dsum[s] == 0) == (Ssum[s] == 0) for s in range(n)) and len(zpoint) == 6,
          'S 值域 = [%d, %d] ; S = 0 之態 = %s' % (min(Ssum), max(Ssum), zpoint))

    claim('A4b', '★★ 新預測（寫於計算前，接續首跑）：混合類貢獻**逐態**抵消 f_tf(s) + f_ft(s) = 0 ⟹ Δ(s) = f_tt(s)',
          all(a['f_tf'] + a['f_ft'] == 0 for a in accs),
          '逐態違反數 = %d ; f_tf 值集 = %s ; f_ft 值集 = %s ; Δ == f_tt 之態數 = %d/%d'
          % (sum(1 for a in accs if a['f_tf'] + a['f_ft'] != 0), sorted(set(a['f_tf'] for a in accs)),
             sorted(set(a['f_ft'] for a in accs)), sum(1 for a in accs if a['f'] == a['f_tt']), n))

    # A6：A₅ 商聯合表
    # overrides 由事件集重算（機器側）
    ov_l = []
    for s0 in range(n):
        st = {'o': 0}

        def sink2(ctx, sw, sr, st=st):
            if K[sr][ctx] != K[sw][ctx]:
                st['o'] += 1
        run(s0, K, MUL, hx, pairs, sink2)
        ov_l.append(st['o'])
    cls = [min(s, MUL[s][cen]) for s in range(n)]
    ncls = len(set(cls))
    vt_ovm = len(set((cls[s], ov_l[s]) for s in range(n)))
    vt_d = len(set((cls[s], dsum[s]) for s in range(n)))
    vt_S = len(set((cls[s], Ssum[s]) for s in range(n)))
    joint = len(set((cls[s], ov_l[s], dsum[s], Ssum[s]) for s in range(n)))
    claim('A6', '★ 合流：#1 之 Δ 與 overrides 皆為 A₅ 商（60 類）上之函數；報告聯合表值數（核 R5 之 26）',
          ncls == 60 and vt_ovm == 26,
          'A₅ 類 = %d ; ov_machine 值數 = %d（R5 之 26）; Δ 值數 = %d（R6 之 22）; S 值數 = %d ; 四元聯合值數 = %d'
          % (ncls, vt_ovm, vt_d, vt_S, joint))

    vals_ovm = sorted(set(ov_l))
    vals_d = sorted(set(dsum))
    vals_S = sorted(set(Ssum))
    claim('A6c', '★ 修正（見數後，非預測）：以**值集**計數 —— ov_machine = 26（R5）、Δ = 22（R6）；S 值數報告；'
                 '首跑 A6 FAIL 係 (類,值) 對計數（恆 = 60）之 instrument 錯誤',
          len(vals_ovm) == 26 and len(vals_d) == 22,
          'ov_machine 值數 = %d ; Δ 值數 = %d ; S 值數 = %d ; (類,值) 對計數 = %d'
          % (len(vals_ovm), len(vals_d), len(vals_S), vt_ovm))

    # A7：預測（零態線 = ΣS 最小之 2 線）
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(sgn(add(U[i][t], U[j][t])) == 0 for t in range(3)):
                partner[i] = j
    key = [min(a, partner[a]) for a in range(ncol)]
    keys = sorted(set(key))
    ktype = {kk: types[kk] for kk in keys}
    vertex_keys = [kk for kk in keys if ktype[kk] == 'vertex']

    def line_of(s):
        for kk in vertex_keys:
            if same_line(U[kk], KV[s]):
                return kk
        return None
    zlines = sorted(set(line_of(s) for s in zeros))
    lineS = {}
    for s in range(n):
        lineS.setdefault(line_of(s), []).append(Ssum[s])
    totS = {kk: sum(v) for kk, v in lineS.items()}
    rank = sorted(totS, key=lambda kk: (totS[kk], kk))
    pred2 = sorted(rank[:2])
    claim('A7', '★★ 預測（見數前）：零態所在之 2 條線 = 6 條線中 Σ_{20 態} S 最小之 2 條',
          zlines == pred2,
          '零態線 = %s ; ΣS 升序 = %s ; 最小 2 = %s ; 各線 ΣS = %s'
          % (zlines, [(kk, totS[kk]) for kk in rank], pred2, {kk: totS[kk] for kk in sorted(totS)}))

    zpc = {}
    for kk in sorted(lineS):
        zc = sum(1 for s in range(n) if line_of(s) == kk and dsum[s] == 0)
        ntt = [accs[s]['n_tt'] for s in range(n) if line_of(s) == kk]
        zpc[kk] = {'n_states': len(lineS[kk]), 'n_zero': zc, 'sumS': sum(lineS[kk]),
                   'n_tt_range': [min(ntt), max(ntt)], 'sum_f_tt': sum(accs[s]['f_tt'] for s in range(n) if line_of(s) == kk)}
    print('[INFO] A7b 逐線細節（零態數、ΣS、n_tt 範圍、Σf_tt）：%s' % zpc)
    print('[INFO] A7b 推導觀察：單線 20 態、零態 3 個 ⟹ 3 ∤ 20 ⟹ 零態不可能係線內任何子群之陪集（封死該類解釋）')

    # A4：抵消結構（報告；若 A3 成立則全零）
    byc = {k: sum(a['byc'][k] for a in accs) for k in ('+', '-')}
    nz_tot = sum(a['nz'] for a in accs)
    zdetail = {str(s): {'nz_events': accs[s]['nz'], '+': accs[s]['byc']['+'], '-': accs[s]['byc']['-'],
                        'n_tt': accs[s]['n_tt'], 'n_tf': accs[s]['n_tf'], 'n_ft': accs[s]['n_ft']} for s in zeros}
    print('[INFO] A4 抵消結構：非零貢獻事件總數 = %d（+%d / -%d）；零態細節 = %s' % (nz_tot, byc['+'], byc['-'], zdetail))
    print('[INFO] Δ 之分項總和：f_tf = %d ; f_ft = %d ; f_tt = %d' % (sum(a['f_tf'] for a in accs),
                                                                      sum(a['f_ft'] for a in accs),
                                                                      sum(a['f_tt'] for a in accs)))

    # ---------- Part B：edge 參考之 tie 幾何 ----------
    edge_keys = [kk for kk in keys if ktype[kk] == 'edge']
    tieset = {kk: sorted(set(key[a] for a in range(ncol) if sgn(dot3(U[a], U[kk])) == 0)) for kk in keys}
    B1ok = 0
    B1det = {}
    for kk in edge_keys:
        ts = tieset[kk]
        vs = [x for x in ts if ktype[x] == 'vertex']
        es = [x for x in ts if ktype[x] == 'edge']
        got = set()
        for p, q in ((vs[0], vs[1]), (vs[1], vs[0])):
            for s in (1, -1):
                v = vadd(U[p], vscale((F(s), F(0)), U[q]))
                for z in es:
                    if same_line(v, U[z]):
                        got.add(z)
        ok = len(vs) == 2 and len(es) == 2 and got == set(es)
        B1det[str(kk)] = {'vertex': vs, 'edge': es, 'p±q 命中': sorted(got), 'ok': ok}
        B1ok += 1 if ok else 0
    claim('B1', '★★ 預測（見數前）：edge 參考 e 之 2 條 vertex tie 軸 p, q ⟹ p+q 與 p−q 之方向線恰為 e 之 2 條 edge tie 軸',
          B1ok == len(edge_keys),
          '全符 = %d/%d ; 樣本 = %s' % (B1ok, len(edge_keys), B1det[str(edge_keys[0])]))

    # B2：六 tie 軸兩兩精確點積（以第一個 edge 參考為樣本 + 全體歸一化值譜）
    spec = collections.Counter()
    for kk in edge_keys:
        ax = tieset[kk]
        for i in range(len(ax)):
            for j in range(i + 1, len(ax)):
                dd = dot3(U[ax[i]], U[ax[j]])
                den = qmul(nrm2(U[ax[i]]), nrm2(U[ax[j]]))
                spec[qstr(qmul(toq(dd), qinv(toq(den))))] += 1
    print('[INFO] B2 六 tie 軸兩兩歸一化平方值譜（15 edge 參考 × 15 對）：%s' % sorted(spec.items()))
    claim('B2', '報告：edge 參考之 6 tie 軸兩兩精確點積之歸一化值譜（報告項，無預測）',
          len(spec) > 0, '值譜 = %s' % sorted(spec.items()))

    # B3：face tie 身份（報告）
    b3 = {}
    for kk in edge_keys[:3]:
        ts = tieset[kk]
        vs = [x for x in ts if ktype[x] == 'vertex']
        es = [x for x in ts if ktype[x] == 'edge']
        fs = [x for x in ts if ktype[x] == 'face']
        row = {'edge': kk, 'vertex': vs, 'edge_tie': es, 'face_tie': fs,
               'cross(p,q)∥e': len(vs) == 2 and same_line(cross3(U[vs[0]], U[vs[1]]), U[kk]),
               'face·(p+q)': [qstr(dot3(U[f], vadd(U[vs[0]], U[vs[1]]))) for f in fs] if len(vs) == 2 else None,
               'face·(p−q)': [qstr(dot3(U[f], vadd(U[vs[0]], vscale((F(-1), F(0)), U[vs[1]])))) for f in fs] if len(vs) == 2 else None}
        b3[str(kk)] = row
    claim('B3', '報告：edge 參考之 2 條 face tie 軸與 p±q 之精確點積 + cross(p,q) ∥ e（報告項，無預測）',
          all(v['cross(p,q)∥e'] for v in b3.values()), '樣本 = %s' % b3[str(edge_keys[0])])

    out = {'rules': RULES,
           'A1': {'events': ev_tot, 'per_event_dev': dev_tot, 'delta_total': sum(dsum)},
           'A2': {'tie_cells': n_tie_cells, 'sum_d': dtot, 'centre_inv': dci, 'per_state_d_values': sorted(set(per_state))},
           'A3': {'zeros': zeros, 'pointwise_zero': zpoint, 'n_pointwise': len(zpoint)},
           'A5': {'S': Ssum, 'S_range': [min(Ssum), max(Ssum)], 'S_zero_set': zpoint},
           'A6': {'n_classes': ncls, 'ovm_distinct': vt_ovm, 'delta_distinct': vt_d, 'S_distinct': vt_S, 'joint4': joint},
           'A4b': {'per_state_zero': sum(1 for a in accs if a['f_tf'] + a['f_ft'] == 0),
                   'delta_eq_ftt': sum(1 for a in accs if a['f'] == a['f_tt'])},
           'A6c': {'ovm_values': len(vals_ovm), 'delta_values': len(vals_d), 'S_values': len(vals_S)},
           'A7': {'zero_lines': zlines, 'line_sumS': {str(kk): totS[kk] for kk in sorted(totS)},
                  'min2_lines': pred2, 'per_line': {str(kk): zpc[kk] for kk in sorted(zpc)}},
           'A4_report': {'nonzero_events': nz_tot, 'plus': byc['+'], 'minus': byc['-'], 'zero_states_detail': zdetail,
                         'f_tf': sum(a['f_tf'] for a in accs), 'f_ft': sum(a['f_ft'] for a in accs),
                         'f_tt': sum(a['f_tt'] for a in accs)},
           'B1': {'ok': B1ok, 'total': len(edge_keys), 'detail': B1det},
           'B2': {'normalized_sq_spectrum': {k: v for k, v in sorted(spec.items())}},
           'B3': b3,
           'delta': dsum, 'S': Ssum, 'overrides_machine': ov_l, 'line_of_state': [line_of(s) for s in range(n)],
           'tie_entries_d': {str(s): sum(dind[s]) for s in range(n)},
           'claims': CLAIMS}
    with io.open(os.path.join(DATA, '28_r7_mechanism2.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 116)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 116)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
