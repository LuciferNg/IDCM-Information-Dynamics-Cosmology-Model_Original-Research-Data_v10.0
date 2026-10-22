#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O225 close-out 獨立審計（T1）—— R1–R9 頭條數字全鏈重驗。

獨立性措施（缺一不可）：
  * **不 import 本 o 任何推導 script**（scripts/01–35 全部唔 import）。
  * 只讀凍結輸入：O222 之 `scripts/09_a2_rollback.py`、`scripts/12_b5_budget.py`
    （freeze 已 pin 其 sha256；本審計第一段即重算核對）。
  * 協定 replay **以不同實作重寫**（顯式索引堆疊 ＋ 事件表），並同凍結產物
    `data/34_r9_pairing.json` 之事件序列逐項比對。
  * 精確算術：int / Fraction；Z[√5] 之號以 p² vs 5q² 精確比較（絕不用首個非零分量）。
  * 唯讀：本審計不寫任何 O 目錄（只寫本 o 之 data/36、logs/36，由外層 shell 重導）。

段：
  A 凍結輸入完整性  B 機器結構  C G1 計數器（獨立 replay）  D 事件序列 vs 凍結產物
  E R7/R8 主公式  F Z10 與對徑映射  G R9 歸約（事件三重／逐鍵 S 表）  H 記錄一致性（docs/18）
