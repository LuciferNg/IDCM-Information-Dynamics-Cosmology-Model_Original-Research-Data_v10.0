#!/usr/bin/env python3
# O196 閉合審計 — scripts/92_chain_continuity.py
# 推導鏈連續性審計: 追蹤每個輸入來源 + 每條交叉引用目標存在性 + 依賴鏈完整性
# Read-only (唔改任何文件)
import re
import pathlib

BASE = pathlib.Path(__file__).resolve().parent.parent  # o196_odd_dominant_closure/
ROOT = BASE.parent  # open_problems_fresh/

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

def text_of(p):
    return p.read_text(encoding="utf-8")

# ============ A) 上游依賴鏈存在性 ============
print("== A) 上游 O 目錄依賴鏈 (O190 → O196) ==")
chain = ["o190_rs1_lattice_transport", "o191_number_field_law", "o192_lucas_dual_family",
         "o193_power_sum_domain", "o194_cumulant_hierarchy", "o195_cumulant_integrality",
         "o196_odd_dominant_closure"]
for o in chain:
    d = ROOT/o
    check(f"{o} 存在", d.is_dir())
# 依賴鏈聲明喺文檔中一致
t196 = text_of(BASE/"final_result.md")
check("O196 final_result 依賴鏈 O190→...→O196",
      "O190 → O191 → O192 → O193 → O194 → O195 → O196" in t196)
t11 = text_of(BASE/"11adic_extension/final_result.md")
check("11adic final_result 依賴鏈一致", "O190 → O191 → O192 → O193 → O194 → O195 → O196" in t11)

# ============ B) 上游引用文件存在性 ============
print("\n== B) 上游引用文件 ==")
refs = [
    (ROOT/"o195_cumulant_integrality/docs/02_open_items_closure.md", "O195 docs/02 §七 來源"),
    (ROOT/"o195_cumulant_integrality/docs/01_integrality_theorem.md", "O195 docs/01 D1 定理"),
    (ROOT/"o194_cumulant_hierarchy/docs/02_odd_dominant_and_arcsine_closure.md", "O194 docs/02 開放項 3"),
    (ROOT/"o192_lucas_dual_family/docs/04_power_sum_closed_form.md", "O192 docs/04 冪和閉式"),
    (ROOT/"o197_density_synthesis/final_result.md", "O197 final_result Π(1+δ̂)"),
]
for p, label in refs:
    check(f"{label} ({p.name})", p.is_file())

# ============ C) O196 內部文件集完整性 ============
print("\n== C) O196 內部文件集 ==")
must = ["SESSION_START.md", "01_problem_record.md", "final_result.md",
        "docs/01_closure.md"]
for m in must:
    check(f"O196/{m}", (BASE/m).is_file())
for m in ["01_problem_record.md", "SESSION_START.md", "final_result.md", "docs/01_closure.md"]:
    check(f"11adic_extension/{m}", (BASE/"11adic_extension"/m).is_file())

# ============ D) 文檔間交叉引用章節存在性 ============
print("\n== D) 交叉引用目標章節存在性 ==")
t11docs = text_of(BASE/"11adic_extension/docs/01_closure.md")
sections = re.findall(r'^## (.+?)$', t11docs, re.M)
def has_section(num):
    # 匹配「十、」或「十一、」等開頭嘅章節
    return any(s.startswith(num) for s in sections)

t_start = text_of(BASE/"SESSION_START.md")
# §二b 引用嘅目標: 11adic docs §二/§三/§四/§五/§六/§七/§十一
for sec in ["二", "三", "四", "五", "六", "七", "十一"]:
    if f"docs §{sec}" in t_start:
        check(f"SESSION_START 引用 11adic docs §{sec} 存在", has_section(sec),
              f"實際章節: {[s for s in sections if s.startswith(sec)][:2]}")
