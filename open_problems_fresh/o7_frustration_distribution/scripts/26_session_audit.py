#!/usr/bin/env python3
"""
O7 — 26_session_audit.py (2026-10-11)
====================================================================
O7/natural-write-closure: 全 session (16-25 scripts, 03-12 docs) 文檔鏈
及結論驗證 audit

  1. 檔案存在性: scripts/16_..25_ 同 docs/03_..12_ 一一對應
  2. 每個 doc 標題行/結論聲稱 vs script 尾行 PASS 數
  3. 重跑全部 scripts (16-25) 對照：聲稱 PASS 數 == 實測 PASS 數
  4. 撤回一致性: docs/06 註明已撤回 (頂部 ⚠️), docs/07 明記 0/3
  5. docs/01 mtime 唔變 (08-19) — 由外部 terminal 驗證
  6. 時序索引完整性: 01_problem_record 含全部 10 個 doc 引用
"""

import re, subprocess, sys
from pathlib import Path

O7 = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o7_frustration_distribution")
SCRIPTS = O7 / "scripts"
DOCS = O7 / "docs"
PY = "/usr/bin/python3"

results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

print("=" * 76)
print("  O7 session audit (scripts 16-25, docs 03-12)")
print("=" * 76)

# ═══ 1. 檔案存在性 + 對應表 ═══
print("\n─── 1. scripts/docs 一覽 ───")
pairs = [
    (16, "natural_write_mechanism", 15, "03_natural_write_mechanism.md"),
    (17, "theta_sky_spectrum", 5, "05_theta_sky_spectrum.md"),
    (18, "three_channel_spectra", 6, "06_three_channel_spectra.md"),
    (19, "channel_structure_tests", 0, "07_channel_structure_tests.md"),
    (20, "a5_ell3_verification_and_klmap", 4, "08_kl_irrep_closure.md"),
    (21, "kl_irrep_subspace_map", 4, "08_kl_irrep_closure.md"),
    (22, "kl_mapping_details_and_88_embedding", 2, "09_kl_mapping_details.md"),
    (23, "a5_group_algebra_labels", 8, "10_a5_group_algebra.md"),
    (24, "seam_type_cross", 6, "11_face_level_frustration.md"),
    (25, "saturated_coloring_family_test", 7, "12_saturated_coloring_family.md"),
]
all_ok = True
for num, name, expect, doc in pairs:
    sp = SCRIPTS / f"{num:02d}_{name}.py"
    dp = DOCS / doc
    ok = sp.exists() and dp.exists()
    all_ok &= ok
    print(f"  s{num:02d} {'✓' if sp.exists() else '✗'} {sp.name[:44]:44s} d{doc[:6]} {'✓' if dp.exists() else '✗'}")
check("1a: scripts 16-25 全存在", all_ok)
check("1b: docs 03-12 (10 個) 全存在", all(dp.exists() for _, _, _, doc in pairs) and len(list(DOCS.glob("*.md"))) >= 12)
print(f"  docs 總數: {len(list(DOCS.glob('*.md')))}")

# ═══ 2-3. 重跑 scripts + PASS 對照 ═══
print("\n─── 2. 重跑 scripts 16-25 (實測 PASS vs 文件聲稱) ───")
for num, name, expect, doc in pairs:
    sp = SCRIPTS / f"{num:02d}_{name}.py"
    r = subprocess.run([PY, str(sp)], capture_output=True, text=True, timeout=550)
    out = r.stdout + r.stderr
    m = re.search(r"結果:\s*(\d+)/(\d+)", out)
    if m:
        got, tot = int(m.group(1)), int(m.group(2))
    else:
        got, tot = -1, -1
    # 文件聲稱 PASS 數 (doc 或 01_problem_record)
    ok = (got == expect)
    print(f"  s{num:02d} {sp.name[:40]:40s} 實測 {got}/{tot}  文件聲稱 {expect}  {'✓' if ok else '✗'}")
    check(f"2-{num:02d}: s{num:02d} PASS 數同聲稱一致", ok, f"{got} vs {expect}")
    if got == -1:
        print(f"    ⚠️ output tail: {out[-300:]}")

# ═══ 4. 撤回一致性 ═══
print("\n─── 3. 撤回/負結果聲稱一致性 ───")
d06 = (DOCS / "06_three_channel_spectra.md").read_text()
d07 = (DOCS / "07_channel_structure_tests.md").read_text()
check("3a: docs/06 頂部有 ⚠️ 更正注明 (撤回)", "撤回" in d06[:600])
check("3b: docs/07 明記 0/3 (撤回事由)", "0/3" in d07 and "撤回" in d07)
print(f"  (docs/07: C7 z=+0.09, C8 z=+0.11, C9 p=0.875 — 見文件內)")

# ═══ 5. 時序索引引用完整性 ═══
print("\n─── 4. 01_problem_record 引用完整性 ───")
rec = (O7 / "01_problem_record.md").read_text()
for doc in ["03_natural_write_mechanism.md", "04_natural_write_theta_audit.md",
            "05_theta_sky_spectrum.md", "06_three_channel_spectra.md",
            "07_channel_structure_tests.md", "08_kl_irrep_closure.md",
            "09_kl_mapping_details.md", "10_a5_group_algebra.md",
            "11_face_level_frustration.md", "12_saturated_coloring_family.md"]:
    check(f"4-{doc[:6]}: record 引用 {doc}", doc in rec)
# 時序索引行數
idx_rows = len(re.findall(r"\|{2} 2026-10-11 \|", rec))
print(f"  2026-10-11 時序索引行數: {idx_rows}")
check("4x: 時序索引 ≥10 行 (10 輪)", idx_rows >= 10, f"{idx_rows}")

# ═══ 6. README / final_result 引用 ═══
print("\n─── 5. README / final_result 同步 ───")
rm = (O7 / "README.md").read_text()
fr = (O7 / "final_result.md").read_text()
chk = all(doc in rm for doc in ["03_", "04_", "05_", "06_", "07_", "08_", "09_", "10_", "11_", "12_"])
check("5a: README 含全部 10 個 docs 引用", chk)
fr_ok = all(x in fr for x in ["自然写", "面級阻挫", "面級定理 30/30", "k↔ℓ 子空間閉合"]) or \
        all(x in fr for x in ["面級阻挫", "面級定理 30/30", "子空間閉合"])
check("5b: final_result 含三層結論", fr_ok)

print("\n" + "=" * 76)
print(f"  AUDIT 結果: {sum(results)}/{len(results)} PASS")
print("=" * 76)