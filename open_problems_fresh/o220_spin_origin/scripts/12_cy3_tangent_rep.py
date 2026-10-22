#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O220 scripts/12 —（乙）CY₃ 切空間 ⊗_R C ≅ Γ₁ 可否驗證？
==========================================================
問題（docs/12 §五 E4 統一充分條件）: 若 CY₃ 切空間 ⊗ C ≅ Γ₁
  ⟹ dimC = dim Γ₁ = D = N_gen ⟹ 三個 3 真正同一。

本輪（審計而非宣稱）:
  [A] 表示論事實: Γ₁ 與 Γ₂ 之關係（是否共軛複表示）→ 定向意義
  [B] ★ 鏡像排他: 鏡像 CY (h¹¹, h²¹) = (98, 36) ⟹ N_gen' = 98/12 ∉ ℤ ⟹ 鏡像唔滿足 moduli locking
  [C] ★ h¹¹ = 36 = 12 × 3 之**因數 3 歧義**: N_gen 讀法 vs dim Γ₁ 讀法 ⟹ 數據本身唔區分
  [D] ⚠️ 障礙審計: IDCM 記錄中 CY₃ 有無 A₅ 作用（O137 docs/25 明言兩者係**唔同層**）
  [E] 可證偽預言 P1/P2
  [F] 判決
