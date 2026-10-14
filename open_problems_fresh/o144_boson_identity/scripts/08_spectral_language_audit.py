#!/usr/bin/env python3
"""
O144-08 — 譜語言有用性審計 (2026-09-17)
=========================================
用戶問題: 譜語言是否有用?

分離兩個組件, 各自實測:
  (i)  譜運動學 (FSR): ε_n=4sin²(πn/2N) → v=c·cos, γ=csc, 質量殼 E²−p²c²=m²c⁴
  (ii) 譜語法 (質量網格): m=M₀⟨Ω⁻,X⟩=M₀γ_nP_f, CSG v2 16 約束=16 自由度

測試:
  [A] 網格語法測試: 只用「先驗」常數池, 每粒子有幾個 (n,P_f) 選項? 解空間維數?
  [B] S₃ 對偶形式一致性: 三家族的「特徵常數」用同一形式還是三種不同形式?
  [C] 音樂測試單調性: α=beat/κ 是否真的排序和諧度? (tritone 反例)
  [D] Out-of-sample: 網格能否預言質子/中微子 (未參與建構的目標)?
  [E] 判決: (i) 與 (ii) 分別有用/無用
"""
import json, math, sys, itertools

M0 = 27.9009
phi = (1 + math.sqrt(5)) / 2
BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'

def gamma(n): return 4 * math.sin(math.pi * n / 88) ** 2

# CSG v2 宣稱的 6 個 T̂ 常數
T_CONST = {"N_d": 44.0, "L₄": 7.0, "L₅": 11.0, "F₇": 13.0, "F₉": 34.0, "L₆/F₅": 3.6}
fermions = {"e": 0.5110, "mu": 105.66, "tau": 1776.86, "u": 2.16, "d": 4.67,
            "s": 93.0, "c": 1270.0, "b": 4180.0}

print("=" * 76)
print("O144-08 譜語言有用性審計")
print("=" * 76)

# ================================================================
# [A] 網格語法測試
# ================================================================
print("\n[A] 網格語法測試: 先驗常數池 → 每粒子 (n,P_f) 選項數")
print("-" * 60)

# 從 6 常數用語言允許的算子生成 P_f 池
pool = {}
for name, v in T_CONST.items():
    pool[f"{name}"] = v
    pool[f"N_d-{name}"] = 44 - v
    pool[f"(N_d-{name})/2"] = (44 - v) / 2
    pool[f"{name}/2"] = v / 2
    pool[f"2*{name}"] = 2 * v
# 兩兩組合
names = list(T_CONST)
for a, b in itertools.combinations(names, 2):
    va, vb = T_CONST[a], T_CONST[b]
    pool[f"{a}+{b}"] = va + vb
    pool[f"{a}-{b}"] = va - vb
    pool[f"{b}-{a}"] = vb - va
    if vb != 0:
        pool[f"{a}/{b}"] = va / vb
    if va != 0:
        pool[f"{b}/{a}"] = vb / va
pool = {k: v for k, v in pool.items() if 0 < v <= 200}

print(f"  常數池 |pool| = {len(pool)} (由 6 T̂ 常數 × 語言算子生成)")

# 每粒子選項
opts = {}
for pname, target in fermions.items():
    cands = []
    for n in range(1, 45):
        gn = gamma(n)
        for pk, pv in pool.items():
            m = M0 * gn * pv
            if abs(m - target) / target < 0.01:
                cands.append((n, pk, pv, m, abs(m - target) / target * 100))
    opts[pname] = cands
    print(f"  {pname:>4}: {len(cands):>3} 個 (n,P_f) 選項 <1%")
    for c in sorted(cands, key=lambda x: x[4])[:4]:
        print(f"        n={c[0]:>2} {c[1]:<14} P_f={c[2]:<7.3f} m={c[3]:<9.3f} ({c[4]:.3f}%)")

prod = 1
for p in opts:
    prod *= max(1, len(opts[p]))
print(f"\n  獨立選項乘積 (解空間上界) = {prod:.3e}")
print(f"  最小選項數 = {min(len(v) for v in opts.values())}")

# ================================================================
# [B] S₃ 對偶形式一致性
# ================================================================
print("\n[B] S₃ 對偶形式一致性 (CSG v2 docs/03 宣稱: 三轉置單射)")
print("-" * 60)
# 宣稱: L 家族 X=L₄=7 → 槽 {n(μ), N_d−P_f(τ)}; D 家族 X=33 → {P_f(d), n(b)}; U 家族 X=13 → {P_f(c), P_f(u)}
checks = [
    ("L", "L₄=7", [("n(μ)", 7), ("N_d−P_f(τ)", 44 - 37)]),
    ("D", "N_d−L₅=33", [("P_f(d)", 33), ("n(b)", 33)]),
    ("U", "F₇=13", [("P_f(c)", 13), ("P_f(u)", (44 - 13) / 2)]),
]
for fam, X, slots in checks:
    forms = []
    for sname, sval in slots:
        if abs(sval - float(X.split("=")[-1])) < 1e-9:
            forms.append(f"{sname} = X")
        elif abs(sval - (44 - float(X.split("=")[-1]))) < 1e-9:
            forms.append(f"{sname} = N_d−X")
        elif abs(sval - (44 - float(X.split("=")[-1])) / 2) < 1e-9:
            forms.append(f"{sname} = (N_d−X)/2")
        else:
            forms.append(f"{sname} = ?")
    print(f"  {fam} 家族 (X = {X}): {forms[0]} | {forms[1]}")
print("  ⟹ L: (X, N_d−X) | D: (X, X) | U: (X, (N_d−X)/2) — 三種不同形式")
print("  ⟹ 「S₃ 單射」是觀察到值後套上的模式, 非單一生成形式 (O136 docs/03 形式不一致同構)")

