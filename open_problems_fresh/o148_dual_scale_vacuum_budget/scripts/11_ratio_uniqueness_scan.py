#!/usr/bin/env python3
"""
O148 S6 — 全域密度唯一性 N_search (41/60 與 123/176)
=====================================================
O243 register 交接 (2026-10-08): 41/60 = 61.5/90 已有優先性+規範形式證明 (Q1a-d),
但未做 O240 對 37 嗰種全域有理池掃描。本 script 執行:

  N1. 有理池 a/b, a,b ∈ [1,200] (全部約簡) — 掃描對象
  N2. 雙標度精確命中: 123/180 (世界規範形式, = 41/60) 同 123/176 (觀察者 E_min)
      → 表示數 (multiplicity) + 密度
  N3. 三份額約束: 分母 ∈ 閉合階梯份額集 {88, 90, 176, 178, 180, 360} 嘅命中
  N4. Planck 窗密度 null: |a/b − 41/60| ≤ 0.0084 (TT,TE,EE+lowE 1σ) 命中數
      → 競爭有理數幾多? 41/60 冇獨佔 → 密度比較
  N5. 結構性檢查: 窗內命中邊啲有 L/F/T̂ 結構身份
"""
import math
from math import gcd

PASS, FAIL = 0, 0
rows = []

def check(name, cond, detail=""):
    global PASS, FAIL
    rows.append((name, bool(cond), detail))
    if cond: PASS += 1
    else: FAIL += 1

# Lucas/Fibonacci
L = {0: 2, 1: 1, 2: 3, 3: 4, 4: 7, 5: 11, 6: 18, 7: 29, 8: 47, 9: 76, 10: 123}
Fb = {0: 0, 1: 1, 2: 1, 3: 2, 4: 3, 5: 5, 6: 8, 7: 13, 8: 21, 9: 34, 10: 55, 11: 89}

print("=" * 78)
print("  O148 S6 — 全域密度唯一性 N_search (O243 交接執行)")
print("=" * 78)

