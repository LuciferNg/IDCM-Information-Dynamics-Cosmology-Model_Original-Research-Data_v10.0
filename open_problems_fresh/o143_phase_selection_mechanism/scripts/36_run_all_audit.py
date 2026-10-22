#!/usr/bin/env python3
"""
O143 #36 — 全套腳本重跑審計 (Task 1)
=====================================
逐個 scripts/01..40 重跑 (排除本檔), 記錄 exit code + 輸出行數 + 尾行。
2026-09-21: 範圍由 01-35 擴至 01-40 (新增 37/38/39/40 審計腳本)。
輸出 data/step33_full_rerun_audit.json
"""
import subprocess, os, json, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = '/usr/bin/python3'
SKIP = {'36_run_all_audit.py'}

scripts = sorted(f for f in os.listdir(HERE) if f.endswith('.py') and f not in SKIP)
res = {}
print(f"重跑 {len(scripts)} 個腳本 (cwd = {ROOT})\n")
print(f"{'腳本':<38}{'exit':>6}{'秒':>8}{'行':>6}  尾行")
print("-"*110)
for s in scripts:
    t0 = time.time()
    try:
        p = subprocess.run([PY, os.path.join(HERE, s)], cwd=ROOT,
                           capture_output=True, text=True,
                           timeout=(1500 if s == '39_verify_o150_corrections.py' else 900))
        out = p.stdout + p.stderr
        rc = p.returncode
    except subprocess.TimeoutExpired:
        out, rc = 'TIMEOUT', -9
    dt = time.time() - t0
    lines = [l for l in out.splitlines() if l.strip()]
    tail = lines[-1][:70] if lines else ''
    res[s] = {'exit': rc, 'seconds': round(dt, 1), 'nlines': len(lines),
              'tail': tail, 'warn': ('Traceback' in out or 'Error' in out)}
    print(f"{s:<38}{rc:>6}{dt:>8.1f}{len(lines):>6}  {tail}")

n_ok = sum(1 for v in res.values() if v['exit'] == 0)
print("-"*110)
print(f"\n總計: {n_ok}/{len(scripts)} exit 0")
bad = [k for k, v in res.items() if v['exit'] != 0]
if bad:
    print(f"非零 exit: {bad}")
with open(os.path.join(ROOT, 'data', 'step33_full_rerun_audit.json'), 'w') as f:
    json.dump({'n_ok': n_ok, 'n_total': len(scripts), 'per_script': res}, f, indent=2, ensure_ascii=False)
print(f"✅ 已存: data/step33_full_rerun_audit.json")
