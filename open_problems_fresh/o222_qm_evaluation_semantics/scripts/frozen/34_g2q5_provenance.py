#!/usr/bin/env python3
"""O222 scripts/34 -- G2 + Q5 PROVENANCE MACHINE (6 cells).

Reads ONLY the 14 pinned read-only upstream artefacts (J1-J14, hashes in data/33_g2q5_freeze.json) and
decides, mechanically, the two unclosed O222 items:
  G2a  the identity of O206's f(n)  (mass-closure factor, hypothesis falsified)
  G2b  availability of the resource-side per-mode frequency  w_n = sqrt(gamma_n) = 2 sin(pi n/88)
  G2c  the UNIQUE new computation: sensitivity bounds of the pass length under a non-uniform cost ladder
  Q5a  the F_proj symbol collision (dim=17 vs the mass shape factor C_f)
  Q5b  the triple identity 17 = N_d - n* = L5 + C(4,2) = L6 - 1 and its algebraic collapse
  Q5c  the energy side: three recorded numbers, E_capture recomputed, and the 8/13 test

Usage:  /usr/bin/python3 scripts/34_g2q5_provenance.py
"""
import hashlib
import io
import json
import os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROOT))
CELLS = ['G2a', 'G2b', 'G2c', 'Q5a', 'Q5b', 'Q5c']
SEP = '~'
RESULTS = []
NUM = {}          # every number this machine reports, for the audit to re-derive


def say(cell, name, verdict, detail):
    RESULTS.append({'cell': cell, 'name': name, 'verdict': verdict, 'detail': detail})
    print('[%s] %-4s %s' % (verdict, cell, name), flush=True)
    print('      %s' % detail, flush=True)


def find(text, needle, label, cell, out):
    hit = [l.strip() for l in text.split('\n') if needle in l]
    out.append((label, needle, len(hit), hit[:2]))
    return hit


