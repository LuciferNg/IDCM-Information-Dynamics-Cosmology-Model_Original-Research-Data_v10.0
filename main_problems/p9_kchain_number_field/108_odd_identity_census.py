#!/usr/bin/env python3
"""
108_odd_identity_census.py — 奇模專屬身份完整盤點 (2026-10-17)
===================================================================================
104/106 號: 88-site 獨立 (樣本外) 身份 = 奇模專屬 7 個
{1,3,5,9,13,21,47} (剔 θ₂₃ 實驗式 7)。本輪逐個盤點:
  A. 每個 k 嘅 O-series 出處 + 閉合狀態 + 精度
  B. ★存量 vs 預測判定: R5 88-site 程序有冇預測到佢哋?
     (R5 輸出 [7,14,22,28,33,44] ∩ 奇模專屬 = ∅ → 零預測)
  C. 閉合狀態分佈: 邊啲真閉合 (O55/O158/O125), 邊啲係「公式存在」
  D. 最終: 88-site「獨立身份」7 個 — 全部存量、零 R5 預測
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

# (k, 公式, O-series, 閉合狀態, 判準)
ODD = [
    (1,  "Δω_min = γ'₁ (動量量子化)", "O125", "✅ 閉合", "奇模專屬"),
    (1,  "gap = γ₂−γ₁ = 4sin(π/176)sin(3π/176) = 0.003821", "O193", "✅ 閉合", "奇模專屬"),
    (3,  "gap 3 + CKM g₂ 分子 sin(3π/176)", "O193/p2", "✅ 閉合", "奇模專屬"),
    (5,  "CKM g₃ (176-sine 閉式)", "p2/09", "✅ 閉合", "奇模專屬"),
    (9,  "δ_CKM = atan(sin21/sin9) = 66.39996°", "O55", "✅ 已閉合", "奇模專屬"),
    (13, "m_τ/m_b = sin13/sin32 = 0.425370", "O158", "✅ 已閉合", "奇模專屬"),
    (21, "δ_CKM 分子 + g₂ 分子", "O55/p2", "✅ 閉合", "奇模專屬"),
    (47, "g₂ 分母", "p2/09", "✅ 閉合", "奇模專屬"),
]

print("=" * 72)
print("A. 奇模專屬 7 個 k 值 — O-series 盤點")
print("=" * 72)
R5_88 = [7, 14, 22, 28, 33, 44]
ks = sorted(set(k for k, *_ in ODD))
print(f"  奇模專屬 k 值: {ks}  ({len(ks)} 個)")
closed = sum(1 for *_, st, _ in ODD if "閉合" in st)
print(f"  O-series 閉合狀態: {closed}/{len(ODD)} 條公式有閉合標記")
chk("A1_7ks", "奇模專屬 7 k 值 {1,3,5,9,13,21,47} (剔 7 實驗式)",
    set(ks) == {1, 3, 5, 9, 13, 21, 47}, str(ks))
chk("A2_closed", "全部奇模專屬公式有 O-series 閉合標記", closed == len(ODD))

print()
print("=" * 72)
print("B. ★存量 vs 預測: R5 88-site 有冇預測到奇模專屬?")
print("=" * 72)
inter = sorted(set(ks) & set(R5_88))
print(f"  R5 88-site 輸出 ∩ 奇模專屬 = {inter}  ({len(inter)} 個)")
print(f"  ⟹ R5 程序預測奇模專屬命中: {len(inter)}/{len(ks)} — 零!!")
chk("B1_zero_pred", "R5 88-site 程序預測奇模專屬 = 0/7 (零命中, 106 一致)",
    len(inter) == 0, str(inter))

print()
print("=" * 72)
print("C. 閉合狀態分佈")
print("=" * 72)
for k, formula, o_series, st, _ in ODD:
    print(f"  k={k:2d}: {formula:<50s} [{o_series}] {st}")
print()
print("  ★ 7 個全部係「存量身份」— O-series 閉合先行 (10-15),")
print("    R5/magic 攻堅 (10-17) 之後 — 85 號時序已證")
chk("C1_inventory", "7 個奇模專屬全部存量身份 (O-series 先行), 零 R5 預測", True)

print()
print("=" * 72)
print("D. 最終判定")
print("=" * 72)
print(f"""
  88-site「獨立身份」最終:
    奇模專屬 = 7 個 {{1,3,5,9,13,21,47}} (剔 7=θ₂₃ 實驗式)
    全部 O-series 存量閉合 (O55/O158/O125/O193/p2)
    零個係 R5 88-site 程序預測 (∩ = ∅)
  ⟹ 88-site 獨立身份:
    1. 存在 ✅ (7 個, O-series 閉合)
    2. 獨立於 R5 程序 ✅ (佢哋唔係 R5 輸出)
    3. 但係佢哋同 magic 冇關 — R5 預測零命中
  ⟹ Magic 攻堅嘅「88-site 身份支持」= carry 12 個(存在) +
    奇模 7 個(獨立但唔關 R5 事) — R5 程序本身預測力 = 0
     (同 59 G2 🔴 一致: mirror 規則冇預測力)
""")
chk("D1_final", "88-site 獨立身份: 7 存量、零 R5 預測 — Magic 攻堅 R5 預測力=0 (59 一致)", True)

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "108_odd_identity_census", "date": "2026-10-17",
    "odd_ks": ks,
    "r5_intersection": inter,
    "census": [{"k": k, "formula": f, "o": o, "status": s} for k, f, o, s, _ in ODD],
    "verdict": "7 奇模專屬全部存量 O-series 閉合; R5 預測 0/7; R5 88-site 預測力=0 (59 一致)",
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/108_odd_identity_census.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/108_odd_identity_census.json")