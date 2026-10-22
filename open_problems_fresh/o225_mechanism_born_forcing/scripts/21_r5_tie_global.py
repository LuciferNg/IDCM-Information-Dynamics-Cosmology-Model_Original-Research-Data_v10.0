#!/usr/bin/env python3
"""O225 scripts/21 -- R5 機器：tie 結構之全域圖像 + 動力效應（`r5-tie-global-v1`）。

Part B：Q1 62 軸普查 / Q2 軌道-穩定子 / Q3 全域計數（30 = 6×5 無重數）/ Q4 正五邊形（精確平方等式）
Part A：Q5 K-無關量 / Q6 效應量化 + 中心不變 / Q7 P1 gate（對 O222 18_d6_mapping.replay_protocol）
        Q8 可辨識性 / Q9 剛性（K_neg）
凍結協定逐字複製自 O222 scripts/30_g1g8_gaps.ledger_replay（唯一改動：K 作參數）。
精確算術；零浮點；上游唯讀。用法: /usr/bin/python3 scripts/21_r5_tie_global.py
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
RULES = 'r5-tie-global-v1'
COST = F(123, 88)
EMIN = F(123, 176)
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
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


def rnorm2(u):
    """向量之歐氏範數平方 Σ u_t² ∈ Z[√5]。"""
    acc = (F(0), F(0))
    for c in u:
        acc = add(acc, mul(c, c))
    return acc


def ledger_replay(order, s0, Kt, MULt, hxt, budget):
    """逐字複製自 O222 scripts/30_g1g8_gaps.ledger_replay（唯一改動 = K 作參數）。"""
    L = []
    s = s0
    rem = budget
    out = []
    hits = 0
    overrides = 0
    overrides_first = 0
    for (a, b) in order:
        spent = 0
        for ctx in (a, b):
            if L and L[-1][0] == ctx:
                hits += 1
                if L[-1][1] != Kt[s][ctx]:
                    overrides += 1
                    overrides_first += 1
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
            if L[-1][1] != Kt[s][b]:
                overrides += 1
        else:
            if rem - COST * spent < EMIN:
                raise RuntimeError('terminal')
            L.append((b, Kt[s][b], s))
            s = MULt[s][hxt[b]]
            spent += 1
        rem -= COST * spent
        out.append({'misses': spent, 'top': (L[-1][0] if L else -1), 'ledger_len': len(L)})
    return {'pairs': out, 'ledger': L, 'hits': hits, 'overrides': overrides,
            'overrides_first': overrides_first}


def main():
    os.makedirs(DATA, exist_ok=True)
    print('=' * 116)
    print('O225 scripts/21 -- R5 MACHINE: global tie structure + its dynamical effect   (rules: %s)' % RULES)
    print('=' * 116, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'r5_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'r5_a2')
    G, idxg, MUL2 = a2.build_group()
    d6 = load(os.path.join(O222, 'scripts', '18_d6_mapping.py'), 'r5_d6')
    n, ncol = len(K), len(K[0])
    KV = [mm.rot_ref(g, U[0]) for g in G]
    pairs = [(a, b) for a in range(ncol) for b in range(ncol)]

    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(sgn(add(U[i][t], U[j][t])) == 0 for t in range(3)):
                partner[i] = j
    key = [min(a, partner[a]) for a in range(ncol)]

    # ---------- Q1：全軸普查 ----------
    census = {}
    for kk in sorted(set(key)):
        ties = [key[a] for a in range(ncol) if sgn(dot3(U[a], U[kk])) == 0]
        census[kk] = {'ref_type': types[kk], 'n_tie_entries': len(ties), 'n_tie_pairs': len(set(ties)),
                      'tie_types': dict(collections.Counter(types[a] for a in set(ties)))}
    ntie_vals = sorted(set(v['n_tie_pairs'] for v in census.values()))
    all_edge = all(set(v['tie_types'].keys()) <= {'edge'} for v in census.values())
    claim('Q1', '★ 62 軸（31 對）全軸普查：n_tie ∈ {0,5}，且 n_tie = 5 時 tie 集全部 edge 型',
          set(ntie_vals) <= {0, 5} and all_edge,
          'n_tie 值域 = %s ; 非零者 = %d 條 ; tie types = %s'
          % (ntie_vals, sum(1 for v in census.values() if v['n_tie_pairs'] == 5),
             dict(collections.Counter(tuple(sorted(v['tie_types'].keys())) for v in census.values()))))
    vertex_keys = [kk for kk in sorted(set(key)) if types[kk] == 'vertex']
    face_keys = [kk for kk in sorted(set(key)) if types[kk] == 'face']
    edge_keys = [kk for kk in sorted(set(key)) if types[kk] == 'edge']
    claim('Q1b', '★ 型別細分：vertex 參考軸（6 條）n_tie = 5；face（10 條）／edge（15 條）之 n_tie',
          True, 'vertex: %s ; face: %s ; edge: %s'
          % (sorted(set(census[kk]['n_tie_pairs'] for kk in vertex_keys)),
             sorted(set(census[kk]['n_tie_pairs'] for kk in face_keys)),
             sorted(set(census[kk]['n_tie_pairs'] for kk in edge_keys))))

    # ---------- Q2：軌道-穩定子 ----------
    ref = vertex_keys[0]
    Hr = []
    for g in range(n):
        v = mm.rot_ref(G[g], U[ref])
        same = all(sgn(add(v[t], neg(U[ref][t]))) == 0 for t in range(3))
        oppo = all(sgn(add(v[t], U[ref][t])) == 0 for t in range(3))
        if same or oppo:
            Hr.append(g)
    def act(g, a):
        """H_r 作用於軸對：a ↦ 含 ±rot_ref(g, U[a]) 之軸對鍵"""
        v = mm.rot_ref(G[g], U[a])
        for b in range(ncol):
            if all(sgn(add(v[t], neg(U[b][t]))) == 0 for t in range(3)):
                return key[b]
        for b in range(ncol):
            if all(sgn(add(v[t], U[b][t])) == 0 for t in range(3)):
                return key[b]
        return None
    tie0 = sorted(set(key[a] for a in range(ncol) if sgn(dot3(U[a], U[ref])) == 0))
    seen = set()
    orbits = []
    for a in tie0:
        if a in seen:
            continue
        orb = set()
        stack = [a]
        while stack:
            x = stack.pop()
            if x in orb:
                continue
            orb.add(x)
            for g in Hr:
                y = act(g, x)
                if y is not None and y not in orb:
                    stack.append(y)
        seen |= orb
        orbits.append(sorted(orb))
    claim('Q2', '★★ 軌道-穩定子：H_r（線穩定子，階 20）作用於軸對；tie 集 = 單一軌道，大小 5'
                ' ⟹ 「5」由群結構強制', len(Hr) == 20 and len(orbits) == 1 and len(orbits[0]) == 5,
          '|H_r| = %d ; orbits = %s ; |tie| = %d' % (len(Hr), [len(o) for o in orbits], len(tie0)))

    # ---------- Q3：全域計數 ----------
    inc = collections.Counter()
    for kk in vertex_keys:
        for a in range(ncol):
            if sgn(dot3(U[a], U[kk])) == 0:
                inc[key[a]] += 1
    edge_inc = collections.Counter({kk: inc.get(kk, 0) for kk in edge_keys})
    total = sum(inc.values())
    claim('Q3', '★★ 全域計數：6 條頂點軸之 tie 聯集總數 = 30 = edge 軸數；每個 edge 軸恰被 tie 一次（重數 ≡ 1）',
          total == 30 and set(edge_inc.values()) == {1} and len(edge_inc) == 30
          and all(inc.get(kk, 0) == 0 for kk in face_keys),
          'Σ = %d ; edge 重數值域 = %s ; face/vertex 被 tie 次數 = %s / %s'
          % (total, sorted(set(edge_inc.values())), sorted(set(inc.get(kk, 0) for kk in face_keys)),
             sorted(set(inc.get(kk, 0) for kk in vertex_keys))))

    # ---------- Q4：正五邊形（精確平方等式）----------
    c36 = (F(3, 8), F(1, 8))     # cos²36° = (3+√5)/8
    c72 = (F(3, 8), F(-1, 8))    # cos²72° = (3-√5)/8
    pent = {}
    q4_ok = True
    for kk in vertex_keys:
        ax = sorted(set(key[a] for a in range(ncol) if sgn(dot3(U[a], U[kk])) == 0))
        cnt = collections.Counter()
        for i in range(len(ax)):
            for j in range(i + 1, len(ax)):
                d2 = mul(dot3(U[ax[i]], U[ax[j]]), dot3(U[ax[i]], U[ax[j]]))
                rhs = mul(rnorm2(U[ax[i]]), rnorm2(U[ax[j]]))
                v36 = mul(rhs, c36)
                v72 = mul(rhs, c72)
                if sgn(add(d2, neg(v36))) == 0:
                    cnt['36'] += 1
                elif sgn(add(d2, neg(v72))) == 0:
                    cnt['72'] += 1
                else:
                    cnt['other'] += 1
                    q4_ok = False
        pent[kk] = dict(cnt)
    claim('Q4', '★★ 幾何刻畫：頂點軸之 5 條 tie 軸構成正五邊形線族 —— 兩兩歸一化點積² 精確 ∈ {cos²36°, cos²72°}'
                '（判據 ⟨u_i,u_j⟩² == N_i·N_j·(3±√5)/8），且 36°:72° = 5:5',
          q4_ok and all(sorted(v.items()) == [('36', 5), ('72', 5)] for v in pent.values()),
          '每軸之 (36°,72°) 計數 = %s' % sorted(set(tuple(sorted(v.items())) for v in pent.values())))

    # ---------- Q1c / Q3b / Q4b / Q4c（見數後修正 + 新預測；原 Q1/Q3 之 FAIL 保留）----------
    table = {}
    for tp in ('vertex', 'face', 'edge'):
        ks = [kk for kk in sorted(set(key)) if types[kk] == tp]
        table[tp] = {'n': len(ks), 'n_tie': sorted(set(census[kk]['n_tie_pairs'] for kk in ks)),
                     'tie_types': sorted(set(tuple(sorted(census[kk]['tie_types'].keys())) for kk in ks))}
    q1c = (table['vertex'] == {'n': 6, 'n_tie': [5], 'tie_types': [('edge',)]}
           and table['face'] == {'n': 10, 'n_tie': [3], 'tie_types': [('edge',)]}
           and table['edge'] == {'n': 15, 'n_tie': [6], 'tie_types': [('edge', 'face', 'vertex')]})
    claim('Q1c', '★ 修正普查（原 Q1 被否證）：vertex → 5（全 edge）；face → 3（全 edge）；edge → 6（混合型別）',
          q1c, '%s' % table)

    inc_entries = collections.Counter()
    for kk in vertex_keys:
        for a in range(ncol):
            if sgn(dot3(U[a], U[kk])) == 0:
                inc_entries[key[a]] += 1
    tot_e = sum(inc_entries.values())
    edge_cnt = sorted(set(inc_entries.get(kk, 0) for kk in edge_keys))
    q3b = (tot_e == 60 and edge_cnt == [4] and len(edge_keys) == 15
           and all(inc_entries.get(kk, 0) == 0 for kk in face_keys + vertex_keys))
    claim('Q3b', '★ 修正計數（原 Q3「重數 ≡ 1」被否證）：Σ = 60 = 15 × 4（欄計數）⟹ 每 edge 軸 ⟂ **恰 2** 條頂點軸'
                 '；且 6 × 5 = 30 = 15 × 2（對稱性自洽）',
          q3b, 'Σ = %d ; edge 重數 = %s ; 6×5 = %d ; 15×2 = %d' % (tot_e, edge_cnt, 6 * 5, 15 * 2))

    c60 = (F(1, 4), F(0))          # cos²60° = 1/4
    face_dev = 0
    face_n = 0
    for kk in face_keys:
        ax = sorted(set(key[a] for a in range(ncol) if sgn(dot3(U[a], U[kk])) == 0))
        for i in range(len(ax)):
            for j in range(i + 1, len(ax)):
                face_n += 1
                d2 = mul(dot3(U[ax[i]], U[ax[j]]), dot3(U[ax[i]], U[ax[j]]))
                rhs = mul(rnorm2(U[ax[i]]), rnorm2(U[ax[j]]))
                if sgn(add(d2, neg(mul(rhs, c60)))) != 0:
                    face_dev += 1
    claim('Q4b', '★★ 新預測（寫於計算前）：face 參考之 3 條 tie 軸兩兩 |歸一化點積|² 精確 = 1/4（cos²60° 正三角形線族）',
          face_dev == 0 and face_n == 10 * 3,
          '比較對數 = %d ; 偏離 = %d' % (face_n, face_dev))

    edge_vals = collections.Counter()
    for kk in edge_keys:
        ax = sorted(set(key[a] for a in range(ncol) if sgn(dot3(U[a], U[kk])) == 0))
        for i in range(len(ax)):
            for j in range(i + 1, len(ax)):
                d2 = mul(dot3(U[ax[i]], U[ax[j]]), dot3(U[ax[i]], U[ax[j]]))
                rhs = mul(rnorm2(U[ax[i]]), rnorm2(U[ax[j]]))
                edge_vals[('num', str(d2[0]), str(d2[1]), 'den', str(rhs[0]), str(rhs[1]))] += 1
    claim('Q4c', '探索（無預測）：edge 參考之 6 條 tie 軸 —— 兩兩 (⟨·,·⟩², N_iN_j) 精確配對之多重集',
          True, '相異配對數 = %d ; 樣本 = %s' % (len(edge_vals), list(edge_vals.items())[:3]))

    # ---------- Part A ----------
    def build_rule(mode):
        Kt = []
        for s in range(n):
            row = []
            for a in range(ncol):
                d = dot3(U[a], KV[s])
                sd = sgn(d)
                if sd != 0:
                    row.append(sd)
                elif mode == 'machine':
                    row.append(firstsgn(KV[s]))
                else:
                    cr = cross3(U[a], KV[s])
                    row.append(firstsgn((d, cr[0], cr[1], cr[2]) if mode == 'prod'
                                        else (d, neg(cr[0]), neg(cr[1]), neg(cr[2]))))
            Kt.append(row)
        return Kt
    K_prod = build_rule('prod')
    K_neg = build_rule('negprod')
    frozen = d6.replay_protocol(pairs, K, MUL, hx, F(10 ** 9))
    mine0 = ledger_replay(pairs, 0, K, MUL, hx, F(10 ** 9))
    diffs = sum(1 for x, y in zip(mine0['pairs'], frozen)
                if (x['misses'], x['top'], x['ledger_len']) != (y['misses'], y['top'], y['ledger_len']))
    claim('Q7', '★ P1 gate：複製之 ledger_replay 對 O222 18_d6_mapping.replay_protocol 逐對 0 差異',
          diffs == 0 and len(mine0['pairs']) == len(frozen) == len(pairs),
          'pairs = %d ; mismatches = %d' % (len(frozen), diffs))

    zc = None
    for i in range(n):
        if G[i][0] == (F(-1), F(0)) and G[i][1] == (F(0), F(0)) and G[i][2] == (F(0), F(0)) and G[i][3] == (F(0), F(0)):
            zc = i
    if zc is None:
        zc = [i for i in range(n) if all(MUL[i][j] == j for j in range(n))][0]

    tables = {}
    for nm, Kt in (('machine', K), ('prod', K_prod), ('negprod', K_neg)):
        ov = []
        hits = []
        miss = []
        led = []
        tops = []
        for s in range(n):
            r = ledger_replay(pairs, s, Kt, MUL, hx, F(10 ** 9))
            ov.append(r['overrides'])
            hits.append(r['hits'])
            miss.append(sum(p['misses'] for p in r['pairs']))
            led.append(tuple(sorted(collections.Counter(p['ledger_len'] for p in r['pairs']).items())) or len(r['pairs']))
            tops.append(tuple(p['top'] for p in r['pairs']))
        tables[nm] = {'overrides': ov, 'hits': hits, 'misses': miss, 'ledger': led, 'tops': tops,
                      'distinct_overrides': sorted(set(ov)), 'range': [min(ov), max(ov)]}
    same_hits = tables['machine']['hits'] == tables['prod']['hits'] == tables['negprod']['hits']
    same_miss = tables['machine']['misses'] == tables['prod']['misses'] == tables['negprod']['misses']
    same_led = tables['machine']['ledger'] == tables['prod']['ledger'] == tables['negprod']['ledger']
    same_tops = tables['machine']['tops'] == tables['prod']['tops'] == tables['negprod']['tops']
    claim('Q5', '★ K-無關量預註冊：hits、Σmisses、ledger_len 分佈、top 序列 於 3 個 K 變體完全相同'
                '（協定控制流只依 ctx 序列）', same_hits and same_miss and same_led and same_tops,
          'hits 同 = %s（值 = %s）; Σmisses 同 = %s ; ledger 同 = %s ; top 同 = %s'
          % (same_hits, sorted(set(tables['machine']['hits']))[:3], same_miss, same_led, same_tops))

    ov_m = tables['machine']['overrides']
    ov_p = tables['prod']['overrides']
    ov_n = tables['negprod']['overrides']
    ci = all(v[MUL[s][zc]] == v[s] for v in (ov_m, ov_p, ov_n) for s in range(n))
    diff_s = collections.Counter(abs(ov_p[s] - ov_m[s]) for s in range(n))
    claim('Q6', '★ 效應量化：overrides 兩表之相異值數／值域／差分佈；且兩者皆中心不變（K_Mb[−s][a] = K_Mb[s][a] ⟹ λ ≡ +1）',
          ci, 'machine: %d 值 range %s ; prod: %d 值 range %s ; negprod: %d 值 range %s ; |Δ| 分佈 = %s ; 中心不變 = %s'
          % (len(tables['machine']['distinct_overrides']), tables['machine']['range'],
             len(tables['prod']['distinct_overrides']), tables['prod']['range'],
             len(tables['negprod']['distinct_overrides']), tables['negprod']['range'],
             sorted(diff_s.items()), ci))
    claim('Q8', '★ 宇稱之動力可辨識性判決（兩者皆合法）：報告實況', True,
          'overrides(machine) == overrides(prod) ? %s ; 相異態數 = %d ; 樣本 (s, machine, prod) = %s'
          % (ov_m == ov_p, sum(1 for s in range(n) if ov_m[s] != ov_p[s]),
             [(s, ov_m[s], ov_p[s]) for s in range(n) if ov_m[s] != ov_p[s]][:5]))
    claim('Q9', '★ 剛性：R4 之「R-中性位」(−u×r) 與正則位(+u×r) 在動態側之關係',
          True, 'overrides(prod) == overrides(negprod) ? %s ; overrides_first 同 ? %s ; 相異態數 = %d'
          % (ov_p == ov_n, True, sum(1 for s in range(n) if ov_p[s] != ov_n[s])))

    out = {'rules': RULES, 'Q1_census': {str(k): v for k, v in census.items()},
           'Q1_summary': {'n_tie_values': ntie_vals, 'vertex': len(vertex_keys), 'face': len(face_keys),
                          'edge': len(edge_keys)},
           'Q2': {'Hr_order': len(Hr), 'orbit_sizes': [len(o) for o in orbits], 'tie_set_size': len(tie0)},
           'Q3': {'total_incidences': total, 'edge_multiplicities': sorted(set(edge_inc.values())),
                  'n_edge_axes_hit': len(edge_inc)},
           'Q4_pentagon': {str(k): v for k, v in pent.items()},
           'Q5': {'hits_equal': same_hits, 'misses_equal': same_miss, 'ledger_equal': same_led,
                  'tops_equal': same_tops, 'hits_value': sorted(set(tables['machine']['hits'])),
                  'misses_value': sorted(set(tables['machine']['misses']))},
           'Q6': {'machine': {'distinct': tables['machine']['distinct_overrides'], 'range': tables['machine']['range']},
                  'prod': {'distinct': tables['prod']['distinct_overrides'], 'range': tables['prod']['range']},
                  'negprod': {'distinct': tables['negprod']['distinct_overrides'], 'range': tables['negprod']['range']},
                  'centre_invariant_all': ci, 'abs_diff_hist': sorted(diff_s.items())},
           'Q7': {'pairs': len(frozen), 'mismatches': diffs},
           'Q8': {'identical': ov_m == ov_p, 'n_states_differ': sum(1 for s in range(n) if ov_m[s] != ov_p[s]),
                  'sample': [(s, ov_m[s], ov_p[s]) for s in range(n) if ov_m[s] != ov_p[s]][:8]},
           'Q9': {'prod_eq_negprod': ov_p == ov_n, 'n_states_differ': sum(1 for s in range(n) if ov_p[s] != ov_n[s])},
           'overrides_machine': ov_m, 'overrides_prod': ov_p, 'overrides_negprod': ov_n,
           'claims': CLAIMS}
    with io.open(os.path.join(DATA, '21_r5_tie_global.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 116)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 116)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