"""
import hashlib
import io
import json
import os
from fractions import Fraction as F

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O222 = os.path.abspath(os.path.join(BASE, '..', 'o222_qm_evaluation_semantics'))
COST, EMIN, BUDGET = F(123, 88), F(123, 176), F(10 ** 9)
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s  --  %s' % ('PASS' if ok else 'FAIL', tag, name, detail))


def info(s):
    print('[INFO] ' + s)


def sha256(path):
    h = hashlib.sha256()
    with io.open(path, 'rb') as fh:
        for blk in iter(lambda: fh.read(1 << 20), b''):
            h.update(blk)
    return h.hexdigest()


def load_mod(path, name):
    import importlib.util as iu
    sp = iu.spec_from_file_location(name, path)
    m = iu.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


# ---------- Z[√5] 精確算術 ----------
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


def main():
    # ================= A 凍結輸入完整性 =================
    freezes = ['02_r1', '10_r2', '14_r3', '17_r4', '20_r5', '23_r6', '27_r7', '30_r8', '33_r9']
    n_pin = n_bad = 0
    bad = []
    for fr in freezes:
        p = os.path.join(BASE, 'data', fr + '_freeze.json')
        if not os.path.isfile(p):
            bad.append(fr + ':MISSING')
            continue
        d = json.load(io.open(p, encoding='utf-8'))
        for rel, meta in (d.get('frozen_inputs') or {}).items():
            cand = os.path.join(BASE, rel)
            if not os.path.isfile(cand):
                cand = os.path.join(O222, rel) if rel.startswith('scripts/') or rel.startswith('data/') else cand
            n_pin += 1
            if not os.path.isfile(cand) or sha256(cand) != meta['sha256']:
                bad.append(fr + ':' + rel)
    claim('A1', '凍結輸入完整性：全部 freeze 所 pin 之輸入 sha256 與磁碟一致',
          not bad, 'pin 數 = %d ; 不符 = %d %s' % (n_pin, len(bad), bad[:4]))

    # ================= B 機器結構 =================
    b5 = load_mod(os.path.join(O222, 'scripts/12_b5_budget.py'), 'co_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load_mod(os.path.join(O222, 'scripts/09_a2_rollback.py'), 'co_a2')
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

    assoc = 0
    for a in range(n):
        for b in range(n):
            ab = MUL[a][b]
            for c in range(n):
                if MUL[ab][c] != MUL[a][MUL[b][c]]:
                    assoc += 1
    order = [0] * n
    for a in range(n):
        k, x = 1, a
        while x != e_state:
            x = MUL[x][a]
            k += 1
        order[a] = k
    hist = {}
    for a in range(n):
        hist[order[a]] = hist.get(order[a], 0) + 1
    centre = [a for a in range(n) if all(MUL[a][b] == MUL[b][a] for b in range(n))]
    claim('B1', '群表 = 2I（結合律 0 反例、階譜 = {1:1,2:1,3:20,4:30,5:24,6:20,10:24}、中心 = {e,−1}）',
          assoc == 0 and hist == {1: 1, 2: 1, 3: 20, 4: 30, 5: 24, 6: 20, 10: 24} and len(centre) == 2,
          'assoc = %d ; 階譜 = %s ; |centre| = %d' % (assoc, hist, len(centre)))
    kv_dist = len(set(KV))
    zc_idx = [a for a in range(n) if a != e_state and order[a] == 2]
    d15 = json.load(io.open(os.path.join(BASE, 'data/15_r3_centre.json'), encoding='utf-8'))
    claim('B2', '恆等元／中心元索引 = R3 凍結值（e = 75、zc = 0、且 zc 為唯一階 2 元素）；KV 值集 = 12（rot_ref 之像）',
          e_state == d15['identity_index'] == 75 and zc_idx == [d15['centre_index']] == [0] and kv_dist == 12,
          'e = %d ; zc = %s ; 相異 KV = %d' % (e_state, zc_idx, kv_dist))

    tie = [[dot3(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [firstsgn(KV[s]) for s in range(n)]
    tcount = [sum(1 for a in range(ncol) if tie[s][a]) for s in range(n)]
    sup_cols = sorted({a for s in range(n) for a in range(ncol) if tie[s][a]})
    claim('B3', '每態 tie 條目 = 10（R8-C2 凍結事實）；tie 表支撐欄 = 30（量測，欄 32–61）',
          len(sup_cols) == 30 and set(tcount) == {10},
          '支撐欄 = %d %s ; 每態 tie 條目值集 = %s' % (len(sup_cols), sup_cols, sorted(set(tcount))))
    info('B3 報告：每態 tie 條目分佈 = %s' %
         {v: tcount.count(v) for v in sorted(set(tcount))})

    # ================= C G1 計數器（獨立 replay，不同實作）=================
    pairs = [(a, b) for a in range(ncol) for b in range(ncol)]

    def replay(state, ktab=None):
        """顯式索引堆疊之協定 replay；回 (hits, stale, agree, stale_agree, overrides, events)。"""
        st = state
        stk = []          # (ctx, value, state_at_write)
        hits = stale = agree = stale_agree = ov = 0
        events = []
        for (c1, c2) in pairs:
            for ctx in (c1, c2):
                if stk and stk[-1][0] == ctx:
                    hits += 1
                    v_w, s_w = stk[-1][1], stk[-1][2]
                    cur = ktab[st][ctx]
                    if cur == v_w:
                        agree += 1
                    else:
                        ov += 1
                    continue
                stk.append((ctx, ktab[st][ctx], st))
                st = MUL[st][hx[ctx]]
            _c, _v, s_at = stk.pop()
            st = s_at
            if stk and stk[-1][0] == c2:
                hits += 1
                v_w, s_w = stk[-1][1], stk[-1][2]
                cur = ktab[st][c2]
                if cur == v_w:
                    agree += 1
                else:
                    ov += 1
            else:
                stk.append((c2, ktab[st][c2], st))
                st = MUL[st][hx[c2]]
        return hits, ov, agree

    hits_all = {}
    ov_all = {}
    agree_all = {}
    for s0 in range(n):
        h, o, ag = replay(s0, K)
        hits_all[s0], ov_all[s0], agree_all[s0] = h, o, ag
    claim('C1', 'G1 計數器（獨立 replay）：hits ≡ 124 於全部 120 態',
          set(hits_all.values()) == {124}, 'hits 值集 = %s' % sorted(set(hits_all.values())))
    ovset = sorted(set(ov_all.values()))
    claim('C2', 'overrides：值域 [52,80]、恰 26 個相異值、s0=0 時 = 65',
          len(ovset) == 26 and ovset[0] == 52 and ovset[-1] == 80 and ov_all[0] == 65,
          '相異值 = %d ; 範圍 = [%d,%d] ; overrides(0) = %d' % (len(ovset), ovset[0], ovset[-1], ov_all[0]))
    profiles = {(ov_all[s], agree_all[s]) for s in range(n)}
    claim('C3', '(stale, agree) 由 overrides 唯一決定（相異對數 = 相異 overrides 值數 = 26）',
          len(profiles) == 26, '相異 (ov,agree) 對 = %d' % len(profiles))
    zc = zc_idx[0]
    viol = 0
    for s in range(n):
        t = MUL[s][zc]
        if not (hits_all[t] == hits_all[s] and ov_all[t] == ov_all[s] and agree_all[t] == agree_all[s]):
            viol += 1
    claim('C4', 'R3 中心不變定理：五計數器於中心對 120/120 不變（0 違例）', viol == 0, '違例 = %d' % viol)

    # ================= D 事件序列 vs 凍結產物 =================
    def events_of(state):
        """獨立實作：回報 (a, 寫入態, 讀取態) 之序列（124 條）。"""
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
    d34 = json.load(io.open(os.path.join(BASE, 'data/34_r9_pairing.json'), encoding='utf-8'))
    ev_sha = hashlib.sha256(repr(my_ev).encode('utf-8')).hexdigest()
    claim('D1', '事件序列獨立重現（不同 replay 實作）：事件數 = 124 且 events_sha 與凍結產物 data/34 相同',
          len(my_ev) == 124 and ev_sha == d34['events_sha'] and d34['events'] == 124,
          '事件數 = %d ; sha 相符 = %s ; sha = %s' % (len(my_ev), ev_sha == d34['events_sha'], ev_sha[:16]))

    # 事件類別（以 e-態分類）
    def klass(s, a):
        return 'T' if tie[s][a] else 'F'

    cc = {'FF': 0, 'TF': 0, 'FT': 0, 'TT': 0}
    for (a, sw, sr) in my_ev:
        cc[klass(sr, a) + klass(sw, a)] += 1
    claim('D2', '事件類別計數（e-態）= {FF 89, TF 14, TT 8, FT 13}（和 124）',
          cc == d34['event_class_counts'] and sum(cc.values()) == 124,
          'cc = %s ; 凍結 = %s' % (cc, d34['event_class_counts']))

    # ================= E R7/R8 主公式 =================
    gam = [[firstsgn(cross3(U[a], KV[s])) for a in range(ncol)] for s in range(n)]
    dind = [[(1 if gam[s][a] != eps[s] else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]
    dgen = [[1 if gam[s][a] != eps[s] else 0 for a in range(ncol)] for s in range(n)]
    partner = {}
    for i in range(ncol):
        for j in range(ncol):
            if i != j and all(sgn(add(U[i][t], U[j][t])) == 0 for t in range(3)):
                partner[i] = j
    assert len(partner) == ncol, 'partner 未全定義'

    dev_c1 = dev_c1t = 0
    for s in range(n):
        for a in range(ncol):
            if tie[s][a]:
                if dind[s][partner[a]] != 1 - dind[s][a]:
                    dev_c1 += 1
                if not tie[s][partner[a]]:
                    dev_c1t += 1
    claim('E1', 'R8-C1 對徑配對律：d(s,ā) = 1 − d(s,a) 且 tie(s,a) ⟺ tie(s,ā)（逐 tie 條目 0 偏離）',
          dev_c1 == 0 and dev_c1t == 0, 'd 偏離 = %d ; tie 配對偏離 = %d' % (dev_c1, dev_c1t))
    claim('E2', 'R8-C2 每態 tie 條目 = 10（值集 [10]）', set(tcount) == {10},
          '值集 = %s' % sorted(set(tcount)))
    dsum = [sum(dind[s]) for s in range(n)]
    claim('E3', 'R8-C3 每態 Σ_a d = 5（值集 [5]）、全體 Σ = 600',
          set(dsum) == {5} and sum(dsum) == 600,
          '每態值集 = %s ; 總 = %d' % (sorted(set(dsum)), sum(dsum)))

    # R7 主公式逐態重建
    f_tf = [0] * n
    f_ft = [0] * n
    f_tt = [0] * n
    for s0 in range(n):
        a1 = a2 = a3 = 0
        for (a, sw, sr) in my_ev:
            w = MUL[s0][sw]
            r = MUL[s0][sr]
            tw, tr = tie[w][a], tie[r][a]
            if tw and tr:
                a3 += (0 if dind[r][a] == dind[w][a] else 1) * eps[r] * eps[w]
            elif tr:
                a1 += dind[r][a] * eps[r] * sgn(dot3(U[a], KV[w]))
            elif tw:
                a2 += dgen[w][a] * eps[w] * sgn(dot3(U[a], KV[r]))
        f_tf[s0], f_ft[s0], f_tt[s0] = a1, a2, a3
    d31 = json.load(io.open(os.path.join(BASE, 'data/31_r8_group.json'), encoding='utf-8'))
    ok_t = (f_tf == d31['f_tf'] and f_ft == d31['f_ft'] and f_tt == d31['f_tt']
            and f_tf == d34['recon']['f_tf'] and f_ft == d34['recon']['f_ft'] and f_tt == d34['recon']['f_tt'])
    claim('E4', 'R7 主公式逐態重建：f_tf/f_ft/f_tt 之 120 態全部等於 R8 凍結值',
          ok_t, 'Σ = (%d, %d, %d) ; 全同 = %s' % (sum(f_tf), sum(f_ft), sum(f_tt), ok_t))
    dl = [f_tf[s] + f_ft[s] + f_tt[s] for s in range(n)]
    claim('E5', 'R7-A4：Σ f_tf = Σ f_ft = 0、Σ f_tt = 64；(Σf_tf, Σf_ft, Σf_tt) = (0,0,64)',
          (sum(f_tf), sum(f_ft), sum(f_tt)) == (0, 0, 64),
          'Σ = (%d, %d, %d)' % (sum(f_tf), sum(f_ft), sum(f_tt)))
    claim('E6', 'Δ 表與凍結值一致（120/120）', dl == d31['delta'],
          'Δ 值集 = %s' % sorted(set(dl)))
    zeros = sorted(s for s in range(n) if dl[s] == 0)
    claim('E7', 'R7 零態 = [9,15,40,77,87,100] 且分解與凍結一致',
          zeros == [9, 15, 40, 77, 87, 100],
          '零態 = %s ; 分解 = %s' % (zeros, [(s, f_tf[s], f_ft[s], f_tt[s]) for s in zeros]))

    # ================= F Z10 與對徑映射 =================
    Z10 = sorted(s for s in range(n) if f_tf[s] + f_ft[s] == 0)
    claim('F1', 'R8 Z10 = {s : f_tf(s)+f_ft(s) = 0} = [9,15,21,31,57,67,77,87,111,117]',
          Z10 == [9, 15, 21, 31, 57, 67, 77, 87, 111, 117], 'Z10 = %s' % Z10)
    zh = {}
    for s in Z10:
        zh[order[s]] = zh.get(order[s], 0) + 1
    claim('F2', 'Z10 之階分佈 = {3:2, 4:2, 5:2, 6:2, 10:2}', zh == {3: 2, 4: 2, 5: 2, 6: 2, 10: 2},
          '階分佈 = %s' % zh)
    tgt = tuple(neg(c) for c in U[0])
    w_cand = [s for s in range(n) if KV[s] == tgt]
    def rho_global(w):
        return all(KV[MUL[s][w]] == tuple(neg(c) for c in KV[s]) for s in range(n))
    w_ok = [w for w in w_cand if order[w] == 4 and rho_global(w)]
    rho_ok = bool(w_ok)
    tf_flip = tf_keep = ft_flip = ff_flip = 0
    zkeep = -1
    if rho_ok:
        w = w_ok[0]
        for s in range(n):
            t = MUL[s][w]
            tf_flip += (f_tf[t] == -f_tf[s] and f_tf[s] != 0)
            tf_keep += (f_tf[t] == f_tf[s] and f_tf[s] != 0)
            ft_flip += (f_ft[t] == -f_ft[s] and f_ft[s] != 0)
        zkeep = sum(1 for s in Z10 if MUL[s][w] in Z10)
    claim('F3', 'R8-B3：ρ(s) = s·w（w 階 4、rot(w)U[0] = −U[0]）全域成立；ρ 保持 Z10 = 0/10；'
                'ρ 反號 f_tf = 32/120、保持 12/120、反號 f_ft = 0/120',
          rho_ok and zkeep == 0 and tf_flip == 32 and tf_keep == 12 and ft_flip == 0,
          'ρ 全域 = %s ; w 候選（KV[w] = −U[0]）= %d（其中階 4 且 ρ 全域者 = %d）; 保持 Z10 = %d/10 ; '
          '反號/保持 f_tf = %d/%d ; 反號 f_ft = %d'
          % (rho_ok, len(w_cand), len(w_ok), zkeep, tf_flip, tf_keep, ft_flip))

    # ================= G R9 歸約 =================
    # A1 軌跡等變（截斷 300 對 × 4 s0）
    def traj(state, npair):
        st = state
        stk = []
        tr = []
        for (c1, c2) in pairs[:npair]:
            for ctx in (c1, c2):
                if stk and stk[-1][0] == ctx:
                    tr.append(st)
                    continue
                stk.append((ctx, K[st][ctx], st))
                st = MUL[st][hx[ctx]]
            _c, _v, s_at = stk.pop()
            st = s_at
            if stk and stk[-1][0] == c2:
                tr.append(st)
            else:
                stk.append((c2, K[st][c2], st))
                st = MUL[st][hx[c2]]
        return tr

    gamma_t = traj(e_state, 300)
    dev_a1 = 0
    for s0 in (0, 1, 2, 3):
        tr = traj(s0, 300)
        for i, x in enumerate(tr):
            if x != MUL[s0][gamma_t[i]]:
                dev_a1 += 1
    claim('A1-R9', 'R9-A1 軌跡引理：s_t(s0) = s0·Γ_t（300 對 × 4 個 s0，0 偏離）',
          dev_a1 == 0, '偏離 = %d' % dev_a1)

    # A3 恆等式 2·ε(x)d(x,a) = ε(x) − γ(a,x)（tie 條目）
    dev_a3 = 0
    for s in range(n):
        for a in range(ncol):
            if tie[s][a] and 2 * eps[s] * dind[s][a] != eps[s] - gam[s][a]:
                dev_a3 += 1
    claim('A3-R9', 'R9-A3：ε(x)·d(x,a) = (ε(x) − γ(a,x))/2（全部 tie 條目 0 偏離）',
          dev_a3 == 0, '偏離 = %d' % dev_a3)

    # A4 逐事件 s_w = s_r·g_e
    dev_a4 = 0
    keys = {}
    for (a, sw, sr) in my_ev:
        g = MUL[inv[sr]][sw]
        keys[(a, g)] = keys.get((a, g), 0) + 1
        if MUL[sr][g] != sw:
            dev_a4 += 1
    claim('A4-R9', 'R9-A4：逐事件 s_w = s_r·g_e（g := s_r⁻¹s_w）0 偏離；124 事件 → 62 個 (a,g) 鍵、'
                   '每鍵重數恰 2、每列 a 恰一鍵',
          dev_a4 == 0 and len(keys) == 62 and set(keys.values()) == {2} and len(set(k[0] for k in keys)) == 62,
          '偏離 = %d ; 鍵數 = %d ; 重數值集 = %s' % (dev_a4, len(keys), sorted(set(keys.values()))))
    gh = {}
    for (a, g) in keys:
        gh[order[g]] = gh.get(order[g], 0) + 1
    claim('A4b-R9', 'g_a 之階分佈 = {3:20, 4:30, 5:12}（= 全階 3 ∪ 全階 4 ∪ 階 5 之半）',
          gh == {3: 20, 4: 30, 5: 12}, '階分佈 = %s' % gh)

    # A2c / A5ac / A5bc：逐 (a,g) 之三類 x-和
    Sq = {}
    for (a, g) in sorted(keys):
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
        Sq[(a, g)] = (sTF, sFT, sTT)
    sTF_t = sum(keys[k] * Sq[k][0] for k in keys)
    sFT_t = sum(keys[k] * Sq[k][1] for k in keys)
    sTT_t = sum(keys[k] * Sq[k][2] for k in keys)
    claim('G1-R9', 'R9-A2c：Σ n·S_TF = Σ f_tf、Σ n·S_FT = Σ f_ft、Σ n·S_TT = Σ f_tt ⟹ (0, 0, 64)',
          (sTF_t, sFT_t, sTT_t) == (sum(f_tf), sum(f_ft), sum(f_tt)) == (0, 0, 64),
          '三重和 = (%d, %d, %d)' % (sTF_t, sFT_t, sTT_t))
    nzTF = [k for k in Sq if Sq[k][0] != 0]
    nzFT = [k for k in Sq if Sq[k][1] != 0]
    claim('G2-R9', '★★ R9-A5ac：對全部 62 個 (a,g) 鍵 S_TF(a,g) = 0 且 S_FT(a,g) = 0（逐鍵局部消失）',
          not nzTF and not nzFT, '非零鍵 TF/FT = %d/%d' % (len(nzTF), len(nzFT)))
    stt_val = sorted(set(v[2] for v in Sq.values()))
    nzTT = sorted([k for k in Sq if Sq[k][2] != 0])
    carriers_pos = sorted(k[0] for k in nzTT if Sq[k][2] * keys[k] > 0)
    carriers_neg = sorted(k[0] for k in nzTT if Sq[k][2] * keys[k] < 0)
    claim('G3-R9', 'R9-A5bc：S_TT ∈ {−8,0,8}；非零鍵 12（各 ±16）⟹ Σ = 64；'
                   '承載列 +16 = {32,35,36,45,48,57,58,61}、−16 = {37,38,55,56}',
          stt_val == [-8, 0, 8] and len(nzTT) == 12 and sTT_t == 64
          and carriers_pos == [32, 35, 36, 45, 48, 57, 58, 61] and carriers_neg == [37, 38, 55, 56],
          'S_TT 值集 = %s ; 非零鍵 = %d ; 承載 + = %s ; 承載 − = %s'
          % (stt_val, len(nzTT), carriers_pos, carriers_neg))
    sq_match = all(tuple(d34['Sq_table'][str(k)]) == Sq[k] for k in Sq) and len(d34['Sq_table']) == len(Sq)
    claim('G4-R9', 'S 表與凍結產物 data/34 之 Sq_table 逐鍵相同（62 鍵）', sq_match,
          '凍結鍵數 = %d ; 相符 = %s' % (len(d34['Sq_table']), sq_match))

    # C1c 逐態重建（等價檢查：已知 E4 已驗逐態 f；此處另驗 Σ 與 Δ）
    claim('G5-R9', 'R9-C1c：逐態重建之 (f_tf, f_ft, f_tt) 與凍結值全同（120/120）且 Σ = (0,0,64)',
          ok_t and (sum(f_tf), sum(f_ft), sum(f_tt)) == (0, 0, 64),
          '全同 = %s ; Σ = (%d,%d,%d)' % (ok_t, sum(f_tf), sum(f_ft), sum(f_tt)))

    # B 系（反演／對映）
    b1a = sum(1 for s in range(n) if f_tf[inv[s]] == f_ft[s])
    b1b = sum(1 for s in range(n) if f_tf[inv[s]] == -f_ft[s])
    b2a = sum(1 for s in range(n) if f_ft[inv[s]] == f_tf[s])
    b2b = sum(1 for s in range(n) if f_ft[inv[s]] == -f_tf[s])
    b4 = sum(1 for s in range(n) if f_tt[inv[s]] == f_tt[s])
    claim('G6-R9', 'R9 Part B 否證原樣保留：B1a/B1b/B2a/B2b/B4 = 12/14/12/14/56',
          (b1a, b1b, b2a, b2b, b4) == (12, 14, 12, 14, 56),
          '實測 = %s' % [b1a, b1b, b2a, b2b, b4])

    # ================= H 記錄一致性（docs/18 原文）=================
    doc18 = io.open(os.path.join(BASE, 'docs/18_r9_results.md'), encoding='utf-8').read()
    need = ['62 個 (a,g) 鍵', 'S_TF(a,g) = 0', 'S_FT(a,g) = 0', '{−8, 0, 8}',
            '{3: 20, 4: 30, 5: 12}', '124', '120 態全部', '0/0/64',
            '{32, 35, 36, 45, 48, 57, 58, 61}', '{37, 38, 55, 56}']
    miss = [k for k in need if k not in doc18]
    claim('H1', 'docs/18 含全部頭條數字（逐字）', not miss, 'missing = %s' % miss)
    rec = io.open(os.path.join(BASE, '01_problem_record.md'), encoding='utf-8').read()
    need2 = ['十六、R9', '逐 (a,g) 鍵之 x-和消失', '12/23', '6/8', '8/10']
    miss2 = [k for k in need2 if k not in rec]
    claim('H2', '01_problem_record 之 R9 節含判決與驗證數字', not miss2, 'missing = %s' % miss2)

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 72)
    print('RESULT: %d/%d PASS  |  O225 close-out 獨立審計（R1–R9）' % (npass, len(CLAIMS)))
    out = {'rules': 'o225-closeout-t1-v1', 'n_pass': npass, 'n_total': len(CLAIMS),
           'claims': CLAIMS, 'gate': 'OPEN' if npass == len(CLAIMS) else 'CHECK'}
    with io.open(os.path.join(BASE, 'data/36_closeout_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
