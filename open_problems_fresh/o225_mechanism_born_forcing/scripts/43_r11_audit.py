#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/43 -- R11 獨立審計（**不 import** 41/42）。

獨立路徑：自寫四元數代數（Fraction 座標）算 KV；自寫事件 replay；自寫 T 項／S 表；自寫 orbit 分組；
另取 RNG 種子作 3 層族抽樣以獨立檢「反例存在」；並獨立重算 Z10／非零 g 集／承載列型別。
用法: /usr/bin/python3 scripts/43_r11_audit.py
"""
import hashlib
import importlib.util
import io
import json
import os
from collections import Counter
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
RULES = 'r11-mechanism-proof-and-laws-v1'
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


# ---- 自寫四元數代數：各分量 = (Fraction, Fraction) 表 a + b√5 ----
def qmul(A, B):
    a0, a1, a2, a3 = A
    b0, b1, b2, b3 = B

    def m(x, y):
        return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + y[0] * x[1])

    def ad(x, y):
        return (x[0] + y[0], x[1] + y[1])

    def sb(x, y):
        return (x[0] - y[0], x[1] - y[1])

    return (sb(sb(m(a0, b0), m(a1, b1)), ad(m(a2, b2), m(a3, b3))),
            ad(ad(m(a0, b1), m(a1, b0)), sb(m(a2, b3), m(a3, b2))),
            ad(sb(m(a0, b2), m(a1, b3)), ad(m(a2, b0), m(a3, b1))),
            ad(ad(m(a0, b3), m(a1, b2)), sb(m(a3, b0), m(a2, b1))))


def qconj(A):
    return (A[0], (-A[1][0], -A[1][1]), (-A[2][0], -A[2][1]), (-A[3][0], -A[3][1]))


def my_rot(q, v):
    Z = (F(0), F(0))
    V = (Z, (F(v[0][0]), F(v[0][1])), (F(v[1][0]), F(v[1][1])), (F(v[2][0]), F(v[2][1])))
    r = qmul(qmul(q, V), qconj(q))
    return ((r[1][0], r[1][1]), (r[2][0], r[2][1]), (r[3][0], r[3][1]))


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


def splitmix64(state):
    state = (state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    return state, z ^ (z >> 31)


def main():
    print('=' * 118)
    print('O225 scripts/43 -- R11 INDEPENDENT AUDIT   (rules: %s)' % RULES)
    print('=' * 118, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'a43_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'a43_a2')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    KVref = [mm.rot_ref(g, U[0]) for g in G]
    KV = [my_rot(g, U[0]) for g in G]
    same = sum(1 for s in range(n) if KV[s] == KVref[s])
    claim('A0', '獨立 KV（自寫四元數代數）與模組 rot_ref 相同 120/120', same == n, '相同 = %d/%d' % (same, n))
    ref42 = json.load(io.open(os.path.join(BASE, 'data/42_r11_machine.json'), encoding='utf-8'))
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
    dgen = [[1 if gam[s][a] != eps[s] else 0 for a in range(ncol)] for s in range(n)]
    PAIR = [[(sgn(dot3(U[a], KV[s])), firstsgn(cross3(U[a], KV[s]))) for a in range(ncol)] for s in range(n)]

    # ---- 軸對：以「獨立法」建（by 反極匹配）----
    pairs = []
    used = set()
    for i in range(ncol):
        if i in used:
            continue
        for j in range(ncol):
            if j != i and j not in used and all(U[i][t] == neg(U[j][t]) for t in range(3)):
                pairs.append((i, j))
                used.add(i)
                used.add(j)
                break
    claim('A1', '獨立重算軸對：31 對、覆蓋 62 欄', len(pairs) == 31 and len(used) == 62,
          '對數 = %d ; 覆蓋 = %d' % (len(pairs), len(used)))

    def orbit_ms(cells_of, s):
        cnt = Counter()
        for (i, j) in pairs:
            cnt[tuple(sorted([cells_of(s, i), cells_of(s, j)]))] += 1
        return sorted(cnt.values())

    c2 = [[sgn(cross3(U[a], KV[s])[1]) for a in range(ncol)] for s in range(n)]
    ms2 = orbit_ms(lambda s, a: PAIR[s][a], 0)
    ms3 = orbit_ms(lambda s, a: (PAIR[s][a][0], PAIR[s][a][1], c2[s][a]), 0)
    claim('A2', '獨立重算 orbit 重數：2 層 = [1,5,12,13]、3 層 = [1,2,3,5,10,10]',
          ms2 == [1, 5, 12, 13] and ms3 == [1, 2, 3, 5, 10, 10], '2 層 = %s ; 3 層 = %s' % (ms2, ms3))

    def antisym(Kt):
        return all(Kt[s][j] == -Kt[s][i] for s in range(n) for (i, j) in pairs)

    # ---- A3：3 層族（另取種子）之反例存在性 ----
    cells3 = [(d, c, cc) for d in (1, -1) for c in (1, 0, -1) for cc in (1, 0, -1)]
    seed = 777000111
    r0_noasym = 0
    ident_ok = 0
    tot = 400
    for m in range(tot):
        seed, r = splitmix64(seed)
        x = r
        bits = []
        for i in range(20):
            bits.append((x >> (i % 64)) & 1)
            if i % 64 == 63:
                seed, r = splitmix64(seed)
                x = r
        nt = {cells3[i]: (1 if bits[i] else -1) for i in range(18)}
        s1 = 1 if bits[18] else -1
        s2 = 1 if bits[19] else -1
        Kt = [[nt[(PAIR[s][a][0], PAIR[s][a][1], c2[s][a])] if not tie[s][a]
               else (s1 if PAIR[s][a][1] == 1 else s2) for a in range(ncol)] for s in range(n)]
        good = True
        for s in range(n):
            cnt = Counter()
            val = {}
            for (i, j) in pairs:
                k = tuple(sorted([(PAIR[s][i][0], PAIR[s][i][1], c2[s][i]),
                                  (PAIR[s][j][0], PAIR[s][j][1], c2[s][j])]))
                cnt[k] += 1
                val[k] = Kt[s][i] + Kt[s][j]
            if sum(Kt[s]) != sum(cnt[k] * val[k] for k in cnt):
                good = False
        ident_ok += good
        if all(sum(Kt[s]) == 0 for s in range(n)) and not antisym(Kt):
            r0_noasym += 1
    claim('A3', '獨立抽樣（另種子 400 表）：恆等式 400/400；反例數目報出（反例罕見，存在性另證）',
          ident_ok == tot, '恆等 = %d/%d ; 另種子之反例 = %d' % (ident_ok, tot, r0_noasym))
    # A3b：顯式重現（同種子 mask 452）並獨立驗其「R ≡ 0 而逐對反號不成立」＋報 s*
    seed = 20261001
    Kt452 = None
    for m in range(453):
        seed, r = splitmix64(seed)
        x = r
        bits = []
        for i in range(20):
            bits.append((x >> (i % 64)) & 1)
            if i % 64 == 63:
                seed, r = splitmix64(seed)
                x = r
        if m == 452:
            nt = {cells3[i]: (1 if bits[i] else -1) for i in range(18)}
            s1 = 1 if bits[18] else -1
            s2 = 1 if bits[19] else -1
            Kt452 = [[nt[(PAIR[s][a][0], PAIR[s][a][1], c2[s][a])] if not tie[s][a]
                      else (s1 if PAIR[s][a][1] == 1 else s2) for a in range(ncol)] for s in range(n)]
    Rz452 = all(sum(Kt452[s]) == 0 for s in range(n))
    sstar = next(s for s in range(n) if any(Kt452[s][j] != -Kt452[s][i] for (i, j) in pairs))
    cnt = Counter()
    val = {}
    for (i, j) in pairs:
        k = tuple(sorted([(PAIR[sstar][i][0], PAIR[sstar][i][1], c2[sstar][i]),
                          (PAIR[sstar][j][0], PAIR[sstar][j][1], c2[sstar][j])]))
        cnt[k] += 1
        val[k] = Kt452[sstar][i] + Kt452[sstar][j]
    claim('A3b', '★ 顯式重現 42 之 T1-⟺ 反例（種子 20261001、mask 452）：R ≡ 0 而逐對反號不成立',
          Rz452 and not antisym(Kt452), 'R ≡ 0 = %s ; 逐對反號 = %s ; 首個違反之 s* = %d ; s* 之 orbit 重數 = %s ; v 值 = %s'
          % (Rz452, antisym(Kt452), sstar, sorted(cnt.values()), sorted(val.values())))

    # ---- A4：S 表（7440）獨立重算 + 62 鍵回歸 + 16/46 分割 ----
    def S_of(a, g):
        sTF = sFT = sTT = 0
        for x in range(n):
            y = MUL[x][g]
            tx, ty = tie[x][a], tie[y][a]
            if tx and ty:
                sTT += (0 if dind[x][a] == dind[y][a] else 1) * eps[x] * eps[y]
            elif tx:
                sTF += dind[x][a] * eps[x] * sgn(dot3(U[a], KV[y]))
            elif ty:
                sFT += dgen[y][a] * eps[y] * sgn(dot3(U[a], KV[x]))
        return (sTF, sFT, sTT)

    # 事件（自寫 replay：與 40 相同之另一寫法）
    def events_of(state):
        st = state
        stk = []
        ev = []
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

    evs = events_of(e_state)
    d34 = json.load(io.open(os.path.join(BASE, 'data/34_r9_pairing.json'), encoding='utf-8'))
    sha_ok = hashlib.sha256(repr(evs).encode()).hexdigest() == d34['events_sha']
    keys = {}
    for (a, sw, sr) in evs:
        g = MUL[inv[sr]][sw]
        keys[(a, g)] = keys.get((a, g), 0) + 1
    S = {(a, g): S_of(a, g) for (a, g) in keys}
    SFULL = {(a, g): S_of(a, g) for a in range(ncol) for g in range(n)}
    reg = all(tuple(d34['Sq_table'][str(k)]) == S[k] for k in keys)
    Sall_TF0 = all(v[0] == 0 for v in SFULL.values())
    claim('A4', '★ 獨立：事件 sha 相符、62 鍵 S 值與凍結相同、且全域 7440 對之 S_TF = 0',
          sha_ok and reg and Sall_TF0, 'events_sha = %s ; 62 鍵回歸 = %s ; 7440 之 S_TF ≡ 0 = %s'
          % (sha_ok, reg, Sall_TF0))

    def Tterm(x, a, g):
        y = MUL[x][g]
        if tie[x][a] and not tie[y][a]:
            return dind[x][a] * eps[x] * sgn(dot3(U[a], KV[y]))
        return 0

    Tx = {k: [Tterm(x, k[0], k[1]) for x in range(n)] for k in sorted(keys)}
    empty = [k for k in Tx if all(v == 0 for v in Tx[k])]
    nonempty = [k for k in Tx if any(v != 0 for v in Tx[k])]
    claim('A5', '獨立分割：空 TF 集之實現鍵 = 46、非空 = 16（原 U1 之 46 個 vacuous）',
          len(empty) == 46 and len(nonempty) == 16, '空 = %d ; 非空 = %d' % (len(empty), len(nonempty)))
    leftok = 0
    hit = []
    for k in nonempty:
        T = Tx[k]
        tfset = set(x for x in range(n) if T[x] != 0)
        for tau in range(n):
            ok = True
            for x in range(n):
                xr = MUL[tau][x]
                if (xr in tfset) != (x in tfset) or (T[xr] != -T[x] if x in tfset else T[xr] != 0):
                    ok = False
                    break
            if ok:
                leftok += 1
                hit.append(sum(1 for t2 in range(n) if all(
                    (((MUL[t2][x] in tfset) == (x in tfset)) and
                     (T[MUL[t2][x]] == (-T[x] if x in tfset else 0))) for x in range(n))))
                break
    claim('A6', '★ 獨立：16 個非空鍵皆有**左乘**反號對合 τ（原 U1 之右乘形式不成立）',
          leftok == 16, '有解 = %d/16 ; 每鍵 τ 命中數 = %s（獨立重算）' % (leftok, sorted(set(hit))))

    # ---- A7：Z10（獨立 f 計算 + 反演/ KV 結構）----
    f_tf = [0] * n
    f_ft = [0] * n
    f_tt = [0] * n
    for s0 in range(n):
        for (a, sw, sr) in evs:
            w = MUL[s0][sw]
            r2 = MUL[s0][sr]
            tw, tr = tie[w][a], tie[r2][a]
            if tw and tr:
                f_tt[s0] += (0 if dind[r2][a] == dind[w][a] else 1) * eps[r2] * eps[w]
            elif tr:
                f_tf[s0] += dind[r2][a] * eps[r2] * sgn(dot3(U[a], KV[w]))
            elif tw:
                f_ft[s0] += dgen[w][a] * eps[w] * sgn(dot3(U[a], KV[r2]))
    Z10 = [s for s in range(n) if f_tf[s] + f_ft[s] == 0]
    kvz = Counter(KV[s] for s in Z10)
    viol = [s for s in Z10 if inv[s] not in Z10]
    kept = [s for s in Z10 if inv[s] in Z10]
    claim('A7', '獨立 Z10：|KV(Z10)| = 4、重數多重集 = {2,2,2,4}、反演違例 8、保持 [57,67]',
          len(kvz) == 4 and sorted(kvz.values()) == [2, 2, 2, 4] and len(viol) == 8 and kept == [57, 67],
          'Z10 = %s ; |KV| = %d ; 重數 = %s ; 違例 = %d ; 保持 = %s'
          % (Z10, len(kvz), sorted(kvz.values()), len(viol), kept))

    # ---- A8：S_TT 承載列 / 非零 g 集 / 補集 ----
    nz_cols = sorted({a for (a, g) in SFULL if SFULL[(a, g)][2] != 0})
    compsets = [frozenset(g for g in range(n) if SFULL[(a, g)][2] == 0) for a in nz_cols]
    comp = sorted(compsets[0])
    tps = Counter(types[a] for a in nz_cols)
    nz62 = [k for k in keys if S[k][2] != 0]
    pos = sorted(k[0] for k in nz62 if S[k][2] * keys[k] > 0)
    negc = sorted(k[0] for k in nz62 if S[k][2] * keys[k] < 0)
    claim('A8', '★ 獨立 S_TT 結構：22 承載列全屬 edge、補集（20）與欄無關、±16 之 12 列全屬 edge',
          len(nz_cols) == 22 and tps == Counter({'edge': 22}) and len(set(compsets)) == 1
          and len(comp) == 20 and all(types[a] == 'edge' for a in pos + negc) and len(pos) == 8 and len(negc) == 4,
          '承載列 = %d（型別 %s）; 補集欄無關 = %s ; 補集 = %s ; +8 = %s ; −4 = %s'
          % (len(nz_cols), dict(tps), len(set(compsets)) == 1, comp, pos, negc))

    # ---- A9：與 42 之 JSON 逐項一致 ----
    j = ref42
    v42 = {'nz_cols': j['W']['nz_cols'], 'pos': j['W']['pos'], 'neg': j['W']['neg'], 'Z10': j['V']['Z10'],
           'kv': j['V']['kv'], 'eps_plus': j['V']['eps_plus']}
    ok = (v42['nz_cols'] == nz_cols and v42['pos'] == pos and v42['neg'] == negc and v42['Z10'] == Z10
          and v42['kv'] == len(kvz) and v42['eps_plus'] == sum(1 for s in Z10 if eps[s] == 1))
    claim('A9', '與 scripts/42 之 JSON 逐項一致（承載列、±列、Z10、|KV|、ε 計數）', ok,
          '42: 承載 %d/±%d/%d/Z10 %d/|KV| %d/ε+ %d' % (len(v42['nz_cols']), len(v42['pos']), len(v42['neg']),
                                                      len(v42['Z10']), v42['kv'], v42['eps_plus']))
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R11 獨立審計' % (npass, len(CLAIMS)))
    out = {'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
           'independent': {'pairs': [list(p) for p in pairs], 'ms2': ms2, 'ms3': ms3,
                           'r0_noasym_3layer_other_seed': r0_noasym, 'empty_keys': len(empty),
                           'nonempty_keys': len(nonempty), 'complement_20': comp,
                           'Z10': Z10, 'kv_mult': sorted(kvz.values())}}
    with io.open(os.path.join(BASE, 'data/43_r11_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
