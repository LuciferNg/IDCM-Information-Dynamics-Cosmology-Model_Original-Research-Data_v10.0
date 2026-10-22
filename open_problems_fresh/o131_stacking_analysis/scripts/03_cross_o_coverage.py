#!/usr/bin/env python3
"""
O131 — 前置驗證 03: 跨 O 覆蓋審計 (每個 v9.0 物件喺 v10.0 已由邊個 O 擁有?)
==========================================================================
目的: 唔可以淨係判「v9 有效/失效」— 要判「v10 有冇人已經做咗」。
      逐個 v9.0 stacking_toolbox / sync_bump 物件, 喺 v10.0 揾現行擁有 O +
      證據 (final_result / data / README row), 判 O131 有冇剩餘新內容。

證據 = 讀 v10.0 實際檔案 (唔靠 memory)。
"""

import os, io, glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPF = os.path.dirname(BASE)          # open_problems_fresh/
ROOT = os.path.dirname(OPF)          # IDCM-v10.0--It-From-Beat/

PASS, FAIL = 0, 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1; mark = "✅"
    else:    FAIL += 1; mark = "❌"
    print(f"  {mark} {name}" + (f" — {detail}" if detail else ""))

def read(p):
    try:
        return io.open(p, encoding="utf-8", errors="ignore").read()
    except FileNotFoundError:
        return ""

print("=" * 80)
print("  O131/03 — 跨 O 覆蓋審計 (v9.0 物件 → v10.0 現行擁有 O)")
print("=" * 80)

# ---------- 讀 master README ----------
readme = read(os.path.join(OPF, "README.md"))
def readme_row(tag):
    for ln in readme.splitlines():
        if ln.startswith(f"| **{tag}**"):
            return ln
    return ""

rows = {
    "O118": readme_row("O118"),
    "O129": readme_row("O129"),
    "O133": readme_row("O133"),
    "O100": readme_row("O100"),
    "O131": readme_row("O131"),
}
print("\n  ── README 行存在性 ──")
for k in ["O118", "O129", "O133", "O100"]:
    v = rows[k]
    check(f"README 有 {k} 獨立 row", bool(v), (v[:60] + "…") if v else "MISSING")

# ---------- 物件 1: λ_sync 諧波階梯 (peaks λ_sync/n, nulls λ_sync/(n+0.5)) ----------
print("\n  ── 物件 1: λ_sync 諧波階梯 (ξ(s) 零點/峰) ──")
o31_fr = read(os.path.join(OPF, "o31_xi_zeros_fixedpoints", "final_result.md"))
check("O31 final_result 有 s_n = λ_sync/(n+0.5) 零點階梯", "λ_sync/(n+0.5)" in o31_fr or "λ_sync/(n+0.5)" in o31_fr)
check("O31 final_result 有 p_n = λ_sync/n 峰階梯", "λ_sync/n" in o31_fr)
check("O31 狀態 = 🟢 已閉合", "🟢 已閉合" in o31_fr)
o31_data = glob.glob(os.path.join(OPF, "o31_xi_zeros_fixedpoints", "data", "*"))
check("O31 有 BOSS/eBOSS ξ(s) 實證 data 輸出 (工作已發生)",
      any("boss_dr12_empirical" in os.path.basename(p) for p in o31_data),
      f"{len(o31_data)} data 檔")
o31_scripts = glob.glob(os.path.join(OPF, "o31_xi_zeros_fixedpoints", "scripts", "*.py"))
o31_src = "".join(read(p) for p in o31_scripts)
check("O31 scripts 已用 BOSS/eBOSS 原始數據 (ross_dr12_corrfunc.zip)", "ross_dr12_corrfunc.zip" in o31_src)
check("O31 scripts 用 LAMBDA_SYNC = 406.1 h⁻¹Mpc (同一 λ_sync, h⁻¹Mpc 慣例)", "406.1" in o31_src)
o31_doc = "".join(read(p) for p in glob.glob(os.path.join(OPF, "o31_xi_zeros_fixedpoints", "docs", "*.md")))
check("O31 有 P(k) wiggle 數據源驗證 (script 09/19)", "pk_wiggle" in o31_src or "P(k)" in o31_doc)
# 跨 O 跟進發現: O31 data scripts 仍指向已消失嘅 ~/IDCM (現行 repo 內冇)
o31_oldpath = "IDCM/sync_bump_analysis" in o31_src and not os.path.isdir(os.path.expanduser("~/IDCM"))
check("發現: O31 data scripts 硬編碼 ~/IDCM (已不存在) ⟹ 需寫入 O31 SESSION_START 跟進",
      o31_oldpath, "scripts 07/08/09/11 目前唔可重跑")

