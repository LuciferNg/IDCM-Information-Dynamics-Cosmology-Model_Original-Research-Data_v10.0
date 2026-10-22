#!/usr/bin/env python3
"""O38 最終文檔一致性核對"""
import subprocess, os, sys, re

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o38_kappa_prediction"
os.chdir(BASE)

print("=== 文檔一致性核對 ===")
checks = []
for f in ["docs/01_derivation_record.md", "01_problem_record.md", "SESSION_START.md"]:
    txt = open(f).read()
    ok = "82/82" in txt
    checks.append(ok)
    print(f"  {f}: 82/82 {'✅' if ok else '❌'}")

fr = open("final_result.md").read()
ok_fr = "🟢 已閉合" in fr and "κ̃²" in fr
checks.append(ok_fr)
print(f"  final_result.md: 🟢 已閉合 + κ̃² {'✅' if ok_fr else '❌'}")

idx = open("01_problem_record.md").read().count("推導時序索引")
checks.append(idx > 0)
print(f"  01_problem_record 時序索引: {'✅' if idx > 0 else '❌'} ({idx} 處)")

# 時序索引完整性: 9 行 scripts
tbl = re.findall(r"scripts/0(\d)_", open("01_problem_record.md").read())
seq_ok = sorted(set(int(x) for x in tbl)) == list(range(1, 10))
checks.append(seq_ok)
print(f"  時序索引 9 步齊全: {'✅' if seq_ok else '❌'} ({sorted(set(int(x) for x in tbl))})")

# 重跑 06_doc_audit
r = subprocess.run([sys.executable, "scripts/06_doc_audit.py"],
                   capture_output=True, text=True, timeout=120)
m = re.search(r"審計: (\d+/\d+ PASS)", r.stdout)
checks.append(bool(m) and m.group(1) == "16/16 PASS")
print(f"  06_doc_audit: {m.group(1) if m else 'NO'} {'✅' if m and m.group(1)=='16/16 PASS' else '❌'}")

print(f"\n  最終: {sum(checks)}/{len(checks)} 一致")
sys.exit(0 if all(checks) else 1)
