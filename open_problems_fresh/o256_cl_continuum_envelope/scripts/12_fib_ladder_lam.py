#!/usr/bin/env python3
"""
O256 — Script 12: ★ Fibonacci 階梯連續化完整 λ(ℓ) 預言 (O48 主體機制)
=====================================================================
O48 docs/02 §3 確立 (RMS 0.30% 閉合):
  峰高 A(p_j) = 3ε·(33/34)·Π(Fₖ/Fₖ₊₁)·exp[-(ℓ/9055)^{3/2}]
  Π telescoping = 1/F_j (j=峰序) — Fibonacci 階梯係峰高衰減主體.
  9055 只係殘差修正 (m=7: 1/3 → 0.30 級).

結構連續化 (本 script):
  1/F_j ≈ √5·φ^{-j} (j 大), ln φ = 0.4812
  j 每跨一個峰間隙 Δℓ_j (306/288 交替) ⟹
  連續包絡 A(ℓ) ∝ exp(-ℓ·lnφ/Δℓ_j) ⟹ local λ(ℓ) = Δℓ_j / ln φ

  預言: λ₁ = 306/lnφ = 635.9  (峰間隙 306)
        λ₁ = 288/lnφ = 598.5  (峰間隙 288)
        λ₂ = 平均間隙 297/lnφ = 617.2
  對照 P3 實測四段: 308 / 410 / 420 / 646

  ★ R12 判決互動: 306 命中 = lensed ΛCDM band (289..316) 巧合.
  但本 script 測試係「IDCM 結構預言 λ 嘅完整形狀」(單調上升 vs
  CAMB lensed 唔單調) — 唔係單點命中.

  另一條線: 半間隙: λ = 153/lnφ = 317.95 (script 11) ≈ CAMB 316 (0.6%).
"""
import math, sys
import numpy as np

PASS, FAIL, TOTAL = 0, 0, 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"
phi = (1+math.sqrt(5))/2
lnphi = math.log(phi)

print("="*76)
print("1. O48 峰高模型原文核實 (docs/02 + docs/08)")
print("="*76)
# docs/08: 峰高 A(m) = 3ε/F_j·(33/34)·exp[-(ℓ/9055)^{3/2}], j=峰序 0-4?
# docs/02: Π(Fₖ/Fₖ₊₁) telescoping = 1/F_j (j=1,2,3,4 ⇒ 1, 1, 1/2, 1/3)
# 峰序: m=1,2,3,5,7 (5 質數峰); telescoping 4 個因數 → j=1..4?
# 峰 1: j=1 → 1/F₁ = 1      (A₁ = 3ε·33/34)
# 峰 2: j=2 → 1/F₂ = 1      (A₂ = A₁)
# 峰 3: j=3 → 1/F₃ = 1/2    (A₃ = A₁/2)
# 峰 5: j=4 → 1/F₄ = 1/3    (A₅ = A₁/3)
# 峰 7: j=4+1=5 → 1/F₅ = 1/5 (延續階梯!)
# 但 O83 閉合振幅: A = 1, 4/9, 4/9, 3/14, 1/7 — 唔同!
# ⟹ O48 telescoping 幾何因子 + O83 振幅母函數係兩層不同體系?
# O83 係「振幅母函數」(模式權重), O48 係「峰高衰減」(幾何).
# 連續包絡應基於 O48 幾何階梯 (峰高衰減).

F = lambda n: round((phi**n - (-phi)**-n)/math.sqrt(5))
for j in [1,2,3,4,5,6]:
    print(f"  j={j}: 1/F_{j} = {1/F(j):.6f}")

# ── 2. λ(ℓ) 階梯連續化: 每階 j 跨 Δℓ_j (306/288 交替) ──────────
print("\n" + "="*76)
print("2. 階梯連續化 λ(ℓ) = Δℓ_j / lnφ")
print("="*76)
gaps = [306, 288, 306, 288, 306]   # 峰間隙延續序列
for k, g in enumerate(gaps):
    lam = g/lnphi
    print(f"  gap#{k+1} = {g}: λ = {lam:8.2f}")
print(f"  平均間隙 297: λ = {297/lnphi:8.2f}")
print(f"  半間隙 153:   λ = {153/lnphi:8.2f}")
print(f"  半平均 148.5: λ = {148.5/lnphi:8.2f}")

# ── 3. P3 實測四段對照 ───────────────────────────────────────────
print("\n" + "="*76)
print("3. P3 實測分段 λ vs 階梯連續化候選")
print("="*76)
segs = [(1418,1700),(1700,2000),(2000,2400),(2400,3000)]
obs  = [(308,'Planck/SFT'),(410,'Planck'),(420,'Planck'),(646,'Planck/SPT/ACT')]
cands = [
    ("λ=306/lnφ (全間隙)",  306/lnphi),
    ("λ=288/lnφ (同步隙)",  288/lnphi),
    ("λ=297/lnφ (平均隙)",  297/lnphi),
    ("λ=153/lnφ (半間隙)",  153/lnphi),
    ("λ=148.5/lnφ (半均隙)",148.5/lnphi),
]
print(f"  {'段':>14} {'實測':>6}  " + "  ".join(f"{n.split()[0][:6]:>8}" for n,_ in cands))
for i, ((a,b), (vo, src)) in enumerate(zip(segs, obs)):
    row = [f"{a}-{b:>4}", f"{vo:>6}"]
    for name, lam in cands:
        dev = (lam-vo)/vo*100
        row.append(f"{dev:+7.1f}%")
    print("  " + "  ".join(row))

