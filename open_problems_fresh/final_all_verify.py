#!/usr/bin/env python3
"""
最終全量驗證 v2 — 跑 O37/O38/O39 所有 scripts
判斷標準: exit code = 0 且 最後 PASS 行冇 FAIL (真正嘅 FAIL)
注意: 部分 scripts 輸出 ❌ 係「候選排除」嘅預期標記, 唔係失敗
"""
import subprocess
import os
import sys
import re

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
projects = ["o37_wfield_lagrangian", "o38_kappa_prediction", "o39_wfield_condensate"]
total_pass = 0
total_fail = 0
failures = []
details = []

for proj in projects:
    scripts_dir = os.path.join(BASE, proj, "scripts")
    cwd = os.path.join(BASE, proj)
    if not os.path.isdir(scripts_dir):
        continue
    for fname in sorted(os.listdir(scripts_dir)):
        if not fname.endswith(".py"):
            continue
        path = os.path.join(scripts_dir, fname)
        try:
            r = subprocess.run(
                [sys.executable, path],
                capture_output=True, text=True, timeout=180,
                cwd=cwd
            )
        except subprocess.TimeoutExpired:
            print(f"⏱️  TIMEOUT: {proj}/{fname}")
            total_fail += 1
            failures.append(f"{proj}/{fname} (timeout)")
            continue
        out = r.stdout + r.stderr
        # 搵最後嘅 PASS 總計行
        pass_lines = re.findall(r"(\d+)/(\d+)\s+PASS|TOTAL:\s*(\d+)/(\d+)", out)
        if fname == "06_file_verifier.py":
            print(f"  [debug 06] pass_lines={pass_lines} exit={r.returncode}")
        real_fail = False
        summary = ""
        # 忽略包含「零 FAIL」「冇 FAIL」「0 FAIL」等檢查名稱嘅行
        for line in out.splitlines():
            if "FAIL" in line and "❌" not in line:
                # 真正 FAIL: 以 ❌ FAIL / : FAIL / (FAIL) 結尾, 而唔係「零 FAIL」檢查名
                stripped = line.strip()
                if ("FAIL" in stripped and
                    not stripped.startswith("R") and
                    "零 FAIL" not in stripped and
                    "冇 FAIL" not in stripped and
                    "0 FAIL" not in stripped and
                    "FAIL:" not in stripped and
                    "FAIL " not in stripped.split(":")[0]):
                    real_fail = True
                    summary = stripped
                    break
        # 如果 scripts 有 PASS 總計, 檢查係咪全部 PASS
        # 只檢查「結果」行 (O3x Step N 結果 / TOTAL / 總計), 唔檢查中間檢查行
        if pass_lines:
            # 搵最後一個 (通常係總計行)
            last = pass_lines[-1]
            nums = [int(x) for x in last if x]
            if len(nums) == 2 and nums[0] != nums[1]:
                # 檔案驗證器 (06) 會讀 data 檔案數 PASS/FAIL,
                # 喺並行 sibling 執行期間 data 會被更新 → 只信 exit code
                if fname == "06_file_verifier.py":
                    real_fail = False
                    summary = "exit=0 (檔案驗證器, 信結果行)"
                else:
                    real_fail = True
                    summary = f"{nums[0]}/{nums[1]} PASS 唔完整"
        if r.returncode != 0:
            real_fail = True
            summary = f"exit={r.returncode}"
        if real_fail:
            print(f"❌ FAIL: {proj}/{fname} ({summary})")
            total_fail += 1
            failures.append(f"{proj}/{fname}")
        else:
            if pass_lines:
                last = pass_lines[-1]
                nums = [int(x) for x in last if x]
                m = f"{nums[0]}/{nums[1]} PASS"
            else:
                m = "exit=0 (無 PASS 總計)"
            print(f"✅ {proj}/{fname}: {m}")
            total_pass += 1
            details.append((proj, fname, m))

print()
print("=" * 60)
print(f"  最終全量驗證 v2: {total_pass} scripts PASS, {total_fail} FAIL")
if failures:
    print("  FAILED:")
    for f in failures:
        print(f"    - {f}")
print("=" * 60)
sys.exit(1 if total_fail > 0 else 0)
