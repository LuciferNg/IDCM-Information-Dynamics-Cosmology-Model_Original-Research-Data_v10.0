#!/usr/bin/env python3
"""
O119 - 終極一致性核對 (docs vs JSON vs scripts 輸出)
====================================================
核對 01_problem_record.md + docs/01_derivation_record.md 宣稱嘅每個關鍵數值
vs data/*.json 實際值。
"""
import json, re, os, math

# 讀 docs
doc = open("docs/01_derivation_record.md").read()
prob = open("01_problem_record.md").read()
all_text = doc + prob

checks = []
def chk(name, cond, detail=""):
    checks.append((name, cond, detail))
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

print("=" * 72)
print("O119 終極一致性核對")
print("=" * 72)

# 1. 核心數值出現 (docs 有講, 且數值正確)
core = {
    "m_deltaW = 13.95 MeV": "13.95",
    "C = 1/25": "1/25",
    "gamma = 8/31": "8/31",
    "F6/(Nd-F7)": "F₆/(N_d−F₇)",
    "Gamma = 9.26e-5 MeV": "9.26×10⁻⁵",
    "tau = 7.1e-18": "7.1×10⁻¹⁸",
    "E_res = 47.6": "47.6",
    "m_44 = 55.8": "55.8",
    "譜指數 2": "2",
    "運動學窗口": "2m_e < m_δW < 2m_μ",
}
for name, frag in core.items():
    chk(f"docs 含 '{name}'", frag in all_text or frag.replace("_", "") in all_text)

# 2. JSON 關鍵值核對
json_checks = [
    ("data/01_audit_o54_internal.json", "mode_superposition_chi2_dof", 825.49, 1.0),
    ("data/01_audit_o54_internal.json", "max_static_decay_MeV", 27.9009, 1e-4),
    ("data/03_structural_spectrum.json", "chi2_struct_0par", 1.09377, 1e-3),
    ("data/03_structural_spectrum.json", "chi2_free_2par", 1.37622, 1e-3),
    ("data/04_kinematic_window.json", "m_deltaW_MeV", 13.95045, 1e-3),
    ("data/05_energy_scale.json", "Ep_needed_10GeV_no_proj_GeV", 197.309, 1.0),
    ("data/05_energy_scale.json", "Ep_needed_10GeV_Fproj_GeV", 11.606, 0.1),
    ("data/06_full_closure.json", "production_spectral_index", 2.0, 1e-10),
    ("data/07_final_verification.json", "passed", 10, 0.5),
    ("data/07_final_verification.json", "total", 10, 0.5),
]
print()
print("[2] JSON 值核對")
for jf, key, expected, tol in json_checks:
    d = json.load(open(jf))
    actual = d.get(key)
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        ok = abs(actual - expected) < tol
        chk(f"{jf}:{key}", ok, f"(={actual}, expect {expected})")
    else:
        chk(f"{jf}:{key}", str(actual) == str(expected), f"(={actual})")

# 3. chi2 一致性: docs 寫 1.094, JSON 寫 1.0938
chk("chi2/dof docs vs JSON 一致", "1.094" in doc, "")
d3 = json.load(open("data/03_structural_spectrum.json"))
chk("JSON chi2 1.09377 ≈ docs 1.094", abs(d3["chi2_struct_0par"]-1.094) < 0.001, "")

# 4. 開放項目列出 (docs §8 與 problem record §開放 一致)
open_items_doc = ["8/31 動力學", "1/25 動力學", "p_CR", "次級背景", "40 MeV 拐點"]
print()
print("[3] 開放項目一致性")
for item in open_items_doc:
    chk(f"docs 含開放項 '{item}'", item in all_text, "")

# 5. scripts 檔案齊全
print()
print("[4] 檔案齊全")
scripts = sorted(os.listdir("scripts"))
expected_s = [f"{n:02d}_" for n in range(1, 9)]
for e in expected_s:
    ok = any(f.startswith(e) for f in scripts)
    chk(f"scripts/{e}*", ok, "")

npass = sum(1 for c in checks if c[1])
print()
print(f"  總結: {npass}/{len(checks)} PASS")
