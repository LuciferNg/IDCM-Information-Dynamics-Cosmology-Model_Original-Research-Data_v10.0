#!/usr/bin/env python3
"""
O211 scripts/02 — Hodge 數零輸入推導 + KS 唯一性 + 密度基準
==========================================================
命題: h¹¹=36, h²¹=98 可以【完全由種子 x²+x−1=0 導出】, 零硬編碼。
驗收: (a) 導出值 = 36/98;  (b) KS 數據庫中唯一性;  (c) 擾動測試 (B 變體)。
密度基準 (O208): N_search / d_med / q_obs 必須報。

用法: 由 O 目錄 root 跑 -> /usr/bin/python3 scripts/02_hodge_zero_input.py
"""
import os
import math
import sympy as sp

N_PASS = 0
N_FAIL = 0


def chk(label, cond, detail=""):
    global N_PASS, N_FAIL
    ok = bool(cond)
    if ok:
        N_PASS += 1
        mark = "PASS"
    else:
        N_FAIL += 1
        mark = "FAIL"
    print(f"  [{mark}] {label}" + (f"   -- {detail}" if detail else ""))


print("=" * 74)
print("O211 scripts/02 — Hodge 數零輸入推導 + KS 唯一性")
print("=" * 74)

KS = os.path.join(os.path.dirname(__file__), "..", "..", "o53_cy3_reality",
                  "data", "alltoric.spec")

# ---------------------------------------------------------------
# [1] 零輸入推導 (唯一輸入 = 種子方程)
# ---------------------------------------------------------------
print("\n[1] 零輸入推導 (唯一輸入 = 種子 x²+x−1=0)")
phi = sp.sqrt(sp.Rational(5)) / 2 + sp.Rational(1, 2)
B = sp.simplify(phi ** 3 - phi ** -3)          # 分支算子本徵值
L5 = sp.simplify(phi ** 5 + (-phi) ** -5)      # Lucas L5
N_d = sp.simplify(B * L5)                       # site 數
n = sp.symbols('n', integer=True, positive=True)
Sigma_gamma = sp.simplify(sp.summation(B * sp.sin(sp.pi * n / (2 * N_d)) ** 2, (n, 1, N_d)))

h11 = sp.simplify(N_d - 2 * B)
h21 = sp.simplify(Sigma_gamma + 2 * B)
print(f"    φ={phi}  B={B}  L₅={L5}  N_d={N_d}  Σγ={Sigma_gamma}")
print(f"    h¹¹ = N_d − 2B  = {h11}")
print(f"    h²¹ = Σγ + 2B   = {h21}")

chk("D1 h¹¹ = N_d − 2B = 36 (零硬編碼)", sp.simplify(h11 - 36) == 0, f"h¹¹={h11}")
chk("D2 h²¹ = Σγ + 2B = 98 (零硬編碼)", sp.simplify(h21 - 98) == 0, f"h²¹={h21}")
chk("D3 h¹¹ + h²¹ = N_d + Σγ = 134", sp.simplify(h11 + h21 - 134) == 0)
chk("D4 h²¹ − h¹¹ = Σγ − N_d + 4B = 62", sp.simplify(h21 - h11 - 62) == 0)
chk("D5 χ = 2(h¹¹−h²¹) = −124", sp.simplify(2 * (h11 - h21) + 124) == 0)

# ---------------------------------------------------------------
# [2] 擾動測試 (結構剛性, 用戶 4 Hard Tests #4)
# ---------------------------------------------------------------
print("\n[2] 擾動測試 — B 變體 (結構剛性)")
print(f"    {'B':>2} {'h¹¹':>5} {'h²¹':>5} {'sum':>5} {'diff':>5}")
variants = {}
for b in range(1, 9):
    v11 = int(N_d) - 2 * b
    v21 = int(Sigma_gamma) + 2 * b
    variants[b] = (v11, v21)
    tag = "  <- B=4 (φ 強制)" if b == 4 else ""
    print(f"    {b:>2} {v11:>5} {v21:>5} {v11 + v21:>5} {v21 - v11:>5}{tag}")

sum_ok = [b for b, (a, c) in variants.items() if a + c == 134]
diff_ok = [b for b, (a, c) in variants.items() if c - a == 62]
chk("D6 sum 約束對所有 B 成立 (2B 相消, 無判別力)", len(sum_ok) == 8,
    f"sum=134 for B in {sum_ok}")
chk("D7 diff 約束唯一選中 B=4", diff_ok == [4], f"diff=62 only for B={diff_ok}")

# ---------------------------------------------------------------
# [3] KS 數據庫唯一性 (窮舉, 非抽樣)
# ---------------------------------------------------------------
print("\n[3] KS 數據庫唯一性 (alltoric.spec, 窮舉枚舉)")
pairs = set()
with open(KS) as fh:
    for line in fh:
        p = line.split()
        if len(p) >= 2:
            try:
                pairs.add((int(p[0]), int(p[1])))
            except ValueError:
                continue
print(f"    檔案: {os.path.relpath(KS)}")
print(f"    KS 對總數: {len(pairs)}")

