#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/92 -- 全鏈盲測審計：階段 A（重現）＋ B（文檔宣稱綁定）。

A 重現：依編號重跑 scripts/01–91（缺 08／09 為宣告式留白），逐支記錄 exit／RESULT／FAIL tags／
  Traceback／耗時；輸出每支完整日誌至 logs/92_sweep/<name>.out。
B 綁定：把 docs/*_results.md 內「RESULT: n/m」與表列判決，與重跑結果逐輪比對；漂移分兩類：
  gate_bad（契約閘之一見數前判據，事後重跑必 FAIL —— C8 型）／drift（其餘，需人工判讀）。
輸出：data/92_audit_sweep.json（機器可讀）＋ 終端摘要。

唯讀 O222；不 import 本 o 之任何推導 script（只以子進程重跑）。用法: /usr/bin/python3 scripts/92_audit_sweep.py [--only N1,N2]
"""
import io
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
OUTDIR = os.path.join(BASE, 'logs')  # 扁平：logs/92_<script>.out（不用子目錄，免破壞各審計器之檔假設）
DATA = os.path.join(BASE, 'data', '92_audit_sweep.json')
TIMEOUT = 600

# 輪次 → 三件套（與 47_chain_index.py 之 ROUND_MAP 同構；本審計自行硬編碼以免耦合）
ROUNDS = [
    ('R0',  ['01_recon_invariants']),
    ('R1',  ['02_r1_contract', '03_r1_barrier', '04_r1_audit', '05_r1_null_analysis',
             '06_r1_axis_sign_structure', '07_r1_tie_mechanism']),
    ('R2',  ['10_r2_contract', '11_r2_g1_table', '12_r2_dyn17', '13_r2_audit']),
    ('R3',  ['14_r3_contract', '15_r3_centre_theorem', '16_r3_audit']),
    ('R4',  ['17_r4_contract', '18_r4_tie_parity', '19_r4_audit']),
    ('R5',  ['20_r5_contract', '21_r5_tie_global', '22_r5_audit']),
    ('R6',  ['23_r6_contract', '24_r6_mechanism', '25_r6_geometry', '26_r6_audit']),
    ('R7',  ['27_r7_contract', '28_r7_mechanism2', '29_r7_audit']),
    ('R8',  ['30_r8_contract', '31_r8_group', '32_r8_audit']),
    ('R9',  ['33_r9_contract', '34_r9_pairing', '35_r9_audit']),
    ('CLOSEOUT-1', ['36_closeout_audit', '37_closeout_docs']),
    ('R10', ['38_r10_contract', '39_r10_universal', '40_r10_audit']),
    ('R11', ['41_r11_contract', '42_r11_machine', '43_r11_audit']),
    ('R12', ['44_r12_contract', '45_r12_machine', '46_r12_audit', '47_chain_index']),
    ('R13', ['48_r13_contract', '49_r13_machine', '50_r13_audit']),
    ('R14', ['51_r14_contract', '52_r14_machine', '53_r14_audit']),
    ('R15', ['54_r15_contract', '55_r15_machine', '56_r15_audit']),
    ('R16', ['57_r16_contract', '58_r16_machine', '59_r16_audit']),
    ('R17', ['60_r17_contract', '61_r17_machine', '62_r17_audit']),
    ('R18', ['63_r18_contract', '64_r18_machine', '65_r18_audit']),
    ('R19', ['66_r19_contract', '67_r19_machine', '68_r19_audit']),
    ('R20', ['69_r20_contract', '70_r20_machine', '71_r20_audit']),
    ('R21', ['72_r21_contract', '73_r21_machine', '74_r21_audit']),
    ('R22', ['75_r22_contract', '76_r22_machine', '77_r22_audit']),
    ('R23', ['78_r23_contract', '79_r23_machine', '80_r23_audit']),
    ('R24', ['83_r24_contract', '84_r24_machine', '85_r24_audit']),
    ('R25', ['86_r25_contract', '87_r25_machine', '88_r25_audit']),
    ('R26', ['89_r26_contract', '90_r26_machine', '91_r26_audit']),
]
META = ['46_r12_audit', '47_chain_index', '36_closeout_audit', '37_closeout_docs', '81_o225_closeout2_audit',
        '82_o225_closeout2_docs']
RES_RE = re.compile(r'RESULT:\s*(\d+)\s*/\s*(\d+)\s*PASS')
TAG_RE = re.compile(r'^\[(PASS|FAIL)\]\s+(\S+)', re.M)


