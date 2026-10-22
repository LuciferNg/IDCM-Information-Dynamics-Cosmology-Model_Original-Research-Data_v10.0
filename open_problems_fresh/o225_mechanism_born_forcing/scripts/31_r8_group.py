#!/usr/bin/env python3
"""O225 scripts/31 -- R8：Z10 群論身份 + Σf 配對 + Σ_a d ≡ 5 推導 + 零態機制（`r8-group-identity-v1`）。

Part C C1/C2/C3（推導核）｜Part A A1/A2/A3（Z10 群論）｜Part B B1/B2（配對搜尋）｜Part D D1/D2/D3（零態）
精確算術；零浮點；上游 O222 唯讀。用法: /usr/bin/python3 scripts/31_r8_group.py
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
RULES = 'r8-group-identity-v1'
COST = F(123, 88)
EMIN = F(123, 176)
BUDGET = F(10 ** 9)
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def info(msg):
    print('[INFO] %s' % msg, flush=True)


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


def cross3(u, r):
    return (add(mul(u[1], r[2]), neg(mul(u[2], r[1]))),
            add(mul(u[2], r[0]), neg(mul(u[0], r[2]))),
            add(mul(u[0], r[1]), neg(mul(u[1], r[0]))))


def firstsgn(v):
    for c in v:
        s = sgn(c)
        if s:
            return s
    return 0


def qmul(a, b):
    return (a[0] * b[0] + 5 * a[1] * b[1], a[0] * b[1] + b[0] * a[1])


def qinv(a):
    nrm = a[0] * a[0] - 5 * a[1] * a[1]
    return (a[0] / nrm, -a[1] / nrm)


def qsub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def toq(x):
    return (F(x[0]), F(x[1]))


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


def run(s0, Kt, MULt, hxt, pairs, sink=None):
    """逐字複製自 O222 scripts/30_g1g8_gaps.ledger_replay；sink(ctx, s_w, s_r) 於每次比較。"""
    L = []
    s = s0
    rem = BUDGET
    hits = 0
    for (a, b) in pairs:
        spent = 0
        for ctx in (a, b):
            if L and L[-1][0] == ctx:
                hits += 1
                if sink is not None:
                    sink(ctx, L[-1][2], s)
                continue
            if rem - COST * spent < EMIN:
                raise RuntimeError('terminal')
            L.append((ctx, Kt[s][ctx], s))
            s = MULt[s][hxt[ctx]]
            spent += 1
        _c, _v, s_at = L.pop()
        s = s_at
        if L and L[-1][0] == b:
            hits += 1
            if sink is not None:
                sink(b, L[-1][2], s)
        else:
            if rem - COST * spent < EMIN:
                raise RuntimeError('terminal')
            L.append((b, Kt[s][b], s))
            s = MULt[s][hxt[b]]
            spent += 1
        rem -= COST * spent
    return {'hits': hits, 'len': len(L)}


def main():
    os.makedirs(DATA, exist_ok=True)
    print('=' * 116)
    print('O225 scripts/31 -- R8: Z10 group identity + Sigma-f pairing + derivation of Sigma_a d == 5   (%s)' % RULES)
    print('=' * 116, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'r8_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    G, _ig, _M2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'r8_a2').build_group()
    n, ncol = len(K), len(K[0])
    KV = [mm.rot_ref(g, U[0]) for g in G]
    pairs = [(a, b) for a in range(ncol) for b in range(ncol)]
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(sgn(add(U[i][t], U[j][t])) == 0 for t in range(3)):
                partner[i] = j
    key = [min(a, partner[a]) for a in range(ncol)]
    keys = sorted(set(key))
    ktype = {kk: types[kk] for kk in keys}
    tie = [[dot3(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [firstsgn(KV[s]) for s in range(n)]
    gam = [{a: firstsgn(cross3(U[a], KV[s])) for a in range(ncol) if tie[s][a]} for s in range(n)]
    dind = [[(1 if (gam[s][a] != eps[s]) else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]
    Kp = [[firstsgn((lambda dd, cc: (dd, cc[0], cc[1], cc[2]))(dot3(U[a], KV[s]), cross3(U[a], KV[s])))
           for a in range(ncol)] for s in range(n)]

    # ---------- Part C ----------
    dev1 = 0
    ntie_cols = []
    for s in range(n):
        cnt = 0
        for a in range(ncol):
            if tie[s][a]:
                cnt += 1
                if dind[s][partner[a]] != 1 - dind[s][a]:
                    dev1 += 1
                if not tie[s][partner[a]]:
                    dev1 += 1
        ntie_cols.append(cnt)
    claim('C1', '★ 對徑配對律（推導）：d(s,ā) = 1 − d(s,a) 且 tie(s,a) ⟺ tie(s,ā)（逐 tie 條目 0 偏離）',
          dev1 == 0, '逐條目偏離 = %d ; 樣本 d 對：%s'
          % (dev1, [(a, dind[0][a], dind[0][partner[a]]) for a in range(ncol) if tie[0][a]][:5]))
    claim('C2', '★ 每態 tie 條目數 = 10（推導：⟂ 於 KV[s] 之軸 = 5 edge 線 × 2 取向）',
          set(ntie_cols) == {10}, '每態 tie 條目之值集 = %s' % sorted(set(ntie_cols)))
    sda = [sum(dind[s]) for s in range(n)]
    claim('C3', '★★ ∴ 每態 Σ_a d = 10/2 = 5（推導；並解釋 R7 之 Σ_tie d = 600 = 1200/2）',
          set(sda) == {5} and sum(sda) == 600, 'Σ_a d 之值集 = %s ; 全體 = %d ; tie 條目總 = %d'
          % (sorted(set(sda)), sum(sda), sum(ntie_cols)))

    # ---------- 協定 pass：f_tf / f_ft / f_tt ----------
    recs = []
    for s0 in range(n):
        st = {'tf': 0, 'ft': 0, 'tt': 0, 'ntf': 0, 'nft': 0, 'ntt': 0,
              'nztf': 0, 'nzft': 0, 'nztt': 0}

        def sink(ctx, sw, sr, st=st):
            tw, tr = tie[sw][ctx], tie[sr][ctx]
            if tw and tr:
                f = (1 if dind[sr][ctx] != dind[sw][ctx] else 0) * eps[sr] * eps[sw]
                st['tt'] += f
                st['ntt'] += 1
                if f:
                    st['nztt'] += 1
            elif tr:
                f = dind[sr][ctx] * eps[sr] * K[sw][ctx]
                st['tf'] += f
                st['ntf'] += 1
                if f:
                    st['nztf'] += 1
            elif tw:
                f = dind[sw][ctx] * eps[sw] * K[sr][ctx]
                st['ft'] += f
                st['nft'] += 1
                if f:
                    st['nzft'] += 1
        run(s0, K, MUL, hx, pairs, sink)
        st['delta'] = st['tf'] + st['ft'] + st['tt']
        recs.append(st)
    f_tf = [r['tf'] for r in recs]
    f_ft = [r['ft'] for r in recs]
    f_tt = [r['tt'] for r in recs]
    dsum = [r['delta'] for r in recs]
    d24 = json.load(io.open(os.path.join(DATA, '24_r6_mechanism.json'), encoding='utf-8'))
    rz = [s for s in range(n) if d24['delta'][s] == 0]
    info('Σ f_tf = %d ; Σ f_ft = %d ; Σ f_tt = %d ; Δ 逐態 == R6 = %s'
         % (sum(f_tf), sum(f_ft), sum(f_tt), all(dsum[s] == d24['delta'][s] for s in range(n))))

    # ---------- 群論基礎 ----------
    ident_l = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))]
    identity = ident_l[0]
    inv = {}
    for s in range(n):
        for t in range(n):
            if MUL[s][t] == identity:
                inv[s] = t
                break
    cen = [i for i in range(n) if i not in ident_l and all(MUL[i][j] == MUL[j][i] for j in range(n))][0]

    def order(s):
        x, k = s, 1
        while x != identity:
            x = MUL[x][s]
            k += 1
        return k
    orders = [order(s) for s in range(n)]
    # A₅ 態類（2I 共軛類模中心合併）
    rawclass = {}
    for s in range(n):
        conj = set()
        for h in range(n):
            conj.add(MUL[MUL[h][s]][inv[h]])
        conj |= {MUL[x][cen] for x in conj}
        rawclass[s] = frozenset(conj)
    rep = {}
    cls_of = {}
    for s in range(n):
        r = min(rawclass[s])
        rep[r] = rawclass[s]
        cls_of[s] = r
    ncls = len(rep)

    def commute(s, t):
        p, q = MUL[s][t], MUL[t][s]
        return p == q or MUL[p][cen] == q or p == MUL[q][cen]
    info('群：|2I| = %d ; 恆等 = %d ; 中心元素 = %d ; A₅ 態類數 = %d ; 階值集 = %s'
         % (n, identity, cen, ncls, sorted(set(orders))))

    # ---------- Part A ----------
    Z10 = [s for s in range(n) if f_tf[s] + f_ft[s] == 0]
    zci = all((MUL[s][cen] in Z10) == (s in Z10) for s in range(n))
    zcls = sorted(set(cls_of[s] for s in Z10))
    ordZ = sorted(set(orders[s] for s in Z10))
    commZ = all(commute(Z10[i], Z10[j]) for i in range(len(Z10)) for j in range(i + 1, len(Z10)))
    claim('A1', '★★ 預測（見數前）：Z10 中心不變 ⟹ 5 個 A₅ 態類；且構成 A₅ 中某 5 階子群（Sylow 5）之陪集 '
                '⟹ ①全部 10 態之群階 = 10 ②5 個態類兩兩可交換',
          len(Z10) == 10 and zci and len(zcls) == 5 and ordZ == [10] and commZ,
          '|Z10| = %d ; 中心不變 = %s ; 態類數 = %d ; 階值集 = %s ; 兩兩可交換 = %s ; 態 = %s'
          % (len(Z10), zci, len(zcls), ordZ, commZ, Z10))
    sig = {str(s): {'line': None, 'f_tf': f_tf[s], 'f_ft': f_ft[s], 'f_tt': f_tt[s], 'delta': dsum[s],
                    'n_tf': recs[s]['ntf'], 'n_ft': recs[s]['nft'], 'n_tt': recs[s]['ntt'], 'order': orders[s],
                    'cls': cls_of[s]} for s in Z10}
    vertex_keys = [kk for kk in keys if ktype[kk] == 'vertex']

    def line_of(s):
        for kk in vertex_keys:
            if same_line(U[kk], KV[s]):
                return kk
        return None
    for s in range(n):
        if str(s) in sig:
            sig[str(s)]['line'] = line_of(s)
    # 6 條線 ↔ 6 個 Sylow-5：線 k 之穩定子（階 20）內之階 10 元素 ⟹ ⟨x⟩ 階 10（提升 C_5）
    syl = {}
    z10_frozen = frozenset(Z10)
    coset_hits = []
    for kk in vertex_keys:
        stab = [g for g in range(n) if same_line(mm.rot_ref(G[g], U[kk]), U[kk])]
        o10 = [g for g in stab if orders[g] == 10]
        H, cls_h = [], []
        if o10:
            x = o10[0]
            y = identity
            for _ in range(10):
                H.append(y)
                cls_h.append(cls_of[y])
                y = MUL[y][x]
        Hset = set(H)
        cosets = {}
        if len(Hset) == 10:
            for g in range(n):
                cosets.setdefault(frozenset(MUL[g][h] for h in H), g)
        hit = [g for cs, g in cosets.items() if cs == z10_frozen]
        if hit:
            coset_hits.append((kk, hit[0]))
        syl[kk] = {'stab_order': len(stab), 'n_order10': len(o10), 'subgroup_classes': sorted(set(cls_h)),
                   'n_cosets': len(cosets), 'coset_rep': hit[0] if hit else None}

    zsub = coset_hits[0][0] if coset_hits else None
    info('A2 報告：Z10 為某線之 Sylow-5 提升（階 10 子群）之**陪集**之命中 = %s（6 線 × 12 陪集；Z10 之 5 態類 = %s）'
         % (coset_hits, zcls))
    info('A2 報告：Z10 ∩ 零態 = %s ; 6 線之 Sylow 提升（穩定子階, 階10 元素數, 陪集數）= %s'
         % (sorted(set(Z10) & set(rz)), {str(k): (v['stab_order'], v['n_order10'], v['n_cosets']) for k, v in syl.items()}))
    info('A2 報告：Z10 逐態簽名 = %s' % sig)
    claim('A2', '報告：Z10 逐態簽名 + 與零態之交集 + 6 線 ↔ Sylow-5 提升之陪集檢驗（報告項，無預測）',
          len(sig) == 10, '交集 = %s ; 陪集命中 = %s' % (sorted(set(Z10) & set(rz)), coset_hits))
    claim('A3', '★★ 預測（見數前）：Z10 之 5 類構成 A₅ 中某 5 階子群之**陪集**（等價：Z10 = 2I 中某階 10 子群之陪集）',
          len(coset_hits) > 0 and ordZ == [10],
          '階值集 = %s ; 5 類 = %s ; 陪集命中（線, 代表）= %s ; 命中數 = %d'
          % (ordZ, zcls, coset_hits, len(coset_hits)))

    # ---------- Part B：配對搜尋 ----------
    gr = [g for g in range(n) if all(f_tf[MUL[s][g]] == -f_tf[s] for s in range(n))]
    gl = [g for g in range(n) if all(f_tf[MUL[g][s]] == -f_tf[s] for s in range(n))]
    gr_ft = [g for g in range(n) if all(f_ft[MUL[s][g]] == -f_ft[s] for s in range(n))]
    gl_ft = [g for g in range(n) if all(f_ft[MUL[g][s]] == -f_ft[s] for s in range(n))]
    both = sorted(set(gr) & set(gl))
    claim('B1', '★ 預測（見數前）：存在非中心階 2 之 g 使 f_tf(s·g) = −f_tf(s) 對全部 120 態成立；'
                '且同一 g 亦反號 f_ft',
          len(gr) > 0 and all(orders[g] == 2 for g in gr) and any(g in gr_ft for g in gr),
          '右乘命中 = %s（階 %s）; 左乘命中 = %s（階 %s）; f_ft 右乘命中 = %s ; f_ft 左乘命中 = %s'
          % (gr, [orders[g] for g in gr], gl, [orders[g] for g in gl], gr_ft, gl_ft))
    # 值配對結構（若 B1 空）：找出 f_tf 之配對函數
    pairing = {}
    for s in range(n):
        cand = [t for t in range(n) if f_tf[t] == -f_tf[s]]
        pairing[s] = cand
    info('B2 報告：f_tf 值配對候選數之值集 = %s ; 命中集合大小（右）%d（左）%d ; 左∩右 = %s'
         % (sorted(set(len(v) for v in pairing.values())), len(gr), len(gl), both))
    claim('B2', '報告：配對搜尋之完整結果（g 之集合大小、階分佈；f_tf 值配對候選數）（報告項，無預測）',
          True, '右乘 %s ; 左乘 %s ; f_tf 值配對候選數值集 = %s'
          % (gr, gl, sorted(set(len(v) for v in pairing.values()))))

    # ---------- Part D：零態 ----------
    l3z = [40, 100]
    l5z = [9, 15, 77, 87]
    d1 = all(recs[s]['nzft'] == 0 for s in l3z)
    claim('D1', '★ 預測（見數前）：線 3 零態 {40,100} 之 f_ft = 0 係 **pointwise**（全部 (F,T) 事件貢獻 = 0）',
          d1 and all(f_ft[s] == 0 for s in l3z),
          '(F,T) 非零貢獻數 = %s ; f_ft = %s ; n_ft = %s'
          % ([recs[s]['nzft'] for s in l3z], [f_ft[s] for s in l3z], [recs[s]['nft'] for s in l3z]))
    d2 = all(recs[s]['nztt'] == 0 for s in l5z)
    claim('D2', '★ 核（R7 探索已知 tt± = 0）：線 5 零態 {9,15,77,87} 之 f_tt = 0 係 **pointwise**',
          d2 and all(f_tt[s] == 0 for s in l5z),
          '(T,T) 非零貢獻數 = %s ; f_tt = %s ; n_tt = %s'
          % ([recs[s]['nztt'] for s in l5z], [f_tt[s] for s in l5z], [recs[s]['ntt'] for s in l5z]))
    zdat = {str(s): {'line': line_of(s), 'order': orders[s], 'cls': cls_of[s], 'S': None,
                     'f_tf': f_tf[s], 'f_ft': f_ft[s], 'f_tt': f_tt[s], 'in_Z10': s in Z10,
                     'nz_tf': recs[s]['nztf'], 'nz_ft': recs[s]['nzft'], 'nz_tt': recs[s]['nztt']}
            for s in rz}
    info('D3 報告：零態群論資料 = %s' % zdat)
    info('D3 報告：零態之態類 = %s ; 其中 ⊆ Z10 = %s ; 線 3 之零態在 Z10 = %s ; 線 5 之零態在 Z10 = %s'
         % (sorted(set(cls_of[s] for s in rz)), sorted(set(cls_of[s] for s in rz)) == sorted(set(cls_of[s] for s in Z10)),
            [s in Z10 for s in l3z], [s in Z10 for s in l5z]))
    claim('D3', '報告：6 零態之群論資料 + 「零態類 ⊆ Z10」之檢驗 + 線 3／線 5 之機制分野（報告項，無預測）',
          True, '零態類 = %s ; Z10 類 ⊇ 零態類 = %s ; 線3 零態在 Z10 = %s ; 線5 零態在 Z10 = %s'
          % (sorted(set(cls_of[s] for s in rz)),
             set(cls_of[s] for s in rz) <= set(cls_of[s] for s in Z10),
             [s in Z10 for s in l3z], [s in Z10 for s in l5z]))

    out = {'rules': RULES, 'C1_dev': dev1, 'C2_tie_per_state': sorted(set(ntie_cols)),
           'C3_per_state_d': sorted(set(sda)), 'C3_total_d': sum(sda),
           'A1': {'Z10': Z10, 'centre_inv': zci, 'n_classes': len(zcls), 'orders': ordZ, 'commuting': commZ,
                  'classes': zcls},
           'A2': {'signatures': sig, 'intersect_zeros': sorted(set(Z10) & set(rz)), 'sylow': {str(k): v for k, v in syl.items()},
                  'z10_coset_line': zsub},
           'A3': {'coset_hits': [[int(a), int(b)] for a, b in coset_hits], 'zsub': zsub},
           'B1': {'right': gr, 'left': gl, 'right_ft': gr_ft, 'left_ft': gl_ft, 'both': both},
           'B2': {'pair_candidate_counts': sorted(set(len(v) for v in pairing.values()))},
           'D1': {'line3': {'nz_ft': [recs[s]['nzft'] for s in l3z], 'f_ft': [f_ft[s] for s in l3z]}},
           'D2': {'line5': {'nz_tt': [recs[s]['nztt'] for s in l5z], 'f_tt': [f_tt[s] for s in l5z]}},
           'D3': {'zero_data': zdat, 'zero_classes': sorted(set(cls_of[s] for s in rz)),
                  'z10_classes': zcls, 'classes_subset': set(cls_of[s] for s in rz) <= set(cls_of[s] for s in Z10)},
           'f_tf': f_tf, 'f_ft': f_ft, 'f_tt': f_tt, 'delta': dsum,
           'orders': orders, 'cls_of': cls_of, 'line_of_state': [line_of(s) for s in range(n)],
           'orders_hist': {str(o): sum(1 for x in orders if x == o) for o in sorted(set(orders))},
           'n_classes_total': ncls, 'claims': CLAIMS}
    with io.open(os.path.join(DATA, '31_r8_group.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 116)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 116)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
