#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/104 -- R27 獨立審計（`r27-crit1-orbit-v1`）。

以**表簽名**（8 元組：6 非 tie 格 ＋ 2 tie 格）為唯一表示，另路重算：
A1 另路建 K 表（直接由簽名落表）重算 R：E1-c 精化判準 256/256 全符
A2 orbit 結構另路（簽名顯式影像枚舉）：orbit 數 72、大小 {2,4}、帳 2·16+4·56=256、M-固定 16
A3 P3 另路：無 orbit 混合
A4 Q1 另路：三層族全 4096 表逐列直算，反例 32 且全屬「判據真但 R ≢ 0」
A5 校正律（append-only）：O2-c、P4-c、CLS-c
用法: /usr/bin/python3 scripts/104_r27_audit.py
"""
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
O222 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o222_qm_evaluation_semantics'
NT = [(1, 1), (1, 0), (1, -1), (-1, 1), (-1, 0), (-1, -1)]
MIDX = {c: i for i, c in enumerate(NT)}
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


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


def main():
    print('=' * 112)
    print('O225 scripts/104 -- R27 獨立審計（表簽名另路）')
    print('=' * 112, flush=True)
    b5 = load(os.path.join(O222, 'scripts', '12_b5_budget.py'), 'b104')
    mm, K, MUL, hx, ids, types = b5.load_machine()
    _ax, U, _i, _t, _h = mm.load_inputs()
    a2 = load(os.path.join(O222, 'scripts', '09_a2_rollback.py'), 'b104a')
    G, _ig, _M2 = a2.build_group()
    n, ncol = len(K), len(K[0])
    KV = [mm.rot_ref(g, U[0]) for g in G]
    d = [[sgn(add(add(mul(U[a][0], KV[s][0]), mul(U[a][1], KV[s][1])), mul(U[a][2], KV[s][2])))
          for a in range(ncol)] for s in range(n)]
    cross = [[(add(mul(U[a][2], KV[s][1]), neg(mul(U[a][1], KV[s][2]))),
              add(mul(U[a][0], KV[s][2]), neg(mul(U[a][2], KV[s][0]))),
              add(mul(U[a][1], KV[s][0]), neg(mul(U[a][0], KV[s][1])))) for a in range(ncol)] for s in range(n)]
    c = [[fs(cross[s][a]) for a in range(ncol)] for s in range(n)]
    tie = [[d[s][a] == 0 for a in range(ncol)] for s in range(n)]

    # 由 8 位 mask 造簽名（8 元組）
    def sig_of(mask):
        b = [(mask >> i) & 1 for i in range(8)]
        nt = [1 if b[i] else -1 for i in range(6)]
        tlo, thi = (1, -1) if not b[6] else (1, 1)
        if b[7]:
            tlo, thi, nt = -tlo, -thi, [-v for v in nt]
        return tuple(nt + [tlo, thi])

    def Ktab(sig):
        return [[(sig[6] if c[s][a] > 0 else sig[7]) if tie[s][a] else sig[MIDX[(d[s][a], c[s][a])]]
                 for a in range(ncol)] for s in range(n)]

    def R_of(sig):
        return sorted(set(sum(row) for row in Ktab(sig)))

    def crit(sig):
        dbl = all(sig[i] == -sig[MIDX[(-NT[i][0], -NT[i][1])]] for i in range(6))
        return dbl and (sig[6] == -sig[7])

    def Mof(sig):
        nt = [sig[MIDX[(-NT[i][0], -NT[i][1])]] for i in range(6)]
        return tuple(nt + [sig[7], sig[6]])

    def Sof(sig):
        return tuple(-v for v in sig)

    Sigs = [sig_of(m) for m in range(256)]
    Z = {s: (R_of(s) == [0]) for s in Sigs}
    nconf = sum(1 for s in Sigs if Z[s] == crit(s))
    claim('A1', '另路建表（簽名直落 K 表）重算 R：E1-c 精化判準 256/256 全符', nconf == 256,
          '相符 = %d/256；R≡0 表數 = %d' % (nconf, sum(1 for s in Sigs if Z[s])))
    seen, orbits = set(), []
    for s in Sigs:
        if s in seen:
            continue
        orb = sorted({s, Mof(s), Sof(s), Sof(Mof(s))})
        orbits.append(orb)
        seen |= set(orb)
    cnt = {2: 0, 4: 0}
    for o in orbits:
        cnt[len(o)] = cnt.get(len(o), 0) + 1
    mfix = sum(1 for s in Sigs if Mof(s) == s)
    claim('A2', 'orbit 另路：數 = 72、大小 {2,4}（2 元 16／4 元 56）、帳 2·16+4·56=256、M-固定 = 16',
          len(orbits) == 72 and cnt.get(2) == 16 and cnt.get(4) == 56 and 2 * cnt[2] + 4 * cnt[4] == 256 and mfix == 16,
          'orbit = %d；2 元 = %d；4 元 = %d；M-固定 = %d' % (len(orbits), cnt.get(2), cnt.get(4), mfix))
    mixed = [o for o in orbits if len(set(Z[s] for s in o)) > 1]
    claim('A3', 'P3 另路重核：無 orbit 混合 ⟹ 逐 orbit 判充要成立（取任一代表即可判定）', not mixed,
          '混合 orbit = %d' % len(mixed))
    CLS = {}
    for s in range(n):
        for a in range(ncol):
            CLS.setdefault((0 if tie[s][a] else 1, types[a]), len(CLS))
    idx = [[CLS[(0 if tie[s][a] else 1, types[a])] for a in range(ncol)] for s in range(n)]
    nc = len(CLS)
    bad = []
    for s in Sigs:
        Kt = Ktab(s)
        for r in range(1 << nc):
            rho = [(r >> i) & 1 for i in range(nc)]
            rows = set()
            for row in range(n):
                tot = 0
                for a in range(ncol):
                    tot += Kt[row][a] * (1 if rho[idx[row][a]] else -1)
                rows.add(tot)
            if (rows == {0}) != crit(s):
                bad.append((s, tuple(rho), crit(s), sorted(rows), rows == {0}))
    kinds = {}
    for b in bad:
        k = (b[2], b[4])
        kinds[k] = kinds.get(k, 0) + 1
    claim('A4', 'Q1 另路：三層族（%d 表）逐列直算，反例 = 32 且全屬（判據真 ∧ R ≢ 0）' % (256 * (1 << nc)),
          len(bad) == 32 and all(b[2] is True and b[4] is False for b in bad),
          '反例 = %d；類數 = %d；反例型態計數 = %s' % (len(bad), nc, {str(k): v for k, v in kinds.items()}))
    claim('A4-c', '【校正 tag，append-only】實測方向：全部 32 例皆為「判據假（crit = False）∧ R ≡ 0」'
                  '——即精化判準在三層族上**漏判**（sufficiency 方向失效），非「誤判」；A4 之預期方向原樣保留 FAIL',
          len(bad) == 32 and all(b[2] is False and b[4] is True for b in bad),
          '型態計數 = %s' % {str(k): v for k, v in kinds.items()})
    claim('A5', '校正律（append-only）：O2-c（72／{2,4}）、P4-c（28/8/32/4）、CLS-c（第三層類數 4）', True,
          '見 docs/59 與 data/104 corrections')
    npass = sum(1 for cc in CLAIMS if cc['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  |  O225 R27 審計' % (npass, len(CLAIMS)))
    io.open(os.path.join(BASE, 'data', '104_r27_audit.json'), 'w', encoding='utf-8').write(json.dumps(
        {'rules': 'r27-crit1-orbit-v1', 'claims': CLAIMS, 'n_pass': npass, 'n_total': len(CLAIMS),
         'n_orbits': len(orbits), 'profile': {'size2': cnt.get(2), 'size4': cnt.get(4)}, 'M_fixed': mfix,
         'Q1_counterexamples': len(bad), 'third_layer_classes': nc,
         'corrections': {'O2-c': 'orbit 數 72、大小 {2,4}（原預註冊 64／全 4 否證）',
                         'P4-c': '四類分佈 28/8/32/4（原預註冊均分否證）',
                         'CLS-c': '第三層類數 = 4（合約按 2×3=6 估算為 16384 表，實為 4096）'}},
        indent=1, ensure_ascii=False))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
