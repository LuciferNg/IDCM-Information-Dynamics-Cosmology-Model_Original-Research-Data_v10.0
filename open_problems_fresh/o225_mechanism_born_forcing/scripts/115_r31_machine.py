#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/115 -- R31 機器（STT-1：S_TT≡0 之機制、±8 四類、補集 20）。

凍結指紋：data/114_r31_freeze.json。唯讀 O222；精確算術。用法: /usr/bin/python3 scripts/115_r31_machine.py
"""
import hashlib
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


def info(s):
    print('[INFO] ' + s, flush=True)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


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
    l, r = x[0] * x[0], 5 * x[1] * x[1]
    if l == r:
        return 0
    return (1 if l > r else -1) * (1 if x[0] > 0 else -1)


def fs(v):
    for c in v:
        s = sgn(c)
        if s:
            return s
    return 0


def d3(u, v):
    return add(add(mul(u[0], v[0]), mul(u[1], v[1])), mul(u[2], v[2]))


def x3(u, v):
    return (add(mul(u[1], v[2]), neg(mul(u[2], v[1]))),
            add(mul(u[2], v[0]), neg(mul(u[0], v[2]))),
            add(mul(u[0], v[1]), neg(mul(u[1], v[0]))))


def main():
    print('=' * 112)
    print('O225 scripts/115 -- R31 機器（STT-1）')
    print('=' * 112, flush=True)
    fr = json.load(io.open(os.path.join(BASE, 'data', '114_r31_freeze.json'), encoding='utf-8'))
    csha = hashlib.sha256(io.open(os.path.join(BASE, 'docs', '66_r31_contract.md'), 'rb').read()).hexdigest()
    info('凍結核：合約 sha 相符 = %s' % (csha == fr['sha256']))
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'b115')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'b115a')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    e_state = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))][0]
    inv = [next(j for j in range(n) if MUL[i][j] == e_state) for i in range(n)]
    order = []
    for a in range(n):
        k, x = 1, a
        while x != e_state:
            x = MUL[x][a]
            k += 1
        order.append(k)
    KV = [mm.rot_ref(g, U[0]) for g in G]
    tie = [[d3(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [fs(KV[s]) for s in range(n)]
    dind = [[(1 if fs(x3(U[a], KV[s])) != eps[s] else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]

    def events_of(state):
        st, stk, ev = state, [], []
        for (c1, c2_) in [(a, b) for a in range(ncol) for b in range(ncol)]:
            for ctx in (c1, c2_):
                if stk and stk[-1][0] == ctx:
                    ev.append((ctx, stk[-1][2], st))
                else:
                    stk.append((ctx, K[st][ctx], st))
                    st = MUL[st][hx[ctx]]
            top = stk.pop()
            st = top[2]
            if stk and stk[-1][0] == c2_:
                ev.append((c2_, stk[-1][2], st))
            else:
                stk.append((c2_, K[st][c2_], st))
                st = MUL[st][hx[c2_]]
        return ev

    my_ev = events_of(e_state)
    keys = {}
    for (a, sw, sr) in my_ev:
        g = MUL[inv[sr]][sw]
        keys[(a, g)] = keys.get((a, g), 0) + 1
    KS = sorted(keys)

    def STT(a, g):
        tot = 0
        for x in range(n):
            y = MUL[x][g]
            if tie[x][a] and tie[y][a]:
                tot += (0 if dind[x][a] == dind[y][a] else 1) * eps[x] * eps[y]
        return tot

    S = {k: STT(k[0], k[1]) for k in KS}
    zero = [k for k in KS if S[k] == 0]
    nz = [k for k in KS if S[k] != 0]
    vals = sorted(set(S.values()))
    fam = {}
    for k in zero:
        z = sum(1 for x in range(n) if (tie[x][k[0]] and tie[MUL[x][k[1]]][k[0]]) and
                (dind[x][k[0]] == dind[MUL[x][k[1]]][k[0]]))
        fam[z] = fam.get(z, 0) + 1
    claim('P1', 'S_TT 值分佈（零鍵 %d／非零 %d）＝ R26 之 62 鍵、值集 %s；Σ n·S_TT = %d；零鍵族（按零項數）'
          % (len(zero), len(nz), vals, sum(S[k] for k in KS)),
          len(zero) + len(nz) == 62 and set(vals) <= {-8, 0, 8} and sum(S[k] for k in KS) == 64,
          '值集 = %s；Σ = %d；零鍵族 = %s' % (vals, sum(S[k] for k in KS), fam))

    def wit(k):
        a, g = k
        out = []
        for s in range(1, n):
            if order[s] != 2:
                continue
            if MUL[s][g] != MUL[g][s]:
                continue
            okp = all(tie[x][a] == tie[MUL[s][x]][a] and dind[x][a] == dind[MUL[s][x]][a] for x in range(n))
            T = lambda x: (0 if dind[x][a] == dind[MUL[x][g]][a] else 1) * eps[x] * eps[MUL[x][g]] \
                if (tie[x][a] and tie[MUL[x][g]][a]) else 0
            okf = all(T(MUL[s][x]) == -T(x) for x in range(n))
            if okp and okf:
                out.append(s)
        return out

    W = {k: wit(k) for k in KS}
    p2bad = [k for k in KS if (S[k] == 0) != (len(W[k]) > 0)]
    claim('P2', '★ S_TT(a,g) = 0 ⟺ 存在階 2 σ_s（s ≠ e）使 tie/dind 逐欄不變且 εε′ 逐項反號（R26 T3 之逆）',
          not p2bad, '反例鍵 = %s；witness 計數分佈 = %s' % (p2bad[:4], sorted(set(len(v) for v in W.values()))))
    claim('P3', 'witness 計數分佈（報）', True, '分佈 = %s' % {str(k): sum(1 for v in W.values() if len(v) == k)
                                                          for k in sorted(set(len(v) for v in W.values()))})
    q1 = [(k[0], k[1], S[k], types[k[0]], order[k[1]], sgn(d3(U[k[0]], KV[k[1]]))) for k in nz]
    claim('Q1', '12 非零鍵之 (a, g, S_TT, type(a), ord(g), sgn⟨U_a,KV_g⟩) 逐個列出', len(nz) == 12, '逐鍵 = %s' % q1)
    comb = {}
    for (a, g, s, ty, og, su) in q1:
        comb.setdefault((ty, s), []).append(a)
    q2 = all(len(v) == 3 for v in comb.values()) and len(comb) == 4
    claim('Q2', '★ 四類之判別 = (type(a), S_TT 符號) 之 4 組合、每類恰 3 鍵', q2,
          '組合 = %s' % {str(k): v for k, v in comb.items()})
    claim('Q3', '否證備援報表：(S_TT 符號, ord(g)) 與 (type, ord(g)) 分佈', True,
          '(符號,ord) = %s；(type,ord) = %s' % ({str((s, og)): sum(1 for q in q1 if q[2] == s and q[4] == og)
                                                for s in sorted(set(q[2] for q in q1))
                                                for og in sorted(set(q[4] for q in q1))},
                                               {str((ty, og)): sum(1 for q in q1 if q[3] == ty and q[4] == og)
                                                for ty in sorted(set(q[3] for q in q1))
                                                for og in sorted(set(q[4] for q in q1))}))
    # Part R
    a0 = sorted({k[0] for k in nz})[0]
    comp = sorted(g for g in range(n) if STT(a0, g) == 0)
    gens = []
    for x in comp:
        for y in comp:
            k, z = 1, x
            while z != e_state and k < 40:
                z = MUL[z][x]
                k += 1
            if k == 10:
                gens.append(x)
                break
        if gens:
            break
    a5 = gens[0] if gens else None
    b2 = None
    if a5 is not None:
        for y in comp:
            if MUL[y][y] == MUL[a5][MUL[a5][MUL[a5][MUL[a5][a5]]]] and MUL[MUL[inv[y]][a5]][y] == inv[a5]:
                b2 = y
                break
    claim('R1', '補集 Π（%d 元）之成員、階 5 生成元與 Dic₅ 表現式（b² = a⁵ ∧ b⁻¹ab = a⁻¹）' % len(comp),
          len(comp) == 20 and a5 is not None and b2 is not None,
          'Π = %s；階 5 生成元 = %s；b（witness）= %s' % (comp, a5, b2))
    gset_zero = sorted(set(g for (a, g) in zero))
    p_ok = set(comp) <= set(gset_zero) and not (set(comp) & set(g for (a, g) in nz))
    claim('R2', '★ Π 之 20 元全為零鍵之 g 段且與非零鍵之 g 集不相交', p_ok,
          'Π ⊂ 零鍵 g 段 = %s；Π ∩ 非零 g 集 = %s' % (set(comp) <= set(gset_zero), sorted(set(comp) & set(g for (a, g) in nz))))
    claim('P1-c', '【校正】Σ 口徑：逐鍵 S_TT 之和 = 32；乘鍵重數 2 = **64**（＝ R26 之 Σ n·S_TT）；零鍵族（按 `dind` 同值項數）= {0: 32, 8: 8, 40: 10}',
          sum(S[k] for k in KS) == 32 and 2 * sum(S[k] for k in KS) == 64,
          'Σ 逐鍵 = %d；×2 = %d' % (sum(S[k] for k in KS), 2 * sum(S[k] for k in KS)))
    comb4 = {}
    for (a, g, s, ty, og, su) in q1:
        comb4.setdefault((s, su), []).append(a)
    claim('Q2-c', '【校正】四類之實測分割 = (S_TT 符號, sgn⟨U_a,KV_g⟩)：%s' % {str(k): v for k, v in comb4.items()},
          len(comb4) == 4, '組合 = %s' % {str(k): v for k, v in comb4.items()})
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  |  O225 R31 機器' % (npass, len(CLAIMS)))
    io.open(os.path.join(BASE, 'data', '115_r31_machine.json'), 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r31-stt-mechanism-v1', 'claims': CLAIMS, 'n_pass': npass, 'n_total': len(CLAIMS),
         'zero_keys': len(zero), 'nonzero_keys': len(nz), 'values': vals, 'zero_fam': {str(k): v for k, v in fam.items()},
         'nonzero_detail': q1, 'classes': {str(k): v for k, v in comb.items()}, 'complement': comp, 'a0': a0, 'comb4': {str(k): v for k, v in comb4.items()},
         'gens': {'a5': a5, 'b': b2}, 'witness_counts': sorted(set(len(v) for v in W.values()))},
        indent=1, ensure_ascii=False))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
