#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/85 -- R24 審計（`r24-two-term-family-v1`）

紀律：**不 import 本 o 任何推導 script**（含 84）；只載凍結 O222 機器（唯讀）並以**另路實作**重算。
A1 P2 恆等式之另路重算（原始叉積 A_0 vs −(T_0+T_1)/u_2；另名 Z[√5] helper）
A2 P5 之另路重算（12 非座標線之 dind 位恆定欄）
A3 Q1／Q2-c 之另路重算（head 路線零集 = 44；與凍結零集 Z10 之交集 = 8）
A4 ★★ MECH-2 定讞：逐事件（a,sw,sr）× 逐態 s0：`f_tf` 加項 ≡ head 形式於 **x = MUL[s0][sr]**（0 反例）；
   而 head 之 `Tterm(s0,a,g)`（x = s0）之差異（(欄,態) 數 > 0）⟹ 不等價之確切位置 = 評估態之選擇。
用法: /usr/bin/python3 scripts/85_r24_audit.py
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
RULES = 'r24-two-term-family-v1'
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


def info(s):
    print('[INFO] ' + s, flush=True)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


# ---- 另名 Z[√5] 代數（獨立實作；不用 84 之名） ----
def zadd(x, y):
    return (x[0] + y[0], x[1] + y[1])


def zneg(x):
    return (-x[0], -x[1])


def zmul(x, y):
    a, b = x
    c, d = y
    return (a * c + 5 * b * d, a * d + b * c)


def zsq(x):
    return zmul(x, x)


def zsgn(x):
    p, q = x
    if p == 0 and q == 0:
        return 0
    if p == 0:
        return (1 if q > 0 else -1)
    if q == 0:
        return (1 if p > 0 else -1)
    if p < 0 and q < 0:
        return -1
    if p > 0 and q > 0:
        return 1
    if p * p == 5 * q * q:
        return 0
    big = (p * p > 5 * q * q)
    return (1 if big else -1) * (1 if p > 0 else (-1 if p < 0 else (1 if q > 0 else -1)))


def zz(u, v):
    return zadd(zadd(zmul(u[0], v[0]), zmul(u[1], v[1])), zmul(u[2], v[2]))


def x3(u, v):
    return (zadd(zmul(u[1], v[2]), zneg(zmul(u[2], v[1]))),
            zadd(zmul(u[2], v[0]), zneg(zmul(u[0], v[2]))),
            zadd(zmul(u[0], v[1]), zneg(zmul(u[1], v[0]))))


def fs(v):
    for c in v:
        s = zsgn(c)
        if s:
            return s
    return 0


def fidx(v):
    for k in range(3):
        if zsgn(v[k]):
            return k
    return -1


