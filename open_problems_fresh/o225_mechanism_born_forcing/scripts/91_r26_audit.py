#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/91 -- R26 審計（獨立重算；不 import 本 o 之任何推導 script）。

A1  T1 之獨立重算：S_TT 以「y-索引」另路（Σ_{y: tie(y,a) ∧ tie(y·g⁻¹,a)}）逐值比對
A2  ★★ 補集 20 之獨立刻畫：{g : ∀a, S_TT(a,g) = 0}（另路）與機器之非零 g 集互補，逐位元
A3  ★★ 群結構獨立驗：封閉性以 Cayley 限制重檢；表現式 b² = a⁵、b⁻¹ab = a⁻¹ 以冪次顯式驗；⟨a,b⟩ 以逐次右乘閉包獨立生成
A4  ★★ Dic₅ 身份獨立驗：階譜 {1:1,2:1,4:10,5:4,10:4}、唯一對合且居中心、階 4 元素數 = 10
唯讀凍結機器；精確算術。用法: /usr/bin/python3 scripts/91_r26_audit.py
"""
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
RES = []


def check(tag, name, ok, detail=''):
    RES.append({'tag': tag, 'ok': bool(ok), 'detail': detail})
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


def main():
    print('=' * 118)
    print('O225 scripts/91 -- R26 AUDIT (independent recomputation)')
    print('=' * 118, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'a26_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'a26_a2')
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

    # ---- 另路（y-索引）：Σ_{y: tie(y,a) ∧ tie(y·g⁻¹,a)} [d 差]·ε(y)·ε(y·g⁻¹) ----
    def S_TT_yindex(a, g):
        gi = inv[g]
        tot = 0
        for y in range(n):
            x = MUL[y][gi]
            if tie[x][a] and tie[y][a]:
                tot += (0 if dind[x][a] == dind[y][a] else 1) * eps[x] * eps[y]
        return tot

    mach = json.load(io.open(os.path.join(BASE, 'data/90_r26_machine.json'), encoding='utf-8'))
    plus = set(mach['S_TT_support_plus8'])
    minus = set(mach['S_TT_support_minus8'])
    comp = sorted(mach['complement20'])
    bad = []
    for (a, g) in sorted(keys):
        v = S_TT_yindex(a, g)
        if (v == 8 and a not in plus) or (v == -8 and a not in minus) or (v not in (-8, 0, 8)):
            bad.append(((a, g), v))
    check('A1', 'T1 之另路重算（y-索引）：值集、+8／−8 欄集逐值一致', not bad,
          '差異數 = %d（樣本 %s）；另路值集 = %s' % (len(bad), bad[:5], sorted(set(S_TT_yindex(a, g) for (a, g) in keys))))

    nzg = sorted(g for g in range(n) if any(S_TT_yindex(a, g) != 0 for a in range(ncol)))
    comp2 = sorted(g for g in range(n) if g not in nzg)
    check('A2', '★★ 補集 20 之獨立刻畫：另路非零 g 集之補 = 機器補集（逐位元）', comp2 == comp,
          '另路 |非零 g| = %d；補集相符 = %s；相異 = %s' % (len(nzg), comp2 == comp, sorted(set(comp2) ^ set(comp))))

    cs = set(comp)
    # A3a 封閉性（另路：以 MUL 限制＋逐對檢）
    prod = sorted({MUL[i][j] for i in comp for j in comp})
    closed = all(p in cs for p in prod)
    # A3b 表現式（以 witness 冪次顯式）
    wit = mach.get('dic5_witness')
    a_, b_, _sz = wit if wit else (None, None, None)
    pres = False
    if a_ is not None:
        a5 = a_
        for _ in range(4):
            a5 = MUL[a5][a_]
        b2 = MUL[b_][b_]
        conjug = MUL[MUL[inv[b_]][a_]][b_]
        pres = (order[a_] == 10 and order[b_] == 4 and b2 == a5 and conjug == inv[a_])
    # A3c ⟨a,b⟩ 以右乘閉包獨立生成
    seen, frontier = {e_state}, [e_state]
    while frontier:
        nxt = []
        for x in frontier:
            for y in (a_, b_):
                z = MUL[x][y]
                if z not in seen:
                    seen.add(z)
                    nxt.append(z)
        frontier = nxt
    gen_ok = (seen == cs) if a_ is not None else False
    check('A3', '★★ 群結構獨立驗：封閉（乘積集 ⊆ 補集）＋ 表現式（階 10／階 4／b²=a⁵／b⁻¹ab=a⁻¹）＋ ⟨a,b⟩ = 補集',
          (closed and pres and gen_ok),
          '封閉 = %s（乘積集 %d）｜表現式 = %s（witness = %s）｜生成 = %s（|⟨a,b⟩| = %d）'
          % (closed, len(prod), pres, wit, gen_ok, len(seen)))

    prof = {o: len([g for g in comp if order[g] == o]) for o in (1, 2, 4, 5, 10)}
    invol = [g for g in comp if order[g] == 2]
    central = all(MUL[x][invol[0]] == MUL[invol[0]][x] for x in comp) if invol else False
    check('A4', '★★ Dic₅ 身份獨立驗：階譜 {1:1,2:1,4:10,5:4,10:4}、唯一對合且居中心（= a⁵）',
          prof == {1: 1, 2: 1, 4: 10, 5: 4, 10: 4} and len(invol) == 1 and central,
          '階譜 = %s；對合數 = %d；對合居中 = %s' % (prof, len(invol), central))

    io.open(os.path.join(BASE, 'data/91_r26_audit.json'), 'w', encoding='utf-8').write(json.dumps(
        {'script': '91_r26_audit', 'checks': RES, 'pass': sum(1 for r in RES if r['ok']), 'total': len(RES)},
        indent=1, ensure_ascii=False))
    p = sum(1 for r in RES if r['ok'])
    print('\nRESULT: %d/%d PASS' % (p, len(RES)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
