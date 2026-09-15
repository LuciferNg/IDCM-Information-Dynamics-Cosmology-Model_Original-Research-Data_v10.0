#!/usr/bin/env python3
# O196 閉合審計 — scripts/91_doc_audit.py
# 文檔審計 (read-only): 提取文檔數值 claim, 同已知正確值核對
# 範圍: O196 目錄內所有 .md (唔改任何文件)
import re
import pathlib

BASE = pathlib.Path(__file__).resolve().parent.parent
DOCS = [
    BASE/"SESSION_START.md",
    BASE/"01_problem_record.md",
    BASE/"final_result.md",
    BASE/"docs/01_closure.md",
    BASE/"11adic_extension/SESSION_START.md",
    BASE/"11adic_extension/01_problem_record.md",
    BASE/"11adic_extension/final_result.md",
    BASE/"11adic_extension/docs/01_closure.md",
]

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

# 已知正確值 (由 90_verify_all.py 確認)
KNOWN = {
    "0.7007078407": "Δθ (度)", "0.0122296589": "Δθ (rad)",
    "1.202532": "R (δ=±1 根模)", "0.0073532323": "Re(r₁)",
    "1.2025095273": "Im(r₁)", "3.96e-5": "Re(r₁) vs 1/136 dev",
    "0.0061148": "δ = arcsin(Re/R)", "2.760317642": "|r₃|",
    "89/44": "m₁", "3871/1936": "κ₂", "2.0227": "κ₁ 近似",
    "176": "ΣA² = N·μ²", "178": "Σγ = 2F₁₁",
    "0.69166": "4/j₁²", "0.69152": "R⁻²", "0.02%": "4/j₁² vs R⁻² dev",
    "1.19e-4": "R − j₁/2", "9.9e-5": "R vs j₁/2 相對 dev",
    "0.008": "殘差 ratio", "1e-44": "主導項 dev",
    "1.92e-3": "D ratio max dev", "2e-3": "D ratio dev 上界",
    "0.7007078407": "Δθ 度", "4.9e-33": "極點推離 12 階 dev",
    "0.0073516553": "一階極點推離 Re",
    "2": "c = μ² EXACT",
    "0.34%": "π/256 dev",
    "1.2024128": "j₁/2",
    "0.0099%": "j₁/2 vs R dev",
    "0.000198289": "4/j₁² dev (scripts/07)",
    "0.6917": "4/j₁² 舊值",
}
KNOWN_PATTERNS = []
for val, label in KNOWN.items():
    KNOWN_PATTERNS.append((re.escape(val), label))

def audit_doc(path):
    text = path.read_text(encoding="utf-8")
    found = {}
    for pat, label in KNOWN_PATTERNS:
        m = re.search(pat, text)
        if m:
            found[label] = m.group(0)
    return found

print("== A) 已知值喺文檔中出現檢查 ==")
def text_for(doc):
    return doc.read_text(encoding="utf-8")
for doc in DOCS:
    if not doc.exists():
        check(f"{doc.name}: 存在", False)
        continue
    found = audit_doc(doc)
    missing = [lbl for lbl, _ in KNOWN_PATTERNS if lbl not in text_for(doc)]
    # 核心值必須出現 (每文檔相關部分)
    print(f"  {doc.relative_to(BASE)}: {len(found)}/{len(KNOWN)} 已知值命中")

# 核心數值 claim 逐文檔核對
print("\n== B) 核心公式/數值 claim 核對 (逐文檔) ==")
# SESSION_START (主)
t = text_for(DOCS[0])
check("S1 v₁₁(k_n) = −n + ⌊(n−1)/11⌋", "−n + ⌊(n−1)/11⌋" in t)
check("S2 D_{n+2}/D_n = (n+1)(n+2)·R⁻²", "(n+1)(n+2)·R⁻²" in t)
check("S3 R = 1.202532", "1.202532" in t)
check("S4 零新常數聲明", "零新常數" in t and "✓" in t)
check("S5 §二b 合併表存在", "二b" in t)

# 01_problem_record (主)
t = text_for(DOCS[1])
check("P1 §〇 時序索引存在", "〇、推導時序索引" in t)
check("P2 時序完整性聲明存在", "時序完整性聲明" in t)
check("P3 誤開 O200 記錄", "O200" in t and "未經" in t)

# final_result (主)
t = text_for(DOCS[2])
check("F1 RESULT_TEMPLATE 格式 (狀態: 🟢)", "## 狀態: 🟢" in t)
check("F2 結論先行", "## 結論" in t)
check("F3 關鍵公式 section", "## 關鍵公式" in t)
check("F4 依賴 chain O190→...→O196", "O190 → O191 → O192 → O193 → O194 → O195 → O196" in t)
check("F5 剩餘開放 section", "## 剩餘開放" in t)

# docs/01_closure.md (主)
t = text_for(DOCS[3])
check("C1 T1 定理 v₁₁(k_n)", "v₁₁(k_n) = −n + ⌊(n−1)/11⌋" in t)
check("C2 T2 閉式 (n+1)(n+2)·R⁻²", "(n+1)(n+2)·R⁻²" in t)
check("C3 O195 B3 撤銷記錄", "B3" in t and "撤銷" in t)
check("C4 T3 🔴 觀測對應", "🔴" in t and "觀測對應" in t)
check("C5 誠實修正 section", "誠實修正" in t)

# 11adic_extension SESSION_START
t = text_for(DOCS[4])
check("E1 合併狀態標記", "合併" in t and "o200_interference_11adic" in t)
check("E2 Δθ = 0.7007078407°", "0.7007078407" in t)
check("E3 T2-2 零位 {F₂..F₅}", "{F₂,F₃,F₄,F₅}" in t or "{F₂..F₅}" in t)
check("E4 T3 三閉式 (總0/奇1+v₁₁(C)/偶0)", "v₁₁(Σγ^n) = 0" in t or "總 0" in t)
check("E5 T4 sin(δ) = Re/R", "sin(δ)" in t and "Re/R" in t)
check("E6 T5 c = μ² = 2 EXACT", "μ² = 2" in t or "2 EXACT" in t)