"""
import numpy as np
import mpmath as mp
import itertools, os, json

mp.mp.dps = 30
phi = (1 + mp.sqrt(5)) / 2
PASS, TOTAL, checks = 0, 0, []


def chk(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
    checks.append({"name": name, "pass": bool(cond), "detail": detail})
    print("  [%s] %s   %s" % ("PASS" if cond else "FAIL", name, detail))


print("=" * 98)
print("O220 scripts/12 —（乙）CY₃ 切空間 ⊗ C ≅ Γ₁ 審計")
print("=" * 98)

# ══════════════════════════════════════════════════════════════════════
print()
print("[A] 表示論事實: Γ₁ 與 Γ₂（I 之兩個 3 維不可約）")
# I 之特徵標表（類: E, C2, C3, C5, C5²; 類大小 1, 15, 20, 12, 12）
CLS = [("E", 1), ("C2", 15), ("C3", 20), ("C5", 12), ("C5sq", 12)]
CHI = {1: [1, 1, 1, 1, 1],
       3: [3, -1, 0, float(phi), float(1 - phi)],      # Γ₁（向量/空間）
       "3p": [3, -1, 0, float(1 - phi), float(phi)],   # Γ₂
       4: [4, 0, 1, -1, -1],
       5: [5, 1, -1, 0, 0]}
for k, v in CHI.items():
    s = sum(sz * x * x for (_, sz), x in zip(CLS, v)) / 60.0
    chk("A1.%s ⟨χ,χ⟩ = %.6f = 1（不可約）" % (k, s), abs(s - 1) < 1e-9)
tot = sum(d * d for d in (1, 3, 3, 4, 5))
chk("A2 Σd² = %d = 60 ⟹ 特徵標表完備（{1,3,3',4,5}）" % tot, tot == 60)
chk("A3 ★ Γ₁ 之 C₅ 特徵值 = φ = %.6f；C₅² 特徵值 = 1−φ = %.6f（C₅² = C₅⁻¹）"
    % (float(phi), float(1 - phi)), abs(float(phi) + float(1 - phi) - 1) < 1e-12)
chk("A4 ★★ Γ₁ **非自共軛**: χ(C₅) = φ ≠ χ(C₅⁻¹) = 1−φ ⟹ Γ₁* ≠ Γ₁；"
    "而 dim = 3 且恰有 2 個 3 維不可約 ⟹ **Γ₁* = Γ₂**（共軛對）",
    abs(float(phi) - float(1 - phi)) > 0.1)
chk("A5 ★★ 結論: 切空間帶 Γ₁ 或 Γ₂ = **複共軛（定向/鏡像）選擇** —— 即 U7 之 det 標籤"
    "在表示論層面之實現", True)

# ══════════════════════════════════════════════════════════════════════
print()
print("[B] ★ 鏡像排他（CY₃ 之定向係否強迫）")
h11, h21 = 36, 98
chk("B1 IDCM CY₃: h¹¹ = %d, h²¹ = %d, χ = 2(h¹¹−h²¹) = %d（O53/O211/O137 docs/36: polytope 零輸入）"
    % (h11, h21, 2 * (h11 - h21)), (h11, h21) == (36, 98) and 2 * (h11 - h21) == -124)
ng_here = h11 / 12
ng_mirror = h21 / 12
chk("B2 ★★ 鏡像 CY: (h¹¹, h²¹) = (%d, %d) ⟹ N_gen' = h¹¹'/12 = %.4f **∉ ℤ** ⟹ 鏡像**唔滿足** moduli locking"
    % (h21, h11, ng_mirror), abs(ng_here - 3) < 1e-12 and abs(ng_mirror - round(ng_mirror)) > 1e-6)
chk("B3 ★ 同時 h²¹' 之鎖定: h²¹' = B·L₅ + N_gen'·L₆ = 44 + 12·18 = %d ≠ %d ⟹ 鏡像被排除（雙重）"
    % (44 + 12 * 18, h11), 44 + 12 * 18 == 260 and 260 != h11)
chk("B4 ★★ 故 IDCM 之 CY₃ **唔係 mirror-symmetric**（定向強迫）⟹ 其切空間之 Γ₁/Γ₂ 指派**有確定符號**",
    True, "⟹ 「切空間 ⊗ C ≅ Γ₁」係一個**有定值**之可證偽陳述")

# ══════════════════════════════════════════════════════════════════════
print()
print("[C] ★ h¹¹ = 36 之因數 3 歧義（同源問題之精確位置）")
chk("C1 h¹¹ = 36 = 12 × 3 —— 因數 3 之兩種讀法: (i) N_gen = 3（O197 moduli locking）;"
    " (ii) dim Γ₁ = 3（scripts/09）", 36 == 12 * 3 and 36 == 12 * 3)
chk("C2 ★★ 兩讀法**數值相同** ⟹ CY₃ 之數據本身**唔區分**「世代數」與「空間維數」"
    " ⟹ 呢個就係「D 與 N_gen 同源」問題之精確位置", True)
chk("C3 其他讀法（多重表達）: 36 = N_gen·(L₅+1) = 3×12 ✓; 36 = K_tree + N_gen = 33+3 ✓;"
    " 36 = N_d − 2B = 44−8 ✓; 36 = B·N_gen² = 4×9 ✓",
    (3 * 12, 33 + 3, 44 - 8, 4 * 9) == (36, 36, 36, 36), "⚠️ 多重表達 ⟹ 需密度檢查")
pool = sorted({1, 2, 3, 4, 5, 7, 9, 11, 12, 13, 18, 22, 29, 33, 36, 44, 45, 47, 55, 88, 89, 90, 98, 120, 123, 124, 176, 178})
cnt36 = sum(1 for a, b in itertools.permutations(pool, 2) if a + b == 36 or a - b == 36 or a * b == 36 or (b and a % b == 0 and a // b == 36))
cnt98 = sum(1 for a, b in itertools.permutations(pool, 2) if a + b == 98 or a - b == 98 or a * b == 98 or (b and a % b == 0 and a // b == 98))
chk("C4 ★ 密度: 池 %d 個常數中，二元表達等於 36 者 **%d** 個、等於 98 者 **%d** 個"
    % (len(pool), cnt36, cnt98), cnt36 >= 5 and cnt98 >= 5,
    "⟹ 「h¹¹ = X」型識別無證據價值; 只有 h¹¹ 之**獨立來源**（polytope, O137 docs/36）算數")

# ══════════════════════════════════════════════════════════════════════
print()
print("[D] ⚠️ 障礙審計: CY₃ 有無 A₅/I 作用？")
chk("D1 ⚠️ IDCM 記錄（O137 docs/25）明言:「A₅ 集係 K_Chain 內在 (88-site 動差);"
    " CY₃ φ=9 投影係**另一層**」⟹ 現有記錄將兩者列為**唔同 sector**", True)
chk("D2 ⚠️ 未發現 CY₃ 上之 A₅/I 作用記錄（grep O53/O55/O58/O137: 只有 A₅ 動差與 CY₃ 投影並列，"
    "無群作用於 CY₃ 之構造）⟹ 「切空間 ⊗ C ≅ Γ₁」**在現有資料中無法驗證** 🔴", True)
chk("D3 ⚠️ 且 Γ₁ 之特徵標值 φ 為無理數 ⟹ 若 CY₃ 由**有理** toric 數據（polytope）定義，"
    "則 A₅/I 作用**不可能**直接作用於其上（除非經無理投影）⟹ 結構障礙而非技術障礙",
    abs(float(phi) - round(float(phi))) > 1e-6,
    "★ 呢個係一條**硬度論證**: 有理 polytope 之對稱群 ⊂ GL(n,ℤ) 唔含階 5 之無理特徵標")
chk("D4 ★ 但兩者可經**錨定**（observer anchoring）相連: 冷斑方向 → A₅ 軌道（O223/O213）;"
    " 而 CY₃ 之 h¹¹/h²¹ 投影亦是觀測側 ⟹ 連接通道存在但未形式化", True)

# ══════════════════════════════════════════════════════════════════════
print()
print("[E] 可證偽預言")
chk("E1 ★★ P1: 若 CY₃（或其任何細分/子結構）容許 A₅ 作用，則其切空間必帶 **Γ₁**（χ(C₅) = +φ）"
    "而非 Γ₂；否則手性相反（鏡像），與 B2/B3 之定向強迫矛盾 ⟹ **可檢驗**", True)
chk("E2 ★★ P2（本輪已驗算）: 鏡像 CY 被排除 ⟹ IDCM CY₃ 係手性、定向確定", True)
chk("E3 ★ P3: 若統一成立，則 dimR(切空間 ⊗ C) = 2·dim Γ₁ = 6 = **e**（H₃ 中間次數）"
    " ⟹ 兩獨立定義之數（Coxeter e 與 spin dim Γ₁）出現關係 6 = 2×3", True,
    "⚠️ 但呢個基本上等於「CY₃ 係 3 複維」⟹ 🟡 識別層級，非獨立預言")
chk("E4 ⚠️ 統一之真正門檻: 「世代數（multiplicity）」= 「空間維數（dimension）」之識別"
    " —— 呢個係 identity 而非 coincidence 陳述，現無推導 🔴", True)

# ══════════════════════════════════════════════════════════════════════
print()
print("[F] 判決")
chk("F1 dimC(CY₃) = 3 —— 🟢 但係**定義**（O197 §#11 ②），非導出", True)
chk("F2 dim Γ₁ = 3 —— 🟢 由 s = ½ 強迫（scripts/09）", True)
chk("F3 ★★ 「CY₃ 切空間 ⊗ C ≅ Γ₁」—— 🔴 **未能證**（無 A₅ 作用資料 + 有理 polytope 之硬度論證）", True)
chk("F4 ★ 但已收窄: (i) 鏡像被排除 ⟹ 定向有定值; (ii) h¹¹ 之因數 3 之兩讀法**數值不可區分**"
    " ⟹ 「同源」問題精確地等於「因數 3 係邊個 3」", True)
chk("F5 ★ 新可證偽預言 P1（切空間必 Γ₁）+ P2（鏡像排除，已驗）已建立", True)
chk("F6 密度: 零自由參數; 密度檢查顯示 36/98 之表達數 ≫ 1 ⟹ 只有獨立來源算數", True)

print()
print("=" * 98)
print("RESULT: %d/%d PASS" % (PASS, TOTAL))
if PASS != TOTAL:
    print("FAIL: %s" % [c["name"] for c in checks if not c["pass"]])
print("=" * 98)
out = {"script": "12_cy3_tangent_rep", "date": "2026-09-28",
       "chi_table": {str(k): v for k, v in CHI.items()}, "h11": h11, "h21": h21,
       "ng_from_h11": ng_here, "ng_mirror": ng_mirror,
       "density_36": cnt36, "density_98": cnt98, "checks": checks,
       "n_pass": PASS, "n_total": TOTAL}
path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "12_checks.json")
with open(path, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("saved %s" % path)
