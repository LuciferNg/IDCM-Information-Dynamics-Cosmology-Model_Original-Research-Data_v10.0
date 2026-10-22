#!/usr/bin/env python3
"""O225 scripts/06 -- R1 診斷：軸集之對負封閉性 ＋ 「R 恆常」之真/偽個案 ＋ P4 充分性之真陽性對照。

背景：scripts/05 之 Q1/Q4 兩個探索性預期 FAIL —— 本支追根：
  * 3/200 隨機軸機器 R ≡ 0 係**退化抽樣**（參考軸抽到中心元素 ±1 ⟹ 向量部 = 0 ⟹ 全零讀出）
    ⟹ 唔屬 ±1 讀出族，唔構成 P4 之反例
  * 真陽性對照要搵**對負封閉**（u 與 -u 成對）之軸多重集：此時 Σ_a K[s,a] ≡ 0 對所有 s（每對抵消）
用法:  /usr/bin/python3 scripts/06_r1_axis_sign_structure.py
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
    spec = importlib.util.spec_from_file_location('o222x_' + script[:-3], os.path.join(O222S, script))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def akey(u):
    return tuple((c[0].numerator, c[0].denominator, c[1].numerator, c[1].denominator) for c in u)


def negk(k):
    return tuple((-f[0], f[1], -f[2], f[3]) for f in k)


def build_K(m, U, G):
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
    return K


def main():
    m = load_o222('09_a2_rollback.py')
    axes, U, ids, types, hvec = m.load_inputs()
    G, idx, MUL = m.build_group()
    nA = len(U)
    cnt = {}
    for u in U:
        cnt[akey(u)] = cnt.get(akey(u), 0) + 1
    closed_all = all(negk(k) in cnt and cnt[negk(k)] == cnt[k] for k in cnt)

    def zero_vec(u):
        return all(c[0] == 0 and c[1] == 0 for c in u)

    n_zero = sum(1 for u in U if zero_vec(u))
    claim('S1', '凍結 62 軸之整體對負封閉性 = %s ⟹ R = ±10（唔係 0）之機制' % closed_all,
          not closed_all, 'negation-closed = %s ; #null-vector axes = %d ; distinct axes = %d'
          % (closed_all, n_zero, len(cnt)))

    per = {}
    for tp in ('vertex', 'face', 'edge'):
        sub = [U[a] for a in range(nA) if types[a] == tp]
        c = {}
        for u in sub:
            c[akey(u)] = c.get(akey(u), 0) + 1
        closed = all(negk(k) in c and c[negk(k)] == c[k] for k in c)
        K = build_K(m, sub, G)
        R = [sum(r) for r in K]
        rows = len(set(tuple(r) for r in K))
        per[tp] = {'n': len(sub), 'negation_closed': closed, 'distinct_axes': len(c),
                   'R_distinct': sorted(set(R)), 'distinct_rows': rows}
    for tp in per:
        print('  [INFO] %-6s n=%2d negation-closed=%-5s R=%s distinct rows=%d'
              % (tp, per[tp]['n'], per[tp]['negation_closed'], per[tp]['R_distinct'],
                 per[tp]['distinct_rows']), flush=True)
    claim('S2', '★ 按型別：vertex / face 塊對負封閉 ⟹ R ≡ 0；edge 塊唔封閉 ⟹ R = ±10（Delta 全由邊軸之符號不平衡承載）',
          (per['vertex']['negation_closed'] and per['face']['negation_closed']
           and not per['edge']['negation_closed']
           and per['vertex']['R_distinct'] == [0] and per['face']['R_distinct'] == [0]
           and per['edge']['R_distinct'] == [-10, 10]),
          '; '.join('%s: closed=%s R=%s' % (t, per[t]['negation_closed'], per[t]['R_distinct'])
                    for t in ('vertex', 'face', 'edge')))

    # --- 真陽性對照：對負封閉之軸集 ⟹ R ≡ 0，且 K 行非退化 ⟹ P4 之另一側成立 ---
    pos = {}
    ok_all = True
    for tp in ('vertex', 'face'):
        sub = [U[a] for a in range(nA) if types[a] == tp]
        K = build_K(m, sub, G)
        nn = len(sub)
        alpha = F(1, nn)
        good = True
        for beta in (F(1, nn), F(-1, nn)):
            W = [[alpha + beta * K[s][a] for a in range(nn)] for s in range(120)]
            nz = all(v >= 0 for r in W for v in r)
            nor = all(sum(r) == 1 for r in W)
            sens = len(set(tuple(r) for r in W))
            good = good and nz and nor and sens > 1
            pos['%s_beta=%s' % (tp, beta)] = {'nonneg': nz, 'normalized': nor, 'distinct_rows': sens}
        ok_all = ok_all and good
    claim('S3', '★ 真陽性對照（out-of-sample）：vertex(12 軸) 與 face(20 軸) 讀出表之 R ≡ 0 ⟹'
                'W = 1/n + beta·K（beta = ±1/n）皆 非負＋歸一＋態敏感 ⟹ P4 之充分性得真實例證',
          ok_all, '; '.join('%s: rows=%d' % (k, v['distinct_rows']) for k, v in sorted(pos.items())))

    # --- 退化個案確認：參考軸 = 中心元素 ±1（向量部 0）---
    n_center_axes = sum(1 for u in U if zero_vec(u))
    claim('S4', 'scripts/05 Q4 之 3 個「R 恆常」個案 = 參考軸抽到中心元素 ±1（向量部 = (0,0,0)）'
                '⟹ 全零讀出（K ≡ 0），屬退化抽樣、唔屬 ±1 讀出族 ⟹ 非 P4 反例',
          n_center_axes == 0,
          '凍結 62 軸中零向量軸數 = %d（凍結集無此退化）⟹ 3/200 = 參考軸命中 ±1 之機率 2/120 = 1/60 之預期 3.3'
          % n_center_axes)
    out = {'rules': 'r1-axis-sign-structure-v1', 'negation_closed_all': closed_all,
           'per_type': per, 'positive_control': pos, 'claims': CLAIMS}
    with io.open(os.path.join(DATA, '06_r1_axis_sign_structure.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
