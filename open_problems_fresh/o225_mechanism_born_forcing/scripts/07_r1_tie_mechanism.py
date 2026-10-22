#!/usr/bin/env python3
"""O225 scripts/07 -- R1 診斷（續）：R(s) = ±10 之精確機制（tie 規則）＋ 零成本修改分支。

scripts/06 之 S1/S2 兩個預期 FAIL（我原以為軸集唔對負封閉）：實測凍結 62 軸**係**對負封閉。
⟹ R ≠ 0 之真機制唔係符號不平衡，而係**tie 規則（dot = 0）之 u-偶性**：
   u 與 -u 成對時，非 tie 條目互相抵消；但 tie 條目之符號取「r 之首個非零分量」（與 u 無關）
   ⟹ 每對 tie 貢獻 2·s（唔抵消）⟹ R(s) = 2·Σ_{tie pairs} s。

本支驗：（T1）tie 計數（T2）R = 2·Σ tie 符號（T3）零成本修改分支 M-b：把 tie 規則改為 u-**奇**
（dot = 0 ⟹ 取 u x r_s 之首個非零分量之符號）⟹ 應得 R ≡ 0、且仿射 Born 族出現（零新欄、零新參數）。

用法:  /usr/bin/python3 scripts/07_r1_tie_mechanism.py
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
    spec = importlib.util.spec_from_file_location('o222y_' + script[:-3], os.path.join(O222S, script))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    m = load_o222('09_a2_rollback.py')
    axes, U, ids, types, hvec = m.load_inputs()
    G, idx, MUL = m.build_group()
    KV = [m.rot_ref(q, U[0]) for q in G]
    A = m.add
    M = m.mul
    nS, nA = 120, len(U)

    K, ties, tie_sign_sum = [], [], []
    Kb = []                                    # M-b: tie 規則改為 u-奇
    for i in range(nS):
        r = KV[i]
        row, trow, tsign, brow = [], [], 0, []
        for u in U:
            dot = A(A(M(u[0], r[0]), M(u[1], r[1])), M(u[2], r[2]))
            s = m.sgn(dot)
            if s == 0:
                trow.append(1)
                ts = 0
                for comp in r:
                    sc = m.sgn(comp)
                    if sc:
                        ts = sc
                        break
                tsign += ts
                # u-奇規則：cross(u, r) 之首個非零分量
                c0 = (M(u[1], r[2])[0] - M(u[2], r[1])[0], M(u[1], r[2])[1] - M(u[2], r[1])[1])
                c1 = (M(u[2], r[0])[0] - M(u[0], r[2])[0], M(u[2], r[0])[1] - M(u[0], r[2])[1])
                c2 = (M(u[0], r[1])[0] - M(u[1], r[0])[0], M(u[0], r[1])[1] - M(u[1], r[0])[1])
                sb = 0
                for comp in (c0, c1, c2):
                    sc = m.sgn(comp)
                    if sc:
                        sb = sc
                        break
                if sb == 0:
                    for comp in r:
                        sc = m.sgn(comp)
                        if sc:
                            sb = sc
                            break
                s = ts
                brow.append(sb)
            else:
                trow.append(0)
                brow.append(s)
            row.append(s)
        K.append(row)
        ties.append(sum(trow))
        tie_sign_sum.append(tsign)
        Kb.append(brow)

    tot_ties = sum(ties)
    claim('T1', 'tie 條目總數 = %d（= 1200 = 16.13%% of 7440，與 O222 docs/13 §2(b) 一致）；每 row 之 tie 數 = %s'
          % (tot_ties, sorted(set(ties))),
          tot_ties == 1200 and set(ties) == {10},
          'total = %d ; per-row distinct = %s' % (tot_ties, sorted(set(ties))))
    R = [sum(r) for r in K]
    claim('T2', '★ R(s) = Σ_{tie 條目} tie_sign（非 tie 條目因對負封閉而兩兩抵消；tie 條目之 u-偶性 ⟹ 唔抵消）'
                '—— 逐 row 精確吻合',
          R == tie_sign_sum, 'R distinct = %s ; Σ_{tie} sign distinct = %s' % (sorted(set(R)),
                                                                              sorted(set(tie_sign_sum))))
    claim('T3', '★ 每 row 10 個 tie **同號** ⟹ Σ = ±10 = R（即 R 唔可能取其他值）',
          set(tie_sign_sum) == {-10, 10} and R == tie_sign_sum,
          'Σ tie sign per row distinct = %s' % sorted(set(tie_sign_sum)))
    Rn = [sum(r) for r in Kb]
    claim('T4', '★ 零成本分支 M-b：tie 規則改為 u-奇（dot = 0 ⟹ sgn(u x r_s 之首非零分量)）⟹ R ≡ 0',
          set(Rn) == {0}, 'M-b row sums distinct = %s' % sorted(set(Rn)))
    Kb_rows = len(set(tuple(r) for r in Kb))
    okb = True
    det = {}
    for beta in (F(1, nA), F(-1, nA)):
        W = [[F(1, nA) + beta * Kb[s][a] for a in range(nA)] for s in range(nS)]
        nz = all(v >= 0 for r in W for v in r)
        nor = all(sum(r) == 1 for r in W)
        sens = len(set(tuple(r) for r in W))
        det[str(beta)] = (nz, nor, sens)
        okb = okb and nz and nor and sens > 1
    claim('T5', '★ M-b 讀出表之仿射 Born 族：W = 1/62 + beta·K_b（beta = ±1/62）皆 非負＋歸一＋態敏感'
          '（相異 row = %d）' % Kb_rows,
          okb and Kb_rows > 1, 'distinct rows of K_b = %d ; per-beta = %s' % (Kb_rows, det))
    claim('T6', '★ M-b 讀出表仍屬 {±1} 族（無 0 值、無新值域）⟹ 零成本分支唔離開凍結讀出字母表',
          set(v for r in Kb for v in r) == {-1, 1},
          'M-b value set = %s' % sorted(set(v for r in Kb for v in r)))
    out = {'rules': 'r1-tie-mechanism-v1', 'total_ties': tot_ties, 'per_row_ties': sorted(set(ties)),
           'R': sorted(set(R)), 'tie_sign_sum_distinct': sorted(set(tie_sign_sum)),
           'M_b_rowsum_distinct': sorted(set(Rn)), 'M_b_distinct_rows': Kb_rows,
           'claims': CLAIMS}
    with io.open(os.path.join(DATA, '07_r1_tie_mechanism.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('RESULT: %d/%d PASS' % (npass, len(CLAIMS)))
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    sys.exit(main())
