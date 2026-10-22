#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/101 -- 審計索引（單一入口）：彙整 data/92–104 之審計層結果為索引表。

產出：data/101_audit_index.json ＋ 終端索引（層／引擎／產物／判決）。
用法: /usr/bin/python3 scripts/101_audit_index.py
"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
D = os.path.join(BASE, 'data')
LAYERS = [
    ('A', '92_audit_sweep.json', 'scripts/92_audit_sweep.py', '逐支重跑（88 支）'),
    ('A2', '97_drift_audit.json', 'scripts/97_drift_audit.py', '三方對帳（凍結 JSON↔重跑↔歷史日誌）'),
    ('B', '95_doc_binding.json', 'scripts/95_doc_binding.py', '宣稱↔證據綁定'),
    ('C/D', '93_audit_blind.json', 'scripts/93_audit_blind.py', '獨立重算＋精確 null'),
    ('Q1', '98_round_claim_check.json', 'scripts/98_round_claim_check.py', '逐輪文檔聲稱↔重跑'),
    ('Q3', '99_gap_blind.json', 'scripts/99_gap_blind.py', '缺口補完（Λ/Z10、f 三重、三支和）'),
    ('Q3', '100_register_sync.json', 'scripts/100_register_sync.py', 'register↔problem_record 同步'),
    ('R27', '103_r27_machine.json', 'scripts/103_r27_machine.py', 'CRIT-1 orbit 分類／三層族'),
    ('R27', '104_r27_audit.json', 'scripts/104_r27_audit.py', 'R27 獨立審計'),
    ('R28', '106_r28_machine.json', 'scripts/106_r28_machine.py', 'CRIT-2 響應矩陣／MISC-1 τ-orbit'),
    ('R28', '107_r28_audit.json', 'scripts/107_r28_audit.py', 'R28 獨立審計'),
    ('R29', '109_r29_machine.json', 'scripts/109_r29_machine.py', 'MECH-1 殘餘／MECH-2 收口'),
    ('R29', '110_r29_audit.json', 'scripts/110_r29_audit.py', 'R29 獨立審計'),
    ('R30', '112_r30_machine.json', 'scripts/112_r30_machine.py', 'Z10-1 選擇律／Z10-2 根因'),
    ('R30', '113_r30_audit.json', 'scripts/113_r30_audit.py', 'R30 獨立審計'),
    ('R31', '115_r31_machine.json', 'scripts/115_r31_machine.py', 'STT-1 機制／四類／補集'),
    ('R31', '116_r31_audit.json', 'scripts/116_r31_audit.py', 'R31 獨立審計'),
    ('R32', '118_r32_machine.json', 'scripts/118_r32_machine.py', 'CRIT-3 充要／MISC-2 混合'),
    ('R32', '119_r32_audit.json', 'scripts/119_r32_audit.py', 'R32 獨立審計'),
    ('R33', '121_r33_machine.json', 'scripts/121_r33_machine.py', '收口批：五項閉合'),
    ('R33', '122_r33_audit.json', 'scripts/122_r33_audit.py', 'R33 獨立審計'),
]


def main():
    idx = []
    print('%-5s %-26s %-12s %s' % ('層', '引擎', '判決', '說明'))
    for layer, data, eng, desc in LAYERS:
        p = os.path.join(D, data)
        verdict = '未產出'
        if os.path.exists(p):
            try:
                d = json.load(io.open(p, encoding='utf-8'))
            except Exception:
                d = {}
            if 'n_pass' in d and 'n_total' in d:
                verdict = '%d/%d' % (d['n_pass'], d['n_total'])
            elif 'checks' in d:
                verdict = '%d/%d' % (sum(1 for c in d['checks'] if c.get('ok')), len(d['checks']))
            elif 'n_bound' in d:
                verdict = 'bound %d / unbound %d' % (d['n_bound'], d['n_unbound'])
            elif 'summary' in d:
                verdict = json.dumps(d['summary'], ensure_ascii=False)[:42]
            elif d and all(isinstance(v, dict) for v in d.values()):
                nres = sum(1 for v in d.values() if v.get('res'))
                verdict = '%d 支重跑' % len(d) if nres or len(d) > 50 else '%d 鍵' % len(d)
            elif 'n_files' in d:
                verdict = '%d files' % d['n_files']
        print('%-5s %-26s %-12s %s' % (layer, eng.split('/')[-1], verdict, desc))
        idx.append({'layer': layer, 'engine': eng, 'data': data, 'verdict': verdict, 'desc': desc})
    io.open(os.path.join(D, '101_audit_index.json'), 'w', encoding='utf-8').write(json.dumps(
        {'script': '101_audit_index', 'layers': idx,
         'note': 'o225-blind-audit-v1 之單一入口索引；細節見各層 JSON 與 docs/57'}, indent=1, ensure_ascii=False))
    print('\n索引已寫 data/101_audit_index.json（%d 層）' % len(idx))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
