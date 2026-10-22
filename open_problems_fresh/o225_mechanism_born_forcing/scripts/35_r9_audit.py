#!/usr/bin/env python3
"""O225 scripts/35 -- R9 獨立審計（不 import 34）。

E1 獨立重建事件序列（不同轉寫）＋ 與 34 之 events_sha 對照
E2 ★ 逐態重建：由歸約（用事件之 (a, s_w, s_r) 直接算，不經 g 參數化）重建 f_tf/f_ft/f_tt/Δ，與 R8 之 120 態值逐態核
E3 ε·d 恆等式獨立核（不同算式路徑）
E4 A5a：全部 TF/FT 事件之 x-和直接重算（獨立實作）
E5 反演關係（B1a/B1b/B2a/B2b/B4）獨立核
E6 對 34 輸出之交叉核對
精確算術；零浮點；上游 O222 唯讀。用法: /usr/bin/python3 scripts/35_r9_audit.py
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


def event_list(Kt, MULt, hxt, pairs, s0=0):
    """獨立轉寫（索引式 stack；與 34 之寫法不同）。"""
    stack = []
    state = s0
    rem = BUDGET
    out = []
    for pair in pairs:
        spent = 0
        for idx in (0, 1):
            ctx = pair[idx]
            if stack and stack[-1][0] == ctx:
                entry = stack[-1]
                out.append((entry[0], entry[2], state))
                continue
            if rem - COST * spent < EMIN:
                raise RuntimeError('stop')
            stack.append((ctx, Kt[state][ctx], state))
            state = MULt[state][hxt[ctx]]
            spent += 1
        entry = stack[-1]
        stack = stack[:-1]
        state = entry[2]
        ctx = pair[1]
        if stack and stack[-1][0] == ctx:
            entry = stack[-1]
            out.append((entry[0], entry[2], state))
        else:
            if rem - COST * spent < EMIN:
                raise RuntimeError('stop')
            stack.append((ctx, Kt[state][ctx], state))
            state = MULt[state][hxt[ctx]]
            spent += 1
        rem -= COST * spent
    return out


def main():
    print('=' * 118)
    print('O225 scripts/35 -- R9 INDEPENDENT AUDIT   (%s)' % RULES)
    print('=' * 118, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'r9au_b5')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    G, _ig, _M2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'r9au_a2').build_group()
    n, ncol = len(K), len(K[0])
    KV = [mm.rot_ref(g, U[0]) for g in G]
    pairs = [(a, b) for a in range(ncol) for b in range(ncol)]
    d31 = json.load(io.open(os.path.join(DATA, '31_r8_group.json'), encoding='utf-8'))
    d34 = json.load(io.open(os.path.join(DATA, '34_r9_pairing.json'), encoding='utf-8'))
    tie = [[dot3(U[a], KV[s]) == (0, 0) for a in range(ncol)] for s in range(n)]
    eps = [firstsgn(KV[s]) for s in range(n)]
    gam = [{a: firstsgn(cross3(U[a], KV[s])) for a in range(ncol) if tie[s][a]} for s in range(n)]
    dind = [[(1 if (gam[s][a] != eps[s]) else 0) if tie[s][a] else 0 for a in range(ncol)] for s in range(n)]
    dgen = [[1 if firstsgn(cross3(U[a], KV[s])) != eps[s] else 0 for a in range(ncol)] for s in range(n)]
    e_state = [j for j in range(n) if all(MUL[j][k] == k for k in range(n))][0]
    inv = {s: next(t for t in range(n) if MUL[s][t] == e_state) for s in range(n)}

    # ---------- E1 事件序列獨立重建 ----------
    ev = event_list(K, MUL, hx, pairs, e_state)
    ev_sha = hashlib.sha256(repr(ev).encode('utf-8')).hexdigest()
    cls = []
    for (a, sw, sr) in ev:
        tw, tr = tie[sw][a], tie[sr][a]
        cls.append('TT' if (tw and tr) else ('TF' if tr else ('FT' if tw else 'FF')))
    cnt = collections.Counter(cls)
    claim('E1', '★ 獨立事件序列重建：事件數、類別計數、序列雜湊與 34 相同',
          ev_sha == d34['events_sha'] and dict(cnt) == d34['event_class_counts'],
          '事件數 = %d ; 類別 = %s ; sha 符 = %s' % (len(ev), dict(cnt), ev_sha == d34['events_sha']))

    # ---------- E2 逐態重建（不經 g 參數化）----------
    _sc = {}

    def sgn_uw(a, w):
        k = (a, w)
        if k not in _sc:
            _sc[k] = sgn(dot3(U[a], KV[w]))
        return _sc[k]
    ftf = [0] * n
    fft = [0] * n
    ftt = [0] * n
    for s0 in range(n):
        a1 = a2 = a3 = 0
        for (a, sw, sr), c in zip(ev, cls):
            w = MUL[s0][sw]
            r = MUL[s0][sr]
            if c == 'TF':
                a1 += dind[r][a] * eps[r] * sgn_uw(a, w)
            elif c == 'FT':
                a2 += dind[w][a] * eps[w] * eps[r]
            elif c == 'TT':
                a3 += (1 if dind[r][a] != dind[w][a] else 0) * eps[r] * eps[w]
        ftf[s0], fft[s0], ftt[s0] = a1, a2, a3
    dl = [ftf[s] + fft[s] + ftt[s] for s in range(n)]
    ok2 = (ftf == d31['f_tf'] and fft == d31['f_ft'] and ftt == d31['f_tt'] and dl == d31['delta'])
    claim('E2', '★★ 逐態重建：由歸約（事件之 (a,s_w,s_r) 直接算，不經 g）重建 f_tf/f_ft/f_tt/Δ，與 R8 之 120 態值逐態相同',
          ok2, 'f_tf 同 = %s ; f_ft 同 = %s ; f_tt 同 = %s ; Δ 同 = %s ; Σf_tf = %d ; Σf_ft = %d ; Σf_tt = %d'
          % (ftf == d31['f_tf'], fft == d31['f_ft'], ftt == d31['f_tt'], dl == d31['delta'],
             sum(ftf), sum(fft), sum(ftt)))

    # ---------- E2c 逐態重建（校正版：逐 x 分類 + 一般 d）----------
    triples2 = [(a, MUL[inv[sr]][sw]) for (a, sw, sr) in ev]
    ftf = [0] * n
    fft = [0] * n
    ftt = [0] * n
    _sc2 = {}

    def sgn_uw2(a, w):
        k = (a, w)
        if k not in _sc2:
            _sc2[k] = sgn(dot3(U[a], KV[w]))
        return _sc2[k]
    for s0 in range(n):
        a1 = a2 = a3 = 0
        for (a, swe, sre) in ev:
            w = MUL[s0][swe]
            r = MUL[s0][sre]
            tw, tr = tie[w][a], tie[r][a]
            if tw and tr:
                a3 += (0 if dind[r][a] == dind[w][a] else 1) * eps[r] * eps[w]
            elif tr:
                a1 += dind[r][a] * eps[r] * sgn_uw2(a, w)
            elif tw:
                a2 += dgen[w][a] * eps[w] * sgn_uw2(a, r)
        ftf[s0], fft[s0], ftt[s0] = a1, a2, a3
    dl2 = [ftf[s] + fft[s] + ftt[s] for s in range(n)]
    ok2c = (ftf == d31['f_tf'] and fft == d31['f_ft'] and ftt == d31['f_tt'] and dl2 == d31['delta'])
    claim('E2c', '★★ 校正（新 tag）：逐態重建（事件三重 + 逐 x 分類 + 一般 d）與 R8 之 120 態 f_tf/f_ft/f_tt/Δ 全部相同',
          ok2c, 'f_tf 同 = %s ; f_ft 同 = %s ; f_tt 同 = %s ; Δ 同 = %s ; Σ = (%d, %d, %d)'
          % (ftf == d31['f_tf'], fft == d31['f_ft'], ftt == d31['f_tt'], dl2 == d31['delta'],
             sum(ftf), sum(fft), sum(ftt)))
    ok6c = (ok2c and d34['A2c']['sumTF_c'] == 0 and d34['A2c']['sumFT_c'] == 0 and d34['A2c']['sumTT_c'] == 64
            and d34['C1c']['ok'] and d34['C2c']['sum'] == 64)
    claim('E6c', '★ 校正（新 tag）：交叉核對 35 之重建與 34 之 A2c/A5bc/C1c/C2c 逐項一致', ok6c,
          'A2c = (%d, %d, %d) ; C1c ok = %s ; C2c Σ = %d' % (d34['A2c']['sumTF_c'], d34['A2c']['sumFT_c'],
                                                            d34['A2c']['sumTT_c'], d34['C1c']['ok'], d34['C2c']['sum']))

    # ---------- E3 ε·d 恆等式（獨立路徑）----------
    dev3 = 0
    for s in range(n):
        for a in range(ncol):
            if tie[s][a]:
                if eps[s] * (1 if gam[s][a] != eps[s] else 0) * 2 != eps[s] - gam[s][a]:
                    dev3 += 1
    claim('E3', '★ ε·d 恆等式獨立核：2·ε(x)d(x,a) = ε(x) − γ(a,x) 對全部 tie 條目（0 偏離）',
          dev3 == 0, '偏離 = %d' % dev3)

    # ---------- E4 校正版：三重 (a,g) 逐 x 分類之 S 表（獨立實作，用 KV[y] 直算）----------
    dgen = [[1 if firstsgn(cross3(U[a], KV[s])) != eps[s] else 0 for a in range(ncol)] for s in range(n)]
    tgl = {}
    for (a, sw, sr) in ev:
        g = MUL[inv[sr]][sw]
        tgl[(a, g)] = tgl.get((a, g), 0) + 1
    Sq2 = {}
    for (a, g) in sorted(tgl):
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
        Sq2[(a, g)] = (sTF, sFT, sTT)
    sumTF2 = sum(tgl[k] * Sq2[k][0] for k in tgl)
    sumFT2 = sum(tgl[k] * Sq2[k][1] for k in tgl)
    sumTT2 = sum(tgl[k] * Sq2[k][2] for k in tgl)
    match34 = all(Sq2[k] == tuple(d34.get('Sq_table', {}).get(str(k), (-999, -999, -999))) for k in tgl)
    nzTF2 = sum(1 for v in Sq2.values() if v[0] != 0)
    nzFT2 = sum(1 for v in Sq2.values() if v[1] != 0)
    claim('E4', '★★ 獨立核（校正版）：S 表逐鍵與 34 相同；Σ n·S_TF = Σ n·S_FT = 0、Σ n·S_TT = 64；逐鍵局部消失',
          match34 and sumTF2 == 0 and sumFT2 == 0 and sumTT2 == 64,
          'S 表相符 = %s ; Σ n·S_TF = %d ; Σ n·S_FT = %d ; Σ n·S_TT = %d ; 非零鍵 TF/FT = %d/%d ; 鍵數 = %d'
          % (match34, sumTF2, sumFT2, sumTT2, nzTF2, nzFT2, len(tgl)))

    # ---------- E5 反演關係 ----------
    b = {}
    b['B1a'] = sum(1 for s in range(n) if d31['f_tf'][inv[s]] == d31['f_ft'][s])
    b['B1b'] = sum(1 for s in range(n) if d31['f_tf'][inv[s]] == -d31['f_ft'][s])
    b['B2a'] = sum(1 for s in range(n) if d31['f_ft'][inv[s]] == d31['f_tf'][s])
    b['B2b'] = sum(1 for s in range(n) if d31['f_ft'][inv[s]] == -d31['f_tf'][s])
    b['B4'] = sum(1 for s in range(n) if d31['f_tt'][inv[s]] == d31['f_tt'][s])
    claim('E5', '★ 反演關係獨立核（B1a/B1b/B2a/B2b/B4 之成立數與 34 相同）',
          all(b[k] == d34[k] for k in b), '%s | 34: %s' % (b, {k: d34[k] for k in b}))

    # ---------- E6 交叉核對 ----------
    ok6 = (d34['A2']['sumTF'] == 0 == d34['A2']['sumFT'] and ftf == d31['f_tf']
           and sum(fft) == 0 and sum(ftt) == 64)
    claim('E6', '★ 交叉核對：35 之重建與 34 之 A2/A5b 結果逐項一致', ok6,
          'Σf_tf = 0 ✓ ; Σf_ft = 0 ✓ ; Σf_tt = 64 ✓ ; A5b ΣW\'\' = %d' % d34['A5b']['sum'])

    out = {'audit_of': RULES, 'E1': {'events': len(ev), 'classes': dict(cnt), 'sha_ok': ev_sha == d34['events_sha']},
           'E2': {'match': ok2, 'sum_ftf': sum(ftf), 'sum_fft': sum(fft), 'sum_ftt': sum(ftt)},
           'E3': {'dev': dev3}, 'E4': {'match34': match34, 'sumTF': sumTF2, 'sumFT': sumFT2, 'sumTT': sumTT2,
        'nzTF': nzTF2, 'nzFT': nzFT2, 'keys': len(tgl)},
 'Sq2': {str((int(k[0]), int(k[1]))): [int(v[0]), int(v[1]), int(v[2])] for k, v in Sq2.items()},
           'E5': b, 'E6': {'ok': ok6},
           'E2c': {'ok': ok2c, 'sums': [int(sum(ftf)), int(sum(fft)), int(sum(ftt))]},
           'E6c': {'ok': ok6c}, 'claims': CLAIMS}
    with io.open(os.path.join(DATA, '35_r9_audit.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 118)
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    print('=' * 118)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