# ================================================================
# [C] 音樂測試單調性
# ================================================================
print("\n[C] 音樂測試: α=beat/κ 是否排序和諧度?")
print("-" * 60)
# CSG docs/04 表 (interval, semitones, alpha, computed_harmony)
music = [
    ("unison", 0, 0.00, 1), ("m2", 1, 1.17, 4.5), ("M2", 2, 2.07, 3),
    ("m3", 3, 3.73, 2), ("M3", 4, 5.66, 2), ("P4", 5, 7.73, 1),
    ("tritone", 6, 9.80, 4), ("P5", 7, 11.73, 1), ("m6", 8, 13.38, 2),
    ("M6", 9, 14.66, 2), ("m7", 10, 15.45, 3), ("M7", 11, 15.73, 4),
]
# 檢查: 和諧度 是否 α 單調遞增 (α 越大越和諧 → 和諧度數字越小)?
viol = []
for i in range(len(music)):
    for j in range(i + 1, len(music)):
        a1, h1 = music[i][2], music[i][3]
        a2, h2 = music[j][2], music[j][3]
        if a1 < a2 and h1 > h2:   # α 大但和諧度差 (數字大) → 違反
            viol.append((music[i][0], a1, h1, music[j][0], a2, h2))
print(f"  單調性違反數: {len(viol)}")
for v in viol[:8]:
    print(f"    {v[0]} (α={v[1]}, H={v[2]}) vs {v[3]} (α={v[4]}, H={v[5]})")
# 關鍵反例
print(f"  ★ 關鍵反例: tritone α=9.80 (H=4 不和諧) 夾在 P4 α=7.73 (H=1) 與 P5 α=11.73 (H=1) 之間")
print(f"  ★ 文檔聲稱「α>>1 → 和諧」— tritone (α=9.80) 與 M7 (α=15.73, H=4) 直接違反")
print(f"  ⟹ 音樂測試的「和諧度」欄 = 音樂理論輸入重標籤; α 不排序它 → cross-domain claim ❌")

# ================================================================
# [D] Out-of-sample
# ================================================================
print("\n[D] Out-of-sample: 網格能否預言未參與建構的目標?")
print("-" * 60)
oos = {"p": 938.2720813, "X(2370)": 2376.3, "nu_ratio(Δm31/Δm21)": 33.6}
print("  網格覆蓋: 8 費米子 (e,μ,τ,u,d,s,c,b) — 全部用於建構 16 約束")
print("  質子 938.272: 網格無複合態機制 → 預言不出")
print("  膠球 2376.3: 同上 (docs/03 已證 85 為後驗)")
print("  中微子: 網格無 ν 槽 (t 亦被排除) → 預言不出")
print("  ⟹ 網格 0 個 out-of-sample 預言 (LOOCV 8/8 是 value-blind, 非 form-blind)")

# ================================================================
# [E] 判決
# ================================================================
print("\n" + "=" * 76)
print("[E] 判決: 譜語言兩個組件分別評估")
print("=" * 76)
print(f"""
(i) 譜運動學 (FSR) — ✅ 有用
    ε_n = 4sin²(πn/2N) 是三公理的直接後果 (A0 有限譜 + A1 離散波方程 + A2 相對論原理)
    v_n = c·cos(πn/2N), γ_n = csc(πn/2N), 質量殼 E²−p²c²=m²c⁴ 精確
    獨立可檢驗: Pantheon+ 1701 SNe 零參數 χ²=2006.8 vs ΛCDM (2 參數) 2002.1
    → 這是有內容的語言: 公理→預言→觀測, 可證偽

(ii) 譜語法 (質量網格) — ❌ 無用 (作為預言語言)
    - 每粒子 <1% 選項數: 見 [A] (最小 {min(len(v) for v in opts.values())} 個)
    - 解空間上界 {prod:.2e} → 16=16「唯一」是靠 5 條後驗約束 (共享對/S₃/行和)
    - S₃ 對偶三種不同形式 ([B]) → 模式後驗套上
    - 0 個 out-of-sample 預言 ([D])
    - 音樂 cross-domain 測試單調性違反 {len(viol)} 次 ([C])
    → 它是「重新編碼」而非「語言」: 把已觀測值用結構名詞重寫, 不產生新預言

判決: 譜運動學有用 (真語言); 譜語法無用 (後驗編碼)。
      盲測失敗的根源 = 用語法去編碼質量, 而非用運動學去推導質量。
""")

out = {
    "session": "2026-09-17 O144-08 spectral language audit",
    "A_grammar": {"pool_size": len(pool),
                  "per_particle_options": {k: len(v) for k, v in opts.items()},
                  "min_options": min(len(v) for v in opts.values()),
                  "solution_space_upper_bound": prod},
    "B_S3_forms": {"L": "(X, N_d-X)", "D": "(X, X)", "U": "(X, (N_d-X)/2)",
                   "verdict": "three distinct forms — pattern imposed post-hoc"},
    "C_music": {"monotonicity_violations": len(viol),
                "key_counterexample": "tritone alpha=9.80 H=4 between P4 7.73 H=1 and P5 11.73 H=1",
                "verdict": "cross-domain claim fails"},
    "D_out_of_sample": {"predictions": 0, "note": "grid covers only the 8 fermions used to build it"},
    "verdict": {"spectral_kinematics_FSR": "USEFUL (axioms → predictions → falsifiable)",
                "spectral_grammar_grid": "NOT USEFUL as predictive language (post-hoc re-encoding)"},
}
with open(f'{BASE}/open_problems_fresh/o144_boson_identity/data/08_spectral_language_audit.json', 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("✅ data/08_spectral_language_audit.json 已寫入")
sys.exit(0)
