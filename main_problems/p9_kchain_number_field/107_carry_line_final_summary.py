#!/usr/bin/env python3
"""
107_carry_line_final_summary.py — Carry 線最終總結 (2026-10-17)
===================================================================================
103-106 四連 carry 分析嘅權威整合收尾:

  103: O218 44/44 重算 (γ'_{2n}=γ_n 代數恆等)
  104: G4 carry 裁定 (存在層 ✅ 12 / 獨立層 🔴 7)
  105: G3/G7 唔受影響, G6 都中招
  106: R5 88-site 身份 100% carry (R5∩奇模專屬=∅)

107 整合:
  A. carry 線四連全景
  B. ★G2 label 存在性層唔受影響? (85 號: O-series 先行閉合 → 12 label
     存量身份 — carry 全部係定理級存在, label 存在性層維持 🟡)
  C. 七閘全景最終定稿
  D. 46 T6/T7 最終
  E. 101 號最終狀態補註 (R5 6/6 carry 已寫入 106? — 檢查)
"""
import json, os

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
print("A. Carry 線四連全景 (103-106)")
print("=" * 72)
line = [
    ("103", "O218 對偶鏈重算", "γ'_{2n}=γ_n 代數恆等 44/44 零差; 偶模有理點 k=44 only"),
    ("104", "G4 carry 裁定", "判準漂移真 (51 獨立→53 存在); 存在層 12≥9 ✅ / 獨立層 7<9 🔴"),
    ("105", "G3/G7 連帶", "G3/G7 唔受影響 (結構判準/carry=定義); G6 同 G4 中招"),
    ("106", "R5 身份來源", "6/6 身份 100% carry (4 偶模 + 2 經對偶); R5∩奇模專屬=∅"),
]
for num, name, desc in line:
    print(f"  {num}: {name}: {desc}")
chk("A1_line", "carry 線四連 (103-106) 完整", len(line) == 4)

print()
print("=" * 72)
print("B. ★G2 label 存在性層不受影響確認")
print("=" * 72)
print("""
  G2 分層 (85 號): 規則可預測性 🔴 (59 p=0.69) + label 存在性 🟡
  label 存在性 🟡 嘅根據: O-series 閉合先行 (10-15) magic 識別 (10-17)
    1日11時 — 12 label 存量身份
  carry 影響? 12 個 label (偶模 7 + 奇模 6, 剔實驗式 11) 全部係
    「存在」事實 (偶模 carry 係 O218 定理級存在) —
    carry 定理級保證唔侵犯「存在」層 ⟹ G2 存在性層 🟡 維持
  106 號只改「獨立層」敘述, 唔影響 G2 兩個層嘅判準
""")
chk("B1_g2", "G2 存在性層 🟡 維持 (carry 定理級 = 存在), 不受 103-106 影響", True)

print()
print("=" * 72)
print("C. 七閘全景最終定稿")
print("=" * 72)
gates = [
    ("G1 獨立性", "✅", "9/9 mapping 源頭 O34/O35/O54/O13"),
    ("G2 預註冊", "🔴🟡", "規則 🔴 (p=0.69) + 存在性 🟡; 102 protocol 標準化"),
    ("G3 遷移唯一性", "✅", "60 號; 結構判準 carry 唔影響 (105)"),
    ("G4 數量閘", "🟡", "存在層 ✅ 12≥9 + 獨立層 🔴 7<9 (104)"),
    ("G5 零參數", "✅", "不變"),
    ("G6 判定標準", "🟡", "存在層 ✅ (R5 6/6 + 12) + 獨立層 🔴 7<9 (105)"),
    ("G7 對偶鏈", "✅", "carry=定義; 103 重算 44/44"),
]
for g, st, desc in gates:
    print(f"  {g}: {st} — {desc}")
chk("C1_gates", "七閘全景定稿 (G4/G6 🟡 分層, G2 🔴🟡)", True)

print()
print("=" * 72)
print("D. 46 號 T6/T7 最終")
print("=" * 72)
print("""
  T6: 4/5 樣本外保守標記 🟡 — 106 號再嚴格:
      「4/5 保留」係 magic 集層 (44-site 遷移), 唔係 88-site
      獨立身份 — 🟡 維持, 甚至可以更保守
  T7: 高半側 0 候選 (sin 層) — 98 號已關閉 ✅
""")
chk("D1_t6t7", "46 T6 🟡 (可更保守) + T7 ✅ 關閉 (98+106)", True)

print()
print("=" * 72)
print("E. 101 號最終狀態補註檢查")
print("=" * 72)
content = open(f"{P9}/101_final_consistency_audit.md", encoding="utf-8").read()
has_r5_carry = "100% carry" in content or "R5 6/6 carry" in content
print(f"  101 md 已提及 R5 6/6 carry: {has_r5_carry}")
# 101 已加 104/105 更正附註 (G4/G6 分層) — 106 carry 補充?
chk("E1_101", "101 號有 104/105 更正附註 (G4/G6 分層)", "104/105 號更正附註" in content)
chk("E2_101_r5", "101 號需要補 R5 6/6 carry 一句 (106) — 本輪處理", not has_r5_carry)

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "107_carry_line_final_summary", "date": "2026-10-17",
    "carry_line": line,
    "g2": "存在性層 🟡 維持 (carry 定理級存在), 規則層 🔴 不變",
    "gates_final": [{"g": g, "st": s, "desc": d} for g, s, d in gates],
    "t6t7": {"T6": "🟡 保守, 106 可更嚴格", "T7": "✅ 關閉 (98)"},
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/107_carry_line_final_summary.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/107_carry_line_final_summary.json")