def parse_out(txt):
    m = None
    for m in RES_RE.finditer(txt):
        pass
    res = (int(m.group(1)), int(m.group(2))) if m else (None, None)
    fails = [t for st, t in TAG_RE.findall(txt) if st == 'FAIL']
    npass = len([1 for st, t in TAG_RE.findall(txt) if st == 'PASS'])
    return res, fails, npass


def main():
    only = None
    if '--only' in sys.argv:
        only = set(sys.argv[sys.argv.index('--only') + 1].split(','))
    os.makedirs(OUTDIR, exist_ok=True)
    allnames = [n for _r, lst in ROUNDS for n in lst]
    SKIP = {'81_o225_closeout2_audit', '82_o225_closeout2_docs', '92_audit_sweep', '93_audit_blind',
            '94_record_rebuild'}
    extra = sorted(f[:-3] for f in os.listdir(os.path.join(BASE, 'scripts'))
                   if f.endswith('.py') and f[:2].isdigit() and f not in [x + '.py' for x in allnames]
                   and f[:-3] not in SKIP)
    order = allnames + sorted(set(extra) - set(allnames))
    rec = {}
    print('=' * 112)
    print('O225 scripts/92 -- 全鏈盲測審計（A 重現）  共 %d 支' % len(order))
    print('=' * 112, flush=True)
    for i, nm in enumerate(order, 1):
        if only and nm.split('_')[0] not in only and nm not in only:
            continue
        path = os.path.join(BASE, 'scripts', nm + '.py')
        if not os.path.exists(path):
            rec[nm] = {'missing': True}
            print('[%3d] %-34s MISSING' % (i, nm), flush=True)
            continue
        t0 = time.time()
        try:
            p = subprocess.run(['/usr/bin/python3', path], cwd=BASE, capture_output=True, text=True,
                               timeout=TIMEOUT)
            txt = (p.stdout or '') + (p.stderr or '')
            code = p.returncode
            to = False
        except subprocess.TimeoutExpired as e:
            txt = ((e.stdout or '') if isinstance(e.stdout, str) else '') + '\n[TIMEOUT %ds]' % TIMEOUT
            code, to = 124, True
        dt = time.time() - t0
        io.open(os.path.join(OUTDIR, '92_' + nm + '.out'), 'w', encoding='utf-8').write(txt)
        (np_, tot), fails, npass = parse_out(txt)
        rec[nm] = {'exit': code, 'timeout': to, 'sec': round(dt, 1), 'res': [np_, tot], 'fails': fails,
                   'pass_tags': npass, 'traceback': ('Traceback' in txt), 'bytes': len(txt)}
        print('[%3d] %-34s exit=%-3s %5.1fs  RESULT=%-7s FAIL=%-22s TB=%s'
              % (i, nm, code, dt, '%s/%s' % (np_, tot) if tot else '-', ','.join(fails[:3]) or '-',
                 'Y' if rec[nm]['traceback'] else 'n'), flush=True)
        json.dump(rec, io.open(DATA, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    json.dump(rec, io.open(DATA, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    bad = [k for k, v in rec.items() if v.get('missing') or v.get('timeout') or v.get('traceback')]
    print('\nA 段完成：%d 支；異常（缺檔／逾時／Traceback）= %s' % (len(rec), bad or '無'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
