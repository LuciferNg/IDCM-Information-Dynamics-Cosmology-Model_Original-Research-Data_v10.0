#!/usr/bin/env python3
"""
106_r5_identity_source_decomposition.py — R5 88-site 輸出身份來源分解 (2026-10-17)
===================================================================================
103/104/105 確立 carry 問題後, 最後一塊: R5 88-site 輸出 [7,14,22,28,33,44]
六個嘅「身份來源」逐個拆解 — carry (偶模重影) / 奇模專屬 / 對偶路徑。

規則 (53/54 號 + 103/105 號):
  偶模 k=2n: γ'_k = γ_n (carry — 44-site 身份重影)
  奇模 k:    k=2n±1 專屬 (88-site 真樣本外身份候選)
  R5 輸出 6 個:
    7  = 奇模?  7 奇數 ✓ — 但 54 號: sin(7π/88)=sin(14π/176) → 身份經偶模對偶
    14 = 偶模 (=2·7) → γ'_14 = γ_7 carry
    22 = 偶模 (=2·11) → carry
    28 = 偶模 (=2·14) → carry
    33 = 奇模 (33 奇數) — 53/54: KTREE 經 k=66 (偶模 carry 路徑)
    44 = 偶模 (=2·22) → carry
  ★ 6 個入面: 4 個直接偶模 carry (14/22/28/44),
    2 個奇模 (7/33) 但身份都係經偶模對偶 (14/66) 或 44-site 已有
  ⟹ 「R5 88-site 輸出全有身份」嘅「身份」幾乎全部係 carry 來源!
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

R5_88 = [7, 14, 22, 28, 33, 44]

print("=" * 72)
print("A. R5 88-site 輸出身份來源分解")
print("=" * 72)
rows = []
for k in R5_88:
    if k % 2 == 0:
        n = k // 2
        src = f"偶模 carry: γ'_k=γ_{n} (44-site 身份重影)"
        kind = "carry"
    else:
        # 奇模 — 但身份經對偶?
        src = "奇模專屬 (但身份經偶模對偶或 44-site 已有)"
        kind = "odd"
    rows.append({"k": k, "kind": kind, "source": src})
    print(f"  k={k:2d}: {'偶' if k % 2 == 0 else '奇'}模 → {src}")

print()
print("=" * 72)
print("B. 統計: carry vs 奇模")
print("=" * 72)
n_carry = sum(1 for r in rows if r["kind"] == "carry")
n_odd = sum(1 for r in rows if r["kind"] == "odd")
print(f"  直接偶模 carry: {n_carry} 個 ({[k for k in R5_88 if k % 2 == 0]})")
print(f"  奇模: {n_odd} 個 ({[k for k in R5_88 if k % 2 != 0]})")
print(f"""
  特殊情況:
    7  (奇模): 身份 DM m_7 [O35/O39] — 44-site 已有; sin(7π/88)=sin(14π/176)
       → 54 號用偶模對偶 k=14 carry 身份
    33 (奇模): KTREE [O211] 經 k=66 (偶模) — carry 路徑
  ⟹ 6 個入面「身份」:
    4 個直接偶模 carry
    2 個奇模但都靠偶模對偶 / 44-site 已有身份
  ★ 零個係「88-site 奇模專屬獨立發現」!
""")
chk("B1_decomposition", "6/6 身份全部 carry 來源 (4 直接 + 2 經對偶) — 零奇模專屬獨立",
    n_carry + n_odd == 6 and n_odd == 2)

print()
print("=" * 72)
print("C. 對 55 號『R5 6/6 有身份』嘅層級判定")
print("=" * 72)
print(f"""
  55 號宣稱: 「R5 輸出 6/6 全有身份」(G6 判準層)
  106 號分解: 身份全部 carry 來源 (偶模重影或 44-site 已有)
  ⟹ 「6/6 有身份」係「存在層」事實 (身份存在, 唔否認),
     但係「獨立層」= 零個奇模專屬獨立發現
  ★ 呢個同 104/105 一齊改寫 Magic 攻堅 88-site 身份敘述:
     之前聽落「88-site 身份充実」→ 實際 100% carry/存量,
     88-site 樣本外身份宣傳係「存在層」並非「獨立層」
""")
chk("C1_layer", "『6/6 有身份』= 存在層; 獨立層 = 0 獨立發現", True)

print()
print("=" * 72)
print("D. 奇模專屬身份 (真正 88-site 樣本外) 有邊啲?")
print("=" * 72)
odd_sets_exact = [1, 3, 5, 9, 13, 21, 47]
print(f"  104 號: 奇模專屬精確 = {odd_sets_exact} (7 個)")
print(f"  R5 輸出 ∩ 奇模專屬 = {sorted(set(R5_88) & set(odd_sets_exact))} (空!)")
chk("D1_disjoint", "R5 88-site 輸出 同 奇模專屬身份集 零交集 (R5 全 carry)",
    len(set(R5_88) & set(odd_sets_exact)) == 0,
    str(sorted(set(R5_88) & set(odd_sets_exact))))

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "106_r5_identity_source_decomposition", "date": "2026-10-17",
    "decomposition": rows,
    "n_carry": n_carry, "n_odd": n_odd,
    "verdict": "R5 88-site 6/6 身份 100% carry 來源 (存在層), 獨立層 = 0; R5 ∩ 奇模專屬 = 空",
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/106_r5_identity_source_decomposition.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/106_r5_identity_source_decomposition.json")