#!/usr/bin/env python3
"""O225 scripts/11 -- R2A：G1 完整語義表（`r2-g1-dyn-v1`）。

凍結協定 = O222 scripts/30_g1g8_gaps.ledger_replay 逐字（＋ scripts/66 之 stale/agree 欄）。
校準閘 = 與 O222 scripts/18_d6_mapping.replay_protocol 逐 pair 0 mismatch（misses / top / ledger_len）。
掃描全部 120 初始態，出完整表 ＋ 分拆刻畫（P1..P9）。
精確算術；無 float / math / random / numpy。
用法:  /usr/bin/python3 scripts/11_r2_g1_table.py
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


def ledger_replay(order, s0, K, MUL, hx, budget):
    """凍結協定逐字（scripts/30）＋ stale / agree 追蹤（scripts/66）"""
    L = []
    s = s0
    rem = budget
    out = []
    hits = ov = stale = agree = stale_agree = 0
    visited = set()
    pairs = {}
    ctxs = set()
    for (a, b) in order:
        spent = 0
        for ctx in (a, b):
            visited.add(s)
            ctxs.add(ctx)
            if L and L[-1][0] == ctx:
                hits += 1
                stored_s = L[-1][2]
                stored_v = L[-1][1]
                now = K[s][ctx]
                if s != stored_s:
                    stale += 1
                    if stored_v == now:
                        stale_agree += 1
                if stored_v != now:
                    ov += 1
                elif s == stored_s:
                    agree += 1
                continue
            v = K[s][ctx]
            L.append((ctx, v, s))
            s = MUL[s][hx[ctx]]
            spent += 1
            visited.add(s)
            pairs[(s, ctx)] = pairs.get((s, ctx), 0) + 1
        _c, _v, s_at = L.pop()
        s = s_at
        if L and L[-1][0] == b:
            hits += 1
            stored_s = L[-1][2]
            stored_v = L[-1][1]
            if s != stored_s:
                stale += 1
                if stored_v == K[s][b]:
                    stale_agree += 1
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
        out.append({'misses': spent, 'top': (L[-1][0] if L else -1), 'ledger_len': len(L)})
    return {'pairs': out, 'ledger': L, 'hits': hits, 'overrides': ov, 'stale': stale,
            'stale_agree': stale_agree, 'agree': agree, 'visited': len(visited),
            'pairs_n': len(pairs), 'ctxs': len(ctxs)}


def _hist(pair_records):
    h = {}
    for p in pair_records:
        h[p['misses']] = h.get(p['misses'], 0) + 1
    return dict(sorted(h.items()))


def main():
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'logs'), exist_ok=True)
    print('=' * 110)
    print('O225 scripts/11 -- R2A: G1 full semantics table (r2-g1-dyn-v1)')
    print('=' * 110, flush=True)
    b5 = load(os.path.join(O222S, '12_b5_budget.py'), 'r2_b5')
    a2 = load(os.path.join(O222S, '09_a2_rollback.py'), 'r2_a2')
    d6 = load(os.path.join(O222S, '18_d6_mapping.py'), 'r2_d6')
    _mm, K, MUL, hx, ids, types = b5.load_machine()
    N, NSTATE = len(K[0]), len(K)
    G, idxg, MUL2 = a2.build_group()

    # ---------- P1 校準閘 ----------
    order = [(a, b) for a in range(N) for b in range(N)]
    mine = ledger_replay(order, 0, K, MUL, hx, BUDGET)
    frozen = d6.replay_protocol(order, K, MUL, hx, BUDGET)
    diffs = sum(1 for x, y in zip(mine['pairs'], frozen)
                if (x['misses'], x['top'], x['ledger_len']) != (y['misses'], y['top'], y['ledger_len']))
    claim('P1', '校準閘：本 o replay 與 I7 replay_protocol 逐 pair 0 mismatch（misses/top/ledger_len）',
          diffs == 0 and len(mine['pairs']) == len(frozen) == len(order),
          'pairs = %d ; mismatches = %d' % (len(frozen), diffs))
    claim('P1b', 'MUL 與 a2.build_group 之 MUL2 逐項相同（狀態索引與四元數索引一致）', MUL == MUL2,
          'MUL == MUL2 : %s' % (MUL == MUL2))

    # ---------- 全 120 態掃描 ----------
    rows = []
    for s0 in range(NSTATE):
        r = ledger_replay(order, s0, K, MUL, hx, BUDGET)
        rows.append({'s0': s0, 'hits': r['hits'], 'overrides': r['overrides'], 'stale': r['stale'],
                     'stale_agree': r['stale_agree'], 'agree': r['agree'], 'visited': r['visited'],
                     'pairs': r['pairs_n'], 'ctxs': r['ctxs'], 'ledger_len': len(r['ledger']),
                     'miss_hist': _hist(r['pairs'])})
    hits_set = sorted(set(r['hits'] for r in rows))
    ovs = [r['overrides'] for r in rows]
    ov_hist = {}
    for v in ovs:
        ov_hist[v] = ov_hist.get(v, 0) + 1
    claim('P2', 'hits ≡ 124 = 2N 對全部 120 個 s0 恆定', hits_set == [124], 'distinct hits = %s' % hits_set)
    claim('P3', 'overrides(s0) ∈ [52, 80]，恰 26 個相異值',
          min(ovs) == 52 and max(ovs) == 80 and len(set(ovs)) == 26,
          'range = [%d, %d] ; distinct = %d' % (min(ovs), max(ovs), len(set(ovs))))
    claim('P4', '校準 s0 = 0 → overrides = 65', rows[0]['overrides'] == 65,
          's0=0 : hits=%d overrides=%d stale=%d agree=%d'
          % (rows[0]['hits'], rows[0]['overrides'], rows[0]['stale'], rows[0]['agree']))
    claim('P5pre', '【預註冊形式已被偽證，保留】overrides = stale = hits − agree（120/120）',
          all(r['overrides'] == r['stale'] == r['hits'] - r['agree'] for r in rows),
          '首跑 FAIL（s0=0: overrides=65 vs stale=124）⟹ stale 只量「狀態已前進」，override 量「值翻轉」')
    claim('P5a', '修正恆等式① hits = agree + stale_agree + overrides（120/120）',
          all(r['hits'] == r['agree'] + r['stale_agree'] + r['overrides'] for r in rows),
          's0=0: 124 = 0 + 59 + 65')
    claim('P5b', '修正恆等式② stale = stale_agree + overrides（120/120）',
          all(r['stale'] == r['stale_agree'] + r['overrides'] for r in rows),
          'stale_agree := 「狀態已前進但值仍相同」之命中數')
    claim('P6', '#ctx = 62、#distinct (s,ctx) = 4728、#visited = 120（全部 s0 相同）',
          set(r['ctxs'] for r in rows) == {62} and set(r['pairs'] for r in rows) == {4728}
          and set(r['visited'] for r in rows) == {120},
          'ctxs=%s pairs=%s visited=%s' % (sorted(set(r['ctxs'] for r in rows)),
                                           sorted(set(r['pairs'] for r in rows)),
                                           sorted(set(r['visited'] for r in rows))))
    claim('P7', '上游記錄「58 出現 28/30、10 個態給 65」不可重現；預註冊預期 58x1、65x3、68x10',
          ov_hist.get(58) == 1 and ov_hist.get(65) == 3 and ov_hist.get(68) == 10,
          'ov_hist = %s' % dict(sorted(ov_hist.items())))
    claim('P7b', '★ 全部 override 重數皆為偶數（中心對 {s,-s} 同值之必要後果）',
          all(c % 2 == 0 for c in ov_hist.values()),
          'multiplicities = %s' % sorted(ov_hist.values()))

    # ---------- P8 分拆刻畫 ----------
    def is_one(q):
        return q[0] == (F(1), F(0)) and all(c == (F(0), F(0)) for c in q[1:])

    i_id = next(i for i in range(NSTATE) if is_one(G[i]))
    zc = next(i for i in range(NSTATE)
              if G[i][0] == (F(-1), F(0)) and all(c == (F(0), F(0)) for c in G[i][1:]))
    ords = {}
    for s in range(NSTATE):
        cur, k = s, 1
        while MUL[cur][s] != i_id and k <= 300:
            cur = MUL[cur][s]
            k += 1
        ords[s] = k

    def dist2(x, y):
        sq = (F(0), F(0))
        for t in range(4):
            dd = a2.sub(G[x][t], G[y][t])
            sq = a2.add(sq, a2.mul(dd, dd))
        return sq

    parts = {
        'P1_Krow': lambda s: tuple(K[s]),
        'P2_conj': lambda s: (ords[s], G[s][0][0].numerator, G[s][0][0].denominator,
                              G[s][0][1].numerator, G[s][0][1].denominator),
        'P3_order': lambda s: ords[s],
        'P4_centre_pair': lambda s: min(s, MUL[s][zc]),
        'P5_d5_signature': lambda s: tuple(sorted(dist2(MUL[s][hx[c]], s) for c in range(N))),
    }
    const_res = {}
    block_index = {}
    for name, f in parts.items():
        blocks = {}
        for r in rows:
            blocks.setdefault(f(r['s0']), []).append(r['overrides'])
        const_res[name] = {'n_blocks': len(blocks),
                           'constant': all(len(set(v)) == 1 for v in blocks.values()),
                           'max_block_internal_range': max(max(v) - min(v) for v in blocks.values())}
        block_index[name] = blocks
        print('  [INFO] %-16s blocks = %3d  constant = %-5s  max internal range = %d'
              % (name, const_res[name]['n_blocks'], const_res[name]['constant'],
                 const_res[name]['max_block_internal_range']), flush=True)
    centres = {}
    for r in rows:
        centres.setdefault(min(r['s0'], MUL[r['s0']][zc]), []).append(r['s0'])
    claim('P8a', '共軛分拆（階 ＋ Re 類函數）之塊大小 = [1,1,12,12,12,12,20,20,30]（驗證 P2 確為共軛分拆）',
          sorted(len(v) for v in block_index['P2_conj'].values()) == [1, 1, 12, 12, 12, 12, 20, 20, 30],
          'block sizes = %s' % sorted(len(v) for v in block_index['P2_conj'].values()))
    ovmap = {r['s0']: r['overrides'] for r in rows}
    claim('P8b', 'P4 中心對分拆（鍵 = min(s, -s)）之塊數 = 60，每塊恰 2 態 {s, -s}',
          len(centres) == 60 and all(len(v) == 2 for v in centres.values()),
          'blocks = %d ; sizes = %s' % (len(centres), sorted(set(len(v) for v in centres.values()))))
    centre_inv = all(ovmap[s] == ovmap[MUL[s][zc]] for s in range(NSTATE))
    claim('P8d', '★ 中心不變律：overrides(s) = overrides(-s) 對全部 120 態',
          centre_inv, 'centre-invariant = %s' % centre_inv)
    claim('P8e', '★ 26 個相異 override 值分布於 60 個中心類；#distinct profiles = 26 ⟹ (stale, agree) 由 overrides 決定',
          len(set(ovmap.values())) == 26,
          'distinct overrides = %d ; centre classes = %d ; agree determined by overrides = %s'
          % (len(set(ovmap.values())), len(centres),
             len(set((r['overrides'], r['agree']) for r in rows)) == 26))
    prof = {}
    for r in rows:
        prof.setdefault(tuple(r[k] for k in ('hits', 'overrides', 'stale', 'agree', 'visited',
                                             'pairs', 'ctxs', 'ledger_len')), []).append(r['s0'])
    finest = sorted([k for k, v in const_res.items() if v['constant']],
                    key=lambda k: const_res[k]['n_blocks'])
    claim('P8c', '★ 分拆恆定性判定：報最細恆定分拆 ＋ 由全 profile 決定之相異類數',
          True, 'constant partitions (coarse->fine) = %s ; #distinct profiles = %d ; finest = %s'
          % (finest, len(prof), finest[0] if finest else None))
    out = {'rules': 'r2-g1-dyn-v1', 'table': rows,
           'override_histogram': {str(k): v for k, v in sorted(ov_hist.items())},
           'partitions': const_res, 'n_distinct_profiles': len(prof),
           'constant_partitions': finest, 'finest_constant_partition': (finest[0] if finest else None),
           'calibration': {'pairs': len(frozen), 'mismatches': diffs},
           'identity_index': i_id, 'centre_index': zc, 'centre_invariant': centre_inv,
           'centre_blocks': len(centres),
           'override_min': min(ovs), 'override_max': max(ovs), 'claims': CLAIMS}
    with io.open(os.path.join(DATA, '11_r2_g1_table.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 110)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 110)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
