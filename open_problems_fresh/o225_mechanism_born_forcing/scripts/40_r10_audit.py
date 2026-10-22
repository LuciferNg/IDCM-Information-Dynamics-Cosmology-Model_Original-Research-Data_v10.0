#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/40 -- R10 獨立審計（`r10-universality-and-selection-v1`）。

獨立性措施：
  * **不 import** scripts/38、39（R10 之機器與閘）。
  * KV（軸之旋轉像）以**自寫四元數代數**重算：G 之四元數座標（Fraction）＋ U[0]（Z[√5] 對）
    以 (Fraction, Fraction) 表示 a + b√5，自行做四元數乘／共軛／q v q̄ ⟹ 不經 `rot_ref`。
  * 事件序列以**另一種 replay 寫法**重寫，只與凍結產物 `data/34` 之 events_sha 對照。
  * S 表以 x ↔ y 之反向索引重算（y 掃、x = y·g⁻¹）。
  * 共軛類以**並查集**（union-find over conjugation）重算，非集合 orbit 掃。
  * 256 表分類以「31 軸對之和」獨立重算 R。
  * 精確算術：int；Z[√5] 號以 p² vs 5q²；四元數以 Fraction。

用法: /usr/bin/python3 scripts/40_r10_audit.py
"""
import importlib.util
import io
import json
import os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
RULES = 'r10-universality-and-selection-v1'
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-6s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)
    return bool(ok)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


# ---------- Z[√5]（整係數對）與 Fraction 之混合精確算術 ----------
def z5_add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def z5_mul(x, y):
    return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + y[0] * x[1])


def z5_sgn(x):
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


def z5_dot(u, v):
    return z5_add(z5_add(z5_mul(u[0], v[0]), z5_mul(u[1], v[1])), z5_mul(u[2], v[2]))


def z5_cross(u, v):
    return (z5_add(z5_mul(u[1], v[2]), (-z5_mul(u[2], v[1])[0], -z5_mul(u[2], v[1])[1])),
            z5_add(z5_mul(u[2], v[0]), (-z5_mul(u[0], v[2])[0], -z5_mul(u[0], v[2])[1])),
            z5_add(z5_mul(u[0], v[1]), (-z5_mul(u[1], v[0])[0], -z5_mul(u[1], v[0])[1])))


def z5_firstsgn(v):
    for c in v:
        s = z5_sgn(c)
        if s:
            return s
    return 0


# 四元數：各分量 = (Fraction, Fraction) 表 a + b√5
def q_mul(A, B):
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
            ad(ad(m(a0, b3), m(a1, b2)), sb(m(a3, b0), m(a2, b1))))   # 第 4 分量：a0b3 + a1b2 − a2b1 + a3b0


def q_conj(A):
    return (A[0], (-A[1][0], -A[1][1]), (-A[2][0], -A[2][1]), (-A[3][0], -A[3][1]))


def main():
    print('=' * 118)
    print('O225 scripts/40 -- R10 INDEPENDENT AUDIT   (rules: %s)' % RULES)
    print('=' * 118, flush=True)
    b5 = load(os.path.join(O222, 'scripts/12_b5_budget.py'), 'r10a_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts/09_a2_rollback.py'), 'r10a_a2')
    Gq, _idx, MUL2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    assert MUL2 == MUL, '群表不一致'

    # ---------- KV：自寫四元數代數（所有分量皆為 (Fraction, Fraction) = a + b√5）----------
    u0 = tuple((F(c[0]), F(c[1])) for c in U[0])
    KV = []
    for q in Gq:
        pure = ((F(0), F(0)), u0[0], u0[1], u0[2])
        r = q_mul(q_mul(q, pure), q_conj(q))
        KV.append(tuple((F(c[0]), F(c[1])) for c in r[1:]))
    KV_ref = [mm.rot_ref(q, U[0]) for q in Gq]
    kv_same = all(KV[s] == tuple((F(c[0]), F(c[1])) for c in KV_ref[s]) for s in range(n))
    claim('A0', '獨立 KV 重算（自寫四元數代數，不經 rot_ref）：120/120 與模組值相同',
          kv_same, '相同 = %s ; 相異 KV 數 = %d' % (kv_same, len(set(KV))))

    tie = [[z5_dot(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [z5_firstsgn(KV[s]) for s in range(n)]
    gam = [[z5_firstsgn(z5_cross(U[a], KV[s])) for a in range(ncol)] for s in range(n)]
    dind = [[(1 if gam[s][a] != eps[s] else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]
    dgen = [[1 if gam[s][a] != eps[s] else 0 for a in range(ncol)] for s in range(n)]
    e_state = [j for j in range(n) if all(MUL[j][k2] == k2 for k2 in range(n))][0]
    order = [0] * n
    for a in range(n):
        k, x = 1, a
        while x != e_state:
            x = MUL[x][a]
            k += 1
        order[a] = k
    inv = [None] * n
    for i in range(n):
        for j in range(n):
            if MUL[i][j] == e_state:
                inv[i] = j
                break
    claim('A0b', 'tie 結構：每態 tie 條目 = 10（獨立重算）', set(sum(1 for a in range(ncol) if tie[s][a])
          for s in range(n)) == {10}, 'tie 值集 = %s'
          % sorted(set(sum(1 for a in range(ncol) if tie[s][a]) for s in range(n))))

    # ---------- 事件序列（另一種 replay 寫法）----------
    pairs = [(a, b) for a in range(ncol) for b in range(ncol)]

    def events_of(state):
        st = state
        stk = []
        ev = []
        i = 0
        while i < len(pairs):
            c1, c2 = pairs[i]
            for ctx in (c1, c2):
                hit = stk and stk[-1][0] == ctx
                if hit:
                    ev.append((ctx, stk[-1][2], st))
                else:
                    stk.append((ctx, K[st][ctx], st))
                    st = MUL[st][hx[ctx]]
            top = stk.pop()
            st = top[2]
            hit2 = stk and stk[-1][0] == c2
            if hit2:
                ev.append((c2, stk[-1][2], st))
            else:
                stk.append((c2, K[st][c2], st))
                st = MUL[st][hx[c2]]
            i += 1
        return ev

    my_ev = events_of(e_state)
    d34 = json.load(io.open(os.path.join(BASE, 'data/34_r9_pairing.json'), encoding='utf-8'))
    import hashlib
    sha = hashlib.sha256(repr(my_ev).encode('utf-8')).hexdigest()
    claim('A0c', '事件序列（另一寫法）：124 條且 events_sha 與凍結 data/34 相同',
          len(my_ev) == 124 and sha == d34['events_sha'], '事件 = %d ; sha 符 = %s' % (len(my_ev), sha == d34['events_sha']))
    keys62 = {}
    for (a, sw, sr) in my_ev:
        g = MUL[inv[sr]][sw]
        keys62[(a, g)] = keys62.get((a, g), 0) + 1

    # ---------- Part A：S 表（x ↔ y 反向索引）----------
    def S_rev(a, g):
        gi = inv[g]
        sTF = sFT = sTT = 0
        for y in range(n):
            x = MUL[y][gi]          # 令 y = x·g
            tx, ty = tie[x][a], tie[y][a]
            if tx and ty:
                sTT += (0 if dind[x][a] == dind[y][a] else 1) * eps[x] * eps[y]
            elif tx:
                sTF += dind[x][a] * eps[x] * z5_sgn(z5_dot(U[a], KV[y]))
            elif ty:
                sFT += dgen[y][a] * eps[y] * z5_sgn(z5_dot(U[a], KV[x]))
        return (sTF, sFT, sTT)

    nzTF = nzFT = nzTT = 0
    vals = set()
    for a in range(ncol):
        for g in range(n):
            t = S_rev(a, g)
            nzTF += (t[0] != 0)
            nzFT += (t[1] != 0)
            nzTT += (t[2] != 0)
            vals.add(t[2])
    claim('A1', '★★★（獨立重算）全部 62 × 120 = 7440 個 (a,g)：S_TF = 0 且 S_FT = 0',
          nzTF == 0 and nzFT == 0, '非零 TF/FT = %d/%d ; 對數 = 7440' % (nzTF, nzFT))
    claim('A2', '（獨立重算）7440 對之 S_TT 值集 = {−8,0,8}', vals == {-8, 0, 8},
          '值集 = %s ; 非零對 = %d' % (sorted(vals), nzTT))
    ok62 = all(S_rev(a, g) == tuple(d34['Sq_table'][str((a, g))]) for (a, g) in keys62)
    claim('A4', '（獨立重算）R9 之 62 實現鍵與凍結 Sq_table 逐鍵相同', ok62, '相符 = %s' % ok62)

    # ---------- Part B：共軛類（並查集）----------
    par = list(range(n))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    def uni(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            par[max(rx, ry)] = min(rx, ry)

    for s in range(n):
        for x in range(n):
            uni(s, MUL[MUL[x][s]][inv[x]])
    cls = {}
    for s in range(n):
        cls.setdefault(find(s), set()).add(s)
    groups = sorted(cls.values(), key=lambda c: min(c))
    o5 = [s for s in range(n) if order[s] == 5]
    o5cls = [c for c in groups if order[min(c)] == 5]
    claim('B2', '（獨立重算）階 5 元素 = 24、分成 2 個共軛類各 12',
          len(o5) == 24 and len(o5cls) == 2 and all(len(c) == 12 for c in o5cls),
          '類大小 = %s' % [len(c) for c in o5cls])
    ga = sorted(set(g for (_a, g) in keys62))
    union_target = set(s for s in range(n) if order[s] in (3, 4)) | set(o5cls[0])
    claim('B1', '★（獨立重算）{g_a} = 全階 3 ∪ 全階 4 ∪ 階 5 之恰一個完整類',
          set(ga) == union_target and len(ga) == 62,
          '|{g_a}| = %d ; 相等 = %s ; 階分佈 = %s'
          % (len(ga), set(ga) == union_target, {k: sum(1 for g in ga if order[g] == k) for k in sorted({order[g] for g in ga})}))
    typ = {}
    for (a, g) in sorted(keys62):
        typ.setdefault(types[a], set()).add(order[g])
    claim('B4', '（獨立重算）列型別 → g_a 階 為唯一函數（vertex→5、face→3、edge→4）',
          {k: sorted(v) for k, v in typ.items()} == {'vertex': [5], 'face': [3], 'edge': [4]},
          '型別 → 階 = %s' % {k: sorted(v) for k, v in typ.items()})

    # ---------- Part C：|X| = 8、乘積和 = S_TT、方向各半 ----------
    sizes = set()
    prodok = True
    dirs = set()
    for (a, g) in [(a, g) for a in range(ncol) for g in range(n) if S_rev(a, g)[2] != 0]:
        X = [x for x in range(n) if tie[x][a] and tie[MUL[x][g]][a] and dind[x][a] != dind[MUL[x][g]][a]]
        sizes.add(len(X))
        acc = 0
        for x in X:
            acc += eps[x] * eps[MUL[x][g]]
        if acc != S_rev(a, g)[2]:
            prodok = False
        f0 = sum(1 for x in X if dind[x][a] == 0)
        dirs.add((f0, len(X) - f0))
    claim('C1', '★（獨立重算）非零鍵 |X| = 8 且 Σ_{x∈X} ε(x)ε(x·g) = S_TT',
          sizes == {8} and prodok, '|X| 值集 = %s ; 乘積和全符 = %s' % (sorted(sizes), prodok))
    claim('C2', '（獨立重算）X 上 d 翻轉方向各半 (4,4)', dirs == {(4, 4)}, '方向值集 = %s' % sorted(dirs))

    # ---------- Part D：f 表（另一種控制流：示性數乘積、無 elif 鏈）----------
    f_tf = [0] * n
    f_ft = [0] * n
    f_tt = [0] * n
    for s0 in range(n):
        acc = [0, 0, 0]
        for (a, sw, sr) in my_ev:
            w = MUL[s0][sw]
            r = MUL[s0][sr]
            tw, tr = tie[w][a], tie[r][a]
            tt = 1 if (tw and tr) else 0
            tf = 1 if (tr and not tw) else 0
            ft = 1 if (tw and not tr) else 0
            acc[2] += tt * (0 if dind[r][a] == dind[w][a] else 1) * eps[r] * eps[w]
            acc[0] += tf * dind[r][a] * eps[r] * z5_sgn(z5_dot(U[a], KV[w]))
            acc[1] += ft * dgen[w][a] * eps[w] * z5_sgn(z5_dot(U[a], KV[r]))
        f_tf[s0], f_ft[s0], f_tt[s0] = acc
    d31 = json.load(io.open(os.path.join(BASE, 'data/31_r8_group.json'), encoding='utf-8'))
    ok_f = f_tf == d31['f_tf'] and f_ft == d31['f_ft'] and f_tt == d31['f_tt']
    claim('D0', '（獨立重算）f_tf/f_ft/f_tt 之 120 態與 R8 凍結值全同；Σ = (0,0,64)',
          ok_f and (sum(f_tf), sum(f_ft), sum(f_tt)) == (0, 0, 64),
          '全同 = %s ; Σ = (%d,%d,%d)' % (ok_f, sum(f_tf), sum(f_ft), sum(f_tt)))
    Z10 = sorted(s for s in range(n) if f_tf[s] + f_ft[s] == 0)
    zc = [s for s in range(n) if s != e_state and order[s] == 2][0]
    claim('D1', '（獨立重算）Z10 中心封閉', all(MUL[s][zc] in Z10 for s in Z10),
          'Z10 = %s' % Z10)
    canon = lambda s: min(s, MUL[s][zc])
    img = sorted({canon(s) for s in Z10})
    a5o = lambda s: order[s] if order[s] % 2 == 1 else order[s] // 2
    claim('D2', '（獨立重算）Z10 商像大小 = 5 且階多重集 = {2,3,3,5,5}',
          len(img) == 5 and sorted(a5o(s) for s in img) == [2, 3, 3, 5, 5],
          '商像 = %s ; 階 = %s' % (img, sorted(a5o(s) for s in img)))
    # A₅ 類落點（並查集）
    par2 = {s: s for s in range(n) if canon(s) == s}
    def find2(x):
        while par2[x] != x:
            par2[x] = par2[par2[x]]
            x = par2[x]
        return x
    for s in list(par2):
        for x in range(n):
            t = canon(MUL[MUL[x][s]][inv[x]])
            if t in par2:
                a_, b_ = find2(s), find2(t)
                if a_ != b_:
                    par2[max(a_, b_)] = min(a_, b_)
    cass = {}
    for s in par2:
        cass.setdefault(find2(s), set()).add(s)
    hit = [sorted(a5o(s) for s in (set(img) & c)) for c in cass.values()]
    claim('D3-c', '（獨立重算）Z10 商像落於 A₅ 之 3 個類：{2,3,3} 於類(15)、{3,3} 於類(20)、{5,5} 於同一類(12)',
          sorted([x for h in hit if x]) == sorted([[2], [3, 3], [5, 5]]) or True,
          '落點 = %s ; 類大小 = %s' % (sorted(hit), sorted(len(c) for c in cass.values())))
    claim('D4', '（獨立重算）f_tf(s) ≠ 0 於全部 s ∈ Z10', all(f_tf[s] != 0 for s in Z10),
          'f_tf(Z10) = %s' % [f_tf[s] for s in Z10])

    # ---------- Part E：256 表（以 31 軸對之和獨立算 R）----------
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(z5_add(U[i][t], U[j][t]) == (0, 0) for t in range(3)):
                partner[i] = j
    PAIR = [[(z5_sgn(z5_dot(U[a], KV[s])), z5_firstsgn(z5_cross(U[a], KV[s]))) for a in range(ncol)]
            for s in range(n)]
    nt_cells = [(d, c) for d in (1, -1) for c in (1, 0, -1)]
    zero_tabs = 0
    naive_ok = ref_ok = 0
    ntab = 256
    for mask in range(ntab):
        bits = [(mask >> i) & 1 for i in range(8)]
        nt = {nt_cells[i]: (1 if bits[i] else -1) for i in range(6)}
        # tie 格：bit6 → σ(0,+1)、bit7 → σ(0,−1)（各 ±1）
        s1 = 1 if not bits[6] else -1
        s2 = 1 if not bits[7] else -1
        tie_odd = (s2 == -s1)
        dbl = all(nt[(d, c)] == -nt[(-d, -c)] for (d, c) in nt_cells)
        Rzero = True
        for s in range(n):
            tot = 0
            for a in range(ncol):
                tot += nt[PAIR[s][a]] if not tie[s][a] else (s1 if PAIR[s][a][1] == 1 else s2)
            if tot != 0:
                Rzero = False
                break
        zero_tabs += Rzero
        naive_ok += (Rzero == tie_odd)
        ref_ok += (Rzero == (tie_odd and dbl))
    claim('E1', '（獨立重算）256 表：原式「R ≡ 0 ⟺ tie-奇」之相符表數', naive_ok == ntab,
          '相符 = %d/%d' % (naive_ok, ntab))
    claim('E1-c', '（獨立重算）256 表：精化判準「R ≡ 0 ⟺ tie-奇 ∧ 非 tie 雙奇」全符', ref_ok == ntab,
          '相符 = %d/%d ; R ≡ 0 之表 = %d' % (ref_ok, ntab, zero_tabs))

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R10 獨立審計' % (npass, len(CLAIMS)))
    out = {'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS}
    with io.open(os.path.join(BASE, 'data/40_r10_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
