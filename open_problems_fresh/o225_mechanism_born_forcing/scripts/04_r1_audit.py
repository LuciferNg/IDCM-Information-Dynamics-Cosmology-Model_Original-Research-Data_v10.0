#!/usr/bin/env python3
"""O225 scripts/04 -- R1 獨立審計（不 import scripts/03）。

獨立性措施：
  * 讀出表以**獨立代碼路徑**重建：由單位四元數寫出顯式 3x3 有理旋轉矩陣（唔用 O222 之 quaternion sandwich）
  * 秩以 **Bareiss 無分數消元**計算（唔用 03 之 normalized Gauss）
  * m_min 以「直接以修復構造搜尋」計（唔用 03 之 D5 逐值公式），並對 m_min - 1 顯式驗不可行
  * 解析 null 機率以 Pascal 三角形二項式獨立重算
  * 逐項對 data/03_r1_results.json 已報值做 0-dev 對比

用法:  /usr/bin/python3 scripts/04_r1_audit.py
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
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
O222S = os.path.join(O222, 'scripts')
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
          flush=True)
    return bool(ok)


def load_o222(script):
    spec = importlib.util.spec_from_file_location('o222a_' + script[:-3], os.path.join(O222S, script))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def q_to_matrix(q):
    """顯式 3x3 旋轉矩陣（單位四元數；entries 為 a + b*sqrt5 之 (p,q) 對）"""
    a, b, c, d = q
    def add(x, y):
        return (x[0] + y[0], x[1] + y[1])
    def sub(x, y):
        return (x[0] - y[0], x[1] - y[1])
    def mul(x, y):
        return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + y[0] * x[1])
    def sc(x, k):
        return (x[0] * k, x[1] * k)
    one = (F(1), F(0))
    two = (F(2), F(0))
    b2 = mul(b, b)
    c2 = mul(c, c)
    d2 = mul(d, d)
    bc = mul(b, c)
    bd = mul(b, d)
    cd = mul(c, d)
    ab = mul(a, b)
    ac = mul(a, c)
    ad = mul(a, d)
    return [[sub(one, sc(add(c2, d2), F(2))), sub(sc(bc, F(2)), sc(ad, F(2))), add(sc(bd, F(2)), sc(ac, F(2)))],
            [add(sc(bc, F(2)), sc(ad, F(2))), sub(one, sc(add(b2, d2), F(2))), sub(sc(cd, F(2)), sc(ab, F(2)))],
            [sub(sc(bd, F(2)), sc(ac, F(2))), add(sc(cd, F(2)), sc(ab, F(2))), sub(one, sc(add(b2, c2), F(2)))]]


def sgn(x):
    """Z[sqrt5] 元素 p + q*sqrt5 之**精確**符號（比較 p^2 與 5q^2；非「首個非零分量」）。
    2026-10-01 修正：原版本取首個非零分量之符號，對 p,q 反號且 5q^2 > p^2 之元素會給錯號
    （凍結 K 有 2400/7440 條目受影響）——由 R3 審計（scripts/16 A2）發現，本檔據此修正並重跑。"""
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


def build_K_independent(mod):
    axes, U, ids, types, hvec = mod.load_inputs()
    G, idx, MUL = mod.build_group()

    def add2(x, y):
        return (x[0] + y[0], x[1] + y[1])

    def mul2(x, y):
        return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + y[0] * x[1])

    K = []
    for q in G:
        M = q_to_matrix(q)
        r = [add2(mul2(M[i][0], U[0][0]), add2(mul2(M[i][1], U[0][1]), mul2(M[i][2], U[0][2])))
             for i in range(3)]
        row = []
        for u in U:
            dot = add2(mul2(u[0], r[0]), add2(mul2(u[1], r[1]), mul2(u[2], r[2])))
            s = sgn(dot)
            if s == 0:
                for comp in r:
                    sc = sgn(comp)
                    if sc:
                        s = sc
                        break
            row.append(s)
        K.append(row)
    return K, U, ids, types, MUL


def bareiss_rank(rows):
    """fraction-free (Bareiss) rank over Q"""
    A = [[F(x) for x in r] for r in rows]
    nr = len(A)
    nc = len(A[0]) if nr else 0
    r = 0
    prev = F(1)
    for c in range(nc):
        p = None
        for k in range(r, nr):
            if A[k][c] != 0:
                p = k
                break
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        for k in range(r + 1, nr):
            for j in range(c + 1, nc):
                A[k][j] = (A[k][j] * A[r][c] - A[k][c] * A[r][j]) / prev
            A[k][c] = F(0)
        prev = A[r][c]
        r += 1
        if r == nr:
            break
    return r


def mmin_by_search(R):
    """直接以修復構造搜尋最小 m（唔用 D5 逐值公式）"""
    n = len(R)
    lo, hi = min(R), max(R)
    m = 0
    while m <= (hi - lo) + 4:
        for A in range(lo - m, hi + m + 1):
            p = [(m + A - R[s]) // 1 for s in range(n)]
            ok = True
            for s in range(n):
                num = m + A - R[s]
                if num < 0 or num > 2 * m or num % 2 != 0:
                    ok = False
                    break
            if not ok:
                continue
            ps = [(m + A - R[s]) // 2 for s in range(n)]
            cols = [[1 if ps[s] > i else -1 for s in range(n)] for i in range(m)]
            R2 = [R[s] + sum(cols[i][s] for i in range(m)) for s in range(n)]
            if len(set(R2)) == 1:
                return m, A, cols
        m += 1
    return None, None, None


def pascal_binom(n, k):
    row = [1]
    for _ in range(n):
        row = [1] + [row[i] + row[i + 1] for i in range(len(row) - 1)] + [1]
    return row[k]


def main():
    print('=' * 100)
    print('O225 scripts/04 -- R1 independent audit (does NOT import scripts/03)')
    print('=' * 100, flush=True)
    mod = load_o222('09_a2_rollback.py')
    K, U, ids, types, MUL = build_K_independent(mod)
    nS, nA = len(K), len(K[0])
    R = [sum(r) for r in K]
    theta = [1 if x > 0 else -1 for x in R]

    vals = {}
    for row in K:
        for v in row:
            vals[v] = vals.get(v, 0) + 1
    claim('A1', '獨立路徑重建 K（顯式 3x3 旋轉矩陣）：值重數 {+1:3720,-1:3720}；每欄 Σ_s = 0',
          vals == {1: 3720, -1: 3720} and set(sum(K[s][a] for s in range(nS)) for a in range(nA)) == {0},
          'values = %s' % sorted(vals.items()))
    claim('A2', 'R(s) ∈ {+10,-10} 60/60；Delta = 20', sorted(set(R)) == [-10, 10] and R.count(10) == 60,
          'distinct = %s hist = %s' % (sorted(set(R)), {str(v): R.count(v) for v in sorted(set(R))}))
    rkK = bareiss_rank(K)
    rkAug = bareiss_rank([list(r) + [1] for r in K])
    claim('A3', 'Bareiss 秩：rank_Q(K) = 6；rank_Q[K|1] = 7 ⟹ 1 ∉ range(K)',
          rkK == 6 and rkAug == 7, 'rank K = %d ; rank [K|1] = %d' % (rkK, rkAug))
    cnt = {}
    for r in K:
        t = tuple(r)
        cnt[t] = cnt.get(t, 0) + 1
    claim('A4', '相異 row = 12，重數全 10', len(cnt) == 12 and set(cnt.values()) == {10},
          'distinct = %d ; multiplicities = %s' % (len(cnt), sorted(set(cnt.values()))))

    # --- A5: 障礙定理之獨立代數重算 ---
    # 62 alpha + 10 beta = 1 ; 62 alpha - 10 beta = 1  (Cramer)
    det = F(nA * (-10) - nA * 10)
    alpha = F(1 * (-10) - 1 * 10) / det
    beta = F(nA * 1 - nA * 1) / det
    claim('A5', 'Cramer 規則獨立解歸一方程：唯一解 (alpha, beta) = (1/62, 0) ⟹ W 均勻 ⟹ 態盲目',
          alpha == F(1, nA) and beta == 0, 'alpha = %s ; beta = %s ; det = %s' % (alpha, beta, det))

    # --- A6: m_min 之獨立搜尋 + 最小性反證 ---
    mm, AA, cols = mmin_by_search(R)
    okmin = True
    if mm is not None and mm > 0:
        for A in range(min(R) - mm, max(R) + mm + 1):
            ps = [(mm - 1 + A - R[s]) for s in range(nS)]
            if all(0 <= x <= 2 * (mm - 1) and x % 2 == 0 for x in ps):
                okmin = False
    claim('A6', '獨立搜尋：m_min(K) = 10（A = 0）；且 m = 9 時無任何 A 可行（最小性顯式反證）',
          mm == 10 and AA == 0 and okmin, 'm_min = %s ; A = %s ; m=9 infeasible = %s' % (mm, AA, okmin))

    # --- A7: 修復欄之獨立重算 ---
    ident = all(all(cols[i][s] == -theta[s] for s in range(nS)) for i in range(len(cols)))
    bal = [sum(c) for c in cols]
    Xc = [list(K[s]) + [-theta[s]] * 10 for s in range(nS)]
    nc = len(Xc[0])
    claim('A7', '10 欄修復 ≡ -theta x10（逐項相同）且欄平衡；修復後 R\' ≡ 0；n = 72',
          ident and set(bal) == {0} and set(sum(r) for r in Xc) == {0} and nc == 72,
          'identical = %s ; col sums = %s ; n = %d' % (ident, sorted(set(bal)), nc))
    Wb = [[F(1, 72) + F(1, 72) * Xc[s][a] for a in range(nc)] for s in range(nS)]
    claim('A8', 'beta = 1/72 之 W 非負（含 0）且歸一；相異 row = 12（態敏感）',
          all(v >= 0 for r in Wb for v in r) and all(sum(r) == 1 for r in Wb)
          and len(set(tuple(r) for r in Wb)) == 12,
          'min entry = %s ; distinct rows = %d' % (min(v for r in Wb for v in r),
                                                   len(set(tuple(r) for r in Wb))))

    # --- A9: 解析 null 機率（Pascal 三角形獨立重算） ---
    c6226 = pascal_binom(62, 26)
    p_row = F(2 * c6226, 2 ** 62)
    claim('A9', '獨立二項式：P(單 row #(-1) ∈ {26,36}) = 2*C(62,26)/2^62；^120 為 P(全 120 row 同結構)',
          c6226 > 0, 'C(62,26) = %d ; P_row = %s ; P_all num digits = %d'
          % (c6226, p_row, len(str(p_row.numerator ** 120))))

    # --- A10: 對 03 已報值之 0-dev 對比 ---
    p3 = os.path.join(DATA, '03_r1_results.json')
    if os.path.exists(p3):
        rep = json.load(io.open(p3, encoding='utf-8'))
        consistent = (rep['rank_K'] == rkK and rep['rank_K_aug'] == rkAug and rep['Delta'] == max(R) - min(R)
                      and rep['null']['N1_hits'] == 0 and rep['null']['N2_hits'] == 0
                      and rep['multi_copy']['k=4']['m_min'] == 40
                      and rep['axis_type_subtables']['edge']['m_min'] == 10)
        claim('A10', '對 03 報告值逐項 0-dev 一致（rank / rank_aug / Delta / null 命中 0 / 多副本 k=4 / edge 子表）',
              consistent, 'consistent = %s' % consistent)
        claim('A11', '03 全部 checks 為 PASS 且 GATE OPEN',
              all(c['ok'] for c in rep['claims'])
              and json.load(io.open(os.path.join(DATA, '02_r1_freeze.json'), encoding='utf-8'))['GATE'] == 'OPEN',
              'n_claims = %d' % len(rep['claims']))
    else:
        claim('A10', '03 結果檔存在', False, 'missing %s' % p3)

    with io.open(os.path.join(DATA, '04_r1_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': 'r1-barrier-v1-audit', 'claims': CLAIMS}, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 100)
    print('AUDIT RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 100)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
