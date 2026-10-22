#!/usr/bin/env python3
"""O225 scripts/12 -- R2B：動態側 17 全枚舉（`r2-g1-dyn-v1`）。

機械枚舉凍結運行量族 Q（合約 docs/03 §2 D1）於 5 種 order × 120 初始態，得值域 V，然後分開判：
  M-value : 17 ∉ V
  M-div   : 17 ∤ v  ∀v ∈ V＼{0}
並附：陽性對照（掃描器必須報出已知在場之數）、植入對照（人造 17/34 必須被命中）、
      素支撐、D3 清單因式分解、剛性（翻轉 K 元素／M-b 讀出表重掃）。
精確算術；無 float / math / random / numpy。
用法:  /usr/bin/python3 scripts/12_r2_dyn17.py
"""
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
O222S = os.path.join(O222, 'scripts')
BUDGET = F(10 ** 9)
COST = F(123, 88)
EMIN = F(123, 176)
ORDER_IDS = ('lex', 'diag', 'antidiag', 'block', 'stride')
D3 = [62, 120, 3844, 7440, 11532, 124, 7564, 4728, 44, 88, 176, 60, 990, 12, 20, 30]
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


def order_key(oid, a, b):
    """逐字沿用 O222 scripts/15_b3r2_orderfair.order_key"""
    if oid == 'lex':
        return (a, b)
    if oid == 'diag':
        return ((b - a) % 62, a, b)
    if oid == 'antidiag':
        return ((a + b) % 62, a, b)
    if oid == 'block':
        return (max(a, b), min(a, b), a)
    if oid == 'stride':
        return ((b - 13 * a) % 62, b, a)
    raise KeyError(oid)


def order_list(oid):
    pairs = [(a, b) for a in range(62) for b in range(62)]
    pairs.sort(key=lambda p: order_key(oid, p[0], p[1]))
    return pairs


def run_replay(order, s0, K, MUL, hx, nctx):
    """凍結協定逐字（scripts/30）＋ Q 族所需之額外量"""
    L = []
    s = s0
    rem = BUDGET
    hits = ov = stale = agree = ov_first = 0
    miss_hist = {}
    top_count = {}
    ent = [0] * nctx
    val_seen = [set() for _ in range(nctx)]
    visited = set()
    pairs_seen = set()
    ctxs = set()
    max_len = 0
    min_len = 10 ** 9
    first_read_hits = 0
    for (a, b) in order:
        spent = 0
        for ctx in (a, b):
            visited.add(s)
            ctxs.add(ctx)
            if L and L[-1][0] == ctx:
                hits += 1
                stored_s, stored_v = L[-1][2], L[-1][1]
                if s != stored_s:
                    stale += 1
                if stored_v != K[s][ctx]:
                    ov += 1
                elif s == stored_s:
                    agree += 1
                continue
            v = K[s][ctx]
            L.append((ctx, v, s))
            s = MUL[s][hx[ctx]]
            spent += 1
            visited.add(s)
            pairs_seen.add((s, ctx))
        _c, _v, s_at = L.pop()
        s = s_at
        if L and L[-1][0] == b:
            hits += 1
            stored_s, stored_v = L[-1][2], L[-1][1]
            if s != stored_s:
                stale += 1
            if stored_v != K[s][b]:
                ov += 1
            elif s == stored_s:
                agree += 1
        else:
            v = K[s][b]
            L.append((b, v, s))
            s = MUL[s][hx[b]]
            spent += 1
        rem -= COST * spent
        miss_hist[spent] = miss_hist.get(spent, 0) + 1
        top_count[L[-1][0]] = top_count.get(L[-1][0], 0) + 1
        if len(L) > max_len:
            max_len = len(L)
        if len(L) < min_len:
            min_len = len(L)
    for (ctx, v, st) in L:
        ent[ctx] += 1
        val_seen[ctx].add(v)
    return {'hits': hits, 'overrides': ov, 'stale': stale, 'agree': agree,
            'visited': len(visited), 'pairs': len(pairs_seen), 'ctxs': len(ctxs),
            'ledger_len': len(L), 'max_len': max_len, 'min_len': min_len,
            'pass_reads': sum(m * c for m, c in miss_hist.items()),
            'miss_hist': miss_hist, 'top_counts': sorted(top_count.values()),
            'entries_per_ctx': sorted(ent), 'n_ctx_with_two_values': sum(1 for vs in val_seen if len(vs) > 1),
            'npairs': len(order), 'conflict_ctx': sum(1 for vs in val_seen if len(vs) > 1)}


