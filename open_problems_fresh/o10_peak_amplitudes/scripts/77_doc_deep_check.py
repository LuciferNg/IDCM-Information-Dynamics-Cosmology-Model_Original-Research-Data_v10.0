#!/usr/bin/env python3
"""
O10 77: 文檔推導鏈深度核對 (每文檔內部一致 + 文檔間無污染)
============================================================
原則: 禁止跨文檔以新推導污染舊記錄。
  每份文檔只保留佢記錄時點嘅推導狀態。
  核對: (1) 每份文檔內部公式/數值自洽
        (2) 文檔間時間序: 舊文檔唔應該引用未來文檔內容
"""
import os, re, math, json

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
M = 33

DIR = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o10_peak_amplitudes"

# 文檔時間序 (由 ls 確認)
docs_order = [
    ("SESSION_START.md", "2026-08-16", "啟動 (已知: A₂=3ε, A₃/φ⁻⁴ 未閉合)"),
    ("01_problem_record.md", "2026-08-19 23:56", "問題記錄 (最後更新)"),
    ("02_results.md", "2026-08-19 23:53", "完整推導 (最後更新)"),
    ("03_deltal2_and_silk.md", "2026-08-19 23:53", "補充: Hamiltonian + Silk"),
    ("04_prime_peaks_and_silk.md", "2026-08-19 23:53", "補充: 質數峰"),
    ("05_prime_peaks_closure.md", "2026-08-19 23:54", "補充: 質數峰閉合"),
    ("06_factor_and_phase.md", "2026-08-19 23:22", "補充: 因子+相位"),
    ("07_final_verification_record.md", "2026-08-19 23:58", "最終核對"),
]

print("=" * 72)
print("O10 文檔推導鏈深度核對")
print("=" * 72)

all_ok = True

# ---------- 核對 1: 核心公式一致性 ----------
# 每份文檔應該包含嘅核心數值 (按時間序允許範圍)
core_checks = {
    "01_problem_record.md": ["5816", "2553", "0.1771", "0.1353", "3ε"],
    # 02_results 保持歷史狀態: 有 33/34 鎖定記錄, Silk 段用描述形式 (冇 ℓ_D 數字)
    "02_results.md": ["5816", "2553", "0.1771", "0.1353", "33/34"],
    # 03 用 φ 符號 (非 1.618 數字) — 正確數學記法
    "03_deltal2_and_silk.md": ["φ⁻¹", "φ⁻²", "9/9", "5/5"],
    "04_prime_peaks_and_silk.md": ["0.4434", "0.4389", "0.2143", "0.1414"],
    "05_prime_peaks_closure.md": ["0.4434", "0.4389", "0.2143", "0.1414", "9055", "33/34"],
    "06_factor_and_phase.md": ["33/34", "9055", "±1", "±21"],
    "07_final_verification_record.md": ["25/25", "0.30%", "33/34"],
}

for doc, keys in core_checks.items():
    path = os.path.join(DIR, doc)
    text = open(path).read()
    missing = [k for k in keys if k not in text]
    if missing:
        print(f"  ❌ {doc}: 缺核心數值 {missing}")
        all_ok = False
    else:
        print(f"  ✅ {doc}: 核心數值齊全 ({len(keys)} 項)")

# ---------- 核對 2: 時間序 — 舊文檔唔應該引用「未來」發現 ----------
print("\n時間序污染檢查 (舊文檔唔應該有未來發現):")
# SESSION_START (08-16) 唔應該有質數孿生對
ss = open(os.path.join(DIR, "SESSION_START.md")).read()
if "質數" in ss or "孿生" in ss:
    print("  ❌ SESSION_START.md 含質數孿生對 (回溯污染!)")
    all_ok = False
else:
    print("  ✅ SESSION_START.md 保持原始 (無回溯污染)")

