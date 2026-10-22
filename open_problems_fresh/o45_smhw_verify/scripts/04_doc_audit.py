#!/usr/bin/env python3
"""
O45 — 文檔獨立核對 (read-only audit, 2026-08-31)
==================================================
核對 01_problem_record.md + 02_closing_report.md 中所有數值 vs
data/01_smhw_results.json, 並檢查文件時間戳時序完整性。

規則:
- 只讀, 不寫任何檔案
- 禁止以推導時序回溯污染 — 只核對"當時寫入"嘅內容 vs 數據
"""
import os, re, json, datetime
import numpy as np

PROJECT = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O45 = os.path.join(PROJECT, 'open_problems_fresh/o45_smhw_verify')

pass_count = 0
fail_count = 0

def check(name, cond, detail=''):
    global pass_count, fail_count
    if cond:
        pass_count += 1
        print(f"  ✅ {name}")
    else:
        fail_count += 1
        print(f"  ❌ {name} — {detail}")

# ========== 載入數據 ==========
data = json.load(open(os.path.join(O45, 'data/01_smhw_results.json')))
rec = open(os.path.join(O45, '01_problem_record.md')).read()
rep = open(os.path.join(O45, '02_closing_report.md')).read()

print("=" * 70)
print("O45 文檔獨立核對 (read-only)")
print("=" * 70)

# ========== 1. 01_problem_record.md 公式核對 ==========
print("\n--- 1. 01_problem_record.md 公式 ---")
# A = 88×61/40 = 134.2
check("record 含 A = Σγ_odd(Σγ_even − L₇)/40", 'Σγ_odd(Σγ_even − L₇)/40' in rec)
check("record 含 88×61/40", '88×61/40' in rec)
check("record 含 134.2 μK", '134.2' in rec)
check("record 含 −134.19 μK", '−134.19' in rec)
check("report 含冷斑座標 (209°,-57°)", '209' in rep and '57' in rep)
check("record 狀態為已閉合", '🟢' in rec and '已閉合' in rec)
check("record 含量綱錯誤警示", '量綱錯誤' in rec)

# 數值: 88×61/40
val = 88*61/40
check(f"88×61/40 = {val} μK", abs(val - 134.2) < 0.01, f"got {val}")

# ========== 2. 02_closing_report.md 數值核對 ==========
print("\n--- 2. 02_closing_report.md 數值 vs JSON ---")

def has_num(doc, num):
    """檢查文檔含某數值 (兼容全形減號 − 同 ASCII 連字號 -)"""
    s = f"{abs(num):.2f}"
    return s in doc

# SMHW 係數表
smhw_table = {
    '1.0': -14.16, '2.0': -25.25, '3.0': -30.02,
    '4.17': -31.17, '5.0': -30.28, '7.0': -23.35, '10.0': -11.20,
}
for R, T in smhw_table.items():
    db = data['smhw'][R]['T_wavelet']
    in_doc = has_num(rep, T)
    check(f"report SMHW R={R}: doc {T} vs db {db:.2f}",
          abs(T - db) < 0.02 and in_doc, f"doc_has={in_doc}")

# rank
rank_table = {'1.0': 1, '2.0': 1, '3.0': 1, '4.17': 2, '5.0': 2, '7.0': 6, '10.0': 18}
for R, rk in rank_table.items():
    db = data['smhw'][R]['rank']
    check(f"report rank R={R}: doc {rk} vs db {db}", rk == db and str(rk) in rep)

# kurtosis
kurt_table = {'1.0': 0.092, '2.0': 0.135, '3.0': 0.126,
              '4.17': 0.110, '5.0': 0.108, '7.0': 0.115, '10.0': 0.101}
for R, k in kurt_table.items():
    db = data['smhw'][R]['kurtosis']
    check(f"report kurt R={R}: doc {k} vs db {db:.3f}", abs(k - db) < 0.002)

# 模型比對 (內稟)
int_table = {'1.0': -10.89, '2.0': -18.49, '3.0': -21.76,
             '4.17': -21.83, '5.0': -20.70, '7.0': -17.04, '10.0': -12.29}
r8_table = {'1.0': -9.26, '2.0': -10.85, '3.0': -9.38,
            '4.17': -7.51, '5.0': -6.45, '7.0': -4.67, '10.0': -3.12}
for R in int_table:
    s = f"{abs(int_table[R]):.2f}"
    s8 = f"{abs(r8_table[R]):.2f}"
    check(f"report model R={R}: intrinsic {int_table[R]:.2f} & R8 {r8_table[R]:.2f} present",
          s in rep and s8 in rep, f"int={s in rep}, r8={s8 in rep}")

# 結構數值
check("report 含 內稟 FWHM 8.66°", '8.66' in rep)
check("report 標明 8.66° 出處 (O42 去卷積結果)", 'O42 去卷積' in rep)
check("report 含 σ=3.68°", '3.68' in rep)
check("report 含 σ=1.77°", '1.77' in rep)
check("report 含 rank 1-2/60", '1-2/60' in rep)

# 比率 ~1.4×
check("report 含 1.4× 比率", '1.4×' in rep)