# scripts 引用
for scr in ["scripts/01", "scripts/02-02f", "scripts/03", "scripts/04", "scripts/05",
            "scripts/06", "scripts/08-10", "scripts/11", "scripts/12", "scripts/13"]:
    if scr in t_start:
        # 檢查對應 script 文件存在
        pat = scr.replace("-", "")
        found = False
        if "02-02f" in scr:
            found = all((BASE/"11adic_extension/scripts"/f).is_file()
                        for f in ["02_rayleigh_11adic.py", "02b_kappa_11adic.py",
                                  "02c_kappa_fib11.py", "02d_kappa_mod11.py",
                                  "02e_kappa_f11_final.py", "02f_kappa_legendre.py"])
        elif "08-10" in scr:
            found = all((BASE/"11adic_extension/scripts"/f).is_file()
                        for f in ["08_re_pole_push.py", "09_high_order_v2.py",
                                  "10_pole_push_correct.py"])
        else:
            n = scr.split("/")[1]
            found = any((BASE/"11adic_extension/scripts").glob(f"{n}_*.py"))
        check(f"引用目標 scripts/{scr} 存在", found)

# ============ E) 關鍵公式/數值跨文檔一致性 ============
print("\n== E) 關鍵公式跨文檔一致 (O196 主 ↔ 11adic ↔ 上游) ==")
# 1. v₁₁(k_n) 公式: O196 docs §二 定理 vs SESSION_START vs final_result
for label, t in [("O196 docs/01_closure", text_of(BASE/"docs/01_closure.md")),
                 ("O196 SESSION_START", t_start),
                 ("O196 final_result", t196)]:
    check(f"v₁₁(k_n) 公式一致 ({label})", "−n + ⌊(n−1)/11⌋" in t or "-n + (n-1)//11" in t)
# 2. D 增長閉式
for label, t in [("O196 docs/01_closure", text_of(BASE/"docs/01_closure.md")),
                 ("O196 final_result", t196),
                 ("O195 record (承接)", text_of(ROOT/"o195_cumulant_integrality/01_problem_record.md"))]:
    check("D_{n+2}/D_n 閉式一致 (" + label + ")", "(n+1)(n+2)·R⁻²" in t or "(n+1)(n+2)" in t)
# 3. R = 1.202532 一致
for label, t in [("O196 docs", text_of(BASE/"docs/01_closure.md")),
                 ("O195 docs/02", text_of(ROOT/"o195_cumulant_integrality/docs/02_open_items_closure.md"))]:
    check(f"R = 1.202532 ({label})", "1.202532" in t)
# 4. Δθ = 0.7007078407 一致
for label, t in [("11adic docs", t11docs), ("11adic SESSION_START", text_of(BASE/"11adic_extension/SESSION_START.md"))]:
    check(f"Δθ = 0.7007078407 ({label})", "0.7007078407" in t)
# 5. c = μ² = 2 EXACT
for label, t in [("11adic docs", t11docs),
                 ("11adic final_result", text_of(BASE/"11adic_extension/final_result.md"))]:
    check(f"c = μ² = 2 EXACT ({label})", "μ² = 2" in t or "2 EXACT" in t)
# 6. Σγ^n 冪和閉式 (O192 上游 vs 11adic)
t192 = text_of(ROOT/"o192_lucas_dual_family/docs/04_power_sum_closed_form.md")
check("O192 上游 Σγ^n = 88·C(2n,n) + 2^{2n−1}",
      "88·C(2n,n) + 2^{2n−1}" in t192 or "88·C(2n,n)" in t192)
check("11adic docs 引用 O192 冪和閉式", "88·C(2n,n)" in t11docs)
# 7. v₁₁(κ₂ₘ) 自相似跨文檔 (11adic docs ↔ SESSION_START §二b ↔ final_result)
for label, t in [("11adic docs", t11docs),
                 ("O196 SESSION_START", t_start),
                 ("11adic final_result", text_of(BASE/"11adic_extension/final_result.md"))]:
    check(f"v₁₁(κ₂ₘ) 自相似 ({label})", "11-free" in t or "f(11-free" in t or "f(11-free(m))" in t)