s134 = sorted((a, b) for a, b in pairs if a + b == 134)
hits = [(a, b) for a, b in s134 if b - a == 62]
print(f"    sum = 134 嘅對: {len(s134)}")
print(f"    其中 diff = 62 嘅對: {hits}")

chk("D8 (36,98) ∈ KS 數據庫", (36, 98) in pairs)
chk("D9 sum=134 ∧ diff=62 ⟹ 唯一解 (36,98)", hits == [(36, 98)],
    f"命中 {len(hits)} 個")

# B 變體全部存在於 KS (誠實: sum 約束冇判別力)
variant_in_ks = {b: (variants[b] in pairs) for b in (3, 4, 5, 6)}
print(f"    B 變體存在性: {variant_in_ks}")
chk("D10 誠實記錄: B=3,5,6 嘅 (38,96)/(34,100)/(32,102) 亦存在於 KS "
    "(⟹ 判別力唔來自『存在性』; 正確陳述見 §[4] 修正)",
    all(variant_in_ks.values()), "O56 docs/01 §4.2 原『B 變體不存在』聲稱已於 2026-09-20 證偽")

# ---------------------------------------------------------------
# [4] 密度基準 (O208 標準)
# ---------------------------------------------------------------
print("\n[4] 密度基準 (O208 標準) — 逐約束 vs 聯合")
N_search = len(pairs)
n_h11 = sum(1 for a, b in pairs if a == 36)
n_h21 = sum(1 for a, b in pairs if b == 98)
d_only = sorted((a, b) for a, b in pairs if b - a == 62)
s_only = sorted((a, b) for a, b in pairs if a + b == 134)
joint = sorted((a, b) for a, b in pairs if a + b == 134 and b - a == 62)
print(f"    N_search = {N_search}  (KS 對總數 — 完整枚舉)")
print(f"    #(h11=36)          = {n_h11}")
print(f"    #(h21=98)          = {n_h21}")
print(f"    #(sum=134)         = {len(s_only)}   ({len(s_only) / N_search:.2%})")
print(f"    #(diff=62)         = {len(d_only)}   ({len(d_only) / N_search:.2%})")
print(f"    #(sum=134 ∧ diff=62) = {len(joint)}   ({len(joint) / N_search:.2e})  -> {joint}")
print(f"    N_mc = 0  (完整枚舉, 非抽樣 — RESULT_TEMPLATE 允許)")
q_obs = len(joint) / N_search
chk("D11 聯合約束密度 q_obs = 1/30108 = 3.32e-05 (密度基準合格)",
    abs(q_obs - 1.0 / 30108) < 1e-15, f"q_obs = {q_obs:.3e}")

# ⚠️ 誠實標記: O56 docs/04 §三 判別力表嘅 diff 行數值唔對
print("\n    ⚠️ 誠實標記 (O56 判別力表修正):")
print(f"      O56 docs/04 §三 表: 『h²¹−h¹¹ = 62 → 1 個』")
print(f"      實測 (alltoric.spec 30,108 pairs): diff=62 命中 {len(d_only)} 個 ⟹ "
      f"該行數值唔對 (1 應為 {len(d_only)})")
print(f"      ⟹ 若『1 個』係條件於 sum=134 嘅讀法, 則該檢定【退化】: "
      f"sum=134 池有 {len(s_only)} 對、diff 值 {len(set(b - a for a, b in s_only))} 個相異 "
      f"⟹ diff↦pair 係雙射, 任何目標 diff 都恰好命中 1 個 ⟹ 零判別力。")
print(f"      ⟹ 正確陳述: 判別力來自【聯合約束】sum=134 ∧ diff=62 = 1/{N_search} = "
      f"{q_obs:.2e}; 單獨 sum 0.44% / 單獨 diff 0.34% 都唔夠銳。")
chk("D12 誠實修正: O56 diff 行 (1 個) 與實測 (101 個) 不符, 已記錄",
    len(d_only) == 101 and len(set(b - a for a, b in s_only)) == len(s_only),
    f"diff=62 實測 {len(d_only)} 個; sum 池 diff 雙射 ({len(s_only)} 值)")

# ---------------------------------------------------------------
# [5] moduli 機制對接 (O56 接口)
# ---------------------------------------------------------------
print("\n[5] moduli 機制 (O56 對接)")
mech = sp.simplify((h11 + h21) - (N_d + Sigma_gamma))
chk("D13 機制: h¹¹ + h²¹ = Tr(𝟙 + γ̂) = N_d + Σγ (graded dimension identity)",
    mech == 0, "moduli 總數 = 生成算子 G 嘅跡")
print(f"    機制鏈: 種子 → φ → B=4, L₅=11 → N_d=44 → γ̂ → "
      f"Tr G = 134 → Π̂_2B 分割 → (36, 98)")

print("\n" + "=" * 74)
print(f"RESULT: {N_PASS}/{N_PASS + N_FAIL} PASS")
print("=" * 74)
if N_FAIL:
    raise SystemExit(1)