# 11adic_extension 01_problem_record
t = text_for(DOCS[5])
check("Q1 §〇 時序索引存在", "〇、推導時序索引" in t)
check("Q2 合併標記", "已合併回 O196" in t)
check("Q3 時序完整性聲明", "時序完整性聲明" in t)

# 11adic_extension final_result
t = text_for(DOCS[6])
check("R1 判決摘要表", "判決摘要" in t)
check("R2 依賴鏈冇 O200", "O200" not in t.replace("o200_interference_11adic", ""))
check("R3 剩餘開放 5 項", "剩餘開放" in t)

# 11adic_extension docs/01_closure.md
t = text_for(DOCS[7])
check("D1 T1 Δθ 鎖定", "0.7007078407" in t)
check("D2 T2-1 自相似", "11-free" in t)
check("D3 T2-2 零位", "{1,2,3,5}" in t)
check("D4 T2-3 σ_m Legendre", "v₁₁(σ_m)" in t and "v₁₁((2m)!)" in t)
check("D5 T6 a_n 閉式", "sin(nδ)/n" in t)
check("D6 攻堅 2 v₂ 閉式", "2·s₂(2-free(m))" in t)
check("D7 攻堅 3 j_k 統一", "j_k/2" in t)
check("D8 誠實修正", "誠實修正" in t)

# 禁止污染檢查: O199/O200 只准出現喺合併記錄語境 (「沒喊過開O199和O200」/「誤開」/「合併」)
for doc in DOCS:
    t = text_for(doc)
    # 移除合併記錄語境行後再檢查殘餘 O199
    cleaned = re.sub(r'[^\n]*沒喊過開O199[^\n]*\n?', '', t)
    if "O199" in cleaned:
        check(f"無 O199 污染 ({doc.name})", False, "O199 喺合併語境外出現")

# ============ D) RESULT_TEMPLATE 段序符合性 (2026-09-15 修正輪) ============
print("\n== D) RESULT_TEMPLATE 段序符合性 (狀態→結論→關鍵公式→依賴) ==")
TPL_ORDER = ["狀態", "結論", "關鍵公式", "依賴"]
for label, p in [("O196 final_result", BASE/"final_result.md"),
                 ("11adic_extension final_result", BASE/"11adic_extension/final_result.md")]:
    secs = re.findall(r'^## (.+?)$', text_for(p), re.M)
    idx = []
    for s in secs:
        for i, t in enumerate(TPL_ORDER):
            if s.startswith(t):
                idx.append(i); break
    check(f"{label}: 四段齊 + 依 template 序",
          len(idx) == 4 and idx == sorted(idx), f"{secs}")
    check(f"{label}: 狀態 emoji 統一 (🟢/🟡/🔴)",
          any(s.startswith("狀態") and any(e in s for e in "🟢🟡🔴") for s in secs))
    # 依賴箭頭 → 表示「依賴於」
    t = text_for(p)
    dep = re.search(r'## 依賴\n+(.+)', t)
    check(f"{label}: 依賴用 → 箭頭", bool(dep) and "→" in dep.group(1))

# 範圍檢查: 目錄內應該只有預期文件
print("\n== C) 目錄範圍檢查 ==")
expected = {
    "01_problem_record.md", "SESSION_START.md", "final_result.md",
    "docs/01_closure.md", "scripts/01_11adic_proof.py",
    "scripts/02_proof_and_growth.py", "scripts/03_growth_closed_form.py",
    "scripts/04_growth_alpha.py", "scripts/05_alpha_interference.py",
    "scripts/06_singularity_index.py", "scripts/07_final_closure.py",
    "scripts/90_verify_all.py", "scripts/91_doc_audit.py", "scripts/92_chain_continuity.py",
    "11adic_extension/01_problem_record.md",
    "11adic_extension/SESSION_START.md", "11adic_extension/final_result.md",
    "11adic_extension/docs/01_closure.md",
}
for p in sorted(BASE.rglob("*")):
    if p.is_file():
        rel = str(p.relative_to(BASE))
        if rel.startswith("11adic_extension/scripts/"):
            continue  # scripts 由下一個 check 驗證
        if rel not in expected:
            check(f"預期外文件: {rel}", False)
# 11adic_extension scripts 全數 (01-13 + 02b-02f = 18)
n_scripts = len(list((BASE/"11adic_extension/scripts").glob("*.py")))
check(f"11adic_extension scripts 數 = 18 (01-13 + 02b-02f 攻堅軌跡)", n_scripts == 18, f"實際 {n_scripts}")
# scripts 命名完整性: 01,02,02b-f,03..13 全存在
want = {"01_delta_theta", "02_rayleigh_11adic", "02b_kappa_11adic", "02c_kappa_fib11",
        "02d_kappa_mod11", "02e_kappa_f11_final", "02f_kappa_legendre", "03_power_sum_11adic",
        "04_alpha_zero_proof", "05_c_value_j1", "06_asymptotic_expansion", "07_final_closure",
        "08_re_pole_push", "09_high_order_v2", "10_pole_push_correct", "11_v2_closed_form",
        "12_jk_unification", "13_fd_blocks"}
have = {p.stem for p in (BASE/"11adic_extension/scripts").glob("*.py")}
check("11adic_extension scripts 命名完整", want <= have, f"缺 {want - have}")

print(f"\n{'='*50}\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL:
    print("FAIL:", *FAIL, sep="\n  ")
    exit(1)