def main():
    freeze = json.load(io.open(os.path.join(ROOT, 'data', '33_g2q5_freeze.json'), encoding='utf-8'))
    bad = []
    T = {}
    for j in sorted(freeze['pins']):
        p = os.path.join(REPO, freeze['pins'][j]['path'])
        if hashlib.sha256(io.open(p, 'rb').read()).hexdigest() != freeze['pins'][j]['sha256']:
            bad.append(j)
        T[j] = io.open(p, encoding='utf-8').read()
    if bad:
        print('PIN DRIFT: %s -- abort' % bad)
        return 1
    J = json.loads(T['J6'])
    spec = json.loads(T['J11'])['k_chain_modes']
    n_d, l_6, l_5 = 44, 18, 11
    cells = {}

    # ---------------------------------------------------------------- G2a
    ev = []
    find(T['J3'], 'μ²·f(n)', 'J3 f(n) 定義式', 'G2a', ev)
    find(T['J3'], '未導出', 'J3 f(n) 未導出', 'G2a', ev)
    f1 = find(T['J1'], '證偽', 'J1 f(n) 證偽', 'G2a', ev)
    f2 = find(T['J2'], '真實開放項', 'J2 剩餘開放項', 'G2a', ev)
    st1 = [l.strip() for l in T['J1'].split('\n') if l.startswith('## 狀態')]
    st2 = [l.strip() for l in T['J2'].split('\n') if l.startswith('## 狀態')]
    NUM['G2a_state_labels'] = [st1[:1], st2[:1]]
    def_line = [x for x in ev if x[0] == 'J3 f(n) 定義式'][0][2]
    ok = def_line >= 1 and len(f1) >= 1 and len(ev) >= 3
    say('G2a', 'O206 之 f(n) = 質量閉合因子（`ω_n = μ²·f(n)`），其假說已明文否證；'
               '與資源成本之頻率無關', '✅' if ok else '🔴',
        'J3 定義行 %d 條；J1 否證行 %d 條；J2 剩餘開放項 %d 條；'
        '狀態標籤 J1=%s vs J2=%s（⚠ 上游記載層不一致，唯讀不改）'
        % (def_line, len(f1), len(f2), (st1[:1] or ['?'])[0][:34], (st2[:1] or ['?'])[0][:34]))
    cells['G2a'] = ok
    NUM['G2a_f1_quote'] = [l[:150] for l in f1[:1]]

    # ---------------------------------------------------------------- G2b
    om = [(int(k), v['omega'], v['gamma']) for k, v in spec.items()]
    om.sort()
    rel = max(abs(g - w * w) / (w * w) for _n, w, g in om)
    def_g = [(int(k), v['gamma']) for k, v in spec.items() if int(k) >= 1]
    nmodes = len(om)
    w44 = [w for n, w, _g in om if n == 44][0]
    fid = find(T['J4'], 'fiducial', 'J4 fiducial', 'G2b', ev) + \
        find(T['J4'], '結構強制', 'J4 結構強制', 'G2b', ev) + \
        find(T['J5'], 'fiducial 約定', 'J5 fiducial 約定', 'G2b', ev)
    i4 = find(T['J13'], '均勻', 'J13 I4 均勻', 'G2b', ev)
    okb = nmodes == 44 and rel <= float(F(1, 10 ** 9)) and abs(w44 - 2) <= float(F(1, 10 ** 9)) \
        and len(fid) >= 2
    NUM['G2b'] = {'n_modes': nmodes, 'max_rel_dev_gamma_vs_omega_sq': rel, 'omega_44': w44}
    say('G2b', '資源側逐模頻率已存在且可算：`ω_n = √γ_n = 2sin(πn/88)`（44 模；`ω_44 = 2` Nyquist）；'
               '`ω = μ²` 係 fiducial 非結構強制', '✅' if okb else '🔴',
        '模數 %d；max|γ_n − ω_n²|/ω_n² = %.3e；ω_44 = %.12f；fiducial/結構強制 語句 %d 條；J13 I4 之「均勻」語句 %d 條'
        % (nmodes, rel, w44, len(fid), len(i4)))
    cells['G2b'] = okb

    # ---------------------------------------------------------------- G2c
    per_read, budget, e_min = F(123, 88), F(123, 2), F(123, 176)
    sw = sum(w for _n, w, _g in om)
    mean_w = sw / nmodes
    cs = [(n, float(per_read) * (w / mean_w)) for n, w, _g in om]
    c_min = min(c for _n, c in cs)
    c_max = max(c for _n, c in cs)
    tot = sum(c for _n, c in cs)
    def nmax(c):
        return int((float(budget) - float(e_min)) / c) + 1
    n_uniform = nmax(float(per_read))
    lo, hi = nmax(c_max), nmax(c_min)
    okc = abs(tot - float(budget)) <= float(F(1, 10 ** 9)) and lo <= 88 <= hi and n_uniform == 44
    NUM['G2c'] = {'sum_c_n': tot, 'mean_omega': mean_w, 'c_min': c_min, 'c_max': c_max,
                  'n_max_low': lo, 'n_max_high': hi, 'n_max_uniform_sanity': n_uniform,
                  'reads_sigma_omega': float(sw), 'budget': float(budget), 'E_min': float(e_min)}
    say('G2c', '非均勻歷階 `c_n = (123/88)(ω_n/⟨ω⟩)`：Σc_n = 61.5 精確；讀數界 = [最貴模態, 最平模態] = '
               '[%d, %d]（uniform 88 ∈ 界內；uniform 上限重現 B5 之 44 讀／pass = 內建 sanity）' % (lo, hi),
        '✅' if okc else '🔴',
        'Σω_n = %.9f、⟨ω⟩ = %.9f；c_min = %.9f（n=1）、c_max = %.9f（n=44）；'
        'n_max(c) = ⌊(123/2 − 123/176)/c⌋ + 1；n_max(123/88) = %d == B5 之 44 ✓；'
        '⚠ read↦mode n 未定義 ⟹ 只報界；採用非均勻歷階 = modelling choice'
        % (sw, mean_w, c_min, c_max, n_uniform))
    cells['G2c'] = okc

    # ---------------------------------------------------------------- Q5a
    m17 = find(T['J7'], 'F_proj = dim ker T_pipe = 17 = L₆−1', 'J7 F_proj=17', 'Q5a', ev)
    mreg = find(T['J8'], 'F_proj = 17 = dim ker T_pipe', 'J8 registry', 'Q5a', ev)
    m193 = find(T['J10'], 'F_proj = L₆−1', 'J10 跨O引用', 'Q5a', ev)
    mcf = find(T['J14'], '18/5', 'J14 F_proj 形狀因子值', 'Q5a', ev)
    mcf1 = find(T['J1'], 'C_f(gen1) = 18/5', 'J1 C_f(gen1)', 'Q5a', ev)
    eq = [l.strip()[:120] for j in sorted(T) for l in T[j].split('\n')
          if ('F_proj = C' in l or 'C_f = F_proj' in l) and 'C_f(gen1)' not in l]
    oka = len(m17) >= 1 and len(mreg) >= 1 and len(m193) >= 1 and len(mcf) >= 1 and len(mcf1) >= 1 and not eq
    NUM['Q5a'] = {'dim_route_hits': len(m17) + len(mreg) + len(m193),
                  'cf_route_hits': len(mcf) + len(mcf1), 'equality_assertions': eq}
    say('Q5a', '`F_proj` 符號碰撞：兩個互不相同之對象（(i) 17 = dim ker T_pipe；(ii) 質量框架之形狀因子 '
               'C_f = {18/5, 15.5, 37, 42}）；全 14 件 pinned 檔中**冇**任何等式斷言 ⟹ 三方「衝突」= 同名',
        '✅' if oka else '🔴',
        '維數路線命中 %d 條（J7/J8/J10）；形狀因子路線命中 %d 條（J14 + J1 之 C_f(gen1)=18/5）；'
        '等式斷言 = %s' % (len(m17) + len(mreg) + len(m193), len(mcf) + len(mcf1), eq or 'none'))
    cells['Q5a'] = oka

    # ---------------------------------------------------------------- Q5b
    a, b, c = n_d - J['n_star'], l_5 + 6, l_6 - 1                      # 44-27, 11+C(4,2), 18-1
    luc = [2, 1]
    for _i in range(2, 7):
        luc.append(luc[-1] + luc[-2])
    alg = (n_d - (n_d - l_6 + 1)) == (l_6 - 1)
    kern = J['kernel_modes'] if isinstance(J['kernel_modes'], list) else []
    tri = J.get('triple_identity', {})
    okb2 = a == b == c == 17 and alg and kern == list(range(28, 45)) and J['kernel_count'] == 17
    NUM['Q5b'] = {'A_Nd_minus_n_star': a, 'B_L5_plus_C42': b, 'C_L6_minus_1': c, 'L6_lucas': luc[6],
                  'algebraic_collapse': alg, 'kernel_modes_count': len(kern),
                  'recorded_triple': tri}
    say('Q5b', '三重身份 `17 = N_d − n* = L₅ + C(4,2) = L₆ − 1`（A/B/C 全 17）且 `n* ≡ N_d − L₆ + 1` '
               '使 A 與 C **代數同一** ⟹ 恆等式非數值巧合；O121 譜資料之 kernel_modes = [28..44] 共 17',
        '✅' if okb2 else '🔴',
        'A = 44 − 27 = %d；B = 11 + 6 = %d；C = L₆ − 1 = %d（Lucas 迭代 L₆ = %d）；代數收斂 = %s；'
        'O121 recorded triple = %s' % (a, b, c, luc[6], alg, tri))
    cells['Q5b'] = okb2

    # ---------------------------------------------------------------- Q5c
    e_sync = F(44 * 123, 88)
    e_cap_rec = J['E_capture_geq28']
    g = {int(k): v['gamma'] for k, v in spec.items()}
    e_cap = sum(g[n] for n in range(28, 45))
    e_theory = J['E_sync_theory']
    e_bot = J['E_bottleneck_sync']
    bot_own = float(e_sync) - e_cap
    d813 = F(8, 13)
    dev = abs(e_bot - float(d813))
    okc2 = abs(e_cap - e_cap_rec) <= float(F(1, 10 ** 9)) and abs(bot_own - e_bot) <= float(F(1, 10 ** 9)) \
        and e_sync == F(123, 2)
    NUM['Q5c'] = {'E_sync_closed': float(e_sync), 'E_capture_recorded': e_cap_rec,
                  'E_capture_recomputed': e_cap, 'E_sync_theory': e_theory, 'E_bottleneck_recorded': e_bot,
                  'E_bottleneck_recomputed': bot_own, 'eight_thirteenths': float(d813),
                  'dev_from_8_13': dev, 'is_8_13': dev <= float(F(1, 10 ** 6))}
    say('Q5c', '能量側三數逐字 ＋ 由 γ 譜獨立重算 E_capture；`E_sync^{closed} = 44×123/88 = 61.5` '
               '**＝ O222 B5 之 I1（跨 O 連結）**；`E_bottleneck` 對 8/13 之偏差 = %.3e ⟹ **唔係** 8/13'
        % dev, '✅' if okc2 else '🔴',
        'E_sync = %r（精確 123/2）vs E_sync_theory = %.14f vs E_capture(γ 譜 n≥28) = %.14f'
        '（記錄 %.14f）；E_bottleneck = %.16f（自算 %.16f）；8/13 = %.16f ⟹ 偏差 %.3e > 1e-6 '
        '（小數級近似，非等式）；成因未定 ⟹ 能量側維持 🟡'
        % (float(e_sync), e_theory, e_cap, e_cap_rec, e_bot, bot_own, float(d813), dev))
    cells['Q5c'] = okc2

    out = {'cells': cells, 'results': RESULTS, 'numbers': NUM,
           'verdicts': {'G2': '🟢 已判定（負面 ＋ 層次修正）' if cells['G2a'] and cells['G2b'] and cells['G2c']
                        else '🔴',
                        'Q5_dim': '🟢 維數側已統一' if cells['Q5b'] else '🔴',
                        'Q5_energy': '🟡 已量化（成因未定）'},
           'pins': {j: freeze['pins'][j]['sha256'][:16] for j in sorted(freeze['pins'])}}
    with io.open(os.path.join(ROOT, 'data', '34_g2q5_results.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print('-' * 110)
    print('CELLS = %s ; pass = %d/%d' % (cells, sum(1 for v in cells.values() if v), len(CELLS)))
    print('-' * 110)
    return 0 if all(cells.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
