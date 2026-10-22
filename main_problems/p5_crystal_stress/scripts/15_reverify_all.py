#!/usr/bin/env python3
"""
重驗主控 — 一鍵跑晒所有重驗劇本 (10-14 + 02) 並彙總裁決
======================================================
crystal_stress 重驗 (2026-09-27): 在 IDCM v10.0 框架下重新驗證舊公式有效性。
舊 scripts/00/01 保持不變 (只作歷史); 本系列為新劇本。
"""
import os, subprocess, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
CS = os.path.dirname(HERE)
SCRIPTS = [
    ("02_o169_correction_reverify.py", "O169 伸長律修正點 (#17)"),
    ("10_reverify_energy.py",          "UHECR 能量尺度 (01 §2.1-2.4)"),
    ("11_reverify_anisotropy.py",      "Auger 各向異性 (01 §2.5)"),
    ("12_reverify_cluster_vacuum.py",  "星系團節點真空 (01 §2.6)"),
    ("13_reverify_lrd_spectral.py",    "譜結構 + LRD 標度 (04)"),
    ("14_reverify_predictions.py",     "偏振/GRB/盲測 (03 §7)"),
    ("16_reverify_doc_consistency.py", "文檔一致性 (docs/)"),
]

print("=" * 82)
print("crystal_stress 重驗主控 — IDCM v10.0 框架")
print("=" * 82)
summary = []
for fn, desc in SCRIPTS:
    path = os.path.join(HERE, fn)
    if not os.path.exists(path):
        print(f"⚠️  缺 {fn}"); continue
    r = subprocess.run([sys.executable, path], capture_output=True, text=True, cwd=CS)
    out = r.stdout
    # 抽結果行
    res = next((l.strip() for l in out.splitlines() if "結果:" in l or "檢查完成" in l), "")
    ok = (r.returncode == 0)
    summary.append((fn, desc, ok, res))
    print(f"  {'✅' if ok else '❌'}  {fn:<34} {res}")

print("\n" + "=" * 82)
npass = sum(1 for *_, ok, _ in summary if ok)
print(f"彙總: {npass}/{len(summary)} 劇本全綠")
for fn, desc, ok, res in summary:
    print(f"  {'PASS' if ok else 'FAIL'}  {desc}")
out = os.path.join(CS, 'data', 'reverify_master.json')
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump({"scripts": [{"file": f, "desc": d, "pass": o, "result": r} for f, d, o, r in summary],
           "n_pass": npass, "n_total": len(summary)}, open(out, 'w'), indent=2, ensure_ascii=False)
print(f"\n已存 {out}")
sys.exit(0 if npass == len(summary) else 1)
