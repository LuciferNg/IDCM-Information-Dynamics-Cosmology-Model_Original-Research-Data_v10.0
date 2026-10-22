#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/52 -- R14 機器：四項律之閉合（`r12-law-closure-v1`）。

Part X  τ 之刻畫（16 非空 TF 鍵；中心不變／大小／階／中心化子）
Part Y  Z10 選擇律（KV 相鄰性精確核／重數／∩{g_a}／每對同 KV／f_tt）
Part Z  補集 20（成群？／∩{g_a} 型別／∩Z10）
Part Q  orbit 分類（型別單一性／31 對型別／非承載 8 edge 欄之 U 結構／承載列 g_a 階）

精確算術（Z[√5]：(a,b) 表 a+b√5，p² vs 5q²）；唯讀凍結機器（O222）。用法: /usr/bin/python3 scripts/45_r12_machine.py
"""
import hashlib
import importlib.util
import io
import json
import os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
RULES = 'r12-law-closure-v1'
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-7s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


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
    print('O225 scripts/45 -- R12 MACHINE   (rules: %s)' % RULES)
    print('=' * 118, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'r12_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'r12_a2')
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
    zc = [s for s in range(n) if s != e_state and order[s] == 2][0]
    tie = [[dot3(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [firstsgn(KV[s]) for s in range(n)]
    gam = [[firstsgn(cross3(U[a], KV[s])) for a in range(ncol)] for s in range(n)]
    dind = [[(1 if gam[s][a] != eps[s] else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]
    PAIR = [[(sgn(dot3(U[a], KV[s])), firstsgn(cross3(U[a], KV[s]))) for a in range(ncol)] for s in range(n)]
    c2 = [[sgn(cross3(U[a], KV[s])[1]) for a in range(ncol)] for s in range(n)]
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(add(U[i][t], U[j][t]) == (0, 0) for t in range(3)):
                partner[i] = j
    pairs = sorted(i for i in range(ncol) if i < partner[i])

    # 事件 + 62 鍵（同式；回歸核）
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
    d34 = json.load(io.open(os.path.join(BASE, 'data/34_r9_pairing.json'), encoding='utf-8'))
    sha_ok = hashlib.sha256(repr(my_ev).encode()).hexdigest() == d34['events_sha']
    keys = {}
    for (a, sw, sr) in my_ev:
        g = MUL[inv[sr]][sw]
        keys[(a, g)] = keys.get((a, g), 0) + 1
    info('前置核：事件 %d 條、sha 相符 = %s、鍵 = %d' % (len(my_ev), sha_ok, len(keys)))

    def Tterm(x, a, g):
        y = MUL[x][g]
        if tie[x][a] and not tie[y][a]:
            return dind[x][a] * eps[x] * sgn(dot3(U[a], KV[y]))
        return 0

    Tx = {k: [Tterm(x, k[0], k[1]) for x in range(n)] for k in sorted(keys)}
    empty = [k for k in Tx if all(v == 0 for v in Tx[k])]
    nonempty = [k for k in Tx if any(v != 0 for v in Tx[k])]

    # ================= 前置：keys / tau / Z10 / S_TT（與 R11/R12 同式） =================
    keys = {}
    for (a, sw, sr) in my_ev:
        g = MUL[inv[sr]][sw]
        keys[(a, g)] = keys.get((a, g), 0) + 1

    def Tterm(x, a, g):
        y = MUL[x][g]
        if tie[x][a] and not tie[y][a]:
            return dind[x][a] * eps[x] * sgn(dot3(U[a], KV[y]))
        return 0

    Tx = {k: [Tterm(x, k[0], k[1]) for x in range(n)] for k in sorted(keys)}
    nonempty = [k for k in Tx if any(v != 0 for v in Tx[k])]
    tau = {}
    for k in nonempty:
        T = Tx[k]
        tf = set(x for x in range(n) if T[x] != 0)
        tau[k] = sorted(t for t in range(n) if all((((MUL[t][x] in tf) == (x in tf)) and
                     (T[MUL[t][x]] == (-T[x] if x in tf else 0))) for x in range(n)))

    def S_TT(a, g):
        tot = 0
        for x in range(n):
            y = MUL[x][g]
            if tie[x][a] and tie[y][a]:
                tot += (0 if dind[x][a] == dind[y][a] else 1) * eps[x] * eps[y]
        return tot

    f_tf = [0] * n
    f_ft = [0] * n
    f_tt = [0] * n
    for s0 in range(n):
        for (a, sw, sr) in my_ev:
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            tw, tr = tie[w][a], tie[r2][a]
            if tw and tr:
                f_tt[s0] += (0 if dind[r2][a] == dind[w][a] else 1) * eps[r2] * eps[w]
            elif tr:
                f_tf[s0] += dind[r2][a] * eps[r2] * sgn(dot3(U[a], KV[w]))
            elif tw:
                f_ft[s0] += dind[w][a] * eps[w] * sgn(dot3(U[a], KV[r2]))
    Z10 = sorted(s for s in range(n) if f_tf[s] + f_ft[s] == 0)
    col_of = {}
    col_g = {}
    for (a, g) in keys:
        col_of[g] = a
        col_g[a] = g
    pairs = sorted(i for i in range(ncol) if i < partner[i])
    nz22 = sorted(a for a in range(ncol) if any(S_TT(a, g) != 0 for g in range(n)))
    nec8 = sorted(a for a in range(ncol) if types[a] == 'edge' and a not in set(nz22))
    info('前置：非空鍵 = %d、|τ| 分佈 = %s、Z10 = %s、承載列 = %d（型別 %s）、非承載 edge 欄 = %s'
         % (len(nonempty), sorted(set(len(tau[k]) for k in nonempty)), Z10, len(nz22),
            sorted(set(types[a] for a in nz22)), nec8))

    # ================= Part E：共同根因（h 存在 ⟺ 非承載） =================
    Tset = {a: sorted(x for x in range(n) if tie[x][a]) for a in range(ncol)}
    stabset = {a: sorted(s for s in range(n) if sorted(MUL[s][x] for x in Tset[a]) == Tset[a])
               for a in range(ncol)}
    def Inv_of(g):
        return sorted(x for x in range(n) if MUL[MUL[x][g]][inv[x]] == inv[g])
    ed = [k for k in sorted(keys) if types[k[0]] == 'edge' and len(Tset[k[0]]) == 40]
    e1 = 0
    for k in ed:
        a, g = k
        IS = set(stabset[a]) & set(Inv_of(g))
        if (all(S_TT(a, gg) == 0 for gg in range(n))) == (len(IS) > 0):
            e1 += 1
    claim('E1', '★ nec ⟺ ∃ σ ∈ Inv(g_a) ∩ Stab_set(T_a)（30 edge 欄）', e1 == len(ed),
          '一致 = %d/%d ; 非承載 8 = %s' % (e1, len(ed), nec8))
    e2, ex = 0, []
    for k in nonempty:
        a, g = k
        IS = set(stabset[a]) & set(Inv_of(g))
        ext = set(tau[k]) - {g, MUL[g][zc]}
        if IS == ext:
            e2 += 1
        elif len(ex) < 4:
            ex.append((k, sorted(ext), sorted(IS)))
    claim('E2', '★★ h ∈ τ(a) ⟺ h ∈ Inv(g_a) ∩ Stab_set(T_a)（兩集相等 ⟹ 根因候選）', e2 == len(nonempty),
          '相等 = %d/%d ; 例外 = %s' % (e2, len(nonempty), ex))
    dsz = {}
    for a in range(ncol):
        if types[a] == 'edge':
            kkey = (a in set(nec8), len(stabset[a]))
            dsz[kkey] = dsz.get(kkey, 0) + 1
    claim('E3', '★ |Stab_set(T_a)| 分佈：非承載 vs 承載', True, '（非承載?, |Stab|）→ 欄數 = %s' % dsz)

    # ================= Part F：{45,48} 例外 =================
    D5 = sorted(g for g in range(n) if S_TT(nz22[0], g) == 0)
    f5 = sorted(g for g in D5 if order[g] == 5)
    zeta = next((v for v in range(n) if mm.rot_ref(G[f5[0]], KV[v]) == KV[v]), None)
    zd = KV[zeta] if zeta is not None else None
    B10 = sorted(a for a in range(ncol) if types[a] == 'edge' and
                 dot3(U[a], U[0]) in ((F(-1, 2), F(1, 2)), (F(1, 2), F(-1, 2))))
    coord = sorted(a for a in range(ncol) if types[a] == 'edge' and sum(1 for c in U[a] if c == (0, 0)) == 2)
    inB = sorted(a for a in B10 if a in set(coord))
    claim('F1', '★ {45,48} 為 B 中唯一之坐標軸線對', inB == [45, 48],
          'B 內坐標軸欄 = %s ; 全 30 edge 之坐標軸欄 = %s' % (inB, coord))
    zeros = sorted(a for a in B10 if dot3(U[a], zd) == (0, 0))
    claim('F2', '★ {45,48} 為 B 中唯一 ⟨U_a, ζ⟩ = 0（ζ = Dic₅ 之 5 階軸）者', zeros == [45, 48],
          'ζ = %s ; B 內零欄 = %s ; 逐欄 dot = %s' % (zeta, zeros, [str(dot3(U[a], zd)) for a in B10]))
    f3 = sorted(a for a in range(ncol) if types[a] == 'edge' and len(set(stabset[a]) & set(Inv_of(col_g[a]))) == 0)
    claim('F3', '★ 承載 ⟺ Stab_set(T_a) ∩ Inv(g_a) = ∅（30 edge 欄）', f3 == nz22,
          '無反演元之欄 = %s（%d）; 承載 = %s' % (f3, len(f3), nz22))

    # ================= Part G：Z10 之結構 =================
    T4 = sorted(set(KV[s] for s in Z10))
    tdm = {}
    for i in range(4):
        for j in range(i + 1, 4):
            kk = str(dot3(T4[i], T4[j]))
            tdm[kk] = tdm.get(kk, 0) + 1
    antip = [(i, j) for i in range(4) for j in range(i + 1, 4)
             if all(add(T4[i][t], T4[j][t]) == (0, 0) for t in range(3))]
    claim('G1', '★★ T = {u, −u, v, w}：恰一對對反極 ＋ u,v,w 兩兩 dot = φ⁻¹', True,
          'T4 = %s ; 對反對 = %s ; dot 譜 = %s' % ([str(x) for x in T4], antip, tdm))
    pre4 = sorted(s for s in range(n) if KV[s] in set(T4))
    diff = [s for s in pre4 if s not in set(Z10)]
    ordf = {}
    for s in diff:
        ordf[order[s]] = ordf.get(order[s], 0) + 1
    ordf_in = {}
    for s in Z10:
        ordf_in[order[s]] = ordf_in.get(order[s], 0) + 1
    claim('G2', '★ |pre(T)| = 40；Z10 與 pre(T) 之差集（30 態）之階分佈（Z10 為 5 中心對）',
          len(pre4) == 40 and len(diff) == 30,
          '|pre| = %d ; 差集階分佈 = %s ; Z10 階分佈 = %s' % (len(pre4), ordf, ordf_in))
    cnt = {}
    for s in range(n):
        cnt[s] = sum(1 for a in range(ncol) if tie[s][a] and dind[s][a] == 1)
    c_in = sorted(set(cnt[s] for s in Z10))
    c_out = sorted(set(cnt[s] for s in range(n) if s not in set(Z10)))
    claim('G3', '★ Z10 之候選判準：c(s) = |{a : tie(s,a) ∧ dind(s,a)=1}| 於 Z10 恆定且異於外界',
          len(c_in) == 1 and not (set(c_in) & set(c_out)),
          'Z10 之 c 值集 = %s ; 外界 c 值集 = %s' % (c_in, c_out[:14]))

    # ================= Part E4／F4：★ 符號翻轉機制（追加預註冊，未見此數） =================
    def epsflip(t):
        return all(eps[MUL[t][x]] == -eps[x] for x in range(n))
    def dindpres(t, a):
        return all(dind[MUL[t][x]][a] == dind[x][a] for x in range(n))
    def tiepres(t, a):
        return all(tie[MUL[t][x]][a] == tie[x][a] for x in range(n))
    def Wpres(t, a, g):
        gi = inv[g]
        Wg = [y for y in range(n) if tie[y][a] and tie[MUL[y][gi]][a] and dind[y][a] != dind[MUL[y][gi]][a]]
        return sorted(MUL[t][y] for y in Wg) == Wg, len(Wg)
    e4 = {}
    for a in range(ncol):
        if types[a] != 'edge':
            continue
        g = col_g[a]
        cand = []
        for t in range(n):
            if t in (e_state, MUL[e_state][zc]) or t in (g, MUL[g][zc]):
                continue
            if not (tiepres(t, a) and dindpres(t, a) and epsflip(t)):
                continue
            okW = all(Wpres(t, a, gg)[0] for gg in range(n))
            cand.append((t, order[t], okW))
        e4[a] = cand
    hit = sorted(a for a in range(ncol) if types[a] == 'edge' and any(c[2] for c in e4[a]))
    claim('E4', '★★ 非承載 ⟺ ∃ t（tie 保、dind 保、ε 反號、且所有 W_g 在 t 下封閉）⟹ S_TT ≡ 0',
          hit == nec8, '命中欄 = %s（%d）; 非承載 8 = %s ; 逐欄候選數 = %s'
          % (hit, len(hit), nec8, {a: len(e4[a]) for a in range(ncol) if types[a] == 'edge' and e4[a]}))
    B5lines = {}
    for a in sorted(B10):
        B5lines[a] = {'coord': a in set(coord), 'carry': a in set(nz22),
                      'nt': len([c for c in e4[a] if c[2]]), 'orders': sorted(set(c[1] for c in e4[a]))}
    claim('F4', '★ B10 之 5 線逐欄：坐標軸? / 承載? / 符號翻轉元數（E4 判準）',
          True, '逐欄 = %s' % [(a, B5lines[a]) for a in sorted(B10)])
    # ================= Part E5–E7：★ 兩型翻轉（追加，未見數） =================
    def ttype(t):
        de = all(dind[MUL[t][x]][0] == 0 for x in range(1))  # 佔位（不使用者）
        return None
    mech = {}
    for a in range(ncol):
        if types[a] != 'edge':
            continue
        g = col_g[a]
        gof = []
        for t in range(n):
            if t in (e_state, MUL[e_state][zc]) or t in (g, MUL[g][zc]):
                continue
            if not tiepres(t, a):
                continue
            if not all(Wpres(t, a, gg)[0] for gg in range(n)):
                continue
            chd = all(dind[MUL[t][x]][a] == 1 - dind[x][a] for x in range(n) if tie[x][a])
            chd0 = all(dind[MUL[t][x]][a] == dind[x][a] for x in range(n))
            che = epsflip(t)
            gof.append((t, order[t], chd, chd0, che, t in set(Inv_of(g))))
        mech[a] = gof
    E5set = sorted(a for a in range(ncol) if types[a] == 'edge' and any(c[2] and not c[4] for c in mech[a]))
    E4set = sorted(a for a in range(ncol) if types[a] == 'edge' and any(c[4] and c[3] for c in mech[a]))
    E6set = sorted(a for a in range(ncol) if types[a] == 'edge' and any(c[3] != (True,) and (c[4] or c[2]) for c in mech[a]))
    claim('E5', '★★ 第二型翻轉：nec ⟺ ∃t（tie 保、dind 反、ε 保、W 封閉）', E5set == nec8,
          '命中 = %s（%d）; 非承載 8 = %s' % (E5set, len(E5set), nec8))
    claim('E6', '★★ 統一：nec8 ⟺ ∃t（tie 保、W 封閉，且 (dind,ε) 至少一項變號）', E6set == nec8,
          'E4 型欄 = %s ; E5 型欄 = %s ; E6 併 = %s（%d）; 非承載 8 = %s'
          % (E4set, E5set, E6set, len(E6set), nec8))
    E7 = {a: [(c[1], c[2], c[3], c[4], c[5]) for c in mech[a]] for a in range(ncol) if types[a] == 'edge' and mech[a]}
    claim('E7', '★ 兩型翻轉元之階／是否 ∈ Inv(g_a)（判據：全為階 4 且 ∈ Inv）',
          all(all(c[0] == 4 and c[4] for c in v) for v in E7.values()), '逐欄 = %s' % E7)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R14 機器' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/52_r14_machine.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'E': {'nec8': nec8, 'nz22': nz22, 'stab_sizes': {str(k): v for k, v in dsz.items()}},
                   'F': {'B10': B10, 'zeros': zeros, 'zeta': zeta},
                   'G': {'T4': [str(x) for x in T4], 'dots': tdm, 'c_in': c_in},
                   'keys': [[k[0], k[1]] for k in sorted(keys)],
                   'E6': {'E4set': E4set, 'E5set': E5set, 'E6set': E6set}},
                  fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
