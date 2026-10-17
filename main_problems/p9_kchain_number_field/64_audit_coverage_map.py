#!/usr/bin/env python3
"""
64_audit_coverage_map.py — P9 審計覆蓋全景盤點 (2026-10-17)
==============================================================
用戶: 「先審計，整個P9有哪些文件和數值未經過審計」

已做五輪審計:
  R1 = 21_doc_independent_audit (53/53): 基礎/數域/946/鏈閉合/CKM/文檔數字(05-20抽樣)
  R2 = 24_numeric_audit (21/21): 22_galois + 23_bridge + 00_record 新章節
  R3 = 28_numeric_audit_round3 (46/46): 25/26/27
  R4 = 44_numeric_audit_round4 (58/59): 33–43
  R5 = 50_numeric_audit_round5 (35/36): 30/31/32
  D  = 45_data_audit (25/25): DATA 定義/Q1-Q5

分類: ✅已審 / 🟡部分(文檔數字抽查) / 🔴未審
"""
import json, os, re

os.chdir("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p9_kchain_number_field")

files = sorted(f for f in os.listdir(".") if f.endswith(".py") or f.endswith(".md"))

# 審計輪覆蓋定義 (根據 script 頭部範圍)
def audit_round(fn):
    """返回邊輪審咗 (R1/R2/R3/R4/R5/D) 或 None"""
    base = re.match(r"(\d+)_", fn)
    if not base:
        return None
    n = int(base.group(1))
    if n == 21: return "R1(21自身=審計員)"
    if n == 24: return "R2(24自身=審計員)"
    if n == 28: return "R3(28自身=審計員)"
    if n == 44: return "R4(44自身=審計員)"
    if n == 45: return "D(45自身=審計員)+R4範圍前"
    if n == 50: return "R5(50自身=審計員)"
    if n == 22: return "R2(24審22)"
    if n == 23: return "R2(24審23)"
    if n in (25, 26, 27): return "R3(28審)"
    if n in (30, 31, 32): return "R5(50審)"
    if 33 <= n <= 43: return "R4(44審)"
    if n in (1, 2, 3): return "R1文檔數字覆蓋(scripts自身未逐行)"
    if n in (4, 5): return "R1文檔數字覆蓋(05表抽樣12個)"
    if 6 <= n <= 20: return "R1文檔數字覆蓋(06-20關鍵數字)"
    if n == 29: return None  # 探針未審
    return None

# 未審定判定: 46-63 全部新產物 (但 50 係審計員自身, 64 係本盤點)
rows = []
for fn in files:
    base = re.match(r"(\d+)_", fn)
    n = int(base.group(1)) if base else 0
    if fn == "64_audit_coverage_map.py":
        status, audited = "⚙️ 審計員自身", "64(本盤點)"
    elif n == 50:
        status, audited = "⚙️ 審計員自身", "R5(50自身=審計員)"
    elif n >= 46:
        status, audited = "🔴 未審 (46+ 新產物)", None
    else:
        audited = audit_round(fn)
        if audited is None:
            status = "🔴 未審"
        elif audited.startswith("R1文檔"):
            status = "🟡 部分 (文檔數字抽查, scripts 自身未逐行)"
        elif "自身" in audited:
            status = "⚙️ 審計員自身"
        else:
            status = "✅ 已審"
    rows.append((fn, status, audited or ""))

print("=" * 100)
print("P9 審計覆蓋全景 (2026-10-17, 檔 2026-10-17 水位)")
print("=" * 100)
count = {}
for fn, st, ro in rows:
    key = st.split(" ")[0]
    count[key] = count.get(key, 0) + 1
    print(f"{st:<28} {ro:<24} {fn}")

print()
print("=" * 100)
print(f"合計: {len(files)} 檔案")
for k in ("✅", "🟡", "🔴", "⚙️"):
    print(f"  {k}: {count.get(k, 0)}")