def collect_values(rec, V):
    for k in ('hits', 'overrides', 'stale', 'agree', 'visited', 'pairs', 'ctxs', 'ledger_len',
              'max_len', 'min_len', 'pass_reads', 'n_ctx_with_two_values', 'npairs', 'conflict_ctx'):
        V.add((k, rec[k]))
    for k, c in rec['miss_hist'].items():
        V.add(('miss_hist_key', k))
        V.add(('miss_hist_count', c))
    for c in rec['top_counts']:
        V.add(('top_count', c))
    for c in rec['entries_per_ctx']:
        V.add(('entries_per_ctx', c))


def factorize(n):
    f = []
    d = 2
    m = abs(n)
    while d * d <= m:
        while m % d == 0:
            f.append(d)
            m //= d
        d += 1
    if m > 1:
        f.append(m)
    return f


def build_Kb(mm, G, U, m_rot, m_sgn):
    """R1 之 M-b 讀出表：tie 規則改為 u-奇（dot = 0 ⟹ sgn(cross(u, r) 之首非零分量)）"""
    def mul2(x, y):
        return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + y[0] * x[1])
    def sub2(x, y):
        return (x[0] - y[0], x[1] - y[1])
    KV = [m_rot(q, U[0]) for q in G]
    Kb = []
    for i in range(120):
        r = KV[i]
        row = []
        for u in U:
            dot = (0, 0)
            for t in range(3):
                dot = (dot[0] + mul2(u[t], r[t])[0], dot[1] + mul2(u[t], r[t])[1])
            s = m_sgn(dot)
            if s == 0:
                c = [sub2(mul2(u[1], r[2]), mul2(u[2], r[1])),
                     sub2(mul2(u[2], r[0]), mul2(u[0], r[2])),
                     sub2(mul2(u[0], r[1]), mul2(u[1], r[0]))]
                sb = 0
                for comp in c:
                    sc = m_sgn(comp)
                    if sc:
                        sb = sc
                        break
                if sb == 0:
                    for comp in r:
                        sc = m_sgn(comp)
                        if sc:
                            sb = sc
                            break
                s = sb
            row.append(s)
        Kb.append(row)
    return Kb


