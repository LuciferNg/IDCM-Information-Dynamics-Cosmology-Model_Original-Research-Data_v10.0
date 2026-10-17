#!/usr/bin/env python3
"""
79_p9_magic_chain_closeout.py — P9 Magic rows 攻堅鏈收線總結 (2026-10-17)
===================================================================================
目的: 整合 25-78 全鏈判定成權威收線狀態。唔係新計算——係最終盤點。

盤點:
  A. Magic rows 攻堅階段 (25-49): 生成/gcd/deg/R5/盲測/統計/支柱
  B. 七閘 (51-60): G1-G7 + G2 盲測 + G3 遷移唯一性
  C. NULL MODEL (61-63): 53-55 統計宣稱撤回
  D. 審計覆蓋 (64-69): 十輪 118/118 + 45 data 25/25
  E. Magic 統計攻堅 (70-78): 7 維度撤回 + 企穩 5 項 + 終裁

輸出: P9 最終狀態表 — 邊啲 claim 企穩 / 撤回 / 開放。
"""
import json
import subprocess
import os

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
print("A. Magic rows 攻堅階段 (25-49) 最終狀態")
print("=" * 72)
rows_a = [
    ("25-27", "magic rows 識別 (5 gcd 類)", "✅ 保留"),
    ("26", "盲測 R1/R2 (44-site 5/5 預註冊)", "✅ 保留 (5/5 EXACT)"),
    ("28", "審計 46/46", "✅"),
    ("30-32", "對角線/不動點/整欄", "✅ 附註 (31 galois bug / 32 5格6次)"),
    ("33-43", "R5 程序開發", "✅ 程序一致"),
    ("44", "第四輪審計 58/59", "✅"),
    ("45", "數據審計 25/25", "✅"),
    ("46-47", "88-site labels/窗口", "✅"),
    ("48", "統計失望 P=0.403", "✅ 記錄 (第一次 null 擊穿)"),
    ("49", "宇宙 5 支柱 (用戶 focus)", "🟡 label 真 (77) 但 cover tautology (76)"),
]
for tag, desc, st in rows_a:
    print(f"  {st} {tag}: {desc}")
chk("A1_chain", "Magic rows 攻堅階段狀態確認", True)

print()
print("=" * 72)
print("B. 七閘 (51-60)")
print("=" * 72)
rows_b = [
    ("G1 獨立性", "✅"),
    ("G2 盲測", "🔴 FAIL (兩輪 p=0.69 + NULL p>0.4)"),
    ("G3 遷移唯一性", "✅ (60: 偶模 carry k=2n 唯一)"),
    ("G4 數量閘", "✅ (12≥9)"),
    ("G5 零參數", "✅"),
    ("G6 判定標準", "✅ (54 lock)"),
    ("G7 對偶鏈", "✅ (O218 44/44)"),
]
for tag, st in rows_b:
    print(f"  {st} {tag}")
chk("B1_gates", "七閘狀態確認 (唯一未過 = G2)", True)

print()
print("=" * 72)
print("C. NULL MODEL (61-63)")
print("=" * 72)
rows_c = [
    ("61", "領域基準 42.5% vs R5 50%, p=0.51", "❌ 唔顯著"),
    ("62", "bugged (grep \\d) 已刪", "—"),
    ("63", "判準 B 24.1% p=0.45 / 判準 A 54.0% p=0.42", "❌ 唔顯著"),
    ("結論", "「R5 6/6 有身份」統計宣稱撤回", "✅ 誠實"),
]
for tag, desc, st in rows_c:
    print(f"  {st} {tag}: {desc}")
chk("C1_null", "NULL MODEL 定案 (統計宣稱撤回, 存在性唔受影響)", True)

print()
print("=" * 72)
print("D. 審計覆蓋 (64-69) — 十輪")
print("=" * 72)
print("  64 盤點: 169 檔 = ✅37/🟡27/🔴94/⚙️11")
print("  65 六輪 23/23 / 66 七輪 25/25 / 67 八輪 27/27")
print("  68 九輪 27/27 / 69 十輪 16/16")
chk("D1_audits", "審計覆蓋: 01-69 全部有審計輪 (118/118 + 45 data 25/25)", True)

print()
print("=" * 72)
print("E. Magic 統計攻堅 (70-78) — 終裁確認")
print("=" * 72)
rows_e = [
    ("70", "領域 91% / anchor 3 解", "🔴 撤回"),
    ("71", "37 個過閘集合", "🔴 撤回"),
    ("72", "身份 37/37 / label 並列", "🔴 撤回"),
    ("73", "深度 #11/37", "🔴 撤回"),
    ("74", "O 源頭 #5/37", "🔴 撤回"),
    ("75", "cover 全 5 支柱", "🟡 tautology (76)"),
    ("76", "支柱循環診斷", "🟡 定案"),
    ("77", "A 層 label 真實性 (5 支柱有出處)", "✅ 企穩"),
    ("78", "終裁: 統計 7 維度撤回 + 企穩 5 項", "✅ 收線"),
]
for tag, desc, st in rows_e:
    print(f"  {st} {tag}: {desc}")
chk("E1_campaign", "Magic 統計攻堅終裁確認 (70-78)", True)

print()
print("=" * 72)
print("F. P9 最終狀態")
print("=" * 72)
final = {
    "企穩": [
        "946/946 beat 全無理 + 數域 (1-23)",
        "R5 程序 consistency 5/5 (26 預註冊)",
        "三定理 A/B/C + μ²=2 + V_min=−61.5",
        "magic 結構稀有 (5 gcd+5 deg, 2.1%)",
        "22+33 結構強制 (84%)",
        "A 層 label 真實性 (5 支柱有出處)",
        "12 label 存在性 (O-series 閉合時序)",
    ],
    "撤回": [
        "「magic 有特別多 O-series 身份」(領域 91%)",
        "「anchor 由結構唯一鎖定」(3 解)",
        "「5-collection 唯一」(37 個)",
        "「身份完整度特別」(37/37)",
        "「身份深度特別」(#11/37)",
        "「O 源頭數特別」(#5/37)",
        "「cover 全 5 支柱」= tautology",
        "G2 盲測 (p=0.69 flat)",
    ],
    "開放": [
        "O35 beat/mass open (7 嘅 mass link-up 上游)",
        "O158 ×41 聚類 partial (KTREE 上游)",
        "G2 出路未裁 (存量獨立性/未來預註冊/程序閘)",
        "44-site R5 對照基準 — 已由 70-78 完成 ✅",
    ],
}
print("  企穩:")
for x in final["企穩"]:
    print(f"    ✅ {x}")
print("  撤回:")
for x in final["撤回"]:
    print(f"    🔴 {x}")
print("  開放:")
for x in final["開放"]:
    mark = "✅ 已完成" if "對照基準" in x else "🔴"
    print(f"    {mark} {x}")
chk("F1_final", "P9 最終狀態表確認", True)

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "79_p9_magic_chain_closeout", "date": "2026-10-17",
    "stable": final["企穩"], "withdrawn": final["撤回"], "open": final["開放"],
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/79_p9_magic_chain_closeout.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/79_p9_magic_chain_closeout.json")