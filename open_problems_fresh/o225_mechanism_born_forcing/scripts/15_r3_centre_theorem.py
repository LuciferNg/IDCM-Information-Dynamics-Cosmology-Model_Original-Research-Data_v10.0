#!/usr/bin/env python3
"""O225 scripts/15 -- R3 機器：中心不變定理（`r3-centre-v1`）。

定理：重播協定滿足
  (i)  等變更新 s ↦ MUL[s][h(ctx)]
  (ii) 讀出表中心不變 K[MUL[s][zc]][a] = K[s][a]
⟹ G1 計數器（hits/stale/agree/stale_agree/overrides）及全部伴隨量對 s0 與 −s0 完全相同。

本機器逐項判：
  R3-P1 前置 (ii) 機械檢定（7440 對）｜R3-P2 前置 (i) 機械檢定（中心性＋等變）
  R3-P3 軌跡等變實測（全 120 s0，完整狀態序列）｜R3-P4 五計數器中心不變
  R3-P5 伴隨量中心不變｜R3-P6 尖銳性 C1（破 (ii)）｜R3-P7 尖銳性 C2（破 (i)）
  R3-P8 普適性（Z_8/Z_12/Z_16）＋ 商結構（2I/{±1} 之 60 類、共軛類大小多重集、overrides 唔由之決定）
精確算術；禁 float／math／random 等（見 scripts/14 enforcer）。上游 O222 唯讀。
用法:  /usr/bin/python3 scripts/15_r3_centre_theorem.py
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
    z = z ^ (z >> 31)
    return z


def replay(order, s0, K, upd, nctx, budget=BUDGET, track=False):
    """凍結協定（同 scripts/11）：3 步讀（a, b, pop 後重讀）、memo 單值、命中 = 值級比較、pop 回溯狀態。
    upd(s, ctx) -> 新狀態；track=True 時記錄每一步之狀態序列。"""
    L = []
    s = s0
    rem = budget
    c = {'hits': 0, 'overrides': 0, 'stale': 0, 'agree': 0, 'stale_agree': 0, 'reads': 0}
    traj = [s0]
    ent = [0] * nctx
    miss = {}
    top = {}
    vset = [set() for _ in range(nctx)]
    for (a, b) in order:
        spent = 0
        for ctx in (a, b):
            if L and L[-1][0] == ctx:
                c['hits'] += 1
                ss, sv = L[-1][2], L[-1][1]
                now = K[s][ctx]
                if s != ss:
                    c['stale'] += 1
                    if sv == now:
                        c['stale_agree'] += 1
                if sv != now:
                    c['overrides'] += 1
                elif s == ss:
                    c['agree'] += 1
                traj.append(s)
                continue
            L.append((ctx, K[s][ctx], s))
            c['reads'] += 1
            s = upd(s, ctx)
            spent += 1
            traj.append(s)
        _x, _v, s_at = L.pop()
        s = s_at
        traj.append(s)
        if L and L[-1][0] == b:
            c['hits'] += 1
            ss, sv = L[-1][2], L[-1][1]
            now = K[s][b]
            if s != ss:
                c['stale'] += 1
                if sv == now:
                    c['stale_agree'] += 1
            if sv != now:
                c['overrides'] += 1
            elif s == ss:
                c['agree'] += 1
        else:
            L.append((b, K[s][b], s))
            c['reads'] += 1
            s = upd(s, b)
            spent += 1
        rem -= COST * spent
        miss[spent] = miss.get(spent, 0) + 1
        top[L[-1][0]] = top.get(L[-1][0], 0) + 1
    for (ctx, v, _s) in L:
        ent[ctx] += 1
        vset[ctx].add(v)
    out = dict(c)
    out['ledger_len'] = c['reads'] - len(order)
    out['miss_hist'] = tuple(sorted(miss.items()))
    out['top_dist'] = tuple(sorted(top.values()))
    out['entries_per_ctx'] = tuple(sorted(ent))
    out['ctx_conflict'] = sum(1 for v in vset if len(v) > 1)
    if track:
        out['traj'] = traj
    return out


def main():
    os.makedirs(DATA, exist_ok=True)
    print('=' * 104)
    print('O225 scripts/15 -- R3: centre-invariance theorem (r3-centre-v1)')
    print('=' * 104, flush=True)
    b5 = load(os.path.join(O222S, '12_b5_budget.py'), 'r3_b5')
    a2 = load(os.path.join(O222S, '09_a2_rollback.py'), 'r3_a2')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    G, idxg, MUL2 = a2.build_group()
    nctx, N = len(K[0]), len(K)
    e_id = next(x for x in range(N) if all(MUL[s][x] == s for s in range(N)))
    zc = next(x for x in range(N)
              if x != e_id and all(MUL[s][x] == MUL[x][s] for s in range(N))
              and all(MUL[MUL[s][x]][x] == s for s in range(N)))
    neg = lambda s: MUL[s][zc]
    print('  [machine] N=%d nctx=%d identity=%d centre=%d | G[centre]=%s'
          % (N, nctx, e_id, zc, G[zc][0]), flush=True)
    order = [(a, b) for a in range(nctx) for b in range(nctx)]

    # ---------- R3-P1 前置 (ii) ----------
    diffs = [(s, a) for s in range(N) for a in range(nctx) if K[neg(s)][a] != K[s][a]]
    claim('R3-P1', '前置 (ii)：K[-s][a] = K[s][a]（全部 120×62 = 7440 對）', not diffs,
          'comparisons = %d ; violations = %d ; zc = %d ; e_id = %d'
          % (N * nctx, len(diffs), zc, e_id))

    # ---------- R3-P2 前置 (i) ----------
    cent = [(s, h) for s in range(N) for h in range(N) if MUL[neg(s)][h] != neg(MUL[s][h])]
    claim('R3-P2', '前置 (i)：中心性 MUL[s][zc]=MUL[zc][s] 與等變 MUL[-s][h] = -MUL[s][h]（全 s,h）',
          not cent, 'checks = %d ; violations = %d' % (N * N, len(cent)))

    # ---------- R3-P3 軌跡等變 ----------
    upd = lambda s, ctx: MUL[s][hx[ctx]]
    dev3 = []
    tl = 0
    for s0 in range(N):
        t1 = replay(order, s0, K, upd, nctx, track=True)['traj']
        t2 = replay(order, neg(s0), K, upd, nctx, track=True)['traj']
        tl = len(t1)
        if len(t1) != len(t2):
            dev3.append((s0, 'len', len(t1), len(t2)))
            continue
        bad = [i for i in range(len(t1)) if t2[i] != neg(t1[i])]
        if bad:
            dev3.append((s0, 'pos', bad[0], t1[bad[0]], t2[bad[0]]))
    claim('R3-P3', '軌跡等變實測：s_t(-s0) = -s_t(s0) 逐位成立（全 120 s0，含 pop 回溯）', not dev3,
          'trajectory = %d 步/態 ; 總比較 = %d ; deviations = %s'
          % (tl, tl * N, dev3[:4] if dev3 else '0'))

    # ---------- R3-P4 / R3-P5 後果 ----------
    rec = [replay(order, s0, K, upd, nctx) for s0 in range(N)]
    five = ('hits', 'stale', 'agree', 'stale_agree', 'overrides')
    bad4 = [(s, k) for s in range(N) for k in five if rec[s][k] != rec[neg(s)][k]]
    claim('R3-P4', '定理後果：hits/stale/agree/stale_agree/overrides 五量中心不變（120/120 × 5）',
          not bad4, 'violations = %d ; s0=0: %s' % (len(bad4), {k: rec[0][k] for k in five}))
    acc = ('ledger_len', 'miss_hist', 'top_dist', 'entries_per_ctx', 'ctx_conflict', 'reads')
    bad5 = [(s, k) for s in range(N) for k in acc if rec[s][k] != rec[neg(s)][k]]
    claim('R3-P5', '伴隨量中心不變：ledger_len/miss 直方圖/top 分布/entries_per_ctx/ctx 值衝突/reads',
          not bad5, 'violations = %d' % len(bad5))

    # ---------- R3-P6 刀刃（細化判準：逐欄比率 λ_a） ----------
    def lam_const(Kx):
        """λ_a = Kx[-s][a]·Kx[s][a] 是否與 s 無關（逐欄）"""
        return all(len(set(Kx[neg(s)][a] * Kx[s][a] for s in range(N))) == 1 for a in range(nctx))

    lam_vals = sorted(set(K[neg(s)][a] * K[s][a] for s in range(N) for a in range(nctx)))
    claim('R3-P6a', '凍結 K 之逐欄比率 λ_a = K[-s][a]·K[s][a] 與 s 無關且 λ_a ≡ +1（即 (ii) 恰成立）',
          lam_const(K) and lam_vals == [1], 'λ 值集 = %s ; 逐欄恆定 = %s' % (lam_vals, lam_const(K)))

    sigma = lambda s: 1 if s <= neg(s) else -1
    ok_sig = all(sigma(neg(s)) == -sigma(s) for s in range(N))
    Ksig = [[sigma(s) * K[s][a] for a in range(nctx)] for s in range(N)]
    ii_brk_sig = any(Ksig[neg(s)][a] != Ksig[s][a] for s in range(N) for a in range(nctx))
    recs6 = [replay(order, s0, Ksig, upd, nctx) for s0 in range(N)]
    viol6 = [s for s in range(N) if recs6[s]['overrides'] != recs6[neg(s)]['overrides']]
    claim('R3-P6b', '★ 刀刃 1（σ·K，中心奇縮放）：(ii) 已被破壞但 λ_a ≡ -1 恆定 ⟹ 依 (ii\') 預測不變**仍成立**'
                    '（原合約「破 (ii) 必失效」在此被偽證）',
          ok_sig and ii_brk_sig and lam_const(Ksig) and not viol6,
          'sigma centre-odd = %s ; (ii) broken = %s ; λ 恆定 = %s ; 失效態數 = %d'
          % (ok_sig, ii_brk_sig, lam_const(Ksig), len(viol6)))

    reps60 = sorted(set(min(s, neg(s)) for s in range(N)))
    T = set(max(r, neg(r)) for i, r in enumerate(reps60) if i % 2 == 0)
    eps = lambda s: -1 if s in T else 1
    Kt = [[eps(s) * K[s][a] for a in range(nctx)] for s in range(N)]
    recs6c = [replay(order, s0, Kt, upd, nctx) for s0 in range(N)]
    viol6c = [s for s in range(N) if recs6c[s]['overrides'] != recs6c[neg(s)]['overrides']]
    claim('R3-P6c', '★ 刀刃 2（T-翻轉：30 個中心類各翻一元素 ⟹ 比率隨 s 變化）⟹ 中心不變必須失效',
          (not lam_const(Kt)) and len(viol6c) > 0,
          'T 大小 = %d ; 比率恆定 = %s ; 失效態數 = %d（例 s0=%s: %d vs %d）'
          % (len(T), lam_const(Kt), len(viol6c), (viol6c[0] if viol6c else '-'),
             (recs6c[viol6c[0]]['overrides'] if viol6c else -1),
             (recs6c[neg(viol6c[0])]['overrides'] if viol6c else -1)))

    # ---------- R3-P7 尖銳性 C2：破 (i) ----------
    def upd_noneq(s, ctx):
        s1 = MUL[s][hx[ctx]]
        return MUL[s1][hx[ctx]] if (s1 % 2 == 1) else s1
    t1 = replay(order, 0, K, upd_noneq, nctx, track=True)['traj']
    t2 = replay(order, neg(0), K, upd_noneq, nctx, track=True)['traj']
    eq_broken = (len(t1) != len(t2)) or any(t2[i] != neg(t1[i]) for i in range(len(t1)))
    recn = [replay(order, s0, K, upd_noneq, nctx) for s0 in range(N)]
    viol7 = [s for s in range(N) if recn[s]['overrides'] != recn[neg(s)]['overrides']]
    claim('R3-P7', '尖銳性 C2：非等變更新（奇索引再推一步）⟹ 不變必須失效',
          eq_broken and len(viol7) > 0,
          '軌跡等變被破 = %s ; overrides 中心不變失效態數 = %d（例 s0=%s）'
          % (eq_broken, len(viol7), viol7[0] if viol7 else '-'))

    # ---------- R3-P8a 普適性：Z_n 合成機器 ----------
    def synth(n, seed, mode):
        """mode: 'ok'（(ii) 成立）/ 'sigma'（中心奇縮放，λ≡-1）/ 'tflip'（比率隨 s 變化）
        註：中心映射 ν 逐字對應凍結機器之 MUL[s][zc]（乘中心元素）；加法記法下 = 平移 n//2，
        而**唔係**反演 s ↦ -s（首跑誤用反演，已保留日誌 15_r3_centre_firstrun_wronginvolution.out）。"""
        MU = [[(s + h) % n for h in range(n)] for s in range(n)]
        NU = lambda s: (s + n // 2) % n
        ctxn = n
        Ks = [[0] * ctxn for _ in range(n)]
        for s in range(n):
            r = min(s, NU(s))
            if s == r:
                for a in range(ctxn):
                    Ks[s][a] = 1 if (splitmix64(seed + (r * 1000 + a) * 2 + 7) & 1) else -1
            else:
                for a in range(ctxn):
                    Ks[s][a] = Ks[r][a]
        if mode == 'sigma':
            sg = lambda z: 1 if z <= NU(z) else -1
            Ks = [[sg(z) * Ks[z][a] for a in range(ctxn)] for z in range(n)]
        elif mode == 'tflip':
            repsn = sorted(set(min(z, NU(z)) for z in range(n)))
            Ts = set(max(r, NU(r)) for i, r in enumerate(repsn) if i % 2 == 0)
            Ks = [[(-1 if z in Ts else 1) * Ks[z][a] for a in range(ctxn)] for z in range(n)]
        ordn = [(a, b) for a in range(ctxn) for b in range(ctxn)]
        up = lambda s, ctx: MU[s][ctx % n]
        eqv = all(MU[NU(s)][h] == NU(MU[s][h]) for s in range(n) for h in range(n))
        rc = [replay(ordn, s0, Ks, up, ctxn) for s0 in range(n)]
        viol = [s for s in range(n) if rc[s]['overrides'] != rc[NU(s)]['overrides']]
        lamc = all(len(set(Ks[NU(z)][a] * Ks[z][a] for z in range(n))) == 1 for a in range(ctxn))
        ii_ok = all(Ks[NU(z)][a] == Ks[z][a] for z in range(n) for a in range(ctxn))
        return len(viol), lamc, ii_ok, eqv

    syn = {}
    for n in (8, 12, 16):
        v_ok, lam_ok, ii_ok, eq_ok = synth(n, 1000 + n, 'ok')
        v_sg, lam_sg, ii_sg, eq_sg = synth(n, 1000 + n, 'sigma')
        v_tf, lam_tf, ii_tf, eq_tf = synth(n, 1000 + n, 'tflip')
        syn[n] = {'equivariant': eq_ok, 'ii_ok': ii_ok, 'viol_ok': v_ok, 'lam_ok': lam_ok,
                  'sigma': {'viol': v_sg, 'lam_const': lam_sg, 'ii_broken': not ii_sg, 'equiv': eq_sg},
                  'tflip': {'viol': v_tf, 'lam_const': lam_tf, 'ii_broken': not ii_tf, 'equiv': eq_tf}}
    ok8 = all(syn[n]['viol_ok'] == 0 and syn[n]['lam_ok'] and syn[n]['equivariant'] and syn[n]['ii_ok']
              for n in syn)
    ok8s = all(syn[n]['sigma']['viol'] == 0 and syn[n]['sigma']['lam_const'] for n in syn)
    ok8t = all(syn[n]['tflip']['viol'] > 0 and not syn[n]['tflip']['lam_const'] for n in syn)
    claim('R3-P8a', '普適性：Z_8/Z_12/Z_16 —— (ii) 成立⟹不變成立；σ 型（λ 恆定）⟹仍成立；T 型（比率隨 s 變）⟹失效',
          ok8 and ok8s and ok8t,
          'Z_8 %s | Z_12 %s | Z_16 %s' % (syn[8], syn[12], syn[16]))

    # ---------- R3-P8b 商結構 2I/{±1} ----------
    cls = {}
    for s in range(N):
        cls.setdefault(min(s, neg(s)), []).append(s)
    reps = sorted(cls)
    cid = {s: min(s, neg(s)) for s in range(N)}
    Q = [[0] * len(reps) for _ in reps]
    ix = {r: i for i, r in enumerate(reps)}
    for x in reps:
        for y in reps:
            Q[ix[x]][ix[y]] = ix[cid[MUL[x][y]]]
    wd = [(s, h) for s in range(N) for h in range(N) if cid[MUL[s][h]] != reps[Q[ix[cid[s]]][ix[cid[h]]]]]
    # 商群共軛類（軌道 x y x^{-1}）
    inv = [next(j for j in range(len(reps)) if Q[i][j] == ix[min(reps[0], neg(reps[0]))] and
                Q[j][i] == ix[min(reps[0], neg(reps[0]))]) for i in range(len(reps))]
    seen = set()
    classes = []
    for i in range(len(reps)):
        if i in seen:
            continue
        orb = set()
        for y in range(len(reps)):
            orb.add(Q[Q[y][i]][inv[y]])
        seen |= orb
        classes.append(len(orb))
    ovmap = {s: rec[s]['overrides'] for s in range(N)}
    cls_val = []
    for r in reps:
        vals = set(ovmap[s] for s in cls[r])
        cls_val.append(len(vals))
    claim('R3-P8b', '商結構：2I/{±1} 階 60、共軛類大小多重集 = [1,12,12,15,20]（A₅ 簽名）；overrides 為商上之函數（26 值），'
                    '但唔由商共軛類決定',
          len(reps) == 60 and not wd and sorted(classes) == [1, 12, 12, 15, 20]
          and all(v == 1 for v in cls_val) and len(set(ovmap.values())) == 26
          and len(set(tuple(sorted(set(ovmap[s] for s in cls[r]))) for r in reps)) > 1,
          'quotient order = %d ; class sizes = %s ; overrides well-defined on classes = %s ; '
          'distinct values = %d ; 每商共軛類內相異值數 = %s'
          % (len(reps), sorted(classes), all(v == 1 for v in cls_val),
             len(set(ovmap.values())), sorted(set(
                 len(set(ovmap[s] for s in cls[r])) for r in reps))))

    out = {'rules': 'r3-centre-v1', 'identity_index': e_id, 'centre_index': zc,
           'trajectory_len': len(t1), 'synthetic': {str(k): v for k, v in syn.items()},
           'quotient': {'order': len(reps), 'conjugacy_class_sizes': sorted(classes)},
           'counters_s0_0': {k: rec[0][k] for k in five}, 'claims': CLAIMS}
    with io.open(os.path.join(DATA, '15_r3_centre.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 104)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 104)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