# 未審 / 部分 清單
un = [r for r in rows if r[1].startswith("🔴")]
pa = [r for r in rows if r[1].startswith("🟡")]
print()
print("=== 🔴 未審計檔案 ===")
for fn, st, ro in un:
    print(f"  {fn}")
print()
print("=== 🟡 部分審計檔案 ===")
for fn, st, ro in pa:
    print(f"  {fn}")

# 未審計數值類別
print()
print("=" * 100)
print("未經審計嘅數值類別:")
categories = [
    ("🔴 46-63 新產物 (全部 scripts 輸出 + md 聲稱):",
     ["46_88site_labels (44-site 25 element label table, 4/5)",
      "47_r5_extrapolation_176 (N=176/352 窗口凍結)",
      "48_magic_44site_specificity (MC null P=0.403)",
      "49_magic_distinctiveness (5 支柱)", "51 label gate 七閘",
      "52 pre-scan (Σk偶=90)", "53 γ176 labels (γ'_{2n}=γ_n 44/44)",
      "54 G6 重定義 (θ₂₃ 49.3202°)", "55 G4 count (12 label)",
      "56/57/58/59 G2 盲測 (B* 3/4, B2 0/5, 合併 p=0.69)",
      "60 G3 (ω_n=ω_{88−n} 87/87)", "61/63 NULL MODEL (領域 24-54%)"]),
    ("🔴 早期無編號 scripts (Aug 25-27, 21 號冇逐行審):",
     ["blind_test_*.py ×9", "chain_closure*.py ×3", "deg_formula.py",
      "direction_*.py ×4", "dual_verify.py", "edge_*.py ×3",
      "extrapolate.py", "gamma87_identity.py", "identity_84*.py ×2",
      "isotope_search.py", "layer_final.py", "low_endpoint_structure.py",
      "magic_*.py ×5", "microcode_*.py ×5", "missing_gcd.py",
      "periodic_table.py", "phys_highdeg.py", "physics_island_test.py",
      "rule_*.py ×3", "s33_*.py ×2", "seed_90_88.py", "self_loop*.py ×2",
      "seven_identity.py", "significance.py", "smod4_rule.py",
      "spectral_match.py", "spectroscopy.py", "spectrum_analysis.py",
      "unassigned_opcodes.py"]),
    ("🔴 29_probe_88site_extension.py:", ["88/176 擴展探針 (未見審計輪)"]),
    ("🟡 01-20 文檔數字 (21 號抽樣, 未全部):",
     ["01-03 主 scripts 自身邏輯", "06/07/08/09/10 盲測+microcode+自環+鏈閉合",
      "16/17/18/19/20 magic rows 規則+layer+data+v2+週期表+quark 家族"]),
    ("🔴 md 聲稱 vs script 輸出一致性 (45 data audit 之外):",
     ["41_sync_saxis / 42_d29 / 43 33對偶 md 是否與 json 一致"]),
]
for title, items in categories:
    print(f"\n{title}")
    for it in items:
        print(f"    · {it}")

# JSON 輸出
map_data = {"as_of": "2026-10-17",
            "total_files": len(files),
            "R1_53_53": "21_doc: 基礎/數域/946/鏈閉合/CKM/05-20文檔數字",
            "R2_21_21": "24_numeric: 22+23+00新章節",
            "R3_46_46": "28_round3: 25+26+27",
            "R4_58_59": "44_round4: 33-43 (B6 更正)",
            "R5_35_36": "50_round5: 30-32 (B4 script bug)",
            "D_25_25": "45_data_audit: DATA 定義/Q1-Q5",
            "uncovered": [fn for fn, st, _ in un],
            "partial": [fn for fn, st, _ in pa]}
with open("data/64_audit_coverage_map.json", "w") as f:
    json.dump(map_data, f, indent=1, ensure_ascii=False, default=str)
print("\n輸出: data/64_audit_coverage_map.json")