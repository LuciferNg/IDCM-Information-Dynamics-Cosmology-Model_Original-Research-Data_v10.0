#!/usr/bin/env python3
"""O225 scripts/34 -- R9：Σf 之 protocol 層配對機制（`r9-protocol-pairing-v1`）。

Part A A1–A7（軌跡引理／事件歸約／ε·d 恆等式／逐事件 x-和）
Part B B1a/B1b/B2a/B2b/B3/B4（反演關係、Z10 商形式、對徑軸映射 ρ）
Part C C1–C2（零態事件級分解、Σf_tt = 64 之承載）
精確算術；零浮點；上游 O222 唯讀。用法: /usr/bin/python3 scripts/34_r9_pairing.py
"""
import collections
import hashlib
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
RULES = 'r9-protocol-pairing-v1'
COST = F(123, 88)
EMIN = F(123, 176)
BUDGET = F(10 ** 9)
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''),
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


def run_events(s0, Kt, MULt, hxt, pairs, n_pairs=None):
    """協定逐字同 O222 scripts/30_g1g8_gaps.ledger_replay，但記錄每個比較事件之 (ctx, s_w, s_r)。

    回傳 events = [(ctx, s_w, s_r)]（次序 = 協定比較次序）。pop 還原狀態。
    """
    L = []
    s = s0
    rem = BUDGET
    hits = 0
    events = []
    seq = pairs if n_pairs is None else pairs[:n_pairs]
    for (a, b) in seq:
        spent = 0
        for ctx in (a, b):
            if L and L[-1][0] == ctx:
                hits += 1
                cw, _v, sw = L[-1]
                events.append((cw, sw, s))
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
            cw, _v, sw = L[-1]
            events.append((cw, sw, s))
        else:
            if rem - COST * spent < EMIN:
                raise RuntimeError('terminal')
            L.append((b, Kt[s][b], s))
            s = MULt[s][hxt[b]]
            spent += 1
        rem -= COST * spent
    return events, hits


