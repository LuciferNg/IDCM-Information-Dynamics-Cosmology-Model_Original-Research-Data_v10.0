#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/93 -- 全鏈盲測審計：階段 C（獨立重算）＋ D（精確 null）。

原則：**只由「定義」自行實作**（凍結物件之定義見 docs 與 O222 唯讀機器），不 import 本 o 任何推導
script，亦不讀任何輪次之輸出值；比對值以各輪 docs 之宣稱（claim）為對象，逐項報 PASS／FAIL。

B01 K 表：值集 {±1}、+1／−1 平衡、120/120 列之列和 ≠ 1（O222 交接 §二）
B02 協議重現：124 事件、62 鍵（多重度 2）、事件 sha 與 data/34_r9_pairing.json 相符
B03 tie 表三型別之欄計數（報值；供 docs 綁定）
B04 dind 雙路線等價：γ≠ε（機器定義）vs R22 之 (lidx 叉積, lidx KV) 判準，逐 (態,欄) 比對
B05 S_TT：y-索引路線（獨立於 x-索引）⟹ 值集／±8 欄／Σ n·S_TT = 64
B06 筆架（partner）閉合：−8 欄集 = 自身 partner 對合
B07 補集 20：群公理直驗（封閉／單位／逆／結合律全檢）＋階譜＋唯一對合居中心
B08 R24 恆等式：T_0 + T_1 = −u_2·A_0（A_0 由叉積自算，Z[√5] 逐值）
B09 R25 S4：8 非承載欄之 dind 共同值 ⟺ sgn(u_2)
B10 R26：零鍵項數分佈 {0,8,40}；非零鍵 8 項同號
B11 精確 null：G 內階 20 子群之數目（枚舉生成子群）vs C(120,20) ⟹ 補集為子群之機率
B12 精確 null：30 edge 欄中隨機 4-子集為 partner-閉合之機率 vs 實測 −8 欄集
唯讀凍結機器；精確算術（無浮點；null 用精確組合計數）。用法: /usr/bin/python3 scripts/93_audit_blind.py
"""
import importlib.util
import io
import json
import os
from fractions import Fraction as F
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
RES = []


def check(tag, name, ok, detail=''):
    RES.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


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


def dot3(u, v):
    return add(add(mul(u[0], v[0]), mul(u[1], v[1])), mul(u[2], v[2]))


def cross3(u, v):
    return (add(mul(u[1], v[2]), neg(mul(u[2], v[1]))),
            add(mul(u[2], v[0]), neg(mul(u[0], v[2]))),
            add(mul(u[0], v[1]), neg(mul(u[1], v[0]))))


def firstsgn(v):
    for c in v:
        s = sgn(c)
        if s:
            return s
    return 0


def lidx(v):
    for i, c in enumerate(v):
        if sgn(c) != 0:
            return i
    return None


def main():
    print('=' * 118)
    print('O225 scripts/93 -- BLIND AUDIT (independent re-derivation + exact nulls)')
    print('=' * 118, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'b93')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'b93a2')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    KV = [mm.rot_ref(g, U[0]) for g in G]
    e_state = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))][0]
    inv = [next(j for j in range(n) if MUL[i][j] == e_state) for i in range(n)]
    order = []
    for a in range(n):
        k, x = 1, a
        while x != e_state:
            x = MUL[x][a]
            k += 1
        order.append(k)
    tie = [[dot3(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [firstsgn(KV[s]) for s in range(n)]
    gam = [[firstsgn(cross3(U[a], KV[s])) for a in range(ncol)] for s in range(n)]
    dind = [[(1 if gam[s][a] != eps[s] else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]

    # B01 K 表
    vals = sorted({K[s][a] for s in range(n) for a in range(ncol)})
    np_, nm = len([1 for s in range(n) for a in range(ncol) if K[s][a] > 0]), \
        len([1 for s in range(n) for a in range(ncol) if K[s][a] < 0])
    rowsum_ok = all(sum(K[s]) != 1 for s in range(n))
    check('B01', 'K 表：值集 {±1}、+1/−1 平衡、120/120 列之列和 ≠ 1', vals == [-1, 1] and np_ == nm and rowsum_ok,
          '值集 = %s；+1/−1 = %d/%d；列和 ≠ 1 之列 = %d/120' % (vals, np_, nm, len([1 for s in range(n) if sum(K[s]) != 1])))

    # B02 協議重現（自寫 stack 協議，獨立於機器之實作）
    def events_stack(state):
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

    ev = events_stack(e_state)
    import hashlib
    sha = hashlib.sha256(repr(ev).encode()).hexdigest()
    d34 = json.load(io.open(os.path.join(BASE, 'data/34_r9_pairing.json'), encoding='utf-8'))
    keys = {}
    for (a, sw, sr) in ev:
        g = MUL[inv[sr]][sw]
        keys[(a, g)] = keys.get((a, g), 0) + 1
    mult2 = all(v == 2 for v in keys.values())
    check('B02', '協議重現：事件 124、鍵 62（多重度全 2）、事件 sha 符 data/34', 
          len(ev) == 124 and len(keys) == 62 and mult2 and sha == d34['events_sha'],
          '事件 = %d；鍵 = %d；多重度全 2 = %s；sha 相符 = %s' % (len(ev), len(keys), mult2, sha == d34['events_sha']))

    # B03 tie 三型別（報值）
    tc = {}
    for a in range(ncol):
        tc[str(types[a])] = tc.get(str(types[a]), 0) + 1
    check('B03', 'tie 表型別欄計數（報值；供 docs 綁定）', True, '型別計數 = %s' % tc)

    # B04 dind 雙路線
    mism = []
    for s in range(n):
        for a in range(ncol):
            cr = cross3(U[a], KV[s])
            i, j = lidx(cr), lidx(KV[s])
            if i is None or j is None:
                r22 = 0
            else:
                r22 = 1 if (sgn(cr[i]) * sgn(KV[s][j]) == -1) else 0
                if not tie[s][a]:
                    r22 = 0
            if r22 != dind[s][a]:
                mism.append((s, a, r22, dind[s][a]))
    check('B04', 'dind 雙路線等價：γ≠ε vs R22 (lidx 叉積, lidx KV) 判準，逐 (態,欄)',
          not mism, '不符 = %d（樣本 %s）' % (len(mism), mism[:5]))

    # B05 S_TT（y-索引）
    def S_TT_y(a, g):
        gi = inv[g]
        tot = 0
        for y in range(n):
            x = MUL[y][gi]
            if tie[x][a] and tie[y][a]:
                tot += (0 if dind[x][a] == dind[y][a] else 1) * eps[x] * eps[y]
        return tot

    S = {k: S_TT_y(*k) for k in keys}
    valset = sorted(set(S.values()))
    nzk = [k for k in keys if S[k] != 0]
    tot64 = sum(S[k] * keys[k] for k in keys)
    p8 = sorted({a for (a, g) in nzk if S[(a, g)] == 8})
    m8 = sorted({a for (a, g) in nzk if S[(a, g)] == -8})
    check('B05', 'S_TT（y-索引，獨立路線）：值集 {−8,0,8}、非零鍵 12、Σ n·S_TT = 64、±8 欄集',
          valset == [-8, 0, 8] and len(nzk) == 12 and tot64 == 64 and p8 == [32, 35, 36, 45, 48, 57, 58, 61]
          and m8 == [37, 38, 55, 56],
          '值集 = %s；非零鍵 = %d；Σ = %d；+8 = %s；−8 = %s' % (valset, len(nzk), tot64, p8, m8))

    # B06 partner 閉合
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(add(U[i][t], U[j][t]) == (0, 0) for t in range(3)):
                partner[i] = j
    pclose = sorted(a for a in m8 if partner.get(a) in m8)
    check('B06', '−8 欄集 [37,38,55,56] = 自身 partner 對合之閉合', pclose == m8,
          'partner 對：%s' % [(a, partner.get(a)) for a in m8])

    # B07 補集 20 群公理
    nzg = sorted(g for g in range(n) if any(S_TT_y(a, g) != 0 for a in range(ncol)))
    comp = sorted(g for g in range(n) if g not in nzg)
    cs = set(comp)
    closed = all(MUL[i][j] in cs for i in comp for j in comp)
    has_e = e_state in cs
    invs = all(inv[i] in cs for i in comp)
    assoc = all(MUL[MUL[i][j]][k] == MUL[i][MUL[j][k]] for i in comp for j in comp for k in comp)
    prof = {o: len([g for g in comp if order[g] == o]) for o in (1, 2, 4, 5, 10)}
    invol = [g for g in comp if order[g] == 2]
    central = all(MUL[x][invol[0]] == MUL[invol[0]][x] for x in comp) if invol else False
    check('B07', '補集 20：群公理全檢（封閉／單位／逆／結合律 8000 三元組）＋階譜＋唯一對合居中心',
          closed and has_e and invs and assoc and prof == {1: 1, 2: 1, 4: 10, 5: 4, 10: 4} and len(invol) == 1 and central,
          '封閉 = %s；單位 ∈ = %s；逆 ∈ = %s；結合律 = %s；階譜 = %s；對合 = %d；居中 = %s'
          % (closed, has_e, invs, assoc, prof, len(invol), central))

    # B08 R24 恆等式（A_0 由叉積自算）
    bad = []
    checked = 0
    for a in (41, 42):
        for s in range(n):
            if not tie[s][a]:
                continue
            x, u = KV[s], U[a]
            A0 = add(mul(u[1], x[2]), neg(mul(u[2], x[1])))
            T0 = mul(mul(u[0], u[1]), x[0])
            T1 = mul(add(mul(u[1], u[1]), mul(u[2], u[2])), x[1])
            lhs, rhs = add(T0, T1), neg(mul(u[2], A0))
            checked += 1
            if lhs != rhs:
                bad.append((a, s, lhs, rhs))
    check('B08', 'R24 恆等式：T_0 + T_1 = −u_2·A_0（A_0 = (u×x)_0 自算；Z[√5] 逐值）',
          not bad and checked > 0, '檢查 %d 個 (欄,態)；反例 = %d %s' % (checked, len(bad), bad[:3]))

    # B09 R25 S4
    noncar = [39, 40, 41, 42, 51, 52, 53, 54]
    rows = []
    for a in noncar:
        vs = sorted({dind[s][a] for s in range(n) if tie[s][a]})
        rows.append((a, vs, sgn(U[a][2])))
    ok9 = all(len(v) == 1 and ((v[0] == 0) == (s == -1)) for (_a, v, s) in rows)
    check('B09', 'R25 S4：8 非承載欄之 dind 共同值 = 0 ⟺ sgn(u_2) = −1；= 1 ⟺ +1',
          ok9, '逐欄 (欄, {dind}, sgn u_2) = %s' % rows)

    # B10 R26 零鍵三族 + 非零鍵同號
    def terms(a, g):
        out = []
        for x in range(n):
            y = MUL[x][g]
            if tie[x][a] and tie[y][a]:
                out.append((0 if dind[x][a] == dind[y][a] else 1) * eps[x] * eps[y])
        return out

    prof_k = {}
    for k in keys:
        ts = terms(*k)
        prof_k[k] = (len(ts), sum(1 for t in ts if t > 0), sum(1 for t in ts if t < 0))
    zf = sorted({prof_k[k][0] for k in keys if S[k] == 0})
    nzsame = all((prof_k[k][1] == 8 or prof_k[k][2] == 8) for k in keys if S[k] != 0)
    check('B10', 'R26：零鍵項數分佈 = {0,8,40}；非零鍵 8 項全同號', zf == [0, 8, 40] and nzsame,
          '零鍵項數集 = %s；非零鍵同號 = %s' % (zf, nzsame))

    # B11 精確 null：階 20 子群數 vs C(120,20)
    subs = set()
    for x in range(n):
        for y in range(n):
            seen, fr = {e_state}, [e_state]
            while fr:
                nx = []
                for z in fr:
                    for w in (x, y):
                        t = MUL[z][w]
                        if t not in seen:
                            seen.add(t)
                            nx.append(t)
                fr = nx
            if len(seen) == 20:
                subs.add(tuple(sorted(seen)))
    from math import comb
    total20 = comb(120, 20)
    check('B11', '精確 null：G 內階 20 子群之數目 / C(120,20) = 補集為子群之機率',
          True, '階 20 子群 = %d 個；C(120,20) = %d；P(隨機 20-子集為子群) ≤ %.3e' % (len(subs), total20, len(subs) / total20))

    # B12 精確 null：edge 欄中隨機 4-子集為 partner-閉合之機率
    edge = [a for a in range(ncol) if str(types[a]) == 'edge']
    n_pair_closed = 0
    for q in combinations(edge, 4):
        if all(partner.get(a) in q for a in q):
            n_pair_closed += 1
    tot4 = comb(len(edge), 4)
    obs = 1 if pclose == m8 else 0
    check('B12', '精確 null：30 edge 欄中隨機 4-子集為 partner-閉合之機率（vs 實測 −8 欄集）',
          True, 'partner-閉合 4-子集 = %d/%d（P ≈ %.4f）；實測 −8 欄閉合 = %s' % (n_pair_closed, tot4, n_pair_closed / tot4, obs))

    io.open(os.path.join(BASE, 'data', '93_audit_blind.json'), 'w', encoding='utf-8').write(json.dumps(
        {'script': '93_audit_blind', 'checks': RES, 'pass': sum(1 for r in RES if r['ok']), 'total': len(RES)},
        indent=1, ensure_ascii=False))
    p = sum(1 for r in RES if r['ok'])
    print('\nRESULT: %d/%d PASS' % (p, len(RES)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
