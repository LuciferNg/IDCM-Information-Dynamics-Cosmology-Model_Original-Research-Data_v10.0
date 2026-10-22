#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/39 -- R10 機器：普遍性／選擇律／S_TT 結構／Z10 階律／非仿射族（`r10-universality-and-selection-v1`）。

Part A  逐鍵局部消失之普遍性：全部 62 × 120 = 7440 個 (a,g) 之 S 表
Part B  g_a 之選擇律（共軛類）
Part C  S_TT = ±8 之來源（|X| = 8、方向各半）
Part D  Z10 之階律（中心封閉、商像 5、A₅ 類落點、f_tf ≠ 0）
Part E  非仿射讀出族：**全部 64 個雙層布爾表**（非 tie 4 格 × tie 2 格）之 R 分類

精確算術（int；Z[√5] 以 p² vs 5q² 判號）；唯讀凍結機器（O222 `12_b5_budget.py`、`09_a2_rollback.py`）。
用法: /usr/bin/python3 scripts/39_r10_universal.py
"""
import hashlib
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
RULES = 'r10-universality-and-selection-v1'
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-6s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)
    return bool(ok)


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
    lhs, rhs = x[0] * x[0], 5 * x[1] * x[1]
    if lhs == rhs:
        return 0
    return (1 if lhs > rhs else -1) * (1 if x[0] > 0 else -1)


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
    print('O225 scripts/39 -- R10 MACHINE   (rules: %s)' % RULES)
    print('=' * 118, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'r10_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'r10_a2')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    KV = [mm.rot_ref(g, U[0]) for g in G]
    e_state = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))][0]
    inv = [None] * n
    for i in range(n):
        for j in range(n):
            if MUL[i][j] == e_state:
                inv[i] = j
                break
    order = [0] * n
    for a in range(n):
        k, x = 1, a
        while x != e_state:
            x = MUL[x][a]
            k += 1
        order[a] = k
    zc = [a for a in range(n) if a != e_state and order[a] == 2][0]

    tie = [[dot3(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [firstsgn(KV[s]) for s in range(n)]
    gam = [[firstsgn(cross3(U[a], KV[s])) for a in range(ncol)] for s in range(n)]
    dind = [[(1 if gam[s][a] != eps[s] else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]
    dgen = [[1 if gam[s][a] != eps[s] else 0 for a in range(ncol)] for s in range(n)]

    # ---- 事件序列（協定 replay，與 R9 凍結實作同式） ----
    pairs = [(a, b) for a in range(ncol) for b in range(ncol)]

    def events_of(state):
        st = state
        stk = []
        ev = []
        for (c1, c2) in pairs:
            for ctx in (c1, c2):
                if stk and stk[-1][0] == ctx:
                    ev.append((ctx, stk[-1][2], st))
                    continue
                stk.append((ctx, K[st][ctx], st))
                st = MUL[st][hx[ctx]]
            _c, _v, s_at = stk.pop()
            st = s_at
            if stk and stk[-1][0] == c2:
                ev.append((c2, stk[-1][2], st))
            else:
                stk.append((c2, K[st][c2], st))
                st = MUL[st][hx[c2]]
        return ev

    my_ev = events_of(e_state)
    keys = {}
    for (a, sw, sr) in my_ev:
        g = MUL[inv[sr]][sw]
        keys[(a, g)] = keys.get((a, g), 0) + 1
    d34 = json.load(io.open(os.path.join(BASE, 'data/34_r9_pairing.json'), encoding='utf-8'))
    info('事件數 = %d ; R9 實現鍵數 = %d ; 每鍵重數值集 = %s' % (len(my_ev), len(keys), sorted(set(keys.values()))))

    # ================= Part A 普遍性：全部 7440 (a,g) =================
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

    S = {}
    for a in range(ncol):
        for g in range(n):
            S[(a, g)] = S_of(a, g)
    nzTF = [k for k in S if S[k][0] != 0]
    nzFT = [k for k in S if S[k][1] != 0]
    claim('A1', '★★★ 普遍性（核心）：對全部 62 × 120 = 7440 個 (a,g) 對，S_TF = 0 且 S_FT = 0',
          not nzTF and not nzFT,
          '非零 TF = %d ; 非零 FT = %d ; 對數 = %d' % (len(nzTF), len(nzFT), len(S)))
    stt_all = sorted(set(S[k][2] for k in S))
    claim('A2', '全部 7440 對之 S_TT 值集 ⊆ {−8, 0, 8}',
          set(stt_all) <= {-8, 0, 8}, 'S_TT 值集 = %s' % stt_all)
    nzTT = [k for k in S if S[k][2] != 0]
    percol = {}
    for (a, g) in nzTT:
        percol[a] = percol.get(a, 0) + 1
    claim('A3', '非零 S_TT 對之計數與分佈（報告項）：總數與「每列非零 g 數」值集',
          True, '非零對 = %d ; 每列非零 g 數值集 = %s ; 承載列數 = %d'
          % (len(nzTT), sorted(set(percol.values())) if percol else [], len(percol)))
    sq_match = all(tuple(d34['Sq_table'][str(k)]) == S[k] for k in keys) and len(d34['Sq_table']) == len(keys)
    claim('A4', '回歸核：R9 之 62 個實現鍵之 S 值與凍結 data/34 之 Sq_table 逐鍵相同',
          sq_match, '凍結鍵 = %d ; 相符 = %s' % (len(d34['Sq_table']), sq_match))
    stt62 = sorted(set(S[k][2] for k in keys))
    info('A3 詳情：62 實現鍵之 S_TT 值集 = %s ; 7440 對之非零數 = %d（= 62 實現鍵中 12 個 × 重數 1 導致 n·S = ±16）'
         % (stt62, len(nzTT)))

    # ================= Part B g_a 之選擇律 =================
    ga_set = sorted(set(g for (_a, g) in keys))
    ord_sets = {}
    for g in range(n):
        ord_sets.setdefault(order[g], set()).add(g)
    # 共軛類
    def conj_class(s):
        return frozenset(MUL[MUL[x][s]][inv[x]] for x in range(n))

    cls_of = {s: conj_class(s) for s in range(n)}
    o5 = sorted(ord_sets[5])
    o5_classes = sorted({cls_of[g] for g in o5}, key=lambda c: min(c))
    claim('B2', '2I 之階 5 元素 24 個分成 2 個共軛類各 12',
          len(o5) == 24 and len(o5_classes) == 2 and all(len(c) == 12 for c in o5_classes),
          '階 5 元素 = %d ; 類數 = %d ; 類大小 = %s' % (len(o5), len(o5_classes), [len(c) for c in o5_classes]))
    o3, o4 = ord_sets[3], ord_sets[4]
    full_o5 = set().union(*o5_classes)
    hit = [i for i, c in enumerate(o5_classes) if c == set(ga_set) & c and (set(ga_set) & c == set(c))]
    one_class = [i for i, c in enumerate(o5_classes) if set(c) <= set(ga_set)]
    claim('B1', '★ {g_a}（62 個）= 全部階 3（20）∪ 全部階 4（30）∪ 階 5 之恰一個完整共軛類（12）',
          set(ga_set) == (set(o3) | set(o4) | (set(o5_classes[one_class[0]]) if len(one_class) == 1 else set()))
          and len(one_class) == 1 and len(ga_set) == 62,
          '|{g_a}| = %d ; 階分佈 = %s ; 命中完整階 5 類之數 = %d ; 類索引 = %s'
          % (len(ga_set), {k: sum(1 for g in ga_set if order[g] == k) for k in sorted({order[g] for g in ga_set})},
             len(one_class), one_class))
    a2g = sorted(keys)
    inject = len(set(g for (_a, g) in a2g)) == len(a2g) == 62
    typetab = {}
    for (a, g) in a2g:
        typetab.setdefault(types[a], {}).setdefault(order[g], []).append(a)
    claim('B3', 'a ↦ g_a 單射（62 個相異值）；列型別 × g_a 階之列聯表（報告項）',
          inject, '單射 = %s ; 型別×階 = %s'
          % (inject, {t: {k: len(v) for k, v in d.items()} for t, d in typetab.items()}))
    b4 = {t: sorted({order[g] for (a, g) in a2g if types[a] == t}) for t in sorted(set(types))}
    claim('B4', 'g_a 之階由列 axis 之型別唯一決定（階 3 ↔ vertex、4 ↔ face、5 ↔ edge 之假設）',
          all(len(v) == 1 for v in b4.values()), '型別 → 階值集 = %s' % b4)
    claim('B4-c', '【校正 tag】以量測之型別 × 階列聯表表述（原 B4 假設之判決見上）',
          True, '型別×階 = %s' % {t: {k: len(v) for k, v in d.items()} for t, d in typetab.items()})

    # ================= Part C S_TT = ±8 之來源 =================
    Xs = {}
    for (a, g) in nzTT:
        X = [x for x in range(n) if tie[x][a] and tie[MUL[x][g]][a] and dind[x][a] != dind[MUL[x][g]][a]]
        Xs[(a, g)] = X
    sizes = sorted(set(len(v) for v in Xs.values()))
    prodok = True
    for kk in Xs:
        acc = 0
        for xx in Xs[kk]:
            acc += eps[xx] * eps[MUL[xx][kk[1]]]
        if acc != S[kk][2]:
            prodok = False
            break
    claim('C1', '★ 非零鍵 (a,g)：|{x : tie(x,a) ∧ tie(x·g,a) ∧ d 翻轉}| = 8，且 Σ_{x∈X} ε(x)ε(x·g) = S_TT（= ±8）',
          sizes == [8] and prodok and all(abs(S[k][2]) == len(Xs[k]) for k in Xs),
          '|X| 值集 = %s ; 乘積和相符 = %s ; 鍵數 = %d' % (sizes, prodok, len(Xs)))
    dirs = {}
    for k in Xs:
        f0 = sum(1 for x in Xs[k] if dind[x][k[0]] == 0)
        dirs[k] = (f0, len(Xs[k]) - f0)
    dvals = sorted(set(dirs.values()))
    claim('C2', '於 X 上 d(x,a) = 0 → d(x·g,a) = 1 之數 = 4、反向 = 4（各半）',
          dvals == [(4, 4)], '方向分佈值集 = %s' % dvals)
    carriers_all_pos = sorted({k[0] for k in nzTT if S[k][2] > 0})
    carriers_all_neg = sorted({k[0] for k in nzTT if S[k][2] < 0})
    nz62 = [k for k in keys if S[k][2] != 0]
    carriers_pos = sorted(k[0] for k in nz62 if S[k][2] * keys[k] > 0)
    carriers_neg = sorted(k[0] for k in nz62 if S[k][2] * keys[k] < 0)
    sTT_t = sum(keys[k] * S[k][2] for k in keys if k in S)
    claim('C3', '回歸核（R9 之 62 實現鍵，重數 2）：承載列 +16 = {32,35,36,45,48,57,58,61}、−16 = {37,38,55,56}；Σ n·S_TT = 64',
          carriers_pos == [32, 35, 36, 45, 48, 57, 58, 61] and carriers_neg == [37, 38, 55, 56] and sTT_t == 64,
          '承載 + = %s ; − = %s ; Σ n·S_TT = %d ; （全 7440 表之承載 + = %d 欄、− = %d 欄，非 R9 之判據）'
          % (carriers_pos, carriers_neg, sTT_t, len(carriers_all_pos), len(carriers_all_neg)))

    # ================= Part D Z10 之階律 =================
    f_tf = [0] * n
    f_ft = [0] * n
    f_tt = [0] * n
    for s0 in range(n):
        for (a, sw, sr) in my_ev:
            w = MUL[s0][sw]
            r = MUL[s0][sr]
            tw, tr = tie[w][a], tie[r][a]
            if tw and tr:
                f_tt[s0] += (0 if dind[r][a] == dind[w][a] else 1) * eps[r] * eps[w]
            elif tr:
                f_tf[s0] += dind[r][a] * eps[r] * sgn(dot3(U[a], KV[w]))
            elif tw:
                f_ft[s0] += dgen[w][a] * eps[w] * sgn(dot3(U[a], KV[r]))
    d31 = json.load(io.open(os.path.join(BASE, 'data/31_r8_group.json'), encoding='utf-8'))
    Z10 = sorted(s for s in range(n) if f_tf[s] + f_ft[s] == 0)
    info('D 前置核：f 重建與 R8 凍結值全同 = %s ; Z10 = %s'
         % (f_tf == d31['f_tf'] and f_ft == d31['f_ft'] and f_tt == d31['f_tt'], Z10))
    clos = all(MUL[s][zc] in Z10 for s in Z10)
    claim('D1', 'Z10 中心封閉：s ∈ Z10 ⟹ s·(−1) ∈ Z10',
          clos, '閉合 = %s ; Z10 = %s' % (clos, Z10))
    canon = lambda s: min(s, MUL[s][zc])
    img = sorted({canon(s) for s in Z10})
    claim('D2', 'Z10 於商 2I/{±1} 之像大小 = 5', len(img) == 5, '商像 = %s' % img)
    # A₅ 階與類
    a5_order = lambda s: order[s] if order[s] % 2 == 1 else order[s] // 2
    a5_cls = {}
    for s in range(n):
        if canon(s) != s:
            continue
        a5_cls[s] = frozenset(canon(MUL[MUL[x][s]][inv[x]]) for x in range(n))
    classes = sorted({a5_cls[s] for s in a5_cls}, key=lambda c: min(c))
    img_orders = sorted(a5_order(s) for s in img)
    hit_cls = []
    for c in classes:
        if set(img) & set(c):
            hit_cls.append(sorted(a5_order(s) for s in (set(img) & set(c))))
    claim('D3', '★ Z10 之商像恰各屬 A₅ 之 5 個共軛類中之一（類代表橫截）',
          len(hit_cls) == 5 and all(len(x) == 1 for x in hit_cls),
          '商像階 = %s ; 命中類數 = %d ; 各類命中 = %s ; A₅ 類大小 = %s'
          % (img_orders, len(hit_cls), hit_cls, sorted(len(c) for c in classes)))
    claim('D3-c', '【校正 tag】以量測表述 Z10 商像之 A₅ 階多重集與類落點（原 D3 判決見上）',
          True, '商像階多重集 = %s ; 類落點（每類之階） = %s' % (img_orders, hit_cls))
    nz = [s for s in Z10 if f_tf[s] == 0]
    claim('D4', 'f_tf(s) ≠ 0 於全部 s ∈ Z10（Z10 非由 0+0 構成）', not nz,
          'f_tf = 0 之 Z10 元素 = %s' % nz)

    # ================= Part E 非仿射讀出族（全部 64 表）=================
    def R_of_table(Ktab):
        return sorted(set(sum(Ktab[s]) for s in range(n)))

    # 預計算 (s,a) 之讀出對（d, c）——一次性，避免 256 表重複 Z[√5] 運算
    PAIR = [[(sgn(dot3(U[a], KV[s])), firstsgn(cross3(U[a], KV[s]))) for a in range(ncol)] for s in range(n)]
    # 格子模型（8 格）：非 tie 6 格 (d, c)，d ∈ {±1}、c ∈ {−1,0,1}（c = 0 發生於 u ∥ r）；tie 2 格 (0, c)
    nt_cells = [(d, c) for d in (1, -1) for c in (1, 0, -1)]
    tables = []
    for mask in range(1 << 8):
        bits = [(mask >> i) & 1 for i in range(8)]
        nt = {nt_cells[i]: (1 if bits[i] else -1) for i in range(6)}
        tb = {1: 1, -1: -1} if not bits[6] else {1: 1, -1: 1}
        if bits[7]:
            tb = {k: -v for k, v in tb.items()}
        tables.append({'nt': nt, 'tie': tb, 'mask': mask})

    def double_odd(tb):
        nt = tb['nt']
        return all(nt[(d, c)] == -nt[(-d, -c)] for (d, c) in nt_cells)

    def tie_odd(tb):
        return tb['tie'][1] == -tb['tie'][-1]

    res = []
    for tb in tables:
        Kt = [[tb['nt'][PAIR[s][a]] if not tie[s][a] else tb['tie'][PAIR[s][a][1]]
               for a in range(ncol)] for s in range(n)]
        R = R_of_table(Kt)
        res.append({'double_odd': double_odd(tb), 'tie_odd': tie_odd(tb), 'R': R, 'tb': tb, 'zero': R == [0]})
    n_naive_ok = sum(1 for r in res if r['zero'] == r['tie_odd'])
    n_ref_ok = sum(1 for r in res if r['zero'] == (r['tie_odd'] and r['double_odd']))
    claim('E1', '★ 非仿射族上「R ≡ 0 ⟺ tie 規則 u-奇」（R1/R4 之充要式；256 表全枚舉）',
          n_naive_ok == len(res),
          '表數 = %d ; 原式相符 = %d ; 反例（tie-odd 但 R ≠ 0）= %d'
          % (len(res), n_naive_ok, sum(1 for r in res if r['tie_odd'] and not r['zero'])))
    claim('E1-c', '【校正 tag】精化判準：R ≡ 0 ⟺ tie u-奇 ∧ 非 tie 雙奇（σ(−d,−c) = −σ(d,c)）；256 表全符',
          n_ref_ok == len(res),
          '精化式相符 = %d/%d ; 反例 = %d'
          % (n_ref_ok, len(res), sum(1 for r in res if r['zero'] != (r['tie_odd'] and r['double_odd']))))
    sub = [r for r in res if r['double_odd'] and not r['tie_odd']]
    e2_bad = []
    for r in sub:
        tb = r['tb']
        for s in range(n):
            ntt = sum(1 for a in range(ncol) if tie[s][a]) // 2
            val = 0
            for a in range(ncol):
                if tie[s][a]:
                    val += tb['tie'][PAIR[s][a][1]]
                else:
                    val += tb['nt'][PAIR[s][a]]
            if abs(val) != 2 * ntt:
                e2_bad.append((r['tb']['mask'], s, val, ntt))
    claim('E2', '非 u-奇（而雙奇）之非仿射表：|R(s)| = 2·n_tie(s) 逐態成立',
          not e2_bad, '子族表數 = %d ; 違例 = %d %s' % (len(sub), len(e2_bad), e2_bad[:2]))
    claim('E3', '對照（報告項）：256 表之 R ≡ 0 數／R ≠ 0 數、值集種類，以及「雙奇 ∧ tie-奇」之表數',
          True, 'R ≡ 0 之表 = %d ; R ≠ 0 之表 = %d ; 雙奇表 = %d ; tie-奇表 = %d ; 值集種類 = %d'
          % (sum(1 for r in res if r['zero']), sum(1 for r in res if not r['zero']),
             sum(1 for r in res if r['double_odd']), sum(1 for r in res if r['tie_odd']),
             len({tuple(r['R']) for r in res})))
    info('E3 詳情：R 值集樣本 = %s' % sorted({tuple(r['R']) for r in res})[:5])

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R10 機器（普遍性／選擇律／S_TT／Z10／非仿射族）' % (npass, len(CLAIMS)))
    out = {'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
           'A': {'n_pairs': len(S), 'nonzero_TF': len(nzTF), 'nonzero_FT': len(nzFT),
                 'S_TT_valset': stt_all, 'nonzero_TT': len(nzTT),
                 'nonzero_TT_percol_valset': sorted(set(percol.values())) if percol else [],
                 'carriers_pos': carriers_pos, 'carriers_neg': carriers_neg},
           'B': {'n_ga': len(ga_set), 'order_hist': {str(k): sum(1 for g in ga_set if order[g] == k)
                                                     for k in sorted({order[g] for g in ga_set})},
                 'o5_classes': [sorted(c) for c in o5_classes], 'chosen_class': one_class,
                 'typetab': {t: {str(k): len(v) for k, v in d.items()} for t, d in typetab.items()}},
           'C': {'sizes': sizes, 'dirs': sorted(set(dirs.values()))},
           'D': {'Z10': Z10, 'img': img, 'img_orders': img_orders, 'class_hits': hit_cls,
                 'a5_class_sizes': sorted(len(c) for c in classes)},
           'E': {'n_tables': len(res), 'naive_ok': n_naive_ok, 'refined_ok': n_ref_ok,
                 'R_zero': sum(1 for r in res if r['zero']),
                 'double_odd_tables': sum(1 for r in res if r['double_odd']),
                 'tie_odd_tables': sum(1 for r in res if r['tie_odd']),
                 'counterexamples_naive': [r['tb']['mask'] for r in res if r['tie_odd'] and not r['zero']][:8],
                 'ghash': hashlib.sha256(repr(sorted(tuple(r['R']) for r in res)).encode()).hexdigest()}}
    with io.open(os.path.join(BASE, 'data/39_r10_universal.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
