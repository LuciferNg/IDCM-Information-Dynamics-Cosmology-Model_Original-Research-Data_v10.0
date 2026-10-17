#!/usr/bin/env python3
"""
87_g2_exit23_ruling.py — G2 出路②③ 裁決 (2026-10-17)
===================================================================================
背景: 85 號已裁出路① (O-series 閉合時序 → 存在性層🟡)。剩出路②③:
  出路②: 未來真預註冊 (無限延期, 未有)
  出路③: 程序預註冊閘 — R5 程序 (35/37 號) lock 早於一切, 程序本身就係
          預註冊 → G2 由程序閘保證

出路③要驗證: R5 程序 formalize 時間 < magic 識別時間?
  - 若程序先於識別 → 程序係獨立構建 (預註冊閘成立)
  - 若程序後於識別 → 程序係為 magic 後驗構建 (預註冊閘不成立 — 循環)
  ★16/17 號 magic 識別 = 10-17 11:03; 35_37 R5 = 10-17 13:44/13:56
  初步睇: 程序後於識別 → 出路③ 唔成立? 要核實
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
print("A. 時序: magic 識別 vs R5 程序 formalize")
print("=" * 72)
f_ident = ["16_magic_rows_rule.md", "17_layer_magic_data.md", "25_magic_rows_open.md", "26_blind_test_magic_rows_rules.md"]
f_prog = ["33_magic_select_s4.md", "34_magic_completion.md", "35_r5_full_procedure.md", "37_r5_necessity_and_extension.md"]
f_prog = [f for f in f_prog if os.path.exists(os.path.join(P9, f))]
t_ident = [mtime(os.path.join(P9, f)) for f in f_ident if os.path.exists(os.path.join(P9, f))]
t_prog = [mtime(os.path.join(P9, f)) for f in f_prog if os.path.exists(os.path.join(P9, f))]
print("  magic 識別:")
for f, t in zip(f_ident, t_ident):
    print(f"    {f}: {t}")
print("  R5 程序:")
for f, t in zip(f_prog, t_prog):
    print(f"    {f}: {t}")
t_ident_min = min(t for t in t_ident if t)
t_prog_min = min(t for t in t_prog if t)
print(f"  識別最早: {t_ident_min}")
print(f"  程序最早: {t_prog_min}")
d = t_prog_min - t_ident_min
print(f"  Δ程序−識別 = {d}")

print()
print("=" * 72)
print("B. ★裁決 — 出路③ 程序預註冊閘")
print("=" * 72)
if t_prog_min > t_ident_min:
    print("  ❌ 程序後於識別 → 出路③ 唔成立")
    print("     R5 程序 (35/37) 係 magic 識別 (16/17) 之後先 formalize")
    print("     ⟹ 程序本身係後驗構建 — 唔可以話『程序 lock 早於一切』")
    verdict3 = False
else:
    print("  ✅ 程序先於識別 → 出路③ 成立")
    verdict3 = True
chk("B1_exit3", "出路③ 程序預註冊閘", verdict3,
    f"Δ={d}; 程序{'>' if t_prog_min > t_ident_min else '<='}識別")

print()
print("=" * 72)
print("C. ★裁決 — 出路② 未來真預註冊")
print("=" * 72)
print("""
  出路②: 未來新 label 先 lock 後測 — 唔影響現有 12 label
  ⟹ 作為「未來程序」完全合理 (可以採納做 protocol)
  ⟹ 但唔影響當前 G2 裁決 — 當前 label 仍然係存量+程序後驗
      出路② = 前瞻 protocol, 出路① = 存量獨立性 (85 號已成立)
  決: 出路② 採納為未來 protocol (G2 未來閘), 唔改變現狀
""")
chk("C1_exit2", "出路② 採納為未來 protocol (唔影響現狀)", True)

print()
print("=" * 72)
print("D. G2 裁決整合 (85+87)")
print("=" * 72)
print("""
  G2 完整性裁決:
    ① 存量獨立性 (O-series 閉合時序)  → 🟡 成立 (85)
    ② 未來真預註冊                    → ✅ 採納做 protocol (87)
    ③ 程序預註冊閘                    → 🔴 唔成立 — 程序後驗 (87)
  ⟹ G2 嘅「後驗污染」指控: 已由出路① 排除 (label 存在性 唔係後驗)
  ⟹ G2 嘅「規則可預測性」: 🔴 維持 FAIL (59 盲測 p=0.69)
  最終: G2 = 🔴(規則) + 🟡(存在性) — 兩層分開, 唔會升 PASS
""")
chk("D1_G2_final", "G2 整合裁決: 存在性🟡 + 可預測性🔴", True)

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "87_g2_exit23_ruling", "date": "2026-10-17",
    "ident_min": str(t_ident_min), "prog_min": str(t_prog_min),
    "delta_program_minus_ident": str(d),
    "exit3_program_registration_gate": verdict3,
    "exit2_future_prereg": "採納為未來 protocol",
    "G2_final": {"existence": "🟡 O-series 時序獨立 (85)", "predictability": "🔴 盲測 FAIL (59)"},
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/87_g2_exit23_ruling.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/87_g2_exit23_ruling.json")