def main():
    os.makedirs(DATA, exist_ok=True)
    print('=' * 118)
    print('O225 scripts/34 -- R9: protocol-layer pairing of Sigma-f   (%s)' % RULES)
    print('=' * 118, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'r9_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    G, _ig, _M2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'r9_a2').build_group()
    n, ncol = len(K), len(K[0])
    KV = [mm.rot_ref(g, U[0]) for g in G]
    pairs = [(a, b) for a in range(ncol) for b in range(ncol)]
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(sgn(add(U[i][t], U[j][t])) == 0 for t in range(3)):
                partner[i] = j
    d31 = json.load(io.open(os.path.join(DATA, '31_r8_group.json'), encoding='utf-8'))
    f_tf_in, f_ft_in, f_tt_in = d31['f_tf'], d31['f_ft'], d31['f_tt']
    tie = [[dot3(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [firstsgn(KV[s]) for s in range(n)]
    gam = [{a: firstsgn(cross3(U[a], KV[s])) for a in range(ncol) if tie[s][a]} for s in range(n)]
    dind = [[(1 if (gam[s][a] != eps[s]) else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]
    # 一般 d（γ 對任何 (s,a) 皆有定義；不設 tie 限制作為 R7 主公式之 (F,T) 分支用）
    dgen = [[1 if firstsgn(cross3(U[a], KV[s])) != eps[s] else 0 for a in range(ncol)] for s in range(n)]
    ident_l = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))]
    e_state = ident_l[0]
    inv = {}
    for s in range(n):
        for t in range(n):
            if MUL[s][t] == e_state:
                inv[s] = t
                break

    # ---------- 全協定一次（從 e）----------
    events, hits = run_events(e_state, K, MUL, hx, pairs)
    ev_cls = []
    for (a, sw, sr) in events:
        tw, tr = tie[sw][a], tie[sr][a]
        ev_cls.append('TT' if (tw and tr) else ('TF' if tr else ('FT' if tw else 'FF')))
    cnt = collections.Counter(ev_cls)
    info('事件總 = %d ; 類別計數 = %s（R6 之 11200/1120/1280/1280 對照）' % (len(events), dict(cnt)))

    # ---------- A1 軌跡引理（等變）----------
    ev_tr, _h = run_events(e_state, K, MUL, hx, pairs, n_pairs=300)
    dev1 = 0
    for s0 in (0, 1, 5, 62):
        ev2, _h2 = run_events(s0, K, MUL, hx, pairs, n_pairs=300)
        if len(ev2) != len(ev_tr):
            dev1 += 1
            continue
        for i, (a, sw, sr) in enumerate(ev_tr):
            a2, sw2, sr2 = ev2[i]
            if a2 != a or sw2 != MUL[s0][sw] or sr2 != MUL[s0][sr]:
                dev1 += 1
    # 事件集 K-無關（人造 K ≡ 0 對照）
    Kz = [[0] * ncol for _ in range(n)]
    ev_z, _h3 = run_events(e_state, Kz, MUL, hx, pairs, n_pairs=300)
    kfree = (ev_z == ev_tr)
    claim('A1', '★ 推導+核：軌跡等變 — s_t(s0) = s0·s_t(e)（截斷前 300 對、4 個 s0 逐事件核）；且事件集 K-無關',
          dev1 == 0 and kfree and len(ev_tr) > 0,
          '逐事件偏離 = %d ; 事件集 K-無關 = %s ; 截斷事件數 = %d' % (dev1, kfree, len(ev_tr)))

    # ---------- A2 事件歸約 ----------
    def integrand_tf(a, g, x):
        return dind[x][a] * eps[x] * sgn(dot3(U[a], mm.rot_ref(G[x], KV[g])))

    def integrand_ft(a, h, x):
        return dind[x][a] * eps[x] * eps[MUL[x][h]]

    def integrand_tt(a, h, x):
        return (1 if dind[x][a] != dind[MUL[x][h]][a] else 0) * eps[x] * eps[MUL[x][h]]

    cacheTF, cacheFT = {}, {}
    sumTF = sumFT = 0
    Wvec = {}
    for (a, sw, sr), cls in zip(events, ev_cls):
        if cls == 'TF':
            g = MUL[inv[sr]][sw]
            key = (a, g)
            if key not in cacheTF:
                cacheTF[key] = sum(integrand_tf(a, g, x) for x in range(n))
            sumTF += cacheTF[key]
        elif cls == 'FT':
            h = MUL[inv[sw]][sr]
            key = (a, h)
            if key not in cacheFT:
                cacheFT[key] = sum(integrand_ft(a, h, x) for x in range(n))
            sumFT += cacheFT[key]
    # 第三條算式：按 (a,g) 群化重算
    grpTF = collections.Counter()
    grpFT = collections.Counter()
    for (a, sw, sr), cls in zip(events, ev_cls):
        if cls == 'TF':
            grpTF[(a, MUL[inv[sr]][sw])] += 1
        elif cls == 'FT':
            grpFT[(a, MUL[inv[sw]][sr])] += 1
    sumTF_grp = sum(nm * cacheTF[k] for k, nm in grpTF.items())
    sumFT_grp = sum(nm * cacheFT[k] for k, nm in grpFT.items())
    dev2 = 0
    # 直接逐事件重算（不經快取）抽核全部 TF/FT 事件
    sumTF_direct = 0
    for (a, sw, sr), cls in zip(events, ev_cls):
        if cls == 'TF':
            g = MUL[inv[sr]][sw]
            sumTF_direct += sum(integrand_tf(a, g, x) for x in range(n))
    claim('A2', '★ 推導+核：Σ_{s0} f_tf(s0) = Σ_{e∈TF} W_e 且 Σ_{s0} f_ft(s0) = Σ_{e∈FT} W\'_e（三條算式互核，0 偏離）',
          sumTF == sum(f_tf_in) == 0 and sumFT == sum(f_ft_in) == 0
          and sumTF == sumTF_grp == sumTF_direct and sumFT == sumFT_grp,
          'Σf_tf(輸入) = %d ; Σ W_e = %d（群化 %d／直接 %d）；Σf_ft(輸入) = %d ; Σ W\'_e = %d（群化 %d）'
          % (sum(f_tf_in), sumTF, sumTF_grp, sumTF_direct, sum(f_ft_in), sumFT, sumFT_grp))

    # ---------- A3 ε·d 恆等式 ----------
    dev3 = 0
    for s in range(n):
        for a in range(ncol):
            if tie[s][a]:
                lhs = eps[s] * dind[s][a]
                rhs = (eps[s] - gam[s][a]) // 2
                if lhs != rhs:
                    dev3 += 1
    claim('A3', '★ 推導+核：ε(x)·d(x,a) = (ε(x) − γ(a,x))/2（全部 1200 個 tie 條目，0 偏離）',
          dev3 == 0, '偏離 = %d（tie 條目總 = %d）' % (dev3, sum(1 for s in range(n) for a in range(ncol) if tie[s][a])))

    # ---------- A4 事件級關係 s_w = s_r·g_e（歸約之核心）----------
    dev4 = 0
    keyset = set()
    for (a, sw, sr), cls in zip(events, ev_cls):
        if cls == 'TF':
            g = MUL[inv[sr]][sw]
            if MUL[sr][g] != sw:
                dev4 += 1
            keyset.add(('TF', a, g))
        elif cls == 'FT':
            h = MUL[inv[sw]][sr]
            if MUL[sw][h] != sr:
                dev4 += 1
            keyset.add(('FT', a, h))
    claim('A4', '★ 預測（見數前）：逐事件 s_w = s_r·g_e（或 s_r = s_w·ĥ_e）成立；Φ_e 只依 (a_e, g_e)',
          dev4 == 0, '關係偏離 = %d ; 相異 (類,a,g) 鍵數 = %d ; TF/FT 鍵數 = %d/%d'
          % (dev4, len(keyset), len(cacheTF), len(cacheFT)))

    # ---------- A2c/A5ac/A5bc/A5cc/A5dc：校正版（按事件三重 (a,g)，分類**逐 x** 判定）----------
    tg = collections.Counter()
    for (a, sw, sr) in events:
        g = MUL[inv[sr]][sw]
        tg[(a, g)] += 1
    Sq = {}
    for (a, g) in sorted(tg):
        kv_g = KV[g]
        perm_g = [MUL[x][g] for x in range(n)]
        sTF = sFT = sTT = 0
        for x in range(n):
            tx = tie[x][a]
            ty = dot3(U[a], mm.rot_ref(G[x], kv_g)) == (0, 0)
            y = perm_g[x]
            if tx and ty:
                sTT += (1 if dind[x][a] != dind[y][a] else 0) * eps[x] * eps[y]
            elif tx and not ty:
                sTF += dind[x][a] * eps[x] * sgn(dot3(U[a], mm.rot_ref(G[x], kv_g)))
            elif ty and not tx:
                sFT += dgen[y][a] * eps[y] * sgn(dot3(U[a], KV[x]))
        Sq[(a, g)] = (sTF, sFT, sTT)
    sumTF_c = sum(tg[k] * Sq[k][0] for k in tg)
    sumFT_c = sum(tg[k] * Sq[k][1] for k in tg)
    sumTT_c = sum(tg[k] * Sq[k][2] for k in tg)
    claim('A2c', '★ 校正（新 tag）：Σ_{s0} f_tf = Σ_{(a,g)} n·S_TF、Σ f_ft = Σ n·S_FT、Σ f_tt = Σ n·S_TT（三重 (a,g) 逐 x 分類）',
          sumTF_c == sum(f_tf_in) == 0 and sumFT_c == sum(f_ft_in) == 0 and sumTT_c == sum(f_tt_in) == 64,
          'Σ n·S_TF = %d ; Σ n·S_FT = %d ; Σ n·S_TT = %d（輸入 0 / 0 / 64）；三重數 = %d ; 相異 (a,g) = %d'
          % (sumTF_c, sumFT_c, sumTT_c, len(events), len(tg)))
    nzTF_c = [(k, v[0]) for k, v in Sq.items() if v[0] != 0]
    nzFT_c = [(k, v[1]) for k, v in Sq.items() if v[1] != 0]
    claim('A5ac', '★★ 校正（新 tag，核心）：對全部 (a,g)：S_TF(a,g) = 0 且 S_FT(a,g) = 0（逐鍵局部消失）',
          not nzTF_c and not nzFT_c,
          'S_TF 非零鍵 = %d（%s）；S_FT 非零鍵 = %d（%s）；鍵數 = %d'
          % (len(nzTF_c), nzTF_c[:4], len(nzFT_c), nzFT_c[:4], len(tg)))
    claim('A5bc', '★ 校正（新 tag）：S_TT 之值集與 Σ n·S_TT = 64 之承載',
          sumTT_c == 64, 'Σ n·S_TT = %d ; S_TT 值集 = %s ; 非零鍵 = %d'
          % (sumTT_c, sorted(set(v[2] for v in Sq.values())), sum(1 for v in Sq.values() if v[2] != 0)))
    tf_keys = [k for k in Sq if Sq[k][0] != 0] or [k for k in Sq]
    c1c = sum(1 for (a, g) in tf_keys if Sq.get((partner[a], g), (0,))[0] == -Sq[(a, g)][0])
    c2c = sum(1 for (a, g) in tf_keys if Sq.get((a, inv[g]), (0,))[0] == -Sq[(a, g)][0])
    claim('A5cc', '★ 校正（新 tag）：S_TF(a,g) = −S_TF(ā,g)', c1c == len(tf_keys), '成立 %d / %d' % (c1c, len(tf_keys)))
    claim('A5dc', '★ 校正（新 tag）：S_TF(a,g) = −S_TF(a,g^{-1})', c2c == len(tf_keys), '成立 %d / %d' % (c2c, len(tf_keys)))

    # ---------- A5a 逐事件 x-和之消失 ----------
    nzTF = [(a, g, v) for (a, g), v in cacheTF.items() if v != 0]
    nzFT = [(a, h, v) for (a, h), v in cacheFT.items() if v != 0]
    claim('A5a', '★★ 預測（見數前，核心）：對全部 (T,F) 事件 W_e = 0；對全部 (F,T) 事件 W\'_e = 0',
          not nzTF and not nzFT,
          'TF 非零鍵 = %d（例 %s）；FT 非零鍵 = %d（例 %s）；TF 鍵數 = %d、FT 鍵數 = %d'
          % (len(nzTF), nzTF[:3], len(nzFT), nzFT[:3], len(cacheTF), len(cacheFT)))

    # ---------- A5b (T,T) 之 W'' ----------
    tt_vals = []
    for (a, sw, sr), cls in zip(events, ev_cls):
        if cls == 'TT':
            h = MUL[inv[sw]][sr]
            tt_vals.append(sum(integrand_tt(a, h, x) for x in range(n)))
    claim('A5b', '預測：報告 (T,T) 事件之 W\'\'_e 值集，並核 Σ W\'\'_e = Σf_tt = 64',
          sum(tt_vals) == sum(f_tt_in) == 64,
          'Σ W\'\'_e = %d ; Σf_tt(輸入) = %d ; 值集 = %s ; TT 事件數 = %d'
          % (sum(tt_vals), sum(f_tt_in), sorted(set(tt_vals)), len(tt_vals)))

    # ---------- A5c/A5d（A5a 若敗才判）----------
    wsp = {}
    for (a, g), v in cacheTF.items():
        wsp[('TF', a, g)] = v
    for (a, h), v in cacheFT.items():
        wsp[('FT', a, h)] = v
    keysTF = sorted(cacheTF)
    c1 = sum(1 for (a, g) in keysTF if (partner[a], g) in cacheTF and cacheTF[(partner[a], g)] == -cacheTF[(a, g)])
    c2 = sum(1 for (a, g) in keysTF if (a, inv[g]) in cacheTF and cacheTF[(a, inv[g])] == -cacheTF[(a, g)])
    claim('A5c', '預測（A5a 若敗才判）：W(a,g) = −W(ā,g) 逐 (a,g)',
          len(keysTF) > 0 and c1 == len(keysTF), '成立對數 = %d / %d' % (c1, len(keysTF)))
    claim('A5d', '預測（A5a 若敗才判）：W(a,g) = −W(a,g^{-1}) 逐 (a,g)',
          len(keysTF) > 0 and c2 == len(keysTF), '成立對數 = %d / %d' % (c2, len(keysTF)))

    # ---------- A6 兩半相等 ----------
    dev6 = 0
    for (a, g) in keysTF:
        B = [sgn(dot3(U[a], mm.rot_ref(G[x], KV[g]))) for x in range(n)]
        W1 = sum(eps[x] * B[x] for x in range(n) if tie[x][a])
        W2 = sum(gam[x][a] * B[x] for x in range(n) if tie[x][a])
        if 2 * cacheTF[(a, g)] != W1 - W2:
            dev6 += 1
    claim('A6', '★ 預測（見數前）：W = ½[W1 − W2] 逐 (a,g) 成立（W1 := Σ_{tie} εB、W2 := Σ_{tie} γB）',
          dev6 == 0, '偏離 = %d / %d' % (dev6, len(keysTF)))

    # ---------- A7 報告 ----------
    allg = collections.Counter()
    for (a, g) in keysTF:
        allg[g] += 1
    Wvals = sorted(set(cacheTF.values()))
    info('A7 報告：TF 相異 (a,g) 對 = %d（快取鍵）；FT = %d；W 值集 = %s' % (len(cacheTF), len(cacheFT), Wvals))
    info('A7 報告：TF 之 g 階分佈 = %s ; n(a,g) 重數分佈 = %s'
         % (dict(sorted(collections.Counter(d31['orders'][g] for g in allg).items())),
            dict(sorted(collections.Counter(grpTF.values()).items()))))
    claim('A7', '報告：(a,g) 表（鍵數、重數分佈、W 值集、g 階分佈）＋ 事件類計數',
          True, 'TF 鍵 = %d、FT 鍵 = %d；g 階 = %s；重數分佈 = %s；事件類 = %s'
          % (len(cacheTF), len(cacheFT), dict(sorted(collections.Counter(d31['orders'][g] for g in allg).items())),
             dict(sorted(collections.Counter(grpTF.values()).items())), dict(cnt)))

    # ---------- Part B ----------
    b1a = sum(1 for s in range(n) if f_tf_in[inv[s]] == f_ft_in[s])
    b1b = sum(1 for s in range(n) if f_tf_in[inv[s]] == -f_ft_in[s])
    claim('B1a', '★ 預測（見數前）：f_tf(s^{-1}) = f_ft(s) ∀120', b1a == n, '成立 %d/120' % b1a)
    claim('B1b', '★ 預測（見數前）：f_tf(s^{-1}) = −f_ft(s) ∀120', b1b == n, '成立 %d/120' % b1b)
    b2a = sum(1 for s in range(n) if f_ft_in[inv[s]] == f_tf_in[s])
    b2b = sum(1 for s in range(n) if f_ft_in[inv[s]] == -f_tf_in[s])
    claim('B2a', '★ 預測（見數前）：f_ft(s^{-1}) = f_tf(s) ∀120', b2a == n, '成立 %d/120' % b2a)
    claim('B2b', '★ 預測（見數前）：f_ft(s^{-1}) = −f_tf(s) ∀120', b2b == n, '成立 %d/120' % b2b)
    b4 = sum(1 for s in range(n) if f_tt_in[inv[s]] == f_tt_in[s])
    claim('B4', '★ 預測（見數前）：f_tt(s^{-1}) = f_tt(s) ∀120', b4 == n, '成立 %d/120' % b4)
    # B3 報告：ρ（對徑軸映射）
    tgt0 = tuple(neg(c) for c in U[0])
    w_cand = [s for s in range(n) if KV[s] == tgt0]
    rho_ok = False
    Z10 = d31['A1']['Z10']
    if w_cand:
        w = w_cand[0]
        rho_ok = all(KV[MUL[s][w]] == tuple(neg(c) for c in KV[s]) for s in range(n))
        keep = sum(1 for s in Z10 if MUL[s][w] in Z10)
        flip_tf = sum(1 for s in range(n) if f_tf_in[MUL[s][w]] == -f_tf_in[s])
        flip_ft = sum(1 for s in range(n) if f_ft_in[MUL[s][w]] == -f_ft_in[s])
        same_tf = sum(1 for s in range(n) if f_tf_in[MUL[s][w]] == f_tf_in[s])
        info('B3 報告：w（KV[w] = −U[0]）之階 = %d ; 候選數 = %d ; ρ 全域成立 = %s ; ρ(Z10) ⊆ Z10 : %d/10 ; '
             'ρ 反號 f_tf : %d/120 ; ρ 保持 f_tf : %d/120 ; ρ 反號 f_ft : %d/120'
             % (d31['orders'][w], len(w_cand), rho_ok, keep, flip_tf, same_tf, flip_ft))
        claim('B3', '報告：Z10 之商形式 + 對徑軸映射 ρ(s) = s·w（rot(w)U[0] = −U[0]）之作用',
              rho_ok and keep == 10, 'w 階 = %d ; ρ 保持 Z10 = %d/10 ; ρ 反號 f_tf = %d ; ρ 保持 f_tf = %d'
              % (d31['orders'][w], keep, flip_tf, same_tf))
    else:
        claim('B3', '報告：Z10 之商形式 + 對徑軸映射 ρ', False, '找不到 w（KV[w] = −U[0]）')

    # ---------- Part C（校正版：逐態、逐 x 分類之重建；原 C1/C2 之 buggy 值保留）----------
    triples = [(a, MUL[inv[sr]][sw]) for (a, sw, sr) in events]
    _sc = {}

    def sgn_uw(a, w):
        k = (a, w)
        if k not in _sc:
            _sc[k] = sgn(dot3(U[a], KV[w]))
        return _sc[k]
    tfv = [0] * n
    ftv = [0] * n
    ttv = [0] * n
    for s0 in range(n):
        a1 = a2 = a3 = 0
        for (a, swe, sre) in events:          # 以**實際**讀／寫態（s0·s_r(e)、s0·s_w(e)）逐態分類
            w = MUL[s0][swe]
            r = MUL[s0][sre]
            tw, tr = tie[w][a], tie[r][a]
            if tw and tr:
                a3 += (0 if dind[r][a] == dind[w][a] else 1) * eps[r] * eps[w]
            elif tr:
                a1 += dind[r][a] * eps[r] * sgn_uw(a, w)
            elif tw:
                a2 += dgen[w][a] * eps[w] * sgn_uw(a, r)
        tfv[s0], ftv[s0], ttv[s0] = a1, a2, a3
    okc = (tfv == f_tf_in and ftv == f_ft_in and ttv == f_tt_in)
    claim('C1c', '★★ 校正（新 tag）：逐態、逐 x 分類之重建 — f_tf/f_ft/f_tt 之 120 態值全部等於 R8 輸入（0 偏離）',
          okc, 'f_tf 同 = %s ; f_ft 同 = %s ; f_tt 同 = %s ; Σ = (%d, %d, %d)'
          % (tfv == f_tf_in, ftv == f_ft_in, ttv == f_tt_in, sum(tfv), sum(ftv), sum(ttv)))
    zeros = [s for s in range(n) if d31['delta'][s] == 0]
    info('C1c 報告：零態之（重建）分解 = %s' % {str(s): (tfv[s], ftv[s], ttv[s]) for s in zeros})
    by_a = collections.Counter()
    for (a, g) in triples:
        by_a[a] += Sq[(a, g)][2]
    claim('C2c', '校正（新 tag）：Σf_tt = 64 之 (a, W'') 承載（三重版）',
          sum(by_a.values()) == 64, '列承載和 = %d ; 承載列數 = %d ; 列值 = %s'
          % (sum(by_a.values()), len(by_a), dict(sorted(by_a.items()))))
    info('C2c 報告：Σf_tt 之列承載 = %s' % dict(sorted(by_a.items())))

    out = {'rules': RULES, 'events': len(events), 'event_class_counts': dict(cnt),
           'events_sha': hashlib.sha256(repr(events).encode('utf-8')).hexdigest(),
           'A1': {'dev': dev1, 'k_free': kfree}, 'A2': {'sumTF': sumTF, 'sumFT': sumFT, 'sumTF_grp': sumTF_grp,
                                                        'sumTF_direct': sumTF_direct},
           'A3': {'dev': dev3}, 'A4': {'dev': dev4, 'keys': len(keyset)},
 'A2c': {'sumTF_c': sumTF_c, 'sumFT_c': sumFT_c, 'sumTT_c': sumTT_c, 'n_triples': len(events),
         'n_keys': len(tg)},
 'A5ac': {'nzTF': [[int(k[0]), int(k[1]), int(v)] for k, v in nzTF_c],
          'nzFT': [[int(k[0]), int(k[1]), int(v)] for k, v in nzFT_c]},
 'A5bc': {'sum': sumTT_c, 'S_TT_valset': sorted(set(v[2] for v in Sq.values()))},
 'Sq_table': {str((int(k[0]), int(k[1]))): [int(v[0]), int(v[1]), int(v[2])] for k, v in Sq.items()},
 'tg': {str((int(k[0]), int(k[1]))): int(v) for k, v in tg.items()},
           'A5a': {'nzTF': [[int(a), int(g), int(v)] for a, g, v in nzTF],
                   'nzFT': [[int(a), int(h), int(v)] for a, h, v in nzFT],
                   'nTF_keys': len(cacheTF), 'nFT_keys': len(cacheFT)},
           'A5b': {'sum': sum(tt_vals), 'valset': sorted(set(tt_vals)), 'n_TT': len(tt_vals)},
           'A5c': {'hit': c1, 'total': len(keysTF)}, 'A5d': {'hit': c2, 'total': len(keysTF)},
           'A6': {'dev': dev6}, 'A7': {'W_valset': Wvals, 'g_orders': dict(sorted(
               collections.Counter(d31['orders'][g] for g in allg).items())),
               'mult_dist': dict(sorted(collections.Counter(grpTF.values()).items()))},
           'B1a': b1a, 'B1b': b1b, 'B2a': b2a, 'B2b': b2b, 'B4': b4, 'C1': {'superseded_by': 'C1c'},
           'C1c': {'ok': okc, 'zeros': {str(s): [int(tfv[s]), int(ftv[s]), int(ttv[s])] for s in zeros},
                   'sums': [int(sum(tfv)), int(sum(ftv)), int(sum(ttv))]},
           'C2c': {'by_a': {str(k): int(v) for k, v in sorted(by_a.items())}, 'sum': int(sum(by_a.values()))},
           'recon': {'f_tf': [int(x) for x in tfv], 'f_ft': [int(x) for x in ftv], 'f_tt': [int(x) for x in ttv]},
           'C2': {'superseded_by': 'C2c'},
           'claims': CLAIMS}
    with io.open(os.path.join(DATA, '34_r9_pairing.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 118)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
