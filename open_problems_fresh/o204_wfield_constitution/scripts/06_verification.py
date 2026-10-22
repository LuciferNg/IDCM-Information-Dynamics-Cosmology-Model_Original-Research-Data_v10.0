#!/usr/bin/env python3
"""
O204 — Script 06: 重跑驗證 (Closure Discipline: 重跑腳本驗證 + data/stdout 一致)
================================================================================
1. 重跑 scripts/01-05 (subprocess, 全新 process)
2. 解析 stdout 之 PASS/FAIL 計數
3. 同 data/*.txt 記錄比較 (data 與 stdout 一致律)
4. 輸出 data/00_verification.json (機器可讀)
"""
import os
import re
import json
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = ['01_decomposition', '02_constitution', '03_behavior', '04_principle', '05_audit']
DATA = os.path.join(BASE, 'data')

report = {}
total_pass = total_all = 0
print("=" * 78)
print("  O204 Script 06 — 重跑驗證")
print("=" * 78)
for s in SCRIPTS:
    path = os.path.join(BASE, 'scripts', f'{s}.py')
    r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=600)
    out = r.stdout
    m = re.search(r'總計: (\d+)/(\d+) PASS', out)
    npass, nall = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    nfail = out.count('[FAIL]')
    # data 檔案記錄
    df = os.path.join(DATA, f'{s}_results.txt')
    stored = ''
    if os.path.exists(df):
        stored = open(df).read()
    sm = re.search(r'(\d+)/(\d+) PASS', stored)
    stored_pair = (int(sm.group(1)), int(sm.group(2))) if sm else None
    consistent = (stored_pair == (npass, nall))
    total_pass += npass
    total_all += nall
    report[s] = {
        'exit_code': r.returncode,
        'pass': npass, 'total': nall, 'fail_lines': nfail,
        'stored_data': stored_pair,
        'data_consistent': consistent,
        'status': 'PASS' if (r.returncode == 0 and nfail == 0 and npass == nall and consistent)
                  else 'FAIL',
    }
    print(f"  {s:18s} exit={r.returncode} {npass}/{nall} FAILlines={nfail} "
          f"data={stored_pair} consistent={consistent} → {report[s]['status']}")

allok = all(v['status'] == 'PASS' for v in report.values())
print("-" * 78)
print(f"  總計: {total_pass}/{total_all} PASS")
print(f"  全部腳本 exit=0 + 零 FAIL + data 一致: {'✅ 是' if allok else '❌ 否'}")
print("=" * 78)

report['_summary'] = {
    'total_pass': total_pass,
    'total_checks': total_all,
    'all_scripts_clean': allok,
    'date': '2026-09-18',
    'o': 'O204',
}
with open(os.path.join(DATA, '00_verification.json'), 'w') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"\n  → {os.path.join(DATA, '00_verification.json')}")
sys.exit(0 if allok else 1)
