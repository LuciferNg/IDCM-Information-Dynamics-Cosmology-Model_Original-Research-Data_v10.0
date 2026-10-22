#!/usr/bin/env python3
"""O225 scripts/25 -- R6 Part B/C：edge 參考之 tie 集完整刻畫 + 非邊軸非正交定理（`r6-mechanism-v1`）。

B1 型別分解 (2v, f, e) 與奇偶約束／B2 H_edge 軌道（6 ∤ 8）／B3 精確點積值譜
C1 非邊軸兩兩非正交定理／C2 完備正交圖雙計數表／C3 幾何身份（五邊形邊／三角形邊，預測）／C4 H_face 單一軌道
精確算術；零浮點；上游唯讀。用法: /usr/bin/python3 scripts/25_r6_geometry.py
"""
import collections
import importlib.util
import io
import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
RULES = 'r6-mechanism-v1'
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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


def dot3(u, r):
    return add(add(mul(u[0], r[0]), mul(u[1], r[1])), mul(u[2], r[2]))


def vadd(u, w):
    """向量（Z[√5]³）加法；注意 add 為純量加法。"""
    return (add(u[0], w[0]), add(u[1], w[1]), add(u[2], w[2]))


def qsub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def qmul(a, b):
    return (a[0] * b[0] + 5 * a[1] * b[1], a[0] * b[1] + b[0] * a[1])


def qinv(a):
    nrm = a[0] * a[0] - 5 * a[1] * a[1]
    return (a[0] / nrm, -a[1] / nrm)


def qstr(a):
    p, q = a
    if q == 0:
        return str(p)
    sign = '+' if q > 0 else '-'
    return '%s%s%s√5' % (p, sign, abs(q))


def toq(x):
    return (F(x[0]), F(x[1]))


def nrm2(u):
    acc = (F(0), F(0))
    for c in u:
        acc = add(acc, mul(c, c))
    return acc


def same_line(u, x):
    t = None
    for j in range(3):
        if x[j] != (0, 0):
            t = j
            break
    if t is None:
        return False
    lam = qmul(toq(u[t]), qinv(toq(x[t])))
    return all(qsub(toq(u[j]), qmul(lam, toq(x[j]))) == (0, 0) for j in range(3))


