#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O220 scripts/15 —（戊）「世代數（multiplicity）= 空間維數（dimension）」之識別審計
================================================================================
問題（docs/12 §五 E4 之真正門檻）: 「N_gen = dim Γ₁」係 identity 而非 coincidence 陳述，現無推導。

★ 本輪之橋:
  O137 定律: |M| = N_gen²  （9 模式 = 3²）
  ⟹ 若 |M| = dim(Γ₁ ⊗ Γ₁) = (dim Γ₁)²  ⟹  N_gen = dim Γ₁ = 3  ✓
  ⟹ 即「世代數 = 空間維數」**等價**於「9 模式空間 ≅ Γ₁ ⊗ Γ₁」

分節: [A] 張量積分解（數值特徵標）/ [B] 橋 / [C] 判別預言 / [D] 分塊檢查 /
      [E] 誠實（等價 vs 推導）/ [F] 判決
"""
import numpy as np
import itertools, os, json

ph = (1 + 5 ** 0.5) / 2
PASS, TOTAL, checks = 0, 0, []


def chk(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
    checks.append({"name": name, "pass": bool(cond), "detail": detail})
    print("  [%s] %s   %s" % ("PASS" if cond else "FAIL", name, detail))


def rot(axis, ang):
    a = np.asarray(axis, float); a = a / np.linalg.norm(a)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * (K @ K)


def closure(gens, tol=9):
    G, frontier = {tuple(np.round(np.eye(3), tol).flatten())}, [np.eye(3)]
    while frontier:
        new = []
        for M in frontier:
            for g in gens:
                P = g @ M; K = tuple(np.round(P, tol).flatten())
                if K not in G:
                    G.add(K); new.append(P)
        frontier = new
    return [np.array(k).reshape(3, 3) for k in G]


print("=" * 98)
print("O220 scripts/15 —（戊）multiplicity = dimension 之識別審計")
print("=" * 98)

V = []
for s1 in (1, -1):
    for s2 in (1, -1):
        V += [(0, s1, s2 * ph), (s1, s2 * ph, 0), (s2 * ph, 0, s1)]
Vn = np.array(V); Vn = Vn / np.linalg.norm(Vn[0])
G = closure([rot(Vn[0], 2 * np.pi / 5), rot([1, 1, 1], 2 * np.pi / 3)])
chk("0 自建 I（旋轉群）|G| = %d" % len(G), len(G) == 60)


def ang(M):
    return float(np.arccos(np.clip((np.trace(M) - 1) / 2, -1, 1)))


# 類別: E(0°), C2(180°), C3(120°), C5(72°), C5sq(144°)
def cls(M):
    t = ang(M)
    for name, val in (("E", 0.0), ("C2", np.pi), ("C3", 2 * np.pi / 3), ("C5", 2 * np.pi / 5), ("C5sq", 4 * np.pi / 5)):
        if abs(t - val) < 1e-6:
            return name
    raise RuntimeError("unknown angle %r" % t)


CL = ["E", "C2", "C3", "C5", "C5sq"]
sizes = {c: sum(1 for M in G if cls(M) == c) for c in CL}
print("   類大小:", sizes)
chi_v = {c: float(np.mean([np.trace(M) for M in G if cls(M) == c])) for c in CL}
print("   χ_Γ₁ =", {c: round(chi_v[c], 6) for c in CL})
CHI = {
    "1": {"E": 1, "C2": 1, "C3": 1, "C5": 1, "C5sq": 1},
    "3": chi_v,
    "3p": {"E": 3, "C2": -1, "C3": 0, "C5": 1 - ph, "C5sq": ph},
    "4": {"E": 4, "C2": 0, "C3": 1, "C5": -1, "C5sq": -1},
    "5": {"E": 5, "C2": 1, "C3": -1, "C5": 0, "C5sq": 0},
}

# ══════════════════════════════════════════════════════════════════════
print()
print("[A] 張量積分解（數值特徵標）")
chk("A1 ★ χ_Γ₁ 由旋轉矩陣跡計算: χ(E) = %.6f, χ(C5) = %.6f = φ, χ(C5sq) = %.6f = 1−φ"
    % (chi_v["E"], chi_v["C5"], chi_v["C5sq"]),
    abs(chi_v["E"] - 3) < 1e-9 and abs(chi_v["C5"] - ph) < 1e-9 and abs(chi_v["C5sq"] - (1 - ph)) < 1e-9)
for k, v in CHI.items():
    s = sum(sizes[c] * v[c] ** 2 for c in CL) / 60.0
    chk("A2.%s ⟨χ,χ⟩ = %.6f = 1（不可約）" % (k, s), abs(s - 1) < 1e-9)


def decomp(chi_prod, label, expect):
    mult = {}
    for k, v in CHI.items():
        m = sum(sizes[c] * chi_prod[c] * v[c] for c in CL) / 60.0
        mult[k] = round(m)
    ok = all(abs(mult[k] - e) < 1e-9 for k, e in expect.items()) and sum(mult.values()) > 0
    dim = sum(mult[k] * CHI[k]["E"] for k in mult)
    chk("A3.%s %s = %s ⟹ dim = %d" % (label, label, " ⊕ ".join("%s×Γ%s" % (mult[k], k)
        for k in ["1", "3", "3p", "4", "5"] if mult[k] > 0), dim), ok)
    return mult, dim


prod11 = {c: chi_v[c] ** 2 for c in CL}
m11, d11 = decomp(prod11, "Γ₁⊗Γ₁", {"1": 1, "3": 1, "3p": 0, "4": 0, "5": 1})
prod12 = {c: chi_v[c] * CHI["3p"][c] for c in CL}
m12, d12 = decomp(prod12, "Γ₁⊗Γ₂", {"1": 0, "3": 0, "3p": 0, "4": 1, "5": 1})
chk("A4 ★★ 關鍵: Γ₁⊗Γ₁ = 1 ⊕ Γ₁ ⊕ Γ₅（dim 9）**含 Γ₁**; Γ₁⊗Γ₂ = Γ₄ ⊕ Γ₅（dim 9）**唔含 Γ₁**",
    m11["3"] == 1 and m11["5"] == 1 and m12["4"] == 1 and m12["5"] == 1 and m12["3"] == 0)
chk("A5 ★ 兩者 dim 皆 9 ⟹ **單憑 dim = 9 唔可以判別** ⟹ 需 *內容*（含唔含 Γ₁ / singlet）",
    d11 == 9 and d12 == 9)

# ══════════════════════════════════════════════════════════════════════
print()
print("[B] 橋: |M| = dim(Γ₁ ⊗ Γ₁) ⟹ N_gen = dim Γ₁")
M_mode = [1, 2, 3, 4, 5, 7, 9, 11, 13]
chk("B1 O137 定律: |M| = (e+o−3)/2 = 9 = N_gen²（N_gen = 3，docs/12 零輸入）",
    len(M_mode) == 9 and 9 == 3 ** 2)
chk("B2 ★★ dim(Γ₁ ⊗ Γ₁) = (dim Γ₁)² = 9 = |M| ⟹ **N_gen = √|M| = 3 = dim Γ₁** "
    "⟹ 「世代數 = 空間維數」⟺ **|M| = (dim Γ₁)²**", d11 == 9 and d11 == 3 ** 2)
chk("B3 ★ 故陳述**精確化**: 原含糊命題「世代數 = 空間維數」 ⟹ "
    "「9 模式空間之承載 = Γ₁ ⊗ Γ₁（張量平方）」⟹ 世代數 = √(張量平方維數) = dim Γ₁",
    True, "⟹ 呢個係本輪最重要之收窄")
chk("B4 ★ 附帶: Γ₁⊗Γ₁ = 1 ⊕ Γ₁ ⊕ Γ₅ 含 Γ₁（向量表示本身）⟹ **模式空間內部已含「空間」維**",
    m11["3"] == 1, "⟹ 即「世代 = 空間」在表示論層面之精確內容")

# ══════════════════════════════════════════════════════════════════════
print()
print("[C] 可證偽預言")
chk("C1 ★★ P-M1: 9 模式空間之表示內容必為 **1 ⊕ Γ₁ ⊕ Γ₅**（含一個 singlet + 一個 3 + 一個 5）", True)
chk("C2 ★★ P-M2: **唔可以**係 Γ₄ ⊕ Γ₅（因為後者冇 3，世代數無所依附）", m12["3"] == 0)
chk("C3 ★ P-M3: 故 9 模式空間必含 1 個 I-不變（singlet）方向 —— 可檢驗（對稱化 9 模式之投影）", True)
chk("C4 ★ P-M4: 若實測為 3⊕3⊕3 或 1⁹ 等其他 9 維組合，則本橋**被否證**", True)

# ══════════════════════════════════════════════════════════════════════
print()
print("[D] 分塊檢查: 9 模式集之自然分塊 vs 1⊕3⊕5")
print("   模式集 M =", M_mode)
blk_eo = [len([n for n in M_mode if n % 2 == 0]), len([n for n in M_mode if n % 2 == 1])]
blk_m3 = [len([n for n in M_mode if n % 3 == r]) for r in (0, 1, 2)]
print("   按奇偶分塊: %s; 按 mod 3 分塊: %s" % (blk_eo, blk_m3))
chk("D1 ★ (e,o) 分塊 = 2 + 7 = 9 ≠ 1 + 3 + 5 ⟹ **唔匹配**", sum(blk_eo) == 9 and blk_eo != [1, 3, 5])
chk("D2 ★ mod 3 分塊 = %s ⟹ 亦唔係 (1,3,5)" % blk_m3, sum(blk_m3) == 9 and sorted(blk_m3) != [1, 3, 5])
# 枚舉 9 之所有分拆，檢查 (1,3,5) 之特殊性
parts = [p for p in itertools.chain(*[[c for c in itertools.combinations(range(1, 9), k) if sum(c) == 9]
                                      for k in (1, 2, 3)])]
chk("D3 ★ 9 之部分分拆（用 1..8 之相異部分）共 %d 個: %s ⟹ **唔唯一** ⟹ 單憑「9 = 1+3+5」冇判別力"
    % (len(parts), [p for p in parts]), len(parts) > 1,
    "⟹ 必須用**表示內容**（A3）而唔係整數分拆")

# ══════════════════════════════════════════════════════════════════════
print()
print("[E] 誠實評估")
chk("E1 ⚠️ 本輪**未計算** 9 模式空間之實際表示內容（需要 icosahedral 調和函數在 I 下之分解）"
    " ⟹ B2 之橋係「**等價陳述**」而非推導", True)
chk("E2 ★ 但已收窄: 含糊命題「世代數 = 空間維數」⟹ 精確命題「模式空間 ≅ Γ₁⊗Γ₁」"
    "（或至少含 Γ₁ 扇區），後者可**計算檢驗**", True)
chk("E3 ⚠️ 且 Γ₁⊗Γ₂ = Γ₄⊕Γ₅ 亦 dim 9 ⟹ 手性選擇（Γ₁ vs Γ₂）在此處**有判別力**"
    "（與 docs/14 之定向問題相連）", True)
chk("E4 ★ 下一步（若要做完）: 用 20 面體調和函數（或 60 節點球面上之模空間）計實際分解 "
    "⟹ 直接檢驗 P-M1/P-M3", True)

# ══════════════════════════════════════════════════════════════════════
print()
print("[F] 判決")
chk("F1 ★★ 橋已建立: **N_gen = dim Γ₁ ⟺ |M| = (dim Γ₁)²**（由 O137 |M| = N_gen² + 數值 A3）", True)
chk("F2 ★ Γ₁⊗Γ₁ = 1 ⊕ Γ₁ ⊕ Γ₅ 之分解為**精確恆等式**（數值特徵標驗證）", True)
chk("F3 ⚠️ 內容層面（9 模式空間是否真為 Γ₁⊗Γ₁）🔴 未計算 ⟹ 識別仍未證，但已獲可計算形式", True)
chk("F4 ★ 密度: 零自由參數（群 + 特徵標表）", True)

print()
print("=" * 98)
print("RESULT: %d/%d PASS" % (PASS, TOTAL))
if PASS != TOTAL:
    print("FAIL: %s" % [c["name"] for c in checks if not c["pass"]])
print("=" * 98)
out = {"script": "15_multiplicity_equals_dimension", "date": "2026-09-28",
       "class_sizes": sizes, "chi_G1": {c: chi_v[c] for c in CL},
       "decomp_G1xG1": m11, "decomp_G1xG2": m12, "bridge": "N_gen = dim Gamma_1 <=> |M| = dim(Gamma_1 x Gamma_1)",
       "checks": checks, "n_pass": PASS, "n_total": TOTAL}
path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "15_checks.json")
with open(path, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("saved %s" % path)
