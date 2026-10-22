#!/usr/bin/env python3
"""O38 開放問題 + 時序索引完整性檢查"""
import os, re

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o38_kappa_prediction"
os.chdir(BASE)

print("=" * 72)
print("  O38 開放問題 + 時序索引檢查")
print("=" * 72)
checks = []

# ═══ 1. SESSION_START 開放問題 ═══
sess = open("SESSION_START.md").read()
print("\n─── SESSION_START 開放問題 ───")
# 搵 🔴 / 🟡 標記
open_items = re.findall(r"🔴|🟡", sess)
print(f"  🔴/🟡 標記數: {len(open_items)}")
# 遺留開放問題 table
if "44-tone 同步嚴格動力學證明" in sess:
    print(f"  ✅ 44-tone 同步證明 🔴 已記錄")
# 裁決回覆存在
print(f"  裁決回覆 section: {'✅' if '⚠️ 裁決回覆' in sess else '❌'}")
checks.append("⚠️ 裁決回覆" in sess)

# ═══ 2. 01_problem_record 開放問題 ═══
rec = open("01_problem_record.md").read()
print("\n─── 01_problem_record 開放問題 ───")
# 誠實標記 table
open_rec = re.findall(r"🔴", rec)
print(f"  🔴 標記數: {len(open_rec)}")
for line in rec.splitlines():
    if "🔴" in line and "|" in line:
        print(f"    {line.strip()[:90]}")

# ═══ 3. final_result 開放問題 ═══
fr = open("final_result.md").read()
print("\n─── final_result 開放問題 ───")
open_fr = re.findall(r"🔴", fr)
print(f"  🔴 標記數: {len(open_fr)}")
for line in fr.splitlines():
    if "🔴" in line:
        print(f"    {line.strip()[:90]}")

# ═══ 4. 時序索引完整性 (01_problem_record) ═══
print("\n─── 時序索引完整性 ───")
if "推導時序索引" in rec:
    print("  ✅ 時序索引存在")
    # 搵 scripts 引用
    scripts_in_idx = re.findall(r"scripts/(0\d)_", rec)
    print(f"  scripts 引用: {sorted(set(scripts_in_idx))}")
    checks.append(len(scripts_in_idx) > 0)
else:
    print("  ❌ 時序索引唔存在")
    checks.append(False)

# ═══ 5. 所有 scripts 有冇記錄 ═══
print("\n─── scripts 完整性 ───")
py_scripts = sorted(os.listdir("scripts"))
py_scripts = [s for s in py_scripts if s.endswith(".py")]
print(f"  scripts 數: {len(py_scripts)}")
for s in py_scripts:
    in_rec = s in rec
    in_sess = s in sess
    print(f"    {'✅' if in_rec else '❌'} {s} (rec={'✓' if in_rec else '✗'}, sess={'✓' if in_sess else '✗'})")

print(f"\n{'='*72}")
print(f"  檢查完成: {sum(checks)}/{len(checks)} 核心項")
print("=" * 72)
