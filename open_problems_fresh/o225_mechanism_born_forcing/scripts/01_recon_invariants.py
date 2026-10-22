#!/usr/bin/env python3
"""O225 scripts/01 -- 唯讀重算 O222 已引用之不變量（recon inventory）。

目的：把 B3 所講嘅障礙講清楚之前，先用本 o 自己嘅精確算術（Fractions/整數，零浮點）
重算 O222 文檔已發表嘅每個數字，並額外量度「列和」精確結構。

唯讀聲明：只 import O222 之輸入載入器（09_a2_rollback）與 12_b5_budget.load_machine 之構造，
唔執行 O222 之 main()，唔寫任何 O222 檔案。

用法:  /usr/bin/python3 scripts/01_recon_invariants.py
"""
import importlib.util
import io
import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
LOGS = os.path.join(ROOT, 'logs')
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
O222S = os.path.join(O222, 'scripts')

CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s%s' % ('PASS' if ok else 'FAIL', tag, name,
                              ('  --  ' + detail) if detail else ''), flush=True)
    return bool(ok)


def load_o222(script):
    spec = importlib.util.spec_from_file_location('o222_' + script[:-3], os.path.join(O222S, script))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_K(m):
    """逐字複製 O222 scripts/12_b5_budget.load_machine 之讀出表構造（凍結定義）"""
    axes, U, ids, types, hvec = m.load_inputs()
    G, idx, MUL = m.build_group()
    hydx = [idx[m.qkey(h)] for h in hvec]
    KV = [m.rot_ref(q, U[0]) for q in G]
    K = []
    for i in range(120):
        r = KV[i]
        row = []
        for u in U:
            dot = m.add(m.add(m.mul(u[0], r[0]), m.mul(u[1], r[1])), m.mul(u[2], r[2]))
            s = m.sgn(dot)
            if s == 0:
                for comp in r:
                    sc = m.sgn(comp)
                    if sc:
                        s = sc
                        break
            row.append(s)
        K.append(row)
    return m, K, MUL, hydx, ids, types, U


def rank_rational(rows):
    M = [[F(x) for x in r] for r in rows]
    nr = len(M)
    nc = len(M[0]) if nr else 0
    piv = 0
    for c in range(nc):
        p = None
        for r in range(piv, nr):
            if M[r][c] != 0:
                p = r
                break
        if p is None:
            continue
        M[piv], M[p] = M[p], M[piv]
        pv = M[piv][c]
        M[piv] = [x / pv for x in M[piv]]
        for r in range(nr):
            if r != piv and M[r][c] != 0:
                f = M[r][c]
                M[r] = [a - f * b for a, b in zip(M[r], M[piv])]
        piv += 1
        if piv == nr:
            break
    return piv


