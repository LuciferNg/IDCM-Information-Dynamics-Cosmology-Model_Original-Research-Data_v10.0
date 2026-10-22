#!/usr/bin/env python3
"""O38 全面最終驗證 — 重跑全部 15 scripts"""
import subprocess, os, sys, re

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o38_kappa_prediction"
os.chdir(BASE)

scripts = sorted(os.listdir("scripts"))
py_scripts = [s for s in scripts if s.endswith(".py")]

print("=" * 70)
print("  O38 全面最終驗證 — 全部 scripts")
print("=" * 70)

results = []
for s in py_scripts:
    try:
        r = subprocess.run([sys.executable, f"scripts/{s}"],
                           capture_output=True, text=True, timeout=180)
        out = r.stdout + r.stderr
        # 搵結果行
        m = re.search(r"(結果|審計|核對|整合驗證|獨立 Audit|裁決|一致性|誤標|影響量化)[^:：]*[:：]?\s*(\d+/\d+ PASS)", out)
        summary = m.group(0).strip() if m else ""
        if not summary:
            # 搵任何 PASS 計數
            m2 = re.search(r"(\d+/\d+ PASS)", out)
            summary = m2.group(1) if m2 else ""
        status = "✅" if r.returncode == 0 else "❌"
        print(f"  {status} {s}: exit={r.returncode} {summary}")
        results.append((s, r.returncode == 0))
    except subprocess.TimeoutExpired:
        print(f"  ⏱️ {s}: TIMEOUT")
        results.append((s, False))

n_pass = sum(1 for _, ok in results if ok)
print(f"\n{'='*70}")
print(f"  總計: {n_pass}/{len(results)} PASS")
print("=" * 70)
sys.exit(0 if n_pass == len(results) else 1)