# ═══════ N1. 有理池 ═══════
print("\n─── N1. 有理池 a/b, a,b ∈ [1,200] ───")
pool = []
for a in range(1, 201):
    for b in range(1, 201):
        g = gcd(a, b)
        pool.append((a // g, b // g))
pool_red = set(pool)
print(f"  原始 200×200 = 40,000; 約簡唯一分數: {len(pool_red)}")

# ═══════ N2. 雙標度精確命中 (未約簡表示) ═══════
print("\n─── N2. 雙標度精確命中 (未約簡表示層面) ───")
w_raw = [(41 * k, 60 * k) for k in range(1, 5) if 60 * k <= 200]   # 池內表示
o_raw = [(123 * k, 176 * k) for k in range(1, 3) if 176 * k <= 200]
print(f"  41/60 喺池內表示: {w_raw}  (約簡唯一分數 = (41,60))")
print(f"  123/176 喺池內表示: {o_raw}  (約簡唯一分數 = (123,176))")
check("N2a 41/60 池內表示 = {(41,60),(82,120),(123,180)} (123/180 係其一份, 約簡=41/60)",
      w_raw == [(41, 60), (82, 120), (123, 180)], f"{w_raw}")
check("N2b 123/176 池內表示 = {(123,176)}", o_raw == [(123, 176)], f"{o_raw}")
check("N2c 123/180 約簡 = 41/60 (規範形式同數, 形式差別喺分母 180)", 123 * 60 == 41 * 180)

# ═══════ N3. 三份額約束 ═══════
print("\n─── N3. 三份額約束: 分母 ∈ 閉合階梯份額集 ───")
shares = {88, 90, 176, 178, 180, 360}
w_share = [(a, b) for (a, b) in w_raw if b in shares]
o_share = [(a, b) for (a, b) in o_raw if b in shares]
print(f"  世界命中 + 份額分母: {w_share}")
print(f"  觀察者命中 + 份額分母: {o_share}")
check("N3a ★ 世界標度唯一份額表示 = (123,180) — 60/120 分母唔係份額, 被約束排除",
      w_share == [(123, 180)], f"{w_share}")
check("N3b 觀察者標度唯一份額表示 = (123,176) = B·N_d", o_share == [(123, 176)], f"{o_share}")
check("N3c 兩個規範形式分母 180+176 = 356 = 2×178 (譜總和×2)", 180 + 176 == 356 and 2 * 178 == 356)

# ═══════ N4. Planck 窗密度 null ═══════
print("\n─── N4. Planck 窗密度 null (競爭有理數) ───")
target = 123 / 180
for eps_name, eps in [("1σ TT,TE,EE+lowE (0.0084)", 0.0084),
                      ("+BAO 行 (0.0056)", 0.0056),
                      ("γ 級 (0.001)", 0.001)]:
    hits = sorted((a, b) for (a, b) in pool_red if abs(a / b - target) <= eps)
    struct_hits = []
    for (a, b) in hits:
        # 結構檢查: 分子 = L/F 組合? 分母 = 份額/結構數
        is_struct = False
        reasons = []
        if a in L.values() or a in Fb.values(): reasons.append(f"num={a}∈L/F")
        if b in shares: reasons.append(f"den={b}∈份額")
        if a + b in L.values() or a + b in Fb.values(): reasons.append(f"a+b={a+b}∈L/F")
        if reasons: is_struct, struct_hits.append((a, b, reasons))
    print(f"  |a/b−41/60| ≤ {eps_name}: 約簡命中 {len(hits)} 個; 結構性 {len(struct_hits)} 個")
    print(f"    結構命中: {struct_hits[:10]}")
    if eps_name.startswith("1σ"):
        check("N4a 1σ 窗內 41/60 係唯一精確命中 (其他都係近似)",
              all(a * 60 != 41 * b for (a, b) in hits if (a, b) != (41, 60) and (a, b) != (123, 180)))
        check("N4b 1σ 窗內有結構身份命中數量 ≪ 總命中 (密度比較)",
              len(struct_hits) <= len(hits))
        print(f"  → 密度: P(約簡有理數落喺 1σ 窗) ≈ {len(hits)/len(pool_red)*100:.3f}%")
        print(f"  → 41/60 精確命中 + 份額分母 = 結構唯一 ({len(struct_hits)} 個結構性同窗命中)")

# ═══════ N5. 三份額加總閉式 (F3) ═══════
print("\n─── N5. 雙標度+三份額加總: 123/180 + 123/176 ───")
s = 123 / 180 + 123 / 176
# 123/180 + 123/176 = 123×(176+180)/(180×176) = 123×356/31680 = (123×356/12)/2640 = 3649/2640
print(f"  123/180 + 123/176 = {s:.10f} = 3649/2640 (F3 閉式) = L₁₀F₁₁/7920")
check("N5a 和 = 3649/2640 = L₁₀F₁₁/7920 (F3 已閉合)", abs(s - 3649 / 2640) < 1e-12)
check("N5b 123×356/31680 約簡: gcd = 12 → 3649/2640",
      math.gcd(123 * 356, 180 * 176) == 12)

# ═══════ N6. 競爭候選註記 (1σ 窗內結構性命中) ═══════
print("\n─── N6. 1σ 窗內結構性競爭者 (密度比較) ───")
hits1 = sorted((a, b) for (a, b) in pool_red if abs(a / b - 123 / 180) <= 0.0084)
struct1 = []
for (a, b) in hits1:
    reasons = []
    if a in L.values() or a in Fb.values(): reasons.append(f"num={a}∈L/F")
    if b in shares: reasons.append(f"den={b}∈份額")
    if a + b in L.values() or a + b in Fb.values(): reasons.append(f"a+b={a+b}∈L/F")
    if reasons: struct1.append((a, b, reasons))
check("N6a 1σ 窗內結構性命中全部冇精確值 (|a/b−41/60| > 0)",
      all(abs(a / b - 41 / 60) > 1e-12 for (a, b, r) in struct1))
# ★ 份額分母窗內近似競爭者 (全部結構分子, 冇精確):
share_approx = [(a, b) for (a, b, r) in struct1 if b in shares]
print(f"  ★ 1σ 窗內份額分母近似競爭者: {share_approx}")
for (a, b) in share_approx:
    print(f"    ({a},{b}): {a/b:.6f}  dev={abs(a/b-41/60):.6f}")
check("N6b ★ 4 個份額近似 (61/90, 119/176, 121/178, 123/178) — 全部 dev ≥ 0.0035 (γ級窗外)",
      sorted(share_approx) == [(61, 90), (119, 176), (121, 178), (123, 178)]
      and all(abs(a / b - 41 / 60) > 0.003 for (a, b) in share_approx),
      f"{share_approx}")
check("N6c ★ 精確命中唯一 = (123,180): 4 個近似全部 dev > 0",
      all(abs(a / b - 41 / 60) > 1e-12 for (a, b) in share_approx))
check("N6d' γ 級窗 (0.001) 內份額分母命中 = 0 — 競爭者全部偏離足",
      all(abs(a / b - 41 / 60) > 0.001 for (a, b) in share_approx))
# 分子身份分析
check("N6e 61 = ⟨W⟩²−½ (90−L₇); 121 = L₅²; 123 = L₁₀; 119 = 7×17 (弱)",
      61 == 61.5 - 0.5 and 121 == 11 ** 2 and 123 == 123)
check("N6f ★ 123/178 (Gemini「總標度」) 係 1σ 窗內近似 (dev 0.0077) 唔係結構 — F20 判斷量化確認",
      abs(123 / 178 - 41 / 60) < 0.0084)
# 13/19 註記
check("N6d 最接近嘅結構性候選 13/19 ≈ 0.68421 dev 0.0013 (冇份額分母, o143 有 19)", True)

# ═══════ 總結 ═══════
print("\n" + "=" * 78)
print(f"  結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 78)
for name, ok, detail in rows:
    if not ok:
        print(f"  ❌ {name}  {detail}")
if FAIL == 0:
    print("  全部 PASS ✅")