def main():
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    print('=' * 100)
    print('O225 scripts/01 -- recon inventory (only-read re-derivation of O222 cited invariants)')
    print('=' * 100, flush=True)

    m = load_o222('09_a2_rollback.py')
    m, K, MUL, hydx, ids, types, U = build_K(m)
    nS, nA = len(K), len(K[0])
    out = {'rules': 'o225-recon-v1', 'K_shape': [nS, nA], 'axis_ids': ids, 'axis_types': types}

    # ---- cited in O222 docs/43 section 2(a) and docs/13 P2d / docs/19 C2,C5 ----
    vals = {}
    for row in K:
        for v in row:
            vals[v] = vals.get(v, 0) + 1
    claim('R1', 'K value multiset = {+1: 3720, -1: 3720} (完全平衡)', vals == {1: 3720, -1: 3720},
          'multiset = %s' % sorted(vals.items()))
    claim('R2', 'K 值集 size = 2', len(vals) == 2, 'values = %s' % sorted(vals))
    colsum = [sum(K[s][a] for s in range(nS)) for a in range(nA)]
    pcount = [sum(1 for s in range(nS) if K[s][a] == 1) for a in range(nA)]
    claim('R3', '62/62 欄（軸）之 sum_s K[s][a] = 0 且 +1 個數 = 60', set(colsum) == {0} and set(pcount) == {60},
          'colsum distinct = %s ; +1 count distinct = %s' % (sorted(set(colsum)), sorted(set(pcount))))
    rowsum = [sum(r) for r in K]
    out['rowsum_distinct'] = sorted(set(rowsum))
    out['rowsum_histogram'] = {str(v): rowsum.count(v) for v in sorted(set(rowsum))}
    claim('R4b', '★ 本 o 新量度：列和 R(s) = sum_a K[s,a] 恰為兩值 {+10, -10}，60/60 分裂',
          sorted(set(rowsum)) == [-10, 10] and rowsum.count(10) == 60,
          'distinct = %s ; histogram = %s ; Delta = %d' %
          (sorted(set(rowsum)), out['rowsum_histogram'], max(rowsum) - min(rowsum)))
    claim('R4', '120/120 列和 ≠ 1（O222 docs/43 §二(a)）', all(x != 1 for x in rowsum),
          'row sums = %s' % sorted(set(rowsum)))
    ind = [sum((1 + v) // 2 for v in r) for r in K]
    out['indicator_rowsum_distinct'] = sorted(set(ind))
    claim('R5', '「(1+K)/2 投影」之列和 = 26 / 36（= (62 -/+ 10)/2），120/120 ≠ 1',
          sorted(set(ind)) == [26, 36],
          'distinct = %s' % sorted(set(ind)))
    rk = rank_rational(K)
    claim('R6', 'rank_Q(K) = 6（O222 docs/19 C5）', rk == 6, 'rank_Q(K) = %d' % rk)
    R1s = set(tuple(r) for r in K)
    claim('R7', '相異 row = 12（O222 docs/19 C5）', len(R1s) == 12, 'distinct rows = %d' % len(R1s))
    eq = comp = neit = 0
    Rl = [tuple(r) for r in K]
    for i in range(nS):
        for j in range(i + 1, nS):
            if Rl[i] == Rl[j]:
                eq += 1
            elif all(a == -b for a, b in zip(Rl[i], Rl[j])):
                comp += 1
            else:
                neit += 1
    out['row_pair_classes'] = {'equal': eq, 'complementary': comp, 'neither': neit}
    claim('R8', 'row 對：equal 540 / complementary 600 / neither 6000（O222 docs/19 C5「6000/7140 非等非互補」）',
          (eq, comp, neit) == (540, 600, 6000), 'equal=%d complementary=%d neither=%d' % (eq, comp, neit))

    # ---- 「全 1 向量是否落喺 K 之行空間」= 複讀出/per-context 相位修復之可解性 ----
    aug = [list(r) + [1] for r in K]
    rk_aug = rank_rational(aug)
    out['rank_K_augmented_by_ones'] = rk_aug
    claim('R9', 'rank[K | 1] = rank(K) ⟺ 全 1 向量 ∈ 行空間（複相位修復存在性之充要條件，R1 機器用）',
          True, 'rank[K|1] = %d ; rank(K) = %d ⟹ 全 1 ∈ range(K) = %s' %
          (rk_aug, rk, rk_aug == rk))

    # ---- 軸型別子表（out-of-sample 用） ----
    sub = {}
    for tp in sorted(set(types)):
        idxs = [a for a in range(nA) if types[a] == tp]
        Sub = [[K[s][a] for a in idxs] for s in range(nS)]
        rs = [sum(r) for r in Sub]
        sub[tp] = {'n_axes': len(idxs), 'rowsum_distinct': sorted(set(rs)),
                   'delta': max(rs) - min(rs), 'm_min_pred': (max(rs) - min(rs) + 1) // 2}
    out['axis_type_subtables'] = sub
    for tp in sorted(sub):
        print('  [INFO] axis type %-6s : n=%2d  rowsum distinct=%s  Delta=%d  ceil(Delta/2)=%d'
              % (tp, sub[tp]['n_axes'], sub[tp]['rowsum_distinct'], sub[tp]['delta'], sub[tp]['m_min_pred']))

    # ---- 中心 Z2 與 theta(s) = sign(R(s)) 之關係 ----
    GC, idxC, MULC = m.build_group()
    zkey = ((F(-1), F(0)), (F(0), F(0)), (F(0), F(0)), (F(0), F(0)))   # -1 in 2T
    ikkey = ((F(1), F(0)), (F(0), F(0)), (F(0), F(0)), (F(0), F(0)))    # +1 in 2T
    i_id = idxC.get(ikkey)
    zc = idxC.get(zkey)
    out['identity_index'] = i_id
    out['center_index'] = zc
    print('  [INFO] identity index = %s ; center (-1) index = %s' % (i_id, zc))
    hz = None
    for a, h in enumerate(hydx):
        if h == zc:
            hz = a
            break
    theta = [1 if x > 0 else -1 for x in rowsum]
    if hz is not None:
        flip = sum(1 for s in range(nS) if theta[MUL[s][hz]] == -theta[s])
        same = sum(1 for s in range(nS) if theta[MUL[s][hz]] == theta[s])
        out['center_partner'] = {'h_index': hz, 'axis_id': ids[hz], 'axis_type': types[hz],
                                 'flip': flip, 'same': same}
        claim('R10', '★ theta(s) = sign(R(s)) 喺中心元素 -1 之伴隨下完全翻轉（theta 為中心 Z2 特徵）',
              flip == nS and same == 0,
              'z-axis = %s (%s) ; flip = %d/120 ; same = %d' % (ids[hz], types[hz], flip, same))
    else:
        claim('R10', '中心元素 -1 之伴隨軸唔喺 62 軸集內', True,
              'no axis with h == center index %d (資訊性，非判據)' % zc)

    # ---- R11/R12: theta 之 Z2 奇偶性 + 左平移穩定子 ----
    if zc is not None:
        cmul = MUL
        flip = sum(1 for s in range(nS) if theta[cmul[s][zc]] == -theta[s])
        same = sum(1 for s in range(nS) if theta[cmul[s][zc]] == theta[s])
        out['theta_center_parity'] = {'flip': flip, 'same': same}
        claim('R11', '★ theta 喺中心元素 -1 之左平移下不變（rot_ref 對 q 與 -q 同值 ⟹ 列 s 與列 -s 相同）',
              flip == 0 and same == nS, 'flip = %d/120 ; same = %d' % (flip, same))
    stab = []
    for h in range(nS):
        if all(theta[MUL[s][h]] == theta[s] for s in range(nS)):
            stab.append(h)
    out['theta_stabilizer_order'] = len(stab)
    out['theta_stabilizer_contains_center'] = (zc in stab) if zc is not None else None
    print('  [INFO] theta 之左平移穩定子階 = %d ; 含中心元素 = %s'
          % (len(stab), out['theta_stabilizer_contains_center']))

    # ---- R14: K 之相異 row 重數（相異 row = 12，每款出現 10 次） ----
    cnt = {}
    for r in Rl:
        cnt[r] = cnt.get(r, 0) + 1
    mult = sorted(set(cnt.values()))
    out['distinct_row_multiplicity'] = {'n_distinct': len(cnt), 'multiplicities': mult}
    claim('R14', '★ K 恰有 12 個相異 row，每款重數恰為 10（= 120/12 = |Stab(theta)|）',
          len(cnt) == 12 and mult == [10],
          'distinct = %d ; multiplicities = %s' % (len(cnt), mult))

    # ---- R15: 同一 row 之態集 = Stab(theta) 之左陪集？ ----
    ok_coset = True
    for r, c in cnt.items():
        support = set(s for s in range(nS) if Rl[s] == r)
        if len(support) != 10:
            ok_coset = False
            break
        sset = sorted(support)
        anchor = sset[0]
        coset = set(MUL[anchor][h] for h in stab)
        if coset != support:
            ok_coset = False
            break
    claim('R15', '★ 每個 row 類 = Stab(theta)（階 10 子群）之一個左陪集', ok_coset,
          'coset test over all 12 row classes = %s' % ok_coset)

    # ---- R16: 10 個穩定子元素之階分佈 ----
    order_hist = {}
    for h in stab:
        k, cur = 1, MUL[h][h]
        while cur != h:
            cur = MUL[cur][h]
            k += 1
            if k > 200:
                break
        order_hist[k] = order_hist.get(k, 0) + 1
    out['theta_stabilizer_orders'] = {str(k): order_hist[k] for k in sorted(order_hist)}
    print('  [INFO] Stab(theta) 之元素階分佈 = %s' % out['theta_stabilizer_orders'])

    # ---- 邊軸塊獨立承載 Delta ----
    eidx = [a for a in range(nA) if types[a] == 'edge']
    erow = [sum(K[s][a] for a in eidx) for s in range(nS)]
    out['edge_block'] = {'n_axes': len(eidx), 'rowsum_distinct': sorted(set(erow)),
                         'plus_counts': sorted(set((x + len(eidx)) // 2 for x in erow))}
    claim('R13', '★ Delta 完全由 30 條邊軸承載（vertex 12 + face 20 塊之列和恆 0）',
          sorted(set(erow)) == [-10, 10] and sub['vertex']['delta'] == 0 and sub['face']['delta'] == 0,
          'edge block row sums = %s ; edge +1 count per row = %s'
          % (sorted(set(erow)), out['edge_block']['plus_counts']))

    out['claims'] = CLAIMS
    with io.open(os.path.join(DATA, '01_recon_invariants.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 100)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 100)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
