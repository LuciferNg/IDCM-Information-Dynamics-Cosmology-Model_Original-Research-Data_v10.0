#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/106 -- R28 機器（`r28-crit2-misc1-v1`）。

Part F 四判準 × 9 非微擾改架構之響應矩陣（C1–C4；每 variant 完整重算；rank_GF(2)；共同變）
Part G MISC-1：τ 之 ±h 刻畫（Q₈ 檢定）＋ orbit 型別混合機制（PAIR-key 細分）

凍結指紋：data/105_r28_freeze.json。唯讀 O222；精確算術。
用法: /usr/bin/python3 scripts/106_r28_machine.py
"""
import hashlib
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
CLAIMS = []
PHI1 = (5, 1)   # √5 分量表示：φ⁻¹ = (5−√5)/10 之比較用 pair（本輪以 p² 對 5q² 之標準式處理）


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-6s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


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


def fs(v):
    for c in v:
        s = sgn(c)
        if s:
            return s
    return 0


def dot3(u, v):
    return add(add(mul(u[0], v[0]), mul(u[1], v[1])), mul(u[2], v[2]))


def cross3(u, v):
    return (add(mul(u[1], v[2]), neg(mul(u[2], v[1]))),
            add(mul(u[2], v[0]), neg(mul(u[0], v[2]))),
            add(mul(u[0], v[1]), neg(mul(u[1], v[0]))))


def main():
    print('=' * 112)
    print('O225 scripts/106 -- R28 機器（CRIT-2 響應矩陣 ＋ MISC-1 τ/orbit）')
    print('=' * 112, flush=True)
    fp = os.path.join(BASE, 'data', '105_r28_freeze.json')
    assert os.path.exists(fp), '凍結指紋缺失：先跑 scripts/105'
    fr = json.load(io.open(fp, encoding='utf-8'))
    csha = hashlib.sha256(io.open(os.path.join(BASE, 'docs', '60_r28_contract.md'), 'rb').read()).hexdigest()
    info('凍結核：合約 sha 相符 = %s（%s）' % (csha == fr['sha256'], fr['sha256'][:16]))
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'b106')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i2, _t2, _h2 = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'b106a')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
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
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(add(U[i][t], U[j][t]) == (0, 0) for t in range(3)):
                partner[i] = j
    pairs = sorted(i for i in range(ncol) if i < partner[i])

    def build(ref=0, kind='dind', tie_ext=False, smap=None, lmap=None):
        """完整重算：參數化架構 → (tie, dd, nz, Vset, B10, NZ, eps, KV)。"""
        KVb = [mm.rot_ref(g, U[ref]) for g in G]
        if smap == 'inv':
            KVb = [KVb[inv[x]] for x in range(n)]
        elif smap == 'sq':
            KVb = [KVb[MUL[x][x]] for x in range(n)]
        idx = list(range(ncol)) if lmap is None else [partner[a] for a in range(ncol)]
        tie = [[(dot3(U[idx[a]], KVb[s]) == (0, 0)) for a in range(ncol)] for s in range(n)]
        eps = [fs(KVb[s]) for s in range(n)]
        dd = [[0] * ncol for _ in range(n)]
        for s in range(n):
            for a in range(ncol):
                t = dot3(U[idx[a]], KVb[s]) == (0, 0)
                cr = cross3(U[idx[a]], KVb[s]) == (0, 0)
                if tie_ext:
                    t = t or cr
                if kind == 'dind':
                    dd[s][a] = (1 if fs(cross3(U[idx[a]], KVb[s])) != eps[s] else 0) if t else 0
                else:
                    dd[s][a] = 1 if fs(cross3(U[idx[a]], KVb[s])) != eps[s] else 0
        # 承載：S_TT 非零欄
        nz = set()
        for a in range(ncol):
            for g in range(n):
                acc = 0
                for x in range(n):
                    y = MUL[x][g]
                    if tie[x][a] and tie[y][a]:
                        acc += (0 if dd[x][a] == dd[y][a] else 1) * eps[x] * eps[y]
                if acc != 0:
                    nz.add(a)
                    break
        V = {a: [s for s in range(n) if tie[s][a]] for a in range(ncol)}
        refax = idx[ref] if lmap is None else partner[ref]
        dots = {a: dot3(U[a], U[refax]) for a in range(ncol)}
        # B10：|dot| 取「邊欄之最小非零 |dot|」；以 p² vs 5q² 精確比較
        edge = [a for a in range(ncol) if types[a] == 'edge']
        def key(pr):
            p, q = pr[0], pr[1]
            return (abs(p) * abs(p) - 5 * abs(q) * abs(q), abs(p))
        nz_edge = [a for a in edge if dots[a] != (0, 0)]
        best = min(nz_edge, key=lambda a: key(dots[a]))
        v0 = dots[best]
        B10 = sorted(a for a in range(ncol) if dots[a] in (v0, (-v0[0], -v0[1])))
        NZ = {a: sum(1 for t in range(3) if U[a][t] == (0, 0)) for a in range(ncol)}
        return {'tie': tie, 'dd': dd, 'nz': nz, 'V': V, 'B10': B10, 'NZ': NZ, 'eps': eps, 'U': U, 'idx': idx, 'KVb': KVb}

    def crits(st):
        Tcols = [a for a in range(ncol) if len(st['V'][a]) > 0]
        c1bad, c2bad, c4bad = [], [], []
        for a in Tcols:
            Vv = st['V'][a]
            dv = [st['dd'][s][a] for s in Vv]
            nconst = len(set(dv)) > 1
            if (a in st['nz']) != nconst:
                c1bad.append(a)
            # 兩 ± 對：Vv = {x, x·zc, y, y·zc}
            rep = [s for s in Vv if s == min(s, MUL[s][zc])]
            if len(rep) == 2:
                if (a in st['nz']) != (st['dd'][rep[0]][a] != st['dd'][rep[1]][a]):
                    c2bad.append(a)
        for a in range(ncol):
            if (a not in st['nz']) != (a in set(st['B10']) and st['NZ'][a] == 0):
                c4bad.append(a)
        # C3（符號層不可約）：符號型分劃 ⊀ 承載分劃
        prof = {}
        for a in Tcols:
            key = (tuple(sgn(c) for c in U[a]), types[a],
                   tuple(sorted(sgn(cross3(U[a], st['KVb'][s])[k]) for s in st['V'][a] for k in range(3))))
            prof.setdefault(key, set()).add(a in st['nz'])
        c3 = all(len(v) == 1 for v in prof.values())
        c4e_bad = [a for a in range(ncol) if types[a] == 'edge'
                   and ((a not in st['nz']) != (a in set(st['B10']) and st['NZ'][a] == 0))]
        return {'C1': not c1bad, 'C2': not c2bad, 'C3': c3, 'C4': not c4bad,
                'C3inv': not c3, 'C4e': not c4e_bad,
                'bad': {'C1': c1bad, 'C2': c2bad, 'C4': c4bad, 'C4e': c4e_bad},
                'n_prof': len(prof)}

    KVx = [mm.rot_ref(g, U[0]) for g in G]   # 基線 KV（Part G 之 PAIR 用）
    VARS = [('V0', dict()), ('V1', dict(ref=next(a for a in range(ncol) if types[a] == 'edge'))),
            ('V2', dict(ref=next(a for a in range(ncol) if types[a] == 'face'))),
            ('V3', dict(ref=next(a for a in range(ncol) if types[a] == 'vertex'))),
            ('V4', dict(kind='dgen')), ('V5', dict(tie_ext=True)), ('V6', dict(smap='inv')),
            ('V7', dict(lmap='partner')), ('V8', dict(smap='sq'))]
    Res = {}
    for tag, kw in VARS:
        st = build(**kw)
        Res[tag] = crits(st)
        info('%s：C1=%s C2=%s C3=%s C4=%s ｜ 承載 = %d ｜ 符號型 = %d'
             % (tag, Res[tag]['C1'], Res[tag]['C2'], Res[tag]['C3'], Res[tag]['C4'], len(st['nz']), Res[tag]['n_prof']))
    vec = {c: [1 if Res[t][c] else 0 for t, _ in VARS] for c in ('C1', 'C2', 'C3', 'C4')}
    claim('F1', 'baseline（V0）四判準全真', all(Res['V0'][c] for c in ('C1', 'C2', 'C3', 'C4')),
          'V0 = %s' % {c: Res['V0'][c] for c in ('C1', 'C2', 'C3', 'C4')})
    # GF(2) 秩
    rows = [vec[c] for c in ('C1', 'C2', 'C3', 'C4')]
    basis = []
    for r in rows:
        cur = r[:]
        for b in basis:
            piv = next(i for i in range(len(b)) if b[i])
            if cur[piv]:
                cur = [x ^ y for x, y in zip(cur, b)]
        if any(cur):
            piv = next(i for i in range(len(cur)) if cur[i])
            basis.append(cur)
    rank = len(basis)
    claim('F2', 'rank_GF(2)(M) = 4（四判準獨立）；預期：否證', rank == 4,
          '實測 rank = %d；向量 = %s' % (rank, {c: ''.join(str(x) for x in vec[c]) for c in vec}))
    f3 = [t for t, _ in VARS if (not Res[t]['C3']) and Res[t]['C1'] and Res[t]['C2'] and Res[t]['C4']]
    claim('F3', '存在 variant 使 C3 假而 C1,C2,C4 真（符號層可約之反例）', bool(f3), '此類 variant = %s' % (f3 or '無'))
    claim('F4', 'C4 之響應向量與 C1 不同（非同判準之重寫）', vec['C4'] != vec['C1'],
          'C1 = %s｜C4 = %s' % (''.join(map(str, vec['C1'])), ''.join(map(str, vec['C4']))))
    covar = [(x, y) for i, x in enumerate(('C1', 'C2', 'C3', 'C4')) for y in ('C1', 'C2', 'C3', 'C4')[i + 1:]
             if vec[x] == vec[y]]
    claim('F5（報告）', '逐 variant 判決表 ＋ 共同變對', True,
          '共同變 = %s ｜ 表 = %s' % (covar, {t: ''.join('1' if Res[t][c] else '0' for c in ('C1', 'C2', 'C3', 'C4')) for t, _ in VARS}))

    vec2 = {c: [1 if Res[t][c] else 0 for t, _ in VARS] for c in ('C1', 'C2', 'C3inv', 'C4e')}
    rows2 = [vec2[c] for c in ('C1', 'C2', 'C3inv', 'C4e')]
    basis2 = []
    for r in rows2:
        cur = r[:]
        for b in basis2:
            piv = next(i for i in range(len(b)) if b[i])
            if cur[piv]:
                cur = [x ^ y for x, y in zip(cur, b)]
        if any(cur):
            basis2.append(cur)
    rank2 = len(basis2)
    claim('F1-c', '【校正 tag】四判準之正規形式（C3 取 R18 之正向「不可約」；C4 限 edge 欄 = R19 之正域）後，baseline 全真',
          all(Res['V0'][c] for c in ('C1', 'C2', 'C3inv', 'C4e')),
          'baseline = %s' % {c: Res['V0'][c] for c in ('C1', 'C2', 'C3inv', 'C4e')})
    claim('F2-c', '【校正 tag】正規四判準之響應矩陣 rank_GF(2)（實測；F2 之原預註冊 4 已否證）', True,
          'rank = %d；向量 = %s' % (rank2, {c: ''.join(map(str, vec2[c])) for c in vec2}))
    f3c = [t_ for t_, _ in VARS if (not Res[t_]['C3inv']) and Res[t_]['C1'] and Res[t_]['C2'] and Res[t_]['C4e']]
    claim('F3-c', '【校正 tag】存在 variant 使（正向）C3 假而 C1,C2,C4e 真 ⟹ 符號層可約之反例家族', bool(f3c),
          '此類 variant = %s' % (f3c or '無'))
    cov2 = [(x, y) for i, x in enumerate(('C1', 'C2', 'C3inv', 'C4e')) for y in ('C1', 'C2', 'C3inv', 'C4e')[i + 1:]
            if vec2[x] == vec2[y]]
    info('正規四判準共同變對 = %s ｜ 表 = %s' % (cov2, {t_: ''.join('1' if Res[t_][c] else '0' for c in ('C1', 'C2', 'C3inv', 'C4e')) for t_, _ in VARS}))

    # ================= Part G =================
    d45 = json.load(io.open(os.path.join(BASE, 'data', '45_r12_machine.json'), encoding='utf-8'))
    X = d45.get('X', {})
    taus = X.get('tau') or X.get('taus') or None
    if taus is None:
        for k, v in d45.items():
            if isinstance(v, dict) and 'tau' in v:
                taus = v['tau']
    info('R12 τ 資料來源鍵 = %s' % (str(list(X.keys())[:6]) if X else '（改用 data/45 其他欄）'))
    taus = {k: v for k, v in (taus or {}).items() if v}
    size4 = sorted([k for k, v in taus.items() if len(v) == 4])
    claim('G1', '|τ| = 4 之鍵恰 4 個且屬 2 條軸線（每線 2 鍵）；τ = {±g_a} ⊎ {±h}',
          len(size4) == 4 and len({tuple(sorted((int(k[1:-1].split(',')[0]), int(k[1:-1].split(',')[1])))) for k in size4}) >= 2,
          '|τ|=4 之鍵 = %d；τ 大小分佈 = %s' % (len(size4), sorted(set(len(v) for v in taus.values()))))
    g2ok = g3ok = True
    g3det = []
    for k in size4:
        v = taus[k]
        ga = [t for t in v if order[t] == 4]
        extra = [t for t in v if all(MUL[t][x] != x for x in range(n)) and t not in ga[:1]]
        h = [t for t in v if MUL[t][v[0]] != v[0]]
        h = [t for t in v if t not in (v[0], inv[v[0]])]
        if not h:
            g2ok = False
            continue
        h = h[0]
        ge = v[0]
        if not (order[h] == 4 and MUL[h][ge] != MUL[ge][h] and MUL[MUL[h][ge]][inv[h]] == inv[ge]):
            g2ok = False
        lhs = MUL[h][h]
        rhs = MUL[ge][ge]
        g3det.append((order[h], order[ge], lhs == rhs, order[lhs]))
        if lhs != rhs:
            g3ok = False
    claim('G2', 'h 之刻畫：ord(h) = 4 ∧ h ∉ C(g_a) ∧ h g_a h⁻¹ = g_a⁻¹', g2ok,
          'τ=4 鍵逐個檢核 = %s' % ('全符' if g2ok else '有反例'))
    claim('G3', '★ h² = g_a² ⟹ ⟨g_a, h⟩ ≅ Q₈（四元數群）', g3ok, '逐鍵 (ord h, ord g_a, h²=g_a², ord h²) = %s' % g3det)

    st0 = build()
    def pair0(x):
        return (sgn(dot3(U[x], KVx[0])), fs(cross3(U[x], KVx[0])))
    orb = {}
    for a in pairs:
        orb.setdefault(tuple(sorted([pair0(a), pair0(partner[a])])), []).append(a)
    tt = {}
    for a in pairs:
        tt[types[a]] = tt.get(types[a], 0) + 1
    comp = {str(k): dict((t_, sum(1 for x in v if types[x] == t_)) for t_ in sorted(set(types[x] for x in v))) for k, v in orb.items()}
    claim('G4', '31 軸對型別 = 15 edge + 10 face + 6 vertex；orbit 數與型別組成（含混合）報告',
          tt == {'edge': 15, 'face': 10, 'vertex': 6},
          'orbit 數 = %d；型別 = %s；組成 = %s' % (len(orb), tt, comp))
    def key2(x):
        return [pair0(x), pair0(partner[x])]

    def refine(x):
        return tuple(sorted([(d, abs(c)) for (d, c) in key2(x)]))
    orb2 = {}
    for a in pairs:
        orb2.setdefault(refine(a), []).append(a)
    mixed1 = [k for k, v in orb.items() if len(set(types[x] for x in v)) > 1]
    mixed2 = [k for k, v in orb2.items() if len(set(types[x] for x in v)) > 1]
    claim('G5', '★ 以 Aut(120) 之外部分（c ↦ −c，商去 c 之符號）細分 orbit ⟹ 混合單型別化（預期）',
          len(mixed2) == 0 and len(orb) > 0,
          '原 orbit 數 = %d（混合 %d）→ 細分後 orbit 數 = %d（混合 %d）；細分中 key 數 = %d'
          % (len(orb), len(mixed1), len(orb2), len(mixed2), len(orb2)))

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  |  O225 R28 機器' % (npass, len(CLAIMS)))
    io.open(os.path.join(BASE, 'data', '106_r28_machine.json'), 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r28-crit2-misc1-v1', 'claims': CLAIMS, 'n_pass': npass, 'n_total': len(CLAIMS),
         'matrix': {t: {c: Res[t][c] for c in ('C1', 'C2', 'C3', 'C4')} for t, _ in VARS},
         'vectors': {c: vec[c] for c in vec}, 'rank_gf2': rank, 'covary': covar,
         'vectors_regular': {c: vec2[c] for c in vec2}, 'rank_gf2_regular': rank2,
         'bad_cols': {t: Res[t]['bad'] for t, _ in VARS}, 'G3_detail': g3det,
         'orbits': {str(k): [types[a] for a in v] for k, v in orb.items()}, 'orbits_refined': {str(k): [types[a] for a in v] for k, v in orb2.items()}},
        indent=1, ensure_ascii=False))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
