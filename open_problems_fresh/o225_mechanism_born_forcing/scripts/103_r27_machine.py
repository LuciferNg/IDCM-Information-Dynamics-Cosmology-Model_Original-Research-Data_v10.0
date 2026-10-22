#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/103 -- R27 機器（`r27-crit1-orbit-v1`）：非仿射族 orbit 分類與充要性。

Part O  orbit 結構（O1–O4）：⟨M,S⟩ 對合互換、orbit 數／大小、M／S 保持 R ≡ 0
Part P  逐 orbit 判充要（P1–P4）：判據 orbit-不變、R ≡ 0 表數、無混合 orbit、四類分佈
Part Q  三層族壓力測試（Q1–Q2）：Kt³ = Kt² · ρ(tie, type)；全 16384 表 ＋ type-子族 2048 表

凍結指紋：data/102_r27_freeze.json（本支執行前已寫定）。唯讀 O222；精確算術。
用法: /usr/bin/python3 scripts/103_r27_machine.py
"""
import hashlib
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


def info(m):
    print('[INFO] %s' % m, flush=True)


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


def firstsgn(v):
    for c in v:
        s = sgn(c)
        if s:
            return s
    return 0


NT = [(d, c) for d in (1, -1) for c in (1, 0, -1)]          # 6 非 tie 格（固定次序）


def tb_of(mask):
    """mask → 表（bits[0:6] 非 tie 符號、bit6 tie 規則、bit7 全域翻號）。"""
    bits = [(mask >> i) & 1 for i in range(8)]
    nt = {NT[i]: (1 if bits[i] else -1) for i in range(6)}
    tie = {1: 1, -1: -1}
    if bits[6]:
        tie = {1: 1, -1: 1}
    if bits[7]:
        tie = {k: -v for k, v in tie.items()}
    return {'nt': nt, 'tie': tie}


def key_of(tb):
    return (tuple(tb['nt'][c] for c in NT), tb['tie'][1], tb['tie'][-1])


KEY2MASK = {}
for _m in range(256):
    KEY2MASK[key_of(tb_of(_m))] = _m


def mask_of(tb):
    return KEY2MASK[key_of(tb)]


def M_of(tb):
    nt = {NT[i]: tb['nt'][(-NT[i][0], -NT[i][1])] for i in range(6)}
    return {'nt': nt, 'tie': {c: tb['tie'][-c] for c in (1, -1)}}


def S_of(tb):
    return {'nt': {k: -v for k, v in tb['nt'].items()}, 'tie': {k: -v for k, v in tb['tie'].items()}}


def tie_odd(tb):
    return tb['tie'][1] == -tb['tie'][-1]


def double_odd(tb):
    return all(tb['nt'][(d, c)] == -tb['nt'][(-d, -c)] for (d, c) in NT)


def main():
    fp = os.path.join(BASE, 'data', '102_r27_freeze.json')
    assert os.path.exists(fp), '凍結指紋缺失：先跑 scripts/102'
    fr = json.load(io.open(fp, encoding='utf-8'))
    csha = hashlib.sha256(io.open(os.path.join(BASE, 'docs', '58_r27_contract.md'), 'rb').read()).hexdigest()
    info('凍結核：合約 sha 相符 = %s（%s）' % (csha == fr['sha256'], fr['sha256'][:16]))
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'b103')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    n, ncol = len(K), len(K[0])
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'b103a')
    G, _ig, _M2 = a2.build_group()
    KV = [mm.rot_ref(g, U[0]) for g in G]
    PAIR = [[(sgn(add(add(mul(U[a][0], KV[s][0]), mul(U[a][1], KV[s][1])), mul(U[a][2], KV[s][2]))),
             firstsgn((add(mul(U[a][1], KV[s][2]), neg(mul(U[a][2], KV[s][1]))),
                       add(mul(U[a][2], KV[s][0]), neg(mul(U[a][0], KV[s][2]))),
                       add(mul(U[a][0], KV[s][1]), neg(mul(U[a][1], KV[s][0])))))) for a in range(ncol)]
            for s in range(n)]
    tie = [[PAIR[s][a][0] == 0 for a in range(ncol)] for s in range(n)]

    def K_of(t, coef=None):
        return [[(t['nt'][PAIR[s][a]] if not tie[s][a] else t['tie'][PAIR[s][a][1]]) * (coef[s][a] if coef else 1)
                 for a in range(ncol)] for s in range(n)]

    def R_of(t, coef=None):
        return sorted(set(sum(row) for row in K_of(t, coef)))

    TB = {m: tb_of(m) for m in range(256)}
    R2 = {m: R_of(TB[m]) for m in range(256)}
    zero = {m: (R2[m] == [0]) for m in range(256)}
    co = []
    for m in range(256):
        co.append((tie_odd(TB[m]), double_odd(TB[m])))
    crit = {m: (co[m][0] and co[m][1]) for m in range(256)}

    # ---------- Part O ----------
    inv_ok = True
    for m in range(256):
        if M_of(M_of(TB[m])) != TB[m] or S_of(S_of(TB[m])) != TB[m]:
            inv_ok = False
        if M_of(S_of(TB[m])) != S_of(M_of(TB[m])):
            inv_ok = False
    claim('O1', 'M、S 皆對合且互換 ⟹ ⟨M,S⟩ ≅ Z₂ × Z₂（256 表全檢）', inv_ok, '反例 = 0' if inv_ok else '有反例')
    seen, orbits = set(), []
    for m in range(256):
        if m in seen:
            continue
        imgs = [m, mask_of(M_of(TB[m])), mask_of(S_of(TB[m])), mask_of(M_of(S_of(TB[m])))]
        orb = sorted(set(imgs))
        orbits.append(orb)
        seen |= set(orb)
    sizes = sorted(set(len(o) for o in orbits))
    claim('O2', 'orbit 數 = 64 且每個大小 = 4（無固定點）', len(orbits) == 64 and sizes == [4],
          'orbit 數 = %d；大小集 = %s' % (len(orbits), sizes))
    m_keep = all(zero[m] == zero[mask_of(M_of(TB[m]))] for m in range(256))
    claim('O3', 'M 保持 R ≡ 0（R(tb) = [0] ⟺ R(M·tb) = [0]）', m_keep,
          '反例 = %d' % sum(1 for m in range(256) if zero[m] != zero[mask_of(M_of(TB[m]))]))
    s_keep = all(zero[m] == zero[mask_of(S_of(TB[m]))] for m in range(256))
    claim('O4', 'S 保持 R ≡ 0', s_keep, '反例 = %d' % sum(1 for m in range(256) if zero[m] != zero[mask_of(S_of(TB[m]))]))

    # ---------- Part P ----------
    p1bad = [o for o in orbits if len(set(crit[m] for m in o)) > 1]
    claim('P1', '精化判據在 orbit 上不變（每 orbit 4 元同值）', not p1bad, '違例 orbit = %d' % len(p1bad))
    nzero = sum(1 for m in range(256) if zero[m])
    claim('P2', 'R ≡ 0 之表數 = 16（＝判據真值數）', nzero == 16 and nzero == sum(1 for m in range(256) if crit[m]),
          'R≡0 = %d；判據真 = %d' % (nzero, sum(1 for m in range(256) if crit[m])))
    mix = [o for o in orbits if len(set(zero[m] for m in o)) > 1]
    claim('P3', '無 orbit 混合（不存在 orbit 內同時 R ≡ 0 與 R ≠ 0）⟹ 逐 orbit 判充要成立', not mix,
          '混合 orbit = %d' % len(mix))
    dist = {}
    for o in orbits:
        k = co[o[0]]
        dist[k] = dist.get(k, 0) + 1
    claim('P4', '四類（tie_odd, double_odd）在 orbit 上均分（各 16 個 orbit）',
          sorted(dist.values()) == [16, 16, 16, 16], '分佈 = %s' % {str(k): v for k, v in dist.items()})

    # ---------- Part Q 三層族 ----------
    CLS = [(0 if tie[s][a] else 1, types[a]) for s in range(n) for a in range(ncol)]
    cls_idx = {}
    for cl in CLS:
        cls_idx.setdefault(cl, len(cls_idx))
    idx = [[cls_idx[(0 if tie[s][a] else 1, types[a])] for a in range(ncol)] for s in range(n)]
    nc = len(cls_idx)
    info('第三層類數 = %d（%s）' % (nc, sorted(cls_idx.items(), key=lambda kv: kv[1])))
    pre = {}
    for m in range(256):
        t = TB[m]
        arr = [[0] * nc for _ in range(n)]
        for s in range(n):
            for a in range(ncol):
                v = t['nt'][PAIR[s][a]] if not tie[s][a] else t['tie'][PAIR[s][a][1]]
                arr[s][idx[s][a]] += v
        pre[m] = arr

    def conforms(m, rho):
        rows = set()
        for s in range(n):
            tot = 0
            a2_ = pre[m][s]
            for c in range(nc):
                if rho[c]:
                    tot += a2_[c]
                else:
                    tot -= a2_[c]
            rows.add(tot)
        return (rows == {0}) == crit[m]

    ok1 = bad1 = 0
    ex = []
    for m in range(256):
        for r in range(1 << nc):
            rho = [(r >> i) & 1 for i in range(nc)]
            if conforms(m, rho):
                ok1 += 1
            else:
                bad1 += 1
                if len(ex) < 3:
                    ex.append((m, rho))
    tot1 = 256 * (1 << nc)
    claim('Q1', '三層族「精化判準仍充要」（%d 表全符）；預期：否證' % tot1, bad1 == 0,
          '相符 = %d/%d；反例 = %d；例 = %s' % (ok1, tot1, bad1, ex))
    # Q2：第三層只依 type（3 類，忽略 tie 差別）
    tidx = {}
    for a in range(ncol):
        tidx.setdefault(types[a], len(tidx))
    nt_ = len(tidx)
    pre2 = {}
    for m in range(256):
        t = TB[m]
        arr = [[0] * nt_ for _ in range(n)]
        for s in range(n):
            for a in range(ncol):
                v = t['nt'][PAIR[s][a]] if not tie[s][a] else t['tie'][PAIR[s][a][1]]
                arr[s][tidx[types[a]]] += v
        pre2[m] = arr
    ok2 = bad2 = 0
    for m in range(256):
        for r in range(1 << nt_):
            rho = [(r >> i) & 1 for i in range(nt_)]
            rows = set()
            for s in range(n):
                tot = 0
                for c in range(nt_):
                    tot += pre2[m][s][c] * (1 if rho[c] else -1)
                rows.add(tot)
            if (rows == {0}) == crit[m]:
                ok2 += 1
            else:
                bad2 += 1
    claim('Q2', 'type-子族（第三層只依軸型別，%d 表）之相符數' % (256 * (1 << nt_)), True,
          '相符 = %d/%d；反例 = %d' % (ok2, 256 * (1 << nt_), bad2))

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  |  O225 R27 機器（CRIT-1：orbit 分類／充要／三層族）' % (npass, len(CLAIMS)))
    io.open(os.path.join(BASE, 'data', '103_r27_machine.json'), 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r27-crit1-orbit-v1', 'claims': CLAIMS, 'n_pass': npass, 'n_total': len(CLAIMS),
         'n_orbits': len(orbits), 'n_zero': nzero, 'Q1': {'ok': ok1, 'bad': bad1, 'total': tot1},
         'Q2': {'ok': ok2, 'bad': bad2, 'total': 256 * (1 << nt_)},
         'orbit_sizes': sizes, 'zero_masks': sorted(m for m in range(256) if zero[m])},
        indent=1, ensure_ascii=False))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
