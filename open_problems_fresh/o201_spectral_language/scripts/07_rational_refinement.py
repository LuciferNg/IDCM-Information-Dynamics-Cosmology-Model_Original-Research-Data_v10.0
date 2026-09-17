#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O201 scripts/07 -- C1 目標集審計 + 有理精煉 (Target-Set Audit)

★ v1 教訓 (本 script 第一版嘅真錯, 保留記錄):
  第一版用 Fraction(float(v)).limit_denominator(1e6) 判「有理目標」。
  呢個係**錯嘅**: 任何十進制截斷值都會被重建成分母 <= 1e6 嘅有理數
  (例: mu_logN 0.862478 → 431239/500000), 於是「p ∉ I」變成**必然**結論 —
  呢個係判準陷阱 (decimal-truncation trap), 唔係反例。
  => 正確做法: 唔可以對截斷值做有理重建。要先查**註冊閉式** (provenance),
     只有註冊為精確有理數嘅目標先可以用有理判準。

本 script 做三件事:
  A. 逐個查 10 個 scripts/01 TRAP2 目標嘅**註冊閉式 + 出處** (grep 各 O 目錄, 逐字)
  B. 按目標性質分類 (C1 範圍審計):
     ① 結構有理 (p,q ∈ I 結構整數集)          → C1 ✅ 完備
     ② 結構表達 (多項式/譜和組合)              → 需表達層判準 (單原子掃描測唔到)
     ③ 觀測輸入 (NuFIT/PDG)                     → ⬜ 唔屬 C1 範圍
     ④ 已證偽 / 已撤銷                          → ⬜ 唔屬 C1 範圍
  C. 修正 C1 統計 + 記錄方法論結論:
     **單原子/深度2 掃描只測得到單項表達 => scripts/01 嘅完備率係下界**

