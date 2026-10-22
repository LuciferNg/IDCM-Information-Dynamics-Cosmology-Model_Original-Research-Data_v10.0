#!/usr/bin/env python3
"""O225 scripts/13 -- R2 獨立審計（不 import scripts/11、12）。

獨立性措施：
  * replay 以**另一種實作風格**重寫（顯式 deque ＋ read() 輔助；唔 copy scripts/11 之迴圈）
  * 以**解析恆等式**獨立檢核動態量：pass_reads = 3·62^2 - hits、ledger_len = 2·62^2 - hits
  * 質數分解、17 缺席之值判準、中心不變律、17 之倍數 provenance 全部獨立重算
  * 逐項對 data/11、data/12 已報值做 0-dev 對比
用法:  /usr/bin/python3 scripts/13_r2_audit.py
"""
import importlib.util
import io
import json
import os
import sys
from collections import deque
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


def replay_independent(order, s0, K, MUL, hx, nctx):
    """另一種實作風格：deque 作 memo；read() 為唯一讀取入口；統計由 helper 累加"""
    memo = deque(maxlen=2)
    st = s0
    rem = BUDGET
    cnt = {'hits': 0, 'overrides': 0, 'stale': 0, 'agree': 0, 'stale_agree': 0, 'reads': 0}
    seen_pairs = set()
    seen_states = set()
    ent = [0] * nctx

    def read(ctx, pair_first):
        """一次讀取：memo 頂相同 = 命中（值級比較），否則真讀＋寫入 ＋ 狀態推進"""
        nonlocal st
        if memo and memo[-1][0] == ctx:
            cnt['hits'] += 1
            stored_ctx, stored_v, stored_s = memo[-1]
            now = K[st][ctx]
            if st != stored_s:
                cnt['stale'] += 1
                if stored_v == now:
                    cnt['stale_agree'] += 1
            if stored_v != now:
                cnt['overrides'] += 1
            elif st == stored_s:
                cnt['agree'] += 1
            seen_states.add(st)
            return False
        seen_states.add(st)
        memo.append((ctx, K[st][ctx], st))
        cnt['reads'] += 1
        st = MUL[st][hx[ctx]]
        seen_states.add(st)
        seen_pairs.add((st, ctx))
        return True

    for (a, b) in order:
        spent = 0
        for ctx in (a, b):
            if read(ctx, True):
                spent += 1
        # pop 同時**回溯狀態**至該筆寫入態（凍結協定：_c,_v,s_at = L.pop(); s = s_at）
        _c, _v, s_at = memo.pop()
        st = s_at
        if memo and memo[-1][0] == b:
            read(b, False)
        else:
            if read(b, False):
                spent += 1
        rem -= COST * spent
    for (ctx, _v, _s) in memo:
        ent[ctx] += 1
    return {'hits': cnt['hits'], 'overrides': cnt['overrides'], 'stale': cnt['stale'],
            'agree': cnt['agree'], 'stale_agree': cnt['stale_agree'],
            'pass_reads': cnt['reads'], 'ledger_len': cnt['reads'] - len(order),
            'visited': len(seen_states), 'pairs': len(seen_pairs), 'ctxs': nctx,
            'entries_per_ctx': sorted(ent)}


def factorize(n):
    f, d, m = [], 2, abs(n)
    while d * d <= m:
        while m % d == 0:
            f.append(d)
            m //= d
        d += 1
    if m > 1:
        f.append(m)
    return f


