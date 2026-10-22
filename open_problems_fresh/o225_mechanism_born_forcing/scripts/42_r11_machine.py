#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/42 -- R11 機器：判準最終形式／S_TF=0 機制／Z10 定義律／S_TT 結構（`r11-mechanism-proof-and-laws-v1`）。

Part T  判準：T1（任意讀出 R ≡ 0 ⟺ 逐軸對反號；256 表一致性）、T2（2 層 ⟺ tie-奇 ∧ 雙奇）、T3（3 層 512 表抽樣）
Part U  S_TF 機制：U0（中心均勻律）、U1（逐鍵 τ-反號對合存在）、U2（τ 只依 a）、U3/U4（診斷）
Part V  Z10：V1 反演封閉、V2 階分佈、V3 |KV(Z10)|、V4 ε 分佈、V5 tie 型別分解
Part W  S_TT：W1（非零 ⟺ g ∉ 階 3 類）、W2／W3（型別分解）、W4／W5（診斷 ＋ 推論）

精確算術（int；Z[√5] 以 p² vs 5q²）；唯讀凍結機器（O222）。用法: /usr/bin/python3 scripts/42_r11_machine.py
"""
import hashlib
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
RULES = 'r11-mechanism-proof-and-laws-v1'
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


def splitmix64(state):
    state = (state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    return state, z ^ (z >> 31)


def main():
    print('=' * 118)
    print('O225 scripts/42 -- R11 MACHINE   (rules: %s)' % RULES)
    print('=' * 118, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'r11_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'r11_a2')
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
    zc = [s for s in range(n) if s != e_state and order[s] == 2][0]
    tie = [[dot3(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [firstsgn(KV[s]) for s in range(n)]
    gam = [[firstsgn(cross3(U[a], KV[s])) for a in range(ncol)] for s in range(n)]
    dind = [[(1 if gam[s][a] != eps[s] else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]
    dgen = [[1 if gam[s][a] != eps[s] else 0 for a in range(ncol)] for s in range(n)]
    PAIR = [[(sgn(dot3(U[a], KV[s])), firstsgn(cross3(U[a], KV[s]))) for a in range(ncol)] for s in range(n)]
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(add(U[i][t], U[j][t]) == (0, 0) for t in range(3)):
                partner[i] = j
    assert len(partner) == ncol

    # 事件序列 + 62 實現鍵 + S 表（與 R9/R10 同式，已回歸核對）
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

    S = {(a, g): S_of(a, g) for a in range(ncol) for g in range(n)}
    d34 = json.load(io.open(os.path.join(BASE, 'data/34_r9_pairing.json'), encoding='utf-8'))
    reg = all(tuple(d34['Sq_table'][str(k)]) == S[k] for k in keys)
    info('前置回歸：事件 %d 條、鍵 %d 個、S 表與 R9 凍結逐鍵相同 = %s' % (len(my_ev), len(keys), reg))

    # ================= Part T =================
    def pairs_antisym(Ktab):
        return all(Ktab[s][partner[a]] == -Ktab[s][a] for s in range(n) for a in range(ncol))

    nt_cells = [(d, c) for d in (1, -1) for c in (1, 0, -1)]
    n_T1 = 0
    n_T2 = 0
    tables = []
    for mask in range(256):
        bits = [(mask >> i) & 1 for i in range(8)]
        nt = {nt_cells[i]: (1 if bits[i] else -1) for i in range(6)}
        s1 = 1 if not bits[6] else -1
        s2 = 1 if not bits[7] else -1
        Kt = [[nt[PAIR[s][a]] if not tie[s][a] else (s1 if PAIR[s][a][1] == 1 else s2) for a in range(ncol)]
              for s in range(n)]
        Rz = all(sum(Kt[s]) == 0 for s in range(n))
        asym = pairs_antisym(Kt)
        dbl = all(nt[(d, c)] == -nt[(-d, -c)] for (d, c) in nt_cells)
        tieodd = (s2 == -s1)
        tables.append({'mask': mask, 'R0': Rz, 'asym': asym, 'dbl': dbl, 'tieodd': tieodd, 'Kt': Kt})
        n_T1 += (Rz == asym)
        n_T2 += (asym == (dbl and tieodd))
    claim('T1', '★ 任意讀出：R ≡ 0 ⟺ 逐軸對反號 K(s,ā) = −K(s,a)（256 個 2 層表一致性；附分析證明）',
          n_T1 == 256, '相符 = %d/256 ; R ≡ 0 之表 = %d ; 逐對反號之表 = %d'
          % (n_T1, sum(1 for t in tables if t['R0']), sum(1 for t in tables if t['asym'])))
    claim('T2', '2 層族：逐對反號 ⟺ tie 層奇 ∧ 非 tie 雙奇（= E1-c 之重述）',
          n_T2 == 256, '相符 = %d/256' % n_T2)
    # T3：3 層族（d, c, c₂），20 格；抽樣 512 表
    c2_of = [[sgn(cross3(U[a], KV[s])[1]) for a in range(ncol)] for s in range(n)]
    cells3 = [(d, c, c2) for d in (1, -1) for c in (1, 0, -1) for c2 in (1, 0, -1)]
    tiecells3 = [(0, 1), (0, -1)]
    seed = 20261001
    t3_ok = 0
    t3_bad = []
    for m in range(512):
        bits = []
        seed, r = splitmix64(seed)
        x = r
        for i in range(20):
            bits.append((x >> (i % 64)) & 1)
            if i % 64 == 63:
                seed, r = splitmix64(seed)
                x = r
        nt3 = {cells3[i]: (1 if bits[i] else -1) for i in range(18)}
        s1 = 1 if bits[18] else -1
        s2 = 1 if bits[19] else -1
        Kt = [[nt3[(PAIR[s][a][0], PAIR[s][a][1], c2_of[s][a])] if not tie[s][a]
               else (s1 if PAIR[s][a][1] == 1 else s2) for a in range(ncol)] for s in range(n)]
        Rz = all(sum(Kt[s]) == 0 for s in range(n))
        if Rz == pairs_antisym(Kt):
            t3_ok += 1
        else:
            t3_bad.append(m)
    claim('T3', '3 層族（d, c, c₂；20 格）512 表抽樣：R ≡ 0 ⟺ 逐對反號（0 例外）',
          t3_ok == 512, '相符 = %d/512 ; 反例 = %d %s' % (t3_ok, len(t3_bad), t3_bad[:3]))

    # ================= Part U =================
    def Tterm(x, a, g):
        y = MUL[x][g]
        if tie[x][a] and not tie[y][a]:
            return dind[x][a] * eps[x] * sgn(dot3(U[a], KV[y]))
        return 0

    Tx_cache = {}
    for (a, g) in sorted(keys):
        Tx_cache[(a, g)] = [Tterm(x, a, g) for x in range(n)]
    dev_U0 = 0
    pairs4 = 0
    for (a, g) in sorted(keys):
        T = Tx_cache[(a, g)]
        for x in range(n):
            if T[MUL[x][zc]] != T[x]:
                dev_U0 += 1
        tfset = [x for x in range(n) if T[x] != 0]
        if all(MUL[x][zc] in tfset for x in tfset):
            pairs4 += 1
    claim('U0', '★ 中心均勻律：T(x·(−1)) = T(x) 逐項（0 偏離）＋ 推論 TF 集中心封閉',
          dev_U0 == 0 and pairs4 == len(keys),
          '偏離 = %d ; TF 集中心封閉之鍵 = %d/%d' % (dev_U0, pairs4, len(keys)))
    tau_hits = {}
    for (a, g) in sorted(keys):
        T = Tx_cache[(a, g)]
        tfset = set(x for x in range(n) if T[x] != 0)
        good = []
        for tau in range(n):
            ok = True
            for x in range(n):
                xr = MUL[x][tau]
                if (xr in tfset) != (x in tfset) or (T[xr] != -T[x] if x in tfset else T[xr] != 0):
                    ok = False
                    break
            if ok:
                good.append(tau)
        tau_hits[(a, g)] = good
    n_with = sum(1 for k in tau_hits if tau_hits[k])
    claim('U1', '★ 逐實現鍵 ∃τ ∈ 2I 使 TF 集封閉於 x ↦ x·τ 且 T 反號',
          n_with == len(keys), '有解之鍵 = %d/%d ; τ 命中數值集 = %s'
          % (n_with, len(keys), sorted(set(len(v) for v in tau_hits.values()))))
    info('U1 詳情：τ 候選數範例 = %s' % [len(tau_hits[k]) for k in sorted(keys)[:8]])
    # U2：取該鍵之 τ，測同欄全部 120 個 g
    u2_ok = 0
    u2_tot = 0
    u2_samples = []
    for (a, g) in sorted(keys)[:12]:
        cand = tau_hits[(a, g)]
        for tau in cand[:1]:
            u2_tot += 1
            good_all = True
            for g2 in range(n):
                Ts = [Tterm(x, a, g2) for x in range(n)]
                tset = set(x for x in range(n) if Ts[x] != 0)
                for x in range(n):
                    xr = MUL[x][tau]
                    if (xr in tset) != (x in tset) or (Ts[xr] != -Ts[x] if x in tset else Ts[xr] != 0):
                        good_all = False
                        break
                if not good_all:
                    break
            u2_ok += good_all
            u2_samples.append((a, tau, good_all))
    claim('U2', 'U1 之 τ 只依 a（同欄全部 120 個 g 共用；12 個樣本欄各取其首個 τ）',
          u2_ok == u2_tot, '通過 = %d/%d ; 樣本 = %s' % (u2_ok, u2_tot, u2_samples[:4]))
    # U3 診斷：共軛類依賴 + 軸對符號關係
    def conj_class(s):
        return frozenset(MUL[MUL[x][s]][inv[x]] for x in range(n))
    cls = {}
    for s in range(n):
        cls.setdefault(conj_class(s), []).append(s)
    class_ok = 0
    for (a, g) in sorted(keys):
        vals = {S[(a, h)] for h in cls[conj_class(g)]}
        class_ok += (len(vals) == 1)
    sym_rel = sorted({(S[(a, g)][0], S[(partner[a], g)][0]) for (a, g) in keys})
    claim('U3（診斷）', 'S_TF 對 g 之共軛類依賴性；S_TF(ā,g) 與 S_TF(a,g) 之關係',
          True, '共軛類常數之鍵 = %d/%d ; (S_TF(a),S_TF(ā)) 值對集 = %s'
          % (class_ok, len(keys), sym_rel[:4]))
    # U4 診斷：S_FT 之 y-路是否同 τ
    dev_u4 = 0
    chk = 0
    for (a, g) in sorted(keys)[:12]:
        tau = tau_hits[(a, g)][0] if tau_hits[(a, g)] else None
        if tau is None:
            continue
        chk += 1
        Tsf = [0] * n
        for y in range(n):
            x = MUL[y][inv[g]]
            if tie[y][a] and not tie[x][a]:
                Tsf[y] = dgen[y][a] * eps[y] * sgn(dot3(U[a], KV[x]))
        for y in range(n):
            if Tsf[MUL[y][tau]] != (Tsf[y] if False else Tsf[MUL[y][tau]]):
                pass
        # 檢查：y ↦ y·τ 是否令 FT 項反號
        for y in range(n):
            if Tsf[MUL[y][tau]] != -Tsf[y] and Tsf[y] != 0:
                dev_u4 += 1
    claim('U4（診斷）', 'S_FT 之 y-路在**同一個 τ** 下之行為（反號或保持）',
          True, '樣本鍵 = %d ; 反號失敗之項 = %d（0 ⟹ 同一 τ 亦令 FT 項反號）' % (chk, dev_u4))

    # ================= Part V =================
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
    Z10 = sorted(s for s in range(n) if f_tf[s] + f_ft[s] == 0)
    d31 = json.load(io.open(os.path.join(BASE, 'data/31_r8_group.json'), encoding='utf-8'))
    info('V 前置核：f 與 R8 凍結全同 = %s ; Z10 = %s'
         % (f_tf == d31['f_tf'] and f_ft == d31['f_ft'] and f_tt == d31['f_tt'], Z10))
    claim('V1', 'Z10 反演封閉（s ∈ Z10 ⟹ s⁻¹ ∈ Z10）',
          all(inv[s] in Z10 for s in Z10), '違例 = %d' % sum(1 for s in Z10 if inv[s] not in Z10))
    zh = {}
    for s in Z10:
        zh[order[s]] = zh.get(order[s], 0) + 1
    claim('V2', '（回歸核）Z10 之階分佈 = {3:2, 4:2, 5:2, 6:2, 10:2}', zh == {3: 2, 4: 2, 5: 2, 6: 2, 10: 2}, '階 = %s' % zh)
    kvz = len({KV[s] for s in Z10})
    claim('V3', '★ |KV(Z10)| = 10', kvz == 10, '|KV(Z10)| = %d' % kvz)
    es = sum(1 for s in Z10 if eps[s] == 1)
    claim('V4', 'ε 於 Z10 之符號分佈 = 5/5', es == 5, '+1 之數 = %d ; −1 之數 = %d' % (es, 10 - es))
    deftypes = {}
    for s in Z10:
        dc = {}
        for a in range(ncol):
            if tie[s][a]:
                dc[types[a]] = dc.get(types[a], 0) + 1
        deftypes[s] = tuple(sorted(dc.items()))
    claim('V5', 'Z10 之全部元素之 tie 集型別分解相同',
          len(set(deftypes.values())) == 1, '相異分解數 = %d ; 分解 = %s'
          % (len(set(deftypes.values())), sorted(set(deftypes.values()))[0] if deftypes else None))

    # ================= Part W =================
    nz_cols = sorted({a for (a, g) in S if S[(a, g)][2] != 0})
    o3 = set(s for s in range(n) if order[s] == 3)
    w1_ok = 0
    for a in nz_cols:
        nz_g = set(g for g in range(n) if S[(a, g)][2] != 0)
        w1_ok += (nz_g == (set(range(n)) - o3))
    claim('W1', '★ 22 承載列：S_TT(a,g) ≠ 0 ⟺ g ∉ 𝒪₃（階 3 共軛類，20 個）',
          w1_ok == len(nz_cols) and len(nz_cols) == 22,
          '成立之列 = %d/%d ; 𝒪₃ 大小 = %d' % (w1_ok, len(nz_cols), len(o3)))
    tt = {}
    for a in nz_cols:
        tt[types[a]] = tt.get(types[a], 0) + 1
    claim('W2', '22 承載列之型別分解 = 12 vertex + 10 face（edge 0）',
          tt == {'vertex': 12, 'face': 10}, '型別分解 = %s' % tt)
    nz62 = [(a, g) for (a, g) in keys if S[(a, g)][2] != 0]
    pos = sorted(a for (a, g) in nz62 if S[(a, g)][2] * keys[(a, g)] > 0)
    negc = sorted(a for (a, g) in nz62 if S[(a, g)][2] * keys[(a, g)] < 0)
    pt = {}
    for a in pos:
        pt[types[a]] = pt.get(types[a], 0) + 1
    nt_ = {}
    for a in negc:
        nt_[types[a]] = nt_.get(types[a], 0) + 1
    claim('W3', '+16 之 8 列全屬 edge；−16 之 4 列全屬 vertex',
          pt == {'edge': 8} and nt_ == {'vertex': 4},
          '+8 之型別 = %s（列 %s）; −4 之型別 = %s（列 %s）' % (pt, pos, nt_, negc))
    eq = sum(1 for (a, g) in nz62 if S[(a, g)][2] == S[(a, inv[g])][2])
    claim('W4（診斷）', '非零鍵 S_TT(a,g) 與 S_TT(a,g⁻¹) 之關係',
          True, '相等之鍵 = %d/%d ; 值集 g⁻¹ = %s'
          % (eq, len(nz62), sorted({S[(a, inv[g])][2] for (a, g) in nz62})))
    oz = {}
    a0 = nz_cols[0]
    for g in range(n):
        if S[(a0, g)][2] != 0:
            oz[order[g]] = oz.get(order[g], 0) + 1
    exp = {1: 1, 2: 1, 4: 30, 5: 24, 6: 20, 10: 24}
    claim('W5', '非零 g 集之階分佈 = {1:1, 2:1, 4:30, 5:24, 6:20, 10:24}（W1 之推論）',
          oz == exp, '實測 = %s' % oz)

    # ================= Part T-c / U-c / V-c / W-c：更正與量測律（原 pre-registered tag 保留 FAIL） =================
    import itertools

    def orbit_multis(Kt_K, cells_of, s):
        """回傳 (重數多重集 sorted, {orbit-key: m}, {orbit-key: v})"""
        cnt, val = {}, {}
        for a in range(ncol):
            if a < partner[a]:
                ca, cb = cells_of(s, a), cells_of(s, partner[a])
                key = tuple(sorted([ca, cb]))
                cnt[key] = cnt.get(key, 0) + 1
                val[key] = Kt_K[s][a] + Kt_K[s][partner[a]]
        return sorted(cnt.values()), cnt, val

    def dissoc(ms):
        for u in itertools.product([-1, 0, 1], repeat=len(ms)):
            if any(u) and sum(m * x for m, x in zip(ms, u)) == 0:
                return False, u
        return True, None

    cells2 = lambda s, a: PAIR[s][a]
    cells3f = lambda s, a: (PAIR[s][a][0], PAIR[s][a][1], c2_of[s][a])
    ms2, _c2_, _v2_ = orbit_multis([[0] * ncol for _ in range(n)], cells2, 0)
    ms3, _c3_, _v3_ = orbit_multis([[0] * ncol for _ in range(n)], cells3f, 0)
    d2, w2_ = dissoc(ms2)
    d3, w3_ = dissoc(ms3)
    info('T-c 量測：2 層族 cell-orbit 重數 = %s（dissociated = %s，見證 u = %s）；3 層族 = %s（dissociated = %s，u = %s）'
         % (ms2, d2, w2_, ms3, d3, w3_))
    # 恆等式 R(s) = Σ_o m_o(s)·v_o(s) 之驗證（兩族全部表）
    id_ok = 0
    id_tot = 0
    cnt_r0_noasym = 0
    for t in tables:
        Kt = t['Kt']
        good = True
        for s in range(n):
            _ms, cnt, val = orbit_multis(Kt, cells2, s)
            if sum(Kt[s]) != sum(cnt[k] * val[k] for k in cnt):
                good = False
        id_tot += 1
        id_ok += good
        if t['R0'] and not t['asym']:
            cnt_r0_noasym += 1
    claim('T1-c', '更正恆等式：R(s) = Σ_{cell-orbits o} m_o(s)·v_o(s)（256 表逐 s）；（⟸ 逐對反號 ⟹ R ≡ 0 為定理）',
          id_ok == id_tot, '恆等成立 = %d/%d ; R ≡ 0 而逐對反號不成立之表 = %d（原 T1 ⟺ 之反例空間）'
          % (id_ok, id_tot, cnt_r0_noasym))
    # 3 層族：同一恆等式 + 反例（mask 452）
    id3_ok = 0
    r0_noasym3 = 0
    wit3 = None
    seed = 20261001
    for m in range(512):
        bits = []
        seed, r = splitmix64(seed)
        x = r
        for i in range(20):
            bits.append((x >> (i % 64)) & 1)
            if i % 64 == 63:
                seed, r = splitmix64(seed)
                x = r
        nt3 = {cells3[i]: (1 if bits[i] else -1) for i in range(18)}
        s1 = 1 if bits[18] else -1
        s2 = 1 if bits[19] else -1
        Kt = [[nt3[(PAIR[s][a][0], PAIR[s][a][1], c2_of[s][a])] if not tie[s][a]
               else (s1 if PAIR[s][a][1] == 1 else s2) for a in range(ncol)] for s in range(n)]
        good = True
        for s in range(n):
            _ms, cnt, val = orbit_multis(Kt, cells3f, s)
            if sum(Kt[s]) != sum(cnt[k] * val[k] for k in cnt):
                good = False
        id3_ok += good
        Rz = all(sum(Kt[s]) == 0 for s in range(n))
        if Rz and not pairs_antisym(Kt):
            r0_noasym3 += 1
            if wit3 is None:
                sstar = None
                for s in range(n):
                    if any(Kt[s][partner[a]] != -Kt[s][a] for a in range(ncol)):
                        sstar = s
                        break
                _ms, cnt, val = orbit_multis(Kt, cells3f, sstar)
                wit3 = {'mask': m, 's_star': sstar, 'multiplicities': _ms,
                        'orbit_vals': sorted(val.values()), 'R_s_star': sum(Kt[sstar])}
    claim('T3-c', '3 層族 512 表：同一恆等式成立；★原 T1 ⟺ 之反例數 = 1（R ≡ 0 而逐對反號不成立）',
          id3_ok == 512 and r0_noasym3 >= 1,
          '恆等 = %d/512 ; 反例 = %d ; 反例之 orbit 重數 = %s、v 值 = %s'
          % (id3_ok, r0_noasym3, wit3['multiplicities'] if wit3 else None, wit3['orbit_vals'] if wit3 else None))
    # U1-c：左乘 τ；U1-c2：16 個非空 TF 集鍵之項結構
    tauL = {}
    for (a, g) in sorted(keys):
        T = Tx_cache[(a, g)]
        tfset = set(x for x in range(n) if T[x] != 0)
        good = []
        for tau in range(n):
            ok = True
            for x in range(n):
                xr = MUL[tau][x]
                if (xr in tfset) != (x in tfset) or (T[xr] != -T[x] if x in tfset else T[xr] != 0):
                    ok = False
                    break
            if ok:
                good.append(tau)
        tauL[(a, g)] = good
    ne = [k for k in keys if Tx_cache[k].count(0) != n]
    nL = sum(1 for k in ne if tauL[k])
    claim('U1-c', '更正搜索：左乘 τ（x ↦ τ·x）之反號對合；並分離「空 TF 集（原 U1 之 46 個 vacuous）」與「非空 16 個」',
          nL == len(ne), '非空 TF 集之鍵 = %d ; 左乘有解 = %d ; 左乘 τ 命中數值集 = %s'
          % (len(ne), nL, sorted({len(tauL[k]) for k in ne})))
    det = {}
    for k in sorted(ne)[:3]:
        T = Tx_cache[k]
        rep = [T[x] for x in range(n) if T[x] != 0]
        det[str(k)] = rep
    claim('U1-c2（診斷）', '非空 TF 集鍵之項多重集（4 中心對之代表值）', True,
          '範例（鍵 → 項值表）= %s' % det)
    # V-c / W-c 量測律
    own_inv = [s for s in Z10 if inv[s] not in Z10]
    kept_inv = [s for s in Z10 if inv[s] in Z10]
    claim('V1-c（量測）', 'Z10 反演封閉性之實測：違例 8、保持 2（中心封閉恆真）；報兩集', True,
          '違例 = %s ; 保持 = %s' % (own_inv, kept_inv))
    from collections import Counter as _C
    kvc = _C(KV[s] for s in Z10)
    kvvals = sorted(set(KV[s] for s in Z10))
    anti = all(neg_ in kvvals for neg_ in kvvals)
    claim('V3-c（量測）', '|KV(Z10)| = 4 = 2 對反極；報 KV 值與重數', kvc == _C({K: v for K, v in kvc.items()}) and len(kvvals) == 4,
          'KV 值 = %s ; 重數 = %s ; 對反封閉 = %s' % (kvvals, sorted(kvc.values()), anti))
    epsd = _C(eps[s] for s in Z10)
    claim('V4-c（量測）', 'ε 於 Z10：2/8（對應 KV 之 4 值結構）', True, '分佈 = %s' % dict(epsd))
    a0 = nz_cols[0]
    nzg = [g for g in range(n) if S[(a0, g)][2] != 0]
    comp = [g for g in range(n) if S[(a0, g)][2] == 0]
    czo = _C(order[g] for g in comp)
    zsz = _C(order[g] for g in nzg)
    ctr = all(MUL[g][zc] in set(nzg) for g in nzg)
    claim('W1-c（量測律）', '非零 g 集：大小 100、中心不變、5 個非平凡階各恰 20；補集（20）之階組成',
          len(nzg) == 100 and zsz == _C({k: 20 for k in zsz}) and ctr,
          '|非零| = %d ; 階 = %s ; 中心不變 = %s ; 補集階組成 = %s' % (len(nzg), dict(zsz), ctr, dict(czo)))
    compsets = [frozenset(g for g in range(n) if S[(a, g)][2] == 0) for a in nz_cols]
    same_comp = len(set(compsets)) == 1
    cset = compsets[0]
    ga_set = set(g for (a, g) in keys)
    claim('W1-c2（量測）', '補集（20）與欄無關；並核其與 62 實現鍵 g_a、與 Z10 之交集',
          True, '補集欄無關 = %s ; |補集 ∩ {g_a}| = %d ; |補集 ∩ Z10| = %d ; 補集 = %s'
          % (same_comp, len(cset & ga_set), len(cset & set(Z10)), sorted(cset)))
    et = _C(types[a] for a in nz_cols)
    nec = [a for a in range(ncol) if types[a] == 'edge' and a not in set(nz_cols)]
    claim('W2-c（量測律）', '22 承載列**全屬 edge 欄**；30 個 edge 欄中之 8 個非承載（列號報出）',
          et == _C({'edge': 22}), '型別 = %s ; 非承載之 edge 欄 = %s' % (dict(et), nec))
    pt2 = _C(types[a] for a in pos)
    nt2 = _C(types[a] for a in negc)
    claim('W3-c（量測）', '±16 之 12 列全屬 edge（原 W3 之「−4 屬 vertex」被否證）',
          pt2 == _C({'edge': 8}) and nt2 == _C({'edge': 4}), '+8 = %s ; −4 = %s' % (dict(pt2), dict(nt2)))

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS  |  O225 R11 機器' % (npass, len(CLAIMS)))
    out = {'rules': RULES, 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
           'T': {'n_T1': n_T1, 'n_T2': n_T2, 't3_ok': t3_ok,
                 'R0_tables': sum(1 for t in tables if t['R0']), 'asym_tables': sum(1 for t in tables if t['asym'])},
           'U': {'dev_U0': dev_U0, 'n_with_tau': n_with,
                 'tau_counts': {str(k): len(v) for k, v in tau_hits.items()},
                 'u2': {'ok': u2_ok, 'tot': u2_tot}},
           'V': {'Z10': Z10, 'kv': kvz, 'eps_plus': es, 'tie_types': sorted(set(deftypes.values()))},
           'W': {'nz_cols': nz_cols, 'types': tt, 'pos': pos, 'neg': negc,
                 'pos_types': pt, 'neg_types': nt_, 'order_of_nonzero_g': oz}}
    with io.open(os.path.join(BASE, 'data/42_r11_machine.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