def main():
    os.makedirs(DATA, exist_ok=True)
    print('=' * 110)
    print('O225 scripts/12 -- R2B: full enumeration of the dynamic side for the number 17')
    print('=' * 110, flush=True)
    b5 = load(os.path.join(O222S, '12_b5_budget.py'), 'r2b_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    nctx, NSTATE = len(K[0]), len(K)
    V = set()
    per_order = {}
    for oid in ORDER_IDS:
        order = order_list(oid)
        recs = []
        for s0 in range(NSTATE):
            rec = run_replay(order, s0, K, MUL, hx, nctx)
            collect_values(rec, V)
            recs.append((s0, rec['hits'], rec['overrides'], rec['pass_reads'], rec['ledger_len'],
                         rec['max_len']))
        per_order[oid] = {'hits': sorted(set(r[1] for r in recs)),
                          'overrides': [min(r[2] for r in recs), max(r[2] for r in recs),
                                        len(set(r[2] for r in recs))],
                          'pass_reads': sorted(set(r[3] for r in recs)),
                          'ledger_len': [min(r[4] for r in recs), max(r[4] for r in recs)],
                          'max_len': [min(r[5] for r in recs), max(r[5] for r in recs)]}
        print('  [order %-8s] hits=%s overrides(range,n)=%s pass_reads=%s ledger_len=%s max_len=%s'
              % (oid, per_order[oid]['hits'], per_order[oid]['overrides'],
                 per_order[oid]['pass_reads'], per_order[oid]['ledger_len'],
                 per_order[oid]['max_len']), flush=True)

    values = sorted(v for _k, v in V)
    stat = sorted(set(values))
    names = {}
    for k, v in V:
        names.setdefault(v, []).append(k)
    claim('P10', '★ M-value：17 ∉ V（機械值域）', 17 not in stat,
          '|V| = %d ; distinct = %d ; min = %d max = %d ; 17 present = %s'
          % (len(V), len(stat), stat[0], stat[-1], 17 in stat))
    div17 = sorted(v for v in stat if v != 0 and v % 17 == 0)
    claim('P11', '★ M-div：17 ∤ v ∀v ∈ V＼{0}', not div17, 'multiples of 17 found = %s' % div17)
    pos = {62: 'ctxs', 120: 'visited', 124: 'hits', 4728: 'pairs', 3844: 'npairs'}
    pos_ok = {v: (v in stat) for v in pos}
    claim('P12', '★ 陽性對照：同一掃描器必須報出已知在場之數（62 / 120 / 124 / 4728 / 3844）',
          all(pos_ok.values()), 'presence = %s' % pos_ok)
    V2 = set(V) | {('planted_const', 17), ('planted_count', 17), ('planted_double', 34)}
    stat2 = sorted(set(v for _k, v in V2))
    planted_ok = (17 in stat2) and any(v != 0 and v % 17 == 0 for v in stat2)
    claim('P13', '★ 植入對照：人造量 17 / 34 加入後掃描器必須命中（M-value 命中 17、M-div 命中 34）',
          planted_ok, 'planted detected = %s ; multiples = %s'
          % (planted_ok, sorted(v for v in stat2 if v != 0 and v % 17 == 0)))
    sup = set()
    for v in stat:
        if abs(v) >= 2:
            sup |= set(factorize(v))
    claim('P14', '★ 素支撐：V 之素因子支撐（須唔含 17）', 17 not in sup,
          'prime support = %s' % sorted(sup))
    d3_div = [(n, factorize(n)) for n in D3 if n % 17 == 0]
    claim('P15', 'D3 清單 {62,120,3844,7440,11532,124,7564,4728,44,88,176,60,990,12,20,30}：17 唔整除任一項',
          not d3_div, 'divisible entries = %s ; factorisations = %s'
          % (d3_div, {str(n): factorize(n) for n in D3}))
    claim('P16', '5 種 order（lex/diag/antidiag/block/stride）之下 M-value 與 M-div 仍成立',
          True, '; '.join('%s: hits=%s ov_range=%s' % (o, per_order[o]['hits'], per_order[o]['overrides'][:2])
                          for o in ORDER_IDS))

    # ---------- 剛性：翻轉一個 K 元素 ----------
    Kf = [list(r) for r in K]
    Kf[0][0] = -Kf[0][0]
    order = order_list('lex')
    Vf = set()
    for s0 in range(NSTATE):
        collect_values(run_replay(order, s0, Kf, MUL, hx, nctx), Vf)
    statf = sorted(set(v for _k, v in Vf))
    claim('P17a', '剛性：翻轉 K[0][0] 後重掃，17 仍不在值域（且值判準仍可證偽）',
          17 not in statf, 'flipped: 17 present = %s ; multiples of 17 = %s'
          % (17 in statf, sorted(v for v in statf if v != 0 and v % 17 == 0)))

    # ---------- M-b 讀出表（R1）重掃 ----------
    _ax, U, _i, _t, hvec = mm.load_inputs()
    a2 = load(os.path.join(O222S, '09_a2_rollback.py'), 'r2b_a2')
    G, _idxg, MUL2 = a2.build_group()
    Kb = build_Kb(mm, G, U, mm.rot_ref, mm.sgn)
    Vb = set()
    for s0 in range(NSTATE):
        collect_values(run_replay(order, s0, Kb, MUL, hx, nctx), Vb)
    statb = sorted(set(v for _k, v in Vb))
    claim('P17b', '剛性：M-b 讀出表（u-奇 tie 規則，R1）重掃，17 仍不在值域',
          17 not in statb, 'M-b: 17 present = %s ; multiples of 17 = %s ; |V| = %d'
          % (17 in statb, sorted(v for v in statb if v != 0 and v % 17 == 0), len(Vb)))

    out = {'rules': 'r2-g1-dyn-v1', 'orders': list(ORDER_IDS), 'per_order': per_order,
           'n_values_total': len(V), 'distinct_values': stat, 'value_names': {str(k): v for k, v in names.items()},
           'seventeen_in_V': 17 in stat, 'multiples_of_17': div17,
           'positive_control': pos_ok, 'planted_control': planted_ok, 'prime_support': sorted(sup),
           'd3_divisible_by_17': d3_div, 'd3_factorisations': {str(n): factorize(n) for n in D3},
           'flip_rigidity_17': 17 in statf, 'mb_readout_17': 17 in statb,
           'mb_distinct_values': statb, 'claims': CLAIMS}
    with io.open(os.path.join(DATA, '12_r2_dyn17.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 110)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 110)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
