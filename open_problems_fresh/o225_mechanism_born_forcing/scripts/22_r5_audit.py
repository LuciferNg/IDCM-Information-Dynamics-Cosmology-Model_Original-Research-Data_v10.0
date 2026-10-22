#!/usr/bin/env python3
"""O225 scripts/22 -- R5 獨立審計（唔 import scripts/21）。

A1 軸對普查（元組比較）獨立重算 + 逐參考 n_tie
A2 軌道獨立計法（單一元素 ⋃ 作用 = 全 tie 集；唔用 BFS）
A3 全域計數（重數分佈）
A4 五邊形之獨立恆等式：Σ_{j≠i} ⟨u_i,u_j⟩²/(N_i N_j) = 3/2 EXACT
A5 第二套 replay 實作（不同結構）複現 21 之 K-無關量與 overrides 抽樣
A6 中心不變性（另一路線定中心元素）
用法: /usr/bin/python3 scripts/22_r5_audit.py
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


def A_(x, y):
    return (x[0] + y[0], x[1] + y[1])


def M_(x, y):
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
    return A_(A_(M_(u[0], r[0]), M_(u[1], r[1])), M_(u[2], r[2]))


def Cr(u, r):
    return (A_(M_(u[1], r[2]), Ng(M_(u[2], r[1]))),
            A_(M_(u[2], r[0]), Ng(M_(u[0], r[2]))),
            A_(M_(u[0], r[1]), Ng(M_(u[1], r[0]))))


def fs(v):
    for c in v:
        s = sg(c)
        if s:
            return s
    return 0


def nrm2(u):
    acc = (F(0), F(0))
    for c in u:
        acc = A_(acc, M_(c, c))
    return acc


def replay2(order, s0, Kt, MULt, hxt):
    """第二套實作：狀態機寫法（唔用嵌套 pop 風格），語義同 30_g1g8 之協定。"""
    buf = []
    st = s0
    hits = ov = 0
    miss_total = 0
    recs = []
    for pair in order:
        spent = 0
        for ctx in pair:
            if buf and buf[-1][0] == ctx:
                hits += 1
                if buf[-1][1] != Kt[st][ctx]:
                    ov += 1
                continue
            buf.append((ctx, Kt[st][ctx], st))
            st = MULt[st][hxt[ctx]]
            spent += 1
        ctx, val, st_at = buf[-1]
        buf.pop()
        st = st_at
        if buf and buf[-1][0] == pair[1]:
            hits += 1
            if buf[-1][1] != Kt[st][pair[1]]:
                ov += 1
        else:
            buf.append((pair[1], Kt[st][pair[1]], st))
            st = MULt[st][hxt[pair[1]]]
            spent += 1
        miss_total += spent
        recs.append((spent, buf[-1][0] if buf else -1, len(buf)))
    return {'hits': hits, 'overrides': ov, 'misses': miss_total, 'recs': recs, 'len': len(buf)}


def main():
    print('=' * 112)
    print('O225 scripts/22 -- R5 INDEPENDENT AUDIT')
    print('=' * 112, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'r5a_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    G, idxg, _M2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'r5a_a2').build_group()
    n, ncol = len(K), len(K[0])
    KV = [mm.rot_ref(g, U[0]) for g in G]
    pairs = [(a, b) for a in range(ncol) for b in range(ncol)]

    # A1
    pr = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and U[i][0] == Ng(U[j][0]) and U[i][1] == Ng(U[j][1]) and U[i][2] == Ng(U[j][2]):
                pr[i] = j
    keys = sorted(set(min(i, pr[i]) for i in range(ncol)))
    census = {}
    for kk in keys:
        t = [a for a in range(ncol) if sg(Dt(U[a], U[kk])) == 0]
        census[kk] = (types[kk], len(set(min(x, pr[x]) for x in t)))
    vt = sorted(set(census[k][1] for k in census if census[k][0] == 'vertex'))
    ft = sorted(set(census[k][1] for k in census if census[k][0] == 'face'))
    et = sorted(set(census[k][1] for k in census if census[k][0] == 'edge'))
    ttypes = {}
    for tp in ('vertex', 'face', 'edge'):
        ks = [k for k in census if census[k][0] == tp]
        sigs = set()
        for k in ks:
            c = collections.Counter(types[min(x, pr[x])] for x in range(ncol) if sg(Dt(U[x], U[k])) == 0)
            sigs.add(tuple(sorted(c.keys())))
        ttypes[tp] = sorted(sigs)
    a1c = (vt == [5] and ft == [3] and et == [6]
           and ttypes['vertex'] == [('edge',)] and ttypes['face'] == [('edge',)]
           and ttypes['edge'] == [('edge', 'face', 'vertex')])
    claim('A1c', '獨立普查（原 A1 之樸素形式 vertex/face/edge ∈ {0,5} 全 edge 被否證，首跑日誌保留）：'
                 'vertex → 5 全 edge；face → 3 全 edge；edge → 6 混合',
          len(pr) == 62 and len(keys) == 31 and a1c,
          'pairs=%d ; vertex=%s face=%s edge=%s ; 型別 = %s' % (len(keys), vt, ft, et, ttypes))

    # A2 + A4
    ref = [k for k in keys if types[k] == 'vertex'][0]
    Hr = []
    for g in range(n):
        v = mm.rot_ref(G[g], U[ref])
        if all(sg(A_(v[t], Ng(U[ref][t]))) == 0 for t in range(3)) or \
           all(sg(A_(v[t], U[ref][t])) == 0 for t in range(3)):
            Hr.append(g)
    tie = sorted(set(min(a, pr[a]) for a in range(ncol) if sg(Dt(U[a], U[ref])) == 0))

    def act(g, a):
        v = mm.rot_ref(G[g], U[a])
        for b in range(ncol):
            if all(sg(A_(v[t], Ng(U[b][t]))) == 0 for t in range(3)) or \
               all(sg(A_(v[t], U[b][t])) == 0 for t in range(3)):
                return min(b, pr[b])
        return None
    orb = set()
    for g in Hr:
        y = act(g, tie[0])
        if y is not None:
            orb.add(y)
    claim('A2', '獨立軌道計法：單一 tie 元素在 H_r 下之軌跡 = 全 tie 集（大小 5）',
          len(orb) == 5 and orb == set(tie) and len(Hr) == 20,
          '|H_r|=%d ; |orbit|=%d ; orbit == tie set ? %s' % (len(Hr), len(orb), orb == set(tie)))

    c36 = (F(3, 8), F(1, 8))
    c72 = (F(3, 8), F(-1, 8))
    s_ok = True
    details = []
    for kk in [k for k in keys if types[k] == 'vertex']:
        ax = sorted(set(min(a, pr[a]) for a in range(ncol) if sg(Dt(U[a], U[kk])) == 0))
        details.append(len(ax))
        # 獨立恆等式：Σ_{j≠i} ⟨u_i,u_j⟩²/(N_i N_j) = 3/2（用逐對分類計數核對）
        cnt = collections.Counter()
        for i in range(len(ax)):
            for j in range(i + 1, len(ax)):
                d2 = M_(Dt(U[ax[i]], U[ax[j]]), Dt(U[ax[i]], U[ax[j]]))
                rhs = M_(nrm2(U[ax[i]]), nrm2(U[ax[j]]))
                if sg(A_(d2, Ng(M_(rhs, c36)))) == 0:
                    cnt[36] += 1
                elif sg(A_(d2, Ng(M_(rhs, c72)))) == 0:
                    cnt[72] += 1
                else:
                    s_ok = False
        if sorted(cnt.items()) != [(36, 5), (72, 5)]:
            s_ok = False
    claim('A4', '獨立幾何核：每頂點軸之 tie 五線族 —— 36°:72° = 5:5，無第三種值（兩條精確平方等式）',
          s_ok, 'tie 集大小 = %s ; 全符 = %s' % (details, s_ok))

    # A3
    inc = collections.Counter()
    for kk in [k for k in keys if types[k] == 'vertex']:
        for a in range(ncol):
            if sg(Dt(U[a], U[kk])) == 0:
                inc[min(a, pr[a])] += 1
    edge_keys = [k for k in keys if types[k] == 'edge']
    a3c = (sum(inc.values()) == 60 and set(inc.get(k, 0) for k in edge_keys) == {4}
           and all(inc.get(k, 0) == 0 for k in keys if types[k] != 'edge')
           and 6 * 5 == 15 * 2)
    claim('A3c', '獨立全域計數（原 A3 之「重數 ≡ 1」被否證）：Σ = 60 = 15 × 4（欄計數）⟹ 每 edge 軸 ⟂ 恰 2 條頂點軸；'
                 '對稱自洽 6×5 = 15×2 = 30', a3c,
          'Σ=%d ; edge 重數=%s ; 6×5=%d ; 15×2=%d' % (sum(inc.values()),
           sorted(set(inc.get(k, 0) for k in edge_keys)), 6 * 5, 15 * 2))

    # A4b：face 參考之正三角形（獨立重算 Q4b 之預測）
    fdev = fn = 0
    for kk in [k for k in keys if types[k] == 'face']:
        ax = sorted(set(min(a, pr[a]) for a in range(ncol) if sg(Dt(U[a], U[kk])) == 0))
        for i in range(len(ax)):
            for j in range(i + 1, len(ax)):
                fn += 1
                d2 = M_(Dt(U[ax[i]], U[ax[j]]), Dt(U[ax[i]], U[ax[j]]))
                rhs = M_(nrm2(U[ax[i]]), nrm2(U[ax[j]]))
                if sg(A_(d2, Ng(M_(rhs, (F(1, 4), F(0)))))) != 0:
                    fdev += 1
    claim('A4b', '獨立核 Q4b：face 參考之 3 條 tie 軸兩兩 ⟨·,·⟩² = N_i N_j / 4 EXACT（正三角形線族）',
          fdev == 0 and fn == 30, '對數 = %d ; 偏離 = %d' % (fn, fdev))

    # A5：第二套 replay（3 變體 × 8 態）
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
    samples = [0, 1, 7, 23, 44, 61, 88, 119]
    res = {nm: {} for nm in ('m', 'p', 'n')}
    for nm, Kt in (('m', K), ('p', Kp), ('n', Kn)):
        for s in samples:
            res[nm][s] = replay2(pairs, s, Kt, MUL, hx)
    hits_ok = all(res['m'][s]['hits'] == res['p'][s]['hits'] == res['n'][s]['hits'] for s in samples)
    miss_ok = all(res['m'][s]['misses'] == res['p'][s]['misses'] == res['n'][s]['misses'] for s in samples)
    rec_ok = all(res['m'][s]['recs'] == res['p'][s]['recs'] for s in samples)
    ref21 = json.load(io.open(os.path.join(DATA, '21_r5_tie_global.json'), encoding='utf-8'))
    ov_m = [res['m'][s]['overrides'] for s in samples]
    ov_p = [res['p'][s]['overrides'] for s in samples]
    match21 = (ov_m == [ref21['overrides_machine'][s] for s in samples]
               and ov_p == [ref21['overrides_prod'][s] for s in samples])
    claim('A5', '第二套 replay 實作：hits/Σmisses/逐對記錄 三變體相同；overrides 抽樣 8 態與 21 之輸出逐值一致',
          hits_ok and miss_ok and rec_ok and match21,
          'hits 同=%s ; misses 同=%s ; recs 同=%s ; 對 21 逐值一致=%s ; overrides(m)=%s overrides(p)=%s'
          % (hits_ok, miss_ok, rec_ok, match21, ov_m[:4], ov_p[:4]))

    # A6：中心不變（另一路線定中心）
    ident = [i for i in range(n) if all(MUL[i][j] == j for j in range(n))]
    cen = [i for i in range(n) if i not in ident and all(MUL[i][j] == MUL[j][i] for j in range(n))]
    ci_ok = True
    if cen:
        z = cen[0]
        need = set()
        for s in samples:
            need.add(MUL[s][z])
        for s in sorted(need - set(samples)):
            res['p'][s] = replay2(pairs, s, Kp, MUL, hx)
        for s in samples:
            if res['p'][s]['overrides'] != res['p'][MUL[s][z]]['overrides']:
                ci_ok = False
    claim('A6', '中心不變（獨立定中心元素）：overrides_prod(s) = overrides_prod(−s) 於抽樣態',
          bool(cen) and ci_ok, '中心元素 = %s ; 抽樣全符 = %s' % (cen, ci_ok))

    out = {'audit_of': '21_r5_tie_global.py',
           'A1': {'pairs': len(keys), 'vertex': vt, 'face': ft, 'edge': et},
           'A2': {'Hr': len(Hr), 'orbit': len(orb)}, 'A3': {'total': sum(inc.values())},
           'A4': {'tie_sizes': details, 'ok': s_ok},
           'A5': {'hits_equal': hits_ok, 'misses_equal': miss_ok, 'recs_equal': rec_ok, 'match21': match21},
           'A6': {'centre': cen, 'ok': ci_ok}, 'claims': CLAIMS}
    with io.open(os.path.join(DATA, '22_r5_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 112)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
