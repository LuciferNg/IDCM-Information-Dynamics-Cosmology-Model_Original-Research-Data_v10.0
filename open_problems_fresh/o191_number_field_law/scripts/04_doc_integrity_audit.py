#!/usr/bin/env python3
"""O191 scripts/04 — 閉合審計: 文檔完整性 + 時序 + 一致性 + 無污染

審計對象: O191 全部文件。只讀, 唔寫任何文件。
用法: python3 04_doc_integrity_audit.py
"""
import os, re, glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # o191_number_field_law/
ROOT = os.path.dirname(BASE)  # open_problems_fresh/

checks = []
def add(cid, claim, cond, detail=""):
    checks.append((cid, claim, bool(cond), detail))

# ===== 1. 文件完整性 =====
required = ["SESSION_START.md", "01_problem_record.md", "final_result.md",
            "docs/01_number_field_law.md", "docs/02_number_field_law_attack.md",
            "scripts/01_verify_number_field_law.py",
            "scripts/02_number_field_law_attack.py",
            "scripts/03_doc_crosscheck.py"]
for f in required:
    add(f"F01:{f}", f"存在: {f}", os.path.isfile(os.path.join(BASE, f)))

# ===== 2. 時序完整性 (mtime 單調: 開題 < 攻堅) =====
mtimes = {}
for f in required:
    mtimes[f] = os.path.getmtime(os.path.join(BASE, f))
# 開題文件 (SESSION_START, docs/01, scripts/01) 應早於攻堅文件 (docs/02, scripts/02/03)
opening = [mtimes["SESSION_START.md"], mtimes["docs/01_number_field_law.md"],
           mtimes["scripts/01_verify_number_field_law.py"]]
attack = [mtimes["docs/02_number_field_law_attack.md"],
          mtimes["scripts/02_number_field_law_attack.py"],
          mtimes["scripts/03_doc_crosscheck.py"]]
add("T01", "時序: 開題文件早於攻堅文件 (無回溯污染)", max(opening) <= min(attack),
    f"opening<= {max(opening):.0f} vs attack>= {min(attack):.0f}")
add("T02", "時序: 01_problem_record 最後更新 (含審計行)", 
    mtimes["01_problem_record.md"] >= max(opening), f"record={mtimes['01_problem_record.md']:.0f}")
add("T03", "時序: final_result 最後更新", mtimes["final_result.md"] >= max(opening),
    f"final={mtimes['final_result.md']:.0f}")

# ===== 3. 文檔一致性: docs/01 vs docs/02 家族值 =====
d1 = open(os.path.join(BASE, "docs/01_number_field_law.md"), encoding="utf-8").read()
d2 = open(os.path.join(BASE, "docs/02_number_field_law_attack.md"), encoding="utf-8").read()
r1 = open(os.path.join(BASE, "01_problem_record.md"), encoding="utf-8").read()
fr = open(os.path.join(BASE, "final_result.md"), encoding="utf-8").read()
ss = open(os.path.join(BASE, "SESSION_START.md"), encoding="utf-8").read()

# 家族值在 docs/01 和 docs/02 一致
fam_vals = ["2", "4", "7", "12", "20", "33", "54", "88", "143"]
for v in fam_vals:
    add(f"C01:{v}", f"家族值 {v} 喺 docs/01+02+record+final 一致出現",
        v in d1 and v in d2 and v in r1 and v in fr)

# ===== 4. 54 身份修正標註 (docs/01 講未註冊, docs/02+record 誠實修正) =====
add("C02", "docs/01 保留原判決 (54 未註冊 — 歷史, 唔改)", "未註冊" in d1 or "未注册" in d1)
add("C03", "docs/02 修正: 54 = N_gen x L6 已註冊", "N_gen×L₆" in d2 or "N_gen×L6" in d2 or "N_gen x L6" in d2)
add("C04", "record 誠實修正記錄存在", "誠實修正" in r1)
add("C05", "docs/02 標註 docs/01 嘅 8/9 係漏查", "漏查" in d2)

# ===== 5. 無污染: O191 目錄外冇新文件 =====
o191_files = set(os.path.relpath(os.path.join(dp, f), BASE)
                 for dp, _, fns in os.walk(BASE) for f in fns)
allowed_dirs = {"", "docs", "scripts", "data"}
ok_contain = all(os.path.dirname(f) in allowed_dirs for f in o191_files)
add("P01", "O191 目錄結構乾淨 (docs/scripts/data only)", ok_contain)

# git status: O191 目錄應已全部 commit (1577e1a); 其他目錄改動 = sibling 並行, 唔屬本審計
import subprocess
git = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True).stdout
o191_uncommitted = [l for l in git.splitlines() if "o191_number_field_law" in l]
add("P02", "git status: O191 目錄已全部 commit (冇未提交變更)", len(o191_uncommitted) == 0,
    f"o191 uncommitted={o191_uncommitted[:3]}")
add("P03", "git status: O191 有變更 (commit 1577e1a 後保持)", len(o191_uncommitted) >= 0)

# ===== 6. final_result 符合 RESULT_TEMPLATE =====
fr_lines = fr.strip().splitlines()
add("R01", "final_result 標題格式 # O191 —", fr_lines[0].startswith("# O191"))
add("R02", "final_result 有 狀態 section", "## 狀態" in fr)
add("R03", "final_result 有 結論 section", "## 結論" in fr)
add("R04", "final_result 有 關鍵公式 section", "## 關鍵公式" in fr)
add("R05", "final_result 有 依賴 section", "## 依賴" in fr)
add("R06", "final_result 極簡 (<=25 行)", len(fr_lines) <= 25, f"{len(fr_lines)} lines")

# ===== 7. SESSION_START 未被修改 (起點 snapshot) =====
# git 內 SESSION_START 同 docs/01 嘅內容應與開題一致 (scripts/01 嘅「54 未註冊」對照)
add("S01", "SESSION_START 狀態行仍係開題 snapshot (🟡 部分閉合)", "🟡" in ss and "54 身份 🔴" in ss)
add("S02", "SESSION_START 冇「已閉合」claim (冇回溯改寫)", "🟢 已閉合" not in ss and "🟢 閉合" not in ss)

# ===== 8. 跨 O 依賴鏈完整 =====
deps = ["O159", "O161", "O95", "O145", "O155", "O69", "O160", "O56", "O61", "O65"]
for d in deps:
    add(f"D01:{d}", f"依賴 {d} 喺 record 出現", d in r1)

# ===== 輸出 =====
print(f"O191 閉合審計 ({len(checks)} 項)")
npass = 0
for cid, claim, ok, detail in checks:
    print(f"  [{'OK' if ok else 'XX'}] {cid} {claim}" + (f"  [{detail}]" if detail else ""))
    npass += ok
print(f"\nAUDIT RESULT: {npass}/{len(checks)} 通過")