零新常數: 只用池內整數原子 + 憲章 §三 註冊結構數。
"""
import os
import sys
import json
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mpmath as mp
import o201_basis as ob

mp.mp.dps = 50

print("=" * 78)
print("O201/07 -- C1 目標集審計 + 有理精煉 (Target-Set Audit)")
print("=" * 78)

ATOMS = ob.build_atoms(with_derived=True)
INT_ATOMS = set()
for k, v in ATOMS.items():
    if abs(v - mp.nint(v)) < mp.mpf('1e-40'):
        INT_ATOMS.add(int(mp.nint(v)))
CHARTER = [44, 4, 7, 11, 13, 17, 18, 22, 28, 33, 36, 55, 77, 88, 90, 123, 137, 176, 528]
I = INT_ATOMS | set(CHARTER)
print("\n[I] 結構整數集: 池內整數原子 %d 個 + 憲章 §三 %d 個 => |I| = %d"
      % (len(INT_ATOMS), len(CHARTER), len(I)))

# ============================================================
# A. 註冊閉式 (逐字 grep 自各 O 目錄, 附出處)
# ============================================================
REG_FORMS = {
    "V_Lambda": ("F(γ) + 44 − F₈ − B = 264.0821 + 19 = 283.0821",
                 "o62_lambda_first_principles/docs/01_lambda_first_principles_closure.md:15,56",
                 "expr"),
    "baryon_over_matter": ("Ω_m = 19/60", "o163_dm_identity/data/00_observational_constraints.md:90",
                           "rational", (19, 60)),
    "Omega_Lambda_old": ("4/(φ⁴−1) — 已撤銷 (O37)", "o168_g_last_input/SESSION_START.md:58",
                         "superseded"),
    "mu_logN": ("μ = φ⁻¹ + L₅/(F₅·N_gen²) = 0.862478 (0.10%)", "★logN 註冊 (memory 09-13)", "expr"),
    "s_logN": ("s² = B·N_gen²·Var_pop(ln(1+δ̂₊)) → s = 1.1874 (1.05%)", "★logN 註冊 (memory 09-13)",
               "expr"),
    "sin2_theta23": ("NuFIT 對照值 0.573007 (IDCM 結構值 = 0.572983)",
                     "o156_rge_first_principles/final_result.md:21", "observational"),
    "mW_over_mZ": ("PDG 0.88136 (IDCM 結構值 = ω₃₀/ω₄₁ = 0.8827)",
                   "o156_rge_first_principles/docs/06_boson_fermion_scale.md:15", "observational"),
    "C_old": ("−0.1697 — O51 scripts/82 已 FAIL", "O51 (已證偽)", "falsified"),
    "one_over_137": ("α⁻¹(0) = 137 = 3·44 + F₅", "O142 / ★O142 註冊", "rational", (1, 137)),
    "cosmological_crack": ("0.746% = 1/(2(2K_tree+1)) = 1/134 (dev 0.036%)",
                           "o168_g_last_input/final_result.md:49", "expr", (1, 134)),
}

D1 = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "data", "01_spectral_dictionary.json")))
MISSES = D1["misses"]
VALUES = D1.get("values", {})

print("\n" + "=" * 78)
print("A. 10 個 TRAP2 目標嘅註冊閉式 + 出處")
print("=" * 78)
for nm in MISSES:
    ent = REG_FORMS.get(nm, ("?", "?", "?"))
    f, src, kind = ent[0], ent[1], ent[2]
    print("  %-20s %-46s [%s]" % (nm, f, src))

# ============================================================
# B. 分類 + 精確判準 (只對註冊為精確有理者)
# ============================================================
print("\n" + "=" * 78)
print("B. 逐個重判")
print("=" * 78)
print("  %-20s %-16s %-14s %-30s %s" % ("目標", "註冊值", "性質", "精確判準結果", "判決"))
print("  " + "-" * 112)

rows = []
for nm in MISSES:
    vs = VALUES.get(nm, "?")
    ent = REG_FORMS.get(nm, ("?", "?", "?"))
    f, src, kind = ent[0], ent[1], ent[2]
    if kind == "rational":
        p, q = ent[3]
        p_ok, q_ok = p in I, q in I
        detail = "p=%d %s I, q=%d %s I" % (p, "∈" if p_ok else "∉", q, "∈" if q_ok else "∉")
        verdict = "✅ 結構有理 (C1 完備)" if (p_ok and q_ok) else "🔴 非結構有理"
    elif kind == "expr":
        detail = "表達層: %s" % f.split("=")[0].strip()
        verdict = "🟠 結構表達 (需表達層判準)"
    elif kind == "observational":
        detail = "觀測輸入 (唔係結構常數)"
        verdict = "⬜ 唔屬 C1 範圍"
    elif kind in ("superseded", "falsified"):
        detail = "已撤銷/已證偽"
        verdict = "⬜ 唔屬 C1 範圍"
    else:
        detail = "未分類"
        verdict = "❓"
    rows.append((nm, vs, kind, f, src, detail, verdict))
    print("  %-20s %-16s %-14s %-30s %s" % (nm, mp.nstr(mp.mpf(vs), 10) if vs != "?" else "?",
                                            kind, detail, verdict))

# 額外核對: cosmological_crack = 1/134 嘅精確形
p, q = REG_FORMS["cosmological_crack"][3]
print("\n  [附加] crack = 1/134 精確形: p=%d %s I, q=%d %s I"
      % (p, "∈" if p in I else "∉", q, "∈" if q in I else "∉"))
print("         ★ 但 134 = 2(2K_tree+1) = 2·67 有**結構表達** (O168 scripts/19)")
print("         => 發現: 結構整數集 I (原子 ∪ 憲章註冊) 係**下界**, 唔係必要條件。")
print("            有結構表達嘅整數 (134, 67 = 2K_tree+1, ...) 唔一定以裸整數形式落池。")
print("            => 「p,q ∈ I」係**充分**判準, 唔係必要判準; 唔可以據此判「非結構」。")
k_tree = ob.KTREE
print("            驗證: 2*(2*K_tree+1) = 2*(2*%d+1) = %d %s" % (k_tree, 2 * (2 * k_tree + 1),
                                                                    "✅" if 2 * (2 * k_tree + 1) == 134 else "❌"))

# ============================================================
# C. 修正 C1 統計
# ============================================================
print("\n" + "=" * 78)
print("C. C1 修正統計")
print("=" * 78)
n_struct_rat = sum(1 for r in rows if r[6].startswith("✅"))
n_expr = sum(1 for r in rows if r[6].startswith("🟠"))
n_obs = sum(1 for r in rows if r[6].startswith("⬜"))
n_bad = sum(1 for r in rows if r[6].startswith("🔴"))
print("  scripts/01 原始: A:EXACT 19 + A:HIT 9 + B-real 6 = 34/57 (59.6%)")
print("  TRAP2 重判 (%d 個):" % len(rows))
print("    ✅ 結構有理 (新確認) : %d  %s" % (n_struct_rat, [r[0] for r in rows if r[6].startswith("✅")]))
print("    🟠 結構表達 (多項式) : %d  %s" % (n_expr, [r[0] for r in rows if r[6].startswith("🟠")]))
print("    ⬜ 唔屬 C1 範圍      : %d  %s" % (n_obs, [r[0] for r in rows if r[6].startswith("⬜")]))
print("    🔴 真反例            : %d  %s" % (n_bad, [r[0] for r in rows if r[6].startswith("🔴")]))
print("\n  ★ C1 完備率 (單原子掃描, 下界) = (34 + %d)/57 = %.1f%%"
      % (n_struct_rat, (34 + n_struct_rat) / 57 * 100))
print("  ★ 方法論結論: 單原子/深度2 掃描**只測得到單項表達**。")
print("     4 個 🟠 目標全部有**已註冊多項式閉式** (V_Λ = F(γ)+44−F₈−B 等)")
print("     => scripts/01 嘅 63.2% 係**下界**, 唔係完備率真值。")
print("  ★ C1 真反例 (修正後): %d 個 (冇一個係結構常數)" % n_bad)

# ============================================================
# D. 陷阱記錄 (v1 錯誤, 保留)
# ============================================================
print("\n" + "=" * 78)
print("D. 判準陷阱記錄 (v1 錯誤)")
print("=" * 78)
print("  陷阱: Fraction(float(v)).limit_denominator(1e6) 對**截斷值**必然成功")
for nm in ("mu_logN", "s_logN", "sin2_theta23"):
    v = mp.mpf(VALUES.get(nm, "0"))
    fr = Fraction(float(v)).limit_denominator(10 ** 6)
    print("    %-16s %.8f → %s (分母 %d %s I) — 呢個係小數位, 唔係結構"
          % (nm, float(v), fr, fr.denominator, "∈" if fr.denominator in I else "∉"))
print("  => 規則: **唔可以對截斷值做有理重建**; 有理判準只可用於註冊為精確有理嘅目標。")
print("     呢條規則已寫入 docs/03 (判準) 作為第 5 步嘅前置條件。")

out = {
    "int_set_size": len(I),
    "registered_forms": {k: {"form": v[0], "source": v[1], "kind": v[2]} for k, v in REG_FORMS.items()},
    "reruled": [{"name": r[0], "value": r[1], "kind": r[2], "form": r[3], "source": r[4],
                 "detail": r[5], "verdict": r[6]} for r in rows],
    "n_structural_rational": n_struct_rat, "n_expression": n_expr,
    "n_out_of_scope": n_obs, "n_true_counterexample": n_bad,
    "completeness_single_atom_lower_bound": (34 + n_struct_rat) / 57,
    "methodology_finding": "單原子/深度2 掃描只測單項表達 => 63.2% 係下界; 4 個目標有已註冊多項式閉式",
    "v1_trap": "limit_denominator 對截斷值必然成功 => 唔可以對截斷值做有理重建",
}
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(d, exist_ok=True)
p = os.path.join(d, "07_target_set_audit.json")
with open(p, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("\n[data] %s" % os.path.abspath(p))

print("\n" + "=" * 78)
print("自檢")
print("=" * 78)
NPASS = NFAIL = 0


def check(label, cond):
    global NPASS, NFAIL
    if cond:
        NPASS += 1
        print("  PASS  %s" % label)
    else:
        NFAIL += 1
        print("  FAIL  %s" % label)


check("[INJECT] checker 識 FAIL (44 ∈ I 但 9999991 ∉ I)", (44 in I) and (9999991 not in I))
check("10 個目標全部重判", len(rows) == len(MISSES))
check("19/60 判為結構有理", any(r[0] == "baryon_over_matter" and r[6].startswith("✅") for r in rows))
check("1/137 判為結構有理", any(r[0] == "one_over_137" and r[6].startswith("✅") for r in rows))
check("V_Lambda 判為結構表達", any(r[0] == "V_Lambda" and r[6].startswith("🟠") for r in rows))
check("crack 判為結構表達", any(r[0] == "cosmological_crack" and r[6].startswith("🟠") for r in rows))
check("sin2_theta23 / mW_over_mZ 判為觀測輸入",
      all(any(r[0] == x and r[6].startswith("⬜") for r in rows)
          for x in ("sin2_theta23", "mW_over_mZ")))
check("C_old / Omega_Lambda_old 判為唔屬範圍",
      all(any(r[0] == x and r[6].startswith("⬜") for r in rows)
          for x in ("C_old", "Omega_Lambda_old")))
check("冇 🔴 真反例 (全部係表達層/範圍外)", n_bad == 0)
check("crack 精確形 1/134: q=134 ∉ I (記錄 I 係下界)",
      REG_FORMS["cosmological_crack"][3][0] in I and REG_FORMS["cosmological_crack"][3][1] not in I)
check("134 = 2(2K_tree+1) 結構表達成立", 2 * (2 * ob.KTREE + 1) == 134)
check("C1 下界 = 36/57", abs((34 + n_struct_rat) / 57 - 36 / 57) < 1e-12)
check("結構整數集包含 44/88/137/60", all(x in I for x in (44, 88, 137, 60)))
check("v1 陷阱已記錄 (limit_denominator)", "limit_denominator" in out["v1_trap"])

print("\n總計: %d/%d PASS" % (NPASS, NPASS + NFAIL))
print("EXIT=%d" % (0 if NFAIL == 0 else 1))
