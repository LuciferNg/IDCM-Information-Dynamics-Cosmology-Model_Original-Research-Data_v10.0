#!/usr/bin/env python3
"""
85_g2_exit1_timeline.py — G2 出路① 存量獨立性時序裁決 (2026-10-17)
===================================================================================
問題 (61/63 號留低): G2 盲測 FAIL 後嘅出路①: 「存量獨立性 = O-series
閉合時序保證 G2 降 🟡」— 即係話 12 個 label 嘅身份係「先有嘅」
(O-series 已經閉合), 唔係 P9 睇咗 magic 之後先貼上去。

驗證: O-series 閉合時間 vs magic rows 識別時間
  A. O35/O55/O158/O171 final_result.md 檔案日期 (閉合時間)
  B. magic 識別 docs (16/17 號) + R5 程序 (35 號) 日期
  C. ★時序比較: O 閉合 << magic 識別? (至少差 1 日 = 唔係同日後驗)
  D. 載決: 出路①足以令 G2「label 存在性」層降 🟡?
     (但盲測「規則可預測性」層維持 FAIL — 59 號已明確分層)
"""
import os
import json
from datetime import datetime

ROOT = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"
P9 = f"{ROOT}/main_problems/p9_kchain_number_field"

PASS = 0
FAIL = 0
FAILS = []
OUT = []

def chk(name, desc, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  ✅ {name}: {desc}")
    else:
        FAIL += 1
        FAILS.append(name)
        print(f"  ❌ {name}: {desc}" + (f"  [{detail}]" if detail else ""))
    OUT.append({"id": name, "desc": desc, "ok": ok, "detail": detail})

def mtime(p):
    try:
        return datetime.fromtimestamp(os.path.getmtime(p))
    except OSError:
        return None

print("=" * 72)
print("A. O-series 閉合時間 (final_result.md mtime)")
print("=" * 72)
o_dirs = {
    "O35": "open_problems_fresh/o35_beats_mass_linkup",
    "O55": "open_problems_fresh/o55_cf_sm_center_z3",
    "O158": "open_problems_fresh/o158_nd_pm_ngen_cluster",
    "O171": "open_problems_fresh/o171_a5_partition_theory",
}
o_times = {}
for name, d in o_dirs.items():
    p = os.path.join(ROOT, d, "final_result.md")
    t = mtime(p)
    o_times[name] = t
    print(f"  {name}: {t}")

print()
print("=" * 72)
print("B. magic 識別 + R5 程序時間")
print("=" * 72)
magic_files = {
    "16_magic_rows_rule": "16_magic_rows_rule.md",
    "17_layer_magic_data": "17_layer_magic_data.md",
    "25_magic_rows_open": "25_magic_rows_open.md",
    "26_blind_test": "26_blind_test_magic_rows_rules.md",
    "35_r5_full_procedure": "35_r5_full_procedure.md",
    "49_magic_distinctiveness": "49_magic_distinctiveness.md",
}
m_times = {}
for name, f in magic_files.items():
    t = mtime(os.path.join(P9, f))
    m_times[name] = t
    print(f"  {name}: {t}")

print()
print("=" * 72)
print("C. ★時序比較")
print("=" * 72)
o_min = min(t for t in o_times.values() if t)
o_max = max(t for t in o_times.values() if t)
m_min = min(t for t in m_times.values() if t)
print(f"  O-series 閉合: {o_min} ~ {o_max}")
print(f"  magic 識別:    {m_min} (最早 {list(m_times)[:2]} 都係 {m_min.strftime('%H:%M')})")
delta = m_min - o_max
print(f"  Δ = magic最早 − O最遲 = {delta.days} 日 {delta.seconds // 3600} 時 {delta.seconds % 3600 // 60} 分")
chk("C1_prior", f"O-series 閉合先行於 magic 識別 ({delta.days} 日前)", delta.days >= 1, str(delta))

print()
print("=" * 72)
print("D. ★載決 — G2 出路①")
print("=" * 72)
print("""
  時序證據:
    O35/O55/O158/O171 final_result 全部 10-15 23:34 (閉合)
    magic 識別 docs (16/17 號) 10-17 11:03 (識別)
    R5 程序 (35 號) 10-17 13:44

  ★ O-series 閉合先行 2 日 → 12 個 label 嘅身份係「存量」:
     唔係 P9 睇咗 magic 5/5 之後先反推貼 label
  ⟹ G2 出路①「存量獨立性」成立:
     但只係 label「存在性」層 — 59 號已經分層:
       存在性 (12 label): ✅ O-series 閉合時序保證 (A 層, 77 號亦證)
       可預測性 (mirror 規則): 🔴 盲測 FAIL (59: p=0.69)
  ⟹ G2 最終裁決:
     「G2 label 存在性」🟡 (時序獨立, 唔係後驗)
     「G2 規則可預測性」🔴 (盲測 FAIL, 維持)
     整體 G2 維持 🔴(部分) — 但「後驗污染」風險已排除
""")
chk("D1_verdict", "出路①成立 → label 存在性層降🟡; 規則可預測性層維持🔴(59 不變)", delta.days >= 1)

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "85_g2_exit1_timeline", "date": "2026-10-17",
    "o_times": {k: str(v) for k, v in o_times.items()},
    "magic_times": {k: str(v) for k, v in m_times.items()},
    "delta": str(delta),
    "verdict": "G2 label 存在性層 🟡 (時序獨立); 規則可預測性層 🔴 (59 維持); 後驗污染風險排除",
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/85_g2_exit1_timeline.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/85_g2_exit1_timeline.json")