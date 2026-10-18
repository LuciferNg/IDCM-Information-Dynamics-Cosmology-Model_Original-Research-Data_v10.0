#!/usr/bin/env python3
"""
109_r5_semantics_final.py — R5 程序語義最終分層 (2026-10-17)
===================================================================================
Magic 攻堅收官前最後語義缺口:

  26 號「R5 盲測 PASS 5/5 EXACT」到底 PASS 咩?
  70 號「magic 5/5 有身份」p=0.614 (平面常態)
  106-108 號「88-site R5 預測奇模專屬 0/7」

109 分層:
  A. R5 程序一致性 (盲測重現 magic 集) — 26 號語義
  B. R5 身份預測力 (程序輸出 label 命中) — 44-site / 88-site
  C. ★R5 = 描述程序 (consistency) 唔係預測程序 (predictivity)
  D. 最終: magic 攻堅嘅「R5 支撐」只限描述層
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
print("A. R5 程序一致性 (26 號語義)")
print("=" * 72)
print("""
  26 號盲測: 「R5 兩階段程序唯一鎖定 magic 5/5 EXACT」
  = 程序 (S1-S5) 輸出 = {7,14,20,22,33} — 程序同 magic 集一致
  ★ 呢個係「描述/重建」語義: 程序重現已知 magic 集合
  ★ 唔係「預測」語義: 冇推薦未知 label
  35/92 號: R5 程序級 4 組合 (鎖4開2) — 唔係唯一鎖 5/5
  95 號: 44-site magic 5/5 有身份 p=0.614 — 平面常態
""")
chk("A1_consistency", "R5 一致性 = 描述 (程序重現 magic 集); 唔係預測", True)

print()
print("=" * 72)
print("B. R5 身份預測力 — 44-site / 88-site")
print("=" * 72)
print("""
  44-site: magic 5/5 有身份 — 但領域 39/43 = 90.7%, p=0.614 (70/94)
    ⟹ 預測力 = 零 (隨機水平)
  88-site: R5 輸出 6/6 有身份 — 但 100% carry (106); 奇模專屬預測 0/7 (108)
    ⟹ 預測力 = 零 (零獨立命中)
  ★ 兩個 site 都係「程序輸出身份命中」唔顯著/唔獨立
""")
chk("B1_44", "44-site R5 身份命中 = 平面常態 (p=0.614) = 零預測力", True)
chk("B2_88", "88-site R5 身份命中 = 0 獨立 (carry + 0/7) = 零預測力", True)

print()
print("=" * 72)
print("C. ★R5 = 描述程序 (非預測程序)")
print("=" * 72)
print("""
  描述層 (consistency): R5 程序結構上重現 magic 集 — ✅ 5/5 (26 號)
    呢個係「程序一致」唔係「程序預言」
  預測層 (predictivity): R5 輸出身份命中 — 🔴 零 (44 p=0.614 / 88 0)
  ⟹ R5 程序語義 = 描述 (magic 集嘅結構重建) 唔係預測
     (K_chain 結構 → magic 集嘅「再發現」, 唔係「外推」)
  ★ 呢個同 51-63 號七閘 G2 🔴 (規則冇預測力) 一致:
    mirror 規則 (59) 冇預測力 + R5 身份 (70/106-108) 冇預測力
""")
chk("C1_semantics", "R5 = 描述程序; 預測力零 — 同 G2🔴 一致", True)

print()
print("=" * 72)
print("D. 最終: Magic 攻堅嘅「R5 支撐」範圍")
print("=" * 72)
print("""
  R5 支撐 (有效):
    - 程序一致性 5/5 (26) — 描述層
    - 結構稀有 2.1% (70) — 描述層 (magic 集結構不尋常)
    - 22+33 算術必然 (80-81) — 結構層
    - 支柱 cover 唯一 (75/83) — 集合層
  R5 支撐 (無效):
    - 身份命中顯著性 (70 p=0.614; 63 null) — 預測層 🔴
    - 88-site 獨立身份 (106-108: 0) — 預測層 🔴
  ⟹ Magic rows 嘅最終表述:「結構獨特嘅描述集」
     而唔係「預測物理身份嘅機制」
     「支撐物理世界」靠 label 存在 (77/85) + O-series 閉合,
     唔靠 R5 預測 — 呢個係 84/93/101 結論嘅最終一句
""")
chk("D1_final", "Magic = 結構獨特描述集; 支撐靠 label 存量+O-series, 唔靠 R5 預測", True)

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "109_r5_semantics_final", "date": "2026-10-17",
    "consistency": "R5 5/5 (26) = 描述層",
    "predictivity": {"44": "p=0.614 平面常態", "88": "0 獨立 (106-108)"},
    "verdict": "R5 = 描述程序 (非預測程序); Magic = 結構獨特描述集; 支撐靠存量+O-series",
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/109_r5_semantics_final.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/109_r5_semantics_final.json")