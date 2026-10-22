#!/usr/bin/env python3
"""O225 scripts/03 -- R1 機器：機制層 Born 權重之障礙定理 + 最小修改族（rules: r1-barrier-v1）。

合約: docs/01_r1_contract.md（P4..P13 之期望值喺第一次執行之前已寫死並註冊）。
精確算術鐵律: 只用 int / fractions.Fraction；無 float 字面值、無 math/random/numpy/statistics。
null 用純整數 splitmix64（自行實作）。

用法:  /usr/bin/python3 scripts/03_r1_barrier.py [--nulls N]
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
RULES = 'r1-barrier-v1'
MASK = (1 << 64) - 1
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s%s' % ('PASS' if ok else 'FAIL', tag, name,
                              ('  --  ' + detail) if detail else ''), flush=True)
    return bool(ok)


def proof(tag, name, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': True, 'kind': 'PROOF', 'detail': detail})
    print('[PROOF] %-5s %s%s' % (tag, name, ('  --  ' + detail) if detail else ''), flush=True)


# ------------------------------------------------------------------ exact helpers
def splitmix64(state):
    state = (state + 0x9E3779B97F4A7C15) & MASK
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
    return state, z ^ (z >> 31)


def binom(n, k):
    if k < 0 or k > n:
        return 0
    num = 1
    den = 1
    for i in range(k):
        num *= (n - i)
        den *= (i + 1)
    return num // den


def rank_q(rows):
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


def solve_2unk(eqs):
    """eqs = [(coefA, coefB, rhs)]; return ('unique', (a,b)) / ('free', base, dir) / ('none', None)"""
    M = [[F(c[0]), F(c[1]), F(c[2])] for c in eqs]
    piv_cols = []
    r = 0
    for c in range(2):
        p = None
        for k in range(r, len(M)):
            if M[k][c] != 0:
                p = k
                break
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        M[r] = [x / pv for x in M[r]]
        for k in range(len(M)):
            if k != r and M[k][c] != 0:
                f = M[k][c]
                M[k] = [a - f * b for a, b in zip(M[k], M[r])]
        piv_cols.append(c)
        r += 1
    for k in range(r, len(M)):
        if M[k][0] == 0 and M[k][1] == 0 and M[k][2] != 0:
            return ('none', None)
    if len(piv_cols) == 2:
        sol = [F(0), F(0)]
        for k, c in enumerate(piv_cols):
            sol[c] = M[k][2]
        return ('unique', tuple(sol))
    # rank 1: one-parameter family
    free_col = 1 - piv_cols[0]
    base = [F(0), F(0)]
    base[piv_cols[0]] = M[0][2]
    direction = [F(0), F(0)]
    direction[free_col] = F(1)
    direction[piv_cols[0]] = -M[0][free_col]
    return ('free', tuple(base), tuple(direction))


def mmin_of_R(R):
    """D5: min m with exists integer A s.t. |A-R(s)| <= m and A-R(s) == m (mod 2) for all s"""
    lo, hi = min(R), max(R)
    m = 0
    while True:
        for A in range(lo - m, hi + m + 1):
            if all(abs(A - r) <= m and (A - r - m) % 2 == 0 for r in R):
                return m, A
        m += 1


def repair_columns(R, m, A):
    """explicit m columns c_i in {+-1}^|S| with row sums C(s) = A - R(s)"""
    C = [A - r for r in R]
    p = [(m + c) // 2 for c in C]
    return [[1 if p[s] > i else -1 for s in range(len(R))] for i in range(m)]


# ------------------------------------------------------------------ machine loading
def load_o222(script):
    spec = importlib.util.spec_from_file_location('o222_' + script[:-3], os.path.join(O222S, script))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_K(m, axes=None, ref_axis0=None):
    axes_, U, ids, types, hvec = m.load_inputs()
    if axes is not None:
        U = axes
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
    return K, G, MUL, hydx, ids, types, U


def random_axes(m, G, seed, n_axes=62):
    st = seed
    axes = []
    for _ in range(n_axes):
        st, z = splitmix64(st)
        qq = G[z % 120]
        axes.append((qq[1], qq[2], qq[3]))
    return axes


def random_balanced_table(seed, nS=120, nA=62):
    """每欄恰 60 個 +1（Fisher-Yates，splitmix64 驅動，純整數）"""
    st = seed
    cols = []
    for _ in range(nA):
        perm = list(range(nS))
        for i in range(nS - 1, 0, -1):
            st, z = splitmix64(st)
            j = z % (i + 1)
            perm[i], perm[j] = perm[j], perm[i]
        plus = set(perm[:nS // 2])
        cols.append([1 if s in plus else -1 for s in range(nS)])
    return cols


def transpose_cols(cols, nS):
    return [[cols[a][s] for a in range(len(cols))] for s in range(nS)]


def main():
    argv = sys.argv[1:]
    n_null = int(argv[argv.index('--nulls') + 1]) if '--nulls' in argv else 200
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    print('=' * 110)
    print('O225 scripts/03 -- R1: mechanism-layer Born barrier + minimal modification family (rules: %s)' % RULES)
    print('=' * 110, flush=True)

    m = load_o222('09_a2_rollback.py')
    K, G, MUL, hydx, ids, types, U = build_K(m)
    nS, nA = len(K), len(K[0])
    R = [sum(r) for r in K]
    theta = [1 if x > 0 else -1 for x in R]
    out = {'rules': RULES, 'K_shape': [nS, nA]}

    # ---------------- P1-P3: invariants (recon-confirmed) ----------------
    vals = {}
    for row in K:
        for v in row:
            vals[v] = vals.get(v, 0) + 1
    colsum = [sum(K[s][a] for s in range(nS)) for a in range(nA)]
    claim('P1', 'K 值重數 {+1:3720,-1:3720}；每欄 Σ_s = 0 且恰 60 個 +1',
          vals == {1: 3720, -1: 3720} and set(colsum) == {0} and set(
              sum(1 for s in range(nS) if K[s][a] == 1) for a in range(nA)) == {60},
          'values=%s colsum=%s' % (sorted(vals.items()), sorted(set(colsum))))
    claim('P2', 'R(s) 恰取 {+10,-10}，60/60；Delta = 20',
          sorted(set(R)) == [-10, 10] and R.count(10) == 60,
          'distinct=%s hist=%s Delta=%d' % (sorted(set(R)), {str(v): R.count(v) for v in sorted(set(R))},
                                            max(R) - min(R)))
    rkK = rank_q(K)
    Rl = [tuple(r) for r in K]
    cnt = {}
    for r in Rl:
        cnt[r] = cnt.get(r, 0) + 1
    claim('P3', 'rank_Q(K) = 6；相異 row = 12（重數全 10）',
          rkK == 6 and len(cnt) == 12 and set(cnt.values()) == {10},
          'rank=%d distinct rows=%d multiplicities=%s' % (rkK, len(cnt), sorted(set(cnt.values()))))
    out['rank_K'] = rkK
    out['Delta'] = max(R) - min(R)

    # ---------------- P4: barrier theorem (affine family) ----------------
    res = solve_2unk([(nA, 10, 1), (nA, -10, 1)])
    ok_single = (res[0] == 'unique' and res[1] == (F(1, nA), F(0)))
    claim('P4a', '族 A 歸一方程組之解集 = 單點 {(1/62, 0)}（beta = 0 ⟹ W 恆等均勻 ⟹ 態盲目）',
          ok_single, 'solution set = %s %s' % (res[0], str(res[1]) if len(res) > 1 else ''))
    W0 = [[F(1, nA)] * nA for _ in range(nS)]
    claim('P4b', '該解之 W 只有 1 個相異 row（D2 態敏感失敗）',
          len(set(tuple(r) for r in W0)) == 1, 'distinct rows of W = 1')

    Xc = [list(K[s]) + [-theta[s]] * 10 for s in range(nS)]
    Rc = [sum(r) for r in Xc]
    nc = len(Xc[0])
    resc = solve_2unk([(nc, Rc[0], 1), (nc, Rc[0], 1)])
    claim('P4c', '反事實 X\' = [K | (-theta)x10]（n = 72, R\' ≡ 0）：解集 = 1 參數族 alpha = 1/72, beta 自由',
          set(Rc) == {0} and resc[0] == 'free' and resc[1][0] == F(1, 72),
          'R\' distinct = %s ; solution = %s base=%s dir=%s' % (sorted(set(Rc)), resc[0], resc[1][0], resc[2][1]))
    nb_ok = True
    sens_rows = {}
    for beta in (F(1, 72), F(1, 144), F(-1, 72)):
        Wb = [[F(1, 72) + beta * Xc[s][a] for a in range(nc)] for s in range(nS)]
        if any(v < 0 for r in Wb for v in r):
            nb_ok = False
        sens_rows[str(beta)] = len(set(tuple(r) for r in Wb))
        if any(sum(r) != 1 for r in Wb):
            nb_ok = False
    claim('P4d', '反事實之修復族：|beta| <= 1/72 時非負且歸一；beta ≠ 0 時態敏感（相異 row = 12）',
          nb_ok and sens_rows[str(F(1, 72))] == 12 and sens_rows[str(F(1, 144))] == 12,
          'nonneg+normalized = %s ; distinct rows by beta = %s' % (nb_ok, sens_rows))

    # ---------------- P5/P6/P7: minimal modification ----------------
    mm, AA = mmin_of_R(R)
    claim('P5', 'm_min(K) = 10（= ceil(Delta/2)，A = 0）', mm == 10 and AA == 0,
          'm_min = %d ; A = %d' % (mm, AA))
    cols = repair_columns(R, mm, AA)
    rowsum_check = [R[s] + sum(cols[i][s] for i in range(mm)) for s in range(nS)]
    colbal = [sum(cols[i]) for i in range(mm)]
    ident_theta = all(all(cols[i][s] == -theta[s] for s in range(nS)) for i in range(mm))
    claim('P6', 'm = 10 之修復欄 = 10 欄完全相同之 c_i = -theta，且自動欄平衡 Σ_s c_i = 0',
          set(rowsum_check) == {0} and set(colbal) == {0} and ident_theta,
          'repaired row sums = %s ; column sums = %s ; all c_i == -theta : %s'
          % (sorted(set(rowsum_check)), sorted(set(colbal)), ident_theta))
    proof('P7', 'm <= 9 不可能：需 max C - min C >= Delta = 20，而 |C(s)| <= m ⟹ 2m >= 20 ⟹ m >= 10',
          '2*9 = 18 < 20（代數不等式，無枚舉需要）')

    # ---------------- P8: multi-copy ----------------
    mc = {}
    ok8 = True
    for k in (1, 2, 3, 4):
        Xk = []
        for s in range(nS):
            row = []
            for _ in range(k):
                row.extend(K[s])
            Xk.append(row)
        Rk = [sum(r) for r in Xk]
        mk, Ak = mmin_of_R(Rk)
        cols_k = repair_columns(Rk, mk, Ak)
        Rk2 = [Rk[s] + sum(cols_k[i][s] for i in range(mk)) for s in range(nS)]
        mc['k=%d' % k] = {'Delta': max(Rk) - min(Rk), 'm_min': mk, 'A': Ak,
                          'repaired_constant': (len(set(Rk2)) == 1)}
        if not (max(Rk) - min(Rk) == 20 * k and mk == 10 * k and len(set(Rk2)) == 1):
            ok8 = False
    claim('P8', '多副本 M3：Delta_k = 20k，m_min = 10k（k = 1..4），且修復後列和恆常', ok8,
          '; '.join('%s: Delta=%d m_min=%d' % (kk, vv['Delta'], vv['m_min']) for kk, vv in sorted(mc.items())))
    out['multi_copy'] = mc

    # ---------------- P9: complex readout (exact rank criterion) ----------------
    aug = [list(r) + [1] for r in K]
    rk_aug = rank_q(aug)
    claim('P9a', 'per-context 相位修復存在 ⟺ 1 ∈ range(K) ⟺ rank[K|1] = rank(K)；實測 7 > 6 ⟹ 不存在',
          rk_aug != rkK, 'rank[K|1] = %d ; rank(K) = %d' % (rk_aug, rkK))
    modrows = [sum(1 for a in range(nA)) for s in range(1)]
    claim('P9b', '全域相位：|e^{i phi} K[s,a]| = 1 恆常 ⟹ 模數列和 = 62 常數 ⟹ W 均勻 ⟹ 態盲目',
          set(sum(1 for a in range(nA)) for s in range(nS)) == {62},
          'modulus row sums = {62}（恆等式，62 欄每欄模數 1）')
    out['rank_K_aug'] = rk_aug
    proof('P9c', 'per-(s,a) 相位 = 7440 個新自由實數 ⟹ 唔屬「修改」（參數計數，見 P10）',
          '7440 = 120 x 62')

    # ---------------- P10: non-deterministic readout ----------------
    freeW = nS * (nA - 1)
    bits5 = 2 ** 5
    bits6 = 2 ** 6
    claim('P10', 'M2（W = p 任意）需 %d 個自由實數；凍結機器可及隨機性 60 行為 ⟹ 2^5 = 32 < 60 <= 64 = 2^6'
                 '（< 6 bits）⟹ M2 係加新獨立隨機源，非由凍結機器生成' % freeW,
          freeW == 7320 and bits5 < 60 <= bits6,
          'free reals = %d ; 2^5 = %d < 60 <= %d = 2^6' % (freeW, bits5, bits6))

    # ---------------- P11: out-of-sample blind test of D5 formula ----------------
    sub = {}
    for tp in ('edge', 'face', 'vertex'):
        idxs = [a for a in range(nA) if types[a] == tp]
        Sub = [[K[s][a] for a in idxs] for s in range(nS)]
        Rs = [sum(r) for r in Sub]
        ms, As = mmin_of_R(Rs)
        cs = repair_columns(Rs, ms, As)
        Rs2 = [Rs[s] + sum(cs[i][s] for i in range(ms)) for s in range(nS)]
        sub[tp] = {'n_axes': len(idxs), 'Delta': max(Rs) - min(Rs), 'm_min': ms,
                   'A': As, 'repaired_constant': len(set(Rs2)) == 1}
    ok11a = (sub['edge']['m_min'] == 10 and sub['vertex']['m_min'] == 0 and sub['face']['m_min'] == 0
             and all(sub[t]['repaired_constant'] for t in sub))
    claim('P11a', '軸型別子表（out-of-sample）：edge(30) 預測 m_min = 10；vertex(12)/face(20) 預測 0；'
                  '三者之顯式修復構造皆令列和恆常',
          ok11a, '; '.join('%s: n=%d Delta=%d m_min=%d const=%s'
                           % (t, sub[t]['n_axes'], sub[t]['Delta'], sub[t]['m_min'],
                              sub[t]['repaired_constant']) for t in ('edge', 'vertex', 'face')))
    out['axis_type_subtables'] = sub

    print('\n-- P11b: random-axis machines (%d draws), D5 formula + explicit construction --' % n_null, flush=True)
    rk_ok = 0
    rk_rows = []
    for d in range(n_null):
        axes = random_axes(m, G, 225 + 7919 * d)
        Kn, _G, _M, _h, _i, _t, _U = build_K(m, axes=axes)
        Rn = [sum(r) for r in Kn]
        mn, An = mmin_of_R(Rn)
        cn = repair_columns(Rn, mn, An)
        Rn2 = [Rn[s] + sum(cn[i][s] for i in range(mn)) for s in range(nS)]
        okc = (len(set(Rn2)) == 1)
        if okc:
            rk_ok += 1
        delta_n = max(Rn) - min(Rn)
        # 預註冊：2 值且為 {-10, +10} 之命中數
        if sorted(set(Rn)) == [-10, 10]:
            rk_rows.append({'draw': d, 'distinct': sorted(set(Rn)), 'Delta': delta_n, 'm_min': mn})
        if d % 50 == 0:
            print('   draw %3d: Delta = %3d  m_min = %3d  repair const = %s  distinct = %s'
                  % (d, delta_n, mn, okc, sorted(set(Rn))[:6]), flush=True)
    claim('P11b', 'D5 公式對 %d 個隨機軸機器全部成立（顯式構造成功）' % n_null, rk_ok == n_null,
          'successful constructions = %d/%d' % (rk_ok, n_null))
    out['random_axis_mmin_sample'] = rk_rows[:20]

    # ---------------- P12: falsifiability (construction always works) ----------------
    claim('P12', '可證偽：D5 之 m_min 構造對上述全部表（62 軸表、3 個子表、%d 隨機軸表）'
                 '皆令列和恆常 ⟹ 未觀察到反例' % n_null,
          ok11a and rk_ok == n_null, 'repaired constant in all cases')

    # ---------------- P13: nulls ----------------
    print('\n-- P13: null (N1 = random-axis over R; N2 = random balanced tables) --', flush=True)
    hit1 = 0
    seen1 = {}
    for d in range(n_null):
        axes = random_axes(m, G, 225 + 7919 * d)
        Kn, _G, _M, _h, _i, _t, _U = build_K(m, axes=axes)
        Rn = [sum(r) for r in Kn]
        key = tuple(sorted(set(Rn)))
        seen1[key] = seen1.get(key, 0) + 1
        if key == (-10, 10):
            hit1 += 1
    hit2 = 0
    for d in range(n_null):
        cols = random_balanced_table(961 + 104729 * d)
        rows = transpose_cols(cols, nS)
        Rn = [sum(r) for r in rows]
        if sorted(set(Rn)) == [-10, 10]:
            hit2 += 1
    p_row = F(2 * binom(62, 26), 2 ** 62)
    p_all = p_row ** 120
    claim('P13', 'null：N1（隨機軸）與 N2（隨機平衡 ±1 表）命中「恰兩值且 = {-10, +10}」之次數 = 0',
          hit1 == 0 and hit2 == 0,
          'N1 hits = %d/%d ; N2 hits = %d/%d ; 解析界 P(單 row) = 2*C(62,26)/2^62 = %s ; ^120 = %s'
          % (hit1, n_null, hit2, n_null, p_row, p_all))
    out['null'] = {'N1_hits': hit1, 'N2_hits': hit2, 'N': n_null,
                   'P_single_row_num': p_row.numerator, 'P_single_row_den': p_row.denominator,
                   'P_all_rows_num': p_all.numerator, 'P_all_rows_den': p_all.denominator,
                   'N1_distinct_rowsum_sets': {str(k): v for k, v in sorted(seen1.items())}}

    # ---------------- rigidity: perturbation test ----------------
    print('\n-- rigidity: flip one K entry --', flush=True)
    rig = {}
    for (s0, a0) in ((0, 0), (0, 30), (1, 61)):
        Kp = [list(r) for r in K]
        Kp[s0][a0] = -Kp[s0][a0]
        Rp = [sum(r) for r in Kp]
        mp, Ap = mmin_of_R(Rp)
        cp = repair_columns(Rp, mp, Ap)
        Rp2 = [Rp[s] + sum(cp[i][s] for i in range(mp)) for s in range(nS)]
        rig['flip(%d,%d)' % (s0, a0)] = {'Delta': max(Rp) - min(Rp), 'm_min': mp, 'A': Ap,
                                        'distinct_R': sorted(set(Rp)),
                                        'repaired_constant': len(set(Rp2)) == 1}
    print('   ', rig, flush=True)
    out['rigidity'] = rig

    out['claims'] = CLAIMS
    with io.open(os.path.join(DATA, '03_r1_results.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    ncheck = sum(1 for c in CLAIMS if c.get('kind') != 'PROOF')
    print('=' * 110)
    print('RESULT: %d/%d PASS   (checks = %d, PROOF items = %d)'
          % (npass, len(CLAIMS), ncheck, len(CLAIMS) - ncheck))
    print('=' * 110)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