def main():
    print('=' * 118)
    print('O225 scripts/85 -- R24 AUDIT   (rules: %s)' % RULES)
    print('=' * 118, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'a24_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'a24_a2')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    KV = [mm.rot_ref(g, U[0]) for g in G]
    e_state = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))][0]
    inv = [next(j for j in range(n) if MUL[i][j] == e_state) for i in range(n)]
    tie = [[zz(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [fs(KV[s]) for s in range(n)]
    dind = [[(1 if fs(x3(U[a], KV[s])) != eps[s] else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]

    def ev_of(state):
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

    my_ev = ev_of(e_state)
    d34 = json.load(io.open(os.path.join(BASE, 'data/34_r9_pairing.json'), encoding='utf-8'))
    info('事件 %d 條；sha 相符 = %s；鍵數 = %d'
         % (len(my_ev), hashlib.sha256(repr(my_ev).encode()).hexdigest() == d34['events_sha'],
            len(set((a, MUL[inv[sr]][sw]) for (a, sw, sr) in my_ev))))

    # ---------- A1：P2 恆等式之另路重算 ----------
    bad1 = []
    for L in (41, 42):
        u = U[L]
        for x in sorted(set(KV[s] for s in range(n) if tie[s][L])):
            A0 = x3(u, x)[0]
            T0 = zmul(zmul(u[0], u[1]), x[0])
            T1 = zmul(zadd(zsq(u[1]), zsq(u[2])), x[1])
            lhs = zadd(T0, T1)
            rhs = zneg(zmul(u[2], A0))
            if lhs != rhs:
                bad1.append((L, str(x), str(lhs), str(rhs)))
    claim('A1', '★★（另路）P2：T_0 + T_1 = −u_2·A_0（Z[√5] 元素相等；以原始叉積與獨立 helper 重算）',
          bad1 == [], '反例 = %s' % bad1)

    # ---------- A2：P5 之另路重算 ----------
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(zadd(U[i][t], U[j][t]) == (0, 0) for t in range(3)):
                partner[i] = j
    lines = sorted(i for i in range(ncol) if i < partner[i])
    ncl = [L for L in lines if all(U[L][t] != (0, 0) for t in range(3))]
    A2rows = []
    for L in ncl:
        u = U[L]
        bits = sorted(set((1 if zsgn(x3(u, x)[0]) * zsgn(x[fidx(x)]) == -1 else 0)
                          for x in sorted(set(KV[s] for s in range(n) if tie[s][L])) if fs(x) != 0))
        A2rows.append((L, bits))
    const = sorted(r[0] for r in A2rows if len(r[1]) == 1)
    claim('A2', '★★（另路）P5：12 非座標線上 dind 位恆定之欄 = {39,40,41,42}',
          const == [39, 40, 41, 42], '恆定欄 = %s ; 逐線 = %s' % (const, A2rows))

    # ---------- A3：Q1／Q2-c 之另路重算 ----------
    def head_term(x, a, g):
        y = MUL[x][g]
        if tie[x][a] and not tie[y][a]:
            return dind[x][a] * eps[x] * zsgn(zz(U[a], KV[y]))
        return 0

    keys = {}
    for (a, sw, sr) in my_ev:
        g = MUL[inv[sr]][sw]
        keys[(a, g)] = keys.get((a, g), 0) + 1
    Hk = sorted(s0 for s0 in range(n)
                if sum(keys[(a, g)] * head_term(s0, a, g) for (a, g) in keys) == 0)
    f_tf, f_ft = [0] * n, [0] * n
    for s0 in range(n):
        for (a, sw, sr) in my_ev:
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            if tie[r2][a] and not tie[w][a]:
                f_tf[s0] += dind[r2][a] * eps[r2] * zsgn(zz(U[a], KV[w]))
            elif tie[w][a] and not tie[r2][a]:
                f_ft[s0] += dind[w][a] * eps[w] * zsgn(zz(U[a], KV[r2]))
    Zf = sorted(s0 for s0 in range(n) if f_tf[s0] + f_ft[s0] == 0)
    claim('A3', '★★（另路）Q1／Q2-c：head 路線零集 = 44 態；與凍結路線零集（10 態）之交集 = 8',
          len(Hk) == 44 and len(Zf) == 10 and len(set(Hk) & set(Zf)) == 8,
          '|Hk| = %d ; |Zf| = %d ; 交 = %d' % (len(Hk), len(Zf), len(set(Hk) & set(Zf))))

    # ---------- A4：★★ MECH-2 定讞（評估態之選擇） ----------
    mis_align, ok_align = [], 0
    for (a, sw, sr) in my_ev:
        g = MUL[inv[sr]][sw]
        for s0 in range(n):
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            frz = dind[r2][a] * eps[r2] * zsgn(zz(U[a], KV[w])) if (tie[r2][a] and not tie[w][a]) else 0
            hd_at_r = head_term(r2, a, g)
            if frz != hd_at_r:
                mis_align.append((a, sw, sr, s0, frz, hd_at_r))
            else:
                ok_align += 1
    diff_head = sum(1 for s0 in range(n) for (a, g) in keys
                    if head_term(s0, a, g) * keys[(a, g)] !=
                    sum((dind[MUL[s0][sr]][a] * eps[MUL[s0][sr]] * zsgn(zz(U[a], KV[MUL[s0][sw]]))
                         if (tie[MUL[s0][sr]][a] and not tie[MUL[s0][sw]][a]) else 0)
                        for (a2, sw, sr) in my_ev if a2 == a and MUL[inv[sr]][sw] == g))
    claim('A4', '★★（定讞·MECH-2）f_tf 加項 ≡ head 形式於 **x = MUL[s0][sr]**（逐事件逐態 0 反例）；'
                '而 head 於 x = s0 之聚合列與凍結列之差異（欄,態）數 = %d > 0 ⟹ 不等價之確切位置 = **評估態之選擇**（`(x,g)` 定向丟失 `sr`）'
          % diff_head, mis_align == [] and diff_head > 0,
          '對齊反例 = %d（逐事件×逐態 = %d 項相符）; 聚合差異（欄,態）數 = %d ; 首 4 反例 = %s'
          % (len(mis_align), ok_align, diff_head, mis_align[:4]))

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R24 審計' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data/85_r24_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'A2': A2rows, 'Hk': Hk, 'Zf': Zf, 'align_ok': ok_align, 'align_bad': mis_align[:20],
                   'aggregate_diff': diff_head}, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