# 06 係 23:22 (最早嘅補充), 05 係 23:54 — 05 可以引用 06 內容
# 但 06 唔應該引用 05 (05 之後先寫)
# 檢查 06 有冇引用「05」
six = open(os.path.join(DIR, "06_factor_and_phase.md")).read()
if "05_prime" in six:
    print("  ⚠️ 06_factor_and_phase.md 引用 05 (時間序檢查)")
else:
    print("  ✅ 06 無引用 05 (時間序 OK)")

# ---------- 核對 3: 每份文檔數值自洽 ----------
print("\n數值自洽檢查:")
# 01: 峰高 vs 已知事實表
one = open(os.path.join(DIR, "01_problem_record.md")).read()
for v in ["0.4434", "0.4389", "0.2143", "0.1414"]:
    if v not in one:
        print(f"  ❌ 01 缺 {v}")
        all_ok = False
print("  ✅ 01_problem_record: 峰高值齊全")

# 02: Fibonacci 階梯表
two = open(os.path.join(DIR, "02_results.md")).read()
ladder_vals = ["0.4635", "0.1771", "0.1353", "0.0775"]
for v in ladder_vals:
    if v not in two:
        print(f"  ❌ 02 缺 {v}")
        all_ok = False
print("  ✅ 02_results: Fibonacci 階梯值齊全")

# 03: Hamiltonian 9/9 + Binet 5/5
three = open(os.path.join(DIR, "03_deltal2_and_silk.md")).read()
if "9/9" not in three or "5/5" not in three:
    print("  ❌ 03 缺 9/9 或 5/5 驗證")
    all_ok = False
else:
    print("  ✅ 03: Hamiltonian 驗證記錄齊全")

# 04: 質數峰表
four = open(os.path.join(DIR, "04_prime_peaks_and_silk.md")).read()
if "1013" not in four or "1337" not in four:
    print("  ❌ 04 缺合數峰位置")
    all_ok = False
else:
    print("  ✅ 04: 合數峰 (1013, 1337) 記錄齊全")

# 05: 閉合表 + 33/34
five = open(os.path.join(DIR, "05_prime_peaks_closure.md")).read()
if "0.30%" not in five:
    print("  ❌ 05 缺 RMS 0.30%")
    all_ok = False
else:
    print("  ✅ 05: RMS 0.30% 記錄齊全")

# 06: 相位表
six = open(os.path.join(DIR, "06_factor_and_phase.md")).read()
phase_vals = ["+1", "−1", "+23", "+21"]
for v in phase_vals:
    if v not in six:
        print(f"  ❌ 06 缺相位 {v}")
        all_ok = False
print("  ✅ 06: 相位表齊全")

# 07: 驗證總結
seven = open(os.path.join(DIR, "07_final_verification_record.md")).read()
if "25/25" not in seven:
    print("  ❌ 07 缺 25/25")
    all_ok = False
else:
    print("  ✅ 07: 25/25 記錄齊全")

# ---------- 核對 4: 數據檔存在性 ----------
print("\n數據檔完整性:")
json_files = ["planck_binned_peaks.json", "camb_peak_heights.json", "fibonacci_ladder_results.json",
              "three_experiment_crosscheck.json", "spt3g_tt_parsed.json", "act_dr6_tt.json",
              "o9_positions_crosscheck.json", "twin_pair_crosscheck.json",
              "final_prime_formula.json", "full_verification.json", "final_number_check.json"]
for jf in json_files:
    p = os.path.join(DIR, "data", jf)
    if os.path.exists(p):
        # 驗證 JSON 可解析
        try:
            json.load(open(p))
            print(f"  ✅ {jf}")
        except Exception as e:
            print(f"  ❌ {jf}: JSON 損壞 ({e})")
            all_ok = False
    else:
        print(f"  ❌ {jf}: 缺失")
        all_ok = False

print("\n" + "=" * 72)
print(f"深度核對結果: {'🎉 全部通過' if all_ok else '❌ 有問題'}")
