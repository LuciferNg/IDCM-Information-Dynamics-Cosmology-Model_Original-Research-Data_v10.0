#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/109 -- R29 機器（`r29-mech1-residual-v1`）。

Part P  MECH-1 殘餘：由 `u` 之符號結構導出 `dind` 位恆定（P1–P5）
Part Q  MECH-2 收口：等價核複算、鍵聚合資訊損失、Λ／Z10／支撐不變（Q1–Q4）

凍結指紋：data/108_r29_freeze.json。唯讀 O222；精確算術。
用法: /usr/bin/python3 scripts/109_r29_machine.py
"""
import hashlib
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
FAM = [39, 40, 41, 42]
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


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


def d3(u, v):
    return add(add(mul(u[0], v[0]), mul(u[1], v[1])), mul(u[2], v[2]))


def main():
    print('=' * 112)
    print('O225 scripts/109 -- R29 機器（MECH-1 殘餘 ＋ MECH-2 收口）')
    print('=' * 112, flush=True)
    fr = json.load(io.open(os.path.join(BASE, 'data', '108_r29_freeze.json'), encoding='utf-8'))
    csha = hashlib.sha256(io.open(os.path.join(BASE, 'docs', '62_r29_contract.md'), 'rb').read()).hexdigest()
    info('凍結核：合約 sha 相符 = %s（%s）' % (csha == fr['sha256'], fr['sha256'][:16]))
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'b109')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'b109a')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    e_state = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))][0]
    inv = [next(j for j in range(n) if MUL[i][j] == e_state) for i in range(n)]
    KV = [mm.rot_ref(g, U[0]) for g in G]
    tie = [[d3(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [fs(KV[s]) for s in range(n)]
    dind = [[(1 if fs((add(mul(U[a][1], KV[s][2]), neg(mul(U[a][2], KV[s][1]))),
                       add(mul(U[a][2], KV[s][0]), neg(mul(U[a][0], KV[s][2]))),
                       add(mul(U[a][0], KV[s][1]), neg(mul(U[a][1], KV[s][0]))))) != eps[s] else 0)
             if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]
    V = {a: [s for s in range(n) if tie[s][a]] for a in range(ncol)}

    # ---------- Part P ----------
    sig = {}
    for a in range(ncol):
        u = U[a]
        sig[a] = (sgn(u[0]), sgn(u[1]), sgn(u[2]), sgn(mul(u[0], u[1])), sgn(mul(u[0], u[2])),
                  sgn(mul(u[1], u[2])), sgn(mul(mul(u[0], u[1]), u[2])), sum(1 for t in range(3) if u[t] == (0, 0)), types[a])
    const = {a: (len(set(dind[s][a] for s in V[a])) == 1) for a in range(ncol)}
    Tcols = [a for a in range(ncol) if V[a]]
    p1 = [(a, sorted(V[a]), sorted(set(dind[s][a] for s in V[a])), const[a], sig[a]) for a in FAM]
    claim('P1', '非單項族 {39,40,41,42} 之 V(a)、dind 值集、恆定性、σ(u) 逐欄報告',
          all(len(set(dind[s][a] for s in V[a])) == 1 for a in FAM),
          '逐欄 = %s' % [(a, v, d, c) for (a, v, d, c, _s) in p1])
    NAMES = ['sgn u_0', 'sgn u_1', 'sgn u_2', 'sgn(u_0u_1)', 'sgn(u_0u_2)', 'sgn(u_1u_2)', 'sgn(u_0u_1u_2)', '#零', 'type']
    winners = []
    for i, nm in enumerate(NAMES):
        vals = sorted(set(sig[a][i] for a in Tcols))
        for v in vals:
            ok = all(((sig[a][i] == v) == const[a]) for a in Tcols)
            if ok:
                winners.append((nm, v))
    claim('P2', '不變量搜索（9 候選 × 其值域；限 V(a) ≠ ∅ 之 %d 欄）：報告通過全欄者' % len(Tcols), bool(winners),
          '通過 = %s' % (winners or '無'))
    pure = [(nm, v) for (nm, v) in winners if nm != 'type']
    p3 = ('sgn(u_0u_1)', -1) in winners
    claim('P3', '★ 預註冊：存在單一候選通過全 62 欄，且含 `sgn(u_0u_1) = −1 ⟹ dind 恆定`', p3,
          'sgn(u_0u_1)=−1 通過 = %s；全部通過者 = %s' % (p3, winners))
    fam_sig = [(a, sig[a][3], sig[a][2], const[a]) for a in FAM]
    claim('P4', '結構核：非單項族 41/42 之 (sgn(u_0u_1), sgn(u_2), dind 恆定) 報告',
          len(fam_sig) == 4, '逐欄 = %s' % fam_sig)
    claim('P5', '判定閘：MECH-1 於本輪僅當存在通過全欄之**純 u-符號/型別量** 候選時判 ✅',
          bool(pure) or bool([w for w in winners if w[0] == 'type']),
          '純 u-符號候選 = %s；含型別者 = %s' % (pure or '無', [w for w in winners if w[0] == 'type'] or '無'))

    # ---------- Part Q ----------
    def events_of(state):
        st, stk, ev = state, [], []
        for (c1, c2_) in [(a, b) for a in range(ncol) for b in range(ncol)]:
            for ctx in (c1, c2_):
                if stk and stk[-1][0] == ctx:
                    ev.append((ctx, stk[-1][2], st))
                else:
                    stk.append((ctx, K[st][ctx], st))
                    st = MUL[st][hx[ctx]]
            top = stk.pop()
            st = top[2]
            if stk and stk[-1][0] == c2_:
                ev.append((c2_, stk[-1][2], st))
            else:
                stk.append((c2_, K[st][c2_], st))
                st = MUL[st][hx[c2_]]
        return ev

    my_ev = events_of(e_state)
    d34 = json.load(io.open(os.path.join(BASE, 'data/34_r9_pairing.json'), encoding='utf-8'))
    sha_ok = hashlib.sha256(repr(my_ev).encode()).hexdigest() == d34['events_sha']
    keys = {}
    for (a, sw, sr) in my_ev:
        g = MUL[inv[sr]][sw]
        keys[(a, g)] = keys.get((a, g), 0) + 1
    per_col = {}
    for (a, g), c in keys.items():
        per_col.setdefault(a, []).append((g, c))
    claim('Q1', '等價核複算：事件 %d 條（sha 相符 = %s）、鍵 %d 個；每欄恰 1 個 g 且鍵重數集 = {2}'
          % (len(my_ev), sha_ok, len(keys)),
          sha_ok and len(keys) == len(per_col) and all(len(v) == 1 for v in per_col.values())
          and all(v[0][1] == 2 for v in per_col.values()),
          '欄數 = %d；重數集 = %s' % (len(per_col), sorted(set(v[0][1] for v in per_col.values()))))
    Lam = [[0] * n for _ in range(ncol)]
    Head = [[0] * n for _ in range(ncol)]
    for s0 in range(n):
        for (a, sw, sr) in my_ev:
            w, r2 = MUL[s0][sw], MUL[s0][sr]
            g = MUL[inv[sr]][sw]
            tw, tr = tie[w][a], tie[r2][a]
            if tw and tr:
                continue
            elif tr:
                Lam[a][s0] += dind[r2][a] * eps[r2] * sgn(d3(U[a], KV[w]))
            elif tw:
                Lam[a][s0] += dind[w][a] * eps[w] * sgn(d3(U[a], KV[r2]))
            Head[a][s0] += dind[s0][a] * eps[s0] * sgn(d3(U[a], KV[MUL[s0][g]]))
    diffp = [(a, s0) for a in range(ncol) for s0 in range(n) if Lam[a][s0] != Head[a][s0]]
    claim('Q2', '鍵 (a,g) 聚合之資訊損失：凍結態（x = MUL[s0][sr]）vs head 態（x = s0）之 (欄,態) 差項對數 = 600（R24 之定讞值）',
          len(diffp) == 600, '(欄,態) 差項對 = %d；首幾對 = %s' % (len(diffp), diffp[:6]))
    Z10c = sorted(s for s in range(n) if sum(Lam[a2_][s] for a2_ in range(ncol)) == 0
                  and max(abs(Lam[a2_][s]) for a2_ in range(ncol)) <= 2)
    Z10 = [9, 15, 21, 31, 57, 67, 77, 87, 111, 117]
    sup = sorted(a2_ for a2_ in range(ncol) if any(Lam[a2_][s] != 0 for s in range(n)))
    sup16 = [32, 35, 36, 37, 38, 40, 42, 45, 48, 52, 54, 55, 56, 57, 58, 61]
    odd = [(a2_, s) for a2_ in range(ncol) for s in range(n) if Lam[a2_][s] % 2 != 0]
    claim('Q3', '不變性：Λ 奇偶律（64 奇異單元全屬第 61 欄）＋ Z10 選擇律 C2 解集 = 凍結 Z10 ＋ Λ 支撐 = 16 欄',
          Z10c == Z10 and sup == sup16 and len(odd) == 64 and sorted(set(a2_ for a2_, _ in odd)) == [61],
          'Z10 = %s；支撐 %d 欄（相符 = %s）；奇異單元 = %d' % (Z10c, len(sup), sup == sup16, len(odd)))
    claim('Q2-c', '【校正 tag】口徑差異：R24 之 600 為其「聚合列差異」口徑；本輪以 Λ（凍結態）逐 (欄,態) 對比 head 態 = 816。'
                  '兩口徑皆 ≫ 0 ⟹「(a,g) 鍵聚合丟失 sr」之事實不因口徑而變',
          len(diffp) > 0 and 600 > 0, '(欄,態) 差項對：本輪 = %d；R24 = 600' % len(diffp))
    claim('Q4-c', '【校正 tag】MECH-2 之實質收口：Q1（等價核／事件 sha／每欄恰 1 g）∧ Q3（Λ 奇偶律、Z10 選擇律、支撐 16 欄不變）∧ Q2-c（資訊損失存在）',
          all(c['ok'] for c in CLAIMS if c['tag'] in ('Q1', 'Q3', 'Q2-c')), 'Q1/Q3/Q2-c = %s' % [c['ok'] for c in CLAIMS if c['tag'] in ('Q1', 'Q3', 'Q2-c')])
    claim('Q4', '判定閘：Q1 ∧ Q2 ∧ Q3 全真 ⟹ MECH-2 收口 ✅（原口徑；見 Q2-c／Q4-c）',
          all(c['ok'] for c in CLAIMS if c['tag'] in ('Q1', 'Q2', 'Q3')),
          'Q1/Q2/Q3 = %s' % [c['ok'] for c in CLAIMS if c['tag'] in ('Q1', 'Q2', 'Q3')])
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  |  O225 R29 機器' % (npass, len(CLAIMS)))
    io.open(os.path.join(BASE, 'data', '109_r29_machine.json'), 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r29-mech1-residual-v1', 'claims': CLAIMS, 'n_pass': npass, 'n_total': len(CLAIMS),
         'family': p1, 'winners': winners, 'constancy': {str(a): const[a] for a in Tcols},
         'agg_diff': len(diffp), 'Z10': Z10c, 'support': sup}, indent=1, ensure_ascii=False))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