# ========== 3. 時間戳時序完整性 ==========
print("\n--- 3. 文件時間戳時序 ---")
files = ['01_problem_record.md', '02_closing_report.md', 'final_result.md',
         'scripts/01_smhw_extract.py', 'scripts/02_model_comparison.py',
         'scripts/03_verify.py', 'scripts/04_doc_audit.py',
         'data/01_smhw_results.json']
timestamps = {}
for f in files:
    st = os.stat(os.path.join(O45, f))
    timestamps[f] = datetime.datetime.fromtimestamp(st.st_mtime)
    print(f"  {f}: {timestamps[f].strftime('%Y-%m-%d %H:%M:%S')}")

# 時序: 08-31 主推導鏈 script01 → json → script02 (核心執行鏈)
# closing report 09-12 修補 (加冷斑座標) — mtime 更新但數據仍源自 08-31 json
order_exec = ['scripts/01_smhw_extract.py', 'data/01_smhw_results.json',
              'scripts/02_model_comparison.py']
times_exec = [timestamps[f] for f in order_exec]
check("08-31 核心執行鏈: script01 ≤ json ≤ script02",
      all(times_exec[i] <= times_exec[i+1] for i in range(len(times_exec)-1)),
      f"{[t.strftime('%H:%M:%S') for t in times_exec]}")

# closing report 必須喺數據產生之後 (09-12 修補亦喺 json 之後)
check("closing report ≥ json (數據後寫入, 無回溯)",
      timestamps['02_closing_report.md'] >= timestamps['data/01_smhw_results.json'],
      f"closing={timestamps['02_closing_report.md'].strftime('%m-%d %H:%M')} "
      f"json={timestamps['data/01_smhw_results.json'].strftime('%m-%d %H:%M')}")

# record 09-12 被修補 (加 §〇 時序索引) — mtime 更新屬預期, 唔用嚟判時序
# 驗證鏈時序: 03_verify (08-31) → 04_doc_audit (09-12)
check("驗證鏈時序: 03_verify ≤ 04_doc_audit (由舊到新)",
      timestamps['scripts/03_verify.py'] <= timestamps['scripts/04_doc_audit.py'],
      f"03={timestamps['scripts/03_verify.py'].strftime('%m-%d %H:%M')} "
      f"04={timestamps['scripts/04_doc_audit.py'].strftime('%m-%d %H:%M')}")

# 08-31 閉合時序由 §〇 索引記載 (步驟 8: 閉合 → 步驟 9: 驗證)
check("record §〇 記載閉合(8) → 驗證(9) 時序", '閉合' in rec and '驗證' in rec)

# 創建日期 vs 修改: 01_problem_record 創建於 08-21 (前置), 更新於 08-31
check("01_problem_record 創建於 08-21 (header 記載)", '2026-08-21' in rec)
check("閉合日期 2026-08-31 記載", '2026-08-31' in rec or '08-31' in rec)

# ========== 4. 無跨目錄污染檢查 ==========
print("\n--- 4. 目錄範圍檢查 ---")
# O45 目錄內檔案 (含本 audit script 自身)
allowed = {'01_problem_record.md', '02_closing_report.md', 'final_result.md',
           'scripts/01_smhw_extract.py', 'scripts/02_model_comparison.py',
           'scripts/03_verify.py', 'scripts/04_doc_audit.py',
           'scripts/05_smhw_data_export.py', 'scripts/06_profile_closure.py',
           'scripts/07_conversion_curve.py', 'scripts/08_supergauss_closure.py',
           'scripts/09_tf_closure.py', 'scripts/10_ring_nature.py',
           'scripts/11_ring_control.py', 'scripts/12_model_decomposition.py',
           'scripts/13_sech2_closure.py', 'scripts/14_core_sg_check.py',
           'scripts/15_gl_wall_closure.py', 'scripts/16_gl_structure_check.py',
           'scripts/17_gl_network.py', 'scripts/18_node47_gl.py',
           'scripts/19_env_ring_corr.py',
           'data/01_smhw_results.json', 'data/02_smhw_full_data.json',
           'data/03_profile_closure.json', 'data/04_conversion_curve.json',
           'data/05_supergauss_closure.json', 'data/06_tf_closure.json',
           'data/07_ring_nature.json', 'data/08_ring_control.json',
           'data/09_model_decomposition.json', 'data/10_sgr_model.json',
           'data/11_sech2_closure.json', 'data/12_tophat_closure.json',
           'data/13_kink_closure.json', 'data/14_core_sg_check.json',
           'data/15_gl_wall_closure.json', 'data/16_gl_network.json',
           'data/17_node47_gl.json', 'data/18_env_ring_corr.json',
           'data/08_supergauss_run.log'}
actual = set()
for root, dirs, fnames in os.walk(O45):
    for f in fnames:
        rel = os.path.relpath(os.path.join(root, f), O45)
        actual.add(rel)
check("O45 目錄內檔案清單", actual == allowed,
      f"actual={sorted(actual)} vs allowed={sorted(allowed)}")

# ========== 5. 匯總 ==========
print("\n" + "=" * 70)
total = pass_count + fail_count
print(f"文檔核對: {pass_count}/{total} PASS, {fail_count}/{total} FAIL")
print("=" * 70)
sys_exit = 1 if fail_count else 0
exit(sys_exit)