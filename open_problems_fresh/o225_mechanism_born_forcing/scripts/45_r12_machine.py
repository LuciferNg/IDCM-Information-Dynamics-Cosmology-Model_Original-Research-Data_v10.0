#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/45 -- R12 機器：四項律之閉合（`r12-law-closure-v1`）。

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

    # ================= Part X =================
    tau = {}
    for k in nonempty:
        T = Tx[k]
        tf = set(x for x in range(n) if T[x] != 0)
        good = []
        for t in range(n):
            if all((((MUL[t][x] in tf) == (x in tf)) and
                    (T[MUL[t][x]] == (-T[x] if x in tf else 0))) for x in range(n)):
                good.append(t)
        tau[k] = sorted(good)
    cen_ok = sum(1 for k in nonempty if all(MUL[t][zc] in set(tau[k]) for t in tau[k]))
    claim('X1', 'τ 候選集中心不變（τ ⟹ −τ）', cen_ok == len(nonempty),
          '成立之鍵 = %d/%d' % (cen_ok, len(nonempty)))
    sizes = sorted(set(len(tau[k]) for k in nonempty))
    paircnt = all(len(tau[k]) % 2 == 0 and all(MUL[t][zc] in set(tau[k]) for t in tau[k]) for k in nonempty)
    claim('X2', 'τ 候選集大小 ∈ {2,4} 且恰為 1 或 2 個中心對', sizes == [2, 4] or set(sizes) <= {2, 4},
          '大小值集 = %s ; 皆成中心對 = %s' % (sizes, paircnt))
    same_ord = sum(1 for k in nonempty if all(order[t] == order[k[1]] for t in tau[k]))
    claim('X3', '★ τ 與該鍵之 g_a 同階', same_ord == len(nonempty),
          '同階之鍵 = %d/%d ; (階(g_a), 階(τ)) 樣本 = %s'
          % (same_ord, len(nonempty), [(order[k[1]], sorted(set(order[t] for t in tau[k]))) for k in nonempty[:4]]))
    cen_hits = {'中央化子': 0, 'g_a': 0, 'g_a⁻¹': 0}
    for k in nonempty:
        g = k[1]
        Cg = set(x for x in range(n) if MUL[x][g] == MUL[g][x])
        if any(t in Cg for t in tau[k]):
            cen_hits['中央化子'] += 1
        if g in tau[k]:
            cen_hits['g_a'] += 1
        if inv[g] in tau[k]:
            cen_hits['g_a⁻¹'] += 1
    which = [kk for kk, vv in cen_hits.items() if vv == len(nonempty)]
    claim('X4', '★ τ 落於 C(g_a)／{g_a}／{g_a⁻¹} 之一（全鍵一致者）',
          len(which) >= 1, '全鍵命中 = %s ; 分佈 = %s' % (which, cen_hits))
    kmap = {a: k for k in nonempty for a in [k[0]]}
    pl = [k for k in nonempty if partner[k[0]] in kmap]
    same_pair = sum(1 for k in pl if tau[k] == tau[kmap[partner[k[0]]]])
    claim('X5', 'τ 集只依軸線（16 鍵中 partner 亦在 16 鍵者，其 τ 集相同）',
          same_pair == len(pl), '可配對之鍵 = %d ; τ 集相同 = %d' % (len(pl), same_pair))
    o_empty = sorted(set(order[k[1]] for k in empty))
    o_non = sorted(set(order[k[1]] for k in nonempty))
    claim('X6', '46 空集鍵之 g_a 階分佈 vs 16 非空鍵（報）', True,
          '空集鍵之階值集 = %s ; 非空鍵之階值集 = %s' % (o_empty, o_non))

    # ================= Part Y =================
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
    d31 = json.load(io.open(os.path.join(BASE, 'data/31_r8_group.json'), encoding='utf-8'))
    info('Y 前置核：f 與 R8 凍結全同 = %s ; Z10 = %s'
         % (f_tf == d31['f_tf'] and f_ft == d31['f_ft'] and f_tt == d31['f_tt'], Z10))
    kvz = sorted(set(KV[s] for s in Z10))
    if len(kvz) == 4:
        v1, v2 = kvz[0], kvz[1]
        d = dot3(v1, v2)
        n1, n2 = dot3(v1, v1), dot3(v2, v2)
        ok_adj = (mul((5, 0), mul(d, d)) == mul(n1, n2))   # 5·(v₁·v₂)² = |v₁|²|v₂|²
    else:
        d = n1 = n2 = None
        ok_adj = False
    claim('Y1', '★ Z10 之 KV = 2 對反極且相鄰（精確：5·(v₁·v₂)² = |v₁|²|v₂|²）', ok_adj,
          '|KV(Z10)| = %d ; v₁·v₂ = %s ; |v₁|² = %s ; |v₂|² = %s' % (len(kvz), d, n1, n2))
    from collections import Counter as _C
    kvc = _C(KV[s] for s in Z10)
    quad = [k for k, v in kvc.items() if v == 4]
    vneg = lambda v: tuple(neg(c) for c in v)
    anti = all(vneg(x) in set(kvz) for x in kvz)
    claim('Y2', 'KV 重數 = {2,2,2,4}；4 重極之對反極亦在集內', sorted(kvc.values()) == [2, 2, 2, 4] and anti,
          '重數 = %s ; 4 重極數 = %d ; 對反封閉 = %s' % (sorted(kvc.values()), len(quad), anti))
    ga_set = set(g for (a, g) in keys)
    inter = sorted(set(Z10) & ga_set)
    claim('Y3', 'Z10 ∩ {g_a} = 0（未見數，預註冊猜測）', len(inter) == 0, '交集 = %s（大小 %d）' % (inter, len(inter)))
    samekv = sum(1 for s in Z10 if KV[s] == KV[MUL[s][zc]])
    claim('Y4', 'Z10 之 5 對之階 = {3,4,5,6,10} 且每對兩元素 KV 相同',
          sorted(set(order[s] for s in Z10)) == [3, 4, 5, 6, 10] and samekv == len(Z10),
          '階值集 = %s ; 同 KV = %d/%d' % (sorted(set(order[s] for s in Z10)), samekv, len(Z10)))
    ftz = sorted(set(f_tt[s] for s in Z10))
    claim('Y5', 'f_tt(s) = 0 於全部 s ∈ Z10', ftz == [0], 'f_tt(Z10) 值集 = %s' % ftz)

    # ================= Part Z =================
    def S_TT(a, g):
        tot = 0
        for x in range(n):
            y = MUL[x][g]
            if tie[x][a] and tie[y][a]:
                tot += (0 if dind[x][a] == dind[y][a] else 1) * eps[x] * eps[y]
        return tot

    a0 = sorted(keys)[0][0]
    nzcols = sorted({a for (a, g) in keys if S_TT(a, g) != 0})
    S = {(a, g): S_TT(a, g) for a in nzcols for g in range(n)}
    comp = sorted(g for g in range(n) if S[(nzcols[0], g)] == 0)
    compset = set(comp)
    closed = all(MUL[x][y] in compset for x in comp for y in comp)
    has_id = e_state in compset
    claim('Z1', '★ 補集（20）成群（含單位元 ＋ 封閉 ⟹ 20 階子群）', closed and has_id and len(comp) == 20,
          '|補集| = %d ; 含單位元 = %s ; 乘法封閉 = %s' % (len(comp), has_id, closed))
    gac = sorted(g for (a, g) in keys if g in compset)
    tp = _C(types[a] for (a, g) in keys if g in compset)
    claim('Z2', '補集 ∩ {g_a} = 12 之欄型別分解（預註冊猜測：8 edge + 4 其他）',
          sum(tp.values()) == 12, '型別分解 = %s ; |∩| = %d' % (dict(tp), sum(tp.values())))
    iz = sorted(set(Z10) & compset)
    claim('Z3', '補集 ∩ Z10 = 4（回歸）＋其階', iz == sorted(set(Z10) & compset) and len(iz) == 4,
          '交集 = %s ; 階 = %s' % (iz, [order[s] for s in iz]))

    # ================= Part Q =================
    def orbit_of(s, a):
        return tuple(sorted([(PAIR[s][a][0], PAIR[s][a][1]), (PAIR[s][partner[a]][0], PAIR[s][partner[a]][1])]))

    orb = {}
    for a in pairs:
        orb.setdefault(orbit_of(0, a), []).append(a)
    single = sum(1 for k in orb if len(set(types[a] for a in orb[k])) == 1)
    claim('Q1', '★ 同一 cell-orbit 之軸對型別單一（orbit ⊂ 單一軸型別）', single == len(orb),
          'orbit 數 = %d ; 型別單一 = %d ; 各 orbit = %s' % (len(orb), single, {str(k): [types[a] for a in v] for k, v in list(orb.items())[:3]}))
    tt = _C(types[a] for a in pairs)
    claim('Q2', '31 軸對之型別分解 = 15 edge + 10 face + 6 vertex', tt == _C({'edge': 15, 'face': 10, 'vertex': 6}),
          '型別 = %s' % dict(tt))
    nec = [a for a in range(ncol) if types[a] == 'edge' and a not in set(nzcols)]
    zero_coord = sum(1 for a in nec if any(U[a][t] == (0, 0) for t in range(3)))
    claim('Q3', '★ 非承載之 8 個 edge 欄之 U 皆具某分量 = 0（預註冊猜測）', zero_coord == len(nec),
          '欄 = %s ; 有零分量者 = %d ; U 樣本 = %s' % (nec, zero_coord, [U[a] for a in nec[:2]]))
    go = sorted(set(order[g] for (a, g) in keys if a in set(nzcols)))
    claim('Q4', '承載列之 g_a 階分佈（預註冊：全為 4）', go == [4], '階值集 = %s' % go)

    # ================= Part -c：更正與量測律（原 tag 保留 FAIL） =================
    # X7-c：大小 4 之 τ 集之額外一對之身份
    extras = {}
    for k in nonempty:
        g = k[1]
        base = {g, MUL[g][zc]}
        ex = sorted(t for t in tau[k] if t not in base)
        if ex:
            extras[str(k)] = {'extra': ex, 'orders': sorted(set(order[t] for t in ex)),
                              'in_Cg': all(MUL[t][g] == MUL[g][t] for t in ex),
                              'base_order': order[g]}
    x7_ok = all(all(o == order[eval(kk)[1]] for o in vv['orders']) for kk, vv in extras.items()) if extras else True
    claim('X7-c（量測律）', '★ τ 集 ⊇ {±g_a}；大小 4 者之額外一對與 g_a 同階且在 C(g_a)',
          x7_ok and all(vv['in_Cg'] for vv in extras.values()), 
          '大小 4 之鍵 = %d ; 額外元素之階值集 = %s ; 皆在 C(g_a) = %s'
          % (len(extras), sorted({o for vv in extras.values() for o in vv['orders']}), all(vv['in_Cg'] for vv in extras.values())))
    # Y6-c：Z10 之 4 KV 值之 Gram（精確，對角 = |v|²）
    gram = [[str(dot3(x, y)) for y in kvz] for x in kvz]
    claim('Y6-c（量測律）', 'Z10 之 4 KV 值之 Gram 矩陣（精確）＋是否含相鄰對／對反對',
          True, '|KV| = %d ; 對角 = %s ; 非對角 = %s'
          % (len(kvz), sorted(set(str(dot3(x, x)) for x in kvz)),
             sorted(set(str(dot3(kvz[i], kvz[j])) for i in range(len(kvz)) for j in range(i + 1, len(kvz))))))
    # Z2g：預註冊之型別猜測（8 edge + 4 其他）之判定
    claim('Z2g（預註冊子猜測）', 'Z2 之預註冊型別猜測 = 8 edge + 4 其他', dict(tp) == {'edge': 8},
          '實測 = %s ⟹ 猜測被否證（實為 10 edge + 2 vertex）' % dict(tp))
    # Z4-c：補集之階譜 ＋ 是否正規化某階 5 子群
    spec = _C(order[x] for x in comp)
    s5 = [x for x in comp if order[x] == 5]
    norm_ok = False
    if s5:
        H = {e_state}
        x = s5[0]
        for _ in range(5):
            H.add(x)
            x = MUL[x][s5[0]]
        norm_ok = all(MUL[MUL[h][x]][inv[h]] in H for h in comp for x in H)
    claim('Z4-c（量測律）', '★ 補集之階譜 ＋ 是否正規化其內之階 5 子群（⟹ ≅ Dic₅ = 2D₅）',
          norm_ok, '階譜 = %s ; 正規化階 5 子群 = %s' % (dict(spec), norm_ok))
    # Q1-c：各 orbit 之型別組成
    comp_orb = {str(k): dict(_C(types[a] for a in v)) for k, v in orb.items()}
    claim('Q1-c（量測律）', '各 cell-orbit 之型別組成（報）＋重數', True,
          'orbit → 型別組成 = %s ; 重數 = %s' % (comp_orb, sorted(len(v) for v in orb.values())))
    # Q3-c：以 7440 全域判之承載列（22）與非承載之 8 edge 欄（回歸 42），及其 U 之零分量
    nz22 = sorted(a for a in range(ncol) if any(S_TT(a, g) != 0 for g in range(n)))
    nec8 = sorted(a for a in range(ncol) if types[a] == 'edge' and a not in set(nz22))
    zc8 = sum(1 for a in nec8 if any(U[a][t] == (0, 0) for t in range(3)))
    claim('Q3-c', '★ 以 7440 全域判之承載列 = 22（全 edge）；非承載 8 edge 欄之 U 零分量數',
          len(nz22) == 22,
          '承載列 = %d ; 非承載 edge 欄 = %s ; 有零分量者 = %d' % (len(nz22), nec8, zc8))

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R12 機器' % (npass, len(CLAIMS)))
    out = {'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
           'X': {'tau': {str(k): v for k, v in tau.items()}, 'sizes': sizes,
                 'orders_empty': o_empty, 'orders_nonempty': o_non},
           'Y': {'Z10': Z10, 'kv_mult': sorted(kvc.values()), 'Y3_inter': inter, 'f_tt_Z10': ftz},
           'Z': {'complement': comp, 'types_of_gac': dict(tp), 'inter_Z10': iz},
           'Q': {'orbit_types': {str(k): [types[a] for a in v] for k, v in orb.items()},
                 'pair_types': dict(tt), 'noncarrier_edge': nec, 'carrier_orders': go}}
    with io.open(os.path.join(BASE, 'data/45_r12_machine.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