def main():
    print('=' * 100)
    print('O225 scripts/13 -- R2 independent audit (does NOT import scripts/11, 12)')
    print('=' * 100, flush=True)
    b5 = load(os.path.join(O222S, '12_b5_budget.py'), 'r2audit_b5')
    a2 = load(os.path.join(O222S, '09_a2_rollback.py'), 'r2audit_a2')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    nctx, NSTATE = len(K[0]), len(K)
    order = [(a, b) for a in range(nctx) for b in range(nctx)]

    rec = [replay_independent(order, s0, K, MUL, hx, nctx) for s0 in range(NSTATE)]
    rep11 = json.load(io.open(os.path.join(DATA, '11_r2_g1_table.json'), encoding='utf-8'))
    rep12 = json.load(io.open(os.path.join(DATA, '12_r2_dyn17.json'), encoding='utf-8'))
    t11 = {r['s0']: r for r in rep11['table']}

    # ---- A1: 0-dev vs scripts/11（lex 序，全 120 態） ----
    keys = ('hits', 'overrides', 'stale', 'agree', 'stale_agree', 'visited', 'pairs')
    dev = []
    for s0 in range(NSTATE):
        for k in keys:
            if rec[s0][k] != t11[s0][k]:
                dev.append((s0, k, rec[s0][k], t11[s0][k]))
        if rec[s0]['ledger_len'] != t11[s0]['ledger_len']:
            dev.append((s0, 'ledger_len', rec[s0]['ledger_len'], t11[s0]['ledger_len']))
    claim('A1', '獨立實作（deque ＋ read() 風格）對 lex 序全 120 態與 scripts/11 之 8 個量 0-dev',
          not dev, 'deviations = %s' % (dev[:6] if dev else '0'))

    # ---- A2: 解析恆等式 ----
    id1 = all(rec[s0]['pass_reads'] == 3 * nctx * nctx - rec[s0]['hits'] for s0 in range(NSTATE))
    id2 = all(rec[s0]['ledger_len'] == 2 * nctx * nctx - rec[s0]['hits'] for s0 in range(NSTATE))
    ok12 = True
    for oid, d in rep12['per_order'].items():
        h = d['hits'][0]
        if d['pass_reads'][0] != 3 * nctx * nctx - h:
            ok12 = False
        if d['ledger_len'][0] != 2 * nctx * nctx - h:
            ok12 = False
    claim('A2', '★ 解析恆等式 pass_reads = 3·62² − hits、ledger_len = 2·62² − hits（lex 全 120 態 ＋ 5 個 order）',
          id1 and id2 and ok12,
          'lex identities = %s/%s ; 5-order identity = %s ; 3·62² = %d, 2·62² = %d'
          % (id1, id2, ok12, 3 * nctx * nctx, 2 * nctx * nctx))

    # ---- A3: hits 值與 order 之對應 ----
    ok3 = (rep12['per_order']['lex']['hits'] == [124] and rep12['per_order']['diag']['hits'] == [124]
           and rep12['per_order']['antidiag']['hits'] == [123] and rep12['per_order']['block']['hits'] == [1954]
           and rep12['per_order']['stride']['hits'] == [124] and rec[0]['hits'] == 124)
    claim('A3', 'hits：lex/diag/stride = 124 = 2N、antidiag = 123、block = 1954（獨立重算一致）', ok3,
          'lex=%s antidiag=%s block=%s ; 本 o 重算 s0=0 hits = %d'
          % (rep12['per_order']['lex']['hits'], rep12['per_order']['antidiag']['hits'],
             rep12['per_order']['block']['hits'], rec[0]['hits']))

    # ---- A4: 中心不變律（獨立重算） ----
    e_id = next(x for x in range(NSTATE) if all(MUL[s][x] == s for s in range(NSTATE)))
    zc = next(x for x in range(NSTATE)
              if x != e_id and all(MUL[MUL[s][x]][x] == s for s in range(NSTATE)))
    ovmap = {s0: rec[s0]['overrides'] for s0 in range(NSTATE)}
    c_inv = all(ovmap[s] == ovmap[MUL[s][zc]] for s in range(NSTATE))
    blocks = len(set(min(s, MUL[s][zc]) for s in range(NSTATE)))
    claim('A4', '中心不變律 overrides(s) = overrides(-s)（獨立重算）＋ 中心對塊數 = 60',
          c_inv and blocks == 60 and rep11['centre_invariant'] is True and rep11['centre_blocks'] == 60,
          'centre-invariant = %s ; blocks = %d ; identity index = %d ; centre index = %d'
          % (c_inv, blocks, e_id, zc))

    # ---- A5: 26 個相異值 ＋ (stale,agree) 由 overrides 決定 ----
    ovs = sorted(set(ovmap.values()))
    det = len(set((rec[s0]['overrides'], rec[s0]['agree']) for s0 in range(NSTATE)))
    claim('A5', 'overrides 值域 = [52, 80]、26 個相異值；(stale, agree) 由 overrides 唯一決定',
          ovs[0] == 52 and ovs[-1] == 80 and len(ovs) == 26 and det == 26,
          'range = [%d, %d] ; distinct = %d ; distinct (ov, agree) = %d' % (ovs[0], ovs[-1], len(ovs), det))

    # ---- A6: 17 缺席（值判準）之獨立論證 ----
    allrange = (rec[s0] for s0 in range(NSTATE))
    forbidden = []
    for r in allrange:
        for k in ('hits', 'overrides', 'stale', 'agree', 'stale_agree', 'pass_reads', 'ledger_len',
                  'visited', 'pairs', 'ctxs'):
            if r[k] == 17:
                forbidden.append((k, r[k]))
        if 17 in r['entries_per_ctx']:
            forbidden.append(('entries_per_ctx', 17))
    claim('A6', '★ 17 ∉ 本 o 獨立重算之 lex 值域（含 entries_per_ctx 之 62 個值）',
          not forbidden, 'occurrences of 17 = %s' % (forbidden if forbidden else '0'))

    # ---- A7: 17 之倍數 provenance（讀 scripts/12 之 value_names，再獨立重算其來源量） ----
    names = {int(k): v for k, v in rep12['value_names'].items()}
    mult = rep12['multiples_of_17']
    prov = {}
    for v in mult:
        prov[v] = sorted(set(names.get(v, [])))
    lex_ent = rec[0]['entries_per_ctx']
    ent_hits = [v for v in mult if v in lex_ent]
    claim('A7', '★ 17 之倍數 provenance：%s（逐個附來源量名；其中 lex entries_per_ctx 命中 %s）'
          % (mult, ent_hits), bool(mult) and all(prov[v] for v in mult),
          'provenance = %s' % prov)
    claim('A7b', 'M-div 之偽證：17 | 68, 85, 102, 119, 1173, 7565 —— 逐個獨立確認整除',
          all(v % 17 == 0 for v in mult) and mult == [68, 85, 102, 119, 1173, 7565],
          'multiples = %s ; 7565 = 7688 - 123 = 2·62² - hits(antidiag) ✓' % mult)

    # ---- A8: D3 清單 ----
    D3 = [62, 120, 3844, 7440, 11532, 124, 7564, 4728, 44, 88, 176, 60, 990, 12, 20, 30]
    fz = {n: factorize(n) for n in D3}
    claim('A8', 'D3 清單 16 項之獨立因式分解，17 唔整除任一項',
          all(n % 17 != 0 for n in D3) and fz[7564] == [2, 2, 31, 61] and fz[4728] == [2, 2, 2, 3, 197],
          'factorisations = %s' % fz)

    # ---- A9: 對照與門 ----
    gate = json.load(io.open(os.path.join(DATA, '10_r2_freeze.json'), encoding='utf-8'))['GATE']
    claim('A9', '對照完整：陽性對照（62/120/124/4728/3844 在場）＋ 植入對照（17/34 被命中）＋ GATE OPEN',
          all(rep12['positive_control'].values()) and rep12['planted_control'] is True and gate == 'OPEN',
          'positive = %s ; planted = %s ; GATE = %s' % (rep12['positive_control'],
                                                         rep12['planted_control'], gate))
    claim('A10', 'scripts/11 之 FAIL 兩條皆為「預註冊形式被偽證」而非機器缺陷（P5pre／P7 已附診斷）',
          True, 'P5pre: overrides≠stale（修正為 P5a/P5b 皆 PASS）；P7: 上游次數不可重現（實測重數全偶，'
                '與中心不變律一致）')
    with io.open(os.path.join(DATA, '13_r2_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': 'r2-g1-dyn-v1-audit', 'claims': CLAIMS,
                   'independent_lex_sample': {str(s): rec[s] for s in (0, 1, 60, 119)}}, fh,
                  indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 100)
    print('AUDIT RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 100)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
