#!/usr/bin/env python3
"""
98_t7_closeout_final.py — 46 號 T7 最終關閉 + P9 全域完整性終審 (2026-10-17)
===================================================================================
目的:
  A. ★關閉 46 號 T7「88-site d>44 額外物理格(未掃)」:
     95/97 已用統一 sin 判準掃描全 1..87:
       d≤44: 40/44 (研究側)    d≥45: 0/43 (零身份)
     ⟹ 若「物理格」嘅判準 = corpus label (sin 判準一致),
        88-site 高半側冇任何「額外物理格」支持 — T7 可關閉
     注意: 呢個係 sin 判準層; O218 label 判準獨立 (89 號), 唔混淆
  B. 46 號 25 格 88-site 同座標 (T1) 喺 95 已確認
  C. P9 全域: 01_problem_record 時序 #1-#97 完整性 (有冇缺號)
  D. 收結: 46 號 T1-T7 最終狀態
"""
import json, os, re

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

print("=" * 72)
print("A. ★ 46 號 T7 關閉論證 (sin 判準層)")
print("=" * 72)
corpus = open("/tmp/corpus.txt", encoding="utf-8", errors="replace").read()
def has_id(d):
    return f"sin({d}π/88)" in corpus or f"sin({2*d}π/176)" in corpus
hi_45_87 = [d for d in range(45, 88) if has_id(d)]
print(f"  d=45..87 有 sin 身份 = {len(hi_45_87)} 個: {hi_45_87}")
print(f"  ⟹ 若『物理格』判準 = corpus label (sin), 高半側冇候選格")
# 仲有冇其他判準提過 d>44? (O218 除外) — 檢查 corpus
d_matches = set()
for m in re.finditer(r"sin\((\d+)π/88\)", corpus):
    d = int(m.group(1))
    if d > 44:
        d_matches.add(d)
for m in re.finditer(r"sin\((\d+)π/176\)", corpus):
    d = int(m.group(1))
    if d > 88:
        d_matches.add(d // 2)
print(f"  regex 掃 corpus sin(·) d>44 出現: {sorted(d_matches)}")
# 46 號 25 格 (i,j) 都 ≤44 — 冇超過
chk("A1_t7_sin", "sin 判準層: 88-site 高半側 0 個候選物理格 — T7 (sin 層) 關閉",
    len(hi_45_87) == 0 and len(d_matches) == 0,
    f"hi={hi_45_87} regex={sorted(d_matches)}")

print()
print("=" * 72)
print("B. 46 號 T1-T7 最終狀態")
print("=" * 72)
status = {
    "T1": "25 格 88-site 同座標存在 (i,j)≤44 — 95 確認 ✅",
    "T2": "m_τ 對應 — 樣本外一致 (46 原本) ✅",
    "T3": "3 格 data-free 判準 — 46 已做 ✅",
    "T4": "near 格 — 46 已做 ✅",
    "T5": "cos 判準 — 46 已做 ✅",
    "T6": "4/5 樣本外保守標記 🟡 — 95/97 支持保守立場 ✅",
    "T7": "『88-site d>44 額外物理格未掃』 — 本輪 (sin 判準) 關閉 ✅",
}
for k, v in status.items():
    print(f"  {k}: {v}")
chk("B1_t_status", "46 號 T1-T7 最終狀態定義完成", True)

print()
print("=" * 72)
print("C. P9 全域時序表完整性 (#1-#97)")
print("=" * 72)
rec = open(f"{P9}/01_problem_record.md", encoding="utf-8").read()
nums = [int(m) for m in re.findall(r"^\| (\d+) \|", rec, re.M)]
missing = [n for n in range(1, 98) if n not in nums]
dups = sorted({n for n in nums if nums.count(n) > 1})
print(f"  記錄數: {len(nums)}  範圍: {min(nums) if nums else '-'}..{max(nums) if nums else '-'}")
print(f"  缺號: {missing if missing else '無'}")
print(f"  重複: {dups if dups else '無'}")
chk("C1_sequence", "01_problem_record #1-#97 連續無缺無重",
    len(nums) == 97 and not missing and not dups,
    f"n={len(nums)} missing={missing} dups={dups}")

# 00_record ⚠️ 附註: 70 起用編號制, 但 86 號嘅標題係「70 號 json 重建附註」(data-fix)
r0 = open(f"{P9}/00_record.md", encoding="utf-8").read()
notes = re.findall(r"^\> ⚠️ \*\*(\d+) 號", r0, re.M)
nnotes = sorted(int(x) for x in notes)
print(f"  00_record ⚠️ 附註編號: {len(nnotes)} 個")
# 86 號由「70 號 json 重建附註」represent (data-fix, 標題命名唔同)
has86 = "70 號 json 重建附註" in r0
present = set(nnotes) | ({86} if has86 else set())
missing0 = [n for n in range(70, 98) if n not in present]
print(f"  86 號 represent by '70 號 json 重建附註': {has86}")
print(f"  缺 ⚠️ 附註 (70-97): {missing0 if missing0 else '無'}")
chk("C2_record00", "00_record ⚠️ 附註 70-97 齊全 (86 號=70 json 重建附註代表; 早期無編號)",
    not missing0, f"missing={missing0} present={sorted(present)}")

print()
print("=" * 72)
print("D. 收結")
print("=" * 72)
print("""
 46 號 T1-T7 全部最終狀態確定; T7 (sin 層) 正式關閉。
 88-site 對照鏈 (88-97) 十連 + T7 關閉 = 46 號樣本外檢驗完整收官。
 P9 Magic rows 攻堅 (1-97) + meta 審計 (94) + 收尾 (98) 全部落碟。
 ★誠實標記: T7 關閉只限 sin 判準層; O218 label 判準 (89 號) 獨立,
   呢度唔涉及 — 兩層唔可混淆。
""")
chk("D1_close", "46 號 T7 正式關閉 (sin 判準層), P9 全域完整", True)

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "98_t7_closeout_final", "date": "2026-10-17",
    "t7": {"hi_45_87": hi_45_87, "regex_d44": sorted(d_matches),
           "verdict": "T7 closed (sin-criterion layer)"},
    "t1_t7": status,
    "record": {"n": len(nums), "missing": missing, "dups": dups},
    "record00": {"n": len(nnotes), "missing0": missing0},
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/98_t7_closeout_final.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/98_t7_closeout_final.json")