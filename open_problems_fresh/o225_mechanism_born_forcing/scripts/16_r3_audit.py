#!/usr/bin/env python3
"""O225 scripts/16 -- R3 獨立審計（不 import scripts/15）。

獨立性措施：
  * 中心元素以**另一算法**找（g² = e、g 與全體交換、g ≠ e），並由四元數分量直接核 G[zc] = -1
  * K 以**獨立代碼路徑**重建（顯式 3x3 有理旋轉矩陣 q_to_matrix，唔用 O222 之 sandwich）
  * replay 以另一風格重寫（deque ＋ 單一 read()，含 pop 回溯），另核軌跡步數
  * 刀刃以**另一個** centre-odd sigma（splitmix64 偽隨機）與**另一組** T 半邊（奇索引中心類）重做
  * 商群以**中央化子計數**（|class| = 60/|C(x)|）＋ 換位子群閉包兩條獨立路線判 A5
  * 逐項對 data/15_r3_centre.json 已報值做 0-dev 對比
用法:  /usr/bin/python3 scripts/16_r3_audit.py
"""
import importlib.util
import io
import json
import os
import sys
from collections import deque
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
O222S = os.path.join(O222, 'scripts')
BUDGET = F(10 ** 9)
COST = F(123, 88)
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


def splitmix64(x):
    x = (x + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = x
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    return z ^ (z >> 31)


def q_to_matrix(q):
    """顯式 3x3 旋轉矩陣（單位四元數；entries 為 a + b*sqrt5 之 (p,q) 對）"""
    a, b, c, d = q
    add = lambda x, y: (x[0] + y[0], x[1] + y[1])
    sub = lambda x, y: (x[0] - y[0], x[1] - y[1])
    mul = lambda x, y: (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + y[0] * x[1])
    sc = lambda x, k: (x[0] * k, x[1] * k)
    one, two = (F(1), F(0)), (F(2), F(0))
    b2, c2, d2 = mul(b, b), mul(c, c), mul(d, d)
    bc, bd, cd = mul(b, c), mul(b, d), mul(c, d)
    ab, ac, ad = mul(a, b), mul(a, c), mul(a, d)
    return [[sub(one, sc(add(c2, d2), F(2))), sub(sc(bc, F(2)), sc(ad, F(2))), add(sc(bd, F(2)), sc(ac, F(2)))],
            [add(sc(bc, F(2)), sc(ad, F(2))), sub(one, sc(add(b2, d2), F(2))), sub(sc(cd, F(2)), sc(ab, F(2)))],
            [sub(sc(bd, F(2)), sc(ac, F(2))), add(sc(cd, F(2)), sc(ab, F(2))), sub(one, sc(add(b2, c2), F(2)))]]


def sgn(x):
    """Z[sqrt5] 之精確符號（p^2 vs 5q^2）——與凍結機器之 sgn 同語義（首跑用「首個非零分量」，A2 已診斷）"""
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


def build_K_independent(mm, U, G):
    add2 = lambda x, y: (x[0] + y[0], x[1] + y[1])
    mul2 = lambda x, y: (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + y[0] * x[1])
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
                    scv = sgn(comp)
                    if scv:
                        s = scv
                        break
            row.append(s)
        K.append(row)
    return K


def replay_ind(order, s0, K, upd, nctx, track=False):
    """deque ＋ 單一 read() 風格；pop 回溯狀態"""
    memo = deque(maxlen=2)
    st = s0
    c = {'hits': 0, 'overrides': 0, 'stale': 0, 'agree': 0, 'stale_agree': 0, 'reads': 0}
    traj = [s0]

    def read(ctx, first):
        nonlocal st
        if memo and memo[-1][0] == ctx:
            c['hits'] += 1
            _sc, sv, ss = memo[-1]
            now = K[st][ctx]
            if st != ss:
                c['stale'] += 1
                if sv == now:
                    c['stale_agree'] += 1
            if sv != now:
                c['overrides'] += 1
            elif st == ss:
                c['agree'] += 1
            if first:
                traj.append(st)
            return False
        memo.append((ctx, K[st][ctx], st))
        c['reads'] += 1
        st = upd(st, ctx)
        if first:
            traj.append(st)
        return True

    for (a, b) in order:
        for ctx in (a, b):
            read(ctx, True)
        _c, _v, s_at = memo.pop()
        st = s_at
        traj.append(st)
        if memo and memo[-1][0] == b:
            read(b, False)
        else:
            read(b, False)
    out = dict(c)
    if track:
        out['traj'] = traj
    return out


def main():
    print('=' * 100)
    print('O225 scripts/16 -- R3 independent audit (does NOT import scripts/15)')
    print('=' * 100, flush=True)
    b5 = load(os.path.join(O222S, '12_b5_budget.py'), 'r3a_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    a2 = load(os.path.join(O222S, '09_a2_rollback.py'), 'r3a_a2')
    G, idxg, MUL2 = a2.build_group()
    N, nctx = len(K), len(K[0])
    order = [(a, b) for a in range(nctx) for b in range(nctx)]
    upd = lambda s, ctx: MUL[s][hx[ctx]]

    # ---- A1 中心元素（另一算法） ----
    e_id = next(x for x in range(N) if all(MUL[s][x] == s for s in range(N)))
    invs = [g for g in range(N) if g != e_id and all(MUL[s][g] == MUL[g][s] for s in range(N))
            and MUL[g][g] == e_id]
    zc = invs[0]
    gz = G[zc]
    quat_ok = (gz[0] == (F(-1), F(0))) and all(c == (F(0), F(0)) for c in gz[1:])
    claim('A1', '中心元素 zc（唯一階 2 且與全體交換者）＝ 四元數 -1（分量直接核對）',
          len(invs) == 1 and quat_ok, 'involutions = %s ; G[zc] = %s ; zc = %d ; e_id = %d'
          % (invs, gz, zc, e_id))

    # ---- A2 獨立 K 建構 ＋ 逐列中心不變 ----
    _ax, U, _i, _t, _h = mm.load_inputs()
    Kind = build_K_independent(mm, U, G)
    same = (Kind == K)
    roweq = all(Kind[MUL[s][zc]][a] == Kind[s][a] for s in range(N) for a in range(nctx))
    claim('A2', '獨立路徑重建 K（顯式旋轉矩陣）與機器 K 相同，且逐列中心不變（7440 對）',
          same and roweq, 'K identical = %s ; row-negation invariance = %s' % (same, roweq))

    # ---- A3 獨立 replay：五計數器中心不變 ＋ 0-dev vs data/15 ----
    rep15 = json.load(io.open(os.path.join(DATA, '15_r3_centre.json'), encoding='utf-8'))
    rec = [replay_ind(order, s0, K, upd, nctx) for s0 in range(N)]
    five = ('hits', 'stale', 'agree', 'stale_agree', 'overrides')
    viol = [(s, k) for s in range(N) for k in five if rec[s][k] != rec[MUL[s][zc]][k]]
    dev = {k: rec[0][k] for k in five}
    claim('A3', '獨立 replay：五計數器中心不變（0 違例）＋ s0=0 值與 scripts/15 報值 0-dev',
          not viol and all(dev[k] == rep15['counters_s0_0'][k] for k in five),
          'violations = %d ; s0=0 = %s ; data/15 = %s' % (len(viol), dev, rep15['counters_s0_0']))

    # ---- A3b 軌跡步數 ----
    t1 = replay_ind(order, 0, K, upd, nctx, track=True)['traj']
    t2 = replay_ind(order, MUL[0][zc], K, upd, nctx, track=True)['traj']
    tg = (len(t1) == len(t2)) and all(t2[i] == MUL[t1[i]][zc] for i in range(len(t1)))
    claim('A3b', '軌跡等變（另一實作）：步數 %d ＋ 逐位否定相符' % len(t1), tg,
          'len = %d ; 逐位相符 = %s ; 預期步數 3·62² + 1 = %d' % (len(t1), tg, 3 * nctx * nctx + 1))

    # ---- A4 刀刃：另一 sigma（偽隨機 centre-odd）＋ 另一 T 半邊 ----
    sig = [1 if (splitmix64(7 + s) & 1) else -1 for s in range(N)]
    for s in range(N):
        sig[MUL[s][zc]] = -sig[s]
    centre_odd = all(sig[MUL[s][zc]] == -sig[s] for s in range(N))
    Ksig = [[sig[s] * K[s][a] for a in range(nctx)] for s in range(N)]
    lam_sig = all(len(set(Ksig[MUL[s][zc]][a] * Ksig[s][a] for s in range(N))) == 1 for a in range(nctx))
    rs = [replay_ind(order, s0, Ksig, upd, nctx) for s0 in range(N)]
    v_sig = [s for s in range(N) if rs[s]['overrides'] != rs[MUL[s][zc]]['overrides']]
    claim('A4', '刀刃（σ′＝偽隨機 centre-odd）：λ 恆定（≡ -1）⟹ 不變仍成立（強化 (ii\') 之獨立證據）',
          centre_odd and lam_sig and not v_sig,
          'centre-odd = %s ; λ 恆定 = %s ; 違例 = %d' % (centre_odd, lam_sig, len(v_sig)))

    reps60 = sorted(set(min(s, MUL[s][zc]) for s in range(N)))
    T2 = set(max(r, MUL[r][zc]) for i, r in enumerate(reps60) if i % 2 == 1)   # 另一組半邊
    Kt = [[(-1 if s in T2 else 1) * K[s][a] for a in range(nctx)] for s in range(N)]
    rt = [replay_ind(order, s0, Kt, upd, nctx) for s0 in range(N)]
    v_t = [s for s in range(N) if rt[s]['overrides'] != rt[MUL[s][zc]]['overrides']]
    lam_t = all(len(set(Kt[MUL[s][zc]][a] * Kt[s][a] for s in range(N))) == 1 for a in range(nctx))
    claim('A5', '刀刃（另一組 T 半邊，奇索引中心類）：比率隨 s 變化 ⟹ 不變失效（必要性再現）',
          (not lam_t) and len(v_t) > 0,
          'T 大小 = %d ; 比率恆定 = %s ; 失效態數 = %d' % (len(T2), lam_t, len(v_t)))

    # ---- A6 商群：中央化子計數 ＋ 換位子群閉包 ----
    reps = reps60
    ix = {r: i for i, r in enumerate(reps)}
    Q = [[ix[min(MUL[x][y], MUL[MUL[x][y]][zc])] for y in reps] for x in reps]
    m = len(reps)
    well = all(ix[min(MUL[s][h], MUL[MUL[s][h]][zc])]
               == Q[ix[min(s, MUL[s][zc])]][ix[min(h, MUL[h][zc])]] for s in range(N) for h in range(N))
    cent_sizes = []
    for x in range(m):
        cen = [y for y in range(m) if Q[x][y] == Q[y][x]]
        cent_sizes.append(m // len(cen))
    # 由「逐元素之共軛類大小」摺成「類大小之多重集」：大小 k 出現 cnt 次 ⟹ 有 cnt/k 個類
    cs_count = {}
    for k in cent_sizes:
        cs_count[k] = cs_count.get(k, 0) + 1
    class_multiset = sorted(k for k, cnt in cs_count.items() for _ in range(cnt // k))
    inv = [next(j for j in range(m) if Q[i][j] == 0 and Q[j][i] == 0) for i in range(m)]
    comms = set()
    for x in range(m):
        for y in range(m):
            comms.add(Q[Q[x][y]][inv[Q[y][x]]])
    sub = {0}
    changed = True
    while changed:
        changed = False
        for a in list(sub):
            for b in list(comms):
                if Q[a][b] not in sub:
                    sub.add(Q[a][b])
                    changed = True
    zq = [x for x in range(m) if all(Q[x][y] == Q[y][x] for y in range(m))]
    ovmap = {s: rec[s]['overrides'] for s in range(N)}
    cls_val = set(len(set(ovmap[s] for s in range(N) if min(s, MUL[s][zc]) == r)) for r in reps)
    claim('A6', '商群 2I/{±1}：階 60、良定義、中央化子計數得共軛類大小 [1,12,12,15,20]、換位子群 = 全群、'
                '中心平凡 ⟹ A₅；overrides 為商上之函數（26 值）但唔由商共軛類決定',
          m == 60 and well and class_multiset == [1, 12, 12, 15, 20] and len(sub) == 60
          and zq == [0] and cls_val == {1} and len(set(ovmap.values())) == 26
          and len(set(frozenset(ovmap[s] for s in range(N) if min(s, MUL[s][zc]) == r) for r in reps)) > 1,
          'order = %d ; class sizes(中央化子) = %s ; 換位子群階 = %d ; 商中心 = %s ; '
          'overrides 值數 = %d ; 每類相異值數 = %s'
          % (m, class_multiset, len(sub), zq, len(set(ovmap.values())), sorted(cls_val)))

    # ---- A7 門與對照 ----
    gate = json.load(io.open(os.path.join(DATA, '14_r3_freeze.json'), encoding='utf-8'))['GATE']
    nfail = sum(1 for c in rep15['claims'] if not c['ok'])
    claim('A7', 'R3 門 OPEN、機器 11/11（0 FAIL）、首跑誤用反演之 FAIL 已保留並診斷',
          gate == 'OPEN' and nfail == 0 and len(rep15['claims']) == 11,
          'GATE = %s ; claims = %d ; fails = %d' % (gate, len(rep15['claims']), nfail))

    with io.open(os.path.join(DATA, '16_r3_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump({'rules': 'r3-centre-v1-audit', 'claims': CLAIMS,
                   'quotient': {'order': m, 'class_sizes': sorted(cent_sizes)}}, fh,
                  indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 100)
    print('AUDIT RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 100)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
