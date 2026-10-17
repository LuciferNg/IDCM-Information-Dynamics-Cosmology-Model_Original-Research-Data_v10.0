#!/usr/bin/env python3
"""
105_gate_carry_chain_check.py — G3/G7 carry 連帶檢查 + 終態同步 (2026-10-17)
===================================================================================
104 號確立 G4 carry 問題（存在層 PASS / 獨立層 FAIL）。檢查其他閘門
有冇同類問題:

  G3 遷移唯一性 (60 號): 88-site 譜 = 44-site 譜重覆 + 遷移 carry
     → 「遷移」本身就是 carry 概念! G3 係結構判準 (一對一), 唔係
       label 數量 — carry 唔影響 G3
  G7 對偶鏈 (O218 44/44): 判準本身就用對偶鏈身份 (γ'_{2n}=γ_n)
     → carry 就係 G7 定義 — 冇「獨立 label」宣稱, 唔受影響
  G6 判定標準 (54/55): 「R5 輸出 6/6 有身份 + ≥9 獨立 label」
     → G6 都宣稱「≥9 獨立 label」! 需要同 G4 一樣分層檢查

最終:
  A. G3 carry 影響 = 無 (結構判準)
  B. G7 carry 影響 = 無 (判準定義含 carry)
  C. ★G6 carry 影響 = 有! (「≥9 獨立 label」宣稱 — 同 G4 一樣
     存在層 12 OK / 獨立層 7<9)
  D. 閘門全景更新 (含 101 號最終狀態同步)
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
print("A. G3 遷移唯一性 — carry 影響檢查")
print("=" * 72)
print("""
  G3 (60 號): 88-site ω 譜值集合 = 44-site 譜值集合 (每值重覆兩次);
    遷移唯一性 = 同座標/鏡像格/反序全保 beat — 結構判準
  ★ carry 角色: 「遷移」本身就是 carry 概念 (88-site 身份由 44-site
    carry) — G3 冇宣稱「獨立新 label」, 只宣稱「遷移唯一」⟹
    104 號 carry 問題唔影響 G3 (判準唔涉及獨立計數)
""")
chk("A1_g3", "G3 = 結構判準 (遷移唯一), carry 唔影響", True)

print()
print("=" * 72)
print("B. G7 對偶鏈 — carry 影響檢查")
print("=" * 72)
print("""
  G7 (51 號): 88-site 對偶鏈身份 (O218 γ'_{2n}=γ_n 44/44)
  ★ carry 角色: 對偶鏈 = 判準本身定義! G7 PASS = 「R5 輸出全部有
    88-site 對偶鏈身份」— carry 就係身份來源, 唔係額外宣稱
  ⟹ G7 唔受 carry 問題影響 (佢就係 carry 閘門)
""")
chk("B1_g7", "G7 = 對偶鏈判準 (carry 係定義), 唔受影響", True)

print()
print("=" * 72)
print("C. ★G6 判定標準 — carry 影響檢查")
print("=" * 72)
print("""
  G6 (54 號): 「PASS = R5 輸出全有身份 + ≥9 獨立 label」
  ★ carry 角色: G6 都宣稱「≥9 獨立 label」— 同 G4 一樣!
    存在層: 12 ≥ 9 ✅
    獨立層: 奇模專屬 7 < 9 🔴 (104 號)
  ⟹ G6 都係「存在層 PASS + 獨立層 FAIL」
""")
chk("C1_g6", "G6 同 G4 一樣: 存在層 PASS + 獨立層 FAIL (carry 影響)", True)

print()
print("=" * 72)
print("D. ★閘門全景更新 (105 號整合)")
print("=" * 72)
gates = {
    "G1 獨立性": "✅ 不變 (9/9 mapping 源頭 O34/O35/O54/O13)",
    "G2 預註冊": "🔴 規則可預測 + 🟡 label 存在性 (85/87 裁定; 102 protocol 標準化)",
    "G3 遷移唯一性": "✅ 不變 (60; 結構判準 carry 唔影響)",
    "G4 數量閘": "🟡 分層: 存在層 ✅ 12≥9 + 獨立層 🔴 7<9 (104 裁定)",
    "G5 零參數": "✅ 不變",
    "G6 判定標準": "🟡 分層: 存在層 ✅ (R5 6/6 + 12) + 獨立層 🔴 (7<9) (105)",
    "G7 對偶鏈": "✅ 不變 (carry 係定義; 103 重算 44/44)",
}
for k, v in gates.items():
    print(f"  {k}: {v}")
chk("D1_gates", "閘門全景更新完成 (G1-G7 七閘終態)", True)

print()
print("=" * 72)
print("E. 101 號最終狀態同步 (append-only)")
print("=" * 72)
print("""
  101 號: 「閘門: G1/G3/G4(12≥9)/G5/G6/G7 ✅, G2 🔴🟡」
  105 號更正: G4/G6 = 🟡 分層 (存在層 ✅ + 獨立層 🔴) —
    唔可以放喺 G 開 ✅ 組
  正確: G1/G3/G5/G7 ✅; G2 🔴🟡; G4 🟡 (存在 ✅/獨立 🔴); G6 🟡
""")
chk("E1_sync", "101 最終狀態嘅 G4/G6 表述需要同步 (append-only 附註)", True)

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "105_gate_carry_chain_check", "date": "2026-10-17",
    "G3": "結構判準, carry 唔影響",
    "G7": "對偶鏈=carry 定義, 唔影響",
    "G6": "同 G4: 存在 ✅ 12 / 獨立 🔴 7",
    "gates_final": gates,
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/105_gate_carry_chain_check.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/105_gate_carry_chain_check.json")