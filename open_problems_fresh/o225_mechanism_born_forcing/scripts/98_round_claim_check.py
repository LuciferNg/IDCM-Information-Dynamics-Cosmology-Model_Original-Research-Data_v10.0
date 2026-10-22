#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/98 -- 逐輪「文檔聲稱 ↔ 當日重跑」嚴格比對（第 1 問之定讞表）。

對每一輪（R1→R26、close-out1/2、鏈核對）之每支腳本：
  ① 取當日重跑之 (pass,total) 與 FAIL tag 集（data/92_audit_sweep.json）；
  ② 在該輪 related docs（合約＋結果）中，環繞該腳本之引用（`scripts/NN`／`NN_name`／`scripts/NN_name`）
     取 ±260 字元窗，收集窗內所有 n/m 樣式；
  ③ 判：match（重跑值在窗內）／diverge（有 n/m 但無一相符）／no_claim（窗內無 n/m）。
另對每輪之 FAIL tag：檢查重跑 FAIL tag 是否在該輪 doc 文中出現（`FAIL` 制度之記載完整性）。

出：data/98_round_claim_check.json ＋ 終端逐輪表。唯讀。
用法: /usr/bin/python3 scripts/98_round_claim_check.py
"""
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
DOCS, DATA = os.path.join(BASE, 'docs'), os.path.join(BASE, 'data')
SW = json.load(io.open(os.path.join(DATA, '92_audit_sweep.json'), encoding='utf-8'))

PLAN = [
    ('R1', ['01_r1_contract.md', '02_r1_results.md'], ['02', '03', '04', '05', '06', '07']),
    ('R2', ['03_r2_contract.md', '04_r2_results.md'], ['10', '11', '12', '13']),
    ('R3', ['05_r3_contract.md', '06_r3_results.md'], ['14', '15', '16']),
    ('R4', ['07_r4_contract.md', '08_r4_results.md'], ['17', '18', '19']),
    ('R5', ['09_r5_contract.md', '10_r5_results.md'], ['20', '21', '22']),
    ('R6', ['11_r6_contract.md', '12_r6_results.md'], ['23', '24', '25', '26']),
    ('R7', ['13_r7_contract.md', '14_r7_results.md'], ['27', '28', '29']),
    ('R8', ['15_r8_contract.md', '16_r8_results.md'], ['30', '31', '32']),
    ('R9', ['17_r9_contract.md', '18_r9_results.md'], ['33', '34', '35']),
    ('CLOSEOUT-1', ['19_closeout_r1-r9.md'], ['36', '37']),
    ('R10', ['20_r10_contract.md', '21_r10_results.md'], ['38', '39', '40']),
    ('R11', ['22_r11_contract.md', '23_r11_results.md'], ['41', '42', '43']),
    ('R12', ['24_r12_contract.md', '25_r12_results.md'], ['44', '45', '46']),
    ('CHAIN', ['26_script_chain_index.md'], ['47']),
    ('R13', ['27_r13_contract.md', '28_r13_results.md'], ['48', '49', '50']),
    ('R14', ['29_r14_contract.md', '30_r14_results.md'], ['51', '52', '53']),
    ('R15', ['31_r15_contract.md', '32_r15_results.md'], ['54', '55', '56']),
    ('R16', ['33_r16_contract.md', '34_r16_results.md'], ['57', '58', '59']),
    ('R17', ['35_r17_contract.md', '36_r17_results.md'], ['60', '61', '62']),
    ('R18', ['37_r18_contract.md', '38_r18_results.md'], ['63', '64', '65']),
    ('R19', ['39_r19_contract.md', '40_r19_results.md'], ['66', '67', '68']),
    ('R20', ['41_r20_contract.md', '42_r20_results.md'], ['69', '70', '71']),
    ('R21', ['43_r21_contract.md', '44_r21_results.md'], ['72', '73', '74']),
    ('R22', ['45_r22_contract.md', '46_r22_results.md'], ['75', '76', '77']),
    ('R23', ['47_r23_contract.md', '48_r23_results.md'], ['78', '79', '80']),
    ('CLOSEOUT-2', ['49_o225_closeout_r1-r23.md'], ['81', '82']),
    ('R24', ['50_r24_contract.md', '51_r24_results.md'], ['83', '84', '85']),
    ('R25', ['52_r25_contract.md', '53_r25_results.md'], ['86', '87', '88']),
    ('R26', ['55_r26_contract.md', '56_r26_results.md'], ['89', '90', '91']),
]
NUM = re.compile(r'(\d+)\s*/\s*(\d+)')


def scripts_for(num):
    return [k for k in sorted(SW) if k.startswith(num + '_')]


def main():
    rows, diverge = [], []
    for label, docs, nums in PLAN:
        texts = []
        for d in docs:
            pth = os.path.join(DOCS, d)
            if os.path.exists(pth):
                texts.append((d, io.open(pth, encoding='utf-8').read()))
        per = []
        for num in nums:
            names = scripts_for(num)
            if not names:
                per.append({'num': num, 'status': 'no_script'}); continue
            v = SW[names[0]]
            rr = v.get('res')
            run = tuple(rr) if (rr and all(isinstance(x, int) for x in rr)) else None
            fails = sorted(v.get('fails') or [])
            cands, where = set(), []
            for dname, txt in texts:
                for mm in re.finditer(r'scripts/' + num + r'\b|`' + num + r'[_`]|' + num + r'_[a-z0-9_]+', txt):
                    w = txt[max(0, mm.start() - 260): mm.end() + 260]
                    for a, b in NUM.findall(w):
                        cands.add((int(a), int(b)))
                    where.append(dname)
            if run is None:
                status = 'gate_ok' if (v.get('pass_tags') and not fails) else 'no_result'
            elif not cands:
                status = 'no_claim'
            elif run in cands:
                status = 'match'
            else:
                status = 'diverge'
            ftxt = ' '.join(t for _d, t in texts)
            fails_documented = {f: (f in ftxt) for f in fails}
            per.append({'num': num, 'script': names[0], 'run': run, 'cands': sorted(cands)[:12],
                        'status': status, 'fails': fails, 'fails_documented': fails_documented,
                        'docs': sorted(set(where))})
            if status == 'diverge':
                diverge.append((label, num, run, sorted(cands)))
        rows.append({'round': label, 'docs': docs, 'scripts': per})
    summ = {}
    for r in rows:
        for s in r['scripts']:
            summ[s['status']] = summ.get(s['status'], 0) + 1
    out = {'script': '98_round_claim_check', 'summary': summ, 'rounds': rows}
    io.open(os.path.join(DATA, '98_round_claim_check.json'), 'w', encoding='utf-8').write(
        json.dumps(out, indent=1, ensure_ascii=False))
    print('=' * 116)
    print('O225 scripts/98 -- 逐輪「文檔聲稱 ↔ 當日重跑」比對（%d 輪 / %d 支）' % (len(rows), sum(len(r['scripts']) for r in rows)))
    print('=' * 116)
    print('分類 = %s' % summ)
    print()
    for r in rows:
        line = []
        for s in r['scripts']:
            tag = {'match': '✓', 'diverge': '✗', 'gate_ok': 'G', 'no_claim': '—', 'no_result': '?'}.get(s['status'], '?')
            if s.get('run'):
                line.append('%s %s/%s%s' % (s['num'], s['run'][0], s['run'][1], tag))
            else:
                line.append('%s %s' % (s['num'], tag))
        undoc = [f for s in r['scripts'] for f, ok in s.get('fails_documented', {}).items() if not ok]
        print('%-11s | %s%s' % (r['round'], '  '.join(line), ('   ⚠ 未載 FAIL: ' + ','.join(sorted(set(undoc)))) if undoc else ''))
    print()
    if diverge:
        print('**分歧清單**：')
        for lb, num, run, cands in diverge:
            print('  %s scripts/%s：重跑 %s；doc 窗內候選 %s' % (lb, num, run, cands))
    else:
        print('**分歧 = 0**（每支有文檔聲稱者，重跑值皆落在其引用窗內之候選集合中）')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