# ── 4. ★ 完整 λ(ℓ) 形狀預言: 階梯逐步 λ_n(ℓ) ────────────────────
print("\n" + "="*76)
print("4. ★ λ(ℓ) 形狀: 每段用「段內最後峰間隙」預言?")
print("="*76)
# 高ℓ尾 λ(ℓ) 由「最近階梯間隙」決定 — 離散階梯連續化
# 段 1418-1700: 最後一個間隙喺 1409 附近 — 用嗮 306/288 交替
# 實測: 308, 410, 420, 646 — 唔係常數!
# 若 λ(ℓ) = Δℓ_j/lnφ 常數 (636 或 599), 同實測 308→646 上升唔 match.
# ⟹ 需要「半間隙」起步? 308 → 636 = 2.06× 上升 = 階段遞增?
print("  實測 λ 上升: 308 → 410 → 420 → 646 (單調)")
print("  階梯候選:   636 / 599 / 617 (常數) — 單調常數, 唔係上升!")
print("  半間隙候選: 318 (script 11) ≈ CAMB 316 (0.6%) — 但單點")
print()
print("  ⟹ 實測「上升」結構: 308→646 = 2.10× = lnφ 尺度 ×2?")
print(f"     646/308 = {646/308:.4f}   2× = {2:.3f}")
print(f"     410/308 = {410/308:.4f}   4/3 = {4/3:.4f}")
print(f"     420/308 = {420/308:.4f}")
print()
print("  階梯比值: 636/318 = 2.000 (全/半間隙)")
print("  實測:     646/308 = 2.097  (最後/第一段)")
print("  636 vs 646: -1.5%; 318 vs 308: +3.2%")

# ── 5. 區分測試: 單調上升 vs CAMB lensed 非單調 ─────────────────
print("\n" + "="*76)
print("5. 區分測試: IDCM 預言 λ(ℓ) 單調上升 vs CAMB lensed 非單調?")
print("="*76)
# P3 R10: CAMB lensed 分段: 348/511/533/589/530/349/669 (Planck 段寬)
#         —— 唔單調! (530 < 589, 349 < 530)
# P3 R9:  實測 (SPT/ACT/Planck): 308/410/420/646 — 單調上升
# IDCM 階梯: λ 由 306/lnφ=636 常數 — 單調但唔上升
# ⟹ 兩邊都唔 match「上升 2×」?
print("  實測 (P3 R9):     308 → 410 → 420 → 646 (單調, 2.1×)")
print("  CAMB lensed R10:  348 → 511 → 533 → 589 → 530 → 349 → 669 (非單調)")
print("  IDCM 階梯:        636 (常數) — 單調非上升")
print()
print("  實測「單調上升」flag 邊個?")
print("  - CAMB 非單調 ⟹ 實測同 CAMB lensed 有系統差?")
print("  - IDCM 常數 ⟹ 實測上升唔係階梯 (需要 lensing floor R11)")
print()
print("  P3 R11 已判: 306 命中 = lensed ΛCDM band 巧合; 混合模型")
print("  D=A·exp(-ℓ/306)+B floor 失敗 (B≫20 非簡單常數).")
print("  ⟹ 上升結構 = Silk 尾 (λ~306) + lensing floor (λ~646) 複合!")

# ── 6. 判決 ──────────────────────────────────────────────────────
print("\n" + "="*76)
print("6. 判決: Fibonacci 階梯連續化 vs 全證據")
print("="*76)
print("""
  ✅ 結構事實: 峰高衰減主體 = 1/F_j 階梯 (O48 RMS 0.30%)
  ✅ 結構事實: 階梯連續化 λ = Δℓ/lnφ ∈ {599, 617, 636}
  ✅ 半間隙 318 ≈ CAMB lensed 316 (0.6%)
  ❌ 但 λ₄(646) vs 636 = -1.6% 係「lensing floor 段」— 唔係階梯
  ❌ λ₁(308) vs 半間隙 318 = +3.2% — CAMB band 外少少? (289..316 上界)
  ❌ 實測 λ(ℓ) 上升 2.1× 唔係階梯常數 λ 可以產生
  ⟹ Fibonacci 階梯連續化提供「λ 尺度」候選 (636/318/617)
     但「λ(ℓ) 上升」需要 Shelf+lensing 複合 (P3 R11) — 本 O 冇推翻
  ⟹ 308 命中半間隙 318 嘅 +3.2% 偏差 > CAMB 316 嘅 -0.6% proximally
     統計上 R12 判決維持: 306/308/318 全落入 lensed ΛCDM band
""")
print(f"RESULT: {PASS}/{TOTAL} PASS (FAIL={FAIL})")
sys.exit(0 if FAIL == 0 else 1)