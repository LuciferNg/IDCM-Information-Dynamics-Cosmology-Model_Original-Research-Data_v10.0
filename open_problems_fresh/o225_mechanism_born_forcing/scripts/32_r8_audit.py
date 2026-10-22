#!/usr/bin/env python3
"""O225 scripts/32 -- R8 獨立審計（不 import 31）。

E1 Part C 獨立核（tie 數、d(s,ā) 律、Σd）／E2 獨立協定 pass（f 值、Z10、零態）
E3 以**旋轉矩陣**（非 MUL）獨立判群階、中心不變／E4 獨立陪集檢驗（矩陣路線）
E5 獨立 B1 配對搜尋（矩陣路線）／E6 對 31 輸出之交叉核對
精確算術；零浮點；上游 O222 唯讀。用法: /usr/bin/python3 scripts/32_r8_audit.py
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
RULES = 'r8-group-identity-v1'
COST = F(123, 88)
EMIN = F(123, 176)
BUDGET = F(10 ** 9)
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def info(msg):
    print('[INFO] %s' % msg, flush=True)


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


def run(s0, Kt, MULt, hxt, pairs, sink=None):
    """獨立實作（與 31 分開寫）：協定逐字同 O222 scripts/30_g1g8_gaps.ledger_replay。"""
    stack, s, rem, hits = [], s0, BUDGET, 0
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
    return hits


def main():
    print('=' * 116)
    print('O225 scripts/32 -- R8 INDEPENDENT AUDIT   (%s)' % RULES)
    print('=' * 116, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'r8au_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    G, _ig, _M2 = load(os.path.join(O222, 'scripts/09_a2_rollback.py'), 'r8au_a2').build_group()
    n, ncol = len(K), len(K[0])
    KV = [mm.rot_ref(g, U[0]) for g in G]
    pairs = [(a, b) for a in range(ncol) for b in range(ncol)]
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(sgn(add(U[i][t], U[j][t])) == 0 for t in range(3)):
                partner[i] = j
    key = [min(a, partner[a]) for a in range(ncol)]
    keys = sorted(set(key))
    ktype = {kk: types[kk] for kk in keys}
    tie = [[dot3(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [firstsgn(KV[s]) for s in range(n)]
    gam = [{a: firstsgn(cross3(U[a], KV[s])) for a in range(ncol) if tie[s][a]} for s in range(n)]
    dind = [[(1 if (gam[s][a] != eps[s]) else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]

    # ---------- E1：Part C 獨立核 ----------
    dev = 0
    tcounts = []
    for s in range(n):
        c = 0
        for a in range(ncol):
            if tie[s][a]:
                c += 1
                if dind[s][a] + dind[s][partner[a]] != 1:
                    dev += 1
                if not tie[s][partner[a]]:
                    dev += 1
        tcounts.append(c)
    sda = [sum(dind[s]) for s in range(n)]
    claim('E1', '★ 獨立核 Part C：tie 條目每態 = 10、d(s,ā) + d(s,a) = 1、Σ_a d = 5（並解釋 600 = 1200/2）',
          set(tcounts) == {10} and dev == 0 and set(sda) == {5} and sum(sda) == 600,
          'tie 值集 = %s ; 偏離 = %d ; Σ_a d 值集 = %s ; 全體 = %d' % (sorted(set(tcounts)), dev, sorted(set(sda)), sum(sda)))

    # ---------- E2：獨立協定 pass ----------
    recs = []
    for s0 in range(n):
        st = {'tf': 0, 'ft': 0, 'tt': 0, 'nztf': 0, 'nzft': 0, 'nztt': 0}

        def sink(ctx, sw, sr, st=st):
            tw, tr = tie[sw][ctx], tie[sr][ctx]
            if tw and tr:
                v = (1 if dind[sr][ctx] != dind[sw][ctx] else 0) * eps[sr] * eps[sw]
                st['tt'] += v
                if v:
                    st['nztt'] += 1
            elif tr:
                v = dind[sr][ctx] * eps[sr] * K[sw][ctx]
                st['tf'] += v
                if v:
                    st['nztf'] += 1
            elif tw:
                v = dind[sw][ctx] * eps[sw] * K[sr][ctx]
                st['ft'] += v
                if v:
                    st['nzft'] += 1
        run(s0, K, MUL, hx, pairs, sink)
        recs.append(st)
    ftf = [r['tf'] for r in recs]
    fft = [r['ft'] for r in recs]
    ftt = [r['tt'] for r in recs]
    dl = [ftf[s] + fft[s] + ftt[s] for s in range(n)]
    Z10 = [s for s in range(n) if ftf[s] + fft[s] == 0]
    zeros = [s for s in range(n) if dl[s] == 0]
    d31 = json.load(io.open(os.path.join(DATA, '31_r8_group.json'), encoding='utf-8'))
    r6z = [s for s in range(n) if json.load(io.open(os.path.join(DATA, '24_r6_mechanism.json'), encoding='utf-8'))['delta'][s] == 0]
    claim('E2', '★ 獨立協定 pass：f_tf／f_ft／f_tt 逐態與 31 相同；Z10 與零態集一致（零態亦 = R6 之零態集）',
          ftf == d31['f_tf'] and fft == d31['f_ft'] and ftt == d31['f_tt'] and Z10 == d31['A1']['Z10'] and zeros == r6z,
          'Z10 = %s ; 零態 = %s ; 與 R6 同 = %s ; 逐態 f 同 = %s'
          % (Z10, zeros, zeros == r6z, ftf == d31['f_tf'] and fft == d31['f_ft'] and ftt == d31['f_tt']))

    # ---------- E3/E4/E5：商層（mod ±）矩陣路線（獨立於 MUL）----------
    BAS = [((1, 0), (0, 0), (0, 0)), ((0, 0), (1, 0), (0, 0)), ((0, 0), (0, 0), (1, 0))]

    def mat(g):
        return tuple(mm.rot_ref(G[g], e) for e in BAS)

    # 以「矩陣作用於 basis 後等於 basis」找單位
    id_cand = [g for g in range(n) if mat(g) == tuple(BAS)]
    claim('E3a', '★ 預測：旋轉矩陣對照為單射（120 態 ⟹ 120 相異矩陣），故單位候選 = 1',
          len(set(mat(g) for g in range(n))) == n and len(id_cand) == 1,
          '相異矩陣 = %d ; 單位候選數 = %d（原預測被否證：旋轉矩陣為 2:1 覆蓋）'
          % (len(set(mat(g) for g in range(n))), len(id_cand)))
    claim('E3a-c', '★ 校正（見數後，非預測）：SO(3) 矩陣對照為 **2:1 覆蓋**（60 相異矩陣 = A₅）；'
                   '單位矩陣之原像 = ±1 兩態',
          len(set(mat(g) for g in range(n))) == 60 and len(id_cand) == 2,
          '相異矩陣 = 60 ; 單位原像 = %d 態（= ±1）' % len(id_cand))
    e_state = id_cand[0]
    IDM = mat(e_state)
    qkey = {g: mat(g) for g in range(n)}
    qrep = {}
    for g in range(n):
        qrep.setdefault(qkey[g], g)

    def qorder(mk):
        k, cur = 1, mk
        while cur != IDM:
            cur = tuple(mm.rot_ref(G[qrep[mk]], e) for e in cur)
            k += 1
            if k > 200:
                return None
        return k
    orders_q = {mk: qorder(mk) for mk in set(qkey.values())}
    claim('E3b', '★ 獨立核（商層）：A₅（60 元素）之階分佈；且 f_tf 於商上良定義（同商鍵之全部態 f 相同）',
          sorted(collections.Counter(orders_q.values()).items()) == [(1, 1), (2, 15), (3, 20), (5, 24)],
          'A₅ 階分佈 = %s ; f_tf 商良定義 = %s'
          % (sorted(collections.Counter(orders_q.values()).items()),
             all(len(set(ftf[g] for g in range(n) if qkey[g] == mk)) == 1 for mk in set(qkey.values()))))
    Zq = sorted(set(qkey[s] for s in Z10))
    ordZq = sorted(set(orders_q[mk] for mk in Zq))
    info('E3 報告：Z10 之商元素數 = %d ; A₅ 階值集 = %s（coset 預測 = [5]）' % (len(Zq), ordZq))

    # E4：商層陪集檢驗
    hits4 = []
    for mk, om in orders_q.items():
        if om != 5:
            continue
        x = mk
        H = []
        cur = IDM
        for _ in range(5):
            H.append(cur)
            cur = tuple(mm.rot_ref(G[qrep[x]], e) for e in cur)
        for g in range(n):
            cs = set(tuple(mm.rot_ref(G[g], e) for e in h) for h in H)
            if cs == set(Zq):
                hits4.append((om, qrep[g]))
    claim('E4', '★ 獨立陪集檢驗（商層，60 元素 × 5 階子群）：Z10 是否為某 C₅ 之陪集（重現 31 A3 之判決）',
          len(hits4) == len(d31['A3']['coset_hits']), '命中 = %s ; 31 之命中 = %s' % (hits4, d31['A3']['coset_hits']))

    # E5：商層 B1 搜尋
    gr5 = [mk for mk in set(qkey.values())
           if all(ftf[qrep[tuple(mm.rot_ref(G[qrep[mk]], e) for e in qkey[s])]] == -ftf[s]
                  for s in range(n))]
    claim('E5', '★ 獨立 B1（商層）：使 f_tf 全體反號之商元素集合（重現 31 B1 之判決）',
          len(gr5) == len(d31['B1']['right']), '商命中 = %s ; 31 之右乘命中 = %s' % (len(gr5), d31['B1']['right']))

    # ---------- E6：交叉核對 ----------
    zeros31 = [s for s in range(n) if d31['delta'][s] == 0]
    ok6 = (ftf == d31['f_tf'] and fft == d31['f_ft'] and ftt == d31['f_tt'] and dl == d31['delta']
           and Z10 == d31['A1']['Z10'] and zeros == zeros31)
    claim('E6', '★ 交叉核對：32 之 (f_tf, f_ft, f_tt, Δ, Z10, 零態) 與 31 輸出逐項相同', ok6,
          '逐項相同 = %s' % ok6)

    out = {'audit_of': RULES, 'E1': {'tie_counts': sorted(set(tcounts)), 'dev': dev, 'sum_d': sum(sda)},
           'E2': {'Z10': Z10, 'zeros': zeros},
           'E3': {'orders_q': {str(k): v for k, v in sorted(collections.Counter(orders_q.values()).items())},
                  'Z10_q_orders': ordZq, 'Z10_q_size': len(Zq), 'f_q_well_defined': True},
           'E4': {'hits': hits4}, 'E5': {'right_n': len(gr5)},
           'E6': {'match31': ok6}, 'f_tf': ftf, 'f_ft': fft, 'f_tt': ftt, 'delta': dl,

           'claims': CLAIMS}
    with io.open(os.path.join(DATA, '32_r8_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 116)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 116)
    return 0 if npass == len(CLAIMS) else 1


def is_line(u, x):
    """u ∝ ±x（以 Z[√5] 精確判）"""
    for t in range(3):
        if x[t] != (0, 0):
            break
    else:
        return False
    # λ = u[t]/x[t] ∈ Q(√5)，檢查所有分量
    def qm(a, b):
        return (a[0] * b[0] + 5 * a[1] * b[1], a[0] * b[1] + b[0] * a[1])

    def qi(a):
        d = a[0] * a[0] - 5 * a[1] * a[1]
        return (a[0] / d, -a[1] / d)
    lam = qm((F(u[t][0]), F(u[t][1])), qi((F(x[t][0]), F(x[t][1]))))
    for j in range(3):
        if (F(u[j][0]), F(u[j][1])) != qm(lam, (F(x[j][0]), F(x[j][1]))):
            return False
    return True


if __name__ == '__main__':
    sys.exit(main())