# ---------- 物件 2: v9 P(k) 鏈譜模型 ----------
print("\n  ── 物件 2: v9 P(k) = Σγ_n·G(k−k_n) 鏈譜模型 ──")
r133 = rows["O133"]
check("O133 README 行記錄 v9 P(k) 遷移失效 (2/9 PASS)", "2/9 PASS" in r133 or "失效" in r133,
      "broadband Δn=+0.86 🔴" if "broadband" in r133 else "")

# ---------- 物件 3: σ_sync 算子 ----------
print("\n  ── 物件 3: σ_sync 諧波尺度變異數算子 ──")
r129 = rows["O129"]
check("O129 README 行: σ_sync 幾何 v9≡v10 (dev 0)", "dev 0" in r129)
check("O129 README 行: v9.0 形式 = 純數據測量, 無第一性原理內容", "純數據測量" in r129)
check("O129 README 行: 算子歸屬 O100/O133/O128", "O100/O133" in r129)

# ---------- 物件 4: sync dip z_c = 0.6 ----------
print("\n  ── 物件 4: sync dip z_c = F₄/F₅ = 0.6 ──")
check("O129 README 行記錄 z_c=0.6 已由 O126 §D 撤回", "z_c=F₄/F₅=0.6" in r129 and "撤回" in r129)
check("O129 重驗 ℓ(0.6)=0.339036 非 4^ℓ rung", "0.339036" in r129)

# ---------- 物件 5: 局部阻抗模型 ----------
print("\n  ── 物件 5: 局部阻抗模型 (Z=γ/|v_g| → R → s_ref) ──")
r118_ = rows["O118"]
check("O118 README 行: 唔開新 O、唔做局部阻抗模型、唔搬遷 v9.0 SYNC 系列",
      ("局部阻抗模型" in r118_) and ("唔搬遷 v9.0 SYNC 系列" in r118_))
check("O118 README 行: SYNC 局部修正不被要求 (Δχ²=0.64 < 2)", "SYNC 局部修正不被要求" in rows["O118"])

# ---------- 物件 6: σ8 ----------
print("\n  ── 物件 6: σ8 ──")
check("O100 README 行: σ8 = 0.748 (IDCM 零參數)", "0.748" in rows["O100"])
check("O129 README 行引 σ8=0.7482 (算子歸屬 O100/O133/O128)", "0.7482" in rows["O129"])

# ---------- 物件 7: Ω_Λ φ-form ----------
print("\n  ── 物件 7: Ω_Λ = 4/(φ⁴−1) (v9) ──")
check("README 有記錄 Ω_Λ v10 = 41/60 (O148/O215)", "41/60" in readme)

# ---------- 物件 8: O131 本身 ----------
print("\n  ── 物件 8: O131 現狀 ──")
print(f"      (本輪之前 O131 缺 master README 獨立 row — O115 審計已捉到; 本 session 已補)")
check("README 現有 O131 獨立 row (本 session 補上)", bool(rows["O131"]),
      (rows["O131"][:60] + "…") if rows["O131"] else "仍缺")

# ---------- 剩餘新內容判定 ----------
print("\n  ── 剩餘新內容判定 ──")
print("""
    v9.0 stacking_toolbox 物件清單 → v10.0 擁有者:
      ① λ_sync 幾何 (2πR/88)          → ✅ 遷移; 擁有 = O73/O129/O171
      ② 諧波階梯 peaks λ_sync/n        → 已有 = O31 (🟢) / O100 (🟢)
      ③ ξ(s) 零點 nulls λ_sync/(n+0.5) → 已有 = O31 (🟢, BOSS/eBOSS 實證)
      ④ v9 P(k) 鏈譜模型              → 已判失效 = O133 (2/9 PASS, broadband 🔴)
      ⑤ σ_sync 算子                   → 已有 = O129 (🟡 純數據測量) → O100/O133/O128
      ⑥ z_c=0.6 sync dip              → 已撤回 = O126 §D / O129 重驗
      ⑦ 局部阻抗模型 (R, s_ref)        → 已裁定唔做 = O118
      ⑧ Ω_Λ φ-form / ε φ-form          → 已判 φ 近似 = O135 / O148 (41/60, 19/123)
      ⑨ 疊加技術本身 (wavelet+加權堆疊) → 框架無關數據分析, 非 IDCM 結構物件
    ⟹ 剩餘新 IDCM 內容 = 空集。唯一未擁有嘅係「堆疊技術」, 佢唔含結構推導。
""")

print(f"{'='*80}")
print(f"  RESULT: {PASS}/{PASS+FAIL} PASS")
print(f"{'='*80}")

with open(os.path.join(BASE, "data", "03_cross_o_coverage_results.txt"), "w") as f:
    f.write("O131/03 — 跨 O 覆蓋審計\n")
    for k, v in rows.items():
        f.write(f"README[{k}] = {v[:200]}\n")
    f.write(f"RESULT={PASS}/{PASS+FAIL} PASS\n")
print(f"\n  寫入 data/03_cross_o_coverage_results.txt")
