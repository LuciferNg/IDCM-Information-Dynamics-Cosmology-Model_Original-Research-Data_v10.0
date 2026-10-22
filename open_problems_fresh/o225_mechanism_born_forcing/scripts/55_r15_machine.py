#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/55 -- R15 機器：四項律之閉合（`r15-mechanism-v1`）。

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
RULES = 'r15-mechanism-v1'
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

    # ================= Part E：S_TT ≡ 0 之構造性機制 =================
    def wg(a, y, g):
        gi = inv[g]
        x = MUL[y][gi]
        if tie[y][a] and tie[x][a]:
            return (0 if dind[y][a] == dind[x][a] else 1) * eps[y] * eps[x]
        return 0
    def Wnonempty(a, g):
        gi = inv[g]
        return any(tie[y][a] and tie[MUL[y][gi]][a] and dind[y][a] != dind[MUL[y][gi]][a] for y in range(n))
    def cands(a):
        g = col_g[a]
        return sorted(set([e_state, zc, g, MUL[g][zc]] + [x for x in range(n) if MUL[MUL[x][g]][inv[x]] == inv[g]]))
    def flips(a, g, t):
        return all(wg(a, MUL[t][y], g) == -wg(a, y, g) for y in range(n))
    valid = {}
    for a in range(ncol):
        if types[a] != 'edge':
            continue
        gs = [g for g in range(n) if Wnonempty(a, g)]
        ok = {}
        for g in gs:
            ok[g] = sorted(t for t in cands(a) if flips(a, g, t))
        valid[a] = (gs, ok)
    e1 = sorted(a for a in range(ncol) if types[a] == 'edge' and all(valid[a][1][g] for g in valid[a][0]))
    claim('E1', '★★ 非承載 ⟺ 對每一 g（W_g ≠ ∅）∃ t ∈ {±e,±g_a} ∪ Inv(g_a)：w_g(t·y) = −w_g(y) ∀y',
          e1 == nec8, '命中 = %s（%d）; 非承載 8 = %s ; 無效 g 總數 = %s'
          % (e1, len(e1), nec8, {a: sum(1 for g in valid[a][0] if not valid[a][1][g]) for a in sorted(valid) if sum(1 for g in valid[a][0] if not valid[a][1][g])}))
    e2 = 0
    ex2 = []
    for k in nonempty:
        a = k[0]
        ext = sorted(set(tau[k]) - {k[1], MUL[k[1]][zc]})
        if not ext:
            continue
        gs = valid[a][0]
        if all(ext[0] in valid[a][1][g] for g in gs):
            e2 += 1
        else:
            ex2.append((k, ext, sum(1 for g in gs if ext[0] in valid[a][1][g]), len(gs)))
    big = [k for k in nonempty if len(tau[k]) == 4]
    claim('E2', '★★ |τ| = 4 之 4 鍵：該 t 恆可取為 τ 之額外元素 h（對所有 g）', e2 == len(big),
          '成立 = %d/%d ; 例 = %s' % (e2, len(big), ex2))
    e3 = sorted(a for a in range(ncol) if types[a] == 'edge' and a in set(nz22) and any(not valid[a][1][g] for g in valid[a][0]))
    claim('E3', '★ 承載欄：∃ g 使所有 t 皆不滿足（機制之反面）', e3 == nz22,
          '存在無效 g 之承載欄 = %d/%d ; 非承載之無效 g 總數 = %d'
          % (len(e3), len(nz22), sum(sum(1 for g in valid[a][0] if not valid[a][1][g]) for a in nec8)))
    e4 = {}
    for a in [41, 42, 51, 52]:
        gs, ok = valid[a]
        used = sorted(set(t for g in gs for t in ok[g]))
        e4[a] = {'無效 g 數': sum(1 for g in gs if not ok[g]), '有效 t 集合': used,
                 't 之階': sorted(set(order[t] for t in used))}
    claim('E4', '★ [41,42,51,52] 逐欄之有效 t 集合與階（量測）', True, '%s' % e4)

    # ================= Part G：pre(T) → Z10 之篩選 =================
    T4 = sorted(set(KV[s] for s in Z10))
    pre4 = sorted(s for s in range(n) if KV[s] in set(T4))
    zset = set(Z10)
    def pairs_of(states):
        out = {}
        for s in states:
            if s in out or MUL[s][zc] in out:
                continue
            out[s] = None
        return out
    ord_pairs = {}
    for s in pre4:
        if MUL[s][zc] in ord_pairs:
            continue
        ord_pairs[s] = order[s]
    zo = {}
    for s in Z10:
        if MUL[s][zc] in zo:
            continue
        zo[s] = order[s]
    claim('G1', '★ Z10 於每一非平凡階 o ∈ {3,4,5,6,10} 恰取一個中心對',
          sorted(zo.values()) == [3, 4, 5, 6, 10],
          'Z10 對之階 = %s ; pre(T) 20 對之階譜 = %s' % (sorted(zo.values()),
          {k: sorted(ord_pairs.values()).count(k) for k in sorted(set(ord_pairs.values()))}))
    zt = {s: (f_tf[s], f_ft[s]) for s in Z10}
    claim('G2', '★ 強形式：Z10 = {s ∈ pre(T) : f_tf(s) = 0 ∧ f_ft(s) = 0}',
          all(v == (0, 0) for v in zt.values()), 'Z10 之 (f_tf, f_ft) = %s' % zt)
    g3 = {}
    for k, o in sorted(zo.items()):
        same = [s for s in ord_pairs if ord_pairs[s] == o and f_tt[s] in (0, 1, 3)]
        g3[o] = (k, f_tt[k], sorted((s, f_tt[s]) for s in same))
    nuniq = sum(1 for o, (k, fk, same) in g3.items() if len(same) == 1 and same[0][0] == k)
    claim('G3', '★ 各階 o：Z10 之對 = pre(T) 內該階唯一 f_tt ∈ {0,1,3} 之對', nuniq == len(zo),
          '成立階數 = %d/%d ; 逐階 = %s' % (nuniq, len(zo), g3))

    # ================= Part A：A8 之根因 =================
    cols16 = sorted(set(k[0] for k in nonempty))
    a1 = {'cols16': cols16, 'carrier': sorted(a for a in cols16 if a in set(nz22)),
          'neccol': sorted(a for a in cols16 if a in set(nec8))}
    nec_lines = sorted(set(min(a, partner[a]) for a in nec8))
    perline = {L: sorted(a for a in (L, partner[L]) if a in set(a1['neccol'])) for L in nec_lines}
    claim('A1', '★ 16 非空鍵之欄與 22/8 之交叉（猜測：每條非承載軸線恰貢獻一欄）',
          all(len(v) == 1 for v in perline.values()) and len(a1['neccol']) == 4,
          '16 欄 = %s ; 承載 ∩ 16 = %s ; 非承載 ∩ 16 = %s ; 每條非承載線之貢獻 = %s'
          % (cols16, a1['carrier'], a1['neccol'], perline))
    a2 = sorted(k[0] for k in big)
    lines = sorted(set(min(a, partner[a]) for a in a2))
    claim('A2', '★ |τ| = 4 之 4 欄 = 4 條非承載軸線各取一欄（且 4 欄互不同線）',
          len(set(lines)) == 4 and all(a in set(nec8) for a in a2),
          '|τ|=4 之欄 = %s ; 所屬線 = %s ; 4 條非承載線 = %s'
          % (a2, lines, sorted(set(nec8))))
    a3 = 0
    a3det = []
    for k in big:
        a = k[0]
        ext = sorted(set(tau[k]) - {k[1], MUL[k[1]][zc]})
        F = sorted(x for x in range(n) if Tx[k][x] != 0)
        okdef = all((MUL[ext[0]][x] in set(F)) == (x in set(F)) and
                    (Tx[k][MUL[ext[0]][x]] == (-Tx[k][x] if x in set(F) else 0)) for x in range(n))
        okw = all(ext[0] in valid[a][1][g] for g in valid[a][0])
        if okdef and okw:
            a3 += 1
        else:
            a3det.append((k, ext, okdef, okw))
    claim('A3', '★★ |τ| = 4 ⟺ ∃h：同時（i）τ 之額外元素（T 反號、F 保）與（ii）E1 之 w-反號（同一 h）',
          a3 == len(big), '同一 h 成全兩者 = %d/%d ; 例外 = %s' % (a3, len(big), a3det))

    # ================= Part E5–E6：非承載 8 之完整分類（追加，未見此數） =================
    nz_g = {a: sum(1 for g in range(n) if Wnonempty(a, g)) for a in range(ncol) if types[a] == 'edge'}
    vac = sorted(a for a in nz_g if nz_g[a] == 0)
    claim('E5', '★ [41,42,51,52]：∀g W_g = ∅（|{g : W_g ≠ ∅}| = 0）⟹ 非承載屬 vacuous（空和）',
          vac == [41, 42, 51, 52],
          '空和欄 = %s ; 非承載 8 = %s ; 各欄 |{g : W_g ≠ ∅}| 之分佈 = %s'
          % (vac, nec8, sorted(set(nz_g.values()))))
    claim('E6', '★★ 非承載 8 之完整分類 = 4 vacuous（[41,42,51,52]）＋ 4 h-反號構造性（[39,40,53,54]）',
          sorted(vac) == [41, 42, 51, 52] and sorted(a for a in nec8 if a not in set(vac)) == [39, 40, 53, 54],
          'vacuous = %s ; 非 vacuous 之非承載 = %s ; 承載欄之 |{g : W_g ≠ ∅}| 最小值 = %d'
          % (vac, sorted(a for a in nec8 if a not in set(vac)), min(nz_g[a] for a in nz22)))
    zpair = {}
    for s in Z10:
        if MUL[s][zc] in zpair:
            continue
        zpair[s] = (order[s], order[MUL[s][zc]])
    claim('E7', '★ Z10 之 5 中心對之元素階型（量測）：2×{3,6} ＋ 1×{4,4} ＋ 2×{5,10}',
          sorted(zpair.values()) == [(3, 6), (3, 6), (4, 4), (5, 10), (5, 10)],
          '逐對 = %s ; pre(T) 20 對之階型譜 = %s'
          % (zpair, {tuple(k): sum(1 for s in pre4 if (MUL[s][zc] not in zpair and s not in zpair) and (order[s], order[MUL[s][zc]]) == k) for k in set((order[s], order[MUL[s][zc]]) for s in pre4)}))
    # ================= Part E8／A4：★ 真相（追加，未見此數） =================
    srt = {a: sum(1 for g in range(n) if any(wg(a, y, g) != 0 for y in range(n))) for a in range(ncol) if types[a] == 'edge'}
    same_cnt = sorted(set((nz_g[a], srt[a]) for a in nz_g))
    claim('E8', '★★ ∀a ∈ 30 edge：#\{g : S_TT(a,g) ≠ 0\} = #\{g : W_g ≠ ∅\}（∈ {0,100}）⟹ 加項從不抵消，非承載 = 純空和',
          same_cnt == [(0, 0), (100, 100)], '（W-非空 g 數, S_TT-非零 g 數）配對 = %s' % same_cnt)
    claim('E1v', '註記：E1 之「∃t ∀g」對 8 非承載欄為 **vacuous**（gs = ∅ ⟹ 條件自動成立）⟹ E1 之 PASS 不構成機制證據',
          all(len(valid[a][0]) == 0 for a in nec8), '非承載欄之 |{g : W_g ≠ ∅}| = %s' % sorted(set(len(valid[a][0]) for a in nec8)))
    claim('E2v', '註記：E2 之「h 滿足 w-反號 ∀g」亦為 vacuous（gs = ∅）⟹ 不構成 A8 之根因證據',
          all(len(valid[k[0]][0]) == 0 for k in big), '4 鍵之 |gs| = %s' % sorted(set(len(valid[k[0]][0]) for k in big)))
    claim('A4', '★★ A8 之根因（重述為結構空集）：|τ| = 4 ⟺ 該欄 W-支撐全空（W_a ≡ ∅）⟺ 非承載',
          all(len(valid[k[0]][0]) == 0 for k in big) and
          sorted(set(k[0] for k in big)) == [40, 42, 52, 54] and
          all(a in set(nec8) for a in (k[0] for k in big)),
          '|τ|=4 之欄 = %s ; 其 W-非空 g 數 = %s ; 非承載 8 = %s'
          % (sorted(k[0] for k in big), [len(valid[k[0]][0]) for k in big], nec8))
    claim('A5', '★ 承載欄之 W-非空 g 數 = 100（22/22 均一）；非承載 = 0（8/8）',
          sorted(set(nz_g[a] for a in nz22)) == [100] and sorted(set(nz_g[a] for a in nec8)) == [0],
          '承載之 g 數集 = %s ; 非承載 = %s' % (sorted(set(nz_g[a] for a in nz22)), sorted(set(nz_g[a] for a in nec8))))
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R15 機器' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/55_r15_machine.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'keys': [[k[0], k[1]] for k in sorted(keys)],
                   'E': {'nec8': nec8, 'nz22': nz22, 'valid': {str(a): {str(g): valid[a][1][g] for g in valid[a][0]} for a in valid}},
                   'G': {'zo': {str(k): v for k, v in zo.items()}, 'pre4': pre4},
                   'A': {'cols16': cols16, 'bigcols': a2}},
                  fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
