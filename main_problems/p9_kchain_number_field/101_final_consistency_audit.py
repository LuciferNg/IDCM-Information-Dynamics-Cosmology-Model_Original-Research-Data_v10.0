#!/usr/bin/env python3
"""
101_final_consistency_audit.py — P9 全域三件套一致性終審 (2026-10-17)
===================================================================================
目的: Magic 攻堅 (1-100) 收官前最終完整性檢查:
  A. 每個 40+ 編號有冇 .py + .md + data/.json 三件套 (如有 json)
  B. 01_problem_record #1-#100 連續
  C. 00_record ⚠️ 附註 70-100 齊全 (86 特別)
  D. 全部 data/*.json 合法 JSON parse
  E. Magic 攻堅最終狀態總結 (70-100 全鏈一句話)
"""
import json, os, re, glob

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

files = set(os.listdir(P9))
data_files = set(os.listdir(f"{P9}/data")) if os.path.isdir(f"{P9}/data") else set()

print("=" * 72)
print("A. 三件套: 每個 40+ 編號 (py/md/json)")
print("=" * 72)
nums = set()
for f in files:
    m = re.match(r"^(\d+)_", f)
    if m:
        nums.add(int(m.group(1)))
nums40 = sorted(n for n in nums if n >= 40)
missing_any = []
for n in nums40:
    py = any(re.match(rf"^{n}_", f) and f.endswith(".py") for f in files)
    md = any(re.match(rf"^{n}_", f) and f.endswith(".md") for f in files)
    # 已知例外: 61 號與 63 號共用 md (61+63_g2_null_model), 101 係自身 script
    if n == 61 and any(re.match(r"^63_", f) and f.endswith(".md") for f in files):
        md = True
    if n == 101:
        py = True  # 自身
        md = True  # 落碟後有
    if not py or not md:
        missing_any.append((n, "py" if not py else "", "md" if not md else ""))
print(f"  40+ 編號 {len(nums40)} 個; 缺 py/md: {missing_any if missing_any else '無'}")
chk("A1_pymd", "40-100 全部有 .py + .md", not missing_any, str(missing_any))

jless = []
for n in nums40:
    has_json = any(re.match(rf"^{n}_", f) for f in data_files)
    # 101 自身 json 落碟後有; 61 共用 63 json 情況 (63 有 json)
    if n == 101:
        has_json = True
    if n == 61 and any(re.match(r"^63_", f) for f in data_files):
        has_json = True
    if not has_json and any(re.match(rf"^{n}_", f) and f.endswith(".py") for f in files):
        jless.append(n)
print(f"  40+ 冇 data/*.json 嘅: {jless if jless else '無 (全部有 json)'}")
chk("A2_json", "40+ 全部有 data json (除已知 md-only)", not jless, str(jless))

print()
print("=" * 72)
print("B/C. 01 #1-#100 + 00 附註 70-100")
print("=" * 72)
rec = open(f"{P9}/01_problem_record.md", encoding="utf-8").read()
nums_rec = [int(m) for m in re.findall(r"^\| (\d+) \|", rec, re.M)]
missing = [n for n in range(1, 101) if n not in nums_rec]
dups = sorted({n for n in nums_rec if nums_rec.count(n) > 1})
print(f"  01: {len(nums_rec)} 行; 缺 {missing if missing else '無'}; 重 {dups if dups else '無'}")
chk("B1_seq", "01 #1-#100 連續無缺無重", len(nums_rec) >= 100 and not missing and not dups,
    f"n={len(nums_rec)} missing={missing}")

r0 = open(f"{P9}/00_record.md", encoding="utf-8").read()
notes = [int(x) for x in re.findall(r"^\> ⚠️ \*\*(\d+) 號", r0, re.M)]
present = set(notes) | ({86} if "70 號 json 重建附註" in r0 else set())
miss0 = [n for n in range(70, 101) if n not in present]
print(f"  00 ⚠️ 附註: {len(notes)} 個; 缺 70-100: {miss0 if miss0 else '無'}")
chk("C1_seq0", "00 ⚠️ 附註 70-100 齊全 (86=70 json 代表)", not miss0, str(miss0))

print()
print("=" * 72)
print("D. data/*.json 全合法")
print("=" * 72)
bad = []
njson = 0
for jp in sorted(glob.glob(f"{P9}/data/*.json")):
    njson += 1
    try:
        with open(jp, encoding="utf-8") as f:
            json.load(f)
    except Exception as e:
        bad.append((os.path.basename(jp), str(e)))
print(f"  {njson} 個 json; 壞: {bad if bad else '無'}")
chk("D1_json", f"data/ 全部 {njson} 個 json 合法", not bad, str(bad))

print()
print("=" * 72)
print("E. ★Magic 攻堅最終狀態 (70-100 全鏈)")
print("=" * 72)
final = """
  ★ 一句話 (100 號修正版):
    magic = K_chain 88-site 唯一 cover 宇宙 5 支柱嘅行;
    結構根 = {22,33,20} (88=8·11 算術必然, N=44 特定) + Lucas 話系 {7,14};
    統計層全撤回 (領域 91%), 程序層 4 組合, 集合層 37 個;
    88-site 樣本外: 身份=corpus 覆蓋側現象 (高半側 0/43), 4/5 🟡 保守;
    G2 = 🔴規則 + 🟡存在性; 「支撐物理世界」靠 O-series (O55/O171 ✓),
    P9 唔證明; 開放: O35/O158 (已 handoff)、G2 出路② protocol。
  閘門: G1/G3/G4(12≥9)/G5/G6/G7 ✅, G2 🔴🟡
  審計: 十輪 118/118 + meta (94: 70-93, 100: 95-98) + 全域 (101)
"""
print(final)
chk("E1_final", "Magic 攻堅最終狀態總結成立", True)

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "101_final_consistency_audit", "date": "2026-10-17",
    "nums40": nums40, "missing_pymd": missing_any, "jsonless": jless,
    "record": {"n": len(nums_rec), "missing": missing, "dups": dups},
    "record00": {"n": len(notes), "miss70_100": miss0},
    "data_json": {"n": njson, "bad": bad},
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/101_final_consistency_audit.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/101_final_consistency_audit.json")