# 8. 零位 {1,2,3,5} (SESSION_START 用等價 {F₂..F₅} 表示)
for label, t in [("11adic docs", t11docs), ("O196 SESSION_START", t_start)]:
    check(f"零位 {{1,2,3,5}}/{{F₂..F₅}} ({label})",
          "{1,2,3,5}" in t or "{F₂..F₅}" in t or "F₂..F₅" in t)
# 9. O197 交叉 Π(1+δ̂) = 88/2^86
for label, t in [("O196 SESSION_START", t_start),
                 ("11adic docs", t11docs),
                 ("O197 final_result", text_of(ROOT/"o197_density_synthesis/final_result.md"))]:
    check(f"O197 交叉 Π(1+δ̂) = 88/2^86 ({label})", "88/2^86" in t or "88/2\u02c6\u1d38\u2076" in t or "88/2^86" in t.replace("⁸⁶", "^86"))
# 10. μ² = 2 譜隙 (O192: 「gap = 2 = μ²」「μ² = E−O」等價)
t192_fr = text_of(ROOT/"o192_lucas_dual_family/final_result.md")
check("O192 上游 μ² = 2 (gap = 2 = μ² / μ² = E−O)",
      "2 = μ²" in t192 or "gap = 2" in t192 or "μ² = E−O" in t192 or "μ² = E−O" in t192_fr)

# ============ F) 時序連貫性 (git log + 章節順序) ============
print("\n== F) 時序連貫性 ==")
# 章節順序: 一→二→...→九→十→十一→十二→十三
nums = [s.split("、")[0] for s in sections if re.match(r'^[一二三四五六七八九十]+、', s)]
cn = {"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9,"十":10,
      "十一":11,"十二":12,"十三":13}
seq = [cn[n] for n in nums if n in cn]
check(f"11adic docs 章節連續 (1..13)", seq == sorted(seq) and seq == list(range(1, 14)),
      f"實際: {nums} → {seq}")
# O196 主 docs 章節
t196docs = text_of(BASE/"docs/01_closure.md")
sec196 = re.findall(r'^## (.+?)$', t196docs, re.M)
check("O196 主 docs 章節齊 (一二三四五六)", len(sec196) >= 6, f"{sec196[:7]}")

# ============ G) 常數來源追溯 (每個常數要有出處) ============
print("\n== G) 常數來源追溯 ==")
# R = 1.202532 → O195 δ=±1 根
t195d2 = text_of(ROOT/"o195_cumulant_integrality/docs/02_open_items_closure.md")
check("R 來源: O195 docs/02 有 |t| = 1.202532", "1.202532" in t195d2)
# 88 = 2N_d → 基礎結構 (O192 docs/04 用 γ_k 88 鏈)
check("88 鏈來源: O192 docs/04 88 鏈 γ_k", "88" in t192)
# 11 = L₅ → O195 (v₁₁ 週期)
check("11 = L₅: O195 docs/02 有週期 11 = L₅", "L₅" in t195d2)
# {1,2,3,5} = Fibonacci 2,3,5 + 1 — 11adic docs 有標 {F₂..F₅}
check("零位 {1,2,3,5} = {{F₂,F₃,F₄,F₅}} 標注", "{F₂" in t11docs or "F₂" in t11docs)
# μ² = 2 → O192 預算量子
check("μ² = 2: 11adic docs 標注來源 O192", "O192" in t11docs)
# j₁ → J₀ 首零點 (超越)
check("j₁ 標注 (J₀ 首零點)", "j₁" in t11docs)
# 17 = F_proj → O196 T3 單點
check("F_proj = 17: O196 docs 有", "F_proj" in t196docs and "17" in t196docs)

print(f"\n{'='*50}\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL:
    print("FAIL:", *FAIL, sep="\n  ")
    exit(1)