def main():
    print('=' * 116)
    print('O225 scripts/25 -- R6 PART B/C: full tie characterization (edge refs) + non-edge orthogonality theorem')
    print('=' * 116, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'r6b_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    G, _ig, _M2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'r6b_a2').build_group()
    n, ncol = len(K), len(K[0])
    pairs = [(a, b) for a in range(ncol) for b in range(ncol)]
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(sgn(add(U[i][t], U[j][t])) == 0 for t in range(3)):
                partner[i] = j
    key = [min(a, partner[a]) for a in range(ncol)]
    keys = sorted(set(key))
    ktype = {kk: types[kk] for kk in keys}
    tieset = {kk: sorted(set(key[a] for a in range(ncol) if sgn(dot3(U[a], U[kk])) == 0)) for kk in keys}
    typeset = {kk: collections.Counter(ktype[x] for x in tieset[kk]) for kk in keys}

    # ---------- B1：型別分解 + 奇偶約束 ----------
    edge_keys = [kk for kk in keys if ktype[kk] == 'edge']
    face_keys = [kk for kk in keys if ktype[kk] == 'face']
    vertex_keys = [kk for kk in keys if ktype[kk] == 'vertex']
    decomp = {}
    e_vals = set()
    for kk in edge_keys:
        c = typeset[kk]
        decomp[str(kk)] = {'vertex': c.get('vertex', 0), 'face': c.get('face', 0), 'edge': c.get('edge', 0)}
        e_vals.add(c.get('edge', 0))
    v_ok = all(decomp[str(kk)]['vertex'] == 2 and decomp[str(kk)]['face'] + decomp[str(kk)]['edge'] == 4
               and decomp[str(kk)]['face'] % 2 == 0 and decomp[str(kk)]['face'] + decomp[str(kk)]['edge'] + 2 == 6
               for kk in edge_keys)
    P = 0
    for i in range(len(edge_keys)):
        for j in range(i + 1, len(edge_keys)):
            if edge_keys[j] in tieset[edge_keys[i]]:
                P += 1
    e_val = sorted(e_vals)[0] if len(e_vals) == 1 else None
    claim('B1', '★ 型別分解（推導約束）：每 edge 參考 = 2 vertex + f face + e edge，f + e = 4 且 f 偶；'
                '並核 15e = 2P（edge–edge 正交對數 P）',
          v_ok and e_val is not None and 15 * e_val == 2 * P and (decomp[str(edge_keys[0])]['face'],
                                                                 decomp[str(edge_keys[0])]['edge']) in ((0, 4), (2, 2), (4, 0)),
          '分解 = %s ; e = %s ; P = %d ; 15e = %d ; 2P = %d ; 實際 (f,e) = %s'
          % (sorted(set(tuple(sorted(decomp[str(kk)].items())) for kk in edge_keys)), e_val, P, 15 * e_val, 2 * P,
             sorted(set((decomp[str(kk)]['face'], decomp[str(kk)]['edge']) for kk in edge_keys))))

    # ---------- B2：H_edge 軌道 ----------
    def stabilizer(kk):
        return [g for g in range(n) if same_line(mm.rot_ref(G[g], U[kk]), U[kk])]

    def act_key(g, x):
        v = mm.rot_ref(G[g], U[x])
        for b in range(ncol):
            if same_line(v, U[b]):
                return key[b]
        return None
    He = stabilizer(edge_keys[0])
    seen, orbits = set(), []
    for x in tieset[edge_keys[0]]:
        if x in seen:
            continue
        orb, stack = set(), [x]
        while stack:
            y = stack.pop()
            if y in orb:
                continue
            orb.add(y)
            for g in He:
                z = act_key(g, y)
                if z is not None and z not in orb:
                    stack.append(z)
        seen |= orb
        orbits.append(sorted(orb))
    sizes = sorted(len(o) for o in orbits)
    claim('B2', '★★ 群論：H_edge 階 8；6 條 tie 軸**不可能**為單一軌道（6 ∤ 8）；型別類為軌道之並（大小 ∈ {1,2,4,8}）',
          len(He) == 8 and len(orbits) > 1 and all(s in (1, 2, 4, 8) for s in sizes),
          '|H_edge| = %d ; 軌道大小 = %s ; 軌道 = %s' % (len(He), sizes, orbits))

    # ---------- B3：精確點積值譜 ----------
    norm_spec = collections.Counter()
    raw_spec = collections.Counter()
    for kk in edge_keys:
        ax = tieset[kk]
        for i in range(len(ax)):
            for j in range(i + 1, len(ax)):
                d = dot3(U[ax[i]], U[ax[j]])
                den = qmul(nrm2(U[ax[i]]), nrm2(U[ax[j]]))
                norm_spec[qstr(qmul(toq(d), qinv(den)))] += 1
                raw_spec['(%s)/(%s)' % (qstr(toq(d)), qstr(den))] += 1
    claim('B3', '★ 精確幾何：15 條 edge 參考之 6 tie 軸兩兩（45 對/軸 = 225 對）之歸一化平方值 Q(√5) 值譜',
          len(norm_spec) > 1, '歸一化平方值譜 = %s ; 原始 (⟨·,·⟩, N_iN_j) 相異對 = %d'
          % (sorted(norm_spec.items()), len(raw_spec)))

    # ---------- C1/C2：完備正交圖 ----------
    tpc = collections.Counter()
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = keys[i], keys[j]
            if b in tieset[a]:
                tpc[tuple(sorted((ktype[a], ktype[b])))] += 1
    nonedge_pairs = [('face', 'face'), ('face', 'vertex'), ('vertex', 'vertex')]
    c1 = all(tpc.get(p, 0) == 0 for p in nonedge_pairs)
    claim('C1', '★★★ 非邊軸兩兩非正交定理：16 條非 edge 線（6 vertex + 10 face）中任兩條皆不正交 '
                '⟹ vertex–vertex = vertex–face = face–face = 0 ⟹ 頂點／face 參考之 tie 必然全 edge 型（#2 之答案）',
          c1, '型別對正交數 = %s' % {('%s-%s' % k): v for k, v in sorted(tpc.items())})
    ve = tpc.get(('edge', 'vertex'), 0)
    ef = tpc.get(('edge', 'face'), 0)
    ee = tpc.get(('edge', 'edge'), 0)
    claim('C2', '★ 完備正交圖雙計數表：edge–vertex = 30 = 6×5；edge–face = 30 = 10×3；edge–edge = P',
          ve == 30 and ef == 30 and ee == P and ve == 6 * 5 and ef == 10 * 3,
          'edge–vertex = %d (= 6×5) ; edge–face = %d (= 10×3) ; edge–edge = %d (= P) ; 總正交對 = %d'
          % (ve, ef, ee, sum(tpc.values())))

    # ---------- C3：幾何身份（原預測；取向錨定版，預期 FAIL = 概念否證）----------
    def adj_ok(u, w):
        """|⟨u,w⟩| = |u||w|/√5（二十面體鄰接／次鄰接共同滿足）"""
        d = dot3(u, w)
        if sgn(d) == 0:
            return False
        return qsub(toq(mul(d, d)), qmul(qmul(nrm2(u), nrm2(w)), (F(1, 5), F(0)))) == (0, 0)

    def negv(u):
        return (neg(u[0]), neg(u[1]), neg(u[2]))

    def smul(s, u):
        z = (F(s), F(0))
        return (mul(z, u[0]), mul(z, u[1]), mul(z, u[2]))

    def axis_of(vec):
        for b in range(ncol):
            if same_line(vec, U[b]):
                return key[b]
        return None
    edge_all = set(edge_keys)
    v_ok_n = 0
    v_bad = []
    partitions = {}
    rings = {}
    for kk in vertex_keys:
        v = U[kk]
        ring = [w for w in range(ncol) if types[w] == 'vertex' and sgn(dot3(v, U[w])) > 0 and adj_ok(v, U[w])]
        rings[kk] = ring
        c1, c2 = set(), set()
        for i in range(len(ring)):
            for j in range(i + 1, len(ring)):
                if not adj_ok(U[ring[i]], U[ring[j]]):
                    continue
                k = axis_of(vadd(U[ring[i]], U[ring[j]]))
                if k is None:
                    continue
                (c1 if sgn(dot3(U[ring[i]], U[ring[j]])) > 0 else c2).add(k)
        c3 = edge_all - c1 - c2
        partitions[kk] = (sorted(c1), sorted(c2), sorted(c3))
        if sorted(c1) == tieset[kk]:
            v_ok_n += 1
        else:
            v_bad.append((kk, len(ring), sorted(c1), tieset[kk]))
    def endpoint_lines(e):
        """端點線識別（收緊）：需 ①±u_a ± u_b ∝ U[e] 且 ②該取向對為**鄰接**（點積 = +√(N_aN_b/5)，即最小距離）"""
        out = set()
        for a, b in ((x, y) for x in vertex_keys for y in vertex_keys if x < y):
            for sa in (1, -1):
                for sb in (1, -1):
                    ua, ub = smul(sa, U[a]), smul(sb, U[b])
                    if not same_line(vadd(ua, ub), U[e]):
                        continue
                    d = dot3(ua, ub)
                    if sgn(d) <= 0:
                        continue
                    if qsub(toq(mul(d, d)), qmul(qmul(nrm2(U[a]), nrm2(U[b])), (F(1, 5), F(0)))) == (0, 0):
                        out.add(a)
                        out.add(b)
        return sorted(out)
    f_ok_n = 0
    f_bad = []
    for kk in face_keys:
        f = U[kk]
        tris = {}
        for a, b, c in ((x, y, z) for x in vertex_keys for y in vertex_keys for z in vertex_keys if x < y < z):
            if not (adj_ok(U[a], U[b]) and adj_ok(U[b], U[c]) and adj_ok(U[a], U[c])):
                continue
            for sa in (1, -1):
                for sb in (1, -1):
                    for sc in (1, -1):
                        if same_line(vadd(vadd(smul(sa, U[a]), smul(sb, U[b])), smul(sc, U[c])), f):
                            tris.setdefault((a, b, c), (sa, sb, sc))
                            break
        tl = [(a, b, c, pat) for (a, b, c), pat in tris.items()]
        edges = sorted({axis_of(vadd(smul(t[3][0], U[t[0]]), smul(t[3][1], U[t[1]]))) for t in tl}
                       | {axis_of(vadd(smul(t[3][1], U[t[1]]), smul(t[3][2], U[t[2]]))) for t in tl}
                       | {axis_of(vadd(smul(t[3][0], U[t[0]]), smul(t[3][2], U[t[2]]))) for t in tl})
        tris = tl
        if len(tris) == 2 and sorted(edges) == tieset[kk]:
            f_ok_n += 1
        else:
            f_bad.append((kk, len(tris), edges, tieset[kk]))
    claim('C3', '★★ 原預測（見數前）：vertex 參考之 5 tie 軸 = 該頂點鄰居五邊形之 5 條邊；face 參考之 3 tie 軸 = 該面之 3 條邊'
                '——（取向錨定版；FAIL = 概念否證：邊方向 ⟂ r ≠ 邊之 2-fold 軸 ⟂ r）',
          v_ok_n == 6 and f_ok_n == 10,
          'vertex 全符 = %d/6 %s ; face 全符 = %d/10 %s' % (v_ok_n, v_bad[:2], f_ok_n, f_bad[:2]))

    # ---------- C3a：見數後修正（tie = 三分之第三族 = 赤道帶中點線）----------
    pa_ok = all(partitions[kk][0] and partitions[kk][1] and partitions[kk][2]
                and sorted(set(partitions[kk][0]) | set(partitions[kk][1]) | set(partitions[kk][2])) == sorted(edge_all)
                and len(partitions[kk][0]) == len(partitions[kk][1]) == len(partitions[kk][2]) == 5
                and not (set(partitions[kk][0]) & set(partitions[kk][1]))
                and not (set(partitions[kk][1]) & set(partitions[kk][2]))
                and not (set(partitions[kk][0]) & set(partitions[kk][2]))
                for kk in vertex_keys)
    tie_is_c3 = all(partitions[kk][2] == tieset[kk] for kk in vertex_keys)
    mult = {}
    for kk in vertex_keys:
        c = collections.Counter()
        for e in tieset[kk]:
            for k2 in endpoint_lines(e):
                c[k2] += 1
        mult[kk] = sorted(c.values())
        rings[kk] = sorted({x for e in tieset[kk] for x in endpoint_lines(e)})
    ring_lines_ok = all(len(rings[kk]) == 5 and mult[kk] == [2] * 5 for kk in vertex_keys)
    claim('C3a', '★★ 見數後修正（非預測）：15 條 edge 線三分為三族各 5（環邊／環對角／跨環＝赤道帶），互斥且並為全體；'
                 '**tie 集 = 第 ③ 族**；每條 tie edge 軸之端點線對 = 5 條 ring 線各 2 次',
          pa_ok and tie_is_c3 and ring_lines_ok,
          '三分核 = %s ; tie = 第三族 = %s ; 端點多重集 = %s ; 樣本 (環邊,環對角,跨環) = %s'
          % (pa_ok, tie_is_c3, {k: mult[k] for k in vertex_keys[:3]}, partitions[vertex_keys[0]]))

    # ---------- C3b：新預測（見數前）face 之 tie 軸端點 = 3 條中間層頂點線 ×2 ----------
    fb_mult = {}
    fb_lines = {}
    for kk in face_keys:
        c = collections.Counter()
        for e in tieset[kk]:
            for k2 in endpoint_lines(e):
                c[k2] += 1
        fb_mult[kk] = sorted(c.values())
        fb_lines[kk] = sorted(c.keys())
    fb_ok = all(len(fb_lines[kk]) == 3 and fb_mult[kk] == [2, 2, 2] for kk in face_keys)
    claim('C3b', '★★ 新預測（見數前，主部）：face 參考之 3 條 tie edge 軸之端點（作為頂點線）多重集 = 3 條頂點線 × 各 2',
          fb_ok, '端點多重集全 = [2,2,2] = %s ; 線數 = %s' % (fb_ok, sorted(set(len(v) for v in fb_lines.values()))))
    hgt2 = {}
    for kk in face_keys:
        vals = sorted(set(qstr(mul(dot3(U[k2], U[kk]), dot3(U[k2], U[kk]))) for k2 in fb_lines[kk]))
        other = sorted(set(qstr(mul(dot3(U[k2], U[kk]), dot3(U[k2], U[kk])))
                           for k2 in vertex_keys if k2 not in fb_lines[kk]))
        hgt2[kk] = [vals, other]
    fb_h_ok = all(len(v[0]) == 1 for v in hgt2.values())
    claim('C3b-h', '★ 原預測之高度部分（見數前）：該 3 條端點線之 |⟨U[k],U[f]⟩|² 一致（且 ≠ 其餘 3 條線之值）',
          fb_h_ok and all(v[0] != v[1] for v in hgt2.values()),
          '端點線 |dot|² 值集 = %s ; 其餘 3 線之值集 = %s'
          % (sorted(set(str(v[0]) for v in hgt2.values())), sorted(set(str(v[1]) for v in hgt2.values()))))
    pairrel = []
    for kk in face_keys:
        for e in tieset[kk]:
            for a, b in ((x, y) for x in vertex_keys for y in vertex_keys if x < y):
                for sa in (1, -1):
                    for sb in (1, -1):
                        ua, ub = smul(sa, U[a]), smul(sb, U[b])
                        if same_line(vadd(ua, ub), U[e]) and sgn(dot3(ua, ub)) > 0:
                            ha, hb = dot3(ua, U[kk]), dot3(ub, U[kk])
                            pairrel.append(qstr(add(ha, hb)))
                            break
    claim('C3b-r', '報告（無預測）：每條 tie edge 軸之端點高度和 = 0（定向後精確恆等，赤道穿越之代數內容）',
          all(x == '0' for x in pairrel), '逐軸高度和之相異值 = %s ; 軸數 = %d' % (sorted(set(pairrel)), len(pairrel)))

    # ---------- C4：H_face / H_r 單一軌道 ----------
    res = {}
    for nm, kk, order in (('face', face_keys[0], 12), ('vertex', vertex_keys[0], 20)):
        H = stabilizer(kk)
        seen, orbits = set(), []
        for x in tieset[kk]:
            if x in seen:
                continue
            orb, stack = set(), [x]
            while stack:
                y = stack.pop()
                if y in orb:
                    continue
                orb.add(y)
                for g in H:
                    z = act_key(g, y)
                    if z is not None and z not in orb:
                        stack.append(z)
            seen |= orb
            orbits.append(sorted(orb))
        res[nm] = {'H': len(H), 'orbits': [len(o) for o in orbits], 'n_tie': len(tieset[kk])}
    claim('C4', '★ 群論計數：face 參考之 3 tie 軸 = H_face（階 12）單一軌道（3 = 12/4）；vertex 之 5 = H_r（階 20）單一軌道',
          res['face']['H'] == 12 and res['face']['orbits'] == [3] and res['vertex']['H'] == 20 and res['vertex']['orbits'] == [5],
          '%s' % res)

    # ---------- #2 之直接重述 ----------
    f_all_edge = all(set(ktype[x] for x in tieset[kk]) == {'edge'} for kk in face_keys)
    v_all_edge = all(set(ktype[x] for x in tieset[kk]) == {'edge'} for kk in vertex_keys)
    e_has = sorted(set(tuple(sorted(set(ktype[x] for x in tieset[kk]))) for kk in edge_keys))
    claim('C5', '★ 型別封閉性：face/vertex 參考之 tie 全部 edge 型；edge 參考之 tie 含三型別',
          f_all_edge and v_all_edge and e_has == [('edge', 'face', 'vertex')],
          'face 全 edge = %s ; vertex 全 edge = %s ; edge 之型別集合 = %s' % (f_all_edge, v_all_edge, e_has))

    out = {'rules': RULES, 'B1': {'decomposition': decomp, 'P': P, 'e_values': sorted(e_vals), '15e': 15 * (e_val or 0)},
           'B2': {'H_edge': len(He), 'orbit_sizes': sizes, 'orbits': orbits},
           'B3': {'normalized_squared_spectrum': sorted(norm_spec.items()), 'n_raw_pairs': len(raw_spec),
                  'raw_sample': sorted(raw_spec.items())[:6]},
           'C2': {'edge_vertex': ve, 'edge_face': ef, 'edge_edge': ee,
                  'by_type_pair': {('%s-%s' % k): v for k, v in sorted(tpc.items())}},
           'C1': {'nonedge_orthogonal_pairs': {('%s-%s' % k): tpc.get(k, 0) for k in nonedge_pairs}},
           'C3': {'vertex_ok': v_ok_n, 'face_ok': f_ok_n, 'bad': {'vertex': str(v_bad[:2]), 'face': str(f_bad[:2])}},
           'C3a': {'partition_ok': pa_ok, 'tie_is_third_class': tie_is_c3,
                   'partitions': {str(k): partitions[k] for k in vertex_keys},
                   'endpoint_multiplicity': {str(k): mult[k] for k in vertex_keys}},
           'C3b': {'endpoint_multiset_ok': fb_ok, 'height_uniform': fb_h_ok,
                   'lines': {str(k): fb_lines[k] for k in face_keys},
                   'height_mag2': {str(k): hgt2[k] for k in face_keys},
                   'pair_height_sum': sorted(set(pairrel))}, 'C4': res,
           'C5': {'face_all_edge': f_all_edge, 'vertex_all_edge': v_all_edge, 'edge_type_sets': e_has},
           'tie_types_by_key': {str(kk): dict(typeset[kk]) for kk in keys}, 'claims': CLAIMS}
    with io.open(os.path.join(DATA, '25_r6_geometry.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 116)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 116)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
